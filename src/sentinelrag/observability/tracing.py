"""OpenTelemetry tracing helpers (console export by default)."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

_TRACER: trace.Tracer | None = None


def setup_tracing(service_name: str = "sentinelrag") -> trace.Tracer:
    """Idempotent tracer setup for local/CI (console spans)."""
    global _TRACER  # noqa: PLW0603
    if _TRACER is not None:
        return _TRACER
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _TRACER = trace.get_tracer(service_name)
    return _TRACER


def get_tracer() -> trace.Tracer:
    return setup_tracing()
