# CI cookbook

## Fixture-bound vs app-bound

| Mode | What a green gate proves | What it does **not** prove |
| --- | --- | --- |
| **Fixture-bound** (default `sentinelrag-gate run`) | Bundled mini/public corpus + SentinelRAG reference chunker/pipeline still pass policy | That *your* application chunk-size / overlap / strategy change cannot silently regress retrieval |
| **App-bound** (`app-bound-check`, adapter, or your ingest → gate) | Chunks produced under the exercised revision + chunker config fail/pass Retrieve on the same cases | Prompt/model claims until those knobs are also in the gated path |

The original “chunk-size tweak looked fine” incident is only closed when the gate indexes **chunks from the changed application code** (or the same chunker settings), not only pre-baked fixture metrics.

`evidence.json` now stamps:

- `app_revision` — `SENTINELRAG_APP_REVISION` / `GITHUB_SHA` / local `git rev-parse HEAD`
- `chunker_config` — `{ strategy, chunk_size, chunk_overlap }`
- `binding_mode` — `fixture` | `app`

## Minimal gate job (fixture-bound)

```yaml
- uses: astral-sh/setup-uv@v5
- run: uv sync --extra dev
- run: uv run pytest -q
- run: uv run sentinelrag-gate run --refresh
```

## Composite Action

```yaml
- uses: prakash888kp/SentinelRAG/.github/actions/sentinelrag-gate@v0.2.2
  with:
    refresh: "true"
    binding-mode: fixture
    app-bound-check: "true"   # optional: prove harmful chunk-size fails Retrieve
```

## App-bound Retrieve regression (recommended integration check)

Run the unmodified chunker, then introduce a known harmful chunk-size change. Relevance is remapped by gold chunk **text** so cases stay identical across re-chunking. Retrieve must drop.

```bash
uv run sentinelrag-gate app-bound-check \
  --baseline-chunk-size 500 \
  --harmful-chunk-size 64 \
  --out .sentinelrag/app-bound
```

Artifact: `.sentinelrag/app-bound/evidence.json` includes both chunker configs + `app_revision`.

Wire it in CI **before** extending claims to prompt or model changes:

```yaml
- name: App-bound chunk regression
  run: uv run sentinelrag-gate app-bound-check
  env:
    SENTINELRAG_APP_REVISION: ${{ github.sha }}
```

Full example: [`examples/workflows/app-bound-retrieve.yml`](../examples/workflows/app-bound-retrieve.yml).

## Import foreign evals then gate

```yaml
- run: promptfoo eval --output build/pf.json
- run: uv run sentinelrag-gate import promptfoo build/pf.json -o build/artifact.json --source-revision "$GITHUB_SHA"
- run: uv run sentinelrag-gate compare build/artifact.json benchmarks/baseline_evidence.json
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Policy passed |
| 1 | Violation / failed scan / app-bound check failed |
| 2+ | Invalid args / unexpected error |

Artifacts land in `.sentinelrag/gate/` (`evidence.json`, `junit.xml`, `sarif.json`, `summary.md`).
