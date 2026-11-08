# Publishing to PyPI

Package name: **`sentinelrag`** (PyPI account: `prakash888kp`).

## Local dry run

```bash
uv sync --extra dev
uv build
uv run twine check dist/*
```

## First upload (manual token)

1. Create an API token at https://pypi.org/manage/account/token/
2. Store it in your password manager — never commit it
3. Upload:

```bash
uv publish --username __token__ --password pypi-XXXX
```

## Recommended: trusted publishing

After the GitHub repo is **public**, configure PyPI trusted publisher for
`prakash888kp/SentinelRAG` and add a `publish.yml` workflow (see PyPI docs).

## What users get

```bash
pip install sentinelrag
# or
uv add sentinelrag
```

CLI entry point: `sentinelrag` → runs the FastAPI app via uvicorn (see `pyproject.toml`).

Default installs use **mock** providers unless `.env` overrides.
