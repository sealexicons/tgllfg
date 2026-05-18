"""Phase 8.F: existential `may` + V-headed nominalized complement.

Closes the audit-named construction class where Tagalog `may`
admits a V-headed nominalized complement in addition to the
bare-N variant (Phase 5j Commit 5a / earlier `may` rules).

Examples:
  `May binalak siya.`              "He had a plan."
  `May nakita siya.`               "He saw something."
  `May ginagawa ka ba?`            "Do you have something you're doing?"
  `May nagdala ng kape.`           "Someone brought coffee."

Two new rules in `cfg/clause.py`:

Rule (a) — possessive shape:
  S → PART[EXISTENTIAL, POLARITY=POS] V[VOICE=X] NP[CASE=NOM]
    (↑ PRED) = 'EXIST <SUBJ>'
    (↑ SUBJ LEMMA) = ↓2 LEMMA
    (↑ SUBJ NOMINALIZED) = true
    (↑ SUBJ V_VOICE) = ↓2 VOICE
    (↑ SUBJ V_ASPECT) = ↓2 ASPECT
    (↑ SUBJ POSSESSOR) = ↓3
    (↑ HAVE) = true
  (registered for each VOICE value: AV / OV / RV / LF / DV / IV / BV)

Rule (b) — agentive (headless-RC) shape:
  S → PART[EXISTENTIAL, POLARITY=POS] V[VOICE=AV] NP[CASE=GEN]
    (↑ SUBJ OBJ) = ↓3
  (GEN-NP is the OBJ of the V; the empty SUBJ of V is the
  existence-asserted entity — "someone-who-brought" reading)

The V is captured as a deverbal-noun-like SUBJ via LEMMA capture
rather than full f-structure lift, to avoid leaking the V's
transitive PRED template (`BALAK <SUBJ, OBJ>`) into the matrix
where its argument slots wouldn't be realized.

Corpus audit: 12 candidates surveyed (Wave 2 + Wave 3). Direct
closures: 4 of 12 (33%). Remaining 8 blocked by OOV verb forms
(`naisip`, `gagawin`, `kakilala`) or OOV nouns (`Jose`,
`magagandang`, `banig`) — future 8.B-class lex pass.
"""

from __future__ import annotations

import pytest


def _has_exist_subj_v_pred(parses, pred_prefix):
    """True iff at least one parse has PRED='EXIST <SUBJ>' with
    SUBJ.V_PRED starting with pred_prefix (e.g., 'BALAK')."""
    for p in parses:
        if str(p[1].feats.get("PRED")) != "EXIST <SUBJ>":
            continue
        subj = p[1].feats.get("SUBJ")
        if subj and str(subj.feats.get("V_PRED", "")).startswith(
            pred_prefix
        ):
            return True
    return False


class TestPhase8fPossessiveShape:
    """Rule (a): `may + V + NOM-pivot` possessive shape."""

    @pytest.mark.parametrize("sentence,v_pred_prefix", [
        ("May binalak siya.", "BALAK"),
        ("May nakita siya.", "KITA"),
        ("May ginagawa ka ba?", "MAKE"),
    ])
    def test_possessive_v_headed(
        self, sentence: str, v_pred_prefix: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_exist_subj_v_pred(parses, v_pred_prefix), (
            f"{sentence!r} parsed but no EXIST/SUBJ.V_PRED prefix "
            f"{v_pred_prefix!r}"
        )


class TestPhase8fAgentiveShape:
    """Rule (b): `may + V[AV] + GEN-NP` agentive (headless-RC) shape."""

    def test_may_v_av_gen_np(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("May nagdala ng kape.", n_best=3)
        assert len(parses) >= 1
        assert _has_exist_subj_v_pred(parses, "DALA"), (
            "May nagdala ng kape. — no EXIST/SUBJ.V_PRED=DALA..."
        )


class TestPhase8fSubjFeats:
    """The SUBJ f-structure carries the nominalization signature
    (LEMMA, NOMINALIZED, V_VOICE, V_ASPECT) plus POSSESSOR."""

    def test_subj_carries_voice_aspect(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("May binalak siya.", n_best=3)
        # Find the parse with the expected SUBJ
        for p in parses:
            subj = p[1].feats.get("SUBJ")
            if subj and str(
                subj.feats.get("V_PRED", "")
            ).startswith("BALAK"):
                assert subj.feats.get("NOMINALIZED") is True
                assert str(subj.feats.get("V_VOICE")) == "OV"
                assert str(subj.feats.get("V_ASPECT")) == "PFV"
                assert "POSSESSOR" in subj.feats
                return
        pytest.fail("no BALAK-headed SUBJ found")


class TestPhase8fHaveFlag:
    """The possessive V-headed reading carries HAVE=true (matches
    the Phase 5j Commit 5a possessive convention for the N-headed
    variant: `May libro ako.` "I have a book.")."""

    def test_have_flag_set(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("May binalak siya.", n_best=3)
        # At least one parse has HAVE=true
        assert any(
            p[1].feats.get("HAVE") is True for p in parses
        ), "HAVE=true not set on any parse"


class TestPhase8fRegressions:
    """Pre-8.F may-existential parses are unaffected."""

    @pytest.mark.parametrize("sentence", [
        # Phase 5j C2 bare-N existential
        "May tao.",
        "May aklat sa mesa.",
        # Phase 5j C5a N-pivot possessive (the template for 8.F)
        "May tao siya.",
        "May aklat ako.",
        # Linker variant (mayroon)
        "Mayroong tao.",
        # Negative existential (wala)
        "Walang tao.",
    ])
    def test_existing_may_unaffected(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"


class TestPhase8fOutOfScope:
    """Audit corpus candidates that remain zero-parse after 8.F —
    all blocked by orthogonal OOV. Pin one of each cluster."""

    def test_oov_verb_form_naisip(self) -> None:
        """``May naisip ang mama.`` — `naisip` (RV PFV of `isip`)
        was OOV before 9.X.pre-1.24. The pre-1.24 affix-class extension
        (added ``ma`` to ``isip``'s affix_class) closes the surface;
        flipped to assert parse-success."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("May naisip ang mama.", n_best=3)
        assert len(parses) >= 1, (
            "naisip should now parse via the may + V-headed clause-type "
            "after the 9.X.pre-1.24 isip+ma affix-class extension."
        )

    def test_oov_verb_form_gagawin(self) -> None:
        """``May gagawin ka ba?`` — `gagawin` (LF FUT of `gawa`)
        is OOV. Future 8.B-class lex pass."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("May gagawin ka ba?", n_best=3)
        assert len(parses) == 0, (
            "gagawin OOV resolved — flip if 8.B-class lex sub-PR "
            "added the missing paradigm cell."
        )

    def test_oov_recp_form_kakilala(self) -> None:
        """``May kakilala ba kayo dito?`` — `kakilala` (RECP-ka- of
        `kilala`) is OOV. The CV-redup-ka- prefix lift isn't
        productive for this paradigm class. Future lex pass."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("May kakilala ba kayo dito?", n_best=3)
        assert len(parses) == 0, (
            "kakilala OOV resolved — flip if the relevant paradigm "
            "cell sub-PR added the missing entry."
        )

    def test_proper_name_jose_closed_in_9j(self) -> None:
        """``May ginagawa si Jose.`` — ``Jose`` proper name was
        an 8.F deferral pin asserting OOV-blocked. Phase 9.J
        catch-all OOV pass added ``jose`` as a NOUN entry with
        ``subclass: [PERSON, MALE]``, ``source: audit-corpus``;
        the audit sentence now parses."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("May ginagawa si Jose.", n_best=3)
        assert len(parses) >= 1, (
            "9.J added jose proper-name; sentence should now parse."
        )
