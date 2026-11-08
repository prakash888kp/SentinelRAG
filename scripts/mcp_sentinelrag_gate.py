#!/usr/bin/env python3
"""Minimal MCP-style stdio server exposing run_gate for AI IDEs (experimental)."""

from __future__ import annotations

import json
import sys

from sentinelrag.gate.runner import run_gate


def main() -> int:
    line = sys.stdin.readline()
    if not line:
        return 0
    req = json.loads(line)
    if req.get("method") != "tools/call" or req.get("params", {}).get("name") != "run_gate":
        sys.stdout.write(json.dumps({"error": "unsupported"}) + "\n")
        return 0
    result = run_gate(refresh=bool(req.get("params", {}).get("arguments", {}).get("refresh")))
    sys.stdout.write(
        json.dumps(
            {
                "result": {
                    "passed": result.outcome.passed,
                    "violations": result.outcome.violations,
                    "out_dir": str(result.out_dir),
                }
            }
        )
        + "\n"
    )
    return 0 if result.outcome.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
