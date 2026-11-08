#!/usr/bin/env python3
"""Fail CI if red-team defense probes regress (Phase 5)."""

from __future__ import annotations

import json
import sys

import yaml

from sentinelrag.paths import project_root


def main() -> int:
    root = project_root()
    cfg = yaml.safe_load((root / "config" / "eval_thresholds.yaml").read_text(encoding="utf-8"))
    phase5 = cfg.get("phase5_redteam")
    if not phase5:
        print("Missing phase5_redteam in config/eval_thresholds.yaml", file=sys.stderr)
        return 1

    path = root / "benchmarks" / "asr_vs_alpha.json"
    if not path.is_file():
        print("Missing benchmarks/asr_vs_alpha.json — run benchmarks/run_redteam_sweep.py", file=sys.stderr)
        return 1

    alpha_ref = float(phase5.get("reference_alpha", 0.5))
    floor = float(phase5["defense_probe_blocked_fraction_min"])
    sweep = json.loads(path.read_text(encoding="utf-8"))["sweep"]
    row = next((r for r in sweep if r["alpha"] == alpha_ref), None)
    if row is None:
        print(f"No sweep row for alpha={alpha_ref}", file=sys.stderr)
        return 1

    blocked = float(row["defense_probe_blocked_fraction"])
    if blocked < floor:
        print(
            f"FAIL phase5 defense_probe_blocked_fraction {blocked} < {floor} (alpha={alpha_ref})",
            file=sys.stderr,
        )
        return 1

    print(f"Red-team gate passed (defense probe {blocked} at alpha={alpha_ref}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
