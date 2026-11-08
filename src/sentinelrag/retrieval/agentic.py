"""Agentic multi-hop retrieval (small state machine; no LangGraph dependency)."""

from __future__ import annotations

from dataclasses import dataclass

from sentinelrag.eval.trajectory import RetrievalHop
from sentinelrag.observability.tracing import get_tracer
from sentinelrag.retrieval.stores import ScoredChunk
from sentinelrag.retrieval.strategies import HybridRerankRetriever


@dataclass(frozen=True, slots=True)
class AgenticResult:
    chunks: list[ScoredChunk]
    hops: list[RetrievalHop]


class AgenticMultiHopRetriever:
    """Runs up to ``max_hops`` hybrid retrievals with sub-query reformulation."""

    name = "agentic"

    def __init__(self, base: HybridRerankRetriever, *, max_hops: int = 3) -> None:
        self._base = base
        self._max_hops = max(1, max_hops)
        self._tracer = get_tracer()

    def retrieve(self, query: str, *, top_k: int) -> AgenticResult:
        merged: dict[str, ScoredChunk] = {}
        hops: list[RetrievalHop] = []
        subquery = query

        for hop_idx in range(self._max_hops):
            with self._tracer.start_as_current_span("retrieval_hop") as span:
                span.set_attribute("hop_index", hop_idx)
                span.set_attribute("subquery", subquery)
                hits = self._base.retrieve(subquery, top_k=top_k)
                chunk_ids = [h.chunk_id for h in hits]
                max_score = max((h.score for h in hits), default=0.0)
                span.set_attribute("chunk_ids", ",".join(chunk_ids))
                span.set_attribute("max_score", max_score)
                for hit in hits:
                    prev = merged.get(hit.chunk_id)
                    if prev is None or hit.score > prev.score:
                        merged[hit.chunk_id] = hit
                hops.append(
                    RetrievalHop(
                        hop_index=hop_idx,
                        subquery=subquery,
                        chunk_ids=chunk_ids,
                        max_score=max_score,
                    )
                )
                if hop_idx + 1 >= self._max_hops:
                    break
                if not hits:
                    break
                # Reformulate: bias next hop toward under-covered doc themes.
                subquery = _reformulate(query, hits, hop_idx)

        ranked = sorted(merged.values(), key=lambda h: -h.score)[:top_k]
        return AgenticResult(chunks=ranked, hops=hops)


def _reformulate(original: str, hits: list[ScoredChunk], hop: int) -> str:
    doc_hints = " ".join(sorted({h.doc_id.replace("-", " ") for h in hits[:3]}))
    return f"{original} related context: {doc_hints} hop{hop + 1}"
