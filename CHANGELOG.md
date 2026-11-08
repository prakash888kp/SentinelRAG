# Changelog

All notable changes to SentinelRAG are documented here.

## [0.1.0] — 2026-11-08

### Added

- **Phase 3**: Multi-hop `AgenticMultiHopRetriever`, trajectory metrics, OTel spans, `strategy=agentic|auto` on `/query`.
- **Phase 4**: Query complexity router and cost/latency Pareto benchmark (`benchmarks/pareto_points.json`).
- **Phase 5**: Red-team attacks/defenses, ASR vs hybrid-alpha sweep, `redteam-gate` CI workflow, ADR-002 security notes.
- **Phase 6**: v0.1.0 package, expanded tests (≥80% coverage), README claims table, `scripts/demo.ps1`.

### Changed

- OpenTelemetry API/SDK and matplotlib (dev) dependencies.
- Eval thresholds extended with Phase 5 defense probe gate.

### Fixed

- Benchmark runners now invoke `main()` when executed as scripts.
- Red-team `metadata_only_poison` bypasses trust_score validation via `model_construct`.
