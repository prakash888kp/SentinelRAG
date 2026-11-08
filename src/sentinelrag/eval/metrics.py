"""Retrieval and grounding evaluation metrics."""

from __future__ import annotations

import re


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], *, k: int) -> float:
    if not relevant_ids:
        return 0.0
    top = set(retrieved_ids[:k])
    return len(top & relevant_ids) / len(relevant_ids)


def hit_rate_at_k(retrieved_ids: list[str], relevant_ids: set[str], *, k: int) -> float:
    """1.0 if at least one relevant id appears in top-k, else 0.0."""
    if not relevant_ids:
        return 0.0
    return 1.0 if set(retrieved_ids[:k]) & relevant_ids else 0.0


def mrr(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    for rank, cid in enumerate(retrieved_ids, start=1):
        if cid in relevant_ids:
            return 1.0 / rank
    return 0.0


_CITATION = re.compile(r"\[(?:cite|source|doc|chunk)[:\s]?([^\]]+)\]", re.IGNORECASE)


def citation_coverage(answer: str, retrieved_ids: list[str]) -> float:
    """Share of citation markers that point at retrieved chunk ids (0–1)."""
    marks = _CITATION.findall(answer)
    if not marks:
        return 0.0
    allowed = set(retrieved_ids)
    hits = sum(1 for m in marks if m.strip() in allowed)
    return hits / len(marks)
