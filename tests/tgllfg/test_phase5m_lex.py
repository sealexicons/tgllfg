"""Phase 5m Commit 1: discourse / register / indefinite lex inventory.

Roadmap §12.1 / plan-of-record §4.1-4.4. Twenty-five new lex
entries across particles.yaml, pronouns.yaml, and nouns.yaml:

* **Politeness 2P clitics** (``po`` / ``ho``): PART with
  ``REGISTER=POLITE`` / ``COLLOQUIAL_POLITE``, ``is_clitic: true``,
  ``clitic_class: 2P``. Composes via the existing Phase 5i
  Rule A (generic 2P absorption); REGISTER lifts to the matrix S.
* **Modal / mood particles** (``siguro`` / ``marahil``): PART with
  ``EPISTEMIC=PROBABLY``, ``DISCOURSE_POS=SENTENCE_INITIAL``.
  Composes via the new Phase 5m Commit 4 sentence-initial PART
  rule.
* **Single-word discourse connectives** (``samakatuwid`` /
  ``gayunpaman``): same shape as modal particles, with
  ``DISCOURSE=THEREFORE`` / ``HOWEVER``.
* **Multi-word discourse connective heads** (``gayon`` / ``ganon``
  / ``bukod``): LEMMA-only PARTs that feed the Phase 5m Commit 11
  multi-word rules. The existing ``din`` 2P clitic and the
  existing ``dito`` ADP[DEM] are the second daughters.
* **Emphatic post-N particle** (``mismo``): PART with
  ``EMPHATIC=YES``. Composes via the new Phase 5m Commit 7
  ``NP → NP PART[mismo]`` rule.
* **Frequency adverbs** (``madalas`` / ``palagi`` / ``lagi`` /
  ``minsan`` / ``paminsan-minsan``): ADV with
  ``ADV_TYPE=FREQUENCY``, new ``FREQ_VALUE`` (HIGH / HABITUAL /
  SOMETIMES / OCCASIONAL). Routes through the existing Phase 5f
  Commit 5 sentential-FREQ rule.
* **Negative-indefinite PRON** (``sinuman``): PRON with
  ``INDEF=NEG_INDEF``. Composes via the existing Phase 5j
  ``walang NP`` existential negation grammar.
* **Answer interjections** (``opo`` / ``oho``): PRON with
  ``INTERJ=YES``, ``ANSWER=AFFIRM``. Stand-alone clause answers
  via the existing fragment-answer mechanism.
* **Reflexive NOUN** (``sarili``): NOUN with
  ``SEM_CLASS=REFLEXIVE``. Composes via the existing NP grammar
  (``ang sarili niya`` = D + N + GEN-PRON); anaphora resolution
  is Phase 6.

This commit is lex-only — no grammar / analyzer code changes. The
Phase 5m grammar rules (Commits 2-11) constrain on ``REGISTER``,
``EPISTEMIC``, ``DISCOURSE``, ``EMPHATIC``, ``ADV_TYPE``,
``INDEF``, ``INTERJ`` to fire on these surfaces. Pre-state
(verified 2026-05-07): all 25 surfaces were ``_UNK`` or had only
unrelated readings (``minsan`` was referenced in a comment but
not lex'd; ``dito`` exists as ADP[DEM] only — preserved). Phase
5l ``kahit`` (PART[COMP_TYPE=CONC]) is preserved and reused by
Phase 5m Commit 8 indefinite-builder rules.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === (a) Politeness 2P clitics =========================================


POLITENESS_CLITICS = [
    # (surface, register, lemma)
    ("po", "POLITE", "po"),
    ("ho", "COLLOQUIAL_POLITE", "ho"),
]


class TestPolitenessClitics:
    """``po`` and ``ho`` are 2P clitics with ``REGISTER`` lift."""

    @pytest.mark.parametrize("surface,register,lemma", POLITENESS_CLITICS)
    def test_indexed_as_2p_politeness_clitic(
        self, surface: str, register: str, lemma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        clitics = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("REGISTER") == register
            and a.feats.get("LEMMA") == lemma
        ]
        assert len(clitics) == 1, (
            f"expected exactly one PART[REGISTER={register}, "
            f"LEMMA={lemma}] for {surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
        assert clitics[0].feats.get("is_clitic") is True
        assert clitics[0].feats.get("CLITIC_CLASS") == "2P"


# === (b) Modal / mood particles ========================================


MODAL_PARTICLES = [
    # (surface, lemma, register_or_none)
    ("siguro", "siguro", None),
    ("marahil", "marahil", "FORMAL"),
]


class TestModalParticles:
    """``siguro`` and ``marahil`` are epistemic particles with
    ``EPISTEMIC=PROBABLY``. Phase 5n.B Commit 18 (§18 L98) added
    polysemous CLITIC_CLASS=2P entries to admit clause-medial
    usage; the original DISCOURSE_POS=SENTENCE_INITIAL entries
    remain. Both readings must surface in the analyzer output."""

    @pytest.mark.parametrize("surface,lemma,register", MODAL_PARTICLES)
    def test_indexed_as_modal_particle(
        self, surface: str, lemma: str, register: str | None,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        modals = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("EPISTEMIC") == "PROBABLY"
            and a.feats.get("LEMMA") == lemma
        ]
        assert len(modals) == 2, (
            f"expected exactly two PART[EPISTEMIC=PROBABLY, "
            f"LEMMA={lemma}] entries (sentence-initial + 2P-clitic) "
            f"for {surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
        # Sentence-initial entry: DISCOURSE_POS=SENTENCE_INITIAL,
        # not is_clitic.
        sent_initial = [
            a for a in modals
            if a.feats.get("DISCOURSE_POS") == "SENTENCE_INITIAL"
        ]
        assert len(sent_initial) == 1
        if register is not None:
            assert sent_initial[0].feats.get("REGISTER") == register
        # 2P-clitic entry: is_clitic=True, CLITIC_CLASS='2P'.
        clitic = [a for a in modals if a.feats.get("is_clitic") is True]
        assert len(clitic) == 1
        assert clitic[0].feats.get("CLITIC_CLASS") == "2P"


# === (c) Single-word discourse connectives =============================


DISCOURSE_CONNECTIVES = [
    # (surface, discourse, lemma)
    ("samakatuwid", "THEREFORE", "samakatuwid"),
    ("gayunpaman", "HOWEVER", "gayunpaman"),
]


class TestDiscourseConnectives:
    """``samakatuwid`` and ``gayunpaman`` are sentence-initial
    discourse connectives with ``DISCOURSE`` feat."""

    @pytest.mark.parametrize("surface,discourse,lemma", DISCOURSE_CONNECTIVES)
    def test_indexed_as_discourse_connective(
        self, surface: str, discourse: str, lemma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        connectives = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("DISCOURSE") == discourse
            and a.feats.get("LEMMA") == lemma
        ]
        assert len(connectives) == 1, (
            f"expected exactly one PART[DISCOURSE={discourse}, "
            f"LEMMA={lemma}] for {surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
        assert connectives[0].feats.get("DISCOURSE_POS") == "SENTENCE_INITIAL"


# === (d) Multi-word discourse connective heads =========================


DISCOURSE_HEADS = ["gayon", "ganon", "bukod"]


class TestDiscourseHeads:
    """LEMMA-only PARTs that feed the Phase 5m Commit 11 multi-word
    rules. They have no DISCOURSE / DISCOURSE_POS feat at the lex
    level — the multi-word rule supplies those on the virtual
    composed PART."""

    @pytest.mark.parametrize("surface", DISCOURSE_HEADS)
    def test_indexed_as_lemma_only_part(self, surface: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        heads = [
            a for a in out
            if a.pos == "PART" and a.feats.get("LEMMA") == surface
        ]
        assert len(heads) >= 1, (
            f"expected at least one PART[LEMMA={surface}] for "
            f"{surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


# === (e) Emphatic mismo ================================================


class TestEmphaticMismo:
    """``mismo`` is a post-N particle with ``EMPHATIC=YES``."""

    def test_mismo_indexed_as_emphatic_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("mismo"))
        emphatics = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("EMPHATIC") is True
            and a.feats.get("LEMMA") == "mismo"
        ]
        assert len(emphatics) == 1, (
            f"expected exactly one PART[EMPHATIC=YES, LEMMA=mismo]; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


# === (f) Frequency adverbs =============================================


FREQUENCY_ADVERBS = [
    # (surface, freq_value, lemma)
    # Note: the analyzer-internal form for the reduplicated
    # ``paminsan-minsan`` is the joined form ``paminsanminsan``
    # — the parse-pipeline merger collapses ``X-Y`` to ``XY``
    # before lookup (Phase 5f Commit 14 precedent for ``tag-init``
    # / ``taginit``). LEMMA preserves the user-visible
    # hyphenated form.
    ("madalas",          "HIGH",       "madalas"),
    ("palagi",           "HABITUAL",   "palagi"),
    ("lagi",             "HABITUAL",   "lagi"),
    ("minsan",           "SOMETIMES",  "minsan"),
    ("paminsanminsan",   "OCCASIONAL", "paminsan-minsan"),
]


class TestFrequencyAdverbs:
    """Five new ADV[ADV_TYPE=FREQUENCY] entries. The existing Phase
    5f Commit 5 sentential-FREQ rule (``S → S AdvP[FREQUENCY]``)
    auto-routes them as clause-final adjuncts."""

    @pytest.mark.parametrize("surface,freq_value,lemma", FREQUENCY_ADVERBS)
    def test_indexed_as_frequency_adv(
        self, surface: str, freq_value: str, lemma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        adverbs = [
            a for a in out
            if a.pos == "ADV"
            and a.feats.get("ADV_TYPE") == "FREQUENCY"
            and a.feats.get("FREQ_VALUE") == freq_value
            and a.feats.get("LEMMA") == lemma
        ]
        assert len(adverbs) == 1, (
            f"expected exactly one ADV[ADV_TYPE=FREQUENCY, "
            f"FREQ_VALUE={freq_value}, LEMMA={lemma}] for "
            f"{surface!r}; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


# === (g) Negative-indefinite PRON ======================================


class TestNegativeIndefinitePronoun:
    """``sinuman`` "anyone / no one" is the negative-indefinite
    PRON used in ``walang sinuman`` constructions."""

    def test_sinuman_indexed_as_neg_indef_pron(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sinuman"))
        prons = [
            a for a in out
            if a.feats.get("INDEF") == "NEG_INDEF"
            and a.feats.get("LEMMA") == "sinuman"
        ]
        assert len(prons) == 1, (
            f"expected exactly one PRON[INDEF=NEG_INDEF, "
            f"LEMMA=sinuman]; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


# === (h) Answer interjections ==========================================


ANSWER_INTERJECTIONS = [
    # (surface, register, lemma)
    ("opo", "POLITE", "opo"),
    ("oho", "COLLOQUIAL_POLITE", "oho"),
]


class TestAnswerInterjections:
    """``opo`` (= ``oo`` + ``po``) and ``oho`` (= ``oo`` + ``ho``)
    are fused affirmative-answer PRONs with ``INTERJ=YES``."""

    @pytest.mark.parametrize("surface,register,lemma", ANSWER_INTERJECTIONS)
    def test_indexed_as_answer_interj(
        self, surface: str, register: str, lemma: str,
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        interjs = [
            a for a in out
            if a.feats.get("INTERJ") is True
            and a.feats.get("ANSWER") == "AFFIRM"
            and a.feats.get("REGISTER") == register
            and a.feats.get("LEMMA") == lemma
        ]
        assert len(interjs) == 1, (
            f"expected exactly one PRON[INTERJ=YES, ANSWER=AFFIRM, "
            f"REGISTER={register}, LEMMA={lemma}] for {surface!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


# === (i) Reflexive NOUN ================================================


class TestReflexiveSarili:
    """``sarili`` is a NOUN (not PRON) with
    ``SEM_CLASS=REFLEXIVE``. Distribution: ``ang sarili niya`` =
    D + N + GEN-PRON via existing NP grammar."""

    def test_sarili_indexed_as_reflexive_noun(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sarili"))
        nouns = [
            a for a in out
            if a.pos == "NOUN"
            and a.feats.get("SEM_CLASS") == "REFLEXIVE"
        ]
        assert len(nouns) == 1, (
            f"expected exactly one N[SEM_CLASS=REFLEXIVE] for "
            f"sarili; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


# === Polysemy / preservation checks ====================================


class TestKahitPolysemyPreserved:
    """Phase 5l ``kahit`` (PART[COMP_TYPE=CONC]) is preserved
    after Phase 5m. The Phase 5m Commit 8 indefinite-builder rule
    constrains on ``LEMMA=kahit`` and the daughter category to
    distinguish ``kahit S`` (CONC, 5l) from ``kahit + wh-PRON``
    (INDEF, 5m)."""

    def test_kahit_carries_conc_comp_type(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kahit"))
        conc = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("COMP_TYPE") == "CONC"
            and a.feats.get("LEMMA") == "kahit"
        ]
        assert len(conc) == 1


class TestDitoPreserved:
    """Existing ``dito`` ADP[CASE=DAT, DEIXIS=PROX, DEM=YES] entry
    is preserved. Phase 5m does NOT add a PART entry for
    ``dito`` — the multi-word ``bukod dito`` rule consumes the
    existing ADP entry directly (mixed-POS daughters)."""

    def test_dito_remains_adp_dem(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("dito"))
        adps = [
            a for a in out
            if a.pos == "ADP"
            and a.feats.get("DEM") is True
            and a.feats.get("DEIXIS") == "PROX"
            and a.feats.get("CASE") == "DAT"
        ]
        assert len(adps) == 1, (
            f"expected exactly one ADP[CASE=DAT, DEIXIS=PROX, "
            f"DEM=YES] for dito; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


class TestDinPreserved:
    """Existing ``din`` 2P clitic (PART[ADV=ALSO]) is preserved.
    The Phase 5m Commit 11 multi-word ``gayon din`` rule
    constrains on ``(↓2 LEMMA) =c 'din'`` and re-emits a virtual
    PART[DISCOURSE=LIKEWISE, DISCOURSE_POS=SENTENCE_INITIAL]; the
    underlying ``din`` clitic is unchanged."""

    def test_din_remains_2p_clitic(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("din"))
        clitics = [
            a for a in out
            if a.pos == "PART"
            and a.feats.get("ADV") == "ALSO"
        ]
        assert len(clitics) == 1
        assert clitics[0].feats.get("is_clitic") is True


# === Smoke tests: no surface still _UNK ================================


PHASE_5M_SURFACES = [
    "po", "ho", "opo", "oho",
    "siguro", "marahil",
    "samakatuwid", "gayunpaman",
    "gayon", "ganon", "bukod",
    "mismo",
    "madalas", "palagi", "lagi", "minsan", "paminsanminsan",
    "sinuman", "sarili",
]


class TestNoUnknown:
    """Every Phase 5m surface produces at least one non-``_UNK``
    analysis. The ``_strip_non_content`` pre-pass would silently
    drop ``_UNK`` analyses and produce bogus parses for sentences
    using these surfaces; this test catches the lex-loading
    regression directly."""

    @pytest.mark.parametrize("surface", PHASE_5M_SURFACES)
    def test_surface_is_lexed(self, surface: str) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        non_unk = [a for a in out if a.pos != "_UNK"]
        assert non_unk, (
            f"surface {surface!r} produced only _UNK analyses; got "
            f"{[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )
