"""Phase 8.N: Wave 2 lex pass.

Closes the audit-surfaced lex gaps from the Wave 2 (R&C 1990 +
R&G Intermediate + Ramos 1971) section of
``docs/coverage-audit-2026-05.md`` §§9-11 and the R&G Conv
greeting-cluster from §16.

Lex additions (in ``data/tgl/nouns.yaml``):

- ``kumusta``  NOUN  regards, greetings (the noun sense — GT's
                     "respect / regard"). Registered with
                     ``FRAGMENT_HOST: true``; admits the bare
                     ``Magandang kumusta!`` NP head and the
                     interjection ``Kumusta!`` standalone.
- ``palabas``  NOUN  show, performance        (R&G Int. §10 sample)
- ``patyo``    NOUN  yard, patio              (R&G Int. §10 sample)
- ``pelikula`` NOUN  film, movie              (R&G Int. §10 sample)
- ``sanga``    NOUN  branch (of tree)         (Ramos §10 sample)
- ``kahoy``    NOUN  wood, tree               (Ramos §10 sample)
- ``tawad``    NOUN  forgiveness; discount    (R&C 1990 §10 sample)

Lex addition (in ``data/tgl/particles.yaml``):

- ``kumusta``  ADV   how (interrogative, MANNER). Parallel to
                     ``paano`` / ``papaano`` — same wh-ADV cell.
                     Unlocks ``Kumusta ka?`` / ``Kumusta ang
                     pamilya mo?`` (the audit's predicational use).

Verb update (in ``data/tgl/verbs.yaml``):

- ``sabi`` — affix_class extended to include ``magpa``, enabling
  ``nagpasabi`` / ``nagpapasabi`` to compose via the analyzer's
  mag-pa- causative paradigm cell with the existing root
  (lemma stays ``sabi``). Probed in 8.N: extending the affix_class
  is sufficient to lift ``nagpasabi`` / ``nagpapasabi`` /
  ``magpapasabi`` from ``_UNK`` to ``VERB(lemma=sabi)``. The
  infinitive ``magpasabi`` and future-OF ``papasabihin`` remain
  ``_UNK`` — those are general paradigm-cell gaps not specific to
  ``sabi`` (same gap on ``kain``), tracked toward Phase 8.H.

Out of 8.N scope (each surfaces a *distinct* construction-class
or a-structure gap, properly closed in a follow-on sub-PR):

- ``Nagpasabi si Gina na uuwi siya.`` — finite-clause subord +
  SAY-class causative-of-saying argument-structure; Phase 8.O.
  (Pre-8.N this incorrectly fragment-parsed because ``nagpasabi``
  was ``_UNK``; post-8.N it correctly zero-parses, with a
  ``completeness-failed`` diagnostic surfacing the genuine missing
  XCOMP argument.)
- ``Humingi ba ng tawad si Deo?`` — proper-noun lex gap on
  ``Deo``; orthogonal to 8.N.
- ``Tumingin siya sa pelikula.`` — ``tingin`` registered TR (OBJ
  required); the AV form's OBL-via-``sa`` complement-licensing
  is its own a-structure question; orthogonal to 8.N.

Anti-deferral note (Phase 8.N expansion C5): the original 8.N
plan had pinned ``Kumusta ang pamilya mo?`` as out-of-scope on
the rationale "needs new construction rule". A diagnostic probe
showed that rationale was wrong — registering ``kumusta`` as a
wh-ADV (parallel to ``paano``/``bakit``/``kailan``) plugs into the
existing wh-ADV + ang-NP infrastructure with no construction work
required. Per the anti-deferral discipline (Phase 8.Y/8.Z
pattern), the carve-out was closed in 8.N itself rather than
queued as a follow-on. The user's pointer to GT's POS analysis
(ADV "how" + NOUN "respect/regard") was the prompt for the
diagnostic probe.
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


class TestPhase8nNounsKnown:
    """Each new NOUN is registered as a known surface."""

    @pytest.mark.parametrize("noun", [
        "kumusta", "palabas", "patyo", "pelikula",
        "sanga", "kahoy", "tawad",
    ])
    def test_noun_is_known(self, noun: str) -> None:
        assert _ANALYZER.is_known_surface(noun), (
            f"noun {noun!r} not known after 8.N lex add"
        )


class TestPhase8nSabiMagpaCell:
    """The ``sabi`` affix_class extension enables ``nagpasabi`` /
    ``nagpapasabi`` / ``magpapasabi`` to compose with ``lemma=sabi``
    via the mag-pa- causative cell. Pre-8.N these were ``_UNK``."""

    @pytest.mark.parametrize("form", [
        "nagpasabi",     # mag-pa- PFV
        "nagpapasabi",   # mag-pa- IPFV
        "magpapasabi",   # mag-pa- FUT
    ])
    def test_mag_pa_sabi_form_analyses(self, form: str) -> None:
        a = _first_analysis(form)
        assert a is not None, f"{form!r} produced no analysis"
        assert a.pos == "VERB", (
            f"{form!r} has pos={a.pos!r}, expected VERB"
        )
        assert a.lemma == "sabi", (
            f"{form!r} has lemma={a.lemma!r}, expected 'sabi'"
        )


class TestPhase8nKumustaDualPOS:
    """The surface ``kumusta`` produces BOTH an ADV analysis (wh-
    MANNER, from particles.yaml) and a NOUN analysis (with
    FRAGMENT_HOST, from nouns.yaml). The parser selects between
    them by context: predicational uses → ADV; nominal uses → NOUN.

    Tracks GT's POS analysis (adverb "how" + noun "respect/regard")
    — dual registration matches the observed polysemy."""

    def test_both_pos_analyses_present(self) -> None:
        toks = tokenize("kumusta")
        analyses = analyze_tokens(toks)
        assert analyses and analyses[0], "no analyses for 'kumusta'"
        seen_pos = {a.pos for a in analyses[0]}
        assert "ADV" in seen_pos, (
            f"expected ADV analysis, got {seen_pos}"
        )
        assert "NOUN" in seen_pos, (
            f"expected NOUN analysis, got {seen_pos}"
        )


class TestPhase8nSentencesParseable:
    """Audit-derived sentences whose only blocker was the 8.N lex
    addition now produce a clean parse. Each sentence below uses
    one or more of the new entries in a constructive way (predicate
    + arg, existential, modifier position, or wh-predicate)."""

    @pytest.mark.parametrize("sentence", [
        # Common-noun additions
        "Humingi siya ng tawad.",         # hingi + tawad
        "May palabas sa patyo.",          # palabas + patyo
        "Pumutol ka ng sanga sa kahoy.",  # sanga + kahoy
        "Maganda ang pelikula.",          # pelikula
        "Maganda ang kahoy.",             # kahoy (NOM pivot)
        "Mataas ang sanga.",              # sanga (NOM pivot)
        "Nasa patyo ang bata.",           # patyo (locative pred)
        "Maganda ang palabas.",           # palabas (NOM pivot)
        # kumusta wh-ADV sense (audit's predicational use)
        "Kumusta!",                       # bare interjection
        "Kumusta ka?",                    # wh-pred + PRON subj
        "Kumusta ang pamilya mo?",        # wh-pred + ang-NP subj
        # kumusta NOUN sense (head + linker-modifier)
        "Magandang kumusta!",
    ])
    def test_sentence_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"no parse for {sentence!r} after 8.N lex add"
        )


class TestPhase8nOutOfScope:
    """Pin the out-of-scope cases so a future construction-class
    sub-PR flipping them to parsing is a visible signal."""

    @pytest.mark.parametrize("sentence", [
        "Nagpasabi si Gina na uuwi siya.",
    ])
    def test_construction_gap_still_zero(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=1)
        # When this flips (a future construction sub-PR adds the
        # rule), update or delete this pin — the failure is a
        # success signal.
        assert len(parses) == 0, (
            f"unexpectedly parsed {sentence!r} — likely a "
            f"construction sub-PR has shipped; update this pin"
        )
