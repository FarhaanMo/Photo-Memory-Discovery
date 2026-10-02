import re

# Phrase list is the scan definition. Longer phrases are tested first.
MEMORY_PHRASES = [
    "cannot remember the name",
    "don't know the date",
    "don't know where",
    "don't know the name",
    "trying to find an old photo",
    "picture from years ago",
    "looking for a photo of",
    "trying to locate a picture",
    "vaguely remember",
    "cannot remember",
    "can't remember",
    "don't remember",
    "can't recall",
    "not sure when",
    "not sure where",
    "I think it was",
    "around the time",
    "know I have",
    "know it exists",
    "remember a photo",
    "remember that",
    "all I remember",
    "only remember",
    "during a trip",
    "when we went",
    "when I was",
    "sent it to",
    "took it because",
    "saved it because",
    "somewhere",
    "sometime",
    "roughly",
    "forgot",
    "forget",
    "maybe",
    "after",
    "before",
]


def _compile_patterns():
    compiled = []
    for phrase in MEMORY_PHRASES:
        escaped = re.escape(phrase)
        if " " in phrase or "'" in phrase:
            pattern = re.compile(escaped, re.IGNORECASE)
        else:
            pattern = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)
        compiled.append((phrase, pattern))
    return compiled


_PATTERNS = _compile_patterns()


def matched_terms(raw_text):
    text = raw_text if raw_text is not None else ""
    hits = []
    seen = set()
    for phrase, pattern in _PATTERNS:
        if phrase in seen:
            continue
        if pattern.search(text):
            hits.append(phrase)
            seen.add(phrase)
    return hits


def scan_record(raw_text):
    hits = matched_terms(raw_text)
    return bool(hits), hits
