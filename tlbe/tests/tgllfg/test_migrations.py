# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Round-trip tests for the Alembic baseline migration (§6.2).

Verifies that ``alembic upgrade head`` against an empty Postgres 17
testcontainer creates every table, extension, and index named in the
plan, and that ``alembic downgrade base`` removes them all cleanly.
Catches schema drift between the baseline migration and the plan
specification.
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Connection, text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from tgllfg.lex import build_alembic_config
from tgllfg.lex.models import Base

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
    "paradigm_cell",
    "lemma_sense",
}

_EXPECTED_EXTENSIONS = {"pgcrypto", "pg_trgm"}

_EXPECTED_INDEXES = {
    "ix_lemma_lang_form",
    "ix_lemma_citation_form_trgm",
    "ix_lex_entry_lemma_sense",
    "ix_lemma_sense_lemma",
    "ix_particle_lang_surface",
    "ix_example_text_fts",
    "ix_paradigm_cell_lang",
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


def _include_non_index(
    obj: Any, name: str | None, type_: str, reflected: bool, compare_to: Any
) -> bool:
    # Indexes (incl. the GIN trgm + FTS-expression indexes) are
    # migration-owned and gated above by ``_EXPECTED_INDEXES``; the ORM
    # models deliberately don't declare them, so exclude indexes from the
    # model<->migration structural drift comparison.
    return type_ != "index"


def _compare_models(sync_conn: Connection) -> list[Any]:
    ctx = MigrationContext.configure(
        sync_conn,
        opts={"compare_type": True, "include_object": _include_non_index},
    )
    return compare_metadata(ctx, Base.metadata)


async def test_models_match_migrations_no_drift(
    postgres_container: PostgresContainer, fresh_pg_engine: AsyncEngine
) -> None:
    """Phase 13.B schema-current gate: the ORM models in ``lex/models.py``
    match ``upgrade head`` at the table / column / constraint level, so a
    model change shipped without a migration (or vice versa) fails CI.

    ``compare_metadata`` is the rigorous form of "upgrade head == fresh
    create_all": it reports the migration ops needed to turn the migrated
    DB into the models' schema, so an empty list means they already agree.
    Indexes + extensions are migration-owned (excluded here; gated by the
    round-trip tests above).
    """
    await _reset_database(fresh_pg_engine)
    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")

    async with fresh_pg_engine.connect() as conn:
        diffs = await conn.run_sync(_compare_models)

    assert diffs == [], f"models drifted from migrations: {diffs}"
