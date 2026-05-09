"""Phase 5n.A Commit 25 — pang- purpose nominals (§18 L27).

Closes §18 L27. Hand-authored ``pang-`` (and ``pam-`` / ``pan-``
allomorph) instrumental / purpose nominals lex'd as NOUN with a
``PANG_DERIVED: true`` traceability feat. Each entry covers a
single attested form; the productive ``pang-`` derivation engine
is deferred to L31 (NOUN-root engine).

Lex inventory (6 entries):

* ``pambili``    — money for buying / shopping money
* ``pamasahe``   — transport fare
* ``pangharang`` — instrument for blocking / blockade
* ``pangkain``   — food / something to eat
* ``pangsuot``   — clothing / garment
* ``pansulat``   — pen / writing instrument

Allomorphy: ``pang-`` selects ``pam-`` before /b, p/, ``pan-``
before /t, d, s, l, n/, and ``pang-`` proper before vowels and
/k, g, h, ng, w, y/. The base nominal class denotes the
instrument or stuff used for an action (S&O 1972 §5.x).

Sources: ``pambili`` and ``pamasahe`` are attested in the
intermediate-Tagalog corpus; ``pansulat`` / ``pangkain`` /
``pangsuot`` / ``pangharang`` are S&O 1972 §5.x derived-nominal
class examples.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer, load_morph_data


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


PANG_NOMINALS = [
    "pambili",
    "pamasahe",
    "pangharang",
    "pangkain",
    "pangsuot",
    "pansulat",
]


# === Morph-layer assertions =========================================


class TestPangNominalLex:
    """Each new pang- nominal is indexed as a NOUN with the
    PANG_DERIVED traceability feat and lemma identical to the
    surface citation."""

    @pytest.mark.parametrize("citation", PANG_NOMINALS)
    def test_pang_nominal_indexed_as_noun(self, citation: str) -> None:
        analyzer = Analyzer(load_morph_data())
        out = analyzer.analyze_one(_tok(citation))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(nouns) == 1, (
            f"expected exactly one NOUN analysis for {citation!r}, "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )
        assert nouns[0].lemma == citation
        assert nouns[0].feats.get("PANG_DERIVED") is True


# === Parse-level: pang- nominal as OBJ ==============================


class TestPangNominalAsObj:
    """pang- nominals compose as the OBJ of an AV verb via the
    existing N-DET-MOD machinery (no Commit 25 grammar additions
    needed)."""

    @pytest.mark.parametrize("sentence,obj_lemma", [
        ("Bumili siya ng pansulat.", "pansulat"),
        ("Bumili ako ng pangkain.",  "pangkain"),
        ("Bumili siya ng pangsuot.", "pangsuot"),
    ])
    def test_pang_nominal_obj_parses(
        self, sentence: str, obj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == obj_lemma


# === Parse-level: pang- nominal in HAVE construction ===============


class TestPangNominalInHave:
    """pang- nominals compose as the existence-asserted N in HAVE
    constructions (Phase 5j Commit 5 + Phase 5n.A Commit 21
    mayroon-with-linker)."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("May pansulat ako.",       "pansulat"),
        ("May pangkain si Maria.",  "pangkain"),
        ("Mayroong pansulat ako.",  "pansulat"),
    ])
    def test_pang_nominal_have(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses if p[1].feats.get("HAVE") == "YES"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("HAVE") == "YES"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma


# === IV-INSTR regression ============================================


class TestIVInstrRegression:
    """Adding NOUN entries for bare ``pambili`` / ``pansulat`` etc.
    does NOT crossfire with the existing IV-INSTR ``ipang-``
    paradigm. The IV-INSTR analysis fires on inflected forms
    (``ipinambili`` etc.); the bare forms get the new NOUN
    analysis only."""

    def test_ipinambili_still_iv_instr(self) -> None:
        analyzer = Analyzer(load_morph_data())
        out = analyzer.analyze_one(_tok("ipinambili"))
        verbs = [a for a in out if a.pos == "VERB"]
        assert len(verbs) >= 1
        iv_instr = [
            v for v in verbs
            if v.feats.get("VOICE") == "IV"
            and v.feats.get("APPL") == "INSTR"
        ]
        assert len(iv_instr) >= 1
        assert iv_instr[0].lemma == "bili"

    def test_pambili_only_noun_no_verb(self) -> None:
        """The bare ``pambili`` surface gets only the new NOUN
        analysis, not a (hypothetical) IV-INSTR infinitive
        analysis (which the existing paradigm doesn't generate)."""
        analyzer = Analyzer(load_morph_data())
        out = analyzer.analyze_one(_tok("pambili"))
        verbs = [a for a in out if a.pos == "VERB"]
        assert verbs == []
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(nouns) == 1
        assert nouns[0].feats.get("PANG_DERIVED") is True


# === panulat / pansulat coexistence =================================


class TestPanulatPansulatCoexistence:
    """``panulat`` (existing common noun, "pen") and ``pansulat``
    (new pang- derived nominal, "writing instrument") are
    distinct surface lex entries. Both parse independently."""

    def test_panulat_still_parses(self) -> None:
        parses = parse_text("Bumili ako ng panulat.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "panulat"

    def test_pansulat_carries_pang_derived(self) -> None:
        analyzer = Analyzer(load_morph_data())
        out = analyzer.analyze_one(_tok("pansulat"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(nouns) == 1
        assert nouns[0].feats.get("PANG_DERIVED") is True

    def test_panulat_does_not_carry_pang_derived(self) -> None:
        analyzer = Analyzer(load_morph_data())
        out = analyzer.analyze_one(_tok("panulat"))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(nouns) >= 1
        # The existing panulat entry has no PANG_DERIVED feat.
        assert all(
            n.feats.get("PANG_DERIVED") is None for n in nouns
        )
