"""Embedding backends."""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

import numpy as np


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return a dense vector for ``text``."""


class MockEmbedder(Embedder):
    """Deterministic, offline-friendly embedder for CI and benchmarks."""

    def __init__(self, *, dim: int = 384, model_name: str = "mock-embedder") -> None:
        self.dim = dim
        self.model_name = model_name

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(f"{self.model_name}:{text}".encode()).digest()
        seed = int.from_bytes(digest[:8], "little")
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dim)
        normed = vec / (np.linalg.norm(vec) + 1e-9)
        return [float(x) for x in normed]


def build_embedder(
    model_name: str,
    *,
    dim: int = 384,
    seed: int = 42,
) -> Embedder:
    """Factory: ``mock-embedder`` or optional SentenceTransformers."""
    if model_name == "mock-embedder":
        _ = seed  # Reserved for future seeded mock variants; hash stays deterministic per text.
        return MockEmbedder(dim=dim, model_name=model_name)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        msg = (
            f"Model {model_name!r} requires optional dep: "
            "uv sync --extra ml (sentence-transformers)"
        )
        raise RuntimeError(msg) from exc

    class _STEmbedder(Embedder):
        def __init__(self) -> None:
            self._model = SentenceTransformer(model_name)

        def embed(self, text: str) -> list[float]:
            vec = self._model.encode(text, normalize_embeddings=True)
            return [float(x) for x in vec]

    return _STEmbedder()
