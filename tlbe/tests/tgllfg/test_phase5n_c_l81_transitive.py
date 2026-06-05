# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C Commit 7.6 — L81 distributive-Q topic transitive variants.

Closes the L81 transitive deferral surfaced in user review of
Commit 7 (anti-deferral discipline per ``tgllfg-phase-5n-c.md``
§8). Adds three parallel rules to the Commit 7 intransitive rule,
mirroring the Phase 4 §7.1 canonical AV clause shapes
(``cfg/clause.py:48-58``):

- intransitive + DAT ADJUNCT
- transitive (GEN OBJ)
- transitive + DAT ADJUNCT

Surfaces (sample): ``Bawat bata, tumakbo sa parke.``,
``Bawat bata, kumain ng kanin.``,
``Bawat isa, bumili ng aklat.`` (Q + NUM via Commit 7.5),
``Bawat bata, kumain ng kanin sa parke.``

Reference: Schachter & Otanes 1972 §10; Phase 4 §7.1 AV clause
shapes (``cfg/clause.py:48-58``).
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Intransitive + DAT ADJUNCT =======================================


class TestIntransitivePlusDatAdjunct:
    """``Bawat bata, tumakbo sa parke.`` — universal-Q topic + comma
    + AV-intransitive verb + DAT ADJUNCT — parses with
    DISTRIB=YES."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Bawat bata, tumakbo sa parke.", "TAKBO <SUBJ>"),
        ("Bawat tao, tumakbo sa parke.",  "TAKBO <SUBJ>"),
        ("Kada bata, tumakbo sa parke.",  "TAKBO <SUBJ>"),
    ])
    def test_intrans_plus_dat(self, sentence: str, verb_pred: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"intrans + DAT distributive-Q topic should parse: "
            f"{sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISTRIB") is True
        assert fs.feats.get("PRED") == verb_pred
        # SUBJ is the topic-NP.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") is True
        # DAT is in ADJUNCT.
        assert fs.feats.get("ADJUNCT") is not None


# === Transitive (GEN OBJ) =============================================


class TestTransitiveGenObj:
    """``Bawat bata, kumain ng kanin.`` — universal-Q topic + comma
    + AV verb + GEN OBJ — parses with DISTRIB=YES + OBJ binding."""

    @pytest.mark.parametrize("sentence,verb_pred,obj_lemma", [
        ("Bawat bata, kumain ng kanin.",  "EAT <SUBJ, OBJ>",  "kanin"),
        ("Bawat tao, bumili ng aklat.",   "BUY <SUBJ, OBJ>",  "aklat"),
        ("Kada bata, kumain ng kanin.",   "EAT <SUBJ, OBJ>",  "kanin"),
    ])
    def test_trans_gen_obj(
        self, sentence: str, verb_pred: str, obj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"transitive distributive-Q topic should parse: "
            f"{sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISTRIB") is True
        assert fs.feats.get("PRED") == verb_pred
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") is True
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == obj_lemma


# === Transitive + DAT ADJUNCT =========================================


class TestTransitivePlusDatAdjunct:
    """``Bawat bata, kumain ng kanin sa parke.`` — full 5-daughter
    shape (topic + comma + V + GEN OBJ + DAT ADJUNCT) — parses with
    DISTRIB=YES, OBJ binding, and DAT in ADJUNCT."""

    @pytest.mark.parametrize("sentence,verb_pred,obj_lemma", [
        ("Bawat bata, kumain ng kanin sa parke.",
            "EAT <SUBJ, OBJ>", "kanin"),
        ("Bawat tao, bumili ng aklat sa parke.",
            "BUY <SUBJ, OBJ>", "aklat"),
    ])
    def test_trans_gen_obj_plus_dat(
        self, sentence: str, verb_pred: str, obj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"trans + DAT ADJUNCT distributive-Q topic should "
            f"parse: {sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISTRIB") is True
        assert fs.feats.get("PRED") == verb_pred
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == obj_lemma
        assert fs.feats.get("ADJUNCT") is not None


# === Q + NUM topic with transitive verb ===============================


class TestQNumTopicWithTransitive:
    """The Phase 5n.C Commit 7.5 Q + NUM composition fires
    transparently here too — ``Bawat isa, kumain ng kanin.`` parses
    with DISTRIB=YES, OBJ=kanin, and SUBJ.CARDINAL_VALUE=1."""

    @pytest.mark.parametrize("sentence,cardinal_value,verb_pred,obj_lemma", [
        ("Bawat isa, kumain ng kanin.",     "1",
            "EAT <SUBJ, OBJ>", "kanin"),
        ("Bawat dalawa, kumain ng kanin.",  "2",
            "EAT <SUBJ, OBJ>", "kanin"),
        ("Bawat isa, bumili ng aklat.",     "1",
            "BUY <SUBJ, OBJ>", "aklat"),
        ("Kada isa, kumain ng kanin.",      "1",
            "EAT <SUBJ, OBJ>", "kanin"),
    ])
    def test_q_num_with_trans(
        self,
        sentence: str,
        cardinal_value: str,
        verb_pred: str,
        obj_lemma: str,
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISTRIB") is True
        assert fs.feats.get("PRED") == verb_pred
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") is True
        assert subj.feats.get("CARDINAL_VALUE") == cardinal_value
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == obj_lemma


# === Anti-overgeneration: same UNIV gating across variants ============


class TestNonUniversalTopicStillRejected:
    """The new transitive rules retain the
    ``(↓1 UNIV) =c 'YES'`` gating — non-universal topics
    (proper names, plain ang-NPs) do not fire any of the
    transitive variants either."""

    @pytest.mark.parametrize("sentence", [
        "Si Maria, kumain ng kanin.",       # transitive, non-UNIV
        "Si Maria, tumakbo sa parke.",      # intrans+DAT, non-UNIV
        "Ang bata, kumain ng kanin.",       # transitive, non-UNIV
    ])
    def test_non_universal_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"non-UNIV topic must not parse via L81 transitive "
            f"rules: {sentence!r}"
        )


# === Top-1 uniqueness ================================================


class TestNoAmbiguityBlowup:
    """Each transitive variant produces a bounded number of parses
    for the canonical surface; no ambiguity blowup with the
    Commit 7 intransitive rule or with existing V-S transitive
    rules. The 5-daughter shape with sa-PP admits two readings
    after the 9.X.c8 NP-internal sa-PP modifier rule (clausal
    ADJUNCT vs OBJ-internal modifier on ``kanin``)."""

    @pytest.mark.parametrize("sentence,expected", [
        ("Bawat bata, kumain ng kanin.", 1),
        ("Bawat bata, tumakbo sa parke.", 1),
        ("Bawat bata, kumain ng kanin sa parke.", 2),
        ("Bawat isa, kumain ng kanin.", 1),
    ])
    def test_unique_parse(self, sentence: str, expected: int) -> None:
        parses = parse_text(sentence)
        assert len(parses) == expected
