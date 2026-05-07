"""Phase 5j Commit 1: existential lex inventory + supporting NOUN lex.

Roadmap §12.1 / plan-of-record §4.1, §4.3. Seven new lex entries
across two clusters:

* Existential clause-typers (``data/tgl/particles.yaml``):
  ``may`` / ``mayroon`` (positive existential) and ``wala``
  (negative existential), all PART[EXISTENTIAL=YES] with the
  matching POLARITY feat. ``nasa`` is a separate locative-
  existential clause-typer with PART[LOC_EXISTENTIAL=YES].
* Locative / supporting NOUN lex (``data/tgl/nouns.yaml``):
  ``labas`` (outside), ``tuktok`` (top), ``bukid`` (field /
  countryside) — surface inside locative-PP composition and the
  R&G "Ang Manok" simples #5 / #7 (Phase 5j §8 integration
  benchmark).

This commit is lex-only — no grammar / analyzer code changes.
The Phase 5j existential / locative grammar rules
(Commits 2-4) constrain on ``EXISTENTIAL=YES`` /
``LOC_EXISTENTIAL=YES`` to fire on these surfaces.

Pre-state (verified 2026-05-06): all four PART surfaces
(``may`` / ``mayroon`` / ``wala`` / ``nasa``) and all three
NOUN surfaces (``labas`` / ``tuktok`` / ``bukid``) were
``_UNK``. Per the §3 reconnaissance, no Phase 5j-target
existential / locative sentences parse today (they all return
0 parses); the only flip-risk surface for the phase is
``Hindi ka dapat kumain.`` which lands in Commit 7. So this
commit is purely additive.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Existential clause-typers ========================================


EXISTENTIAL_PARTS = [
    # (surface, polarity, lemma)
    ("may",     "POS", "may"),
    ("mayroon", "POS", "mayroon"),
    ("wala",    "NEG", "wala"),
]


class TestExistentialParts:
    """Each existential clause-typer indexes as PART with
    EXISTENTIAL=YES + the matching POLARITY feat."""

    @pytest.mark.parametrize("surface,polarity,lemma", EXISTENTIAL_PARTS)
    def test_indexed_as_existential_part(
        self, surface: str, polarity: str, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        existentials = [
            a for a in out
            if a.pos == "PART" and a.feats.get("EXISTENTIAL") == "YES"
        ]
        assert len(existentials) == 1, (
            f"expected exactly one existential PART analysis for "
            f"{surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    @pytest.mark.parametrize("surface,polarity,lemma", EXISTENTIAL_PARTS)
    def test_carries_polarity_and_lemma(
        self, surface: str, polarity: str, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        part = next(
            a for a in analyzer.analyze_one(_tok(surface))
            if a.pos == "PART" and a.feats.get("EXISTENTIAL") == "YES"
        )
        assert part.feats.get("EXISTENTIAL") == "YES"
        assert part.feats.get("POLARITY") == polarity
        assert part.feats.get("LEMMA") == lemma


# === Locative existential `nasa` =====================================


class TestLocativeExistentialNasa:
    """``nasa`` is a separate locative-existential clause-typer
    with PART[LOC_EXISTENTIAL=YES] (NOT EXISTENTIAL=YES). Three-
    daughter rule shape lands in Commit 4."""

    def test_indexed_as_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("nasa"))
        nasas = [
            a for a in out
            if a.pos == "PART" and a.feats.get("LOC_EXISTENTIAL") == "YES"
        ]
        assert len(nasas) == 1, (
            f"expected exactly one LOC_EXISTENTIAL PART analysis for "
            f"'nasa'; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    def test_carries_loc_existential_and_lemma(self) -> None:
        analyzer = Analyzer.from_default()
        part = next(
            a for a in analyzer.analyze_one(_tok("nasa"))
            if a.pos == "PART"
        )
        assert part.feats.get("LOC_EXISTENTIAL") == "YES"
        assert part.feats.get("LEMMA") == "nasa"
        # Crucially NOT EXISTENTIAL=YES (different clause-type
        # rule fires).
        assert part.feats.get("EXISTENTIAL") is None
        # And no POLARITY (locative existential doesn't carry
        # NEG polarity at the clause-typer level — would compose
        # with hindi-wrap if needed).
        assert part.feats.get("POLARITY") is None


# === Supporting locative / proper nouns ===============================


SUPPORTING_NOUNS = [
    ("labas",  "labas"),
    ("tuktok", "tuktok"),
    ("bukid",  "bukid"),
]


class TestSupportingNouns:
    """Three supporting NOUN entries that surface inside locative-PP
    composition (``sa labas``, ``sa bukid``) and the R&G "Ang Manok"
    simples #5 (``Nasa bundok ang bahay.``) and #7 (``Nasa tuktok
    ng bundok ang bahay.``)."""

    @pytest.mark.parametrize("surface,lemma", SUPPORTING_NOUNS)
    def test_indexed_as_noun(self, surface: str, lemma: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        nouns = [a for a in out if a.pos == "NOUN"]
        assert len(nouns) == 1, (
            f"expected exactly one NOUN analysis for {surface!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
        assert nouns[0].lemma == lemma


# === Cross-cluster: pre-state-flip checks ============================


class TestExistentialPolaritiesAreDistinct:
    """``may`` and ``wala`` carry distinct POLARITY values so the
    Commits 2 / 3 rules can use category-pattern matching to
    disambiguate at parse time."""

    def test_may_polarity_pos_only(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("may"))
        existentials = [
            a for a in out
            if a.pos == "PART" and a.feats.get("EXISTENTIAL") == "YES"
        ]
        polarities = {a.feats.get("POLARITY") for a in existentials}
        assert polarities == {"POS"}, (
            f"expected may to be POLARITY=POS only; got {polarities}"
        )

    def test_wala_polarity_neg_only(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("wala"))
        existentials = [
            a for a in out
            if a.pos == "PART" and a.feats.get("EXISTENTIAL") == "YES"
        ]
        polarities = {a.feats.get("POLARITY") for a in existentials}
        assert polarities == {"NEG"}, (
            f"expected wala to be POLARITY=NEG only; got {polarities}"
        )


class TestLinkerSplitOnVowelFinalForms:
    """``walang`` / ``mayroong`` are vowel-final + bound ``-ng``
    linker. After Phase 5j Commit 1 lands ``wala`` and ``mayroon``
    as known surfaces, ``split_linker_ng`` should split:

    * ``walang`` → ``wala`` + ``-ng``
    * ``mayroong`` → ``mayroon`` + ``-ng``

    This test exercises the bare bound surface — the split is
    enacted at the pre-parse stage. The bound ``walang`` /
    ``mayroong`` token returns _UNK from the analyzer directly
    (matching Phase 5i ``aling`` precedent in Commit 6)."""

    @pytest.mark.parametrize("surface", ["walang", "mayroong"])
    def test_bound_surface_is_unk_pre_split(self, surface: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        # All analyses should be _UNK for the raw bound surface;
        # split_linker_ng (called at pre-parse) handles the split.
        assert all(a.pos == "_UNK" for a in out), (
            f"expected {surface!r} as bare token to be _UNK pre-split; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
