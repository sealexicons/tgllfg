from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tgllfg.common import Token
from tgllfg.morph import (
    Analyzer,
    MorphData,
    Operation,
    ParadigmCell,
    Particle,
    Pronoun,
    Root,
    analyze_tokens,
    generate_form,
    load_morph_data,
)
from tgllfg.morph.sandhi import (
    attach_suffix,
    cv_reduplicate,
    first_cv,
    infix_after_first_consonant,
    is_vowel,
)


# === Sandhi primitives ====================================================

class TestVowels:
    def test_basic(self) -> None:
        for c in "aeiou":
            assert is_vowel(c)
        for c in "bcdfg":
            assert not is_vowel(c)

    def test_uppercase(self) -> None:
        for c in "AEIOU":
            assert is_vowel(c)


class TestFirstCV:
    def test_consonant_initial(self) -> None:
        assert first_cv("kain") == "ka"
        assert first_cv("bili") == "bi"
        assert first_cv("sulat") == "su"

    def test_vowel_initial(self) -> None:
        # Vowel-initial: the redup target is the vowel alone.
        assert first_cv("alis") == "a"
        assert first_cv("isda") == "i"

    def test_empty(self) -> None:
        assert first_cv("") == ""


class TestInfixation:
    def test_consonant_initial(self) -> None:
        # -um- after first consonant: kain → k-um-ain.
        assert infix_after_first_consonant("kain", "um") == "kumain"
        # -in- realis: kain → k-in-ain.
        assert infix_after_first_consonant("kain", "in") == "kinain"

    def test_vowel_initial_becomes_prefix(self) -> None:
        # -um- on vowel-initial roots prefixes: alis → um-alis.
        assert infix_after_first_consonant("alis", "um") == "umalis"
        assert infix_after_first_consonant("isda", "in") == "inisda"

    def test_empty_base(self) -> None:
        assert infix_after_first_consonant("", "um") == "um"


class TestSuffixation:
    def test_consonant_final(self) -> None:
        assert attach_suffix("kain", "in") == "kainin"
        assert attach_suffix("kain", "an") == "kainan"

    def test_vowel_hiatus_repair(self) -> None:
        # bili (vowel-final) + -in (vowel-initial) → bilhin.
        assert attach_suffix("bili", "in") == "bilhin"
        assert attach_suffix("bili", "an") == "bilhan"

    def test_consonant_initial_suffix(self) -> None:
        # Hypothetical consonant-initial suffix: no hiatus.
        assert attach_suffix("bili", "ng") == "biling"

    def test_empty_suffix(self) -> None:
        assert attach_suffix("kain", "") == "kain"


class TestReduplication:
    def test_consonant_initial(self) -> None:
        assert cv_reduplicate("kain") == "kakain"
        assert cv_reduplicate("bili") == "bibili"
        assert cv_reduplicate("sulat") == "susulat"

    def test_vowel_initial(self) -> None:
        # Just-vowel redup for vowel-initial roots.
        assert cv_reduplicate("alis") == "aalis"


# === Generation: kain family across all 12 cells =========================

KAIN_FORMS = [
    # (voice, aspect, expected surface)
    ("AV", "PFV",  "kumain"),
    ("AV", "IPFV", "kumakain"),
    ("AV", "CTPL", "kakain"),
    ("OV", "PFV",  "kinain"),
    ("OV", "IPFV", "kinakain"),
    ("OV", "CTPL", "kakainin"),
    ("DV", "PFV",  "kinainan"),
    ("DV", "IPFV", "kinakainan"),
    ("DV", "CTPL", "kakainan"),
    ("IV", "PFV",  "ikinain"),
    ("IV", "IPFV", "ikinakain"),
    ("IV", "CTPL", "ikakain"),
]


@pytest.fixture(scope="module")
def default_data() -> MorphData:
    return load_morph_data()


@pytest.mark.parametrize("voice,aspect,expected", KAIN_FORMS)
def test_kain_paradigm(
    voice: str,
    aspect: str,
    expected: str,
    default_data: MorphData,
) -> None:
    root = next(r for r in default_data.roots if r.citation == "kain")
    cell = next(
        c for c in default_data.paradigm_cells
        if c.voice == voice and c.aspect == aspect
        and (not c.transitivity or c.transitivity == root.transitivity)
    )
    assert generate_form(root, cell) == expected


# === bili exercises vowel-hiatus sandhi ==================================

BILI_FORMS = [
    ("AV", "PFV",  "bumili"),
    ("AV", "IPFV", "bumibili"),
    ("AV", "CTPL", "bibili"),
    ("OV", "PFV",  "binili"),
    ("OV", "IPFV", "binibili"),
    ("OV", "CTPL", "bibilhin"),     # vowel-hiatus: bili + -in → bilhin
    ("DV", "PFV",  "binilhan"),     # bili + -an → bilhan
    ("DV", "IPFV", "binibilhan"),
    ("DV", "CTPL", "bibilhan"),
    ("IV", "PFV",  "ibinili"),
    ("IV", "IPFV", "ibinibili"),
    ("IV", "CTPL", "ibibili"),
]


@pytest.mark.parametrize("voice,aspect,expected", BILI_FORMS)
def test_bili_paradigm(
    voice: str,
    aspect: str,
    expected: str,
    default_data: MorphData,
) -> None:
    root = next(r for r in default_data.roots if r.citation == "bili")
    cell = next(
        c for c in default_data.paradigm_cells
        if c.voice == voice and c.aspect == aspect
        and (not c.transitivity or c.transitivity == root.transitivity)
    )
    assert generate_form(root, cell) == expected


# === Analyzer: surface → analysis ========================================

@pytest.fixture(scope="module")
def analyzer(default_data: MorphData) -> Analyzer:
    return Analyzer(default_data)


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


@pytest.mark.parametrize("voice,aspect,surface", KAIN_FORMS + BILI_FORMS)
def test_analyze_paradigm_form(
    voice: str, aspect: str, surface: str, analyzer: Analyzer
) -> None:
    out = analyzer.analyze_one(_tok(surface))
    matches = [
        a for a in out
        if a.pos == "VERB"
        and a.feats.get("VOICE") == voice
        and a.feats.get("ASPECT") == aspect
    ]
    assert matches, f"expected {voice}/{aspect} analysis for {surface!r}; got {out}"


def test_analyze_unknown_word_falls_back(analyzer: Analyzer) -> None:
    out = analyzer.analyze_one(_tok("xyzzy"))
    assert len(out) == 1
    assert out[0].pos == "_UNK"


# === Particle and pronoun lookup =========================================

class TestParticles:
    def test_ang_marker(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("ang"))
        det = [a for a in out if a.pos == "DET"]
        assert det
        assert det[0].feats == {"CASE": "NOM", "MARKER": "ANG"}

    def test_ng_genitive(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("ng"))
        adp = [a for a in out if a.pos == "ADP"]
        assert adp
        assert adp[0].feats == {"CASE": "GEN", "MARKER": "NG"}

    def test_si_personal_marker(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("si"))
        det = [a for a in out if a.pos == "DET"]
        assert det
        assert det[0].feats.get("HUMAN") is True
        assert det[0].feats.get("CASE") == "NOM"

    def test_negation(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("hindi"))
        assert any(a.feats.get("POLARITY") == "NEG" for a in out)

    def test_linker_na(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("na"))
        assert any(a.feats.get("LINKER") is True for a in out)


class TestPronouns:
    @pytest.mark.parametrize("surface,pers,num,case", [
        ("ako",   1, "SG", "NOM"),
        ("ko",    1, "SG", "GEN"),
        ("akin",  1, "SG", "DAT"),
        ("siya",  3, "SG", "NOM"),
        ("niya",  3, "SG", "GEN"),
        ("kanya", 3, "SG", "DAT"),
        ("sila",  3, "PL", "NOM"),
        ("nila",  3, "PL", "GEN"),
        ("kanila",3, "PL", "DAT"),
        ("kayo",  2, "PL", "NOM"),
        ("ninyo", 2, "PL", "GEN"),
        ("inyo",  2, "PL", "DAT"),
    ])
    def test_pronoun_lookup(
        self,
        surface: str,
        pers: int,
        num: str,
        case: str,
        analyzer: Analyzer,
    ) -> None:
        out = analyzer.analyze_one(_tok(surface))
        prons = [a for a in out if a.pos == "PRON"]
        assert prons
        assert prons[0].feats.get("PERS") == pers
        assert prons[0].feats.get("NUM") == num
        assert prons[0].feats.get("CASE") == case

    def test_clusivity_inclusive(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("tayo"))
        prons = [a for a in out if a.pos == "PRON"]
        assert prons[0].feats.get("CLUSV") == "INCL"

    def test_clusivity_exclusive(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("kami"))
        prons = [a for a in out if a.pos == "PRON"]
        assert prons[0].feats.get("CLUSV") == "EXCL"

    def test_2sg_clitic_and_full_both_present(
        self, analyzer: Analyzer
    ) -> None:
        # 2sg-NOM has both `ikaw` (full) and `ka` (clitic).
        ikaw = analyzer.analyze_one(_tok("ikaw"))
        ka = analyzer.analyze_one(_tok("ka"))
        assert any(a.pos == "PRON" for a in ikaw)
        assert any(a.pos == "PRON" for a in ka)


# === Noun lookup =========================================================

class TestNouns:
    def test_aso(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("aso"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert nouns and nouns[0].lemma == "aso"

    def test_isda(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("isda"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert nouns and nouns[0].lemma == "isda"


# === Module-level entry point ============================================

def test_module_entry_point_works() -> None:
    out = analyze_tokens([_tok("kinain"), _tok("ng"), _tok("aso")])
    assert len(out) == 3
    # First token has at least one VERB analysis.
    assert any(a.pos == "VERB" for a in out[0])
    assert any(a.pos == "ADP" for a in out[1])
    assert any(a.pos == "NOUN" for a in out[2])


# === Round-trip property test ============================================

class TestRoundTrip:
    """Every (root, cell) generation must analyse back to a record
    whose features include the cell's voice/aspect."""

    @given(idx=st.integers(min_value=0, max_value=11))
    @settings(max_examples=12)
    def test_kain_round_trip(self, idx: int) -> None:
        # Pre-build the expected forms; compare round-trip per index.
        data = load_morph_data()
        analyzer = Analyzer(data)
        kain = next(r for r in data.roots if r.citation == "kain")
        cell = data.paradigm_cells[idx]
        if cell.transitivity and cell.transitivity != kain.transitivity:
            return
        surface = generate_form(kain, cell)
        out = analyzer.analyze_one(_tok(surface))
        kept = [
            a for a in out
            if a.lemma == "kain"
            and a.feats.get("VOICE") == cell.voice
            and a.feats.get("ASPECT") == cell.aspect
        ]
        assert kept, (
            f"round-trip failed for {kain.citation} {cell.voice}/"
            f"{cell.aspect} → {surface!r}; got {out}"
        )


# === Loader: hand-crafted MorphData ======================================

class TestAnalyzerWithCustomData:
    def test_minimal_data(self) -> None:
        data = MorphData(
            roots=[Root(citation="rud", pos="VERB", transitivity="TR")],
            paradigm_cells=[ParadigmCell(
                voice="OV", aspect="PFV", mood="IND", transitivity="TR",
                operations=[Operation(op="infix", value="in")],
            )],
            particles=[Particle(
                surface="foo", pos="PART", feats={"BAR": True},
            )],
            pronouns=[Pronoun(
                surface="me", feats={"PERS": 1, "NUM": "SG", "CASE": "NOM"},
            )],
        )
        analyzer = Analyzer(data)
        # Generated form: r-in-ud → rinud.
        out = analyzer.analyze_one(_tok("rinud"))
        assert any(a.lemma == "rud" and a.pos == "VERB" for a in out)
        # Particle and pronoun lookup.
        assert analyzer.analyze_one(_tok("foo"))[0].pos == "PART"
        assert analyzer.analyze_one(_tok("me"))[0].pos == "PRON"


# === Demo + percolation still pass through the new analyzer ==============

class TestDemoStillPasses:
    def test_kinain_sentence(self) -> None:
        from tgllfg.pipeline import parse_text
        results = parse_text("Kinain ng aso ang isda.")
        assert len(results) >= 1
        _, f, _, _ = results[0]
        assert f.feats["VOICE"] == "OV"
        assert f.feats["ASPECT"] == "PFV"
        assert "SUBJ" in f.feats and "OBJ" in f.feats
