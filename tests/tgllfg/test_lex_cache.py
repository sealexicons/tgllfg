"""Tests for the SQLAlchemy models, async repository, and LexCache builder.

A single Postgres testcontainer is migrated, seeded with a minimal
fixture set covering every table, and then queried through both the
repository and the cache builder. Verifies:

* ORM models map cleanly to the §6.2 schema (insert/select round-trip).
* ``AsyncLexRepository`` returns frozen dataclasses, not ORM rows.
* ``build_cache`` populates every collection and the surface indexes.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from tgllfg.lex import AsyncLexRepository, build_alembic_config, build_cache

pytestmark = pytest.mark.postgres


@pytest_asyncio.fixture
async def migrated_engine(
    postgres_container: PostgresContainer,
) -> AsyncIterator[AsyncEngine]:
    """A freshly migrated database with one full row per table."""
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

    lang_id = uuid.uuid4()
    lemma_id = uuid.uuid4()
    affix_id = uuid.uuid4()
    paradigm_id = uuid.uuid4()
    async with sessionmaker() as session:
        await session.execute(
            text("INSERT INTO language (id, iso_code, name) VALUES (:i, 'tgl', 'Tagalog')"),
            {"i": lang_id},
        )
        await session.execute(
            text(
                "INSERT INTO source (short_name, full_citation) "
                "VALUES ('Kroeger1993', 'Kroeger 1993, Phrase Structure...')"
            )
        )
        await session.execute(
            text(
                "INSERT INTO lemma (id, language_id, citation_form, pos, gloss) "
                "VALUES (:i, :l, 'kain', 'VERB', 'eat')"
            ),
            {"i": lemma_id, "l": lang_id},
        )
        await session.execute(
            text(
                "INSERT INTO lex_entry "
                "(lemma_id, pred_template, a_structure, morph_constraints, "
                "intrinsic_classification) "
                "VALUES (:l, 'EAT <SUBJ, OBJ>', :a, :m, :ic)"
            ),
            {
                "l": lemma_id,
                "a": json.dumps(["AGENT", "PATIENT"]),
                "m": json.dumps({"VOICE": "OV"}),
                "ic": json.dumps({"AGENT": {"r": "-", "o": "-"}}),
            },
        )
        await session.execute(
            text(
                "INSERT INTO affix (id, language_id, shape, type, features, position) "
                "VALUES (:i, :l, 'um', 'INFIX', :f, 0)"
            ),
            {
                "i": affix_id,
                "l": lang_id,
                "f": json.dumps({"VOICE": "AV", "ASPECT": "PFV"}),
            },
        )
        await session.execute(
            text(
                "INSERT INTO paradigm (id, language_id, name) "
                "VALUES (:i, :l, 'verb_voice_aspect')"
            ),
            {"i": paradigm_id, "l": lang_id},
        )
        await session.execute(
            text(
                "INSERT INTO paradigm_slot (paradigm_id, position, affix_id) "
                "VALUES (:p, 0, :a)"
            ),
            {"p": paradigm_id, "a": affix_id},
        )
        await session.execute(
            text(
                "INSERT INTO sandhi_rule (language_id, pattern, replacement, conditions, ordering) "
                "VALUES (:l, 'V_V', 'V_h_V', :c, 0)"
            ),
            {"l": lang_id, "c": json.dumps({"context": "vowel-hiatus"})},
        )
        await session.execute(
            text(
                "INSERT INTO particle "
                "(language_id, surface, pos, features, is_clitic) "
                "VALUES (:l, 'ang', 'DET', :f, FALSE)"
            ),
            {"l": lang_id, "f": json.dumps({"CASE": "NOM"})},
        )
        await session.execute(
            text(
                "INSERT INTO pronoun (language_id, surface, features, is_clitic) "
                "VALUES (:l, 'ako', :f, FALSE)"
            ),
            {"l": lang_id, "f": json.dumps({"PERS": 1, "NUM": "SG", "CASE": "NOM"})},
        )
        await session.execute(
            text(
                "INSERT INTO voice_alias (language_id, label, voice) VALUES (:l, 'AF', 'AV')"
            ),
            {"l": lang_id},
        )
        await session.execute(
            text("INSERT INTO lex_metadata (key, value) VALUES ('data_version', '0.0.1')")
        )
        await session.commit()

    try:
        yield engine
    finally:
        await engine.dispose()


async def test_repository_language_lookup(migrated_engine: AsyncEngine) -> None:
    sessionmaker = async_sessionmaker(migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        repo = AsyncLexRepository(session)
        lang = await repo.get_language_by_iso("tgl")
        assert lang is not None
        assert lang.iso_code == "tgl"
        assert lang.name == "Tagalog"
        assert await repo.get_language_by_iso("xxx") is None


async def test_repository_particle_and_pronoun_lookup(migrated_engine: AsyncEngine) -> None:
    sessionmaker = async_sessionmaker(migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        repo = AsyncLexRepository(session)
        ang = await repo.find_particles_by_surface("ang")
        assert len(ang) == 1
        assert ang[0].pos == "DET"
        assert ang[0].features == {"CASE": "NOM"}

        ako = await repo.find_pronouns_by_surface("ako")
        assert len(ako) == 1
        assert ako[0].features["PERS"] == 1


async def test_repository_metadata_lookup(migrated_engine: AsyncEngine) -> None:
    sessionmaker = async_sessionmaker(migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        repo = AsyncLexRepository(session)
        assert await repo.get_metadata("data_version") == "0.0.1"
        assert await repo.get_metadata("nonexistent") is None


async def test_build_cache_populates_every_collection(migrated_engine: AsyncEngine) -> None:
    sessionmaker = async_sessionmaker(migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        cache = await build_cache(session)

    assert len(cache.languages) == 1
    assert len(cache.sources) == 1
    assert len(cache.lemmas) == 1
    assert len(cache.lex_entries) == 1
    assert len(cache.affixes) == 1
    assert len(cache.paradigms) == 1
    assert len(cache.sandhi_rules) == 1
    assert len(cache.particles) == 1
    assert len(cache.pronouns) == 1
    assert len(cache.voice_aliases) == 1
    assert cache.metadata == {"data_version": "0.0.1"}

    assert cache.paradigms[0].slots[0].position == 0
    assert cache.lex_entries[0].pred_template == "EAT <SUBJ, OBJ>"
    assert cache.lex_entries[0].a_structure == ["AGENT", "PATIENT"]


async def test_build_cache_surface_indexes(migrated_engine: AsyncEngine) -> None:
    sessionmaker = async_sessionmaker(migrated_engine, expire_on_commit=False)
    async with sessionmaker() as session:
        cache = await build_cache(session)

    assert "ang" in cache.particles_by_surface
    assert cache.particles_by_surface["ang"][0].pos == "DET"
    assert "ako" in cache.pronouns_by_surface
    assert cache.pronouns_by_surface["ako"][0].features["NUM"] == "SG"
    assert "kain" in cache.lemmas_by_citation
    assert cache.lemmas_by_citation["kain"][0].pos == "VERB"
