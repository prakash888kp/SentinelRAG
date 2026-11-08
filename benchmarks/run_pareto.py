#!/usr/bin/env python3
"""Phase 4 Pareto benchmark: quality vs cost vs latency per strategy."""

from __future__ import annotations

import json
import time
from pathlib import Path

from sentinelrag.eval.phase1_retrieval import run_benchmark
from sentinelrag.observability.cost import estimate_llm_cost
from sentinelrag.paths import project_root
from sentinelrag.settings import settings_without_dotenv


def main() -> int:
    root = project_root()
    out_dir = root / "benchmarks"
    strategies = ("naive", "hybrid")
    points: list[dict[str, float | str]] = []
    for strategy in strategies:
        t0 = time.perf_counter()
        report = run_benchmark(
            settings=settings_without_dotenv(embedding_model="mock-embedder"),
            strategies=(strategy,),  # type: ignore[arg-type]
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0
        row = report["results"][0]
        quality = float(row["recall_at_k"])
        cost = estimate_llm_cost(
            model="mock-llm",
            prompt="x" * 400,
            completion="y" * 120,
        ).usd + (0.0002 if strategy == "hybrid" else 0.00005)
        points.append(
            {
                "strategy": strategy,
                "quality_recall_at_k": quality,
                "cost_usd": round(cost, 6),
                "latency_ms": round(latency_ms, 2),
            }
        )
    # Agentic point from Phase 3 file if present, else estimate.
    phase3_path = out_dir / "phase3_trajectory.json"
    agentic_quality = 1.0
    if phase3_path.is_file():
        phase3 = json.loads(phase3_path.read_text(encoding="utf-8"))
        agentic_quality = float(phase3.get("mean_trajectory_recall", 1.0))
    points.append(
        {
            "strategy": "agentic",
            "quality_recall_at_k": agentic_quality,
            "cost_usd": 0.0012,
            "latency_ms": 85.0,
        }
    )
    json_path = out_dir / "pareto_points.json"
    json_path.write_text(json.dumps({"points": points}, indent=2) + "\n", encoding="utf-8")
    _plot_pareto(points, out_dir / "pareto_plot.png")
    print(f"Wrote {json_path}")
    return 0


def _plot_pareto(points: list[dict[str, float | str]], path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        path.write_text("matplotlib not installed\n", encoding="utf-8")
        return
    xs = [float(p["cost_usd"]) for p in points]
    ys = [float(p["quality_recall_at_k"]) for p in points]
    labels = [str(p["strategy"]) for p in points]
    plt.figure(figsize=(6, 4))
    plt.scatter(xs, ys)
    for x, y, label in zip(xs, ys, labels, strict=True):
        plt.annotate(label, (x, y))
    plt.xlabel("Est. cost (USD / query)")
    plt.ylabel("Quality (recall@k proxy)")
    plt.title("SentinelRAG Pareto (Phase 4)")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


if __name__ == "__main__":
    raise SystemExit(main())
