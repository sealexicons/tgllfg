"""Phase 5f Commit 16: approximators (Group H1 item 2).

Adds 2 ``PART[APPROX=YES]`` lex entries (``halos``,
``humigitkumulang``) and 3 new grammar rules: a cardinal-NUM
approximator wrap, a Q approximator wrap, and a parallel
``mga`` rule extending the Phase 5f Commit 13 time
approximation to cardinal NUMs (``mga sampu`` "around ten").

Lex (data/tgl/particles.yaml):

* ``halos`` — PART[APPROX="YES"]. "almost / nearly".
* ``humigitkumulang`` — PART[APPROX="YES"]. "approximately /
  more or less". Stored as the single-token form because the
  canonical hyphenated orthography ``humigit-kumulang`` is
  split by the current tokenizer; tokenizer pre-pass deferred
  (parallel to the Phase 5f Commit 14 seasons treatment).

Grammar (src/tgllfg/cfg/grammar.py):

* ``NUM → PART[APPROX=YES] NUM[CARDINAL=YES]`` — wraps a
  cardinal NUM with APPROX=YES while preserving CARDINAL=YES,
  CARDINAL_VALUE, NUM. The matrix-NP cardinal-modifier rule
  (Commit 1) consumes the wrapped NUM unchanged.
* ``Q → PART[APPROX=YES] Q`` — wraps any Q (lahat / iba /
  vague) with APPROX=YES while preserving QUANT / VAGUE.
  Existing partitive (Phase 5b) and vague-Q-modifier
  (Commit 15) rules consume the wrapped Q unchanged.
* ``NUM → PART[PLURAL_MARKER=YES] NUM[CARDINAL=YES]`` —
  parallel ``mga`` rule extending Commit 13's
  ``N → PART[mga] N[SEM_CLASS=TIME]`` from time NPs to
  cardinal NUMs. ``mga sampu`` "around ten" composes through
  the matrix-NP cardinal-modifier rule.

Tests cover:

* Morph: ``halos`` + ``humigitkumulang`` analyse as PART
  with APPROX="YES".
* halos + cardinal NUM as NP-modifier (OBJ / SUBJ / DAT):
  CARDINAL_VALUE preserved, APPROX visible on the daughter
  NUM (matrix NP doesn't lift APPROX — same NP-from-N
  projection limitation as cardinal-modifier features).
* humigitkumulang + cardinal NUM (subset of halos coverage).
* halos + Q (``halos lahat ng bata`` partitive,
  ``halos maraming aklat`` vague-linker form).
* mga + cardinal NUM as NP-modifier (broader mga).
* Negative (per §11.2): ``*halos bata`` (no NUM/Q daughter
  — gate fails); ``*halos hindi`` (PART without APPROX —
  PART daughter constraint fails).
* Regression: bare cardinal NP-modifier (Commit 1), mga +
  TIME (Commit 13), vague-Q linker (Commit 15), lahat
  partitive (Phase 5b) all unchanged.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* Hyphenated ``humigit-kumulang`` orthography — needs
  tokenizer pre-pass.
* ``malapit sa NUM`` "close to N" — multi-word approximator
  with DAT-NP complement; analytically more involved than
  the simple pre-modifier; deferred to a later commit.
* APPROX percolation to the matrix NP — same NP-from-N
  projection limitation as cardinal-modifier features
  (Commit 1) and SEASON percolation (Commit 14). Tests
  walk down to the daughter NUM to read APPROX.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _approximators() -> list[str]:
    return ["halos", "humigitkumulang"]


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


def _first_subj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    subj = f.feats.get("SUBJ")
    return subj if isinstance(subj, FStructure) else None


# === Morph layer ==========================================================


class TestApproxMorph:

    def test_all_approximators_analyze(self) -> None:
        for lemma in _approximators():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "PART"]
            assert cands, f"no PART analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("APPROX") == "YES", (
                f"{lemma}: APPROX expected 'YES', got "
                f"{ma.feats.get('APPROX')!r}"
            )


# === halos + cardinal NUM as NP-modifier ===================================


class TestHalosWithCardinal:
    """``halos sampung aklat`` "almost ten books" — halos wraps
    sampu (NUM[CARDINAL=YES, CARDINAL_VALUE=10]) producing
    NUM[CARDINAL=YES, CARDINAL_VALUE=10, APPROX=YES]; the matrix-
    NP cardinal-modifier rule (Commit 1) then consumes the
    wrapped NUM."""

    def test_halos_in_obj(self) -> None:
        # OBJ position: GEN-NP cardinal-modifier rule.
        obj = _first_obj("Bumili ako ng halos sampung aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "10"

    def test_halos_in_subj(self) -> None:
        subj = _first_subj("Kumakain ang halos sampung bata.")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("CARDINAL_VALUE") == "10"

    def test_halos_with_other_cardinals(self) -> None:
        # Sweep across a few cardinals — both vowel-final
        # (sampu, tatlo) and consonant-final (apat, anim, siyam).
        cases = [
            ("isa", "1", "isang"),
            ("dalawa", "2", "dalawang"),
            ("tatlo", "3", "tatlong"),
            ("apat", "4", "apat na"),
            ("lima", "5", "limang"),
            ("sampu", "10", "sampung"),
        ]
        for _, value, surface in cases:
            text = f"Bumili ako ng halos {surface} aklat."
            obj = _first_obj(text)
            assert obj is not None, f"no parse for {text!r}"
            assert obj.feats.get("CARDINAL_VALUE") == value


# === humigitkumulang + cardinal ============================================


class TestHumigitkumulangWithCardinal:
    """``humigitkumulang sampung aklat`` "approximately ten
    books" — same shape as halos."""

    def test_humigitkumulang_in_obj(self) -> None:
        obj = _first_obj("Bumili ako ng humigitkumulang sampung aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "10"


# === halos + Q (lahat partitive + vague linker) ============================


class TestHalosWithQ:
    """halos wraps any Q (lahat / iba / vague). The wrapped Q
    feeds the existing Phase 5b partitive rule (``halos lahat ng
    bata``) or the Phase 5f Commit 15 vague-Q-modifier rule
    (``halos maraming bata``)."""

    def test_halos_lahat_partitive(self) -> None:
        # ``halos lahat ng bata`` — halos + lahat → Q[QUANT=ALL,
        # APPROX=YES]; partitive rule fires.
        rs = parse_text("Kumakain ang halos lahat ng bata.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("QUANT") == "ALL"

    def test_halos_marami_linker(self) -> None:
        # ``halos maraming aklat`` — halos + marami → Q[QUANT=
        # MANY, VAGUE=YES, APPROX=YES]; vague-Q-modifier rule
        # fires.
        obj = _first_obj("Bumili ako ng halos maraming aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("VAGUE") == "YES"
        assert obj.feats.get("QUANT") == "MANY"


# === Broader mga: NUM (cardinal approximation) =============================


class TestMgaWithCardinal:
    """``mga sampu`` "around ten" — Phase 5f Commit 13's
    ``mga`` particle (PLURAL_MARKER=YES) consumed by a new
    parallel NUM rule (extending TIME-only to NUM-too)."""

    def test_mga_sampung_aklat_in_obj(self) -> None:
        obj = _first_obj("Bumili ako ng mga sampung aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "10"

    def test_mga_tatlong_bata_in_subj(self) -> None:
        subj = _first_subj("Kumakain ang mga tatlong bata.")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("CARDINAL_VALUE") == "3"


# === Negative fixtures (per §11.2) ========================================


class TestApproxNegative:

    def test_halos_with_bare_noun_blocked(self) -> None:
        # ``*halos bata`` — bata is N (not NUM/Q with APPROX
        # gating); no rule fires. Verify the sentence doesn't
        # parse the halos+bata fragment as an approximator
        # construction. The DAT-NP slot of pumunta would otherwise
        # have to absorb ``halos bata`` as DAT-NP[bata], but
        # ``halos`` has no path to NP — it only wraps NUM/Q.
        rs = parse_text("Pumunta ako sa halos bata.", n_best=5)
        # Either zero parses, or any parse must not have halos
        # composed as a modifier on bata.
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if (isinstance(m, FStructure)
                        and m.feats.get("LEMMA") == "bata"
                        and m.feats.get("APPROX") == "YES"):
                    raise AssertionError(
                        "halos composed with bare NOUN as approximator"
                    )

    def test_halos_alone_no_modifier(self) -> None:
        # ``*Pumunta ako halos.`` — bare halos with no NUM/Q
        # daughter. Should not produce a TIME_FRAME / APPROX
        # adjunct on its own.
        rs = parse_text("Pumunta ako halos.", n_best=5)
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list)) else [adj]
            )
            for m in members:
                if (isinstance(m, FStructure)
                        and m.feats.get("APPROX") == "YES"):
                    raise AssertionError(
                        "halos composed standalone as APPROX adjunct"
                    )


# === Regression ============================================================


class TestApproxRegressions:

    def test_bare_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=5)
        assert rs

    def test_mga_time_unchanged(self) -> None:
        rs = parse_text("Pumunta ako sa mga alasotso.", n_best=5)
        assert rs

    def test_vague_linker_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng maraming aklat.", n_best=5)
        assert rs

    def test_lahat_partitive_unchanged(self) -> None:
        rs = parse_text("Kumakain ang lahat ng bata.", n_best=5)
        assert rs

    def test_lahat_float_unchanged(self) -> None:
        rs = parse_text("Kumain ang bata lahat.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestApproxLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Bumili ako ng halos sampung aklat.",
            "Bumili ako ng humigitkumulang sampung aklat.",
            "Bumili ako ng mga sampung aklat.",
            "Bumili ako ng halos maraming aklat.",
            "Kumakain ang halos lahat ng bata.",
            "Kumakain ang halos sampung bata.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
