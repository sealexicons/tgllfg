# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.2: ``dahilan sa`` REASON-PP head fronting +
clause-final + post-half closures.

Adds:

1. ``dahilan`` PREP entry in particles.yaml with ``PREP_TYPE=REASON``
   — the nominal-form variant of ``dahil`` (Phase 5e Commit 3 PREP).
   Both heads now route through the same chart and pipeline paths:

   - chart's ``PP → PREP NP[CASE=DAT]`` (extraction.py)
   - chart's ``S → PP[PREP_TYPE=REASON] PUNCT[COMMA] S`` (discourse.py)
   - chart's ``S → S PP[PREP_TYPE=REASON]`` (NEW post-7.2 lift below)
   - pipeline's fronted-PP-comma split (``_REASON_PREP_LEMMAS``
     extended to include ``dahilan`` in pipeline.py)

2. Clause-final ``S → S PP[PREP_TYPE=REASON]`` rule added to the
   discourse.py post-V-PP loop (which previously covered only
   BENEFICIARY / TOPIC / GOAL — the c12 deferral on REASON is
   lifted post-7.2; see the loop's updated comment).

3. ``S → V[VOICE=AV] AdvP NP[CASE=NOM]`` chart rule for V-ADV-NOM
   ordering (Tagalog admits ADV between V and SUBJ; previously the
   chart had ``V NOM`` and the post-wrap ``S → S AdvP`` covered
   V-NOM-ADV, but the medial position was missing). Gated to
   ``ADV_TYPE=TIME`` to match the existing post-wrap discipline.

4. Lex extensions for the inner-clause vocabulary in the post-7.2
   constructed exemplars:

   - ``hirap`` VERB gains ``mag`` affix_class + ``AV_ABSOL: true``
     so ``Naghirap ang pamilya.`` (suffer reading) parses without
     an explicit OBJ.
   - ``pagkawala`` NOUN (``pagka-`` nominalization of ``wala``) for
     the inner-NP ``pagkawala niya ng trabaho`` "his job loss".
   - ``pagod`` NOUN (state-nominal use, polysemous with the existing
     ADJ + VERB) for ``Sa pagod.`` "from exhaustion".

Closes all 4 ``pending_closure: post-7.2`` constructed exemplars
(``dahilan-sa/ulan``, ``dahilan-sa/pagkawala-trabaho``,
``dahilan-sa/pagod``, ``dahilan-sa/ulan-postv``) plus the parallel
``dahil sa`` clause-final case that was previously a chart-coverage
gap (the c12 deferral surfaced on no audit-corpus pressure but
became reachable when post-7.2 added the canonical dahilan exemplars).
"""

from tgllfg.core.pipeline import parse_text


class TestDahilanSaPp:
    """post-7.2: ``dahilan`` PREP variant of ``dahil`` (PREP_TYPE=REASON)."""

    def test_dahilan_sa_ulan_fronted(self) -> None:
        """Smallest fronted-PP-comma exemplar."""
        s = "Dahilan sa ulan, hindi kami nakapasok sa eskwela."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # Fronted PP is TOPIC + member of ADJ set
        topic = fs.feats.get("TOPIC")
        assert topic is not None, "expected TOPIC on matrix"
        assert topic.feats.get("PREP_TYPE") == "REASON", (
            f"expected PREP_TYPE=REASON on TOPIC, got "
            f"{topic.feats.get('PREP_TYPE')}"
        )

    def test_dahilan_sa_pagod_fronted(self) -> None:
        """Fronted ``dahilan sa pagod`` + V-ADV-NOM post-half. Both
        the dahilan lex add and the V-ADV-NOM chart rule are needed
        to close this exemplar."""
        s = "Dahilan sa pagod, natulog kaagad si Maria."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1

    def test_dahilan_sa_pagkawala_fronted(self) -> None:
        """Fronted PP with embedded GEN-PRON + GEN-OBJ in the
        PP-internal NP (``pagkawala niya ng trabaho``); post-half
        uses the ``naghirap`` mag-AV-INTR form (new affix-class
        addition + AV_ABSOL)."""
        s = ("Dahilan sa pagkawala niya ng trabaho, "
             "naghirap ang pamilya.")
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1

    def test_dahilan_sa_ulan_postv(self) -> None:
        """Clause-final REASON PP (NEW: REASON added to discourse.py's
        ``S → S PP`` loop, lifting the Phase 9.X.c12 deferral)."""
        s = "Hindi kami nakapasok sa eskwela dahilan sa ulan."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # Clause-final PP joins matrix ADJUNCT
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None and len(adj) >= 1


class TestDahilSaClauseFinal:
    """post-7.2 also lifts the c12 deferral on REASON for the
    pre-existing ``dahil`` PREP — both surface forms now close
    clause-finally."""

    def test_dahil_sa_ulan_postv(self) -> None:
        """The ``dahil`` parallel that was previously a chart-
        coverage gap (the c12 loop omitted REASON pending audit
        justification — post-7.2 lifts it)."""
        s = "Hindi kami nakapasok sa eskwela dahil sa ulan."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1


class TestVAdvNomOrder:
    """post-7.2: ``S → V[VOICE=AV] AdvP NP[CASE=NOM]`` chart rule
    closes the V-ADV-SUBJ ordering, parallel to the existing
    ``V SUBJ`` rule (line 50) and the ``S → S AdvP`` post-wrap.

    Gated to ``ADV_TYPE=TIME`` (mirrors the post-wrap gate) so MANNER
    / LOCATION / SPATIAL AdvPs (deferred for placement elsewhere)
    don't over-fire here.
    """

    def test_v_adv_nom_intr(self) -> None:
        """``Natulog kaagad si Maria.`` — AV-INTR + time-frame ADV +
        NOM-SUBJ."""
        parses = parse_text("Natulog kaagad si Maria.", n_best=2)
        assert len(parses) >= 1

    def test_v_adv_nom_av_absol(self) -> None:
        """``Sumulat dati si Pedro.`` — AV-TR with AV_ABSOL (sulat is
        intransitive in the relevant sub-paradigm)."""
        parses = parse_text("Sumulat dati si Pedro.", n_best=2)
        assert len(parses) >= 1

    def test_v_nom_adv_unchanged(self) -> None:
        """Anti-regression: the V-NOM-ADV order still parses via the
        existing post-wrap ``S → S AdvP``."""
        parses = parse_text("Natulog si Maria kaagad.", n_best=2)
        assert len(parses) >= 1

    def test_v_nom_only_unchanged(self) -> None:
        """Anti-regression: bare V-NOM still parses via line-50."""
        parses = parse_text("Natulog si Maria.", n_best=2)
        assert len(parses) >= 1


class TestLexExtensions:
    """post-7.2 lex additions stand alone, verifying the morph + chart
    interactions are clean."""

    def test_naghirap_pamilya_av_absol(self) -> None:
        """``Naghirap ang pamilya.`` — the new mag affix-class +
        AV_ABSOL on ``hirap`` together license the bare AV-TR + NOM
        composition (no GEN-OBJ required for the suffer reading)."""
        parses = parse_text("Naghirap ang pamilya.", n_best=2)
        assert len(parses) >= 1

    def test_pagkawala_inner_np(self) -> None:
        """``Sa pagkawala niya ng trabaho`` — pagkawala NOUN with
        GEN-PRON possessor + GEN-N theme — parses inside the post-7
        fronted-PP-comma split."""
        s = ("Dahil sa pagkawala niya ng trabaho, "
             "naghirap ang pamilya.")
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1

    def test_pagod_state_nominal(self) -> None:
        """``pagod`` NOUN (state-nominal) is polysemous with the
        existing ADJ + VERB — anti-regression for the ADJ + VERB
        readings."""
        # ADJ predicate (existing)
        parses = parse_text("Pagod si Maria.", n_best=2)
        assert len(parses) >= 1, "pagod ADJ predicate regressed"
        # VERB (existing INTR with ma class — napagod)
        parses = parse_text("Napagod si Maria.", n_best=2)
        assert len(parses) >= 1, "pagod VERB napagod regressed"
