#!/usr/bin/env python3
"""Run Phase 2 eval and write benchmarks/phase2_eval.json."""

from __future__ import annotations

import json

from sentinelrag.eval.phase2_rag import run_phase2_eval
from sentinelrag.paths import project_root


def main() -> int:
    report = run_phase2_eval()
    out_dir = project_root() / "benchmarks"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "phase2_eval.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out_dir / "phase2_eval.md"
    md.write_text(
        "\n".join(
            [
                "# Phase 2 RAG eval",
                "",
                f"| mean_faithfulness | {report['mean_faithfulness']} |",
                f"| mean_relevance | {report['mean_relevance']} |",
                f"| mean_recall@k | {report['mean_recall_at_k']} |",
                (
                    "| judge agreement (within 0.2) | "
                    f"{report['judge_agreement']['within_0_2_rate']} |"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
