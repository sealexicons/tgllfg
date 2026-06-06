# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.E: OTel tracing — env-gated; gross compute vs DB I/O spans.

Tracing is off by default (no provider), so most tests are unaffected.
When a test injects an in-memory exporter on ``app.state.span_exporter``,
the lifespan instruments the app (FastAPI request spans + SQLAlchemy DB
spans) and the routes' explicit ``kind=compute`` spans are recorded. The
DB-span test needs a real Postgres (the lex query), so it's postgres-marked.
"""

from alembic import command
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

import pytest

from tgllfg.api import create_app
from tgllfg.api.settings import Settings
from tgllfg.lex import build_alembic_config


def test_telemetry_noop_when_unconfigured(api_app: FastAPI) -> None:
    with TestClient(api_app) as client:
        assert client.get("/health").status_code == 200
    # No endpoint + no exporter -> no provider was created (env-gated no-op).
    assert getattr(api_app.state, "tracer_provider", None) is None


def test_compute_span_on_parse(api_app: FastAPI) -> None:
    exporter = InMemorySpanExporter()
    api_app.state.span_exporter = exporter  # before TestClient -> lifespan uses it
    with TestClient(api_app) as client:
        assert client.post(
            "/api/v1/parse", json={"text": "Kumain ang aso."}
        ).status_code == 200
    spans = exporter.get_finished_spans()
    parse_spans = [s for s in spans if s.name == "parse"]
    assert parse_spans, f"expected a 'parse' compute span; got {[s.name for s in spans]}"
    assert parse_spans[0].attributes is not None
    assert parse_spans[0].attributes.get("tgllfg.kind") == "compute"


@pytest.mark.postgres
def test_db_span_on_lex_query(postgres_container: PostgresContainer) -> None:
    command.upgrade(build_alembic_config(postgres_container.get_connection_url()), "head")
    exporter = InMemorySpanExporter()
    app = create_app(
        settings=Settings(
            database_url=postgres_container.get_connection_url(),
            auth_mode="anonymous",
        )
    )
    app.state.span_exporter = exporter
    with TestClient(app) as client:
        # The query runs (returns no rows) — enough to produce a DB span.
        assert client.get("/api/v1/lex/search", params={"q": "aso"}).status_code == 200
    db_spans = [
        s
        for s in exporter.get_finished_spans()
        if s.attributes and s.attributes.get("db.system")
    ]
    assert db_spans, "expected a SQLAlchemy DB span (db.system) for the lex query"
