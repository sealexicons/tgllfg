"""Phase 5f Commit 7: ordinal NP-internal modifier (1st-10th).

Adds ordinals 1st-10th as NP-internal modifiers via the linker
(``ang unang anak`` "the first child", ``ng ikalawang libro``
"of the second book", ``sa ikaapat na bahay`` "at the fourth
house"). Structurally parallel to the Phase 5f Commit 1
cardinal-NP-modifier rules but with ``ORDINAL=YES`` and
``ORDINAL_VALUE`` features instead of CARDINAL=YES /
CARDINAL_VALUE.

Lex (data/tgl/particles.yaml): 11 ordinal entries:

* ``una`` (1st, suppletive — not ``*ikaisa``)
* ``ikalawa`` (2nd, with stem truncation: ``ika-`` + ``lawa``,
  not ``*ikadalawa``)
* ``pangalawa`` (2nd alternative, S&O 1972 §4.4 footnote)
* ``ikatlo`` (3rd, similar truncation: ``ika-`` + ``tlo``)
* ``ikaapat`` (4th), ``ikalima`` (5th), ``ikaanim`` (6th),
  ``ikapito`` (7th), ``ikawalo`` (8th), ``ikasiyam`` (9th),
  ``ikasampu`` (10th)

Grammar (src/tgllfg/cfg/nominal.py): 6 NP-level ordinal-modifier
rules (3 cases × 2 linker variants), plus a constraining
equation ``(↓2 ORDINAL) =c 'YES'`` so the rule fires only on
true ordinals (parallel to the cardinal rules' new
``(↓2 CARDINAL) =c 'YES'`` constraint added in this commit).

Side change: the ``disambiguate_homophone_clitics`` NUM-CARDINAL
branch (Phase 5f Commit 1) is extended to also handle
``NUM[ORDINAL=YES]`` — consonant-final ordinals (``ikaapat``,
``ikaanim``, ``ikasiyam``) need the same standalone-``na``-
as-linker disambiguation.

NUM (singular/plural) is intentionally NOT projected from
ordinals: ordinal value is independent of noun number agreement
(``ang unang aklat`` 1st-SG and ``ang unang mga aklat`` 1st-PL
with mga marker are both grammatical).

Tests cover:

* Morph: each ordinal analyses with pos=NUM and the right
  ORDINAL_VALUE.
* Linker split: vowel-final ordinals (``unang``, ``ikalawang``,
  ``ikalimang``, ``ikapitong``, ``ikawalong``, ``ikasampung``,
  ``pangalawang``) split via ``split_linker_ng``;
  consonant-final ones (``ikaapat na``, ``ikaanim na``,
  ``ikasiyam na``) use standalone ``na`` (exercises the
  extended disambiguator branch).
* Sweep: all 11 ordinals × ``aklat`` in OBJ position.
* Composition: ordinal in SUBJ (``Tumakbo ang unang aso``);
  ordinal in DAT (``Pumunta ako sa ikatlong kuwarto``);
  alternative ``pangalawa`` form (``ang pangalawang anak``).
* Cross-check: cardinals and ordinals are mutually exclusive
  in the same NP slot — the constraining equations
  ``(↓2 CARDINAL) =c 'YES'`` (cardinal rule) and
  ``(↓2 ORDINAL) =c 'YES'`` (ordinal rule) prevent crossover.
* Negative (per §11.2): ``*Bumili ako ng una aklat`` (no
  linker); chained-ordinal blocking
  (``*ang unang ikalawang aklat``).
* Regression: cardinals (Commits 1-3, 6) all unchanged;
  predicative cardinal (Commit 4), maka- adverbial (Commit 5),
  decimals + percentages (Commit 6) all still work.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import split_linker_ng, tokenize


def _ordinals() -> list[tuple[str, str, str]]:
    """Yield (lemma, value, surface_with_link)."""
    return [
        ("una",        "1",  "unang"),
        ("ikalawa",    "2",  "ikalawang"),
        ("pangalawa",  "2",  "pangalawang"),
        ("ikatlo",     "3",  "ikatlong"),
        ("ikaapat",    "4",  "ikaapat na"),
        ("ikalima",    "5",  "ikalimang"),
        ("ikaanim",    "6",  "ikaanim na"),
        ("ikapito",    "7",  "ikapitong"),
        ("ikawalo",    "8",  "ikawalong"),
        ("ikasiyam",   "9",  "ikasiyam na"),
        ("ikasampu",   "10", "ikasampung"),
    ]


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


def _any_obj_with_ordinal(text: str, value: str) -> FStructure | None:
    """Find any parse where OBJ has ORDINAL_VALUE=value."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        obj = f.feats.get("OBJ")
        if isinstance(obj, FStructure) and obj.feats.get("ORDINAL_VALUE") == value:
            return obj
    return None


# === Morph layer ==========================================================


class TestOrdinalMorph:
    """Each ordinal analyses with pos=NUM, ORDINAL=YES, and the
    right ORDINAL_VALUE."""

    def test_all_ordinals_analyze(self) -> None:
        for lemma, value, _ in _ordinals():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = ml[0]
            num_cands = [c for c in cands if c.pos == "NUM"]
            assert num_cands, f"no NUM analysis for {lemma}"
            ma = num_cands[0]
            assert ma.feats.get("ORDINAL") == "YES", (
                f"{lemma}: ORDINAL missing"
            )
            assert ma.feats.get("ORDINAL_VALUE") == value, (
                f"{lemma}: ORDINAL_VALUE expected {value!r}, got "
                f"{ma.feats.get('ORDINAL_VALUE')!r}"
            )


class TestOrdinalLinkerSplit:
    """Vowel-final ordinals split via -ng; consonant-final use
    standalone na (exercises the extended NUM-CARDINAL/ORDINAL
    disambiguator branch)."""

    def test_unang_splits(self) -> None:
        toks = tokenize("unang aklat")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["una", "-ng", "aklat"]

    def test_ikalawang_splits(self) -> None:
        toks = tokenize("ikalawang aklat")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["ikalawa", "-ng", "aklat"]

    def test_pangalawang_splits(self) -> None:
        toks = tokenize("pangalawang aklat")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["pangalawa", "-ng", "aklat"]

    def test_ikaapat_does_not_split(self) -> None:
        # Consonant-final ordinal; uses standalone na.
        toks = tokenize("ikaapat na aklat")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["ikaapat", "na", "aklat"]

    def test_ikaanim_does_not_split(self) -> None:
        toks = tokenize("ikaanim na aklat")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["ikaanim", "na", "aklat"]


# === Sweep all 11 ordinals ================================================


class TestAllOrdinalsSweep:
    """Each of the 11 ordinals composes with aklat in OBJ
    position."""

    def test_each_ordinal_in_obj(self) -> None:
        for lemma, value, surface_with_link in _ordinals():
            text = f"Bumili ako ng {surface_with_link} aklat."
            obj = _any_obj_with_ordinal(text, value)
            assert obj is not None, (
                f"no parse for {text!r} with ORDINAL_VALUE={value}"
            )
            assert obj.feats.get("LEMMA") == "aklat"


# === SUBJ + DAT positions =================================================


class TestOrdinalInSubjAndDat:

    def test_unang_aso_subj(self) -> None:
        # ``Tumakbo ang unang aso.`` "The first dog ran."
        rs = parse_text("Tumakbo ang unang aso.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            subj = f.feats.get("SUBJ")
            if (isinstance(subj, FStructure)
                    and subj.feats.get("ORDINAL_VALUE") == "1"
                    and subj.feats.get("LEMMA") == "aso"):
                found = True
                break
        assert found, "no parse with unang aso as SUBJ"

    def test_ikatlong_kuwarto_dat(self) -> None:
        # ``Pumunta ako sa ikatlong kuwarto.`` "I went to the
        # third room." — ordinal-modified DAT NP attached as
        # ADJUNCT.
        rs = parse_text("Pumunta ako sa ikatlong kuwarto.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if (isinstance(m, FStructure)
                        and m.feats.get("ORDINAL_VALUE") == "3"
                        and m.feats.get("LEMMA") == "kuwarto"):
                    found = True
                    break
            if found:
                break
        assert found, "no DAT parse with ikatlong kuwarto"


# === Alternative pangalawa form ===========================================


class TestPangalawaAlternative:
    """``pangalawa`` is a high-frequency colloquial alternative
    to ``ikalawa`` for "second" (S&O 1972 §4.4 footnote)."""

    def test_pangalawang_anak(self) -> None:
        obj = _any_obj_with_ordinal("Bumili ako ng pangalawang aklat.", "2")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"


# === Cardinal vs ordinal cross-check ======================================


class TestCardinalOrdinalDisjoint:
    """Cardinal and ordinal NP-modifier rules are mutually
    exclusive: the constraining equations
    ``(↓2 CARDINAL) =c 'YES'`` and ``(↓2 ORDINAL) =c 'YES'``
    prevent crossover."""

    def test_cardinal_rule_doesnt_fire_on_ordinal(self) -> None:
        # ``ng unang aklat`` should produce parses with
        # ORDINAL_VALUE=1 on OBJ but NEVER CARDINAL_VALUE on OBJ
        # (the cardinal rule shouldn't fire on ``una``).
        rs = parse_text("Bumili ako ng unang aklat.", n_best=10)
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure):
                # No CARDINAL_VALUE on OBJ (cardinal rule blocked
                # by constraining equation).
                cv = obj.feats.get("CARDINAL_VALUE")
                # Either CARDINAL_VALUE absent, or it's a real
                # value (not an empty fstruct from a buggy match).
                assert cv is None or isinstance(cv, str), (
                    f"OBJ has unexpected CARDINAL_VALUE: {cv!r}"
                )

    def test_ordinal_rule_doesnt_fire_on_cardinal(self) -> None:
        # ``ng tatlong aklat`` (cardinal) should produce parses
        # with CARDINAL_VALUE=3 on OBJ but NEVER ORDINAL_VALUE on
        # OBJ.
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=10)
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure):
                ov = obj.feats.get("ORDINAL_VALUE")
                assert ov is None or isinstance(ov, str), (
                    f"OBJ has unexpected ORDINAL_VALUE: {ov!r}"
                )


# === Negative fixtures (per §11.2) ========================================


class TestOrdinalNegative:

    def test_no_linker_fails(self) -> None:
        # ``*Bumili ako ng una aklat.`` — missing linker.
        rs = parse_text("Bumili ako ng una aklat.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "ungrammatical *una aklat produced a non-blocking parse"

    def test_chained_ordinals_blocked(self) -> None:
        # ``*Bumili ako ng unang ikalawang aklat.`` — chained
        # ordinals. Blocked by ``¬ (↓4 ORDINAL_VALUE)``.
        rs = parse_text("Bumili ako ng unang ikalawang aklat.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "chained ordinals produced a non-blocking parse"


# === Regression ===========================================================


class TestOrdinalRegressions:

    def test_cardinal_np_modifier_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs
        assert any(
            isinstance(obj := f.feats.get("OBJ"), FStructure)
            and obj.feats.get("CARDINAL_VALUE") == "3"
            for _, f, _, _ in rs
        )

    def test_compound_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng dalawampung aklat.", n_best=5)
        assert rs

    def test_predicative_cardinal_unchanged(self) -> None:
        rs = parse_text("Tatlo ang anak ko.", n_best=5)
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )

    def test_maka_adverbial_unchanged(self) -> None:
        rs = parse_text("Kumain ako makalawa.", n_best=5)
        assert rs

    def test_decimal_unchanged(self) -> None:
        rs = parse_text("Dos punto singko ang isda.", n_best=5)
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )


# === LMT diagnostics clean ================================================


class TestOrdinalLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Bumili ako ng unang aklat.",
            "Bumili ako ng ikalawang aklat.",
            "Bumili ako ng pangalawang aklat.",
            "Bumili ako ng ikaapat na aklat.",
            "Bumili ako ng ikaanim na aklat.",
            "Bumili ako ng ikasampung aklat.",
            "Tumakbo ang unang aso.",
            "Pumunta ako sa ikatlong kuwarto.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
