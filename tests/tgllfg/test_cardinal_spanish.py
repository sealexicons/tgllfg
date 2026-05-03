"""Phase 5f Commit 2: Spanish-borrowed cardinals 1-10.

Lex-only addition. The Phase 5f Commit 1 cardinal-NP-modifier
rules (NP-level + N-level) fire on these surfaces unchanged once
the lex entries are in place.

Spanish cardinals: ``uno`` (1), ``dos`` (2), ``tres`` (3),
``kuwatro`` (4), ``singko`` (5), ``sais`` (6), ``siyete`` (7),
``otso`` (8), ``nuwebe`` (9), ``dies`` (10). They dominate in
prices, ages, telephone numbers, and clock times; native forms
dominate in counting and ritual / ceremonial register.
(S&O 1972 §4; R&G 1981 dialogue corpus.)

The linker variant follows the borrowed surface form, not the
original Spanish:

* Vowel-final → bound ``-ng`` linker: ``uno``, ``kuwatro``,
  ``singko``, ``siyete``, ``otso``, ``nuwebe``.
* Consonant-final → standalone ``na`` linker: ``dos``, ``tres``,
  ``sais``, ``dies``.

Tests cover:

* Morph: each Spanish cardinal analyses with pos=NUM and the
  right CARDINAL_VALUE / NUM features.
* Linker split: vowel-final ``unong`` / ``kuwatrong`` / etc.
  split via ``split_linker_ng``; consonant-final ``dos`` /
  ``tres`` / etc. don't need splitting.
* Sweep: all 10 Spanish cardinals × bata in OBJ position.
* Composition with parang (``Parang dos aso ang bata`` "the
  child is like two dogs") — exercises the N-level cardinal
  rule from Commit 1.
* Coexistence: Spanish and native cardinals both work in the
  same suite (``ng dos isda`` and ``ng dalawang isda`` both
  parse with CARDINAL_VALUE=2).
* Negative (per §11.2 convention): ``*Kumain ako ng dos isda``
  with the consonant-final cardinal ``dos`` followed
  immediately by N (no linker) should fail.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import split_linker_ng, tokenize


def _spanish_cards() -> list[tuple[str, str, str, str]]:
    """Yield (lemma, value, num, surface_with_link)."""
    return [
        ("uno",     "1",  "SG", "unong"),
        ("dos",     "2",  "PL", "dos na"),
        ("tres",    "3",  "PL", "tres na"),
        ("kuwatro", "4",  "PL", "kuwatrong"),
        ("singko",  "5",  "PL", "singkong"),
        ("sais",    "6",  "PL", "sais na"),
        ("siyete",  "7",  "PL", "siyeteng"),
        ("otso",    "8",  "PL", "otsong"),
        ("nuwebe",  "9",  "PL", "nuwebeng"),
        ("dies",    "10", "PL", "dies na"),
    ]


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


# === Morph layer ==========================================================


class TestSpanishCardinalMorph:
    """Each Spanish cardinal lemma analyses with pos=NUM and the
    right CARDINAL_VALUE / NUM features."""

    def test_all_spanish_cardinals_analyze(self) -> None:
        for lemma, value, num, _ in _spanish_cards():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = ml[0]
            num_cands = [c for c in cands if c.pos == "NUM"]
            assert num_cands, f"no NUM analysis for {lemma}"
            ma = num_cands[0]
            assert ma.feats.get("CARDINAL") == "YES", f"{lemma}: CARDINAL missing"
            assert ma.feats.get("CARDINAL_VALUE") == value, (
                f"{lemma}: CARDINAL_VALUE expected {value!r}, got "
                f"{ma.feats.get('CARDINAL_VALUE')!r}"
            )
            assert ma.feats.get("NUM") == num, (
                f"{lemma}: NUM expected {num!r}, got {ma.feats.get('NUM')!r}"
            )


class TestSpanishCardinalLinkerSplit:
    """Bound -ng splits off vowel-final Spanish cardinals; the
    consonant-final ones don't need splitting."""

    def test_unong_splits(self) -> None:
        toks = tokenize("unong bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["uno", "-ng", "bata"]

    def test_kuwatrong_splits(self) -> None:
        toks = tokenize("kuwatrong bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["kuwatro", "-ng", "bata"]

    def test_otsong_splits(self) -> None:
        toks = tokenize("otsong bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["otso", "-ng", "bata"]

    def test_dos_does_not_split(self) -> None:
        # Consonant-final; nothing to split.
        toks = tokenize("dos na bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["dos", "na", "bata"]

    def test_dies_does_not_split(self) -> None:
        toks = tokenize("dies na bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["dies", "na", "bata"]


# === All 10 Spanish cardinals — sweep =====================================


class TestAllSpanishCardinalsSweep:
    """Each of the 10 Spanish cardinals composes with bata in OBJ
    position."""

    def test_each_spanish_cardinal_in_obj(self) -> None:
        for lemma, value, num, surface_with_link in _spanish_cards():
            text = f"Kumain ako ng {surface_with_link} bata."
            f = _first_obj(text)
            assert f is not None, f"no parse for {text!r}"
            assert f.feats.get("CARDINAL_VALUE") == value, (
                f"{lemma}: expected CARDINAL_VALUE={value!r}, got "
                f"{f.feats.get('CARDINAL_VALUE')!r} for {text!r}"
            )
            assert f.feats.get("NUM") == num, (
                f"{lemma}: expected NUM={num!r}, got "
                f"{f.feats.get('NUM')!r} for {text!r}"
            )
            assert f.feats.get("LEMMA") == "bata"


# === Composition with parang (uses N-level cardinal rule) =================


class TestSpanishCardinalWithParang:
    """``Parang dos aso ang bata`` "The child is like two dogs."
    The N-level cardinal rule (Commit 1) fires here — parang's
    standard slot wants a bare N."""

    def test_parang_dos_aso(self) -> None:
        rs = parse_text("Parang dos na aso ang bata.", n_best=10)
        assert rs, "no parse"
        # Find a parse with PRED='LIKE <SUBJ, OBJ>' and OBJ
        # carrying CARDINAL_VALUE=2.
        found = False
        for _, f, _, _ in rs:
            if f.feats.get("PRED") != "LIKE <SUBJ, OBJ>":
                continue
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("CARDINAL_VALUE") == "2":
                found = True
                break
        assert found, "no parang+cardinal parse with CARDINAL_VALUE=2"

    def test_parang_unong_aso(self) -> None:
        # Vowel-final Spanish cardinal with bound -ng.
        rs = parse_text("Parang unong aso ang bata.", n_best=10)
        assert rs, "no parse"
        found = False
        for _, f, _, _ in rs:
            if f.feats.get("PRED") != "LIKE <SUBJ, OBJ>":
                continue
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("CARDINAL_VALUE") == "1":
                found = True
                break
        assert found, "no parang+unong parse with CARDINAL_VALUE=1"


# === Coexistence: Spanish and native cardinals ============================


class TestSpanishNativeCoexistence:
    """Spanish and native cardinals are both available; choosing
    between them is a register / context decision, not a grammar
    one. Both parse into the same f-structure shape."""

    def test_dos_and_dalawa_same_value(self) -> None:
        f_dos = _first_obj("Kumain ako ng dos na isda.")
        f_dalawa = _first_obj("Kumain ako ng dalawang isda.")
        assert f_dos is not None and f_dalawa is not None
        assert f_dos.feats.get("CARDINAL_VALUE") == "2"
        assert f_dalawa.feats.get("CARDINAL_VALUE") == "2"
        # Same NUM, same lemma — only the originating surface differs.
        assert f_dos.feats.get("NUM") == f_dalawa.feats.get("NUM") == "PL"
        assert f_dos.feats.get("LEMMA") == f_dalawa.feats.get("LEMMA") == "isda"

    def test_uno_and_isa_same_value(self) -> None:
        f_uno = _first_obj("Kumain ako ng unong isda.")
        f_isa = _first_obj("Kumain ako ng isang isda.")
        assert f_uno is not None and f_isa is not None
        assert f_uno.feats.get("CARDINAL_VALUE") == "1"
        assert f_isa.feats.get("CARDINAL_VALUE") == "1"
        assert f_uno.feats.get("NUM") == f_isa.feats.get("NUM") == "SG"


# === Negative fixtures (per Phase 5f §11.2) ===============================


class TestSpanishCardinalNegative:
    """Per Phase 5f §11.2 negative-fixture convention."""

    def test_no_linker_fails(self) -> None:
        # ``*Kumain ako ng dos isda.`` — consonant-final cardinal
        # without the linker. The cardinal-NP-modifier rule
        # requires a PART[LINK=...]; without it, the rule does not
        # fire and no other rule consumes ``dos isda`` as an N or NP.
        rs = parse_text("Kumain ako ng dos isda.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "ungrammatical *dos isda produced a non-blocking parse"

    def test_chained_spanish_native_blocked(self) -> None:
        # ``*Kumain ako ng tatlong dos na bata.`` — chaining a
        # native cardinal with a Spanish one is still chained-
        # cardinals (different origin doesn't change the structural
        # ban). Blocked by ``¬ (↓4 CARDINAL_VALUE)`` on NP-level
        # rule and ``¬ (↓3 CARDINAL_VALUE)`` on N-level rule.
        rs = parse_text("Kumain ako ng tatlong dos na bata.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "chained native+Spanish cardinals produced a non-blocking parse"


# === LMT diagnostics clean ================================================


class TestSpanishCardinalLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumain ako ng unong isda.",
            "Kumain ako ng dos na isda.",
            "Kumain ako ng tres na isda.",
            "Kumain ako ng kuwatrong isda.",
            "Kumain ako ng singkong isda.",
            "Kumain ako ng sais na isda.",
            "Kumain ako ng siyeteng isda.",
            "Kumain ako ng otsong isda.",
            "Kumain ako ng nuwebeng isda.",
            "Kumain ako ng dies na isda.",
            "Parang dos na aso ang bata.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
