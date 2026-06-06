# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.A: FastAPI scaffold — health/readiness probes + DI wiring.

DB-free: ``/ready``'s DB probe is overridden so the fast suite needs no
Postgres; the real-DB readiness check lands in Phase 13.B alongside the
migration test infrastructure.
"""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from tgllfg.api import create_app
from tgllfg.api.deps import ANONYMOUS, get_principal
from tgllfg.api.health import check_db
from tgllfg.api.settings import Settings


def _app() -> FastAPI:
    return create_app(
        settings=Settings(
            database_url="postgresql+asyncpg://test:test@localhost:5432/test",
            auth_mode="anonymous",
        )
    )


@pytest.fixture
def client_db_ok() -> Iterator[TestClient]:
    app = _app()
    app.dependency_overrides[check_db] = lambda: True
    with TestClient(app) as client:
        yield client


def test_health_ok(client_db_ok: TestClient) -> None:
    resp = client_db_ok.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ready_ok_when_db_and_grammar(client_db_ok: TestClient) -> None:
    resp = client_db_ok.get("/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert body["checks"] == {"database": True, "grammar": True}


def test_ready_503_when_db_down() -> None:
    app = _app()
    app.dependency_overrides[check_db] = lambda: False
    with TestClient(app) as client:
        resp = client.get("/ready")
    assert resp.status_code == 503
    assert resp.json()["checks"]["database"] is False


def test_openapi_under_api_prefix_with_unversioned_health(
    client_db_ok: TestClient,
) -> None:
    # OpenAPI + docs live under /api so the whole API surface is behind
    # the single /api reverse-proxy path; root /openapi.json is gone.
    assert client_db_ok.get("/openapi.json").status_code == 404
    schema = client_db_ok.get("/api/openapi.json").json()
    # Health/readiness stay unversioned at the root (orchestrator probes).
    assert "/health" in schema["paths"]
    assert "/ready" in schema["paths"]


def test_get_principal_anonymous_returns_wildcard() -> None:
    principal = get_principal(Settings(auth_mode="anonymous"))
    assert principal is ANONYMOUS
    assert principal.is_anonymous is True
    assert "*" in principal.roles


def test_get_principal_keycloak_not_implemented() -> None:
    with pytest.raises(HTTPException) as exc:
        get_principal(Settings(auth_mode="keycloak"))
    assert exc.value.status_code == 501


async def test_check_db_false_without_sessionmaker() -> None:
    class _State:
        pass

    class _App:
        state = _State()

    class _Req:
        app = _App()

    assert await check_db(_Req()) is False  # type: ignore[arg-type]
