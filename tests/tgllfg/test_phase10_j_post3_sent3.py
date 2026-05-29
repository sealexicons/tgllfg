# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-3 PANAHON sent-3 close-out: ay-fronting pipeline
split-and-glue (third instance of the post-* split pattern).

PANAHON sent-3 (R&G 1981): ``Ang natitirang limang buwan ay naroong
maghati sa init at ulan.`` "The remaining five months are-there to
divide between heat and rain."

The chart-level Phase 4 §7.4 ``S → NP[CASE=NOM] PART[LINK=AY]
S_GAP`` rule produces the canonical parse but it sat past
``max_tree_iterations=5000`` because the matrix-span fan-out
(NP_internal_alts × S_GAP_alts) and the Phase 5n.B C21 colloquial
no-``ay`` variant (``S → NP[CASE=NOM] S_GAP`` with solve-time
``(↓1 INDEF) =c 'YES'``) compound to push the canonical past the
cap. The pipeline-level ay-split bypasses the cross-product
entirely: parses pre-``ay`` half as ``NP[CASE=NOM]`` and
post-``ay`` half as ``S_GAP``, then synthesizes the matrix S
mirroring the chart rule's equations (``(↑) = ↓3``,
``(↑ TOPIC) = ↓1``, ``(↓3 REL-PRO) = ↓1``,
``(↓3 REL-PRO) =c (↓3 SUBJ)`` — re-points REL-PRO / SUBJ to the
fronted NP so TOPIC, REL-PRO, and SUBJ share identity).

Activation: input contains a free-standing ``ay`` token (or the
bound ``'y`` contraction) at a sentence-internal position with
non-trivial halves on each side. Conservative — single first
match.
"""

from tgllfg.core.pipeline import (
    _looks_ay_fronted,
    _split_on_ay,
    parse_text,
)


class TestSent3Closure:
    def test_sent3_closes_at_default_cap(self) -> None:
        """sent-3 should close at the default
        ``max_tree_iterations=5000`` via the ay-split fast path —
        the chart-level rule was timing-blocked at cap 50000
        (60.8s) before post-3."""
        parses = parse_text(
            "Ang natitirang limang buwan ay naroong maghati "
            "sa init at ulan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        subj = fs.feats.get("SUBJ")
        rel_pro = fs.feats.get("REL-PRO")
        # The post-3 glue mirrors the chart rule's full identity:
        # TOPIC == REL-PRO == SUBJ.
        assert topic is not None
        assert subj is not None
        assert rel_pro is not None
        assert topic is subj
        assert topic is rel_pro


class TestAyDetection:
    """``_looks_ay_fronted`` is the activation heuristic — must
    accept the genuine ay-fronting shape, reject everything else.
    """

    def test_ay_in_middle_accepted(self) -> None:
        assert _looks_ay_fronted("Ang aso ay tumakbo.") is True

    def test_apostrophe_y_accepted(self) -> None:
        # The bound ``'y`` contraction after a vowel-final word.
        assert _looks_ay_fronted("Rito'y siyesta na.") is True

    def test_leading_ay_rejected(self) -> None:
        # Sentence-initial ``ay`` (interjection-like, no fronting).
        assert _looks_ay_fronted("Ay, sandali lang.") is False

    def test_no_ay_rejected(self) -> None:
        assert _looks_ay_fronted("Kumain ang bata.") is False

    def test_too_short_rejected(self) -> None:
        # Need non-trivial halves on each side.
        assert _looks_ay_fronted("Aso ay") is False


class TestAySplit:
    """``_split_on_ay`` partitions the input around the leftmost
    free-standing ``ay`` or bound ``'y``.
    """

    def test_basic_split(self) -> None:
        result = _split_on_ay("Ang aso ay tumakbo.")
        assert result == ("Ang aso", "tumakbo.")

    def test_apostrophe_split(self) -> None:
        result = _split_on_ay("Rito'y siyesta na.")
        # ``Rito'y siyesta na.`` → ``'y `` after Rito.
        assert result == ("Rito", "siyesta na.")

    def test_long_sentence_split(self) -> None:
        result = _split_on_ay(
            "Ang natitirang limang buwan ay naroong maghati "
            "sa init at ulan."
        )
        assert result == (
            "Ang natitirang limang buwan",
            "naroong maghati sa init at ulan.",
        )

    def test_no_ay_returns_none(self) -> None:
        assert _split_on_ay("Kumain ang bata.") is None


class TestNoRegressionOnExistingAyFronting:
    """The chart's Phase 4 §7.4 ``S → NP[CASE=NOM] PART[LINK=AY]
    S_GAP`` rule is still functional via the chart path when the
    split doesn't fire OR after the split succeeds. Confirm that
    sentences that previously parsed via the chart-level rule
    still parse (and the ``TOPIC.id == SUBJ.id`` invariant from
    ``test_relativization_ay_phase4`` holds)."""

    def test_intransitive_av(self) -> None:
        parses = parse_text("Ang aso ay tumakbo.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        subj = fs.feats.get("SUBJ")
        assert topic is not None and subj is not None
        assert topic is subj

    def test_transitive_av(self) -> None:
        parses = parse_text("Ang aso ay kumain ng isda.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "EAT <SUBJ, OBJ>"
