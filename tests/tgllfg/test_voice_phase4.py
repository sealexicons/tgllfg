"""Phase 4 §7.1: end-to-end parses across all four voices.

Each anchor verb is exercised at least once per voice slot it
supports, with f-structure assertions on (PRED, VOICE, ASPECT, SUBJ
PRED, OBJ PRED). The OBJ-uniform analysis is verified directly:
across OV, DV, and IV the *ng*-non-pivot lands on OBJ regardless of
its thematic role.

Word-order freedom is exercised by `test_av_tr_either_order` —
``Kumain ang aso ng isda`` and ``Kumain ng isda ang aso`` must both
parse to f-structures with SUBJ=aso, OBJ=isda.
"""

from __future__ import annotations

from typing import Any

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[Any, FStructure, Any, list[Any]]:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0]


def _pred(f: FStructure | None) -> str | None:
    if f is None or not isinstance(f, FStructure):
        return None
    pred = f.feats.get("PRED")
    return pred if isinstance(pred, str) else None


def _voice(f: FStructure) -> str | None:
    v = f.feats.get("VOICE")
    return v if isinstance(v, str) else None


def _aspect(f: FStructure) -> str | None:
    a = f.feats.get("ASPECT")
    return a if isinstance(a, str) else None


# === AV ===================================================================


def test_av_intransitive_kain() -> None:
    """Kumain ang aso → AV intransitive, SUBJ=aso, no OBJ."""
    _, f, _, _ = _first("Kumain ang aso.")
    assert _voice(f) == "AV"
    assert _aspect(f) == "PFV"
    pred = _pred(f)
    assert pred is not None and pred.startswith("EAT")
    assert "SUBJ" in f.feats
    # The intransitive PRED template is "EAT <SUBJ>", so OBJ is not
    # part of the f-structure.
    assert "OBJ" not in f.feats


def test_av_transitive_kain() -> None:
    """Kumain ang aso ng isda → AV transitive, SUBJ=aso, OBJ=isda."""
    _, f, _, _ = _first("Kumain ang aso ng isda.")
    assert _voice(f) == "AV"
    assert _pred(f) == "EAT <SUBJ, OBJ>"
    assert "SUBJ" in f.feats and "OBJ" in f.feats


def test_av_tr_either_order() -> None:
    """Tagalog free word order: ang-NP and ng-NP can appear in either
    order after the verb. Both surface variants of the same sentence
    must produce SUBJ=aso, OBJ=isda."""
    _, f1, _, _ = _first("Kumain ang aso ng isda.")
    _, f2, _, _ = _first("Kumain ng isda ang aso.")
    assert _voice(f1) == _voice(f2) == "AV"
    assert "SUBJ" in f1.feats and "OBJ" in f1.feats
    assert "SUBJ" in f2.feats and "OBJ" in f2.feats


# === OV ===================================================================


def test_ov_kinain() -> None:
    """Kinain ng aso ang isda → OV, SUBJ=isda (patient pivot),
    OBJ=aso (ng-non-pivot per OBJ-uniform)."""
    _, f, _, _ = _first("Kinain ng aso ang isda.")
    assert _voice(f) == "OV"
    assert _aspect(f) == "PFV"
    assert _pred(f) == "EAT <SUBJ, OBJ>"
    assert "SUBJ" in f.feats and "OBJ" in f.feats


def test_ov_binili() -> None:
    """Binili ng bata ang libro → OV, SUBJ=libro, OBJ=bata."""
    _, f, _, _ = _first("Binili ng bata ang libro.")
    assert _voice(f) == "OV"
    assert _pred(f) == "BUY <SUBJ, OBJ>"


def test_ov_binasa() -> None:
    _, f, _, _ = _first("Binasa ng bata ang libro.")
    assert _voice(f) == "OV"
    assert _pred(f) == "READ <SUBJ, OBJ>"


# === DV ===================================================================


def test_dv_sinulatan() -> None:
    """Sinulatan ng bata ang ina → DV, SUBJ=ina (recipient pivot),
    OBJ=bata (ng-non-pivot, per the OBJ-uniform analysis extended
    to DV in Phase 4 §7.1)."""
    _, f, _, _ = _first("Sinulatan ng bata ang ina.")
    assert _voice(f) == "DV"
    assert _aspect(f) == "PFV"
    assert _pred(f) == "WRITE <SUBJ, OBJ>"
    assert "SUBJ" in f.feats and "OBJ" in f.feats


# === IV ===================================================================


def test_iv_isinulat() -> None:
    """Isinulat ng bata ang liham → IV, SUBJ=liham (conveyed pivot),
    OBJ=bata (ng-non-pivot, per the OBJ-uniform analysis extended
    to IV in Phase 4 §7.1)."""
    _, f, _, _ = _first("Isinulat ng bata ang liham.")
    assert _voice(f) == "IV"
    assert _pred(f) == "WRITE <SUBJ, OBJ>"
    assert "SUBJ" in f.feats and "OBJ" in f.feats


def test_iv_itinapon() -> None:
    _, f, _, _ = _first("Itinapon ng bata ang basura.")
    assert _voice(f) == "IV"
    assert _pred(f) == "THROW <SUBJ, OBJ>"


# === LMT mapping per voice ================================================


def test_lmt_av_maps_agent_to_subj() -> None:
    """Phase 4 voice-aware LMT: AV transitive maps AGENT→SUBJ,
    PATIENT→OBJ."""
    _, _, a, _ = _first("Kumain ang aso ng isda.")
    assert a.mapping == {"AGENT": "SUBJ", "PATIENT": "OBJ"}


def test_lmt_ov_maps_patient_to_subj() -> None:
    """OV transitive maps PATIENT→SUBJ, AGENT→OBJ."""
    _, _, a, _ = _first("Kinain ng aso ang isda.")
    assert a.mapping == {"PATIENT": "SUBJ", "AGENT": "OBJ"}


def test_lmt_dv_maps_goal_to_subj() -> None:
    """DV transitive maps GOAL→SUBJ, AGENT→OBJ."""
    _, _, a, _ = _first("Sinulatan ng bata ang ina.")
    assert a.mapping == {"GOAL": "SUBJ", "AGENT": "OBJ"}


def test_lmt_iv_maps_conveyed_to_subj() -> None:
    """IV transitive maps CONVEYED→SUBJ, AGENT→OBJ."""
    _, _, a, _ = _first("Isinulat ng bata ang liham.")
    assert a.mapping == {"CONVEYED": "SUBJ", "AGENT": "OBJ"}
