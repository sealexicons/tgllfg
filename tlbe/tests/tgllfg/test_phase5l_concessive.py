# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5l Commit 4: concessive subordination — kahit / bagaman.

Roadmap §12.1 / plan-of-record §5.2, §6 Commit 4. One new rule
in ``cfg/subordination.py``:

    SubordClause → PART[COMP_TYPE=CONC] S       (builder)

The matrix-attachment rules from Commit 2 (post-matrix and
pre-matrix-comma) are SUBORD_TYPE-agnostic and admit the new
CONC SubordClause without modification. Both concessive PARTs
(kahit / bagaman — Commit 1 lex) feed the same builder; the
chart picks the right entry from the input token. ``bagaman``
additionally carries ``REGISTER=FORMAL`` on its PART f-structure.

End-to-end target sentences:

    Kahit umulan, pumunta si Maria.            # pre-matrix kahit
    Pumunta si Maria kahit umulan.             # post-matrix kahit
    Bagaman umulan, pumunta si Maria.          # pre-matrix bagaman
    Pumunta si Maria bagaman umulan.           # post-matrix bagaman

Note on inner-clause verb choice: the canonical concessive
sentence in the plan uses ``kahit umulan`` "even if it rained".
For grammar regression-safety in this commit, the tests below
prefer simple intransitive AV-PFV verbs with explicit subjects
(``kumain si Maria``, ``pumunta si Juan``) — which we know
parse cleanly post-Phase-5j.
"""

from tgllfg.core.pipeline import parse_text


def _adjunct_with_subord_type(fs, subord_type: str):
    adjuncts = fs.feats.get("ADJUNCT")
    if adjuncts is None:
        return None
    for adj in adjuncts:
        if adj.feats.get("SUBORD_TYPE") == subord_type:
            return adj
    return None


# === kahit — concessive ===============================================


class TestKahitConcessive:
    """``kahit`` "even if / although" embeds a clause as a
    concessive adjunct. Same shape as conditional (Commit 2),
    different SUBORD_TYPE."""

    def test_kahit_pre_matrix(self) -> None:
        parses = parse_text("Kahit kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix is the post-comma S.
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        conc = _adjunct_with_subord_type(fs, "CONC")
        assert conc is not None
        # Inner clause's PRED is from kumain.
        assert (conc.feats.get("PRED") or "").startswith("EAT")

    def test_kahit_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan kahit kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        conc = _adjunct_with_subord_type(fs, "CONC")
        assert conc is not None
        assert (conc.feats.get("PRED") or "").startswith("EAT")

    def test_kahit_pre_post_same_fstruct(self) -> None:
        pre = parse_text("Kahit kumain si Maria, pumunta si Juan.")[0][1]
        post = parse_text("Pumunta si Juan kahit kumain si Maria.")[0][1]
        assert (pre.feats.get("PRED") or "")[:5] == (
            post.feats.get("PRED") or ""
        )[:5]
        pre_conc = _adjunct_with_subord_type(pre, "CONC")
        post_conc = _adjunct_with_subord_type(post, "CONC")
        assert pre_conc is not None and post_conc is not None
        assert (pre_conc.feats.get("PRED") or "")[:3] == (
            post_conc.feats.get("PRED") or ""
        )[:3]


# === bagaman — formal concessive ======================================


class TestBagamanConcessive:
    """``bagaman`` is the formal-register variant of ``kahit``.
    Same syntactic distribution; carries ``REGISTER=FORMAL`` on
    its PART daughter, which percolates onto the SubordClause
    f-structure via ``(↑) = ↓2``."""

    def test_bagaman_pre_matrix(self) -> None:
        parses = parse_text("Bagaman kumain si Maria, pumunta si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        conc = _adjunct_with_subord_type(fs, "CONC")
        assert conc is not None
        assert (conc.feats.get("PRED") or "").startswith("EAT")

    def test_bagaman_post_matrix(self) -> None:
        parses = parse_text("Pumunta si Juan bagaman kumain si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        conc = _adjunct_with_subord_type(fs, "CONC")
        assert conc is not None


# === CONC × negation interactions =====================================


class TestNegatedInnerConcessive:
    """The inner clause of a CONC subord can be negated."""

    def test_kahit_negated_inner(self) -> None:
        parses = parse_text(
            "Kahit hindi kumain si Maria, pumunta si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        conc = _adjunct_with_subord_type(fs, "CONC")
        assert conc is not None
        assert conc.feats.get("POLARITY") == "NEG"


class TestNegatedMatrixConcessive:
    """Matrix-clause negation composes orthogonally with CONC."""

    def test_kahit_negated_matrix(self) -> None:
        parses = parse_text(
            "Hindi pumunta si Juan kahit kumain si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        conc = _adjunct_with_subord_type(fs, "CONC")
        assert conc is not None
        assert conc.feats.get("POLARITY") != "NEG"


# === CONC × NP-coord inside ===========================================


class TestNPCoordInsideConc:
    """Phase 5k NP-coord SUBJ inside a concessive clause."""

    def test_kahit_inner_np_coord(self) -> None:
        parses = parse_text(
            "Kahit pumunta si Maria at si Juan, kumain si Pedro."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        conc = _adjunct_with_subord_type(fs, "CONC")
        assert conc is not None
        inner_subj = conc.feats.get("SUBJ")
        assert inner_subj is not None
        assert inner_subj.feats.get("COORD") == "AND"


# === CONC vs COND don't cross-fire ====================================


class TestConcCondDisjoint:
    """A CONC sentence has SUBORD_TYPE=CONC on its adjunct, NOT
    SUBORD_TYPE=COND. A COND sentence has the converse. The two
    SUBORD_TYPEs never appear together on the same adjunct."""

    def test_kahit_does_not_produce_cond_adjunct(self) -> None:
        parses = parse_text("Kahit kumain si Maria, pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        # CONC adjunct present, COND adjunct absent.
        assert _adjunct_with_subord_type(fs, "CONC") is not None
        assert _adjunct_with_subord_type(fs, "COND") is None

    def test_kung_does_not_produce_conc_adjunct(self) -> None:
        parses = parse_text("Kung kumain si Maria, pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        assert _adjunct_with_subord_type(fs, "COND") is not None
        assert _adjunct_with_subord_type(fs, "CONC") is None


# === C-tree shape (regression-safety) =================================


class TestCTreeShape:
    """Same daughter-count invariants as Commit 2 — pre-matrix
    has SubordClause + PUNCT + S; post-matrix has S + SubordClause."""

    def test_pre_matrix_three_daughters(self) -> None:
        parses = parse_text("Kahit kumain si Maria, pumunta si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        assert ctree.label.startswith("S")
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("SubordClause")
        assert labels[1].startswith("PUNCT")
        assert labels[2].startswith("S")

    def test_post_matrix_two_daughters(self) -> None:
        parses = parse_text("Pumunta si Juan kahit kumain si Maria.")
        ctree, _fs, _astr, _diags = parses[0]
        assert ctree.label.startswith("S")
        labels = [c.label for c in ctree.children]
        assert labels[0].startswith("S")
        assert labels[1].startswith("SubordClause")
