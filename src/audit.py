import json

from src.config import (
    GROQ_STRUCTURED_MAX_COMPLETION_TOKENS,
    GROQ_STRUCTURED_REASONING_EFFORT,
    PROJECT_ROOT,
)
from src.llm_client import complete_json
from src.relevance import prepare_text_for_llm
from src.schema import (
    REMEMBERED_FIELDS,
    SchemaError,
    stringify_optional,
    validate_extraction_payload,
)

FIRST_PASS_FIELDS = [
    "photo_type",
] + REMEMBERED_FIELDS + [
    "remembered_clues_detail",
    "forgotten_information",
    "search_strategy",
    "failure_stage",
    "failure_stage_reason",
    "refinement_attempt",
    "workaround",
    "retrieval_outcome",
    "problem_theme",
    "evidence_strength",
    "extraction_warning",
    "extraction_notes",
]


def _load_prompt():
    path = PROJECT_ROOT / "prompts" / "audit.md"
    return path.read_text(encoding="utf-8")


def audit_record(record_id, raw_text, platform, first_pass):
    """Second-pass audit of a first-pass extraction (Corpus B only).

    Returns (LLMResult, truncated). On success, result.data is the corrected,
    schema-validated extraction plus audit_note.
    """
    excerpt, truncated = prepare_text_for_llm(raw_text)
    first = {"record_id": record_id}
    first.update({k: first_pass.get(k, "unknown") for k in FIRST_PASS_FIELDS})
    user = (
        "record_id: {rid}\n"
        "platform: {platform}\n"
        "raw_text:\n{text}\n\n"
        "first_pass:\n{first}"
    ).format(
        rid=record_id,
        platform=platform or "unknown",
        text=excerpt,
        first=json.dumps(first, ensure_ascii=False, indent=2),
    )
    result = complete_json(
        _load_prompt(),
        user,
        max_completion_tokens=GROQ_STRUCTURED_MAX_COMPLETION_TOKENS,
        reasoning_effort=GROQ_STRUCTURED_REASONING_EFFORT,
    )
    if not result.ok:
        return result, truncated
    try:
        data = validate_extraction_payload(result.data, record_id)
        for field in REMEMBERED_FIELDS:
            if data[field] != "true":
                data[field] = "false"
        note = stringify_optional(result.data.get("audit_note"))
        data["audit_note"] = "no correction required" if note == "unknown" else note
        result.data = data
    except SchemaError as exc:
        result.ok = False
        result.error = "Audit: {}".format(exc)
        result.data = None
    return result, truncated
