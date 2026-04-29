"""Smoke tests for the Phase 3 Postgres test harness.

These verify only that the testcontainer can be started, that an async
SQLAlchemy session round-trips a trivial query, and that the two
extensions the §6.2 schema requires (``pg_trgm`` for fuzzy lemma lookup,
``pgcrypto`` for ``gen_random_uuid()``) are loadable in this image.
Schema creation lands in Commit 2 (the Alembic baseline).
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.postgres


async def test_session_round_trips_trivial_query(pg_session: AsyncSession) -> None:
    result = await pg_session.execute(text("SELECT 1"))
    assert result.scalar_one() == 1


async def test_pg_trgm_extension_loads(pg_session: AsyncSession) -> None:
    await pg_session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    result = await pg_session.execute(text("SELECT similarity('kain', 'kain')"))
    assert result.scalar_one() == pytest.approx(1.0)


async def test_pgcrypto_extension_loads(pg_session: AsyncSession) -> None:
    await pg_session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    result = await pg_session.execute(text("SELECT gen_random_uuid()"))
    assert result.scalar_one() is not None


async def test_postgres_version_is_17(pg_session: AsyncSession) -> None:
    result = await pg_session.execute(text("SHOW server_version_num"))
    version_num = int(result.scalar_one())
    assert 170000 <= version_num < 180000
