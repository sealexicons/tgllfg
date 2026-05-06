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

import re
from dataclasses import dataclass, field

from ..core.common import MorphAnalysis, Token
from .paradigms import (
    MorphData,
    Operation,
    ParadigmCell,
    Root,
)
from .sandhi import (
    attach_suffix,
    cv_reduplicate,
    d_to_r_intervocalic,
    infix_after_first_consonant,
    nasal_assim_prefix,
    nasal_substitute,
)

# Phase 5f closing deferral (digit tokenization): a bare digit string
# (``5``, ``1990``, ``42``) analyses as a cardinal NUM, parallel to
# the word-form cardinals (``isa`` / ``dalawa`` / ``tatlo`` / ...) in
# ``data/tgl/particles.yaml``. The same NP-internal modifier /
# predicative-cardinal / arithmetic-predicate / decimal-NUM rules
# that consume ``CARDINAL=YES`` daughters then accept the digit form
# unchanged. ASCII digits only (``\d`` would also match Arabic-Indic
# / Devanagari digits, which the corpus doesn't use).
_DIGIT_RE = re.compile(r"^[0-9]+$")


def generate_form(root: Root, cell: ParadigmCell) -> str:
    """Apply ``cell.operations`` to ``root.citation`` in YAML-declared
    order and return the resulting surface form.

    Per-root sandhi flags (Phase 2C) are applied at the appropriate
    stage: ``high_vowel_deletion`` modifies suffix attachment;
    ``d_to_r`` runs as a post-processor over the final form so it
    catches both intra-stem and stem-suffix intervocalic /d/.

    Accepts any :class:`ParadigmCell` (the base) or its subclasses
    (:class:`VerbalCell` for verbal-paradigm cells,
    :class:`AdjectiveCell` for Phase 5g adjective derivation). The
    function only consumes ``cell.operations``, which lives on the
    base, so the operation-application engine is shared across both
    paradigm families.
    """
    flags = set(root.sandhi_flags)
    base = root.citation
    for op in cell.operations:
        base = _apply(op, base, flags)
    if "d_to_r" in flags:
        base = d_to_r_intervocalic(base)
    return base


def _apply(op: Operation, base: str, flags: set[str]) -> str:
    if op.op == "cv_redup":
        return cv_reduplicate(base)
    if op.op == "infix":
        return infix_after_first_consonant(base, op.value)
    if op.op == "suffix":
        return attach_suffix(
            base, op.value, high_vowel_deletion="high_vowel_deletion" in flags
        )
    if op.op == "prefix":
        return op.value + base
    if op.op == "nasal_substitute":
        return nasal_substitute(base)
    if op.op == "nasal_assim_prefix":
        return nasal_assim_prefix(op.value, base)
    raise ValueError(f"unknown operation: {op.op!r}")


# === Analyzer state =======================================================

@dataclass
class _Index:
    """Surface-keyed lookup tables built once per analyzer instance.
    All list-valued tables permit multiple analyses per surface (e.g.
    ``na`` is both the linker and the aspectual 2P enclitic, and
    ``kuwarto`` carries both "room" and "quarter-of-hour" NOUN readings
    — Phase 5f closing deferral on multiple lex entries per ``(lemma,
    pos)`` tuple). Phase 5g adds the ``adjectives`` table for
    productively-derived ADJ surfaces (``maganda``, ``matanda``, etc.)."""
    verb_forms: dict[str, list[MorphAnalysis]] = field(default_factory=dict)
    nouns: dict[str, list[MorphAnalysis]] = field(default_factory=dict)
    adjectives: dict[str, list[MorphAnalysis]] = field(default_factory=dict)
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
        """Construct an analyzer using the backend selected by
        ``TGLLFG_LEX_BACKEND`` (default ``yaml``). When the env var
        is unset or set to ``yaml``, this is the legacy YAML path.
        Set it to ``db`` to load from a Postgres lexicon at
        ``DATABASE_URL`` (Phase 3+)."""
        from tgllfg.lex.loader import resolve_morph_data

        return cls(resolve_morph_data())

    def analyze_one(self, token: Token) -> list[MorphAnalysis]:
        """Return all analyses for a single token, in enumeration order:
        digit-form cardinal, particles, pronouns, verb forms,
        adjectives, nouns. Falls back to a single ``_UNK`` analysis if
        nothing matches. Order here is presentational — the ranker
        decides priority among the multi-analysis output.
        """
        n = token.norm
        out: list[MorphAnalysis] = []
        if _DIGIT_RE.match(n):
            value = int(n)
            out.append(MorphAnalysis(
                lemma=n,
                pos="NUM",
                feats={
                    "CARDINAL": "YES",
                    "CARDINAL_VALUE": n,
                    "DIGIT_FORM": "YES",
                    "NUM": "SG" if value == 1 else "PL",
                },
            ))
        if n in self._index.particles:
            out.extend(self._index.particles[n])
        if n in self._index.pronouns:
            out.append(self._index.pronouns[n])
        if n in self._index.verb_forms:
            out.extend(self._index.verb_forms[n])
        if n in self._index.adjectives:
            out.extend(self._index.adjectives[n])
        if n in self._index.nouns:
            out.extend(self._index.nouns[n])
        if not out:
            out.append(MorphAnalysis(lemma=n, pos="_UNK", feats={}))
        return out

    def analyze(self, tokens: list[Token]) -> list[list[MorphAnalysis]]:
        return [self.analyze_one(t) for t in tokens]

    def is_known_surface(self, norm: str) -> bool:
        """True iff a non-_UNK analysis exists for ``norm`` (lower-cased
        surface)."""
        idx = self._index
        return (
            norm in idx.particles
            or norm in idx.pronouns
            or norm in idx.verb_forms
            or norm in idx.adjectives
            or norm in idx.nouns
        )

    # --- Index construction -----------------------------------------------

    def _build_index(self) -> None:
        for p in self._data.particles:
            feats: dict[str, object] = dict(p.feats)
            if p.is_clitic:
                # Phase 4 §7.3: ``is_clitic`` (boolean) drives
                # pre-parse clitic placement; it is invisible to the
                # grammar because only str-valued feats are emitted as
                # lex equations / category-pattern features.
                feats["is_clitic"] = True
            if p.clitic_class:
                # ``CLITIC_CLASS`` (string, e.g. "2P") *is* exposed to
                # the grammar so rules can match ``PART[CLITIC_CLASS=2P]``
                # for the Wackernagel-cluster attachment.
                feats["CLITIC_CLASS"] = p.clitic_class
            # Phase 4 §7.8: default DEM=NO on DET/ADP entries that
            # don't explicitly mark DEM. The standalone-demonstrative
            # NP rule expects ``DEM=YES``; without the sentinel,
            # plain ``ang`` / ``ng`` / ``sa`` would also match under
            # the parser's non-conflict matcher.
            if p.pos in ("DET", "ADP"):
                feats.setdefault("DEM", "NO")
            # Phase 5e Commit 3: ADV / PREP particles auto-carry
            # LEMMA so the grammar's `(↑) = ↓1` percolation in
            # `AdvP → ADV` and `PP → PREP NP[CASE=DAT]` exposes the
            # head's lemma at the AdvP / PP f-structure (mirroring
            # the noun pattern from Phase 5c §8 follow-on Commit 6).
            if p.pos in ("ADV", "PREP"):
                feats.setdefault("LEMMA", p.surface)
            self._index.particles.setdefault(p.surface.lower(), []).append(
                MorphAnalysis(
                    lemma=p.surface,
                    pos=p.pos,
                    feats=feats,
                )
            )
        for pn in self._data.pronouns:
            feats = dict(pn.feats)
            if pn.is_clitic:
                feats["is_clitic"] = True
            self._index.pronouns[pn.surface.lower()] = MorphAnalysis(
                lemma=pn.surface,
                pos="PRON",
                feats=feats,
            )
        for r in self._data.roots:
            if r.pos == "VERB":
                self._index_verb_paradigms(r)
            elif r.pos == "NOUN":
                # Phase 5c §8 follow-on (Commit 6): expose the noun
                # lemma + per-root feats on the MorphAnalysis. The
                # multi-OBL classifier consults LEMMA / SEM_CLASS to
                # disambiguate sa-NPs (palengke → OBL-LOC,
                # bata → OBL-BEN, etc.) when multiple OBL-θ roles
                # compete for multiple sa-NPs. Previously feats was
                # hardcoded empty.
                noun_feats: dict[str, object] = {**r.feats}
                noun_feats.setdefault("LEMMA", r.citation)
                self._index.nouns.setdefault(r.citation.lower(), []).append(
                    MorphAnalysis(
                        lemma=r.citation,
                        pos="NOUN",
                        feats=noun_feats,
                    ),
                )
            elif r.pos == "ADJ":
                # Phase 5h §4.2: dispatch on affix_class. Roots with a
                # non-empty list go through the productive paradigm
                # (``ma_adj`` family — Phase 5g + 5h Commits 1, 2);
                # roots with an empty list (``pareho``,
                # ``magkapareho``, ``magkaiba`` — non-productive
                # equative-identity predicates) get the bare citation
                # indexed directly. The two paths are kept separate
                # because the legacy ``_affix_class_match`` treats an
                # empty cell_class as a wildcard, which would otherwise
                # cause a bare-cell with ``affix_class: ""`` to fire on
                # every root including the productive ``ma_adj`` ones.
                if r.affix_class:
                    self._index_adjective_paradigms(r)
                else:
                    self._index_adjective_bare_root(r)

    def _index_adjective_bare_root(self, root: Root) -> None:
        """Index the bare citation as ADJ for non-productive roots.

        Phase 5h §4.2: ADJ entries declared with ``affix_class: []``
        (e.g., ``pareho`` "same/alike", ``magkapareho`` "alike",
        ``magkaiba`` "different") have no productive ``ma-`` /
        ``pinaka-`` / ``napaka-`` / ``kasing-`` / ``sing-`` derivation
        — the bare citation IS the adjectival surface. Lemma policy:
        ``LEMMA == root.citation``, surface == citation.lower(). The
        intrinsic ``PREDICATIVE: YES`` flag matches the productive
        cells so the same Phase 5g predicative-adj clause rule fires
        on these surfaces unchanged. Per-root ``feats`` (``EQUATIVE``,
        ``COMP_DEGREE``) ride into every generated MorphAnalysis via
        ``setdefault`` — same merge convention as
        :meth:`_index_adjective_paradigms`.
        """
        feats: dict[str, object] = {
            "PREDICATIVE": "YES",
            "LEMMA": root.citation,
        }
        for k, v in root.feats.items():
            feats.setdefault(k, v)
        self._index.adjectives.setdefault(root.citation.lower(), []).append(
            MorphAnalysis(
                lemma=root.citation,
                pos="ADJ",
                feats=feats,
            ),
        )

    def _index_adjective_paradigms(self, root: Root) -> None:
        """Index the surfaces produced by every matching adjective cell.

        Phase 5g §12.1: ADJ-pos roots productively derive surfaces via
        adjective-paradigm cells (the seed is ``ma-`` prefixation;
        Phase 5h adds ``pinaka-``, ``napaka-``, ``kasing-``, ``sing-``).
        Every derived surface carries the intrinsic ``PREDICATIVE: YES``
        feature, the analytical commitment that lets the predicative-adj
        clause rule fire on a feature rather than a POS.

        The bare-root surface (e.g., ``ganda`` for the root that
        produces ``maganda``) is intentionally NOT indexed as ADJ —
        bare roots are nouns ("beauty") in this analysis, and the
        paradigm-driven derivation is what produces the adjectival
        surface. Non-productive ADJ entries (``pareho``,
        ``magkapareho``, ``magkaiba``) take the
        :meth:`_index_adjective_bare_root` path instead and DO have
        their citation indexed.
        """
        for cell in self._data.adjective_cells:
            if not _affix_class_match(cell.affix_class, root.affix_class):
                continue
            surface = generate_form(root, cell).lower()
            # LEMMA mirrors the noun convention (lex token carries
            # ``LEMMA`` in feats so the grammar's
            # ``(↑ LEMMA) = ↓ LEMMA`` percolation surfaces the lex's
            # bare-root lemma in NP-modifier and predicative-adj
            # f-structures).
            feats: dict[str, object] = {
                "PREDICATIVE": "YES",
                "LEMMA": root.citation,
            }
            # Per-cell feats may extend / override the intrinsic
            # PREDICATIVE (e.g., a future non-predicative manner-only
            # cell could set PREDICATIVE: NO).
            for k, v in cell.feats.items():
                feats[k] = v
            # Per-root feats ride into every generated form (parallel
            # to verb roots' CTRL_CLASS / APPL / CAUS handling). For
            # ADJ this is where future SEM_CLASS values (SIZE / COLOUR
            # / EVALUATIVE / ...) will land.
            for k, v in root.feats.items():
                feats.setdefault(k, v)
            self._index.adjectives.setdefault(surface, []).append(
                MorphAnalysis(
                    lemma=root.citation,
                    pos="ADJ",
                    feats=feats,
                ),
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
            # Per-cell lex feats (Phase 4 §7.7): APPL and CAUS values
            # ride from the paradigm cell into the MorphAnalysis. Cell
            # feats win over root feats for the same key (the cell is
            # the more specific source — a single verb root can
            # generate forms across multiple applicative variants).
            for k, v in cell.feats.items():
                feats[k] = v
            # Per-root lex feats (Phase 4 §7.6): CTRL_CLASS et al.
            # ride into every generated form so the parser's
            # category-pattern matcher can discriminate control
            # verbs (V[CTRL_CLASS=INTRANS] vs V[CTRL_CLASS=TRANS])
            # at the rule level.
            for k, v in root.feats.items():
                feats.setdefault(k, v)
            # Default CTRL_CLASS=NONE on verbs not declared as a
            # control class. Without this, the grammar's
            # ``V[CTRL_CLASS=PSYCH]`` (etc.) patterns would fire on
            # ANY verb under the parser's non-conflict matcher
            # (shared keys must agree; missing keys don't conflict).
            # The sentinel value ensures non-control verbs are
            # ruled out at rule-match time.
            feats.setdefault("CTRL_CLASS", "NONE")
            # Same sentinel pattern for APPL / CAUS: non-applicative
            # / non-causative verbs need a NONE default so the
            # grammar's ``V[APPL=BEN]`` etc. don't fire on plain
            # verbs.
            feats.setdefault("APPL", "NONE")
            feats.setdefault("CAUS", "NONE")
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
