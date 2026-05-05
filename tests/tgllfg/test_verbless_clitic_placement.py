"""Phase 5e Commit 22: verbless clitic placement.

The Phase 4 §7.3 Wackernagel placement pass was verb-anchored:
when no VERB token was present in the input, the pass returned
the analyses unchanged. This left verbless predicate
constructions like ``Maganda na ka`` "You're beautiful already"
or ``Hindi ka maganda`` "You're not beautiful" without proper
clitic placement — even though the cluster ordering rules
themselves don't depend on the anchor being a verb.

Phase 5e Commit 22 lifts the deferral by adding a fallback
anchor: when no VERB exists, the first non-clitic, non-NEG-PART,
non-punctuation token serves as the placement anchor. The same
cluster machinery (PRON post-anchor, adv enclitics at clause-end)
applies uniformly, so existing post-NOUN PRON / pre-linker PRON
exceptions and clitic ordering all carry over.

These tests cover:

* Verbless adj-pred + adv enclitic: ``Maganda na ka`` reorders
  to put adv at clause-end and PRON in the post-anchor cluster.
* Verbless adj-pred + multiple clitics: ``Maganda na ka ba``
  composes the PRON-cluster with two adv enclitics.
* Verbless + pre-anchor clitic: ``Hindi ka maganda`` hoists
  ``ka`` to post-anchor; ``hindi`` stays pre-anchor.
* No regression on verbed clauses (the VERB anchor still wins
  when present).
* No regression on existing exceptions: post-NOUN PRON
  (``Bahay ko``) and other already-correct surfaces still
  return unchanged.
* Anchor selection: the first non-clitic content word is the
  anchor. ``hindi`` is skipped (NEG-PART). Punctuation is
  skipped. Demonstrative DET (``ito``) and other content words
  still serve as valid anchors.
"""

from __future__ import annotations

from tgllfg.clitics import reorder_clitics
from tgllfg.morph import analyze_tokens
from tgllfg.text import split_enclitics, split_linker_ng, tokenize


def _pipeline(text: str) -> list[str]:
    """Run tokenize + clitic-pass and return the lemma list."""
    toks = tokenize(text)
    toks = split_enclitics(toks)
    toks = split_linker_ng(toks)
    ml = analyze_tokens(toks)
    ml = reorder_clitics(ml)
    return [c[0].lemma if c else "?" for c in ml]


# === Verbless adj-pred + adv enclitic =====================================


class TestVerblessAdvEnclitic:
    """The clearest motivating case: an adj-pred sentence with an
    adv enclitic that lands BEFORE a PRON clitic in the input.
    Cluster ordering puts PRON in the post-anchor cluster and adv
    at clause-end."""

    def test_maganda_na_ka(self) -> None:
        # ``Maganda na ka.`` → ``maganda ka . na``
        # (PRON `ka` post-anchor cluster; adv `na` at clause-end).
        # Phase 5g: ``maganda`` analyses as ADJ with lemma ``ganda``,
        # mirroring the verbal-paradigm convention (``kumain`` →
        # ``kain``); the placement order itself is unchanged.
        out = _pipeline("Maganda na ka.")
        assert out == ["ganda", "ka", ".", "na"]

    def test_maganda_na_ka_ba(self) -> None:
        # Two adv enclitics + PRON.
        out = _pipeline("Maganda na ka ba.")
        # PRON in cluster, both advs at clause-end (priority order).
        assert out == ["ganda", "ka", ".", "na", "ba"]

    def test_maganda_ba_ka(self) -> None:
        # adv before PRON in input.
        out = _pipeline("Maganda ba ka.")
        assert out == ["ganda", "ka", ".", "ba"]

    def test_maganda_ka_ba(self) -> None:
        # Already in canonical order — no actual reorder needed but
        # the pass still recognises the anchor and keeps it stable.
        out = _pipeline("Maganda ka ba.")
        assert out == ["ganda", "ka", ".", "ba"]


# === Verbless + pre-anchor NEG hoisting ====================================


class TestVerblessNegHoist:
    """``hindi`` and ``huwag`` (PART[POLARITY=NEG]) sit pre-anchor.
    Pre-anchor PRON clitics hoist out and join the post-anchor
    cluster."""

    def test_hindi_ka_maganda(self) -> None:
        # ``Hindi ka maganda.`` → ``hindi maganda ka .``
        # (`hindi` pre-anchor stays; `ka` hoists to post-anchor).
        # Phase 5g: ``maganda`` lemma is ``ganda``.
        out = _pipeline("Hindi ka maganda.")
        assert out == ["hindi", "ganda", "ka", "."]

    def test_hindi_na_ka_maganda(self) -> None:
        # NEG + adv + PRON before predicate.
        out = _pipeline("Hindi na ka maganda.")
        # `hindi` pre-anchor; `maganda` anchor; `ka` post-anchor;
        # `na` adv at clause-end.
        assert out == ["hindi", "ganda", "ka", ".", "na"]

    def test_hindi_ba_ka_maganda(self) -> None:
        out = _pipeline("Hindi ba ka maganda.")
        assert out == ["hindi", "ganda", "ka", ".", "ba"]


# === Anchor selection rules ===============================================


class TestVerblessAnchorSelection:
    """The anchor is the first non-clitic, non-NEG-PART,
    non-punctuation token. Various predicate-head categories
    (NOUN, ADJ, ADP, DET) all qualify."""

    def test_anchor_is_adj(self) -> None:
        # ``maganda`` is ADJ (Phase 5g) with lemma ``ganda`` — the
        # anchor selection still picks the first content token.
        out = _pipeline("Maganda na ka.")
        assert out[0] == "ganda"

    def test_anchor_is_noun(self) -> None:
        # ``Bata ka.`` "You're a child." NOUN anchor. ``ka`` is
        # PRON post-NOUN, the §7.8 exception keeps it in place.
        # Net result: unchanged surface.
        out = _pipeline("Bata ka.")
        assert out == ["bata", "ka", "."]

    def test_anchor_is_adp(self) -> None:
        # ``Dito ka.`` "You're here." ADP (locative dem) is the
        # anchor. ``ka`` is PRON-clitic; not post-NOUN, so it
        # joins the post-anchor cluster — which is the same
        # position as its original index. Net result: unchanged.
        out = _pipeline("Dito ka.")
        assert out == ["dito", "ka", "."]

    def test_noun_with_post_noun_na_is_linker(self) -> None:
        # ``Bata na ka.`` — the §7.5 disambiguator (Phase 5e
        # Commit 16) treats post-NOUN ``na`` as the linker, not
        # the adv enclitic. So ``na`` stays in place; only ``ka``
        # is a clitic. The cluster slot for ``ka`` is right after
        # the NOUN anchor — but that's the post-NOUN exception
        # case, so ``ka`` would normally stay there too. The
        # reorder pulls ``ka`` into the cluster post-anchor (which
        # IS the same position) and leaves ``na`` in place.
        out = _pipeline("Bata na ka.")
        assert out == ["bata", "ka", "na", "."]


# === Existing exceptions still work =======================================


class TestVerblessExistingExceptions:
    """Post-NOUN PRON (Phase 5c §7.8 lift) — kept in place even in
    verbless inputs."""

    def test_post_noun_pron_stays(self) -> None:
        # ``Bahay ko.`` — `ko` is post-NOUN, stays as possessor.
        out = _pipeline("Bahay ko.")
        assert out == ["bahay", "ko", "."]

    def test_post_noun_pron_with_dem(self) -> None:
        # ``Bahay ko ito.`` — `ko` post-NOUN, `ito` is dem (DET).
        out = _pipeline("Bahay ko ito.")
        assert out == ["bahay", "ko", "ito", "."]


# === Verbed clauses unchanged =============================================


class TestVerbedRegression:
    """When a VERB is present, the verb-anchor wins (existing
    behavior). Verbless anchor lookup only fires when no VERB
    exists. Pin a few representative verbed surfaces."""

    def test_verbed_av_intransitive(self) -> None:
        out = _pipeline("Kumain ako.")
        assert out == ["kain", "ako", "."]

    def test_verbed_with_neg_and_clitic(self) -> None:
        out = _pipeline("Hindi ka kumain.")
        assert out == ["hindi", "kain", "ka", "."]

    def test_verbed_with_adv_enclitic(self) -> None:
        out = _pipeline("Kumain na ako.")
        assert out == ["kain", "ako", ".", "na"]

    def test_verbed_with_pron_and_adv(self) -> None:
        out = _pipeline("Kumain na ka.")
        assert out == ["kain", "ka", ".", "na"]


# === Edge cases ===========================================================


class TestVerblessEdgeCases:
    """Inputs that have no anchor at all should pass through
    unchanged (no infinite loop, no error)."""

    def test_only_punct(self) -> None:
        out = _pipeline(".")
        assert out == ["."]

    def test_empty(self) -> None:
        # Tokenizer may produce empty or single-element lists; the
        # pass should handle both gracefully.
        out = _pipeline("")
        assert out in ([], [""])
