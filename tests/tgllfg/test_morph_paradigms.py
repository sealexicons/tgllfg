"""Paired surface↔analysis assertions across the seed verb lexicon.

Each entry is ``(root, voice, aspect, expected_surface)`` for a cell
the root participates in (per its ``affix_class``). The full table
gives ~300 paired assertions covering the kain/bili anchors plus 25+
additional verbs spanning the diversity of affix classes — -um-/mag-
alternations, mang- distributive (with nasal substitution), maka-
abilitative, intransitives, vowel-initial roots, and consonant-
initial roots that exercise the standard sandhi.

Citations: Ramos & Bautista 1986 (R&B), Schachter & Otanes 1972 (S&O)
verbal chart, and Kroeger 1993 ch. 4. Where R&B and S&O attest a form
in a different shape, the form here matches R&B (the more recent and
more comprehensively paradigmatized source) and the discrepancy is
recorded in ``docs/analysis-choices.md``.
"""

from __future__ import annotations

import pytest

from tgllfg.common import Token
from tgllfg.morph import Analyzer, generate_form, load_morph_data


# === Paired assertion table ==============================================
#
# Format: (root, voice, aspect, expected_surface).
# Mood is IND for everything except maka- (ABIL) — checked separately.

# -- -um- class transitives ----------------------------------------------

UM_PARADIGM_FORMS = [
    # kain — eat
    ("kain", "AV", "PFV",  "kumain"),
    ("kain", "AV", "IPFV", "kumakain"),
    ("kain", "AV", "CTPL", "kakain"),
    ("kain", "OV", "PFV",  "kinain"),
    ("kain", "OV", "IPFV", "kinakain"),
    ("kain", "OV", "CTPL", "kakainin"),
    ("kain", "DV", "PFV",  "kinainan"),
    ("kain", "DV", "IPFV", "kinakainan"),
    ("kain", "DV", "CTPL", "kakainan"),
    ("kain", "IV", "PFV",  "ikinain"),
    ("kain", "IV", "IPFV", "ikinakain"),
    ("kain", "IV", "CTPL", "ikakain"),
    # bili — buy (vowel-final, exercises hiatus sandhi on -in/-an)
    ("bili", "AV", "PFV",  "bumili"),
    ("bili", "AV", "IPFV", "bumibili"),
    ("bili", "AV", "CTPL", "bibili"),
    ("bili", "OV", "PFV",  "binili"),
    ("bili", "OV", "IPFV", "binibili"),
    ("bili", "OV", "CTPL", "bibilihin"),
    ("bili", "DV", "PFV",  "binilihan"),
    ("bili", "DV", "IPFV", "binibilihan"),
    ("bili", "DV", "CTPL", "bibilihan"),
    ("bili", "IV", "PFV",  "ibinili"),
    ("bili", "IV", "IPFV", "ibinibili"),
    ("bili", "IV", "CTPL", "ibibili"),
    # inom — drink
    ("inom", "AV", "PFV",  "uminom"),
    ("inom", "AV", "IPFV", "umiinom"),
    ("inom", "AV", "CTPL", "iinom"),
    ("inom", "OV", "PFV",  "ininom"),
    ("inom", "OV", "IPFV", "iniinom"),
    # NB: o→u stem-vowel raising on suffixation is now applied
    # the engine doesn't model this Phase 2 root-specific rule, so
    # automatically (Phase 2C sandhi rule).
    ("inom", "OV", "CTPL", "iinumin"),
    # basa — read
    ("basa", "AV", "PFV",  "bumasa"),
    ("basa", "AV", "IPFV", "bumabasa"),
    ("basa", "AV", "CTPL", "babasa"),
    ("basa", "OV", "PFV",  "binasa"),
    ("basa", "OV", "IPFV", "binabasa"),
    ("basa", "OV", "CTPL", "babasahin"),
    ("basa", "DV", "PFV",  "binasahan"),
    ("basa", "DV", "IPFV", "binabasahan"),
    ("basa", "DV", "CTPL", "babasahan"),
    # gawa — do, make
    ("gawa", "AV", "PFV",  "gumawa"),
    ("gawa", "AV", "IPFV", "gumagawa"),
    ("gawa", "AV", "CTPL", "gagawa"),
    ("gawa", "OV", "PFV",  "ginawa"),
    ("gawa", "OV", "IPFV", "ginagawa"),
    ("gawa", "OV", "CTPL", "gagawahin"),
    # gamit — use
    ("gamit", "AV", "PFV",  "gumamit"),
    ("gamit", "AV", "IPFV", "gumagamit"),
    ("gamit", "AV", "CTPL", "gagamit"),
    ("gamit", "OV", "PFV",  "ginamit"),
    ("gamit", "OV", "IPFV", "ginagamit"),
    ("gamit", "OV", "CTPL", "gagamitin"),
    # tawag — call
    ("tawag", "AV", "PFV",  "tumawag"),
    ("tawag", "AV", "IPFV", "tumatawag"),
    ("tawag", "AV", "CTPL", "tatawag"),
    ("tawag", "OV", "PFV",  "tinawag"),
    ("tawag", "OV", "IPFV", "tinatawag"),
    ("tawag", "OV", "CTPL", "tatawagin"),
    # bilang — count
    ("bilang", "AV", "PFV",  "bumilang"),
    ("bilang", "AV", "IPFV", "bumibilang"),
    ("bilang", "AV", "CTPL", "bibilang"),
    ("bilang", "OV", "PFV",  "binilang"),
    ("bilang", "OV", "IPFV", "binibilang"),
    ("bilang", "OV", "CTPL", "bibilangin"),
    # putol — cut
    ("putol", "AV", "PFV",  "pumutol"),
    ("putol", "AV", "IPFV", "pumuputol"),
    ("putol", "AV", "CTPL", "puputol"),
    ("putol", "OV", "PFV",  "pinutol"),
    ("putol", "OV", "IPFV", "pinuputol"),
    # Same o→u raising as inom (puputol → puputul- before -in).
    ("putol", "OV", "CTPL", "puputulin"),
]

# -- mag- class verbs ----------------------------------------------------

MAG_PARADIGM_FORMS = [
    # linis — clean (mag- only in seed; OV requires sonorant -in- → ni-,
    # deferred to Phase 2C).
    ("linis", "AV", "PFV",  "naglinis"),
    ("linis", "AV", "IPFV", "naglilinis"),
    ("linis", "AV", "CTPL", "maglilinis"),
    # bigay — give
    ("bigay", "AV", "PFV",  "nagbigay"),
    ("bigay", "AV", "IPFV", "nagbibigay"),
    ("bigay", "AV", "CTPL", "magbibigay"),
    # luto — cook
    ("luto", "AV", "PFV",  "nagluto"),
    ("luto", "AV", "IPFV", "nagluluto"),
    ("luto", "AV", "CTPL", "magluluto"),
    # hatid — bring, deliver
    ("hatid", "AV", "PFV",  "naghatid"),
    ("hatid", "AV", "IPFV", "naghahatid"),
    ("hatid", "AV", "CTPL", "maghahatid"),
    # bayad — pay
    ("bayad", "AV", "PFV",  "nagbayad"),
    ("bayad", "AV", "IPFV", "nagbabayad"),
    ("bayad", "AV", "CTPL", "magbabayad"),
    # bihis — dress
    ("bihis", "AV", "PFV",  "nagbihis"),
    ("bihis", "AV", "IPFV", "nagbibihis"),
    ("bihis", "AV", "CTPL", "magbibihis"),
    # tayo — build
    ("tayo", "AV", "PFV",  "nagtayo"),
    ("tayo", "AV", "IPFV", "nagtatayo"),
    ("tayo", "AV", "CTPL", "magtatayo"),
    # ipon — collect
    ("ipon", "AV", "PFV",  "nagipon"),
    ("ipon", "AV", "IPFV", "nagiipon"),
    ("ipon", "AV", "CTPL", "magiipon"),
    # trabaho — work
    ("trabaho", "AV", "PFV",  "nagtrabaho"),
    ("trabaho", "AV", "IPFV", "nagtatrabaho"),
    ("trabaho", "AV", "CTPL", "magtatrabaho"),
    # hintay — wait
    ("hintay", "AV", "PFV",  "naghintay"),
    ("hintay", "AV", "IPFV", "naghihintay"),
    ("hintay", "AV", "CTPL", "maghihintay"),
    # palit — change
    ("palit", "AV", "PFV",  "nagpalit"),
    ("palit", "AV", "IPFV", "nagpapalit"),
    ("palit", "AV", "CTPL", "magpapalit"),
    # punas — wipe
    ("punas", "AV", "PFV",  "nagpunas"),
    ("punas", "AV", "IPFV", "nagpupunas"),
    ("punas", "AV", "CTPL", "magpupunas"),
]

# -- -um/mag alternations ------------------------------------------------

UM_MAG_PARADIGM_FORMS = [
    # sulat — write (both -um- and mag- AV)
    ("sulat", "AV", "PFV",  "sumulat"),
    ("sulat", "AV", "IPFV", "sumusulat"),
    ("sulat", "AV", "CTPL", "susulat"),
    ("sulat", "OV", "PFV",  "sinulat"),
    ("sulat", "OV", "IPFV", "sinusulat"),
    ("sulat", "OV", "CTPL", "susulatin"),
    # sayaw — dance
    ("sayaw", "AV", "PFV",  "sumayaw"),
    ("sayaw", "AV", "IPFV", "sumasayaw"),
    ("sayaw", "AV", "CTPL", "sasayaw"),
    # balik — return (AV with both -um- and mag-)
    ("balik", "AV", "PFV",  "bumalik"),
    ("balik", "AV", "IPFV", "bumabalik"),
    ("balik", "AV", "CTPL", "babalik"),
    # akyat — climb
    ("akyat", "AV", "PFV",  "umakyat"),
    ("akyat", "AV", "IPFV", "umaakyat"),
    ("akyat", "AV", "CTPL", "aakyat"),
    ("akyat", "OV", "PFV",  "inakyat"),
    ("akyat", "OV", "IPFV", "inaakyat"),
    ("akyat", "OV", "CTPL", "aakyatin"),
    # lipat — transfer
    ("lipat", "AV", "PFV",  "lumipat"),
    ("lipat", "AV", "IPFV", "lumilipat"),
    ("lipat", "AV", "CTPL", "lilipat"),
    # tawid — cross
    ("tawid", "AV", "PFV",  "tumawid"),
    ("tawid", "AV", "IPFV", "tumatawid"),
    ("tawid", "AV", "CTPL", "tatawid"),
]

# -- mang- distributive --------------------------------------------------

MANG_PARADIGM_FORMS = [
    # bili — shop (mang- + bili → mamili series)
    ("bili", "AV", "PFV",  "namili"),
    ("bili", "AV", "IPFV", "namimili"),
    ("bili", "AV", "CTPL", "mamimili"),
    # kuha — gather (mang- + kuha → manguha; k → ng)
    ("kuha", "AV", "PFV",  "nanguha"),
    ("kuha", "AV", "IPFV", "nangunguha"),
    ("kuha", "AV", "CTPL", "mangunguha"),
    # tahi — sew distributively (mang- + tahi → nanahi; t → n)
    ("tahi", "AV", "PFV",  "nanahi"),
    ("tahi", "AV", "IPFV", "nananahi"),
    ("tahi", "AV", "CTPL", "mananahi"),
    # putol — cut up (mang- + putol → namutol; p → m)
    ("putol", "AV", "PFV",  "namutol"),
    ("putol", "AV", "IPFV", "namumutol"),
    ("putol", "AV", "CTPL", "mamumutol"),
]

# -- maka- abilitative (MOOD=ABIL) ---------------------------------------

MAKA_PARADIGM_FORMS = [
    ("kain",  "AV", "PFV",  "nakakain"),
    ("kain",  "AV", "IPFV", "nakakakain"),
    ("kain",  "AV", "CTPL", "makakakain"),
    ("bili",  "AV", "PFV",  "nakabili"),
    ("bili",  "AV", "IPFV", "nakabibili"),
    ("bili",  "AV", "CTPL", "makabibili"),
    ("tulog", "AV", "PFV",  "nakatulog"),
    ("tulog", "AV", "IPFV", "nakatutulog"),
    ("tulog", "AV", "CTPL", "makatutulog"),
    ("sulat", "AV", "PFV",  "nakasulat"),
    ("sulat", "AV", "IPFV", "nakasusulat"),
    ("sulat", "AV", "CTPL", "makasusulat"),
    ("basa",  "AV", "PFV",  "nakabasa"),
    ("basa",  "AV", "IPFV", "nakababasa"),
    ("basa",  "AV", "CTPL", "makababasa"),
]

# -- Intransitives -------------------------------------------------------

INTR_PARADIGM_FORMS = [
    # takbo — run
    ("takbo", "AV", "PFV",  "tumakbo"),
    ("takbo", "AV", "IPFV", "tumatakbo"),
    ("takbo", "AV", "CTPL", "tatakbo"),
    # alis — depart (vowel-initial)
    ("alis", "AV", "PFV",  "umalis"),
    ("alis", "AV", "IPFV", "umaalis"),
    ("alis", "AV", "CTPL", "aalis"),
    # dating — arrive. /d/ → /r/ intervocalic (Phase 2C; declared on
    # the root via sandhi_flags=[d_to_r]). PFV "dumating" keeps /d/
    # because it's adjacent to /m/ (not vowel-bracketed); IPFV and
    # CTPL surface the /r/.
    ("dating", "AV", "PFV",  "dumating"),
    ("dating", "AV", "IPFV", "dumarating"),
    ("dating", "AV", "CTPL", "darating"),
    # tawa — laugh
    ("tawa", "AV", "PFV",  "tumawa"),
    ("tawa", "AV", "IPFV", "tumatawa"),
    ("tawa", "AV", "CTPL", "tatawa"),
    # iyak — cry
    ("iyak", "AV", "PFV",  "umiyak"),
    ("iyak", "AV", "IPFV", "umiiyak"),
    ("iyak", "AV", "CTPL", "iiyak"),
    # lakad — walk
    ("lakad", "AV", "PFV",  "lumakad"),
    ("lakad", "AV", "IPFV", "lumalakad"),
    ("lakad", "AV", "CTPL", "lalakad"),
    # tulog — sleep. "natulog" is the ma- non-volitional PFV which
    # the engine doesn't yet model (Phase 2C); the canonical mag-
    # forms are asserted here.
    ("tulog", "AV", "PFV",  "nagtulog"),
    ("tulog", "AV", "IPFV", "nagtutulog"),
    ("tulog", "AV", "CTPL", "magtutulog"),
]


# -- ma- non-volitional (MOOD=NVOL) --------------------------------------
#
# Phase 2C: ma- AV class for non-volitional / accidental / stative
# readings, distinct from maka- abilitative (MOOD=ABIL). The realis
# carries the na- prefix (PFV/IPFV) and the irrealis carries ma-
# (CTPL); both pattern with cv-redup in IPFV/CTPL.

MA_NVOL_PARADIGM_FORMS = [
    ("tulog", "AV", "PFV",  "natulog"),
    ("tulog", "AV", "IPFV", "natutulog"),
    ("tulog", "AV", "CTPL", "matutulog"),
]


# -- Sonorant-initial roots: realis -in- → ni- prefix --------------------
#
# Phase 2C: when a non-AV cell applies the realis -in- infix to a
# sonorant-initial base (m, n, ng, l, r, w, y, h), the infix surfaces
# as a ni- prefix instead.

SONORANT_NI_PARADIGM_FORMS = [
    ("linis", "OV", "PFV",  "nilinis"),
    ("linis", "OV", "IPFV", "nililinis"),
    ("linis", "OV", "CTPL", "lilinisin"),
    ("linis", "DV", "PFV",  "nilinisan"),
    ("linis", "DV", "IPFV", "nililinisan"),
    ("linis", "DV", "CTPL", "lilinisan"),
]


# -- /d/ → /r/ intervocalic alternation ----------------------------------
#
# Phase 2C: per-root opt-in via sandhi_flags=[d_to_r]. Catches
# stem-internal d→r in reduplication (dadating → darating) and stem-
# suffix-boundary d→r (lakadin → lakarin). PFV "dumating" keeps /d/
# because position is /m_a/, not vowel-vowel.

D_TO_R_PARADIGM_FORMS = [
    # dating exercises stem-internal d→r in cv-redup.
    ("dating", "AV", "IPFV", "dumarating"),
    ("dating", "AV", "CTPL", "darating"),
    # bayad exercises stem-suffix-boundary d→r on -an attachment.
    ("bayad", "DV", "CTPL", "babayaran"),
]


# === Test parametrization ================================================

ALL_PAIRED_FORMS = (
    UM_PARADIGM_FORMS
    + MAG_PARADIGM_FORMS
    + UM_MAG_PARADIGM_FORMS
    + MANG_PARADIGM_FORMS
    + MAKA_PARADIGM_FORMS
    + INTR_PARADIGM_FORMS
    + MA_NVOL_PARADIGM_FORMS
    + SONORANT_NI_PARADIGM_FORMS
    + D_TO_R_PARADIGM_FORMS
)


@pytest.fixture(scope="module")
def analyzer() -> Analyzer:
    return Analyzer.from_default()


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


@pytest.mark.parametrize("root,voice,aspect,surface", ALL_PAIRED_FORMS)
def test_surface_analyses_to_expected(
    root: str,
    voice: str,
    aspect: str,
    surface: str,
    analyzer: Analyzer,
) -> None:
    """The surface form analyses back to a record with the expected
    lemma, voice, and aspect — one of the n-best for this surface."""
    out = analyzer.analyze_one(_tok(surface))
    matches = [
        a for a in out
        if a.pos == "VERB"
        and a.lemma == root
        and a.feats.get("VOICE") == voice
        and a.feats.get("ASPECT") == aspect
    ]
    assert matches, (
        f"no analysis matching ({root!r}, {voice}, {aspect}) for "
        f"surface {surface!r}; analyses={out}"
    )


@pytest.mark.parametrize("root,voice,aspect,surface", ALL_PAIRED_FORMS)
def test_generation_produces_expected_surface(
    root: str,
    voice: str,
    aspect: str,
    surface: str,
) -> None:
    """The reverse direction: generate from (root, cell) and confirm
    we land on the same surface."""
    data = load_morph_data()
    root_obj = next((r for r in data.roots if r.citation == root), None)
    assert root_obj is not None, f"root {root!r} not in seed lexicon"
    candidates = [
        c for c in data.paradigm_cells
        if c.voice == voice and c.aspect == aspect
        and (not c.transitivity or c.transitivity == root_obj.transitivity)
        and (not c.affix_class or c.affix_class in root_obj.affix_class)
    ]
    assert candidates, (
        f"no paradigm cell for ({root!r}, {voice}, {aspect}) given "
        f"affix_class={root_obj.affix_class}"
    )
    surfaces = {generate_form(root_obj, c) for c in candidates}
    assert surface in surfaces, (
        f"expected {surface!r} for ({root!r}, {voice}, {aspect}); "
        f"engine generated {sorted(surfaces)}"
    )


# === Mood verification for maka- =========================================

@pytest.mark.parametrize("root,voice,aspect,_surface", MAKA_PARADIGM_FORMS)
def test_maka_forms_carry_mood_abil(
    root: str,
    voice: str,
    aspect: str,
    _surface: str,
    analyzer: Analyzer,
) -> None:
    out = analyzer.analyze_one(_tok(_surface))
    matches = [
        a for a in out
        if a.pos == "VERB"
        and a.lemma == root
        and a.feats.get("MOOD") == "ABIL"
    ]
    assert matches, (
        f"maka- form {_surface!r} did not carry MOOD=ABIL; "
        f"analyses={out}"
    )


# === Coverage statistics =================================================

def test_seed_lexicon_size() -> None:
    """Track lexicon scale; trigger if it shrinks unexpectedly."""
    data = load_morph_data()
    verbs = [r for r in data.roots if r.pos == "VERB"]
    nouns = [r for r in data.roots if r.pos == "NOUN"]
    assert len(verbs) >= 50, f"verb count regressed: {len(verbs)}"
    assert len(nouns) >= 30, f"noun count regressed: {len(nouns)}"


def test_paired_assertion_count() -> None:
    """At least 100 paired assertions in the table — bumps the floor
    well above the kain/bili anchors and below the plan's 500 target,
    which would require Phase 2C scale-up."""
    assert len(ALL_PAIRED_FORMS) >= 100
