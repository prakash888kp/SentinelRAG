"""Settings validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sentinelrag.settings import Settings


def test_defaults() -> None:
    s = Settings(_env_file=None)
    assert s.app_name == "SentinelRAG"
    assert s.llm_provider == "mock"
    assert s.qdrant_url == "http://localhost:6333"
    assert s.port == 8000


def test_qdrant_url_requires_http_scheme() -> None:
    with pytest.raises(ValidationError):
        Settings(qdrant_url="localhost:6333", _env_file=None)


def test_qdrant_url_strips_trailing_slash() -> None:
    s = Settings(qdrant_url="http://qdrant:6333/", _env_file=None)
    assert s.qdrant_url == "http://qdrant:6333"


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTINELRAG_ENV", "ci")
    monkeypatch.setenv("SENTINELRAG_LLM_PROVIDER", "mock")
    s = Settings(_env_file=None)
    assert s.env == "ci"
    assert s.llm_provider == "mock"
