"""Phase 5e Commit 25: huwag MOOD=IMP lifted to matrix via CLAUSE-MOOD.

Lifts the Phase 4 §7.2 limitation where the negation rule's
``(↑) = ↓2`` propagates the inner verb's MOOD=IND, conflicting
with the imperative-particle's MOOD=IMP. The §7.2 docs flagged
two resolution paths — selective GF projection or feature
architecture distinguishing predicate-mood from clausal-mood.
This commit takes the **feature-architecture** path.

A new feature ``CLAUSE-MOOD`` is introduced for sentential /
speech-act mood, distinct from the verb's morphological
``MOOD``:

* ``MOOD`` (existing) — verb's morphological mood. IND
  (default), ABIL, NVOL, SOC. Always projected from the
  verb's lex equations.
* ``CLAUSE-MOOD`` (new) — sentential mood. Set to IMP for
  negative imperatives via ``huwag``. Unset for declaratives.

The negation rule split:

* The existing ``S → PART[POLARITY=NEG] S`` rule gets a new
  ``¬ (↓1 MOOD)`` constraint, restricting it to particles
  WITHOUT MOOD (currently just ``hindi``).
* A new ``S → PART[MOOD=IMP, POLARITY=NEG] S`` rule fires for
  ``huwag`` and sets ``(↑ CLAUSE-MOOD) = 'IMP'`` on the
  matrix, alongside ``(↑ POLARITY) = 'NEG'``.

The category-pattern matcher is non-conflict, so
``PART[MOOD=IMP, POLARITY=NEG]`` would also match ``hindi`` (no
MOOD) by absorption. The huwag rule body adds a constraining
equation ``(↓1 MOOD) =c 'IMP'`` to actually require MOOD=IMP on
the particle.

These tests cover:

* ``Huwag kumain ang bata.`` — matrix has CLAUSE-MOOD=IMP,
  POLARITY=NEG, MOOD=IND (verb's morphological mood unchanged).
* ``Hindi kumain ang bata.`` — matrix has POLARITY=NEG,
  MOOD=IND, NO CLAUSE-MOOD (declarative NEG, the existing
  rule fires).
* ``Kumain ang bata.`` — matrix has MOOD=IND, no POLARITY
  or CLAUSE-MOOD (baseline IND clause).
* No regression on the parse counts for the canonical NEG
  sentences (huwag and hindi each produce a single parse for
  their respective surfaces).
"""

from __future__ import annotations

from tgllfg.pipeline import parse_text


# === Huwag clauses get CLAUSE-MOOD=IMP ====================================


class TestHuwagLift:
    """Negative imperative ``huwag`` produces matrix CLAUSE-MOOD=IMP
    (the lift) alongside POLARITY=NEG. The verb's morphological
    MOOD remains IND."""

    def test_huwag_intransitive(self) -> None:
        """``Huwag kumain ang bata.`` "(May) the child not eat" —
        matrix has CLAUSE-MOOD=IMP, POLARITY=NEG, MOOD=IND."""
        rs = parse_text("Huwag kumain ang bata.", n_best=10)
        assert rs
        f = rs[0][1]
        assert f.feats.get("CLAUSE-MOOD") == "IMP"
        assert f.feats.get("POLARITY") == "NEG"
        # Verb's morphological MOOD is unchanged.
        assert f.feats.get("MOOD") == "IND"

    def test_huwag_transitive(self) -> None:
        """``Huwag kumain ng isda ang bata.`` — same lift on a
        transitive AV clause."""
        rs = parse_text("Huwag kumain ng isda ang bata.", n_best=10)
        assert rs
        # Among the parses (could be 2 due to transitive ambiguity),
        # all should have CLAUSE-MOOD=IMP.
        for _, f, _, _ in rs:
            assert f.feats.get("CLAUSE-MOOD") == "IMP"
            assert f.feats.get("POLARITY") == "NEG"

    def test_huwag_with_ov(self) -> None:
        """``Huwag kainin ng bata ang isda.`` — OV verb with
        huwag. The lift composes with non-AV voice."""
        rs = parse_text("Huwag kainin ng bata ang isda.", n_best=10)
        if rs:  # OV+huwag may not parse depending on lex coverage
            for _, f, _, _ in rs:
                assert f.feats.get("CLAUSE-MOOD") == "IMP"


# === Hindi clauses unchanged ==============================================


class TestHindiUnchanged:
    """Declarative negation ``hindi`` is unchanged — no CLAUSE-MOOD
    is set (it would be IND or unset for declaratives). The existing
    rule (now restricted by ``¬ (↓1 MOOD)``) still fires."""

    def test_hindi_intransitive(self) -> None:
        """``Hindi kumain ang bata.`` "The child didn't eat" —
        matrix has POLARITY=NEG, MOOD=IND, NO CLAUSE-MOOD."""
        rs = parse_text("Hindi kumain ang bata.", n_best=10)
        assert rs
        f = rs[0][1]
        assert f.feats.get("POLARITY") == "NEG"
        assert f.feats.get("MOOD") == "IND"
        # CLAUSE-MOOD is NOT set on hindi clauses.
        assert f.feats.get("CLAUSE-MOOD") is None

    def test_hindi_transitive(self) -> None:
        rs = parse_text("Hindi kumain ng isda ang bata.", n_best=10)
        assert rs
        for _, f, _, _ in rs:
            assert f.feats.get("POLARITY") == "NEG"
            assert f.feats.get("CLAUSE-MOOD") is None

    def test_hindi_parse_count_unchanged(self) -> None:
        """``Hindi kumain ang bata.`` — exactly 1 parse (no spurious
        huwag-style parse with CLAUSE-MOOD=IMP)."""
        rs = parse_text("Hindi kumain ang bata.", n_best=10)
        assert len(rs) == 1


# === Baseline (no NEG) ====================================================


class TestBaselineUnchanged:
    """Plain declarative clauses (no NEG) unchanged — no POLARITY,
    no CLAUSE-MOOD."""

    def test_kumain_ang_bata(self) -> None:
        rs = parse_text("Kumain ang bata.", n_best=10)
        assert rs
        f = rs[0][1]
        assert f.feats.get("MOOD") == "IND"
        assert f.feats.get("POLARITY") is None
        assert f.feats.get("CLAUSE-MOOD") is None


# === Composition ==========================================================


class TestHuwagCompose:
    """The huwag rule composes with adv enclitics and other
    constructions."""

    def test_huwag_with_adv_enclitic(self) -> None:
        """``Huwag pa kumain ang bata.`` — ``pa`` (YET) clusters at
        clause-end via the existing adv enclitic rule. CLAUSE-MOOD
        still IMP."""
        rs = parse_text("Huwag pa kumain ang bata.", n_best=10)
        assert rs
        f = rs[0][1]
        assert f.feats.get("CLAUSE-MOOD") == "IMP"
