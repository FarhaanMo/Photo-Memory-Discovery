import json
from typing import List

REQUIRED_COLUMNS: List[str] = [
    "record_id",
    "source",
    "date",
    "url",
    "raw_text",
]

INGEST_MISSING_COLUMNS = "missing_columns"
INGEST_UNEXPECTED_COLUMNS = "unexpected_columns"
INGEST_DUPLICATE_RECORD_ID = "duplicate_record_id"
INGEST_EMPTY_FILE = "empty_file"
INGEST_UNREADABLE = "unreadable_csv"
INGEST_INVALID_SAMPLING_FRAME = "invalid_sampling_frame"
INGEST_MISSING_TEXT_MODE = "missing_text_mode"

SAMPLING_FRAME_BROAD = "broad"
SAMPLING_FRAME_TARGETED = "targeted_direct"

TARGETED_COLUMNS: List[str] = [
    "record_id",
    "sampling_frame",
    "source",
    "platform",
    "date",
    "url",
    "raw_text",
    "text_mode",
    "inclusion_reason",
]

RELEVANCE_TRUE = "true"
RELEVANCE_FALSE = "false"
RELEVANCE_UNCLEAR = "unclear"

RELEVANCE_LEVELS = [
    "direct_vague_retrieval",
    "retrieval_adjacent",
    "irrelevant",
]

RELEVANCE_LEVEL_ALIASES = {
    "direct_vague_retrieval": "direct_vague_retrieval",
    "direct": "direct_vague_retrieval",
    "vague": "direct_vague_retrieval",
    "retrieval_adjacent": "retrieval_adjacent",
    "adjacent": "retrieval_adjacent",
    "irrelevant": "irrelevant",
}

FAILURE_STAGES = [
    "expression",
    "retrieval",
    "evaluation",
    "recovery",
    "other_unclear",
]

FAILURE_STAGE_ALIASES = {
    "expression": "expression",
    "expression_failure": "expression",
    "retrieval": "retrieval",
    "retrieval_interpretation_failure": "retrieval",
    "retrieval / interpretation failure": "retrieval",
    "evaluation": "evaluation",
    "evaluation_failure": "evaluation",
    "recovery": "recovery",
    "recovery_refinement_failure": "recovery",
    "recovery / refinement failure": "recovery",
    "other": "other_unclear",
    "other_unclear": "other_unclear",
    "unclear": "other_unclear",
    "unknown": "other_unclear",
}

WORKAROUNDS = [
    "classic_search",
    "disabled_ask_photos_or_gemini",
    "quoted_text_search",
    "timeline_scrolling",
    "albums",
    "people_pets",
    "places_maps",
    "reformulated_query",
    "added_descriptions_metadata",
    "another_application",
    "asking_another_person",
    "folder_browsing",
    "giving_up",
    "unknown",
    "none_mentioned",
]

WORKAROUND_ALIASES = {
    "classic_search": "classic_search",
    "switched_to_classic_search": "classic_search",
    "classic": "classic_search",
    "disabled_ask_photos_or_gemini": "disabled_ask_photos_or_gemini",
    "disabled_gemini": "disabled_ask_photos_or_gemini",
    "disabled_ask_photos": "disabled_ask_photos_or_gemini",
    "quoted_text_search": "quoted_text_search",
    "quoted_text": "quoted_text_search",
    "reformulated_query": "reformulated_query",
    "reformulate": "reformulated_query",
    "added_descriptions_metadata": "added_descriptions_metadata",
    "added_descriptions": "added_descriptions_metadata",
    "timeline_scrolling": "timeline_scrolling",
    "timeline": "timeline_scrolling",
    "manual_scrolling": "timeline_scrolling",
    "scrolling": "timeline_scrolling",
    "folder_browsing": "folder_browsing",
    "checked_albums": "albums",
    "checked_another_device_or_app": "another_application",
    "asked_another_person": "asking_another_person",
}

PHOTO_TYPES = [
    "people_or_pet",
    "travel_or_place",
    "food_or_restaurant",
    "screenshot",
    "document_or_receipt",
    "object_or_product",
    "event",
    "landscape",
    "other",
    "unknown",
]

PHOTO_TYPE_ALIASES = {
    "people": "people_or_pet",
    "person": "people_or_pet",
    "pet": "people_or_pet",
    "people_or_pet": "people_or_pet",
    "travel": "travel_or_place",
    "place": "travel_or_place",
    "travel_or_place": "travel_or_place",
    "food": "food_or_restaurant",
    "restaurant": "food_or_restaurant",
    "food_or_restaurant": "food_or_restaurant",
    "screenshot": "screenshot",
    "document": "document_or_receipt",
    "receipt": "document_or_receipt",
    "document_or_receipt": "document_or_receipt",
    "object": "object_or_product",
    "product": "object_or_product",
    "object_or_product": "object_or_product",
    "sega_saturn": "object_or_product",
    "saturn": "object_or_product",
    "event": "event",
    "landscape": "landscape",
    "other": "other",
    "unknown": "unknown",
}

_FORBIDDEN_FORGOTTEN_MARKERS = (
    "result",
    "random",
    "error",
    "fail",
    "limitation",
    "engine",
    "gemini",
    "ask photos",
    "returns",
    "returned",
    "wrong photo",
    "search does",
)

OUTCOMES = ["found", "partial", "not_found", "gave_up", "unclear"]
OUTCOME_ALIASES = {"abandoned": "gave_up", "giving_up": "gave_up", "notfound": "not_found"}

_PLACEHOLDER_STRATEGIES = (
    "initial attempt",
    "search attempt",
    "photos memories search",
    "initial search",
)
CONFIDENCE = ["high", "medium", "low", "unclear"]
EVIDENCE_STRENGTH = ["strong", "moderate", "weak", "unclear"]
REFINEMENT = ["yes", "no", "unknown"]
TRI_STATE = ["true", "false", "unknown"]

REMEMBERED_FIELDS = [
    "remembered_people",
    "remembered_time",
    "remembered_place",
    "remembered_object",
    "remembered_text",
    "remembered_event",
    "remembered_purpose",
    "remembered_sequence",
    "remembered_association",
    "remembered_visual",
]

EXTRACTION_TEXT_FIELDS = [
    "photo_type",
    "forgotten_information",
    "search_strategy",
    "workaround",
    "retrieval_outcome",
    "problem_theme",
    "evidence_strength",
    "extraction_notes",
    "remembered_clues_detail",
]

AI_COLUMNS = (
    [
        "processing_status",
        "processing_error",
        "classified_at",
        "model_name",
        "prompt_version",
        "text_truncated_for_llm",
        "relevant_to_retrieval",
        "relevance_level",
        "relevance_reason",
        "relevance_confidence",
        "photo_type",
    ]
    + REMEMBERED_FIELDS
    + [
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
        "audit_note",
        "sanitizer_changes",
    ]
)


class IngestError(Exception):
    def __init__(self, code, message, details=None):
        super(IngestError, self).__init__(message)
        self.code = code
        self.message = message
        self.details = details if details is not None else {}


class SchemaError(Exception):
    pass


def _norm(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def coerce_enum(value, allowed, default="unknown", aliases=None):
    text = _norm(value).lower().replace(" ", "_").replace("-", "_")
    if aliases and text in aliases:
        text = aliases[text]
    if text in allowed:
        return text
    return default


def coerce_tri_state(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    text = _norm(value).lower()
    if text in ("true", "yes", "1"):
        return "true"
    if text in ("false", "no", "0"):
        return "false"
    if text in ("unknown", "unclear", ""):
        return "unknown"
    return "unknown"


def coerce_relevance(value):
    if isinstance(value, bool):
        return RELEVANCE_TRUE if value else RELEVANCE_FALSE
    text = _norm(value).lower()
    if text in ("true", "yes", "1", "relevant"):
        return RELEVANCE_TRUE
    if text in ("false", "no", "0", "irrelevant"):
        return RELEVANCE_FALSE
    return RELEVANCE_UNCLEAR


def coerce_relevance_level(value):
    return coerce_enum(
        value, RELEVANCE_LEVELS, "irrelevant", RELEVANCE_LEVEL_ALIASES
    )


def relevant_flag_from_level(level):
    if level in ("direct_vague_retrieval", "retrieval_adjacent"):
        return RELEVANCE_TRUE
    return RELEVANCE_FALSE


TRIAGE_CONFIDENCE = ["high", "medium", "low"]


def validate_triage_item(payload, expected_record_id):
    if not isinstance(payload, dict):
        raise SchemaError("Triage payload must be an object.")
    returned_id = _norm(payload.get("record_id"))
    if returned_id != _norm(expected_record_id):
        raise SchemaError("record_id mismatch.")
    if "relevance_level" not in payload:
        raise SchemaError("Missing relevance_level.")
    reason = stringify_optional(payload.get("triage_reason"))
    if reason == "unknown":
        reason = ""
    return {
        "record_id": _norm(expected_record_id),
        "relevance_level": coerce_relevance_level(payload.get("relevance_level")),
        "triage_reason": reason,
        "triage_confidence": coerce_enum(
            payload.get("triage_confidence"), TRIAGE_CONFIDENCE, "low"
        ),
    }


def coerce_photo_type(value):
    text = _norm(value).lower().replace(" ", "_")
    if not text or text in ("unknown", "unclear"):
        return "unknown"
    mapped = coerce_enum(text, PHOTO_TYPES, "", PHOTO_TYPE_ALIASES)
    if mapped:
        return mapped
    return "other"


def coerce_forgotten_information(value):
    text = stringify_optional(value)
    if text == "unknown":
        return "unknown"
    low = text.lower()
    if any(marker in low for marker in _FORBIDDEN_FORGOTTEN_MARKERS):
        return "unknown"
    return text


def stringify_optional(value):
    if value is None:
        return "unknown"
    if isinstance(value, list):
        parts = [_norm(item) for item in value if _norm(item)]
        return "; ".join(parts) if parts else "unknown"
    text = _norm(value)
    return text if text else "unknown"


def empty_extraction_fields():
    data = {
        "photo_type": "unknown",
        "remembered_clues_detail": "unknown",
        "forgotten_information": "unknown",
        "search_strategy": "unknown",
        "failure_stage": "unknown",
        "failure_stage_reason": "",
        "refinement_attempt": "unknown",
        "workaround": "unknown",
        "retrieval_outcome": "unknown",
        "problem_theme": "unknown",
        "evidence_strength": "unclear",
        "extraction_warning": "none",
        "extraction_notes": "",
    }
    for field in REMEMBERED_FIELDS:
        data[field] = "unknown"
    return data


def original_columns(df):
    return [c for c in df.columns if c != "raw_text_empty"]


def parse_json_object(text):
    if text is None:
        raise SchemaError("Empty model response.")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise SchemaError("Invalid JSON: {}".format(exc))
    if not isinstance(parsed, dict):
        raise SchemaError("JSON root must be an object.")
    return parsed


def validate_relevance_payload(payload, expected_record_id):
    if not isinstance(payload, dict):
        raise SchemaError("Relevance payload must be an object.")
    returned_id = _norm(payload.get("record_id"))
    if returned_id != _norm(expected_record_id):
        raise SchemaError("record_id mismatch.")
    if "relevance_level" not in payload and "relevant_to_retrieval" not in payload and "is_relevant" not in payload:
        raise SchemaError("Missing relevance_level.")
    if "relevance_level" in payload:
        level = coerce_relevance_level(payload.get("relevance_level"))
    else:
        flag = coerce_relevance(payload.get("relevant_to_retrieval", payload.get("is_relevant")))
        level = "retrieval_adjacent" if flag == RELEVANCE_TRUE else "irrelevant"
    return {
        "record_id": _norm(expected_record_id),
        "relevance_level": level,
        "relevant_to_retrieval": relevant_flag_from_level(level),
        "relevance_reason": stringify_optional(payload.get("relevance_reason")),
        "relevance_confidence": coerce_enum(
            payload.get("relevance_confidence"), CONFIDENCE, "unclear"
        ),
    }


def _flatten_remembered(payload):
    nested = payload.get("remembered_clues")
    out = {}
    clue_map = {
        "people": "remembered_people",
        "time": "remembered_time",
        "place": "remembered_place",
        "object": "remembered_object",
        "text": "remembered_text",
        "event": "remembered_event",
        "purpose": "remembered_purpose",
        "sequence": "remembered_sequence",
        "association": "remembered_association",
        "visual": "remembered_visual",
    }
    for field in REMEMBERED_FIELDS:
        out[field] = coerce_tri_state(payload.get(field, "unknown"))
    if isinstance(nested, dict):
        for short_name, field in clue_map.items():
            if short_name in nested:
                out[field] = coerce_tri_state(nested.get(short_name))
    return out


def validate_extraction_payload(payload, expected_record_id):
    if not isinstance(payload, dict):
        raise SchemaError("Extraction payload must be an object.")
    returned_id = _norm(payload.get("record_id"))
    if returned_id != _norm(expected_record_id):
        raise SchemaError("record_id mismatch.")

    stage_raw = payload.get("failure_stage", payload.get("primary_failure_stage"))
    data = empty_extraction_fields()
    data.update(_flatten_remembered(payload))
    data["photo_type"] = coerce_photo_type(payload.get("photo_type"))
    data["remembered_clues_detail"] = stringify_optional(
        payload.get("remembered_clues_detail")
    )
    data["forgotten_information"] = coerce_forgotten_information(
        payload.get("forgotten_information")
    )
    strategy = stringify_optional(payload.get("search_strategy"))
    if strategy.lower().strip(" .") in _PLACEHOLDER_STRATEGIES:
        strategy = "unknown"
    data["search_strategy"] = strategy
    data["failure_stage"] = coerce_enum(
        stage_raw, FAILURE_STAGES, "other_unclear", FAILURE_STAGE_ALIASES
    )
    reason = stringify_optional(payload.get("failure_stage_reason"))
    data["failure_stage_reason"] = "" if reason == "unknown" else reason
    warning = stringify_optional(payload.get("extraction_warning"))
    data["extraction_warning"] = "none" if warning == "unknown" else warning
    data["refinement_attempt"] = coerce_enum(
        payload.get("refinement_attempt", payload.get("attempted_refinement")),
        REFINEMENT,
        "unknown",
    )
    data["workaround"] = coerce_enum(
        payload.get("workaround"), WORKAROUNDS, "unknown", WORKAROUND_ALIASES
    )
    data["retrieval_outcome"] = coerce_enum(
        payload.get("retrieval_outcome"), OUTCOMES, "unclear", OUTCOME_ALIASES
    )
    data["problem_theme"] = stringify_optional(
        payload.get("problem_theme", payload.get("primary_problem_theme"))
    )
    data["evidence_strength"] = coerce_enum(
        payload.get("evidence_strength"), EVIDENCE_STRENGTH, "unclear"
    )
    notes = payload.get("extraction_notes")
    data["extraction_notes"] = _norm(notes)
    return data
