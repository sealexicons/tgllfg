"""Phase 5n.C.4 Commit 3 — compiler + equation parser accept bool literals.

The compiler gains:

* ``PART[WH=true]`` / ``PART[WH=false]`` — bool literals on binary feats.
* ``PART[WH]`` — shorthand for ``PART[WH=true]``, permitted only on
  feats in ``BINARY_FEATS``.
* ``PART[X=YES]`` / ``PART[X=NO]`` — legacy syntax preserved as aliases
  during the migration window.

The equation parser gains bare ``true`` / ``false`` keywords at value
position. All four shapes (``=true``, ``=YES``, ``[X]``, ``= 'YES'``)
canonicalize to the same internal representation (string ``"YES"`` /
``"NO"``) for C3 — Commit 4 will flip the internal rep to Python
``bool``.

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
    ("PART[WH=true]", "WH", "YES"),
    ("PART[WH=false]", "WH", "NO"),
    ("PART[WH=YES]", "WH", "YES"),
    ("PART[WH=NO]", "WH", "NO"),
    ("PART[WH]", "WH", "YES"),
])
def test_binary_feat_bool_forms_canonicalize_to_yes_no(
    src: str, feat: str, value: str
) -> None:
    p = parse_pattern(src)
    assert p.features == ((feat, value),)


def test_shorthand_and_explicit_yes_yield_equal_patterns() -> None:
    """``PART[WH]`` and ``PART[WH=YES]`` produce hash-equal patterns —
    the shorthand decodes to the same internal representation."""
    a = parse_pattern("PART[WH]")
    b = parse_pattern("PART[WH=YES]")
    assert a == b


def test_bool_literal_and_legacy_alias_yield_equal_patterns() -> None:
    """``PART[WH=true]`` and ``PART[WH=YES]`` are interchangeable in
    C3 — both produce the legacy string sentinel internally."""
    a = parse_pattern("PART[WH=true]")
    b = parse_pattern("PART[WH=YES]")
    assert a == b
    a = parse_pattern("PART[WH=false]")
    b = parse_pattern("PART[WH=NO]")
    assert a == b


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
    assert feats["QUESTION"] == "YES"
    assert feats["CLITIC_CLASS"] == "2P"


def test_shorthand_works_alongside_explicit_pair() -> None:
    """``PART[QUESTION, CLITIC_CLASS=2P]`` — shorthand for one feat,
    explicit pair for another."""
    p = parse_pattern("PART[QUESTION, CLITIC_CLASS=2P]")
    feats = dict(p.features)
    assert feats["QUESTION"] == "YES"
    assert feats["CLITIC_CLASS"] == "2P"


def test_existing_legacy_patterns_unaffected() -> None:
    """Regression: every shape that worked before C3 keeps working."""
    p = parse_pattern("PART[CLITIC_CLASS=2P, QUESTION=YES]")
    assert p == CategoryPattern(
        "PART",
        (("CLITIC_CLASS", "2P"), ("QUESTION", "YES")),
    )


# === Equation parsing: bool literals =====================================


def test_equation_defining_with_bool_true() -> None:
    eq = parse_equation("(↑ WH) = true")
    assert isinstance(eq, DefiningEquation)
    assert isinstance(eq.rhs, Atom)
    assert eq.rhs.value == "YES"


def test_equation_defining_with_bool_false() -> None:
    eq = parse_equation("(↑ WH) = false")
    assert isinstance(eq, DefiningEquation)
    assert isinstance(eq.rhs, Atom)
    assert eq.rhs.value == "NO"


def test_equation_constraining_with_bool_true() -> None:
    eq = parse_equation("(↓2 QUESTION) =c true")
    assert isinstance(eq, ConstrainingEquation)
    assert isinstance(eq.rhs, Atom)
    assert eq.rhs.value == "YES"


def test_equation_legacy_quoted_yes_atom_unchanged() -> None:
    """``=c 'YES'`` continues to parse to the same Atom("YES") that
    ``=c true`` produces — they're interchangeable in C3."""
    a = parse_equation("(↓2 QUESTION) =c 'YES'")
    b = parse_equation("(↓2 QUESTION) =c true")
    assert a == b


def test_equation_unparse_renders_atom_form() -> None:
    """The unparser renders Atom("YES") as ``'YES'`` (single-quoted),
    not as ``true``. That's fine for C3 — round-trip integrity is
    preserved, and Commit 5 will switch rule strings to ``true`` /
    ``false`` directly."""
    parsed = parse_equation("(↑ WH) = true")
    rendered = unparse(parsed)
    assert rendered == "(↑ WH) = 'YES'"
    reparsed = parse_equation(rendered)
    assert reparsed == parsed
