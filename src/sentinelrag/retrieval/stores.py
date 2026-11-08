"""Vector stores for dense retrieval."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np

from sentinelrag.ingest.schema import ChunkPayload
from sentinelrag.settings import Settings, get_settings


@dataclass(frozen=True, slots=True)
class ScoredChunk:
    chunk_id: str
    score: float
    text: str
    doc_id: str


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, chunks: list[ChunkPayload], vectors: list[list[float]]) -> None:
        """Index chunks with precomputed vectors."""

    @abstractmethod
    def clear(self) -> None:
        """Drop all indexed chunks."""

    @abstractmethod
    def search(self, query_vector: list[float], *, top_k: int) -> list[ScoredChunk]:
        """Cosine similarity search."""


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._chunks: dict[str, ChunkPayload] = {}
        self._vectors: dict[str, np.ndarray] = {}

    def clear(self) -> None:
        self._chunks = {}
        self._vectors = {}

    def upsert(self, chunks: list[ChunkPayload], vectors: list[list[float]]) -> None:
        for chunk, vec in zip(chunks, vectors, strict=True):
            self._chunks[chunk.chunk_id] = chunk
            self._vectors[chunk.chunk_id] = np.array(vec, dtype=np.float64)

    def search(self, query_vector: list[float], *, top_k: int) -> list[ScoredChunk]:
        if not self._vectors:
            return []
        q = np.array(query_vector, dtype=np.float64)
        qn = np.linalg.norm(q) + 1e-9
        scored: list[ScoredChunk] = []
        for cid, vec in self._vectors.items():
            sim = float(np.dot(q, vec) / (qn * (np.linalg.norm(vec) + 1e-9)))
            chunk = self._chunks[cid]
            scored.append(
                ScoredChunk(chunk_id=cid, score=sim, text=chunk.text, doc_id=chunk.doc_id)
            )
        scored.sort(key=lambda x: -x.score)
        return scored[:top_k]


class QdrantVectorStore(VectorStore):
    """Qdrant-backed store (production path on Azure VM)."""

    def __init__(self, settings: Settings | None = None) -> None:
        from qdrant_client import QdrantClient
        from qdrant_client.http import models as qmodels

        self._qmodels = qmodels
        cfg = settings or get_settings()
        self._collection = cfg.qdrant_collection
        self._client = QdrantClient(url=cfg.qdrant_url)
        self._chunks: dict[str, ChunkPayload] = {}
        self._ensure_collection(dim=384)

    def _ensure_collection(self, *, dim: int) -> None:
        qmodels = self._qmodels
        names = {c.name for c in self._client.get_collections().collections}
        if self._collection not in names:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE),
            )

    def clear(self) -> None:
        self._client.delete_collection(self._collection)
        self._chunks = {}
        self._ensure_collection(dim=384)

    def upsert(self, chunks: list[ChunkPayload], vectors: list[list[float]]) -> None:
        if chunks:
            self._ensure_collection(dim=len(vectors[0]))
        qmodels = self._qmodels
        points: list[Any] = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            self._chunks[chunk.chunk_id] = chunk
            points.append(
                qmodels.PointStruct(
                    id=_stable_point_id(chunk.chunk_id),
                    vector=vector,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "doc_id": chunk.doc_id,
                        "text": chunk.text,
                    },
                )
            )
        if points:
            self._client.upsert(collection_name=self._collection, points=points)

    def search(self, query_vector: list[float], *, top_k: int) -> list[ScoredChunk]:
        response = self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            limit=top_k,
        )
        out: list[ScoredChunk] = []
        for hit in response.points:
            payload = hit.payload or {}
            cid = str(payload.get("chunk_id", hit.id))
            cached = self._chunks.get(cid)
            text = str(payload.get("text", cached.text if cached else ""))
            score = float(hit.score) if hit.score is not None else 0.0
            out.append(
                ScoredChunk(
                    chunk_id=cid,
                    score=score,
                    text=text,
                    doc_id=str(payload.get("doc_id", "")),
                )
            )
        return out


def _stable_point_id(chunk_id: str) -> int:
    """Map string ids to a positive int for Qdrant."""
    import hashlib

    digest = hashlib.sha256(chunk_id.encode()).digest()
    return int.from_bytes(digest[:8], "big") % (2**63 - 1)
