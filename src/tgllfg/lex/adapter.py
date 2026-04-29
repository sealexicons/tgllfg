"""Convert a Postgres-backed :class:`LexCache` into the parser-facing
:class:`MorphData` shape.

The analyzer in :mod:`tgllfg.morph` consumes ``MorphData``: a flat,
list-valued container of Roots, ParadigmCells, Particles, Pronouns,
and SandhiRules. This module is the bridge from the DB-backed cache
to that shape, so the existing analyzer needs no changes when it runs
off the database.

Filtering by language: a single ``LexCache`` may carry rows for
multiple languages once §6.2 grows beyond Tagalog. ``cache_to_morph_data``
takes an ISO code and projects only that language's rows.
"""

from __future__ import annotations

from tgllfg.lex.cache import LexCache
from tgllfg.morph.paradigms import (
    MorphData,
    Operation,
    ParadigmCell,
    Particle,
    Pronoun,
    Root,
    SandhiRule,
)


def cache_to_morph_data(cache: LexCache, iso_code: str = "tgl") -> MorphData:
    """Project the ``iso_code`` slice of ``cache`` into a ``MorphData``.

    Returns an empty ``MorphData`` if the language is not present.
    """
    lang = next((entry for entry in cache.languages if entry.iso_code == iso_code), None)
    if lang is None:
        return MorphData()
    lang_id = lang.id

    roots = [
        Root(
            citation=lemma.citation_form,
            pos=lemma.pos,
            gloss=lemma.gloss or "",
            transitivity=lemma.transitivity,
            affix_class=list(lemma.affix_class),
            sandhi_flags=list(lemma.sandhi_flags),
        )
        for lemma in cache.lemmas
        if lemma.language_id == lang_id
    ]

    paradigm_cells = [
        ParadigmCell(
            voice=cell.voice,
            aspect=cell.aspect,
            mood=cell.mood,
            transitivity=cell.transitivity,
            affix_class=cell.affix_class,
            operations=[Operation(op=op["op"], value=op.get("value", "")) for op in cell.operations],
            notes=cell.notes or "",
        )
        for cell in sorted(
            (c for c in cache.paradigm_cells if c.language_id == lang_id),
            key=lambda c: c.ordering,
        )
    ]

    particles = [
        Particle(
            surface=p.surface,
            pos=p.pos,
            feats=dict(p.features),
            is_clitic=p.is_clitic,
            clitic_class=p.clitic_class or "",
        )
        for p in cache.particles
        if p.language_id == lang_id
    ]

    pronouns = [
        Pronoun(
            surface=p.surface,
            feats=dict(p.features),
            is_clitic=p.is_clitic,
        )
        for p in cache.pronouns
        if p.language_id == lang_id
    ]

    sandhi_rules = [
        SandhiRule(
            description=str(r.conditions.get("description", "")) if r.conditions else "",
            pattern=r.pattern,
            replacement=r.replacement,
            context=str(r.conditions.get("context", "")) if r.conditions else "",
        )
        for r in sorted(
            (r for r in cache.sandhi_rules if r.language_id == lang_id),
            key=lambda r: r.ordering,
        )
    ]

    return MorphData(
        roots=roots,
        paradigm_cells=paradigm_cells,
        particles=particles,
        pronouns=pronouns,
        sandhi_rules=sandhi_rules,
    )


__all__ = ["cache_to_morph_data"]
