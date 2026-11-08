from sentinelrag.ingest.pipeline import IndexState, build_chunker, ingest_document_body
from sentinelrag.retrieval.embeddings import MockEmbedder
from sentinelrag.settings import Settings


def test_ingest_document_body_and_contextual_chunker() -> None:
    settings = Settings(
        chunk_strategy="contextual",
        embedding_model="mock-embedder",
        vector_store_backend="memory",
        _env_file=None,
    )
    state = IndexState()
    embedder = MockEmbedder()
    from sentinelrag.ingest.chunking import ContextualChunker

    assert isinstance(build_chunker(settings, embedder), ContextualChunker)
    count = ingest_document_body(
        doc_id="inline",
        title="Inline",
        text="Alpha sentence. Beta sentence.",
        state=state,
        settings=settings,
    )
    assert count >= 1
    assert state.is_ready()
