"""Chunking strategies behind one interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sentinelrag.ingest.schema import ChunkPayload, DocumentMetadata

if TYPE_CHECKING:
    from sentinelrag.retrieval.embeddings import Embedder


class Chunker(ABC):
    @abstractmethod
    def chunk(self, metadata: DocumentMetadata, text: str) -> list[ChunkPayload]:
        """Split a document into retrievable chunks."""


class FixedChunker(Chunker):
    """Fixed character windows with overlap."""

    def __init__(self, *, chunk_size: int = 500, overlap: int = 80) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, metadata: DocumentMetadata, text: str) -> list[ChunkPayload]:
        chunks: list[ChunkPayload] = []
        start = 0
        index = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append(
                    ChunkPayload(
                        chunk_id=f"{metadata.doc_id}::{index}",
                        doc_id=metadata.doc_id,
                        text=piece,
                        metadata=metadata,
                    )
                )
                index += 1
            if end >= len(text):
                break
            start = max(0, end - self.overlap)
        return chunks


class ContextualChunker(Chunker):
    """Fixed windows with a short parent context prefix on each chunk."""

    def __init__(self, *, chunk_size: int = 450, overlap: int = 60) -> None:
        self._inner = FixedChunker(chunk_size=chunk_size, overlap=overlap)

    def chunk(self, metadata: DocumentMetadata, text: str) -> list[ChunkPayload]:
        base = self._inner.chunk(metadata, text)
        prefix = f"[{metadata.title}] "
        return [
            ChunkPayload(
                chunk_id=c.chunk_id,
                doc_id=c.doc_id,
                text=prefix + c.text,
                metadata=metadata,
            )
            for c in base
        ]


class SemanticChunker(Chunker):
    """Sentence merges until embedding similarity to the next sentence drops."""

    def __init__(self, embedder: Embedder, *, similarity_floor: float = 0.25) -> None:
        self._embedder = embedder
        self.similarity_floor = similarity_floor

    def chunk(self, metadata: DocumentMetadata, text: str) -> list[ChunkPayload]:
        import numpy as np

        sentences = _split_sentences(text)
        if not sentences:
            return []
        vectors = [np.array(self._embedder.embed(s)) for s in sentences]
        groups: list[list[str]] = [[sentences[0]]]
        for idx in range(1, len(sentences)):
            prev = vectors[idx - 1]
            curr = vectors[idx]
            sim = float(np.dot(prev, curr) / (np.linalg.norm(prev) * np.linalg.norm(curr) + 1e-9))
            if sim >= self.similarity_floor:
                groups[-1].append(sentences[idx])
            else:
                groups.append([sentences[idx]])
        out: list[ChunkPayload] = []
        for i, group in enumerate(groups):
            body = " ".join(group).strip()
            if body:
                out.append(
                    ChunkPayload(
                        chunk_id=f"{metadata.doc_id}::sem-{i}",
                        doc_id=metadata.doc_id,
                        text=body,
                        metadata=metadata,
                    )
                )
        return out


def _split_sentences(text: str) -> list[str]:
    """Lightweight sentence split on punctuation."""
    import re

    parts = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    return [p.strip() for p in parts if p.strip()]
