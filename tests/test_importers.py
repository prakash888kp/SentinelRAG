"""External evaluator importers."""

from __future__ import annotations

from pathlib import Path

from sentinelrag.gate.importers import import_deepeval, import_promptfoo, import_ragas
from sentinelrag.paths import project_root


def test_import_promptfoo_fixture() -> None:
    path = project_root() / "examples" / "import_promptfoo" / "results.json"
    bundle = import_promptfoo(path)
    assert bundle.metrics["promptfoo_success_rate"] == 0.9
    assert bundle.metrics["phase2_mean_faithfulness"] == 0.88


def test_import_ragas_fixture() -> None:
    path = project_root() / "examples" / "import_ragas" / "evaluation-result-records.json"
    bundle = import_ragas(path, metrics=["faithfulness", "answer_relevancy"])
    assert bundle.metrics["ragas_faithfulness"] == 0.88
    assert "phase2_mean_faithfulness" in bundle.metrics


def test_import_deepeval_fixture() -> None:
    path = project_root() / "examples" / "import_deepeval" / "report.json"
    bundle = import_deepeval(path)
    assert bundle.metrics["deepeval_faithfulness"] == 0.88
    assert Path(path).is_file()
