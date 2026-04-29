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

from __future__ import annotations

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
    """
    op: str
    value: str = ""


@dataclass
class ParadigmCell:
    """One cell of a verbal paradigm."""
    voice: str              # AV / OV / DV / IV
    aspect: str             # PFV / IPFV / CTPL
    mood: str = "IND"
    transitivity: str = ""  # filter: cell only fires for roots with this transitivity
    affix_class: str = ""   # filter: cell only fires for roots whose affix_class
                            # list contains this string. Empty means "applies to
                            # roots whose affix_class is also empty" (legacy default).
    operations: list[Operation] = field(default_factory=list)
    notes: str = ""


@dataclass
class Particle:
    """A function word: determiner, adposition, polarity marker, linker, etc."""
    surface: str
    pos: str                # "DET", "ADP", "PART"
    feats: dict[str, object] = field(default_factory=dict)
    is_clitic: bool = False
    clitic_class: str = ""


@dataclass
class Pronoun:
    """A pronominal form."""
    surface: str
    feats: dict[str, object] = field(default_factory=dict)
    # PERS in {1,2,3}; NUM in {SG,PL}; CASE in {NOM,GEN,DAT};
    # CLUSV in {INCL,EXCL} when applicable; HUMAN True for proper-noun-like.
    is_clitic: bool = False


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
    paradigm_cells: list[ParadigmCell] = field(default_factory=list)
    particles: list[Particle] = field(default_factory=list)
    pronouns: list[Pronoun] = field(default_factory=list)
    sandhi_rules: list[SandhiRule] = field(default_factory=list)


__all__ = [
    "MorphData",
    "Operation",
    "ParadigmCell",
    "Particle",
    "Pronoun",
    "Root",
    "SandhiRule",
]
