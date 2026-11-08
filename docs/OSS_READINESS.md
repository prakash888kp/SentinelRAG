# OSS readiness

| Item | Status |
|------|--------|
| MIT license | Yes |
| PyPI `sentinelrag` | Published |
| CI (pytest, eval-gate, redteam, supply-chain) | Yes |
| Dependabot / CodeQL | Yes |
| SECURITY.md / CODE_OF_CONDUCT / CONTRIBUTING | Yes |
| Public corpus (original) | `data/public_corpus/` |
| Secrets scanner in CI | `scripts/verify_repo_secrets.py` |
| JSON Schemas | `schemas/` |
| Composite Action | `.github/actions/sentinelrag-gate` |
| No maintainer-only publish how-tos in tree | Yes |

Before flipping the GitHub repo to **public**: rotate any keys that ever appeared in chat/logs, confirm `.env` is untracked, enable secret scanning.
