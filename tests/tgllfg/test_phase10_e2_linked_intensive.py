# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.E.2 — the ``ma-X na ma-X`` linked-intensive adjective.

PK91 (Kroeger 1991 §4.5) analyses a gradable ``ma-`` adjective doubled
across the linker (free ``na`` after consonant-final ``mabait``; bound
``-ng`` after vowel-final ``maganda``) as a complex zero-level adjective
(A°) meaning "very X". Two pieces:

* **Grammar** — a ``cfg/nominal.py`` rule
  ``ADJ[PREDICATIVE=true, COMP_DEGREE=INTENSIVE] → ADJ PART[LINK] ADJ``
  with a same-lemma gate (``(↑ LEMMA) = ↓3 LEMMA``) producing the
  intensive ADJ constituent (``COMP_DEGREE=INTENSIVE`` + the Phase-10
  redup-taxonomy tag ``REDUP_SEM=INTENS``). The basic predicative-ADJ-S
  rule lifts ``REDUP_SEM`` to the matrix (parallel to the existing
  ``INTENS`` / ``DISTRIB`` / ``KASING_N`` lifts and the Phase 10.E.1
  clause-level ``REDUP_SEM``). Closes kroeger ex-25a + so1972
  sent-810 / sent-1100.

* **Clitic placement** — ``_is_post_doubled_adj_pron`` keeps a 2P clitic
  in situ after the whole complex (``Mabait na mabait ka``) instead of
  hoisting it between the conjuncts (PK91's A° diagnostic
  ``*Mabait ka=ng mabait``).

The same-lemma gate keeps the unrelated two-adjective linker
construction (``mahirap na masarap``, rg-int sent-1372) out of the
intensive reading.

* **OCR tokenisation** — the ay-fronted surface's OCR'd form
  ``Kayo•y mabait na mabait`` (so1972 sent-1099) was blocked because the
  ``'y`` enclitic apostrophe is rendered as a bullet (U+2022). The
  bound-clitic splitters (``split_apostrophe_y`` / ``split_apostrophe_t``)
  now accept ``•`` / ``·`` in the apostrophe slot — guarded by the
  existing vowel-final-host + bare-``y``/``t`` follower so hyphen-redup
  (``dala•dalawa``) and leading bullets (``•Juan``) are untouched.
"""

import pytest

from tgllfg.clitics import reorder_clitics
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import analyze_tokens
from tgllfg.text import (
    split_apostrophe_t,
    split_apostrophe_y,
    split_enclitics,
    split_linker_ng,
    tokenize,
)


def _clause_redup_sems(text: str) -> set[str]:
    """The atom-valued ``REDUP_SEM`` of every parse's matrix
    f-structure (ignores the empty-FStructure no-op nodes the
    lift-from-absent leaves on degree-less predicates)."""
    out: set[str] = set()
    for _ct, fs, _a, _d in parse_text(text):
        v = fs.feats.get("REDUP_SEM")
        if isinstance(v, str):
            out.add(v)
    return out


def _has_intensive_constituent(text: str) -> bool:
    """True if some parse contains the doubled-ADJ constituent
    (``ADJ[...COMP_DEGREE=INTENSIVE...]``) — frame-independent proof
    that the Phase 10.E.2 rule fired (works for the ay-fronted variant
    whose intensive marking rides on the constituent, not the matrix)."""
    def walk(node) -> bool:
        if "COMP_DEGREE=INTENSIVE" in node.label:
            return True
        return any(walk(c) for c in node.children)
    return any(walk(ct) for ct, _fs, _a, _d in parse_text(text))


def _reorder(text: str) -> list[str]:
    """tokenize + clitic-pass → lemma list (mirrors the established
    verbless-clitic-placement test idiom)."""
    toks = split_linker_ng(split_enclitics(tokenize(text)))
    return [c[0].lemma if c else "?" for c in reorder_clitics(analyze_tokens(toks))]


# === Grammar: linked-intensive parses with INTENSIVE degree ============


@pytest.mark.parametrize(
    "text",
    [
        "Mabait na mabait ka.",       # PK91 ex-25a (free na, 2P clitic)
        "Mabait na mabait kayo.",     # so1972 sent-810 / sent-1100
        "Magandang maganda ang bata.",  # bound -ng, full-NP subject
        "Maganda na maganda ang bata.",  # free-na variant of the same
    ],
)
def test_linked_intensive_surfaces_redup_sem_intens(text: str) -> None:
    """A ``ma-X na ma-X`` predicative clause parses and some parse
    carries ``REDUP_SEM=INTENS`` on the matrix f-structure."""
    assert "INTENS" in _clause_redup_sems(text), text


@pytest.mark.parametrize(
    "text",
    [
        "Mabait na mabait ka.",
        "Magandang maganda ang bata.",
        "Kayo ay mabait na mabait.",   # ay-fronted: intensive on the constituent
    ],
)
def test_linked_intensive_builds_intensive_constituent(text: str) -> None:
    """Every linked-intensive frame (incl. the ay-fronted variant)
    builds the ``ADJ[COMP_DEGREE=INTENSIVE]`` doubled-ADJ constituent."""
    assert _has_intensive_constituent(text), text


def test_ay_fronted_linked_intensive_parses() -> None:
    """``Kayo ay mabait na mabait.`` (S&O 1972 ay-inversion) parses —
    the doubled-ADJ feeds the ay-fronted predicative-ADJ gap clause."""
    assert len(parse_text("Kayo ay mabait na mabait.")) >= 1


# === Same-lemma gate ===================================================


def test_different_adjectives_not_intensive() -> None:
    """``Mahirap na masarap ang buhay.`` (two DIFFERENT adjectives via
    the linker, rg-int sent-1372 "difficult but delicious") must NOT
    read as a linked-intensive — the same-lemma gate
    (``(↑ LEMMA) = ↓3 LEMMA``) blocks it. It may still parse via the
    pre-existing manner-adverb path, but never with REDUP_SEM=INTENS."""
    assert "INTENS" not in _clause_redup_sems("Mahirap na masarap ang buhay.")


def test_different_adjectives_no_intensive_constituent() -> None:
    """The doubled-ADJ constituent is never built for two distinct
    adjectives (the lemma-clash kills the rule at unification)."""
    assert not _has_intensive_constituent("Mahirap na masarap ang buhay.")


# === Audit closures (exact attested surfaces) ==========================


@pytest.mark.parametrize(
    "text",
    [
        "Mabait na mabait ka.",     # kroeger1991 page-126/ex-25a
        "Mabait na mabait kayo.",   # so1972 page-498/sent-810 + page-598/sent-1100
    ],
)
def test_audit_sentences_close(text: str) -> None:
    """The naturalistic-audit zero-parse sentences this sub-PR targets
    now parse (≥1 complete parse)."""
    assert len(parse_text(text)) >= 1


# === Clitic placement: A° keeps the 2P clitic post-complex =============


def test_clitic_kept_after_complex_free_na() -> None:
    """``Mabait na mabait ka.`` — the 2P NOM clitic ``ka`` stays after
    the whole ``ma-X na ma-X`` complex; it is NOT hoisted between the
    conjuncts (``*Mabait ka na mabait``, PK91's A° diagnostic)."""
    assert _reorder("Mabait na mabait ka.") == ["bait", "na", "bait", "ka", "."]


def test_clitic_kept_after_complex_bound_ng() -> None:
    """Bound ``-ng`` variant: ``Magandang maganda ka.`` keeps ``ka``
    after the complex (the ``-ng`` linker is split off by
    ``split_linker_ng`` and still anchors the doubled-ADJ domain)."""
    assert _reorder("Magandang maganda ka.") == ["ganda", "-ng", "ganda", "ka", "."]


def test_single_adj_clitic_unaffected() -> None:
    """The exclusion is narrow: a plain single-ADJ predicate
    (``Mabait ka.``) keeps its ordinary post-anchor 2P clitic — the
    doubled-ADJ exclusion must not perturb it."""
    assert _reorder("Mabait ka.") == ["bait", "ka", "."]


# === Bullet-as-apostrophe OCR tokenisation (split_apostrophe_{y,t}) ====


def _apos_norm(text: str) -> list[str]:
    return [t.surface for t in split_apostrophe_y(split_apostrophe_t(tokenize(text)))]


def test_bullet_apostrophe_ay_linked_intensive_closes() -> None:
    """``Kayo•y mabait na mabait.`` (so1972 sent-1099, the OCR'd
    ``Kayo'y`` ay-fronted linked-intensive) now parses — the bullet is
    normalised to the ``ay`` clitic and the doubled-ADJ feeds the
    ay-fronted predicate."""
    assert len(parse_text("Kayo•y mabait na mabait.")) >= 1


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Kayo•y mabait", ["Kayo", "ay", "mabait"]),   # • → 'y → ay
        ("ko·y bahay", ["ko", "ay", "bahay"]),          # · (middle dot) too
        ("bawa•t araw", ["bawat", "araw"]),             # • → 't → joined bawat
        ("rito'y siyesta", ["rito", "ay", "siyesta"]),  # straight quote intact
        ("Maria't Juan", ["Maria", "at", "Juan"]),      # straight quote intact
    ],
)
def test_apostrophe_like_glyphs_normalise(text: str, expected: list[str]) -> None:
    """The bound-clitic splitters accept ``•`` / ``·`` / ``'`` in the
    apostrophe slot."""
    assert _apos_norm(text) == expected


@pytest.mark.parametrize("text", ["dala•dalawa", "•Juan", "Lumakad nang dala•dalawa"])
def test_bullet_not_apostrophe_when_guard_fails(text: str) -> None:
    """The vowel-final-host + bare-``y``/``t`` guard keeps the bullet
    intact for the hyphen-redup (``dala•dalawa``) and leading-bullet
    (``•Juan``) uses — it is NOT collapsed to ``ay`` / ``at``."""
    assert "•" in _apos_norm(text)
