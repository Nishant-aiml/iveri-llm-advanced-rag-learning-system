"""Typo correction for search queries using difflib.

Builds vocabulary from document chunks and suggests corrections
for misspelled words using fuzzy matching.
"""
import re
import json
import logging
from pathlib import Path
from difflib import get_close_matches
from app.state import chunk_store
from app.config import CHUNKS_DIR

logger = logging.getLogger(__name__)

# Cache vocabularies per doc
_vocab_cache: dict[str, set[str]] = {}


def _load_chunks(doc_id: str) -> list[dict]:
    """Load chunks from memory first, then disk as fallback."""
    chunks = chunk_store.get(doc_id, [])
    if chunks:
        return chunks

    # Fallback: read from disk
    chunks_path = Path(CHUNKS_DIR) / f"{doc_id}.json"
    if chunks_path.exists():
        try:
            with open(chunks_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            logger.info(f"[spell] Loaded {len(chunks)} chunks from disk for {doc_id}")
            return chunks
        except Exception as e:
            logger.error(f"[spell] Failed to load chunks from disk for {doc_id}: {e}")

    return []


def build_vocabulary(doc_id: str) -> set[str]:
    """Build word vocabulary from document chunks."""
    if doc_id in _vocab_cache and _vocab_cache[doc_id]:
        return _vocab_cache[doc_id]

    chunks = _load_chunks(doc_id)
    vocab = set()
    for chunk in chunks:
        text = chunk.get("text", "")
        # Extract words, lowercase, filter short/numeric
        words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        vocab.update(words)

    # Add common academic terms that might not be in the doc
    common_terms = {
        "machine", "learning", "artificial", "intelligence", "neural", "network",
        "algorithm", "data", "structure", "database", "programming", "python",
        "computer", "science", "mathematics", "physics", "chemistry", "biology",
        "operating", "system", "software", "engineering", "analysis", "design",
        "function", "variable", "array", "string", "class", "object", "method",
        "model", "training", "testing", "validation", "accuracy", "performance",
        "search", "query", "index", "vector", "embedding", "retrieval"
    }
    vocab.update(common_terms)

    _vocab_cache[doc_id] = vocab
    logger.info(f"Built vocabulary for {doc_id}: {len(vocab)} words")
    return vocab


def suggest_query(query: str, doc_id: str) -> dict:
    """Check query for typos and suggest corrections.

    Returns:
        {
            "original": "machien lerning",
            "corrected": "machine learning",
            "did_you_mean": True/False,
            "corrections": {"machien": "machine", "lerning": "learning"}
        }
    """
    vocab = build_vocabulary(doc_id)
    if not vocab:
        return {"original": query, "corrected": query, "did_you_mean": False, "corrections": {}}

    words = query.split()
    corrected_words = []
    corrections = {}

    for word in words:
        word_lower = word.lower()
        # Skip if word exists in vocabulary or is very short
        if word_lower in vocab or len(word_lower) < 3:
            corrected_words.append(word)
            continue

        # Find close matches with a slightly relaxed cutoff for better suggestions
        matches = get_close_matches(word_lower, list(vocab), n=3, cutoff=0.65)
        if matches and matches[0] != word_lower:
            corrections[word] = matches[0]
            corrected_words.append(matches[0])
            logger.debug(f"Typo correction: '{word}' → '{matches[0]}'")
        else:
            corrected_words.append(word)

    corrected = " ".join(corrected_words)
    did_you_mean = corrected.lower() != query.lower()

    return {
        "original": query,
        "corrected": corrected,
        "did_you_mean": did_you_mean,
        "corrections": corrections,
    }
