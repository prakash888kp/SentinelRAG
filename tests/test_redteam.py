from sentinelrag.redteam.harness import run_redteam


def test_redteam_runs() -> None:
    report = run_redteam(alpha=0.5)
    assert "attacks" in report
    assert len(report["attacks"]) == 3
