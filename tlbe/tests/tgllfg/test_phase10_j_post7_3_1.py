# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.3.1: Q-existential-possessive + dapat-V-cluster.

Adds five chart rules in cfg/clause.py covering the
Q-existential-possessive construction family with internal-clitic
possessor (parallel to Phase 5j Commit 5b's may/wala HAVE family
which handles the PART[EXISTENTIAL] predicate slot):

Q-existential family (Q QUANT — marami / kaunti / ilan / etc.):
- ``S → Q PRON[CASE=NOM] PART[LINK=NG|NA] N``        — N possessum
- ``S → Q PRON[CASE=NOM] PART[LINK=NG|NA] V``        — V possessum
  (V as deverbal nominalization — "many to-do")
- ``S → Q PRON[CASE=NOM] PART[LINK=NG|NA] V[MODAL] V[OV]``
  — modal+OV V-cluster possessum

Mayroon-existential family (PART[EXISTENTIAL]):
- ``S → PART[EXISTENTIAL] PRON[CASE=NOM] PART[LINK=NG|NA] V``
- ``S → PART[EXISTENTIAL] PRON[CASE=NOM] PART[LINK=NG|NA] V[MODAL] V[OV]``

All three Q-family variants gate ``¬ (↓1 DUAL)`` to exclude the
DUAL-Q ``kapwa`` / ``pareho`` (QUANT=BOTH) which carry their own
DUAL-modifier clause type (test_q_clitic_predicate) — without the
gate, the rule fires on ``Kapwa kayong kumain.`` etc. and produces
a spurious EXIST parse that competes with the canonical DUAL reading.

Closes the alalaong-2 exemplar (``Alalaong baga, marami pa tayong
dapat gawin.``) — the post-7.3 deferred residue. Also closes the
parallel mayroon V-variant gap (``Mayroon akong gagawin.``) that
the existing Phase 5j Commit 5b HAVE rules didn't cover.

Audit-attested closures: TBD (multi-wave audit prerequisite).
"""

from tgllfg.core.pipeline import parse_text


class TestQExistentialPossessiveN:
    """post-7.3.1 (a): Q + PRON[CASE=NOM] + LINK + N."""

    def test_marami_akong_aklat(self) -> None:
        """``Marami akong aklat.`` "I have many books." Canonical
        Q-existential possessive with N possessum."""
        parses = parse_text("Marami akong aklat.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("HAVE") is True
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("QUANT") == "MANY"
        # PRON-possessor binds to SUBJ POSSESSOR (ako = 1SG NOM-clitic)
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        possessor = subj.feats.get("POSSESSOR")
        assert possessor is not None
        assert possessor.feats.get("CASE") == "NOM"
        assert possessor.feats.get("is_clitic") is True
        assert possessor.feats.get("NUM") == "SG"

    def test_marami_pron_variants(self) -> None:
        """Multiple PRON-NOM clitics close — ako/siya/tayo/sila."""
        for s in (
            "Marami akong aklat.",
            "Marami siyang aklat.",
            "Marami tayong aklat.",
            "Marami silang aklat.",
            "Marami kayong aklat.",
        ):
            parses = parse_text(s, n_best=2)
            assert len(parses) >= 1, f"failed: {s!r}"


class TestQExistentialPossessiveV:
    """post-7.3.1 (b): Q + PRON[CASE=NOM] + LINK + V."""

    def test_marami_akong_gagawin(self) -> None:
        """``Marami akong gagawin.`` "I have many to do" — V[OV,CTPL]
        as deverbal nominalization."""
        parses = parse_text("Marami akong gagawin.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("NOMINALIZED") is True
        # V_VOICE / V_ASPECT signature from the V daughter
        assert subj.feats.get("V_VOICE") == "OV"
        assert subj.feats.get("V_ASPECT") == "CTPL"


class TestQExistentialPossessiveModalOv:
    """post-7.3.1 (c): Q + PRON[CASE=NOM] + LINK + V[MODAL] + V[OV]
    — closes the alalaong-2 inner clause."""

    def test_marami_pa_tayong_dapat_gawin(self) -> None:
        """The alalaong-2 inner clause closes."""
        parses = parse_text(
            "Marami pa tayong dapat gawin.", n_best=2
        )
        assert len(parses) >= 1

    def test_alalaong_2_full_exemplar(self) -> None:
        """The full alalaong-2 exemplar (REFORM marker + comma + Q-
        existential-possessive inner clause)."""
        s = "Alalaong baga, marami pa tayong dapat gawin."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # Matrix REFORM marker
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None
        types = {a.feats.get("DISCOURSE") for a in adj}
        assert "REFORM" in types
        # Matrix EXIST predicate (post-comma half)
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("HAVE") is True


class TestQExistentialNoPossessor:
    """post-7.3.1: Q + LINK + V (no possessor) — parallel to the
    existing ``Q PART[LINK] N`` rule (line 3793) but with V or
    V-cluster complement. Closes ``Maraming dapat gawin.`` and
    ``Maraming gagawin.`` from the post-7.3.1 PoR list.
    """

    def test_maraming_gagawin(self) -> None:
        """``Maraming gagawin.`` "There is much to do." (Q-LINK + V)"""
        parses = parse_text("Maraming gagawin.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("QUANT") == "MANY"

    def test_maraming_dapat_gawin(self) -> None:
        """``Maraming dapat gawin.`` (Q-LINK + modal+OV cluster)"""
        parses = parse_text("Maraming dapat gawin.", n_best=2)
        assert len(parses) >= 1


class TestMayroonVPossessum:
    """post-7.3.1 mayroon V-variant: PART[EXISTENTIAL] + PRON + LINK + V.

    Sister rule to the Q-existential V-variant — closes the parallel
    gap in the Phase 5j Commit 5b HAVE family (which previously
    handled only N possessums via internal-clitic possessor).
    """

    def test_mayroon_akong_gagawin(self) -> None:
        """``Mayroon akong gagawin.`` "I have things to do" — the
        gap user surfaced when post-7.3.1 first probed; closed by the
        sister rule."""
        parses = parse_text("Mayroon akong gagawin.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("HAVE") is True

    def test_mayroon_modal_ov_cluster(self) -> None:
        """Modal+OV cluster variant."""
        parses = parse_text(
            "Mayroon akong dapat gawin.", n_best=2
        )
        assert len(parses) >= 1


class TestDualQAntiRegression:
    """post-7.3.1 anti-regression: DUAL Q (kapwa / pareho) does NOT
    fire as existential. Without the ``¬ (↓1 DUAL)`` gate, the new
    Q-existential rules would produce a spurious EXIST parse for
    ``Kapwa kayong kumain.`` etc., overriding the canonical DUAL
    reading (test_q_clitic_predicate).
    """

    def test_kapwa_pareho_intransitive_preserves_dual(self) -> None:
        """Canonical reading: PRED=EAT, not EXIST."""
        for s in (
            "Kapwa kayong kumain.",
            "Kapwa silang kumain.",
            "Pareho tayong kumain.",
            "Pareho silang kumain.",
            "Pareho kaming kumain.",
        ):
            parses = parse_text(s, n_best=3)
            assert len(parses) >= 1, f"no parse for {s!r}"
            # The canonical reading must be among the parses
            preds = {p[1].feats.get("PRED") for p in parses}
            assert "EAT <SUBJ>" in preds, (
                f"DUAL Q lost canonical PRED reading on {s!r}; "
                f"got PREDs={preds}"
            )
