"""Phase 1 retrieval benchmark on the mini corpus (offline, mock embedder default)."""

from __future__ import annotations

import json
from pathlib import Path

from sentinelrag.eval.phase1_retrieval import run_benchmark
from sentinelrag.paths import project_root


def _markdown_table(report: dict[str, object]) -> str:
    lines = [
        "# Phase 1 retrieval benchmark",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| embedding_model | `{report['embedding_model']}` |",
        f"| corpus_hash | `{report['corpus_hash']}` |",
        f"| seed | {report['seed']} |",
        f"| retrieval_top_k | {report['retrieval_top_k']} |",
        f"| hybrid_alpha | {report['hybrid_alpha']} |",
        "",
        "| strategy | recall@k | MRR |",
        "| --- | ---: | ---: |",
    ]
    for row in report["results"]:  # type: ignore[index]
        lines.append(
            f"| {row['strategy']} | {row['recall_at_k']:.4f} | {row['mrr']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = run_benchmark()
    out_dir: Path = project_root() / "benchmarks"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "phase1_retrieval.json"
    md_path = out_dir / "phase1_retrieval.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown_table(report), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
