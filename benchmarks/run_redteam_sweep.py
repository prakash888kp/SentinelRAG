#!/usr/bin/env python3
"""Phase 5 ASR vs hybrid alpha sweep."""

from __future__ import annotations

import json

from sentinelrag.paths import project_root
from sentinelrag.redteam.harness import run_redteam


def main() -> int:
    rows = []
    for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]:
        report = run_redteam(alpha=alpha)
        rows.append(
            {
                "alpha": alpha,
                "mean_retrieval_asr": report["mean_retrieval_asr"],
                "mean_generation_asr": report["mean_generation_asr"],
                "defense_probe_blocked_fraction": report["defense_probe_blocked_fraction"],
            }
        )
    out = project_root() / "benchmarks" / "asr_vs_alpha.json"
    out.write_text(json.dumps({"sweep": rows}, indent=2) + "\n", encoding="utf-8")
    _plot(rows, project_root() / "benchmarks" / "asr_vs_alpha.png")
    print(f"Wrote {out}")
    return 0


def _plot(rows: list[dict[str, float]], path: object) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    alphas = [r["alpha"] for r in rows]
    asr = [r["mean_retrieval_asr"] for r in rows]
    plt.figure(figsize=(6, 4))
    plt.plot(alphas, asr, marker="o")
    plt.xlabel("Hybrid alpha (dense weight)")
    plt.ylabel("Mean retrieval ASR")
    plt.title("Attack Success Rate vs alpha")
    plt.tight_layout()
    plt.savefig(path)  # type: ignore[arg-type]
    plt.close()


if __name__ == "__main__":
    raise SystemExit(main())
