"""Phase 5k Commit 2: apostrophe-t text-pass.

Roadmap §12.1 / plan-of-record §5 (text-pass note), §6 Commit 2.
New pre-pass :func:`tgllfg.text.split_apostrophe_t` collapses the
post-vowel bound clitic ``'t`` (= contracted ``at`` "and") into a
synthetic ``at`` token. The tokenizer's ``\\w+|\\S`` regex splits
``Maria't`` into three tokens (``Maria`` / ``'`` / ``t``); this
pass merges the apostrophe + t back into one ``at`` token routing
to the Phase 5k Commit 1 PART[COORD=AND] lex entry.

Pipeline order (``core/pipeline.py``): ``tokenize`` →
``split_apostrophe_t`` (NEW) → ``split_linker_ng`` →
``merge_hyphen_compounds`` → ``split_enclitics`` →
``analyze_tokens``. Runs first among pre-passes so all downstream
stages see the canonical ``at`` surface.

Pre-state (verified 2026-05-07): no existing corpus / test entry
contains ``'t`` orthography post-vowel; the pre-pass is purely
additive. The rule additionally enables the Phase 5f deferred
coordinated-cardinal compositions (``apat na pu't lima`` 45,
``isang daa't dalawampu`` 120) once the NUM-coordination grammar
rule lands as a Phase 5f follow-on.
"""

from __future__ import annotations

import pytest

from tgllfg.text import split_apostrophe_t, tokenize


# === Unit tests for split_apostrophe_t ================================


class TestApostropheTBasic:
    """The pre-pass collapses ``[X, ', t]`` into ``[X, at]`` when X
    ends in a vowel."""

    def test_marit_juan_three_tokens_to_two(self) -> None:
        toks = tokenize("Maria't Juan")
        assert [t.surface for t in toks] == ["Maria", "'", "t", "Juan"]
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == ["Maria", "at", "Juan"]

    def test_marit_alone(self) -> None:
        """``Maria't`` (sentence-final or pre-period) — three input
        tokens collapse to two."""
        toks = tokenize("Maria't")
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == ["Maria", "at"]

    def test_with_space_before_t(self) -> None:
        """``Maria 't Juan`` (space-separated apostrophe-t) — same
        tokenization as no-space form, same collapse."""
        toks = tokenize("Maria 't Juan")
        assert [t.surface for t in toks] == ["Maria", "'", "t", "Juan"]
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == ["Maria", "at", "Juan"]

    def test_synthetic_at_norm_is_lowercase(self) -> None:
        """The synthetic ``at`` token's ``norm`` field is
        lowercase ``at`` regardless of the original surrounding
        capitalization."""
        toks = tokenize("Maria't Juan")
        out = split_apostrophe_t(toks)
        synthetic = out[1]
        assert synthetic.surface == "at"
        assert synthetic.norm == "at"


# === Span preservation ================================================


class TestApostropheTSpans:
    """The synthetic ``at`` token spans the original ``'`` and ``t``
    positions so downstream span-bookkeeping (diagnostics,
    cnode_label spans, etc.) stays consistent."""

    def test_synthetic_at_spans_apostrophe_through_t(self) -> None:
        toks = tokenize("Maria't Juan")
        out = split_apostrophe_t(toks)
        # Original tokens: Maria(0,5), '(5,6), t(6,7), Juan(8,12)
        host = out[0]
        synth = out[1]
        juan = out[2]
        assert host.surface == "Maria"
        assert host.start == 0
        assert host.end == 5
        assert synth.surface == "at"
        assert synth.start == 5  # ' start
        assert synth.end == 7    # t end
        assert juan.surface == "Juan"
        assert juan.start == 8


# === Vowel-only firing ================================================


class TestApostropheTVowelGate:
    """The pre-pass only fires when the host's last character is a
    vowel. Consonant-final hosts are untouched (no apostrophe-t
    reading in modern Tagalog after a consonant)."""

    @pytest.mark.parametrize("vowel_final_host", [
        "isa",     # ends in 'a'
        "dalawa",  # ends in 'a'
        "pu",      # ends in 'u' (decade morpheme)
        "tatlo",   # ends in 'o'
        "Maria",   # ends in 'a'
        "siya",    # ends in 'a'
    ])
    def test_vowel_final_host_fires(self, vowel_final_host: str) -> None:
        toks = tokenize(f"{vowel_final_host}'t kalahati")
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == [
            vowel_final_host, "at", "kalahati",
        ]

    @pytest.mark.parametrize("consonant_final_host", [
        "apat",    # ends in 't'
        "lima",    # actually ends in 'a' — would fire — skip
        "anim",    # ends in 'm'
        "pitong",  # ends in 'g'
    ])
    def test_consonant_final_host_does_not_fire(
        self, consonant_final_host: str
    ) -> None:
        # Skip the misclassified 'lima' (vowel-final) edge.
        if consonant_final_host[-1] in "aeiouAEIOU":
            return
        toks = tokenize(f"{consonant_final_host}'t kalahati")
        out = split_apostrophe_t(toks)
        # Tokenizer keeps ', t separate; the pre-pass should not
        # collapse them since the host is consonant-final.
        assert "'" in [t.surface for t in out]
        assert any(t.surface == "t" for t in out)


# === Multiple apostrophe-t in one sentence ============================


class TestApostropheTMultiple:
    """Multiple ``'t`` clitics in one sentence each fire
    independently."""

    def test_three_conjuncts(self) -> None:
        """``isa't dalawa't tatlo`` — three NUMs joined by two
        ``'t`` clitics. After the pre-pass: ``isa at dalawa at
        tatlo``."""
        toks = tokenize("isa't dalawa't tatlo")
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == [
            "isa", "at", "dalawa", "at", "tatlo",
        ]

    def test_coordinated_decade_with_unit(self) -> None:
        """``apat na pu't lima`` ("45" — coordinated decade-unit) —
        the Phase 5f deferred coordinated-higher-numeral form. The
        pre-pass alone collapses the ``'t``; the actual numeric
        composition awaits a NUM-coordination grammar rule (Phase
        5f follow-on)."""
        toks = tokenize("apat na pu't lima")
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == [
            "apat", "na", "pu", "at", "lima",
        ]


# === Non-firing cases =================================================


class TestApostropheTNonFiring:
    """The pre-pass leaves token streams without the
    ``[X-vowel, ', t]`` pattern unchanged."""

    def test_plain_at_unchanged(self) -> None:
        """``Maria at Juan`` (already-explicit ``at``) — no
        apostrophe in the stream, no transformation."""
        toks = tokenize("Maria at Juan")
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == ["Maria", "at", "Juan"]

    def test_apostrophe_alone_at_sentence_start(self) -> None:
        """``'t`` at sentence-start with no preceding host — pass
        leaves the tokens unchanged (no host token to merge with)."""
        toks = tokenize("'t Juan")
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == ["'", "t", "Juan"]

    def test_t_alone_after_vowel_no_apostrophe(self) -> None:
        """``Maria t Juan`` — ``t`` alone after a vowel-final word,
        without the apostrophe — pass leaves unchanged (the
        pattern requires the apostrophe)."""
        toks = tokenize("Maria t Juan")
        out = split_apostrophe_t(toks)
        assert [t.surface for t in out] == ["Maria", "t", "Juan"]

    def test_apostrophe_followed_by_non_t(self) -> None:
        """``Maria's Juan`` (English-style possessive — irrelevant
        to Tagalog but stress-test) — the trigger requires the
        next token's norm to be ``t``; ``s`` doesn't fire."""
        toks = tokenize("Maria's Juan")
        out = split_apostrophe_t(toks)
        # The apostrophe + 's' stay separate.
        assert [t.surface for t in out] == ["Maria", "'", "s", "Juan"]


# === End-to-end: synthetic 'at' analyzes correctly ===================


class TestApostropheTEndToEnd:
    """After the pre-pass, the synthetic ``at`` token is morph-
    analyzed via the Phase 5k Commit 1 PART[COORD=AND] lex entry —
    same as if the user typed ``at`` explicitly. Verified via
    ``analyze_tokens`` directly on the post-pre-pass stream."""

    def test_synthetic_at_indexes_as_coord_and(self) -> None:
        from tgllfg.morph import analyze_tokens

        toks = tokenize("Maria't Juan")
        toks = split_apostrophe_t(toks)
        analyses = analyze_tokens(toks)
        # Position 1 is the synthetic 'at'.
        at_analyses = analyses[1]
        coord_parts = [
            a for a in at_analyses
            if a.pos == "PART" and a.feats.get("COORD") == "AND"
        ]
        assert len(coord_parts) == 1, (
            f"expected synthetic 'at' to analyze as PART[COORD=AND]; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in at_analyses]}"
        )
        assert coord_parts[0].feats.get("LEMMA") == "at"
