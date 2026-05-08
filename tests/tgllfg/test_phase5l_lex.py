"""Phase 5l Commit 1: subordinator + sana lex inventory.

Roadmap §12.1 / plan-of-record §4.1. Fifteen new lex entries:

* **Conditional** (``kung`` / ``kapag`` / ``pag`` / ``sakali``):
  ``data/tgl/particles.yaml``, ``COMP_TYPE=COND``. ``kung`` is a
  second entry alongside the Phase 5i ``COMP_TYPE=INTERROG``
  reading; the chart picks via rule context (sentence-initial /
  matrix-adjunct vs post-V[ASK]).
* **Concessive** (``kahit`` / ``bagaman``): ``COMP_TYPE=CONC``.
* **Temporal** (``bago`` / ``pagkatapos`` / ``habang`` /
  ``hanggang`` / ``nang``): ``COMP_TYPE=TEMP_<X>`` with five
  distinct subord-type values.
* **Purpose** (``para`` / ``upang``): ``COMP_TYPE=PURP``.
  ``para`` is polysemous with the Phase 5e PREP[BENEFICIARY]
  (``para sa NP`` "for X"); polysemy resolved by POS at parse.
* **Reason** (``dahil``): ``COMP_TYPE=REAS``. Polysemous with
  Phase 5e PREP[REASON] (``dahil sa NP`` "because of X").
* **Counterfactual** (``sana``): 2P enclitic, NOT a subordinator.
  Adds ``COUNTERFACTUAL=YES`` to the host S; ``is_clitic: true``;
  cluster priority 195 in ``data/tgl/clitics.yaml``.

This commit is lex-only — no grammar / analyzer code changes.
The Phase 5l grammar rules (Commits 2-13) constrain on
``COMP_TYPE`` to fire on these surfaces. Pre-state (verified
2026-05-07): all 14 subordinator surfaces except ``kung``,
``para``, ``dahil`` were ``_UNK``; ``kung`` had only the
``COMP_TYPE=INTERROG`` reading; ``para`` and ``dahil`` had only
their PREP readings; ``sana`` was ``_UNK``.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Subordinator inventory ==========================================


SUBORDINATORS = [
    # (surface, comp_type, lemma)
    ("kung",       "COND",        "kung"),
    ("kapag",      "COND",        "kapag"),
    ("pag",        "COND",        "pag"),
    ("sakali",     "COND",        "sakali"),
    ("kahit",      "CONC",        "kahit"),
    ("bagaman",    "CONC",        "bagaman"),
    ("bago",       "TEMP_BEFORE", "bago"),
    ("pagkatapos", "TEMP_AFTER",  "pagkatapos"),
    ("habang",     "TEMP_WHILE",  "habang"),
    ("hanggang",   "TEMP_UNTIL",  "hanggang"),
    ("nang",       "TEMP_SINCE",  "nang"),
    ("para",       "PURP",        "para"),
    ("upang",      "PURP",        "upang"),
    ("dahil",      "REAS",        "dahil"),
]


class TestSubordinatorParts:
    """Each subordinator indexes as PART with the expected
    ``COMP_TYPE`` and ``LEMMA``. Polysemous surfaces (``kung``,
    ``para``, ``dahil``) keep their existing readings; the new
    entries surface alongside, gated by COMP_TYPE."""

    @pytest.mark.parametrize("surface,comp_type,lemma", SUBORDINATORS)
    def test_indexed_as_subord_part(
        self, surface: str, comp_type: str, lemma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        subord = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("COMP_TYPE") == comp_type
            and a.feats.get("LEMMA") == lemma
        ]
        assert len(subord) == 1, (
            f"expected exactly one PART[COMP_TYPE={comp_type}, "
            f"LEMMA={lemma}] for {surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


# === Polysemy preservation ===========================================


class TestKungPolysemy:
    """``kung`` carries both the Phase 5i INTERROG reading
    (indirect-Q complementizer) and the Phase 5l COND reading
    (conditional subordinator). Both must surface; the chart
    picks via rule context."""

    def test_kung_carries_both_comp_types(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kung"))
        comp_types = {
            a.feats.get("COMP_TYPE") for a in out
            if a.pos == "PART"
        }
        assert "COND" in comp_types
        assert "INTERROG" in comp_types


class TestParaPolysemy:
    """``para`` carries both the Phase 5e PREP[PREP_TYPE=BENEFICIARY]
    reading (``para sa NP`` "for X") and the Phase 5l
    PART[COMP_TYPE=PURP] reading (``para S`` "in order to S").
    Polysemy by POS — chart picks per immediate constituent."""

    def test_para_carries_prep_and_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("para"))
        positions = {(a.pos, a.feats.get("PREP_TYPE"),
                      a.feats.get("COMP_TYPE")) for a in out}
        assert ("PREP", "BENEFICIARY", None) in positions
        assert ("PART", None, "PURP") in positions


class TestDahilPolysemy:
    """``dahil`` carries both the Phase 5e PREP[REASON] reading
    (``dahil sa NP``) and the Phase 5l PART[COMP_TYPE=REAS]
    reading (``dahil S``)."""

    def test_dahil_carries_prep_and_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("dahil"))
        positions = {(a.pos, a.feats.get("PREP_TYPE"),
                      a.feats.get("COMP_TYPE")) for a in out}
        assert ("PREP", "REASON", None) in positions
        assert ("PART", None, "REAS") in positions


# === Register + subord-variant feats =================================


class TestRegisterFormal:
    """``bagaman`` and ``upang`` are formal-register variants of
    ``kahit`` and ``para``; they carry ``REGISTER=FORMAL``."""

    @pytest.mark.parametrize("surface", ["bagaman", "upang"])
    def test_register_formal(self, surface: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        formal = [
            a for a in out
            if a.pos == "PART" and a.feats.get("REGISTER") == "FORMAL"
        ]
        assert len(formal) == 1


class TestSakaliVariant:
    """``sakali`` "in case" carries SUBORD_VARIANT=IN_CASE
    alongside COMP_TYPE=COND. Future grammar rules can
    distinguish ``sakali`` from ``kung`` via the variant feat
    if semantic distinctions surface."""

    def test_sakali_in_case_variant(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sakali"))
        variants = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("SUBORD_VARIANT") == "IN_CASE"
        ]
        assert len(variants) == 1


class TestNangSinceVariant:
    """``nang`` carries SUBORD_VARIANT=SINCE alongside
    COMP_TYPE=TEMP_SINCE — gated so the multi-word
    ``mula nang`` rule (Commit 7) can pick this entry over any
    homonym readings."""

    def test_nang_since_variant(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("nang"))
        variants = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("SUBORD_VARIANT") == "SINCE"
        ]
        assert len(variants) == 1


# === sana counterfactual enclitic ====================================


class TestSanaCounterfactual:
    """``sana`` is a 2P enclitic (NOT a subordinator). It carries
    ``COUNTERFACTUAL=YES`` and ``is_clitic=true``; cluster
    priority 195 lives in ``data/tgl/clitics.yaml``."""

    def test_sana_indexed_as_clitic_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sana"))
        sana = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("COUNTERFACTUAL") == "YES"
        ]
        assert len(sana) == 1, (
            f"expected exactly one PART[COUNTERFACTUAL=YES] for 'sana'; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    def test_sana_is_clitic_flag(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sana"))
        clitics = [
            a for a in out
            if a.pos == "PART" and a.feats.get("is_clitic") is True
        ]
        assert len(clitics) == 1

    def test_sana_lemma(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sana"))
        sana = [a for a in out if a.lemma == "sana" and a.pos == "PART"]
        assert len(sana) == 1
