"""Token and USD cost accounting (estimated; no vendor billing APIs)."""

from __future__ import annotations

from dataclasses import dataclass

# USD per 1K tokens (rough public list prices; benchmarks only).
MODEL_USD_PER_1K: dict[str, float] = {
    "mock-llm": 0.0,
    "gpt-4o-mini": 0.00015,
    "gemini-2.0-flash": 0.0001,
}


@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    prompt_tokens: int
    completion_tokens: int
    usd: float


def estimate_tokens(text: str) -> int:
    """Heuristic: ~4 chars per token."""
    return max(1, len(text) // 4)


def estimate_llm_cost(
    *,
    model: str,
    prompt: str,
    completion: str,
) -> CostRecord:
    prompt_tokens = estimate_tokens(prompt)
    completion_tokens = estimate_tokens(completion)
    rate = MODEL_USD_PER_1K.get(model, 0.0002)
    usd = (prompt_tokens + completion_tokens) / 1000.0 * rate
    return CostRecord(
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        usd=round(usd, 6),
    )
