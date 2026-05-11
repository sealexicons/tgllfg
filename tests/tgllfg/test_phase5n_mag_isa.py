"""Phase 5n.A Commit 5 — mag-isa "alone" ADV tokenizer hyphen-split (§18 L60).

The default tokenizer splits on internal hyphens, so ``mag-isa``
"alone" surfaces as three tokens (``mag``, ``-``, ``isa``) rather
than one. The ``mag`` element analyses as ``_UNK`` and ``isa`` as
NUM[CARDINAL_VALUE=1], breaking any composition that needs the
manner-adverb reading. This blocks R&G "Ang Manok" simple #3
(``Nakatira siyang mag-isa sa bahay.``) and any other use of
``mag-isa``.

Closure (this commit): add ``magisa`` as the joined-form lex surface
in ``data/tgl/particles.yaml`` so the Phase 5f Commit 14
``merge_hyphen_compounds`` pre-pass collapses the three tokens into
one. The ``LEMMA: mag-isa`` feat (via the Phase 5j Commit 7 /
Phase 5n.A Commit 4 collapse mechanic) maps the analysis's
``lemma`` field to the canonical hyphenated form. The ``MAGISA: YES``
flag is set as a diagnostic discriminator for future grammar rules.

Same lex pattern as Phase 5m Commit 5's ``paminsanminsan`` /
``LEMMA: paminsan-minsan``.

The full sentence integration (R&G #3) requires Commits 6 and 7 too.
"""

from __future__ import annotations

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer
from tgllfg.text.multiword import merge_hyphen_compounds
from tgllfg.text.tokenizer import tokenize


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Tokenizer + multiword pre-pass =======================================


class TestTokenizerCollapse:
    """The tokenizer splits on hyphen; the multiword pre-pass
    collapses the three tokens into one ``magisa`` token."""

    def test_raw_tokenizer_splits_on_hyphen(self) -> None:
        toks = tokenize("mag-isa")
        surfaces = [t.surface for t in toks]
        assert surfaces == ["mag", "-", "isa"], (
            f"raw tokenizer should produce three tokens; got {surfaces!r}"
        )

    def test_multiword_prepass_collapses(self) -> None:
        toks = tokenize("mag-isa")
        merged = merge_hyphen_compounds(toks)
        surfaces = [t.surface for t in merged]
        assert surfaces == ["magisa"], (
            f"merge_hyphen_compounds should collapse to one ``magisa`` "
            f"token; got {surfaces!r}"
        )


# === Lex hit ==============================================================


class TestLexAnalysis:
    """The joined surface ``magisa`` analyses as ADV with the
    canonical hyphenated lemma and the diagnostic MAGISA flag."""

    def test_magisa_analyses_as_adv(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("magisa"))
        adv = [a for a in out if a.pos == "ADV"]
        assert len(adv) == 1, (
            f"expected exactly one ADV analysis for ``magisa``; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )

    def test_magisa_lemma_is_canonical_hyphenated(self) -> None:
        """The Phase 5n.A Commit 4 LEMMA-collapse maps the analysis's
        lemma field to ``mag-isa`` (the canonical hyphenated form)
        even though the indexed surface is the joined ``magisa``."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("magisa"))
        adv = next(a for a in out if a.pos == "ADV")
        assert adv.lemma == "mag-isa", (
            f"lemma should be canonical ``mag-isa``; got {adv.lemma!r}"
        )

    def test_magisa_carries_diagnostic_feats(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("magisa"))
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
