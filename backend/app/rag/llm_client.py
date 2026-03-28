"""Sarvam-M LLM client — with caching, timeout, retry, streaming, and rate limiting."""
import asyncio
import hashlib
import json
import re
import time
import logging
import httpx
from app.config import (
    SARVAM_API_KEY, SARVAM_API_URL, SARVAM_MODEL, LLM_TEMPERATURE,
    LLM_MAX_TOKENS_DEFAULT, LLM_MAX_TOKENS_BY_TASK,
    LLM_TIMEOUT_SECONDS,
    LLM_MAX_RETRIES, LLM_RETRY_DELAY, RATE_LIMIT_GAP_SECONDS,
    PROMPT_VERSION,
    sarvam_model_id_for_variant,
)
from app.state import llm_cache, last_request_time, doc_locks

logger = logging.getLogger(__name__)

TIMEOUT_FALLBACK = "Response taking too long. Please retry."


def _cache_key(doc_id: str, task_type: str, context: str, model_id: str) -> tuple:
    context_hash = hashlib.md5(context.encode()).hexdigest()
    return (doc_id, task_type, context_hash, PROMPT_VERSION, model_id)


async def _rate_limit(doc_id: str):
    """Enforce minimum gap between LLM calls for a document."""
    last = last_request_time.get(doc_id, 0)
    elapsed = time.time() - last
    if elapsed < RATE_LIMIT_GAP_SECONDS:
        await asyncio.sleep(RATE_LIMIT_GAP_SECONDS - elapsed)
    last_request_time[doc_id] = time.time()


def _max_tokens_for_task(task_type: str) -> int:
    return LLM_MAX_TOKENS_BY_TASK.get(task_type, LLM_MAX_TOKENS_DEFAULT)


async def call_llm(
    doc_id: str,
    task_type: str,
    prompt: str,
    context: str,
    stream: bool = False,
    use_cache: bool = True,
    temperature: float | None = None,
    max_tokens: int | None = None,
    llm_variant: str | None = None,
) -> dict:
    """Call Sarvam chat with caching, timeout, retry, and rate limiting.

    ``llm_variant``: ``\"105b\"`` | ``\"30b\"`` (default 105B slot via config).

    Returns: {"answer": str, "source_chunks": list, "cached": bool, "llm_model": str}
    """
    model_id = sarvam_model_id_for_variant(llm_variant)
    key = _cache_key(doc_id, task_type, context, model_id)

    # Check cache first → instant return (optional)
    if use_cache and key in llm_cache:
        logger.info(f"LLM cache hit for {doc_id}/{task_type}")
        cached = llm_cache[key].copy()
        cached["cached"] = True
        cached.setdefault("llm_model", model_id)
        return cached

    # Rate limit
    await _rate_limit(doc_id)

    # Build messages
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": context},
    ]

    temp = LLM_TEMPERATURE if temperature is None else temperature
    mtok = _max_tokens_for_task(task_type) if max_tokens is None else max_tokens

    # Retry loop with backoff (network/API failures)
    last_error = None
    for attempt in range(LLM_MAX_RETRIES):
        try:
            response = await asyncio.wait_for(
                _make_api_call(messages, temperature=temp, max_tokens=mtok, model=model_id),
                timeout=LLM_TIMEOUT_SECONDS,
            )

            result = {
                "answer": response,
                "source_chunks": [],
                "cached": False,
                "llm_model": model_id,
            }

            # Cache the final response
            if use_cache:
                llm_cache[key] = {"answer": response, "source_chunks": [], "llm_model": model_id}

            return result

        except asyncio.TimeoutError:
            logger.warning(f"LLM timeout (attempt {attempt+1}/{LLM_MAX_RETRIES})")
            last_error = "timeout"
        except Exception as e:
            logger.error(f"LLM error (attempt {attempt+1}): {e}")
            last_error = str(e)

        if attempt < LLM_MAX_RETRIES - 1:
            await asyncio.sleep(LLM_RETRY_DELAY)

    return {
        "answer": TIMEOUT_FALLBACK if last_error == "timeout" else f"Error: {last_error}",
        "source_chunks": [],
        "cached": False,
        "llm_model": model_id,
    }


def _clean_response(text: str) -> str:
    """Strip <think>...</think> CoT reasoning blocks and clean up LLM output."""
    if not isinstance(text, str):
        return ""
    # Remove <think>...</think> blocks (chain-of-thought reasoning)
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()
    # Remove any leftover standalone <think> or </think> tags
    cleaned = re.sub(r'</?think>', '', cleaned).strip()
    return cleaned if cleaned else text


def _extract_assistant_text(data: dict) -> str:
    """Read `message.content`; Sarvam 105B may use reasoning tokens first, leaving content null."""
    if "choices" in data and data["choices"]:
        choice0 = data["choices"][0]
        msg = choice0.get("message") or {}
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return _clean_response(content)
        rc = msg.get("reasoning_content")
        if isinstance(rc, str) and rc.strip():
            logger.warning(
                "LLM returned empty content but reasoning_content is non-empty "
                "(finish_reason=%s, reasoning_chars=%s). Raise max_tokens if outputs are missing.",
                choice0.get("finish_reason"),
                len(rc),
            )
        return ""
    if "result" in data:
        r = data["result"]
        return _clean_response(r) if isinstance(r, str) else json.dumps(r)
    return json.dumps(data)


async def _make_api_call(
    messages: list[dict],
    temperature: float = LLM_TEMPERATURE,
    max_tokens: int = LLM_MAX_TOKENS_DEFAULT,
    model: str | None = None,
) -> str:
    """Make the actual HTTP call to Sarvam chat completions API."""
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model or SARVAM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT_SECONDS + 5) as client:
        response = await client.post(
            SARVAM_API_URL,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

        raw = _extract_assistant_text(data)
        usage = data.get("usage")
        if usage:
            logger.debug("LLM usage: %s", usage)
        return raw
