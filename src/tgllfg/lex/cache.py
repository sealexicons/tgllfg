"""Parser-facing in-memory cache (frozen dataclasses, no SQLAlchemy).

The parser must not depend on SQLAlchemy. ``LexCache`` is the typed,
read-only view it sees; ``build_cache(session)`` materializes one from
a live async SQLAlchemy session by issuing a small fixed set of
``SELECT *`` queries (no per-token round-trips at parse time).

Mapping from ``LexCache`` to the legacy ``MorphData`` shape consumed
by the existing analyzer lives in Commit 5; this commit only delivers
the cache and its builder.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tgllfg.lex import models as m


@dataclass(frozen=True)
class LanguageEntry:
    id: UUID
    iso_code: str
    name: str
    notes: str | None = None


@dataclass(frozen=True)
class SourceEntry:
    id: UUID
    short_name: str
    full_citation: str
    notes: str | None = None


@dataclass(frozen=True)
class LemmaEntry:
    id: UUID
    language_id: UUID
    citation_form: str
    pos: str
    gloss: str | None = None
    source_ref: str | None = None
    transitivity: str = ""
    affix_class: tuple[str, ...] = ()
    sandhi_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class LexEntryRow:
    id: UUID
    lemma_id: UUID
    pred_template: str
    a_structure: Any
    morph_constraints: Mapping[str, Any]
    intrinsic_classification: Mapping[str, Any]
    default_mapping: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class AffixEntry:
    id: UUID
    language_id: UUID
    shape: str
    type: str
    features: Mapping[str, Any]
    position: int | None = None


@dataclass(frozen=True)
class ParadigmSlotEntry:
    paradigm_id: UUID
    position: int
    affix_id: UUID


@dataclass(frozen=True)
class ParadigmEntry:
    id: UUID
    language_id: UUID
    name: str
    slots: tuple[ParadigmSlotEntry, ...] = ()


@dataclass(frozen=True)
class ParadigmCellEntry:
    id: UUID
    language_id: UUID
    voice: str
    aspect: str
    mood: str
    transitivity: str
    affix_class: str
    operations: tuple[Mapping[str, Any], ...]
    ordering: int
    notes: str | None = None


@dataclass(frozen=True)
class SandhiRuleEntry:
    id: UUID
    language_id: UUID
    pattern: str
    replacement: str
    conditions: Mapping[str, Any]
    ordering: int


@dataclass(frozen=True)
class ParticleEntry:
    id: UUID
    language_id: UUID
    surface: str
    pos: str
    features: Mapping[str, Any]
    is_clitic: bool
    clitic_class: str | None = None


@dataclass(frozen=True)
class PronounEntry:
    id: UUID
    language_id: UUID
    surface: str
    features: Mapping[str, Any]
    is_clitic: bool


@dataclass(frozen=True)
class VoiceAliasEntry:
    id: UUID
    language_id: UUID
    label: str
    voice: str
    appl: str | None = None
    caus: str | None = None


@dataclass(frozen=True)
class LexCache:
    """Frozen, parser-facing snapshot of the entire lexicon."""

    languages: tuple[LanguageEntry, ...] = ()
    sources: tuple[SourceEntry, ...] = ()
    lemmas: tuple[LemmaEntry, ...] = ()
    lex_entries: tuple[LexEntryRow, ...] = ()
    affixes: tuple[AffixEntry, ...] = ()
    paradigms: tuple[ParadigmEntry, ...] = ()
    paradigm_cells: tuple[ParadigmCellEntry, ...] = ()
    sandhi_rules: tuple[SandhiRuleEntry, ...] = ()
    particles: tuple[ParticleEntry, ...] = ()
    pronouns: tuple[PronounEntry, ...] = ()
    voice_aliases: tuple[VoiceAliasEntry, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    particles_by_surface: Mapping[str, tuple[ParticleEntry, ...]] = field(default_factory=dict)
    pronouns_by_surface: Mapping[str, tuple[PronounEntry, ...]] = field(default_factory=dict)
    lemmas_by_citation: Mapping[str, tuple[LemmaEntry, ...]] = field(default_factory=dict)


def _group(items: list[Any], key: str) -> Mapping[str, tuple[Any, ...]]:
    out: dict[str, list[Any]] = defaultdict(list)
    for item in items:
        out[getattr(item, key)].append(item)
    return {k: tuple(v) for k, v in out.items()}


async def build_cache(session: AsyncSession) -> LexCache:
    """Build a :class:`LexCache` from a live async session.

    Issues a fixed number of ``SELECT *`` queries (one per table plus
    a slot fetch). Suitable for parser startup, not per-token paths.
    """
    languages = [
        LanguageEntry(id=r.id, iso_code=r.iso_code, name=r.name, notes=r.notes)
        for r in (await session.scalars(select(m.Language))).all()
    ]
    sources = [
        SourceEntry(
            id=r.id, short_name=r.short_name, full_citation=r.full_citation, notes=r.notes
        )
        for r in (await session.scalars(select(m.Source))).all()
    ]
    lemmas = [
        LemmaEntry(
            id=r.id,
            language_id=r.language_id,
            citation_form=r.citation_form,
            pos=r.pos,
            gloss=r.gloss,
            source_ref=r.source_ref,
            transitivity=r.transitivity or "",
            affix_class=tuple(r.affix_class or ()),
            sandhi_flags=tuple(r.sandhi_flags or ()),
        )
        for r in (await session.scalars(select(m.Lemma))).all()
    ]
    lex_entries = [
        LexEntryRow(
            id=r.id,
            lemma_id=r.lemma_id,
            pred_template=r.pred_template,
            a_structure=r.a_structure,
            morph_constraints=r.morph_constraints,
            intrinsic_classification=r.intrinsic_classification,
            default_mapping=r.default_mapping,
        )
        for r in (await session.scalars(select(m.LexEntry))).all()
    ]
    affixes = [
        AffixEntry(
            id=r.id,
            language_id=r.language_id,
            shape=r.shape,
            type=r.type,
            features=r.features,
            position=r.position,
        )
        for r in (await session.scalars(select(m.Affix))).all()
    ]
    slot_rows = (await session.scalars(select(m.ParadigmSlot))).all()
    slots_by_paradigm: dict[UUID, list[ParadigmSlotEntry]] = defaultdict(list)
    for s in slot_rows:
        slots_by_paradigm[s.paradigm_id].append(
            ParadigmSlotEntry(paradigm_id=s.paradigm_id, position=s.position, affix_id=s.affix_id)
        )
    paradigms = [
        ParadigmEntry(
            id=r.id,
            language_id=r.language_id,
            name=r.name,
            slots=tuple(sorted(slots_by_paradigm.get(r.id, []), key=lambda s: s.position)),
        )
        for r in (await session.scalars(select(m.Paradigm))).all()
    ]
    paradigm_cells = [
        ParadigmCellEntry(
            id=r.id,
            language_id=r.language_id,
            voice=r.voice,
            aspect=r.aspect,
            mood=r.mood,
            transitivity=r.transitivity or "",
            affix_class=r.affix_class or "",
            operations=tuple(r.operations),
            ordering=r.ordering,
            notes=r.notes,
        )
        for r in (await session.scalars(select(m.ParadigmCellRow))).all()
    ]
    sandhi_rules = [
        SandhiRuleEntry(
            id=r.id,
            language_id=r.language_id,
            pattern=r.pattern,
            replacement=r.replacement,
            conditions=r.conditions,
            ordering=r.ordering,
        )
        for r in (await session.scalars(select(m.SandhiRule))).all()
    ]
    particles = [
        ParticleEntry(
            id=r.id,
            language_id=r.language_id,
            surface=r.surface,
            pos=r.pos,
            features=r.features,
            is_clitic=r.is_clitic,
            clitic_class=r.clitic_class,
        )
        for r in (await session.scalars(select(m.Particle))).all()
    ]
    pronouns = [
        PronounEntry(
            id=r.id,
            language_id=r.language_id,
            surface=r.surface,
            features=r.features,
            is_clitic=r.is_clitic,
        )
        for r in (await session.scalars(select(m.Pronoun))).all()
    ]
    voice_aliases = [
        VoiceAliasEntry(
            id=r.id,
            language_id=r.language_id,
            label=r.label,
            voice=r.voice,
            appl=r.appl,
            caus=r.caus,
        )
        for r in (await session.scalars(select(m.VoiceAlias))).all()
    ]
    meta_rows = (await session.scalars(select(m.LexMetadata))).all()
    metadata = {r.key: r.value for r in meta_rows}

    return LexCache(
        languages=tuple(languages),
        sources=tuple(sources),
        lemmas=tuple(lemmas),
        lex_entries=tuple(lex_entries),
        affixes=tuple(affixes),
        paradigms=tuple(paradigms),
        paradigm_cells=tuple(paradigm_cells),
        sandhi_rules=tuple(sandhi_rules),
        particles=tuple(particles),
        pronouns=tuple(pronouns),
        voice_aliases=tuple(voice_aliases),
        metadata=metadata,
        particles_by_surface=_group(particles, "surface"),
        pronouns_by_surface=_group(pronouns, "surface"),
        lemmas_by_citation=_group(lemmas, "citation_form"),
    )


__all__ = [
    "AffixEntry",
    "LanguageEntry",
    "LemmaEntry",
    "LexCache",
    "LexEntryRow",
    "ParadigmCellEntry",
    "ParadigmEntry",
    "ParadigmSlotEntry",
    "ParticleEntry",
    "PronounEntry",
    "SandhiRuleEntry",
    "SourceEntry",
    "VoiceAliasEntry",
    "build_cache",
]
