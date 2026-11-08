"""Validated application settings (env-driven; no secrets in code)."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime knobs for SentinelRAG."""

    model_config = SettingsConfigDict(
        env_prefix="SENTINELRAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SentinelRAG"
    env: Literal["dev", "test", "ci", "prod"] = "dev"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "sentinelrag"

    embedding_model: str = "mock-embedder"
    reranker_model: str = "mock-reranker"
    llm_provider: Literal["mock", "openai", "anthropic", "bedrock"] = "mock"
    llm_model: str = "mock-llm"

    cost_budget_usd: float = Field(default=0.01, ge=0.0)
    latency_budget_ms: int = Field(default=2000, ge=1)

    @field_validator("qdrant_url")
    @classmethod
    def _qdrant_url_must_be_http(cls, value: str) -> str:
        if not (value.startswith("http://") or value.startswith("https://")):
            msg = "qdrant_url must start with http:// or https://"
            raise ValueError(msg)
        return value.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton for FastAPI dependency injection."""
    return Settings()
