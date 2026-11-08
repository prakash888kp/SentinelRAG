"""Trajectory-level retrieval scoring."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalHop:
    hop_index: int
    subquery: str
    chunk_ids: list[str]
    max_score: float


def hop_added_evidence(hop: RetrievalHop, seen_chunk_ids: set[str]) -> bool:
    return any(cid not in seen_chunk_ids for cid in hop.chunk_ids)


def trajectory_usefulness(hops: list[RetrievalHop]) -> float:
    """Fraction of hops that retrieved at least one new chunk."""
    if not hops:
        return 0.0
    seen: set[str] = set()
    useful = 0
    for hop in hops:
        if hop_added_evidence(hop, seen):
            useful += 1
        seen.update(hop.chunk_ids)
    return useful / len(hops)


def trajectory_recall(hops: list[RetrievalHop], relevant_ids: set[str]) -> float:
    """Union recall: any hop hit a relevant chunk."""
    if not relevant_ids:
        return 0.0
    found: set[str] = set()
    for hop in hops:
        found.update(hop.chunk_ids)
    return len(found & relevant_ids) / len(relevant_ids)
