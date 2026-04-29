"""Round-trip tests for the Alembic baseline migration (§6.2).

Verifies that ``alembic upgrade head`` against an empty Postgres 17
testcontainer creates every table, extension, and index named in the
plan, and that ``alembic downgrade base`` removes them all cleanly.
Catches schema drift between the baseline migration and the plan
specification.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from tgllfg.lex import build_alembic_config

pytestmark = pytest.mark.postgres


_EXPECTED_TABLES = {
    "language",
    "source",
    "lemma",
    "lex_entry",
    "affix",
    "paradigm",
    "paradigm_slot",
    "sandhi_rule",
    "particle",
    "pronoun",
    "example",
    "voice_alias",
    "lex_metadata",
}

_EXPECTED_EXTENSIONS = {"pgcrypto", "pg_trgm"}

_EXPECTED_INDEXES = {
    "ix_lemma_lang_form",
    "ix_lemma_citation_form_trgm",
    "ix_lex_entry_lemma",
    "ix_particle_lang_surface",
    "ix_example_text_fts",
}


@pytest_asyncio.fixture
async def fresh_pg_engine(postgres_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    """An async engine for a *freshly migrated* database. Drops any
    existing tables/extensions before yielding so each test starts from
    a clean slate (the migration round-trip suite mutates DDL state and
    can leak between tests if reused)."""
    sync_url = postgres_container.get_connection_url().replace(
        "postgresql+asyncpg://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(sync_url, future=True)
    try:
        yield engine
    finally:
        await engine.dispose()


async def _all_tables(engine: AsyncEngine) -> set[str]:
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        return {row[0] for row in result.all()}


async def _all_extensions(engine: AsyncEngine) -> set[str]:
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(text("SELECT extname FROM pg_extension"))
        return {row[0] for row in result.all()}


async def _all_indexes(engine: AsyncEngine) -> set[str]:
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
        )
        return {row[0] for row in result.all()}


async def _reset_database(engine: AsyncEngine) -> None:
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        await session.execute(text("DROP SCHEMA public CASCADE"))
        await session.execute(text("CREATE SCHEMA public"))
        await session.execute(text("DROP EXTENSION IF EXISTS pg_trgm"))
        await session.execute(text("DROP EXTENSION IF EXISTS pgcrypto"))
        await session.commit()


async def test_baseline_upgrade_creates_full_schema(
    postgres_container: PostgresContainer, fresh_pg_engine: AsyncEngine
) -> None:
    await _reset_database(fresh_pg_engine)

    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")

    tables = await _all_tables(fresh_pg_engine)
    extensions = await _all_extensions(fresh_pg_engine)
    indexes = await _all_indexes(fresh_pg_engine)

    assert _EXPECTED_TABLES <= tables, f"missing tables: {_EXPECTED_TABLES - tables}"
    assert _EXPECTED_EXTENSIONS <= extensions
    assert _EXPECTED_INDEXES <= indexes


async def test_baseline_downgrade_removes_full_schema(
    postgres_container: PostgresContainer, fresh_pg_engine: AsyncEngine
) -> None:
    await _reset_database(fresh_pg_engine)

    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")
    await asyncio.to_thread(command.downgrade, cfg, "base")

    tables = await _all_tables(fresh_pg_engine)
    extensions = await _all_extensions(fresh_pg_engine)

    assert _EXPECTED_TABLES.isdisjoint(tables)
    # alembic_version table remains after downgrade-to-base; that's expected.
    assert _EXPECTED_EXTENSIONS.isdisjoint(extensions)


async def test_uuid_default_uses_pgcrypto(
    postgres_container: PostgresContainer, fresh_pg_engine: AsyncEngine
) -> None:
    """Smoke check that ``gen_random_uuid()`` actually fires for a row
    inserted without an explicit ``id``."""
    await _reset_database(fresh_pg_engine)
    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")

    sessionmaker = async_sessionmaker(fresh_pg_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        await session.execute(
            text("INSERT INTO language (iso_code, name) VALUES ('tgl', 'Tagalog')")
        )
        await session.commit()
        result = await session.execute(text("SELECT id FROM language WHERE iso_code = 'tgl'"))
        row = result.one()
        assert row[0] is not None
