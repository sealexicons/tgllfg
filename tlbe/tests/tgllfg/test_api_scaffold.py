# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 13.A: FastAPI scaffold — health/readiness probes + DI wiring.

DB-free: ``/ready``'s DB probe is overridden so the fast suite needs no
Postgres; the real-DB readiness check lands in Phase 13.B alongside the
migration test infrastructure. Uses the shared ``api_app`` fixture
(conftest).
"""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from tgllfg.api.deps import ANONYMOUS, get_principal
from tgllfg.api.health import check_db
from tgllfg.api.settings import Settings


@pytest.fixture
def client_db_ok(api_app: FastAPI) -> Iterator[TestClient]:
    api_app.dependency_overrides[check_db] = lambda: True
    with TestClient(api_app) as client:
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


def test_ready_503_when_db_down(api_app: FastAPI) -> None:
    api_app.dependency_overrides[check_db] = lambda: False
    with TestClient(api_app) as client:
        resp = client.get("/ready")
    assert resp.status_code == 503
    assert resp.json()["checks"]["database"] is False


def test_openapi_under_api_prefix_with_unversioned_health(client_db_ok: TestClient) -> None:
    # OpenAPI + docs live under /api so the whole API surface is behind
    # the single /api reverse-proxy path; root /openapi.json is gone.
    assert client_db_ok.get("/openapi.json").status_code == 404
    schema = client_db_ok.get("/api/openapi.json").json()
    # Health/readiness stay unversioned at the root (orchestrator probes).
    assert "/health" in schema["paths"]
    assert "/ready" in schema["paths"]


async def test_get_principal_anonymous_returns_wildcard() -> None:
    # Anonymous mode short-circuits before touching the request/JWKS.
    req = Request({"type": "http", "headers": []})
    principal = await get_principal(req, Settings(auth_mode="anonymous"))
    assert principal is ANONYMOUS
    assert principal.is_anonymous is True
    assert "*" in principal.roles
    # Keycloak-mode JWT verification + role gates are in test_api_auth.py.


async def test_check_db_false_without_sessionmaker() -> None:
    class _State:
        pass

    class _App:
        state = _State()

    class _Req:
        app = _App()

    assert await check_db(_Req()) is False  # type: ignore[arg-type]
