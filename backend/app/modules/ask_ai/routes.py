"""Ask AI module — routes."""
import logging
from fastapi import APIRouter, HTTPException

from app.shared.schemas.ask import AskRequest, MentorRequest
from app.modules.ask_ai.service import handle_ask, handle_mentor

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Ask AI"])


@router.post("/ask")
async def ask_question(req: AskRequest):
    """RAG Q&A across the user's entire document library."""
    text = (req.query or req.question or "").strip()
    if not text:
        raise HTTPException(400, "Provide `query` or `question`")
    if len(text) < 3:
        raise HTTPException(400, "Please enter a valid question")
    return await handle_ask(req, text)


@router.post("/mentor")
async def mentor_chat(req: MentorRequest):
    """AI Mentor mode — context-aware chat for a document."""
    return await handle_mentor(req)
