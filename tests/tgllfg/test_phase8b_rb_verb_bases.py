# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.B: R&B 1986 missing-from-lex verb bases + pag_an cell.

Closes the audit-surfaced lex gap from the Wave 1 pilot's R&B
1986 verb-base inventory — see ``docs/coverage.md`` § "Wave 1
pilot baseline" (formerly ``docs/coverage-audit-2026-05.md`` §5;
rolled up 2026-05-22). All 71 distinct missing bases extracted
post-8.A/8.N are addressed here by adding 52 new VERB entries to
``data/tgl/verbs.yaml``. Also lands the ``pag_an`` paradigm cell
follow-on from Phase 8.A for ``pinagbintangan``-style LF PFV
forms.

Affix-class translations (R&B notation → YAML cell name):

    -um-  → um         -in    → in_oblig
    mag-  → mag        -an    → an_oblig
    ma-   → ma         i-     → i_oblig
    mang- → mang       ika-   → ika
    maka- → maka       ipag-  → ipag
                       ipang- → ipang
                       pag-...-an → pag_an  (new in 8.B C3)

Convention: every entry's ``affix_class`` ends in ``maka``
(aptative), per the Phase 8.A pattern.

Skipped R&B headwords (out of 8.B scope; tracked separately):

- ``pa-`` / ``pag-`` prefixed derivations of existing bases
  (``paalam``, ``pagbili``, ``pakamatay``, ``palari``,
  ``paligo``, ``panalo``, ``pangyari``, ``patingin``,
  ``patuloy``, ``pakinig``, ``pakiusap``, ``pagkaroon``).
  Productive derivations; analyzer composes from existing base.
- ``asso`` (OCR mis-extraction of ``usap``, already in lex).
- ``lari`` (likely OCR of ``laki``, already in adjectives.yaml).
- ``galit`` / ``gulat`` / ``gutom`` / ``haba`` / ``puno`` —
  already present as ADJ / NOUN; verbal-state senses are
  produced by ``ma_adj`` and ``ma-`` derivation paradigms.
- ``magka-`` reciprocal/coincidence senses (no paradigm cell;
  separate paradigm-extension work).

Known coverage edges (deferred):

- The ``pag_an`` cell generates correct LF surfaces for
  consonant-final stems (``pinagbintangan``, ``pinagsikapan``)
  and for ``/a/``-final stems via the analyzer's h-insertion
  pipeline (``pinaggastahan``). Vowel-final stems ending in
  ``/o/``, ``/i/``, ``/u/`` (e.g., ``laro`` → ``*pinaglaruan``,
  ``pili`` → ``*pinagpilian``) need additional sandhi flags
  (h-insertion or o→u raising) — separate paradigm-extension
  follow-on. The ``affix_class`` registration includes
  ``pag_an`` for those bases anyway, so the gap closes when
  the sandhi work lands.
- The ``ika`` cell has ``transitivity: TR`` constraint, so
  INTR bases with R&B-listed ``ika-`` (``gulo``, ``punit``)
  don't currently produce ``ikinagulo``-style surfaces.
  Either drop ``ika`` from those INTR registrations later
  or relax the cell's TR constraint — separate paradigm work.
"""

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


class TestPhase8bNewBasesAnalyze:
    """Each new R&B base produces a non-_UNK analysis on a
    representative AV inflected form (mostly PFV via mag-/-um-/ma-
    based on the registered affix_class)."""

    @pytest.mark.parametrize("form,lemma", [
        # Bucket A — 40 clean adds
        ("nagaaksaya",     "aksaya"),
        ("nagaalaala",     "alaala"),
        ("nagaalaga",      "alaga"),
        ("umaasa",         "asa"),
        ("nagaaway",       "away"),
        ("nagbabalita",    "balita"),
        ("nabuhay",        "buhay"),
        ("nagdidilig",     "dilig"),
        ("narinig",        "dinig"),
        ("gumagamot",      "gamot"),
        ("ginanap",        "ganap"),
        ("gumasta",        "gasta"),
        ("humihinga",      "hinga"),
        ("hinintuhan",     "hinto"),
        ("umiibig",        "ibig"),
        ("kumakasal",      "kasal"),
        ("naglaban",       "laban"),
        ("lumangoy",       "langoy"),
        ("naglaro",        "laro"),
        ("naligo",         "ligo"),
        ("nagliligpit",    "ligpit"),
        ("nagnakaw",       "nakaw"),
        ("nagpigil",       "pigil"),
        ("pinili",         "pili"),  # OF PFV (in_oblig)
        ("nagpaplantsa",   "plantsa"),
        ("napunit",        "punit"),
        ("nagregalo",      "regalo"),
        ("sumagot",        "sagot"),
        ("sumali",         "sali"),
        ("nagsikap",       "sikap"),
        ("nagsugal",       "sugal"),
        ("nasunog",        "sunog"),
        ("nagsuot",        "suot"),
        ("nagtago",        "tago"),
        ("natalo",         "talo"),
        ("tumalon",        "talon"),
        ("tumanggap",      "tanggap"),
        ("nagturo",        "turo"),
        ("nagumpisa",      "umpisa"),
        # Bucket B — affix-OCR normalize
        ("lumalamig",      "lamig"),
        ("pumansin",       "pansin"),
        ("ipininta",       "pinta"),
        ("sumakay",        "sakay"),
        ("sumasakit",      "sakit"),
        ("sumalubong",     "salubong"),
        ("sumama",         "sama"),
        ("sumunod",        "sunod"),
        ("tumugtog",       "tugtog"),
        # Bucket C — pa-prefix false positive
        ("pumatay",        "patay"),
        # Bucket D — OCR-fix renames
        ("nagpakilala",    "pakilala"),
        ("nakalimot",      "limot"),
    ])
    def test_base_analyzes_to_lemma(
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


class TestPhase8bPagAnCell:
    """The new ``pag_an`` paradigm cell generates the LF PFV /
    IPFV / CTPL surfaces for mag-class verbs.

    PFV (the audit-surfaced target) is canonical
    ``pinag-X-an``. IPFV adds cv-redup of the base; CTPL drops
    the ``-in-`` infix.

    Tested on a consonant-final base (``bintang``) and a
    consonant-final mag-class with mag + pag_an
    (``sikap``)."""

    @pytest.mark.parametrize("form,lemma,voice,aspect", [
        ("pinagbintangan",   "bintang", "DV", "PFV"),
        ("pinagbibintangan", "bintang", "DV", "IPFV"),
        ("pagbibintangan",   "bintang", "DV", "CTPL"),
        ("pinagsikapan",     "sikap",   "DV", "PFV"),
        ("pinagsisikapan",   "sikap",   "DV", "IPFV"),
        ("pagsisikapan",     "sikap",   "DV", "CTPL"),
    ])
    def test_pag_an_surface(
        self, form: str, lemma: str, voice: str, aspect: str
    ) -> None:
        a = _first_analysis(form)
        assert a is not None, f"{form!r} produced no analysis"
        assert a.pos == "VERB"
        assert a.lemma == lemma
        feats = dict(a.feats) if a.feats else {}
        assert feats.get("VOICE") == voice, (
            f"{form!r} voice={feats.get('VOICE')}, expected {voice}"
        )
        assert feats.get("ASPECT") == aspect, (
            f"{form!r} aspect={feats.get('ASPECT')}, expected {aspect}"
        )


class TestPhase8bDinigSandhi:
    """The ``d_to_r`` sandhi flag added to ``dinig`` enables the
    canonical ``narinig`` (heard) surface from ``ma- + dinig`` via
    /d/ → /r/ between vowels."""

    @pytest.mark.parametrize("form", ["narinig", "maririnig"])
    def test_dinig_d_to_r(self, form: str) -> None:
        a = _first_analysis(form)
        assert a is not None
        assert a.pos == "VERB"
        assert a.lemma == "dinig"


class TestPhase8bPagAnVowelFinalDeferred:
    """Vowel-final stems ending in ``/o/``, ``/i/``, ``/u/`` don't
    yet produce correct LF surfaces under the new ``pag_an`` cell
    (need additional sandhi flags: h-insertion / o→u raising).

    Pin the current (still-UNK) behavior so a future paradigm-
    extension PR adding the sandhi flags will surface as a visible
    signal here."""

    @pytest.mark.parametrize("form", [
        "pinaglaruan",     # laro LF PFV with o→u raising
        "pinagpilian",     # pili LF PFV
    ])
    def test_vowel_final_pag_an_still_unk(self, form: str) -> None:
        a = _first_analysis(form)
        # When the sandhi work lands, this will produce a VERB
        # analysis — flip the assertion at that point.
        assert a is None or a.pos == "_UNK", (
            f"unexpectedly parsed {form!r} — flip the pin"
        )
