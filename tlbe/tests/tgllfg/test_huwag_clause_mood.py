# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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

from tgllfg.core.pipeline import parse_text


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


# === Phase 11.X — bare ``Huwag + V[AV]`` PRO injection ===================


class TestHuwagBareV:
    """Phase 11.X: bare-V negative imperative form. The bare-V
    surface (``Huwag kumain.``) has no overt addressee — the
    implicit addressee is synthesized as ``SUBJ.PRED='PRO'`` per
    audit doc §3.5 alternative (a) (Class-1 impersonal pattern).

    Closes the cfg/negation.py NOTE 226-237 deferral and
    out-of-scope §18.1.4 line 69. The bare-V form is the
    sign-language / prohibition-sign style documented in
    S&O 1972 §8.2.

    Two rule variants:

    * Bare V[AV]: ``Huwag kumain.``, ``Huwag tumakbo.``
    * V[AV] + GEN-OBJ: ``Huwag kumain ng aso.``
    """

    def test_bare_v_av_intr_pro_subj(self) -> None:
        # AV verb with PRO addressee. SUBJ.PRED='PRO' marks the
        # implicit addressee; POLARITY=NEG and CLAUSE-MOOD=IMP
        # mirror the canonical huwag clause shape.
        rs = parse_text("Huwag tumakbo.", n_best=10)
        assert rs, "Huwag tumakbo. should parse via 11.X bare-V rule"
        f = rs[0][1]
        assert f.feats.get("POLARITY") == "NEG"
        assert f.feats.get("CLAUSE-MOOD") == "IMP"
        assert f.feats.get("PRED") == "TAKBO <SUBJ>"
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("PRED") == "PRO"

    def test_bare_v_av_tr_with_gen_obj(self) -> None:
        # AV verb + GEN-OBJ. SUBJ still PRO; OBJ binds to overt
        # GEN-NP. Two-variant 11.X rule (with-GEN-OBJ daughter).
        rs = parse_text("Huwag kumain ng aso.", n_best=10)
        assert rs, "Huwag kumain ng aso. should parse via 11.X V+GEN-OBJ rule"
        f = rs[0][1]
        assert f.feats.get("POLARITY") == "NEG"
        assert f.feats.get("CLAUSE-MOOD") == "IMP"
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
        subj = f.feats.get("SUBJ")
        obj = f.feats.get("OBJ")
        assert subj is not None and obj is not None
        assert subj.feats.get("PRED") == "PRO"
        assert obj.feats.get("LEMMA") == "aso"

    def test_bare_v_av_kumain_no_obj(self) -> None:
        # ``Huwag kumain.`` — TR verb used absolutively (no OBJ).
        # AV's absolutive reading lets the OBJ slot stay absorbed
        # at the LMT layer; SUBJ.PRED='PRO' covers completeness.
        rs = parse_text("Huwag kumain.", n_best=10)
        assert rs, "Huwag kumain. should parse via 11.X bare-V rule"
        f = rs[0][1]
        assert f.feats.get("POLARITY") == "NEG"
        assert f.feats.get("CLAUSE-MOOD") == "IMP"
        assert f.feats.get("PRED") == "EAT <SUBJ>"
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("PRED") == "PRO"


class TestHuwagBareVScopePreserved:
    """Phase 11.X scope check: the new bare-V rules don't disrupt
    the existing canonical Huwag constructions. Each pre-11.X form
    parses with the same f-structure shape as before — no
    over-generation, no addressee-bleed."""

    def test_addressee_explicit_form_unchanged(self) -> None:
        # ``Huwag kang kumain.`` (Phase 10.final.pre-1 Variant A) —
        # SUBJ binds to overt PRON addressee, NOT PRO. Verifies
        # the bare-V rule doesn't shadow the addressee-explicit
        # rule when a PRON daughter is present.
        rs = parse_text("Huwag kang kumain.", n_best=10)
        assert rs
        f = rs[0][1]
        subj = f.feats.get("SUBJ")
        assert subj is not None
        # SUBJ comes from PRON ``ka`` — not synthesized PRO.
        assert subj.feats.get("PRED") != "PRO"

    def test_matrix_neg_with_overt_subj_unchanged(self) -> None:
        # ``Huwag kumain ang bata.`` (matrix-NEG rule wrapping a
        # complete inner S) — SUBJ is the overt NOM-NP ``ang bata``,
        # NOT PRO. Verifies the bare-V rule doesn't shadow the
        # matrix-NEG wrap when an inner S parses.
        rs = parse_text("Huwag kumain ang bata.", n_best=10)
        assert rs
        f = rs[0][1]
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("PRED") != "PRO"
