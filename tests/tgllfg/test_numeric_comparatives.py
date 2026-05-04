"""Phase 5f Commit 17: numeric comparatives (Group H1 item 3).

Adds 4 ``PART[COMP_PHRASE=...]`` lex entries (``higit``,
``kulang``, ``bababa``, ``hihigit``) and 4 new grammar frame
rules wrapping a NUM[CARDINAL=YES] standard via the DAT marker
``sa`` and modifying a NUM head with COMP feature:

  higit sa N         "more than N"        COMP=GT
  kulang sa N        "less than N"        COMP=LT
  hindi bababa sa N  "no less than N"     COMP=GE
  hindi hihigit sa N "no more than N"     COMP=LE

Per plan §11.1 Group H item 3: "These compose existing
constituents (negation hindi, the NEG-headed copula in
bababa / hihigit, DAT-NP sa NUM) plus a small frame rule for
the NUM modifier."

Lex (data/tgl/particles.yaml):

* ``higit``    — PART[COMP_PHRASE="HIGIT"]. "more (than)".
* ``kulang``   — PART[COMP_PHRASE="KULANG"]. "less (than)".
* ``bababa``   — PART[COMP_PHRASE="BABABA"]. Used in negated
                  context (``hindi bababa sa`` "at least").
                  Polysemous with the verb-form analysis (AV
                  CTPL of root ``baba`` "descend").
* ``hihigit``  — PART[COMP_PHRASE="HIHIGIT"]. Used in negated
                  context (``hindi hihigit sa`` "at most").
                  Polysemous with the verb-form analysis (AV
                  CTPL of root ``higit`` "exceed").

Grammar (src/tgllfg/cfg/grammar.py):

* 2 solo-frame rules (higit / kulang):
    NUM → PART[COMP_PHRASE] ADP[CASE=DAT] NUM[CARDINAL=YES]
* 2 negated-frame rules (hindi bababa / hindi hihigit):
    NUM → PART[POLARITY=NEG] PART[COMP_PHRASE]
          ADP[CASE=DAT] NUM[CARDINAL=YES]

Each rule sets ``COMP`` to GT / LT / GE / LE on the wrapped
NUM. Output is NUM (preserving CARDINAL=YES, CARDINAL_VALUE,
NUM=PL/SG via shared-fstruct ``(↑) = ↓N`` on the inner NUM
daughter), so the matrix-NP cardinal-modifier rule (Phase 5f
Commit 1) consumes the wrapped NUM unchanged.

Tests cover:

* Morph: each comparator analyses with pos=PART and the right
  COMP_PHRASE; bababa / hihigit additionally retain their
  generated VERB analyses (polysemy verified — different POS
  coexists; same-POS would collapse per the analyzer's
  duplicate-collapse semantics).
* Solo comparators: ``higit sa <CARD>ng aklat`` and
  ``kulang sa <CARD>ng aklat`` in OBJ / SUBJ / DAT positions,
  CARDINAL_VALUE preserved on the matrix NP. Sweep across a
  few cardinals (sampu, tatlo, apat — both vowel-final ``-ng``
  and consonant-final ``na`` linker variants).
* Negated comparators: ``hindi bababa sa <CARD>ng aklat`` and
  ``hindi hihigit sa <CARD>ng aklat``, CARDINAL_VALUE
  preserved.
* Negative (per §11.2): ``*higit sampung aklat`` (missing
  ``sa``); ``*higit sa bata`` (head is N, not NUM[CARDINAL=
  YES]); ``*hindi bababa sampung aklat`` (missing ``sa``).
* Regression: ``Bababa ang bata.`` (bababa as verb in normal
  clause) still composes via the existing intransitive AV
  rule — polysemy doesn't break the verb path. Bare cardinal
  NP-modifier (Commit 1), halos approximator (Commit 16),
  vague-Q linker (Commit 15) all unchanged.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* Gradable / scalar ``mas`` (without numeric reference) —
  Phase 5h (gradable adjective comparison).
* Comparators on Q heads (``higit sa kalahati`` "more than
  half") — extending the frame rules to admit FRACTION /
  PERCENTAGE / MULTIPLIER daughters; additive but out of
  Group H1 scope.
* COMP percolation to the matrix NP — same NP-from-N
  projection limitation as APPROX (Commit 16) and CARDINAL_-
  VALUE (Commit 1). Tests walk down to verify CARDINAL_VALUE
  preservation; COMP is set on the inner NUM and rides
  unchanged.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _solo_comparators() -> list[tuple[str, str]]:
    return [("higit", "GT"), ("kulang", "LT")]


def _negated_comparators() -> list[tuple[str, str]]:
    return [("bababa", "GE"), ("hihigit", "LE")]


def _all_comparators() -> list[str]:
    return [c for c, _ in _solo_comparators()] + [
        c for c, _ in _negated_comparators()
    ]


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


class TestComparatorMorph:

    def test_higit_kulang_part_only(self) -> None:
        # ``higit`` and ``kulang`` are added as PART entries with
        # COMP_PHRASE; their bare-root verb analyses don't surface
        # as finite forms, so PART is the sole analysis.
        for lemma, _ in _solo_comparators():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "PART"]
            assert cands, f"no PART analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("COMP_PHRASE") == lemma.upper(), (
                f"{lemma}: COMP_PHRASE expected {lemma.upper()!r}, "
                f"got {ma.feats.get('COMP_PHRASE')!r}"
            )

    def test_bababa_hihigit_polysemy(self) -> None:
        # ``bababa`` and ``hihigit`` are generated by the paradigm
        # engine as AV CTPL verb forms (of roots ``baba`` and
        # ``higit`` respectively) AND added as PART entries here.
        # Both analyses must coexist (different POS — same-POS
        # would collapse per the morph analyzer's duplicate-
        # collapse semantics).
        for lemma, _ in _negated_comparators():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            poses = {c.pos for c in ml[0]}
            assert "PART" in poses, f"{lemma}: no PART analysis"
            assert "VERB" in poses, (
                f"{lemma}: no VERB analysis (polysemy regression)"
            )
            part = next(c for c in ml[0] if c.pos == "PART")
            assert part.feats.get("COMP_PHRASE") == lemma.upper()


# === Solo comparators (higit / kulang) ====================================


class TestSoloComparators:
    """``higit sa N`` / ``kulang sa N`` — solo frame rule:
    PART + ADP[DAT] + NUM[CARDINAL=YES]. Wrapped NUM feeds the
    matrix-NP cardinal-modifier rule (Commit 1)."""

    def test_higit_in_obj(self) -> None:
        obj = _first_obj("Bumili ako ng higit sa sampung aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "10"
        assert obj.feats.get("CASE") == "GEN"

    def test_kulang_in_obj(self) -> None:
        obj = _first_obj("Bumili ako ng kulang sa sampung aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "10"

    def test_higit_in_subj(self) -> None:
        subj = _first_subj("Kumakain ang higit sa sampung bata.")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("CARDINAL_VALUE") == "10"

    def test_higit_in_dat(self) -> None:
        # ``Pumunta ako sa higit sa sampung kuwarto.`` "I went to
        # more than ten rooms." — DAT slot of intransitive routes
        # to ADJUNCT.
        adj = _adjunct_with_lemma(
            "Pumunta ako sa higit sa sampung kuwarto.", "kuwarto"
        )
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"
        assert adj.feats.get("CARDINAL_VALUE") == "10"

    def test_higit_kulang_with_various_cardinals(self) -> None:
        # Sweep across a few cardinals — both vowel-final and
        # consonant-final linker variants.
        cases = [
            ("isa", "1", "isang"),
            ("tatlo", "3", "tatlong"),
            ("apat", "4", "apat na"),
            ("anim", "6", "anim na"),
            ("sampu", "10", "sampung"),
        ]
        for lemma, _ in _solo_comparators():
            for _, value, surface in cases:
                text = f"Bumili ako ng {lemma} sa {surface} aklat."
                obj = _first_obj(text)
                assert obj is not None, f"no parse for {text!r}"
                assert obj.feats.get("CARDINAL_VALUE") == value


# === Negated comparators (hindi bababa / hindi hihigit) ===================


class TestNegatedComparators:
    """``hindi bababa sa N`` "no less than N" / ``hindi hihigit
    sa N`` "no more than N" — 4-daughter frame rule:
    PART[POLARITY=NEG] + PART + ADP[DAT] + NUM[CARDINAL=YES]."""

    def test_hindi_bababa_in_obj(self) -> None:
        obj = _first_obj("Bumili ako ng hindi bababa sa sampung aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "10"

    def test_hindi_hihigit_in_obj(self) -> None:
        obj = _first_obj("Bumili ako ng hindi hihigit sa sampung aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CARDINAL_VALUE") == "10"

    def test_hindi_bababa_in_subj(self) -> None:
        subj = _first_subj(
            "Kumakain ang hindi bababa sa sampung bata."
        )
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("CARDINAL_VALUE") == "10"

    def test_hindi_hihigit_with_cardinals(self) -> None:
        cases = [
            ("tatlo", "3", "tatlong"),
            ("apat", "4", "apat na"),
            ("sampu", "10", "sampung"),
        ]
        for _, value, surface in cases:
            text = f"Bumili ako ng hindi hihigit sa {surface} aklat."
            obj = _first_obj(text)
            assert obj is not None, f"no parse for {text!r}"
            assert obj.feats.get("CARDINAL_VALUE") == value


# === Negative fixtures (per §11.2) ========================================


class TestComparatorNegative:

    def test_higit_without_sa_blocked(self) -> None:
        # ``*higit sampung aklat`` — frame rule requires ADP[CASE=
        # DAT] between the comparator and the NUM standard.
        rs = parse_text("Bumili ako ng higit sampung aklat.", n_best=10)
        # The standalone path (no comparator wrap) shouldn't either:
        # `higit` as PART without a matching frame doesn't form a
        # NUM, so the cardinal-modifier rule has no NUM[CARDINAL=
        # YES] daughter to consume. Expect zero parses.
        assert rs == [], (
            f"higit-without-sa not blocked: got {len(rs)} parses"
        )

    def test_higit_with_non_cardinal_blocked(self) -> None:
        # ``*higit sa bata`` — bata is N (not NUM[CARDINAL=YES]).
        # The frame rule's daughter constraint fails.
        rs = parse_text("Bumili ako ng higit sa bata.", n_best=10)
        # The standalone `sa bata` could parse as a DAT-NP, but
        # there's no path from `higit` + NP[DAT] + N to a matrix
        # OBJ (the cardinal-modifier rule needs NUM[CARDINAL=YES]
        # not Q / NP). Expect zero parses.
        assert rs == [], (
            f"higit-with-non-cardinal not blocked: got {len(rs)} parses"
        )

    def test_hindi_bababa_without_sa_blocked(self) -> None:
        # ``*hindi bababa sampung aklat`` — negated frame rule
        # requires ADP[CASE=DAT].
        rs = parse_text(
            "Bumili ako ng hindi bababa sampung aklat.", n_best=10
        )
        # The verb-form analysis of bababa might still let some
        # other path compose; verify no comparator wrap on a NUM
        # surfaces.
        for _, f, _, _ in rs:
            obj = f.feats.get("OBJ")
            if (isinstance(obj, FStructure)
                    and obj.feats.get("CARDINAL_VALUE") == "10"):
                # If OBJ surfaced with CV=10 and the comparator
                # composed, that's the regression. Acceptable: zero
                # parses, or parses where OBJ doesn't carry CV=10.
                raise AssertionError(
                    "hindi-bababa-without-sa composed comparator wrap"
                )


# === Regression ===========================================================


class TestComparatorRegressions:

    def test_bababa_as_verb_unchanged(self) -> None:
        # ``Bababa ang bata.`` "The child will descend." — bababa
        # as the AV CTPL verb form. The PART analysis added in
        # this commit shouldn't break the verb path.
        rs = parse_text("Bababa ang bata.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"

    def test_bare_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=5)
        assert rs

    def test_consonant_final_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng apat na aklat.", n_best=5)
        assert rs

    def test_halos_approximator_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng halos sampung aklat.", n_best=5)
        assert rs

    def test_vague_linker_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng maraming aklat.", n_best=5)
        assert rs

    def test_lahat_partitive_unchanged(self) -> None:
        rs = parse_text("Kumakain ang lahat ng bata.", n_best=5)
        assert rs

    def test_negation_in_normal_clause_unchanged(self) -> None:
        # ``Hindi kumain ang bata.`` "The child didn't eat." —
        # standard clause-level negation. The comparator addition
        # of bababa / hihigit shouldn't disturb this.
        rs = parse_text("Hindi kumain ang bata.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestComparatorLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Bumili ako ng higit sa sampung aklat.",
            "Bumili ako ng kulang sa sampung aklat.",
            "Bumili ako ng hindi bababa sa sampung aklat.",
            "Bumili ako ng hindi hihigit sa sampung aklat.",
            "Kumakain ang higit sa sampung bata.",
            "Bumili ako ng higit sa apat na aklat.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
