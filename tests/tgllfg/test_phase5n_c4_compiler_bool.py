"""Phase 5n.C.4 Commits 3 + 8 — compiler + equation parser accept bool literals.

The compiler accepts:

* ``PART[WH=true]`` / ``PART[WH=false]`` — Python bool literals on
  binary feats.
* ``PART[WH]`` — shorthand for ``PART[WH=true]``, permitted only on
  feats in ``BINARY_FEATS``.

Commit 8 removed the legacy ``YES`` / ``NO`` aliases:

* ``PART[WH=YES]`` — rejected (use ``[WH=true]`` or ``[WH]``).
* ``PART[WH=NO]`` — rejected (use ``[WH=false]``).

The equation parser accepts bare ``true`` / ``false`` keywords at
value position; quoted ``'YES'`` / ``'NO'`` atoms remain as string
atoms (used for enum YES tags on PRED / INDEF).

Non-binary feats reject bool syntax:

* ``PART[CASE]`` — shorthand error (CASE is enum NOM/GEN/DAT).
* ``PART[CASE=true]`` — bool literal error (semantic mismatch).
"""

from __future__ import annotations

import pytest

from tgllfg.cfg.compile import CategoryPattern, parse_pattern
from tgllfg.fstruct.equations import (
    Atom,
    ConstrainingEquation,
    DefiningEquation,
    parse_equation,
    unparse,
)


# === Pattern parsing: bool literals ======================================


@pytest.mark.parametrize("src,feat,value", [
    ("PART[WH=true]", "WH", True),
    ("PART[WH=false]", "WH", False),
    ("PART[WH]", "WH", True),
])
def test_binary_feat_bool_forms_canonicalize_to_bool(
    src: str, feat: str, value: bool
) -> None:
    p = parse_pattern(src)
    assert p.features == ((feat, value),)


def test_shorthand_and_explicit_true_yield_equal_patterns() -> None:
    """``PART[WH]`` and ``PART[WH=true]`` produce hash-equal patterns."""
    a = parse_pattern("PART[WH]")
    b = parse_pattern("PART[WH=true]")
    assert a == b


@pytest.mark.parametrize("src", [
    "PART[WH=YES]",
    "PART[WH=NO]",
])
def test_legacy_yes_no_aliases_rejected(src: str) -> None:
    """Commit 8 removed the ``YES`` / ``NO`` aliases — binary feats
    accept only ``true`` / ``false`` / shorthand."""
    with pytest.raises(ValueError, match="binary feats accept only"):
        parse_pattern(src)


# === Pattern parsing: enum feats stay string =============================


@pytest.mark.parametrize("src,feat,value", [
    ("NP[CASE=NOM]", "CASE", "NOM"),
    ("NP[CASE=GEN]", "CASE", "GEN"),
    ("V[VOICE=AV,ASPECT=PFV]", "VOICE", "AV"),
    # INDEF takes both YES (enum tag for generic indefinite) and
    # NEG_INDEF; the YES stays a literal string under the enum
    # exclusion since INDEF is not in BINARY_FEATS.
    ("PRON[INDEF=YES]", "INDEF", "YES"),
    ("PRON[INDEF=NEG_INDEF]", "INDEF", "NEG_INDEF"),
])
def test_enum_feats_preserve_string_value(src: str, feat: str, value: str) -> None:
    p = parse_pattern(src)
    assert (feat, value) in p.features


# === Pattern parsing: rejections =========================================


def test_shorthand_rejected_on_enum_feat() -> None:
    with pytest.raises(ValueError, match="shorthand"):
        parse_pattern("NP[CASE]")


def test_shorthand_rejected_on_unknown_feat() -> None:
    """A feat name not in BINARY_FEATS — including typos — fails
    shorthand parsing. Catches grammar bugs at compile time."""
    with pytest.raises(ValueError, match="shorthand"):
        parse_pattern("PART[NOT_A_REAL_FEAT]")


def test_bool_literal_rejected_on_enum_feat() -> None:
    with pytest.raises(ValueError, match="bool literal not allowed"):
        parse_pattern("NP[CASE=true]")


def test_bool_literal_rejected_on_unknown_feat() -> None:
    with pytest.raises(ValueError, match="bool literal not allowed"):
        parse_pattern("PART[NOT_A_REAL_FEAT=true]")


# === Pattern parsing: mixed binary + enum ================================


def test_mixed_bool_and_enum_in_one_pattern() -> None:
    """A common shape: ``PART[QUESTION=true, CLITIC_CLASS=2P]``."""
    p = parse_pattern("PART[QUESTION=true, CLITIC_CLASS=2P]")
    feats = dict(p.features)
    assert feats["QUESTION"] is True
    assert feats["CLITIC_CLASS"] == "2P"


def test_shorthand_works_alongside_explicit_pair() -> None:
    """``PART[QUESTION, CLITIC_CLASS=2P]`` — shorthand for one feat,
    explicit pair for another."""
    p = parse_pattern("PART[QUESTION, CLITIC_CLASS=2P]")
    feats = dict(p.features)
    assert feats["QUESTION"] is True
    assert feats["CLITIC_CLASS"] == "2P"


def test_post_c8_canonical_pattern() -> None:
    """Phase 5n.C.4 Commit 8 end-state: the binary feat must be
    written as ``[QUESTION]`` shorthand or ``[QUESTION=true]``;
    other forms are rejected."""
    p = parse_pattern("PART[CLITIC_CLASS=2P, QUESTION]")
    assert p == CategoryPattern(
        "PART",
        (("CLITIC_CLASS", "2P"), ("QUESTION", True)),
    )


# === Equation parsing: bool literals =====================================


def test_equation_defining_with_bool_true() -> None:
    eq = parse_equation("(↑ WH) = true")
    assert isinstance(eq, DefiningEquation)
    assert isinstance(eq.rhs, Atom)
    assert eq.rhs.value is True


def test_equation_defining_with_bool_false() -> None:
    eq = parse_equation("(↑ WH) = false")
    assert isinstance(eq, DefiningEquation)
    assert isinstance(eq.rhs, Atom)
    assert eq.rhs.value is False


def test_equation_constraining_with_bool_true() -> None:
    eq = parse_equation("(↓2 QUESTION) =c true")
    assert isinstance(eq, ConstrainingEquation)
    assert isinstance(eq.rhs, Atom)
    assert eq.rhs.value is True


def test_equation_legacy_quoted_yes_distinct_from_bool() -> None:
    """``=c 'YES'`` parses to a *string* Atom("YES") while
    ``=c true`` parses to a *bool* Atom(True). They are
    interchangeable at unification time via the
    :func:`fstruct.graph._atoms_compatible` aliasing, but the parsed
    AST values are distinct types."""
    str_atom = parse_equation("(↓2 QUESTION) =c 'YES'")
    bool_atom = parse_equation("(↓2 QUESTION) =c true")
    assert str_atom != bool_atom
    assert isinstance(str_atom, ConstrainingEquation)
    assert isinstance(bool_atom, ConstrainingEquation)
    assert isinstance(str_atom.rhs, Atom) and str_atom.rhs.value == "YES"
    assert isinstance(bool_atom.rhs, Atom) and bool_atom.rhs.value is True


def test_equation_unparse_renders_bool_keyword() -> None:
    """The unparser renders ``Atom(True)`` as the bare ``true`` keyword
    (not as ``'YES'``). Round-trips cleanly."""
    parsed = parse_equation("(↑ WH) = true")
    rendered = unparse(parsed)
    assert rendered == "(↑ WH) = true"
    reparsed = parse_equation(rendered)
    assert reparsed == parsed
