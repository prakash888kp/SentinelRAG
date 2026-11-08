# Ingestion and Chunking

The ingest module loads plain text and Markdown sources, validates document metadata
with Pydantic models, and splits text using fixed-size, semantic, or contextual
chunkers. A poisoning filter interface allows red-team filters later; the default
implementation is a no-op pass-through for offline CI.

Chunk identifiers are stable per document: each chunk receives a `chunk_id` derived
from the source `doc_id` and chunk index so golden qrels stay reproducible.
