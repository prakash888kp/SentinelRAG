"""LLM provider interface + deterministic MockLLM for CI/offline."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from sentinelrag.settings import Settings, get_settings

ProviderName = Literal["mock", "openai", "anthropic", "bedrock"]


@dataclass(frozen=True, slots=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str


class LLMProvider(ABC):
    """Shared interface for generation backends."""

    name: ProviderName

    @abstractmethod
    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        """Return a completion string for the given chat messages."""


class MockLLM(LLMProvider):
    """Scripted, deterministic replies — never calls a network API."""

    name: ProviderName = "mock"

    def __init__(self, model: str = "mock-llm") -> None:
        self.model = model

    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        _ = temperature  # Mock ignores sampling; kept for interface parity.
        user_bits = [m.content for m in messages if m.role == "user"]
        query = user_bits[-1] if user_bits else ""
        return (
            f"[mock:{self.model}] Grounded stub answer for: {query.strip() or '(empty)'}. "
            "Citations will attach from retrieval context."
        )


class OpenAIProvider(LLMProvider):
    """Sketch only — not called in Phase 0 / CI."""

    name: ProviderName = "openai"

    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        raise NotImplementedError("OpenAI client lands in a later phase; use MockLLM in CI.")


class AnthropicProvider(LLMProvider):
    """Sketch only — not called in Phase 0 / CI."""

    name: ProviderName = "anthropic"

    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        raise NotImplementedError("Anthropic client lands in a later phase; use MockLLM in CI.")


class BedrockProvider(LLMProvider):
    """Sketch only — not called in Phase 0 / CI."""

    name: ProviderName = "bedrock"

    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        raise NotImplementedError("Bedrock client lands in a later phase; use MockLLM in CI.")


def get_llm(settings: Settings | None = None) -> LLMProvider:
    """Factory: Phase 0 defaults to MockLLM; other providers are sketched."""
    cfg = settings or get_settings()
    if cfg.llm_provider == "mock":
        return MockLLM(model=cfg.llm_model)
    if cfg.llm_provider == "openai":
        return OpenAIProvider()
    if cfg.llm_provider == "anthropic":
        return AnthropicProvider()
    if cfg.llm_provider == "bedrock":
        return BedrockProvider()
    raise ValueError(f"Unknown llm_provider: {cfg.llm_provider}")
