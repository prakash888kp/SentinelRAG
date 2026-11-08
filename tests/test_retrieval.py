from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.paths import mini_corpus_dir
from sentinelrag.retrieval.embeddings import MockEmbedder
from sentinelrag.retrieval.reranker import MockReranker
from sentinelrag.retrieval.stores import InMemoryVectorStore
from sentinelrag.retrieval.strategies import HybridRerankRetriever, NaiveRetriever
from sentinelrag.settings import Settings


def _index() -> IndexState:
    settings = Settings(
        embedding_model="mock-embedder",
        reranker_model="mock-reranker",
        vector_store_backend="memory",
        _env_file=None,
    )
    state = IndexState(store=InMemoryVectorStore(), embedder=MockEmbedder())
    ingest_corpus_dir(mini_corpus_dir(), state, settings=settings)
    return state


def test_naive_retrieves_chunks() -> None:
    state = _index()
    assert state.store and state.embedder
    retriever = NaiveRetriever(state.store, state.embedder)
    hits = retriever.retrieve("What is SentinelRAG?", top_k=3)
    assert hits
    assert hits[0].chunk_id


def test_hybrid_retrieves_chunks() -> None:
    state = _index()
    assert state.store and state.embedder
    hybrid = HybridRerankRetriever(
        state.store,
        state.bm25,
        state.embedder,
        MockReranker(),
        alpha=0.5,
        chunks_by_id=state.chunks,
    )
    hits = hybrid.retrieve("hybrid retrieval BM25", top_k=3)
    assert hits
