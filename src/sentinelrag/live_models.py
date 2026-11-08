"""Locked live-demo model IDs (Gemini-only generation; real ML retrieval).

CI stays on mock-embedder / mock-reranker / MockLLM — these constants are for
Azure VM / local 30–60s demos only.
"""

from __future__ import annotations

LIVE_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
# Small CE keeps warm demos under ~60s after first download.
LIVE_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LIVE_LLM_PROVIDER = "gemini"
LIVE_LLM_MODEL = "gemini-2.5-flash"
