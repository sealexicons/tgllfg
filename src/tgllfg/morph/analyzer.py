# tgllfg/morph/analyzer.py

"""Rule-cascade morphological analyzer.

The engine pre-generates every ``(verb root × paradigm cell)``
surface form at construction time and indexes them in a hash map by
surface. Particle and pronoun lookups are also hash maps. Per-token
analysis is therefore O(1) plus a tiny constant for the few
fallbacks (noun, ``_UNK``).

Operations are applied to the root in YAML-declared order — the
engine does not reorder them. This matters for paradigms like
mang- distributive IPFV where the reduplication target is the
*post-substitution* base (``bili`` → ``mili`` via nasal substitution
→ ``mimili`` via cv_redup → ``namimili`` via prefix).

Operation vocabulary:

* ``cv_redup``         — prepend the first CV of the current base.
* ``infix``            — insert ``value`` after first consonant
                         (or as prefix when base is vowel-initial).
* ``suffix``           — append ``value`` with vowel-hiatus repair.
* ``prefix``           — prepend ``value`` (e.g. ``nag-``, ``mag-``,
                         ``naka-``, ``maka-``, the ``i-`` of IV, or
                         the head ``na-`` / ``ma-`` of a nasal-final
                         prefix that has already had its final ``ng``
                         consumed by ``nasal_substitute``).
* ``nasal_substitute`` — replace the base's first consonant with the
                         homorganic nasal: b/p → m, t/d/s → n,
                         k/g → ng. Used by mang- distributive
                         paradigms; the trailing ``ng`` of the prefix
                         is supplied by this operation, leaving the
                         author to prepend just ``na-`` / ``ma-`` /
                         ``pa-``.

Affix-class filtering: a cell with a non-empty ``affix_class`` only
fires for roots whose ``affix_class`` list contains that string.
This prevents a ``-um-`` only root like ``kain`` from generating
``mag-`` or ``mang-`` forms that don't exist in the language.
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
    nasal_substitute,
)


def generate_form(root: Root, cell: ParadigmCell) -> str:
    """Apply ``cell.operations`` to ``root.citation`` in YAML-declared
    order and return the resulting surface form."""
    base = root.citation
    for op in cell.operations:
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
    if op.op == "nasal_substitute":
        return nasal_substitute(base)
    raise ValueError(f"unknown operation: {op.op!r}")


# === Analyzer state =======================================================

@dataclass
class _Index:
    """Surface-keyed lookup tables built once per analyzer instance.
    Particles and verb_forms are list-valued because a single surface
    can carry multiple analyses (e.g. ``na`` is both the linker and
    the aspectual second-position enclitic ``na`` "already")."""
    verb_forms: dict[str, list[MorphAnalysis]] = field(default_factory=dict)
    nouns: dict[str, MorphAnalysis] = field(default_factory=dict)
    particles: dict[str, list[MorphAnalysis]] = field(default_factory=dict)
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
            out.extend(self._index.particles[n])
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
            self._index.particles.setdefault(p.surface.lower(), []).append(
                MorphAnalysis(
                    lemma=p.surface,
                    pos=p.pos,
                    feats=dict(p.feats),
                )
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
            if not _affix_class_match(cell.affix_class, root.affix_class):
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


def _affix_class_match(cell_class: str, root_classes: list[str]) -> bool:
    """Filter rule: a cell with a non-empty affix_class only fires for
    roots whose affix_class list contains it. A cell with no
    affix_class (the default for the original AV/OV/DV/IV-um/in/an/i
    paradigms) fires for any root — this preserves backward
    compatibility with the seed authored before affix_class existed."""
    if not cell_class:
        return True
    return cell_class in root_classes


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
