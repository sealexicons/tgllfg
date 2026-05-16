"""Phase 9.D: common-noun batch 2 lex pass.

24 audit-attested common nouns added to ``data/tgl/nouns.yaml``
covering rank ~30-150 of the post-9.C OOV TSV (freq >= 3).
Follows the 9.C / 9.C.pre schema convention.

8 SPANISH-loan entries (bola / dentista / kandidato / pader /
pare / pisara / regalo / telepono).

ADJ-root coexistence: 2 entries (``ingay``, ``tabi``) also exist
in ``adjectives.yaml`` as paradigm-input ADJ roots — they only
generate derived surfaces (``maingay``, ``nakatabi``); the bare
citation surface is contributed solely by the new N root. No
conflict.

V-root coexistence: 6 entries (``laro``, ``regalo``, ``sakit``,
``tabi``, ``tanong``, ``tingin``) have V roots in ``verbs.yaml``;
the V root continues to generate inflected verbal surfaces, the
new N root attests only the bare nominal form.
"""

from __future__ import annotations

import pytest

ALL_NEW = [
    "bola", "daliri", "dentista", "ilalim", "ingay", "kaklase",
    "kandidato", "kasama", "kayamanan", "laro", "laruan", "pader",
    "palagay", "panganay", "pare", "pisara", "pulong", "regalo",
    "sakit", "silid", "tabi", "tanong", "telepono", "tingin",
]

SPANISH_LOANS = [
    "bola", "dentista", "kandidato", "pader", "pare", "pisara",
    "regalo", "telepono",
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

    @pytest.mark.parametrize("cit", ALL_NEW)
    def test_noun_registered(self, roots_by_cit, cit: str) -> None:
        assert cit in roots_by_cit, f"missing root: {cit}"
        nouns = [r for r in roots_by_cit[cit] if r.pos == "NOUN"]
        assert nouns, f"no NOUN root for {cit}"
        r = nouns[0]
        assert r.source == "audit-corpus"
        assert r.subclass == []
        assert r.gloss
        assert "(" not in r.gloss


# ---- Loan-field plumbing ------------------------------------------

class TestLoanFields:

    @pytest.mark.parametrize("cit", SPANISH_LOANS)
    def test_spanish_loan(self, roots_by_cit, cit: str) -> None:
        r = [n for n in roots_by_cit[cit] if n.pos == "NOUN"][0]
        assert r.loan == "SPANISH"

    @pytest.mark.parametrize("cit", [
        c for c in ALL_NEW if c not in SPANISH_LOANS
    ])
    def test_no_loan_on_native(self, roots_by_cit, cit: str) -> None:
        r = [n for n in roots_by_cit[cit] if n.pos == "NOUN"][0]
        assert r.loan == ""


# ---- ADJ-root / V-root coexistence --------------------------------

class TestAdjRootCoexistence:
    """``ingay`` / ``tabi`` exist as ADJ roots in adjectives.yaml;
    the new N citation surfaces independently."""

    @pytest.fixture
    def analyzer(self):
        from tgllfg.morph.analyzer import Analyzer
        from tgllfg.morph.loader import load_morph_data
        return Analyzer(load_morph_data())

    @pytest.mark.parametrize("cit", ["ingay", "tabi"])
    def test_bare_surface_yields_noun(self, analyzer, cit: str) -> None:
        from tgllfg.core.common import Token
        analyses = analyzer.analyze_one(
            Token(surface=cit, norm=cit, start=0, end=len(cit))
        )
        poses = {m.pos for m in analyses}
        assert "NOUN" in poses, (
            f"{cit} bare surface yields no NOUN analysis (got {poses})"
        )


class TestNVPairsCoexist:
    """The 6 N–V citation pairs surface as NOUN at the bare form;
    V roots remain inflection-only."""

    NV_PAIRS = ["laro", "regalo", "sakit", "tabi", "tanong", "tingin"]

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

    @pytest.mark.parametrize("sentence", [
        # ma-ADJ pivots
        "Maganda ang bola.",
        "Maganda ang daliri.",
        "Mabuti ang dentista.",
        "Maganda ang kasama.",
        "Maganda ang silid.",
        "Maganda ang regalo.",
        "Maganda ang laro.",
        # ng-marked OBL
        "Bumili siya ng bola.",
        "Bumili siya ng laruan.",
        "Bumili siya ng regalo.",
        "Bumili siya ng pisara.",
        "Bumili siya ng pader.",
        # sa-marked locative
        "Pumunta siya sa silid.",
        "Pumunta siya sa pulong.",
        # may-existential
        "May ingay sa bahay.",
        "May sakit siya.",
        "May tanong ako.",
        # ang-pivot bare N
        "Dumating ang panganay.",
        "Dumating ang kasama.",
        "Bumili siya ng telepono.",
        "Nagsalita ang kandidato.",
    ])
    def test_simple_parse(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# ---- V-root no-regression ----------------------------------------

class TestVRootNoRegression:
    """Adding the N reading must not break inflected V surfaces.
    Only ``tabi`` V (INTR) generates a bare AV form that parses
    cleanly under the current grammar (the other 9.D N–V pairs —
    laro / regalo / sakit / tanong / tingin — are TR verbs whose
    bare AV forms run into a pre-existing TR-without-OBJ coverage
    gap unrelated to this sub-PR)."""

    @pytest.mark.parametrize("sentence", [
        "Tumabi siya.",          # um-AV-PFV of tabi (INTR)
    ])
    def test_v_form_still_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"V-form regression: {sentence!r}"
