"""Lexical retrieval for Ask the Research. No embeddings and no model calls.

Only the top-scoring records are returned. Calculated statistics are attached
separately by qa.py and are never computed here.
"""
import re
from collections import OrderedDict

STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "what", "when", "where",
    "which", "who", "why", "how", "are", "was", "were", "did", "does", "have",
    "has", "they", "them", "their", "users", "user", "show", "into", "about",
    "both", "than", "then", "not", "but", "you", "your", "can", "all", "any",
    "main", "most", "more", "some", "there", "these", "those", "using", "used",
}

SOURCE_CUES = OrderedDict([
    ("corpus_a", ("corpus a", "broad public", "public landscape", "reddit")),
    ("corpus_b", ("corpus b", "targeted sample", "targeted vague")),
    ("survey", ("survey", "respondent")),
    ("interview", ("interview", "observed task", "int00")),
])

THEME_WORDS = (
    "expression", "evaluation", "retrieval", "recovery", "scroll", "scrolling",
    "remember", "forgot", "forgotten", "date", "counter", "screenshot", "friction",
    "fallback", "workaround", "memory", "vague",
)

EXCERPT_CHARS = 420


def tokens(text):
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def select_sources(question):
    """Which evidence streams the question is about. Default: all four, still top-k."""
    low = (question or "").lower()
    selected = [name for name, cues in SOURCE_CUES.items() if any(cue in low for cue in cues)]
    if "survey" in low and "interview" in low:
        for name in ("survey", "interview"):
            if name not in selected:
                selected.append(name)
    if "counter" in low and "interview" not in selected:
        selected.append("interview")
    if not selected:
        selected = list(SOURCE_CUES.keys())
    if any(word in low for word in ("limitation", "uncertain", "attempt", "failed", "failure")) and not any(
        word in low for word in ("public", "broad", "reddit", "landscape")
    ):
        selected = [name for name in selected if name != "corpus_a"]
    return selected


def _score(q_tokens, text, boost=0):
    low = (text or "").lower()
    return boost + sum(1 for token in q_tokens if token in low)


def _excerpt(text):
    text = " ".join((text or "").split())
    if len(text) <= EXCERPT_CHARS:
        return text
    return text[:EXCERPT_CHARS].rsplit(" ", 1)[0] + "…"


def _stage_boost(question, stage):
    low = question.lower()
    boost = 0
    for name in ("expression", "evaluation", "retrieval", "recovery", "no_failure"):
        if name.replace("_", " ") in low or name in low:
            if stage == name:
                boost += 4
    if "counter" in low and stage == "no_failure":
        boost += 4
    if any(word in low for word in ("scroll", "scrolling", "fallback")) and stage in (
        "expression", "evaluation", "retrieval", "recovery"
    ):
        boost += 1
    return boost


def score_corpus_a(question, df, q_tokens):
    rows = []
    if df is None or df.empty:
        return rows
    for _, row in df.iterrows():
        text = " ".join([
            row.get("raw_text", ""), row.get("triage_reason", ""), row.get("relevance_level", ""),
            row.get("source", ""),
        ])
        boost = 0
        if "direct" in question.lower() and row.get("relevance_level") == "direct_vague_retrieval":
            boost += 4
        score = _score(q_tokens, text, boost)
        if score <= 0:
            continue
        rows.append({
            "id": row["record_id"],
            "evidence_type": "public",
            "stream": "Broad Public Research",
            "facet": row.get("relevance_level", ""),
            "score": score,
            "url": row.get("url", ""),
            "excerpt": _excerpt(row.get("raw_text", "")),
            "labels": "source: {}; relevance: {}".format(row.get("source", ""), row.get("relevance_level", "")),
        })
    return rows


def score_corpus_b(question, df, q_tokens):
    rows = []
    if df is None or df.empty:
        return rows
    usable = df[df["processing_status"] == "success"] if "processing_status" in df.columns else df
    for _, row in usable.iterrows():
        text = " ".join([
            row.get("raw_text", ""), row.get("failure_stage", ""), row.get("forgotten_information", ""),
            row.get("problem_theme", ""), row.get("search_strategy", ""), row.get("workaround", ""),
            row.get("platform", ""), row.get("photo_type", ""),
        ])
        score = _score(q_tokens, text, _stage_boost(question, row.get("failure_stage", "")))
        if "date" in q_tokens and "date" in str(row.get("forgotten_information", "")).lower():
            score += 3
        if score <= 0:
            continue
        rows.append({
            "id": row["record_id"],
            "evidence_type": "public",
            "stream": "Targeted Vague-Memory Research",
            "facet": row.get("failure_stage", ""),
            "score": score,
            "url": row.get("url", ""),
            "excerpt": _excerpt(row.get("raw_text", "")),
            "labels": "platform: {}; stage: {}; forgotten: {}; outcome: {}".format(
                row.get("platform", ""), row.get("failure_stage", ""),
                row.get("forgotten_information", ""), row.get("retrieval_outcome", ""),
            ),
        })
    return rows


def score_survey(question, df, q_tokens):
    rows = []
    if df is None or df.empty:
        return rows
    fields = [c for c in ("remembered", "methods", "difficulty", "outcome", "open_text", "screening") if c in df.columns]
    for _, row in df.iterrows():
        text = " ".join(str(row.get(c, "")) for c in fields)
        score = _score(q_tokens, text)
        if score <= 0:
            continue
        rows.append({
            "id": row["respondent_id"],
            "evidence_type": "survey",
            "stream": "Survey",
            "facet": "survey",
            "score": score,
            "url": "",
            "excerpt": _excerpt(text),
            "labels": "screening: {}; outcome: {}".format(row.get("screening", ""), row.get("outcome", "")),
        })
    return rows


def score_interviews(question, df, q_tokens):
    rows = []
    if df is None or df.empty:
        return rows
    fields = [
        "target_description", "remembered_before_retrieval", "observed_sequence",
        "failure_stage_observed", "failure_stage_reason", "hardest_moment_quote",
        "researcher_observation", "first_query", "fallback_or_workaround", "retrieval_outcome",
    ]
    for _, row in df.iterrows():
        text = " ".join(str(row.get(c, "")) for c in fields if c in row.index)
        score = _score(q_tokens, text, _stage_boost(question, row.get("failure_stage_observed", "")))
        if score <= 0:
            continue
        rows.append({
            "id": row["participant_id"],
            "evidence_type": "interview",
            "stream": "Interviews",
            "facet": row.get("failure_stage_observed", ""),
            "score": score,
            "url": "",
            "excerpt": _excerpt(text),
            "labels": "stage: {}; first query: {}; fallback: {}; scrolling: {}; outcome: {}; minutes: {}".format(
                row.get("failure_stage_observed", ""), row.get("first_query", ""),
                row.get("fallback_or_workaround", ""),
                "intended method, not a fallback" if (
                    row.get("manual_scrolling") == "yes" and row.get("fallback_or_workaround") in ("none", "")
                ) else row.get("manual_scrolling", ""),
                row.get("retrieval_outcome", ""),
                row.get("time_to_target_minutes", ""),
            ),
        })
    return rows


def has_research_theme(question):
    low = (question or "").lower()
    if any(word in low for word in THEME_WORDS):
        return True
    return any(any(cue in low for cue in cues) for cues in SOURCE_CUES.values())


def in_research_scope(question):
    """False for general questions that only brush the corpus by accident."""
    if has_research_theme(question):
        return True
    low = (question or "").lower()
    if re.search(r"\b(?:dv|gp|int|s)\d+\b", low):
        return True
    domain = {
        "photo", "photos", "picture", "pictures", "image", "images", "search", "query",
        "google", "album", "folder", "screenshot", "interview", "interviews", "survey",
        "respondent", "clue", "clues", "stage", "browse", "browsing", "refine",
        "refinement", "evidence", "limitation", "limitations", "finding", "findings",
        "participant", "retrieval", "remember", "remembered", "forgot", "forgotten",
        "attempt", "attempts", "failed", "failure", "refine", "refined",
    }
    return any(word in domain for word in tokens(question))


def _diversify(rows, per_source):
    """Take the strongest rows, rotating across facets so one stage cannot fill the pack."""
    buckets = OrderedDict()
    for row in rows:
        buckets.setdefault(row.get("facet") or row["id"], []).append(row)
    picked = []
    while len(picked) < per_source and any(buckets.values()):
        for key in list(buckets):
            if not buckets[key]:
                continue
            picked.append(buckets[key].pop(0))
            if len(picked) >= per_source:
                break
    return picked


def _merge_rows(kept, extra, limit):
    ids = {row["id"] for row in kept}
    merged = list(kept)
    for row in extra:
        if row["id"] in ids:
            continue
        merged.append(row)
        ids.add(row["id"])
        if len(merged) >= limit:
            break
    return merged


def _broaden(question, bundle, sources, kept, limit):
    """Add coded evidence when keyword overlap is too thin. Do not pull unrelated streams."""
    low = (question or "").lower()
    extra = []
    interviewish = any(word in low for word in (
        "interview", "scroll", "brows", "fallback", "refine", "counter", "participant", "attempt",
    ))
    memoryish = any(word in low for word in ("date", "remember", "forgot", "forgotten", "clue", "memory"))
    limitationish = any(word in low for word in ("limitation", "uncertain"))

    if "counter" in low:
        interviews = bundle.get("interviews")
        if interviews is not None and not getattr(interviews, "empty", True):
            matched = interviews[interviews["failure_stage_observed"] == "no_failure"]
            extra.extend(score_interviews(
                "no_failure counter interview",
                matched,
                tokens("no_failure counter interview memory"),
            ))
    if (interviewish or "interview" in sources) and "counter" not in low:
        if not any(row["stream"] == "Interviews" for row in kept):
            extra.extend(_backfill_interviews(question, bundle.get("interviews")))
    if memoryish and not any(row["stream"] == "Targeted Vague-Memory Research" for row in kept):
        extra.extend(score_corpus_b(
            question + " date remembered forgotten",
            bundle.get("corpus_b"),
            tokens("date time remembered forgotten expression"),
        )[:4])
    if any(word in low for word in ("scroll", "brows", "fallback")):
        extra.extend(score_survey(
            "scrolling browsing",
            bundle.get("survey"),
            tokens("scrolling browsing manual"),
        )[:3])
    if limitationish and len(kept) + len(extra) < 3:
        extra.extend(_backfill_interviews(question, bundle.get("interviews"))[:3])
    if len(_merge_rows(kept, extra, limit)) < 3 and "counter" not in low and ("photo" in low or "retriev" in low or "search" in low):
        relaxed = tokens(question + " photo retrieval memory search")
        if "interview" in sources or interviewish:
            extra.extend(score_interviews(question, bundle.get("interviews"), relaxed)[:5])
        if "corpus_b" in sources or memoryish:
            extra.extend(score_corpus_b(question, bundle.get("corpus_b"), relaxed)[:3])
        if "survey" in sources:
            extra.extend(score_survey(question, bundle.get("survey"), relaxed)[:2])
        if "corpus_a" in sources and any(word in low for word in ("public", "broad", "reddit", "landscape")):
            extra.extend(score_corpus_a(question, bundle.get("corpus_a"), relaxed)[:3])
    return _merge_rows(kept, extra, limit)


def _backfill_interviews(question, df):
    """An interview-wide question may not share words with the notes. Include the five tasks."""
    if df is None or df.empty:
        return []
    return score_interviews(question + " expression retrieval evaluation scrolling memory", df, tokens(
        "expression retrieval evaluation scrolling memory photo"
    ))


def retrieve(question, bundle, per_source=4, limit=12):
    """Return compact evidence. bundle keys: corpus_a, corpus_b, survey, interviews."""
    q_tokens = tokens(question)
    sources = select_sources(question)
    scored = []
    if "corpus_a" in sources:
        scored += score_corpus_a(question, bundle.get("corpus_a"), q_tokens)
    if "corpus_b" in sources:
        scored += score_corpus_b(question, bundle.get("corpus_b"), q_tokens)
    if "survey" in sources:
        scored += score_survey(question, bundle.get("survey"), q_tokens)
    if "interview" in sources:
        scored += score_interviews(question, bundle.get("interviews"), q_tokens)

    by_stream = {}
    for row in scored:
        by_stream.setdefault(row["stream"], []).append(row)
    for stream in by_stream:
        by_stream[stream].sort(key=lambda row: (-row["score"], row["id"]))

    low = question.lower()
    if "interview" in sources and "interview" in low and not by_stream.get("Interviews"):
        by_stream["Interviews"] = _backfill_interviews(question, bundle.get("interviews"))
        by_stream["Interviews"].sort(key=lambda row: row["id"])

    kept = []
    interview_cap = 5 if "interview" in sources and "interview" in low else per_source
    for stream, cap in (
        ("Interviews", interview_cap),
        ("Survey", per_source),
        ("Targeted Vague-Memory Research", per_source),
        ("Broad Public Research", per_source),
    ):
        kept.extend(_diversify(by_stream.get(stream, []), cap))
    kept = kept[:limit]
    if "counter" in (question or "").lower():
        kept = [
            row for row in kept
            if row.get("stream") != "Interviews" or row.get("facet") == "no_failure"
        ]
    if len(kept) < 3:
        kept = _broaden(question, bundle, sources, kept, limit)

    streams_with_rows = {row["stream"] for row in kept}
    return {
        "sources": sources,
        "records": kept,
        "theme": has_research_theme(question),
        "streams_with_rows": sorted(streams_with_rows),
    }
