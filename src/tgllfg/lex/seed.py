"""YAML → Postgres seed loader for the §6.2 lexicon.

Reads the existing ``data/tgl/`` YAML files (the same source the
in-process morphology engine consumes) and upserts them into the
Postgres-backed schema. Idempotent: re-running produces zero diffs.

Scope: this commit seeds the data classes that map cleanly between
the YAML shape and §6.2 — ``language``, ``lemma``, ``affix``,
``sandhi_rule``, ``particle``, ``pronoun``, plus a ``data_version``
row in ``lex_metadata``. The richer ``lex_entry`` /
``paradigm`` / ``paradigm_slot`` / ``voice_alias`` mappings, which
require deriving ``pred_template`` and structured argument frames
from a-structure semantics, land in Commit 5 alongside the parser
wiring.

Idempotency strategy:

* ``language`` and ``lex_metadata`` use ``ON CONFLICT DO UPDATE``
  upserts on their natural keys.
* ``lemma`` upserts on the (``language_id``, ``citation_form``,
  ``pos``) unique constraint; the gloss column is refreshed on each
  run so YAML edits propagate.
* ``particle``, ``pronoun``, ``affix``, and ``sandhi_rule`` lack
  natural unique keys in §6.2 (homophones are first-class for
  particles), so for these the seed truncates the language's rows
  and re-inserts. YAML is the source of truth for these tables; the
  ``lex import`` CLI (Commit 6) is the path for additive data with
  citations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tgllfg.lex import models as m
from tgllfg.morph.loader import load_morph_data

DATA_VERSION = "0.1.0"
DEFAULT_LANGUAGE_ISO = "tgl"
DEFAULT_LANGUAGE_NAME = "Tagalog"

_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "tgl"

logger = logging.getLogger(__name__)


@dataclass
class SeedReport:
    """Counts of rows present in each table after seeding completes.

    The seed runs in a single transaction; counts are observed at the
    end of that transaction and are exact, not deltas.
    """

    languages: int
    lemmas: int
    affixes: int
    paradigm_cells: int
    sandhi_rules: int
    particles: int
    pronouns: int
    metadata_keys: int


def _ensure_async_url(url: str) -> str:
    """Coerce a plain ``postgresql://`` URL to the asyncpg variant."""
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


def _read_yaml_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        loaded = yaml.safe_load(fh)
    if loaded is None:
        return []
    if not isinstance(loaded, list):
        raise ValueError(f"{path}: expected top-level list, got {type(loaded).__name__}")
    return loaded


async def _upsert_language(session: AsyncSession, iso_code: str, name: str) -> UUID:
    stmt = (
        pg_insert(m.Language)
        .values(iso_code=iso_code, name=name)
        .on_conflict_do_update(
            index_elements=["iso_code"],
            set_={"name": name},
        )
        .returning(m.Language.id)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def _upsert_lemmas(
    session: AsyncSession, language_id: UUID, roots: list[Any]
) -> int:
    if not roots:
        return 0
    rows = [
        {
            "language_id": language_id,
            "citation_form": r.citation,
            "pos": r.pos,
            "gloss": r.gloss or None,
            "transitivity": r.transitivity or "",
            "affix_class": list(r.affix_class or ()),
            "sandhi_flags": list(r.sandhi_flags or ()),
        }
        for r in roots
    ]
    stmt = pg_insert(m.Lemma).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_lemma_lang_form_pos",
        set_={
            "gloss": stmt.excluded.gloss,
            "transitivity": stmt.excluded.transitivity,
            "affix_class": stmt.excluded.affix_class,
            "sandhi_flags": stmt.excluded.sandhi_flags,
        },
    )
    await session.execute(stmt)
    return len(rows)


async def _replace_particles(
    session: AsyncSession, language_id: UUID, particles: list[Any]
) -> int:
    await session.execute(
        text("DELETE FROM particle WHERE language_id = :l"), {"l": language_id}
    )
    if not particles:
        return 0
    rows = [
        {
            "language_id": language_id,
            "surface": p.surface,
            "pos": p.pos,
            "features": dict(p.feats),
            "is_clitic": bool(p.is_clitic),
            "clitic_class": (p.clitic_class or None),
        }
        for p in particles
    ]
    await session.execute(pg_insert(m.Particle).values(rows))
    return len(rows)


async def _replace_pronouns(
    session: AsyncSession, language_id: UUID, pronouns: list[Any]
) -> int:
    await session.execute(
        text("DELETE FROM pronoun WHERE language_id = :l"), {"l": language_id}
    )
    if not pronouns:
        return 0
    rows = [
        {
            "language_id": language_id,
            "surface": p.surface,
            "features": dict(p.feats),
            "is_clitic": bool(p.is_clitic),
        }
        for p in pronouns
    ]
    await session.execute(pg_insert(m.Pronoun).values(rows))
    return len(rows)


async def _replace_paradigm_cells(
    session: AsyncSession, language_id: UUID, cells: list[Any]
) -> int:
    await session.execute(
        text("DELETE FROM paradigm_cell WHERE language_id = :l"), {"l": language_id}
    )
    if not cells:
        return 0
    rows = []
    for i, c in enumerate(cells):
        rows.append(
            {
                "language_id": language_id,
                "voice": c.voice,
                "aspect": c.aspect,
                "mood": c.mood or "IND",
                "transitivity": c.transitivity or "",
                "affix_class": c.affix_class or "",
                "operations": [{"op": op.op, "value": op.value} for op in c.operations],
                "ordering": i,
                "notes": (c.notes or None),
            }
        )
    await session.execute(pg_insert(m.ParadigmCellRow).values(rows))
    return len(rows)


async def _replace_sandhi_rules(
    session: AsyncSession, language_id: UUID, rules: list[Any]
) -> int:
    await session.execute(
        text("DELETE FROM sandhi_rule WHERE language_id = :l"), {"l": language_id}
    )
    if not rules:
        return 0
    rows = []
    for i, r in enumerate(rules):
        rows.append(
            {
                "language_id": language_id,
                "pattern": r.pattern or "",
                "replacement": r.replacement or "",
                "conditions": {
                    "context": r.context or "",
                    "description": r.description or "",
                },
                "ordering": i,
            }
        )
    await session.execute(pg_insert(m.SandhiRule).values(rows))
    return len(rows)


async def _replace_affixes(
    session: AsyncSession, language_id: UUID, affix_records: list[dict[str, Any]]
) -> int:
    await session.execute(
        text("DELETE FROM affix WHERE language_id = :l"), {"l": language_id}
    )
    if not affix_records:
        return 0
    rows = []
    for i, rec in enumerate(affix_records):
        if "shape" not in rec or "position" not in rec:
            raise ValueError(f"affix record {i}: missing 'shape' or 'position'")
        rows.append(
            {
                "language_id": language_id,
                "shape": rec["shape"],
                # The §6.2 schema's `type` column corresponds to the
                # YAML's `position` field (PREFIX/INFIX/SUFFIX/...);
                # the schema's `position` integer is just an ordering
                # offset within the YAML inventory.
                "type": rec["position"],
                "features": dict(rec.get("features", {})),
                "position": i,
                "notes": rec.get("notes"),
            }
        )
    await session.execute(pg_insert(m.Affix).values(rows))
    return len(rows)


async def _upsert_metadata(session: AsyncSession, key: str, value: str) -> None:
    stmt = (
        pg_insert(m.LexMetadata)
        .values(key=key, value=value)
        .on_conflict_do_update(index_elements=["key"], set_={"value": value})
    )
    await session.execute(stmt)


async def _count(session: AsyncSession, table: str) -> int:
    result = await session.execute(text(f"SELECT count(*) FROM {table}"))
    return int(result.scalar_one())


async def seed_database(
    database_url: str,
    data_dir: Path | None = None,
    *,
    iso_code: str = DEFAULT_LANGUAGE_ISO,
    language_name: str = DEFAULT_LANGUAGE_NAME,
    data_version: str = DATA_VERSION,
) -> SeedReport:
    """Seed the Postgres lexicon from the YAML files under ``data_dir``.

    The whole operation runs in a single transaction. ``database_url``
    may be the plain ``postgresql://`` form; it is rewritten to
    ``postgresql+asyncpg://`` automatically.
    """
    base = Path(data_dir) if data_dir is not None else _DEFAULT_DATA_DIR
    morph = load_morph_data(base)
    affix_records = _read_yaml_list(base / "affixes.yaml")

    engine = create_async_engine(_ensure_async_url(database_url), future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessionmaker() as session:
            async with session.begin():
                language_id = await _upsert_language(session, iso_code, language_name)
                await _upsert_lemmas(session, language_id, morph.roots)
                await _replace_affixes(session, language_id, affix_records)
                await _replace_paradigm_cells(session, language_id, morph.paradigm_cells)
                await _replace_sandhi_rules(session, language_id, morph.sandhi_rules)
                await _replace_particles(session, language_id, morph.particles)
                await _replace_pronouns(session, language_id, morph.pronouns)
                await _upsert_metadata(session, "data_version", data_version)

            async with session.begin():
                report = SeedReport(
                    languages=await _count(session, "language"),
                    lemmas=await _count(session, "lemma"),
                    affixes=await _count(session, "affix"),
                    paradigm_cells=await _count(session, "paradigm_cell"),
                    sandhi_rules=await _count(session, "sandhi_rule"),
                    particles=await _count(session, "particle"),
                    pronouns=await _count(session, "pronoun"),
                    metadata_keys=await _count(session, "lex_metadata"),
                )
    finally:
        await engine.dispose()

    logger.info("seed complete: %s", report)
    return report


__all__ = ["DATA_VERSION", "SeedReport", "seed_database"]
