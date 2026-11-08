# Security policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a vulnerability

**Please do not** open public issues for exploitable security bugs.

1. Open a **private** security advisory on GitHub
   ([Security → Advisories → Report a vulnerability](https://github.com/prakash888kp/SentinelRAG/security/advisories/new))
   when the repository is public, **or**
2. File a minimal GitHub issue that says *“security sensitive — please contact me here”*
   without exploit details until a private channel exists.

We will acknowledge reports within a reasonable window and coordinate fixes before
disclosure.

## Scope

In scope:

- Corpus poisoning bypassing ingest defenses
- Authentication/authorization issues if/when added to the API
- Secret leakage in the repository or CI logs

Out of scope (for now):

- Denial-of-service against a self-hosted demo with no auth (documented limitation)
- Attacks requiring full compromise of your cloud VM credentials

## Secret hygiene

- Never commit `.env` or API keys
- Run `uv run python scripts/verify_repo_secrets.py` before pushing
- See `docs/SECURITY_AUDIT.md` for the latest repo hygiene check
