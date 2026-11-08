# ADR-002: Red-team scope and defense honesty

## Status

Accepted (Phase 5).

## Context

SentinelRAG must quantify poisoning ASR and document what each defense does **not** stop.

## Decision

- Implement three attack families on the mini corpus: single-document, dual sleeper+trigger, metadata-only trust inflation.
- Measure **retrieval ASR** (poison chunk in top-k) and proxy **generation ASR** (same condition in Phase 5 harness).
- Defenses shipped in Phase 5: hybrid alpha tuning, `MetadataTrustFilter`, `LexicalAnomalyFilter`.
- Sweep `hybrid_alpha` 0.0–1.0; publish `benchmarks/asr_vs_alpha.json`.

## Defense limits (honest)

| Defense | Stops | Does **not** stop |
|---------|--------|-------------------|
| Metadata trust cap | metadata-only high `trust_score` | single-doc semantic poison |
| Lexical anomaly filter | obvious injection phrases | paraphrased / subtle poison |
| Hybrid alpha ↑ dense | some sparse-ranked poisons | poisons winning dense channel |

## Consequences

- ASR before/after defenses must come from `run_redteam_sweep.py`, not README guesses.
- Production needs additional signals (perplexity filter, source-trust graph) in later releases.
