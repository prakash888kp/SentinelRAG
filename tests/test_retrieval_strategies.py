"""Retriever strategies with in-memory store."""

from __future__ import annotations

from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.ingest.schema import ChunkPayload, DocumentMetadata
from sentinelrag.paths import mini_corpus_dir
from sentinelrag.retrieval.embeddings import MockEmbedder
from sentinelrag.retrieval.reranker import MockReranker
from sentinelrag.retrieval.stores import InMemoryVectorStore
from sentinelrag.retrieval.strategies import HybridRerankRetriever, NaiveRetriever
from sentinelrag.settings import Settings


def test_naive_and_hybrid_on_mini_corpus() -> None:
    cfg = Settings(_env_file=None)
    state = IndexState()
    count = ingest_corpus_dir(mini_corpus_dir(), state, settings=cfg)
    assert count >= 5
    assert state.store is not None and state.embedder is not None

    naive = NaiveRetriever(state.store, state.embedder)
    hits = naive.retrieve("What is SentinelRAG?", top_k=3)
    assert hits
    assert hits[0].chunk_id.endswith("::0")

    hybrid = HybridRerankRetriever(
        state.store,
        state.bm25,
        state.embedder,
        MockReranker(),
        alpha=cfg.hybrid_alpha,
        chunks_by_id=state.chunks,
    )
    hybrid_hits = hybrid.retrieve("recall at k", top_k=3)
    assert any("04-eval" in h.chunk_id for h in hybrid_hits)


def test_in_memory_store_roundtrip() -> None:
    store = InMemoryVectorStore()
    meta = DocumentMetadata(doc_id="d1", title="T", source="test")
    chunk = ChunkPayload(chunk_id="d1::0", doc_id="d1", text="hello world", metadata=meta)
    emb = MockEmbedder()
    store.upsert([chunk], [emb.embed(chunk.text)])
    found = store.search(emb.embed("hello"), top_k=1)
    assert found[0].chunk_id == "d1::0"
