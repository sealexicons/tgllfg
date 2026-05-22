# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 5: formal ``nang higit`` ADJ-wrapper (§18 L41).

Closes §18.1 deferral L41 (formal ``nang higit`` comparison)
by adding an ADJ-wrapper rule

    ADJ → PART[LEMMA=nang] PART[COMP_PHRASE=HIGIT] ADJ
        (↑) = ↓3
        (↑ COMP_DEGREE) = 'COMPARATIVE'
        (↑ REGISTER) = 'FORMAL'
        (↓1 LEMMA) =c 'nang'
        (↓2 COMP_PHRASE) =c 'HIGIT'
        (↓3 PREDICATIVE) =c 'YES'

in ``cfg/nominal.py``, parallel to the Phase 5h Commit 3 ``mas``
ADJ-wrapper. Per Phase 5h §9.2: ``mas`` is the standard /
colloquial comparative; ``nang higit`` is the formal alternative
("rather more so / more than"). The wrapped ADJ rides into the
existing Phase 5g Commit 3 predicative-ADJ clause rule and the
Phase 5h Commit 4 kaysa wrap unchanged.
"""

import pytest

from tgllfg.core.common import CNode, FStructure
from tgllfg.core.pipeline import parse_text


def _ay_or_pred_parse(text: str) -> tuple[CNode, FStructure] | None:
    """Find a parse with PRED='ADJ <SUBJ>'."""
    parses = parse_text(text, n_best=10)
    for ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "ADJ <SUBJ>":
            return ct, fs
    return None


def _find_adj_with_comp(node: CNode) -> CNode | None:
    """Walk c-tree and return the first ADJ node (depth-first)
    whose label starts with 'ADJ' (post-Phase-6.C C3d the
    nang-higit ADJ-wrapper LHS advertises feats, so the label is
    ``ADJ[PREDICATIVE=true, COMP_DEGREE=COMPARATIVE]`` rather than
    bare ``ADJ``) and whose first equation marks
    COMP_DEGREE=COMPARATIVE."""
    if node.label.startswith("ADJ"):
        if any(
            "COMP_DEGREE) = 'COMPARATIVE'" in eq for eq in node.equations
        ):
            return node
    for c in node.children:
        found = _find_adj_with_comp(c)
        if found is not None:
            return found
    return None


# === Bare nang higit + ADJ predicative ==============================


class TestNangHigitPredicative:
    """``Nang higit + ADJ + NOM-NP`` parses as a formal-register
    comparative predicative-ADJ. The predicative-ADJ matrix is
    built by the existing Phase 5g Commit 3 rule on top of the
    ADJ-wrapped output."""

    @pytest.mark.parametrize("sentence,adj_lemma", [
        ("Nang higit matalino si Maria.",   "talino"),
        ("Nang higit maganda ang bata.",    "ganda"),
        ("Nang higit mabilis ang kabayo.",  "bilis"),
    ])
    def test_nang_higit_predicative(
        self, sentence: str, adj_lemma: str
    ) -> None:
        result = _ay_or_pred_parse(sentence)
        assert result is not None, (
            f"no predicative-ADJ parse for {sentence!r}"
        )
        ct, fs = result
        assert fs.feats.get("ADJ_LEMMA") == adj_lemma
        # The ADJ-wrapper output is a sub-c-tree node; verify
        # the wrapper fired by finding an ADJ with the
        # COMPARATIVE equation.
        wrapped = _find_adj_with_comp(ct)
        assert wrapped is not None, (
            "expected wrapped ADJ with COMP_DEGREE=COMPARATIVE"
        )


# === nang higit + ADJ + kaysa-PP ====================================


class TestNangHigitWithKaysa:
    """Phase 5h Commit 4 kaysa wrap composes on top of the
    ay-fronted-or-bare predicative-ADJ S; ``Nang higit matalino
    si Maria kaysa kay Juan.`` produces the same kaysa-PP
    attachment as the colloquial ``mas`` form."""

    def test_nang_higit_plus_kaysa(self) -> None:
        result = _ay_or_pred_parse(
            "Nang higit matalino si Maria kaysa kay Juan."
        )
        assert result is not None
        _ct, fs = result
        assert fs.feats.get("ADJ_LEMMA") == "talino"
        # kaysa-PP joins ADJUNCT with ROLE=STANDARD
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None
        standard = [
            m for m in adj if m.feats.get("ROLE") == "STANDARD"
        ]
        assert len(standard) == 1


# === Negation composition ===========================================


class TestNangHigitNegation:
    """Phase 4 §7.2 hindi-wrap composes with the formal
    comparative."""

    def test_hindi_nang_higit(self) -> None:
        result = _ay_or_pred_parse(
            "Hindi nang higit matalino si Maria."
        )
        assert result is not None
        _ct, fs = result
        assert fs.feats.get("POLARITY") == "NEG"
        assert fs.feats.get("ADJ_LEMMA") == "talino"


# === Regression: existing mas-comparative unaffected ==================


class TestMasUnaffected:
    """``Mas matalino si Maria.`` continues to parse via the
    Phase 5h Commit 3 mas-wrapper unchanged."""

    def test_mas_matalino_still_works(self) -> None:
        result = _ay_or_pred_parse("Mas matalino si Maria.")
        assert result is not None
        _ct, fs = result
        assert fs.feats.get("ADJ_LEMMA") == "talino"


# === Regression: numeric higit comparison unaffected ==================


class TestNumericHigitUnaffected:
    """The Phase 5f Commit 17 numeric ``higit sa N`` comparator
    fires only on NUM heads with DAT-NP standard; the new
    ``nang higit + ADJ`` wrapper has disjoint structure and
    doesn't perturb it."""

    def test_higit_sa_sampung_aklat(self) -> None:
        # ``higit sa sampung aklat`` "more than ten books" — NP
        # context with the Phase 5f Commit 17 numeric path.
        parses = parse_text("Bumili siya ng higit sa sampung aklat.")
        assert len(parses) >= 1
        # Top parse should be a BUY clause.
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("BUY")
