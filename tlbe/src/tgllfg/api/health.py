# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Liveness + readiness probes (Phase 13.A).

Intentionally **unversioned** — mounted at the app root, not under
``/api/v1`` — because compose / k8s point liveness and readiness at
fixed paths that must not move when the API version bumps, and probes
hit the container directly rather than through the ``/api`` proxy.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

health_router = APIRouter(tags=["health"])


async def check_db(request: Request) -> bool:
    """Probe DB connectivity with ``SELECT 1``. Returns ``False`` rather
    than raising on any failure, so :func:`ready` can report a degraded
    state. Overridden in tests via ``app.dependency_overrides`` to keep
    the fast suite Postgres-free; the real probe is exercised by the
    Phase 13.B migration tests.
    """
    sessionmaker = getattr(request.app.state, "sessionmaker", None)
    if sessionmaker is None:
        return False
    try:
        async with sessionmaker() as session:
            await session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 — any DB error means "not ready"
        return False
    return True


@health_router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: the process is up and serving. No external deps."""
    return {"status": "ok"}


@health_router.get("/ready")
async def ready(
    request: Request,
    db_ok: Annotated[bool, Depends(check_db)],
) -> JSONResponse:
    """Readiness: DB reachable **and** the compiled grammar warmed.
    Returns ``503`` with a per-check breakdown until both hold."""
    grammar_ok = getattr(request.app.state, "grammar", None) is not None
    ok = db_ok and grammar_ok
    return JSONResponse(
        {
            "status": "ready" if ok else "not ready",
            "checks": {"database": db_ok, "grammar": grammar_ok},
        },
        status_code=200 if ok else 503,
    )
