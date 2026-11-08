# CI cookbook

## Minimal gate job

```yaml
- uses: astral-sh/setup-uv@v5
- run: uv sync --extra dev
- run: uv run pytest -q
- run: uv run sentinelrag-gate run --refresh
```

## Composite Action

```yaml
- uses: prakash888kp/SentinelRAG/.github/actions/sentinelrag-gate@v0.2.0
  with:
    refresh: "true"
```

## Import foreign evals then gate

```yaml
- run: promptfoo eval --output build/pf.json
- run: uv run sentinelrag-gate import promptfoo build/pf.json -o build/artifact.json
- run: uv run sentinelrag-gate compare build/artifact.json benchmarks/baseline_evidence.json
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Policy passed |
| 1 | Violation / failed scan |
| 2+ | Invalid args / unexpected error |

Artifacts land in `.sentinelrag/gate/` (`evidence.json`, `junit.xml`, `sarif.json`, `summary.md`).
