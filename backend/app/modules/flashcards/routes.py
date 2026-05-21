"""Flashcards/Generate module — routes."""
import logging
from fastapi import APIRouter, HTTPException

from app.shared.schemas.generate import GenerateRequest
from app.modules.flashcards.service import handle_generate

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Flashcards & Content"])

VALID_CONTENT_TYPES = [
    "flashcards", "summary", "slides", "fun_facts",
    "mock_test", "rapid_fire", "true_false", "fill_blanks",
]


@router.post("/generate")
async def generate(req: GenerateRequest):
    """Generate content: flashcards, summary, slides, fun_facts, etc."""
    if req.content_type not in VALID_CONTENT_TYPES:
        raise HTTPException(400, f"Invalid content type. Must be one of: {VALID_CONTENT_TYPES}")
    return await handle_generate(req)
