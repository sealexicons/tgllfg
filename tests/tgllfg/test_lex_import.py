"""End-to-end tests for ``tgllfg lex import`` and the data-version
compatibility check."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from tgllfg.lex import build_alembic_config
from tgllfg.lex.import_csv import import_lemmas_csv
from tgllfg.lex.loader import (
    BACKEND_ENV,
    DATABASE_URL_ENV,
    IncompatibleDataVersionError,
    aload_morph_data_from_url,
)
from tgllfg.lex.seed import seed_database

pytestmark = pytest.mark.postgres


@pytest_asyncio.fixture
async def seeded_engine(
    postgres_container: PostgresContainer,
) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(postgres_container.get_connection_url(), future=True)
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("DROP EXTENSION IF EXISTS pg_trgm"))
        await conn.execute(text("DROP EXTENSION IF EXISTS pgcrypto"))

    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")
    await seed_database(postgres_container.get_connection_url())

    try:
        yield engine
    finally:
        await engine.dispose()


def _write_csv(tmp_path: Path, rows: list[str]) -> Path:
    p = tmp_path / "lemmas.csv"
    p.write_text("citation_form,pos,gloss,transitivity,affix_class\n" + "\n".join(rows) + "\n")
    return p


async def test_import_lemmas_inserts_rows(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
    tmp_path: Path,
) -> None:
    csv_path = _write_csv(
        tmp_path,
        [
            "halimbawa,NOUN,example,,",
            "talaga,ADV,really,,",
        ],
    )
    report = await import_lemmas_csv(
        postgres_container.get_connection_url(),
        csv_path,
        source_short_name="TestSource",
        source_full_citation="Test fixture, 2026",
    )
    assert report.rows_read == 2
    assert report.rows_upserted == 2

    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT pos, source_ref FROM lemma WHERE citation_form = 'halimbawa'")
        )
        assert result.one() == ("NOUN", "TestSource")
        result = await session.execute(
            text("SELECT full_citation FROM source WHERE short_name = 'TestSource'")
        )
        assert result.scalar_one() == "Test fixture, 2026"


async def test_import_lemmas_is_idempotent(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
    tmp_path: Path,
) -> None:
    csv_path = _write_csv(tmp_path, ["halimbawa,NOUN,example,,"])
    first = await import_lemmas_csv(
        postgres_container.get_connection_url(),
        csv_path,
        source_short_name="S",
        source_full_citation="C",
    )
    second = await import_lemmas_csv(
        postgres_container.get_connection_url(),
        csv_path,
        source_short_name="S",
        source_full_citation="C",
    )
    assert first.rows_read == second.rows_read == 1
    assert first.rows_upserted == second.rows_upserted == 1

    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT count(*) FROM lemma WHERE citation_form = 'halimbawa'")
        )
        assert result.scalar_one() == 1


async def test_import_lemmas_refreshes_gloss_on_conflict(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
    tmp_path: Path,
) -> None:
    csv_path = _write_csv(tmp_path, ["halimbawa,NOUN,old gloss,,"])
    await import_lemmas_csv(
        postgres_container.get_connection_url(),
        csv_path,
        source_short_name="S",
        source_full_citation="C",
    )
    csv_path = _write_csv(tmp_path, ["halimbawa,NOUN,new gloss,,"])
    await import_lemmas_csv(
        postgres_container.get_connection_url(),
        csv_path,
        source_short_name="S",
        source_full_citation="C",
    )
    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT gloss FROM lemma WHERE citation_form = 'halimbawa'")
        )
        assert result.scalar_one() == "new gloss"


async def test_import_requires_seeded_language(
    postgres_container: PostgresContainer,
    tmp_path: Path,
) -> None:
    """Importing into a freshly-migrated but unseeded database must
    fail loudly: the language row hasn't been created yet."""
    engine = create_async_engine(postgres_container.get_connection_url(), future=True)
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("DROP EXTENSION IF EXISTS pg_trgm"))
        await conn.execute(text("DROP EXTENSION IF EXISTS pgcrypto"))
    cfg = build_alembic_config(postgres_container.get_connection_url())
    await asyncio.to_thread(command.upgrade, cfg, "head")
    await engine.dispose()

    csv_path = _write_csv(tmp_path, ["halimbawa,NOUN,example,,"])
    with pytest.raises(RuntimeError, match="language with iso_code"):
        await import_lemmas_csv(
            postgres_container.get_connection_url(),
            csv_path,
            source_short_name="S",
            source_full_citation="C",
        )


async def test_data_version_mismatch_raises(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
) -> None:
    """A stale data_version in lex_metadata must produce
    IncompatibleDataVersionError."""
    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        async with session.begin():
            await session.execute(
                text("UPDATE lex_metadata SET value = '0.0.1' WHERE key = 'data_version'")
            )

    with pytest.raises(IncompatibleDataVersionError, match="older than"):
        await aload_morph_data_from_url(postgres_container.get_connection_url())


async def test_data_version_missing_raises(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
) -> None:
    sessionmaker = async_sessionmaker(seeded_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        async with session.begin():
            await session.execute(text("DELETE FROM lex_metadata WHERE key = 'data_version'"))

    with pytest.raises(IncompatibleDataVersionError, match="not set"):
        await aload_morph_data_from_url(postgres_container.get_connection_url())


async def test_cli_import_subcommand(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from tgllfg.cli import main

    csv_path = _write_csv(tmp_path, ["halimbawa,NOUN,example,,"])
    await asyncio.to_thread(
        main,
        [
            "lex",
            "--database-url",
            postgres_container.get_connection_url(),
            "import",
            str(csv_path),
            "--source-short-name",
            "S",
            "--source-full-citation",
            "C",
        ],
    )
    out = capsys.readouterr().out
    assert "imported: rows_read=1" in out
    assert "rows_upserted=1" in out


def test_resolve_morph_data_yaml_default_does_not_check_data_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The data_version check applies only to the DB backend; the
    YAML default path must continue to work without any DB at all."""
    monkeypatch.delenv(BACKEND_ENV, raising=False)
    monkeypatch.delenv(DATABASE_URL_ENV, raising=False)
    from tgllfg.lex.loader import resolve_morph_data

    data = resolve_morph_data()
    assert any(r.citation == "kain" for r in data.roots)
