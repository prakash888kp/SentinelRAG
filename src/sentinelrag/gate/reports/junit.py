"""JUnit XML for gate violations."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from sentinelrag.gate.evidence import EvidenceBundle
from sentinelrag.gate.policy import PolicyOutcome


def write_junit(
    outcome: PolicyOutcome,
    evidence: EvidenceBundle,
    path: Path,
    *,
    suite_name: str = "sentinelrag-gate",
) -> None:
    testsuite = ET.Element(
        "testsuite",
        name=suite_name,
        tests=str(max(1, len(outcome.violations))),
        failures=str(len(outcome.violations)),
        errors="0",
    )
    if not outcome.violations:
        case = ET.SubElement(testsuite, "testcase", name="gate", classname="sentinelrag")
        _ = case
    for v in outcome.violations:
        case = ET.SubElement(
            testsuite,
            "testcase",
            name=v.get("rule", "rule"),
            classname="sentinelrag.gate",
        )
        fail = ET.SubElement(case, "failure", message=v.get("message", ""))
        fail.text = v.get("message", "")
    for w in outcome.advisories:
        case = ET.SubElement(
            testsuite,
            "testcase",
            name=w.get("rule", "advisory"),
            classname="sentinelrag.gate",
        )
        skip = ET.SubElement(case, "skipped", message=w.get("message", ""))
        _ = skip
    tree = ET.ElementTree(testsuite)
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    _ = evidence
