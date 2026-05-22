"""Unit tests — LLM Router."""
import pytest


def test_llm_router_default_provider():
    """LLM Router defaults to Sarvam when LLM_PROVIDER is unset."""
    import os
    os.environ.pop("LLM_PROVIDER", None)
    from app.modules.llm_router.router import LLMRouter
    router = LLMRouter()
    assert router.provider.provider_name == "sarvam"


def test_llm_router_switch_provider():
    """LLMRouter.switch_provider() changes the active provider."""
    from app.modules.llm_router.router import LLMRouter
    router = LLMRouter()
    # Switching to groq returns a GroqProvider
    router.switch_provider("groq")
    assert router.provider.provider_name == "groq"
    # Switch back to sarvam
    router.switch_provider("sarvam")
    assert router.provider.provider_name == "sarvam"


def test_llm_router_unknown_provider_falls_back():
    """Unknown provider name falls back to Sarvam with a warning."""
    from app.modules.llm_router.router import LLMRouter
    router = LLMRouter()
    router.switch_provider("banana_provider")
    assert router.provider.provider_name == "sarvam"


def test_llm_router_balanced_routing():
    """LLMRouter routes task_types appropriately in 'balanced' mode."""
    from app.modules.llm_router.router import LLMRouter
    router = LLMRouter()
    router.switch_provider("balanced")
    
    # "ask", "ask_user_library", "summary", "mentor" -> gemini
    assert router.route_task("ask") == "gemini"
    assert router.route_task("summary") == "gemini"
    
    # "quiz", "mock_test", "rapid_fire", "true_false", "fill_blanks" -> openai
    assert router.route_task("quiz") == "openai"
    assert router.route_task("mock_test") == "openai"
    
    # "flashcards", "weakness_advisor", "classify", "slides", "fun_facts" -> deepseek
    assert router.route_task("flashcards") == "deepseek"
    assert router.route_task("classify") == "deepseek"
    
    # Other fallback -> gemini
    assert router.route_task("random_unknown_task") == "gemini"
