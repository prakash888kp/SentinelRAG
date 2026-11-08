"""Reranker factory + mock scoring."""

from __future__ import annotations

from sentinelrag.ingest.schema import ChunkPayload, DocumentMetadata
from sentinelrag.retrieval.reranker import MockReranker, build_reranker


def test_mock_reranker_ranks_overlap() -> None:
    meta = DocumentMetadata(doc_id="d1", title="t", source="test")
    chunks = [
        ChunkPayload(
            chunk_id="c1",
            doc_id="d1",
            text="unrelated alphabet soup",
            metadata=meta,
        ),
        ChunkPayload(
            chunk_id="c2",
            doc_id="d1",
            text="poison corpus hygiene gate",
            metadata=meta,
        ),
    ]
    ranked = MockReranker().score("poison gate", chunks)
    assert ranked[0][0] == "c2"


def test_build_reranker_mock_cached() -> None:
    a = build_reranker("mock-reranker")
    b = build_reranker("mock-reranker")
    assert a is b
