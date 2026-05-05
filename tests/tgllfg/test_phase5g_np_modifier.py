"""Phase 5g Commit 2: NP-internal ADJ modifier rules.

Adds four ``N``-level rules that admit pre-N and post-N adjectival
modification with both linker variants (the standalone ``na`` and
the bound ``-ng``):

    N → ADJ PART[LINK=NA] N      pre-N, consonant-final adj
    N → ADJ PART[LINK=NG] N      pre-N, vowel-final adj
    N → N PART[LINK=NA] ADJ      post-N, consonant-final N
    N → N PART[LINK=NG] ADJ      post-N, vowel-final N

The rules are right-recursive in the pre-N case (the rightmost
daughter is ``N``, and an adj-modified ``N`` is still ``N``), so
multi-modifier composition (``mabilis na magandang bata``) parses
without further rules.

The disambiguator (``clitics/placement.py``) gains an ADJ + ``na``
+ (NOUN | ADJ) right-context branch that selects the linker reading
of ``na`` in NP-internal modifier contexts; the ALREADY-clitic
reading (``Maganda na ka.``) is preserved because its right-context
is PRON / DET / clause-end.

These tests verify rule firing via c-tree shape rather than
f-structure inspection — the modifier sits on the head N's
``ADJ-MOD`` set, which is not lifted to the matrix NP in this
commit. Lift to NP-level visibility lands separately if needed.
"""

from __future__ import annotations

import pytest

from tgllfg.common import CNode
from tgllfg.pipeline import parse_text


# === Helpers ==============================================================


def _ctree_labels(node: CNode) -> list[str]:
    """Pre-order labels of a c-tree, stripped of the empty-string
    leaf (``CNode("•")``-equivalent) used by the renderer."""
    out = [node.label]
    for c in node.children:
        out.extend(_ctree_labels(c))
    return out


def _adj_modified_n(node: CNode) -> CNode | None:
    """Find an ``N`` node whose immediate children include an ``ADJ``
    daughter (either pre-N or post-N order)."""
    if node.label == "N":
        labels = [c.label for c in node.children]
        if "ADJ" in labels and "PART" in labels and "N" in labels:
            return node
    for c in node.children:
        m = _adj_modified_n(c)
        if m is not None:
            return m
    return None


def _parse_or_none(text: str) -> CNode | None:
    parses = parse_text(text, n_best=1)
    if not parses:
        return None
    return parses[0][0]


# === Pre-N ADJ modifier ===================================================


class TestPreNVowelFinalAdj:
    """Pre-N adjectives ending in a vowel take the bound ``-ng``
    linker. ``magandang bata`` "beautiful child"."""

    def test_subj_position(self) -> None:
        ctree = _parse_or_none("Kumain ang magandang bata.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        # The N has ADJ + PART + N as immediate children (pre-N order).
        assert [c.label for c in n.children] == ["ADJ", "PART", "N"]

    def test_obj_position(self) -> None:
        # ``Kumain ng magandang isda ang bata.`` — fish in OBJ.
        ctree = _parse_or_none("Kumain ng magandang isda ang bata.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["ADJ", "PART", "N"]

    def test_dat_position(self) -> None:
        # ``Pumunta ako sa magandang bahay.`` "I went to a beautiful house."
        ctree = _parse_or_none("Pumunta ako sa magandang bahay.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["ADJ", "PART", "N"]


class TestPreNConsonantFinalAdj:
    """Pre-N adjectives ending in a consonant take the standalone
    ``na`` linker. ``mabilis na bata`` "quick child"."""

    def test_subj_position(self) -> None:
        ctree = _parse_or_none("Tumakbo ang mabilis na bata.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["ADJ", "PART", "N"]

    def test_obj_position(self) -> None:
        ctree = _parse_or_none("Kumain ang aso ng mabilis na isda.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["ADJ", "PART", "N"]

    def test_dat_position(self) -> None:
        ctree = _parse_or_none("Pumunta ang bata sa mabilis na aso.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["ADJ", "PART", "N"]


# === Post-N ADJ modifier ==================================================


class TestPostNVowelFinalN:
    """Post-N modifier where the head N is vowel-final → bound
    ``-ng`` linker on the head. ``batang maganda`` "child who is
    beautiful"."""

    def test_subj_position(self) -> None:
        ctree = _parse_or_none("Tumakbo ang batang maganda.")
        assert ctree is not None
        # Find the N with [N PART ADJ] daughter sequence.
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["N", "PART", "ADJ"]

    def test_obj_position(self) -> None:
        ctree = _parse_or_none("Kumain ang aso ng isdang maganda.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["N", "PART", "ADJ"]


class TestPostNConsonantFinalN:
    """Post-N modifier where the head N is consonant-final →
    standalone ``na`` linker. ``aklat na maganda`` "beautiful book"."""

    def test_subj_position(self) -> None:
        ctree = _parse_or_none("Kumain ang bata ng aklat na maganda.")
        assert ctree is not None
        n = _adj_modified_n(ctree)
        assert n is not None
        assert [c.label for c in n.children] == ["N", "PART", "ADJ"]


# === Multi-modifier composition (right-recursion in pre-N rules) =========


class TestMultiModifier:
    """Pre-N modifiers chain via right-recursion: the rightmost
    daughter of ``N → ADJ PART N`` is itself ``N``, so a second
    modifier rule can fire over an already-modified N."""

    def test_two_pre_n_modifiers(self) -> None:
        # ``mabilis na magandang bata`` "quick beautiful child".
        # Outer rule: ADJ_mabilis + PART_na + N where the inner N
        # is itself adj-modified (ADJ_maganda + PART_-ng + N_bata).
        ctree = _parse_or_none("Kumain ang mabilis na magandang bata.")
        assert ctree is not None
        # Find any N that has ADJ + PART + N children where the
        # inner N also has ADJ + PART + N (= recursion).
        outer = _adj_modified_n(ctree)
        assert outer is not None
        outer_labels = [c.label for c in outer.children]
        assert outer_labels == ["ADJ", "PART", "N"]
        inner = outer.children[2]  # the rightmost N
        # inner should itself be adj-modified
        inner_labels = [c.label for c in inner.children]
        assert inner_labels == ["ADJ", "PART", "N"]

    def test_three_pre_n_modifiers(self) -> None:
        # ``mabilis na maliit na magandang bata`` "quick small
        # beautiful child".
        ctree = _parse_or_none(
            "Kumain ang mabilis na maliit na magandang bata."
        )
        assert ctree is not None
        # Walk the spine of ADJ-modified Ns and count.
        depth = 0
        cur = _adj_modified_n(ctree)
        while cur is not None and [c.label for c in cur.children] == [
            "ADJ", "PART", "N",
        ]:
            depth += 1
            cur = cur.children[2]
            if [c.label for c in cur.children] != ["ADJ", "PART", "N"]:
                break
        assert depth == 3, f"expected 3 nested adj-modifiers; got {depth}"


# === Disambiguator: ADJ + na + N is the linker, not ALREADY ==============


class TestDisambiguatorAdjNa:
    """Phase 5g Commit 2 added an ADJ + ``na`` + (NOUN | ADJ)
    right-context branch to ``disambiguate_homophone_clitics`` so
    NP-internal modifier surfaces don't lose the linker reading
    of ``na`` to the ALREADY-clitic reading."""

    def test_adj_na_n_picks_linker(self) -> None:
        # Without the disambiguator branch, ``mabilis na bata``
        # would have ``na`` hoisted to clause-end as ALREADY,
        # breaking the modifier composition and leaving the
        # sentence unparseable as an NP-modifier construction.
        ctree = _parse_or_none("Tumakbo ang mabilis na bata.")
        assert ctree is not None

    def test_adj_na_adj_picks_linker(self) -> None:
        # ``mabilis na magandang bata`` — the inner ``maganda``
        # is the right-context content for the outer ``na``.
        ctree = _parse_or_none("Kumain ang mabilis na magandang bata.")
        assert ctree is not None


# === Negative: predicative-adj clauses don't regress ======================


class TestNoPredicativeRegression:
    """The disambiguator distinguishes NP-modifier contexts (ADJ +
    ``na`` + N/ADJ) from predicative-adj clause contexts (ADJ +
    ``na`` + PRON / DET / clause-end). The latter must continue
    to pre-parse correctly via the placement pipeline."""

    def test_maganda_na_ka_placement_unchanged(self) -> None:
        # Already covered by test_verbless_clitic_placement.py
        # but pin the regression here too: the ALREADY-clitic
        # reading of ``na`` after a predicative ADJ followed by
        # a PRON is preserved.
        from tgllfg.morph import analyze_tokens
        from tgllfg.text import tokenize, split_enclitics, split_linker_ng
        from tgllfg.clitics import disambiguate_homophone_clitics

        toks = split_linker_ng(split_enclitics(tokenize("Maganda na ka.")))
        ml = disambiguate_homophone_clitics(analyze_tokens(toks))
        # The ``na`` token should have BOTH analyses preserved
        # (linker AND clitic) — the disambiguator's ADJ + ``na``
        # + N-or-ADJ branch only fires when the right context is
        # NOUN / N / ADJ, not PRON.
        na_idx = next(i for i, t in enumerate(toks) if t.surface == "na")
        kinds = {ma.feats.get("is_clitic") is True for ma in ml[na_idx]}
        assert True in kinds, "clitic reading preserved before PRON"


# === Edge case: bare N still parses without modifier =====================


class TestBareNRegression:
    """The Phase 5g Commit 2 N-level modifier rules don't fire
    when no ADJ is present; bare-N parses are unaffected."""

    @pytest.mark.parametrize("text", [
        "Kumain ang bata.",
        "Tumakbo ang aso.",
        "Pumunta ako sa bahay.",
    ])
    def test_bare_n_parses_unchanged(self, text: str) -> None:
        parses = parse_text(text, n_best=1)
        assert parses, f"no parse for {text!r}"
        ctree = parses[0][0]
        # No ADJ daughter anywhere in the tree.
        assert "ADJ" not in _ctree_labels(ctree)
