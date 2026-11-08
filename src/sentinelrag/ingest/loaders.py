"""Corpus loaders."""

from __future__ import annotations

from pathlib import Path

from sentinelrag.ingest.schema import DocumentMetadata


def load_markdown_dir(corpus_dir: Path) -> list[tuple[DocumentMetadata, str]]:
    """Load ``*.md`` files as ``(metadata, body)`` pairs."""
    docs: list[tuple[DocumentMetadata, str]] = []
    for path in sorted(corpus_dir.glob("*.md")):
        stem = path.stem
        raw = path.read_text(encoding="utf-8")
        title_line = stem.replace("-", " ").title()
        if raw.startswith("# "):
            title_line = raw.splitlines()[0].lstrip("# ").strip()
        meta = DocumentMetadata(doc_id=stem, title=title_line, source=str(corpus_dir.name))
        docs.append((meta, raw))
    return docs
