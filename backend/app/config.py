"""Central configuration for the IVERI LLM — Advanced RAG System."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
FAISS_INDEX_DIR = STORAGE_DIR / "faiss_index"
CHUNKS_DIR = STORAGE_DIR / "chunks"
UPLOAD_DIR = STORAGE_DIR / "uploads"
LIBRARY_DIR = STORAGE_DIR / "library"
EVAL_DIR = STORAGE_DIR / "evaluation"

for d in [STORAGE_DIR, FAISS_INDEX_DIR, CHUNKS_DIR, UPLOAD_DIR, LIBRARY_DIR, EVAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# --- Database ---
DATABASE_URL = f"sqlite:///{BASE_DIR / 'learning_engine.db'}"

# --- LLM ---
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_API_URL = os.getenv("SARVAM_API_URL", "https://api.sarvam.ai/v1/chat/completions")

# --- Embedding ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- RAG / Chunking ---
MAX_CONTEXT_TOKENS = 1500
CHUNK_SIZE_WORDS = 350
CHUNK_OVERLAP_WORDS = 50
CHUNK_MIN_WORDS = 100      # Merge chunks below this
CHUNK_MAX_WORDS = 500      # Split chunks above this

# --- Hybrid Retrieval (RRF) ---
RRF_K_DEFAULT = 10          # RRF constant
DEFAULT_VECTOR_WEIGHT = 0.5
DEFAULT_BM25_WEIGHT = 0.5

# --- Reranker ---
RERANK_MIN_CANDIDATES = 5   # Min chunks before triggering reranker
RERANK_SCORE_GAP = 0.02     # Score gap threshold for triggering reranker

# --- MMR ---
MMR_LAMBDA = 0.7             # Relevance vs diversity tradeoff
MMR_SIMILARITY_THRESHOLD = 0.85  # Near-duplicate threshold

# --- Performance ---
MAX_DOCS_IN_MEMORY = 50
MAX_UPLOAD_SIZE_MB = 20
LLM_TIMEOUT_SECONDS = 30
LLM_MAX_RETRIES = 2
LLM_RETRY_DELAY = 2.0
RATE_LIMIT_GAP_SECONDS = 0.5

# --- Gamification ---
XP_UPLOAD = 20
XP_ASK = 5
XP_QUIZ_COMPLETE = 50
XP_CORRECT_ANSWER = 10
XP_DAILY_STREAK = 30

# --- Prompt ---
PROMPT_VERSION = "v3"

# --- Allowed file types ---
ALLOWED_EXTENSIONS = {".pdf", ".xlsx"}

# --- Trust / Confidence ---
CONFIDENCE_FALLBACK_THRESHOLD = 0.25  # Below this, return fallback response
