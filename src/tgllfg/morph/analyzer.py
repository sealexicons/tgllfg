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
    full_reduplicate,
    kani_reduplicate,
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
        base = _apply(op, base, flags, root.citation)
    if "d_to_r" in flags:
        base = d_to_r_intervocalic(base)
    return base


def _apply(
    op: Operation, base: str, flags: set[str], root_citation: str = ""
) -> str:
    if op.op == "cv_redup":
        return cv_reduplicate(base, cluster_redup="cluster_redup" in flags)
    if op.op == "full_redup":
        # Phase 5n.C.3 Commit 2 (§18 L31): whole-root reduplication
        # for compound cardinals (``libo`` → ``libulibo``). Distinct
        # from ``cv_redup`` (first-CV only) and from the
        # Phase 5n.C.3 Commit 6 ``redup_root`` op (which redups
        # AFTER prefix attachment, used by ADJ intensives).
        return full_reduplicate(base)
    if op.op == "kani_redup":
        # Phase 5n.C.3 Commit 5 (§18 L31): distributive-possessive
        # redup for 3rd-person DAT pronouns. ``kanya`` (2-syl) →
        # ``kanyakanya`` via full redup; ``kaniya`` / ``kanila``
        # (3-syl) → first copy truncated to 2 syllables +
        # full base (``kanikaniya`` / ``kanikanila``).
        return kani_reduplicate(base)
    if op.op == "redup_root":
        # Phase 5n.C.3 Commit 6 (§18 L31): post-prefix root
        # reduplication. Appends the original root citation to
        # the current base. ``ganda`` after ``ma-`` prefix
        # (giving ``maganda``) followed by ``redup_root`` yields
        # ``maganda`` + ``ganda`` = ``magandaganda`` — the L37
        # reduplicated-intensive surface (canonical orthography
        # ``maganda-ganda``; the hyphen-merge tokenizer pre-pass
        # collapses the hyphenated input to the single-token
        # form for lex lookup).
        #
        # Distinct from ``full_redup`` (Commit 2) which redups
        # the WHOLE current base — that op produces
        # ``magandaganda`` only if applied BEFORE the prefix
        # (the L37 pattern requires the order
        # ``prefix → redup_root`` so the prefix appears only
        # on the first copy).
        if not root_citation:
            raise ValueError(
                "redup_root op requires root_citation context "
                "(generate_form passes it; standalone callers "
                "must pass it explicitly)"
            )
        return base + root_citation
    if op.op == "infix":
        return infix_after_first_consonant(base, op.value)
    if op.op == "suffix":
        return attach_suffix(
            base,
            op.value,
            high_vowel_deletion="high_vowel_deletion" in flags,
            a_deletion="a_deletion" in flags,
            no_o_raise="no_o_raise" in flags,
            no_h_epenthesis="no_h_epenthesis" in flags,
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
                    "CARDINAL": True,
                    "CARDINAL_VALUE": n,
                    "DIGIT_FORM": True,
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
                feats.setdefault("DEM", False)
            # Phase 5e Commit 3: ADV / PREP particles auto-carry
            # LEMMA so the grammar's `(↑) = ↓1` percolation in
            # `AdvP → ADV` and `PP → PREP NP[CASE=DAT]` exposes the
            # head's lemma at the AdvP / PP f-structure (mirroring
            # the noun pattern from Phase 5c §8 follow-on Commit 6).
            #
            # Phase 5n.B Commit 1 (§18 L42 + L52) extends the auto-
            # LEMMA pattern to ``Q`` so the Phase 5n.B Commit 1
            # predicative-Q clause rule (S → Q[VAGUE=YES] NP[CASE=
            # NOM]) can lift ``Q_LEMMA`` from bare vague-Q heads
            # (``marami`` / ``konti`` / ``kakaunti`` / ``karamihan``)
            # that don't carry an explicit ``LEMMA`` feat in YAML.
            # Wh-Q lex entries (``magkano`` / ``alin`` / ``ilan``-wh)
            # already declare ``LEMMA`` explicitly per Phase 5j
            # Commit 7's orthographic-variant convention; the
            # ``setdefault`` is a no-op on those.
            if p.pos in ("ADV", "PREP", "Q"):
                feats.setdefault("LEMMA", p.surface)
            # Phase 5j Commit 7: orthographic-variant collapse.
            # When a particle entry's ``LEMMA`` feat differs from
            # its surface (e.g., ``surface: pwede``,
            # ``feats: {LEMMA: puwede}``), the LEMMA feat names the
            # canonical lemma and the analysis's ``lemma`` field
            # adopts it. Variants then route to the same
            # ``LexicalEntry`` in ``core/lexicon.py`` keyed by
            # canonical lemma — no entry duplication. For the
            # majority of entries where ``LEMMA == surface`` (or
            # no LEMMA feat is set), this is a no-op: the
            # canonical lemma equals the surface.
            canonical_lemma = feats.get("LEMMA", p.surface)
            if not isinstance(canonical_lemma, str):
                canonical_lemma = p.surface
            self._index.particles.setdefault(p.surface.lower(), []).append(
                MorphAnalysis(
                    lemma=canonical_lemma,
                    pos=p.pos,
                    feats=feats,
                )
            )
            # Phase 6.I Commit 2 (§18 L105): PART-base paradigm cells
            # fire on particles with non-empty affix_class. The
            # ``adv_redup`` cell (data/tgl/paradigms.yaml) derives
            # productive ``pa-X-X`` ADV-FREQUENCY surfaces from base
            # ADV roots like ``minsan`` (→ ``paminsanminsan`` with
            # canonical hyphenated LEMMA ``paminsan-minsan``).
            if p.affix_class:
                self._index_particle_paradigms(p)
        for pn in self._data.pronouns:
            feats = dict(pn.feats)
            if pn.is_clitic:
                feats["is_clitic"] = True
            # Phase 5n.A Commit 4 (§18 L74): orthographic-variant
            # collapse extended from the particles branch (Phase 5j
            # Commit 7) to pronouns. When a pronoun entry's ``LEMMA``
            # feat differs from its surface (e.g., ``surface: nya``,
            # ``feats: {LEMMA: niya}``), the LEMMA feat names the
            # canonical lemma and the analysis's ``lemma`` field
            # adopts it. Variants then route to the same canonical
            # lemma — no entry duplication. For the majority of
            # entries where ``LEMMA == surface`` (or no LEMMA feat is
            # set), this is a no-op.
            canonical_lemma = feats.get("LEMMA", pn.surface)
            if not isinstance(canonical_lemma, str):
                canonical_lemma = pn.surface
            self._index.pronouns[pn.surface.lower()] = MorphAnalysis(
                lemma=canonical_lemma,
                pos="PRON",
                feats=feats,
            )
            # Phase 5n.C.3 Commit 5 (§18 L31): PRON-base paradigm
            # cells fire on pronouns with non-empty affix_class.
            # The ``kani_redup`` cell (data/tgl/paradigms.yaml)
            # derives distributive-possessive Q surfaces from
            # 3rd-person DAT pronouns. Derived surfaces are indexed
            # into the particles table (since the cell flips
            # ``pos: Q``); the bare PRON entry continues to be
            # looked up via the pronouns table.
            if pn.affix_class:
                self._index_pronoun_paradigms(pn)
        for r in self._data.roots:
            if r.pos == "VERB":
                self._index_verb_paradigms(r)
                # Phase 9.X.pre-4.7: VERB→NOUN/ADJ POS-flip cells
                # (pag- gerund, ka- nominalization, pang- instrument,
                # etc.) fire here. The guard in
                # _index_paradigm_via_base_pos skips same-POS cells
                # (cell.pos == "") so this doesn't double-index the
                # standard verb-paradigm output already handled by
                # _index_verb_paradigms above.
                self._index_paradigm_via_base_pos(r)
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
                # Phase 5n.A Commit 4 (§18 L74): orthographic-variant
                # collapse extended from the particles branch. If the
                # NOUN root declares a ``LEMMA`` feat that differs
                # from its citation, the analysis's ``lemma`` field
                # adopts the canonical name (e.g., a future
                # ``citation: kwarto, feats: {LEMMA: kuwarto}`` entry
                # would yield analyses with lemma=kuwarto, routing
                # all spelling variants to one canonical entry).
                canonical_lemma = noun_feats.get("LEMMA", r.citation)
                if not isinstance(canonical_lemma, str):
                    canonical_lemma = r.citation
                noun_analysis = MorphAnalysis(
                    lemma=canonical_lemma,
                    pos="NOUN",
                    feats=noun_feats,
                )
                self._index.nouns.setdefault(r.citation.lower(), []).append(
                    noun_analysis,
                )
                # Phase 9.X.c31: also index under the hyphen-stripped
                # form. The tokenizer's ``-`` → empty normalization
                # (see text/tokenizer.py) means a citation like
                # ``mag-aaral`` is looked up as ``magaaral``; without
                # this dual-indexing the NOUN reading is unreachable
                # for hyphenated citations.
                citation_no_hyphen = r.citation.lower().replace("-", "")
                if citation_no_hyphen != r.citation.lower():
                    self._index.nouns.setdefault(
                        citation_no_hyphen, []
                    ).append(noun_analysis)
                # Phase 5n.C.3 Commit 1: NOUN-base paradigm cells
                # (``card_redup``, ``tig_distrib``, ``tag_season``,
                # ``kani-``) fire here. Cells live in
                # ``data/tgl/paradigms.yaml`` with ``base_pos: NOUN``.
                self._index_paradigm_via_base_pos(r)
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
                # Phase 5n.C.3 Commit 1: ADJ-base paradigm cells
                # (Phase 5n.C.3 L37 reduplicated intensives, L38
                # archaic ``kasing-`` reduplication) fire here too.
                # Cells live in ``data/tgl/paradigms.yaml`` with
                # ``base_pos: ADJ``; the operation-execution engine
                # is shared with verb / noun paradigms.
                self._index_paradigm_via_base_pos(r)
            elif r.pos == "NUM":
                # Phase 5n.C.3 Commit 3 (§18 L31): NUM-pos roots
                # (cardinal numerals 1-10 from
                # ``data/tgl/numerals.yaml``) only drive paradigm
                # cells — bare-NUM lookup continues to come from
                # the matching ``particles.yaml`` entries. The
                # ``tig_distrib`` cell with ``base_pos: NUM`` fires
                # here and produces ``tigisa`` / ``tigdalawa`` /
                # etc., indexed into the particles table.
                self._index_paradigm_via_base_pos(r)

    def _index_pronoun_paradigms(self, pn) -> None:  # type: ignore[no-untyped-def]
        """Phase 5n.C.3 Commit 5: iterate paradigm cells with
        ``base_pos: PRON`` against the pronoun, indexing derived
        surfaces. Surfaces are routed by ``cell.pos`` (default
        PRON): a Q-pos cell routes to the particles table (the
        ``kani_redup`` cell flips PRON → Q for the distributive-
        possessive quantifier output).
        """
        for cell in self._data.paradigm_cells:
            if cell.base_pos != "PRON":
                continue
            if not _affix_class_match(cell.affix_class, pn.affix_class):
                continue
            # Construct a synthetic Root from the Pronoun so
            # generate_form can apply the cell's operations.
            from .paradigms import Root as _Root
            synthetic = _Root(
                citation=pn.surface,
                pos="PRON",
                feats=dict(pn.feats),
                affix_class=list(pn.affix_class),
            )
            surface = generate_form(synthetic, cell).lower()
            feats: dict[str, object] = {**pn.feats}
            for k, v in cell.feats.items():
                feats[k] = v
            # LEMMA defaults to the source pronoun's surface (or its
            # canonical LEMMA feat per Phase 5n.A Commit 4
            # orthographic-variant convention).
            canonical_lemma = feats.get("LEMMA", pn.surface)
            if not isinstance(canonical_lemma, str):
                canonical_lemma = pn.surface
            out_pos = cell.pos or "PRON"
            analysis = MorphAnalysis(
                lemma=canonical_lemma,
                pos=out_pos,
                feats=feats,
            )
            if out_pos == "PRON":
                # Stay in pronouns table for PRON-typed derivations
                # (none in the current seed; reserved for future).
                self._index.pronouns[surface] = analysis
            else:
                # POS-flipped derivations (Q for kani_redup,
                # potentially others) land in particles where the
                # grammar looks up Q / DET / etc.
                self._index.particles.setdefault(surface, []).append(analysis)

    def _index_particle_paradigms(self, p) -> None:  # type: ignore[no-untyped-def]
        """Phase 6.I Commit 2 (§18 L105): iterate paradigm cells with
        ``base_pos`` matching the particle's ``pos`` (typically ADV),
        indexing derived surfaces. Mirrors
        :meth:`_index_pronoun_paradigms` for the PART namespace.

        LEMMA construction for cells whose final op is ``redup_root``
        inserts a hyphen between the pre-redup base and the redup'd
        copy (``paminsan`` + ``-`` + ``minsan`` = ``paminsan-minsan``)
        to preserve the canonical hyphenated form. Other cells fall
        through to the source particle's LEMMA / surface default.
        """
        for cell in self._data.paradigm_cells:
            if cell.base_pos != p.pos:
                continue
            if not _affix_class_match(cell.affix_class, p.affix_class):
                continue
            from .paradigms import Root as _Root
            synthetic = _Root(
                citation=p.surface,
                pos=p.pos,
                feats=dict(p.feats),
                affix_class=list(p.affix_class),
            )
            surface = generate_form(synthetic, cell).lower()
            feats: dict[str, object] = {**p.feats}
            for k, v in cell.feats.items():
                feats[k] = v
            # Canonical LEMMA for redup_root-final cells: the
            # pre-redup base hyphenated with the root citation
            # (``paminsan-minsan``). For other cells, fall through
            # to the source particle's LEMMA feat or surface.
            if cell.operations and cell.operations[-1].op == "redup_root":
                pre_redup_root = _Root(
                    citation=p.surface,
                    pos=p.pos,
                    feats=dict(p.feats),
                    affix_class=list(p.affix_class),
                )
                pre_redup_cell = type(cell)(  # shallow clone w/o last op
                    **{
                        **{
                            f.name: getattr(cell, f.name)
                            for f in cell.__dataclass_fields__.values()
                        },
                        "operations": list(cell.operations[:-1]),
                    }
                )
                pre_redup_base = generate_form(
                    pre_redup_root, pre_redup_cell
                )
                canonical_lemma = f"{pre_redup_base}-{p.surface}"
            else:
                canonical_lemma_obj = feats.get("LEMMA", p.surface)
                canonical_lemma = (
                    canonical_lemma_obj
                    if isinstance(canonical_lemma_obj, str)
                    else p.surface
                )
            # Stamp LEMMA into feats so downstream consumers see the
            # canonical form (mirrors the existing particle-loading
            # convention at the top of this method's caller).
            feats["LEMMA"] = canonical_lemma
            out_pos = cell.pos or p.pos
            analysis = MorphAnalysis(
                lemma=canonical_lemma,
                pos=out_pos,
                feats=feats,
            )
            self._index.particles.setdefault(surface, []).append(analysis)

    def _index_paradigm_via_base_pos(self, root: Root) -> None:
        """Index paradigm cells in ``paradigm_cells`` whose
        ``base_pos`` matches ``root.pos``. Phase 5n.C.3 Commit 1
        infrastructure for non-verbal derivations (NOUN-root
        ``card_redup`` / ``tig_distrib`` / ``tag_season`` / ``kani-``;
        ADJ-root ``redup_root`` intensives / ``kasing-`` redup).

        Routes generated surfaces to the POS-appropriate index
        (``nouns`` / ``adjectives``). If the cell declares ``pos:``,
        that overrides the base ``root.pos`` for both the
        MorphAnalysis ``pos`` field and the destination index —
        mirroring :meth:`_index_pronoun_paradigms`'s ``cell.pos``
        routing (Phase 5n.C.3 Commit 5). Phase 8.C uses this to
        route the new ``pinaka_adj_from_n`` cell (``base_pos: NOUN,
        pos: ADJ``) so ``pinakapuno`` lands in the adjectives index
        as well as the nouns one.

        Per-root + per-cell feats are merged with cell.feats winning
        over root.feats (mirrors the VERB / ADJ-paradigm convention);
        LEMMA defaults to ``root.citation`` if not explicitly set.
        """
        for cell in self._data.paradigm_cells:
            if cell.base_pos != root.pos:
                continue
            # Phase 9.X.pre-4.7: when called from the VERB-root
            # branch, skip same-POS (cell.pos == "") cells — those
            # are the standard verbal-paradigm cells already
            # processed by :meth:`_index_verb_paradigms`. Only
            # POS-flip cells (e.g., pag-gerund's `pos: NOUN`) fire
            # here. NOUN/ADJ/NUM root paths don't have a parallel
            # indexer, so this guard only triggers for VERB roots.
            if cell.base_pos == "VERB" and not cell.pos:
                continue
            if not _affix_class_match(cell.affix_class, root.affix_class):
                continue
            surface = generate_form(root, cell).lower()
            feats: dict[str, object] = {**root.feats}
            for k, v in cell.feats.items():
                feats[k] = v
            feats.setdefault("LEMMA", root.citation)
            canonical_lemma = feats.get("LEMMA", root.citation)
            if not isinstance(canonical_lemma, str):
                canonical_lemma = root.citation
            out_pos = cell.pos or root.pos
            analysis = MorphAnalysis(
                lemma=canonical_lemma,
                pos=out_pos,
                feats=feats,
            )
            if out_pos == "NOUN":
                self._index.nouns.setdefault(surface, []).append(analysis)
            elif out_pos == "ADJ":
                self._index.adjectives.setdefault(surface, []).append(analysis)
            elif out_pos == "NUM":
                # Phase 5n.C.3 Commit 3: derived NUM surfaces are
                # indexed into the particles table — this is where
                # ``analyze_one`` looks up NUM particles (cardinal
                # numerals are loaded from particles.yaml). Mirrors
                # the existing particles dispatch for bare-numeral
                # lookup; the derived analyses carry the same
                # pos="NUM" so grammar consumers see no distinction.
                self._index.particles.setdefault(surface, []).append(analysis)
            else:
                # PRON / other POS-bases would extend here; ignored
                # for now (no PRON-root paradigms in the seed).
                pass

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
        # Phase 5n.A Commit 4 (§18 L74): build feats so root.feats's
        # ``LEMMA`` (if any) wins over the citation default. Order:
        #   1. start from root.feats (may carry LEMMA + SEM_CLASS etc.)
        #   2. setdefault intrinsic ``PREDICATIVE: True`` (overridable
        #      by root.feats; future cell.feats override too).
        #   3. setdefault ``LEMMA: root.citation`` as fallback.
        feats: dict[str, object] = {**root.feats}
        feats.setdefault("PREDICATIVE", True)
        feats.setdefault("LEMMA", root.citation)
        canonical_lemma = feats.get("LEMMA", root.citation)
        if not isinstance(canonical_lemma, str):
            canonical_lemma = root.citation
        self._index.adjectives.setdefault(root.citation.lower(), []).append(
            MorphAnalysis(
                lemma=canonical_lemma,
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
            # Phase 5n.A Commit 4 (§18 L74): same merge order as
            # _index_adjective_bare_root + cell.feats override step.
            # Order:
            #   1. start from root.feats (may carry LEMMA / SEM_CLASS).
            #   2. apply cell.feats — per-cell overrides win
            #      (Phase 5g/5h precedent for COMP_DEGREE etc.).
            #   3. setdefault PREDICATIVE: YES (intrinsic fallback).
            #   4. setdefault LEMMA: root.citation (fallback).
            # The cell can override LEMMA in principle, though no
            # current cell does.
            feats: dict[str, object] = {**root.feats}
            for k, v in cell.feats.items():
                feats[k] = v
            feats.setdefault("PREDICATIVE", True)
            feats.setdefault("LEMMA", root.citation)
            canonical_lemma = feats.get("LEMMA", root.citation)
            if not isinstance(canonical_lemma, str):
                canonical_lemma = root.citation
            self._index.adjectives.setdefault(surface, []).append(
                MorphAnalysis(
                    lemma=canonical_lemma,
                    pos="ADJ",
                    feats=feats,
                ),
            )

    def _index_verb_paradigms(self, root: Root) -> None:
        for cell in self._data.paradigm_cells:
            # Phase 5n.C.3 Commit 1: filter to VERB-base cells only.
            # Non-verbal cells (base_pos: NOUN / ADJ / PRON) fire via
            # :meth:`_index_paradigm_via_base_pos` below.
            if cell.base_pos != "VERB":
                continue
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
            #
            # Phase 5n.A Commit 3 audit (§18 L91 closure): this
            # ``setdefault`` loop projects the root's ``feats:`` block
            # uniformly across every paradigm cell that fires for the
            # root's affix_class. There is no per-cell or per-affix-
            # class filtering — if a cell didn't already set the key
            # via the cell.feats loop above, the root value lands.
            # Tests in test_phase5n_paradigm_feats_projection.py pin
            # the uniform behaviour against future regressions
            # (SAY_CLASS=YES on every sabi cell; ASK_CLASS=YES on
            # every tanong cell; CTRL_CLASS uniform on payag /
            # pilit / utos).
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
            # Phase 5n.A Commit 4 (§18 L74): orthographic-variant
            # collapse for paradigm-derived VERB surfaces. If the
            # root declares a ``LEMMA`` feat that differs from its
            # citation, the analysis's ``lemma`` field adopts the
            # canonical name on every inflected cell — so a future
            # alt-spelling root (e.g.,
            # ``citation: kwento, feats: {LEMMA: kuwento}``) routes
            # all of its mag-/in-/an-/i-/maka-derived surfaces back
            # to one canonical lemma.
            canonical_lemma = feats.get("LEMMA", root.citation)
            if not isinstance(canonical_lemma, str):
                canonical_lemma = root.citation
            analysis = MorphAnalysis(
                lemma=canonical_lemma,
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
