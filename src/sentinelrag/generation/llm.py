"""LLM provider interface + deterministic MockLLM for CI/offline."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from sentinelrag.settings import Settings, get_settings

ProviderName = Literal[
    "mock", "openai", "anthropic", "bedrock", "gemini", "azure_openai"
]


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


class GeminiProvider(LLMProvider):
    """Google Gemini via Generative Language API (httpx; no extra SDK)."""

    name: ProviderName = "gemini"

    def __init__(self, model: str, api_key: str) -> None:
        if not api_key.strip():
            msg = "GEMINI_API_KEY is required when SENTINELRAG_LLM_PROVIDER=gemini"
            raise ValueError(msg)
        self.model = model
        self._api_key = api_key

    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        system_parts: list[str] = []
        contents: list[dict[str, Any]] = []
        for message in messages:
            if message.role == "system":
                system_parts.append(message.content)
            elif message.role == "user":
                contents.append({"role": "user", "parts": [{"text": message.content}]})
            else:
                contents.append({"role": "model", "parts": [{"text": message.content}]})
        if not contents:
            contents = [{"role": "user", "parts": [{"text": ""}]}]

        body: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if system_parts:
            body["systemInstruction"] = {"parts": [{"text": "\n".join(system_parts)}]}

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models"
            f"/{self.model}:generateContent"
        )
        headers = {"x-goog-api-key": self._api_key, "Content-Type": "application/json"}
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, headers=headers, json=body)
            if response.is_error:
                # Never include request URL (may contain secrets in older clients).
                detail = response.text[:300]
                msg = f"Gemini HTTP {response.status_code} for model={self.model}: {detail}"
                raise RuntimeError(msg)
            payload = response.json()

        try:
            return str(payload["candidates"][0]["content"]["parts"][0]["text"])
        except (KeyError, IndexError, TypeError) as exc:
            msg = f"Unexpected Gemini response shape: {payload!r}"
            raise RuntimeError(msg) from exc


class OpenAIProvider(LLMProvider):
    """Sketch only — wire in a later phase unless OPENAI_API_KEY is set."""

    name: ProviderName = "openai"

    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        raise NotImplementedError("OpenAI client lands in a later phase; use gemini or MockLLM.")


class AzureOpenAIProvider(LLMProvider):
    """Optional Azure OpenAI stub — live demo track uses Gemini only."""

    name: ProviderName = "azure_openai"

    def __init__(self, settings: Settings) -> None:
        missing = [
            name
            for name, val in (
                ("AZURE_OPENAI_API_KEY", settings.azure_openai_api_key),
                ("AZURE_OPENAI_ENDPOINT", settings.azure_openai_endpoint),
                ("AZURE_OPENAI_DEPLOYMENT", settings.azure_openai_deployment),
            )
            if not (val and str(val).strip())
        ]
        if missing:
            msg = f"Missing Azure OpenAI settings: {', '.join(missing)}"
            raise ValueError(msg)
        self._settings = settings

    def complete(self, messages: Sequence[Message], *, temperature: float = 0.0) -> str:
        endpoint = str(self._settings.azure_openai_endpoint).rstrip("/")
        deployment = str(self._settings.azure_openai_deployment)
        url = (
            f"{endpoint}/openai/deployments/{deployment}/chat/completions"
            f"?api-version={self._settings.azure_openai_api_version}"
        )
        oai_messages = [{"role": m.role, "content": m.content} for m in messages]
        body = {
            "messages": oai_messages,
            "temperature": temperature,
        }
        headers = {
            "api-key": str(self._settings.azure_openai_api_key),
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
        try:
            return str(payload["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            msg = f"Unexpected Azure OpenAI response: {payload!r}"
            raise RuntimeError(msg) from exc


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
    """Factory for generation backends."""
    cfg = settings or get_settings()
    if cfg.llm_provider == "mock":
        return MockLLM(model=cfg.llm_model)
    if cfg.llm_provider == "gemini":
        return GeminiProvider(model=cfg.llm_model, api_key=cfg.gemini_api_key or "")
    if cfg.llm_provider == "azure_openai":
        return AzureOpenAIProvider(cfg)
    if cfg.llm_provider == "openai":
        return OpenAIProvider()
    if cfg.llm_provider == "anthropic":
        return AnthropicProvider()
    if cfg.llm_provider == "bedrock":
        return BedrockProvider()
    raise ValueError(f"Unknown llm_provider: {cfg.llm_provider}")
