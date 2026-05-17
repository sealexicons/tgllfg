"""Phase 8.G: ``bago`` as ADJ "new" + ``ani`` NOUN lex closures.

Closes the audit-named `Bagong ani ang palay.` (rg81 ANG MANOK
Wave 1, "The rice is newly harvested"). The audit-task description
suggested a "LEMMA gate on the linker" — diagnostic during 8.G
probing showed that misleading: the actual blockers are pure lex
gaps.

1. ``bago`` was only registered as ``PART`` with
   ``COMP_TYPE: TEMP_BEFORE`` (the subordinator "before",
   `cfg/subordination.py`). The ADJ "new" sense was missing
   entirely from adjectives.yaml.
2. ``ani`` "harvest" was OOV in nouns.yaml.

Once both lex entries land, the canonical Phase 5g + Phase 5n.B
N-pivot-predication-with-ADJ-modifier infrastructure consumes
``Bagong ani ang palay.`` unchanged — no rule changes needed.

Out of 8.G scope (subordinator-`bago` sentences from R&C 1990):
``Bago dumating ang pulis, nakatakbo siya.`` etc. The
subordinator-``bago`` already parses (the PART registration
handles it). The audit-pressure for the SUBJ-of-bago-CP shape
in 8.G is zero — the 54 zero-parse corpus matches mostly use
the subordinator sense, which belongs to the Phase 8.M
(temporal subordinator) family of follow-ons.
"""

from __future__ import annotations

import pytest


class TestPhase8gBagoAdj:
    """The new ``bago`` ADJ entry produces clean parses on the
    audit-target sentence and adjacent variants."""

    @pytest.mark.parametrize("sentence", [
        # Wave 1 audit target (rg81 ANG MANOK).
        "Bagong ani ang palay.",
        # Constructed variants — bago as predicative ADJ.
        "Bago ang palay.",
        "Bago ang aklat.",
        # bago as NP-internal modifier (Phase 5g pre-N modifier
        # rule fires uniformly across all ma_adj=[] entries).
        "Maganda ang bagong aklat.",
        "Kinakain niya ang bagong aklat.",
    ])
    def test_sentence_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"no parse for {sentence!r} after 8.G lex add"
        )


class TestPhase8gLexEntries:
    """Sanity-check the two new lex entries are loaded as
    expected."""

    def test_bago_is_known_adj(self) -> None:
        """``bago`` is now registered as ADJ in addition to its
        existing PART (subordinator) registration in particles.yaml.
        The standalone surface is a known ADJ analysis."""
        from tgllfg.morph.analyzer import analyze_tokens
        from tgllfg.text.tokenizer import tokenize
        analyses = analyze_tokens(tokenize("bago"))
        assert analyses and analyses[0]
        poses = {a.pos for a in analyses[0]}
        assert "ADJ" in poses, (
            f"bago should be analyzable as ADJ; got {poses}"
        )

    def test_ani_is_known_noun(self) -> None:
        """``ani`` "harvest" is in nouns.yaml."""
        from tgllfg.morph.analyzer import _get_default
        analyzer = _get_default()
        assert analyzer.is_known_surface("ani"), (
            "ani not known after 8.G lex add"
        )


class TestPhase8gSubordinatorBagoUnchanged:
    """Sanity-check the existing PART (subordinator "before")
    sense of ``bago`` still parses on its canonical inputs.
    Adding the ADJ sense should not affect the subordinator
    pathway."""

    def test_subordinator_bago_unchanged(self) -> None:
        """The Phase 5l subordinator-bago rule
        (PART[COMP_TYPE=TEMP_BEFORE]) handles temporal
        subordinate clauses."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Bago dumating ang pulis, nakatakbo siya.",
            n_best=3,
        )
        assert len(parses) >= 1, (
            "subordinator-bago temporal SubordClause regressed"
        )


class TestPhase8gOutOfScope:
    """The audit-mga-bago probe found 55 corpus candidates;
    only `Bagong ani ang palay.` is in 8.G's named scope.
    The other 54 are subordinator-`bago` sentences (Phase 8.M
    temporal-subordinator territory) or have orthogonal blockers
    (compound `bagong-taon`, OOV `dating` noun-from-verb, etc.).
    Pin a representative non-closure as a marker; flipping it
    would be a future sub-PR's signal."""

    def test_complex_bago_dating_closed_in_9j(self) -> None:
        """``Ikaw ba ang bagong dating?`` — bagong + dating + Q.
        ``dating`` "arrival" was an 8.G deferral pin asserting
        OOV-blocked. Phase 9.J catch-all OOV pass added ``dating``
        as a NOUN entry (zero-conversion coexisting with the V
        root in verbs.yaml); ``bago`` + linker + ``dating`` now
        composes as an NP and the audit sentence parses."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Ikaw ba ang bagong dating?", n_best=3
        )
        assert len(parses) >= 1, (
            "9.J added dating N; complex bagong+dating should parse."
        )
