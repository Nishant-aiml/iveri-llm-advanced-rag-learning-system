"""User-library RAG: single entry point for AI Ask across all of a user's PDFs.

Rules: retrieve-first only; LLM sees only retrieved chunks; strict not-found handling.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from collections import defaultdict
from typing import Any

from app.config import PROMPT_VERSION
from app.database import SessionLocal, Document
from app.generators.prompts import get_prompt
from app.llm.trust import build_source_citations, compute_confidence
from app.query.expander import sanitize_query
from app.rag.llm_client import call_llm
from app.retrieval.context_filter import filter_context
from app.retrieval.hybrid import retrieve_for_task
from app.retrieval.mmr import mmr_filter
from app.state import MAX_USER_ASK_CACHE, user_ask_cache, touch_doc

logger = logging.getLogger(__name__)

NOT_FOUND = "Not found in your documents"


def _put_user_ask_cache(key: str, payload: dict) -> None:
    if key in user_ask_cache:
        user_ask_cache.pop(key, None)
    user_ask_cache[key] = payload
    while len(user_ask_cache) > MAX_USER_ASK_CACHE:
        user_ask_cache.popitem(last=False)
# RRF scores are typically small (e.g. 0.01–0.15); below this, treat as no match.
MIN_TOP_RRF = 0.008
EXTRACTIVE_RRF = 0.06
MAX_CONTEXT_TOKENS = 1100
MERGE_POOL = 28
MMR_MAX = 7


def normalize_query(raw: str) -> str | None:
    return sanitize_query(raw)


def _cache_key(user_id: str, normalized_q: str) -> str:
    h = hashlib.sha256(f"{user_id}\n{normalized_q}".encode("utf-8")).hexdigest()
    return h


def _diverse_by_doc(chunks: list[dict], max_total: int = MMR_MAX, max_per_doc: int = 3) -> list[dict]:
    """Prefer chunks from multiple documents when scores are similar."""
    if not chunks:
        return []
    out: list[dict] = []
    counts: dict[str, int] = defaultdict(int)
    for c in chunks:
        did = str(c.get("doc_id", "") or "")
        if counts[did] >= max_per_doc:
            continue
        out.append(c)
        counts[did] += 1
        if len(out) >= max_total:
            break
    if len(out) < min(3, len(chunks)):
        for c in chunks:
            if c in out:
                continue
            out.append(c)
            if len(out) >= max_total:
                break
    return out[:max_total]


async def retrieve_context(user_id: str, query: str, scope_doc_id: str | None = None) -> list[dict]:
    """Hybrid retrieval across all ready user documents; returns top chunks with doc_id set."""
    from app.api.routes import _ensure_doc_assets_ready

    db = SessionLocal()
    try:
        q = db.query(Document).filter(
            Document.user_id == user_id,
            Document.status.in_(["ready", "partially_ready"]),
        )
        if scope_doc_id:
            q = q.filter(Document.doc_id == scope_doc_id)
        docs = q.order_by(Document.created_at.desc()).all()
    finally:
        db.close()

    merged: list[dict] = []
    for d in docs:
        try:
            await _ensure_doc_assets_ready(d.doc_id)
            touch_doc(d.doc_id)
        except Exception as e:
            logger.warning("[user_ask] skip doc %s: %s", d.doc_id, e)
            continue

        try:
            part = await retrieve_for_task(d.doc_id, query, task_type="ask")
        except Exception as e:
            logger.warning("[user_ask] retrieve failed for %s: %s", d.doc_id, e)
            continue

        for c in part:
            ch = dict(c)
            ch["doc_id"] = d.doc_id
            merged.append(ch)

    merged.sort(key=lambda x: float(x.get("rrf_score", x.get("score", 0)) or 0), reverse=True)
    merged = merged[:MERGE_POOL]
    merged = mmr_filter(merged, max_chunks=MMR_MAX, similarity_threshold=0.85)
    merged = _diverse_by_doc(merged, max_total=MMR_MAX, max_per_doc=3)
    merged = filter_context(merged, max_tokens=MAX_CONTEXT_TOKENS)
    return merged


def post_filter(chunks: list[dict]) -> list[dict]:
    """Trim token budget (filter_context already ran); enforce cap."""
    if not chunks:
        return []
    return filter_context(chunks, max_tokens=MAX_CONTEXT_TOKENS)


def should_call_llm(chunks: list[dict], query: str) -> bool:
    """Skip LLM for very strong match + simple definition-style queries."""
    if not chunks:
        return True
    top = float(chunks[0].get("rrf_score", chunks[0].get("score", 0)) or 0)
    if top < EXTRACTIVE_RRF:
        return True
    q = query.lower().strip()
    simple = bool(
        re.match(r"^(what is|what are|define|definition of|meaning of|who is)\b", q)
        or (len(q.split()) <= 6 and len(q) < 80)
    )
    return not simple


def extractive_answer(chunks: list[dict], query: str) -> dict[str, Any]:
    """Cheap answer from the best chunk text (no LLM)."""
    text = (chunks[0].get("text") or "").strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    body = " ".join(sentences[:3]).strip()
    if len(body) > 900:
        body = body[:897] + "..."
    sources = _sources_payload(chunks[:3])
    return {
        "answer": body or NOT_FOUND,
        "sources": sources,
        "confidence": "medium",
        "confidence_detail": compute_confidence(
            [float(c.get("rrf_score", c.get("score", 0)) or 0) for c in chunks[:5]],
            reranker_score=0.0,
            llm_confidence="medium",
            num_chunks=len(chunks),
        ),
        "llm_skipped": True,
    }


def _sources_payload(chunks: list[dict]) -> list[dict]:
    out = []
    for c in chunks:
        out.append({
            "chunk_id": c.get("chunk_id", ""),
            "doc_id": c.get("doc_id", ""),
            "page": c.get("page", 1),
            "section": c.get("section", "") or "",
        })
    return out


def _parse_llm_json(answer: str) -> dict[str, Any] | None:
    if not answer or not answer.strip():
        return None
    cleaned = answer.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        decoder = json.JSONDecoder()
        i = cleaned.find("{")
        if i < 0:
            return None
        obj, _ = decoder.raw_decode(cleaned[i:])
        if isinstance(obj, dict) and "answer" in obj:
            return obj
    except Exception:
        pass
    return None


async def generate_answer_with_llm(
    chunks: list[dict],
    query: str,
    user_id: str,
    llm_variant: str | None,
) -> dict[str, Any]:
    """Call LLM with strict JSON-shaped prompt; only context chunks as input."""
    context_parts = []
    for i, c in enumerate(chunks, 1):
        meta = f"[doc={c.get('doc_id','')}|chunk={c.get('chunk_id','')}|page={c.get('page',1)}|section={c.get('section','')}]"
        context_parts.append(f"--- Chunk {i} {meta} ---\n{c.get('text','')}")
    context = "\n\n".join(context_parts)
    prompt = get_prompt("ask_user_library")
    user_block = f"Context:\n{context}\n\nQuestion:\n{query}\n\nRespond with ONLY valid JSON as specified in the system prompt."

    doc_key = f"userlib:{user_id}"
    t0 = time.time()
    result = await call_llm(
        doc_key,
        "ask_user_library",
        prompt,
        user_block,
        llm_variant=llm_variant,
        temperature=0.2,
    )
    llm_ms = (time.time() - t0) * 1000
    raw = (result.get("answer") or "").strip()
    parsed = _parse_llm_json(raw)
    if parsed:
        ans = (parsed.get("answer") or "").strip()
        conf_s = (parsed.get("confidence") or "medium").lower()
        if conf_s not in ("high", "medium", "low"):
            conf_s = "medium"
        src = parsed.get("sources") or []
        if isinstance(src, list):
            norm_sources = []
            for s in src:
                if isinstance(s, dict):
                    norm_sources.append({
                        "chunk_id": s.get("chunk_id", ""),
                        "doc_id": s.get("doc_id", ""),
                        "page": s.get("page", 1),
                        "section": s.get("section", "") or "",
                    })
            sources_out = norm_sources or _sources_payload(chunks)
        else:
            sources_out = _sources_payload(chunks)
        if NOT_FOUND.lower() in ans.lower() or "not found in your documents" in ans.lower():
            return {
                "answer": NOT_FOUND,
                "sources": [],
                "confidence": "low",
                "confidence_detail": compute_confidence([0.01], num_chunks=0),
                "llm_ms": llm_ms,
                "cached": result.get("cached", False),
            }
        scores = [float(c.get("rrf_score", c.get("score", 0)) or 0) for c in chunks]
        detail = compute_confidence(scores, reranker_score=0.0, llm_confidence=conf_s, num_chunks=len(chunks))
        return {
            "answer": ans,
            "sources": sources_out,
            "confidence": conf_s,
            "confidence_detail": detail,
            "llm_ms": llm_ms,
            "cached": result.get("cached", False),
        }

    # Plain text fallback — treat as answer only if not empty
    if raw and NOT_FOUND not in raw:
        detail = compute_confidence(
            [float(c.get("rrf_score", c.get("score", 0)) or 0) for c in chunks],
            llm_confidence="medium",
            num_chunks=len(chunks),
        )
        return {
            "answer": raw[:4000],
            "sources": _sources_payload(chunks),
            "confidence": detail.get("level", "medium"),
            "confidence_detail": detail,
            "llm_ms": llm_ms,
            "cached": result.get("cached", False),
        }
    return {
        "answer": NOT_FOUND,
        "sources": [],
        "confidence": "low",
        "confidence_detail": compute_confidence([0.02], num_chunks=len(chunks)),
        "llm_ms": llm_ms,
        "cached": result.get("cached", False),
    }


async def ask_ai(
    query: str,
    user_id: str,
    *,
    scope_doc_id: str | None = None,
    llm_variant: str | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Single entry point for user-library AI Ask."""
    timings: dict[str, float] = {}
    t_start = time.time()

    nq = normalize_query(query)
    if not nq:
        return {
            "answer": NOT_FOUND,
            "sources": [],
            "confidence": "low",
            "confidence_detail": compute_confidence([], num_chunks=0),
            "timings": {"total_ms": 0},
            "cached": False,
        }

    ck = _cache_key(user_id, nq)
    if use_cache and ck in user_ask_cache:
        user_ask_cache.move_to_end(ck)
        hit = dict(user_ask_cache[ck])
        hit["cached"] = True
        hit.setdefault("timings", {})["total_ms"] = round((time.time() - t_start) * 1000, 1)
        return hit

    t0 = time.time()
    chunks = await retrieve_context(user_id, nq, scope_doc_id=scope_doc_id)
    timings["retrieval_ms"] = round((time.time() - t0) * 1000, 1)

    chunks = post_filter(chunks)
    if not chunks:
        out = {
            "answer": NOT_FOUND,
            "sources": [],
            "confidence": "low",
            "confidence_detail": compute_confidence([], num_chunks=0),
            "timings": {**timings, "total_ms": round((time.time() - t_start) * 1000, 1)},
            "cached": False,
            "source_chunks": [],
        }
        if use_cache:
            _put_user_ask_cache(ck, {k: v for k, v in out.items() if k != "cached"})
        return out

    top_score = float(chunks[0].get("rrf_score", chunks[0].get("score", 0)) or 0)
    if top_score < MIN_TOP_RRF:
        out = {
            "answer": NOT_FOUND,
            "sources": [],
            "confidence": "low",
            "confidence_detail": compute_confidence([top_score], num_chunks=len(chunks)),
            "timings": {**timings, "total_ms": round((time.time() - t_start) * 1000, 1)},
            "cached": False,
            "source_chunks": [],
        }
        if use_cache:
            _put_user_ask_cache(ck, {k: v for k, v in out.items() if k != "cached"})
        return out

    if not should_call_llm(chunks, nq):
        ex = extractive_answer(chunks, nq)
        lev = ex["confidence_detail"].get("level", "medium")
        out = {
            "answer": ex["answer"],
            "sources": ex["sources"],
            "confidence": lev,
            "confidence_detail": ex["confidence_detail"],
            "timings": {
                **timings,
                "llm_ms": 0.0,
                "total_ms": round((time.time() - t_start) * 1000, 1),
            },
            "cached": False,
            "llm_skipped": True,
            "source_chunks": build_source_citations(chunks),
        }
        if use_cache:
            _put_user_ask_cache(ck, {k: v for k, v in out.items() if k != "cached"})
        return out

    gen = await generate_answer_with_llm(chunks, nq, user_id, llm_variant)
    out = {
        "answer": gen["answer"],
        "sources": gen.get("sources") or _sources_payload(chunks),
        "confidence": gen.get("confidence", "medium"),
        "confidence_detail": gen.get("confidence_detail"),
        "timings": {
            **timings,
            "llm_ms": round(gen.get("llm_ms", 0), 1),
            "total_ms": round((time.time() - t_start) * 1000, 1),
        },
        "cached": gen.get("cached", False),
        "source_chunks": build_source_citations(chunks),
    }
    if use_cache:
        _put_user_ask_cache(ck, {k: v for k, v in out.items() if k != "cached"})
    return out
