# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 5 — mag-isa "alone" ADV tokenizer hyphen-split (§18 L60).

Phase 10.Y revision: the Phase 9.I tokenizer joins ``mag-isa`` into
a single token, and Phase 10.Y preserves the hyphen in the
``norm`` (since ``mag`` is in the CC-final hyphenated-only prefix
family). The lex entry's ``surface`` is now ``mag-isa`` (matching
the new canonical norm); legacy hyphenless ``magisa`` no longer
resolves.

Original Phase 5n.A note (preserved for history): the default
tokenizer used to split ``mag-isa`` into three tokens, surface
``magisa`` was the joined-form lex key, and the multiword pre-pass
collapsed the triple. Post-10.Y this is no longer the load-bearing
mechanism — the raw tokenizer handles the join AND keeps the
hyphen.
"""

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer
from tgllfg.text.multiword import merge_hyphen_compounds
from tgllfg.text.tokenizer import tokenize


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Tokenizer + multiword pre-pass =======================================


class TestTokenizerCollapse:
    """As of Phase 9.I the raw tokenizer joins
    ``Tagalog-prefix-vowelStem`` patterns (including ``mag-isa``)
    into a single token directly — the multiword pre-pass is no
    longer the load-bearing layer for this specific case. Phase 10.Y
    further preserves the internal hyphen in the ``norm`` for
    CC-final-prefix + V tokens (``mag-isa`` keeps norm ``mag-isa``).
    The pre-pass remains in place for non-prefix-vowelStem compounds
    (``tag-init``, ``daan-daan``, ``humigit-kumulang``, etc.)
    which the raw tokenizer still splits.
    """

    def test_raw_tokenizer_joins_mag_isa(self) -> None:
        """Post-10.Y: the raw tokenizer's Tagalog-prefix-vowelStem
        pattern recognises ``mag-isa`` as a single token; the norm
        preserves the hyphen since ``mag`` is in the CC-final
        hyphenated-only prefix family."""
        toks = tokenize("mag-isa")
        assert len(toks) == 1
        assert toks[0].surface == "mag-isa"
        assert toks[0].norm == "mag-isa"

    def test_multiword_prepass_idempotent_on_mag_isa(self) -> None:
        """The pre-pass receives the already-joined token from the
        raw tokenizer and leaves it unchanged (no 3-token triple to
        merge). Post-10.Y the analyzer sees the hyphenated norm
        ``mag-isa`` — matching the new canonical lex key."""
        toks = tokenize("mag-isa")
        merged = merge_hyphen_compounds(toks)
        # Pre-pass is a no-op when no 3-token X-Y triple is present.
        assert [t.norm for t in merged] == ["mag-isa"]


# === Lex hit ==============================================================


class TestLexAnalysis:
    """The canonical hyphenated surface ``mag-isa`` analyses as ADV
    with the canonical hyphenated lemma and the diagnostic MAGISA
    flag. Post-10.Y the lex key is ``mag-isa`` (matches the tokenizer
    norm); hyphenless ``magisa`` no longer resolves."""

    def test_mag_isa_analyses_as_adv(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("mag-isa"))
        adv = [a for a in out if a.pos == "ADV"]
        assert len(adv) == 1, (
            f"expected exactly one ADV analysis for ``mag-isa``; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )

    def test_mag_isa_lemma_is_canonical_hyphenated(self) -> None:
        """The analysis's lemma field is the canonical hyphenated
        ``mag-isa`` (post-10.Y same as the indexed surface)."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("mag-isa"))
        adv = next(a for a in out if a.pos == "ADV")
        assert adv.lemma == "mag-isa", (
            f"lemma should be canonical ``mag-isa``; got {adv.lemma!r}"
        )

    def test_mag_isa_carries_diagnostic_feats(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("mag-isa"))
        adv = next(a for a in out if a.pos == "ADV")
        assert adv.feats.get("MAGISA") is True
        assert adv.feats.get("ADV_TYPE") == "MANNER"
        assert adv.feats.get("LEMMA") == "mag-isa"


# === End-to-end (tokenize + collapse + analyze) ===========================


class TestEndToEnd:
    """Combined tokenizer + multiword-collapse + analyzer path: the
    raw input string ``mag-isa`` produces a single ADV analysis
    after going through the full pre-parse pipeline."""

    def test_hyphenated_input_yields_single_adv(self) -> None:
        analyzer = Analyzer.from_default()
        toks = tokenize("mag-isa")
        merged = merge_hyphen_compounds(toks)
        assert len(merged) == 1
        out = analyzer.analyze_one(merged[0])
        adv = [a for a in out if a.pos == "ADV"]
        assert len(adv) == 1
        assert adv[0].lemma == "mag-isa"
        assert adv[0].feats.get("MAGISA") is True


# === No-op regression on related multiword forms ==========================


class TestNoRegression:
    """The new ``magisa`` lex entry must not interfere with related
    forms — bare ``isa`` (cardinal 1) and bare ``mag`` (_UNK) are
    unaffected; ``paminsan-minsan`` (sibling lex pattern) still works."""

    def test_bare_isa_still_cardinal(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("isa"))
        nums = [a for a in out if a.pos == "NUM"]
        assert any(
            a.feats.get("CARDINAL") is True
            and a.feats.get("CARDINAL_VALUE") == "1"
            for a in nums
        )

    def test_paminsan_minsan_still_works(self) -> None:
        analyzer = Analyzer.from_default()
        toks = tokenize("paminsan-minsan")
        merged = merge_hyphen_compounds(toks)
        assert len(merged) == 1
        out = analyzer.analyze_one(merged[0])
        adv = [a for a in out if a.pos == "ADV"]
        assert any(a.lemma == "paminsan-minsan" for a in adv)
