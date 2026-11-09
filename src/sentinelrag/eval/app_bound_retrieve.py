"""App-bound Retrieve regression: exercise the *application* chunker settings.

The default MockLLM gate can pass on bundled fixture metrics while still missing
a chunk-size regression in application code. This check:

1. Runs Retrieve on the unmodified chunker config (baseline).
2. Remaps relevance by gold chunk *text* so case identity survives re-chunking.
3. Re-runs with a known harmful chunk-size change and requires recall to drop.
4. Returns evidence metadata (app_revision + chunker_config) for both legs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sentinelrag.eval.metrics import recall_at_k
from sentinelrag.eval.phase1_retrieval import load_qrels
from sentinelrag.gate.evidence import (
    EvidenceBundle,
    chunker_config_from_settings,
    resolve_app_revision,
)
from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.paths import mini_corpus_dir, mini_qrels_path, project_root
from sentinelrag.retrieval.reranker import build_reranker
from sentinelrag.retrieval.strategies import HybridRerankRetriever
from sentinelrag.settings import Settings, settings_without_dotenv


def _token_set(text: str) -> set[str]:
    return {t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if t}


def text_overlap_ratio(left: str, right: str) -> float:
    """Jaccard overlap on alphanumeric tokens (order-insensitive)."""
    a, b = _token_set(left), _token_set(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def remap_relevant_chunk_ids(
    *,
    gold_texts: list[str],
    candidate_chunks: dict[str, str],
    min_overlap: float = 0.35,
) -> set[str]:
    """Map baseline-relevant texts onto candidate chunk ids after re-chunking."""
    remapped: set[str] = set()
    for chunk_id, text in candidate_chunks.items():
        for gold in gold_texts:
            if gold in text or text in gold or text_overlap_ratio(text, gold) >= min_overlap:
                remapped.add(chunk_id)
                break
    return remapped


def _hybrid_recall_with_remap(
    *,
    settings: Settings,
    corpus_dir: Path,
    qrels: list[dict[str, Any]],
    gold_by_query: dict[str, list[str]],
    top_k: int,
) -> tuple[float, IndexState]:
    state = IndexState()
    ingest_corpus_dir(corpus_dir, state, settings=settings)
    assert state.store is not None and state.embedder is not None
    retriever = HybridRerankRetriever(
        state.store,
        state.bm25,
        state.embedder,
        build_reranker(settings.reranker_model),
        alpha=settings.hybrid_alpha,
        chunks_by_id=state.chunks,
    )
    candidate_texts = {cid: chunk.text for cid, chunk in state.chunks.items()}
    recalls: list[float] = []
    for item in qrels:
        qid = str(item["id"])
        query = str(item["query"])
        relevant = remap_relevant_chunk_ids(
            gold_texts=gold_by_query[qid],
            candidate_chunks=candidate_texts,
        )
        retrieved = [h.chunk_id for h in retriever.retrieve(query, top_k=top_k)]
        recalls.append(recall_at_k(retrieved, relevant, k=top_k) if relevant else 0.0)
    mean = sum(recalls) / len(recalls) if recalls else 0.0
    return mean, state


@dataclass(frozen=True, slots=True)
class AppBoundRetrieveResult:
    passed: bool
    baseline_recall: float
    harmful_recall: float
    baseline_chunker: dict[str, Any]
    harmful_chunker: dict[str, Any]
    app_revision: str | None
    message: str

    def to_evidence(self) -> EvidenceBundle:
        return EvidenceBundle(
            app_revision=self.app_revision,
            commit=self.app_revision,
            chunker_config=self.harmful_chunker if not self.passed else self.baseline_chunker,
            binding_mode="app",
            metrics={
                "phase1_hybrid_recall_at_k": self.harmful_recall,
                "app_bound_baseline_hybrid_recall_at_k": self.baseline_recall,
                "app_bound_harmful_hybrid_recall_at_k": self.harmful_recall,
            },
            security_probes={
                "app_bound_retrieve": {
                    "passed": self.passed,
                    "baseline_chunker": self.baseline_chunker,
                    "harmful_chunker": self.harmful_chunker,
                    "message": self.message,
                }
            },
            passed=self.passed,
            violations=(
                []
                if self.passed
                else [{"rule": "retrieve.app_bound_chunk_regression", "message": self.message}]
            ),
        )


def run_app_bound_chunk_regression(
    *,
    baseline_chunk_size: int = 500,
    baseline_overlap: int = 80,
    harmful_chunk_size: int = 64,
    harmful_overlap: int = 0,
    min_drop: float = 0.15,
    corpus_dir: Path | None = None,
    qrels_path: Path | None = None,
    root: Path | None = None,
) -> AppBoundRetrieveResult:
    """Require Retrieve to fail after a known harmful chunk-size change.

    Cases stay identity-stable via text remapping of relevant chunks.
    """
    root = root or project_root()
    corpus_dir = corpus_dir or mini_corpus_dir()
    qrels_path = qrels_path or mini_qrels_path()
    _, qrels = load_qrels(qrels_path)

    baseline_settings = settings_without_dotenv(
        embedding_model="mock-embedder",
        reranker_model="mock-reranker",
        vector_store_backend="memory",
        chunk_strategy="fixed",
        chunk_size=baseline_chunk_size,
        chunk_overlap=baseline_overlap,
    )
    baseline_state = IndexState()
    ingest_corpus_dir(corpus_dir, baseline_state, settings=baseline_settings)
    gold_by_query: dict[str, list[str]] = {}
    for item in qrels:
        texts = [
            baseline_state.chunks[cid].text
            for cid in item["relevant_chunk_ids"]
            if cid in baseline_state.chunks
        ]
        gold_by_query[str(item["id"])] = texts

    top_k = baseline_settings.retrieval_top_k
    baseline_recall, _ = _hybrid_recall_with_remap(
        settings=baseline_settings,
        corpus_dir=corpus_dir,
        qrels=qrels,
        gold_by_query=gold_by_query,
        top_k=top_k,
    )

    harmful_settings = settings_without_dotenv(
        embedding_model="mock-embedder",
        reranker_model="mock-reranker",
        vector_store_backend="memory",
        chunk_strategy="fixed",
        chunk_size=harmful_chunk_size,
        chunk_overlap=harmful_overlap,
    )
    harmful_recall, _ = _hybrid_recall_with_remap(
        settings=harmful_settings,
        corpus_dir=corpus_dir,
        qrels=qrels,
        gold_by_query=gold_by_query,
        top_k=top_k,
    )

    drop = baseline_recall - harmful_recall
    passed = drop >= min_drop and harmful_recall < baseline_recall
    baseline_chunker = chunker_config_from_settings(baseline_settings).to_dict()
    harmful_chunker = chunker_config_from_settings(harmful_settings).to_dict()
    revision = resolve_app_revision(root=root)
    if passed:
        message = (
            f"Retrieve regressed as expected after harmful chunk-size "
            f"{harmful_chunk_size} (baseline={baseline_recall:.3f}, "
            f"harmful={harmful_recall:.3f}, drop={drop:.3f})."
        )
    else:
        message = (
            f"Expected Retrieve to drop by >= {min_drop:.2f} after chunk_size "
            f"{baseline_chunk_size}->{harmful_chunk_size}; "
            f"baseline={baseline_recall:.3f}, harmful={harmful_recall:.3f}, drop={drop:.3f}."
        )
    return AppBoundRetrieveResult(
        passed=passed,
        baseline_recall=baseline_recall,
        harmful_recall=harmful_recall,
        baseline_chunker=baseline_chunker,
        harmful_chunker=harmful_chunker,
        app_revision=revision,
        message=message,
    )
