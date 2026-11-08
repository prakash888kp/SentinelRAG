#!/usr/bin/env python3
"""Render clearer Pareto + ASR plots from committed JSON (for README)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
ASSETS = ROOT / "docs" / "assets"


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": "#f8fafc",
            "figure.facecolor": "#ffffff",
            "axes.edgecolor": "#94a3b8",
            "axes.labelcolor": "#0f172a",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
            "grid.color": "#e2e8f0",
            "grid.linestyle": "--",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
        }
    )


def pareto() -> Path:
    data = json.loads((BENCH / "pareto_points.json").read_text(encoding="utf-8"))
    points = data["points"]
    colors = {"naive": "#64748b", "hybrid": "#0d9488", "agentic": "#d97706"}
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=160)
    ax.grid(True, alpha=0.7)
    for p in points:
        name = str(p["strategy"])
        x, y = float(p["cost_usd"]), float(p["quality_recall_at_k"])
        ax.scatter([x], [y], s=120, color=colors.get(name, "#334155"), zorder=3)
        ax.annotate(
            name,
            (x, y),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=11,
            fontweight="bold",
            color=colors.get(name, "#334155"),
        )
    ax.set_xlabel("Estimated cost (USD / query)")
    ax.set_ylabel("Quality (recall@k)")
    ax.set_title("Strategy trade-off — quality vs cost")
    ax.set_ylim(0.80, 1.03)
    fig.tight_layout()
    out = ASSETS / "benchmark-pareto.png"
    fig.savefig(out)
    # keep benchmarks/ copy in sync
    fig.savefig(BENCH / "pareto_plot.png")
    plt.close(fig)
    return out


def asr() -> Path:
    data = json.loads((BENCH / "asr_vs_alpha.json").read_text(encoding="utf-8"))
    rows = data["sweep"]
    xs = [float(r["alpha"]) for r in rows]
    ys = [float(r["mean_retrieval_asr"]) for r in rows]
    blocked = [float(r["defense_probe_blocked_fraction"]) for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=160)
    ax.grid(True, alpha=0.7)
    ax.plot(xs, ys, marker="o", linewidth=2.4, color="#dc2626", label="Retrieval ASR (attack succeeds)")
    ax.plot(
        xs,
        blocked,
        marker="s",
        linewidth=2.0,
        color="#0d9488",
        label="Ingest defenses blocked",
    )
    ax.set_xlabel("Hybrid α (higher = more dense retrieval)")
    ax.set_ylabel("Rate")
    ax.set_title("Poison probes — ASR vs hybrid α")
    ax.set_ylim(0.55, 1.08)
    ax.legend(frameon=True, facecolor="white")
    fig.tight_layout()
    out = ASSETS / "benchmark-asr.png"
    fig.savefig(out)
    fig.savefig(BENCH / "asr_vs_alpha.png")
    plt.close(fig)
    return out


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    _style()
    print(pareto())
    print(asr())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
