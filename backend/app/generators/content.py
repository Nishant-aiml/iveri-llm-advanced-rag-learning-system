"""General content generators — flashcards, summary, slides, fun facts, mentor.
Upgraded: uses hybrid retrieval pipeline.
"""
import json
import re
import logging
from app.retrieval.hybrid import retrieve_for_task
from app.rag.llm_client import call_llm
from app.generators.prompts import get_prompt
from app.generators.cache import get_cached, set_cached

logger = logging.getLogger(__name__)


async def generate_content(doc_id: str, content_type: str, query: str = "") -> dict:
    """Generic generator for flashcards, summary, slides, fun_facts, mock_test."""
    cached = await get_cached(doc_id, content_type)
    if cached:
        cached["cached"] = True
        return cached

    if content_type == "summary":
        query_text = "Summarize the entire document covering introduction, main topics, and conclusion"
    elif content_type == "slides":
        query_text = "Key points and main themes for a presentation"
    else:
        query_text = query or f"Generate {content_type} about the main topics"

    # Use new hybrid retrieval
    chunks = await retrieve_for_task(doc_id, query_text, task_type=content_type)

    if not chunks:
        return {"error": "No content found in document"}

    context = "\n\n".join(c["text"] for c in chunks)
    prompt = get_prompt(content_type)
    result = await call_llm(doc_id, content_type, prompt, context)

    parsed = _parse_json_response(result["answer"])
    if parsed:
        parsed["source_chunks"] = [
            {"chunk_id": c["chunk_id"], "section": c.get("section", "")}
            for c in chunks
        ]
        parsed["cached"] = False
        await set_cached(doc_id, content_type, parsed)
        return parsed

    return {"raw": result["answer"], "cached": False}


async def ask_mentor(doc_id: str, question: str, conversation_history: list = None) -> dict:
    """AI Mentor — context-aware Q&A with follow-up questions."""
    chunks = await retrieve_for_task(doc_id, question, task_type="mentor")

    if not chunks:
        return {"answer": "Not in document.", "source_chunks": [], "follow_up": None}

    context = "\n\n".join(c["text"] for c in chunks)

    full_context = context
    if conversation_history:
        history_text = "\n".join(
            f"{'Student' if m['role']=='user' else 'Mentor'}: {m['content']}"
            for m in conversation_history[-4:]
        )
        full_context = f"Previous conversation:\n{history_text}\n\nDocument context:\n{context}"

    prompt = get_prompt("mentor")
    result = await call_llm(doc_id, "mentor", prompt, f"{full_context}\n\nStudent's question: {question}")

    return {
        "answer": result["answer"],
        "source_chunks": [
            {"chunk_id": c["chunk_id"], "section": c.get("section", ""), "text": c["text"][:200]}
            for c in chunks
        ],
        "cached": result.get("cached", False),
    }


def _parse_json_response(text: str) -> dict | None:
    """Robust JSON extraction — handles <think> tags, markdown fences, and reasoning preamble."""
    if not text or not isinstance(text, str):
        return None

    # 1) Strip <think>...</think> blocks
    clean = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE).strip()

    # 2) Try direct JSON parse
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # 3) Extract from markdown code fences ```json ... ```
    fence_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', clean)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # 4) Find the last { ... } block (LLM often puts reasoning before JSON)
    brace_positions = [i for i, c in enumerate(clean) if c == '{']
    for start_pos in reversed(brace_positions):
        depth = 0
        end_pos = start_pos
        for i in range(start_pos, len(clean)):
            if clean[i] == '{':
                depth += 1
            elif clean[i] == '}':
                depth -= 1
                if depth == 0:
                    end_pos = i + 1
                    break
        if end_pos > start_pos:
            candidate = clean[start_pos:end_pos]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue

    # 5) Try finding a JSON array [ ... ]
    arr_match = re.search(r'\[[\s\S]*\]', clean)
    if arr_match:
        try:
            arr = json.loads(arr_match.group())
            if isinstance(arr, list) and arr:
                # Guess the wrapper key from content
                if all('q' in item and 'a' in item for item in arr if isinstance(item, dict)):
                    return {"flashcards": arr}
                if all('q' in item and 'options' in item for item in arr if isinstance(item, dict)):
                    return {"questions": arr}
                return {"items": arr}
        except json.JSONDecodeError:
            pass

    logger.warning(f"Could not parse JSON from LLM response ({len(text)} chars)")
    return None

