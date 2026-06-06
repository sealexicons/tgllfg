# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Postgres testcontainer fixtures for the lexicon backend.

The session-scoped ``postgres_container`` fixture lazily spins a single
Postgres 17 container; tests that don't request it (or anything derived
from it) pay no startup cost. ``pg_engine`` and ``pg_session`` are
function-scoped — sharing the engine across pytest-asyncio's per-test
event loops triggers asyncpg ``cannot perform operation: another
operation is in progress`` errors, and the per-test cost of building an
asyncpg pool against an already-running container is negligible
compared to container startup itself.

Tests that need any of these fixtures should also be marked
``@pytest.mark.postgres`` so they can be excluded by tag in environments
without Docker (``pytest -m "not postgres"``).
"""

from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    container = PostgresContainer("postgres:17", driver="asyncpg")
    container.start()
    try:
        yield container
    finally:
        container.stop()


@pytest_asyncio.fixture
async def pg_engine(postgres_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    url = postgres_container.get_connection_url()
    engine = create_async_engine(url, future=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def pg_session(pg_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    sessionmaker = async_sessionmaker(pg_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
        await session.rollback()


# --- references-corpus skip -------------------------------------------
# The gitignored data/tgl/references/ tree (hand-transcriptions + licensed
# source texts) is absent on a fresh clone / CI. Tests that read it are
# marked ``@pytest.mark.references``; auto-skip them when the tree is
# absent so the suite stays green on CI without losing local coverage.
_REFERENCES_DIR = Path(__file__).resolve().parents[2] / "data" / "tgl" / "references"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if _REFERENCES_DIR.is_dir():
        return
    skip_refs = pytest.mark.skip(
        reason="data/tgl/references/ absent (gitignored licensed material; CI / fresh clone)"
    )
    for item in items:
        if "references" in item.keywords:
            item.add_marker(skip_refs)
