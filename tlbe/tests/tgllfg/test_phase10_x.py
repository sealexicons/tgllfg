# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.X: shared-NOM V-V-V coord under N-predicate control.

Closes the last remaining wave-1 ZPF — PAMILYA/sent-8:

    Sa kabilang dako ay tungkulin niyang pakainin, bigyan ng
    matitirhan at pag-aralin ang mga miyembro ng kanyang pamilya.

The three V-conjuncts (``pakainin`` / ``bigyan ng matitirhan`` /
``pag-aralin``) share the matrix ``niyang`` (GEN-clitic, the matrix
SUBJ → routed via REL-PRO as the typed-actor gap inside each V) AND
the single ``ang mga miyembro ng kanyang pamilya`` NOM-NP (SUBJ of
each V's clause).

The Phase 10.J.post-12.11 ``S_XCOMP`` coord rules already chain
``REL-PRO`` across conjuncts — but every non-AV ``S_XCOMP`` rule in
:mod:`tgllfg.cfg.control` bundles an ``NP[CASE=NOM]`` pivot daughter
inside the body, so the post-12.11 path only fires when each
conjunct has its OWN NOM-NP. Phase 10.X adds a bare-V
``S_XCOMP_BARE`` non-terminal + coord variants + shared-pivot wrap
``S_XCOMP → S_XCOMP_BARE_COORD NP[CASE=NOM]`` so the single right-
edge NOM-NP can serve as the shared SUBJ for all conjuncts.

Net audit-corpus delta: **wave1 121/122 → 122/122 (+1; PAMILYA/
sent-8). All other waves 0 delta, 0 regressions. XWAVE 1936 → 1937.**

All wave-1 ZPFs are now closed (1/122 → 0/122).
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === PAMILYA/sent-8 + shape variants =====================================

class TestPamilyaSent8Closure:
    """Phase 10.X closes the canonical wave-1 ZPF PAMILYA/sent-8 and
    its 5 substructure variants (full sentence + ay-stripped + each
    of 3 sub-V-conjuncts inside a binary coord)."""

    @pytest.mark.parametrize("sent", [
        # Full PAMILYA/sent-8 — the canonical wave-1 closure target.
        (
            "Sa kabilang dako ay tungkulin niyang pakainin, bigyan ng "
            "matitirhan at pag-aralin ang mga miyembro ng kanyang "
            "pamilya."
        ),
        # ay-stripped (pure V-V-V under control).
        (
            "Tungkulin niyang pakainin, bigyan ng matitirhan at "
            "pag-aralin ang mga miyembro ng kanyang pamilya."
        ),
        # Homogeneous V-V-V (no PP-complement on the middle V).
        "Tungkulin niyang pakainin, bigyan at pag-aralin ang mga bata.",
        # 3-conjunct with a simpler NOM-pivot.
        "Tungkulin niyang pakainin, bigyan at pag-aralin si Pedro.",
    ])
    def test_sent_8_variant_parses(self, sent: str) -> None:
        parses = parse_text(sent, n_best=2)
        assert len(parses) >= 1, (
            f"shared-NOM V-V-V coord under control should parse: "
            f"{sent!r}; got {len(parses)} parses"
        )


# === Shared-NOM binary V-V coord =========================================

class TestSharedNomBinaryCoord:
    """Phase 10.X binary variant: ``V1 at V2 ang/si NOM`` — two V-
    conjuncts share a single right-edge NOM-NP."""

    @pytest.mark.parametrize("sent", [
        # Two OV+CAUS=DIRECT conjuncts.
        "Tungkulin niyang pakainin at pag-aralin ang mga bata.",
        # OV+CAUS=NONE + OV+CAUS=DIRECT (aralin = teach; pag-aralin = cause to study).
        "Tungkulin niyang aralin at pag-aralin si Pedro.",
        # DV-with-PP + OV+CAUS=DIRECT (V2 has its own GEN theme).
        "Tungkulin niyang bigyan ng matitirhan at pag-aralin ang mga bata.",
        # OV + DV-with-PP (reversed order).
        "Tungkulin niyang pag-aralin at bigyan ng matitirhan ang mga bata.",
    ])
    def test_binary_shared_nom_parses(self, sent: str) -> None:
        parses = parse_text(sent, n_best=2)
        assert len(parses) >= 1, (
            f"binary shared-NOM V coord should parse: {sent!r}; "
            f"got {len(parses)} parses"
        )


# === Existing-path regression check ======================================

class TestExistingPathsUnchanged:
    """Phase 10.X must not regress the existing post-12.11 per-V
    NOM-NP path (each V has its OWN overt NOM-NP). The wrap rule
    requires the dedicated ``S_XCOMP_BARE_COORD`` non-terminal, so
    the bare-V rules don't fire on the per-V-NOM case."""

    @pytest.mark.parametrize("sent", [
        # Per-V NOM-NPs: each conjunct has its own si Maria / si Pedro.
        "Tungkulin niyang pakainin si Maria at pag-aralin si Pedro.",
        # Single-V (no coord at all): existing single-V S_XCOMP rule.
        "Tungkulin niyang pakainin ang mga bata.",
        "Tungkulin niyang bigyan ng matitirhan ang mga bata.",
        "Tungkulin niyang pag-aralin ang mga bata.",
        # AV intransitive coord (no NOM-NP, post-12.11 path).
        "Tungkulin niyang umalis at bumalik.",
    ])
    def test_existing_path_parses(self, sent: str) -> None:
        parses = parse_text(sent, n_best=2)
        assert len(parses) >= 1, (
            f"existing path regression: {sent!r}; "
            f"got {len(parses)} parses"
        )


# === F-structure check: CONJUNCTS / SUBJ / REL-PRO chaining ==============

class TestSharedNomFStructure:
    """Phase 10.X f-structure invariants: the shared NOM-pivot binds
    to ``XCOMP.SUBJ`` and propagates to every conjunct's ``SUBJ``;
    the matrix ``niyang`` (GEN-clitic, matrix SUBJ) routes through
    ``XCOMP.REL-PRO`` to each conjunct's typed-actor slot."""

    def test_binary_subj_propagates_to_each_conjunct(self) -> None:
        """In ``Tungkulin niyang pakainin at pag-aralin ang mga bata``,
        both V-conjuncts inside ``XCOMP.CONJUNCTS`` share the SUBJ
        slot bound to ``ang mga bata``."""
        sent = "Tungkulin niyang pakainin at pag-aralin ang mga bata."
        parses = parse_text(sent, n_best=2)
        assert parses
        _ctree, fs, _astr, _diags = parses[0]
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None, "XCOMP missing on matrix"
        conjs = xcomp.feats.get("CONJUNCTS")
        assert conjs is not None, "XCOMP.CONJUNCTS missing"
        # Both conjuncts must share the same SUBJ as the XCOMP coord.
        coord_subj = xcomp.feats.get("SUBJ")
        assert coord_subj is not None, "XCOMP.SUBJ missing"
        for c in conjs:
            c_subj = c.feats.get("SUBJ")
            assert c_subj is coord_subj, (
                f"conjunct SUBJ {c_subj!r} != coord SUBJ {coord_subj!r}"
            )

    def test_binary_rel_pro_chains_to_each_conjunct(self) -> None:
        """Each conjunct's ``REL-PRO`` (the typed-actor gap) unifies
        with the matrix ``XCOMP.REL-PRO`` (= matrix SUBJ niya)."""
        sent = "Tungkulin niyang pakainin at pag-aralin ang mga bata."
        parses = parse_text(sent, n_best=2)
        assert parses
        _ctree, fs, _astr, _diags = parses[0]
        # Matrix SUBJ = XCOMP REL-PRO per the N-pred control wrap.
        matrix_subj = fs.feats.get("SUBJ")
        xcomp = fs.feats.get("XCOMP")
        assert matrix_subj is not None and xcomp is not None
        rel_pro = xcomp.feats.get("REL-PRO")
        assert rel_pro is matrix_subj, (
            f"matrix SUBJ {matrix_subj!r} should be XCOMP REL-PRO "
            f"{rel_pro!r}"
        )
        # Each conjunct's REL-PRO must equal the coord REL-PRO.
        conjs = xcomp.feats.get("CONJUNCTS")
        for c in conjs:
            c_rel = c.feats.get("REL-PRO")
            assert c_rel is rel_pro, (
                f"conjunct REL-PRO {c_rel!r} != coord REL-PRO "
                f"{rel_pro!r}"
            )

    def test_ternary_subj_and_rel_pro_chain(self) -> None:
        """3-conjunct case: all three conjuncts share SUBJ + REL-PRO."""
        sent = (
            "Tungkulin niyang pakainin, bigyan at pag-aralin "
            "ang mga bata."
        )
        parses = parse_text(sent, n_best=2)
        assert parses
        _ctree, fs, _astr, _diags = parses[0]
        xcomp = fs.feats.get("XCOMP")
        assert xcomp is not None
        conjs = xcomp.feats.get("CONJUNCTS")
        assert len(conjs) == 3, f"expected 3 conjuncts; got {len(conjs)}"
        coord_subj = xcomp.feats.get("SUBJ")
        coord_rel = xcomp.feats.get("REL-PRO")
        for c in conjs:
            assert c.feats.get("SUBJ") is coord_subj
            assert c.feats.get("REL-PRO") is coord_rel
