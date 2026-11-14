"""Extra coverage for gate CLI, adapter, and reports."""

from __future__ import annotations

from pathlib import Path

from sentinelrag.eval.golden_io import from_golden_dataset, load_jsonl
from sentinelrag.gate.adapter import bundle_from_adapter, write_adapter_template
from sentinelrag.gate.cli import build_parser
from sentinelrag.gate.reports.junit import write_junit
from sentinelrag.gate.reports.markdown import render_summary, write_markdown
from sentinelrag.gate.runner import run_gate
from sentinelrag.paths import golden_dataset_path, project_root


def test_run_gate_writes_artifacts(tmp_path: Path, monkeypatch: object) -> None:
    # noqa: ARG001 - monkeypatch reserved
    out = tmp_path / "gate-out"
    result = run_gate(out_dir=out, refresh=False)
    assert (out / "evidence.json").is_file()
    assert (out / "sarif.json").is_file()
    assert (out / "junit.xml").is_file()
    assert result.outcome.passed


def test_adapter_template(tmp_path: Path) -> None:
    path = tmp_path / "adapter.py"
    write_adapter_template(path)
    bundle = bundle_from_adapter(path)
    assert bundle.metrics["phase1_hybrid_recall_at_k"] == 0.0


def test_golden_jsonl_export(tmp_path: Path) -> None:
    out = tmp_path / "golden.jsonl"
    from_golden_dataset(golden_dataset_path(), out)
    rows = load_jsonl(out)
    assert rows
    assert "query" in rows[0]


def test_markdown_and_junit(tmp_path: Path) -> None:
    from sentinelrag.gate.evidence import collect_evidence
    from sentinelrag.gate.policy import evaluate_policy, load_policy

    ev = collect_evidence()
    outcome = evaluate_policy(ev, load_policy())
    write_markdown(outcome, ev, tmp_path / "s.md")
    write_junit(outcome, ev, tmp_path / "j.xml")
    text = render_summary(outcome, ev)
    assert "SentinelRAG" in text
    assert "j.xml".replace("j.xml", "") or (tmp_path / "j.xml").is_file()


def test_cli_parser() -> None:
    parser = build_parser()
    args = parser.parse_args(["run", "--out", ".sentinelrag/gate"])
    assert args.cmd == "run"


def test_cli_version() -> None:
    from sentinelrag import __version__

    parser = build_parser()
    try:
        parser.parse_args(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("expected --version to exit 0")
    assert __version__


def test_examples_template_loads() -> None:
    template = project_root() / "examples" / "adapter_template.py"
    bundle = bundle_from_adapter(template)
    assert bundle.metrics["phase1_hybrid_recall_at_k"] == 0.95
