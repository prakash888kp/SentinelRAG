#!/usr/bin/env python3
"""Export Pareto + router points for static leaderboards."""

from __future__ import annotations

import json

from sentinelrag.paths import project_root


def main() -> int:
    root = project_root()
    pareto = json.loads((root / "benchmarks" / "pareto_points.json").read_text(encoding="utf-8"))
    payload = {
        "name": "SentinelRAG strategy Pareto",
        "points": pareto.get("points", []),
    }
    out = root / "benchmarks" / "leaderboard.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
