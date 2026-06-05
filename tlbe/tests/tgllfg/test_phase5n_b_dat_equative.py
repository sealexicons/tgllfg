# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 6: DAT-standard equative (§18 L44).

Closes §18.1 deferral L44 (``Kasingganda kay Maria si Ana.``)
by adding a fourth equative-frame rule to ``cfg/clause.py``:

    S → ADJ[COMP_DEGREE=EQUATIVE] NP[CASE=DAT] NP[CASE=NOM]

mirroring the existing GEN-standard frame (``ADJ NP[CASE=GEN]
NP[CASE=NOM]``) one-for-one with ``CASE=DAT`` substituting for
``CASE=GEN``. The DAT-standard form is marginal in modern
Tagalog (GEN-standard is canonical per S&O 1972 / R&B 1986)
but attested.
"""

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _equative_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if fs.feats.get("PRED") == "ADJ <SUBJ>":
            return fs
    return None


def _standard_lemma(fs: FStructure) -> str | None:
    adj = fs.feats.get("ADJUNCT")
    if not adj:
        return None
    for m in adj:
        if m.feats.get("ROLE") == "EQUATIVE_STANDARD":
            v = m.feats.get("LEMMA")
            return v if isinstance(v, str) else None
    return None


# === DAT-standard equative ============================================


class TestDatStandardEquative:
    """``Kasingganda kay Maria si Ana.`` "Ana is as beautiful as
    Maria." — DAT-standard form, marginal but attested. The
    fourth equative-frame rule fires."""

    @pytest.mark.parametrize("sentence,adj_lemma,std_lemma,subj_lemma", [
        ("Kasingganda kay Maria si Ana.",     "ganda",       "maria", "ana"),
        ("Singganda kay Maria si Ana.",       "ganda",       "maria", "ana"),
        ("Kasingtalino kay Maria si Ana.",    "talino",      "maria", "ana"),
        ("Magkapareho kay Maria si Ana.",     "magkapareho", "maria", "ana"),
        ("Pareho kay Maria si Ana.",          "pareho",      "maria", "ana"),
    ])
    def test_dat_equative(
        self,
        sentence: str,
        adj_lemma: str,
        std_lemma: str,
        subj_lemma: str,
    ) -> None:
        fs = _equative_parse(sentence)
        assert fs is not None, f"no equative parse for {sentence!r}"
        assert fs.feats.get("ADJ_LEMMA") == adj_lemma
        assert _standard_lemma(fs) == std_lemma
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == subj_lemma
        assert subj.feats.get("CASE") == "NOM"


# === Regression: existing equative variants unaffected =================


class TestEquativeVariantsUnaffected:
    """The existing three Phase 5h Commit 6 equative frames
    continue to parse: NOM+GEN, GEN+NOM, two-NOM."""

    def test_gen_nom_canonical(self) -> None:
        # GEN+NOM canonical Schachter-Otanes shape.
        fs = _equative_parse("Kasingganda ni Maria si Ana.")
        assert fs is not None
        assert _standard_lemma(fs) == "maria"

    def test_two_nom_colloquial(self) -> None:
        # Two-NOM colloquial form. Per the convention, ↓2 is SUBJ
        # and ↓3 is the standard.
        fs = _equative_parse("Kasingganda si Maria si Ana.")
        assert fs is not None
        # The standard is the second NOM (Ana).
        assert _standard_lemma(fs) == "ana"

    def test_single_np_predicative_unaffected(self) -> None:
        # ``Kasingganda ang bahay.`` single-NP predicative-ADJ
        # via Phase 5g Commit 3.
        fs = _equative_parse("Kasingganda ang bahay.")
        assert fs is not None
        # No standard NP for the bare predicative form.
        assert _standard_lemma(fs) is None
