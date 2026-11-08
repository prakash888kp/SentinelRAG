# Repository security audit (2026-11-08)

Performed before the OSS launch pack. **Repository remains private** until the
maintainer approves `public`.

## `.env` and git history

| Check | Result |
|-------|--------|
| `.env` tracked in git? | **No** — listed in `.gitignore`, not in `git ls-files` |
| `.env` ever committed? | **No** — `git log -- .env` empty |
| Literal `AIza*` / `sk-*` keys in tracked files? | **No** |
| `GEMINI_API_KEY=` assigned values in history? | **No** — only `.env.example` placeholders |

## Remediation applied

| Item | Action |
|------|--------|
| VM public IPv4 in `docs/CHAT_MEMORY.md` | **Redacted** — use private ops notes locally |
| Subscription email in CHAT_MEMORY | **Redacted** |
| Ongoing CI guard | `scripts/verify_repo_secrets.py` in `ci.yml` |

## Historical commits

Older commits (before the OSS launch pack) may still contain **redacted operational
details** (for example a VM public IP in `docs/CHAT_MEMORY.md`). Current `master` no
longer includes those values. Before making the repository **public**, either:

- accept that history once contained infrastructure hints, or
- rewrite history with `git filter-repo` (only if you understand the force-push impact)

## Maintainer actions (recommended)

1. Rotate **Gemini** and any VM credentials if they were ever exposed outside `.env`
2. Keep production secrets only in `.env` on the host / GitHub Actions secrets
3. Re-run before going public:

```bash
uv run python scripts/verify_repo_secrets.py
```

4. After `git push` to a **public** repo, run [GitHub secret scanning](https://docs.github.com/en/code-security/secret-scanning) (enabled by default on public repos)

## Note on chat / IDE

If credentials were loaded from a local `.env` into an IDE session, that does not write
to git. Only **committed files** were audited here.
