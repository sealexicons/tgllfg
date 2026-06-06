# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Async repository for lexicon read paths.

A thin wrapper around an :class:`AsyncSession` that exposes the
read methods Phase 3 actually needs: by-iso-code language lookup, full
table scans (small tables), and a couple of indexed surface lookups
that the parser falls back to when the in-memory cache misses.

The repository never returns ORM rows directly — the parser side is
SQLAlchemy-free. Methods either return a built ``LexCache`` (for
startup) or a list of frozen dataclasses (for ad-hoc queries).
"""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tgllfg.lex import cache as c
from tgllfg.lex import models as m


@dataclass(frozen=True)
class LemmaMatch:
    """A fuzzy lemma-search hit plus its pg_trgm similarity score."""

    id: UUID
    language_id: UUID
    citation_form: str
    pos: str
    gloss: str | None
    score: float


class AsyncLexRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_language_by_iso(self, iso_code: str) -> c.LanguageEntry | None:
        row = (
            await self._session.scalars(select(m.Language).where(m.Language.iso_code == iso_code))
        ).one_or_none()
        if row is None:
            return None
        return c.LanguageEntry(id=row.id, iso_code=row.iso_code, name=row.name, notes=row.notes)

    async def find_particles_by_surface(self, surface: str) -> list[c.ParticleEntry]:
        rows = (
            await self._session.scalars(select(m.Particle).where(m.Particle.surface == surface))
        ).all()
        return [
            c.ParticleEntry(
                id=r.id,
                language_id=r.language_id,
                surface=r.surface,
                pos=r.pos,
                features=r.features,
                is_clitic=r.is_clitic,
                clitic_class=r.clitic_class,
            )
            for r in rows
        ]

    async def find_pronouns_by_surface(self, surface: str) -> list[c.PronounEntry]:
        rows = (
            await self._session.scalars(select(m.Pronoun).where(m.Pronoun.surface == surface))
        ).all()
        return [
            c.PronounEntry(
                id=r.id,
                language_id=r.language_id,
                surface=r.surface,
                features=r.features,
                is_clitic=r.is_clitic,
            )
            for r in rows
        ]

    async def get_metadata(self, key: str) -> str | None:
        row = (
            await self._session.scalars(
                select(m.LexMetadata).where(m.LexMetadata.key == key)
            )
        ).one_or_none()
        return None if row is None else row.value

    async def search_lemmas(self, query: str, *, limit: int = 20) -> list[LemmaMatch]:
        """Fuzzy-match ``query`` against lemma citation forms via pg_trgm
        similarity (the GIN trgm index ``ix_lemma_citation_form_trgm``).
        Returns up to ``limit`` hits above pg_trgm's similarity threshold,
        best score first."""
        score = func.similarity(m.Lemma.citation_form, query)
        stmt = (
            select(m.Lemma, score.label("score"))
            .where(m.Lemma.citation_form.op("%")(query))
            .order_by(score.desc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            LemmaMatch(
                id=lemma.id,
                language_id=lemma.language_id,
                citation_form=lemma.citation_form,
                pos=lemma.pos,
                gloss=lemma.gloss,
                score=float(sc),
            )
            for lemma, sc in rows
        ]

    async def build_cache(self) -> c.LexCache:
        return await c.build_cache(self._session)


__all__ = ["AsyncLexRepository", "LemmaMatch"]
