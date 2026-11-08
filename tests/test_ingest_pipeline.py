"""Ingest pipeline and inline body tests."""

from __future__ import annotations

import pytest

from sentinelrag.ingest.pipeline import (
    IndexState,
    build_chunker,
    ingest_corpus_dir,
    ingest_document_body,
)
from sentinelrag.paths import mini_corpus_dir
from sentinelrag.retrieval.embeddings import build_embedder
from sentinelrag.settings import Settings


def _test_settings(**kwargs: object) -> Settings:
    base: dict[str, object] = {
        "env": "test",
        "embedding_model": "mock-embedder",
        "llm_provider": "mock",
    }
    base.update(kwargs)
    return Settings(**base, _env_file=None)  # type: ignore[call-arg]


def test_build_chunker_strategies() -> None:
    cfg = _test_settings(chunk_strategy="contextual")
    emb = build_embedder(cfg.embedding_model, dim=cfg.embed_dim)
    chunker = build_chunker(cfg, emb)
    assert chunker.__class__.__name__ == "ContextualChunker"


def test_ingest_document_body_merges_index() -> None:
    cfg = _test_settings()
    state = IndexState()
    ingest_corpus_dir(mini_corpus_dir(), state, settings=cfg)
    before = len(state.chunks)
    added = ingest_document_body(
        doc_id="extra-doc",
        title="Extra",
        text="Additional corpus paragraph about eval gates.",
        state=state,
        settings=cfg,
    )
    assert added >= 1
    assert len(state.chunks) == before + added


def test_chunk_overlap_validator() -> None:
    with pytest.raises(ValueError, match="chunk_overlap"):
        _test_settings(chunk_size=400, chunk_overlap=400)
