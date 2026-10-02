from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_CSV_PATH
from src.schema import AI_COLUMNS, REQUIRED_COLUMNS


def _utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def raw_source_columns(raw_df):
    return [c for c in raw_df.columns if c != "raw_text_empty"]


def load_processed(path=None):
    target = Path(path) if path is not None else PROCESSED_CSV_PATH
    if not target.is_file() or target.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(
        target,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
        encoding="utf-8-sig",
    )


def save_processed(df, path=None):
    target = Path(path) if path is not None else PROCESSED_CSV_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8")
    tmp.replace(target)


def blank_ai_row():
    row = {col: "" for col in AI_COLUMNS}
    row["processing_status"] = "pending"
    return row


def upsert_processed_row(raw_row, ai_fields, processed_df=None, path=None):
    """Merge one classified row into the processed CSV. Never writes the raw file."""
    processed = processed_df if processed_df is not None else load_processed(path)
    record_id = str(raw_row["record_id"])
    source_cols = [c for c in raw_row.index if c != "raw_text_empty"]

    new_row = {}
    for col in source_cols:
        new_row[col] = raw_row[col]
    for col in AI_COLUMNS:
        new_row[col] = ai_fields.get(col, "")

    if processed is None or processed.empty:
        out = pd.DataFrame([new_row])
    else:
        keep = processed[processed["record_id"].astype(str) != record_id]
        out = pd.concat([keep, pd.DataFrame([new_row])], ignore_index=True)

    preferred = [c for c in REQUIRED_COLUMNS if c in out.columns]
    rest = [c for c in out.columns if c not in preferred]
    out = out[preferred + rest]
    save_processed(out, path)
    return out


def already_successful_ids(processed_df):
    if processed_df is None or processed_df.empty:
        return set()
    if "processing_status" not in processed_df.columns:
        return set()
    ok = processed_df["processing_status"].astype(str) == "success"
    return set(processed_df.loc[ok, "record_id"].astype(str))
