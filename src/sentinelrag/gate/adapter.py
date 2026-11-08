"""Adapter hook: point the gate at your own RAG entrypoint."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from sentinelrag.gate.evidence import SCHEMA_ID, EvidenceBundle


def load_adapter(path: Path) -> Callable[[], dict[str, Any]]:
    """Load ``adapter.py`` exposing ``def collect_metrics() -> dict``."""

    spec = importlib.util.spec_from_file_location("sentinelrag_adapter", path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load adapter: {path}"
        raise ImportError(msg)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sentinelrag_adapter"] = mod
    spec.loader.exec_module(mod)
    fn = getattr(mod, "collect_metrics", None)
    if fn is None:
        msg = "adapter must define collect_metrics()"
        raise AttributeError(msg)
    return fn  # type: ignore[no-any-return]


def bundle_from_adapter(path: Path) -> EvidenceBundle:
    metrics = load_adapter(path)()
    bundle = EvidenceBundle(schema=SCHEMA_ID)
    bundle.metrics = dict(metrics.get("metrics", metrics))
    bundle.security_probes = dict(metrics.get("security_probes", {}))
    return bundle


def write_adapter_template(path: Path) -> None:
    path.write_text(
        '''"""SentinelRAG adapter — implement collect_metrics for your pipeline."""

from __future__ import annotations

from typing import Any


def collect_metrics() -> dict[str, Any]:
    """Return metrics + security_probes for gate policy."""
    return {
        "metrics": {
            "phase1_hybrid_recall_at_k": 0.0,
            "phase2_mean_faithfulness": 0.0,
        },
        "security_probes": {
            "ingest_defense_blocked_fraction": 1.0,
        },
    }
''',
        encoding="utf-8",
    )


def bundle_to_json(path: Path, bundle: EvidenceBundle) -> None:
    path.write_text(json.dumps(bundle.to_dict(), indent=2) + "\n", encoding="utf-8")
