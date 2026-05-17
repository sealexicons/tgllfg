"""Phase 9.R: Non-SUBJ Ni-focus (B3.E).

Closes the 8.V `test_non_subj_ni_focus` pin (R&G Conversational
sent-1154 ``Ni ito ay hindi umiinom si Rosa.``) — DEM-PRON
Ni-focus on a non-SUBJ position with an in-clause NOM-pivot.

Extends the Phase 8.V SUBJ-focus Ni-X rule with three parallel
non-SUBJ variants (cfg/extraction.py, immediately after the 8.V
rule):

1. **Ni-OBJ-focus**: ``Ni X ay hindi V SUBJ.`` — AV verb with
   extractable OBJ; the fronted NOM-NP binds to S_GAP_OBJ's
   missing OBJ slot.

2. **Ni-OBJ-AGENT-focus**: ``Ni X ay hindi V-OV SUBJ.`` — non-AV
   verb with extractable GEN-actor; the fronted NOM-NP (Ni
   absorbing the case marker) binds to S_GAP_OBJ_AGENT's missing
   OBJ-AGENT slot.

3. **Ni-OBL-focus**: ``Ni sa X ay hindi V SUBJ.`` — any voice
   with extractable locative DAT-NP; the fronted DAT-NP binds
   to S_GAP_OBL (ADJUNCT set-add).

S&O 1972 §7.20: the ``Ni X`` focus-negation construction admits
any in-clause GF as the fronted-and-negated element. 8.V closed
the SUBJ case; 9.R closes the non-SUBJ cases by paralleling
8.V's structure for each non-pivot ay-fronting gap category.

The 8.V SUBJ-focus and 9.R non-SUBJ-focus rules are mutually
exclusive on the inner-clause shape:

* 8.V fires only on ``S_GAP`` (SUBJ missing) — fails when the
  inner has an explicit in-clause SUBJ like ``si Rosa``.
* 9.R rules fire on ``S_GAP_OBJ`` / ``S_GAP_OBJ_AGENT`` /
  ``S_GAP_OBL`` — these tolerate an in-clause SUBJ.

Audit-corpus hits (single-Ni non-SUBJ — 9.R scope):

* ``Ni ito ay hindi umiinom si Rosa.`` (R&G Conv / S&O 1972 p.603)
* ``Ni ilo ay hindi sila nagtitinda.`` (R&G Conv — OCR-garbled
  ``ilo`` → ``ito``)

Paired-Ni (``Ni X ni Y ay hindi Z``) is 9.S scope; ``Ni hindi V``
intensifier-negation is 9.T scope — both pinned in 8.V test file.
"""

from __future__ import annotations

import pytest


# -----------------------------------------------------------
# Class A: 8.V pin closure — DEM Ni-OBJ-focus with in-clause SUBJ
# -----------------------------------------------------------

class TestPhase8vNonSubjPinClosure:
    """The 8.V pin sentence and the underlying audit hit shape
    (DEM-Ni-focus + in-clause SUBJ) parse via 9.R Rule 1
    (Ni-OBJ-focus)."""

    @pytest.mark.parametrize("sentence,topic_dem", [
        # 8.V pin (substituted lex'd form)
        ("Ni ito ay hindi kumain si Maria.", True),
        # Audit-attested original (R&G Conv sent-1154)
        ("Ni ito ay hindi umiinom si Rosa.", True),
        # Other DEMs in topic slot
        ("Ni iyan ay hindi kumain si Maria.", True),
        ("Ni iyon ay hindi kumain si Maria.", True),
    ])
    def test_dem_ni_obj_focus_parses(
        self, sentence: str, topic_dem: bool,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True
        assert str(f.feats.get("POLARITY")) == "NEG"


# -----------------------------------------------------------
# Class B: OBJ-AGENT focus (non-AV with GEN-actor extracted)
# -----------------------------------------------------------

class TestNiObjAgentFocus:
    """``Ni si Maria ay hindi kinain ang aklat.`` — non-AV verb
    (kinain = OV-PFV); Ni-fronted NP binds to the extracted
    GEN-actor (OBJ-AGENT) slot."""

    @pytest.mark.parametrize("sentence", [
        "Ni si Maria ay hindi kinain ang aklat.",
        "Ni si Juan ay hindi kinain ang aklat.",
    ])
    def test_ni_obj_agent_focus(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True


# -----------------------------------------------------------
# Class C: OBL-focus (DAT-NP fronted, locative/directional)
# -----------------------------------------------------------

class TestNiOblFocus:
    """``Ni sa bahay ay hindi pumunta si Juan.`` — Ni-fronted
    locative DAT-NP binds to the inner S_GAP_OBL's ADJUNCT
    set (no scalar REL-PRO=c equation since ADJUNCT is set-
    valued)."""

    @pytest.mark.parametrize("sentence", [
        "Ni sa bahay ay hindi pumunta si Juan.",
        "Ni sa mesa ay hindi kumain si Maria.",
    ])
    def test_ni_obl_focus(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True


# -----------------------------------------------------------
# Class D: NEG gate (Ni-focus requires hindi-negated inner)
# -----------------------------------------------------------

class TestNiNegGate:
    """Affirmative inner clause + Ni non-SUBJ-focus is blocked
    (mirrors 8.V's POLARITY=NEG gate). Per S&O 1972 §7.20, ``Ni``
    "not even" semantically requires negation."""

    @pytest.mark.parametrize("sentence", [
        "Ni ito ay kumain si Maria.",
        "Ni sa bahay ay pumunta si Juan.",
    ])
    def test_affirmative_inner_blocks_ni(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        for _ct, f, *_ in parses:
            assert f.feats.get("FOCUS_NEG") is not True, (
                f"affirmative inner admitted FOCUS_NEG matrix: "
                f"{sentence!r}"
            )


# -----------------------------------------------------------
# Class E: 8.V SUBJ-focus retained (regression)
# -----------------------------------------------------------

class TestSubjFocusRetained:
    """The 8.V SUBJ-focus rule still fires when the inner clause
    has no in-clause SUBJ (S_GAP)."""

    @pytest.mark.parametrize("sentence", [
        "Ni si Juan ay hindi kumain.",
        "Ni si Maria ay hindi umalis.",
        "Ni ito ay hindi kumain.",
    ])
    def test_subj_focus_unchanged(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"8.V SUBJ-focus regression: {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True


# -----------------------------------------------------------
# Class F: regression checks (non-Ni ay-fronting unaffected)
# -----------------------------------------------------------

class TestNonNiAyFrontingRegressions:
    """The 9.R rules add new FOCUS_NEG-gated paths; the existing
    non-pivot ay-fronting rules (GEN+S_GAP_OBJ, GEN+S_GAP_OBJ_AGENT,
    DAT+S_GAP_OBL) should be unaffected."""

    @pytest.mark.parametrize("sentence", [
        # Phase 5d Commit 5: non-pivot OBJ-fronting (no Ni)
        "Ng isda ay kumain si Maria.",
        # Phase 5d Commit 5: non-pivot OBJ-AGENT-fronting (no Ni)
        "Ni Maria ay kinain ang isda.",
        # Phase 5d Commit 5: non-pivot OBL-fronting (no Ni)
        "Sa bahay ay kumain si Maria.",
    ])
    def test_existing_ay_fronting(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"regression: {sentence!r}"


# -----------------------------------------------------------
# Class G: f-structure shape
# -----------------------------------------------------------

class TestFstructShape:
    """The non-SUBJ Ni-focus f-structure carries FOCUS_NEG=true,
    POLARITY=NEG, and TOPIC bound to the fronted NP. The in-clause
    SUBJ remains in the matrix SUBJ slot."""

    def test_obj_focus_fstruct(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni ito ay hindi kumain si Maria.", n_best=3,
        )
        assert len(parses) >= 1
        _ct, f, *_ = parses[0]
        assert f.feats.get("FOCUS_NEG") is True
        assert str(f.feats.get("POLARITY")) == "NEG"
        # TOPIC bound to fronted DEM
        topic = f.feats.get("TOPIC")
        assert topic is not None
        assert str(topic.feats.get("PRED")) == "PRO"
        assert topic.feats.get("DEM") is True
        # In-clause SUBJ is `si Maria`
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert str(subj.feats.get("LEMMA")) == "maria"


# -----------------------------------------------------------
# Class H: out-of-scope (deferred to 9.S / 9.T)
# -----------------------------------------------------------

class TestPhase9rOutOfScope:
    """Construction-class variants NOT closed by 9.R.

    Paired-Ni and Ni-hindi-V have their own pins in
    test_phase8v_ni_focus_neg.py (TestPhase8vOutOfScope).
    This class adds 9.R-specific deferrals."""

    def test_ni_bare_n_focus(self) -> None:
        """``Ni damit ay hindi binili.`` — Ni-fronted bare N
        (no NOM/GEN/DAT marker). Per S&O 1972 §7.20, ``Ni`` can
        absorb the case marker entirely, leaving the fronted
        element as a bare N. This case-less fronting needs a
        separate rule shape (bare-N daughter rather than
        NP[CASE=X]); defer to a follow-on sub-PR. The canonical
        example is paired (``Ni damit ni sapatos ...``) — 9.S
        scope. Single-Ni + bare-N variant pinned here."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni damit ay hindi binili.", n_best=2,
        )
        assert len(parses) == 0, (
            "single-Ni bare-N focus may have closed; review and flip."
        )
