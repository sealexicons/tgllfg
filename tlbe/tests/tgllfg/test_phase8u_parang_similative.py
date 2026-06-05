# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 8.U: ``parang`` similative comparative with NP standard.

Closes the audit-named `Parang kayo ako.` ("I'm like you") via one
new rule in ``cfg/clause.py`` parallel to the Phase 5e Commit 26
``parang`` comparative rule:

    S → V[COMPARATIVE, CTRL_CLASS=RAISING_BARE] NP[CASE=NOM] NP[CASE=NOM]

The Phase 5e Commit 26 rule has a bare ``N`` second daughter,
which fires for ``Parang aso ang bata.`` (bare-N standard).
Audit-named target ``Parang kayo ako.`` uses a PRON as standard;
PRON doesn't project to N (it builds as NP[CASE=NOM] via the
standalone-PRON-as-NP path). The new parallel rule admits any
NP[CASE=NOM]-shaped standard.

Audit-driven discovery: the audit-task description ("Likely a
1-rule extension; verify") was correctly small-scope, but probing
revealed the audit-target ``Parang kayo ako.`` had been parsing 2×
*evidential* SEEMS-LIKE readings rather than the intended LIKE
*comparative* reading. The 8.U fix is to add the missing LIKE path
for the NP-standard case; both SEEMS-LIKE and LIKE readings now
coexist for these inputs (genuine surface ambiguity).

Corpus pressure context: ``/tmp/audit_parang.py`` found 17 corpus
candidates with ``parang``; only 2 already parsed pre-8.U. The
remaining 15 fail due to orthogonal OOV blockers (`gulong`,
`makopa`, `pisngi`, `buhay`, `palasyo`, `pison`) or different-
construction issues (`parang + S` evidential clausal complement
with negation, wh-Q, etc.) — none are 8.U-scope closures.
"""

import pytest


def _has_like_reading(parses):
    """True iff at least one parse has PRED='LIKE <SUBJ, OBJ>'
    (the comparative reading, not the SEEMS-LIKE evidential)."""
    return any(
        str(p[1].feats.get("PRED", "")) == "LIKE <SUBJ, OBJ>"
        for p in parses
    )


class TestPhase8uParangSimilative:
    """The audit-target sentence and constructed variants produce
    the LIKE comparative reading via the new rule."""

    @pytest.mark.parametrize("sentence", [
        # Audit target — PRON standard.
        "Parang kayo ako.",
        # Constructed variants — case-marked-NP standard.
        "Parang si Juan ang bata.",
        "Parang ang lalaki ako.",
        "Parang ako si Juan.",
    ])
    def test_like_reading_available(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=5)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_like_reading(parses), (
            f"{sentence!r} has no LIKE-comparative parse; "
            f"PREDs: {[str(p[1].feats.get('PRED')) for p in parses]}"
        )


class TestPhase8uExistingPathUnchanged:
    """The Phase 5e Commit 26 bare-N comparative rule still fires
    on its canonical inputs after 8.U."""

    @pytest.mark.parametrize("sentence", [
        "Parang aso ang bata.",                # bare-N
        "Parang malaking aso ang bata.",       # modified-N
    ])
    def test_bare_n_comparative_still_works(
        self, sentence: str
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=5)
        assert _has_like_reading(parses), (
            f"Phase 5e C26 bare-N parang regressed on {sentence!r}"
        )


class TestPhase8uEvidentialUnchanged:
    """The Phase 5d Commit 1 evidential ``parang + S`` rule still
    fires on its canonical input. The new 8.U rule and the
    evidential rule both fire on ambiguous surfaces — that
    reflects genuine surface ambiguity in Tagalog."""

    def test_evidential_with_v(self) -> None:
        """``Parang kumain ang bata.`` — evidential parang + V."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Parang kumain ang bata.", n_best=5
        )
        assert len(parses) >= 1
        # At least one parse has SEEMS-LIKE.
        assert any(
            "SEEMS-LIKE" in str(p[1].feats.get("PRED", ""))
            for p in parses
        ), "evidential parang reading regressed"


class TestPhase8uOutOfScope:
    """Corpus candidates that remain zero-parse after 8.U — all
    have orthogonal blockers (OOV lemmas, evidential parang + S
    with negation/wh-Q, etc.), NOT 8.U scope. Pin one
    representative to show the gap class."""

    def test_oov_blocked_corpus_target(self) -> None:
        """``Parang makopa ang pisngi mo.`` — `makopa` "rose-apple"
        and `pisngi` "cheek" are OOV; would close via a separate
        lex pass, not an 8.U rule extension."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Parang makopa ang pisngi mo.", n_best=3
        )
        assert len(parses) == 0, (
            "OOV-blocked parang case unexpectedly parses — "
            "flip if a lex sub-PR added the missing nouns."
        )
