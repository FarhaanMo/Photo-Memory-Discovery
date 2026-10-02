"""Deterministic analytics for researcher-observed retrieval interviews.

Counts describe the completed observed tasks only; never population percentages.
"""
from collections import OrderedDict

import pandas as pd

from src.config import INTERVIEW_CSV_PATH
from src.schema import FAILURE_STAGES, REMEMBERED_FIELDS

PREFIX = "Across the {n} observed retrieval tasks"

# Interviews only. Corpus B keeps the five-stage taxonomy in schema.FAILURE_STAGES.
INTERVIEW_STAGES = FAILURE_STAGES + ["no_failure"]
STAGE_LABELS = OrderedDict([
    ("expression", "Expression"),
    ("retrieval", "Retrieval"),
    ("evaluation", "Evaluation"),
    ("recovery", "Recovery"),
    ("other_unclear", "Other / unclear"),
    ("no_failure", "No failure"),
])

INTERVIEW_COLUMNS = (
    [
        "participant_id",
        "participant_name",
        "target_description",
        "remembered_before_retrieval",
        "observed_sequence",
    ]
    + REMEMBERED_FIELDS
    + [
        "first_observed_action",
        "first_query",
        "first_result_quality",
        "new_memory_triggered_by_results",
        "refinement_attempted",
        "refinement_description",
        "fallback_or_workaround",
        "manual_scrolling",
        "failure_stage_observed",
        "failure_stage_reason",
        "retrieval_outcome",
        "time_to_target_minutes",
        "time_is_approximate",
        "attempts_to_target",
        "hardest_moment_quote",
        "researcher_observation",
    ]
)

CLUE_DISPLAY = OrderedDict((f, f.replace("remembered_", "").capitalize()) for f in REMEMBERED_FIELDS)


def load_interviews(path=None):
    target = path or INTERVIEW_CSV_PATH
    if not target.is_file() or target.stat().st_size == 0:
        return pd.DataFrame(columns=INTERVIEW_COLUMNS)
    return pd.read_csv(target, dtype=str, keep_default_na=False, na_filter=False, encoding="utf-8-sig")


def prefix(df):
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
    return PREFIX.format(n=words.get(len(df), len(df)))


def stage_counts(df):
    counts = df["failure_stage_observed"].value_counts()
    out = OrderedDict((STAGE_LABELS[s], int(counts.get(s, 0))) for s in INTERVIEW_STAGES)
    for key, value in counts.items():
        if key not in INTERVIEW_STAGES:
            out[key] = int(value)
    return out


def clue_counts(df):
    return OrderedDict((label, int((df[field] == "true").sum())) for field, label in CLUE_DISPLAY.items())


def clues_per_participant(df):
    return OrderedDict(
        (row["participant_id"], int(sum(row[f] == "true" for f in REMEMBERED_FIELDS))) for _, row in df.iterrows()
    )


def yes_count(df, column):
    return int((df[column] == "yes").sum())


def outcome_counts(df):
    return OrderedDict((k, int(v)) for k, v in df["retrieval_outcome"].value_counts().items())


def times(df):
    return OrderedDict((row["participant_id"], float(row["time_to_target_minutes"]))
                       for _, row in df.iterrows() if row["time_to_target_minutes"] not in ("", "unknown"))


def median_time(df):
    values = list(times(df).values())
    return float(pd.Series(values).median()) if values else None


def summary(df):
    return OrderedDict([
        ("interviews", len(df)),
        ("stages", stage_counts(df)),
        ("clues", clue_counts(df)),
        ("refined", yes_count(df, "refinement_attempted")),
        ("manual_scrolling", yes_count(df, "manual_scrolling")),
        ("outcomes", outcome_counts(df)),
        ("times", times(df)),
        ("median_time", median_time(df)),
    ])


def unknown_clues(df):
    """Clues coded unknown, so they are neither remembered nor forgotten."""
    found = []
    for _, row in df.iterrows():
        fields = [CLUE_DISPLAY[f] for f in REMEMBERED_FIELDS if row[f] == "unknown"]
        if fields:
            found.append((row["participant_id"], fields))
    return found


def recurring_observations(df):
    """Behavioural patterns computed from coded fields. Not a root-cause statement."""
    n = len(df)
    if n == 0:
        return []
    out = []

    def share(k):
        return "all {}".format(n) if k == n else "{} of {}".format(k, n)

    searched = df[df["first_observed_action"] == "search"]
    one_term = searched[searched["first_query"].str.split().str.len() == 1]
    richer = [
        row["participant_id"] for _, row in one_term.iterrows()
        if sum(row[f] == "true" for f in REMEMBERED_FIELDS) > 1
    ]
    if len(searched):
        out.append(
            "{} of {} tasks began with a typed search. Of those, {} used a single-term first query "
            "({}) while more than one clue was coded, so the first query did not carry all the "
            "remembered context.".format(
                len(searched), n, len(richer),
                ", ".join("{} \"{}\"".format(r["participant_id"], r["first_query"]) for _, r in one_term.iterrows()),
            )
        )

    noisy = df[df["first_result_quality"].str.contains("broad|noisy|too many|irrelevant", case=False)]
    if len(noisy):
        out.append(
            "The first result set was broad, noisy, or too crowded for {}: {}.".format(
                ", ".join(noisy["participant_id"]),
                "; ".join("{} ({})".format(r["participant_id"], r["first_result_quality"]) for _, r in noisy.iterrows()),
            )
        )

    crowded = df[
        (df["failure_stage_observed"] == "evaluation")
        | df["first_result_quality"].str.contains("too many|similar", case=False)
    ]
    noted = df[
        df["researcher_observation"].str.contains("evaluation", case=False)
        & ~df["participant_id"].isin(crowded["participant_id"] if len(crowded) else [])
    ]
    if len(crowded) or len(noted):
        extra = ""
        if len(noted):
            extra = " Researcher notes for {} also describe later difficulty telling the target apart from other photos of the same event.".format(
                ", ".join(noted["participant_id"])
            )
        out.append(
            "Difficulty picking one target out of many similar or plausible images is recorded for {}.{}".format(
                ", ".join(crowded["participant_id"].tolist()) if len(crowded) else "none of the coded stages",
                extra,
            )
        )

    refined = df[df["refinement_attempted"] == "yes"]
    not_refined = df[df["refinement_attempted"] == "no"]["participant_id"].tolist()
    out.append("{} tasks included a refinement ({}){}.".format(
        share(len(refined)).capitalize(),
        "; ".join("{}: {}".format(r["participant_id"], r["refinement_description"]) for _, r in refined.iterrows()),
        "; {} did not refine".format(", ".join(not_refined)) if not_refined else "",
    ))

    scrolled = df[df["manual_scrolling"] == "yes"]
    intended = scrolled[scrolled["fallback_or_workaround"].isin(["none", ""])]["participant_id"].tolist()
    out.append(
        "Manual scrolling occurred in {} tasks. Where a fallback is coded it is {}; {}.".format(
            share(len(scrolled)),
            ", ".join("{}: {}".format(r["participant_id"], r["fallback_or_workaround"])
                      for _, r in scrolled.iterrows() if r["fallback_or_workaround"] not in ("none", "")),
            "{} used scrolling as the intended method, not as a fallback after failure".format(", ".join(intended))
            if intended else "none of these are coded as the intended method",
        )
    )

    easy = df[df["failure_stage_observed"] == "no_failure"]
    if len(easy):
        out.append(
            "{} {} coded no_failure: a strong enough temporal or event memory, used directly through "
            "chronological navigation, retrieved the target without a failed query or a recovery attempt "
            "({}). This is counter-evidence and is not forced into a problem stage.".format(
                ", ".join(easy["participant_id"]),
                "is" if len(easy) == 1 else "are",
                "; ".join("{}: {} min, {} attempt(s), first action {}".format(
                    r["participant_id"], r["time_to_target_minutes"], r["attempts_to_target"], r["first_observed_action"]
                ) for _, r in easy.iterrows()),
            )
        )

    stages = [(label, count) for label, count in stage_counts(df).items() if count]
    out.append(
        "The coded stage is not the same across tasks ({}), so difficulty is not only query formulation.".format(
            ", ".join("{} {}".format(c, s.lower()) for s, c in stages)
        )
    )
    return out
