# promptfoo → SentinelRAG

```bash
promptfoo eval --output build/promptfoo-results.json
uv run sentinelrag-gate import promptfoo build/promptfoo-results.json \
  --output build/sentinelrag-artifact.json \
  --source-revision "$GITHUB_SHA"
```

Expects schema v3-style JSON with `results.stats` and/or `namedScores`.
Fixture: `examples/import_promptfoo/results.json`.
