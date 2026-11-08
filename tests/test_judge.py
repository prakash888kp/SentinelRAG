from sentinelrag.eval.agreement import judge_agreement
from sentinelrag.eval.judge import MockJudge, load_prompt
from sentinelrag.paths import project_root


def test_load_faithfulness_prompt() -> None:
    text = load_prompt("v1", "faithfulness")
    assert "{context}" in text


def test_mock_judge_scores_in_range() -> None:
    judge = MockJudge()
    scored = judge.faithfulness(
        context="SentinelRAG uses hybrid retrieval.",
        question="What retrieval?",
        answer="Hybrid retrieval is used.",
    )
    assert 0.0 <= scored.score <= 1.0


def test_judge_agreement_calibration() -> None:
    path = project_root() / "data" / "judge_calibration.json"
    report = judge_agreement(path, judge=MockJudge())
    assert report.n_samples == 5
    assert 0.0 <= report.within_0_2 <= 1.0
