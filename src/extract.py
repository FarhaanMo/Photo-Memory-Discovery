from src.config import (
    GROQ_STRUCTURED_MAX_COMPLETION_TOKENS,
    GROQ_STRUCTURED_REASONING_EFFORT,
    PROJECT_ROOT,
)
from src.llm_client import complete_json
from src.relevance import prepare_text_for_llm
from src.schema import SchemaError, validate_extraction_payload


def _load_prompt():
    path = PROJECT_ROOT / "prompts" / "extract.md"
    return path.read_text(encoding="utf-8")


def extract_record(record_id, raw_text, source="", platform=""):
    excerpt, truncated = prepare_text_for_llm(raw_text)
    user = (
        "record_id: {rid}\n"
        "source: {source}\n"
        "platform: {platform}\n"
        "raw_text:\n{text}"
    ).format(
        rid=record_id,
        source=source or "unknown",
        platform=platform or "Google Photos",
        text=excerpt,
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
        result.data = validate_extraction_payload(result.data, record_id)
    except SchemaError as exc:
        result.ok = False
        result.error = str(exc)
        result.data = None
    return result, truncated
