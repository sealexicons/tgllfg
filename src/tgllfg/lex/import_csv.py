"""CSV ingestion for additive lemma data with citation tracking.

Where ``seed_database`` loads the project-owned YAML into the
lexicon, ``import_lemmas_csv`` is the path for *external* lemma
data — public-domain wordlists, OCR'd dictionaries, and so on —
where each row carries a citation back to its source. Per plan §6.3
these imports are tracked in the ``source`` table so a lemma's
origin is queryable.

CSV format (one row per lemma; header required):

    citation_form,pos,gloss,transitivity,affix_class

* ``citation_form`` and ``pos`` are required; the (language, form,
  pos) tuple is the natural key used for UPSERT.
* ``gloss`` is optional; empty strings become NULL.
* ``transitivity`` is optional ("TR" / "INTR" / blank).
* ``affix_class`` is a semicolon-delimited list ("um;mag" → ["um", "mag"]).

The source is supplied at import time, not per row: every row in the
file is attributed to the same ``source.short_name``.
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tgllfg.lex import models as m
from tgllfg.lex.seed import _ensure_async_url

logger = logging.getLogger(__name__)


@dataclass
class ImportReport:
    """Result of importing a CSV: total rows seen vs. rows that
    actually upserted (counted as INSERT-or-UPDATE)."""

    rows_read: int
    rows_upserted: int
    source_short_name: str


def _parse_affix_class(value: str) -> list[str]:
    return [s.strip() for s in value.split(";") if s.strip()]


async def import_lemmas_csv(
    database_url: str,
    csv_path: Path,
    *,
    source_short_name: str,
    source_full_citation: str,
    iso_code: str = "tgl",
) -> ImportReport:
    """Idempotent UPSERT of CSV lemmas into the Postgres lexicon.

    The source row is upserted on ``short_name``; lemmas are upserted
    on ``(language_id, citation_form, pos)`` and have their
    ``source_ref`` set to the source's ``short_name``.
    """
    rows_read = 0
    rows_upserted = 0

    engine = create_async_engine(_ensure_async_url(database_url), future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessionmaker() as session:
            async with session.begin():
                lang_id = await _resolve_language_id(session, iso_code)
                await _upsert_source(session, source_short_name, source_full_citation)

                with csv_path.open(encoding="utf-8", newline="") as fh:
                    reader = csv.DictReader(fh)
                    batch: list[dict[str, object]] = []
                    for row in reader:
                        rows_read += 1
                        citation = (row.get("citation_form") or "").strip()
                        pos = (row.get("pos") or "").strip()
                        if not citation or not pos:
                            raise ValueError(
                                f"{csv_path}:{rows_read + 1}: missing citation_form or pos"
                            )
                        batch.append(
                            {
                                "language_id": lang_id,
                                "citation_form": citation,
                                "pos": pos,
                                "gloss": (row.get("gloss") or "").strip() or None,
                                "transitivity": (row.get("transitivity") or "").strip(),
                                "affix_class": _parse_affix_class(
                                    row.get("affix_class") or ""
                                ),
                                "source_ref": source_short_name,
                            }
                        )

                if batch:
                    stmt = pg_insert(m.Lemma).values(batch)
                    stmt = stmt.on_conflict_do_update(
                        constraint="uq_lemma_lang_form_pos",
                        set_={
                            "gloss": stmt.excluded.gloss,
                            "transitivity": stmt.excluded.transitivity,
                            "affix_class": stmt.excluded.affix_class,
                            "source_ref": stmt.excluded.source_ref,
                        },
                    )
                    await session.execute(stmt)
                    rows_upserted = len(batch)
    finally:
        await engine.dispose()

    logger.info(
        "imported %d/%d lemmas from %s (source=%s)",
        rows_upserted,
        rows_read,
        csv_path,
        source_short_name,
    )
    return ImportReport(
        rows_read=rows_read,
        rows_upserted=rows_upserted,
        source_short_name=source_short_name,
    )


async def _resolve_language_id(session: object, iso_code: str) -> UUID:
    result = await session.execute(  # type: ignore[attr-defined]
        text("SELECT id FROM language WHERE iso_code = :i"), {"i": iso_code}
    )
    row = result.one_or_none()
    if row is None:
        raise RuntimeError(
            f"language with iso_code={iso_code!r} not found; run `tgllfg lex seed` first"
        )
    return row[0]


async def _upsert_source(session: object, short_name: str, full_citation: str) -> None:
    stmt = (
        pg_insert(m.Source)
        .values(short_name=short_name, full_citation=full_citation)
        .on_conflict_do_update(
            index_elements=["short_name"],
            set_={"full_citation": full_citation},
        )
    )
    await session.execute(stmt)  # type: ignore[attr-defined]


__all__ = ["ImportReport", "import_lemmas_csv"]
