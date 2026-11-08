from sentinelrag.eval.trajectory import RetrievalHop, trajectory_recall, trajectory_usefulness
from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.paths import mini_corpus_dir
from sentinelrag.retrieval.agentic import AgenticMultiHopRetriever
from sentinelrag.retrieval.reranker import MockReranker
from sentinelrag.retrieval.strategies import HybridRerankRetriever
from sentinelrag.settings import settings_without_dotenv


def test_agentic_multi_hop() -> None:
    cfg = settings_without_dotenv(embedding_model="mock-embedder", agent_max_hops=2)
    state = IndexState()
    ingest_corpus_dir(mini_corpus_dir(), state, settings=cfg)
    assert state.store and state.embedder
    hybrid = HybridRerankRetriever(
        state.store,
        state.bm25,
        state.embedder,
        MockReranker(),
        alpha=0.5,
        chunks_by_id=state.chunks,
    )
    result = AgenticMultiHopRetriever(hybrid, max_hops=2).retrieve(
        "How do security defenses relate to eval?", top_k=3
    )
    assert len(result.hops) >= 1
    assert result.chunks


def test_trajectory_usefulness() -> None:
    hops = [
        RetrievalHop(0, "q", ["a"], 0.5),
        RetrievalHop(1, "q2", ["b"], 0.6),
    ]
    assert trajectory_usefulness(hops) == 1.0
    assert trajectory_usefulness([]) == 0.0
    assert trajectory_recall(hops, {"a", "b"}) == 1.0
