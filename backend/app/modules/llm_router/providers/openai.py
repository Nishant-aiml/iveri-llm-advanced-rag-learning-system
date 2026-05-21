"""OpenAI LLM provider — stub implementation.

Set LLM_PROVIDER=openai and OPENAI_API_KEY in .env to activate.
"""
from __future__ import annotations

import os
from typing import Any

from app.modules.llm_router.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider stub — ready for implementation."""

    @property
    def provider_name(self) -> str:
        return "openai"

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
        TODO: Implement OpenAI chat completions API call.
        
        Required env vars:
            OPENAI_API_KEY — your OpenAI API key
            OPENAI_MODEL   — e.g. gpt-4o, gpt-4o-mini (default: gpt-4o-mini)
            OPENAI_API_URL — optional base URL override
        
        Example implementation:
            import httpx
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context},
                ],
                "temperature": temperature or 0.2,
                "max_tokens": max_tokens or 4096,
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post("https://api.openai.com/v1/chat/completions", ...)
                data = resp.json()
                answer = data["choices"][0]["message"]["content"]
            return {"answer": answer, "source_chunks": [], "cached": False, "llm_model": model}
        """
        raise NotImplementedError(
            "OpenAI provider is not yet implemented. "
            "Set LLM_PROVIDER=sarvam or implement this stub."
        )
