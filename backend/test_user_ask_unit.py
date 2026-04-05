"""Unit tests for user-library Ask (no server)."""
import pytest

from app.rag import user_ask as ua


def test_cache_key_stable():
    a = ua._cache_key("user_1", "hello world")
    b = ua._cache_key("user_1", "hello world")
    c = ua._cache_key("user_2", "hello world")
    assert a == b
    assert a != c


def test_parse_llm_json():
    raw = '{"answer": "ok", "sources": [{"chunk_id": "c1", "page": 1, "section": "S"}], "confidence": "high"}'
    parsed = ua._parse_llm_json(raw)
    assert parsed["answer"] == "ok"
    assert parsed["confidence"] == "high"


def test_not_found_constant():
    assert "not found" in ua.NOT_FOUND.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
