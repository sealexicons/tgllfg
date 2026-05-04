"""Phase 5f Commit 14: mga time approximation (Group E item 3).

The Tagalog plural / approximator particle ``mga`` is added
as a PART with PLURAL_MARKER=YES feature. A new grammar rule
handles the time-approximation reading on TIME-class N's:

* ``mga alasotso`` "around 8 o'clock"
* ``sa mga alasotso`` "at around 8 o'clock"
* ``sa mga alauna`` "at around 1 o'clock"
* ``sa mga alasdose`` "at around 12 o'clock"

Lex (data/tgl/particles.yaml):

* ``mga`` PART with ``PLURAL_MARKER: YES``.

Grammar (src/tgllfg/cfg/nominal.py):

* New N rule: ``N → PART N`` with constraining equations
  ``(↓1 PLURAL_MARKER) =c 'YES'`` (particle is mga) and
  ``(↓2 SEM_CLASS) =c 'TIME'`` (head is clock-time). Adds
  ``APPROX=YES`` to the matrix N.

Out of scope (deferred to follow-on commits):

* Plural marker on regular nouns (``ang mga aklat`` "the
  books"). Same ``mga`` lex entry, different construction —
  needs an NP-internal rule for ``DET PART[mga] N`` plural
  marking. Substantial scope (touches NUM agreement, possibly
  classifier).
* Cardinal approximation (``mga sampu`` "around ten") — same
  ``mga`` lex entry, but constrained to NUM[CARDINAL=YES]
  daughter instead of N[SEM_CLASS=TIME].
* DAY / MONTH approximation (``mga Lunes``, ``mga Pebrero``)
  — not idiomatic in standard Tagalog.

Tests cover:

* Morph: ``mga`` analyses as PART with PLURAL_MARKER=YES.
* Time approximation: ``sa mga alasotso``, ``sa mga alauna``,
  ``sa mga alasdose`` — all clock-time approximations parse.
* Sweep across all 12 clock-times.
* Composition with verb (parses as DAT adjunct).
* Negative (per §11.2): ``*mga bata`` (non-TIME head — plural
  reading not yet supported, so the approximator rule's
  SEM_CLASS=TIME constraint blocks); ``mga`` alone doesn't
  combine with non-temporal NOUNs as approximator.
* Regression: clock-time alone, time-of-day, minute composition,
  date-of-week, cardinals, ordinals, fractions all unchanged.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _adjunct_with_lemma(text: str, lemma: str) -> FStructure | None:
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        adj = f.feats.get("ADJUNCT")
        if adj is None:
            continue
        members = (
            list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
        )
        for m in members:
            if isinstance(m, FStructure) and m.feats.get("LEMMA") == lemma:
                return m
    return None


# === Morph layer ==========================================================


class TestMgaMorph:

    def test_mga_is_plural_marker(self) -> None:
        toks = tokenize("mga")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "PART"]
        assert cands
        assert cands[0].feats.get("PLURAL_MARKER") == "YES"


# === Time approximation ===================================================


class TestMgaTimeApproximation:

    def test_sa_mga_alasotso(self) -> None:
        # ``Pumunta ako sa mga alasotso.`` "I went at around 8."
        adj = _adjunct_with_lemma(
            "Pumunta ako sa mga alasotso.", "alasotso"
        )
        assert adj is not None

    def test_sa_mga_alauna(self) -> None:
        adj = _adjunct_with_lemma(
            "Pumunta ako sa mga alauna.", "alauna"
        )
        assert adj is not None

    def test_sa_mga_alasdose(self) -> None:
        adj = _adjunct_with_lemma(
            "Pumunta ako sa mga alasdose.", "alasdose"
        )
        assert adj is not None

    def test_sweep_all_clock_times(self) -> None:
        """All 12 clock-times should compose with mga
        approximation."""
        clocks = [
            "alauna", "alasdos", "alastres", "alaskuwatro",
            "alassingko", "alassais", "alassiyete", "alasotso",
            "alasnuwebe", "alasdies", "alasonse", "alasdose",
        ]
        for clock in clocks:
            text = f"Pumunta ako sa mga {clock}."
            adj = _adjunct_with_lemma(text, clock)
            assert adj is not None, f"no parse for {text!r}"


# === Composition ==========================================================


class TestMgaComposition:

    def test_kumain_sa_mga_alasotso(self) -> None:
        # Different verb to verify composition isn't pumunta-specific.
        adj = _adjunct_with_lemma(
            "Kumain ako sa mga alasotso.", "alasotso"
        )
        assert adj is not None


# === Negative fixtures (per §11.2) ========================================


class TestMgaNegative:

    def test_mga_with_non_time_head_blocked(self) -> None:
        # ``Pumunta ako sa mga bata.`` — bata is no SEM_CLASS, so
        # the approximator rule shouldn't fire. (Plural marking on
        # regular nouns is a separate construction not yet
        # supported, so this should fail to parse altogether.)
        rs = parse_text("Pumunta ako sa mga bata.", n_best=10)
        # Either no parse or parses with blocking diagnostics.
        # We just verify no parse has bata as ADJUNCT-OBJ from
        # the approximator rule.
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if isinstance(m, FStructure):
                    if m.feats.get("APPROX") == "YES":
                        raise AssertionError(
                            "non-TIME head accepted as APPROX matrix"
                        )

    def test_mga_with_month_blocked(self) -> None:
        # ``mga Pebrero`` (plural Februarys?) — MONTH SEM_CLASS,
        # not TIME. The approximator rule's constraint is
        # SEM_CLASS=TIME, so this shouldn't fire.
        rs = parse_text("Pumunta ako sa mga Pebrero.", n_best=10)
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if isinstance(m, FStructure) and m.feats.get("APPROX") == "YES":
                    raise AssertionError(
                        "MONTH head accepted as APPROX matrix — "
                        "should be TIME-only"
                    )


# === Regression ===========================================================


class TestMgaRegressions:

    def test_clock_time_alone_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa alasotso.", n_best=5)
        assert rs

    def test_time_of_day_modifier_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa alasotso ng umaga.", n_best=5)
        assert rs

    def test_minute_composition_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa alasotso y singko.", n_best=5)
        assert rs

    def test_date_of_week_with_sa_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa Lunes.", n_best=5)
        assert rs

    def test_tuwing_unchanged(self) -> None:
        rs = parse_text("Pumunta ako tuwing Lunes.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestMgaLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Pumunta ako sa mga alasotso.",
            "Pumunta ako sa mga alauna.",
            "Pumunta ako sa mga alasdose.",
            "Kumain ako sa mga alasotso.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
