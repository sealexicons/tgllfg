"""Phase 5n.C.2 Commit 3 — L77 gapping in coordination corpus +
tripwire.

Closes §18.1 L77 (gapping in coord) per R&B 1986 ch.18 + S&O 1972
§10. Canonical pattern: ``<V> <agent1> <args1> at <agent2> <args2>``
where the verb is shared across conjuncts (``Kumain si Maria ng
kanin at si Juan ng tinapay.`` "Maria ate rice and Juan bread").

State at Phase 5n.C.2 branch cut after Commit 3:

* **AV gapping sentences** parse today, but only via spurious
  recursive NP-coord (the post-V material decomposes to
  ``NP[COORD=AND] / NP[CASE=GEN]`` with no real gapping analysis).
  The matrix S has no ``COORD`` feat on these spurious parses;
  the spurious top-1 captures a wrong-meaning interpretation
  where the second conjunct's args are nested into one big NP.
* **DV gapping sentences** 0-parse — the GEN-marked agent
  (``ni Pedro``) can't enter the NOM-NP-coord chain, so the
  spurious-NP-coord path doesn't apply, and no rule covers the
  surface shape.

Commit 5 (this branch) adds the PRED-sharing gapping rule per
the §4.2 design appendix; that commit flips both tripwires
(DV 0-parse → ≥1 parse; AV no-COORD → ≥1-parse-with-COORD=AND).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Tripwire 1 — DV gapping currently 0-parses ===========================


class TestDeferredGappingDVZeroParse:
    """DV gapping is fully 0-parse at the branch cut. Commit 5 lifts
    the pin once the PRED-sharing rule lands."""

    @pytest.mark.parametrize("sentence", [
        "Tinulungan ni Maria si Juan at ni Pedro si Lola.",
        "Sinulatan ni Maria si Juan at ni Pedro si Lola.",
        "Inaralan ni Maria si Juan at ni Pedro si Lola.",
    ])
    def test_pinned_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"expected 0 parses for {sentence!r} pre-Commit-5; got "
            f"{len(parses)}. Did Commit 5 already land? If so, flip "
            f"this tripwire to positive parse."
        )


# === Tripwire 2 — AV gapping parses spuriously (no real-gapping marker) ==


class TestDeferredGappingAVSpurious:
    """AV gapping sentences parse via the existing recursive NP-coord
    rule, producing spurious analyses where the post-V material
    becomes a recursive NP rather than a coord of clauses. The matrix
    S has no ``COORD`` feat on these spurious parses (no real S-coord
    occurred).

    Commit 5 will add real gapping parses alongside the spurious
    ones; the new parses have ``COORD=AND`` on the matrix S, which
    flips this tripwire's polarity.
    """

    @pytest.mark.parametrize("sentence", [
        "Kumain si Maria ng kanin at si Juan ng tinapay.",
        "Bumili si Maria ng aklat at si Pedro ng panulat.",
        "Naglinis si Maria ng bahay at si Pedro ng kotse.",
        ("Kumain si Maria ng kanin, si Juan ng tinapay, "
         "at si Lola ng isda."),
        "Binigayan ni Maria si Juan ng aklat at si Pedro ng panulat.",
    ])
    def test_pinned_no_coord_on_matrix(self, sentence: str) -> None:
        parses = parse_text(sentence)
        # The sentence parses (spuriously) but no parse has matrix
        # COORD=AND. The spurious analysis treats the post-V material
        # as a recursive NP, not as a clause-coord.
        assert len(parses) >= 1, (
            f"expected ≥1 spurious parse for {sentence!r}; "
            f"got 0. Did the spurious-NP-coord path disappear?"
        )
        for _ct, fs, _astr, _diags in parses:
            coord = fs.feats.get("COORD")
            assert coord is None, (
                f"{sentence!r}: unexpected matrix COORD={coord!r} "
                f"pre-Commit-5. Did the gapping rule already land?"
            )
