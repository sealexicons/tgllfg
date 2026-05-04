"""Phase 5f Commit 14: seasons (Group G).

Adds 5 SEM_CLASS=SEASON NOUNs (the canonical two-season system
``taginit`` / ``tagulan`` plus three other ``tag-`` compounds:
``taglamig`` / ``tagaraw`` / ``taggutom``) and extends the
Phase 5f Commit 13 temporal-frame PP rule with a SEASON variant
so ``tuwing tagulan`` "every rainy season" and ``noong taginit``
"during the dry season" parse.

Lex (data/tgl/nouns.yaml):

* 5 season NOUNs with SEM_CLASS=SEASON. Stored as single-token
  forms (``taginit``, ``tagulan``, ...) because the canonical
  hyphenated orthography (``tag-init``, ``tag-ulan``, ...) is
  split by the current tokenizer (``\\w+|\\S``); a tokenizer
  pre-pass to glue the hyphenated forms is deferred.

Grammar (src/tgllfg/cfg/discourse.py):

* Phase 5f Commit 13 temporal-frame PP rule
  (``PP → PART N`` with ``(↓1 TIME_FRAME)`` and
  ``(↓2 SEM_CLASS) =c '<X>'``) gains a SEASON variant in the
  ``for sem_class in (...)`` loop. No other grammar change.

Tests cover:

* Morph: 5 SEASON NOUNs analyze with SEM_CLASS=SEASON.
* DAT-NP composition (existing rule, no SEASON-specific gate):
  ``sa tagulan`` "in the rainy season" via ``Pumunta ako sa <S>.``
* PERIODIC PP composition (new SEASON variant of the
  temporal-frame PP rule): ``Pumunta ako tuwing <S>.`` for each
  season.
* PAST PP composition (same rule, ``noong``): ``Pumunta kami noong
  <S>.`` for each season.
* ay-fronting of a SEASON PP: ``Tuwing tagulan ay pumunta ako.``
* Negatives (per §11.2): ``*Pumunta ako tuwing aklat`` (non-
  temporal head with no SEM_CLASS does not compose) and
  ``*Pumunta ako tuwing araw`` (existing NOUN with no SEM_CLASS
  set — confirms the gate is required, not just descriptive).
* Regression: clock-time / dates / cardinal / mga / minute
  unchanged.
* LMT diagnostics: a sweep of representative SEASON sentences
  parse with at least one non-blocking diagnostic stack.

Out of scope (deferred follow-on commits):

* Hyphenated orthography (``tag-init`` etc.) — needs a tokenizer
  pre-pass.
* Productive ``tag-`` paradigm (figurative / colloquial readings
  beyond the lexicalised season set) — explicit plan §11.1
  Group G choice.
* SEM_CLASS=SEASON percolation to NP (parallel to MONTH_VALUE /
  DAY_VALUE on NPs) — same NP-from-N projection limitation as
  the cardinal-modifier features.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _seasons() -> list[str]:
    return ["taginit", "tagulan", "taglamig", "tagaraw", "taggutom"]


def _adjunct_with_obj_lemma(text: str, lemma: str) -> FStructure | None:
    """Find any parse where an ADJUNCT has an OBJ with the given
    lemma."""
    rs = parse_text(text, n_best=10)
    for _, f, _, _ in rs:
        adj = f.feats.get("ADJUNCT")
        if adj is None:
            continue
        members = (
            list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
        )
        for m in members:
            if not isinstance(m, FStructure):
                continue
            obj = m.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("LEMMA") == lemma:
                return m
    return None


def _adjunct_with_lemma(text: str, lemma: str) -> FStructure | None:
    """Find any parse where an ADJUNCT directly has the given lemma
    (used for sa-NP season constructions)."""
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


class TestSeasonMorph:

    def test_all_seasons_analyze(self) -> None:
        for lemma in _seasons():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "NOUN"]
            assert cands, f"no NOUN analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("SEM_CLASS") == "SEASON", (
                f"{lemma}: SEM_CLASS expected 'SEASON', got "
                f"{ma.feats.get('SEM_CLASS')!r}"
            )


# === Season as DAT-NP (existing rule) =====================================


class TestSeasonWithSa:
    """``sa tagulan`` "in the rainy season" — composes via the
    existing DAT-NP intransitive-ADJUNCT path. No new grammar; this
    test confirms the SEM_CLASS=SEASON addition doesn't disturb
    existing routing."""

    def test_sa_each_season(self) -> None:
        for lemma in _seasons():
            text = f"Pumunta ako sa {lemma}."
            adj = _adjunct_with_lemma(text, lemma)
            assert adj is not None, f"no DAT-NP parse for {text!r}"
            assert adj.feats.get("CASE") == "DAT"


# === Season with `tuwing` (PERIODIC; new SEASON variant) ==================


class TestSeasonWithTuwing:
    """``tuwing tagulan`` "every rainy season" — the Phase 5f
    Commit 13 temporal-frame PP rule extended with a SEM_CLASS=
    SEASON variant in this commit."""

    def test_tuwing_each_season_clause_final(self) -> None:
        for lemma in _seasons():
            text = f"Pumunta ako tuwing {lemma}."
            adj = _adjunct_with_obj_lemma(text, lemma)
            assert adj is not None, f"no tuwing-PP parse for {text!r}"
            assert adj.feats.get("TIME_FRAME") == "PERIODIC"

    def test_tuwing_tagulan_ay_fronted(self) -> None:
        rs = parse_text("Tuwing tagulan ay pumunta ako.", n_best=10)
        assert rs
        found = False
        for _, f, _, _ in rs:
            topic = f.feats.get("TOPIC")
            if not (isinstance(topic, FStructure)
                    and topic.feats.get("TIME_FRAME") == "PERIODIC"):
                continue
            obj = topic.feats.get("OBJ")
            if isinstance(obj, FStructure) and obj.feats.get("LEMMA") == "tagulan":
                found = True
                break
        assert found, "no PERIODIC-TOPIC parse for ay-fronted SEASON PP"


# === Season with `noong` (PAST; new SEASON variant) =======================


class TestSeasonWithNoong:
    """``noong taginit`` "during the dry season" — same PP rule
    with TIME_FRAME=PAST."""

    def test_noong_each_season_clause_final(self) -> None:
        for lemma in _seasons():
            text = f"Pumunta kami noong {lemma}."
            adj = _adjunct_with_obj_lemma(text, lemma)
            assert adj is not None, f"no noong-PP parse for {text!r}"
            assert adj.feats.get("TIME_FRAME") == "PAST"


# === Negative fixtures (per §11.2) ========================================


class TestSeasonNegative:

    def test_tuwing_non_temporal_blocked(self) -> None:
        # ``*Pumunta ako tuwing aklat.`` — ``aklat`` has no
        # SEM_CLASS, so neither the SEASON variant nor the existing
        # DAY/TIME/MONTH variants fire.
        for _, f, _, _ in parse_text("Pumunta ako tuwing aklat.", n_best=10):
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if not isinstance(m, FStructure):
                    continue
                if not m.feats.get("TIME_FRAME"):
                    continue
                obj = m.feats.get("OBJ")
                if (isinstance(obj, FStructure)
                        and obj.feats.get("LEMMA") == "aklat"):
                    raise AssertionError(
                        "tuwing aklat composed despite non-temporal head"
                    )

    def test_tuwing_araw_blocked(self) -> None:
        # ``araw`` (day / sun) is an existing NOUN with NO
        # SEM_CLASS; including it confirms the gate is constraining
        # (not just descriptive — ``araw`` would be a plausible
        # SEASON-domain head if the gate were missing).
        for _, f, _, _ in parse_text("Pumunta ako tuwing araw.", n_best=10):
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if not isinstance(m, FStructure):
                    continue
                if not m.feats.get("TIME_FRAME"):
                    continue
                obj = m.feats.get("OBJ")
                if (isinstance(obj, FStructure)
                        and obj.feats.get("LEMMA") == "araw"):
                    raise AssertionError(
                        "tuwing araw composed despite no SEM_CLASS on head"
                    )

    def test_non_season_not_marked_season(self) -> None:
        # A regular noun (``aklat``) must not pick up
        # SEM_CLASS=SEASON. (Sanity check on the lex addition.)
        toks = tokenize("aklat")
        ml = analyze_tokens(toks)
        for c in ml[0]:
            assert c.feats.get("SEM_CLASS") != "SEASON"


# === Regression ===========================================================


class TestSeasonRegressions:

    def test_clock_time_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa alasotso.", n_best=5)
        assert rs

    def test_tuwing_day_unchanged(self) -> None:
        # Phase 5f Commit 13 DAY variant of the same PP rule.
        adj = _adjunct_with_obj_lemma("Pumunta ako tuwing Lunes.", "lunes")
        assert adj is not None
        assert adj.feats.get("TIME_FRAME") == "PERIODIC"

    def test_noong_month_unchanged(self) -> None:
        # Phase 5f Commit 13 MONTH variant.
        adj = _adjunct_with_obj_lemma("Pumunta kami noong Pebrero.", "pebrero")
        assert adj is not None
        assert adj.feats.get("TIME_FRAME") == "PAST"

    def test_tuwing_time_unchanged(self) -> None:
        # Phase 5f Commit 13 TIME variant.
        adj = _adjunct_with_obj_lemma("Pumunta ako tuwing umaga.", "umaga")
        assert adj is not None
        assert adj.feats.get("TIME_FRAME") == "PERIODIC"

    def test_mga_time_approximation_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa mga alasotso.", n_best=5)
        assert rs

    def test_minute_composition_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa alasotso y singko.", n_best=5)
        assert rs

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Kumain ako ng tatlong isda.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestSeasonLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Pumunta ako sa tagulan.",
            "Pumunta ako tuwing tagulan.",
            "Pumunta ako noong taginit.",
            "Pumunta kami noong tagaraw.",
            "Pumunta ako tuwing taglamig.",
            "Pumunta kami noong taggutom.",
            "Tuwing tagulan ay pumunta ako.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
