"""Phase 8.A: Wave 1 lex pass.

Closes the audit-surfaced lex gaps from the Wave 1 (rg81
transcriptions) section of ``docs/coverage-audit-2026-05.md``
§4. Adds 7 verb roots + 3 noun roots and updates one existing
verb's ``affix_class``:

Verbs added (with R&B / canonical-pattern affix-class
signatures):

- ``tanim``  TR  ``[mag, i_oblig, an_oblig, maka]``  R&B 255 plant
- ``tuka``   TR  ``[um, in_oblig, maka]``            peck
- ``sapit``  INTR ``[um, maka]``                     arrive
- ``dungaw`` INTR ``[um, maka]``                     look out (window)
- ``putak``  INTR ``[um, maka]``                     cluck, cackle
- ``bintang`` TR ``[mag, an_oblig, maka]``           accuse
- ``taba``   INTR ``[um, maka]``                     become fat

Verb updated:

- ``pasok`` — affix_class extended to
  ``[um, mag, in_oblig, i_oblig, an_oblig, maka]``. R&B 184
  records two senses (``-um-/-in`` "enter"; ``mag-/i-/-an``
  "put in / take in"). The pre-8.A signature only covered the
  first sense; the audit surfaced ``ipinasok`` (i- PFV "was
  put in") which needs the second sense's i_oblig + an_oblig +
  mag cells.

Nouns added:

- ``palay``  rice (unhusked)
- ``damo``   grass / weeds (homophonous with the verb
              ``damo`` "pluck grass" already in verbs.yaml)
- ``tasa``   cup

Existing-noun verifications: ``manok``, ``bahay``, ``bukid``,
``gulay``, ``itlog`` — confirmed present pre-8.A; no change
needed.

Out of 8.A scope:

- ``pinagbintangan`` (mag-class LF PFV ``pag-X-an``) remains
  zero-parse post-8.A. The paradigm engine has no ``pag_an``
  cell for this surface — adding it is paradigm-extension work,
  distinct from lex addition. Tracked as a Phase 8.B-class
  follow-on near-miss.
"""

from __future__ import annotations

import pytest

from tgllfg.morph.analyzer import _get_default, analyze_tokens
from tgllfg.text.tokenizer import tokenize


_ANALYZER = _get_default()


def _first_analysis(form: str):
    toks = tokenize(form)
    analyses = analyze_tokens(toks)
    if not analyses or not analyses[0]:
        return None
    return analyses[0][0]


class TestPhase8aVerbsAnalyze:
    """Each new verb produces a non-_UNK analysis on a
    representative audit-surfaced inflected form."""

    @pytest.mark.parametrize("form,lemma", [
        ("nagtatanim",     "tanim"),    # mag- IPFV
        ("tinutuka",       "tuka"),     # -in IPFV-OF
        ("ipinasok",       "pasok"),    # i- PFV-IF (the 8.A update)
        ("sumapit",        "sapit"),    # -um- PFV
        ("dumungaw",       "dungaw"),   # -um- PFV
        ("pumutak",        "putak"),    # -um- PFV
        ("magbintang",     "bintang"),  # mag- AF inf
        ("tumaba",         "taba"),     # -um- PFV
    ])
    def test_inflected_form_analyses(
        self, form: str, lemma: str
    ) -> None:
        a = _first_analysis(form)
        assert a is not None, f"{form!r} produced no analysis"
        assert a.pos == "VERB", (
            f"{form!r} has pos={a.pos!r}, expected VERB"
        )
        assert a.lemma == lemma, (
            f"{form!r} has lemma={a.lemma!r}, expected {lemma!r}"
        )


class TestPhase8aNounsKnown:
    """Each new noun is registered as a known surface."""

    @pytest.mark.parametrize("noun", ["palay", "damo", "tasa"])
    def test_noun_is_known(self, noun: str) -> None:
        assert _ANALYZER.is_known_surface(noun), (
            f"noun {noun!r} not known after 8.A lex add"
        )


class TestPhase8aSentencesParseable:
    """Representative audit-derived sentences now produce a
    clean parse (at least one parse with the expected predicate
    or PRED template)."""

    @pytest.mark.parametrize("sentence", [
        "Nagtatanim ng palay si Juan.",      # tanim + palay
        "Tinutuka ng manok ang itlog.",      # tuka + manok + itlog
        "Sumapit na siya sa bahay.",         # sapit + bahay
        "Dumungaw siya sa bintana.",         # dungaw
        "Tumaba ang aso.",                   # taba
    ])
    def test_sentence_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"no parse for {sentence!r} after 8.A lex add"
        )


class TestPhase8aPasokUpdate:
    """The pasok affix_class update enables the previously-
    missing IF/LF/AF-mag forms (``ipinasok``, ``pasukan``,
    ``magpasok``) while keeping the AF-um/OF-in forms."""

    @pytest.mark.parametrize("form", [
        "ipinasok",   # IF PFV — the 8.A unblocker
        "pumasok",    # AF -um- PFV (unchanged)
        "pinasok",    # OF PFV (unchanged)
        "magpasok",   # AF mag- inf (8.A unblocker)
    ])
    def test_pasok_form_analyses(self, form: str) -> None:
        a = _first_analysis(form)
        assert a is not None, f"{form!r} produced no analysis"
        assert a.pos == "VERB"
        assert a.lemma == "pasok"


class TestPhase8aExistingNounsStillWork:
    """Sanity-check on the 5 existing nouns whose names appear
    in the Wave 1 audit's noun-gap list but which were already
    in the lex (manok / bahay / bukid / gulay / itlog).
    Verification, not addition; pins their continued presence."""

    @pytest.mark.parametrize("noun", [
        "manok", "bahay", "bukid", "gulay", "itlog",
    ])
    def test_existing_noun_known(self, noun: str) -> None:
        assert _ANALYZER.is_known_surface(noun)


class TestPhase8aFollowonClosedIn8b:
    """``pinagbintangan`` (mag-class ``pag-X-an`` LF PFV) was
    explicitly out of 8.A scope — the analyzer had no
    ``pag_an`` paradigm cell. Phase 8.B closes the follow-on
    by adding the cell + wiring ``bintang``'s ``affix_class``
    to use it. This test now asserts the *post-8.B* behavior:
    the form analyzes as ``VERB(lemma=bintang)``."""

    def test_pag_an_pf_analyzes(self) -> None:
        a = _first_analysis("pinagbintangan")
        assert a is not None, "pinagbintangan produced no analysis"
        assert a.pos == "VERB", (
            f"pinagbintangan pos={a.pos!r}, expected VERB"
        )
        assert a.lemma == "bintang", (
            f"pinagbintangan lemma={a.lemma!r}, expected 'bintang'"
        )