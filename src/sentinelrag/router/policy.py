"""Cost/latency-aware routing policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sentinelrag.router.complexity import classify_complexity
from sentinelrag.settings import Settings

RoutedStrategy = Literal["naive", "hybrid", "agentic"]


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    strategy: RoutedStrategy
    complexity: str
    reason: str
    estimated_cost_usd: float


def route_query(query: str, settings: Settings) -> RoutingDecision:
    complexity = classify_complexity(query)
    if complexity == "simple":
        strategy: RoutedStrategy = "naive"
        est = 0.0001
        reason = "simple query → cheapest dense retrieval"
    elif settings.cost_budget_usd < 0.005:
        strategy = "hybrid"
        est = 0.0005
        reason = "complex query but tight budget → hybrid only"
    else:
        strategy = "agentic"
        est = 0.0012
        reason = "complex query → multi-hop agentic"

    return RoutingDecision(
        strategy=strategy,
        complexity=complexity,
        reason=reason,
        estimated_cost_usd=est,
    )
