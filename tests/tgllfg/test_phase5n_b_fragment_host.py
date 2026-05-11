"""Phase 5n.B Commit 16: fragment-host NOUN clause (§18 L96).

Closes §18.1 deferral L96 for the NOUN-host path. Target
sentences:

    Salamat.        "Thanks."
    Salamat po.     "Thank you (polite)."
    Salamat ho.     "Thank you (colloquial-polite)."

Two changes:

* ``data/tgl/nouns.yaml``: ``salamat`` NOUN entry with
  ``feats: {FRAGMENT_HOST: "YES"}``. The quoted string is
  required — bare ``YES`` is parsed as boolean ``True`` by
  pyyaml's YAML 1.1 default.

* ``cfg/clause.py``: new ``S → N`` rule gated on
  ``(↑ FRAGMENT_HOST) =c 'YES'``. Tags the matrix with
  ``CLAUSE_TYPE='FRAGMENT'`` to distinguish it from the Phase
  5m C3 ``FRAGMENT_ANSWER`` (PRON-host) path. The 2P-politeness
  clitic (``po`` / ``ho``) is absorbed by the existing Phase 5m
  ``S → S PART[CLITIC_CLASS=2P, REGISTER=POLITE]`` rule
  (``cfg/clitic.py``) once the bare fragment lifts to S.

Companion deferral L97 (standalone ``Oo.`` / ``Hindi.`` answer
clauses) closes in Phase 5n.B Commit 17 — that adds
``PRON[INTERJ=YES, ANSWER=...]`` lex entries plus an
``S_ANSWER`` rule, distinct from this NOUN-host path.

The ``FRAGMENT_HOST=YES`` lex feat opts in specific NOUNs to the
fragment-S path. Currently only ``salamat`` qualifies; future
fragment-host NOUNs (greetings, exclamations) can opt in via the
same lex feat without grammar changes.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _fragment_parse(text: str):
    """Return the parse with CLAUSE_TYPE='FRAGMENT', or None."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("CLAUSE_TYPE") == "FRAGMENT":
            return p
    return None


# === Bare fragment ===================================================


class TestBareFragment:
    """``Salamat.`` parses as a one-word matrix S with
    CLAUSE_TYPE='FRAGMENT'."""

    def test_salamat_bare(self) -> None:
        result = _fragment_parse("Salamat.")
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("LEMMA") == "salamat"
        assert fs.feats.get("FRAGMENT_HOST") is True
        # No REGISTER on bare fragment (the 2P-clitic absorption
        # rule lifts REGISTER only when the clitic is present).
        assert fs.feats.get("REGISTER") is None


# === Fragment + 2P-politeness clitic =================================


class TestFragmentWithPoliteClitic:
    """The existing Phase 5m clitic-absorption rule attaches the
    2P-politeness clitic on top of the fragment-S, lifting
    REGISTER onto the matrix."""

    @pytest.mark.parametrize("sentence,register", [
        ("Salamat po.", "POLITE"),
        ("Salamat ho.", "COLLOQUIAL_POLITE"),
    ])
    def test_salamat_with_clitic(
        self, sentence: str, register: str
    ) -> None:
        result = _fragment_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("LEMMA") == "salamat"
        assert fs.feats.get("REGISTER") == register


# === Negative: non-fragment-host NOUNs don't qualify =================


class TestNonFragmentHostNouns:
    """Regular NOUNs (without ``FRAGMENT_HOST=YES``) don't form
    one-word matrix-S — the new rule's ``=c 'YES'`` constraint
    rejects them. ``Aklat.`` / ``Bahay.`` / ``Pera.`` etc. all
    fail to parse as fragment-S."""

    @pytest.mark.parametrize("sentence", [
        "Aklat.",
        "Bahay.",
        "Pera.",
    ])
    def test_regular_nouns_dont_fragment(self, sentence: str) -> None:
        parses = parse_text(sentence)
        # No fragment-S parse for regular nouns.
        frag_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "FRAGMENT"
        ]
        assert len(frag_parses) == 0


# === Multi-word predicative-N regression =============================


class TestPredicativeNUnchanged:
    """The existing Phase 5n.B C2 predicative-N rule
    (``S → N NP[CASE=NOM]``) continues to fire on multi-word
    surfaces with salamat as predicate-N. The fragment-S rule
    is single-token only and doesn't shadow."""

    def test_salamat_predicative_n(self) -> None:
        # ``Salamat ang aklat.`` parses via the C2 predicative-N
        # path with salamat as predicate-N (semantically odd —
        # "the book is thanks" — but structurally licensed).
        parses = parse_text("Salamat ang aklat.")
        # Should produce at least one parse with PRED='BE-N <SUBJ>'
        # (predicative-N path, NOT fragment).
        be_n_parses = [
            p for p in parses
            if p[1].feats.get("PRED") == "BE-N <SUBJ>"
        ]
        assert len(be_n_parses) >= 1


# === Phase 5m fragment-answer regression =============================


class TestPhase5mFragmentAnswerUnchanged:
    """Existing Phase 5m C3 fragment-answer (Opo / Oho via PRON)
    continues to fire unchanged."""

    @pytest.mark.parametrize("sentence,register", [
        ("Opo.", "POLITE"),
        ("Oho.", "COLLOQUIAL_POLITE"),
    ])
    def test_opo_oho_unchanged(
        self, sentence: str, register: str
    ) -> None:
        parses = parse_text(sentence)
        answer_parses = [
            p for p in parses
            if p[1].feats.get("CLAUSE_TYPE") == "FRAGMENT_ANSWER"
        ]
        assert len(answer_parses) >= 1
        _ct, fs, _astr, _diags = answer_parses[0]
        assert fs.feats.get("REGISTER") == register
