# Case study — silent RAG regression

**Problem.** A team tweaked chunk overlap. Hybrid recall looked “fine” in a notebook. Users later saw wrong citations. Separately, a trusted-looking poisoned doc inflated `trust_score` and slipped ingest.

**What SentinelRAG changes.**

1. Phase 1 golden retrieval fails the PR when recall/hit-rate drops.  
2. Phase 2 faithfulness/relevance gates catch ungrounded answers.  
3. Hygiene + metadata/lexical defenses + poison probes fail CI before vectors ship.  
4. Evidence + SARIF attach to the PR for auditors.

**Demo narrative:** `uv run sentinelrag-gate demo-poison` then `sentinelrag-gate run`.
See also [STORY.md](STORY.md) and [POISON_BENCHMARK_v1.md](POISON_BENCHMARK_v1.md).
