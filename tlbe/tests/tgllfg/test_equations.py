# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

import pytest

from tgllfg.fstruct import (
    AltFeature,
    Atom,
    ConstrainingEquation,
    DefiningEquation,
    Designator,
    Down,
    ExistentialConstraint,
    Feature,
    InsideOut,
    NegEquation,
    NegExistentialConstraint,
    ParseError,
    PlusAltFeature,
    PlusFeature,
    Right,
    SetMembership,
    StarAltFeature,
    StarFeature,
    Up,
    parse_equation,
    unparse,
)


# === Defining equations ====================================================

def test_atom_assignment():
    eq = parse_equation("(↑ PRED) = 'EAT'")
    assert eq == DefiningEquation(
        lhs=Designator(Up(), (Feature("PRED"),)),
        rhs=Atom("EAT"),
    )


def test_atom_with_special_chars():
    # The PRED template embeds spaces, angle brackets, commas.
    eq = parse_equation("(↑ PRED) = 'EAT <SUBJ, OBJ>'")
    assert isinstance(eq, DefiningEquation)
    assert eq.rhs == Atom("EAT <SUBJ, OBJ>")


def test_path_rhs():
    eq = parse_equation("(↑ VOICE) = ↓1 VOICE")
    assert eq == DefiningEquation(
        lhs=Designator(Up(), (Feature("VOICE"),)),
        rhs=Designator(Down(idx=1), (Feature("VOICE"),)),
    )


def test_bare_down_rhs():
    eq = parse_equation("(↑ SUBJ) = ↓3")
    assert eq == DefiningEquation(
        lhs=Designator(Up(), (Feature("SUBJ"),)),
        rhs=Designator(Down(idx=3), ()),
    )


def test_up_equals_down():
    eq = parse_equation("(↑) = ↓1")
    assert eq == DefiningEquation(
        lhs=Designator(Up(), ()),
        rhs=Designator(Down(idx=1), ()),
    )


def test_no_whitespace_around_eq():
    eq = parse_equation("(↑ CASE)='NOM'")
    assert eq == DefiningEquation(
        lhs=Designator(Up(), (Feature("CASE"),)),
        rhs=Atom("NOM"),
    )


def test_extra_whitespace():
    eq = parse_equation("  (↑   PRED)\t=\t↓1   PRED  ")
    assert eq == DefiningEquation(
        lhs=Designator(Up(), (Feature("PRED"),)),
        rhs=Designator(Down(idx=1), (Feature("PRED"),)),
    )


def test_hyphenated_feature_name():
    # OBL-AG, LEX-ASTRUCT — current grammar uses these.
    eq = parse_equation("(↑ OBL-AG) = ↓2")
    assert isinstance(eq, DefiningEquation)
    assert eq.lhs.path == (Feature("OBL-AG"),)


def test_multi_step_lhs_path():
    # (↑ F G) = v: representable, even though §4.1 unifier won't evaluate it.
    eq = parse_equation("(↑ F G) = 'X'")
    assert isinstance(eq, DefiningEquation)
    assert eq.lhs.path == (Feature("F"), Feature("G"))


# === Constraining, existential, negative, set membership ===================

def test_constraining():
    eq = parse_equation("(↑ CASE) =c 'NOM'")
    assert eq == ConstrainingEquation(
        lhs=Designator(Up(), (Feature("CASE"),)),
        rhs=Atom("NOM"),
    )


def test_existential_paren():
    eq = parse_equation("(↑ TOPIC)")
    assert eq == ExistentialConstraint(Designator(Up(), (Feature("TOPIC"),)))


def test_existential_no_paren():
    # Bare ↑ F is also accepted as an existential; same AST.
    eq = parse_equation("↑ TOPIC")
    assert eq == ExistentialConstraint(Designator(Up(), (Feature("TOPIC"),)))


def test_neg_existential():
    eq = parse_equation("¬ (↑ NEG)")
    assert eq == NegExistentialConstraint(Designator(Up(), (Feature("NEG"),)))


def test_neg_existential_no_space():
    eq = parse_equation("¬(↑ NEG)")
    assert eq == NegExistentialConstraint(Designator(Up(), (Feature("NEG"),)))


def test_neg_equation():
    eq = parse_equation("(↑ FOCUS) ≠ 'WH'")
    assert eq == NegEquation(
        lhs=Designator(Up(), (Feature("FOCUS"),)),
        rhs=Atom("WH"),
    )


def test_set_member_bare_down():
    eq = parse_equation("↓ ∈ (↑ ADJ)")
    assert eq == SetMembership(
        element=Designator(Down(idx=None), ()),
        container=Designator(Up(), (Feature("ADJ"),)),
    )


# === Functional uncertainty (regular paths) ================================

def test_functional_uncertainty_star():
    # The canonical example from the plan.
    eq = parse_equation("(↑ TOPIC) = (↑ COMP* GF)")
    assert eq == DefiningEquation(
        lhs=Designator(Up(), (Feature("TOPIC"),)),
        rhs=Designator(Up(), (StarFeature("COMP"), Feature("GF"))),
    )


def test_plus_feature():
    eq = parse_equation("(↑) = (↑ XCOMP+)")
    assert isinstance(eq, DefiningEquation)
    assert eq.rhs == Designator(Up(), (PlusFeature("XCOMP"),))


def test_alt_feature():
    eq = parse_equation("(↑) = (↑ {SUBJ | OBJ})")
    assert isinstance(eq, DefiningEquation)
    assert eq.rhs == Designator(Up(), (AltFeature(("SUBJ", "OBJ")),))


def test_alt_feature_three_way():
    eq = parse_equation("(↑) = (↑ {SUBJ | OBJ | OBL})")
    assert isinstance(eq, DefiningEquation)
    assert eq.rhs == Designator(Up(), (AltFeature(("SUBJ", "OBJ", "OBL")),))


# === Phase 10.L: Kleene over alternation ===================================
#
# ``{F | G}*`` / ``{F | G}+`` — K&Z 1989 eq. 38 / 39 canonical body form.
# Symmetric to the ``F*`` / ``F+`` single-name Kleene; the body iterates
# over any of the alternative names rather than a single label.

def test_star_alt_feature_two_way():
    eq = parse_equation("(↑ TOPIC) = (↑ {COMP | XCOMP}* SUBJ)")
    assert isinstance(eq, DefiningEquation)
    assert eq.rhs == Designator(
        Up(), (StarAltFeature(("COMP", "XCOMP")), Feature("SUBJ"))
    )


def test_star_alt_feature_three_way():
    eq = parse_equation("(↑) = (↑ {COMP | XCOMP | ADJ}*)")
    assert isinstance(eq, DefiningEquation)
    assert eq.rhs == Designator(
        Up(), (StarAltFeature(("COMP", "XCOMP", "ADJ")),)
    )


def test_plus_alt_feature_two_way():
    eq = parse_equation("(↑ REL-PRO) =c (↑ {COMP | XCOMP}+ SUBJ)")
    assert isinstance(eq, ConstrainingEquation)
    assert eq.rhs == Designator(
        Up(), (PlusAltFeature(("COMP", "XCOMP")), Feature("SUBJ"))
    )


def test_star_alt_concat_with_literal():
    # Mixed path: literal step, then Kleene-on-alternation, then literal.
    eq = parse_equation("(↑ COMP {XCOMP | OBJ}* SUBJ)")
    assert isinstance(eq, ExistentialConstraint)
    path = eq.designator.path
    assert path == (
        Feature("COMP"),
        StarAltFeature(("XCOMP", "OBJ")),
        Feature("SUBJ"),
    )


# === Off-path constraints ==================================================

def test_off_path_simple():
    # (→ TENSE) =c 'PAST' attached to a starred feature.
    eq = parse_equation("(↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)")
    assert isinstance(eq, ExistentialConstraint)
    elements = eq.designator.path
    assert len(elements) == 2
    star = elements[0]
    assert isinstance(star, StarFeature)
    assert star.name == "XCOMP"
    assert star.off_path == (
        ConstrainingEquation(
            lhs=Designator(Right(), (Feature("TENSE"),)),
            rhs=Atom("PAST"),
        ),
    )
    assert elements[1] == Feature("SUBJ")


def test_off_path_multiple_constraints():
    eq = parse_equation(
        "(↑ COMP*<(→ FIN) =c '+', (→ TENSE) =c 'PAST'>)"
    )
    assert isinstance(eq, ExistentialConstraint)
    star = eq.designator.path[0]
    assert isinstance(star, StarFeature)
    assert len(star.off_path) == 2


def test_off_path_on_simple_feature():
    eq = parse_equation("(↑ COMP<(→ FIN) =c '+'>)")
    assert isinstance(eq, ExistentialConstraint)
    feat = eq.designator.path[0]
    assert isinstance(feat, Feature)
    assert feat.off_path != ()


def test_off_path_on_star_alt_feature():
    # Phase 10.L: off-path constraints on a Kleene-over-alternation
    # body attach to the wrapper, applied uniformly to every labeled
    # transition emitted by the FSA compile.
    eq = parse_equation(
        "(↑ {COMP | XCOMP}*<(→ TENSE) =c 'PAST'> SUBJ)"
    )
    assert isinstance(eq, ExistentialConstraint)
    star_alt = eq.designator.path[0]
    assert isinstance(star_alt, StarAltFeature)
    assert star_alt.names == ("COMP", "XCOMP")
    assert star_alt.off_path == (
        ConstrainingEquation(
            lhs=Designator(Right(), (Feature("TENSE"),)),
            rhs=Atom("PAST"),
        ),
    )


def test_off_path_on_plus_alt_feature():
    eq = parse_equation(
        "(↑ {COMP | XCOMP}+<(→ FIN) =c '+'>)"
    )
    assert isinstance(eq, ExistentialConstraint)
    plus_alt = eq.designator.path[0]
    assert isinstance(plus_alt, PlusAltFeature)
    assert len(plus_alt.off_path) == 1


# === Phase 10.N: inside-out designators ====================================
#
# Dalrymple 2001 ch. 14 / 15 inside-out path designators. The surface form
# ``(FEAT INNER_DESIGNATOR)`` means "find the f-structure F such that
# F[FEAT] = INNER" — the resolver traverses upward in the f-graph via
# the new ``FGraph.parents_via`` reverse-lookup.

def test_inside_out_bare():
    """Bare ``(SUBJ ↑)`` — top-level inside-out designator with no
    outside-in path. Inner designator is the ↑ metavariable."""
    eq = parse_equation("(SUBJ ↑) = 'X'")
    assert isinstance(eq, DefiningEquation)
    assert eq.lhs == Designator(
        InsideOut(feat="SUBJ", inner=Designator(Up(), ())),
        (),
    )


def test_inside_out_with_outside_in_path():
    """``((SUBJ ↑) GF)`` — inside-out base, then outside-in step."""
    eq = parse_equation("((SUBJ ↑) GF) = 'X'")
    assert isinstance(eq, DefiningEquation)
    assert eq.lhs == Designator(
        InsideOut(feat="SUBJ", inner=Designator(Up(), ())),
        (Feature("GF"),),
    )


def test_inside_out_with_multi_step_outside_in_path():
    """Inside-out followed by 3-step outside-in path —
    ``((SUBJ ↑) F G H)``."""
    eq = parse_equation("((SUBJ ↑) F G H)")
    assert isinstance(eq, ExistentialConstraint)
    assert eq.designator == Designator(
        InsideOut(feat="SUBJ", inner=Designator(Up(), ())),
        (Feature("F"), Feature("G"), Feature("H")),
    )


def test_inside_out_inner_has_outside_in_path():
    """``(SUBJ (↑ COMP))`` — inside-out where inner has outside-in
    path. Resolves: first ↑ COMP reaches the COMP node; then
    inside-out finds N such that N[SUBJ] = that COMP node."""
    eq = parse_equation("(SUBJ (↑ COMP)) = 'X'")
    assert isinstance(eq, DefiningEquation)
    inner = Designator(Up(), (Feature("COMP"),))
    assert eq.lhs == Designator(
        InsideOut(feat="SUBJ", inner=inner),
        (),
    )


def test_inside_out_nested():
    """``(SUBJ (XCOMP ↑))`` — nested inside-out. Inner is itself an
    inside-out designator: find F such that F[XCOMP] = ↑; then find
    N such that N[SUBJ] = F."""
    eq = parse_equation("(SUBJ (XCOMP ↑)) = 'X'")
    assert isinstance(eq, DefiningEquation)
    inner_iout = Designator(
        InsideOut(feat="XCOMP", inner=Designator(Up(), ())),
        (),
    )
    assert eq.lhs == Designator(
        InsideOut(feat="SUBJ", inner=inner_iout),
        (),
    )


def test_inside_out_on_constraining_eq():
    """``((SUBJ ↑) GF) =c 'X'`` — inside-out designator on the LHS
    of a constraining equation."""
    eq = parse_equation("((SUBJ ↑) GF) =c 'X'")
    assert isinstance(eq, ConstrainingEquation)
    assert eq.lhs.base == InsideOut(
        feat="SUBJ", inner=Designator(Up(), ()),
    )


def test_inside_out_existential():
    """Standalone inside-out designator as existential constraint."""
    eq = parse_equation("(SUBJ ↑)")
    assert isinstance(eq, ExistentialConstraint)
    assert eq.designator.base == InsideOut(
        feat="SUBJ", inner=Designator(Up(), ()),
    )


# === Strings drawn from the existing grammar / earley demo =================

EXISTING_EQUATIONS = [
    # grammar.py
    "(↑ CASE)= 'NOM'",
    "(↑ PRED) = ↓2 PRED",
    "(↑ CASE)= 'GEN'",
    "(↑ CASE)= 'DAT'",
    "(↑ PRED) = 'NOUN(↑ FORM)'",
    "(↑)=↓1",
    "(↑ PRED) = ↓1 PRED",
    "(↑ VOICE) = ↓1 VOICE",
    "(↑ SUBJ) = ↓3",
    "(↑ OBL-AG) = ↓2",
    "(↑ ASPECT) = ↓1 ASPECT",
    "(↑ MOOD) = ↓1 MOOD",
    # earley.py
    "(↑ PRED) = 'EAT <SUBJ, OBJ>'",
    "(↑ VOICE) = 'PV'",
    "(↑ ASPECT) = 'PFV'",
    "(↑ MOOD) = 'IND'",
    "(↑ LEX-ASTRUCT) = 'AGENT,PATIENT'",
    "(↑ CASE)='GEN'",
    "(↑ CASE)='NOM'",
]


@pytest.mark.parametrize("source", EXISTING_EQUATIONS)
def test_parses_existing_grammar_string(source):
    # Smoke-parse: every equation already in the codebase must round-trip.
    parsed = parse_equation(source)
    reparsed = parse_equation(unparse(parsed))
    assert parsed == reparsed


# === Round-trip canonicalisation ===========================================

ROUND_TRIP_CASES = [
    "(↑ PRED) = 'EAT'",
    "(↑ VOICE) = ↓1 VOICE",
    "(↑ SUBJ) = ↓3",
    "(↑) = ↓1",
    "(↑ CASE) =c 'NOM'",
    "(↑ TOPIC)",
    "¬ (↑ NEG)",
    "(↑ FOCUS) ≠ 'WH'",
    "↓ ∈ (↑ ADJ)",
    "(↑ TOPIC) = (↑ COMP* GF)",
    "(↑) = (↑ XCOMP+)",
    "(↑) = (↑ {SUBJ | OBJ})",
    "(↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)",
    # Phase 10.L Kleene-on-alternation:
    "(↑ TOPIC) = (↑ {COMP | XCOMP}* SUBJ)",
    "(↑ REL-PRO) =c (↑ {COMP | XCOMP}+ SUBJ)",
    "(↑ {COMP | XCOMP}*<(→ TENSE) =c 'PAST'> SUBJ)",
    # Phase 10.N inside-out designators:
    "(SUBJ ↑) = 'X'",
    "((SUBJ ↑) GF) =c 'X'",
    "((SUBJ ↑) F G H)",
    "(SUBJ (↑ COMP)) = 'X'",
    "(SUBJ (XCOMP ↑)) = 'X'",
]


@pytest.mark.parametrize("source", ROUND_TRIP_CASES)
def test_unparse_round_trip(source):
    eq1 = parse_equation(source)
    eq2 = parse_equation(unparse(eq1))
    assert eq1 == eq2


# === Errors ================================================================

def test_unbalanced_paren_left():
    with pytest.raises(ParseError):
        parse_equation("(↑ F = 'X'")


def test_unbalanced_paren_right():
    with pytest.raises(ParseError):
        parse_equation("(↑ F)) = 'X'")


def test_unterminated_atom():
    with pytest.raises(ParseError) as exc_info:
        parse_equation("(↑ F) = 'unclosed")
    assert "atom" in exc_info.value.message.lower()


def test_unknown_character():
    with pytest.raises(ParseError):
        parse_equation("(↑ F) @ 'X'")


def test_down_zero_rejected():
    with pytest.raises(ParseError) as exc_info:
        parse_equation("(↑ F) = ↓0")
    assert "≥ 1" in str(exc_info.value)


def test_trailing_tokens():
    with pytest.raises(ParseError) as exc_info:
        parse_equation("(↑ F) = 'X' garbage")
    assert "trailing" in exc_info.value.message.lower()


def test_empty_input_rejected():
    # Nothing in the input — no designator to parse.
    with pytest.raises(ParseError):
        parse_equation("")


def test_invalid_base():
    # Identifier inside parens, no metavariable.
    with pytest.raises(ParseError):
        parse_equation("(F) = 'X'")


def test_alt_requires_at_least_two():
    # AltFeature with one element looks like a stray brace.
    with pytest.raises(ParseError):
        parse_equation("(↑ {SUBJ})")


def test_offset_in_error():
    # Caret should point at the offending character.
    with pytest.raises(ParseError) as exc_info:
        parse_equation("(↑ F)  @  'X'")
    assert exc_info.value.offset == 7  # the '@'
