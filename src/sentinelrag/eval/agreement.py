"""Judge vs human agreement on a calibration set."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sentinelrag.eval.judge import Judge, MockJudge


@dataclass(frozen=True, slots=True)
class AgreementReport:
    prompt_version: str
    n_samples: int
    mean_absolute_error: float
    within_0_2: float


def load_calibration(path: Path) -> tuple[str, list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = str(payload.get("judge_prompt_version", "v1"))
    samples = list(payload.get("samples", []))
    return version, samples


def judge_agreement(
    path: Path,
    *,
    judge: Judge | None = None,
) -> AgreementReport:
    version, samples = load_calibration(path)
    j = judge or MockJudge(prompt_version=version)
    if not samples:
        return AgreementReport(version, 0, 0.0, 0.0)
    abs_errors: list[float] = []
    within: list[float] = []
    for sample in samples:
        human = float(sample["human_faithfulness"])
        scored = j.faithfulness(
            context=str(sample["context"]),
            question=str(sample["question"]),
            answer=str(sample["answer"]),
        )
        err = abs(scored.score - human)
        abs_errors.append(err)
        within.append(1.0 if err <= 0.2 else 0.0)
    return AgreementReport(
        prompt_version=version,
        n_samples=len(samples),
        mean_absolute_error=sum(abs_errors) / len(abs_errors),
        within_0_2=sum(within) / len(within),
    )
