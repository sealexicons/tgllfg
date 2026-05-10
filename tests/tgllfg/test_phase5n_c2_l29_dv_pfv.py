"""Phase 5n.C.2 Commits 1-3 — L29 DV PFV high-frequency verbs.

Closes the §18.1 L29 DV PFV paradigm-coverage gap surfaced during
Phase 5e Commit 18 review. Each canonical DV PFV sentence exercises
the existing DV PFV paradigm cell (``data/tgl/paradigms.yaml``
line 286: ``-in-`` infix + ``-an`` suffix) on a high-frequency verb.

Pattern: ``<DV-PFV-V> ni <agent> si <pivot>`` per S&O 1972 §10 +
R&B 1986 chs.5/7. The agent is GEN-marked; the pivot is NOM-marked
(``si Juan``). DV pivots are semantically dative/locative/recipient.

Commit 1 (this file initial) pins five working verbs as positive
parses and three under-lexicalised verbs at 0-parse via
``TestPinnedDVPFVMissingAnOblig``. Commit 2 adds ``an_oblig`` to
the three under-lexicalised verbs in ``verbs.yaml``; Commit 3
flips the tripwire to positive coverage.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Positive coverage — verbs that work at branch cut ====================


@pytest.mark.parametrize("sentence,verb_lemma,pred", [
    ("Inaralan ni Maria si Juan.",  "aral",   "ARAL <SUBJ, OBJ-AGENT>"),
    ("Binasahan ni Maria si Juan.", "basa",   "BASA <SUBJ, OBJ-AGENT>"),
    ("Binilihan ni Maria si Juan.", "bili",   "BILI <SUBJ, OBJ-AGENT>"),
    ("Ginawahan ni Maria si Juan.", "gawa",   "GAWA <SUBJ, OBJ-AGENT>"),
    ("Tinulungan ni Maria si Juan.", "tulong", "TULONG <SUBJ, OBJ-AGENT>"),
])
def test_dv_pfv_canonical(
    sentence: str, verb_lemma: str, pred: str
) -> None:
    """Canonical DV PFV with V + GEN-agent + NOM-pivot."""
    parses = parse_text(sentence)
    assert len(parses) >= 1, f"expected ≥1 parse for {sentence!r}"
    _ct, fs, _astr, _diags = parses[0]
    assert fs.feats.get("VOICE") == "DV"
    assert fs.feats.get("ASPECT") == "PFV"
    # PRED may vary by lex (some have specific English glosses);
    # assert the LEMMA-based form which the engine produces by
    # default when no LexicalEntry overrides.
    assert fs.feats.get("PRED") == pred, (
        f"PRED mismatch for {sentence!r}: "
        f"expected {pred!r}, got {fs.feats.get('PRED')!r}"
    )


# === Tripwire — verbs missing an_oblig at branch cut ======================


class TestPinnedDVPFVMissingAnOblig:
    """Verbs whose ``verbs.yaml`` entries lack ``an_oblig`` at Phase
    5n.C.2 branch cut (``6ad5841``): ``bigay`` / ``tanong`` / ``usap``.
    Without ``an_oblig``, the analyzer's DV PFV cell does not fire,
    so the canonical DV PFV sentence 0-parses.

    Commit 2 adds ``an_oblig`` to each verb's affix_class list;
    Commit 3 flips this test into positive-parse asserters.
    """

    @pytest.mark.parametrize("sentence,verb_lemma", [
        ("Binigayan ni Maria si Juan.",  "bigay"),
        ("Tinanungan ni Maria si Juan.", "tanong"),
        ("Inusapan ni Maria si Juan.",   "usap"),
    ])
    def test_pinned_zero_parse(
        self, sentence: str, verb_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"expected 0 parses for {sentence!r} pre-Commit-2; got "
            f"{len(parses)}. Did Commit 2 already land? If so, flip "
            f"this tripwire to positive parse (Commit 3 task)."
        )
