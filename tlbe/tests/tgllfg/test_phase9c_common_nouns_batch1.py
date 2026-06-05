# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.C: common-noun batch 1 lex pass.

25 audit-attested common nouns added to ``data/tgl/nouns.yaml``
following the 9.C.pre schema convention:

* ``source: audit-corpus`` — the Phase 8/9 audit harvest surfaced
  every entry at frequency >= 5.
* ``loan: SPANISH`` for the 9 Spanish-origin entries (almusal /
  bisita / diyaryo / liksyon / mekaniko / motorsiklo / opisina /
  pandanggo / sine).
* Bare gloss — no parentheticals.
* ``subclass`` omitted (common-noun batch; the closed-enum
  ``subclass`` axis is reserved for named-entity / nationality
  nouns per 9.B + 9.C.pre).

7 of the 25 citations (balita / bisita / buhay / gamot / lakad /
sulat / tulong) are zero-conversion N–V pairs — the V root in
``verbs.yaml`` continues to generate inflected verbal surfaces;
the new N root only attests the bare citation form for nominal
readings.
"""

import pytest

ALL_NEW = [
    "alak", "almusal", "bagyo", "balita", "balut", "bisita",
    "buhay", "dalaga", "diyaryo", "gamot", "halaman",
    "kasangkapan", "kulay", "lakad", "liksyon", "loob",
    "mekaniko", "motorsiklo", "opisina", "panahon", "pandanggo",
    "sine", "sulat", "tulong", "ulam",
]

SPANISH_LOANS = [
    "almusal", "bisita", "diyaryo", "liksyon", "mekaniko",
    "motorsiklo", "opisina", "pandanggo", "sine",
]


@pytest.fixture(scope="module")
def roots_by_cit():
    from tgllfg.morph.loader import load_morph_data
    m = load_morph_data()
    idx: dict[str, list] = {}
    for r in m.roots:
        idx.setdefault(r.citation, []).append(r)
    return idx


# ---- Registration -------------------------------------------------

class TestEntriesRegistered:
    """Every new citation loads as a NOUN root with source set."""

    @pytest.mark.parametrize("cit", ALL_NEW)
    def test_noun_registered(self, roots_by_cit, cit: str) -> None:
        assert cit in roots_by_cit, f"missing root: {cit}"
        nouns = [r for r in roots_by_cit[cit] if r.pos == "NOUN"]
        assert nouns, f"no NOUN root for {cit}"
        r = nouns[0]
        assert r.source == "audit-corpus"
        assert r.subclass == []  # common-noun batch
        assert r.gloss  # non-empty
        assert "(" not in r.gloss  # bare gloss


# ---- Loan-field plumbing ------------------------------------------

class TestLoanFields:
    """Spanish-loan entries carry ``loan: SPANISH``."""

    @pytest.mark.parametrize("cit", SPANISH_LOANS)
    def test_spanish_loan(self, roots_by_cit, cit: str) -> None:
        r = [n for n in roots_by_cit[cit] if n.pos == "NOUN"][0]
        assert r.loan == "SPANISH", (
            f"{cit} loan is {r.loan!r}, expected 'SPANISH'"
        )

    @pytest.mark.parametrize("cit", [
        c for c in ALL_NEW if c not in SPANISH_LOANS
    ])
    def test_no_loan_on_native(self, roots_by_cit, cit: str) -> None:
        r = [n for n in roots_by_cit[cit] if n.pos == "NOUN"][0]
        assert r.loan == "", (
            f"{cit} should be native (loan empty), got {r.loan!r}"
        )


# ---- Surface indexing for N–V pairs -------------------------------

class TestNVPairsCoexist:
    """The 7 zero-conversion N–V pairs surface as NOUN at the bare
    citation; the V root still generates inflected verbal forms in
    verbs.yaml without conflict."""

    NV_PAIRS = ["balita", "bisita", "buhay", "gamot",
                "lakad", "sulat", "tulong"]

    @pytest.fixture
    def analyzer(self):
        from tgllfg.morph.analyzer import Analyzer
        from tgllfg.morph.loader import load_morph_data
        return Analyzer(load_morph_data())

    @pytest.mark.parametrize("cit", NV_PAIRS)
    def test_bare_surface_is_noun(self, analyzer, cit: str) -> None:
        from tgllfg.core.common import Token
        analyses = analyzer.analyze_one(
            Token(surface=cit, norm=cit, start=0, end=len(cit))
        )
        poses = {m.pos for m in analyses}
        assert "NOUN" in poses, (
            f"{cit} bare surface yields no NOUN analysis (got {poses})"
        )


# ---- Smoke parses --------------------------------------------------

class TestSimpleParses:
    """Each new N parses in a simple ma-ADJ-pivot or numeral
    classifier context. Doesn't try to reproduce the full audit-
    corpus sentence (those often have other OOV gaps); just
    verifies the N integrates into the grammar."""

    @pytest.mark.parametrize("sentence", [
        # ma-ADJ pivots — exercise the NP-pivot route
        "Maganda ang panahon.",
        "Malakas ang bagyo.",
        "Masarap ang almusal.",
        "Masarap ang ulam.",
        "Masarap ang balut.",
        "Mabuti ang balita.",
        "Maganda ang dalaga.",
        "Maganda ang kulay.",
        "Maganda ang halaman.",
        "Mabuti ang loob.",
        "Malaki ang tulong.",
        "Maganda ang mekaniko.",
        # ng-marked OBL — exercise the OBL route
        "Bumili siya ng alak.",
        "Bumili siya ng diyaryo.",
        "Bumili siya ng gamot.",
        "Bumili siya ng motorsiklo.",
        "Sasayaw sila ng pandanggo.",
        "Mag-aral ka ng liksyon.",
        # sa-marked locative — LOC OBL
        "Pumunta siya sa opisina.",
        "Pumunta kami sa sine.",
        # may-existential
        "May lakad ako.",
        "May sulat ako.",
        # ang-pivot bare
        "Dumating ang bisita.",
        "Bumalik ang mga sulat.",
    ])
    def test_simple_parse(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# ---- N–V coexistence parse tests ----------------------------------

class TestNVParseCoexistence:
    """Adding the N root must not regress V-root parses on the
    same surface — the V root continues to generate inflected
    verbal surfaces (sumulat / lumakad / etc.). Note: some
    pre-existing V-forms (tumulong / nagbalita / nagbisita) fail
    on main due to TR-arg coverage gaps unrelated to this sub-PR
    and are explicitly excluded from the assert path."""

    @pytest.mark.parametrize("sentence", [
        "Sumulat siya.",           # um-AV-PFV of sulat
        "Lumakad siya.",           # um-AV-PFV of lakad
        # N-on-same-surface unblockings (improvements):
        "Dumating ang bisita.",    # N reading of bisita
    ])
    def test_v_form_still_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression: {sentence!r}"
