"""Retrieval strategies behind one interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from sentinelrag.ingest.schema import ChunkPayload
from sentinelrag.retrieval.bm25_index import BM25Index
from sentinelrag.retrieval.embeddings import Embedder
from sentinelrag.retrieval.fusion import fuse_hybrid
from sentinelrag.retrieval.reranker import Reranker
from sentinelrag.retrieval.stores import InMemoryVectorStore, ScoredChunk, VectorStore

StrategyName = Literal["naive", "hybrid"]


class Retriever(ABC):
    name: StrategyName

    @abstractmethod
    def retrieve(self, query: str, *, top_k: int) -> list[ScoredChunk]:
        """Return scored chunks for a query."""


class NaiveRetriever(Retriever):
    name: StrategyName = "naive"

    def __init__(self, store: VectorStore, embedder: Embedder) -> None:
        self._store = store
        self._embedder = embedder

    def retrieve(self, query: str, *, top_k: int) -> list[ScoredChunk]:
        vec = self._embedder.embed(query)
        return self._store.search(vec, top_k=top_k)


class HybridRerankRetriever(Retriever):
    name: StrategyName = "hybrid"

    def __init__(
        self,
        store: VectorStore,
        bm25: BM25Index,
        embedder: Embedder,
        reranker: Reranker,
        *,
        alpha: float,
        chunks_by_id: dict[str, ChunkPayload],
    ) -> None:
        self._store = store
        self._bm25 = bm25
        self._embedder = embedder
        self._reranker = reranker
        self._alpha = alpha
        self._chunks_by_id = chunks_by_id

    def retrieve(self, query: str, *, top_k: int) -> list[ScoredChunk]:
        vec = self._embedder.embed(query)
        dense_hits = self._store.search(vec, top_k=max(top_k * 3, 10))
        dense_scores = {h.chunk_id: h.score for h in dense_hits}
        sparse_scores = self._bm25.search(query, top_k=max(top_k * 3, 10))
        fused = fuse_hybrid(dense_scores, sparse_scores, alpha=self._alpha)
        candidate_ids = [cid for cid, _ in fused[: max(top_k * 3, 10)]]
        candidates = [self._chunks_by_id[cid] for cid in candidate_ids if cid in self._chunks_by_id]
        reranked = self._reranker.score(query, candidates)
        out: list[ScoredChunk] = []
        for cid, score in reranked[:top_k]:
            chunk = self._chunks_by_id[cid]
            out.append(
                ScoredChunk(chunk_id=cid, score=score, text=chunk.text, doc_id=chunk.doc_id)
            )
        return out


def build_vector_store(*, use_qdrant: bool) -> VectorStore:
    if use_qdrant:
        try:
            from sentinelrag.retrieval.stores import QdrantVectorStore

            return QdrantVectorStore()
        except Exception:
            return InMemoryVectorStore()
    return InMemoryVectorStore()
