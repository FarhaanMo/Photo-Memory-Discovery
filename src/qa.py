"""Grounded Ask-the-Research synthesis.

Statistics are computed in the analytics modules and passed in as text.
The model is instructed not to invent counts. Citations outside the pack are dropped.
"""
import json
import re

import pandas as pd

from src import analytics_corpus_a as A
from src import analytics_corpus_b as B
from src import analytics_interviews as I
from src import analytics_survey as S
from src.config import MIN_EVIDENCE, PROJECT_ROOT, TOP_K
from src.llm_client import complete_json
from src.retrieve import in_research_scope, retrieve

PUBLIC_LLM_ERROR = (
    "AI synthesis is temporarily unavailable. You can still explore the research "
    "through the dashboard and Evidence Explorer."
)
STAT_IDS = {
    "corpus_a": "STAT_CORPUS_A",
    "corpus_b": "STAT_CORPUS_B",
    "survey": "STAT_SURVEY",
    "interview": "STAT_INTERVIEWS",
}


def _plain(mapping):
    return {str(key): int(value) for key, value in mapping.items()}


def calculated_stats(bundle, sources):
    """Small precomputed blocks. Only selected streams are included."""
    stats = {}
    if "corpus_a" in sources and bundle.get("corpus_a") is not None:
        frame = bundle["corpus_a"]
        status = A.status_summary(frame)
        stats["corpus_a"] = {
            "id": STAT_IDS["corpus_a"],
            "evidence_type": "statistic",
            "role": "Broad public research. 225 public conversations screened into vague-memory retrieval, broader search issues, or unrelated. Not a prevalence estimate.",
            "records": status["total"],
            "screened": status["triaged"],
            "relevance_counts": _plain(A.relevance_counts(frame)),
        }
    if "corpus_b" in sources:
        frame = bundle.get("corpus_b")
        if frame is None:
            frame = pd.DataFrame()
        total = bundle.get("corpus_b_total") or 0
        status = B.status_summary(frame, total)
        block = {
            "id": STAT_IDS["corpus_b"],
            "evidence_type": "statistic",
            "role": (
                "Targeted Vague-Memory Research. {scope}. {note} {limit} "
                "Counts below use only examples that completed structured analysis."
            ).format(
                scope=B.collection_phrase(status["valid"], status["source_total"]),
                note=B.QUALITATIVE_NOTE,
                limit=B.LIMITATION,
            ),
            "analysed": status["valid"],
            "collected": status["source_total"],
            "excluded_from_structured_analysis": status["excluded"],
        }
        if frame is not None and status["valid"]:
            block["failure_stage_counts"] = _plain(B.failure_stage_counts(frame))
            block["remembered_clue_counts"] = _plain(B.clue_counts(frame))
            block["forgotten_information_counts"] = _plain(B.forgotten_counts(frame))
            block["workaround_counts"] = _plain(B.workaround_counts(frame))
            block["outcome_counts"] = _plain(B.outcome_counts(frame))
        stats["corpus_b"] = block
    if "survey" in sources and bundle.get("survey") is not None:
        frame = bundle["survey"]
        summary = S.summary(frame)
        stats["survey"] = {
            "id": STAT_IDS["survey"],
            "evidence_type": "statistic",
            "respondents": len(frame),
            "sample": "Convenience sample. Not representative.",
            "screening_inconsistency": S.screened_out_ids(frame),
            "methods_note": S.METHODS_NOTE,
            "remembered_clue_counts": _plain(summary["remembered"]),
            "difficulty_counts": _plain(summary["difficulty"]),
            "outcome_counts": _plain(summary["outcome"]),
            "retrieval_frequency_counts": _plain(summary["retrieval_frequency"]),
            "screening_counts": _plain(summary["screening"]),
        }
    if "interview" in sources and bundle.get("interviews") is not None:
        frame = bundle["interviews"]
        summary = I.summary(frame)
        stats["interview"] = {
            "id": STAT_IDS["interview"],
            "evidence_type": "statistic",
            "observed_tasks": summary["interviews"],
            "synthetic_interviews": 0,
            "wording": I.prefix(frame),
            "failure_stage_counts": _plain(summary["stages"]),
            "remembered_clue_counts": _plain(summary["clues"]),
            "refinement_attempted": summary["refined"],
            "manual_scrolling": summary["manual_scrolling"],
            "outcomes": _plain(summary["outcomes"]),
            "time_to_target_minutes": {key: value for key, value in summary["times"].items()},
            "median_time_to_target_minutes": summary["median_time"],
        }
    return stats


def _load_prompt():
    return (PROJECT_ROOT / "prompts" / "qa.md").read_text(encoding="utf-8")


def _allowed_ids(records, stats):
    allowed = {row["id"] for row in records}
    allowed.update(block["id"] for block in stats.values())
    return allowed


def _unsupported_percentages(answer, context_blob):
    found = []
    for match in re.findall(r"\d+(?:\.\d+)?\s*%", answer or ""):
        compact = match.replace(" ", "")
        if compact not in context_blob.replace(" ", "") and match not in context_blob:
            found.append(match)
    return found


def _enforce(question, parsed, records, stats, sources):
    allowed = _allowed_ids(records, stats)
    citations = []
    for item in parsed.get("citations") or []:
        if not isinstance(item, dict):
            continue
        cite_id = str(item.get("id", "")).strip()
        if cite_id in allowed and cite_id not in {c["id"] for c in citations}:
            citations.append({
                "id": cite_id,
                "evidence_type": str(item.get("evidence_type", "")).strip() or "unspecified",
            })
    record_cites = [c for c in citations if not c["id"].startswith("STAT_")]
    stat_cites = [c for c in citations if c["id"].startswith("STAT_")]
    insufficient = bool(parsed.get("insufficient_evidence"))
    # A question can legitimately match fewer than three records (for example one counter-example).
    # Require three citations only when the pack itself contains at least that many.
    needed = min(MIN_EVIDENCE, max(len(records), 1))
    if not citations or (len(record_cites) + len(stat_cites) < needed and not stat_cites):
        insufficient = True
    limitations = str(parsed.get("limitations") or "").strip()
    if limitations.lower() == "none":
        limitations = ""
    answer = str(parsed.get("answer") or "").strip()
    blob = json.dumps(stats, ensure_ascii=False) + " " + " ".join(row["excerpt"] for row in records)
    bad_pct = _unsupported_percentages(answer, blob)
    if bad_pct:
        insufficient = True
        limitations = (limitations + " " if limitations else "") + (
            "These percentages were not in the calculated statistics and are not findings: {}.".format(
                ", ".join(bad_pct)
            )
        )
    if insufficient and not answer:
        answer = "The current research does not contain enough evidence to answer that confidently."
    if answer and not record_cites:
        for row in records:
            if row["id"] not in {c["id"] for c in citations}:
                citations.append({"id": row["id"], "evidence_type": row.get("evidence_type") or "unspecified"})
    return {
        "question": question,
        "insufficient_evidence": insufficient,
        "answer": answer,
        "citations": citations,
        "limitations": limitations.strip(),
        "records": records,
        "sources": sources,
    }


OUT_OF_SCOPE = "Ask the Research is designed to answer questions about this photo-retrieval research."
FALLBACK_NOTE = (
    "AI synthesis is temporarily unavailable, so this answer is generated directly "
    "from the retrieved research evidence."
)
NOT_ENOUGH = "The current research does not contain enough evidence to answer that confidently."


def _ids(records, stream=None):
    found = []
    for row in records or []:
        if stream and row.get("stream") != stream:
            continue
        if row["id"] not in found:
            found.append(row["id"])
    return found


def _citations_for(records, stats, used_stats):
    citations = [{"id": row["id"], "evidence_type": row.get("evidence_type") or "unspecified"} for row in records]
    for key in used_stats:
        block = (stats or {}).get(key) or {}
        if block.get("id") and block["id"] not in {c["id"] for c in citations}:
            citations.append({"id": block["id"], "evidence_type": "statistic"})
    return citations


def _count_phrase(value, total, noun):
    return "{v} of {t} {noun}".format(v=int(value), t=int(total), noun=noun)


def _fallback_answer(question, records, stats, bundle):
    """Prose built only from calculated statistics and retrieved record ids."""
    low = (question or "").lower()
    parts = []
    used = []
    interview = (stats or {}).get("interview") or {}
    survey = (stats or {}).get("survey") or {}
    targeted = (stats or {}).get("corpus_b") or {}
    interviews = bundle.get("interviews") if bundle else None

    def add_stat(key):
        if key not in used:
            used.append(key)

    if interviews is not None and not interviews.empty and any(word in low for word in (
        "interview", "reveal", "scroll", "brows", "fallback", "counter", "refine", "attempt",
        "problem", "difficult", "barrier",
    )):
        notes = I.recurring_observations(interviews)
        if "counter" in low:
            chosen = [note for note in notes if "counter-evidence" in note or "no_failure" in note]
        elif any(word in low for word in ("scroll", "brows", "fallback")):
            chosen = [note for note in notes if "scroll" in note.lower() or "refin" in note.lower()]
        elif any(word in low for word in ("attempt", "refine", "failed")):
            chosen = [note for note in notes if "refin" in note.lower() or "scroll" in note.lower() or "first" in note.lower()]
        else:
            chosen = notes
        if chosen:
            parts.append(" ".join(chosen[:4]))
            add_stat("interview")

    if interview and any(word in low for word in ("expression", "evaluation", "compare", "stage", "break")):
        stages = interview.get("failure_stage_counts") or {}
        tasks = interview.get("observed_tasks") or 0
        if tasks and stages:
            parts.append(
                "Across the {n} observed retrieval tasks, expression is recorded in {e} and evaluation in {v}.".format(
                    n=tasks,
                    e=stages.get("Expression", 0),
                    v=stages.get("Evaluation", 0),
                )
            )
            add_stat("interview")

    if targeted and any(word in low for word in (
        "date", "remember", "forgot", "forgotten", "clue", "expression", "evaluation", "targeted", "example",
    )):
        analysed = targeted.get("analysed") or 0
        forgotten = targeted.get("forgotten_information_counts") or {}
        clues = targeted.get("remembered_clue_counts") or {}
        stages = targeted.get("failure_stage_counts") or {}
        if analysed:
            bits = ["Within the {n} analysed targeted examples".format(n=analysed)]
            if any(word in low for word in ("date", "remember", "forgot", "forgotten", "clue")) and forgotten:
                bits.append("date/time is the stated gap in {n}".format(n=forgotten.get("date/time", 0)))
            if clues and any(word in low for word in ("remember", "clue", "date", "forgot")):
                top = sorted(((k, v) for k, v in clues.items() if v), key=lambda item: -item[1])[:3]
                if top:
                    bits.append("the most often evidenced clues are {t}".format(
                        t=", ".join("{k} ({v})".format(k=k.lower(), v=v) for k, v in top)
                    ))
            if stages and any(word in low for word in ("expression", "evaluation", "compare", "break", "stage")):
                bits.append("expression is {e} and evaluation is {v}".format(
                    e=stages.get("Expression", 0), v=stages.get("Evaluation", 0)
                ))
            if len(bits) > 1:
                parts.append(bits[0] + ", " + ", and ".join(bits[1:]) + ".")
                add_stat("corpus_b")

    if survey and any(word in low for word in (
        "scroll", "brows", "survey", "agree", "remember", "date", "word", "problem", "difficult", "barrier",
    )):
        respondents = survey.get("respondents") or 0
        outcomes = survey.get("outcome_counts") or {}
        remembered = survey.get("remembered_clue_counts") or {}
        difficulty = survey.get("difficulty_counts") or {}
        sentences = []
        browsing = outcomes.get("Yes, after manual scrolling / browsing")
        if browsing and any(word in low for word in ("scroll", "brows", "fallback", "agree")):
            sentences.append(
                "{p} reported eventually finding the photo after manual browsing.".format(
                    p=_count_phrase(browsing, respondents, "respondents")
                )
            )
        words = difficulty.get("Didn't know what words to search")
        if words and any(word in low for word in ("word", "search", "expression", "agree")) and not any(
            word in low for word in ("problem", "difficult", "barrier")
        ):
            sentences.append(
                "{p} did not know what words to search.".format(
                    p=_count_phrase(words, respondents, "respondents")
                )
            )
        if difficulty and any(word in low for word in ("problem", "difficult", "barrier")):
            ranked = sorted(
                ((k, v) for k, v in difficulty.items() if v and k != "Other"),
                key=lambda item: -item[1],
            )[:3]
            if ranked:
                sentences.append(
                    "the most selected difficulties were {t}.".format(
                        t="; ".join(
                            "{k} ({p})".format(k=k.lower(), p=_count_phrase(v, respondents, "respondents"))
                            for k, v in ranked
                        )
                    )
                )
        if remembered and any(word in low for word in ("remember", "date", "clue")):
            people = remembered.get("People")
            when = remembered.get("Rough time / year")
            if people is not None:
                sentences.append("{p} remembered people.".format(p=_count_phrase(people, respondents, "respondents")))
            if when is not None and any(word in low for word in ("date", "time", "when")):
                sentences.append("{p} remembered a rough time or year.".format(
                    p=_count_phrase(when, respondents, "respondents")
                ))
        if sentences:
            parts.append("In the survey, " + " ".join(sentences))
            add_stat("survey")

    if any(word in low for word in ("limitation", "uncertain", "biggest limitation")):
        limits = []
        if targeted:
            limits.append(
                "Targeted vague-memory research uses {a} analysed examples from {c} collected public cases. {note}".format(
                    a=targeted.get("analysed") or 0,
                    c=targeted.get("collected") or 0,
                    note=B.LIMITATION,
                )
            )
            add_stat("corpus_b")
        if survey:
            limits.append("The survey is a convenience sample of {n} responses, not a population estimate.".format(
                n=survey.get("respondents") or 0
            ))
            add_stat("survey")
        if interview:
            limits.append("The interviews are {n} observed retrieval tasks, not a representative user study.".format(
                n=interview.get("observed_tasks") or 0
            ))
            add_stat("interview")
        if limits:
            parts.append(" ".join(limits))

    if not parts and records:
        named = ", ".join(_ids(records)[:8])
        parts.append(
            "The closest retrieved evidence is {ids}. The excerpts below are the research records that matched this question.".format(
                ids=named
            )
        )
    if not parts:
        parts.append(NOT_ENOUGH)
    return " ".join(parts), used


def _result(question, answer, records, stats, sources, mode, limitations="", fallback_note="", error=""):
    used = []
    return {
        "question": question,
        "mode": mode,
        "insufficient_evidence": mode in ("scope", "thin"),
        "answer": answer,
        "citations": _citations_for(records, stats, used),
        "limitations": limitations,
        "records": records or [],
        "sources": sources or [],
        "streams": sorted({row["stream"] for row in records or []}),
        "fallback_note": fallback_note,
        "error": error,
    }


def _evidence_result(question, records, stats, sources, bundle, fallback_note=""):
    answer, used = _fallback_answer(question, records, stats, bundle)
    limitations = ""
    if records or stats:
        limitations = B.LIMITATION
    mode = "evidence" if records or (stats and answer != NOT_ENOUGH) else "thin"
    result = _result(question, answer, records, stats, sources, mode, limitations, fallback_note)
    result["citations"] = _citations_for(records, stats, used)
    labels = {
        "interview": "Interviews",
        "survey": "Survey",
        "corpus_b": "Targeted Vague-Memory Research",
        "corpus_a": "Broad Public Research",
    }
    streams = list(result["streams"])
    for key in used:
        label = labels.get(key)
        if label and label not in streams:
            streams.append(label)
    result["streams"] = streams
    return result


def run_research_query(question, bundle, use_model=True, on_progress=None):
    """One path for suggested questions and typed questions. Does not write files."""
    def progress(label):
        if on_progress:
            on_progress(label)

    question = (question or "").strip()
    if not question:
        return {
            "question": "",
            "mode": "invalid",
            "answer": "",
            "citations": [],
            "records": [],
            "sources": [],
            "streams": [],
            "limitations": "",
            "fallback_note": "",
            "error": "Enter a question.",
            "insufficient_evidence": False,
        }

    progress("Searching the research...")
    if not in_research_scope(question):
        return _result(
            question,
            OUT_OF_SCOPE,
            [],
            {},
            [],
            "scope",
            "The question is outside this project's research.",
        )

    try:
        found = retrieve(question, bundle, limit=TOP_K)
    except Exception:
        found = {"sources": [], "records": [], "theme": False}
    sources = list(found.get("sources") or [])
    records = list(found.get("records") or [])
    low = question.lower()
    if any(word in low for word in ("limitation", "uncertain")):
        for name in ("survey", "interview", "corpus_b"):
            if name not in sources:
                sources.append(name)
    stats = calculated_stats(bundle, sources) if sources else {}
    if not records and not stats:
        return _result(question, NOT_ENOUGH, [], {}, sources, "thin")

    key_ok = False
    if use_model:
        try:
            from src.secrets import get_groq_api_key
            key_ok = bool(get_groq_api_key())
        except Exception:
            key_ok = False
    if key_ok:
        progress("Synthesising evidence...")
        try:
            user = (
                "QUESTION:\n{q}\n\nCALCULATED_STATS (do not recompute):\n{stats}\n\nRECORDS:\n{rows}"
            ).format(
                q=question,
                stats=json.dumps(stats, ensure_ascii=False, indent=2),
                rows=json.dumps(records, ensure_ascii=False, indent=2),
            )
            result = complete_json(_load_prompt(), user)
        except Exception:
            result = None
        if result is not None and result.ok and (result.data or {}).get("answer"):
            enforced = _enforce(question, result.data, records, stats, sources)
            enforced["mode"] = "ai"
            enforced["streams"] = sorted({row["stream"] for row in records})
            enforced["fallback_note"] = ""
            enforced["error"] = ""
            if not enforced.get("limitations"):
                enforced["limitations"] = ""
            return enforced

    return _evidence_result(question, records, stats, sources, bundle, FALLBACK_NOTE)


def answer_question(question, bundle):
    """Backward-compatible wrapper around run_research_query."""
    return run_research_query(question, bundle, use_model=True)
