"""API routes — all endpoints with the Advanced RAG pipeline.
Upgraded: hybrid retrieval, search engine mode, personalization, content library.
All existing endpoints preserved + new endpoints added.
"""
import hashlib
import uuid
import time
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional

from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_MB, UPLOAD_DIR
from app.database import SessionLocal, Document, User, Attempt, get_db
from app.state import (
    faiss_indexes, chunk_store, generated_cache, llm_cache,
    doc_locks, leaderboard_cache, bm25_indexes
)
from app.tasks.background import process_document_pipeline

# New pipeline imports
from app.retrieval.hybrid import retrieve_for_task
from app.retrieval.mmr import mmr_filter
from app.retrieval.context_filter import filter_context
from app.reranker.llm_reranker import rerank_chunks
from app.query.router import route_query
from app.query.expander import sanitize_query
from app.llm.trust import compute_confidence, build_source_citations, should_fallback, FALLBACK_RESPONSE
from app.search.engine import search
from app.personalization.tracker import (
    record_quiz_results, get_weak_topics, get_all_topic_scores
)
from app.personalization.advisor import generate_advice, generate_study_plan
from app.core.library import add_to_library, get_subjects, get_subject_docs, remove_from_library
from app.retrieval.hybrid import compare_retrieval
from app.evaluation.runner import run_evaluation, retrieval_comparison_report, get_latest_report, run_multi_evaluation
from app.reranker.llm_reranker import rerank_chunks, validate_reranker
from app.evaluation.final_report import generate_system_report
from app.chunking.validator import validate_chunks

# Existing imports (still used)
from app.rag.llm_client import call_llm
from app.rag.embedder import get_model
from app.indexing.vector_index import delete_vector_index
from app.indexing.bm25_index import delete_bm25_index
from app.generators.prompts import get_prompt
from app.generators.quiz import generate_quiz, evaluate_quiz
from app.generators.content import generate_content, ask_mentor
from app.generators.cache import clear_cached
from app.gamification.engine import add_xp, get_user_score
from app.gamification.leaderboard import get_leaderboard

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Request/Response Models ---

class AskRequest(BaseModel):
    doc_id: str
    question: str
    user_id: str = "default_user"
    stream: bool = False

class QuizStartRequest(BaseModel):
    doc_id: str
    user_id: str = "default_user"
    quiz_type: str = "quiz"

class QuizSubmitRequest(BaseModel):
    doc_id: str
    user_id: str = "default_user"
    questions: list
    answers: list[str]

class GenerateRequest(BaseModel):
    doc_id: str
    content_type: str
    user_id: str = "default_user"
    query: str = ""

class MentorRequest(BaseModel):
    doc_id: str
    question: str
    user_id: str = "default_user"
    history: list = Field(default_factory=list)

class AuthRequest(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    email: Optional[str] = None

class SearchRequest(BaseModel):
    doc_id: str
    query: str
    mode: str = "auto"  # keyword | hybrid | ai | auto
    user_id: str = "default_user"

class LibraryAddRequest(BaseModel):
    doc_id: str
    subject: str
    title: str = ""

class LibraryRemoveRequest(BaseModel):
    doc_id: str
    subject: str = ""


# --- Utility ---

def _log_request(endpoint: str, doc_id: str, query: str = "", cache_hit: bool = False):
    logger.info(f"[REQUEST] {endpoint} | doc={doc_id} | query={query[:80]}... | cache_hit={cache_hit}")

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# --- AUTH ENDPOINTS ---

@router.post("/register")
async def register(req: AuthRequest):
    """Register a new user."""
    if not req.username or len(req.username) < 5:
        raise HTTPException(400, "Email must be valid")
    if not req.password or len(req.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == req.username).first()
        if existing:
            raise HTTPException(409, "An account with this email already exists")

        user_id = f"user_{uuid.uuid4().hex[:10]}"
        user = User(
            id=user_id,
            name=req.name or req.username,
            email=req.email or req.username,
            username=req.username,
            password_hash=_hash_password(req.password),
        )
        db.add(user)
        db.commit()
        return {"user_id": user_id, "username": user.name or req.username, "message": "Registration successful"}
    finally:
        db.close()


@router.post("/login")
async def login(req: AuthRequest):
    """Login with credentials."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == req.username).first()
        if not user or user.password_hash != _hash_password(req.password):
            raise HTTPException(401, "Invalid email or password")
        return {"user_id": user.id, "username": user.name or user.username, "xp": user.xp, "level": user.level, "streak": user.streak}
    finally:
        db.close()


# --- DOCUMENT ENDPOINTS ---

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form("default_user"),
):
    """Upload and process a document."""
    start = time.time()

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise HTTPException(400, f"File too large. Max: {MAX_UPLOAD_SIZE_MB}MB")

    original_filename = file.filename or "document"
    file_hash = hashlib.md5(contents).hexdigest()

    db = SessionLocal()
    try:
        # Check if THIS USER already has this exact file
        existing_for_user = db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.user_id == user_id
        ).first()
        logger.info(f"UPLOAD DEBUG: user_id={user_id}, hash={file_hash[:12]}, existing_for_user={existing_for_user.doc_id if existing_for_user else None}, existing_user_id={existing_for_user.user_id if existing_for_user else None}")
        if existing_for_user and existing_for_user.status == "ready":
            # Update filename if missing
            if not existing_for_user.filename:
                existing_for_user.filename = original_filename
                db.commit()
            await add_xp(user_id, "upload")
            return JSONResponse({
                "doc_id": existing_for_user.doc_id, "status": "ready",
                "filename": existing_for_user.filename or original_filename,
                "message": "Document already processed", "duplicate": True,
            })

        # Check if ANOTHER user has this file (reuse processing, but create new doc for this user)
        existing_other = db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.status == "ready"
        ).first()
    finally:
        db.close()

    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    file_path = UPLOAD_DIR / f"{doc_id}{ext}"
    with open(file_path, "wb") as f:
        f.write(contents)

    # If another user already processed this file, clone the data
    if existing_other:
        source_id = existing_other.doc_id
        logger.info(f"Cloning processed data from {source_id} for user {user_id}")
        # Clone in-memory indexes and chunk data
        if source_id in faiss_indexes:
            faiss_indexes[doc_id] = faiss_indexes[source_id]
        if source_id in chunk_store:
            chunk_store[doc_id] = chunk_store[source_id]
        if source_id in bm25_indexes:
            bm25_indexes[doc_id] = bm25_indexes[source_id]
        if source_id in generated_cache:
            generated_cache[doc_id] = generated_cache[source_id]

        db = SessionLocal()
        try:
            doc = Document(
                doc_id=doc_id, user_id=user_id, filename=original_filename,
                file_hash=file_hash, status="ready", processing_stage="indexed",
            )
            doc.processed_time = datetime.now(timezone.utc)
            db.add(doc)
            db.commit()
        finally:
            db.close()

        await add_xp(user_id, "upload")
        return JSONResponse({
            "doc_id": doc_id, "status": "ready",
            "filename": original_filename,
            "message": "Document processed (shared data)",
        })

    # Brand new document — process from scratch
    db = SessionLocal()
    try:
        doc = Document(
            doc_id=doc_id, user_id=user_id, filename=original_filename,
            file_hash=file_hash, status="processing", processing_stage="uploaded"
        )
        db.add(doc)
        db.commit()
    finally:
        db.close()

    background_tasks.add_task(process_document_pipeline, doc_id, str(file_path))
    await add_xp(user_id, "upload")

    latency = round(time.time() - start, 3)
    logger.info(f"Upload accepted: doc_id={doc_id}, filename={original_filename}, latency={latency}s")
    return JSONResponse({
        "doc_id": doc_id, "status": "processing",
        "filename": original_filename,
        "message": "Document upload accepted, processing in background"
    })


@router.get("/status/{doc_id}")
async def get_document_status(doc_id: str):
    """Get document processing status."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.doc_id == doc_id).first()
        if not doc:
            raise HTTPException(404, "Document not found")
        return {"doc_id": doc.doc_id, "status": doc.status, "processing_stage": doc.processing_stage, "error": doc.error_message}
    finally:
        db.close()


# --- AI ENDPOINTS (UPGRADED with hybrid retrieval) ---

@router.post("/ask")
async def ask_question(req: AskRequest):
    """RAG Q&A — hybrid retrieval + confidence + latency tracking."""
    start = time.time()
    timings = {}
    _log_request("/ask", req.doc_id, req.question)
    _validate_doc_ready(req.doc_id)

    clean_q = sanitize_query(req.question)
    if not clean_q:
        raise HTTPException(400, "Invalid or empty query")

    # Hybrid retrieval (FAISS + BM25 + RRF)
    t0 = time.time()
    chunks = await retrieve_for_task(req.doc_id, clean_q, task_type="ask")
    timings["retrieval_ms"] = round((time.time() - t0) * 1000, 1)

    # MMR diversity filter
    t0 = time.time()
    chunks = mmr_filter(chunks, max_chunks=5)
    timings["mmr_ms"] = round((time.time() - t0) * 1000, 1)

    # Context filter (token-safe)
    t0 = time.time()
    chunks = filter_context(chunks, max_tokens=1500)
    timings["context_filter_ms"] = round((time.time() - t0) * 1000, 1)

    if not chunks:
        return {"answer": FALLBACK_RESPONSE, "source_chunks": [], "confidence": {"level": "low", "score": 0}, "cached": False, "timings": timings}

    # Confidence check (with reranker score if available)
    scores = [c.get("rrf_score", c.get("score", 0)) for c in chunks]
    reranker_score = max((c.get("rerank_score", 0) for c in chunks), default=0)
    confidence = compute_confidence(scores, reranker_score=reranker_score, num_chunks=len(chunks))

    if should_fallback(confidence):
        return {"answer": FALLBACK_RESPONSE, "sources": [], "confidence": confidence, "cached": False, "timings": timings}

    context = "\n\n".join(c["text"] for c in chunks)
    prompt = get_prompt("ask")

    t0 = time.time()
    result = await call_llm(req.doc_id, "ask", prompt, f"{context}\n\nQuestion: {clean_q}")
    timings["llm_ms"] = round((time.time() - t0) * 1000, 1)

    # Source citations
    sources = build_source_citations(chunks)
    result["source_chunks"] = sources
    result["confidence"] = confidence
    result["timings"] = timings
    await add_xp(req.user_id, "ask")

    latency = round(time.time() - start, 3)
    logger.info(f"/ask latency: {latency}s | confidence: {confidence['level']} | timings: {timings}")
    return result


@router.post("/mentor")
async def mentor_chat(req: MentorRequest):
    """AI Mentor mode."""
    start = time.time()
    _validate_doc_ready(req.doc_id)
    result = await ask_mentor(req.doc_id, req.question, req.history)
    await add_xp(req.user_id, "ask")
    return result


@router.post("/quiz/start")
async def start_quiz(req: QuizStartRequest):
    """Generate a quiz — adaptive: prioritizes weak topics."""
    _validate_doc_ready(req.doc_id)
    return await generate_quiz(req.doc_id, req.quiz_type, user_id=req.user_id)


@router.post("/quiz/submit")
async def submit_quiz(req: QuizSubmitRequest):
    """Submit quiz answers — now tracks topic accuracy for personalization."""
    evaluation = evaluate_quiz(req.questions, req.answers)

    # Track topic accuracy (personalization)
    record_quiz_results(req.user_id, evaluation.get("details", []))

    await add_xp(req.user_id, "quiz_complete", correct_count=evaluation["correct"])

    db = SessionLocal()
    try:
        attempt = Attempt(
            user_id=req.user_id, doc_id=req.doc_id, quiz_type="quiz",
            score=evaluation["score"], total=evaluation["total"], accuracy=evaluation["accuracy"],
        )
        db.add(attempt)
        db.commit()
    finally:
        db.close()

    user_score = await get_user_score(req.user_id)
    return {**evaluation, "xp": user_score}


@router.post("/generate")
async def generate(req: GenerateRequest):
    """Generate content: flashcards, summary, slides, fun_facts, etc."""
    _validate_doc_ready(req.doc_id)

    valid_types = ["flashcards", "summary", "slides", "fun_facts", "mock_test", "rapid_fire", "true_false", "fill_blanks"]
    if req.content_type not in valid_types:
        raise HTTPException(400, f"Invalid content type. Must be one of: {valid_types}")

    result = await generate_content(req.doc_id, req.content_type, req.query)
    await add_xp(req.user_id, "ask")
    return result


# --- NEW: SEARCH ENGINE ---

@router.post("/search")
async def search_endpoint(req: SearchRequest):
    """Search engine with keyword/hybrid/AI modes."""
    _validate_doc_ready(req.doc_id)

    clean_q = sanitize_query(req.query)
    if not clean_q:
        raise HTTPException(400, "Invalid or empty query")

    result = await search(req.doc_id, clean_q, mode=req.mode, user_id=req.user_id)
    await add_xp(req.user_id, "ask")
    return result


# --- NEW: EVALUATION ---

@router.post("/evaluate/{doc_id}")
async def evaluate_document(doc_id: str):
    """Run evaluation pipeline on a document — metrics, ablation, latency."""
    _validate_doc_ready(doc_id)
    result = await run_evaluation(doc_id)
    return result


@router.post("/compare/{doc_id}")
async def compare_retrieval_endpoint(doc_id: str, query: str):
    """Compare vector-only vs hybrid retrieval for a query."""
    _validate_doc_ready(doc_id)
    result = await compare_retrieval(doc_id, query)
    return result


@router.post("/validate-reranker/{doc_id}")
async def validate_reranker_endpoint(doc_id: str, query: str):
    """Show before/after reranking for a query."""
    _validate_doc_ready(doc_id)
    chunks = await retrieve_for_task(doc_id, query, task_type="ask")
    result = await validate_reranker(doc_id, query, chunks)
    return result


@router.post("/comparison-report/{doc_id}")
async def comparison_report_endpoint(doc_id: str):
    """Run retrieval comparison for standard test queries."""
    _validate_doc_ready(doc_id)
    test_queries = [
        "What is machine learning?",
        "How does gradient descent work?",
        "Compare supervised and unsupervised learning",
        "What causes overfitting?",
        "Explain backpropagation",
    ]
    result = await retrieval_comparison_report(doc_id, test_queries)
    return {"report": result}


@router.get("/evaluation/report/{doc_id}")
async def get_evaluation_report(doc_id: str):
    """Get latest saved evaluation report from SQLite."""
    report = get_latest_report(doc_id)
    if not report:
        raise HTTPException(404, "No evaluation report found. Run POST /api/evaluate/{doc_id} first.")
    return report


@router.get("/chunk-quality/{doc_id}")
async def get_chunk_quality(doc_id: str):
    """Validate chunk quality for a document."""
    _validate_doc_ready(doc_id)
    return validate_chunks(doc_id)


@router.get("/system/report/{doc_id}")
async def get_system_report(doc_id: str):
    """Get complete system validation report — combines all metrics."""
    _validate_doc_ready(doc_id)
    return await generate_system_report(doc_id)


@router.post("/evaluate/stable/{doc_id}")
async def evaluate_stable(doc_id: str, runs: int = 3):
    """Run multi-run evaluation for statistical stability.

    Flow: run_evaluation x N → aggregate → stability check → final report.
    Proves results are consistent, not lucky.
    """
    _validate_doc_ready(doc_id)
    if runs < 3:
        raise HTTPException(400, "Minimum 3 runs required for statistical validity")

    stable_result = await run_multi_evaluation(doc_id, runs=runs)
    report = await generate_system_report(doc_id, stability_data=stable_result)

    return {
        "stability_evaluation": stable_result,
        "system_report": report,
    }


# --- NEW: PERSONALIZATION ---

@router.get("/weakness/{user_id}")
async def get_weakness_dashboard(user_id: str):
    """Get user's weak topics with AI-generated study insights."""
    weak_topics = get_weak_topics(user_id)
    all_topics = get_all_topic_scores(user_id)

    # Add advisor insights to each weak topic
    enriched_weak = []
    for topic in weak_topics:
        advice = generate_advice(
            topic["topic"],
            topic.get("accuracy", 0),
            topic.get("trend", {}),
        )
        enriched_weak.append({**topic, "advice": advice})

    # Generate overall study plan
    study_plan = generate_study_plan(weak_topics)

    return {
        "user_id": user_id,
        "weak_topics": enriched_weak,
        "all_topics": all_topics,
        "study_plan": study_plan,
    }


# --- NEW: CONTENT LIBRARY ---

@router.post("/library/add")
async def library_add(req: LibraryAddRequest):
    """Add a processed document to the content library."""
    _validate_doc_ready(req.doc_id)
    add_to_library(req.doc_id, req.subject, req.title)
    return {"status": "added", "doc_id": req.doc_id, "subject": req.subject}


@router.get("/library")
async def library_list():
    """List all subjects in the content library."""
    return {"subjects": get_subjects()}


@router.get("/library/{subject}")
async def library_subject_docs(subject: str):
    """List documents in a subject."""
    return {"subject": subject, "documents": get_subject_docs(subject)}


@router.post("/library/remove")
async def library_remove(req: LibraryRemoveRequest):
    """Remove a document from a subject in the library."""
    remove_from_library(req.doc_id, req.subject or None)
    return {"status": "removed", "doc_id": req.doc_id}


@router.post("/library/reclassify")
async def library_reclassify(req: dict):
    """Reclassify all ready documents for a user using LLM."""
    from app.core.classifier import classify_document
    user_id = req.get("user_id", "")
    if not user_id:
        raise HTTPException(400, "user_id required")

    db = SessionLocal()
    try:
        docs = db.query(Document).filter(
            Document.user_id == user_id,
            Document.status == "ready"
        ).all()

        results = []
        for doc in docs:
            try:
                subject = await classify_document(doc.doc_id)
                if subject and subject not in ("General", "General Studies"):
                    title = doc.filename or doc.doc_id
                    add_to_library(doc.doc_id, subject, title)
                    results.append({"doc_id": doc.doc_id, "subject": subject, "title": title})
                else:
                    results.append({"doc_id": doc.doc_id, "subject": subject, "skipped": True})
            except Exception as e:
                results.append({"doc_id": doc.doc_id, "error": str(e)})

        return {"status": "done", "classified": results}
    finally:
        db.close()


# --- EXISTING: LEADERBOARD, SCORE, DELETE, HEALTH ---

@router.get("/documents/{user_id}")
async def list_user_documents(user_id: str):
    """List all documents uploaded by a user."""
    db = SessionLocal()
    try:
        docs = db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).all()
        return {
            "documents": [
                {
                    "doc_id": doc.doc_id,
                    "filename": doc.filename or doc.doc_id,
                    "status": doc.status,
                    "processing_stage": doc.processing_stage,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                }
                for doc in docs
            ]
        }
    finally:
        db.close()


@router.get("/pdf/{doc_id}")
async def serve_pdf(doc_id: str):
    """Serve uploaded PDF for in-app viewing."""
    _validate_doc_ready(doc_id)
    # Find the file in uploads dir
    for ext in ALLOWED_EXTENSIONS:
        file_path = UPLOAD_DIR / f"{doc_id}{ext}"
        if file_path.exists():
            media = "application/pdf" if ext == ".pdf" else "application/octet-stream"
            return FileResponse(
                path=str(file_path),
                media_type=media,
                filename=f"{doc_id}{ext}",
            )
    raise HTTPException(404, "PDF file not found")

@router.get("/leaderboard")
async def leaderboard(limit: int = Query(20, ge=1, le=100)):
    return {"leaderboard": get_leaderboard(limit)}


@router.get("/score")
async def score(user_id: str = "default_user"):
    return await get_user_score(user_id)


@router.delete("/doc/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document and all data."""
    await delete_vector_index(doc_id)
    delete_bm25_index(doc_id)
    await clear_cached(doc_id)

    async with doc_locks[doc_id]:
        keys_to_remove = [k for k in llm_cache if k[0] == doc_id]
        for k in keys_to_remove:
            del llm_cache[k]

    bm25_indexes.pop(doc_id, None)

    for ext in ALLOWED_EXTENSIONS:
        file_path = UPLOAD_DIR / f"{doc_id}{ext}"
        if file_path.exists():
            file_path.unlink()

    db = SessionLocal()
    try:
        db.query(Document).filter(Document.doc_id == doc_id).delete()
        db.query(Attempt).filter(Attempt.doc_id == doc_id).delete()
        db.commit()
    finally:
        db.close()

    return {"status": "deleted", "doc_id": doc_id}


@router.get("/health")
async def health_check():
    """System health check."""
    model_loaded = get_model() is not None
    db_ok = True
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_ok = False

    return {
        "status": "ok" if (model_loaded and db_ok) else "degraded",
        "model_loaded": model_loaded,
        "db_connected": db_ok,
        "faiss_ready": True,
        "docs_in_memory": len(faiss_indexes),
        "bm25_indexes": len(bm25_indexes),
        "cached_generations": len(generated_cache),
    }


def _validate_doc_ready(doc_id: str):
    """Check that a document exists and is ready."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.doc_id == doc_id).first()
        if not doc:
            raise HTTPException(404, "Document not found")
        if doc.status == "processing":
            raise HTTPException(202, "Document is still processing. Please wait.")
        if doc.status == "failed":
            raise HTTPException(500, f"Document processing failed: {doc.error_message}")
    finally:
        db.close()
