"""Phase 8.R: Spanish-loan clock-time construction `alas` + NUM.

Closes the audit-named `alas`-construction class (`alas singko` "5
o'clock", `alas dose` "12 o'clock") with three new lex entries plus
two new CFG rules plus one impersonal-S rule.

Lex (data/tgl/particles.yaml):
  - new PART `alas` with `CLOCK_MARKER=true, LEMMA=alas`
  - new NUM `onse` (CARDINAL_VALUE=11)
  - new NUM `dose` (CARDINAL_VALUE=12)

CFG (src/tgllfg/cfg/nominal.py):
  - N → PART[CLOCK_MARKER=true] NUM[CARDINAL]
      space-separated `alas singko`
  - N → PART[CLOCK_MARKER=true] PUNCT[PUNCT_CLASS=HYPHEN]
        NUM[CARDINAL]
      hyphenated `alas-tres`
  Both emit N[SEM_CLASS=TIME, TIME_VALUE=X, LEMMA=alas]; feeds Phase
  5f Commit 12 minute-composition, Phase 5f Commit 14 `mga` time-
  approximator, and the standard NP-wrapping rules.

Lex (data/tgl/particles.yaml): also adds a second reading of `-`
(Unicode HYPHEN-MINUS, U+002D — polysemous between hyphen, minus,
and en dash per the Unicode Standard) as PUNCT[PUNCT_CLASS=HYPHEN]
to keep the compound-joining hyphen distinct from the arithmetic-
minus PART[OP=MINUS] entry.

CFG (src/tgllfg/cfg/clause.py):
  - S → N[SEM_CLASS=TIME]
      impersonal time predication, no SUBJ daughter (parallels the
      Phase 5n.B C2 N-pivot rule but without the NOM-PRON pivot).

Direct corpus closures: **8 of 30** (27%) — `ng alas X` PP shape +
`sa alas X` PP shape + bare predication + `pa lang` cluster.
Remaining 22 are blocked by orthogonal OOV lex (`pasok` / `regalo`
/ `eskuwela` / `tipan` / `Santos` / `kapeterya` / `naghahapunan` /
`nagsimba` / `nag-aalmusal` / `nagluto`), OCR junk (`rnga` / `s1yete`
/ `Marfa` / `kapete:ya`), the pre-existing `na`-2P-clitic chart
issue (affects all impersonal/DEM-pivot S — not 8.R-specific), and
the colloquial `nang` time-marker reading (S&O 1972; orthogonal to
the Phase 5l/8.M subordinator `nang`).
"""

from __future__ import annotations

import pytest


def _has_time_pred(parses, expected_value=None):
    """True iff at least one parse has PRED='BE-TIME' (and optionally
    matching TIME_VALUE)."""
    for p in parses:
        if str(p[1].feats.get("PRED", "")) == "BE-TIME":
            if expected_value is None:
                return True
            if str(p[1].feats.get("TIME_VALUE")) == str(expected_value):
                return True
    return False


class TestPhase8rAlasNumComposition:
    """C1: `alas` + Spanish-NUM builds N[SEM_CLASS=TIME, TIME_VALUE=X].

    Verified indirectly via the impersonal time predication — the
    bare-N closure shows the N construction is well-formed."""

    @pytest.mark.parametrize("sentence,expected_value", [
        ("Alas tres.", "3"),
        ("Alas singko.", "5"),
        ("Alas sais.", "6"),
        ("Alas siyete.", "7"),
        ("Alas otso.", "8"),
        ("Alas onse.", "11"),
        ("Alas dose.", "12"),
    ])
    def test_alas_num_predication(
        self, sentence: str, expected_value: str,
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_time_pred(parses, expected_value), (
            f"{sentence!r} parsed but no PRED=BE-TIME with "
            f"TIME_VALUE={expected_value}"
        )

    @pytest.mark.parametrize("sentence,expected_value", [
        ("Alas-tres.", "3"),
        ("Alas-singko.", "5"),
        ("Alas-dose.", "12"),
    ])
    def test_alas_hyphen_num_predication(
        self, sentence: str, expected_value: str,
    ) -> None:
        """Hyphen variant (R&C 1990 ortho convention)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_time_pred(parses, expected_value), (
            f"{sentence!r} parsed but no PRED=BE-TIME"
        )


class TestPhase8rPredicationWithClitics:
    """C2: impersonal time S admits 2P clitics (except `na`)
    and post-matrix adjuncts via existing infrastructure."""

    @pytest.mark.parametrize("sentence", [
        "Alas singko ba?",
        "Alas dose ba?",
        "Alas singko pa.",
        "Alas singko daw.",
        "Alas singko pa lang.",
    ])
    def test_impersonal_with_2p_clitic(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"
        assert _has_time_pred(parses), (
            f"{sentence!r} parsed but no PRED=BE-TIME"
        )


class TestPhase8rNgPpShape:
    """C3: N[TIME] head in ng-PP / sa-PP — feeds NP wrappers."""

    @pytest.mark.parametrize("sentence", [
        "Naglalaro ako ng alas singko.",
        "Natutulog ako ng alas onse.",
        "Gumigising ako ng alas sais.",
        "Ano ang ginagawa nila sa alas sais ng umaga?",
        "Ano ang ginagawa nila sa alas siyete ng hapon?",
        "Ano ang ginagawa nila sa alas onse?",
    ])
    def test_alas_in_pp(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"


class TestPhase8rMinuteComposition:
    """C4: Phase 5f Commit 12 minute-composition rules (`y` / `menos`)
    fire correctly on N[TIME] heads built by the new alas+NUM rule."""

    @pytest.mark.parametrize("sentence", [
        "Ano ang ginagawa nila sa alas sais y medya?",
        "Alas siyete y medya.",
        "Alas otso menos singko.",
    ])
    def test_alas_y_minute(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse for {sentence!r}"


class TestPhase8rMgaApproximation:
    """C5: Phase 5f Commit 14 mga-approximation fires on alas+NUM
    N[TIME] heads (`mga alas singko` "around 5 o'clock")."""

    def test_mga_alas(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Naglalaro ako ng mga alas singko.", n_best=3
        )
        assert len(parses) >= 1


class TestPhase8rRegressions:
    """Existing parses unaffected after 8.R changes."""

    @pytest.mark.parametrize("sentence", [
        # Phase 4 §7.10 corpus baseline
        "May isang mamang nakatira sa isang bahay sa bukid.",
        # Phase 5n.B N-pivot predication
        "Doktor ako.",
        "Estudyante si Maria.",
        # ADJ-pred (Phase 5g)
        "Maganda siya.",
    ])
    def test_existing_parses_unaffected(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"regression on {sentence!r}"


class TestPhase8rOutOfScope:
    """Corpus candidates that remain zero-parse after 8.R — all
    blocked by orthogonal issues. Pin one of each cluster."""

    def test_na_clitic_chart_issue(self) -> None:
        """`Alas singko na ba?` — pre-existing `na` 2P-clitic
        absorption issue. Affects impersonal-S (this) AND Q-pred-S
        (`Marami ito na.`) — chart-level issue, not 8.R scope.
        Flip if the underlying chart issue is fixed."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Alas singko na ba?", n_best=3)
        assert len(parses) == 0, (
            "na+ba absorption now works — flip if chart issue fixed"
        )

    def test_oov_blocked_audit_target_closed_in_9b(self) -> None:
        """`Nagluto si Gng. Santos ng alas sais.` — `Santos` was
        the OOV blocker (and `nagluto` was already productively
        derived from `luto`). Phase 9.B adds `santos` as a proper
        surname; this audit target now parses with the existing
        8.R alas-time infrastructure. Anti-deferral pin flip."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagluto si Gng. Santos ng alas sais.", n_best=3
        )
        assert len(parses) >= 1, "Phase 9.B Santos addition unblocked"

    def test_nang_alas_colloquial_time_marker(self) -> None:
        """`Nagsimba si Marfa nang alas otso.` — S&O 1972 uses
        colloquial `nang` as case-marker for time NPs (rather
        than `ng`). Also blocked by `Marfa` OCR-misspelling of
        `Maria` and the Phase 8.M `nang` TEMPORAL gating.
        Orthogonal."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nagsimba si Marfa nang alas otso.", n_best=3
        )
        assert len(parses) == 0, (
            "S&O 1972 nang-colloquial audit target unexpectedly "
            "parses — flip if the lex/colloquial-nang sub-PR added "
            "the missing path."
        )
