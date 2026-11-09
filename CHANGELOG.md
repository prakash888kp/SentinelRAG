# Changelog

## [0.2.2] — 2026-11-09

### Added

- Evidence stamps: `app_revision`, `chunker_config`, `binding_mode` (`fixture` | `app`).
- `sentinelrag-gate app-bound-check` — baseline chunker vs known harmful chunk-size; Retrieve must regress on text-remapped cases.
- Composite Action inputs: `binding-mode`, `app-revision`, `app-bound-check`.
- Example workflow: `examples/workflows/app-bound-retrieve.yml`.
- CI cookbook section: fixture-bound vs app-bound (what a green gate actually protects).

## [0.2.1] — 2026-11-08

### Added

- README **live demo GIF** + SVG hero; EvalForge-style capability matrix.
- `sentinelrag-gate import` for **promptfoo / Ragas / DeepEval** score files.
- Docs suite: ARCHITECTURE, BENCHMARK, METRICS, CI_COOKBOOK, DEPLOYMENT, ECOSYSTEM, INTEROPERABILITY, CASE_STUDY, integrations/*.
- JSON Schemas under `schemas/`; richer `examples/` fixtures.

## [0.2.0] — 2026-11-08

### Added

- Pre-ingest **hygiene scanner** (`sentinelrag-gate scan`) and corpus **provenance** manifests.
- Retrieval **hit_rate@k** + **latency_ms_mean** in Phase 1 / public benchmarks and evidence.
- Citation coverage helper; expanded supply-chain gate policy.
- Dependabot, CodeQL, CODEOWNERS, labeler, release notes config.
- Poison benchmark v1, SARIF/JUnit evidence gate, composite Action (from 0.1.x line).

### Changed

- Package version **0.2.0**; README focused on install + out-of-box gate usage.
- Maintainer-complete surface — no open “good first issue” backlog documents.
- Live track: **Gemini** generation + real MiniLM cross-encoder (cached); phase checklist in `docs/PHASES.md`.
- Publish-ready cleanup: removed private Azure ops scripts/docs; SEO keywords + badges; public ADRs.

## [0.1.0] — 2026-11-08

- Phases 0–6: adaptive RAG, eval gates, red-team, OSS launch pack.
