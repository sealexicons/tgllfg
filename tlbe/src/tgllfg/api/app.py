# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""FastAPI application factory + lifespan (Phase 13.A).

:func:`create_app` builds the app; the async lifespan owns the
SQLAlchemy async engine + sessionmaker (on ``app.state``) and warms the
compiled grammar once at startup. Versioned endpoints mount under
``/api/v1`` and the app's own docs/OpenAPI under ``/api``
(:mod:`tgllfg.api.v1`); liveness/readiness are unversioned at the root
(:mod:`tgllfg.api.health`).
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..__version__ import __version__
from ..cfg import Grammar
from .health import health_router
from .settings import Settings, get_settings
from .v1 import v1_router

#: Versioned endpoints mount under this prefix, and the app's own docs /
#: OpenAPI live under ``API_PREFIX`` too, so the entire API surface sits
#: behind the single ``/api`` reverse-proxy path the Phase 14 frontend
#: forwards. ``/health`` + ``/ready`` stay at the root for orchestrator
#: probes, which reach the container directly rather than via the proxy.
API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown: build the async engine + sessionmaker, warm the
    compiled-grammar singleton, and init the audit-job registry; on
    shutdown, cancel any in-flight audit runs (terminating their
    subprocesses) before disposing the engine."""
    settings: Settings = app.state.settings
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    app.state.engine = engine
    app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    # Warm the compiled grammar once so the first /parse doesn't pay the
    # rule-compilation cost. Phase 15 may relocate this to a shared redis
    # cache for multi-replica deployments.
    app.state.grammar = Grammar.load_default()
    # Audit job state (Phase 13.C.3): run_id -> _AuditJob registry + the
    # set of live audit asyncio.Tasks so shutdown can cancel them.
    app.state.audit_jobs = {}
    app.state.audit_tasks = set()
    try:
        yield
    finally:
        # Cancel in-flight audit runs; each task's `finally` terminates its
        # subprocess and the gather waits for that cleanup, so no audit
        # child process is orphaned past shutdown.
        live = list(app.state.audit_tasks)
        for task in live:
            task.cancel()
        if live:
            await asyncio.gather(*live, return_exceptions=True)
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the tgllfg FastAPI application.

    Pass ``settings`` to override the env-loaded :class:`Settings` (used
    by tests); otherwise the cached :func:`get_settings` is used.
    """
    settings = settings or get_settings()
    app = FastAPI(
        title="tgllfg",
        version=__version__,
        summary="Tagalog LFG parser — REST API",
        lifespan=lifespan,
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
    )
    app.state.settings = settings
    app.include_router(health_router)
    app.include_router(v1_router, prefix=f"{API_PREFIX}/v1")
    return app
