"""MockLLM and provider factory tests."""

from __future__ import annotations

import pytest

from sentinelrag.generation.llm import (
    AnthropicProvider,
    BedrockProvider,
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


def test_sketched_providers_raise() -> None:
    msgs = [Message(role="user", content="hi")]
    with pytest.raises(NotImplementedError):
        OpenAIProvider().complete(msgs)
    with pytest.raises(NotImplementedError):
        AnthropicProvider().complete(msgs)
    with pytest.raises(NotImplementedError):
        BedrockProvider().complete(msgs)
