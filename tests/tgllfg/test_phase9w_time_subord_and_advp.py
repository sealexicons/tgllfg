"""Phase 9.W Cluster A/H: temporal subord-clause body with bare-N +
ALREADY; compound TIME AdvP; clause-final TIME-AdvP attachment;
``sayaw`` TR+AV_ABSOL polysemy; pre-ay PRON guard past intervening
clitics.

Closes:

* R&G Intermediate sent-53 ``Kasi ho puno na ang mga bus pag
  tanghali na.`` — bare-N temporal-conditional body + ADJ-PRED
  matrix + N/ADJ polysemy on ``puno``.
* S&O 1972 p.441 sent-676 (= p.541 sent-962) ``Sila rin ay
  sasayaw ng pandanggo bukas ng gabi.`` — compound TIME AdvP +
  clause-final TIME-AdvP attachment + ``rin`` clitic past topic-
  pre-ay guard + ``sayaw`` cognate-OBJ polysemy.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _has_parse(text: str, n: int = 3) -> int:
    return len(parse_text(text, n_best=n))


# === 9.W Cluster A/H.1 — pag + bare-N[TIME] + ALREADY body ============


class TestPhase9wAh1PagTanghaliNa:
    """``SubordClause → PART[COMP_TYPE=COND, LEMMA=pag]
    N[SEM_CLASS=TIME] PART[ASPECT_PART=ALREADY]`` — the
    ``pag tanghali na`` body. Closes R&G Intermediate sent-53."""

    def test_audit_pin_sent_53(self) -> None:
        assert _has_parse(
            "Kasi ho puno na ang mga bus pag tanghali na."
        ) >= 1

    def test_audit_pin_minus_discourse(self) -> None:
        assert _has_parse(
            "Puno na ang mga bus pag tanghali na."
        ) >= 1

    def test_audit_pin_minus_matrix(self) -> None:
        assert _has_parse(
            "Umalis si Juan pag tanghali na."
        ) >= 1

    @pytest.mark.parametrize("text", [
        "Pag tanghali na, kumain si Juan.",
        "Pag umaga na, umalis si Juan.",
        "Pag gabi na, kumain si Juan.",
        "Pag hapon na, umalis si Juan.",
    ])
    def test_pre_matrix_pag_time_na(self, text: str) -> None:
        assert _has_parse(text) >= 1

    @pytest.mark.parametrize("text", [
        "Kumain si Juan pag tanghali na.",
        "Umalis si Juan pag umaga na.",
        "Tumakbo si Juan pag gabi na.",
    ])
    def test_post_matrix_pag_time_na(self, text: str) -> None:
        assert _has_parse(text) >= 1


# === 9.W Cluster A/H.2 — compound TIME AdvP ==========================


class TestPhase9wAh2CompoundTimeAdvP:
    """``AdvP → ADV[ADV_TYPE=TIME] NP[CASE=GEN, SEM_CLASS=TIME]``
    — compound time AdvP (``bukas ng gabi``, ``kahapon ng umaga``).
    Closes S&O 1972 p.441 sent-676 (= p.541 sent-962)."""

    def test_audit_pin_sent_676(self) -> None:
        assert _has_parse(
            "Sila rin ay sasayaw ng pandanggo bukas ng gabi."
        ) >= 1

    def test_audit_pin_minus_rin(self) -> None:
        assert _has_parse(
            "Sila ay sasayaw ng pandanggo bukas ng gabi."
        ) >= 1

    def test_audit_pin_minus_pandanggo(self) -> None:
        assert _has_parse(
            "Sila ay sasayaw bukas ng gabi."
        ) >= 1

    @pytest.mark.parametrize("text", [
        "Sasayaw siya bukas ng gabi.",
        "Aalis siya bukas ng umaga.",
        "Pumupunta siya bukas ng hapon.",
        # past-deictic compound
        "Pumunta siya kahapon ng gabi.",
    ])
    def test_compound_time_advp(self, text: str) -> None:
        assert _has_parse(text) >= 1


# === 9.W Cluster A/H.3 — clause-final TIME AdvP attachment ============


class TestPhase9wAh3ClauseFinalTimeAdvP:
    """``S → S AdvP`` gated on ``(↓2 ADV_TYPE) =c 'TIME'`` —
    clause-final bare TIME-AdvP attachment. Lifts the Phase 5e
    Commit 3 deferral kept since Phase 5f Commit 5 (FREQUENCY-only
    sibling)."""

    @pytest.mark.parametrize("text", [
        "Sasayaw siya bukas.",
        "Aalis siya bukas.",
        "Kumain siya kahapon.",
        "Pumunta siya kahapon.",
        "Pumunta ako kanina.",
        "Tumakbo ako kahapon.",
    ])
    def test_clause_final_time_adv(self, text: str) -> None:
        assert _has_parse(text) >= 1


# === 9.W Cluster A/H.4 — sayaw cognate-OBJ polysemy ==================


class TestPhase9wAh4SayawCognateObj:
    """``sayaw`` switched from INTR to TR+AV_ABSOL — admits both
    the bare-INTR ``sumayaw`` "dance" use and the cognate-OBJ
    ``sumayaw ng pandanggo`` "dance the pandanggo" use. Mirrors
    the Phase 9.O AV_ABSOL TR/INTR-polysemy pattern."""

    @pytest.mark.parametrize("text", [
        # Bare INTR (AV_ABSOL preservation)
        "Sumayaw si Juan.",
        "Sasayaw siya.",
        # Cognate-OBJ (new TR path)
        "Sumayaw si Juan ng pandanggo.",
        "Sasayaw siya ng pandanggo.",
    ])
    def test_sayaw_polysemy(self, text: str) -> None:
        assert _has_parse(text) >= 1


# === 9.W Cluster A/H.5 — pre-ay PRON guard past intervening clitics ==


class TestPhase9wAh5PreAyPronPastClitics:
    """``_is_pre_ay_pron`` now looks past intervening 2P clitic-
    PARTs so the topic-PRON stays in ay-fronting position even when
    a Wackernagel-eligible adverbial clitic intervenes."""

    @pytest.mark.parametrize("text", [
        "Sila rin ay sasayaw.",
        "Sila rin ay kumain.",
        "Ako rin ay sumusulat.",
        "Siya rin ay tumatakbo.",
    ])
    def test_pron_rin_ay_v(self, text: str) -> None:
        assert _has_parse(text) >= 1


# === Regressions ======================================================


class TestPhase9wAhRegressions:
    """The 9.W Cluster A/H additions don't break canonical
    Wackernagel placement, simple ay-fronting, or existing
    FREQUENCY/INDEF clause-final AdvP attachment."""

    @pytest.mark.parametrize("text", [
        # Canonical FREQUENCY clause-final AdvP (5f C5)
        "Kumain ako makalawa.",
        # INDEF clause-final AdvP (5n.B C19)
        "Pupunta ako kahit saan.",
        # Existing pag + S body
        "Pag kumain siya, umalis ako.",
        # Existing ay-fronting
        "Ako ay kumakain.",
        "Si Juan ay umalis.",
        # Existing canonical V-PRON
        "Kumain ako.",
        # Sayaw bare INTR (regression after lex switch)
        "Sumayaw siya.",
        "Sasayaw sila.",
        # Sayaw TR (new path)
        "Sumayaw siya ng pandanggo.",
    ])
    def test_regression_holds(self, text: str) -> None:
        assert _has_parse(text) >= 1, f"regression on {text!r}"
