# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5m Commit 10: single-word discourse connectives.

Roadmap §12.1 / plan-of-record §5.1 (rule already landed in
Commit 4). Verifies that the Commit 1 PART entries

* ``samakatuwid`` (DISCOURSE=THEREFORE, DISCOURSE_POS=SENTENCE_INITIAL)
* ``gayunpaman``  (DISCOURSE=HOWEVER,   DISCOURSE_POS=SENTENCE_INITIAL)

route through the existing Commit 4 sentence-initial PART rule
in cfg/discourse.py:

    S → PART S
        (↑) = ↓2
        ↓1 ∈ (↑ ADJUNCT)
        (↓1 DISCOURSE_POS) =c 'SENTENCE_INITIAL'

The same rule that fires on Commit 4 modal particles fires on
discourse connectives — the gate is the shared
``DISCOURSE_POS=SENTENCE_INITIAL`` feat. No new grammar in this
commit.

The DISCOURSE feat (THEREFORE / HOWEVER) is preserved on the
ADJUNCT member; it does NOT lift to the matrix S (parallel to
EPISTEMIC on Commit 4 — both are inherently adjunct-scoped).

Reference: R&B 1986 §15.7.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Single-word discourse connectives ================================


DISCOURSE_CASES = [
    # (sentence, pred_prefix, lemma, discourse)
    ("Samakatuwid kumain ang bata.",   "EAT",   "samakatuwid", "THEREFORE"),
    ("Samakatuwid pumupunta siya.",    "PUNTA", "samakatuwid", "THEREFORE"),
    ("Samakatuwid tumakbo ang aso.",   "TAKBO", "samakatuwid", "THEREFORE"),
    ("Gayunpaman kumain ang bata.",    "EAT",   "gayunpaman",  "HOWEVER"),
    ("Gayunpaman pumupunta siya.",     "PUNTA", "gayunpaman",  "HOWEVER"),
]


def _adjunct_with_lemma(fs, lemma: str):
    adj = fs.feats.get("ADJUNCT") or []
    for m in adj:
        if hasattr(m, "feats") and m.feats.get("LEMMA") == lemma:
            return m
    return None


class TestDiscourseConnectivesSingle:
    """``samakatuwid`` and ``gayunpaman`` lift as sentence-initial
    ADJUNCTs carrying their DISCOURSE marker via the Commit 4 rule."""

    @pytest.mark.parametrize(
        "sent,pred_prefix,lemma,discourse", DISCOURSE_CASES,
    )
    def test_discourse_lifts_as_adjunct(
        self, sent: str, pred_prefix: str,
        lemma: str, discourse: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        connective = _adjunct_with_lemma(fs, lemma)
        assert connective is not None, (
            f"expected an ADJUNCT member with LEMMA={lemma!r} for "
            f"{sent!r}; got ADJUNCT={fs.feats.get('ADJUNCT')!r}"
        )
        assert connective.feats.get("DISCOURSE") == discourse
        assert connective.feats.get("DISCOURSE_POS") == "SENTENCE_INITIAL"

    def test_matrix_lacks_discourse_feat(self) -> None:
        """DISCOURSE stays on the ADJUNCT member; it does NOT lift
        to the matrix S (parallel to EPISTEMIC on Commit 4 modal
        particles)."""
        parses = parse_text("Samakatuwid kumain ang bata.")
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISCOURSE") is None


# === Composition with negation ========================================


class TestDiscourseConnectiveWithNegation:
    """Discourse connectives compose with the existing Phase 4
    negation grammar."""

    def test_samakatuwid_hindi(self) -> None:
        """``Samakatuwid hindi kakain ang bata.`` "Therefore the
        child won't eat." — sentence-initial samakatuwid + Phase 4
        hindi negation."""
        parses = parse_text("Samakatuwid hindi kakain ang bata.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        sam = _adjunct_with_lemma(fs, "samakatuwid")
        assert sam is not None


# === Single-parse verification ========================================


class TestSingleParse:
    """Single-word discourse connectives produce exactly one parse
    — no spurious ambiguity from interactions with other clause-
    level rules."""

    def test_samakatuwid_single_parse(self) -> None:
        parses = parse_text("Samakatuwid kumain ang bata.")
        assert len(parses) == 1

    def test_gayunpaman_single_parse(self) -> None:
        parses = parse_text("Gayunpaman pumupunta siya.")
        assert len(parses) == 1
