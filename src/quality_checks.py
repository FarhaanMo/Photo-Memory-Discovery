"""Deterministic quality gates for final Corpus B records.

Lexical checks against raw_text, not LLM judgements. Each failure is reported
as (record_id, field, value, reason).
"""
from src.corpus_b_sanitizer import (
    FORGOTTEN_VOCAB,
    forgotten_category_supported,
    has_explicit_no_refinement,
    has_quote_evidence,
    has_sequence_evidence,
    has_visual_evidence,
    is_placeholder_strategy,
    strategy_matches_workaround,
)
from src.schema import FAILURE_STAGES

GATES = [
    "processing_errors",
    "unsupported_forgotten_information",
    "placeholder_search_strategy",
    "silent_refinement_marked_no",
    "duplicated_strategy_workaround",
    "quoted_search_without_quote_evidence",
    "visual_without_visual_evidence",
    "invalid_failure_stage",
]


def row_gate_failures(raw_text, fields):
    """Return [(gate, field, value, reason)] for one sanitized record."""
    raw = raw_text or ""
    out = []

    forgotten = fields.get("forgotten_information", "unknown")
    if forgotten != "unknown":
        for term in [t.strip() for t in forgotten.split(";") if t.strip()]:
            if term not in FORGOTTEN_VOCAB:
                out.append(("unsupported_forgotten_information", "forgotten_information", term,
                            "not in controlled vocabulary"))
            elif not forgotten_category_supported(raw, term):
                out.append(("unsupported_forgotten_information", "forgotten_information", term,
                            "raw_text does not state this was forgotten"))

    strategy = fields.get("search_strategy", "unknown")
    workaround = fields.get("workaround", "unknown")
    if is_placeholder_strategy(strategy):
        out.append(("placeholder_search_strategy", "search_strategy", strategy, "placeholder, not an observed action"))

    if fields.get("refinement_attempt") == "no" and not has_explicit_no_refinement(raw):
        out.append(("silent_refinement_marked_no", "refinement_attempt", "no", "raw_text is silent on refinement"))

    if strategy_matches_workaround(strategy, workaround) and not has_sequence_evidence(raw):
        out.append(("duplicated_strategy_workaround", "search_strategy/workaround",
                    "{} / {}".format(strategy, workaround), "same action in both without sequence evidence"))

    for field, value in (("search_strategy", strategy), ("workaround", workaround)):
        if "quote" in str(value).lower() and not has_quote_evidence(raw):
            out.append(("quoted_search_without_quote_evidence", field, value, "raw_text never mentions quotes"))

    if fields.get("remembered_visual") == "true" and not has_visual_evidence(raw):
        out.append(("visual_without_visual_evidence", "remembered_visual", "true",
                    "no explicit visual characteristic in raw_text"))

    if fields.get("failure_stage") not in FAILURE_STAGES:
        out.append(("invalid_failure_stage", "failure_stage", fields.get("failure_stage"), "not an allowed stage"))

    return out


def run_quality_checks(processed_df):
    """Return {gate: [(record_id, field, value, reason), ...]} across all rows."""
    failures = {gate: [] for gate in GATES}
    for _, row in processed_df.iterrows():
        rid = str(row["record_id"])
        status = str(row.get("processing_status"))
        if status == "error":
            failures["processing_errors"].append(
                (rid, "processing_status", status, str(row.get("processing_error", ""))[:160])
            )
            continue
        for gate, field, value, reason in row_gate_failures(str(row.get("raw_text", "")), row.to_dict()):
            failures[gate].append((rid, field, value, reason))
    return failures
