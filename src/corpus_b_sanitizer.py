"""Deterministic post-audit sanitation for Corpus B (targeted_direct).

Runs after the LLM auditor. It removes values that raw_text does not lexically
support and normalizes fields to controlled vocabularies. The only additive
rule is remembered_association, set when raw_text names an explicit sharing
action or the surface where the target was seen/stored, outside a forgetting clause. Every change is recorded in sanitizer_changes.
"""
import re

from src.schema import FAILURE_STAGES, PHOTO_TYPES, REMEMBERED_FIELDS, WORKAROUNDS

FORGET_MARKERS = (
    "not remember",
    "not remembering",
    "don't remember",
    "doesn't remember",
    "cannot remember",
    "can't remember",
    "can not remember",
    "cannot recall",
    "can't recall",
    "forgot",
    "forgotten",
    "don't know",
    "do not know",
    "does not know",
    "doesn't know",
    "not sure",
    "unsure",
    "no idea",
    "but not",
)

CLAUSE_BREAK = re.compile(r"[.;]| but ")

FORGOTTEN_VOCAB = [
    "date/time",
    "exact date",
    "approximate time",
    "location",
    "venue/name",
    "folder",
    "album",
    "filename",
    "source",
    "notification type",
    "exact wording",
    "title/name",
]

# (category, keys that map an LLM term to the category, raw_text evidence regexes
# that must appear inside a forgetting clause)
FORGOTTEN_RULES = [
    ("filename", ("filename", "file name", "file"), (r"\bfile ?names?\b",)),
    ("notification type", ("notification",), (r"\bnotification",)),
    ("exact wording", ("wording", "exact words", "words"), (r"\bwording\b", r"\bexact words\b")),
    ("folder", ("folder",), (r"\bfolders?\b",)),
    ("album", ("album",), (r"\balbums?\b",)),
    ("source", ("source", "creator"), (r"\bsource\b", r"\bcreator\b")),
    ("title/name", ("title", "name"), (r"\btitle\b", r"(?<!file )\bname\b")),
    ("venue/name", ("venue",), (r"\bvenue\b",)),
    ("exact date", ("exact date", "precise date"), (r"\b(exact|precise) dates?\b",)),
    ("approximate time", ("approximate time",), (r"\bapproximate time\b",)),
    ("date/time", ("date", "time", "when", "year", "day"), (r"\bwhen\b", r"\bdates?\b", r"\byear\b")),
    ("location", ("location", "place", "where"), (r"\bwhere\b(?! the image is stored)", r"\blocation\b", r"\bplace\b")),
]

QUOTE_EVIDENCE = (r"\bquotes\b", r"\bquotation", r"\bquoted\b", r"\bin quotes\b")

VISUAL_EVIDENCE = (
    r"\b(red|green|blue|black|white|yellow|pink|purple|orange|brown|grey|gray)\b",
    r"\bcolou?rs?\b",
    r"\b(sari|dress|shirt|wearing|outfit|clothing|clothes|hat|jacket)\b",
    r"\bbackground\b",
    r"\bappearance\b",
    r"\bpose\b",
    r"\bholding\b",
    r"\bscene\b",
    r"\bvisual style\b",
    r"\bcomposition\b",
    r"\bface\b",
    r"\b\w+-haired\b",
    r"\bhair\b",
    r"\basleep\b",
    r"\bsleeping\b",
    r"\bedge of the photo\b",
    r"\bdistinctive\b",
)

TEXT_EVIDENCE = (
    r"\btext\b",
    r"\bmessage content\b",
    r"\bcaption",
    r"\bwritten\b",
    r"\bwording\b",
    r"\bsign\b",
    r"\blabel\b",
)

ASSOCIATION_ACTION_EVIDENCE = (
    r"\bsent\s+(?:\w+\s+){0,3}?to\b",
    r"\bshared\s+(?:\w+\s+){0,3}?with\b",
    r"\bshowed\s+(?:\w+\s+){0,3}?to\b",
    r"\bconversation with\b",
    r"\bappeared in\b",
)

_SURFACE_NOUN = r"(?P<noun>notifications?|memories|memory|albums?|folders?)"
_SURFACE_FILLER = (
    r"(?:(?:a|an|the|their|my|his|her|our|its|this|that|google|photos|photo|ios|apple|"
    r"iphone|phone|old|older|same|specific|shared|memory)\s+){0,4}"
)

# Surface words count only as the place the target was seen/stored, never as
# the topic or content of the target ("a video about photo memories").
ASSOCIATION_SURFACE_EVIDENCE = (
    r"\b(?:in|into|inside|from|via|through|stored in|saved in|saved to)\s+" + _SURFACE_FILLER + _SURFACE_NOUN + r"\b",
    r"\b" + _SURFACE_NOUN + r"\s+(?:\w+\s+){0,4}?(?:used to\s+)?(?:belong(?:ed)?\s+to|was in|were in)\b",
)

ASSOCIATION_PHRASE_EVIDENCE = (r"\bphrase\b", r"\bsinging\b", r"\bsaid\b", r"\bdialogue\b")

EXPLICIT_NO_REFINEMENT = (
    "did not try",
    "didn't try",
    "never tried",
    "stopped",
    "gave up",
    "only tried",
    "without trying",
    "no further",
    "did not search again",
    "didn't search again",
)

INITIAL_MARKERS = ("first", "initially", "started by", "began by", "starts by")

SEQUENCE_MARKERS = (
    "then ",
    "eventually",
    "instead",
    "resort",
    "fall back",
    "fallback",
    "ended up",
    "switched to",
    "afterward",
)

PLACEHOLDER_STRATEGIES = ("initial attempt", "search attempt", "photos memories search", "initial search")

SCROLL_TERMS = ("scroll", "timeline")


def _any(patterns, text):
    return any(re.search(p, text) for p in patterns)


def forgetting_spans(raw_text):
    low = raw_text.lower()
    spans = []
    for marker in FORGET_MARKERS:
        for match in re.finditer(re.escape(marker), low):
            start = match.end()
            cut = CLAUSE_BREAK.search(low, start)
            spans.append((start, cut.start() if cut else len(low)))
    return spans


def forgetting_clauses(raw_text):
    low = raw_text.lower()
    return [low[s:e] for s, e in forgetting_spans(raw_text)]


def association_evidence(raw_text):
    """First association pattern matched outside any forgetting clause, else None."""
    low = (raw_text or "").lower()
    spans = forgetting_spans(low)

    def _outside(pos):
        return not any(s <= pos < e for s, e in spans)

    for pattern in ASSOCIATION_ACTION_EVIDENCE:
        for match in re.finditer(pattern, low):
            if _outside(match.start()):
                return match.group(0)
    for pattern in ASSOCIATION_SURFACE_EVIDENCE:
        for match in re.finditer(pattern, low):
            if _outside(match.start("noun")):
                return match.group(0)
    return None


def map_forgotten_term(term):
    low = term.lower()
    for category, keys, _ in FORGOTTEN_RULES:
        if any(k in low for k in keys):
            return category
    return None


def forgotten_category_supported(raw_text, category):
    rule = next((r for r in FORGOTTEN_RULES if r[0] == category), None)
    if rule is None:
        return False
    return any(_any(rule[2], clause) for clause in forgetting_clauses(raw_text))


def split_forgotten(value):
    parts = re.split(r"[;,]| and | or ", (value or "").lower())
    out = []
    for part in parts:
        part = part.strip()
        if not part or part == "unknown":
            continue
        if "/" in part and part not in FORGOTTEN_VOCAB:
            out.extend(p.strip() for p in part.split("/") if p.strip())
        else:
            out.append(part)
    return out


def sanitize_forgotten(raw_text, value):
    kept = []
    for term in split_forgotten(value):
        category = map_forgotten_term(term)
        if category and forgotten_category_supported(raw_text, category) and category not in kept:
            kept.append(category)
    if "exact date" in kept and "date/time" in kept:
        kept.remove("date/time")
    return "; ".join(kept) if kept else "unknown"


def has_quote_evidence(raw_text):
    return _any(QUOTE_EVIDENCE, raw_text.lower())


def has_visual_evidence(raw_text):
    return _any(VISUAL_EVIDENCE, raw_text.lower())


def has_text_evidence(raw_text):
    return _any(TEXT_EVIDENCE, raw_text.lower())


def has_explicit_no_refinement(raw_text):
    low = raw_text.lower()
    return any(m in low for m in EXPLICIT_NO_REFINEMENT)


def has_sequence_evidence(raw_text):
    low = raw_text.lower()
    return any(m in low for m in SEQUENCE_MARKERS)


def is_placeholder_strategy(strategy):
    low = (strategy or "").lower().strip(" .")
    return any(p in low for p in PLACEHOLDER_STRATEGIES)


def strategy_matches_workaround(strategy, workaround):
    low = (strategy or "").lower()
    if low in ("", "unknown") or workaround in ("", "unknown", "none_mentioned"):
        return False
    if low.replace(" ", "_") == workaround:
        return True
    if workaround == "timeline_scrolling" and any(t in low for t in SCROLL_TERMS):
        return True
    tokens = [t for t in workaround.split("_") if len(t) > 3]
    return bool(tokens) and any(t in low for t in tokens)


def deterministic_warning(fields):
    warnings = []
    if fields.get("photo_type") in ("unknown", "other"):
        warnings.append("target type unclear")
    if fields.get("failure_stage") == "other_unclear":
        warnings.append("failure stage unclear")
    if fields.get("search_strategy") in ("unknown", ""):
        warnings.append("search behaviour not stated")
    if fields.get("forgotten_information") in ("unknown", ""):
        warnings.append("memory gap not explicitly specified")
    return "; ".join(warnings) if warnings else "none"


def sanitize_record(raw_text, fields):
    """Return (sanitized_fields, changes). Does not mutate the input."""
    out = dict(fields)
    changes = []
    low = (raw_text or "").lower()

    def _set(field, value, reason):
        if out.get(field) != value:
            changes.append("{}: {} -> {} ({})".format(field, out.get(field), value, reason))
            out[field] = value

    for field in REMEMBERED_FIELDS:
        if out.get(field) != "true":
            out[field] = "false"

    if out.get("failure_stage") not in FAILURE_STAGES:
        _set("failure_stage", "other_unclear", "invalid stage value")
    if out.get("photo_type") not in PHOTO_TYPES:
        _set("photo_type", "unknown", "invalid photo_type value")
    if out.get("workaround") not in WORKAROUNDS:
        _set("workaround", "unknown", "invalid workaround value")

    _set(
        "forgotten_information",
        sanitize_forgotten(raw_text, out.get("forgotten_information", "unknown")),
        "kept only explicitly forgotten concepts",
    )

    strategy = out.get("search_strategy", "unknown") or "unknown"
    if is_placeholder_strategy(strategy):
        _set("search_strategy", "unknown", "placeholder strategy")
    elif "quote" in strategy.lower() and not has_quote_evidence(raw_text):
        if re.search(r"\bphrase\b", low):
            _set("search_strategy", "searched_remembered_phrase", "no quote evidence; phrase search stated")
        else:
            _set("search_strategy", "unknown", "no quote evidence")

    if out.get("workaround") == "quoted_text_search" and not has_quote_evidence(raw_text):
        _set("workaround", "unknown", "no quote evidence")

    strategy = out.get("search_strategy", "unknown")
    explicit_initial = any(m in low for m in INITIAL_MARKERS)
    if any(t in strategy.lower() for t in SCROLL_TERMS) and not explicit_initial:
        if out.get("workaround") in ("unknown", "none_mentioned", "timeline_scrolling"):
            _set("workaround", "timeline_scrolling", "scrolling follows retrieval difficulty")
            _set("search_strategy", "unknown", "scrolling is a fallback, not the initial strategy")
    elif strategy_matches_workaround(strategy, out.get("workaround", "")):
        if not has_sequence_evidence(raw_text):
            _set("search_strategy", "unknown", "same action as workaround without sequence evidence")

    if out.get("refinement_attempt") == "no" and not has_explicit_no_refinement(raw_text):
        _set("refinement_attempt", "unknown", "silence is not 'no'")

    if out.get("remembered_visual") == "true" and not has_visual_evidence(raw_text):
        _set("remembered_visual", "false", "no explicit visual characteristic")

    if out.get("remembered_text") == "true" and not has_text_evidence(raw_text):
        _set("remembered_text", "false", "no text in the target visual")
        if _any(ASSOCIATION_PHRASE_EVIDENCE, low):
            _set("remembered_association", "true", "spoken/contextual phrase is an association")

    if out.get("remembered_association") != "true":
        evidence = association_evidence(raw_text)
        if evidence:
            _set("remembered_association", "true", "added: explicit '{}' context in raw_text".format(evidence))

    out["extraction_warning"] = deterministic_warning(out)
    out["sanitizer_changes"] = " | ".join(changes) if changes else "none"
    return out, changes
