# Ecosystem

| Project | Relationship |
|---------|--------------|
| [promptfoo](https://promptfoo.dev) | Import eval scores into evidence |
| [Ragas](https://docs.ragas.io) | Import metric records |
| [DeepEval](https://docs.confident-ai.com) | Import test-run metrics |
| [EvalForge](https://github.com/jsdhwfmax/EvalForge) | Peer: portable evidence + gates — SentinelRAG also ships the RAG app + poison CI |
| Qdrant | Default vector store |
| GitHub Actions | Native CI + composite Action |
| SARIF / JUnit | Works with code scanning & test reporters |

SentinelRAG’s niche: **triple-gate adaptive RAG** (retrieve + ground + defend) with an offline-first OSS package.
