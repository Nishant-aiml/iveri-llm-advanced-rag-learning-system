"""Background task pipeline — stage-based processing with new chunking + dual indexing.
Upgraded: uses hierarchical chunker, builds both FAISS + BM25 indexes.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from app.database import SessionLocal, Document
from app.parser.router import route_parser
from app.parser.extractors import extract_document
from app.parser.normalizer import normalize_content
from app.chunking.hierarchical import chunk_document
from app.core.course_structure import save_course_structure
from app.core.unified_hierarchy import upsert_doc_hierarchy
from app.indexing.builder import build_indexes, load_indexes
from app.indexing.vector_index import vector_index_exists
from app.state import pending_updates

logger = logging.getLogger(__name__)

STAGES = ["uploaded", "parsed", "structured", "embedded", "indexed"]


def _update_doc_status(doc_id: str, status: str = None, stage: str = None,
                       error: str = None):
    """Update document status in DB."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.doc_id == doc_id).first()
        if doc:
            if status:
                doc.status = status
            if stage:
                doc.processing_stage = stage
            if error:
                doc.error_message = error
            if status == "ready":
                doc.processed_time = datetime.now(timezone.utc)
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update doc status: {e}")
        db.rollback()
    finally:
        db.close()


def _should_run_stage(current_stage: str, target_stage: str) -> bool:
    """Check if we need to run target_stage given current progress."""
    if current_stage not in STAGES:
        return True
    return STAGES.index(current_stage) < STAGES.index(target_stage)


async def process_document_pipeline(doc_id: str, file_path: str, retry_count: int = 0):
    """Full document processing pipeline with stage tracking.

    Stages: uploaded → parsed → structured → embedded → indexed
    """
    max_retries = 1
    start_time = time.time()

    try:
        # Get current stage from DB for resume support
        db = SessionLocal()
        doc = db.query(Document).filter(Document.doc_id == doc_id).first()
        current_stage = doc.processing_stage if doc else "uploaded"
        db.close()

        ext = Path(file_path).suffix.lower()

        # --- Stage: PARSING ---
        raw_content = None
        if _should_run_stage(current_stage, "parsed"):
            logger.info(f"[{doc_id}] Stage: PARSING")
            _update_doc_status(doc_id, stage="uploaded")

            if ext == ".xlsx":
                parser_type = "excel"
            else:
                import pymupdf
                temp_doc = pymupdf.open(file_path)
                sample_text = ""
                page_count = len(temp_doc)
                for page in temp_doc:
                    sample_text += page.get_text("text")
                temp_doc.close()
                parser_type = route_parser(sample_text, page_count)

            raw_content = extract_document(file_path, parser_type)
            _update_doc_status(doc_id, stage="parsed")
            logger.info(f"[{doc_id}] Parsed with {parser_type} ({time.time()-start_time:.1f}s)")
        else:
            logger.info(f"[{doc_id}] Skipping PARSING (already at {current_stage})")

        # --- Stage: STRUCTURING ---
        normalized = None
        if _should_run_stage(current_stage, "structured"):
            logger.info(f"[{doc_id}] Stage: STRUCTURING")
            if raw_content is None:
                logger.info(f"[{doc_id}] Re-parsing for structuring (resume)")
                if ext == ".xlsx":
                    raw_content = extract_document(file_path, "excel")
                else:
                    raw_content = extract_document(file_path, "pymupdf")

            normalized = normalize_content(raw_content, doc_id)
            save_course_structure(normalized, doc_id=doc_id)
            upsert_doc_hierarchy(doc_id, normalized, subject="General Studies")
            _update_doc_status(doc_id, stage="structured")
            sec_count = len(normalized.get("sections", []))
            logger.info(f"[{doc_id}] Structured: {sec_count} sections")
        else:
            logger.info(f"[{doc_id}] Skipping STRUCTURING")

        # --- Stage: CHUNKING + EMBEDDING ---
        chunks = None
        if _should_run_stage(current_stage, "embedded"):
            logger.info(f"[{doc_id}] Stage: CHUNKING + EMBEDDING")
            if normalized is None:
                logger.info(f"[{doc_id}] Re-processing for chunking (resume)")
                if ext == ".xlsx":
                    raw_content = extract_document(file_path, "excel")
                else:
                    raw_content = extract_document(file_path, "pymupdf")
                normalized = normalize_content(raw_content, doc_id)

            # New hierarchical chunker
            chunks = chunk_document(normalized)
            _update_doc_status(doc_id, stage="embedded")
            logger.info(f"[{doc_id}] Chunked: {len(chunks)} chunks ({time.time()-start_time:.1f}s)")
        else:
            logger.info(f"[{doc_id}] Skipping CHUNKING")

        # --- Stage: DUAL INDEXING (FAISS + BM25) ---
        if _should_run_stage(current_stage, "indexed"):
            logger.info(f"[{doc_id}] Stage: DUAL INDEXING")
            if chunks is None:
                if vector_index_exists(doc_id):
                    logger.info(f"[{doc_id}] Index already on disk, loading...")
                    await load_indexes(doc_id)
                else:
                    logger.info(f"[{doc_id}] Re-processing for indexing (resume)")
                    if ext == ".xlsx":
                        raw_content = extract_document(file_path, "excel")
                    else:
                        raw_content = extract_document(file_path, "pymupdf")
                    normalized = normalize_content(raw_content, doc_id)
                    chunks = chunk_document(normalized)

            if chunks:
                # Build both FAISS + BM25 indexes
                await build_indexes(doc_id, chunks)

            _update_doc_status(doc_id, stage="indexed")
        else:
            if not vector_index_exists(doc_id):
                logger.warning(f"[{doc_id}] Stage says indexed but no files found, rebuilding...")
                if ext == ".xlsx":
                    raw_content = extract_document(file_path, "excel")
                else:
                    raw_content = extract_document(file_path, "pymupdf")
                normalized = normalize_content(raw_content, doc_id)
                chunks = chunk_document(normalized)
                await build_indexes(doc_id, chunks)

        # --- DONE ---
        _update_doc_status(doc_id, status="ready", stage="indexed")
        await load_indexes(doc_id)

        # --- AUTO-CLASSIFY into subject library ---
        try:
            from app.core.classifier import classify_document
            from app.core.library import add_to_library
            from app.core.unified_hierarchy import update_subject_title
            # Get filename from DB for library display only.
            db2 = SessionLocal()
            doc2 = db2.query(Document).filter(Document.doc_id == doc_id).first()
            doc_title = doc2.filename if doc2 and doc2.filename else doc_id
            db2.close()

            subject = await classify_document(doc_id)
            final_subject = subject if subject else "General Studies"
            if final_subject == "General":
                final_subject = "General Studies"
            add_to_library(doc_id, final_subject, doc_title)
            update_subject_title(doc_id, final_subject)
            logger.info(f"[{doc_id}] Auto-classified → '{final_subject}'")
        except Exception as e:
            logger.warning(f"[{doc_id}] Auto-classification failed (non-fatal): {e}")

        total_time = time.time() - start_time
        logger.info(f"[{doc_id}] Pipeline complete ✓ ({total_time:.1f}s)")

    except Exception as e:
        logger.error(f"[{doc_id}] Pipeline failed: {e}", exc_info=True)
        if retry_count < max_retries:
            logger.info(f"[{doc_id}] Retrying (attempt {retry_count + 1})...")
            await asyncio.sleep(1)
            await process_document_pipeline(doc_id, file_path, retry_count + 1)
        else:
            _update_doc_status(doc_id, status="failed", error=str(e))


async def flush_pending_updates():
    """Periodically flush cached gamification data to DB."""
    while True:
        await asyncio.sleep(15)
        try:
            if not pending_updates:
                continue

            db = SessionLocal()
            try:
                updates = pending_updates.copy()
                pending_updates.clear()

                for update in updates:
                    update_fn = update.get("fn")
                    if update_fn:
                        update_fn(db)

                db.commit()
                logger.debug(f"Flushed {len(updates)} pending updates to DB")
            except Exception as e:
                logger.error(f"Failed to flush updates: {e}")
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Flush loop error: {e}")
