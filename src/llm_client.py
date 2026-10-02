import json
import time

from src.config import (
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    GROQ_TIMEOUT_SECONDS,
    JSON_REPAIR_ATTEMPTS,
    LLM_MAX_RETRIES,
)
from src.secrets import get_groq_api_key


class LLMResult(object):
    def __init__(self, ok, data=None, error="", auth_failed=False, raw_text=""):
        self.ok = ok
        self.data = data
        self.error = error
        self.auth_failed = auth_failed
        self.raw_text = raw_text


def _strip_fences(text):
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _parse_object(text):
    cleaned = _strip_fences(text)
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("JSON root must be an object.")
    return parsed


def _is_retryable(exc):
    name = type(exc).__name__
    status = getattr(exc, "status_code", None)
    if name in ("RateLimitError", "APIConnectionError", "APITimeoutError", "InternalServerError"):
        return True
    if status in (408, 409, 429, 500, 502, 503, 504):
        return True
    return False


def _is_auth(exc):
    name = type(exc).__name__
    status = getattr(exc, "status_code", None)
    if name in ("AuthenticationError", "PermissionDeniedError"):
        return True
    if status in (401, 403):
        return True
    return False


def _is_truncated(exc=None, finish_reason=None):
    text = str(exc or "").lower()
    if "max completion tokens" in text:
        return True
    return finish_reason == "length"


def _compact_user(user):
    return (
        (user or "").rstrip()
        + "\n\nReturn ONLY one JSON object matching the required schema. "
        "No markdown. No explanation. Do not repeat the source text."
    )


def _chat(client, model, messages, temperature, max_completion_tokens=None, reasoning_effort=None):
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    if max_completion_tokens is not None:
        kwargs["max_completion_tokens"] = max_completion_tokens
    if reasoning_effort:
        kwargs["reasoning_effort"] = reasoning_effort
    return client.chat.completions.create(**kwargs)


def _parsed_choice(response):
    choice = response.choices[0]
    content = choice.message.content or ""
    finish = getattr(choice, "finish_reason", None)
    return _parse_object(content), content, finish


def complete_json(system, user, model=None, temperature=None, max_completion_tokens=None, reasoning_effort=None):
    """Call Groq and return a parsed JSON object, with retries and one repair."""
    api_key = get_groq_api_key()
    if not api_key:
        return LLMResult(False, error="GROQ_API_KEY is missing.")

    try:
        from groq import Groq
    except ImportError:
        return LLMResult(False, error="The groq package is not installed.")

    model_name = model or GROQ_MODEL
    temp = GROQ_TEMPERATURE if temperature is None else temperature
    client = Groq(api_key=api_key, timeout=GROQ_TIMEOUT_SECONDS)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    last_error = "Groq request failed."
    content = ""
    truncated = False
    chat_kwargs = {
        "max_completion_tokens": max_completion_tokens,
        "reasoning_effort": reasoning_effort,
    }
    for attempt in range(LLM_MAX_RETRIES):
        try:
            response = _chat(client, model_name, messages, temp, **chat_kwargs)
            try:
                data, content, finish = _parsed_choice(response)
                return LLMResult(True, data=data, raw_text=content)
            except (ValueError, json.JSONDecodeError) as parse_exc:
                finish = getattr(response.choices[0], "finish_reason", None)
                truncated = _is_truncated(finish_reason=finish)
                last_error = "Invalid JSON from model: {}".format(parse_exc)
                break
        except Exception as exc:
            last_error = str(exc) or type(exc).__name__
            if _is_auth(exc):
                return LLMResult(False, error=last_error, auth_failed=True)
            if _is_truncated(exc):
                truncated = True
                break
            if _is_retryable(exc) and attempt < LLM_MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            if not _is_retryable(exc):
                return LLMResult(False, error=last_error)
            return LLMResult(False, error=last_error)

    if truncated and JSON_REPAIR_ATTEMPTS:
        # Fresh request only. The truncated reply is not sent back.
        repair_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": _compact_user(user)},
        ]
        try:
            response = _chat(client, model_name, repair_messages, temp, **chat_kwargs)
            data, repaired, _finish = _parsed_choice(response)
            return LLMResult(True, data=data, raw_text=repaired)
        except (ValueError, json.JSONDecodeError) as parse_exc:
            return LLMResult(False, error="Invalid JSON from model: {}".format(parse_exc), raw_text=content)
        except Exception as exc:
            return LLMResult(False, error="JSON repair failed: {}".format(exc), raw_text=content)

    if content and JSON_REPAIR_ATTEMPTS and not truncated:
        repair_messages = messages + [
            {"role": "assistant", "content": content},
            {
                "role": "user",
                "content": "Fix the previous reply into a single valid JSON object. No markdown.",
            },
        ]
        try:
            response = _chat(client, model_name, repair_messages, temp, **chat_kwargs)
            repaired = response.choices[0].message.content or ""
            return LLMResult(True, data=_parse_object(repaired), raw_text=repaired)
        except Exception as exc:
            return LLMResult(False, error="JSON repair failed: {}".format(exc), raw_text=content)

    return LLMResult(False, error=last_error, raw_text=content)
