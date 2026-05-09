"""Phase 5n.A Commit 6 — nakatira resultative naka- paradigm (§18 L61).

The verbal ``naka-`` paradigm in ``data/tgl/paradigms.yaml`` produces
abilitative AV cells (``nakatira`` "was able to live", with
MOOD=ABIL). The resultative ADJ reading (``nakatira`` "be living")
was missing — needed for R&G "Ang Manok" simples #1 and #3 where
``nakatira`` functions as a stative predicative ADJ ("there's an old
man who lives in a house in the country").

Closure (this commit): add a new ``naka_resultative`` ADJ paradigm
cell to ``data/tgl/adj_paradigms.yaml`` producing
``ADJ[RESULTATIVE=YES, naka- prefix]``. Add ADJ entries in
``data/tgl/adjectives.yaml`` for the canonical stative-locative
roots per S&O 1972 §6: ``tira``, ``upo``, ``higa``, ``tayo``,
``tabi``. The ADJ entries opt into ``naka_resultative`` only (no
``ma_adj`` — ``*matira`` etc. are ungrammatical).

Both the existing VERB[ABIL] and the new ADJ[RESULTATIVE] readings
coexist on the same surface (``nakatira``); structural disambiguation
at rule-match time picks the right one in context.

The R&G simple #3 (``Nakatira siyang mag-isa sa bahay.``) full
integration depends on Commit 7's ``mama`` lex + composition; pinned
at 0-parse here.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === New naka_resultative ADJ surfaces ====================================


RESULTATIVE_ROOTS = [
    # (root, expected_surface, expected_gloss)
    ("tira", "nakatira", "living, residing (in a place)"),
    ("upo",  "nakaupo",  "sitting, seated"),
    ("higa", "nakahiga", "lying down, recumbent"),
    ("tayo", "nakatayo", "standing"),
    ("tabi", "nakatabi", "beside, adjacent"),
]


class TestNakaResultativeAdjSurfaces:
    """Each canonical stative-locative root produces a new
    ADJ[RESULTATIVE=YES] analysis on the ``naka+root`` surface."""

    @pytest.mark.parametrize("root,surface,_gloss", RESULTATIVE_ROOTS)
    def test_surface_produces_adj_analysis(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = [
            a for a in out
            if a.pos == "ADJ" and a.lemma == root
        ]
        assert len(adj) == 1, (
            f"expected exactly one ADJ[lemma={root}] analysis for "
            f"{surface!r}; got {[(a.pos, a.lemma) for a in out]}"
        )

    @pytest.mark.parametrize("root,surface,_gloss", RESULTATIVE_ROOTS)
    def test_surface_carries_resultative_flag(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adj = next(
            a for a in out if a.pos == "ADJ" and a.lemma == root
        )
        assert adj.feats.get("RESULTATIVE") == "YES"
        assert adj.feats.get("PREDICATIVE") == "YES"
        assert adj.feats.get("LEMMA") == root


# === Existing VERB abilitative reading still fires ========================


class TestVerbAbilitativeStillWorks:
    """The pre-Commit-6 verbal ``naka-`` abilitative reading
    (paradigms.yaml ``maka`` affix-class, MOOD=ABIL) must continue
    to fire — both analyses coexist on the same surface."""

    @pytest.mark.parametrize("root,surface,_gloss", RESULTATIVE_ROOTS)
    def test_surface_also_produces_abil_verb(
        self, root: str, surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        verbs = [
            a for a in out
            if a.pos == "VERB"
            and a.lemma == root
            and a.feats.get("MOOD") == "ABIL"
        ]
        assert len(verbs) >= 1, (
            f"VERB[lemma={root}, MOOD=ABIL] analysis for {surface!r} "
            f"must continue to fire post-Commit-6"
        )


# === Negative: bare roots not indexed as ADJ ==============================


class TestBareRootNotIndexedAsAdj:
    """Per the Phase 5g policy (bare roots are nouns, derivations are
    adjectives), the bare citation forms (``tira``, ``upo``, ``higa``,
    ``tayo``, ``tabi``) should not analyse as ADJ — only the
    ``naka+root`` derivation."""

    @pytest.mark.parametrize("root,_surface,_gloss", RESULTATIVE_ROOTS)
    def test_bare_root_not_adj(
        self, root: str, _surface: str, _gloss: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(root))
        adj = [a for a in out if a.pos == "ADJ"]
        assert adj == [], (
            f"bare root {root!r} should NOT be indexed as ADJ; "
            f"got {[(a.pos, a.lemma) for a in adj]}"
        )


# === Sentence-level integration (predicative-ADJ) =========================


class TestSentenceIntegration:
    """Predicative-ADJ clauses with naka_resultative ADJ heads parse
    via the existing Phase 5g Commit 3 predicative-ADJ rule."""

    def test_nakatira_with_locative_pp(self) -> None:
        """``Nakatira si Maria sa bahay.`` "Maria lives in the
        house" — the Phase 5g predicative-ADJ rule fires on the
        ADJ[RESULTATIVE=YES] head."""
        parses = parse_text("Nakatira si Maria sa bahay.")
        assert len(parses) >= 1

    def test_nakaupo_with_locative_pp(self) -> None:
        parses = parse_text("Nakaupo siya sa silya.")
        assert len(parses) >= 1

    def test_nakatayo_bare_predicative(self) -> None:
        parses = parse_text("Nakatayo ang lalaki.")
        assert len(parses) >= 1


# === R&G "Ang Manok" simple #3 — see test_phase5n_rg_simples.py ==========
#
# Phase 5n.A Commit 7 lands the depictive secondary-predicate rule
# (``NP[CASE=NOM] → PRON[CASE=NOM] PART[LINK=NG] ADV[MAGISA=YES]``)
# in cfg/nominal.py and unblocks ``Nakatira siyang mag-isa sa bahay.``
# (R&G simple #3) plus simple #1. The integration assertions live in
# the dedicated Commit-7 test file.
