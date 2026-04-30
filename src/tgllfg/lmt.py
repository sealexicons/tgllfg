# tgllfg/lmt.py

"""Phase 4 voice-aware role-to-GF heuristic.

This is the §4.2-vintage LMT — a hand-coded mapping per voice rather
than the Bresnan–Kanerva [±r, ±o] feature system. Phase 5 replaces
this with a real LMT that derives the mapping from the verb's
intrinsic role classification plus voice morphology.

The mapping reads ``f.feats["VOICE"]`` to pick the correct
role-to-GF assignment. For non-AV voices the *ng*-non-pivot is OBJ
(``docs/analysis-choices.md`` "ng-non-pivot in transitive non-AV →
OBJ"). The role labels here are placeholders chosen by voice:

* AV — ``[AGENT, PATIENT]``: AGENT → SUBJ, PATIENT → OBJ.
* OV — ``[AGENT, PATIENT]``: PATIENT → SUBJ, AGENT → OBJ.
* DV — ``[AGENT, GOAL]``:    GOAL → SUBJ, AGENT → OBJ.
* IV — ``[AGENT, CONVEYED]``: CONVEYED → SUBJ, AGENT → OBJ.

Intransitive (no OBJ) — ``[ACTOR]``: ACTOR → SUBJ.
"""

from __future__ import annotations

from .common import AStructure, FStructure


def apply_lmt(f: FStructure) -> AStructure:
    pred = (f.feats.get("PRED") or "").split()[0]  # "EAT <SUBJ, OBJ>" -> "EAT"
    voice = f.feats.get("VOICE")
    has_obj = "OBJ" in f.feats

    if not has_obj:
        return AStructure(pred=pred, roles=["ACTOR"], mapping={"ACTOR": "SUBJ"})

    if voice == "AV":
        return AStructure(
            pred=pred,
            roles=["AGENT", "PATIENT"],
            mapping={"AGENT": "SUBJ", "PATIENT": "OBJ"},
        )
    if voice == "OV":
        return AStructure(
            pred=pred,
            roles=["AGENT", "PATIENT"],
            mapping={"PATIENT": "SUBJ", "AGENT": "OBJ"},
        )
    if voice == "DV":
        return AStructure(
            pred=pred,
            roles=["AGENT", "GOAL"],
            mapping={"GOAL": "SUBJ", "AGENT": "OBJ"},
        )
    if voice == "IV":
        return AStructure(
            pred=pred,
            roles=["AGENT", "CONVEYED"],
            mapping={"CONVEYED": "SUBJ", "AGENT": "OBJ"},
        )

    # Voice-less or unknown voice: fall back to the OV-shaped mapping
    # (this preserves Phase 1 behaviour for synthetic test fixtures
    # that don't set VOICE).
    return AStructure(
        pred=pred,
        roles=["AGENT", "PATIENT"],
        mapping={"PATIENT": "SUBJ", "AGENT": "OBJ"},
    )
