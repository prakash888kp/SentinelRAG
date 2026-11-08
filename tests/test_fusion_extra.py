"""Additional fusion edge cases for coverage."""

from __future__ import annotations

from sentinelrag.retrieval.fusion import min_max_normalize


def test_min_max_empty() -> None:
    assert min_max_normalize({}) == {}
