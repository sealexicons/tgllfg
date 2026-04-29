"""LexCache → MorphData equivalence and parser-via-DB end-to-end.

After migrating + seeding a Postgres testcontainer, the
``aload_morph_data_from_url`` path must produce a ``MorphData`` that
the analyzer treats as equivalent to the YAML-loaded one. We don't
require structural identity (UUIDs, ordering of equally-keyed rows)
— we require the *analytic outputs* to be identical for a
representative slice.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from tgllfg.lex import (
    aload_morph_data_from_url,
    build_alembic_config,
    cache_to_morph_data,
)
from tgllfg.lex.loader import (
    BACKEND_ENV,
    DATABASE_URL_ENV,
    resolve_morph_data,
)
from tgllfg.lex.seed import seed_database
from tgllfg.morph import Analyzer, load_morph_data
from tgllfg.morph.analyzer import generate_form

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


def _surface_set(data: object) -> set[str]:
    return {p.surface for p in data.particles}  # type: ignore[attr-defined]


async def test_db_morph_data_matches_yaml_morph_data_shape(
    postgres_container: PostgresContainer, seeded_engine: AsyncEngine
) -> None:
    yaml_data = load_morph_data()
    db_data = await aload_morph_data_from_url(postgres_container.get_connection_url())

    assert {r.citation for r in db_data.roots} == {r.citation for r in yaml_data.roots}
    assert {(c.voice, c.aspect, c.mood, c.affix_class) for c in db_data.paradigm_cells} == {
        (c.voice, c.aspect, c.mood, c.affix_class) for c in yaml_data.paradigm_cells
    }
    assert {p.surface for p in db_data.particles} == {p.surface for p in yaml_data.particles}
    assert {p.surface for p in db_data.pronouns} == {p.surface for p in yaml_data.pronouns}


async def test_analyzer_off_db_generates_same_kain_paradigm(
    postgres_container: PostgresContainer, seeded_engine: AsyncEngine
) -> None:
    """The classic kain paradigm round-trip must succeed with the
    analyzer constructed from DB-derived MorphData."""
    db_data = await aload_morph_data_from_url(postgres_container.get_connection_url())
    yaml_data = load_morph_data()

    kain_db = next(r for r in db_data.roots if r.citation == "kain")
    kain_yaml = next(r for r in yaml_data.roots if r.citation == "kain")

    expected_pairs: list[tuple[str, str, str]] = [
        ("AV", "PFV", "kumain"),
        ("AV", "IPFV", "kumakain"),
        ("AV", "CTPL", "kakain"),
    ]

    def _find(data: object, voice: str, aspect: str, affix: str) -> object:
        for c in data.paradigm_cells:  # type: ignore[attr-defined]
            if c.voice == voice and c.aspect == aspect and c.affix_class == affix:
                return c
        raise AssertionError(f"no cell for {voice}/{aspect}/{affix}")

    for voice, aspect, surface in expected_pairs:
        cell_db = _find(db_data, voice, aspect, "um")
        cell_yaml = _find(yaml_data, voice, aspect, "um")
        assert generate_form(kain_db, cell_db) == surface  # type: ignore[arg-type]
        assert generate_form(kain_yaml, cell_yaml) == surface  # type: ignore[arg-type]


async def test_resolve_morph_data_db_backend(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(BACKEND_ENV, "db")
    monkeypatch.setenv(DATABASE_URL_ENV, postgres_container.get_connection_url())

    data = await asyncio.to_thread(resolve_morph_data)
    assert any(r.citation == "kain" for r in data.roots)


async def test_resolve_morph_data_db_requires_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(BACKEND_ENV, "db")
    monkeypatch.delenv(DATABASE_URL_ENV, raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL is unset"):
        await asyncio.to_thread(resolve_morph_data)


async def test_analyzer_from_default_with_db_backend(
    postgres_container: PostgresContainer,
    seeded_engine: AsyncEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Analyzer.from_default() honors TGLLFG_LEX_BACKEND=db."""
    monkeypatch.setenv(BACKEND_ENV, "db")
    monkeypatch.setenv(DATABASE_URL_ENV, postgres_container.get_connection_url())

    analyzer = await asyncio.to_thread(Analyzer.from_default)
    from tgllfg.common import Token

    analyses = analyzer.analyze_one(Token(surface="kumain", norm="kumain", start=0, end=6))
    assert any("VOICE" in a.feats and a.feats.get("VOICE") == "AV" for a in analyses)


def test_resolve_morph_data_default_is_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BACKEND_ENV, raising=False)
    data = resolve_morph_data()
    assert any(r.citation == "kain" for r in data.roots)


def test_cache_to_morph_data_unknown_language_returns_empty() -> None:
    from tgllfg.lex.cache import LexCache

    empty = cache_to_morph_data(LexCache(), iso_code="tgl")
    assert empty.roots == []
    assert empty.paradigm_cells == []
