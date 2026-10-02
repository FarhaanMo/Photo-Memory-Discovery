from pathlib import Path

from src.config import MAX_CHARS_TO_LLM, PROJECT_ROOT
from src.llm_client import complete_json
from src.schema import SchemaError, validate_relevance_payload


def _load_prompt():
    path = PROJECT_ROOT / "prompts" / "relevance.md"
    return path.read_text(encoding="utf-8")


def prepare_text_for_llm(raw_text):
    text = raw_text if raw_text is not None else ""
    if len(text) <= MAX_CHARS_TO_LLM:
        return text, False
    half = MAX_CHARS_TO_LLM // 2
    clipped = text[:half] + "\n...\n" + text[-half:]
    return clipped, True


def classify_relevance(record_id, raw_text, source=""):
    excerpt, truncated = prepare_text_for_llm(raw_text)
    user = (
        "record_id: {rid}\n"
        "source: {source}\n"
        "raw_text:\n{text}"
    ).format(rid=record_id, source=source or "unknown", text=excerpt)
    result = complete_json(_load_prompt(), user)
    if not result.ok:
        return result, truncated
    try:
        result.data = validate_relevance_payload(result.data, record_id)
    except SchemaError as exc:
        result.ok = False
        result.error = str(exc)
        result.data = None
    return result, truncated
