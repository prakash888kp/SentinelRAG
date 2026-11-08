"""SARIF 2.1.0 emitter for supply-chain gate failures."""

from __future__ import annotations

import json
from pathlib import Path

from sentinelrag.gate.policy import PolicyOutcome

SARIF_VERSION = "2.1.0"


def write_sarif(outcome: PolicyOutcome, path: Path) -> None:
    rules: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    seen: set[str] = set()
    for v in outcome.violations:
        rule_id = v.get("rule", "sentinelrag.gate")
        if rule_id not in seen:
            seen.add(rule_id)
            rules.append(
                {
                    "id": rule_id,
                    "name": rule_id,
                    "shortDescription": {"text": rule_id},
                    "fullDescription": {"text": "SentinelRAG supply-chain gate rule"},
                }
            )
        results.append(
            {
                "ruleId": rule_id,
                "level": "error",
                "message": {"text": v.get("message", "")},
            }
        )
    for w in outcome.advisories:
        rule_id = w.get("rule", "sentinelrag.advisory")
        results.append(
            {
                "ruleId": rule_id,
                "level": "warning",
                "message": {"text": w.get("message", "")},
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SentinelRAG Gate",
                        "informationUri": "https://github.com/prakash888kp/SentinelRAG",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
