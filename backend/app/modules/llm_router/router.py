"""LLM Router — dispatches to the configured provider.

Usage (in any feature module):
    from app.modules.llm_router.router import llm_router
    result = await llm_router.generate(doc_id, task_type, prompt, context)

The active provider is selected by LLM_PROVIDER env var (default: sarvam).
"""
from __future__ import annotations

import logging
import os
from typing import Any

from app.modules.llm_router.base import LLMProvider

logger = logging.getLogger(__name__)


def _load_provider(provider_name: str) -> LLMProvider:
    """Instantiate the provider class for the given name."""
    name = (provider_name or "sarvam").strip().lower()

    if name == "sarvam":
        from app.modules.llm_router.providers.sarvam import SarvamProvider
        return SarvamProvider()
    elif name == "openai":
        from app.modules.llm_router.providers.openai import OpenAIProvider
        return OpenAIProvider()
    elif name == "gemini":
        from app.modules.llm_router.providers.gemini import GeminiProvider
        return GeminiProvider()
    elif name == "deepseek":
        from app.modules.llm_router.providers.deepseek import DeepSeekProvider
        return DeepSeekProvider()
    elif name == "anthropic":
        from app.modules.llm_router.providers.anthropic import AnthropicProvider
        return AnthropicProvider()
    elif name == "groq":
        from app.modules.llm_router.providers.groq import GroqProvider
        return GroqProvider()
    elif name == "ollama":
        from app.modules.llm_router.providers.ollama import OllamaProvider
        return OllamaProvider()
    elif name == "openrouter":
        from app.modules.llm_router.providers.openrouter import OpenRouterProvider
        return OpenRouterProvider()
    else:
        logger.warning(
            "Unknown LLM_PROVIDER '%s'. Falling back to Sarvam.", name
        )
        from app.modules.llm_router.providers.sarvam import SarvamProvider
        return SarvamProvider()


class LLMRouter:
    """Universal LLM dispatch layer. Reads LLM_PROVIDER from env at startup."""

    def __init__(self):
        provider_name = os.getenv("LLM_PROVIDER", "sarvam")
        self._provider: LLMProvider = _load_provider(provider_name)
        logger.info(
            "LLMRouter initialized with provider: %s", self._provider.provider_name
        )

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    def switch_provider(self, provider_name: str) -> None:
        """Hot-switch the provider at runtime (e.g., for A/B testing)."""
        self._provider = _load_provider(provider_name)
        logger.info("LLMRouter switched to provider: %s", self._provider.provider_name)

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
        """Generate a response — dispatches to the active provider with a fallback chain."""
        active_name = self._provider.provider_name

        # Build sequence of providers to try
        providers_to_try = [active_name]
        for fallback in ["openai", "gemini", "sarvam"]:
            if fallback not in providers_to_try:
                providers_to_try.append(fallback)

        last_error = None
        for provider_name in providers_to_try:
            try:
                provider = _load_provider(provider_name)
                logger.debug("[LLMROUTER] Attempting generation via '%s'...", provider_name)
                res = await provider.generate(
                    doc_id=doc_id,
                    task_type=task_type,
                    prompt=prompt,
                    context=context,
                    stream=stream,
                    use_cache=use_cache,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    llm_variant=llm_variant,
                )
                ans = res.get("answer", "")
                # Detect error strings returned as answers from provider calls
                if (
                    ans.startswith("Error:")
                    or ans.startswith("OpenAI call failed")
                    or ans.startswith("Gemini call failed")
                    or ans.startswith("DeepSeek call failed")
                ):
                    logger.warning("[LLMROUTER] Provider '%s' returned error: %s", provider_name, ans[:100])
                    last_error = ans
                    continue

                return res
            except Exception as e:
                logger.warning("[LLMROUTER] Provider '%s' raised exception: %s", provider_name, e)
                last_error = str(e)
                continue

        return {
            "answer": f"All LLM providers in fallback chain failed. Last error: {last_error}",
            "source_chunks": [],
            "cached": False,
            "llm_model": active_name,
        }


# Singleton — import this in all feature modules
llm_router = LLMRouter()
