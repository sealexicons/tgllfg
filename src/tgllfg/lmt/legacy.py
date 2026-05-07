# tgllfg/lmt/legacy.py

"""Phase 4 voice-aware role-to-GF heuristic — defensive fallback.

The §4.2-vintage LMT: a hand-coded role-to-GF mapping per voice,
read off ``f.feats["VOICE"]``. The Phase 5 Bresnan–Kanerva engine
(``tgllfg.lmt.principles``) supersedes this for normal parse output,
but ``apply_lmt(f)`` is preserved as the fallback used by
:func:`tgllfg.lmt.check.apply_lmt_with_check` when
:func:`find_matrix_lex_entry` can't locate a lex entry — e.g.,
synthetic test fixtures that construct an :class:`FStructure`
directly and pass empty ``lex_items``, or library callers outside
the parse pipeline.

For non-AV voices the *ng*-non-pivot is bare OBJ (matching the
Phase 4 grammar's f-structure binding rather than the Phase 5
engine's typed ``OBJ-θ`` upgrade). The role labels are
voice-determined defaults:

* AV — ``[AGENT, PATIENT]``: AGENT → SUBJ, PATIENT → OBJ.
* OV — ``[AGENT, PATIENT]``: PATIENT → SUBJ, AGENT → OBJ.
* DV — ``[AGENT, GOAL]``:    GOAL → SUBJ, AGENT → OBJ.
* IV — ``[AGENT, CONVEYED]``: CONVEYED → SUBJ, AGENT → OBJ.

Intransitive (no OBJ) — ``[ACTOR]``: ACTOR → SUBJ.
"""

from __future__ import annotations

from ..core.common import AStructure, FStructure


def apply_lmt(f: FStructure) -> AStructure:
    pred_raw = (f.feats.get("PRED") or "").split()
    if not pred_raw:
        # Phase 5k Commit 5: matrix coord-S f-structures carry no
        # PRED of their own (the predication lives on each conjunct
        # in CONJUNCTS). The legacy heuristic has nothing useful to
        # say about non-predicational f-structures; return an empty
        # AStructure so downstream code doesn't crash on
        # ``.split()[0]`` of an empty string.
        return AStructure(pred="", roles=[], mapping={})
    pred = pred_raw[0]  # "EAT <SUBJ, OBJ>" -> "EAT"
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
