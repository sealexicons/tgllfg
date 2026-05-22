# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 7a.A: NP-internal ``mga`` plural marker (§18.1.1 #11).

Three case-parallel rules added to ``cfg/nominal.py`` admit
``CASE-MARKER + PART[mga] + N`` and lift ``NUM=PL`` onto the
matrix NP. The defining equation ``(↑ NUM) = 'PL'`` composes
with the Phase 6.H floated-Q DUAL-rule's constraining equation
``(↑ SUBJ NUM) =c 'PL'`` — closing the canonical
``Kumain ang mga bata pareho.`` case probed but not closed
during Phase 6.H.

Closes §18.1.1 #11 (deferral promoted in Phase 6.H closing
notes from informal stress-test gap to formal §18.1 inventory).
"""

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _get_subj(s: str) -> FStructure | None:
    rs = parse_text(s)
    if not rs:
        return None
    v = rs[0][1].feats.get("SUBJ")
    return v if isinstance(v, FStructure) else None


def _get_obj(s: str) -> FStructure | None:
    rs = parse_text(s)
    if not rs:
        return None
    v = rs[0][1].feats.get("OBJ")
    return v if isinstance(v, FStructure) else None


def _has_dual_q_reading(parses: list, q_lemma: str) -> bool:
    """Match Phase 6.H floated-Q test helper: True if any parse has a
    DUAL-Q with ``LEMMA == q_lemma`` in the matrix ADJ set."""
    for _ct, fs, _astr, _diags in parses:
        adj = fs.feats.get("ADJ")
        if not adj:
            continue
        for member in adj:
            if not isinstance(member, FStructure):
                continue
            if (
                member.feats.get("LEMMA") == q_lemma
                and member.feats.get("DUAL") is True
            ):
                return True
    return False


# === Basic NOM / GEN / DAT mga-NP parses ==============================


class TestMgaNPBasicCases:
    """The three case-parallel rules accept ``mga + N`` after the
    case marker and lift ``NUM=PL`` onto the matrix NP."""

    def test_nom_subj_mga_bata(self) -> None:
        # AV intransitive: ``Kumain ang mga bata.`` "The children ate."
        subj = _get_subj("Kumain ang mga bata.")
        assert subj is not None
        assert subj.feats.get("NUM") == "PL"

    def test_nom_subj_mga_aso(self) -> None:
        # AV intransitive with a different N to confirm rule
        # generalizes beyond a single lemma.
        subj = _get_subj("Tumakbo ang mga aso.")
        assert subj is not None
        assert subj.feats.get("NUM") == "PL"

    def test_gen_obj_mga_aklat(self) -> None:
        # AV transitive: ``Bumili ako ng mga aklat.`` "I bought books."
        obj = _get_obj("Bumili ako ng mga aklat.")
        assert obj is not None
        assert obj.feats.get("NUM") == "PL"

    def test_gen_obj_mga_isda(self) -> None:
        # ``Kumain ang aso ng mga isda.`` "The dog ate fish."
        obj = _get_obj("Kumain ang aso ng mga isda.")
        assert obj is not None
        assert obj.feats.get("NUM") == "PL"

    def test_dat_mga_bahay_adjunct(self) -> None:
        # AV motion: ``Pumunta ako sa mga bahay.`` "I went to the houses."
        # The DAT NP lands in ADJUNCT (verified via probe); the new
        # rule lifts NUM=PL onto it.
        parses = parse_text("Pumunta ako sa mga bahay.")
        assert parses, "DAT mga-NP should parse"
        found_pl_dat = False
        for _ct, fs, _astr, _diags in parses:
            adj = fs.feats.get("ADJUNCT")
            if not isinstance(adj, (set, frozenset, list)):
                continue
            for m in adj:
                if (
                    isinstance(m, FStructure)
                    and m.feats.get("LEMMA") == "bahay"
                    and m.feats.get("CASE") == "DAT"
                    and m.feats.get("NUM") == "PL"
                ):
                    found_pl_dat = True
                    break
        assert found_pl_dat, (
            "DAT mga-NP ADJUNCT should carry NUM=PL from the new rule"
        )


# === Floated-Q interaction (Phase 6.H closure) ========================


class TestMgaFloatedQ:
    """The new rule's ``(↑ NUM) = 'PL'`` defining equation feeds the
    Phase 6.H DUAL-Q variant's ``(↑ SUBJ NUM) =c 'PL'`` constraining
    equation — closing the canonical case probed but not closed
    during Phase 6.H."""

    def test_mga_bata_pareho(self) -> None:
        # The canonical case the plan-of-record §3.1 calls out.
        parses = parse_text("Kumain ang mga bata pareho.")
        assert _has_dual_q_reading(parses, "pareho"), (
            "``Kumain ang mga bata pareho.`` should admit the dual-Q "
            "reading via Phase 6.H floated-Q rule with NUM=PL from "
            "the Phase 7a.A mga-NP rule"
        )

    def test_mga_bata_kapwa(self) -> None:
        # Parallel test with kapwa.
        parses = parse_text("Kumain ang mga bata kapwa.")
        assert _has_dual_q_reading(parses, "kapwa")


# === Approximator coexistence (intentional ambiguity for time Ns) =====


class TestMgaApproximatorCoexistence:
    """For time-class Ns the Phase 5f time-approximator rule
    (``N → PART N[SEM_CLASS=TIME]`` with APPROX=true) and the new
    Phase 7a.A NP-internal rule both fire, producing distinct
    readings in the same surface. The time-approximator was tested
    in ``test_mga_approximation.py`` (Phase 5f Commit 14); this
    test pins the coexistence: both paths produce ADJUNCT NPs for
    ``Pumunta ako sa mga alasotso.`` but with different feats —
    NUM=PL (new rule) vs APPROX=true (existing rule)."""

    def test_sa_mga_alasotso_both_readings(self) -> None:
        # ``Pumunta ako sa mga alasotso.`` "I went at (around)
        # eight (o'clock)." Phase 5f time-approximator path:
        # ADJUNCT with APPROX=true. Phase 7a.A new NP rule path:
        # ADJUNCT with NUM=PL.
        parses = parse_text(
            "Pumunta ako sa mga alasotso.", n_best=20
        )
        readings_pl = 0
        readings_approx = 0
        for _ct, fs, _astr, _diags in parses:
            adj = fs.feats.get("ADJUNCT")
            if not isinstance(adj, (set, frozenset, list)):
                continue
            for m in adj:
                if not isinstance(m, FStructure):
                    continue
                if m.feats.get("LEMMA") != "alasotso":
                    continue
                if m.feats.get("NUM") == "PL":
                    readings_pl += 1
                if m.feats.get("APPROX") is True:
                    readings_approx += 1
        assert readings_pl >= 1, (
            "Phase 7a.A NP rule should produce PL reading on the "
            "ADJUNCT NP"
        )
        assert readings_approx >= 1, (
            "Phase 5f time-approximator should still produce APPROX "
            "reading on the ADJUNCT NP (no regression)"
        )


# === Cardinal-approximator path (no double-firing for NUM heads) ======


class TestMgaCardinalApproximatorPath:
    """For cardinal NUMs the new Phase 7a.A rule does NOT fire (its
    ↓3 expects N, not NUM); only the Phase 5f cardinal-approximator
    path fires, producing CARDINAL_VALUE + APPROX on the matrix NP."""

    def test_mga_sampung_aklat_approximator(self) -> None:
        # ``Bumili ako ng mga sampung aklat.`` "I bought about ten
        # books." Parses via cardinal-approximator: ``mga sampu`` →
        # NUM[CARDINAL, APPROX=true]; then linker + N → NP with
        # CARDINAL_VALUE=10 + APPROX=true.
        obj = _get_obj("Bumili ako ng mga sampung aklat.")
        assert obj is not None
        assert obj.feats.get("CARDINAL_VALUE") == "10"
        assert obj.feats.get("APPROX") is True


# === Simple-NP regression (negative-constraint sanity) ================


class TestSimpleNPUnchanged:
    """The new 3-daughter rule does not perturb the existing simple
    NP-from-DET+N and cardinal-NP rules (the negative-existential
    guards on the new rule mirror the simple-NP exclusions)."""

    def test_no_mga_simple_np(self) -> None:
        # ``Kumain ang bata.`` (no mga) — simple NP path unaffected.
        parses = parse_text("Kumain ang bata.")
        assert parses

    def test_no_mga_cardinal_np(self) -> None:
        # ``Bumili ako ng isang aklat.`` (no mga, cardinal modifier)
        # — cardinal NP path unaffected.
        obj = _get_obj("Bumili ako ng isang aklat.")
        assert obj is not None
        assert obj.feats.get("CARDINAL_VALUE") == "1"
