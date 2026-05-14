"""Phase 7a.C: `katatapos + V_inf` raising-from-XCOMP (§18.1.1 item 3).

Two coordinated sub-closures:

1. **Non-AV RECPFV deferral** — reclassified from §18.1.1 to §18.1.3
   per Phase 7a.C closure with the strengthened structural diagnostic
   (recent-perfective forms lack the ``ang``-marked pivot that defines
   non-AV voices structurally; non-AV columns are structurally
   unavailable, not just descriptively absent). See Phase 5e Commit 23
   for the original Handbook-of-Tagalog-Verbs paradigm evidence.
2. **`katatapos + V` raising wiring** — the analytic alternative for
   non-AV "just-finished" readings. New particle entry in
   ``data/tgl/particles.yaml`` with ``CTRL_CLASS=RAISING_BARE``; new
   lex entry in ``data/tgl/lexicon/control.yaml`` with PRED
   ``JUST-FINISHED <XCOMP> SUBJ``. Consumed by the existing Phase 5d
   bare-raising rule (``cfg/control.py``: ``S → V[RAISING_BARE] S``).

The matrix `katatapos` raises the embedded V's SUBJ to its own SUBJ,
allowing the embedded V's voice / pivot to be free. For OV-embedded
clauses, this delivers the non-AV "just-finished" reading the plan-
of-record §3.3 promised: ``Katatapos kainin ko ang isda.`` "The fish
had just been eaten by me" with the OV pivot ``ang isda`` raised to
matrix SUBJ.

Scope limitations (not bugs, just out of v1 scope):

* Bare OV embedded without overt GEN actor (``Katatapos kainin ang
  isda.``) does not parse — the inner ``kainin ang isda`` does not
  parse standalone (the OV grammar requires the actor for CTPL).
* Linker form (``Katatapos kong kumain.`` "I had just eaten") does
  not parse — that construction routes ``ko`` as a 2nd-position
  clitic between the matrix and embedded V, a different syntactic
  shape from the RAISING_BARE rule.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph import analyze_tokens
from tgllfg.text import tokenize


# === Morphology ====================================================


class TestKatatapasMorphology:
    """The new particle entry in ``data/tgl/particles.yaml`` exposes
    ``katatapos`` as ``V[CTRL_CLASS=RAISING_BARE, LEMMA=tapos,
    ASPECT=RECPFV]``. This co-exists with the morphologically-
    generated AV-RECPFV analysis (CTRL_CLASS=NONE) from the existing
    paradigm engine; the parser selects between them by rule fit."""

    def test_raising_bare_analysis_present(self) -> None:
        toks = tokenize("katatapos")
        analyses = analyze_tokens(toks)[0]
        raising = [
            a
            for a in analyses
            if a.feats.get("CTRL_CLASS") == "RAISING_BARE"
        ]
        assert raising, (
            "katatapos should have a CTRL_CLASS=RAISING_BARE analysis"
        )
        assert raising[0].feats.get("LEMMA") == "tapos"
        assert raising[0].feats.get("ASPECT") == "RECPFV"

    def test_morphological_recpfv_analysis_preserved(self) -> None:
        # The existing AV-RECPFV cell still fires (CTRL_CLASS=NONE).
        toks = tokenize("katatapos")
        analyses = analyze_tokens(toks)[0]
        recpfv = [
            a
            for a in analyses
            if a.feats.get("ASPECT") == "RECPFV"
            and a.feats.get("CTRL_CLASS") == "NONE"
        ]
        assert recpfv, (
            "katatapos should retain its AV-RECPFV (CTRL_CLASS=NONE) "
            "analysis from the existing paradigm cell"
        )


# === Raising clause parses =========================================


class TestKatatapasRaisingClause:
    """The existing `S → V[CTRL_CLASS=RAISING_BARE] S` rule
    (Phase 5d Commit 1, `cfg/control.py:868-875`) consumes
    `katatapos` and produces a JUST-FINISHED matrix with the
    embedded V's SUBJ structure-shared via raising."""

    def test_av_intrans_kumain_aso(self) -> None:
        # `Katatapos kumain ang aso.` "The dog had just eaten."
        parses = parse_text("Katatapos kumain ang aso.")
        assert parses, "AV-intrans embedded should parse"
        fs = parses[0][1]
        assert fs.feats.get("PRED") == "JUST-FINISHED <XCOMP> SUBJ"

    def test_av_with_nom_pronoun_subj(self) -> None:
        # `Katatapos kumain ako.` "I had just eaten."
        parses = parse_text("Katatapos kumain ako.")
        assert parses, "AV with NOM pronoun should parse"
        fs = parses[0][1]
        assert fs.feats.get("PRED") == "JUST-FINISHED <XCOMP> SUBJ"

    def test_av_ipfv_embedded(self) -> None:
        # `Katatapos kumakain ang bata.` "The child had just been
        # eating." Embedded V is AV-IPFV.
        parses = parse_text("Katatapos kumakain ang bata.")
        assert parses, "AV-IPFV embedded should parse"

    @pytest.mark.parametrize(
        "sentence,expected_pivot_lemma",
        [
            # The OV cases: pivot raises from the embedded OV verb's
            # NOM-pivot patient to the matrix SUBJ.
            ("Katatapos kainin ko ang isda.", "isda"),
            ("Katatapos kinain ng aso ang isda.", "isda"),
        ],
    )
    def test_ov_pivot_raised(
        self, sentence: str, expected_pivot_lemma: str
    ) -> None:
        # The OV pivot (`ang isda`) becomes the matrix SUBJ via
        # raising — the canonical value of the construction
        # (delivers non-AV "just-finished" reading).
        parses = parse_text(sentence)
        assert parses, f"{sentence!r} should parse"
        fs = parses[0][1]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == expected_pivot_lemma, (
            f"{sentence!r}: SUBJ.lemma should be {expected_pivot_lemma}"
        )

    def test_mga_np_subj_interaction(self) -> None:
        # `Katatapos kumain ang mga bata.` "The children had just
        # eaten." Interaction with Phase 7a.A `mga` plural rule:
        # the SUBJ gets NUM=PL from the new NP rule and that
        # propagates through raising.
        parses = parse_text("Katatapos kumain ang mga bata.")
        assert parses, "mga-NP SUBJ with katatapos should parse"
        fs = parses[0][1]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("NUM") == "PL"


# === Existing raising verbs unaffected =============================


class TestExistingRaisingUnaffected:
    """The pre-Phase-7a.C raising verbs (tila / parang / mukha / baka)
    still parse with their canonical PRED templates. Adding katatapos
    doesn't perturb the existing raising machinery."""

    def test_tila_still_apparent(self) -> None:
        parses = parse_text("Tila kumain ang aso.")
        assert parses
        fs = parses[0][1]
        assert fs.feats.get("PRED") == "APPARENTLY <XCOMP> SUBJ"

    def test_parang_still_seems_like(self) -> None:
        parses = parse_text("Parang kumain ang aso.")
        assert parses
        fs = parses[0][1]
        assert fs.feats.get("PRED") == "SEEMS-LIKE <XCOMP> SUBJ"


# === Scope-limit documentation =====================================


class TestScopeLimits:
    """Surfaces explicitly out of Phase 7a.C v1 scope.

    These don't parse — but the failure is a pre-existing limitation
    of the embedded grammar, not a bug in the katatapos wiring."""

    def test_ov_no_actor_does_not_parse(self) -> None:
        # `Katatapos kainin ang isda.` — bare OV without GEN actor.
        # The inner `kainin ang isda` does not parse standalone
        # (Phase 4 §7 OV grammar limitation), so the raising
        # construction also fails.
        parses = parse_text("Katatapos kainin ang isda.")
        assert not parses, (
            "OV-without-actor embedded shouldn't parse "
            "(inner standalone fails); documented scope limit"
        )

    def test_linker_kong_form_does_not_parse(self) -> None:
        # `Katatapos kong kumain.` — linker-form raising with
        # 2nd-position GEN clitic. Different construction; not
        # routed through RAISING_BARE rule.
        parses = parse_text("Katatapos kong kumain.")
        assert not parses, (
            "Linker `kong` form shouldn't parse via RAISING_BARE; "
            "documented scope limit"
        )
