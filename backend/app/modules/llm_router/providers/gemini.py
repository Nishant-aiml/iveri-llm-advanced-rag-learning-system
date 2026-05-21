"""Gemini LLM provider — stub implementation.

Set LLM_PROVIDER=gemini and GEMINI_API_KEY in .env to activate.
"""
from __future__ import annotations

import os
from typing import Any

from app.modules.llm_router.base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini provider stub."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(
        self,
        doc_id: str,
        task_type: str,
        prompt: str,
        context: str,
        stream: bool = False,
        use_cache: bool = True,
        temperature: float | None = None,
        max_tokens: int | None = None,
        llm_variant: str | None = None,
    ) -> dict[str, Any]:
        """
        TODO: Implement Google Gemini API call.
        
        Required env vars:
            GEMINI_API_KEY — your Google AI Studio API key
            GEMINI_MODEL   — e.g. gemini-1.5-flash, gemini-1.5-pro (default: gemini-1.5-flash)
        
        Use google-generativeai SDK or httpx REST calls.
        """
        raise NotImplementedError("Gemini provider not yet implemented.")
