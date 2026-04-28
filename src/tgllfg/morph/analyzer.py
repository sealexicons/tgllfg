# tgllfg/morph/analyzer.py

"""Rule-cascade morphological analyzer.

The engine pre-generates every ``(verb root × paradigm cell)``
surface form at construction time and indexes them in a hash map by
surface. Particle and pronoun lookups are also hash maps. Per-token
analysis is therefore O(1) plus a tiny constant for the few
fallbacks (noun, ``_UNK``).

Generation schedule for a paradigm cell, applied to a root in this
order:

1. ``cv_redup``  — sandhi-aware reduplication of the first CV.
2. ``infix``     — insert after first consonant
                   (or prefix if base is vowel-initial).
3. ``suffix``    — append with vowel-hiatus repair.
4. ``prefix``    — prepend.

Cells declare their operations in any order; the engine sorts by
step number before applying so the YAML can list operations in a
linguistically natural sequence without affecting the result.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common import MorphAnalysis, Token
from .loader import load_morph_data
from .paradigms import (
    MorphData,
    Operation,
    ParadigmCell,
    Root,
)
from .sandhi import (
    attach_suffix,
    cv_reduplicate,
    infix_after_first_consonant,
)


_OP_ORDER: dict[str, int] = {
    "cv_redup": 1,
    "infix":    2,
    "suffix":   3,
    "prefix":   4,
}


def generate_form(root: Root, cell: ParadigmCell) -> str:
    """Apply ``cell.operations`` to ``root.citation`` in canonical
    order and return the resulting surface form."""
    base = root.citation
    for op in sorted(cell.operations, key=lambda o: _OP_ORDER.get(o.op, 99)):
        base = _apply(op, base)
    return base


def _apply(op: Operation, base: str) -> str:
    if op.op == "cv_redup":
        return cv_reduplicate(base)
    if op.op == "infix":
        return infix_after_first_consonant(base, op.value)
    if op.op == "suffix":
        return attach_suffix(base, op.value)
    if op.op == "prefix":
        return op.value + base
    raise ValueError(f"unknown operation: {op.op!r}")


# === Analyzer state =======================================================

@dataclass
class _Index:
    """Surface-keyed lookup tables built once per analyzer instance."""
    verb_forms: dict[str, list[MorphAnalysis]] = field(default_factory=dict)
    nouns: dict[str, MorphAnalysis] = field(default_factory=dict)
    particles: dict[str, MorphAnalysis] = field(default_factory=dict)
    pronouns: dict[str, MorphAnalysis] = field(default_factory=dict)


class Analyzer:
    """Tagalog morphological analyzer driven by the seed YAML
    lexicon under ``data/tgl/``."""

    def __init__(self, data: MorphData) -> None:
        self._data = data
        self._index = _Index()
        self._build_index()

    @classmethod
    def from_default(cls) -> "Analyzer":
        """Construct an analyzer using the seed lexicon shipped with
        the package."""
        return cls(load_morph_data())

    def analyze_one(self, token: Token) -> list[MorphAnalysis]:
        """Return all analyses for a single token, in priority order:
        particles, pronouns, verb forms, nouns. Falls back to a
        single ``_UNK`` analysis if nothing matches."""
        n = token.norm
        out: list[MorphAnalysis] = []
        if n in self._index.particles:
            out.append(self._index.particles[n])
        if n in self._index.pronouns:
            out.append(self._index.pronouns[n])
        if n in self._index.verb_forms:
            out.extend(self._index.verb_forms[n])
        if n in self._index.nouns:
            out.append(self._index.nouns[n])
        if not out:
            out.append(MorphAnalysis(lemma=n, pos="_UNK", feats={}))
        return out

    def analyze(self, tokens: list[Token]) -> list[list[MorphAnalysis]]:
        return [self.analyze_one(t) for t in tokens]

    # --- Index construction -----------------------------------------------

    def _build_index(self) -> None:
        for p in self._data.particles:
            self._index.particles[p.surface.lower()] = MorphAnalysis(
                lemma=p.surface,
                pos=p.pos,
                feats=dict(p.feats),
            )
        for pn in self._data.pronouns:
            self._index.pronouns[pn.surface.lower()] = MorphAnalysis(
                lemma=pn.surface,
                pos="PRON",
                feats=dict(pn.feats),
            )
        for r in self._data.roots:
            if r.pos == "VERB":
                self._index_verb_paradigms(r)
            elif r.pos == "NOUN":
                self._index.nouns[r.citation.lower()] = MorphAnalysis(
                    lemma=r.citation,
                    pos="NOUN",
                    feats={},
                )

    def _index_verb_paradigms(self, root: Root) -> None:
        for cell in self._data.paradigm_cells:
            if cell.transitivity and cell.transitivity != root.transitivity:
                continue
            surface = generate_form(root, cell).lower()
            feats: dict[str, object] = {
                "VOICE": cell.voice,
                "ASPECT": cell.aspect,
                "MOOD": cell.mood,
            }
            if root.transitivity:
                feats["TR"] = root.transitivity
            analysis = MorphAnalysis(
                lemma=root.citation,
                pos="VERB",
                feats=feats,
            )
            self._index.verb_forms.setdefault(surface, []).append(analysis)


# === Module-level entry point ============================================

_default_analyzer: Analyzer | None = None


def _get_default() -> Analyzer:
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = Analyzer.from_default()
    return _default_analyzer


def analyze_tokens(tokens: list[Token]) -> list[list[MorphAnalysis]]:
    """Public entry point: analyze a list of tokens against the
    default seed lexicon. Backward-compatible with the prototype's
    signature."""
    return _get_default().analyze(tokens)


__all__ = [
    "Analyzer",
    "analyze_tokens",
    "generate_form",
]
