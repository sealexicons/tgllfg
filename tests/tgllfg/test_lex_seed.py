"""End-to-end tests for ``tgllfg lex seed``.

Migrates a fresh Postgres testcontainer, runs the YAML→DB seed against
the shipped ``data/tgl/`` tree, and verifies row counts plus
idempotency on a second invocation. The full seed is exercised, not a
fixture — so this is also a regression check that the YAML parses
cleanly through the seed path.
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
from tgllfg.lex.seed import DATA_VERSION, seed_database

pytestmark = pytest.mark.postgres


@pytest_asyncio.fixture
async def empty_migrated_engine(
    postgres_container: PostgresContainer,
) -> AsyncIterator[AsyncEngine]:
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

    try:
        yield engine
    finally:
        await engine.dispose()


async def test_seed_populates_every_table(
    postgres_container: PostgresContainer, empty_migrated_engine: AsyncEngine
) -> None:
    report = await seed_database(postgres_container.get_connection_url())

    assert report.languages == 1
    assert report.lemmas > 0
    assert report.affixes > 0
    assert report.paradigm_cells > 0
    assert report.sandhi_rules > 0
    assert report.particles > 0
    assert report.pronouns > 0
    assert report.metadata_keys >= 1

    sessionmaker = async_sessionmaker(empty_migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(text("SELECT iso_code, name FROM language"))
        assert result.one() == ("tgl", "Tagalog")

        result = await session.execute(
            text("SELECT value FROM lex_metadata WHERE key = 'data_version'")
        )
        assert result.scalar_one() == DATA_VERSION

        result = await session.execute(
            text("SELECT count(*) FROM lemma WHERE pos = 'VERB'")
        )
        assert result.scalar_one() > 0


async def test_seed_is_idempotent(
    postgres_container: PostgresContainer, empty_migrated_engine: AsyncEngine
) -> None:
    first = await seed_database(postgres_container.get_connection_url())
    second = await seed_database(postgres_container.get_connection_url())

    assert first.languages == second.languages
    assert first.lemmas == second.lemmas
    assert first.affixes == second.affixes
    assert first.paradigm_cells == second.paradigm_cells
    assert first.sandhi_rules == second.sandhi_rules
    assert first.particles == second.particles
    assert first.pronouns == second.pronouns
    assert first.metadata_keys == second.metadata_keys


async def test_seed_refreshes_lemma_gloss(
    postgres_container: PostgresContainer, empty_migrated_engine: AsyncEngine
) -> None:
    """A second seed must overwrite a hand-corrupted gloss."""
    await seed_database(postgres_container.get_connection_url())

    sessionmaker = async_sessionmaker(empty_migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        async with session.begin():
            await session.execute(
                text("UPDATE lemma SET gloss = 'CORRUPTED' WHERE citation_form = 'kain'")
            )
        result = await session.execute(
            text("SELECT gloss FROM lemma WHERE citation_form = 'kain'")
        )
        assert result.scalar_one() == "CORRUPTED"

    await seed_database(postgres_container.get_connection_url())

    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT gloss FROM lemma WHERE citation_form = 'kain'")
        )
        assert result.scalar_one() != "CORRUPTED"


async def test_seed_populates_lemma_morph_metadata(
    postgres_container: PostgresContainer, empty_migrated_engine: AsyncEngine
) -> None:
    """The new lemma.transitivity and lemma.affix_class columns must
    arrive populated for verbs that declare them in roots.yaml."""
    await seed_database(postgres_container.get_connection_url())

    sessionmaker = async_sessionmaker(empty_migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text(
                "SELECT transitivity, affix_class FROM lemma "
                "WHERE citation_form = 'kain' AND pos = 'VERB'"
            )
        )
        row = result.one()
        assert row[0] == "TR"
        assert "um" in row[1]


async def test_seed_populates_paradigm_cell_operations(
    postgres_container: PostgresContainer, empty_migrated_engine: AsyncEngine
) -> None:
    """Paradigm cells round-trip with their full operation list."""
    await seed_database(postgres_container.get_connection_url())

    sessionmaker = async_sessionmaker(empty_migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text(
                "SELECT operations FROM paradigm_cell "
                "WHERE voice = 'AV' AND aspect = 'PFV' AND affix_class = 'um'"
            )
        )
        ops = result.scalar_one()
        assert any(op["op"] == "infix" and op["value"] == "um" for op in ops)


async def test_cli_seed_subcommand(
    postgres_container: PostgresContainer,
    empty_migrated_engine: AsyncEngine,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Smoke test the argparse wiring: ``tgllfg lex seed`` end-to-end."""
    from tgllfg.cli import main

    await asyncio.to_thread(
        main, ["lex", "--database-url", postgres_container.get_connection_url(), "seed"]
    )

    out = capsys.readouterr().out
    assert "seeded:" in out
    assert "language=1" in out
    assert "lemma=" in out
    assert "paradigm_cell=" in out
