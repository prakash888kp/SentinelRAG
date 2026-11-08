"""Import external evaluator outputs into SentinelRAG evidence bundles.

Maps promptfoo / Ragas / DeepEval score files into ``sentinelrag-evidence-v1``
without copying prompts, responses, or traces — metrics only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sentinelrag.gate.evidence import SCHEMA_ID, EvidenceBundle


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def import_promptfoo(
    path: Path,
    *,
    source_revision: str | None = None,
) -> EvidenceBundle:
    """Map promptfoo results schema v3 summary metrics into evidence."""
    data = _load(path)
    metrics: dict[str, Any] = {}
    # Common shapes: {results: {stats: {successes, failures}}} or flat summary
    results = data.get("results", data)
    stats = results.get("stats", {}) if isinstance(results, dict) else {}
    if stats:
        total = float(stats.get("successes", 0) + stats.get("failures", 0) or 1)
        metrics["promptfoo_success_rate"] = float(stats.get("successes", 0)) / total
    for key in ("faithfulness", "answer_relevancy", "context_precision", "context_recall"):
        if key in data:
            metrics[f"promptfoo_{key}"] = float(data[key])
    # Named metric bags
    for bag_name in ("namedScores", "named_scores", "scores"):
        bag = data.get(bag_name) or results.get(bag_name) if isinstance(results, dict) else None
        if isinstance(bag, dict):
            for k, v in bag.items():
                try:
                    metrics[f"promptfoo_{k}"] = float(v)
                except (TypeError, ValueError):
                    continue
    # Bridge common names into SentinelRAG policy keys when present
    if "promptfoo_faithfulness" in metrics:
        metrics.setdefault("phase2_mean_faithfulness", metrics["promptfoo_faithfulness"])
    if "promptfoo_context_recall" in metrics:
        metrics.setdefault("phase1_hybrid_recall_at_k", metrics["promptfoo_context_recall"])
    bundle = EvidenceBundle(schema=SCHEMA_ID, commit=source_revision, metrics=metrics)
    return bundle


def import_ragas(
    path: Path,
    *,
    metrics: list[str] | None = None,
    producer_version: str | None = None,
    source_revision: str | None = None,
) -> EvidenceBundle:
    """Map Ragas record-oriented JSON (list of score dicts) into evidence means."""
    data = _load(path)
    rows: list[dict[str, Any]]
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and isinstance(data.get("scores"), list):
        rows = list(data["scores"])
    else:
        rows = [data] if isinstance(data, dict) else []
    wanted = metrics or ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    sums: dict[str, float] = {m: 0.0 for m in wanted}
    counts: dict[str, int] = {m: 0 for m in wanted}
    for row in rows:
        for m in wanted:
            if m in row and row[m] is not None:
                sums[m] += float(row[m])
                counts[m] += 1
    out: dict[str, Any] = {}
    if producer_version:
        out["ragas_producer_version"] = producer_version
    for m in wanted:
        if counts[m]:
            out[f"ragas_{m}"] = sums[m] / counts[m]
    if "ragas_faithfulness" in out:
        out.setdefault("phase2_mean_faithfulness", out["ragas_faithfulness"])
    if "ragas_answer_relevancy" in out:
        out.setdefault("phase2_mean_relevance", out["ragas_answer_relevancy"])
    if "ragas_context_recall" in out:
        out.setdefault("phase1_hybrid_recall_at_k", out["ragas_context_recall"])
        out.setdefault("phase2_mean_recall_at_k", out["ragas_context_recall"])
    return EvidenceBundle(schema=SCHEMA_ID, commit=source_revision, metrics=out)


def import_deepeval(
    path: Path,
    *,
    source_revision: str | None = None,
) -> EvidenceBundle:
    """Map DeepEval JSON test-run / metric report into evidence."""
    data = _load(path)
    out: dict[str, Any] = {}
    # Flat scores
    for key, val in data.items():
        if isinstance(val, (int, float)) and key not in {"schema_version"}:
            out[f"deepeval_{key}"] = float(val)
    # testResults / test_results list with metrics
    tests = data.get("testResults") or data.get("test_results") or data.get("tests") or []
    if isinstance(tests, list) and tests:
        metric_sums: dict[str, float] = {}
        metric_counts: dict[str, int] = {}
        for t in tests:
            metrics = t.get("metrics") or t.get("metrics_data") or []
            if isinstance(metrics, dict):
                metrics = [{"name": k, "score": v} for k, v in metrics.items()]
            for m in metrics:
                name = str(m.get("name") or m.get("metric") or "score")
                score = m.get("score", m.get("value"))
                if score is None:
                    continue
                metric_sums[name] = metric_sums.get(name, 0.0) + float(score)
                metric_counts[name] = metric_counts.get(name, 0) + 1
        for name, total in metric_sums.items():
            out[f"deepeval_{name}"] = total / max(metric_counts[name], 1)
    # Bridges
    for src, dst in (
        ("deepeval_FaithfulnessMetric", "phase2_mean_faithfulness"),
        ("deepeval_faithfulness", "phase2_mean_faithfulness"),
        ("deepeval_AnswerRelevancyMetric", "phase2_mean_relevance"),
        ("deepeval_answer_relevancy", "phase2_mean_relevance"),
        ("deepeval_ContextualRecallMetric", "phase1_hybrid_recall_at_k"),
        ("deepeval_contextual_recall", "phase1_hybrid_recall_at_k"),
    ):
        if src in out:
            out.setdefault(dst, out[src])
    return EvidenceBundle(schema=SCHEMA_ID, commit=source_revision, metrics=out)
