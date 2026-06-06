# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""OpenTelemetry tracing + structlog logging (Phase 13.E).

Tracing is **env-gated at the API edge**: with no
``OTEL_EXPORTER_OTLP_ENDPOINT`` (and no test ``span_exporter``) no
provider is created, so spans are no-ops — dev / tests / the CLI are
unaffected. When configured, traces export OTLP/gRPC (to ``alloy:4317``
in compose, 13.I) and segment **gross compute from DB I/O**:

* **DB I/O** — ``opentelemetry-instrumentation-sqlalchemy`` auto-spans
  every query / commit / flush on the engine (``db.*`` attributes).
* **Compute** — the routes wrap the parse / audit work in explicit
  ``kind=compute`` spans via :func:`traced`.
* FastAPI request auto-instrumentation provides the parent request span.

structlog is configured **always** (structured JSON to stdout → loki).
No parser-core instrumentation: ``opentelemetry`` stays out of
``tgllfg.core`` (per the Phase 13.E scope decision); per-stage pipeline
spans are deferred.
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated, Any

import structlog
from fastapi import Depends, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

#: Module logger for the API layer (structured once :func:`_configure_structlog`
#: has run, which :func:`configure_telemetry` ensures at startup).
log = structlog.get_logger("tgllfg.api")

_structlog_configured = False


def _configure_structlog() -> None:
    global _structlog_configured
    if _structlog_configured:
        return
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.EventRenamer("message"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _structlog_configured = True


def configure_telemetry(app: Any, engine: Any) -> None:
    """Configure structlog (always) + OTel tracing (env-gated) for ``app``.

    Called from the lifespan after the engine is built. Instruments
    FastAPI (request spans) + SQLAlchemy (DB query/commit/flush spans)
    when an OTLP endpoint — or a test ``app.state.span_exporter`` — is
    configured; otherwise sets a no-op tracer and returns.
    """
    _configure_structlog()
    settings = app.state.settings
    exporter = getattr(app.state, "span_exporter", None)
    if exporter is None and not settings.otel_endpoint:
        app.state.tracer = trace.get_tracer("tgllfg.api")  # no provider → no-op
        return

    provider = TracerProvider(
        resource=Resource.create({"service.name": settings.otel_service_name})
    )
    if exporter is not None:
        # Tests inject an in-memory exporter; SimpleSpanProcessor exports
        # synchronously on span end so assertions see spans immediately.
        provider.add_span_processor(SimpleSpanProcessor(exporter))
    else:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_endpoint))
        )
    app.state.tracer_provider = provider
    app.state.tracer = provider.get_tracer("tgllfg.api")
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    SQLAlchemyInstrumentor().instrument(
        engine=engine.sync_engine, tracer_provider=provider
    )


def shutdown_telemetry(app: Any, engine: Any) -> None:
    """Uninstrument + flush on shutdown so per-test/dev engines don't leak
    instrumentation and pending spans are exported. No-op when tracing
    wasn't configured."""
    provider = getattr(app.state, "tracer_provider", None)
    if provider is None:
        return
    try:
        SQLAlchemyInstrumentor().uninstrument(engine=engine.sync_engine)
    except Exception:  # noqa: BLE001 — best-effort teardown
        pass
    try:
        FastAPIInstrumentor.uninstrument_app(app)
    except Exception:  # noqa: BLE001 — best-effort teardown
        pass
    provider.shutdown()


@contextmanager
def traced(tracer: Any, name: str, **attrs: Any) -> Iterator[Any]:
    """A ``kind=compute`` child span around a gross compute block (a no-op
    when tracing is off). DB I/O is auto-spanned by SQLAlchemy, so this is
    only for compute (parse / audit)."""
    with tracer.start_as_current_span(name) as span:
        span.set_attribute("tgllfg.kind", "compute")
        for key, value in attrs.items():
            if value is not None:
                span.set_attribute(f"tgllfg.{key}", value)
        yield span


def get_tracer(request: Request) -> Any:
    """The request app's tracer (real when tracing is on, else no-op)."""
    return request.app.state.tracer


TracerDep = Annotated[Any, Depends(get_tracer)]
