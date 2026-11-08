# Retrieval Stack

Retrieval supports a deterministic MockEmbedder for CI, optional SentenceTransformer
models when the `ml` extra is installed, BM25 via rank_bm25, and a MockReranker.
Hybrid search fuses dense and sparse scores with min-max normalization controlled by
`hybrid_alpha` in settings. Qdrant integration wraps the official client; tests use
an in-memory vector store so pipelines stay offline.

Naive dense retrieval returns top-k by cosine similarity; hybrid mode reranks fused
candidates before they reach the generation layer.
