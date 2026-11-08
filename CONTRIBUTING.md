# Contributing

SentinelRAG optimizes for **reproducible supply-chain gates**. Keep benchmarks and tests offline-friendly.

## Setup

```bash
git clone https://github.com/prakash888kp/SentinelRAG.git
cd SentinelRAG
uv sync --extra dev
cp .env.example .env
uv run pytest
```

## Before a PR

```bash
uv run ruff check src tests scripts benchmarks
uv run mypy src/sentinelrag
uv run pytest
uv run sentinelrag-gate run --refresh
uv run python scripts/verify_repo_secrets.py
```

Regenerate and commit `benchmarks/*.json` when behavior changes.

## Standards

- Python 3.11+, ruff + mypy strict on `src/sentinelrag`
- No secrets in git (`.env` ignored)
- Prefer focused PRs with tests

## Releases (maintainers)

Automated CD (`.github/workflows/publish.yml`):

1. Bump `version` in `pyproject.toml` and `src/sentinelrag/__init__.py`
2. Update `CHANGELOG.md`
3. Merge to `main`
4. Tag and push:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

That single tag push: verifies version ↔ tag, builds the wheel, publishes to **PyPI**, and creates the **GitHub Release** (notes from CHANGELOG).

Dry-run build only: Actions → **publish** → Run workflow → dry_run = true.

## Community

- **Maintainer:** PRAKASH KUMAR K ([@prakash888kp](https://github.com/prakash888kp))
- **Support:** [GitHub Issues](https://github.com/prakash888kp/SentinelRAG/issues)
- `CODE_OF_CONDUCT.md` · `SECURITY.md`
