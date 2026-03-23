"""Auto-classify documents into subjects using LLM analysis of content."""
import json
import logging
import re
from pathlib import Path
from app.rag.llm_client import call_llm
from app.state import chunk_store
from app.config import CHUNKS_DIR

logger = logging.getLogger(__name__)

CLASSIFY_PROMPT = """You are a document classifier. Given text excerpts from a document, determine the PRIMARY academic subject this document belongs to.

Rules:
- Return ONLY a JSON object: {"subject": "Subject Name", "confidence": 0.0-1.0}
- Subject should be a clean academic category, 1-3 words max
- Examples: "Machine Learning", "Data Structures", "Operating Systems", "Python Programming", "Database Systems", "Computer Networks", "Web Development", "Mathematics", "Physics", "Chemistry", "Biology", "English Literature", "History", "Economics", "Digital Electronics"
- If truly unclear, use "General Studies"
- Do NOT include file extensions, doc IDs, or generic filler words
"""


def _load_chunks(doc_id: str) -> list[dict]:
    """Load chunks from memory first, then disk as fallback."""
    # Try in-memory store first
    chunks = chunk_store.get(doc_id, [])
    if chunks:
        return chunks

    # Fallback: read from disk
    chunks_path = Path(CHUNKS_DIR) / f"{doc_id}.json"
    if chunks_path.exists():
        try:
            with open(chunks_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            logger.info(f"[{doc_id}] Loaded {len(chunks)} chunks from disk for classification")
            return chunks
        except Exception as e:
            logger.error(f"[{doc_id}] Failed to load chunks from disk: {e}")

    return []


async def classify_document(doc_id: str) -> str:
    """Classify a document's subject from its first few chunks.

    Args:
        doc_id: The document ID to classify

    Returns:
        Subject string like "Machine Learning" or "Python Programming"
    """
    chunks = _load_chunks(doc_id)
    if not chunks:
        logger.warning(f"No chunks found for {doc_id}, defaulting to General")
        return "General"

    # Take first 5 chunks (or all if fewer) for classification context
    sample_chunks = chunks[:5]
    sample_text = "\n\n".join(
        f"[Section: {c.get('section', 'Unknown')}]\n{c.get('text', '')[:500]}"
        for c in sample_chunks
    )

    # Limit total context to ~2000 chars
    if len(sample_text) > 2000:
        sample_text = sample_text[:2000]

    try:
        result = await call_llm(
            doc_id,
            "classify",
            CLASSIFY_PROMPT,
            f"Document excerpts:\n\n{sample_text}\n\nClassify this document's subject."
        )

        answer = result.get("answer", "")

        # Try to parse JSON from the response
        # Handle cases where LLM wraps in markdown code blocks
        json_match = re.search(r'\{[^}]+\}', answer)
        if json_match:
            data = json.loads(json_match.group())
            subject = data.get("subject", "General").strip()
            confidence = data.get("confidence", 0.5)
            logger.info(f"[{doc_id}] Classified as '{subject}' (confidence: {confidence})")
            return subject
        else:
            # Fallback: try to extract subject from plain text
            subject = answer.strip().strip('"').strip("'")
            if len(subject) > 40 or len(subject) < 2:
                subject = "General"
            logger.info(f"[{doc_id}] Classified as '{subject}' (plain text fallback)")
            return subject

    except Exception as e:
        logger.error(f"[{doc_id}] Classification failed: {e}")
        return "General"
