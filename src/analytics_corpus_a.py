"""Deterministic analytics for Corpus A (broad public retrieval landscape).

Relevance labels come from the single-pass LLM triage file; every count here
is computed with Pandas. Corpus A must not be used to estimate prevalence among
Google Photos users and is never pooled with Corpus B.
"""
from collections import OrderedDict

import pandas as pd

from src.config import TRIAGE_CSV_PATH

LABEL = "Broad public research"
RELEVANCE_ORDER = ["direct_vague_retrieval", "retrieval_adjacent", "irrelevant"]
RELEVANCE_DISPLAY = {
    "direct_vague_retrieval": "Direct vague-memory retrieval",
    "retrieval_adjacent": "Retrieval-adjacent",
    "irrelevant": "Not retrieval-related",
}


def load_corpus_a(path=None):
    target = path or TRIAGE_CSV_PATH
    if not target.is_file():
        return None
    return pd.read_csv(target, dtype=str, keep_default_na=False, na_filter=False, encoding="utf-8-sig")


def triaged(df):
    if "triage_status" not in df.columns:
        return df
    return df[df["triage_status"] == "success"]


def relevance_counts(df):
    counts = triaged(df)["relevance_level"].value_counts()
    return OrderedDict((RELEVANCE_DISPLAY[k], int(counts.get(k, 0))) for k in RELEVANCE_ORDER)


def source_counts(df):
    counts = df["source"].value_counts()
    return OrderedDict((str(k), int(v)) for k, v in counts.items())


def source_by_relevance(df):
    table = pd.crosstab(triaged(df)["source"], triaged(df)["relevance_level"])
    table = table.reindex(columns=RELEVANCE_ORDER, fill_value=0)
    table.columns = [RELEVANCE_DISPLAY[c] for c in table.columns]
    table["Total"] = table.sum(axis=1)
    return table.sort_values("Total", ascending=False)


def confidence_counts(df):
    counts = triaged(df)["triage_confidence"].value_counts()
    return OrderedDict((k, int(counts.get(k, 0))) for k in ["high", "medium", "low"])


def status_summary(df):
    total = len(df)
    ok = len(triaged(df))
    return {"total": total, "triaged": ok, "not_triaged": total - ok}


def direct_records(df):
    cols = ["record_id", "source", "date", "url", "raw_text", "triage_reason"]
    return triaged(df)[triaged(df)["relevance_level"] == "direct_vague_retrieval"][cols]
