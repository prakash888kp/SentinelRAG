"""FastAPI entrypoint: /health and Phase-0 hello /query."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from sentinelrag import __version__
from sentinelrag.generation.llm import Message, get_llm
from sentinelrag.settings import Settings, get_settings

# Fixed in-memory passage for Phase 0 grounded stub (no Qdrant required for hello path).
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


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    app = FastAPI(title=cfg.app_name, version=__version__)
    app.state.settings = cfg

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        current = app.state.settings
        assert isinstance(current, Settings)
        return HealthResponse(
            status="ok",
            version=__version__,
            env=current.env,
            llm_provider=current.llm_provider,
        )

    @app.post("/query", response_model=QueryResponse)
    def query(body: QueryRequest) -> QueryResponse:
        current = app.state.settings
        assert isinstance(current, Settings)
        llm = get_llm(current)
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
