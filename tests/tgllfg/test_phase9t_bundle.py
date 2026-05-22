# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.T: Wala-interjection + free-relative wh-cleft + 2-arg
AV-CAUS-INDIRECT + nang V-DUPLICATE (B3.F bundle).

Closes four Phase 8 pins across four sub-commits within this PR:

* **9.T.1 Wala-interjection** — 8.D2 documented the polysemy
  obstacle preventing ``Wala, ...`` as a discourse-particle-
  fronted topic (the existential ``wala`` EXISTENTIAL=NEG entry
  precludes the INTERJ reading). Phase 9.T.1 adds a second
  ``wala`` PART entry with ``INTERJ=true`` + ``NEGATIVE=true``
  in particles.yaml; the existing Phase 8.D2 ``S →
  PART[INTERJ=true] PUNCT[COMMA] S`` rule consumes it.

* **9.T.2 Free-relative / pseudo-cleft** — 8.Z
  ``test_pseudo_cleft_still_fails`` pin (``Ang lalaki ang
  nagluto.`` "The man is the one who cooked."). Phase 9.T.2
  closes this purely via a lex addition (``AV_ABSOL: true`` on
  ``luto`` verb root) — the headless-RC ``ang nagluto`` parses
  via the existing Phase 5e Commit 5 free-relative rule once
  ``nagluto`` admits the AV-absolutive variant (without
  requiring an explicit OBJ).

* **9.T.3 2-arg AV-CAUS-INDIRECT** — 8.H
  ``test_two_arg_av_caus_indirect`` pin (``Nagpakain siya ng
  kendi.`` — CAUSER + PATIENT, no overt CAUSEE). Phase 9.T.3
  adds a new ``_AV_CAUS_INDIRECT_2ARG`` lex profile, a matching
  ``kain`` lex entry in causative.yaml, and a 2-daughter
  S-rule in cfg/clause.py.

* **9.T.4 nang V-DUPLICATE** — 8.H ``test_nang_v_duplicate_idiom``
  pin (``Nagpapakain sila nang nagpapakain ng kendi sa kanila.``
  S&O 1972 p.410 sent-593). Phase 9.T.4 adds two S-rules:
  (a) 1-arg AV-intransitive shape (``Tumawa nang tumawa si
  Juan.``), and (b) 3-arg AV-CAUS-INDIRECT-FLAT shape matching
  the pin verbatim.

Audit-corpus lex closures pulled in for these sub-PRs:
``taongbahay`` (NOUN, "homebody, housewife"; closes ``Wala,
taong-bahay siya.`` audit hit) and ``kartero`` (NOUN, SPANISH
loan; closes ``Lumalakad nang lumalakad ang kartero.``).
``luto`` gets ``feats: {AV_ABSOL: true}`` added (closes the
pseudo-cleft pin + many headless-RC parses).
"""

import pytest


# =============================================================
# 9.T.1 — Wala-interjection
# =============================================================

class TestWalaInterjection:
    """Polysemy-split ``wala`` admits the INTERJ + comma topic-
    fronting construction without breaking the existential
    EXISTENTIAL=NEG reading."""

    @pytest.mark.parametrize("sentence", [
        # Audit hit (8.D2 docstring-noted)
        "Wala, taong-bahay siya.",
        # Simpler tests
        "Wala, kumain siya.",
        "Wala, umalis siya.",
    ])
    def test_wala_interjection_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"

    @pytest.mark.parametrize("sentence", [
        # Existential ``wala`` must still work
        "Wala siyang pera.",
        "Walang pera siya.",
        "Wala akong aklat.",
    ])
    def test_existential_wala_retained(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"existential wala regression: {sentence!r}"


# =============================================================
# 9.T.2 — Pseudo-cleft / free-relative
# =============================================================

class TestPseudoCleftFreeRel:
    """Headless-RC ``ang nagluto`` parses as NP[CASE=NOM] via
    the existing Phase 5e Commit 5 free-relative rule once the
    inner V can parse without explicit OBJ. The fix is purely
    lex: ``AV_ABSOL: true`` on ``luto`` (and any other AV-TR
    verb that admits the absolutive use)."""

    @pytest.mark.parametrize("sentence", [
        # 8.Z pin (substituted lex'd form)
        "Ang lalaki ang nagluto.",
        # Audit-attested variants
        "Si Maria ang nagluto.",
        # Free-rel as SUBJ of matrix V
        "Kumain ang nagluto.",
        # OBJ position
        "Nakita ko ang nagluto.",
        # NEG'd pseudo-cleft
        "Hindi si Maria ang kumain.",
    ])
    def test_pseudo_cleft_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"

    def test_av_absol_on_luto(self) -> None:
        """``Nagluto siya.`` (intransitive use of TR-classed
        ``luto``) parses post-9.T.2 — the AV_ABSOL flag emits
        both TR ``<SUBJ, OBJ>`` and INTR ``<SUBJ>`` entries."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Nagluto siya.", n_best=2)
        assert len(parses) >= 1


# =============================================================
# 9.T.3 — 2-arg AV-CAUS-INDIRECT
# =============================================================

class TestTwoArgAvCausIndirect:
    """``Nagpakain siya ng kendi.`` — CAUSER + PATIENT only.
    The CAUSEE is implicit/recoverable but not syntactically
    realized; PRED template drops the OBL-CAUSEE slot."""

    @pytest.mark.parametrize("sentence", [
        "Nagpakain siya ng kendi.",
    ])
    def test_two_arg_caus_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        # The CAUSE-EAT PRED with 2 args (SUBJ + OBJ)
        preds = {str(f.feats.get("PRED", "?")) for _ct, f, *_ in parses}
        assert "CAUSE-EAT <SUBJ, OBJ>" in preds, (
            f"expected CAUSE-EAT <SUBJ, OBJ>; got preds = {preds!r}"
        )

    def test_three_arg_caus_retained(self) -> None:
        """The 8.H flat 3-arg AV-CAUS-INDIRECT remains."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpakain siya ng kendi sa kanila.", n_best=3,
        )
        assert len(parses) >= 1


# =============================================================
# 9.T.4 — nang V-DUPLICATE intensifier
# =============================================================

class TestNangVDuplicate:
    """Two S-rules cover the audit-attested shapes."""

    @pytest.mark.parametrize("sentence", [
        # 1-arg AV-intransitive
        "Tumawa nang tumawa si Juan.",
        "Tumakbo nang tumakbo si Maria.",
        "Kumain nang kumain si Pedro.",
        # IPFV variant
        "Lumalakad nang lumalakad ang kartero.",
        "Lumalakad nang lumalakad si Juan.",
    ])
    def test_av_intr_v_dup(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"
        # At least one parse should have the INTENSIFIER marker
        intens = {f.feats.get("INTENSIFIER") for _ct, f, *_ in parses}
        assert True in intens, (
            f"no parse carries INTENSIFIER=true for {sentence!r}; "
            f"got {intens!r}"
        )

    def test_av_caus_indirect_flat_v_dup(self) -> None:
        """8.H pin verbatim — 3-arg AV-CAUS-INDIRECT-FLAT
        with V-DUP."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpapakain sila nang nagpapakain ng kendi sa kanila.",
            n_best=3,
        )
        assert len(parses) >= 1


# =============================================================
# Regression guards
# =============================================================

class TestNangNotVDupRegressions:
    """The existing TEMP_SINCE / TEMP_WHEN ``nang`` subordinator
    rules still fire on their canonical shapes (those take an
    S complement, not a V duplicate — the daughter-3 V shape is
    mutually exclusive with the inner-S shape, no double-firing
    or shadowing)."""

    @pytest.mark.parametrize("sentence", [
        # TEMP_WHEN — V[PFV] + nang + V[PFV] (different lemmas — V-DUP gate
        # rejects same-lemma; this is the alternative reading)
        "Tumawa nang umalis si Juan.",
    ])
    def test_nang_temporal_retained(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"nang-TEMP regression: {sentence!r}"


class TestBaselineRegressions:
    """Existing parses unaffected."""

    @pytest.mark.parametrize("sentence", [
        "Bumili si Maria ng aklat.",
        "Kumain ang bata.",
        "Magandang aklat ito.",
        "Iyon ang aklat.",
        # 9.O / 9.Q / 9.R / 9.S baselines
        "Nakita ko ang aklat.",
        "Sa bahay ang lapis.",
        "Ni si Juan ay hindi kumain.",
        "Ni si Juan ni si Maria ay hindi kumain.",
    ])
    def test_baseline_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"baseline regression: {sentence!r}"


# =============================================================
# 9.T lex closures (taongbahay, kartero, luto AV_ABSOL)
# =============================================================

class TestLexClosures:
    """Lex/paradigm additions pulled in to close 9.T audit hits
    per user no-deferrals directive."""

    def test_taongbahay_indexed(self) -> None:
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        # Compound form recognized (via merge_hyphen_compounds
        # joining ``taong`` + ``-`` + ``bahay`` to ``taongbahay``).
        # The bare form ``taongbahay`` is the canonical citation;
        # ``taong-bahay`` is the orthographic variant.
        assert a.is_known_surface("taongbahay")

    def test_kartero_indexed(self) -> None:
        from tgllfg.morph.analyzer import _get_default
        a = _get_default()
        assert a.is_known_surface("kartero")

    def test_luto_av_absol_emits_intr(self) -> None:
        """The 9.T.2 ``AV_ABSOL: true`` on ``luto`` makes the synth
        path emit both TR ``<SUBJ, OBJ>`` and INTR ``<SUBJ>``
        entries for AV voice. ``Nagluto siya.`` parses via the
        INTR variant."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Nagluto siya.", n_best=2)
        assert len(parses) >= 1


# =============================================================
# Out-of-scope deferrals
# =============================================================

class TestPhase9tOutOfScope:
    """Audit-attested variants NOT closed by 9.T."""

    def test_bare_n_v_duplicate(self) -> None:
        """``Lakad nang lakad ang kartero.`` — bare-N V-DUP
        variant (the lex root surfaces without verb morphology).
        Requires bare-N → V coercion machinery not in 9.T
        scope. Pin; flip if a follow-on adds the coercion."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Lakad nang lakad ang kartero.", n_best=2,
        )
        assert len(parses) == 0, (
            "bare-N V-DUP may have closed; review and flip."
        )

    def test_biclausal_av_caus_indirect_baseline(self) -> None:
        """``Nagpakain ako kumain ng kanin sa kanila.`` — the
        biclausal AV-CAUS-INDIRECT shape with overt embedded V.
        Pre-existing gap (failed pre-9.T as well). Not in 9.T
        scope; defer."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagpakain ako kumain ng kanin sa kanila.", n_best=2,
        )
        assert len(parses) == 0
