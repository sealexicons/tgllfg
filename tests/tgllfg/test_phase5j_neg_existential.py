"""Phase 5j Commit 3: negative existential clause.

Roadmap §12.1 / plan-of-record §5.2, §6 Commit 3. Two new clause
rules in ``cfg/clause.py``:

    S → PART[EXISTENTIAL=YES, POLARITY=NEG] N
    S → PART[EXISTENTIAL=YES, POLARITY=NEG] PART[LINK=NG] N

Negative-polarity counterpart of the Commit 2 positive
existential. ``wala`` is vowel-final and always takes bound
``-ng`` linker before its complement (``Walang aklat`` —
canonical surface). The bare-N variant is included for parity
with Commit 2 / edge cases; the linker variant is the primary
entry point.

The Commit 2 clause-final DAT-lift rule (``S → S NP[CASE=DAT]``
gated on ``CLAUSE_TYPE=EXISTENTIAL``) composes with negative
existentials unchanged, so locative-PP composition (``Walang tao
sa labas``) falls out without a new rule.

End-to-end target sentences:

    Walang aklat.            "There's no book."
    Walang tao.              "There's no one."
    Walang tao sa labas.     "There's no one outside."
    Walang aso sa bahay.     "There's no dog in the house."
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Bare-wala / wala + linker negative existential ====================


class TestNegativeExistential:
    """The wala rule fires on ``walang`` (= wala + bound -ng)
    + N and produces an existential matrix with POLARITY=NEG."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Walang aklat.",  "aklat"),
        ("Walang tao.",    "tao"),
        ("Walang aso.",    "aso"),
        ("Walang bahay.",  "bahay"),
        ("Walang bundok.", "bundok"),
    ])
    def test_walang_n_parses(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma


class TestWalangCTreeShape:
    """``Walang aklat`` has 3 immediate daughters: PART /
    PART[LINK=NG] / N (linker variant)."""

    def test_walang_aklat_c_tree(self) -> None:
        parses = parse_text("Walang aklat.")
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        ctree, _fs, _astr, _diags = ex_parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 3, (
            f"expected 3 immediate daughters for linker variant; "
            f"got {[c.label for c in ctree.children]}"
        )
        assert ctree.children[0].label == "PART"
        assert ctree.children[1].label == "PART"
        assert ctree.children[2].label.startswith("N")


# === Locative-PP composition (Commit 2 DAT-lift fires on neg too) =====


class TestNegLocativePPComposition:
    """Clause-final ``sa``-PP composes onto a negative existential
    matrix via the Commit 2 EXISTENTIAL-gated DAT-lift rule."""

    @pytest.mark.parametrize("sentence,subj_lemma,loc_lemma", [
        ("Walang tao sa labas.",   "tao",   "labas"),
        ("Walang aklat sa bahay.", "aklat", "bahay"),
        ("Walang aso sa labas.",   "aso",   "labas"),
    ])
    def test_neg_locative_pp(
        self, sentence: str, subj_lemma: str, loc_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        adjuncts = fs.feats.get("ADJUNCT") or frozenset()
        loc_lemmas = {
            adj.feats.get("LEMMA")
            for adj in adjuncts
            if adj.feats.get("CASE") == "DAT"
        }
        assert loc_lemma in loc_lemmas


# === POS / NEG disambiguation ========================================


class TestPolarityDisambiguation:
    """``may`` and ``wala`` carry distinct POLARITY values; the
    Commits 2 / 3 rules disambiguate via category-pattern matching
    (``PART[EXISTENTIAL=YES, POLARITY=POS]`` vs
    ``PART[EXISTENTIAL=YES, POLARITY=NEG]``). No cross-fire:
    ``May`` doesn't fire the wala-rule, and vice versa."""

    def test_may_polarity_is_pos_only(self) -> None:
        parses = parse_text("May aklat.")
        for _ct, fs, _astr, _diags in parses:
            if fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL":
                assert fs.feats.get("POLARITY") == "POS"

    def test_wala_polarity_is_neg_only(self) -> None:
        parses = parse_text("Walang aklat.")
        for _ct, fs, _astr, _diags in parses:
            if fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL":
                assert fs.feats.get("POLARITY") == "NEG"


# === Adjective-modified N composes with neg existential =============


class TestAdjectiveModifiedNegExistential:
    """ADJ + linker + N projects to N (Phase 5g Commit 2 NP-internal
    modifier) and is consumed by the wala rule unchanged: ``Walang
    matandang aklat`` "There's no old book"."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Walang malaking aklat.", "aklat"),
        ("Walang magandang bahay.", "bahay"),
    ])
    def test_adj_modified_neg(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma


# === No phantom NEG existentials =====================================


class TestNoPhantomNegExistentials:
    """Existing constructions don't acquire CLAUSE_TYPE=EXISTENTIAL
    + POLARITY=NEG from the new rules. Phase 4 hindi-negation
    composes with V-headed clauses producing POLARITY=NEG but
    CLAUSE_TYPE remains unset (not EXISTENTIAL)."""

    @pytest.mark.parametrize("sentence", [
        # Phase 4 negation
        "Hindi kumain ang aso.",
        # Phase 5g
        "Maganda ang bata.",
        # Phase 5h
        "Mas matalino siya.",
    ])
    def test_no_phantom_neg_existential(self, sentence: str) -> None:
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("CLAUSE_TYPE") != "EXISTENTIAL", (
                f"unexpected CLAUSE_TYPE=EXISTENTIAL on {sentence!r}: "
                f"{fs.feats}"
            )
