"""Phase 9.S: Paired Ni X ni Y correlative coordination of foci (B3.E).

Closes the 8.V `test_paired_ni_correlative` pin (S&O 1972 p.604
sent-1159 ``Ni si Juan ni si Ben ay hindi bibilhin iyan.``).

Per S&O 1972 §7.20, ``Ni X ni Y`` correlatively coordinates two
foci, both negated by the matrix's ``hindi``. Four new rules in
cfg/extraction.py paralleling 8.V SUBJ-focus + 9.R Non-SUBJ-focus
rules with a second ``PART[FOCUS_NEG=true] NP[CASE=X]`` daughter
inserted before the ``ay`` particle:

1. **Paired-Ni SUBJ-focus**: 6-daughter rule with S_GAP inner.
2. **Paired-Ni OBJ-focus**: S_GAP_OBJ inner.
3. **Paired-Ni OBJ-AGENT-focus**: S_GAP_OBJ_AGENT inner.
4. **Paired-Ni OBL-focus**: 2 DAT-NPs + S_GAP_OBL inner.

F-structure shape:

* ``TOPIC`` = ↓2 (first conjunct — primary focus / gap binder)
* ``NI_CONJUNCTS`` ⊇ {↓4} (second conjunct rides as set member)
* ``FOCUS_NEG`` = true
* ``POLARITY`` = 'NEG'

The gap binds to the first conjunct's f-structure via ``REL-PRO``;
semantically the negation distributes over both ("neither X nor Y
did Z"), but the structural binding pin is the first conjunct,
matching the LFG convention for ay-fronted topic-gap relations.

Both ↓1 and ↓3 ``ni`` particles must carry ``FOCUS_NEG=true``.

Audit-corpus hits (R&G Conversational / S&O 1972):

* ``Ni si Juan ni si Ben ay hindi bibilhin iyan.`` (8.V pin) —
  lex/paradigm-blocked on ``bibilhin`` (OOV) but the construction
  shape closes via Rule 1 (verified with lex'd substitutes).
* ``Ni damit ni sapatos ay hindi nakakabili ang taong iyon.`` —
  lex-blocked on ``nakakabili`` + ``taong`` (OOV / paradigm gap).
* ``Ni ngayon ni hulas ay hindi ako makakaalis.`` — lex-blocked
  on ``hulas`` (OOV; ADV-paired Ni-focus construction).
"""

from __future__ import annotations

import pytest


# -----------------------------------------------------------
# Class A: 8.V pin closure — Paired-Ni SUBJ-focus
# -----------------------------------------------------------

class TestPhase8vPairedPinClosure:
    """The 8.V pin sentence and minor variants parse via 9.S
    Rule 1 (Paired-Ni SUBJ-focus)."""

    @pytest.mark.parametrize("sentence", [
        # 8.V pin (substituted lex'd form)
        "Ni si Juan ni si Maria ay hindi kumain.",
        # Other paired SUBJs
        "Ni si Pedro ni si Ana ay hindi umalis.",
        "Ni si Maria ni si Juan ay hindi kumain.",
    ])
    def test_paired_ni_subj_focus(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True
        assert str(f.feats.get("POLARITY")) == "NEG"


# -----------------------------------------------------------
# Class B: Paired-Ni OBJ-focus (DEMs, in-clause SUBJ)
# -----------------------------------------------------------

class TestPairedNiObjFocus:
    """``Ni ito ni iyan ay hindi kumain si Maria.`` — paired Ni-DEM
    binds to OBJ; in-clause SUBJ ``si Maria`` retained."""

    @pytest.mark.parametrize("sentence", [
        "Ni ito ni iyan ay hindi kumain si Maria.",
        "Ni ito ni iyon ay hindi kumain si Pedro.",
    ])
    def test_paired_obj(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True


# -----------------------------------------------------------
# Class C: Paired-Ni OBJ-AGENT-focus
# -----------------------------------------------------------

class TestPairedNiObjAgentFocus:
    """``Ni si Maria ni si Juan ay hindi kinain ang aklat.`` —
    paired Ni-PROP binds to OBJ-AGENT (non-AV verb)."""

    @pytest.mark.parametrize("sentence", [
        "Ni si Maria ni si Juan ay hindi kinain ang aklat.",
        "Ni si Pedro ni si Ana ay hindi kinain ang aklat.",
    ])
    def test_paired_obj_agent(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class D: Paired-Ni OBL-focus (DAT-NPs)
# -----------------------------------------------------------

class TestPairedNiOblFocus:
    """``Ni sa bahay ni sa kotse ay hindi pumunta si Juan.`` —
    paired Ni-DAT-NP binds to OBL ADJUNCT set."""

    @pytest.mark.parametrize("sentence", [
        "Ni sa bahay ni sa kotse ay hindi pumunta si Juan.",
        "Ni sa mesa ni sa bahay ay hindi pumunta si Maria.",
    ])
    def test_paired_obl(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class E: NEG gate (paired-Ni still requires hindi)
# -----------------------------------------------------------

class TestPairedNiNegGate:
    """Affirmative inner clause + paired Ni-focus is blocked
    (mirrors 8.V / 9.R's POLARITY=NEG gate)."""

    @pytest.mark.parametrize("sentence", [
        "Ni si Juan ni si Maria ay kumain.",
        "Ni sa bahay ni sa kotse ay pumunta si Juan.",
    ])
    def test_affirmative_blocked(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        for _ct, f, *_ in parses:
            assert f.feats.get("FOCUS_NEG") is not True, (
                f"affirmative inner admitted FOCUS_NEG matrix: "
                f"{sentence!r}"
            )


# -----------------------------------------------------------
# Class F: 8.V SUBJ-focus + 9.R Non-SUBJ-focus retained
# -----------------------------------------------------------

class TestSingleNiFocusRetained:
    """The single-Ni 8.V / 9.R rules still fire on their canonical
    inputs — adding the paired-Ni rules doesn't shadow them."""

    @pytest.mark.parametrize("sentence", [
        # 8.V SUBJ-focus
        "Ni si Juan ay hindi kumain.",
        "Ni ito ay hindi kumain.",
        # 9.R Non-SUBJ-focus
        "Ni ito ay hindi kumain si Maria.",
        "Ni ito ay hindi umiinom si Rosa.",
    ])
    def test_single_ni_unchanged(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"single-Ni regression: {sentence!r}"
        f = parses[0][1]
        assert f.feats.get("FOCUS_NEG") is True


# -----------------------------------------------------------
# Class G: f-structure shape — NI_CONJUNCTS set
# -----------------------------------------------------------

class TestPairedNiFstruct:
    """The second conjunct rides on a NI_CONJUNCTS set on the
    matrix S. Verify both conjuncts' LEMMAs surface correctly."""

    def test_subj_focus_ni_conjuncts(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni si Juan ni si Maria ay hindi kumain.", n_best=3,
        )
        assert len(parses) >= 1
        _ct, f, *_ = parses[0]
        assert f.feats.get("FOCUS_NEG") is True
        assert str(f.feats.get("POLARITY")) == "NEG"
        # Primary TOPIC is the first conjunct (Juan)
        topic = f.feats.get("TOPIC")
        assert topic is not None
        assert str(topic.feats.get("LEMMA")) == "juan"
        # Second conjunct rides on NI_CONJUNCTS set
        ni_conj = f.feats.get("NI_CONJUNCTS")
        assert ni_conj is not None, (
            f"no NI_CONJUNCTS set; feats keys = "
            f"{list(f.feats.keys())}"
        )
        members = list(ni_conj)
        assert len(members) == 1
        assert str(members[0].feats.get("LEMMA")) == "maria"


# -----------------------------------------------------------
# Class H: regression — non-Ni and single-Ni baselines
# -----------------------------------------------------------

class TestNonRegressions:
    """Non-Ni and non-paired baselines remain unaffected."""

    @pytest.mark.parametrize("sentence", [
        "Bumili si Maria ng aklat.",
        "Kumain ang bata.",
        "Magandang aklat ito.",
        # Pre-existing non-pivot ay-fronting
        "Ng isda ay kumain si Maria.",
        # Phase 5k coordination retained (no Ni)
        "Si Juan at si Maria ay kumain.",
    ])
    def test_baseline_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"baseline regression: {sentence!r}"


# -----------------------------------------------------------
# Class I: out-of-scope deferrals
# -----------------------------------------------------------

class TestPhase9sOutOfScope:
    """Audit-attested variants not closed by 9.S — each blocked
    by an orthogonal lex / paradigm gap, not a grammar gap. Pin;
    flip when the relevant follow-on closes the lex."""

    def test_audit_bibilhin(self) -> None:
        """``Ni si Juan ni si Ben ay hindi bibilhin iyan.`` — the
        construction parses post-9.S but ``bibilhin`` is OOV
        (OV-CTPL of ``bili``; missing paradigm cell). Flip when
        the relevant paradigm cell lands."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni si Juan ni si Ben ay hindi bibilhin iyan.", n_best=2,
        )
        assert len(parses) == 0, (
            "bibilhin OOV closed — review and flip pin."
        )

    def test_audit_paired_advs(self) -> None:
        """``Ni ngayon ni hulas ay hindi ako makakaalis.`` — ADV-
        paired Ni-focus. Blocked by: (a) ``hulas`` OOV (variant of
        ``bukas`` "tomorrow"); (b) ``makakaalis`` OOV (ABIL CTPL
        of ``alis``). And ADV-headed Ni-focus needs ADV → NP[CASE=X]
        promotion that isn't in 9.S scope. Defer."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni ngayon ni hulas ay hindi ako makakaalis.", n_best=2,
        )
        assert len(parses) == 0, (
            "ADV-paired Ni audit hit closed — review and flip pin."
        )

    def test_audit_bare_n_paired(self) -> None:
        """``Ni damit ni sapatos ay hindi nakakabili ang taong iyon.``
        — bare-N paired-Ni. Blocked by ``nakakabili`` (OOV; ABIL
        CTPL of ``bili``) + ``taong iyon`` (linker form not parsed
        as standalone NP fragment). Also requires bare-N Ni-focus
        rule variant (current 9.S uses NP[CASE=NOM], not bare N).
        Defer to a follow-on bundling lex + bare-N variant."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ni damit ni sapatos ay hindi nakakabili ang taong iyon.",
            n_best=2,
        )
        assert len(parses) == 0, (
            "bare-N paired-Ni audit hit closed — review and flip pin."
        )
