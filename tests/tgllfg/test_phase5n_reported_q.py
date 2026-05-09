"""Phase 5n.A Commit 29 — ASK-class reported-Q (§18 L90.2 + L92).

Closes §18 L90 part 2 of 2. Positive-parse assertions for the 18
corpus fixtures from Phase 5n.A Commit 28; lifts the misanalysis
+ 0-parse pins on the canonical reported-Q sentence
``Tinanong niya kung sino ang kumain.`` and parallel forms.

Two new clause rules in ``cfg/control.py``:

* OV reported-Q:  S → V[VOICE=OV, ASK_CLASS=YES] NP[CASE=GEN]
                    S_INTERROG_COMP
                    (↑ OBJ-AGENT) = ↓2
                    (↑ SUBJ) = ↓3
* AV reported-Q:  S → V[VOICE=AV, ASK_CLASS=YES] NP[CASE=NOM]
                    S_INTERROG_COMP
                    (↑ SUBJ) = ↓2
                    (↑ OBJ) = ↓3

The OV pivot binds the embedded clause to SUBJ (parallel to the
Phase 5n.A Commit 27 SAY-class OV pattern). The AV pivot binds
the asker to SUBJ and the embedded clause to OBJ (the THEME of
asking, mapped to OBJ in AV).

Companion change in ``src/tgllfg/cfg/clitic.py`` —
the kita-fusion rules gained ``(↓2 KITA) =c 'YES'`` constraining
equations to close a non-conflict-matcher leak that was producing
spurious S over V + non-KITA-PRON spans (e.g., ``Tinanong niya``
parsing as a complete S, then triggering the Phase 5l COND-
adjunct misanalysis for ``Tinanong niya kung sino ang kumain.``).

The companion change required quoting the ``KITA`` feat value in
``data/tgl/pronouns.yaml`` (``KITA: "YES"``) so it parses as the
literal string ``YES`` rather than the YAML 1.1 boolean ``True``,
matching the convention used by ``MODAL: "YES"`` /
``ASK_CLASS: "YES"`` and the ``=c 'YES'`` constraining-equation
syntax.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _has_feat_value(fs, feat: str, value: str, _seen=None) -> bool:
    """Walk f-structure recursively; return True iff some node
    carries ``feat = value``."""
    if _seen is None:
        _seen = set()
    if id(fs) in _seen:
        return False
    _seen.add(id(fs))
    if not hasattr(fs, "feats"):
        return False
    if fs.feats.get(feat) == value:
        return True
    for v in fs.feats.values():
        if hasattr(v, "feats") and _has_feat_value(v, feat, value, _seen):
            return True
        elif isinstance(v, (list, tuple, set, frozenset)):
            for el in v:
                if hasattr(el, "feats") and _has_feat_value(
                    el, feat, value, _seen
                ):
                    return True
    return False


# === Canonical sentence ============================================


class TestCanonicalSentence:
    """``Tinanong niya kung sino ang kumain.`` — the canonical
    reported-Q sentence, parses with the kung-S as a
    COMP_TYPE=INTERROG complement bound to the matrix V's SUBJ
    slot (OV pivot)."""

    def test_canonical_parses(self) -> None:
        parses = parse_text("Tinanong niya kung sino ang kumain.")
        assert len(parses) >= 1
        # The new rule's parse carries COMP_TYPE=INTERROG on the
        # SUBJ (the embedded kung-clause). Find that parse.
        interrog_parses = [
            p for p in parses
            if _has_feat_value(p[1], "COMP_TYPE", "INTERROG")
        ]
        assert len(interrog_parses) >= 1
        _ct, fs, _astr, _diags = interrog_parses[0]
        assert fs.feats.get("PRED") == "TANONG <SUBJ, OBJ-AGENT>"
        assert fs.feats.get("VOICE") == "OV"
        # SUBJ is the embedded kung-clause with COMP_TYPE=INTERROG.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COMP_TYPE") == "INTERROG"
        # OBJ-AGENT is the actor PRON (niya, GEN clitic).
        oa = fs.feats.get("OBJ-AGENT")
        assert oa is not None
        assert oa.feats.get("CASE") == "GEN"


# === Corpus parametrization (mirrors Commit 28's 18 fixtures) ======


_OV_FIXTURES = [
    "Tinanong niya kung sino ang kumain.",
    "Tinanong niya kung ano ang kinain ni Maria.",
    "Tinanong niya kung saan pumunta si Maria.",
    "Tinanong niya kung kailan pumunta si Maria.",
    "Tinanong niya kung bakit kumain si Maria.",
    "Tinanong niya kung paano kumain si Maria.",
    "Tinatanong niya kung sino ang kumain.",
    "Tinatanong niya kung saan pumunta si Maria.",
    "Tatanungin niya kung sino ang kumain.",
    "Tatanungin niya kung kailan pumunta si Maria.",
    "Tinanong ng lalaki kung sino ang kumain.",
]

_AV_FIXTURES = [
    "Nagtanong siya kung sino ang kumain.",
    "Nagtanong siya kung saan pumunta si Maria.",
    "Nagtatanong siya kung sino ang kumain.",
    "Nagtatanong siya kung bakit kumain si Maria.",
    "Magtatanong siya kung sino ang kumain.",
    "Magtatanong siya kung paano kumain si Maria.",
    "Nagtanong si Maria kung saan pumunta si Pedro.",
]


class TestOVCorpusFixtures:
    """The 11 OV-voice corpus fixtures parse with PRED='TANONG
    <SUBJ, OBJ-AGENT>' and SUBJ binding the kung-S COMP_TYPE=INTERROG
    complement (the asked-thing). Closes Phase 5n.A Commit 28's
    ``test_phase5n_corpus_misanalysis_pin`` tripwire."""

    @pytest.mark.parametrize("sentence", _OV_FIXTURES)
    def test_ov_parses_with_interrog_subj(self, sentence: str) -> None:
        parses = parse_text(sentence)
        ov_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "TANONG <SUBJ, OBJ-AGENT>"
            and p[1].feats.get("VOICE") == "OV"
            and _has_feat_value(p[1], "COMP_TYPE", "INTERROG")
        ]
        assert len(ov_parses) >= 1, (
            f"{sentence!r}: expected an OV TANONG parse with "
            "COMP_TYPE=INTERROG"
        )


class TestAVCorpusFixtures:
    """The 7 AV-voice corpus fixtures parse with PRED='TANONG
    <SUBJ, OBJ>' and OBJ binding the kung-S COMP_TYPE=INTERROG
    complement. Closes Phase 5n.A Commit 28's
    ``test_phase5n_av_or_full_np_zero_parse`` tripwire."""

    @pytest.mark.parametrize("sentence", _AV_FIXTURES)
    def test_av_parses_with_interrog_obj(self, sentence: str) -> None:
        parses = parse_text(sentence)
        av_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "TANONG <SUBJ, OBJ>"
            and p[1].feats.get("VOICE") == "AV"
            and _has_feat_value(p[1], "COMP_TYPE", "INTERROG")
        ]
        assert len(av_parses) >= 1, (
            f"{sentence!r}: expected an AV TANONG parse with "
            "COMP_TYPE=INTERROG"
        )


# === COND-misanalysis no longer fires =============================


class TestNoCondMisanalysis:
    """The Phase 5l COND-adjunct path no longer fires on
    reported-Q surfaces. Without the kita-fusion's bogus S over
    ``Tinanong niya``, the COND-adjunct rule has no matrix S to
    attach to, so the misanalysis is gone."""

    @pytest.mark.parametrize("sentence", _OV_FIXTURES)
    def test_no_cond_adjunct_in_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            adjuncts = fs.feats.get("ADJUNCT")
            if adjuncts is None:
                continue
            for a in adjuncts:
                assert a.feats.get("SUBORD_TYPE") != "COND", (
                    f"{sentence!r} unexpectedly carries a "
                    "COND-adjunct — kita-fusion leak may have "
                    "regressed"
                )


# === KNOW-class baseline regression (Phase 5i) ====================


class TestKnowClassBaseline:
    """The Phase 5i ``Alam ko kung sino ang kumain.`` path — the
    KNOW-class indirect-Q complement — continues to parse after
    the Commit 29 ASK-class additions. The KNOW rule's CTRL_CLASS=KNOW
    gate remains distinct from the new ASK_CLASS=YES gate."""

    def test_alam_ko_still_parses(self) -> None:
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "KNOW <SUBJ, COMP>"
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"


# === kita-fusion regression ========================================


class TestKitaFusionRegression:
    """The kita-fusion rule continues to fire on legitimate
    ``kita`` input after the Commit 29 ``(↓2 KITA) =c 'YES'``
    tightening."""

    def test_kinain_kita_still_parses(self) -> None:
        parses = parse_text("Kinain kita.")
        assert len(parses) >= 1

    def test_pinakain_kita_ng_kanin_still_parses(self) -> None:
        parses = parse_text("Pinakain kita ng kanin.")
        assert len(parses) >= 1

    def test_tinanong_niya_alone_no_longer_parses(self) -> None:
        """``Tinanong niya.`` (no SUBJ) no longer parses via the
        kita-fusion's bogus path — the constraining ``(↓2 KITA)
        =c 'YES'`` rejects ``niya`` as a non-KITA PRON."""
        parses = parse_text("Tinanong niya.")
        # The OV-2NP frame requires NOM-NP SUBJ; without it, no
        # complete parse exists.
        assert len(parses) == 0
