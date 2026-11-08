"""Repository path anchors (offline-safe; no env secrets)."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """SentinelRAG repo root (parent of ``src/``)."""
    return Path(__file__).resolve().parents[2]


def mini_corpus_dir() -> Path:
    return project_root() / "data" / "mini_corpus"


def mini_qrels_path() -> Path:
    return project_root() / "data" / "mini_qrels.json"
