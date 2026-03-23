"""Quiz generator — CONNECTED to personalization.
Prioritizes weak topics when generating quiz questions.
Includes failure handling for edge cases.
"""
import json
import re
import logging
from app.retrieval.hybrid import retrieve_for_task
from app.rag.llm_client import call_llm
from app.generators.prompts import get_prompt
from app.generators.cache import get_cached, set_cached
from app.personalization.tracker import get_weak_topics_for_quiz

logger = logging.getLogger(__name__)


async def generate_quiz(doc_id: str, quiz_type: str = "quiz", user_id: str = "default_user") -> dict:
    """Generate quiz questions — prioritizes weak topics for adaptive learning."""
    cached = await get_cached(doc_id, quiz_type)
    if cached:
        return cached

    # Get weak topics for this user
    weak_topics = get_weak_topics_for_quiz(user_id)

    if quiz_type == "mock_test":
        query = "Generate comprehensive exam questions covering all sections and advanced topics"
    elif weak_topics:
        # Prioritize weak topics in quiz
        topics_str = ", ".join(weak_topics)
        query = f"Generate quiz questions focusing on these weak areas: {topics_str}. Also include general topics."
        logger.info(f"[ADAPTIVE QUIZ] Prioritizing weak topics for {user_id}: {weak_topics}")
    else:
        query = "Generate quiz questions about the main topics and key definitions"

    # Hybrid retrieval
    try:
        chunks = await retrieve_for_task(doc_id, query, task_type=quiz_type)
    except Exception as e:
        logger.error(f"Retrieval failed during quiz generation: {e}")
        return {"questions": [], "error": "Retrieval failed. Please try again."}

    if not chunks:
        return {"questions": [], "error": "No content found in document"}

    context = "\n\n".join(c["text"] for c in chunks)
    prompt = get_prompt(quiz_type)

    try:
        result = await call_llm(doc_id, quiz_type, prompt, context)
    except Exception as e:
        logger.error(f"LLM call failed during quiz generation: {e}")
        return {"questions": [], "error": "AI service temporarily unavailable. Please try again."}

    parsed = _parse_json_response(result["answer"])
    if parsed:
        parsed["source_chunks"] = [{"chunk_id": c["chunk_id"], "section": c.get("section", "")} for c in chunks]
        if weak_topics:
            parsed["weak_topics_targeted"] = weak_topics
        await set_cached(doc_id, quiz_type, parsed)
        return parsed

    return {"questions": [], "raw": result["answer"], "source_chunks": []}


def evaluate_quiz(questions: list, user_answers: list) -> dict:
    """Evaluate user's quiz answers with robust matching."""
    correct = 0
    total = len(questions)
    details = []

    for i, (q, ua) in enumerate(zip(questions, user_answers)):
        correct_answer = q.get("answer", "").strip()
        user_answer = (ua or "").strip()

        # Normalize: strip letter prefixes like "A)", "B.", "C "
        def normalize(s):
            s = s.strip()
            # Remove leading letter+punctuation: "A) ...", "B. ...", "C ..."
            import re
            s = re.sub(r'^[A-Da-d][\)\\.\:\s]+\s*', '', s)
            return s.lower().strip()

        # Match by: exact, normalized text, or letter prefix
        user_norm = normalize(user_answer)
        correct_norm = normalize(correct_answer)
        user_letter = user_answer[0].upper() if user_answer else ''
        correct_letter = correct_answer[0].upper() if correct_answer else ''

        is_correct = (
            user_norm == correct_norm  # Full text match
            or user_answer.upper() == correct_answer.upper()  # Exact match
            or (len(correct_answer) <= 2 and user_letter == correct_letter)  # Letter-only answer
        )

        logger.debug(
            f"Q{i+1}: user='{user_answer}' correct='{correct_answer}' "
            f"user_norm='{user_norm}' correct_norm='{correct_norm}' → {is_correct}"
        )

        if is_correct:
            correct += 1
        details.append({
            "question": q.get("q", ""),
            "user_answer": ua,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "topic": q.get("topic", "General"),
        })

    return {
        "score": correct,
        "correct": correct,
        "total": total,
        "accuracy": round(correct / max(total, 1), 2),
        "details": details,
    }


def _parse_json_response(text: str) -> dict | None:
    """Robust JSON extraction — handles <think> tags, markdown fences, and reasoning preamble."""
    if not text or not isinstance(text, str):
        return None

    # Strip <think>...</think> blocks
    clean = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE).strip()

    # Try direct parse
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # Extract from markdown code fences
    fence_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', clean)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Find balanced { ... } blocks (last one first — LLM puts reasoning before JSON)
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

    # Try finding a JSON array
    arr_match = re.search(r'\[[\s\S]*\]', clean)
    if arr_match:
        try:
            arr = json.loads(arr_match.group())
            if isinstance(arr, list) and arr:
                return {"questions": arr}
        except json.JSONDecodeError:
            pass

    logger.warning(f"Could not parse quiz JSON from LLM response ({len(text)} chars)")
    return None

