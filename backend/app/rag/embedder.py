"""Embedding engine — singleton MiniLM model with warmup."""
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded successfully")
    return _model


def warmup():
    """Warm up the model on startup to avoid cold-start latency."""
    model = get_model()
    model.encode(["warmup"])
    logger.info("Embedding model warmed up")


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts, returns numpy array of embeddings."""
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings


def embed_single(text: str) -> np.ndarray:
    """Embed a single text."""
    return embed_texts([text])[0]
