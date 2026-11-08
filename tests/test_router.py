from sentinelrag.router.complexity import classify_complexity
from sentinelrag.router.policy import route_query
from sentinelrag.settings import settings_without_dotenv


def test_complexity() -> None:
    assert classify_complexity("hi") == "simple"
    assert classify_complexity("How do ingestion and eval connect in Phase 1?") == "complex"


def test_route_auto() -> None:
    decision = route_query("hello", settings_without_dotenv())
    assert decision.strategy == "naive"
    complex_q = "How do ingestion and eval pipelines connect and compare?"
    assert route_query(complex_q, settings_without_dotenv()).strategy == "agentic"
