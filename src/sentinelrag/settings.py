"""Validated application settings (env-driven; no secrets in code)."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Provider secrets use standard env names (no SENTINELRAG_ prefix); see Field aliases.


class Settings(BaseSettings):
    """All runtime knobs for SentinelRAG."""

    model_config = SettingsConfigDict(
        env_prefix="SENTINELRAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "SentinelRAG"
    env: Literal["dev", "test", "ci", "prod"] = "dev"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "sentinelrag"

    embedding_model: str = "mock-embedder"
    reranker_model: str = "mock-reranker"
    embed_dim: int = Field(default=384, ge=8, le=4096)
    vector_store_backend: Literal["memory", "qdrant"] = "memory"

    retrieval_top_k: int = Field(default=5, ge=1, le=100)
    hybrid_alpha: float = Field(default=0.5, ge=0.0, le=1.0)
    default_retrieval_strategy: Literal["naive", "hybrid"] = "hybrid"

    chunk_size: int = Field(default=500, ge=64, le=8192)
    chunk_overlap: int = Field(default=80, ge=0, le=4096)
    eval_recall_k: int = Field(default=5, ge=1, le=50)
    chunk_strategy: Literal["fixed", "semantic", "contextual"] = "fixed"

    benchmark_seed: int = Field(default=42, ge=0)
    llm_provider: Literal[
        "mock", "openai", "anthropic", "bedrock", "gemini", "azure_openai"
    ] = "mock"
    llm_model: str = "mock-llm"

    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    azure_openai_api_key: str | None = Field(
        default=None, validation_alias="AZURE_OPENAI_API_KEY"
    )
    azure_openai_endpoint: str | None = Field(
        default=None, validation_alias="AZURE_OPENAI_ENDPOINT"
    )
    azure_openai_deployment: str | None = Field(
        default=None, validation_alias="AZURE_OPENAI_DEPLOYMENT"
    )
    azure_openai_api_version: str = Field(
        default="2024-10-21",
        validation_alias="AZURE_OPENAI_API_VERSION",
    )

    cost_budget_usd: float = Field(default=0.01, ge=0.0)
    latency_budget_ms: int = Field(default=2000, ge=1)

    @field_validator("chunk_overlap")
    @classmethod
    def _overlap_lt_chunk_size(cls, value: int, info: object) -> int:
        data = getattr(info, "data", {})
        chunk_size = data.get("chunk_size", 400)
        if value >= int(chunk_size):
            msg = "chunk_overlap must be smaller than chunk_size"
            raise ValueError(msg)
        return value

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


def settings_without_dotenv(**overrides: object) -> Settings:
    """Construct settings without reading a repo ``.env`` file (tests / benchmarks)."""
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg, arg-type]
