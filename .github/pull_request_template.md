## Summary

- 

## Test plan

- [ ] `uv run pytest`
- [ ] `uv run ruff check src tests`
- [ ] `uv run mypy src/sentinelrag`
- [ ] Regenerated `benchmarks/*.json` if behavior changed
- [ ] `uv run python scripts/verify_repo_secrets.py`

## Gates

- [ ] No secrets / `.env` files in the diff
- [ ] CI eval thresholds updated only with justification in PR description
