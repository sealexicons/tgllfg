"""Phase 5f Commit 6: decimals and percentages.

Decimals: Spanish-borrowed ``punto`` joins integer and fractional
cardinals (``dos punto singko`` "2.5", ``apat punto lima``
"4.5"). One new grammar rule:

    NUM[CARDINAL=YES] →
        NUM[CARDINAL=YES] PART[DECIMAL_SEP=YES] NUM[CARDINAL=YES]

The output is itself a ``NUM[CARDINAL=YES]`` so the existing
predicative-cardinal rule (Commit 4) and cardinal-NP-modifier
rules (Commit 1) accept it unchanged. CARDINAL_VALUE on the
matrix is the integer part (the LFG equation language has no
string concatenation to construct "2.5" literally); the
fractional part is recorded as ``FRACTIONAL_VALUE`` and the
matrix is marked ``DECIMAL=YES`` for downstream consumers.

Percentages: Spanish-borrowed ``porsiyento`` "percent" is added
as a NOUN with ``SEM_CLASS=PERCENTAGE``. The existing Phase 5f
Commit 1 cardinal-NP-modifier rule fires on
``dalawampung porsiyento`` "20%" / ``singkuwentang porsiyento``
"50%" / etc. without any new grammar. Predicative use
(``Dalawampung porsiyento ang interes`` "the interest is 20%")
needs an equational sentence rule and is deferred.

Side: parser fix in ``src/tgllfg/parse/earley.py``:
``_step`` now ALWAYS scans (in addition to predicting) when
the expected category is a non-terminal. A category can
legitimately be both a non-terminal (rule LHS) and a preterminal
(lex POS) — ``NUM`` here being the motivating case. Without
this fix, lex NUM tokens (``dos``, ``isa``, etc.) would never
be scanned once any rule has ``NUM[CARDINAL=YES]`` as LHS.
For purely non-terminal categories (S, NP, PP, AdvP) the scan
call is a no-op (no matching lex tokens).

Tests cover:

* Morph: ``punto`` analyses as PART with DECIMAL_SEP=YES;
  ``porsiyento`` as NOUN with SEM_CLASS=PERCENTAGE.
* Decimal constituent recognition (``dos punto singko`` parses
  as a NUM[CARDINAL=YES] inside a clause).
* Decimal in predicative position (``Dos punto singko ang
  isda``) — exercises Commit 4's predicative-cardinal rule.
* Compound + decimal compositions (``dalawampu punto singko``
  20.5; ``sandaan punto lima`` 100.5).
* Percentage as NP-modifier in OBJ position (``Bumili ako ng
  dalawampung porsiyento`` syntactically, even if semantically
  odd — ``porsiyento`` as the head N of a cardinal-modified NP).
* Negative (per §11.2): ``*Dos punto`` (decimal without
  fractional part) — should not parse as a complete decimal
  NUM. ``*Punto singko`` (decimal without integer part) —
  same.
* Regression: existing cardinals (simple, Spanish, compound,
  predicative) all unchanged.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _predicative_parse(text: str) -> FStructure | None:
    """Find a parse with PRED='CARDINAL <SUBJ>'."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") == "CARDINAL <SUBJ>":
            return f
    return None


# === Morph layer ==========================================================


class TestDecimalPercentMorph:

    def test_punto_is_decimal_separator(self) -> None:
        toks = tokenize("punto")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "PART"]
        assert cands
        assert cands[0].feats.get("DECIMAL_SEP") == "YES"

    def test_porsiyento_is_percentage_noun(self) -> None:
        toks = tokenize("porsiyento")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("SEM_CLASS") == "PERCENTAGE"


# === Decimal constituent in predicative position ==========================


class TestDecimalPredicative:
    """Decimals in the predicative-cardinal slot
    (``Dos punto singko ang isda`` "the fish are 2.5")."""

    def test_dos_punto_singko_ang_isda(self) -> None:
        f = _predicative_parse("Dos punto singko ang isda.")
        assert f is not None, "no predicative parse"
        # CARDINAL_VALUE projects from the integer part (the
        # equation language has no string concatenation to
        # construct "2.5" literally).
        assert f.feats.get("CARDINAL_VALUE") == "2"
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "isda"

    def test_tatlo_punto_lima_ang_isda(self) -> None:
        f = _predicative_parse("Tatlo punto lima ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "3"

    def test_apat_punto_anim_ang_aso(self) -> None:
        f = _predicative_parse("Apat punto anim ang aso.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "4"


# === Decimal with compound integer ========================================


class TestDecimalCompound:
    """Compound integer + simple fractional (``dalawampu punto
    singko`` 20.5; ``sandaan punto lima`` 100.5)."""

    def test_dalawampu_punto_singko(self) -> None:
        f = _predicative_parse("Dalawampu punto singko ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "20"

    def test_sandaan_punto_lima(self) -> None:
        f = _predicative_parse("Sandaan punto lima ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "100"

    def test_sanlibo_punto_apat(self) -> None:
        f = _predicative_parse("Sanlibo punto apat ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "1000"


# === Spanish + Spanish decimals ===========================================


class TestSpanishDecimals:
    """Spanish-borrowed integer + Spanish-borrowed fractional —
    canonical for prices (``dos punto singko`` 2.5 pesos)."""

    def test_dos_punto_singko_spanish(self) -> None:
        f = _predicative_parse("Dos punto singko ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "2"

    def test_kuwatro_punto_otso_spanish(self) -> None:
        f = _predicative_parse("Kuwatro punto otso ang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "4"


# === Percentages — cardinal-modified NP ===================================


class TestPercentagesAsNp:
    """``porsiyento`` is a NOUN with SEM_CLASS=PERCENTAGE; it
    appears as the head N of cardinal-modified NPs via the
    existing Commit 1 rules. Predicative percentage use
    (``Dalawampung porsiyento ang interes``) needs an equational
    sentence rule and is deferred."""

    def test_dalawampung_porsiyento_in_obj(self) -> None:
        # ``Bumili ako ng dalawampung porsiyento.`` "I bought
        # 20%." Syntactically valid (cardinal-modified NP as
        # OBJ); semantically odd but grammatical.
        rs = parse_text("Bumili ako ng dalawampung porsiyento.", n_best=10)
        assert rs, "no parse"
        # Find a parse with porsiyento as OBJ + CARDINAL_VALUE=20.
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if (isinstance(obj, FStructure)
                    and obj.feats.get("LEMMA") == "porsiyento"
                    and obj.feats.get("CARDINAL_VALUE") == "20"):
                found = True
                break
        assert found, "no parse with cardinal-modified porsiyento OBJ"

    def test_sandaan_na_porsiyento_in_obj(self) -> None:
        # Compound cardinal + porsiyento, consonant-final cardinal
        # uses standalone ``na`` linker.
        rs = parse_text("Bumili ako ng sandaan na porsiyento.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if (isinstance(obj, FStructure)
                    and obj.feats.get("LEMMA") == "porsiyento"
                    and obj.feats.get("CARDINAL_VALUE") == "100"):
                found = True
                break
        assert found, "no parse with sandaan na porsiyento OBJ"


# === Negative fixtures (per §11.2) ========================================


class TestDecimalPercentNegative:

    def test_decimal_without_fractional_fails(self) -> None:
        # ``*Dos punto.`` — decimal needs both integer and
        # fractional parts.
        rs = parse_text("Dos punto ang isda.", n_best=5)
        # No predicative parse should succeed for the decimal
        # interpretation (since the rule requires NUM PART NUM,
        # not NUM PART).
        assert not any(
            f.feats.get("DECIMAL") == "YES"
            for _, f, _, _ in rs
        ), "decimal without fractional produced a DECIMAL=YES parse"

    def test_decimal_without_integer_fails(self) -> None:
        # ``*Punto singko ang isda.`` — decimal needs an integer
        # before ``punto``.
        rs = parse_text("Punto singko ang isda.", n_best=5)
        # Either no parse, or no parse with the predicative-
        # cardinal shape.
        assert not any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            and f.feats.get("DECIMAL") == "YES"
            for _, f, _, _ in rs
        )

    def test_punto_doesnt_match_linker(self) -> None:
        # The decimal rule's middle daughter is
        # PART[DECIMAL_SEP=YES], constrained by ``(↓2 DECIMAL_SEP)
        # =c 'YES'``. The standalone -ng / na linkers are PART
        # tokens with LINK=NG / LINK=NA but NO DECIMAL_SEP, so
        # they should NOT match the decimal rule's middle slot.
        # Verifies the chained-cardinal blocking is preserved.
        # (Without the constraining equation, ``tatlong dalawang
        # bata`` would parse as a "decimal" tatlo.dalawa with bata
        # — semantically nonsense, structurally permitted by the
        # non-conflict pattern matcher alone.)
        rs = parse_text("Kumain ako ng tatlong dalawang bata.", n_best=10)
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure):
                assert obj.feats.get("DECIMAL") != "YES", (
                    "linker matched as DECIMAL_SEP — constraining "
                    "equation missing"
                )


# === Regression ===========================================================


class TestDecimalPercentRegressions:
    """Existing cardinal constructions are unaffected by the new
    rule, lex, and parser fix."""

    def test_av_intransitive_unchanged(self) -> None:
        rs = parse_text("Tumakbo ako.")
        assert rs

    def test_predicative_cardinal_unchanged(self) -> None:
        rs = parse_text("Tatlo ang anak ko.", n_best=5)
        assert rs
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )

    def test_cardinal_np_modifier_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs
        assert any(
            isinstance(obj := f.feats.get("OBJ"), FStructure)
            and obj.feats.get("CARDINAL_VALUE") == "3"
            for _, f, _, _ in rs
        )

    def test_compound_cardinal_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng dalawampung isda.", n_best=5)
        assert rs

    def test_chained_cardinals_still_blocked(self) -> None:
        # Critical regression: the new decimal rule + parser fix
        # must not unblock chained cardinals.
        rs = parse_text("Kumain ako ng tatlong dalawang bata.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "chained cardinals produced a non-blocking parse"


# === LMT diagnostics clean ================================================


class TestDecimalPercentLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Dos punto singko ang isda.",
            "Tatlo punto lima ang isda.",
            "Dalawampu punto singko ang isda.",
            "Sandaan punto lima ang isda.",
            "Bumili ako ng dalawampung porsiyento.",
            "Bumili ako ng sandaan na porsiyento.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
