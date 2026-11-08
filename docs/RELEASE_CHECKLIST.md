# Release checklist

1. `uv run pytest -q` and `uv run sentinelrag-gate run --refresh`  
2. Bump version in `pyproject.toml` + `src/sentinelrag/__init__.py` + CHANGELOG  
3. Commit on `master`, tag `vX.Y.Z`  
4. `gh release create vX.Y.Z --generate-notes`  
5. Build & publish wheel to PyPI (maintainer machine only — not documented in README)  
6. Update composite Action consumers to the new tag when needed  
