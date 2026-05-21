"""Quiz module — routes."""
import logging
from fastapi import APIRouter, HTTPException

from app.shared.schemas.quiz import QuizStartRequest, QuizSubmitRequest
from app.modules.quizzes.service import handle_quiz_start, handle_quiz_submit

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Quizzes"])


@router.post("/quiz/start")
async def start_quiz(req: QuizStartRequest):
    """Generate a quiz — adaptive: prioritizes weak topics."""
    return await handle_quiz_start(req)


@router.post("/quiz/submit")
async def submit_quiz(req: QuizSubmitRequest):
    """Submit quiz answers — tracks topic accuracy for personalization."""
    return await handle_quiz_submit(req)
