"""FastAPI entrypoint: health, ingest, and retrieval-backed query."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from sentinelrag import __version__
from sentinelrag.eval.phase2_rag import run_phase2_eval
from sentinelrag.generation.llm import Message, get_llm
from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir, ingest_document_body
from sentinelrag.paths import mini_corpus_dir
from sentinelrag.retrieval.agentic import AgenticMultiHopRetriever
from sentinelrag.retrieval.embeddings import build_embedder
from sentinelrag.retrieval.reranker import build_reranker
from sentinelrag.retrieval.stores import ScoredChunk
from sentinelrag.retrieval.strategies import HybridRerankRetriever, NaiveRetriever, StrategyName
from sentinelrag.router.policy import route_query
from sentinelrag.settings import Settings, get_settings, settings_without_dotenv

ApiStrategy = StrategyName | Literal["agentic", "auto"]

HELLO_PASSAGE = {
    "doc_id": "doc-hello-001",
    "chunk_id": "chunk-hello-001",
    "text": (
        "SentinelRAG is an adaptive, attack-tested, eval-gated RAG platform. "
        "Phase 0 proves a hello query path with MockLLM and citations."
    ),
}


class HealthResponse(BaseModel):
    status: str
    version: str
    env: str
    llm_provider: str
    llm_model: str
    embedding_model: str
    reranker_model: str
    index_ready: bool


class IngestRequest(BaseModel):
    corpus_path: str | None = Field(
        default=None,
        description="Filesystem path to a markdown corpus directory",
    )
    doc_id: str | None = None
    title: str | None = None
    text: str | None = None


class IngestResponse(BaseModel):
    chunks_indexed: int
    corpus_path: str | None = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)


class Citation(BaseModel):
    doc_id: str
    chunk_id: str
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    strategy: str
    provider: str


class EvalRunResponse(BaseModel):
    mean_faithfulness: float
    mean_relevance: float
    mean_recall_at_k: float
    judge_prompt_version: str
    n_golden_items: int


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    app = FastAPI(title=cfg.app_name, version=__version__)
    app.state.settings = cfg
    app.state.index = IndexState()

    def _maybe_bootstrap_index(current: Settings) -> None:
        state: IndexState = app.state.index
        if state.is_ready():
            return
        path = mini_corpus_dir()
        if path.is_dir():
            ingest_corpus_dir(path, state, settings=current)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        current = app.state.settings
        assert isinstance(current, Settings)
        state: IndexState = app.state.index
        return HealthResponse(
            status="ok",
            version=__version__,
            env=current.env,
            llm_provider=current.llm_provider,
            llm_model=current.llm_model,
            embedding_model=current.embedding_model,
            reranker_model=current.reranker_model,
            index_ready=state.is_ready(),
        )

    @app.post("/ingest", response_model=IngestResponse)
    def ingest(body: IngestRequest) -> IngestResponse:
        current = app.state.settings
        assert isinstance(current, Settings)
        state: IndexState = app.state.index
        if body.text and body.doc_id:
            count = ingest_document_body(
                doc_id=body.doc_id,
                title=body.title or body.doc_id,
                text=body.text,
                state=state,
                settings=current,
            )
            return IngestResponse(chunks_indexed=count, corpus_path=None)
        corpus = Path(body.corpus_path) if body.corpus_path else mini_corpus_dir()
        count = ingest_corpus_dir(corpus, state, settings=current)
        return IngestResponse(chunks_indexed=count, corpus_path=str(corpus))

    @app.post("/query", response_model=QueryResponse)
    def query_post(
        body: QueryRequest,
        strategy: Annotated[ApiStrategy, Query()] = "hybrid",
    ) -> QueryResponse:
        current = app.state.settings
        assert isinstance(current, Settings)
        _maybe_bootstrap_index(current)
        state: IndexState = app.state.index
        llm = get_llm(current)

        if not state.is_ready() or state.store is None or state.embedder is None:
            prompt = (
                f"Context: {HELLO_PASSAGE['text']}\n\n"
                f"Question: {body.query}\n\n"
                "Answer using only the context."
            )
            answer = llm.complete([Message(role="user", content=prompt)])
            return QueryResponse(
                answer=answer,
                citations=[
                    Citation(
                        doc_id=HELLO_PASSAGE["doc_id"],
                        chunk_id=HELLO_PASSAGE["chunk_id"],
                        snippet=HELLO_PASSAGE["text"][:160],
                    )
                ],
                strategy="hello_stub",
                provider=llm.name,
            )

        resolved = strategy
        if strategy == "auto":
            resolved = route_query(body.query, current).strategy

        embedder = state.embedder or build_embedder(
            current.embedding_model,
            dim=current.embed_dim,
            seed=current.benchmark_seed,
        )
        hits: list[ScoredChunk]
        if resolved == "naive":
            hits = NaiveRetriever(state.store, embedder).retrieve(
                body.query, top_k=current.retrieval_top_k
            )
        elif resolved == "agentic":
            hybrid = HybridRerankRetriever(
                state.store,
                state.bm25,
                embedder,
                build_reranker(current.reranker_model),
                alpha=current.hybrid_alpha,
                chunks_by_id=state.chunks,
            )
            agent = AgenticMultiHopRetriever(hybrid, max_hops=current.agent_max_hops)
            hits = agent.retrieve(body.query, top_k=current.retrieval_top_k).chunks
            resolved = "agentic"
        else:
            hits = HybridRerankRetriever(
                state.store,
                state.bm25,
                embedder,
                build_reranker(current.reranker_model),
                alpha=current.hybrid_alpha,
                chunks_by_id=state.chunks,
            ).retrieve(body.query, top_k=current.retrieval_top_k)
            resolved = "hybrid"
        context = "\n\n".join(h.text for h in hits) if hits else HELLO_PASSAGE["text"]
        prompt = f"Context:\n{context}\n\nQuestion: {body.query}\n\nAnswer using only the context."
        answer = llm.complete([Message(role="user", content=prompt)])
        citations = [
            Citation(doc_id=h.doc_id, chunk_id=h.chunk_id, snippet=h.text[:160]) for h in hits
        ]
        if not citations:
            citations = [
                Citation(
                    doc_id=HELLO_PASSAGE["doc_id"],
                    chunk_id=HELLO_PASSAGE["chunk_id"],
                    snippet=HELLO_PASSAGE["text"][:160],
                )
            ]
        return QueryResponse(
            answer=answer,
            citations=citations,
            strategy=resolved,
            provider=llm.name,
        )

    @app.post("/eval/run", response_model=EvalRunResponse)
    def eval_run() -> EvalRunResponse:
        current = app.state.settings
        assert isinstance(current, Settings)
        offline = settings_without_dotenv(
            llm_provider="mock",
            embedding_model="mock-embedder",
            reranker_model="mock-reranker",
            vector_store_backend="memory",
            env=current.env,
        )
        report = run_phase2_eval(settings=offline)
        return EvalRunResponse(
            mean_faithfulness=float(report["mean_faithfulness"]),
            mean_relevance=float(report["mean_relevance"]),
            mean_recall_at_k=float(report["mean_recall_at_k"]),
            judge_prompt_version=str(report["judge_prompt_version"]),
            n_golden_items=int(report["n_golden_items"]),
        )

    return app


app = create_app()


def main() -> None:
    """CLI entry for `uv run sentinelrag` / uvicorn."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "sentinelrag.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
