# Legal & copyright hygiene (maintainer guide)

Practices common in serious OSS repos so your code stays safer to publish and reuse.

## Already in this repo

| Item | Purpose |
|------|---------|
| `LICENSE` (MIT) | Grants use/modify/distribute rights; keep the notice in copies |
| `NOTICE` | Copyright holder + third-party reminder |
| `SECURITY.md` | How to report vulnerabilities privately |
| `CODE_OF_CONDUCT.md` | Community norms |
| `CONTRIBUTING.md` | How patches are accepted |
| Original corpora | Avoid shipping copyrighted third-party docs as demo data |
| `.gitignore` + secret scan | Keep keys out of git history |

## Recommended additions / habits

1. **Copyright line in LICENSE** — name a person or org (`Copyright (c) 2026 PRAKASH KUMAR K`).  
2. **SPDX identifiers** in source headers for critical files (optional but common):  
   `# SPDX-License-Identifier: MIT`  
3. **DCO or CLA** (optional) — Developer Certificate of Origin (`Signed-off-by`) or a CLA if you need stronger contributor IP assignment.  
4. **Do not commit secrets** — rotate any key that ever appeared in chat/logs; enable GitHub secret scanning when public.  
5. **Dependency licenses** — run `pip-licenses` / `uv tree` before commercial redistribution; MIT-friendly stack is intentional.  
6. **Trademark** — “SentinelRAG” as a project name; don’t claim affiliation with Google/Gemini, Qdrant, promptfoo, Ragas, or DeepEval beyond “compatible / imports scores”.  
7. **Model / API ToS** — Gemini and Hugging Face model cards have their own terms; live demos must obey those separately from MIT.  
8. **No copy-paste of proprietary eval code** — adapters map *metrics*, not vendor source.  
9. **Release tags** — GitHub Releases + CHANGELOG prove provenance of what users install.  
10. **PRIVATE → public** — audit history once before flipping visibility (filter-repo only if secrets were ever committed).

This file is guidance, not legal advice. For company use, have counsel review LICENSE + NOTICE + dependency licenses.
