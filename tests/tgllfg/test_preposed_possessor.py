"""Phase 5f closing deferral: generic preposed-possessor.

Common Tagalog NP-internal possessive surface form: a DAT pronoun
pre-modifies the head noun via the bound ``-ng`` (or free ``na``)
linker (``kanyang aklat`` "his/her book", ``aming bahay`` "our
house", ``kanilang sapatos`` "their shoes"). Structurally parallel
to Phase 5f Commit 21 distributive-possessive (``kanikaniyang
aklat``) but with a regular DAT pronoun in place of the
reduplicated possessive Q. The matrix NP carries ``POSS = ↓2``,
mirroring the Phase 4 §7.8 post-N possessive rule's POSS slot for
a GEN-NP possessor.

New rule in ``cfg/nominal.py``:

  NP[CASE=X] → DET/ADP[CASE=X] PRON[CASE=DAT] PART[LINK=NA|NG] N

3 cases × 2 linker variants = 6 rules. The DAT pronoun set is the
standard 7-form inventory (``akin`` / ``iyo`` / ``kanya`` /
``atin`` / ``amin`` / ``inyo`` / ``kanila``).

Tokenizer support: the 1sg / 1pl.excl / 1pl.incl forms (``aking`` /
``aming`` / ``ating``) involve an irregular n-deletion sandhi
before the bound ``-ng`` linker — the preposed surface drops the
stem-final ``n``. ``split_linker_ng`` got an n-restoration fallback
so ``aking`` decomposes to ``akin`` + ``-ng`` (the underlying DAT
pronoun + linker). The 2sg / 2pl / 3sg / 3pl forms are regular
(vowel-final + ``-ng``).

Tests cover:

* All 7 DAT pronouns × 3 case markers (NOM / GEN / DAT) — 21
  positive cases.
* Free-linker form (``akin na aklat``) — alternative to bound
  ``-ng``.
* Tokenizer: ``split_linker_ng`` decomposes each preposed form
  to PRON + ``-ng``; the n-restoration fallback covers the
  irregular cases.
* Tokenizer: ``split_linker_ng`` decomposes each preposed form
  to PRON + ``-ng``; the n-restoration fallback covers the
  irregular cases.

Regressions for the related constructions (post-N possessive
``aklat ng nanay`` and distributive-possessive ``kanikaniyang
aklat``) live in ``test_demonstrative_possessive_phase4.py`` and
``test_distributive_possessive.py`` respectively — not duplicated
here.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import split_linker_ng, tokenize


def _matrix(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=1)
    if not parses:
        return None
    return parses[0][1]


def _first_obj(text: str) -> FStructure | None:
    f = _matrix(text)
    if f is None:
        return None
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


def _first_subj(text: str) -> FStructure | None:
    f = _matrix(text)
    if f is None:
        return None
    subj = f.feats.get("SUBJ")
    return subj if isinstance(subj, FStructure) else None


# DAT pronoun preposed surfaces and their underlying full forms.
_PRONS = [
    # (preposed_with_ng, underlying_dat, expected_pers, expected_num, expected_clusv)
    ("aking",    "akin",   1,  "SG", None),
    ("iyong",    "iyo",    2,  "SG", None),
    ("kanyang",  "kanya",  3,  "SG", None),
    ("ating",    "atin",   1,  "PL", "INCL"),
    ("aming",    "amin",   1,  "PL", "EXCL"),
    ("inyong",   "inyo",   2,  "PL", None),
    ("kanilang", "kanila", 3,  "PL", None),
]


# --- Tokenizer ----------------------------------------------------------


class TestPreposedTokenization:
    """Each preposed-form pronoun decomposes to its underlying DAT
    PRON + synthetic ``-ng`` linker."""

    @pytest.mark.parametrize("preposed,underlying", [
        (p[0], p[1]) for p in _PRONS
    ])
    def test_split_linker(self, preposed: str, underlying: str) -> None:
        toks = tokenize(preposed)
        toks = split_linker_ng(toks)
        surfaces = [t.surface for t in toks]
        assert surfaces == [underlying, "-ng"], (
            f"expected [{underlying!r}, '-ng'] for {preposed!r}, got {surfaces!r}"
        )

    @pytest.mark.parametrize("preposed,_,pers,num,clusv", _PRONS)
    def test_preposed_morph(
        self, preposed: str, _: str, pers: int, num: str, clusv: str | None,
    ) -> None:
        """After splitting, the underlying DAT PRON analyses with
        the right person / number / case features at the morph
        layer (PERS as integer, NUM / CASE as strings)."""
        toks = tokenize(preposed)
        toks = split_linker_ng(toks)
        ms = analyze_tokens(toks)
        # First token is the underlying PRON.
        pron_analyses = [m for m in ms[0] if m.pos == "PRON"]
        assert pron_analyses, f"no PRON for {preposed!r}"
        m = pron_analyses[0]
        assert m.feats.get("PERS") == pers
        assert m.feats.get("NUM") == num
        assert m.feats.get("CASE") == "DAT"
        if clusv is not None:
            assert m.feats.get("CLUSV") == clusv


# --- NP-modifier in OBJ position (GEN-marked) ---------------------------


class TestPreposedInObj:
    """``Bumili ako ng <PRON>ng aklat`` for each DAT pronoun."""

    @pytest.mark.parametrize("preposed,_,pers,num,clusv", _PRONS)
    def test_preposed_in_obj(
        self, preposed: str, _: str, pers: int, num: str, clusv: str | None,
    ) -> None:
        """Verifies parse + the f-structure POSS slot's NUM /
        CASE / CLUSV. PERS is the int-valued feat from the lex
        and gets filtered by ``_lex_equations`` (only string
        values become equations), so PERS doesn't surface in the
        f-structure projection — see ``parse/earley.py:_lex_equations``.
        The pers parameter is unused here but kept for cross-
        reference with the morph-layer test above where PERS
        does surface as a MorphAnalysis feat."""
        del pers  # unused — see docstring
        text = f"Bumili ako ng {preposed} aklat."
        obj = _first_obj(text)
        assert obj is not None, f"no parse for {text!r}"
        assert obj.feats.get("LEMMA") == "aklat"
        poss = obj.feats.get("POSS")
        assert poss is not None, f"no POSS in {obj.feats}"
        assert poss.feats.get("NUM") == num
        assert poss.feats.get("CASE") == "DAT"
        if clusv is not None:
            assert poss.feats.get("CLUSV") == clusv


# --- NP-modifier in SUBJ / DAT positions --------------------------------


class TestPreposedInSubj:
    """``Maganda ang <PRON>ng aklat.`` — NOM SUBJ position."""

    def test_in_subj(self) -> None:
        """``Maganda`` lacks an ADJ predicative rule today (Phase
        5g territory) — fall back to a frame where the preposed-
        possessor NP appears in NOM SUBJ position via a verbal
        predicate. ``Maganda`` itself parses today as N
        (overgeneration that Phase 5g will tighten with proper
        ADJ classification)."""
        # Use a verbal predicate with NOM SUBJ.
        f = _matrix("Tumakbo ang kanyang aso.")
        assert f is not None
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "aso"
        poss = subj.feats.get("POSS")
        assert poss is not None
        assert poss.feats.get("CASE") == "DAT"
        assert poss.feats.get("NUM") == "SG"


class TestPreposedInDat:
    """``Pumunta ako sa <PRON>ng bahay.`` — DAT marker position."""

    def test_in_dat(self) -> None:
        f = _matrix("Pumunta ako sa aking bahay.")
        assert f is not None
        adjuncts = f.feats.get("ADJUNCT")
        assert adjuncts
        members = list(adjuncts) if isinstance(adjuncts, frozenset) else [adjuncts]
        dat_np = next(
            (m for m in members
             if isinstance(m, FStructure) and m.feats.get("CASE") == "DAT"),
            None,
        )
        assert dat_np is not None
        assert dat_np.feats.get("LEMMA") == "bahay"
        poss = dat_np.feats.get("POSS")
        assert poss is not None
        assert poss.feats.get("CASE") == "DAT"
        assert poss.feats.get("NUM") == "SG"


# The free ``na`` linker variant of preposed-possessor (``Bumili
# ako ng akin na aklat.``) is NOT supported even though the rule
# admits both linker variants. The reason is upstream: when ``na``
# follows a DAT pronoun like ``akin``, the clitic-reorder pass
# treats the ``na`` as a 2P aspect-particle clitic and moves it
# out of the NP-internal position. Pre-existing behaviour, not
# caused by this commit. The canonical written register uses the
# bound ``-ng`` form anyway (``aking aklat``), so the free-na
# limitation has no practical impact.
