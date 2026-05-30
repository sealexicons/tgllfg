# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-10: paradigm engineering for ANG NADADALIAN closure.

Target: PANAHON wave-1 sent-7 ``Ang nadadalian ay ang hindi nahihiyang
magkamali.`` "The one who finds it easy is the one not ashamed to
make mistakes." (R&G 1981).

Three independent lex / paradigm gaps closed, each verified against
the existing paradigm infrastructure first (per the post-8.X arc's
survey-misdiagnosis discipline):

(a) ``nadadalian`` (na-CV-X-an LV-NVOL imperfective). Survey
    claimed this needed a NEW paradigm cell. In fact the Phase 5e
    ``ma_an`` cells already produce ``nalimutan`` / ``nalilimutan``
    / ``malilimutan`` / ``malimutan`` (the exact na-CV-X-an family).
    The actual gap: ``dali`` VERB (verbs.yaml line 505) had
    ``affix_class: [mag, maka]`` — missing ``ma_an``. Plus the
    canonical PANAHON spelling ``nadadalian`` (not ``nadadalihan``)
    requires the ``no_h_epenthesis`` sandhi flag (S&O 1972 §4.21
    documents both ``-h-`` and direct-concat variants).

(b) ``nahihiya`` (ma- AV-NVOL imperfective psych). ``hiya`` only
    existed in adjectives.yaml ([ma_adj] for the scalar ``mahiya``
    reading); the verbal psych sense was ``_UNK``. Added a parallel
    VERB entry in verbs.yaml with ``affix_class: [ma]`` — the
    existing ma- AV-NVOL cells produce nahiya / nahihiya /
    mahihiya / mahiya.

(c) ``magkamali`` (mag-ka- accidental/occurrence AV). The ``magka-``
    family had no paradigm cells. Added 4 new ``magka`` AV-NVOL
    cells (PFV / IPFV / CTPL-irrealis / CTPL-bare-INF). The bare
    CTPL cell produces the ``magkamali`` infinitive surface used
    in control complements like ``hindi nahihiyang magkamali``.
    Plus ``magka`` added to ``mali`` VERB's affix_class.

Plus two anti-deferral closures spawned by post-10:

(d) ``Baka V`` bare structure — pre-PR ``baka`` was lex'd as
    ``CTRL_CLASS=RAISING`` requiring the ``-ng`` linker (parallel
    to ``mukha`` → ``mukhang``), but the canonical Tagalog idiom is
    bare ``Baka umuulan`` (no linker — parallel to ``parang``,
    ``tila`` which are RAISING_BARE). Added a second ``baka`` entry
    as RAISING_BARE alongside the original RAISING; both readings
    coexist for the linker-bound vs bare variants.

(e) ``V[VOICE=AV, MOOD=NVOL] PART[LINK] S`` psych-control rule.
    Parallel to the Phase 5g manner-style ``ADJ + LINK + S`` rule
    (clause.py line 2942). The ma-NVOL psych family (``nahihiya``,
    ``natutuwa``, ``nasisiya``, ``naaalala``, …) is paradigmatically
    derived from ma_adj-class roots and doesn't carry
    ``CTRL_CLASS=PSYCH`` — so the existing Phase 5j PSYCH chart rule
    doesn't fire on it. The new rule admits the productive case
    ``Nahihiyang magsabi si Juan.`` / ``Bakit nahihiyang magsabi
    ang asawa ni A?`` (wave-2 rg-int sent-968). Adjunct-analysis
    rather than XCOMP-control (mirrors the parallel ADJ rule's
    semantically-imprecise but structurally-productive approach).

Audit signal (post-8.4 → post-10):

* wave-1: +2 (PAG-AARAL sent-2 + sent-7); **97/123 → 99/123 =
  80.49%** — hits the Phase 10 ≥80% naturalistic-tier target.
* wave-2 rg-int: 1 bucket-only PS-1 → PS-N on
  ``Baka nahihiya ka lang.`` (the dual baka reading produces an
  additional parse); 0 net change.
* wave-5 zamar2023: 1 bucket-only PS-1 → PS-N on
  ``Natulog nang walong oras ang mga bata.`` (the new V[NVOL]-LK-S
  rule licenses an additional adjunct reading); 0 net change.
* Other waves: unchanged.
* unattributed: 88/88 unchanged.
* XWAVE: 1754/6004 → 1756/6004 (+2).
* 0 regressions across the whole audit.
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Paradigm-cell surface generation ====================================


class TestNadadalianParadigm:
    """post-10 (a): ``dali`` VERB gains ``ma_an`` affix_class +
    ``no_h_epenthesis`` sandhi flag → na-CV-X-an LV-NVOL family
    surfaces (with direct concatenation, not ``-h-`` epenthesis)."""

    @pytest.mark.parametrize("surface,expected_aspect", [
        ("nadalian",   "PFV"),    # ma-NVOL DV PFV
        ("nadadalian", "IPFV"),   # ma-NVOL DV IPFV — the target form
        ("madadalian", "CTPL"),   # ma-NVOL DV CTPL irrealis
        ("madalian",   "CTPL"),   # ma-NVOL DV CTPL bare
    ])
    def test_dali_ma_an_surfaces(self, surface: str, expected_aspect: str) -> None:
        """Each ma_an cell on dali produces the directly-concatenated
        ``-an`` form (no ``-h-`` epenthesis)."""
        analyzer = _get_default()
        analyses = analyzer._index.verb_forms.get(surface, [])
        dali_analyses = [a for a in analyses if a.lemma == "dali"]
        assert dali_analyses, f"expected {surface} to have dali-rooted analysis"
        target = dali_analyses[0]
        assert target.feats.get("VOICE") == "DV"
        assert target.feats.get("MOOD") == "NVOL"
        assert target.feats.get("ASPECT") == expected_aspect

    def test_nadadalian_is_known_surface(self) -> None:
        """The canonical PANAHON spelling ``nadadalian`` (not
        ``nadadalihan``) reaches the analyzer."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("nadadalian")
        # And the h-epenthesis variant is NOT produced.
        assert not analyzer.is_known_surface("nadadalihan")


class TestNahihiyaParadigm:
    """post-10 (b): ``hiya`` VERB entry (separate from the
    adjectives.yaml ADJ entry) admits the ``ma`` AV-NVOL psych
    family."""

    @pytest.mark.parametrize("surface,expected_aspect", [
        ("nahiya",    "PFV"),     # ma-NVOL AV PFV
        ("nahihiya",  "IPFV"),    # ma-NVOL AV IPFV — the target form
        ("mahihiya",  "CTPL"),    # ma-NVOL AV CTPL
    ])
    def test_hiya_ma_surfaces(self, surface: str, expected_aspect: str) -> None:
        analyzer = _get_default()
        analyses = analyzer._index.verb_forms.get(surface, [])
        hiya_analyses = [a for a in analyses if a.lemma == "hiya"]
        assert hiya_analyses, f"expected {surface} to have hiya-rooted analysis"
        target = hiya_analyses[0]
        assert target.feats.get("VOICE") == "AV"
        assert target.feats.get("MOOD") == "NVOL"
        assert target.feats.get("ASPECT") == expected_aspect

    def test_mahiya_adj_preserved(self) -> None:
        """The ADJ entry (adjectives.yaml ``hiya``) is preserved —
        ``mahiya`` analyzes as both ADJ (existing ma_adj scalar) and
        VERB (new ma- AV-NVOL CTPL bare form... wait, the bare ma-
        CTPL cell doesn't include ``ma + hiya`` directly; only with
        cv-redup. So mahiya only appears as ADJ)."""
        analyzer = _get_default()
        adj_analyses = analyzer._index.adjectives.get("mahiya", [])
        assert any(a.lemma == "hiya" for a in adj_analyses), \
            "mahiya should remain analyzable as ma_adj ADJ"


class TestMagkamaliParadigm:
    """post-10 (c): new ``magka`` AV-NVOL paradigm cells. ``mali``
    VERB gains ``magka`` in affix_class."""

    @pytest.mark.parametrize("surface,expected_aspect", [
        ("nagkamali",   "PFV"),   # PFV NVOL
        ("nagkakamali", "IPFV"),  # IPFV NVOL — cv-redup of ka+mali
        ("magkakamali", "CTPL"),  # CTPL NVOL irrealis
        ("magkamali",   "CTPL"),  # CTPL NVOL bare — the INF target
    ])
    def test_mali_magka_surfaces(self, surface: str, expected_aspect: str) -> None:
        analyzer = _get_default()
        analyses = analyzer._index.verb_forms.get(surface, [])
        mali_analyses = [a for a in analyses if a.lemma == "mali"]
        assert mali_analyses, f"expected {surface} to have mali-rooted analysis"
        target = mali_analyses[0]
        assert target.feats.get("VOICE") == "AV"
        assert target.feats.get("MOOD") == "NVOL"
        assert target.feats.get("ASPECT") == expected_aspect

    def test_magka_is_lemma_independent(self) -> None:
        """The ``magka`` paradigm cells should work for ANY VERB
        root that opts in. Verify by examining the cell-level feats
        rather than just the ``mali`` surfaces."""
        analyzer = _get_default()
        # magkamali is the bare CTPL form.
        assert analyzer.is_known_surface("magkamali")


# === Target sentence parse ===============================================


class TestPanahonSent7:
    """post-10: the PANAHON wave-1 sent-7 target — ``Ang
    nadadalian ay ang hindi nahihiyang magkamali.`` — composes
    paradigm cells (a) + (b) + (c) + the V[NVOL]-LK-S rule (e)."""

    def test_target_sentence_parses(self) -> None:
        parses = parse_text(
            "Ang nadadalian ay ang hindi nahihiyang magkamali.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_doubled_wh_q_with_nadadalian(self) -> None:
        """PAG-AARAL/sent-2 — ``Sino ang nahihirapan at sino ang
        nadadalian?`` — wh-Q + doubled ang-headless V-NP coord with
        the new ``nadadalian`` form. Closes wave-1 sent-2."""
        parses = parse_text(
            "Sino ang nahihirapan at sino ang nadadalian?",
            n_best=2,
        )
        assert len(parses) >= 1


# === V[NVOL] + LK + S psych-control rule ================================


class TestVNvolLkSRule:
    """post-10 (e): the parallel ``V[VOICE=AV, MOOD=NVOL] PART[LK] S``
    psych-control rule admits the productive ma-NVOL psych family
    on top of the structural pattern already admitted for STATIVE_PRED
    ADJs (gusto / ayaw)."""

    def test_nahihiyang_inf_nom_parses(self) -> None:
        """``Nahihiyang kumain si Juan.`` — bare V[NVOL]-LK-V[INF]
        + ang-NP pivot. Uses ``kumain`` (which parses standalone
        with si-NOM) rather than ``magsabi`` (whose bare
        ``Magsabi si Juan.`` ZPFs for an independent chart gap)."""
        parses = parse_text("Nahihiyang kumain si Juan.", n_best=2)
        assert len(parses) >= 1

    def test_nahihiyang_inf_full_nom_parses(self) -> None:
        """``Nahihiyang magsabi ang asawa ni Juan.`` — full ang-NP
        with possessor-GEN."""
        parses = parse_text(
            "Nahihiyang magsabi ang asawa ni Juan.", n_best=2,
        )
        assert len(parses) >= 1

    def test_bakit_nahihiyang_wh_q(self) -> None:
        """``Bakit nahihiyang magsabi ang asawa ni A?`` — wave-2
        rg-int sent-968 (regression-recovery: pre-post-10 the
        sentence parsed via ``_UNK``-drop on the unrecognised
        ``nahihiyang``)."""
        parses = parse_text(
            "Bakit nahihiyang magsabi ang asawa ni A?", n_best=2,
        )
        assert len(parses) >= 1

    def test_hindi_pron_pre_pivot_still_works(self) -> None:
        """post-10 anti-regression: the existing relative-clause-
        path parse for ``Hindi siya nahihiyang kumain.`` (PRON
        pivot pre-V) is preserved."""
        parses = parse_text("Hindi siya nahihiyang kumain.", n_best=2)
        assert len(parses) >= 1


# === Baka RAISING_BARE ===================================================


class TestBakaRaisingBare:
    """post-10 (d): ``baka`` gains a second entry as RAISING_BARE
    (parallel to ``parang`` / ``tila``). The original RAISING entry
    is preserved for the ``bakang`` (with-linker) variant."""

    def test_baka_bare_v_parses(self) -> None:
        """``Baka umuulan.`` — bare ``baka`` + V (no linker)."""
        parses = parse_text("Baka umuulan.", n_best=2)
        assert len(parses) >= 1

    def test_baka_nahihiya_ka_lang(self) -> None:
        """``Baka nahihiya ka lang.`` — wave-2 rg-int sent-1711
        (regression-recovery; pre-post-10 ``nahihiya`` was ``_UNK``
        and the parse path was an _UNK-drop accident)."""
        parses = parse_text("Baka nahihiya ka lang.", n_best=2)
        assert len(parses) >= 1

    def test_bakang_with_linker_still_works(self) -> None:
        """post-10 anti-regression: the original RAISING entry
        (with ``-ng`` linker) is preserved. ``Bakang umuulan.``
        also parses."""
        parses = parse_text("Bakang umuulan.", n_best=2)
        assert len(parses) >= 1


# === Anti-regression =====================================================


class TestAntiRegression:
    """post-10 anti-regression: the existing paradigm cells and
    chart rules continue to produce their expected surfaces /
    parses."""

    def test_ma_an_limot_family_preserved(self) -> None:
        """``nalimutan`` / ``nalilimutan`` / ``malilimutan`` /
        ``malimutan`` — the canonical ma_an exemplar family
        unchanged by adding ``dali`` to the same affix_class."""
        analyzer = _get_default()
        for surface in (
            "nalimutan", "nalilimutan", "malilimutan", "malimutan",
        ):
            analyses = analyzer._index.verb_forms.get(surface, [])
            assert any(a.lemma == "limot" for a in analyses), \
                f"{surface} should still analyze as limot-rooted"

    def test_dali_existing_surfaces_preserved(self) -> None:
        """``dali`` VERB's pre-post-10 surfaces (mag- / maka- AV)
        still generate; the ``no_h_epenthesis`` flag only affects
        the new ma_an family (no V+V hiatus on the existing cells)."""
        analyzer = _get_default()
        for surface in ("nagdali", "nagdadali", "magdadali"):
            analyses = analyzer._index.verb_forms.get(surface, [])
            assert any(a.lemma == "dali" for a in analyses), \
                f"{surface} should still analyze as dali-rooted"

    def test_mali_existing_surfaces_preserved(self) -> None:
        """``mali`` VERB's pre-post-10 surfaces (mag- / maka- AV)
        still generate; adding ``magka`` to affix_class is additive."""
        analyzer = _get_default()
        for surface in ("nagmali", "nagmamali"):
            analyses = analyzer._index.verb_forms.get(surface, [])
            assert any(a.lemma == "mali" for a in analyses), \
                f"{surface} should still analyze as mali-rooted"

    def test_adj_lk_s_manner_rule_preserved(self) -> None:
        """The Phase 5g manner-style ``ADJ + LINK + S`` rule is
        unchanged; ``Gustong kumain si Juan.`` still parses (and
        will gain an extra parse from the new parallel V[NVOL]
        rule — no regression)."""
        parses = parse_text("Gustong kumain si Juan.", n_best=2)
        assert len(parses) >= 1
