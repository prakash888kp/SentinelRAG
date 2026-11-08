# Feature map

| Area | What’s in the tree |
|------|--------------------|
| API | FastAPI `/health`, `/ingest`, `/query`, `/eval/run` |
| Retrieval | Naive, hybrid (BM25 + dense), optional cross-encoder, agentic hops |
| Eval | Golden sets, judges, recall / MRR / hit-rate, trajectory metrics |
| Routing | Complexity policy + Pareto cost/latency scripts |
| Security | Hygiene scan, provenance, poison probes, red-team sweeps |
| Gate | `sentinelrag-gate` → evidence, JUnit, SARIF, policy YAML |
| Live models | Gemini 2.5 Flash · `bge-small` · MiniLM CE (CI stays mock) |

```bash
uv run pytest -q
uv run sentinelrag-gate run --refresh
```

Live stack: [DEMO.md](DEMO.md)
