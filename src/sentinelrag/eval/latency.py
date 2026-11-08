"""Lightweight latency helpers for gate evidence."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def timed_ms(fn: Callable[[], T]) -> tuple[T, float]:
    t0 = time.perf_counter()
    value = fn()
    return value, (time.perf_counter() - t0) * 1000.0
