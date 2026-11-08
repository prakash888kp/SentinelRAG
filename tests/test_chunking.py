"""Chunking strategy tests."""

from __future__ import annotations

from sentinelrag.ingest.chunking import ContextualChunker, FixedChunker, SemanticChunker
from sentinelrag.ingest.schema import DocumentMetadata
from sentinelrag.retrieval.embeddings import MockEmbedder


def _meta() -> DocumentMetadata:
    return DocumentMetadata(doc_id="doc-a", title="Doc A", source="test")


def test_fixed_chunker_overlap() -> None:
    text = "word " * 200
    chunks = FixedChunker(chunk_size=100, overlap=20).chunk(_meta(), text)
    assert len(chunks) > 1
    assert chunks[0].chunk_id == "doc-a::0"
    assert all(c.doc_id == "doc-a" for c in chunks)


def test_contextual_prefix() -> None:
    text = "Single chunk body with enough text."
    chunks = ContextualChunker(chunk_size=500, overlap=0).chunk(_meta(), text)
    assert len(chunks) == 1
    assert chunks[0].text.startswith("[Doc A]")


def test_semantic_groups_sentences() -> None:
    text = "Alpha sentence one. Beta sentence two! Gamma sentence three?"
    embedder = MockEmbedder()
    chunks = SemanticChunker(embedder, similarity_floor=0.99).chunk(_meta(), text)
    assert len(chunks) >= 1
    assert chunks[0].chunk_id.startswith("doc-a::sem-")
