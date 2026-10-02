"""Deterministic survey analytics (primary research). Read-only on the raw file.

Multi-select answers are parsed by matching the known option labels, because
one option label itself contains a comma.
"""
from collections import OrderedDict

import pandas as pd

from src.config import resolve_survey_csv_path

QUESTIONS = OrderedDict([
    ("timestamp", "Timestamp"),
    ("usage", "How often do you use Google Photos?"),
    ("tenure", "How long have you been using Google Photos?"),
    ("retrieval_frequency", "How often do you try to find a specific photo or image from the past?"),
    ("screening", "Have you ever known that a particular photo existed in Google Photos"),
    ("remembered", "What did you remember about the photo"),
    ("methods", "What did you do first to try to find it?"),
    ("difficulty", "What made the photo difficult to find?"),
    ("outcome", "Did you eventually find the photo?"),
    ("open_text", "Briefly describe the photo"),
    ("followup", "Would you be willing to do a 5"),
])

USAGE_ORDER = ["Daily", "A few times a week", "Rarely"]
TENURE_ORDER = ["Less than 1 Year", "1-2 Years", "3-5 Years", "More than 5 Years"]
RETRIEVAL_FREQUENCY_ORDER = ["Several times a week", "A few times a month", "A few times a year", "Very rarely"]
SCREENING_ORDER = ["Yes, several times", "Yes, once or twice", "No, I don't remember"]
SCREENING_NO = "No, I don't remember"
FOLLOWUP_ORDER = ["Yes", "No"]

# (raw option label, display label)
REMEMBERED_OPTIONS = [
    ("Person / People in it", "People"),
    ("Rough time or year", "Rough time / year"),
    ("Rough location", "Rough location"),
    ("An object / item in the photo", "Object / item"),
    ("The event or occasion", "Event / occasion"),
    ("What happened before / after the photo", "Before / after context"),
    ("How the photo looked ( indoor / outdoor , day / night )", "Visual appearance"),
    ("I remember very little", "Remember very little"),
    ("Something else", "Other"),
]

METHOD_OPTIONS = [
    ("Typed something into Google Photos search", "Typed into search"),
    ("Scrolled through my photo timeline", "Scrolled timeline"),
    ("Used People & Pets", "People & Pets"),
    ("Used Places / Maps", "Places / Maps"),
    ("Checked Albums / Folders", "Albums / Folders"),
    ("Looked through Screenshots / Documents", "Screenshots / Documents"),
    ("Something else", "Other"),
]

DIFFICULTY_OPTIONS = [
    ("I didn't know what words to search", "Didn't know what words to search"),
    ("I couldn't remember when and where it was taken", "Couldn't remember when / where"),
    ("Search results were not relevant", "Search results not relevant"),
    ("There were too many similar photos", "Too many similar photos"),
    ("I didn't know how to improve / refine my search", "Didn't know how to refine"),
    ("I ended up scrolling manually", "Ended up scrolling manually"),
    ("Something else", "Other"),
]

# Raw labels kept as collected (including the source typo "bowsing").
OUTCOME_OPTIONS = [
    ("Yes, quickly", "Yes, quickly"),
    ("Yes, but only after several attempts", "Yes, after several attempts"),
    ("Yes, after manually scrolling / bowsing", "Yes, after manual scrolling / browsing"),
    ("I gave up", "Gave up"),
]

METHODS_LABEL = "Retrieval methods attempted"
METHODS_NOTE = (
    "Because respondents could select multiple options, this question cannot "
    "establish sequence or the true first retrieval action."
)


def _norm(text):
    return str(text or "").replace("\u2019", "'").replace("\u2018", "'").strip()


def _find_column(columns, fragment):
    for col in columns:
        if _norm(fragment) in _norm(col):
            return col
    return None


def load_survey(path=None):
    """Return (df with short column keys + respondent_id, column_map). Raw file untouched."""
    target = path or resolve_survey_csv_path()
    if target is None:
        return None, {}
    raw = pd.read_csv(target, dtype=str, keep_default_na=False, na_filter=False, encoding="utf-8-sig")
    column_map = {}
    for key, prefix in QUESTIONS.items():
        col = _find_column(raw.columns, prefix)
        if col is not None:
            column_map[key] = col
    df = pd.DataFrame({key: raw[col].map(_norm) for key, col in column_map.items()})
    df.insert(0, "respondent_id", ["S{:02d}".format(i + 1) for i in range(len(df))])
    return df, column_map


def single_select_counts(series, order):
    counts = series.value_counts()
    out = OrderedDict((label, int(counts.get(label, 0))) for label in order)
    for label, value in counts.items():
        if label not in out and label != "":
            out[label] = int(value)
    return out


def parse_multi(cell, options):
    """Return (selected display labels, unrecognised leftover text)."""
    text = _norm(cell)
    selected = []
    for raw_label, display in sorted(options, key=lambda o: -len(o[0])):
        if raw_label in text:
            selected.append(display)
            text = text.replace(raw_label, "")
    leftover = text.replace(",", " ").strip()
    order = [d for _, d in options]
    selected.sort(key=order.index)
    return selected, leftover


def multi_select_counts(series, options):
    counts = OrderedDict((display, 0) for _, display in options)
    for cell in series:
        selected, _ = parse_multi(cell, options)
        for label in selected:
            counts[label] += 1
    return counts


def outcome_counts(series):
    counts = OrderedDict((display, 0) for _, display in OUTCOME_OPTIONS)
    lookup = {raw: display for raw, display in OUTCOME_OPTIONS}
    for cell in series:
        if cell in lookup:
            counts[lookup[cell]] += 1
    return counts


def screened_out_ids(df):
    return df.loc[df["screening"] == SCREENING_NO, "respondent_id"].tolist()


def summary(df):
    return OrderedDict([
        ("usage", single_select_counts(df["usage"], USAGE_ORDER)),
        ("tenure", single_select_counts(df["tenure"], TENURE_ORDER)),
        ("retrieval_frequency", single_select_counts(df["retrieval_frequency"], RETRIEVAL_FREQUENCY_ORDER)),
        ("screening", single_select_counts(df["screening"], SCREENING_ORDER)),
        ("remembered", multi_select_counts(df["remembered"], REMEMBERED_OPTIONS)),
        ("methods", multi_select_counts(df["methods"], METHOD_OPTIONS)),
        ("difficulty", multi_select_counts(df["difficulty"], DIFFICULTY_OPTIONS)),
        ("outcome", outcome_counts(df["outcome"])),
        ("followup", single_select_counts(df["followup"], FOLLOWUP_ORDER)),
    ])


def open_text_responses(df):
    rows = df[df["open_text"] != ""]
    return rows[["respondent_id", "open_text"]].reset_index(drop=True)


def quality_warnings(df):
    """Deterministic data-quality notes. Nothing is deleted or deduplicated."""
    notes = []
    n = len(df)
    notes.append("n = {} responses; convenience / directional sample, not representative of all Google Photos users.".format(n))

    exact_dupes = int(df.drop(columns=["respondent_id"]).duplicated().sum())
    notes.append("Exact duplicate rows: {} (no rows removed).".format(exact_dupes))

    out = screened_out_ids(df)
    downstream = ["remembered", "methods", "difficulty", "outcome"]
    answered = [rid for rid in out if (df.loc[df["respondent_id"] == rid, downstream] != "").any(axis=1).iloc[0]]
    if out:
        notes.append(
            "{} respondent(s) ({}) selected \"No, I don't remember\" on the screening question "
            "but still answered downstream retrieval questions ({} of them). Their answers are "
            "kept and included by default; this screening inconsistency is documented, not silently discarded.".format(
                len(out), ", ".join(out), len(answered)
            )
        )

    notes.append("The \"What did you do first?\" question allowed multiple selections, so order cannot be inferred. " + METHODS_NOTE)

    texts = df.loc[df["open_text"] != "", "open_text"]
    notes.append("Open-text responses are sparse: {} of {} respondents answered the optional description.".format(len(texts), n))
    repeated = texts[texts.duplicated(keep=False)]
    if not repeated.empty:
        ids = df.loc[repeated.index, "respondent_id"].tolist()
        notes.append(
            "Identical open-text answers from {} (rows differ elsewhere, so they are not exact duplicates and are kept).".format(", ".join(ids))
        )
    if texts.str.contains("\ufffd").any():
        notes.append("Some open-text contains an unreadable character (\ufffd) from the export encoding; text is shown as collected.")

    for key, options in (("remembered", REMEMBERED_OPTIONS), ("methods", METHOD_OPTIONS), ("difficulty", DIFFICULTY_OPTIONS)):
        leftovers = [(rid, parse_multi(cell, options)[1]) for rid, cell in zip(df["respondent_id"], df[key])]
        leftovers = [(rid, text) for rid, text in leftovers if text]
        if leftovers:
            notes.append("Unrecognised {} answer text: {}.".format(key, leftovers))

    notes.append("Counts are descriptive only; no statistical significance is inferred.")
    return notes
