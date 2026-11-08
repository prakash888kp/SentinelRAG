from sentinelrag.eval.phase2_rag import run_phase2_eval
from sentinelrag.settings import settings_without_dotenv


def test_run_phase2_eval_offline() -> None:
    report = run_phase2_eval(
        settings=settings_without_dotenv(
            llm_provider="mock",
            embedding_model="mock-embedder",
        )
    )
    assert report["n_golden_items"] == 5
    assert 0.0 <= report["mean_faithfulness"] <= 1.0
    assert report["judge_prompt_version"] == "v1"
