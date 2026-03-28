"""FastAPI main application — IVERI LLM Advanced RAG System entry point."""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import init_db
from app.api.routes import router
from app.rag.embedder import warmup
from app.gamification.leaderboard import load_leaderboard_cache
from app.tasks.background import flush_pending_updates
from app.tasks.pipeline_queue import start_pipeline_pool, stop_pipeline_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 60)
    logger.info("Starting IVERI LLM — Advanced RAG System...")

    # 1. Initialize database tables
    init_db()
    logger.info("✓ Database initialized")

    # 2. Warm up embedding model (MiniLM)
    warmup()
    logger.info("✓ Embedding model warmed up")

    # 3. Load leaderboard cache from DB
    load_leaderboard_cache()
    logger.info("✓ Leaderboard cache loaded")

    # 4. Load content library catalog
    try:
        from app.core.library import _load_catalog
        _load_catalog()
        logger.info("✓ Content library catalog loaded")
    except Exception as e:
        logger.warning(f"Library catalog load skipped: {e}")

    # 5. Start background flush task
    flush_task = asyncio.create_task(flush_pending_updates())
    logger.info("✓ Background flush task started")

    # 6. Start ingestion queue worker pool
    await start_pipeline_pool()
    logger.info("✓ Ingestion worker pool started")

    logger.info("=" * 60)
    logger.info("System READY — Advanced RAG pipeline operational")
    logger.info("  Retrieval: Hybrid (FAISS + BM25 + RRF)")
    logger.info("  Features:  Search Engine | Personalization | Content Library")
    logger.info("=" * 60)

    yield

    # --- SHUTDOWN ---
    flush_task.cancel()
    await stop_pipeline_pool()
    logger.info("System shutting down")


app = FastAPI(
    title="IVERI LLM — Advanced RAG System",
    description="Production-ready AI Document Retrieval + Learning System with hybrid search, personalization, and content library.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No-cache middleware for static files (dev mode)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.endswith(('.js', '.css', '.html')) or request.url.path == '/':
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        return response

app.add_middleware(NoCacheMiddleware)

# API routes
app.include_router(router, prefix="/api")

# Serve frontend static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="root")
else:
    @app.get("/")
    async def root():
        return {"message": "IVERI LLM — Advanced RAG System", "docs": "/docs"}
