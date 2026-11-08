# Contributing

Thanks for helping improve SentinelRAG. This project optimizes for **reproducible
eval gates** — please keep benchmarks and tests offline-friendly.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- Optional: Docker (Qdrant + API compose stack)

## Setup

```bash
git clone https://github.com/prakash888kp/SentinelRAG.git
cd SentinelRAG
uv sync --extra dev
cp .env.example .env   # defaults to mock providers
uv run pytest
```

## Before you open a PR

```bash
uv run ruff check src tests scripts benchmarks
uv run mypy src/sentinelrag
uv run pytest
uv run python benchmarks/run_phase1_retrieval.py
uv run python benchmarks/run_phase2_eval.py
uv run python scripts/check_eval_gate.py
uv run python scripts/verify_repo_secrets.py
```

If you change retrieval, routing, judges, or defenses, regenerate the relevant
`benchmarks/*.json` and commit the updated artifacts.

## Code style

- Match existing ruff/mypy strict settings
- Prefer small, focused PRs
- No secrets in git — `.env` is ignored; use `.env.example` placeholders only

## Community

- **Author / maintainer:** PRAKASH KUMAR K ([@prakash888kp](https://github.com/prakash888kp))
- **Support:** [GitHub Issues](https://github.com/prakash888kp/SentinelRAG/issues) only
- See `CODE_OF_CONDUCT.md` and `SECURITY.md`

## Good first issues

See `docs/GOOD_FIRST_ISSUES.md` for starter tasks we intend to label in the issue tracker.
