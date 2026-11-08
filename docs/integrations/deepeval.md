# DeepEval → SentinelRAG

```bash
uv run sentinelrag-gate import deepeval report.json -o build/sentinelrag-artifact.json
```

Accepts `testResults[].metrics[]` with `name` + `score`.
Fixture: `examples/import_deepeval/report.json`.
