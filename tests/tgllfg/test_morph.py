from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tgllfg.core.common import Token
from tgllfg.morph import (
    Analyzer,
    MorphData,
    Operation,
    Particle,
    Pronoun,
    Root,
    VerbalCell,
    analyze_tokens,
    generate_form,
    load_morph_data,
)
from tgllfg.morph.sandhi import (
    attach_suffix,
    cv_reduplicate,
    d_to_r_intervocalic,
    first_cv,
    infix_after_first_consonant,
    is_sonorant_initial,
    is_vowel,
    nasal_substitute,
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
        # bili (vowel-final) + -in (vowel-initial) → bilihin.
        assert attach_suffix("bili", "in") == "bilihin"
        assert attach_suffix("bili", "an") == "bilihan"

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


# === Phase 2C sandhi rules ================================================

class TestSonorantInitial:
    def test_known_sonorants_match(self) -> None:
        for stem in ("linis", "mahal", "nakaw", "rud", "wala", "yaman"):
            assert is_sonorant_initial(stem), stem

    def test_ng_digraph_matches(self) -> None:
        assert is_sonorant_initial("nguya")

    def test_obstruents_do_not_match(self) -> None:
        # /h/ is excluded from the sonorant set: hampas + -in- → hinampas
        # is the standard form, not *ninampas.
        for stem in ("kain", "bili", "putol", "tahi", "dating", "gawa", "sulat", "hugot"):
            assert not is_sonorant_initial(stem), stem

    def test_vowel_initial_does_not_match(self) -> None:
        assert not is_sonorant_initial("alis")

    def test_empty(self) -> None:
        assert not is_sonorant_initial("")


class TestSonorantNiPrefix:
    """Sonorant-initial roots take the realis -in- as a ni- prefix."""

    def test_l_initial(self) -> None:
        assert infix_after_first_consonant("linis", "in") == "nilinis"

    def test_m_initial(self) -> None:
        assert infix_after_first_consonant("mahal", "in") == "nimahal"

    def test_n_initial(self) -> None:
        assert infix_after_first_consonant("nakaw", "in") == "ninakaw"

    def test_obstruent_unaffected(self) -> None:
        # /k/ is not a sonorant; canonical infix.
        assert infix_after_first_consonant("kain", "in") == "kinain"

    def test_um_infix_unaffected(self) -> None:
        # The rule is specific to the "in" infix; "um" still infixes.
        assert infix_after_first_consonant("linis", "um") == "luminis"


class TestOToURaising:
    """Stem-final /o/ raises to /u/ on suffix attachment."""

    def test_inom_in(self) -> None:
        assert attach_suffix("inom", "in") == "inumin"

    def test_putol_in(self) -> None:
        assert attach_suffix("putol", "in") == "putulin"

    def test_no_o_unaffected(self) -> None:
        assert attach_suffix("kain", "in") == "kainin"

    def test_o_only_in_non_final_syllable_unaffected(self) -> None:
        # Only the final-syllable vowel raises; an earlier /o/ stays.
        assert attach_suffix("oras", "an").startswith("oras")

    def test_redup_does_not_trigger_raising(self) -> None:
        # Reduplication alone is not a suffix; cv_redup keeps /o/.
        assert cv_reduplicate("inom") == "iinom"


class TestHighVowelDeletion:
    """Per-root opt-in: high vowel + V-suffix deletes the stem vowel."""

    def test_bili_in_with_flag(self) -> None:
        assert attach_suffix("bili", "in", high_vowel_deletion=True) == "bilhin"

    def test_bili_in_without_flag(self) -> None:
        # Default is h-epenthesis, not deletion.
        assert attach_suffix("bili", "in") == "bilihin"

    def test_low_vowel_unaffected(self) -> None:
        # /a/ stems take h-epenthesis even with the flag.
        assert attach_suffix("basa", "an", high_vowel_deletion=True) == "basahan"

    def test_consonant_final_unaffected(self) -> None:
        assert attach_suffix("kain", "in", high_vowel_deletion=True) == "kainin"


class TestDToRIntervocalic:
    """Post-processor: /d/ → /r/ when bracketed by vowels."""

    def test_simple_intervocalic(self) -> None:
        assert d_to_r_intervocalic("dadating") == "darating"

    def test_after_um_infix(self) -> None:
        assert d_to_r_intervocalic("dumadating") == "dumarating"

    def test_word_initial_unchanged(self) -> None:
        # Word-initial /d/ has no preceding vowel.
        assert d_to_r_intervocalic("dating") == "dating"

    def test_word_final_unchanged(self) -> None:
        assert d_to_r_intervocalic("lakad") == "lakad"

    def test_d_before_consonant_unchanged(self) -> None:
        assert d_to_r_intervocalic("daw") == "daw"

    def test_at_suffix_boundary(self) -> None:
        # bayad + -an: /d/ between /a/ and /a/.
        assert d_to_r_intervocalic("bayadan") == "bayaran"

    def test_uppercase_d_preserves_case(self) -> None:
        assert d_to_r_intervocalic("aDa") == "aRa"

    def test_empty(self) -> None:
        assert d_to_r_intervocalic("") == ""


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
    ("OV", "CTPL", "bibilihin"),     # vowel-hiatus: bili + -in → bilihin
    ("DV", "PFV",  "binilihan"),     # bili + -an → bilihan
    ("DV", "IPFV", "binibilihan"),
    ("DV", "CTPL", "bibilihan"),
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
        # Phase 4 §7.8: DEM=NO sentinel rides on non-demonstrative
        # DET/ADP entries so the standalone-demonstrative NP rule
        # (which expects DEM=YES) doesn't fire on plain ``ang``.
        assert det[0].feats == {"CASE": "NOM", "MARKER": "ANG", "DEM": "NO"}

    def test_ng_genitive(self, analyzer: Analyzer) -> None:
        out = analyzer.analyze_one(_tok("ng"))
        adp = [a for a in out if a.pos == "ADP"]
        assert adp
        assert adp[0].feats == {"CASE": "GEN", "MARKER": "NG", "DEM": "NO"}

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
        assert any(a.feats.get("LINK") == "NA" for a in out)


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

    @given(idx=st.integers(min_value=0, max_value=20))
    @settings(max_examples=21)
    def test_kain_round_trip(self, idx: int) -> None:
        # Iterate over every paradigm cell. Skip cells filtered out
        # by transitivity or affix_class for kain — those should not
        # generate a form for kain in the first place, so a "no
        # round-trip" outcome is correct rather than a failure.
        data = load_morph_data()
        analyzer = Analyzer(data)
        kain = next(r for r in data.roots if r.citation == "kain")
        if idx >= len(data.paradigm_cells):
            return
        cell = data.paradigm_cells[idx]
        if cell.transitivity and cell.transitivity != kain.transitivity:
            return
        if cell.affix_class and cell.affix_class not in kain.affix_class:
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
            paradigm_cells=[VerbalCell(
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
        # Generated form: sonorant /r/-initial root takes -in- as
        # ni- prefix (Phase 2C sonorant rule).
        out = analyzer.analyze_one(_tok("nirud"))
        assert any(a.lemma == "rud" and a.pos == "VERB" for a in out)
        # Particle and pronoun lookup.
        assert analyzer.analyze_one(_tok("foo"))[0].pos == "PART"
        assert analyzer.analyze_one(_tok("me"))[0].pos == "PRON"


# === Demo + percolation still pass through the new analyzer ==============

class TestDemoStillPasses:
    def test_kinain_sentence(self) -> None:
        from tgllfg.core.pipeline import parse_text
        results = parse_text("Kinain ng aso ang isda.")
        assert len(results) >= 1
        _, f, _, _ = results[0]
        assert f.feats["VOICE"] == "OV"
        assert f.feats["ASPECT"] == "PFV"
        # OBJ-AGENT after the Phase 5b OBJ-θ-in-grammar alignment.
        assert "SUBJ" in f.feats and "OBJ-AGENT" in f.feats


# === Nasal substitution sandhi ===========================================

class TestNasalSubstitute:
    def test_b_to_m(self) -> None:
        # Labial: b/p → m
        assert nasal_substitute("bili") == "mili"
        assert nasal_substitute("putol") == "mutol"

    def test_t_d_s_to_n(self) -> None:
        # Coronal: t/d/s → n
        assert nasal_substitute("tahi") == "nahi"
        assert nasal_substitute("dating") == "nating"
        assert nasal_substitute("sayaw") == "nayaw"

    def test_k_g_to_ng(self) -> None:
        # Velar: k/g → ng
        assert nasal_substitute("kuha") == "nguha"
        assert nasal_substitute("gawa") == "ngawa"

    def test_sonorant_initial_unchanged(self) -> None:
        # l, m, n, r, h, y, w — no substitution.
        for base in ("linis", "manok", "nais", "rito", "hilamos", "yari"):
            assert nasal_substitute(base) == base

    def test_vowel_initial_unchanged(self) -> None:
        for base in ("alis", "isda", "uod"):
            assert nasal_substitute(base) == base

    def test_empty_base(self) -> None:
        assert nasal_substitute("") == ""


# === New paradigm cells: mag-, mang-, maka- ==============================

MAG_FORMS = [
    # (root, voice, aspect, expected)
    ("linis",  "AV", "PFV",  "naglinis"),
    ("linis",  "AV", "IPFV", "naglilinis"),
    ("linis",  "AV", "CTPL", "maglilinis"),
    ("bigay",  "AV", "PFV",  "nagbigay"),
    ("bigay",  "AV", "IPFV", "nagbibigay"),
    ("bigay",  "AV", "CTPL", "magbibigay"),
    ("sulat",  "AV", "PFV",  "nagsulat"),
    ("sulat",  "AV", "IPFV", "nagsusulat"),
    ("sulat",  "AV", "CTPL", "magsusulat"),
    ("takbo",  "AV", "PFV",  "nagtakbo"),
    ("takbo",  "AV", "IPFV", "nagtatakbo"),
    ("takbo",  "AV", "CTPL", "magtatakbo"),
]


@pytest.mark.parametrize("root_name,voice,aspect,expected", MAG_FORMS)
def test_mag_paradigm(
    root_name: str,
    voice: str,
    aspect: str,
    expected: str,
    default_data: MorphData,
) -> None:
    root = next(r for r in default_data.roots if r.citation == root_name)
    cell = next(
        c for c in default_data.paradigm_cells
        if c.voice == voice and c.aspect == aspect and c.affix_class == "mag"
    )
    assert generate_form(root, cell) == expected


MANG_FORMS = [
    # (root, voice, aspect, expected) — exercises nasal substitution.
    ("bili",  "AV", "PFV",  "namili"),
    ("bili",  "AV", "IPFV", "namimili"),
    ("bili",  "AV", "CTPL", "mamimili"),
    ("kuha",  "AV", "PFV",  "nanguha"),
    ("kuha",  "AV", "IPFV", "nangunguha"),
    ("kuha",  "AV", "CTPL", "mangunguha"),
    ("tahi",  "AV", "PFV",  "nanahi"),
    ("tahi",  "AV", "IPFV", "nananahi"),
    ("tahi",  "AV", "CTPL", "mananahi"),
]


@pytest.mark.parametrize("root_name,voice,aspect,expected", MANG_FORMS)
def test_mang_paradigm(
    root_name: str,
    voice: str,
    aspect: str,
    expected: str,
    default_data: MorphData,
) -> None:
    root = next(r for r in default_data.roots if r.citation == root_name)
    cell = next(
        c for c in default_data.paradigm_cells
        if c.voice == voice and c.aspect == aspect and c.affix_class == "mang"
    )
    assert generate_form(root, cell) == expected


MAKA_FORMS = [
    # (root, voice, aspect, expected) — abilitative MOOD=ABIL.
    ("kain",  "AV", "PFV",  "nakakain"),
    ("kain",  "AV", "IPFV", "nakakakain"),
    ("kain",  "AV", "CTPL", "makakakain"),
    ("bili",  "AV", "PFV",  "nakabili"),
    ("bili",  "AV", "IPFV", "nakabibili"),
    ("bili",  "AV", "CTPL", "makabibili"),
    ("tulog", "AV", "PFV",  "nakatulog"),
    ("tulog", "AV", "IPFV", "nakatutulog"),
    ("tulog", "AV", "CTPL", "makatutulog"),
]


@pytest.mark.parametrize("root_name,voice,aspect,expected", MAKA_FORMS)
def test_maka_paradigm(
    root_name: str,
    voice: str,
    aspect: str,
    expected: str,
    default_data: MorphData,
) -> None:
    root = next(r for r in default_data.roots if r.citation == root_name)
    cell = next(
        c for c in default_data.paradigm_cells
        if c.voice == voice and c.aspect == aspect and c.affix_class == "maka"
    )
    assert generate_form(root, cell) == expected
    assert cell.mood == "ABIL"


# === affix_class filtering ===============================================

class TestAffixClassFiltering:
    def test_um_only_root_does_not_generate_mag_forms(
        self, analyzer: Analyzer
    ) -> None:
        # kain is in [um, in_oblig, an_oblig, i_oblig, maka] — no mag.
        # The hypothetical mag-style form "nagkain" must NOT be a
        # recognised verb.
        out = analyzer.analyze_one(_tok("nagkain"))
        # It might match a particle/pronoun (it doesn't); the test
        # is that no VERB analysis with kain-as-lemma comes back.
        verbs = [
            a for a in out
            if a.pos == "VERB" and a.lemma == "kain"
        ]
        assert verbs == []

    def test_mag_only_root_does_not_generate_um_forms(
        self, analyzer: Analyzer
    ) -> None:
        # linis has only [mag] — the -um- form "lumimis" must not exist.
        out = analyzer.analyze_one(_tok("lumimis"))
        verbs = [
            a for a in out if a.pos == "VERB" and a.lemma == "linis"
        ]
        assert verbs == []

    def test_root_with_two_av_classes_generates_both(
        self, analyzer: Analyzer
    ) -> None:
        # sulat is in [um, mag, ...] — both AV PFV forms exist.
        out_um = analyzer.analyze_one(_tok("sumulat"))
        out_mag = analyzer.analyze_one(_tok("nagsulat"))
        assert any(
            a.pos == "VERB" and a.lemma == "sulat"
            and a.feats.get("VOICE") == "AV"
            for a in out_um
        )
        assert any(
            a.pos == "VERB" and a.lemma == "sulat"
            and a.feats.get("VOICE") == "AV"
            for a in out_mag
        )

    def test_intransitive_root_skips_oblig_cells(
        self, analyzer: Analyzer
    ) -> None:
        # takbo is INTR — no OV/DV/IV cells should fire even if
        # the surface coincidentally matches.
        out = analyzer.analyze_one(_tok("tinakbo"))
        # If anything matches as a VERB lemma="takbo", it must not be
        # OV/DV/IV (those are TR-only).
        verbs = [a for a in out if a.pos == "VERB" and a.lemma == "takbo"]
        for v in verbs:
            assert v.feats.get("VOICE") not in ("OV", "DV", "IV")


# === Demonstratives ======================================================

class TestDemonstratives:
    @pytest.mark.parametrize("surface,deixis,case", [
        ("ito",   "PROX", "NOM"),
        ("nito",  "PROX", "GEN"),
        ("dito",  "PROX", "DAT"),
        ("iyan",  "MED",  "NOM"),
        ("niyan", "MED",  "GEN"),
        ("diyan", "MED",  "DAT"),
        ("iyon",  "DIST", "NOM"),
        ("niyon", "DIST", "GEN"),
        ("doon",  "DIST", "DAT"),
    ])
    def test_demonstrative(
        self,
        surface: str,
        deixis: str,
        case: str,
        analyzer: Analyzer,
    ) -> None:
        out = analyzer.analyze_one(_tok(surface))
        ds = [a for a in out if a.feats.get("DEIXIS") == deixis]
        assert ds, f"no demonstrative analysis for {surface!r}; got {out}"
        assert ds[0].feats.get("CASE") == case


# === Second-position enclitic cluster ====================================

class TestEnclitics:
    @pytest.mark.parametrize("surface,key,value", [
        ("pa",   "ASPECT_PART", "STILL"),
        ("ba",   "QUESTION",    True),
        ("daw",  "EVID",        "REPORT"),
        ("raw",  "EVID",        "REPORT"),
        ("din",  "ADV",         "ALSO"),
        ("rin",  "ADV",         "ALSO"),
        ("lang", "ADV",         "ONLY"),
        ("nga",  "EMPHATIC",    True),
        ("pala", "MIRATIVE",    True),
        ("kasi", "DISCOURSE",   "BECAUSE"),
        ("man",  "ADV",         "EVEN"),
        ("yata", "EPISTEMIC",   "PRESUMABLY"),
    ])
    def test_enclitic_lookup(
        self,
        surface: str,
        key: str,
        value: object,
        analyzer: Analyzer,
    ) -> None:
        out = analyzer.analyze_one(_tok(surface))
        match = [a for a in out if a.feats.get(key) == value]
        assert match, f"no analysis with {key}={value} for {surface!r}; got {out}"
        assert match[0].pos == "PART"

    def test_na_is_ambiguous(self, analyzer: Analyzer) -> None:
        # `na` is both the linker and the aspectual "already".
        out = analyzer.analyze_one(_tok("na"))
        feats = [a.feats for a in out]
        assert any(f.get("LINK") == "NA" for f in feats)
        assert any(f.get("ASPECT_PART") == "ALREADY" for f in feats)
