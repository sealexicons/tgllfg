# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 23 — bagamat / 'pag orthographic contractions
(§18 L94 + L107).

Closes §18 L94 (``bagamat`` as orthographic variant of ``bagaman``)
and §18 L107 (``'pag`` / ``pag`` as variants of ``kapag``) via the
Phase 5j Commit 7 LEMMA-collapse mechanic — point YAML entries at
the canonical via the LEMMA feat without replicating the structural
behaviour.

L94: ``bagamat`` (concessive, formal register) — added as a new
PART entry with surface=bagamat and feats=
``{COMP_TYPE: CONC, LEMMA: bagaman, REGISTER: FORMAL}``. The
analyzer's MorphAnalysis.lemma collapses to ``bagaman``.

L107: ``'pag`` (conditional, colloquial elision) — handled via the
existing tokenization pipeline + an updated LEMMA on the existing
``pag`` entry. The tokenizer splits ``'pag`` into ``'`` + ``pag``
(apostrophe is a non-word char); ``_strip_non_content`` filters the
standalone apostrophe; the ``pag`` entry matches the remainder. The
``pag`` entry's LEMMA was updated from ``pag`` → ``kapag`` in
Commit 23 so all short forms (``pag``, ``'pag``) collapse to the
canonical ``kapag``.

Adding a literal ``'pag`` lex entry was considered and rejected:
the tokenizer never yields a single ``'pag`` token, so such an
entry would never fire.
"""

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph import Analyzer, load_morph_data
from tgllfg.text.tokenizer import tokenize


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === bagamat — L94 ==================================================


class TestBagamatLemmaCollapse:
    """``bagamat`` analyzer-level LEMMA collapses to canonical
    ``bagaman``."""

    def test_bagamat_morph_lemma(self) -> None:
        analyzer = Analyzer(load_morph_data())
        out = analyzer.analyze_one(_tok("bagamat"))
        parts = [a for a in out if a.pos == "PART"]
        assert len(parts) >= 1
        bagamat_entries = [
            a for a in parts if a.feats.get("COMP_TYPE") == "CONC"
        ]
        assert len(bagamat_entries) == 1
        assert bagamat_entries[0].lemma == "bagaman"
        assert bagamat_entries[0].feats.get("LEMMA") == "bagaman"
        assert bagamat_entries[0].feats.get("REGISTER") == "FORMAL"


class TestBagamatParse:
    """``bagamat`` heads a CONC adjunct clause exactly like
    ``bagaman`` (the canonical form)."""

    @pytest.mark.parametrize("sentence", [
        "Bagamat kumain ako, pumunta siya.",
        "Bagamat kumain siya, pumunta ako.",
    ])
    def test_bagamat_parses_as_concessive(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        conc_adjuncts = [
            a for a in adjuncts
            if a.feats.get("SUBORD_TYPE") == "CONC"
        ]
        assert len(conc_adjuncts) == 1


# === 'pag — L107 ====================================================


class TestApostrophePagTokenization:
    """``'pag`` tokenizes to two tokens (apostrophe + pag) — direct
    tokenizer assertion documenting the pipeline's contract."""

    def test_apostrophe_pag_splits(self) -> None:
        toks = tokenize("'pag")
        assert [t.surface for t in toks] == ["'", "pag"]

    def test_apostrophe_pag_in_sentence_splits(self) -> None:
        toks = tokenize("'pag kumain ako")
        assert [t.surface for t in toks] == ["'", "pag", "kumain", "ako"]


class TestPagLemmaCollapse:
    """The ``pag`` lex entry's LEMMA is now ``kapag`` (canonical
    full form) so all short forms (``pag``, ``'pag``) collapse via
    the LEMMA-collapse mechanic."""

    def test_pag_morph_lemma_is_kapag(self) -> None:
        analyzer = Analyzer(load_morph_data())
        out = analyzer.analyze_one(_tok("pag"))
        parts = [a for a in out if a.pos == "PART"]
        cond_entries = [
            a for a in parts if a.feats.get("COMP_TYPE") == "COND"
        ]
        assert len(cond_entries) == 1
        assert cond_entries[0].lemma == "kapag"
        assert cond_entries[0].feats.get("LEMMA") == "kapag"


class TestApostrophePagParse:
    """``'pag`` parses as a COND subordinator — the apostrophe is
    stripped as non-content, and the ``pag`` entry matches the
    remainder (which now has LEMMA=kapag)."""

    @pytest.mark.parametrize("sentence", [
        "'Pag kumain ako, pumunta siya.",
        "'pag kumain ako, pumunta siya.",
    ])
    def test_apostrophe_pag_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        cond_adjuncts = [
            a for a in adjuncts
            if a.feats.get("SUBORD_TYPE") == "COND"
        ]
        assert len(cond_adjuncts) == 1


# === Baseline regressions ===========================================


class TestCanonicalFormsRegression:
    """Canonical forms ``bagaman`` and ``kapag`` continue to fire
    after the Commit 23 additions / LEMMA changes."""

    def test_bagaman_still_parses_and_collapses(self) -> None:
        parses = parse_text("Bagaman kumain ako, pumunta siya.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert any(
            a.feats.get("SUBORD_TYPE") == "CONC" for a in adjuncts
        )

    def test_kapag_still_parses(self) -> None:
        parses = parse_text("Kapag kumain ako, pumunta siya.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert any(
            a.feats.get("SUBORD_TYPE") == "COND" for a in adjuncts
        )

    def test_pag_still_parses(self) -> None:
        parses = parse_text("Pag kumain ako, pumunta siya.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        assert any(
            a.feats.get("SUBORD_TYPE") == "COND" for a in adjuncts
        )
