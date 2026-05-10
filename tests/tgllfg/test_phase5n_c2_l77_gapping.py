"""Phase 5n.C.2 Commit 5 — L77 gapping in coordination.

Closes §18.1 L77 (gapping in coord). Canonical pattern: ``<V>
<agent1> <args1> at <agent2> <args2>`` where the verb is shared
across conjuncts (``Kumain si Maria ng kanin at si Juan ng
tinapay.`` "Maria ate rice and Juan bread").

The new gapping rules in ``src/tgllfg/cfg/coordination.py`` produce
parses where:

- the matrix S carries ``COORD=AND``, ``GAPPING=YES``, and a
  ``CONJUNCTS`` set with 2 or 3 conjunct f-structures;
- conjunct1 is the V's own f-structure (carrying PRED + voice
  + aspect + mood, plus SUBJ/OBJ from the first NP pair);
- subsequent conjuncts are fresh sub-f-structures with PRED +
  voice/aspect/mood reentrant to the V's PRED, plus SUBJ/OBJ
  from their own NP pair (the LFG PRED-sharing analysis per
  Bresnan 2001 §6 + Dalrymple 2001 §4).

Design appendix: ``docs/analysis-choices.md`` §"Phase 5n.C.2
Commit 4: L77 PRED-sharing gapping in coord". Bundled C5 also
flipped the Commit 3 tripwires (corpus expected: fragment →
parse for DV cases; AV-spurious matrix-COORD absence → matrix
COORD=AND on the new gapping parse).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Canonical AV gapping (2-conjunct) ====================================


@pytest.mark.parametrize("sentence", [
    "Kumain si Maria ng kanin at si Juan ng tinapay.",
    "Bumili si Maria ng aklat at si Pedro ng panulat.",
    "Naglinis si Maria ng bahay at si Pedro ng kotse.",
])
def test_av_gapping_2conj(sentence: str) -> None:
    """≥1 parse has matrix COORD=AND + GAPPING=YES + 2-conjunct
    CONJUNCTS set with shared PRED."""
    parses = parse_text(sentence)
    assert len(parses) >= 1, f"expected ≥1 parse for {sentence!r}"
    gapping_parses = [
        (ct, fs) for ct, fs, _astr, _diags in parses
        if fs.feats.get("GAPPING") == "YES"
    ]
    assert len(gapping_parses) >= 1, (
        f"expected ≥1 gapping parse for {sentence!r}; got "
        f"{len(parses)} parses but no GAPPING=YES"
    )
    _ct, fs = gapping_parses[0]
    assert fs.feats.get("COORD") == "AND"
    conjuncts = fs.feats.get("CONJUNCTS")
    assert conjuncts is not None
    assert len(conjuncts) == 2


# === Canonical AV gapping (3-conjunct, Oxford comma) ======================


def test_av_gapping_3conj() -> None:
    sentence = (
        "Kumain si Maria ng kanin, si Juan ng tinapay, "
        "at si Lola ng isda."
    )
    parses = parse_text(sentence)
    gapping_parses = [
        (ct, fs) for ct, fs, _astr, _diags in parses
        if fs.feats.get("GAPPING") == "YES"
    ]
    assert len(gapping_parses) >= 1, (
        f"expected ≥1 gapping parse for {sentence!r}"
    )
    _ct, fs = gapping_parses[0]
    assert fs.feats.get("COORD") == "AND"
    conjuncts = fs.feats.get("CONJUNCTS")
    assert conjuncts is not None
    assert len(conjuncts) == 3


# === Canonical DV gapping (2-conjunct) ====================================


@pytest.mark.parametrize("sentence", [
    "Tinulungan ni Maria si Juan at ni Pedro si Lola.",
    "Sinulatan ni Maria si Juan at ni Pedro si Lola.",
    "Inaralan ni Maria si Juan at ni Pedro si Lola.",
    "Binigayan ni Maria si Juan at ni Pedro si Lola.",
])
def test_dv_gapping_2conj(sentence: str) -> None:
    """Canonical DV gapping: ``<V[DV]> <ni AGENT> <si PIVOT> at
    <ni AGENT2> <si PIVOT2>``. ≥1 parse has GAPPING=YES."""
    parses = parse_text(sentence)
    assert len(parses) >= 1, f"expected ≥1 parse for {sentence!r}"
    gapping_parses = [
        (ct, fs) for ct, fs, _astr, _diags in parses
        if fs.feats.get("GAPPING") == "YES"
    ]
    assert len(gapping_parses) >= 1, (
        f"expected ≥1 gapping parse for {sentence!r}"
    )
    _ct, fs = gapping_parses[0]
    assert fs.feats.get("COORD") == "AND"
    conjuncts = fs.feats.get("CONJUNCTS")
    assert conjuncts is not None
    assert len(conjuncts) == 2


# === DV ditransitive gapping (shared AGENT across conjuncts) ==============


def test_dv_ditrans_gapping() -> None:
    """3-arg DV gapping where the GEN-agent is shared and each
    conjunct contributes its own NOM-pivot + GEN-theme pair.

    Canonical: ``Binigayan ni Maria si Juan ng aklat at si Pedro
    ng panulat.`` "Maria gave Juan a book and Pedro a pen". Both
    conjuncts share PRED + OBJ-AGENT (Maria); the SUBJ + OBJ-
    PATIENT differ. Requires the 3-arg DV LexicalEntry for
    ``bigay`` added in this commit.
    """
    sentence = "Binigayan ni Maria si Juan ng aklat at si Pedro ng panulat."
    parses = parse_text(sentence)
    gapping_parses = [
        (ct, fs) for ct, fs, _astr, _diags in parses
        if fs.feats.get("GAPPING") == "YES"
    ]
    assert len(gapping_parses) >= 1, (
        f"expected ≥1 gapping parse for {sentence!r}"
    )
    _ct, fs = gapping_parses[0]
    assert fs.feats.get("COORD") == "AND"
    conjuncts = list(fs.feats["CONJUNCTS"])
    assert len(conjuncts) == 2
    # Both conjuncts share OBJ-AGENT (Maria) via reentrancy.
    c1_agent = conjuncts[0].feats.get("OBJ-AGENT")
    c2_agent = conjuncts[1].feats.get("OBJ-AGENT")
    assert c1_agent is not None
    assert c2_agent is not None
    assert c1_agent == c2_agent, (
        "expected shared OBJ-AGENT (Maria) across both conjuncts"
    )
    # Each conjunct has its own OBJ-PATIENT (aklat vs panulat).
    c1_patient = conjuncts[0].feats.get("OBJ-PATIENT")
    c2_patient = conjuncts[1].feats.get("OBJ-PATIENT")
    assert c1_patient is not None
    assert c2_patient is not None
    assert c1_patient != c2_patient, (
        "expected distinct OBJ-PATIENT per conjunct"
    )


# === PRED-sharing reentrancy ==============================================


def test_pred_sharing_reentrant() -> None:
    """Both conjuncts share the SAME PRED via reentrancy — checked
    by identity of the PRED value across conjuncts."""
    sentence = "Kumain si Maria ng kanin at si Juan ng tinapay."
    parses = parse_text(sentence)
    gapping_parses = [
        (ct, fs) for ct, fs, _astr, _diags in parses
        if fs.feats.get("GAPPING") == "YES"
    ]
    assert len(gapping_parses) >= 1
    _ct, fs = gapping_parses[0]
    conjuncts = list(fs.feats["CONJUNCTS"])
    assert len(conjuncts) == 2
    c1_pred = conjuncts[0].feats.get("PRED")
    c2_pred = conjuncts[1].feats.get("PRED")
    assert c1_pred is not None
    assert c2_pred is not None
    # Both should be 'EAT <SUBJ, OBJ>' (the shared verb's PRED).
    assert c1_pred == c2_pred, (
        f"expected same PRED across conjuncts; got "
        f"c1.PRED={c1_pred!r} vs c2.PRED={c2_pred!r}"
    )


# === Biclausal coord unaffected ==========================================


@pytest.mark.parametrize("sentence", [
    "Tumakbo si Maria at sumayaw si Juan.",
    "Kumain si Maria ng kanin at uminom si Juan ng tubig.",
])
def test_biclausal_coord_unaffected(sentence: str) -> None:
    """Standard biclausal coord (with two Vs) continues to parse
    via the Phase 5k clausal-coord rule — COORD=AND but no
    GAPPING marker, since each conjunct is a full clause with its
    own V."""
    parses = parse_text(sentence)
    assert len(parses) >= 1
    # Each parse with COORD=AND should NOT have GAPPING=YES.
    coord_parses = [
        fs for _ct, fs, _astr, _diags in parses
        if fs.feats.get("COORD") == "AND"
    ]
    assert len(coord_parses) >= 1
    for fs in coord_parses:
        assert fs.feats.get("GAPPING") is None, (
            f"biclausal coord {sentence!r} should not carry "
            f"GAPPING=YES; got GAPPING={fs.feats.get('GAPPING')!r}"
        )
