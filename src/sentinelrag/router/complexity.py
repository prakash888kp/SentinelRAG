"""Query complexity signals for routing (deterministic; CI-stable)."""

from __future__ import annotations

from typing import Literal

Complexity = Literal["simple", "complex"]


def classify_complexity(query: str) -> Complexity:
    q = query.lower()
    words = q.split()
    if len(words) > 14:
        return "complex"
    if " and " in q or " relate " in q or q.startswith("how do"):
        return "complex"
    if any(token in q for token in ("multi-hop", "connect", "compare", "defend")):
        return "complex"
    return "simple"
