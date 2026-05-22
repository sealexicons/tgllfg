# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/morph/paradigms.py

"""Data classes for the morphological lexicon.

These mirror the layout of the YAML seed under ``data/tgl/`` and are
the in-memory shape the analyzer consumes. Concrete instances are
produced by :mod:`tgllfg.morph.loader`.

The verb paradigm is described as an ordered list of *operations* per
cell. Operations are interpreted by the analyzer in a fixed order
(reduplication → infixation → suffixation → prefixation); see
:func:`tgllfg.morph.analyzer.generate_form` for the full schedule.
"""

from dataclasses import dataclass, field


@dataclass
class Root:
    """A lexical root."""
    citation: str           # e.g. "kain", "bili", "aso"
    pos: str                # "VERB", "NOUN", "ADJ"
    gloss: str = ""
    transitivity: str = ""  # "TR" or "INTR" for verbs; empty otherwise
    # Affix classes the root participates in. Generation only fires
    # for paradigm cells whose `affix_class` is in this list. For
    # backward compatibility, an empty list (or a root without this
    # field) is treated as participating in any cell whose
    # `affix_class` is also empty.
    affix_class: list[str] = field(default_factory=list)
    # Per-root opt-in phonological rules. Recognised flags
    # (Phase 2C):
    #   "d_to_r"               — /d/ → /r/ intervocalic post-processor
    #                            (e.g. dating, lakad).
    #   "high_vowel_deletion"  — colloquial high-vowel deletion variant
    #                            of suffix attachment (bili + -in →
    #                            bilhin instead of bilihin).
    sandhi_flags: list[str] = field(default_factory=list)
    # Per-root lex features that the analyzer copies into every
    # generated MorphAnalysis. Phase 4 §7.6 introduces ``CTRL_CLASS``
    # (PSYCH / INTRANS / TRANS) to discriminate control-verb classes
    # at the parser's category-pattern level. String-valued entries
    # become grammar-visible category features; bool/non-str values
    # ride through f-equations only.
    feats: dict[str, object] = field(default_factory=dict)
    # Synonyms — other lex citations that share the gloss. Phase 5f
    # Commit 4 introduces this field to record native / Spanish-
    # borrowed pairs (``aklat`` / ``libro``, ``kape`` / ``kapeng``)
    # and dialect / register variants. The parser does not currently
    # use this data; it's here for downstream tools (dictionary
    # export, cross-reference, future ranker semantic similarity).
    synonyms: list[str] = field(default_factory=list)
    # Phase 9.C.pre — structured metadata extracted from gloss
    # parentheticals.
    #
    # ``subclass`` is a list of orthogonal-axis tags drawn from a
    # closed enum (validated at load time). Two axes are recognised:
    #
    # * Named-entity (one of): PERSON / SURNAME / PLACE / LANGUAGE
    #   / NATIONAL — applies to proper / place / language /
    #   nationality nouns.
    # * Gender (optional): MALE / FEMALE — used when morphology
    #   actually distinguishes (Spanish-loan ``-o``/``-a`` pairs).
    #
    # Pure metadata — not currently surfaced in f-structure feats.
    # A future sub-PR can promote specific atoms to feats if a
    # grammar rule needs to gate on them.
    subclass: list[str] = field(default_factory=list)
    # ``source`` is a short-code citation of the lex entry's
    # provenance (strict enum). See ``_SOURCE_ALLOWED`` in
    # ``morph/loader.py``.
    source: str = ""
    # ``loan`` records the source language for loanwords (closed
    # enum: SPANISH / ENGLISH). Empty = native Tagalog.
    loan: str = ""
    # NB: ``orth_variants`` was removed in Phase 9.X.pre-1.21 — it
    # was loader-validated but never consulted by the analyzer.
    # The canonical mechanism for orthographic variants is a
    # separate root entry with the variant as ``citation`` and
    # ``feats: {LEMMA: <canonical>}`` (e.g. ``tiya`` → ``tita``,
    # ``mr`` → ``mister``). The analyzer honors LEMMA at match time.


@dataclass
class Operation:
    """A single morphological operation applied during paradigm generation.

    Operations are applied to the root in YAML-declared order — the
    engine does not reorder them.

    ``op`` is one of:

    * ``cv_redup``         — prepend the first CV of the current base.
    * ``infix``            — insert ``value`` after the first consonant
                             (or as a prefix when the base is
                             vowel-initial).
    * ``suffix``           — append ``value`` (with vowel-hiatus
                             ``-h-`` epenthesis).
    * ``prefix``           — prepend ``value``.
    * ``nasal_substitute`` — replace the base's first consonant with
                             the homorganic nasal of an ng-final
                             prefix (``mang``/``nang``/``pang``):
                             b/p → m, t/d/s → n, k/g → ng. The
                             prefix head (``na-``/``ma-``/``pa-``)
                             is supplied by a subsequent ``prefix``
                             op.
    * ``nasal_assim_prefix`` — prepend ``value`` (an ng-final
                             prefix like ``"pang"``), place-
                             assimilating its final nasal to the
                             base's first consonant **without**
                             dropping that consonant. Used by the
                             instrumental applicative ``ipang-``
                             (Phase 5c §7.7 follow-on): ``pang`` +
                             ``bili`` → ``pambili`` (later →
                             ``ipinambili``). Distinguished from
                             ``nasal_substitute`` (drop pattern),
                             which the AV distributive ``mang-``
                             still uses on the same root with a
                             different meaning (``mamili`` "be a
                             buyer / shop").
    """
    op: str
    value: str = ""


@dataclass
class ParadigmCell:
    """Common base for paradigm cells.

    Shared attributes for both verbal-paradigm cells (voice / aspect
    / mood / transitivity-bearing — :class:`VerbalCell`) and
    adjective-derivation cells (Phase 5g — :class:`AdjectiveCell`).
    The analyzer's :func:`tgllfg.morph.analyzer.generate_form` takes
    the base class so the operation-application engine is shared.

    The five shared fields are:

    * ``base_pos`` — filter: cell only fires for roots whose
      ``pos`` matches. Defaults to ``"VERB"`` for backward
      compatibility with the original AV/OV/DV/IV paradigm
      cells. Phase 5n.C.3 Commit 1 introduces this discriminator
      so ``NOUN`` and ``ADJ`` roots can drive non-verbal
      derivations (e.g., ``card_redup`` numeral reduplication,
      ``redup_root`` ADJ intensives) through the same
      :func:`tgllfg.morph.analyzer.generate_form` engine.
    * ``affix_class`` — filter: cell only fires for roots whose
      ``affix_class`` list contains this string. Empty means
      "applies to roots whose affix_class is also empty" (legacy
      default for the original AV/OV/DV/IV-um/in/an/i paradigms).
    * ``operations`` — ordered list of :class:`Operation` applied
      to the root in YAML-declared order; the analyzer doesn't
      reorder them.
    * ``notes`` — optional free-text rationale / citation; not
      consumed by the engine.
    * ``feats`` — per-cell lex features merged into every generated
      MorphAnalysis; string-valued entries become grammar-visible
      category features. Phase 4 §7.7 introduced ``APPL`` and
      ``CAUS``; subclasses contribute their own per-cell feature
      conventions.
    """
    base_pos: str = "VERB"
    affix_class: str = ""
    operations: list[Operation] = field(default_factory=list)
    notes: str = ""
    feats: dict[str, object] = field(default_factory=dict)
    # Phase 5n.C.3 Commit 5: optional pos override for the derived
    # MorphAnalysis. Empty string (default) means "use the source's
    # pos" (root.pos for Root-based cells, "PRON" for Pronoun-based
    # cells). Non-empty overrides — the productive ``kani_redup``
    # paradigm derives Q-pos surfaces (distributive-possessive
    # quantifiers) from PRON bases, so its cell sets ``pos: Q``.
    pos: str = ""


@dataclass
class VerbalCell(ParadigmCell):
    """One cell of a verbal paradigm.

    Adds voice / aspect / mood / transitivity to the
    :class:`ParadigmCell` base. Voice and aspect are required at the
    YAML loader level (:func:`tgllfg.morph.loader._load_paradigm_cells`
    calls ``_require``); the dataclass defaults are empty strings to
    comply with dataclass-inheritance ordering (non-default fields
    can't follow default ones).
    """
    voice: str = ""              # AV / OV / DV / IV
    aspect: str = ""             # PFV / IPFV / CTPL / RECPFV
    mood: str = "IND"
    transitivity: str = ""       # TR / INTR — filter: cell only
                                 # fires for roots with this
                                 # transitivity, when non-empty.


@dataclass
class AdjectiveCell(ParadigmCell):
    """One cell of the adjectival derivation paradigm.

    Phase 5g §12.1 analytical commitment: ``ma-`` adjectives are
    ``POS=ADJ`` with intrinsic ``[PREDICATIVE+]``, NOT stative VERBs.
    Adjectives are not voice / aspect / mood-marked, so this subclass
    adds no attributes beyond the :class:`ParadigmCell` base — the
    seed ``ma-`` cell is fully expressible with ``affix_class``,
    ``operations``, and (optionally) ``feats``. Phase 5h is expected
    to add ``pinaka-`` superlative, ``napaka-`` intensifier, and
    ``kasing-`` / ``sing-`` equative cells using this same subclass
    (and may add Phase 5h-specific fields here if a derivation needs
    them).
    """
    pass


@dataclass
class Particle:
    """A function word: determiner, adposition, polarity marker, linker, etc."""
    surface: str
    pos: str                # "DET", "ADP", "PART"
    feats: dict[str, object] = field(default_factory=dict)
    is_clitic: bool = False
    clitic_class: str = ""
    # Phase 6.I Commit 2 (§18 L105): affix_class drives the
    # particle-base paradigm engine. Empty list (default) means no
    # paradigm cells fire on this particle. Non-empty entries match
    # paradigm cells in ``paradigm_cells`` whose ``base_pos`` matches
    # this particle's ``pos`` and whose ``affix_class`` is in this
    # list — e.g., ``[adv_redup]`` on the ``minsan`` ADV entry
    # produces the productive ``paminsan-minsan`` OCCASIONAL form.
    affix_class: list[str] = field(default_factory=list)


@dataclass
class Pronoun:
    """A pronominal form."""
    surface: str
    feats: dict[str, object] = field(default_factory=dict)
    # PERS in {1,2,3}; NUM in {SG,PL}; CASE in {NOM,GEN,DAT};
    # CLUSV in {INCL,EXCL} when applicable; HUMAN True for proper-noun-like.
    is_clitic: bool = False
    # Phase 5n.C.3 Commit 5 (§18 L31): affix_class drives the
    # PRON-base paradigm engine. Empty list (default) means no
    # paradigm cells fire on this pronoun. Non-empty entries match
    # paradigm cells in ``paradigm_cells`` with ``base_pos: PRON``
    # whose ``affix_class`` is in this list — e.g.,
    # ``[kani_redup]`` for 3rd-person DAT pronouns produces the
    # distributive-possessive Q forms.
    affix_class: list[str] = field(default_factory=list)


@dataclass
class SandhiRule:
    """A phonological rewrite, applied during suffix attachment.

    Patterns and replacements use plain strings; ``context`` is a
    short DSL string (currently only ``"vowel-hiatus"`` is recognised
    by the engine — additional contexts can be added without changing
    the data shape).
    """
    description: str
    pattern: str = ""
    replacement: str = ""
    context: str = ""


@dataclass
class MorphData:
    """The fully-loaded morphological lexicon, ready to drive analysis."""
    roots: list[Root] = field(default_factory=list)
    paradigm_cells: list[VerbalCell] = field(default_factory=list)
    adjective_cells: list[AdjectiveCell] = field(default_factory=list)
    particles: list[Particle] = field(default_factory=list)
    pronouns: list[Pronoun] = field(default_factory=list)
    sandhi_rules: list[SandhiRule] = field(default_factory=list)


__all__ = [
    "AdjectiveCell",
    "MorphData",
    "Operation",
    "ParadigmCell",
    "Particle",
    "Pronoun",
    "Root",
    "SandhiRule",
    "VerbalCell",
]
