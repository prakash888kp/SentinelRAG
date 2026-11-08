"""Ingest documents into retrieval indexes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import assert_never

from sentinelrag.ingest.chunking import (
    Chunker,
    ContextualChunker,
    FixedChunker,
    SemanticChunker,
)
from sentinelrag.ingest.filters import NoOpPoisoningFilter, PoisoningFilter
from sentinelrag.ingest.loaders import load_markdown_dir
from sentinelrag.ingest.schema import ChunkPayload
from sentinelrag.retrieval.bm25_index import BM25Index
from sentinelrag.retrieval.embeddings import Embedder, build_embedder
from sentinelrag.retrieval.stores import VectorStore
from sentinelrag.settings import Settings, get_settings


@dataclass
class IndexState:
    """In-process retrieval index (Phase 1; single-node)."""

    chunks: dict[str, ChunkPayload] = field(default_factory=dict)
    bm25: BM25Index = field(default_factory=BM25Index)
    store: VectorStore | None = None
    embedder: Embedder | None = None

    def is_ready(self) -> bool:
        return bool(self.chunks) and self.store is not None and self.embedder is not None


def build_chunker(settings: Settings, embedder: Embedder) -> Chunker:
    """Chunker from ``Settings.chunk_strategy``."""
    if settings.chunk_strategy == "fixed":
        return FixedChunker(chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
    if settings.chunk_strategy == "contextual":
        return ContextualChunker(chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
    if settings.chunk_strategy == "semantic":
        return SemanticChunker(embedder)
    raise ValueError(f"Unknown chunk_strategy: {settings.chunk_strategy}")


def ingest_corpus_dir(
    corpus_dir: Path,
    state: IndexState,
    *,
    settings: Settings | None = None,
    chunker: Chunker | None = None,
    poison_filter: PoisoningFilter | None = None,
) -> int:
    """Load, chunk, embed, and index all markdown files. Returns chunk count."""
    cfg = settings or get_settings()
    poison_filter = poison_filter or NoOpPoisoningFilter()
    embedder = build_embedder(
        cfg.embedding_model,
        dim=cfg.embed_dim,
        seed=cfg.benchmark_seed,
    )
    chunker = chunker or build_chunker(cfg, embedder)
    if state.store is None:
        from sentinelrag.retrieval.strategies import build_vector_store

        state.store = build_vector_store(use_qdrant=cfg.vector_store_backend == "qdrant")
    state.embedder = embedder
    state.chunks.clear()
    state.bm25.clear()
    state.store.clear()

    all_chunks: list[ChunkPayload] = []
    for meta, body in load_markdown_dir(corpus_dir):
        if not poison_filter.accept(meta, body):
            continue
        for chunk in chunker.chunk(meta, body):
            all_chunks.append(chunk)
            state.chunks[chunk.chunk_id] = chunk

    vectors = [embedder.embed(c.text) for c in all_chunks]
    state.store.upsert(all_chunks, vectors)
    state.bm25.add_chunks(all_chunks)
    return len(all_chunks)


def ingest_document_body(
    *,
    doc_id: str,
    title: str,
    text: str,
    state: IndexState,
    settings: Settings | None = None,
) -> int:
    """Ingest a single inline document into ``state`` (rebuilds BM25 + vectors)."""
    from sentinelrag.ingest.schema import DocumentMetadata

    cfg = settings or get_settings()
    meta = DocumentMetadata(doc_id=doc_id, title=title, source="api_body")
    poison_filter = NoOpPoisoningFilter()
    if not poison_filter.accept(meta, text):
        return 0
    embedder = build_embedder(
        cfg.embedding_model,
        dim=cfg.embed_dim,
        seed=cfg.benchmark_seed,
    )
    chunker = build_chunker(cfg, embedder)
    if state.store is None:
        from sentinelrag.retrieval.strategies import build_vector_store

        state.store = build_vector_store(use_qdrant=cfg.vector_store_backend == "qdrant")
    state.embedder = embedder
    new_chunks = chunker.chunk(meta, text)
    for chunk in new_chunks:
        state.chunks[chunk.chunk_id] = chunk
    all_chunks = list(state.chunks.values())
    vectors = [embedder.embed(c.text) for c in all_chunks]
    state.store.clear()
    state.store.upsert(all_chunks, vectors)
    state.bm25.clear()
    state.bm25.add_chunks(all_chunks)
    return len(new_chunks)
