# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.4 Commit 1 — ``lemma_sense`` schema + ORM smoke tests.

Spins up a migrated Postgres testcontainer, exercises the new
``lemma_sense`` table via raw SQL inserts (the path the seed will
take in Commit 2), and verifies:

* Backfill behaves correctly when run against a pre-populated
  ``lemma`` table: one ``lemma_sense`` row per ``lemma``, all at
  ``sense_index = 0`` with empty feats.
* The unique constraint on ``(lemma_id, sense_index)`` rejects a
  duplicate at the same index.
* The ``lex_entry.lemma_sense_id`` FK is nullable in C1 (dual-FK
  during the additive migration window) and round-trips when set.
"""

import asyncio
import json
import uuid
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from tgllfg.lex import build_alembic_config

pytestmark = pytest.mark.postgres


@pytest_asyncio.fixture
async def migrated_with_pre_populated_lemma(
    postgres_container: PostgresContainer,
) -> AsyncIterator[tuple[AsyncEngine, uuid.UUID, uuid.UUID]]:
    """A migrated DB where ``lemma`` was populated mid-migration.

    Simulates the production-DB case where existing lemma rows must
    backfill into ``lemma_sense`` at upgrade time. We run migrations
    up to ``0003``, INSERT a lemma, then upgrade to ``head`` (which
    runs ``0004`` and its backfill).
    """
    engine = create_async_engine(postgres_container.get_connection_url(), future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        await session.execute(text("DROP SCHEMA public CASCADE"))
        await session.execute(text("CREATE SCHEMA public"))
        await session.execute(text("DROP EXTENSION IF EXISTS pg_trgm"))
        await session.execute(text("DROP EXTENSION IF EXISTS pgcrypto"))
        await session.commit()

    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "0003")

    lang_id = uuid.uuid4()
    lemma_id = uuid.uuid4()
    async with sessionmaker() as session:
        await session.execute(
            text("INSERT INTO language (id, iso_code, name) VALUES (:i, 'tgl', 'Tagalog')"),
            {"i": lang_id},
        )
        await session.execute(
            text(
                "INSERT INTO lemma (id, language_id, citation_form, pos, gloss) "
                "VALUES (:i, :l, 'kuwarto', 'NOUN', 'room')"
            ),
            {"i": lemma_id, "l": lang_id},
        )
        await session.commit()

    await asyncio.to_thread(command.upgrade, cfg, "head")

    try:
        yield engine, lang_id, lemma_id
    finally:
        await engine.dispose()


async def test_backfill_creates_one_sense_per_existing_lemma(
    migrated_with_pre_populated_lemma: tuple[AsyncEngine, uuid.UUID, uuid.UUID],
) -> None:
    engine, _lang_id, lemma_id = migrated_with_pre_populated_lemma
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text(
                "SELECT sense_index, feats FROM lemma_sense WHERE lemma_id = :l"
            ),
            {"l": lemma_id},
        )
        rows = result.all()

    assert len(rows) == 1, f"expected 1 backfilled sense for kuwarto, got {len(rows)}"
    assert rows[0][0] == 0
    assert rows[0][1] == {}


async def test_unique_constraint_on_lemma_sense_index(
    migrated_with_pre_populated_lemma: tuple[AsyncEngine, uuid.UUID, uuid.UUID],
) -> None:
    engine, _lang_id, lemma_id = migrated_with_pre_populated_lemma
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        with pytest.raises(IntegrityError):
            await session.execute(
                text(
                    "INSERT INTO lemma_sense (lemma_id, sense_index, feats) "
                    "VALUES (:l, 0, :f)"
                ),
                {"l": lemma_id, "f": json.dumps({"SEM_CLASS": "ROOM"})},
            )
            await session.commit()


async def test_polysemous_lemma_two_senses_via_distinct_indexes(
    migrated_with_pre_populated_lemma: tuple[AsyncEngine, uuid.UUID, uuid.UUID],
) -> None:
    """The C1 schema lets a single ``lemma`` row carry two distinct
    senses via two ``lemma_sense`` rows at different indexes — the
    long-standing kuwarto ROOM / FRACTION case."""
    engine, _lang_id, lemma_id = migrated_with_pre_populated_lemma
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        # Upgrade the backfilled sense 0 to mean "ROOM".
        await session.execute(
            text(
                "UPDATE lemma_sense SET feats = :f, gloss = 'room' "
                "WHERE lemma_id = :l AND sense_index = 0"
            ),
            {"l": lemma_id, "f": json.dumps({"SEM_CLASS": "ROOM"})},
        )
        # Add a second sense at index 1 = "FRACTION".
        await session.execute(
            text(
                "INSERT INTO lemma_sense (lemma_id, sense_index, feats, gloss) "
                "VALUES (:l, 1, :f, 'quarter')"
            ),
            {"l": lemma_id, "f": json.dumps({"SEM_CLASS": "FRACTION"})},
        )
        await session.commit()

        result = await session.execute(
            text(
                "SELECT sense_index, feats, gloss FROM lemma_sense "
                "WHERE lemma_id = :l ORDER BY sense_index"
            ),
            {"l": lemma_id},
        )
        rows = result.all()

    assert len(rows) == 2
    assert rows[0] == (0, {"SEM_CLASS": "ROOM"}, "room")
    assert rows[1] == (1, {"SEM_CLASS": "FRACTION"}, "quarter")


async def test_lex_entry_lemma_sense_id_required_after_c9(
    migrated_with_pre_populated_lemma: tuple[AsyncEngine, uuid.UUID, uuid.UUID],
) -> None:
    """Phase 5n.C.4 Commit 9 enforced NOT NULL on
    ``lex_entry.lemma_sense_id`` and dropped ``lemma_id``. An
    INSERT without a sense_id must fail."""
    engine, _lang_id, lemma_id = migrated_with_pre_populated_lemma
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        with pytest.raises(Exception, match="lemma_sense_id"):
            await session.execute(
                text(
                    "INSERT INTO lex_entry "
                    "(pred_template, a_structure, morph_constraints, "
                    "intrinsic_classification) "
                    "VALUES ('ROOM <>', :a, :m, :ic)"
                ),
                {
                    "a": json.dumps([]),
                    "m": json.dumps({}),
                    "ic": json.dumps({}),
                },
            )
            await session.commit()


async def test_lex_entry_lemma_sense_id_roundtrips_when_set(
    migrated_with_pre_populated_lemma: tuple[AsyncEngine, uuid.UUID, uuid.UUID],
) -> None:
    """LexEntry FKs ``lemma_sense`` directly; round-trip read-back."""
    engine, _lang_id, lemma_id = migrated_with_pre_populated_lemma
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        sense_id = (
            await session.execute(
                text(
                    "SELECT id FROM lemma_sense "
                    "WHERE lemma_id = :l AND sense_index = 0"
                ),
                {"l": lemma_id},
            )
        ).scalar_one()
        await session.execute(
            text(
                "INSERT INTO lex_entry "
                "(lemma_sense_id, pred_template, a_structure, "
                "morph_constraints, intrinsic_classification) "
                "VALUES (:s, 'ROOM <>', :a, :m, :ic)"
            ),
            {
                "s": sense_id,
                "a": json.dumps([]),
                "m": json.dumps({}),
                "ic": json.dumps({}),
            },
        )
        await session.commit()

        result = await session.execute(
            text("SELECT lemma_sense_id FROM lex_entry WHERE lemma_sense_id = :s"),
            {"s": sense_id},
        )
        assert result.scalar_one() == sense_id
