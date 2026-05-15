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


class TestPhase8dOutOfScope:
    """Three construction-class gaps surfaced during 8.D probing.
    These are NOT part of the audit-task scope (`Isang araw,
    ...`) — pin them so a future sub-PR closing them produces a
    visible signal."""

    def test_adv_fronted_topic_still_fails(self) -> None:
        """ADV-only forms like ``bukas`` "tomorrow" don't fire
        the N-variant of the 8.D rule. ``Bukas, kumain siya.``
        needs a sibling ADV-variant. Pinned for follow-on."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Bukas, kumain siya.", n_best=3)
        assert len(parses) == 0, (
            "ADV-fronted topic unexpectedly parses — flip this "
            "pin if a sub-PR added the ADV-variant rule."
        )

    def test_pp_fronted_topic_still_fails(self) -> None:
        """Preposition-headed (sa-PP) topics like ``Sa simula,
        ...`` don't fire the 8.D rules (no PP-variant). Pinned."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Sa simula, kumain si Juan.", n_best=3
        )
        assert len(parses) == 0, (
            "PP-fronted topic unexpectedly parses — flip this "
            "pin if a sub-PR added the PP-variant rule."
        )

    def test_discourse_particle_fronted_still_fails(self) -> None:
        """Discourse-particle-fronted ``Oo, ...`` / ``Eto, ...``
        / ``Wala, ...`` patterns need a PART-variant. Pinned."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Oo, kumain siya.", n_best=3)
        assert len(parses) == 0, (
            "Discourse-particle-fronted topic unexpectedly "
            "parses — flip this pin if a sub-PR added it."
        )
