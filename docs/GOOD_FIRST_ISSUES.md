# Good first issues

Label these in GitHub when the repository is public.

| Title | Skills | Notes |
|-------|--------|-------|
| Add `sentence-transformers` public corpus benchmark script | Python, ML | Document real embedder recall vs mock on `data/public_corpus/` |
| Wire OpenAI judge behind env flag in CI | Python, eval | Keep default mock; optional `workflow_dispatch` job |
| Export GitHub Actions step summary from eval gate | YAML, Python | Mirror rag-ci style tables in `$GITHUB_STEP_SUMMARY` |
| Add HTTP rate limiting middleware (optional settings) | FastAPI | Off by default; document threat model |
| Pluggable poisoning filter registry | Python | Allow third-party filters without forking ingest |
| Improve router complexity heuristics + tests | Python | Cover multi-hop cue phrases from golden set |
| PyPI publish workflow with trusted publishing | GitHub Actions | See `docs/PUBLISHING.md` |
| Docs: 5-minute screencast script for README | Docs | No assets required in first PR |
