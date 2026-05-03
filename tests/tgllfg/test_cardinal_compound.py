"""Phase 5f Commit 3: compound cardinals 11-1000.

Lex-only addition. Adds 19 hand-authored compound cardinal
surfaces: teens (11-19), decades (20-90), 100, 1000. Same
syntactic distribution as the simple cardinals from Commits 1-2;
the cardinal-NP-modifier rules fire on these unchanged.

Orthography: single-token spellings throughout (``labingisa``
not ``labing-isa``; ``apatnapu`` not ``apat na pu``). Hyphenated
and three-word variants are attested in modern Tagalog but
require either a tokenizer pre-pass or NUM-internal grammar
rules — both deferred to follow-on commits (see plan §11.1
Group A item 3 and §18).

Tests cover:

* Morph: each compound analyses with pos=NUM and the right
  CARDINAL_VALUE / NUM features.
* Linker split: vowel-final compounds (most teens, all decades,
  sanlibo) split via ``split_linker_ng``; consonant-final
  (labingapat, labinganim, labinsiyam, sandaan) take standalone
  ``na``.
* Sweep: all 19 compounds in OBJ position with bata.
* Composition: cardinal in SUBJ (``Kumakanta ang dalawampung
  bata``) and DAT (``Pumunta ako sa sandaan na bahay``).
* Composition with parang: ``Parang sandaan na aso ang bata``
  (consonant-final compound) and ``Parang dalawampung aso ang
  bata`` (vowel-final).
* Coexistence with simple cardinals (Commits 1-2): all variants
  fire through the same grammar rules.
* Negative (per §11.2): ``*Kumain ako ng dalawampu bata`` (no
  linker between compound cardinal and N).
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import split_linker_ng, tokenize


def _compounds() -> list[tuple[str, str, str]]:
    """Yield (lemma, value, surface_with_link).

    Linker variant follows the surface phonology: vowel-final
    forms take bound ``-ng``; consonant-final ones take standalone
    ``na``.
    """
    return [
        # Teens 11-19
        ("labingisa",   "11", "labingisang"),
        ("labindalawa", "12", "labindalawang"),
        ("labintatlo",  "13", "labintatlong"),
        ("labingapat",  "14", "labingapat na"),
        ("labinlima",   "15", "labinlimang"),
        ("labinganim",  "16", "labinganim na"),
        ("labimpito",   "17", "labimpitong"),
        ("labingwalo",  "18", "labingwalong"),
        ("labinsiyam",  "19", "labinsiyam na"),
        # Decades 20-90
        ("dalawampu",   "20", "dalawampung"),
        ("tatlumpu",    "30", "tatlumpung"),
        ("apatnapu",    "40", "apatnapung"),
        ("limampu",     "50", "limampung"),
        ("animnapu",    "60", "animnapung"),
        ("pitumpu",     "70", "pitumpung"),
        ("walumpu",     "80", "walumpung"),
        ("siyamnapu",   "90", "siyamnapung"),
        # Hundreds and thousands
        ("sandaan",     "100",  "sandaan na"),
        ("sanlibo",     "1000", "sanlibong"),
    ]


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


# === Morph layer ==========================================================


class TestCompoundCardinalMorph:
    """Each compound cardinal analyses with pos=NUM and the right
    CARDINAL_VALUE feature. All compounds carry NUM=PL (no
    compound is singular)."""

    def test_all_compounds_analyze(self) -> None:
        for lemma, value, _ in _compounds():
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
            assert ma.feats.get("NUM") == "PL", (
                f"{lemma}: NUM expected 'PL', got {ma.feats.get('NUM')!r}"
            )


class TestCompoundLinkerSplit:
    """Vowel-final compounds split via -ng; consonant-final use na."""

    def test_dalawampung_splits(self) -> None:
        toks = tokenize("dalawampung bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["dalawampu", "-ng", "bata"]

    def test_labingisang_splits(self) -> None:
        toks = tokenize("labingisang bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["labingisa", "-ng", "bata"]

    def test_sanlibong_splits(self) -> None:
        toks = tokenize("sanlibong bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["sanlibo", "-ng", "bata"]

    def test_sandaan_does_not_split(self) -> None:
        # Consonant-final ('n'); needs standalone na.
        toks = tokenize("sandaan na bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["sandaan", "na", "bata"]

    def test_labingapat_does_not_split(self) -> None:
        toks = tokenize("labingapat na bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["labingapat", "na", "bata"]


# === All 19 compounds — sweep =============================================


class TestAllCompoundsSweep:
    """Each of the 19 compounds composes with bata in OBJ position."""

    def test_each_compound_in_obj(self) -> None:
        for lemma, value, surface_with_link in _compounds():
            text = f"Kumain ako ng {surface_with_link} bata."
            f = _first_obj(text)
            assert f is not None, f"no parse for {text!r}"
            assert f.feats.get("CARDINAL_VALUE") == value, (
                f"{lemma}: expected CARDINAL_VALUE={value!r}, got "
                f"{f.feats.get('CARDINAL_VALUE')!r} for {text!r}"
            )
            assert f.feats.get("NUM") == "PL", (
                f"{lemma}: expected NUM='PL', got {f.feats.get('NUM')!r} "
                f"for {text!r}"
            )
            assert f.feats.get("LEMMA") == "bata"


# === SUBJ / DAT positions =================================================


class TestCompoundInSubjAndDat:

    def test_dalawampung_bata_subj(self) -> None:
        # ``Kumakanta ang dalawampung bata.`` "Twenty children are
        # singing." — vowel-final compound in SUBJ.
        rs = parse_text("Kumakanta ang dalawampung bata.")
        assert rs
        f = rs[0][1]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CARDINAL_VALUE") == "20"
        assert subj.feats.get("LEMMA") == "bata"

    def test_sandaan_na_aso_subj(self) -> None:
        # ``Tumakbo ang sandaan na aso.`` "A hundred dogs ran." —
        # consonant-final compound in SUBJ.
        rs = parse_text("Tumakbo ang sandaan na aso.")
        assert rs
        f = rs[0][1]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("CARDINAL_VALUE") == "100"

    def test_sanlibong_kuwarto_dat(self) -> None:
        # DAT adjunct.
        rs = parse_text("Pumunta ako sa sanlibong kuwarto.", n_best=10)
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
                        and m.feats.get("CARDINAL_VALUE") == "1000"
                        and m.feats.get("LEMMA") == "kuwarto"):
                    found = True
                    break
            if found:
                break
        assert found, "no DAT parse with CARDINAL_VALUE=1000"


# === Composition with parang (uses N-level cardinal rule) =================


class TestCompoundWithParang:
    """The N-level cardinal rule from Commit 1 fires on compound
    cardinals too."""

    def test_parang_dalawampung_aso(self) -> None:
        rs = parse_text("Parang dalawampung aso ang bata.", n_best=10)
        assert rs, "no parse"
        found = False
        for _, f, _, _ in rs:
            if f.feats.get("PRED") != "LIKE <SUBJ, OBJ>":
                continue
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("CARDINAL_VALUE") == "20":
                found = True
                break
        assert found, "no parang+dalawampung parse with CARDINAL_VALUE=20"

    def test_parang_sandaan_na_aso(self) -> None:
        # Consonant-final compound with standalone na linker.
        rs = parse_text("Parang sandaan na aso ang bata.", n_best=10)
        assert rs, "no parse"
        found = False
        for _, f, _, _ in rs:
            if f.feats.get("PRED") != "LIKE <SUBJ, OBJ>":
                continue
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("CARDINAL_VALUE") == "100":
                found = True
                break
        assert found, "no parang+sandaan parse with CARDINAL_VALUE=100"


# === Coexistence with simple cardinals (Commits 1-2) ======================


class TestCompoundCoexistence:
    """Simple and compound cardinals share grammar; both produce
    the same f-structure shape."""

    def test_dalawa_and_dalawampu_distinct_values(self) -> None:
        f_2 = _first_obj("Kumain ako ng dalawang isda.")
        f_20 = _first_obj("Kumain ako ng dalawampung isda.")
        assert f_2 is not None and f_20 is not None
        assert f_2.feats.get("CARDINAL_VALUE") == "2"
        assert f_20.feats.get("CARDINAL_VALUE") == "20"
        # Same NUM, same lemma — different value only.
        assert f_2.feats.get("NUM") == f_20.feats.get("NUM") == "PL"
        assert f_2.feats.get("LEMMA") == f_20.feats.get("LEMMA") == "isda"


# === Negative fixtures (per §11.2) ========================================


class TestCompoundNegative:

    def test_no_linker_fails(self) -> None:
        # ``*Kumain ako ng dalawampu bata.`` — compound cardinal
        # without the linker. Same blocking as for simple cardinals.
        rs = parse_text("Kumain ako ng dalawampu bata.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "ungrammatical *dalawampu bata produced a non-blocking parse"

    def test_chained_compound_simple_blocked(self) -> None:
        # ``*Kumain ako ng dalawampung tatlong bata.`` — chained
        # compound + simple cardinals. Blocked by the chained-
        # cardinal constraints (¬ CARDINAL_VALUE on the head N
        # daughter).
        rs = parse_text("Kumain ako ng dalawampung tatlong bata.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "chained compound+simple produced a non-blocking parse"


# === LMT diagnostics clean ================================================


class TestCompoundLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumain ako ng labingisang isda.",
            "Kumain ako ng labingapat na isda.",
            "Kumain ako ng dalawampung isda.",
            "Kumain ako ng apatnapung isda.",
            "Kumain ako ng sandaan na isda.",
            "Kumain ako ng sanlibong isda.",
            "Kumakanta ang dalawampung bata.",
            "Tumakbo ang sandaan na aso.",
            "Parang dalawampung aso ang bata.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
