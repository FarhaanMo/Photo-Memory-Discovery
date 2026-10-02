import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import (
    GROQ_MODEL,
    PROJECT_ROOT,
    TRIAGE_BATCH_SIZE,
    TRIAGE_CSV_PATH,
    TRIAGE_PROMPT_VERSION,
)
from src.llm_client import complete_json
from src.persist import _utc_now
from src.relevance import prepare_text_for_llm
from src.schema import SchemaError, validate_triage_item

TRIAGE_AI_COLUMNS = [
    "relevance_level",
    "triage_reason",
    "triage_confidence",
    "triage_status",
    "triage_error",
    "triage_model",
    "triage_prompt_version",
    "triaged_at",
]


def _load_prompt():
    return (PROJECT_ROOT / "prompts" / "triage.md").read_text(encoding="utf-8")


def load_triage(path=None):
    target = Path(path) if path is not None else TRIAGE_CSV_PATH
    if not target.is_file() or target.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(
        target,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
        encoding="utf-8-sig",
    )


def save_triage(df, path=None):
    import time

    target = Path(path) if path is not None else TRIAGE_CSV_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8")
    last_exc = None
    for _attempt in range(10):
        try:
            tmp.replace(target)
            return
        except OSError as exc:
            last_exc = exc
            time.sleep(0.3)
    df.to_csv(target, index=False, encoding="utf-8")
    if tmp.exists():
        try:
            tmp.unlink()
        except OSError:
            pass
    if last_exc and not target.exists():
        raise last_exc


def _blank_ai():
    return {
        "relevance_level": "",
        "triage_reason": "",
        "triage_confidence": "",
        "triage_status": "pending",
        "triage_error": "",
        "triage_model": GROQ_MODEL,
        "triage_prompt_version": TRIAGE_PROMPT_VERSION,
        "triaged_at": "",
    }


def _upsert(raw_row, ai_fields, path=None):
    existing = load_triage(path)
    record_id = str(raw_row["record_id"])
    new_row = {}
    for col in raw_row.index:
        if col == "raw_text_empty":
            continue
        new_row[col] = raw_row[col]
    for col in TRIAGE_AI_COLUMNS:
        new_row[col] = ai_fields.get(col, "")
    if existing is None or existing.empty:
        out = pd.DataFrame([new_row])
    else:
        keep = existing[existing["record_id"].astype(str) != record_id]
        out = pd.concat([keep, pd.DataFrame([new_row])], ignore_index=True)
    save_triage(out, path)
    return out


def _pack_records(rows):
    packed = []
    for row in rows:
        excerpt, _truncated = prepare_text_for_llm(str(row.get("raw_text", "")))
        packed.append(
            {
                "record_id": str(row["record_id"]),
                "source": str(row.get("source", "")),
                "raw_text": excerpt,
            }
        )
    return packed


def _items_from_payload(data):
    if not isinstance(data, dict):
        return []
    items = data.get("items")
    if items is None and "record_id" in data:
        return [data]
    if not isinstance(items, list):
        return []
    return items


def _apply_item(row, item):
    ai = _blank_ai()
    ai["triaged_at"] = _utc_now()
    try:
        parsed = validate_triage_item(item, str(row["record_id"]))
    except SchemaError as exc:
        ai["triage_status"] = "error"
        ai["triage_error"] = str(exc)
        return ai
    ai.update(parsed)
    ai["triage_status"] = "success"
    ai["triage_error"] = ""
    return ai


def triage_single(row):
    packed = _pack_records([row])
    user = "Classify this one record.\n" + json.dumps(packed[0], ensure_ascii=False)
    result = complete_json(_load_prompt(), user)
    if result.auth_failed:
        raise RuntimeError(result.error)
    ai = _blank_ai()
    ai["triaged_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if not result.ok:
        ai["triage_status"] = "error"
        ai["triage_error"] = result.error
        return ai
    items = _items_from_payload(result.data)
    if not items:
        ai["triage_status"] = "error"
        ai["triage_error"] = "No triage items in model response."
        return ai
    return _apply_item(row, items[0])


def triage_batch(rows):
    packed = _pack_records(rows)
    user = "Classify every record below.\n" + json.dumps(packed, ensure_ascii=False)
    result = complete_json(_load_prompt(), user)
    if result.auth_failed:
        raise RuntimeError(result.error)
    by_id = {}
    if result.ok:
        for item in _items_from_payload(result.data):
            if isinstance(item, dict) and item.get("record_id"):
                by_id[str(item.get("record_id"))] = item
    outputs = []
    for row in rows:
        rid = str(row["record_id"])
        if rid in by_id:
            outputs.append(_apply_item(row, by_id[rid]))
        else:
            outputs.append(triage_single(row))
    return outputs


def successful_triage_ids(df):
    if df is None or df.empty or "triage_status" not in df.columns:
        return set()
    ok = df["triage_status"].astype(str) == "success"
    return set(df.loc[ok, "record_id"].astype(str))


def run_triage(raw_df, progress_cb=None, path=None, force=False, batch_size=None):
    """Triage every raw row. Does not call the full classification pipeline."""
    size = int(batch_size or TRIAGE_BATCH_SIZE)
    existing = load_triage(path)
    done = set() if force else successful_triage_ids(existing)
    pending = []
    for _, row in raw_df.iterrows():
        if str(row["record_id"]) not in done:
            pending.append(row)
    total = len(pending)
    halt = None
    processed = 0
    for start in range(0, total, size):
        chunk = pending[start : start + size]
        if progress_cb:
            progress_cb(processed, total, str(chunk[0]["record_id"]), "batch")
        try:
            ais = triage_batch(chunk)
        except RuntimeError as exc:
            halt = str(exc)
            break
        for row, ai in zip(chunk, ais):
            try:
                _upsert(row, ai, path=path)
            except OSError:
                time.sleep(0.5)
                _upsert(row, ai, path=path)
            processed += 1
            if progress_cb:
                progress_cb(
                    processed,
                    total,
                    str(row["record_id"]),
                    ai.get("triage_status", ""),
                )
    return {
        "attempted": total,
        "completed": processed,
        "halt_message": halt,
        "df": load_triage(path),
    }
