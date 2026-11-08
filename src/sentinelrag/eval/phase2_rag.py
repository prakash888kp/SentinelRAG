"""Phase 2 end-to-end RAG eval: retrieval + generation + LLM-as-judge."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sentinelrag.eval.agreement import judge_agreement
from sentinelrag.eval.judge import MockJudge, get_judge
from sentinelrag.eval.metrics import mrr, recall_at_k
from sentinelrag.eval.phase1_retrieval import run_benchmark
from sentinelrag.generation.llm import LLMProvider, Message, get_llm
from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.paths import mini_corpus_dir, project_root
from sentinelrag.retrieval.reranker import build_reranker
from sentinelrag.retrieval.strategies import HybridRerankRetriever
from sentinelrag.settings import Settings, settings_without_dotenv


@dataclass(frozen=True, slots=True)
class GoldenItemResult:
    item_id: str
    item_type: str
    recall_at_k: float
    faithfulness: float
    relevance: float


def golden_dataset_path() -> Path:
    return project_root() / "data" / "golden_dataset.json"


def calibration_path() -> Path:
    return project_root() / "data" / "judge_calibration.json"


def _answer_question(
    llm: LLMProvider,
    *,
    context: str,
    question: str,
) -> str:
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer using only the context."
    return llm.complete([Message(role="user", content=prompt)])


def run_phase2_eval(*, settings: Settings | None = None) -> dict[str, Any]:
    cfg = settings or settings_without_dotenv(
        embedding_model="mock-embedder",
        reranker_model="mock-reranker",
        llm_provider="mock",
        vector_store_backend="memory",
    )
    golden = json.loads(golden_dataset_path().read_text(encoding="utf-8"))
    k = cfg.eval_recall_k

    state = IndexState()
    ingest_corpus_dir(mini_corpus_dir(), state, settings=cfg)
    assert state.store is not None and state.embedder is not None

    hybrid = HybridRerankRetriever(
        state.store,
        state.bm25,
        state.embedder,
        build_reranker(cfg.reranker_model),
        alpha=cfg.hybrid_alpha,
        chunks_by_id=state.chunks,
    )
    llm = get_llm(cfg)
    judge = get_judge(cfg) if cfg.llm_provider != "mock" else MockJudge()

    item_rows: list[GoldenItemResult] = []
    for item in golden["items"]:
        query = str(item["query"])
        relevant = set(item["relevant_chunk_ids"])
        hits = hybrid.retrieve(query, top_k=k)
        retrieved_ids = [h.chunk_id for h in hits]
        recall = recall_at_k(retrieved_ids, relevant, k=k)
        _ = mrr(retrieved_ids, relevant)

        context = "\n\n".join(h.text for h in hits) if hits else ""
        answer = _answer_question(llm, context=context, question=query)
        faith = judge.faithfulness(context=context, question=query, answer=answer)
        rel = judge.relevance(question=query, answer=answer)

        item_rows.append(
            GoldenItemResult(
                item_id=str(item["id"]),
                item_type=str(item["type"]),
                recall_at_k=round(recall, 4),
                faithfulness=faith.score,
                relevance=rel.score,
            )
        )

    phase1 = run_benchmark(settings=cfg, strategies=("hybrid",))
    agreement = judge_agreement(calibration_path(), judge=MockJudge())

    def _mean(field: str) -> float:
        vals = [getattr(r, field) for r in item_rows]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    return {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "judge_prompt_version": "v1",
        "llm_provider": cfg.llm_provider,
        "embedding_model": cfg.embedding_model,
        "golden_seed": golden.get("seed"),
        "n_golden_items": len(item_rows),
        "mean_recall_at_k": _mean("recall_at_k"),
        "mean_faithfulness": _mean("faithfulness"),
        "mean_relevance": _mean("relevance"),
        "items": [asdict(r) for r in item_rows],
        "phase1_hybrid_recall_at_k": phase1["results"][0]["recall_at_k"],
        "judge_agreement": {
            "n_samples": agreement.n_samples,
            "mean_absolute_error": round(agreement.mean_absolute_error, 4),
            "within_0_2_rate": round(agreement.within_0_2, 4),
        },
    }
