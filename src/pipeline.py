from src.audit import audit_record
from src.config import AUDIT_PROMPT_VERSION, GROQ_MODEL, MAX_CLASSIFY_N, PROMPT_VERSION
from src.corpus_b_sanitizer import sanitize_record
from src.extract import extract_record
from src.quality_checks import row_gate_failures
from src.persist import (
    already_successful_ids,
    blank_ai_row,
    load_processed,
    upsert_processed_row,
    _utc_now,
)
from src.relevance import classify_relevance
from src.schema import RELEVANCE_TRUE, empty_extraction_fields


class PipelineHalt(Exception):
    def __init__(self, message):
        super(PipelineHalt, self).__init__(message)
        self.message = message


def _is_rate_limited(error):
    text = str(error or "").lower()
    return "rate_limit" in text or "rate limit" in text or "error code: 429" in text


def _first_n_frame(raw_df, limit_n):
    cap = min(int(limit_n), MAX_CLASSIFY_N, len(raw_df))
    cap = max(cap, 0)
    return raw_df.iloc[:cap].copy(), cap


def classify_one_record(raw_row, processed_path=None, targeted=False):
    """Classify one record.

    When targeted is True (Corpus B, sampling_frame=targeted_direct), the
    relevance gate is skipped because inclusion was decided at collection time.
    """
    ai = blank_ai_row()
    ai["model_name"] = GROQ_MODEL
    ai["prompt_version"] = PROMPT_VERSION
    record_id = str(raw_row["record_id"])
    raw_text = str(raw_row.get("raw_text", ""))
    source = str(raw_row.get("source", ""))
    platform = str(raw_row.get("platform", ""))

    if raw_text.strip() == "":
        ai["processing_status"] = "error"
        ai["processing_error"] = "Empty raw_text; Groq was not called."
        ai["relevance_level"] = "irrelevant"
        ai["relevant_to_retrieval"] = "false"
        ai["classified_at"] = _utc_now()
        processed = upsert_processed_row(raw_row, ai, path=processed_path)
        return ai, processed, False

    if targeted:
        ai["prompt_version"] = "{}+{}".format(PROMPT_VERSION, AUDIT_PROMPT_VERSION)
        ai["text_truncated_for_llm"] = "false"
        ai["relevant_to_retrieval"] = RELEVANCE_TRUE
        ai["relevance_level"] = "direct_vague_retrieval"
        ai["relevance_reason"] = "Included by targeted_direct sampling frame; relevance gate not run."
        ai["relevance_confidence"] = "not_assessed"
        ai.update(empty_extraction_fields())
    else:
        rel_result, truncated = classify_relevance(record_id, raw_text, source)
        ai["text_truncated_for_llm"] = "true" if truncated else "false"
        if rel_result.auth_failed:
            raise PipelineHalt(rel_result.error)
        if not rel_result.ok:
            ai["processing_status"] = "error"
            ai["processing_error"] = rel_result.error
            ai["classified_at"] = _utc_now()
            processed = upsert_processed_row(raw_row, ai, path=processed_path)
            return ai, processed, False

        rel = rel_result.data
        ai["relevant_to_retrieval"] = rel["relevant_to_retrieval"]
        ai["relevance_level"] = rel["relevance_level"]
        ai["relevance_reason"] = rel["relevance_reason"]
        ai["relevance_confidence"] = rel["relevance_confidence"]
        ai.update(empty_extraction_fields())

        if rel["relevant_to_retrieval"] != RELEVANCE_TRUE:
            ai["processing_status"] = "success"
            ai["processing_error"] = ""
            ai["classified_at"] = _utc_now()
            processed = upsert_processed_row(raw_row, ai, path=processed_path)
            return ai, processed, False

    ext_result, ext_truncated = extract_record(record_id, raw_text, source, platform)
    if ext_truncated:
        ai["text_truncated_for_llm"] = "true"
    if ext_result.auth_failed or (targeted and _is_rate_limited(ext_result.error)):
        raise PipelineHalt(ext_result.error)
    if not ext_result.ok:
        ai["processing_status"] = "error"
        ai["processing_error"] = ext_result.error
        ai["classified_at"] = _utc_now()
        processed = upsert_processed_row(raw_row, ai, path=processed_path)
        return ai, processed, False

    ai.update(ext_result.data)

    if targeted:
        gate_failures = []
        for _attempt in range(2):
            audit_result, _ = audit_record(record_id, raw_text, platform, ext_result.data)
            if audit_result.auth_failed or _is_rate_limited(audit_result.error):
                raise PipelineHalt(audit_result.error)
            if not audit_result.ok:
                ai["processing_status"] = "error"
                ai["processing_error"] = audit_result.error
                ai["classified_at"] = _utc_now()
                processed = upsert_processed_row(raw_row, ai, path=processed_path)
                return ai, processed, False
            sanitized, _changes = sanitize_record(raw_text, audit_result.data)
            gate_failures = row_gate_failures(raw_text, sanitized)
            if not gate_failures:
                break
        ai.update(sanitized)
        if gate_failures:
            ai["processing_status"] = "needs_review"
            ai["processing_error"] = " | ".join(
                "{}: {}={} ({})".format(g, f, v, r) for g, f, v, r in gate_failures
            )
            ai["classified_at"] = _utc_now()
            processed = upsert_processed_row(raw_row, ai, path=processed_path)
            return ai, processed, False

    if (
        ai.get("failure_stage") == "expression"
        and ai.get("relevance_level") != "direct_vague_retrieval"
    ):
        ai["failure_stage"] = "other_unclear"
    ai["processing_status"] = "success"
    ai["processing_error"] = ""
    ai["classified_at"] = _utc_now()
    processed = upsert_processed_row(raw_row, ai, path=processed_path)
    return ai, processed, False


def records_to_classify(raw_df, limit_n, retry_errors=False, processed_df=None, force=False):
    subset, cap = _first_n_frame(raw_df, limit_n)
    processed = processed_df if processed_df is not None else load_processed()
    success_ids = already_successful_ids(processed)
    error_ids = set()
    if processed is not None and not processed.empty and "processing_status" in processed.columns:
        err = processed["processing_status"].astype(str) == "error"
        error_ids = set(processed.loc[err, "record_id"].astype(str))
        review = processed["processing_status"].astype(str) == "needs_review"
        success_ids |= set(processed.loc[review, "record_id"].astype(str))

    rows = []
    for _, row in subset.iterrows():
        rid = str(row["record_id"])
        if not force and rid in success_ids:
            continue
        if not force and rid in error_ids and not retry_errors:
            continue
        rows.append(row)
    return rows, cap


def run_first_n(
    raw_df,
    limit_n,
    retry_errors=False,
    progress_cb=None,
    processed_path=None,
    force=False,
    targeted=False,
):
    """Classify at most MAX_CLASSIFY_N records from the start of the file."""
    rows, cap = records_to_classify(
        raw_df,
        limit_n,
        retry_errors=retry_errors,
        processed_df=load_processed(processed_path),
        force=force,
    )
    total = len(rows)
    processed = load_processed(processed_path)
    halt_message = None
    for index, row in enumerate(rows):
        if progress_cb:
            progress_cb(index, total, str(row["record_id"]), "running")
        try:
            _ai, processed, _ = classify_one_record(
                row, processed_path=processed_path, targeted=targeted
            )
        except PipelineHalt as halt:
            halt_message = halt.message
            if progress_cb:
                progress_cb(index, total, str(row["record_id"]), "halted")
            break
        if progress_cb:
            progress_cb(index + 1, total, str(row["record_id"]), "saved")
    return {
        "processed_df": processed,
        "attempted": total,
        "limit": cap,
        "halt_message": halt_message,
    }
