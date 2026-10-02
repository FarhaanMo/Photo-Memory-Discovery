"""Deterministic analytics for Corpus B (targeted vague-memory retrieval sample).

Only rows with processing_status == success are analysed. Counts describe the
targeted qualitative sample only: never population percentages, never pooled
with Corpus A.
"""
from collections import OrderedDict

import pandas as pd

from src.config import TARGETED_CSV_PATH, TARGETED_PROCESSED_CSV_PATH
from src.corpus_b_sanitizer import FORGOTTEN_VOCAB
from src.ingest import load_targeted_csv
from src.schema import FAILURE_STAGES, OUTCOMES, REFINEMENT, REMEMBERED_FIELDS

LABEL = "Targeted vague-memory research"
LIMITATION = "Targeted qualitative research — not a population prevalence estimate."
QUALITATIVE_NOTE = "Targeted public evidence is a deliberately selected qualitative set."


def analysed_prefix(n):
    return "Within the {n} analysed targeted examples".format(n=int(n))


def collection_phrase(analysed, collected):
    return "{v} analysed examples from {t} collected public cases".format(
        v=int(analysed), t=int(collected)
    )
EVIDENCE_ORDER = ["strong", "moderate", "weak", "unclear"]
CLUE_DISPLAY = OrderedDict((f, f.replace("remembered_", "").capitalize()) for f in REMEMBERED_FIELDS)
STAGE_DISPLAY = OrderedDict([
    ("expression", "Expression"),
    ("retrieval", "Retrieval"),
    ("evaluation", "Evaluation"),
    ("recovery", "Recovery"),
    ("other_unclear", "Other / unclear"),
])


def load_corpus_b():
    """Return (processed_df or empty, source_total)."""
    source_total = len(load_targeted_csv(TARGETED_CSV_PATH)) if TARGETED_CSV_PATH.is_file() else 0
    path = TARGETED_PROCESSED_CSV_PATH
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame(), source_total
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False, encoding="utf-8-sig")
    return df, source_total


def valid(df):
    if df.empty or "processing_status" not in df.columns:
        return df
    return df[df["processing_status"] == "success"]


def status_summary(df, source_total):
    statuses = df["processing_status"] if not df.empty else pd.Series(dtype=str)
    n_valid = int((statuses == "success").sum())
    return {
        "source_total": source_total,
        "valid": n_valid,
        "needs_review": int((statuses == "needs_review").sum()),
        "errors": int((statuses == "error").sum()),
        "not_started": max(source_total - len(df), 0),
        "excluded": max(source_total - n_valid, 0),
        "preliminary": False,
    }


def _ordered(series, order, display=None):
    counts = series.value_counts()
    out = OrderedDict()
    for key in order:
        out[(display or {}).get(key, key)] = int(counts.get(key, 0))
    for key, value in counts.items():
        label = (display or {}).get(key, key)
        if label not in out:
            out[label] = int(value)
    return out


def failure_stage_counts(df):
    return _ordered(valid(df)["failure_stage"], FAILURE_STAGES, STAGE_DISPLAY)


def clue_counts(df):
    v = valid(df)
    return OrderedDict((label, int((v[field] == "true").sum())) for field, label in CLUE_DISPLAY.items())


def forgotten_counts(df):
    """Records mentioning each forgotten category (a record can count in several)."""
    counts = OrderedDict((c, 0) for c in FORGOTTEN_VOCAB)
    counts["unknown (not explicitly specified)"] = 0
    for value in valid(df)["forgotten_information"]:
        terms = [t.strip() for t in str(value).split(";") if t.strip()]
        if not terms or terms == ["unknown"]:
            counts["unknown (not explicitly specified)"] += 1
            continue
        for t in terms:
            counts[t] = counts.get(t, 0) + 1
    return OrderedDict((k, v) for k, v in counts.items() if v > 0)


def strategy_counts(df):
    return _ordered(valid(df)["search_strategy"], [])


def workaround_counts(df):
    return _ordered(valid(df)["workaround"], [])


def refinement_counts(df):
    return _ordered(valid(df)["refinement_attempt"], REFINEMENT)


def outcome_counts(df):
    return _ordered(valid(df)["retrieval_outcome"], OUTCOMES)


def evidence_counts(df):
    return _ordered(valid(df)["evidence_strength"], EVIDENCE_ORDER)


def platform_counts(df):
    return _ordered(valid(df)["platform"], [])


def warning_count(df):
    return int((valid(df)["extraction_warning"] != "none").sum())


def remembered_list(row):
    return [label for field, label in CLUE_DISPLAY.items() if row.get(field) == "true"]
