"""Phase 5n.B Commit 21: PRON-headed RC for negative indefinites
(§18 L101).

Closes §18.1 deferral L101. Target sentences:

    Walang sinumang dumating.   "Nobody came."
    Walang sinumang kumain.     "Nobody ate."
    Walang sinumang tumakbo.    "Nobody ran."

Grammar change (cfg/extraction.py): new rules

    PRON → PRON[INDEF=NEG_INDEF] PART[LINK=NA] S_GAP
    PRON → PRON[INDEF=NEG_INDEF] PART[LINK=NG] S_GAP

parallel to the Phase 4 §7.5 N-headed relativization
(``NP[CASE=X] → NP[CASE=X] PART[LINK=Y] S_GAP``) but with
``PRON`` as both head and projection. The
``(↓1 INDEF) =c 'NEG_INDEF'`` constraint keeps the rule narrow
to negative-indefinite PRONs (today: ``sinuman`` "no one";
``anuman`` "nothing" gets its lex entry in Phase 5n.B C22).
Other PRONs (``siya`` / ``ako`` / ``niya`` / ...) lack the
INDEF feat and don't fire.

The new rule produces a ``PRON``, so the existing Phase 5m
Commit 9 negative-existential rule (``S → PART[EXISTENTIAL=
YES, POLARITY=NEG] PART[LINK=NG] PRON[INDEF=NEG_INDEF]``)
consumes the relativized PRON unchanged — closing the path
that the Phase 5m comment ("the relative-clause grammar
handles sinumang dumating") had anticipated but not yet
implemented.

The RC body is an ``S_GAP`` (SUBJ-gapped clause) following
the Phase 4 §7.5 SUBJ-only-relativization restriction. The
gap binds to the head PRON's f-structure via REL-PRO PRED
and CASE shares plus the ``(↓3 REL-PRO) =c (↓3 SUBJ)``
constraining equation (anaphoric, not structure-sharing —
same convention as the N-headed rule).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _exist_neg_parse(text: str):
    """Return the parse with PRED='EXIST <SUBJ>' and POLARITY=NEG,
    or None."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        feats = p[1].feats
        if (
            feats.get("PRED") == "EXIST <SUBJ>"
            and feats.get("POLARITY") == "NEG"
        ):
            return p
    return None


# === Walang sinumang + intransitive V ================================


class TestWalangSinumangIntransitive:
    """``Walang sinumang + V[finite, intransitive]`` parses with
    sinuman as the head of the PRON-RC and the V as the RC body."""

    @pytest.mark.parametrize("sentence", [
        "Walang sinumang dumating.",
        "Walang sinumang kumain.",
        "Walang sinumang tumakbo.",
        "Walang sinumang pumunta.",
        "Walang sinumang umupo.",
        "Walang sinumang umalis.",
    ])
    def test_intransitive_rc(self, sentence: str) -> None:
        result = _exist_neg_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        # SUBJ is the relativized PRON (sinuman) with the RC
        # in its ADJ.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "sinuman"
        assert subj.feats.get("INDEF") == "NEG_INDEF"
        assert subj.feats.get("CASE") == "NOM"
        # The RC lives in subj.ADJ.
        adj = subj.feats.get("ADJ")
        assert adj is not None
        assert len(adj) >= 1


# === Walang sinumang + transitive V (with explicit OBJ) ===============


class TestWalangSinumangTransitive:
    """The PRON-headed RC also admits a transitive AV verb with
    its own OBJ (the OBJ stays inside the RC body — not
    relativized; sinuman fills the SUBJ gap)."""

    def test_transitive_with_obj(self) -> None:
        result = _exist_neg_parse("Walang sinumang kumain ng isda.")
        assert result is not None
        _ct, fs, _astr, _diags = result
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "sinuman"


# === Phase 5m C9 regression ===========================================


class TestPhase5mWalangSinumanUnchanged:
    """The bare ``Walang sinuman.`` (Phase 5m C9 — no RC body)
    continues to parse unchanged."""

    def test_walang_sinuman_bare(self) -> None:
        result = _exist_neg_parse("Walang sinuman.")
        assert result is not None
        _ct, fs, _astr, _diags = result
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "sinuman"
        # No ADJ on the bare path.
        assert not subj.feats.get("ADJ")


# === Other PRONs don't fire ==========================================


class TestNonIndefPronsBlocked:
    """The ``(↓1 INDEF) =c 'NEG_INDEF'`` gate keeps the rule
    narrow. Non-indef PRONs (siya / ako / niya) don't fire it
    because they have no INDEF feat."""

    @pytest.mark.parametrize("sentence", [
        # ``Walang siyang dumating.`` is ungrammatical — pinned
        # at 0-parse so the rule's INDEF gate is exercised.
        "Walang siyang dumating.",
        "Walang akong dumating.",
    ])
    def test_non_indef_pron_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"{sentence!r} parsed unexpectedly — the PRON-headed "
            f"RC rule's INDEF=NEG_INDEF gate has been weakened."
        )


# === Phase 4 §7.5 N-headed RC unchanged ==============================


class TestNHeadedRcUnchanged:
    """The original Phase 4 §7.5 N-headed relativization
    (``ang batang kumain``) continues to fire — the new
    PRON-headed rule is a sibling, not a replacement."""

    def test_n_headed_rc(self) -> None:
        # ``Tumakbo ang batang kumain.`` — N-headed RC: bata as
        # head N, kumain as RC body. Verifies the existing Phase
        # 4 §7.5 N-headed relativization machinery still fires.
        parses = parse_text("Tumakbo ang batang kumain.")
        assert len(parses) >= 1
