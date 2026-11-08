# Red Team and Safety Posture

SentinelRAG treats poisoning and prompt injection as first-class threats. Phase 1
wires a filter hook at ingest time without changing default behavior. Red-team
workflows and adaptive routing land in later phases; the platform already separates
eval gates from serving so unsafe retrieval changes fail CI before deploy.
