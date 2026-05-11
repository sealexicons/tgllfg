"""Phase 5n.C.4 Commit 10 — DB-backed polysemy regression.

Asserts that the DB backend round-trips the long-standing
``kuwarto`` ROOM / FRACTION polysemy that Phase 5f had to drop
on the DB side because the schema lacked a per-sense feats slot.

After Phase 5n.C.4 (lemma_sense child table + per-sense Root
projection in ``adapter.cache_to_morph_data``), both readings
materialize as separate ``Root`` records with distinct feats.

Verification path:

1. Migrate a fresh testcontainer DB.
2. Seed from the YAML lex (full ``data/tgl/`` tree).
3. Inspect ``lemma_sense`` rows directly via SQL to confirm two
   senses on the ``kuwarto`` lemma.
4. Build the ``LexCache`` and project via ``cache_to_morph_data``
   to verify the ROOM and FRACTION Roots reach the analyzer-facing
   :class:`MorphData` shape.
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

from tgllfg.lex import build_alembic_config, build_cache
from tgllfg.lex.adapter import cache_to_morph_data
from tgllfg.lex.seed import seed_database

pytestmark = pytest.mark.postgres


@pytest_asyncio.fixture
async def seeded_engine(
    postgres_container: PostgresContainer,
) -> AsyncIterator[AsyncEngine]:
    """Fresh migrated + fully seeded DB."""
    engine = create_async_engine(postgres_container.get_connection_url(), future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        await session.execute(text("DROP SCHEMA public CASCADE"))
        await session.execute(text("CREATE SCHEMA public"))
        await session.execute(text("DROP EXTENSION IF EXISTS pg_trgm"))
        await session.execute(text("DROP EXTENSION IF EXISTS pgcrypto"))
        await session.commit()

    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")
    await seed_database(postgres_container.get_connection_url())
    try:
        yield engine
    finally:
        await engine.dispose()


async def test_kuwarto_has_two_sense_rows_in_db(seeded_engine: AsyncEngine) -> None:
    """The seeded ``lemma_sense`` table carries two rows for
    ``kuwarto``: one with empty feats (the ROOM reading; sense 0)
    and one with ``SEM_CLASS: FRACTION`` (sense 1)."""
    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text(
                "SELECT ls.sense_index, ls.feats "
                "FROM lemma_sense ls "
                "JOIN lemma l ON l.id = ls.lemma_id "
                "WHERE l.citation_form = 'kuwarto' AND l.pos = 'NOUN' "
                "ORDER BY ls.sense_index"
            )
        )
        rows = result.all()
    assert len(rows) == 2, (
        f"expected two senses for 'kuwarto'; got {len(rows)}: {rows}"
    )
    sense0_index, sense0_feats = rows[0]
    sense1_index, sense1_feats = rows[1]
    assert sense0_index == 0
    assert sense1_index == 1
    # ROOM has no SEM_CLASS feat; FRACTION carries SEM_CLASS=FRACTION.
    assert sense0_feats.get("SEM_CLASS") is None
    assert sense1_feats.get("SEM_CLASS") == "FRACTION"


async def test_db_backend_projects_kuwarto_as_two_roots(
    seeded_engine: AsyncEngine,
) -> None:
    """Going through LexCache → cache_to_morph_data yields two
    ``Root`` entries for ``kuwarto``: one ROOM with empty feats
    and one FRACTION with ``SEM_CLASS: FRACTION``."""
    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        cache = await build_cache(session)

    md = cache_to_morph_data(cache, iso_code="tgl")
    kuwartos = [r for r in md.roots if r.citation == "kuwarto"]
    assert len(kuwartos) == 2, (
        f"expected two 'kuwarto' Roots from DB backend; got "
        f"{len(kuwartos)}: {kuwartos}"
    )
    sem_classes = {r.feats.get("SEM_CLASS") for r in kuwartos}
    assert sem_classes == {None, "FRACTION"}, (
        f"expected SEM_CLASS readings {{None, 'FRACTION'}}; got {sem_classes}"
    )


async def test_db_backend_preserves_monosemous_lemma_shape(
    seeded_engine: AsyncEngine,
) -> None:
    """A representative monosemous lemma (``aklat`` "book") projects
    to exactly one ``Root`` from the DB backend — the same shape as
    the pre-C9 single-row projection. Empty feats on the sole sense
    flow through as an empty :attr:`Root.feats` dict."""
    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        cache = await build_cache(session)

    md = cache_to_morph_data(cache, iso_code="tgl")
    aklats = [r for r in md.roots if r.citation == "aklat"]
    assert len(aklats) == 1
    r = aklats[0]
    assert r.pos == "NOUN"
    assert r.feats == {}
