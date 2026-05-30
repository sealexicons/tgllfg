# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.1: lex completions for ROOTs referenced by
post-8.5's broader paradigm-cell inventory.

First sub-PR in the post-8.5.N series (factored out of post-8.5 per
mechanism class, smallest blast-radius first). Adds 6 simple lex
entries — no new paradigm cells, no chart rules, no sandhi engine.

Subsequent post-8.5.N sub-PRs will build on these ROOTs:

* post-8.5.2 — affix_class extensions on existing roots
  (``pintas`` + ``ma_an`` for ``mapintasan``;
  ``hiya`` ma-X-in disposition cell for ``mahiyain``;
  ``tama`` adj_redup for ``tamang-tama``; etc.)
* post-8.5.3 — NEW ``medial_vowel_syncope`` sandhi engine flag
  (post-8.1 deferral: ``sundin`` / ``sundan`` / ``kilalanin``)
* post-8.5.4..N — NEW paradigm cell families
  (``pag-CV-X-CV-X`` intensive gerund for ``pagsasamasama``;
  ``naka-CV-X`` for ``nakababata``; CV-X collaborative redup
  for ``tulung-tulong``; CV-CV redup on ADJ for ``balubaluktot``;
  ``salin-lahi`` noun-noun hyphen compound merge mechanism)

Six entries:

(a) **baluktot** ADJ "crooked, bent". ``affix_class: []`` (bare-
    indexed, not ``ma_adj`` — parallel to ``tama``, ``husto``,
    ``hilaw``; the ma_adj prefix-deriving class would suppress
    bare-root indexing per analyzer.py line 553 logic). Base
    for the future CV-CV redup ``balubaluktot``
    (PAG-AARAL/sent-8).

(b) **kapisan** ADJ "together, co-resident". Used predicatively
    in PAMILYA/sent-16. Adding directly as ADJ rather than
    deriving from ``pisan`` ROOT + ka- prefix (no
    ``ka_relational`` paradigm cell exists; would be a new
    cell-family). The relational-NOUN family ``kasama``,
    ``kaibigan``, ``kapatid``, ``kapisan`` is irregular enough
    that direct-lex is a reasonable approach.

(c) **kasya** ADJ "sufficient, fitting". Used predicatively
    (``Kasya na ang pera.``). The verbal family
    ``magkasya`` / ``pinagkakasya`` will derive from a parallel
    VERB entry in a later post-8.5.N.

(d) **bigkas** VERB "pronounce, articulate". Closes the bare-
    lex gap on ``pagbigkas`` (NOUN gerund via the existing
    ``pag_gerund`` cell, opt-in via affix_class). Part of the
    PAG-AARAL/sent-5 trio (``mapintasan`` + ``pagbigkas`` +
    ``pagsasamasama`` all needed for that sentence to close;
    only the second piece lands in this sub-PR).

(e) **salin** NOUN "translation, transfer, generation". Used
    in the ``salin-lahi`` compound (PAMILYA/sent-17). The
    compound-merge mechanism is a later post-8.5.N.

(f) **lahi** NOUN "race, lineage, ethnicity". Used in
    ``salin-lahi`` (PAMILYA/sent-17).

Audit signal (post-10 baseline → post-8.5.1): 0 closures, 0
regressions across all 9 waves. Foundational lex with no
immediate audit yield — the gated sentences need additional
paradigm/chart work (scoped to post-8.5.[2-N]). +6 unattributed
exemplars demonstrate immediate parse-readiness of each new
ROOT (Baluktot ang kahoy. / Kapisan din ang kapatid. / Kasya
na ang pera. / Maganda ang pagbigkas ng salita. / Iba ang lahi
nila. / Maganda ang salin.).
"""

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


class TestLexCompletions:
    """post-8.5.1: each new ROOT reaches the analyzer index."""

    def test_baluktot_adj_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("baluktot")
        adj = analyzer._index.adjectives.get("baluktot", [])
        assert any(a.lemma == "baluktot" for a in adj), \
            "baluktot should be bare-indexed as ADJ"

    def test_kapisan_adj_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("kapisan")
        adj = analyzer._index.adjectives.get("kapisan", [])
        assert any(a.lemma == "kapisan" for a in adj)

    def test_kasya_adj_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("kasya")
        adj = analyzer._index.adjectives.get("kasya", [])
        assert any(a.lemma == "kasya" for a in adj)

    def test_bigkas_verb_known(self) -> None:
        """``bigkas`` VERB drives the mag- AV + in_oblig OV +
        pag_gerund family (the canonical TR-verb cell set). Verify
        the AV ``magbigkas`` and the gerund ``pagbigkas`` lex."""
        analyzer = _get_default()
        # magbigkas — AV CTPL bare (mag-class)
        assert analyzer.is_known_surface("magbigkas")
        # pagbigkas — pag- gerund (NOUN POS-flip)
        assert analyzer.is_known_surface("pagbigkas")

    def test_salin_noun_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("salin")
        nouns = analyzer._index.nouns.get("salin", [])
        assert any(a.lemma == "salin" for a in nouns)

    def test_lahi_noun_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("lahi")
        nouns = analyzer._index.nouns.get("lahi", [])
        assert any(a.lemma == "lahi" for a in nouns)


class TestUnattributedExemplars:
    """post-8.5.1: each new lex root parses in a minimal frame."""

    def test_baluktot_predicative(self) -> None:
        parses = parse_text("Baluktot ang kahoy.", n_best=1)
        assert len(parses) >= 1

    def test_kapisan_predicative(self) -> None:
        parses = parse_text("Kapisan din ang kapatid.", n_best=1)
        assert len(parses) >= 1

    def test_kasya_predicative(self) -> None:
        parses = parse_text("Kasya na ang pera.", n_best=1)
        assert len(parses) >= 1

    def test_pagbigkas_gerund(self) -> None:
        parses = parse_text("Maganda ang pagbigkas ng salita.", n_best=1)
        assert len(parses) >= 1

    def test_lahi_noun(self) -> None:
        parses = parse_text("Iba ang lahi nila.", n_best=1)
        assert len(parses) >= 1

    def test_salin_noun(self) -> None:
        parses = parse_text("Maganda ang salin.", n_best=1)
        assert len(parses) >= 1


class TestAntiRegression:
    """post-8.5.1 anti-regression: existing lex unchanged."""

    def test_hirap_adj_preserved(self) -> None:
        """``mahirap`` ADJ still derives from ``hirap`` ROOT
        (sibling of ``baluktot`` in the b/h ADJ block)."""
        analyzer = _get_default()
        adj = analyzer._index.adjectives.get("mahirap", [])
        assert any(a.lemma == "hirap" for a in adj)

    def test_kainin_preserved(self) -> None:
        """``kainin`` OV CTPL bare cell still fires on ``kain``
        (a canonical TR-verb anchor in the audit family). Adding
        ``bigkas`` to the b-VERB block is purely additive."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("kainin")

    def test_lalaki_noun_preserved(self) -> None:
        """``lalaki`` NOUN (the alphabetically-adjacent entry to
        the new ``lahi`` insertion in nouns.yaml) is preserved."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("lalaki")
