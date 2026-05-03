"""Phase 5f Commit 4: predicative cardinal.

The cardinal serves as the matrix predicate with a NOM-NP
pivot:

* ``Dalawa sila.`` "There are two of them."
* ``Tatlo ang anak ko.`` "I have three children" (lit.
  "three the child of-mine").
* ``Sandaan ang aklat.`` "A hundred books."

Structurally parallel to the Phase 5e Commit 26 comparative
parang rule, but with NUM[CARDINAL=YES] as the predicate.
F-structure shape:

* PRED = 'CARDINAL <SUBJ>'
* CARDINAL_VALUE = the count
* NUM = the cardinal's NUM
* SUBJ = the NOM-NP pivot

This commit consumes (a) simple cardinals from Phase 5f
Commit 1, (b) Spanish-borrowed cardinals from Phase 5f
Commit 2, and (c) compound cardinals from Phase 5f Commit 3
— a single new S rule covers all three cardinal classes.

Tests cover:

* Basic predicative cardinal with NOM-PRON pivot
  (``Dalawa sila``, ``Lima kami``).
* Predicative cardinal with full NOM-NP pivot
  (``Tatlo ang anak ko``, ``Lima ang isda``).
* Compound + Spanish cardinals as predicate (``Dalawampu ang
  bata``, ``Sandaan ang aklat``, ``Dos sila``).
* Verbless clitic placement: PRON-clitic SUBJ stays adjacent
  to the cardinal anchor (``Dalawa sila`` not ``*Dalawa . sila``).
* Negation composition: ``Hindi tatlo ang anak ko`` "I don't
  have three children".
* Negative (per §11.2): ``*Tatlo`` standalone (no SUBJ);
  ``*Tatlo ng anak ko`` (wrong case — predicative cardinal
  requires NOM-NP, not GEN).
* Regression: cardinal-NP-modifier surfaces from Commits 1-3
  still parse as before (``Kumain ako ng tatlong isda``).
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _predicative_parse(text: str) -> FStructure | None:
    """Find a parse with PRED='CARDINAL <SUBJ>'."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") == "CARDINAL <SUBJ>":
            return f
    return None


# === Basic: cardinal + PRON-clitic SUBJ ===================================


class TestPredicativeWithPron:
    """Cardinal + PRON-clitic SUBJ (PRON wrapped to NP[CASE=NOM]
    via the existing Phase 4 §7.8 PRON-NP rule)."""

    def test_dalawa_sila(self) -> None:
        # ``Dalawa sila.`` "There are two of them."
        # Note: PERS is stored as integer in pronouns.yaml and gets
        # filtered by _lex_equations (string-only); test asserts on
        # NUM and CASE only (per the Phase 5e Commit 20 PERS-filter
        # memo).
        f = _predicative_parse("Dalawa sila.")
        assert f is not None, "no predicative parse"
        assert f.feats.get("CARDINAL_VALUE") == "2"
        assert f.feats.get("NUM") == "PL"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("NUM") == "PL"

    def test_lima_kami(self) -> None:
        # ``Lima kami.`` "There are five of us (excl)."
        f = _predicative_parse("Lima kami.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "5"

    def test_tatlo_tayo(self) -> None:
        # ``Tatlo tayo.`` "There are three of us (incl)."
        f = _predicative_parse("Tatlo tayo.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "3"


# === Cardinal + full NOM-NP SUBJ ==========================================


class TestPredicativeWithNomNp:
    """Cardinal + NOM-NP SUBJ — the canonical inalienable-
    possession reading (``Tatlo ang anak ko`` "I have three
    children")."""

    def test_tatlo_ang_anak_ko(self) -> None:
        f = _predicative_parse("Tatlo ang anak ko.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "3"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "anak"
        assert subj.feats.get("CASE") == "NOM"
        # Possessor on the SUBJ (POSS slot from Phase 4 §7.8).
        # PERS is an integer-typed feature filtered by
        # _lex_equations; check NUM and CASE instead.
        poss = subj.feats.get("POSS")
        assert isinstance(poss, FStructure)
        assert poss.feats.get("NUM") == "SG"
        assert poss.feats.get("CASE") == "GEN"

    def test_lima_ang_isda(self) -> None:
        f = _predicative_parse("Lima ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "5"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "isda"

    def test_isa_ang_bata(self) -> None:
        # Singular (NUM=SG) cardinal as predicate.
        f = _predicative_parse("Isa ang bata.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "1"
        assert f.feats.get("NUM") == "SG"


# === Compound + Spanish predicative =======================================


class TestPredicativeCompoundSpanish:
    """The single S rule fires on simple, Spanish, and compound
    cardinals alike — all are NUM[CARDINAL=YES]."""

    def test_dalawampu_ang_bata(self) -> None:
        f = _predicative_parse("Dalawampu ang bata.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "20"

    def test_sandaan_ang_aklat(self) -> None:
        f = _predicative_parse("Sandaan ang aklat.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "100"

    def test_sanlibo_ang_isda(self) -> None:
        f = _predicative_parse("Sanlibo ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "1000"

    def test_dos_sila_spanish(self) -> None:
        f = _predicative_parse("Dos sila.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "2"

    def test_singko_ang_isda_spanish(self) -> None:
        f = _predicative_parse("Singko ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "5"


# === Verbless clitic placement ============================================


class TestPredicativeClitics:
    """The Phase 5e Commit 22 verbless clitic-placement pass uses
    the first non-clitic, non-NEG-PART, non-punctuation token as
    the cluster anchor. NUM[CARDINAL=YES] qualifies as a content
    anchor; PRON clitics (sila, kami, tayo) cluster post-anchor
    naturally."""

    def test_pron_stays_post_anchor(self) -> None:
        # ``Dalawa sila.`` already has the PRON in cluster
        # position; the pass leaves it alone.
        f = _predicative_parse("Dalawa sila.")
        assert f is not None
        # Sanity: the parse should be the standard predicative
        # shape, with the PRON-derived SUBJ in NOM-PL form. (PERS
        # is filtered as an integer; we check NUM / CASE only.)
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("NUM") == "PL"
        assert subj.feats.get("CASE") == "NOM"


# === Negation composition =================================================


class TestPredicativeNegation:
    """``hindi tatlo ang anak ko`` "I don't have three children".
    The Phase 4 §7.4 negation rule prepends ``hindi`` to a
    matrix S; predicative-cardinal S is no exception."""

    def test_hindi_tatlo_ang_anak_ko(self) -> None:
        rs = parse_text("Hindi tatlo ang anak ko.", n_best=10)
        assert rs, "no parse"
        # Find a parse with POLARITY=NEG and CARDINAL_VALUE=3.
        found = False
        for _, f, _, _ in rs:
            if (f.feats.get("POLARITY") == "NEG"
                    and f.feats.get("CARDINAL_VALUE") == "3"):
                found = True
                break
        assert found, "no NEG predicative-cardinal parse"


# === Negative fixtures (per §11.2) ========================================


class TestPredicativeNegative:

    def test_bare_cardinal_no_subj_fails(self) -> None:
        # ``*Tatlo.`` — predicative cardinal needs a SUBJ.
        rs = parse_text("Tatlo.", n_best=5)
        # Standalone cardinal isn't a complete utterance; should
        # produce no full parse (or only fragment / blocking parses).
        assert not any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            and not any(d.is_blocking() for d in diags)
            for _, f, _, diags in rs
        ), "*Tatlo. (no SUBJ) produced a clean predicative parse"

    def test_wrong_case_fails(self) -> None:
        # ``*Tatlo ng anak ko.`` — predicative cardinal requires
        # NOM-NP pivot, not GEN-NP.
        rs = parse_text("Tatlo ng anak ko.", n_best=5)
        # The predicative-cardinal rule shouldn't fire because
        # the SUBJ slot is NP[CASE=NOM], not NP[CASE=GEN].
        assert not any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        ), "*Tatlo ng anak ko produced a predicative parse"


# === Regression: NP-modifier still works ==================================


class TestPredicativeRegressions:
    """Adding the predicative S rule must not break the NP-modifier
    rules from Commits 1-3."""

    def test_np_modifier_still_works(self) -> None:
        # ``Kumain ako ng tatlong isda.`` — the canonical NP-modifier
        # use from Commit 1 must still parse with CARDINAL_VALUE on
        # the OBJ NP.
        rs = parse_text("Kumain ako ng tatlong isda.")
        assert rs
        f = rs[0][1]
        # Find any parse with EAT predicate and OBJ carrying the
        # cardinal info.
        found = False
        for _, fp, _, _ in parse_text("Kumain ako ng tatlong isda.", n_best=5):
            obj = fp.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("CARDINAL_VALUE") == "3":
                found = True
                break
        assert found, "NP-modifier parse regressed"

    def test_parang_with_cardinal_still_works(self) -> None:
        # ``Parang isang aso ang bata.`` — Commit 1 N-level rule
        # consumed by parang (Phase 5e Commit 26).
        rs = parse_text("Parang isang aso ang bata.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestPredicativeLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Dalawa sila.",
            "Tatlo ang anak ko.",
            "Lima ang isda.",
            "Isa ang bata.",
            "Dalawampu ang bata.",
            "Sandaan ang aklat.",
            "Dos sila.",
            "Singko ang isda.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
