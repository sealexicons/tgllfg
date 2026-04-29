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

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

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
