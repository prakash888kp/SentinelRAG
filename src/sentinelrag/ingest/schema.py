"""Ingest metadata validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Validated document metadata at ingest time."""

    doc_id: str = Field(..., min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=256)
    source: str = Field(default="mini_corpus", max_length=256)
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0)


class ChunkPayload(BaseModel):
    """One retrievable chunk."""

    chunk_id: str
    doc_id: str
    text: str
    metadata: DocumentMetadata
