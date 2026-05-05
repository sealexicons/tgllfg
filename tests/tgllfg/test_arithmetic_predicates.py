"""Phase 5f Commit 9: arithmetic predicates (Group D).

Word-form arithmetic: ``Dalawa dagdag tatlo ay lima`` "2+3=5",
``Sampu bawas tatlo ay pito`` "10-3=7", ``Dalawa beses tatlo
ay anim`` "2*3=6", ``Anim hati sa dalawa ay tatlo`` "6/2=3".

Lex (data/tgl/particles.yaml): 4 operator PARTs:

* ``dagdag`` PART, OP=PLUS (also exists as VERB root in roots
  for "add to" — bare ``dagdag`` is _UNK from the verbal
  pipeline, so no ambiguity).
* ``bawas`` PART, OP=MINUS (similarly).
* ``beses`` PART, OP=TIMES (coexists with the existing NOUN
  ``beses`` SEM_CLASS=FREQUENCY from Phase 5f Commit 5; the
  PART reading fires in arithmetic-operator positions, the
  NOUN reading in periphrastic-frequency NP positions).
* ``hati`` PART, OP=DIVIDE.

Grammar (src/tgllfg/cfg/clause.py): 4 S rules:

* Plus / minus / times: ``S → NUM[CARDINAL=YES] PART
  NUM[CARDINAL=YES] PART[LINK=AY] NUM[CARDINAL=YES]`` (5
  daughters), with ``(↓2 OP) =c '<OP>'`` constraining
  equation per OP.
* Division: ``S → NUM[CARDINAL=YES] PART ADP[CASE=DAT]
  NUM[CARDINAL=YES] PART[LINK=AY] NUM[CARDINAL=YES]`` (6
  daughters; the ``sa`` is a real DAT marker).

F-structure shape:

* PRED       = 'ARITHMETIC' (no argument list — arithmetic
  doesn't have a conventional SUBJ; using ``<SUBJ>`` would
  trigger Subject Condition / Completeness failures).
* OP         = 'PLUS' | 'MINUS' | 'TIMES' | 'DIVIDE'
* OPERAND_1  = first cardinal's CARDINAL_VALUE
* OPERAND_2  = second cardinal's CARDINAL_VALUE
* RESULT     = result cardinal's CARDINAL_VALUE

Tests cover:

* Morph: each operator analyses with pos=PART and the right OP.
* Plus / minus / times: each parses with the right OP feature
  and operand / result values.
* Division: ``Anim hati sa dalawa ay tatlo`` parses with
  OP=DIVIDE and operands wired correctly.
* Multiple value combinations across all 4 operators.
* Coexistence of beses NOUN vs beses PART:
  ``dalawang beses`` (NP-modifier reading via Commit 5 lex)
  AND ``dalawa beses tatlo ay anim`` (operator reading) both
  work.
* Negative (per §11.2):
  - ``*Dalawa dagdag tatlo lima`` (missing ``ay``)
  - ``*Anim hati dalawa ay tatlo`` (DIVIDE missing the
    DAT-marker ``sa``)
* Regression: cardinals + ordinals + fractions all unchanged;
  beses-as-NOUN periphrastic frequency unchanged.
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _arithmetic_parse(text: str) -> dict | None:
    """Find a parse with PRED='ARITHMETIC' and return its matrix
    feats as a plain dict (or None)."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") == "ARITHMETIC":
            return dict(f.feats)
    return None


# === Morph layer ==========================================================


class TestArithmeticOperatorMorph:
    """Each operator analyses with pos=PART and the right OP."""

    def test_dagdag_plus(self) -> None:
        toks = tokenize("dagdag")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "PART"]
        assert cands
        assert cands[0].feats.get("OP") == "PLUS"

    def test_bawas_minus(self) -> None:
        toks = tokenize("bawas")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "PART"]
        assert cands
        assert cands[0].feats.get("OP") == "MINUS"

    def test_beses_times(self) -> None:
        toks = tokenize("beses")
        ml = analyze_tokens(toks)
        # beses has BOTH a PART (TIMES) and NOUN (FREQUENCY) reading.
        part_cands = [c for c in ml[0] if c.pos == "PART"]
        noun_cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert part_cands, "no PART reading for beses"
        assert noun_cands, "no NOUN reading for beses (regression)"
        assert part_cands[0].feats.get("OP") == "TIMES"
        assert noun_cands[0].feats.get("SEM_CLASS") == "FREQUENCY"

    def test_hati_divide(self) -> None:
        toks = tokenize("hati")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "PART"]
        assert cands
        assert cands[0].feats.get("OP") == "DIVIDE"


# === Addition (PLUS) ======================================================


class TestArithmeticPlus:

    def test_dalawa_dagdag_tatlo_ay_lima(self) -> None:
        # 2+3=5
        f = _arithmetic_parse("Dalawa dagdag tatlo ay lima.")
        assert f is not None, "no ARITHMETIC parse"
        assert f.get("OP") == "PLUS"
        assert f.get("OPERAND_1") == "2"
        assert f.get("OPERAND_2") == "3"
        assert f.get("RESULT") == "5"

    def test_apat_dagdag_apat_ay_walo(self) -> None:
        # 4+4=8
        f = _arithmetic_parse("Apat dagdag apat ay walo.")
        assert f is not None
        assert f.get("OP") == "PLUS"
        assert f.get("OPERAND_1") == "4"
        assert f.get("OPERAND_2") == "4"
        assert f.get("RESULT") == "8"

    def test_lima_dagdag_lima_ay_sampu(self) -> None:
        # 5+5=10
        f = _arithmetic_parse("Lima dagdag lima ay sampu.")
        assert f is not None
        assert f.get("OPERAND_1") == "5"
        assert f.get("RESULT") == "10"


# === Subtraction (MINUS) ==================================================


class TestArithmeticMinus:

    def test_sampu_bawas_tatlo_ay_pito(self) -> None:
        # 10-3=7
        f = _arithmetic_parse("Sampu bawas tatlo ay pito.")
        assert f is not None
        assert f.get("OP") == "MINUS"
        assert f.get("OPERAND_1") == "10"
        assert f.get("OPERAND_2") == "3"
        assert f.get("RESULT") == "7"

    def test_walo_bawas_lima_ay_tatlo(self) -> None:
        # 8-5=3
        f = _arithmetic_parse("Walo bawas lima ay tatlo.")
        assert f is not None
        assert f.get("OP") == "MINUS"
        assert f.get("RESULT") == "3"


# === Multiplication (TIMES) ===============================================


class TestArithmeticTimes:

    def test_dalawa_beses_tatlo_ay_anim(self) -> None:
        # 2*3=6
        f = _arithmetic_parse("Dalawa beses tatlo ay anim.")
        assert f is not None
        assert f.get("OP") == "TIMES"
        assert f.get("OPERAND_1") == "2"
        assert f.get("OPERAND_2") == "3"
        assert f.get("RESULT") == "6"

    def test_lima_beses_dalawa_ay_sampu(self) -> None:
        # 5*2=10
        f = _arithmetic_parse("Lima beses dalawa ay sampu.")
        assert f is not None
        assert f.get("OP") == "TIMES"
        assert f.get("RESULT") == "10"


# === Division (DIVIDE) ====================================================


class TestArithmeticDivide:
    """Division has 6 daughters because ``hati`` takes a sa-marked
    divisor (``hati sa dalawa`` "divided by two")."""

    def test_anim_hati_sa_dalawa_ay_tatlo(self) -> None:
        # 6/2=3
        f = _arithmetic_parse("Anim hati sa dalawa ay tatlo.")
        assert f is not None
        assert f.get("OP") == "DIVIDE"
        assert f.get("OPERAND_1") == "6"
        assert f.get("OPERAND_2") == "2"
        assert f.get("RESULT") == "3"

    def test_sampu_hati_sa_lima_ay_dalawa(self) -> None:
        # 10/5=2
        f = _arithmetic_parse("Sampu hati sa lima ay dalawa.")
        assert f is not None
        assert f.get("OP") == "DIVIDE"
        assert f.get("OPERAND_1") == "10"
        assert f.get("OPERAND_2") == "5"
        assert f.get("RESULT") == "2"


# === Coexistence: beses NOUN vs beses PART ================================


class TestBesesCoexistence:
    """``beses`` has both a NOUN reading (Phase 5f Commit 5
    SEM_CLASS=FREQUENCY) and a PART reading (this commit,
    OP=TIMES). Both should fire in their respective contexts
    without interference."""

    def test_beses_as_noun_periphrastic_frequency(self) -> None:
        # ``dalawang beses`` (frequency NP) — uses the NOUN
        # reading via the Phase 5f Commit 1 cardinal-NP-modifier
        # rule.
        rs = parse_text("Bumili ako ng dalawang beses.", n_best=10)
        assert rs, "no parse for periphrastic-frequency NP"

    def test_beses_as_part_arithmetic(self) -> None:
        # ``dalawa beses tatlo ay anim`` — uses the PART reading
        # via the arithmetic rule.
        f = _arithmetic_parse("Dalawa beses tatlo ay anim.")
        assert f is not None
        assert f.get("OP") == "TIMES"


# === Negative fixtures (per §11.2) ========================================


class TestArithmeticNegative:

    def test_missing_ay(self) -> None:
        # ``*Dalawa dagdag tatlo lima.`` — missing ``ay``.
        rs = parse_text("Dalawa dagdag tatlo lima.", n_best=5)
        # No ARITHMETIC parse (the rule requires PART[LINK=AY]
        # in position 4).
        assert not any(
            f.feats.get("PRED") == "ARITHMETIC"
            for _, f, _, _ in rs
        )

    def test_division_missing_sa(self) -> None:
        # ``*Anim hati dalawa ay tatlo.`` — division requires
        # ``sa`` (DAT marker) on the divisor.
        rs = parse_text("Anim hati dalawa ay tatlo.", n_best=5)
        # The 5-daughter PLUS/MINUS/TIMES rules might match
        # (treating ``hati`` as some operator) but the
        # constraining equation ``(↓2 OP) =c '<OP>'`` would only
        # accept hati for OP=DIVIDE. The division rule (6
        # daughters) requires ADP[CASE=DAT] in position 3; without
        # it, no ARITHMETIC parse.
        assert not any(
            f.feats.get("PRED") == "ARITHMETIC"
            and f.feats.get("OP") == "DIVIDE"
            for _, f, _, _ in rs
        )


# === Regression ===========================================================


class TestArithmeticRegressions:

    def test_predicative_cardinal_unchanged(self) -> None:
        rs = parse_text("Tatlo ang anak ko.", n_best=5)
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )

    def test_cardinal_np_modifier_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs

    def test_ordinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng unang aklat.", n_best=5)
        assert rs

    def test_fraction_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng dalawang kalahati.", n_best=5)
        assert rs

    def test_decimal_unchanged(self) -> None:
        rs = parse_text("Dos punto singko ang isda.", n_best=5)
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )


# === LMT diagnostics clean ================================================


class TestArithmeticLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Dalawa dagdag tatlo ay lima.",
            "Apat dagdag lima ay siyam.",
            "Sampu bawas tatlo ay pito.",
            "Walo bawas dalawa ay anim.",
            "Dalawa beses tatlo ay anim.",
            "Lima beses dalawa ay sampu.",
            "Anim hati sa dalawa ay tatlo.",
            "Sampu hati sa lima ay dalawa.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
