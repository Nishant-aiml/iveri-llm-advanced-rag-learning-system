"""Sarvam-M LLM client — with caching, timeout, retry, streaming, and rate limiting."""
import asyncio
import hashlib
import json
import re
import time
import logging
import httpx
from app.config import (
    SARVAM_API_KEY, SARVAM_API_URL, LLM_TIMEOUT_SECONDS,
    LLM_MAX_RETRIES, LLM_RETRY_DELAY, RATE_LIMIT_GAP_SECONDS,
    PROMPT_VERSION
)
from app.state import llm_cache, last_request_time, doc_locks

logger = logging.getLogger(__name__)

TIMEOUT_FALLBACK = "Response taking too long. Please retry."


def _cache_key(doc_id: str, task_type: str, context: str) -> tuple:
    context_hash = hashlib.md5(context.encode()).hexdigest()
    return (doc_id, task_type, context_hash, PROMPT_VERSION)


async def _rate_limit(doc_id: str):
    """Enforce minimum gap between LLM calls for a document."""
    last = last_request_time.get(doc_id, 0)
    elapsed = time.time() - last
    if elapsed < RATE_LIMIT_GAP_SECONDS:
        await asyncio.sleep(RATE_LIMIT_GAP_SECONDS - elapsed)
    last_request_time[doc_id] = time.time()


async def call_llm(
    doc_id: str,
    task_type: str,
    prompt: str,
    context: str,
    stream: bool = False,
) -> dict:
    """Call Sarvam-M with caching, timeout, retry, and rate limiting.

    Returns: {"answer": str, "source_chunks": list, "cached": bool}
    """
    key = _cache_key(doc_id, task_type, context)

    # Check cache first → instant return
    if key in llm_cache:
        logger.info(f"LLM cache hit for {doc_id}/{task_type}")
        cached = llm_cache[key].copy()
        cached["cached"] = True
        return cached

    # Rate limit
    await _rate_limit(doc_id)

    # Build messages
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": context},
    ]

    # Retry loop with backoff
    last_error = None
    for attempt in range(LLM_MAX_RETRIES):
        try:
            response = await asyncio.wait_for(
                _make_api_call(messages),
                timeout=LLM_TIMEOUT_SECONDS,
            )

            result = {
                "answer": response,
                "source_chunks": [],
                "cached": False,
            }

            # Cache the final response
            llm_cache[key] = {"answer": response, "source_chunks": []}

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
    }


def _clean_response(text: str) -> str:
    """Strip <think>...</think> CoT reasoning blocks and clean up LLM output."""
    # Remove <think>...</think> blocks (chain-of-thought reasoning)
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()
    # Remove any leftover standalone <think> or </think> tags
    cleaned = re.sub(r'</?think>', '', cleaned).strip()
    return cleaned if cleaned else text


async def _make_api_call(messages: list[dict]) -> str:
    """Make the actual HTTP call to Sarvam-M API."""
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sarvam-m",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT_SECONDS + 5) as client:
        response = await client.post(
            SARVAM_API_URL,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

        # Extract content from response
        if "choices" in data and data["choices"]:
            raw = data["choices"][0]["message"]["content"]
        elif "result" in data:
            raw = data["result"]
        else:
            raw = json.dumps(data)

        return _clean_response(raw)
