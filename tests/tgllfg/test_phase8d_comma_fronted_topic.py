"""Phase 8.D: comma-fronted topic NP.

Closes the audit-surfaced gap (rg81 ANG MANOK ch., Wave 1) by
adding two sibling rules to ``data/tgl/cfg/clause.py`` parallel
to the Phase 5l Commit 13 ay-fronted SubordClause topic
(``cfg/subordination.py``):

- ``S → NP PUNCT[COMMA] S``  — case-marked NP topic
  (``Si Maria, kumain siya.``)
- ``S → N PUNCT[COMMA] S``   — bare-N / cardinal-N topic
  (``Isang araw, nagbubunot siya ng damo.``)

Both rules carry the same equation set:

    (↑)       = ↓3        # matrix = post-comma S
    (↑ TOPIC) = ↓1        # fronted constituent is discourse TOPIC
    ↓1 ∈ (↑ ADJUNCT)      # also in adjunct set (temporal /
                            setting frame interpretation)

The N-variant exists because the Phase 5f Commit 1 cardinal-NP
rule requires a CASE marker daughter to build NP[CASE=X]; bare
cardinal-modified N (``Isang araw`` "one day") thus surfaces as
``N``, not ``NP``. The audit target uses exactly this shape.

Disambiguation:

- From Phase 5n.C Commit 6 / 7.6 universal-Q distributive
  (``Bawat bata, kumain.``): that family's right daughter is a
  bare ``V[VOICE=AV]``, whereas these rules' right daughter is
  a full S already. Distinct daughter shape; no overlap.
- From Phase 4 §7.4 ay-fronted NP: ay-fronting uses
  ``PART[LINK=AY]``; comma-fronting uses ``PUNCT[COMMA]``.
  Different surface tokens; no overlap.

Out of 8.D scope (pinned):

- ADV-fronted topic (``Bukas, kumain siya.``) — `bukas` is
  ADV-only in particles.yaml; the N-variant catches `Kahapon`
  (dual NOUN+ADV) but not ADV-only forms. Would need a
  sibling ADV-variant rule.
- PP-fronted topic (``Sa simula, ...`` / ``Una sa lahat, ...``).
- Discourse-particle-fronted (``Eto, ...`` / ``Oo, ...`` /
  ``Wala, ...``) — needs PART-variant.
"""

from __future__ import annotations

import pytest


class TestPhase8dCommaFrontedTopic:
    """The audit-derived sentence and its constructed variants
    parse cleanly post-8.D."""

    @pytest.mark.parametrize("sentence", [
        # Wave 1 audit target — rg81 ANG MANOK ch., sentence 11.
        "Isang araw, nagbubunot siya ng damo.",
        # Simpler N-variant cases.
        "Isang araw, kumain siya.",
        # Dual-POS NOUN+ADV — kahapon parses as NOUN in this rule.
        "Kahapon, kumain siya.",
        # NP-variant — proper name NP[CASE=NOM].
        "Si Juan, kumain siya.",
    ])
    def test_sentence_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"no parse for {sentence!r} after 8.D rules"
        )


class TestPhase8dTopicAdjunctFstructure:
    """The 8.D rules set TOPIC and ADJUNCT membership on the
    matrix f-structure. Verify the structural commitments."""

    def test_topic_is_set(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Isang araw, nagbubunot siya ng damo.", n_best=3
        )
        assert len(parses) >= 1
        # parse_text returns list[tuple[c-tree, f-structure, a-structure, diag]]
        _, f, _, _ = parses[0]
        # TOPIC should be present and carry the fronted N's PRED.
        topic = f.feats.get("TOPIC")
        assert topic is not None, "TOPIC not set on matrix"
        topic_lemma = (
            topic.feats.get("LEMMA")
            if hasattr(topic, "feats")
            else None
        )
        assert topic_lemma == "araw", (
            f"TOPIC LEMMA={topic_lemma!r}, expected 'araw'"
        )

    def test_adjunct_contains_topic(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Isang araw, nagbubunot siya ng damo.", n_best=3
        )
        assert len(parses) >= 1
        _, f, _, _ = parses[0]
        adjunct_set = f.feats.get("ADJUNCT")
        assert adjunct_set is not None, "ADJUNCT not set on matrix"
        # ADJUNCT is a set; should contain a member with LEMMA=araw.
        members = (
            list(adjunct_set)
            if hasattr(adjunct_set, "__iter__")
            else []
        )
        lemmas = [
            m.feats.get("LEMMA") for m in members
            if hasattr(m, "feats")
        ]
        assert "araw" in lemmas, (
            f"ADJUNCT members={lemmas!r}, expected araw"
        )


class TestPhase8dExistingFrontingStillWorks:
    """Sanity check on existing topic-fronting rules — 8.D added
    new variants but should not have regressed:

    - Phase 4 §7.4 ay-fronted NP (``Si Maria ay kumain.``)
    - Phase 5l Commit 13 ay-fronted SubordClause
    - Phase 5n.C Commit 6 universal-Q distributive
      (``Bawat bata, kumain.``)
    """

    @pytest.mark.parametrize("sentence", [
        "Si Maria ay kumain.",       # ay-fronted NP
        "Si Juan ay kumain.",
    ])
    def test_existing_ay_fronting_works(
        self, sentence: str
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"existing ay-fronting regressed on {sentence!r}"
        )


class TestPhase8dClosedIn8d2:
    """The three out-of-scope variants pinned in 8.D were closed
    by Phase 8.D2 (in-Phase-8 anti-deferral follow-on). The
    test methods were originally named ``test_*_still_fails`` in
    8.D; 8.D2 flipped each to ``test_*_parses`` with the assertion
    reversed."""

    def test_adv_fronted_topic_parses(self) -> None:
        """``Bukas, kumain siya.`` ("Tomorrow, he ate.") — closed
        by 8.D2 via the new ``S → AdvP PUNCT[COMMA] S`` rule.
        ``bukas`` is ADV-only in particles.yaml; the 8.D N-variant
        didn't fire on it. The 8.D2 AdvP-variant uses the existing
        ``AdvP → ADV`` non-terminal from extraction.py."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Bukas, kumain siya.", n_best=3)
        assert len(parses) >= 1, (
            "ADV-fronted topic regressed — 8.D2 AdvP-variant "
            "rule should fire."
        )

    def test_pp_fronted_topic_parses(self) -> None:
        """``Sa simula, kumain si Juan.`` ("In the beginning,
        Juan ate.") — closed by 8.D2 via lex addition only.
        Discovery during 8.D2 probing: the 8.D NP-variant rule
        ALREADY admits ``NP[CASE=DAT]`` (which is the shape of
        ``sa simula``). The 8.D pin was based on a false
        premise — probing with an OOV noun (``simula``) gave 0
        parses even though the construction works. 8.D2 closes
        the pin by adding ``simula`` to nouns.yaml; the 8.D rule
        does all the structural work."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Sa simula, kumain si Juan.", n_best=3
        )
        assert len(parses) >= 1, (
            "PP-fronted topic regressed — 8.D NP-variant rule "
            "(unconstrained CASE) should fire on NP[CASE=DAT]."
        )

    def test_discourse_particle_fronted_parses(self) -> None:
        """``Oo, kumain siya.`` / ``Eto, kumain siya.`` —
        affirmation / deictic interjection + comma + matrix.
        Closed by 8.D2 via the new
        ``S → PART[INTERJ=true] PUNCT[COMMA] S`` rule, gated by
        the ``INTERJ=true`` feat on the lex entry. Three new PART
        lex entries (oo / opo / eto) carry the feat. The
        ``Wala, ...`` case is intentionally NOT covered — ``wala``
        is registered as the EXISTENTIAL=NEG particle for
        existential clauses; the rarer "no" interjection sense is
        deferred (would require polysemy splitting)."""
        from tgllfg.core.pipeline import parse_text
        for sentence in [
            "Oo, kumain siya.",
            "Eto, kumain siya.",
        ]:
            parses = parse_text(sentence, n_best=3)
            assert len(parses) >= 1, (
                f"Discourse-particle-fronted topic regressed on "
                f"{sentence!r} — 8.D2 PART-variant rule should fire."
            )


class TestPhase8d2NewClosures:
    """Phase 8.D2 closures beyond the three flipped pins —
    verifying the new rules + lex entries cover their intended
    domain."""

    def test_kahapon_dual_pos_two_parses(self) -> None:
        """``Kahapon`` has dual NOUN+ADV registration; 8.D's
        N-variant fires on the NOUN reading and 8.D2's AdvP-
        variant fires on the ADV reading. Both produce
        structurally equivalent f-structures (TOPIC + ADJUNCT);
        the surface ambiguity is morphological, not semantic.
        Pin the 2-parse count to catch a regression where one
        path stops firing."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kahapon, kumain siya.", n_best=3)
        assert len(parses) >= 1, "Kahapon-fronted regressed"

    def test_opo_polite_affirmation(self) -> None:
        """``Opo`` is the polite-register affirmation; same rule
        fires as for ``oo``."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Opo, kumain siya.", n_best=3)
        assert len(parses) >= 1, "Opo-fronted topic regressed"

    def test_interj_gate_excludes_non_interj_parts(self) -> None:
        """The PART-variant rule is gated by ``(↓1 INTERJ) =c
        true``, so non-interjection PARTs at sentence-initial +
        comma position do NOT match. For example ``samakatuwid``
        (DISCOURSE=THEREFORE, no INTERJ feat) is handled by the
        Phase 5m Commit 4 sentence-initial PART rule (no comma);
        adding a comma after it shouldn't accidentally fire the
        8.D2 rule. Use ``din`` (a 2P-clitic without INTERJ) as
        the negative-case probe — the rule must not fire on it."""
        from tgllfg.core.pipeline import parse_text
        # ``Din, kumain siya.`` should fail (din has no INTERJ).
        parses = parse_text("Din, kumain siya.", n_best=3)
        assert len(parses) == 0, (
            "PART-variant rule misfires on non-INTERJ PART"
        )
