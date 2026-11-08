"""MockLLM and provider factory tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sentinelrag.generation.llm import (
    AnthropicProvider,
    BedrockProvider,
    GeminiProvider,
    Message,
    MockLLM,
    OpenAIProvider,
    get_llm,
)
from sentinelrag.settings import Settings


def test_mock_llm_deterministic() -> None:
    llm = MockLLM(model="mock-llm")
    msgs = [Message(role="user", content="What is SentinelRAG?")]
    a = llm.complete(msgs)
    b = llm.complete(msgs)
    assert a == b
    assert "SentinelRAG" in a
    assert a.startswith("[mock:mock-llm]")


def test_get_llm_mock_default() -> None:
    settings = Settings(llm_provider="mock", llm_model="mock-llm", _env_file=None)
    llm = get_llm(settings)
    assert isinstance(llm, MockLLM)
    assert llm.name == "mock"


def test_get_llm_factory_sketches() -> None:
    assert isinstance(
        get_llm(Settings(llm_provider="openai", _env_file=None)), OpenAIProvider
    )
    assert isinstance(
        get_llm(Settings(llm_provider="anthropic", _env_file=None)), AnthropicProvider
    )
    assert isinstance(
        get_llm(Settings(llm_provider="bedrock", _env_file=None)), BedrockProvider
    )


def test_get_llm_gemini_requires_key() -> None:
    with pytest.raises(ValueError):
        get_llm(
            Settings(
                llm_provider="gemini",
                llm_model="gemini-2.0-flash",
                gemini_api_key=None,
                _env_file=None,
            )
        )


def test_get_llm_azure_openai_missing_raises() -> None:
    with pytest.raises(ValueError, match="Missing Azure OpenAI"):
        get_llm(
            Settings(
                llm_provider="azure_openai",
                llm_model="gpt-4o-mini",
                _env_file=None,
            )
        )


def test_get_llm_gemini_factory() -> None:
    llm = get_llm(
        Settings(
            llm_provider="gemini",
            llm_model="gemini-2.0-flash",
            gemini_api_key="test-key",
            _env_file=None,
        )
    )
    assert isinstance(llm, GeminiProvider)


def test_gemini_complete_parses_response() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "grounded answer"}]}}]
    }
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    llm = GeminiProvider("gemini-2.0-flash", "test-key")
    msgs = [
        Message(role="system", content="Be factual."),
        Message(role="user", content="What is SentinelRAG?"),
    ]
    with patch("sentinelrag.generation.llm.httpx.Client", return_value=mock_client):
        assert llm.complete(msgs) == "grounded answer"
    mock_client.post.assert_called_once()


def test_sketched_providers_raise() -> None:
    msgs = [Message(role="user", content="hi")]
    with pytest.raises(NotImplementedError):
        OpenAIProvider().complete(msgs)
    with pytest.raises(NotImplementedError):
        AnthropicProvider().complete(msgs)
    with pytest.raises(NotImplementedError):
        BedrockProvider().complete(msgs)
