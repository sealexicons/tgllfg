"""Phase 5j Commit 5: HAVE construction.

Roadmap §12.1 / plan-of-record §5.4 + §5.5, §6 Commit 5. Four
new clause rules in ``cfg/clause.py`` covering positive /
negative HAVE × postposed-possessor / internal-clitic-possessor
patterns:

  Commit 5a (positive, postposed):
    S → PART[EXISTENTIAL=YES, POLARITY=POS] N NP[CASE=NOM]
    ``May aklat ako.`` / ``May aklat si Maria.``

  Commit 5b (positive, internal-clitic):
    S → PART[EXISTENTIAL=YES, POLARITY=POS] PRON[CASE=NOM]
        PART[LINK=NG] N
    ``May akong aklat.``

  Commit 5c (negative, postposed):
    S → PART[EXISTENTIAL=YES, POLARITY=NEG] PART[LINK=NG] N
        NP[CASE=NOM]
    ``Walang aklat ako.`` / ``Walang aklat si Maria.``

  Commit 5d (negative, internal-clitic):
    S → PART[EXISTENTIAL=YES, POLARITY=NEG] PRON[CASE=NOM]
        PART[LINK=NG] N
    ``Wala akong aklat.``

Tagalog has no separate HAVE verb. The HAVE reading is the
existential predicate (Commit 2 / 3) + a possessor-NP that binds
to the existence-asserted N's POSSESSOR feature.

F-structure shape (all 4 rules):

  PRED         = 'EXIST <SUBJ>'
  SUBJ         = the existence-asserted N
  SUBJ POSSESSOR = the possessor-NP / clitic-PRON
  CLAUSE_TYPE  = 'EXISTENTIAL'
  HAVE         = 'YES'  (lifts HAVE-reading flag for downstream)
  POLARITY     = 'POS' or 'NEG'

The asymmetry between positive (no bound -ng on may) and negative
(bound -ng on wala) is surface-level. The internal-clitic and
postposed patterns reflect different surface positions of the
possessor — Tagalog admits both.

End-to-end target sentences:

    May aklat ako.            "I have a book."
    May aklat si Maria.       "Maria has a book."
    May akong aklat.          "I have a book."
    Wala akong aklat.         "I don't have a book."
    Walang aklat si Maria.    "Maria doesn't have a book."
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Positive HAVE — postposed possessor (Commit 5a) =================


class TestPositiveHavePostposed:
    """``May aklat ako.`` / ``May aklat si Maria.`` — postposed
    possessor (no internal linker)."""

    @pytest.mark.parametrize("sentence,subj_lemma,poss_lemma", [
        ("May aklat si Maria.", "aklat", "maria"),
        ("May aklat si Juan.",  "aklat", "juan"),
        ("May bahay si Maria.", "bahay", "maria"),
    ])
    def test_full_np_possessor(
        self, sentence: str, subj_lemma: str, poss_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses
            if p[1].feats.get("HAVE") == "YES"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        assert fs.feats.get("POLARITY") == "POS"
        assert fs.feats.get("HAVE") == "YES"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("LEMMA") == poss_lemma

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("May aklat ako.",  "aklat"),
        ("May bahay siya.", "bahay"),
    ])
    def test_clitic_pron_possessor_postposed(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses
            if p[1].feats.get("HAVE") == "YES"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("HAVE") == "YES"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        # Clitic PRONs project to NP[CASE=NOM] but don't carry
        # LEMMA in this codebase — assert CASE instead.
        assert poss.feats.get("CASE") == "NOM"


# === Positive HAVE — internal-clitic possessor (Commit 5b) ==========


class TestPositiveHaveInternalClitic:
    """``May akong aklat.`` — clitic-PRON possessor inside,
    with bound -ng linker before the possessee N."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("May akong aklat.",   "aklat"),
        ("May akong bahay.",   "bahay"),
    ])
    def test_internal_clitic_pos(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses
            if p[1].feats.get("HAVE") == "YES"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("POLARITY") == "POS"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("CASE") == "NOM"


# === Negative HAVE — postposed possessor (Commit 5c) =================


class TestNegativeHavePostposed:
    """``Walang aklat ako.`` / ``Walang aklat si Maria.`` —
    postposed possessor with bound -ng on wala."""

    @pytest.mark.parametrize("sentence,subj_lemma,poss_lemma", [
        ("Walang aklat si Maria.", "aklat", "maria"),
        ("Walang bahay si Juan.",  "bahay", "juan"),
    ])
    def test_full_np_possessor_neg(
        self, sentence: str, subj_lemma: str, poss_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses
            if p[1].feats.get("HAVE") == "YES"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("POLARITY") == "NEG"
        assert fs.feats.get("HAVE") == "YES"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("LEMMA") == poss_lemma

    def test_clitic_pron_possessor_neg_postposed(self) -> None:
        parses = parse_text("Walang aklat ako.")
        ex_parses = [
            p for p in parses
            if p[1].feats.get("HAVE") == "YES"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "aklat"
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("CASE") == "NOM"


# === Negative HAVE — internal-clitic possessor (Commit 5d) ===========


class TestNegativeHaveInternalClitic:
    """``Wala akong aklat.`` — internal-clitic-PRON possessor
    with bound -ng linker between clitic and possessee N."""

    @pytest.mark.parametrize("sentence,subj_lemma", [
        ("Wala akong aklat.", "aklat"),
        ("Wala akong bahay.", "bahay"),
    ])
    def test_internal_clitic_neg(
        self, sentence: str, subj_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        ex_parses = [
            p for p in parses
            if p[1].feats.get("HAVE") == "YES"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("PRED") == "EXIST <SUBJ>"
        assert fs.feats.get("POLARITY") == "NEG"
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        poss = subj.feats.get("POSSESSOR")
        assert poss is not None
        assert poss.feats.get("CASE") == "NOM"


# === HAVE flag is not set on bare existential ========================


class TestHaveFlagOnlyOnHaveRules:
    """The HAVE flag is NOT set by Commit 2 / 3 base existential
    rules — only by Commit 5's HAVE rules. ``May aklat.`` has no
    possessor and no HAVE flag; ``May aklat ako.`` has both."""

    def test_bare_existential_no_have(self) -> None:
        parses = parse_text("May aklat.")
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("HAVE") is None

    def test_have_existential_has_have_flag(self) -> None:
        parses = parse_text("May aklat ako.")
        ex_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "EXISTENTIAL"
        ]
        assert len(ex_parses) >= 1
        _ct, fs, _astr, _diags = ex_parses[0]
        assert fs.feats.get("HAVE") == "YES"


# === No phantom HAVE on V-headed / locative clauses =================


class TestNoPhantomHave:
    """V-headed clauses with NOM-NPs shouldn't acquire HAVE=YES
    from the new rules. Locative existentials (Commit 4) also
    shouldn't acquire HAVE=YES."""

    @pytest.mark.parametrize("sentence", [
        "Kumain ang aso.",
        "Kumain ang aso ng kanin.",
        "Maganda ang bata.",
        "Nasa bundok ang bahay.",
    ])
    def test_no_phantom_have(self, sentence: str) -> None:
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("HAVE") != "YES", (
                f"unexpected HAVE=YES on {sentence!r}: {fs.feats}"
            )
