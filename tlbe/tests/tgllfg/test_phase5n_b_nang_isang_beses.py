# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 24: narrative-opener idiom Nang isang beses
(§18 L30).

Closes §18.1 deferral L30. Target sentences:

    Nang isang beses, may isang manok.   "Once, there was a chicken."
    Nang isang beses, kumain ang bata.   "Once, the child ate."
    Nang isang beses, pumunta si Maria.  "Once, Maria went."

Grammar change (cfg/discourse.py): new fixed-phrase rule

    S → PART NUM PART N PUNCT[PUNCT_CLASS=COMMA] S

with literal-lemma constraints locking the rule to the
narrative idiom surface (PART must be ``nang``, NUM must be
CARDINAL_VALUE='1' (``isa``), N must be ``beses`` /
SEM_CLASS=FREQUENCY). The matrix shares with the inner S via
``(↑) = ↓6`` and adds ``DISCOURSE='NARRATIVE_OPENER'``.

The 6-daughter shape (PART + NUM + PART + N + PUNCT + S)
captures the explicit token sequence after the linker split
``isang → isa + -ng``. An earlier 4-daughter design (PART + N
+ PUNCT + S, relying on the cardinal-internal-modifier rule
to collapse ``isang beses`` into a single N) didn't fire — the
collapse forms a different N projection that doesn't match the
expected category in this position.

Non-idiom uses of nang / isa / beses continue to parse via
their existing rules. The 6-daughter pattern + LEMMA / CARDINAL
/ SEM_CLASS / PUNCT constraints lock the rule to the exact
narrative-opener surface; mismatch on any constraint causes
the rule to not fire.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _narrative_opener_parse(text: str):
    """Return the parse with DISCOURSE='NARRATIVE_OPENER' on the
    matrix, or None."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("DISCOURSE") == "NARRATIVE_OPENER":
            return p
    return None


# === Idiom targets ===================================================


class TestNarrativeOpener:
    """The fixed-phrase ``Nang isang beses, ...`` parses with
    DISCOURSE='NARRATIVE_OPENER' on the matrix. The inner clause's
    f-structure is lifted to the matrix."""

    @pytest.mark.parametrize("sentence,inner_pred", [
        ("Nang isang beses, may isang manok.",   "EXIST <SUBJ>"),
        ("Nang isang beses, may isang aklat.",   "EXIST <SUBJ>"),
        ("Nang isang beses, kumain ang bata.",   "EAT <SUBJ>"),
        ("Nang isang beses, pumunta si Maria.",  "PUNTA <SUBJ>"),
        ("Nang isang beses, tumakbo si Juan.",   "TAKBO <SUBJ>"),
    ])
    def test_idiom_parses(
        self, sentence: str, inner_pred: str
    ) -> None:
        result = _narrative_opener_parse(sentence)
        assert result is not None, (
            f"{sentence!r} did not produce a narrative-opener parse"
        )
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("PRED") == inner_pred
        assert fs.feats.get("DISCOURSE") == "NARRATIVE_OPENER"


# === Non-idiom uses unaffected =======================================


class TestNonIdiomUses:
    """Non-idiom uses of nang / isa / beses continue to parse via
    their existing rules. The 6-daughter pattern + literal-lemma
    constraints keep the rule narrowly scoped."""

    def test_isang_aklat_unchanged(self) -> None:
        # ``May isang aklat.`` — isa + -ng + aklat (existing
        # cardinal-internal-modifier path).
        parses = parse_text("May isang aklat.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Not a narrative-opener.
        assert fs.feats.get("DISCOURSE") != "NARRATIVE_OPENER"

    def test_may_isang_beses_unchanged(self) -> None:
        # ``May isang beses.`` — bare existential, no narrative
        # idiom (no nang prefix, no comma + inner).
        parses = parse_text("May isang beses.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISCOURSE") != "NARRATIVE_OPENER"
