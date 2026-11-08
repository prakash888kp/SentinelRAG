# How SentinelRAG compares

SentinelRAG is a **reference RAG service** plus **`sentinelrag-gate`** — unified supply-chain
CI with evidence bundles, SARIF/JUnit, regression baselines, and poison benchmarks.

| Capability | SentinelRAG |
|------------|-------------|
| End-to-end FastAPI + Qdrant app | Yes |
| Single CLI gate (`sentinelrag-gate run`) | Yes |
| Evidence artifact + policy-as-code | Yes |
| SARIF + JUnit + PR summary | Yes |
| Retrieval + answer quality thresholds | Yes |
| Ingest + post-retrieval poison probes | Yes |
| Adapter hook for external pipelines | Yes |
| Adaptive / agentic routing + Pareto leaderboard | Yes |
| Offline mock CI | Yes |

### Positioning one-liner

**RAG supply-chain CI:** fail the build on **retrieval**, **grounding**, and **poison defenses**
with audit artifacts — not just log lines.

### When to choose something else

- **rag-ci / EvalFlow** — you already have a custom pipeline and only need statistical PR gates
- **RAGAS** — rich offline metric suites and research comparisons
- **LlamaIndex** — broad integrations and data connectors
- **SentinelRAG** — you want a **small, forkable baseline** that encodes eval + red-team culture in CI
