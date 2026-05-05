"""Phase 5f Commit 10: clock-time NOUNs (Group E item 1).

Spanish-borrowed clock-time terms 1-12: ``ala-`` (only ``una``
for 1 o'clock) vs ``alas-`` (everything else). 12 single-token
lex entries with SEM_CLASS=TIME and TIME_VALUE.

Used as DAT-NP for time adjuncts: ``Pumunta ako sa alasotso``
"I went at 8 o'clock". The existing NP-from-N rules and
intransitive-AV ADJUNCT routing handle the syntax — no new
grammar required for this commit.

Tests cover:

* Morph: each clock-time NOUN analyses with the right
  TIME_VALUE.
* Sweep: all 12 clock-times in DAT position with ``Pumunta
  ako sa <time>``.
* Composition: clock-time DAT-NP attaches as ADJUNCT to the
  matrix.
* Special form ``ala-una`` (1 o'clock, vowel-initial
  contraction).
* Negative (per §11.2): ``*Pumunta ako alasotso`` (DAT marker
  ``sa`` required) — though the existing intransitive frame
  may admit bare-NP adjuncts in some readings; we just check
  the time isn't routed as OBJ.
* Regression: cardinals (Commits 1-9), ordinals (Commit 7),
  fractions (Commit 8) all unchanged.

Out of scope (deferred follow-on commits within Group E):

* Hyphenated orthography (``ala-una`` / ``alas-otso``) — addressed
  by the post-Phase-5f deferrals PR's ``merge_hyphen_compounds``.
* Time-of-day modifiers (``alasotso ng umaga`` "8 in the
  morning") — needs ``umaga`` / ``hapon`` / ``gabi`` /
  ``tanghali`` / ``madaling-araw`` lex with SEM_CLASS=TIME
  and a small modifier rule.
* Minute composition (``alasotso y medya`` 8:30,
  ``alasotso menos singko`` 7:55) — needs ``y`` and ``menos``
  PART entries plus a ``TIME → CLOCK [y|menos] NUM`` rule.
* Native time deictics (``kanina``, ``mamaya``, ``tanghali``,
  etc. that aren't already in lex).
* ``mga`` time approximation (``mga alasotso`` "around 8"):
  ``mga`` isn't yet in lex.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


def _clock_times() -> list[tuple[str, str]]:
    """Yield (lemma, time_value)."""
    return [
        ("alauna",      "1"),
        ("alasdos",     "2"),
        ("alastres",    "3"),
        ("alaskuwatro", "4"),
        ("alassingko",  "5"),
        ("alassais",    "6"),
        ("alassiyete",  "7"),
        ("alasotso",    "8"),
        ("alasnuwebe",  "9"),
        ("alasdies",    "10"),
        ("alasonse",    "11"),
        ("alasdose",    "12"),
    ]


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


class TestClockTimeMorph:
    """Each clock-time NOUN analyses with SEM_CLASS=TIME and the
    right TIME_VALUE."""

    def test_all_clock_times_analyze(self) -> None:
        for lemma, value in _clock_times():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "NOUN"]
            assert cands, f"no NOUN analysis for {lemma}"
            ma = cands[0]
            assert ma.feats.get("SEM_CLASS") == "TIME", (
                f"{lemma}: SEM_CLASS expected 'TIME', got "
                f"{ma.feats.get('SEM_CLASS')!r}"
            )
            assert ma.feats.get("TIME_VALUE") == value, (
                f"{lemma}: TIME_VALUE expected {value!r}, got "
                f"{ma.feats.get('TIME_VALUE')!r}"
            )

    def test_alauna_special_form(self) -> None:
        # 1 o'clock uses ala- (vowel-initial contraction), not alas-.
        toks = tokenize("alauna")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("TIME_VALUE") == "1"

    def test_alasonse_eleven(self) -> None:
        # 11 uses alas- not ala- (despite onse being vowel-initial).
        toks = tokenize("alasonse")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "NOUN"]
        assert cands
        assert cands[0].feats.get("TIME_VALUE") == "11"


# === All 12 clock-times — sweep ===========================================


class TestAllClockTimesSweep:
    """Each of the 12 clock-times appears as a DAT-NP adjunct in
    ``Pumunta ako sa <time>``."""

    def test_each_clock_time_in_dat(self) -> None:
        for lemma, value in _clock_times():
            text = f"Pumunta ako sa {lemma}."
            adj = _adjunct_with_lemma(text, lemma)
            assert adj is not None, f"no DAT adjunct for {text!r}"
            assert adj.feats.get("CASE") == "DAT"
            assert adj.feats.get("MARKER") == "SA"


# === Composition with verb ================================================


class TestClockTimeWithVerbs:
    """Clock-time DAT-NPs attach as ADJUNCT to standard verbal
    matrix clauses."""

    def test_pumunta_sa_alasotso(self) -> None:
        # ``Pumunta ako sa alasotso.`` "I went at 8 o'clock."
        adj = _adjunct_with_lemma("Pumunta ako sa alasotso.", "alasotso")
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"

    def test_kumain_sa_alauna(self) -> None:
        # ``Kumain ako sa alauna.`` "I ate at 1 o'clock."
        adj = _adjunct_with_lemma("Kumain ako sa alauna.", "alauna")
        assert adj is not None

    def test_tumakbo_sa_alaskuwatro(self) -> None:
        adj = _adjunct_with_lemma(
            "Tumakbo ako sa alaskuwatro.", "alaskuwatro"
        )
        assert adj is not None

    def test_tulog_sa_alasdose(self) -> None:
        # tulog "sleep" — at midnight.
        adj = _adjunct_with_lemma(
            "Natulog ako sa alasdose.", "alasdose"
        )
        # The intransitive-AV / OV-style "natulog" should attach
        # this DAT as ADJUNCT.
        assert adj is not None


# === Negative fixtures ====================================================


class TestClockTimeNegative:

    def test_clock_not_routed_as_obj(self) -> None:
        # ``Pumunta ako sa alasotso.`` — the clock-time is a DAT
        # adjunct, NOT an OBJ. (Pumunta is intransitive AV; it
        # has no OBJ slot.)
        rs = parse_text("Pumunta ako sa alasotso.", n_best=5)
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if isinstance(obj, FStructure):
                assert obj.feats.get("LEMMA") != "alasotso", (
                    "alasotso routed as OBJ — should be DAT adjunct"
                )


# === Regression ===========================================================


class TestClockTimeRegressions:

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs

    def test_ordinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng unang aklat.", n_best=5)
        assert rs

    def test_fraction_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng dalawang kalahati.", n_best=5)
        assert rs

    def test_arithmetic_unchanged(self) -> None:
        rs = parse_text("Dalawa dagdag tatlo ay lima.", n_best=5)
        assert any(
            f.feats.get("PRED") == "ARITHMETIC"
            for _, f, _, _ in rs
        )

    def test_predicative_cardinal_unchanged(self) -> None:
        rs = parse_text("Tatlo ang anak ko.", n_best=5)
        assert any(
            f.feats.get("PRED") == "CARDINAL <SUBJ>"
            for _, f, _, _ in rs
        )


# === LMT diagnostics clean ================================================


class TestClockTimeLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Pumunta ako sa alauna.",
            "Pumunta ako sa alasdos.",
            "Pumunta ako sa alasotso.",
            "Pumunta ako sa alasdose.",
            "Kumain ako sa alaskuwatro.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
