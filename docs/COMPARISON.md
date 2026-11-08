# How SentinelRAG compares

SentinelRAG is **not** trying to replace LangChain, LlamaIndex, RAGAS, or rag-ci.
It is a **reference RAG service** where **quality and security regressions fail CI**
without stitching together three separate tools.

| Capability | SentinelRAG | RAGAS / DeepEval | rag-ci / ragbench / raggate | LangChain / LlamaIndex |
|------------|-------------|------------------|-----------------------------|-------------------------|
| End-to-end RAG API + Qdrant | Yes | Bring your own | Bring your own | Framework |
| Retrieval regression gate | Yes (`eval-gate`) | Manual integration | Core focus | DIY |
| Answer faithfulness / relevance gate | Yes (`eval-gate`) | Core focus | Optional (`--judge`) | DIY |
| **Ingest poison defense gate** | Yes (`redteam-gate`) | No | No | DIY |
| Adaptive naive / hybrid / agentic router | Yes | No | No | Patterns exist |
| Red-team attack harness in-repo | Yes | No | No | Rare |
| Offline mock CI (no API spend) | Yes | Partial | Often yes | Varies |
| PyPI / CLI eval-only tool | App + gates | Libraries | `uvx rag-ci` etc. | Ecosystem |

### Positioning one-liner

**Triple-gate adaptive RAG:** fail the build on **retrieval**, **answer quality**, or
**ingest-time poison defenses** — with routing and multi-hop in the same repo.

### When to choose something else

- **rag-ci / EvalFlow** — you already have a custom pipeline and only need statistical PR gates
- **RAGAS** — rich offline metric suites and research comparisons
- **LlamaIndex** — broad integrations and data connectors
- **SentinelRAG** — you want a **small, forkable baseline** that encodes eval + red-team culture in CI
