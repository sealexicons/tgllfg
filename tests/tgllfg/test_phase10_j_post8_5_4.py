# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.4: ``pagsasamasama`` lex completion.

Fourth sub-PR in the post-8.5.N series. Closes PAG-AARAL/sent-5
(wave-1) as the **third prerequisite** in the trio
(``mapintasan`` from post-8.5.2 + ``pagbigkas`` from post-8.5.1 +
``pagsasamasama`` from this PR).

## Survey-misdiagnosis #6

The post-8 survey scoped this as needing a NEW ``pag-CV-X-CV-X``
intensive gerund paradigm cell. Probing showed the actual gap is
much narrower: ``samasama`` (the reduplicated form of ``sama``)
isn't lex'd as a base ROOT. With ``samasama`` added as a VERB
entry with ``affix_class: [pag_gerund]``, the **existing**
Phase 9.X.pre-4.7 pag-gerund cells produce BOTH:

* ``pagsamasama`` (pag + samasama, no cv-redup)
* ``pagsasamasama`` (pag + cv_redup(samasama) + ROOT —
  the PAG-AARAL/sent-5 target)

No new paradigm cell needed. The "double-redup" surface
``pagsasamasama`` is just `pag + cv-redup(<already-reduplicated
base>)`. Treating ``samasama`` as its own ROOT (with distinct
semantics "gather together / assemble", distinct from bare
``sama`` "accompany / go with") is the cleanest analysis —
parallel to how `kapisan` (post-8.5.1) was added as a separate
relational-NOUN entry rather than derived from a hypothetical
`pisan` + ka-relational cell.

## Closure

PAG-AARAL/sent-5: ``Ayaw nilang mapintasan ang maling pagbigkas
o maling pagsasamasama ng salita.`` "They don't want their
incorrect pronunciation or incorrect combining-together of words
to be criticized." The three lex prerequisites are now all in
place:

| Word | Prerequisite | Sub-PR |
| --- | --- | --- |
| ``mapintasan`` | pintas + ma_an | post-8.5.2 |
| ``pagbigkas`` | bigkas + pag_gerund (lex) | post-8.5.1 |
| ``pagsasamasama`` | samasama + pag_gerund (lex) | post-8.5.4 |

## Audit signal (post-8.5.3 → post-8.5.4)

* **wave-1 +1** (PAG-AARAL/sent-5) → **102/123 → 103/123 = 83.74%**.
* All other waves unchanged.
* 0 regressions across all 9 waves.

## Unattributed exemplars

* ``unattributed/pag-gerund-redup`` × 2 (Maganda ang pagsasamasama
  ng salita.; Naging madali ang pagsasamasama ng mga estudyante.).
"""

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


class TestSamasamaLex:
    """post-8.5.4: ``samasama`` VERB root produces the pag-gerund
    family."""

    def test_pagsasamasama_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("pagsasamasama")

    def test_pagsamasama_known(self) -> None:
        """The no-cv-redup pag-gerund variant on the same root."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("pagsamasama")

    def test_pagsasamasama_analyzes_as_samasama_rooted(self) -> None:
        analyzer = _get_default()
        analyses = analyzer._index.verb_forms.get("pagsasamasama", [])
        # pag_gerund POS-flips to NOUN; check the nouns index too
        if not analyses:
            analyses = analyzer._index.nouns.get("pagsasamasama", [])
        target = [a for a in analyses if a.lemma == "samasama"]
        assert target, (
            "pagsasamasama should analyze as samasama-rooted NOUN gerund"
        )


class TestPagAaralSent5:
    """post-8.5.4: PAG-AARAL/sent-5 wave-1 closure — the third
    prerequisite (pagsasamasama) lands, paired with post-8.5.1's
    pagbigkas + post-8.5.2's mapintasan."""

    def test_full_sentence(self) -> None:
        parses = parse_text(
            "Ayaw nilang mapintasan ang maling pagbigkas o maling "
            "pagsasamasama ng salita.",
            n_best=1,
        )
        assert len(parses) >= 1

    def test_pagsasamasama_simple(self) -> None:
        """Standalone gerund head."""
        parses = parse_text(
            "Maganda ang pagsasamasama ng salita.", n_best=1,
        )
        assert len(parses) >= 1


class TestAntiRegression:
    """post-8.5.4 anti-regression: existing sama forms preserved."""

    def test_sama_surfaces_preserved(self) -> None:
        """Existing ``sama`` mag-/um- paradigm surfaces unchanged
        by adding ``samasama`` as a separate ROOT."""
        analyzer = _get_default()
        # sama (mag-class IPFV) produces nagsasama
        assert analyzer.is_known_surface("nagsasama")
        # sama (um-class PFV) produces sumama
        assert analyzer.is_known_surface("sumama")

    def test_existing_pag_gerund_preserved(self) -> None:
        """Pre-post-8.5.4 pag-gerund surfaces unchanged
        (``pagaaral``, ``pagbigkas`` continue to fire — note
        ``pagaaral`` is the canonical hyphen-merged index form;
        the surface ``pag-aaral`` reaches the same analysis via
        the tokenizer's special-case prefix handling)."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("pagbigkas")
        assert analyzer.is_known_surface("pagaaral")
