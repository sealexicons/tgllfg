# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C Commit 7.5 — universal Q + NUM composition.

Closes the Phase 5f Commit 20 deferred Q + NUM piece per Phase 5n.C
anti-deferral discipline. Adds parallel rules to ``cfg/nominal.py``
mirroring the Phase 5f Commit 20 Q + N family, with a
``NUM[CARDINAL=YES]`` complement instead of a bare N.

The new rules let ``bawat isa`` / ``bawat dalawa`` / ``kada isa``
compose as NPs — and once they compose as ``NP[CASE=NOM]`` with
``UNIV=YES``, the Phase 5n.C Commit 7 L81 distributive-Q topic rule
fires on them transparently. This unblocks the canonical S&O 1972
§10 distributive-scope example ``Bawat isa, kumain.`` "Each one
ate", which was 0-parsing pre-Commit-7.5.

Reference: Schachter & Otanes 1972 §4.7 / §10; Ramos & Bautista
1986 ch.16.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Q + NUM as NP =====================================================


class TestQNumAsNP:
    """``bawat isa`` / ``bawat dalawa`` / ``kada isa`` compose as NPs
    — DET-marked, ADP-marked, and bare-NOM variants. The composed NP
    carries UNIV=YES (from the Q) and CARDINAL_VALUE percolated from
    the NUM."""

    @pytest.mark.parametrize("sentence,cardinal_value", [
        ("Kumain ang bawat isa.",     "1"),
        ("Kumain ang bawat dalawa.",  "2"),
        ("Kumain ang bawat tatlo.",   "3"),
        ("Kumain ang kada isa.",      "1"),
        ("Kumain ang kada dalawa.",   "2"),
    ])
    def test_det_marked_q_num(
        self, sentence: str, cardinal_value: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"Q+NUM should compose as NP: {sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") is True
        assert subj.feats.get("CARDINAL_VALUE") == cardinal_value

    @pytest.mark.parametrize("sentence,cardinal_value", [
        ("Kumain bawat isa.",     "1"),
        ("Kumain bawat dalawa.",  "2"),
        ("Kumain kada isa.",      "1"),
    ])
    def test_bare_nom_q_num(
        self, sentence: str, cardinal_value: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"bare-NOM Q+NUM should compose: {sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") is True
        assert subj.feats.get("CARDINAL_VALUE") == cardinal_value


# === L81 distributive-Q fires on Q+NUM topics ==========================


class TestL81FiresOnQNumTopics:
    """The canonical S&O 1972 §10 example ``Bawat isa, kumain.`` and
    siblings now parse via the L81 rule (Phase 5n.C Commit 7) with
    DISTRIB=YES — the L81 rule's UNIV=YES daughter constraint matches
    the new Q+NUM-composed NP."""

    @pytest.mark.parametrize("sentence,cardinal_value,verb_pred", [
        ("Bawat isa, kumain.",     "1", "EAT <SUBJ>"),
        ("Bawat dalawa, kumain.",  "2", "EAT <SUBJ>"),
        ("Bawat tatlo, kumain.",   "3", "EAT <SUBJ>"),
        ("Kada isa, kumain.",      "1", "EAT <SUBJ>"),
        ("Kada dalawa, kumain.",   "2", "EAT <SUBJ>"),
        ("Bawat isa, tumakbo.",    "1", "TAKBO <SUBJ>"),
    ])
    def test_l81_with_q_num(
        self, sentence: str, cardinal_value: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"L81 with Q+NUM should parse: {sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISTRIB") is True
        assert fs.feats.get("PRED") == verb_pred
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") is True
        assert subj.feats.get("CARDINAL_VALUE") == cardinal_value


# === Non-cardinal NUMs rejected =======================================


class TestNonCardinalNumRejected:
    """The Q+NUM rules require ``NUM[CARDINAL=YES]``. Ordinals
    (``ikalima`` "fifth") and vague-Q heads (``marami`` "many"; not
    even a NUM) do not match — bawat / kada don't compose with them
    via the new rules."""

    @pytest.mark.parametrize("sentence", [
        "Bawat ikalima, kumain.",   # ordinal
        "Bawat marami, kumain.",    # vague Q (not NUM)
    ])
    def test_non_cardinal_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"non-cardinal Q+? must not parse via Q+NUM rule: "
            f"{sentence!r}"
        )


# === Coexistence: Q + N still works ===================================


class TestQPlusNUnchanged:
    """The Phase 5f Commit 20 Q + N rules continue to fire — adding
    Q + NUM doesn't change the Q + N composition path."""

    @pytest.mark.parametrize("sentence,n_lemma", [
        ("Bawat bata, kumain.", "bata"),
        ("Kada tao, tumakbo.",  "tao"),
        ("Kumain ang bawat aklat.", "aklat"),
    ])
    def test_q_n_still_composes(self, sentence: str, n_lemma: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") is True
        assert subj.feats.get("LEMMA") == n_lemma
