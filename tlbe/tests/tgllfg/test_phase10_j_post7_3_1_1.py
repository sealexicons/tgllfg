# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.3.1.1: bare modal+OV imperative.

Adds two chart rules in cfg/clause.py for the bare V[MODAL]+V[OV]
imperative construction (deferred from post-7.3.1):

- ``S → V[CTRL_CLASS=MODAL] V[VOICE=OV]``
  — bare imperative (``Dapat gawin.`` "(It) should be done.")
- ``S → V[CTRL_CLASS=MODAL] V[VOICE=OV] NP[CASE=GEN]``
  — with GEN-AGENT (``Dapat gawin natin.`` "We should do (it).")

Both project the V[MODAL]'s f-structure onto matrix via ``(↑) = ↓1``
(carrying PRED template like ``DAPAT <SUBJ, XCOMP>``), with XCOMP
bound to the V[OV] daughter (``(↑ XCOMP) = ↓2``). XCOMP-completeness
is satisfied by:

- Matrix SUBJ = PRO (impersonal)
- XCOMP SUBJ shares matrix SUBJ (raising-style control)
- XCOMP OBJ-AGENT = PRO (bare variant) or = GEN-NP (with-experiencer
  variant)

Tagalog OV verbs carry PRED templates with SUBJ + OBJ-AGENT slots
(e.g., ``gawin`` = ``MAKE <SUBJ, OBJ-AGENT>``); the SUBJ slot is the
PATIENT/PIVOT and OBJ-AGENT is the agent.

Matrix MODAL_IMPER=true is set as an analytical marker distinguishing
this construction from the canonical Phase 5j modal-control rules
(which require a NOM-pivot or full S_XCOMP).

Audit-absent in waves 1-5 (per post-7.3.1 survey).
"""

from tgllfg.core.pipeline import parse_text


class TestBareModalOv:
    """post-7.3.1.1: V[CTRL_CLASS=MODAL] + V[VOICE=OV] bare imperative."""

    def test_dapat_gawin_bare(self) -> None:
        """``Dapat gawin.`` "(It) should be done." — bare modal+OV
        imperative without NOM-pivot."""
        parses = parse_text("Dapat gawin.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "DAPAT <SUBJ, XCOMP>"
        assert fs.feats.get("MODAL_IMPER") is True
        # Matrix SUBJ is impersonal PRO
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("PRED") == "PRO"
        # XCOMP is the gawin clause
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        assert xcomp.feats.get("PRED") == "MAKE <SUBJ, OBJ-AGENT>"
        # XCOMP SUBJ shares matrix SUBJ (control)
        xcomp_subj = xcomp.feats.get("SUBJ")
        assert xcomp_subj is not None
        # XCOMP OBJ-AGENT is PRO (no overt GEN)
        obj_agent = xcomp.feats.get("OBJ-AGENT")
        assert obj_agent is not None
        assert obj_agent.feats.get("PRED") == "PRO"

    def test_puwede_gawin_bare(self) -> None:
        """``Puwede gawin.`` — different modal, same shape."""
        parses = parse_text("Puwede gawin.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "PUWEDE <SUBJ, XCOMP>"
        assert fs.feats.get("MODAL_IMPER") is True


class TestModalOvWithAgent:
    """post-7.3.1.1: bare modal+OV with GEN-AGENT experiencer."""

    def test_dapat_gawin_natin(self) -> None:
        """``Dapat gawin natin.`` "We should do (it)." — GEN-PRON
        is the AGENT."""
        parses = parse_text("Dapat gawin natin.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "DAPAT <SUBJ, XCOMP>"
        assert fs.feats.get("MODAL_IMPER") is True
        # XCOMP OBJ-AGENT bound to natin (GEN-PRON)
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        obj_agent = xcomp.feats.get("OBJ-AGENT")
        assert obj_agent is not None
        # natin is 1pl-incl GEN
        assert obj_agent.feats.get("CASE") == "GEN"

    def test_puwede_gawin_natin(self) -> None:
        """``Puwede gawin natin.`` "We can do (it)." — different
        modal, same shape."""
        parses = parse_text("Puwede gawin natin.", n_best=2)
        assert len(parses) >= 1


class TestAntiRegression:
    """post-7.3.1.1 anti-regression: the new rules don't break the
    canonical modal-control rules (control.py:489–600) which handle
    NOM-pivot / full S_XCOMP variants, nor the standalone-modal rule
    (control.py:476) which handles ``Hindi puwede.``-style sentences.
    """

    def test_modal_with_nom_pivot_unchanged(self) -> None:
        """``Dapat gawin ito.`` (NOM-pivot) and ``Dapat gawin natin
        ito.`` (GEN-AGENT + NOM-pivot) still parse via the existing
        Phase 5j Commit 7 / Phase 7a.E modal-control rules — the
        new bare-OV rule shouldn't conflict because the chart's
        daughter sequence is different (3-daughter NP[NOM] vs
        2-daughter bare or 3-daughter NP[GEN])."""
        for s in (
            "Dapat gawin ito.",
            "Dapat gawin natin ito.",
        ):
            parses = parse_text(s, n_best=2)
            assert len(parses) >= 1, f"canonical modal regressed: {s!r}"

    def test_standalone_modal_unchanged(self) -> None:
        """``Hindi puwede.`` (standalone modal) still parses."""
        parses = parse_text("Hindi puwede.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # The standalone-modal path: PRED = PUWEDE
        # (no MODAL_IMPER since that's a post-7.3.1.1 marker for
        # the bare-OV path only)
        assert fs.feats.get("PRED") == "PUWEDE <SUBJ, XCOMP>"
