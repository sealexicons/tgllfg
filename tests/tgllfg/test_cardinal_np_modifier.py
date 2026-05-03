"""Phase 5f Commit 1: native cardinal NP-internal modifier (1-10).

Adds cardinals 1-10 as NP-internal modifiers via the linker
(``isang bata`` "one child", ``tatlong libro`` "three books").
The cardinal precedes the head N via either the bound ``-ng``
linker (after vowel-final cardinals: isa, dalawa, tatlo, lima,
pito, walo, sampu) or the standalone ``na`` linker (after
consonant-final cardinals: apat, anim, siyam).

The cardinal contributes ``NUM`` (SG for isa, PL for 2-10) and
``CARDINAL_VALUE`` to the matrix N's f-structure; ``PRED`` and
``LEMMA`` percolate from the head N. The matrix N feeds existing
NP rules (``NP[CASE=X] → DET/ADP[CASE=X] N``) so case marking
applies uniformly: ``ang tatlong libro``, ``ng dalawang isda``,
``sa apat na bata``.

This commit is foundational: items 2-7 of Group A (Spanish
cardinals, compound cardinals, predicative cardinals, ratios,
decimals, percentages) and Groups B/C/E/F/H all consume the
cardinal NP-modifier rule once it lands.

Tests cover:

* Morph: each cardinal analyses with pos=NUM and the right
  CARDINAL_VALUE / NUM features.
* Linker split: bound ``-ng`` splits off vowel-final cardinals;
  consonant-final ones use the standalone ``na`` particle.
* All 10 cardinals × bata in OBJ position (sweep test).
* Cardinal-modified NP in OBJ position
  (``Kumain ako ng tatlong isda``).
* Cardinal-modified NP in SUBJ position
  (``Kumakanta ang dalawang bata``).
* Cardinal-modified NP in DAT position
  (``Pumunta ako sa tatlong kuwarto``).
* Negative: ``*isa bata`` (no linker between cardinal and N).
* Negative: ``*tatlong dalawang bata`` (chained cardinals;
  blocked by ``¬ (↓3 CARDINAL_VALUE)`` constraint).
* Regression: bare-N and dem-modified-N parses unaffected.
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import split_linker_ng, tokenize


def _all_cards() -> list[tuple[str, str, str, str]]:
    """Yield (lemma, value, num, surface_with_link)."""
    return [
        ("isa",    "1",  "SG", "isang"),
        ("dalawa", "2",  "PL", "dalawang"),
        ("tatlo",  "3",  "PL", "tatlong"),
        ("apat",   "4",  "PL", "apat na"),
        ("lima",   "5",  "PL", "limang"),
        ("anim",   "6",  "PL", "anim na"),
        ("pito",   "7",  "PL", "pitong"),
        ("walo",   "8",  "PL", "walong"),
        ("siyam",  "9",  "PL", "siyam na"),
        ("sampu",  "10", "PL", "sampung"),
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


# === Morph layer ==========================================================


class TestCardinalMorph:
    """Each cardinal lemma analyses with pos=NUM and the right
    CARDINAL_VALUE / NUM features."""

    def test_all_cardinals_analyze(self) -> None:
        for lemma, value, num, _ in _all_cards():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = ml[0]
            num_cands = [c for c in cands if c.pos == "NUM"]
            assert num_cands, f"no NUM analysis for {lemma}"
            ma = num_cands[0]
            assert ma.feats.get("CARDINAL") == "YES", f"{lemma}: CARDINAL missing"
            assert ma.feats.get("CARDINAL_VALUE") == value, (
                f"{lemma}: CARDINAL_VALUE expected {value!r}, got "
                f"{ma.feats.get('CARDINAL_VALUE')!r}"
            )
            assert ma.feats.get("NUM") == num, (
                f"{lemma}: NUM expected {num!r}, got {ma.feats.get('NUM')!r}"
            )


class TestCardinalLinkerSplit:
    """Bound -ng splits off vowel-final cardinals; consonant-final
    ones use the standalone na particle."""

    def test_isang_splits(self) -> None:
        toks = tokenize("isang bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["isa", "-ng", "bata"]

    def test_tatlong_splits(self) -> None:
        toks = tokenize("tatlong bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["tatlo", "-ng", "bata"]

    def test_sampung_splits(self) -> None:
        toks = tokenize("sampung bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["sampu", "-ng", "bata"]

    def test_apat_does_not_split(self) -> None:
        # Consonant-final cardinal; nothing to split.
        toks = tokenize("apat na bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["apat", "na", "bata"]

    def test_anim_does_not_split(self) -> None:
        toks = tokenize("anim na bata")
        toks = split_linker_ng(toks)
        assert [t.norm for t in toks] == ["anim", "na", "bata"]


# === Cardinal NP-modifier in OBJ position =================================


class TestCardinalAsObj:
    """The OBJ of a transitive AV verb is a GEN-NP; cardinal
    modifies the head N."""

    def test_kumain_ng_tatlong_isda(self) -> None:
        f = _first_obj("Kumain ako ng tatlong isda.")
        assert f is not None, "no parse"
        assert f.feats.get("LEMMA") == "isda"
        assert f.feats.get("CASE") == "GEN"
        assert f.feats.get("CARDINAL_VALUE") == "3"
        assert f.feats.get("NUM") == "PL"

    def test_kumain_ng_isang_isda(self) -> None:
        f = _first_obj("Kumain ako ng isang isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "1"
        assert f.feats.get("NUM") == "SG"

    def test_kumain_ng_apat_na_isda(self) -> None:
        # Consonant-final cardinal with standalone na linker.
        f = _first_obj("Kumain ako ng apat na isda.")
        assert f is not None
        assert f.feats.get("CARDINAL_VALUE") == "4"
        assert f.feats.get("NUM") == "PL"


# === Cardinal NP-modifier in SUBJ position ================================


class TestCardinalAsSubj:
    """The SUBJ of an intransitive AV verb is a NOM-NP."""

    def test_kumakanta_ang_dalawang_bata(self) -> None:
        subj = _first_subj("Kumakanta ang dalawang bata.")
        assert subj is not None, "no parse"
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("CARDINAL_VALUE") == "2"
        assert subj.feats.get("NUM") == "PL"

    def test_tumakbo_ang_apat_na_aso(self) -> None:
        # ``Tumakbo ang apat na aso.`` "Four dogs ran." — consonant-
        # final cardinal in SUBJ.
        subj = _first_subj("Tumakbo ang apat na aso.")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "aso"
        assert subj.feats.get("CARDINAL_VALUE") == "4"


# === All 10 cardinals — sweep =============================================


class TestAllCardinalsSweep:
    """Each of the 10 cardinals composes with bata in OBJ position."""

    def test_each_cardinal_in_obj(self) -> None:
        for lemma, value, num, surface_with_link in _all_cards():
            text = f"Kumain ako ng {surface_with_link} bata."
            f = _first_obj(text)
            assert f is not None, f"no parse for {text!r}"
            assert f.feats.get("CARDINAL_VALUE") == value, (
                f"{lemma}: expected CARDINAL_VALUE={value!r}, got "
                f"{f.feats.get('CARDINAL_VALUE')!r} for {text!r}"
            )
            assert f.feats.get("NUM") == num, (
                f"{lemma}: expected NUM={num!r}, got "
                f"{f.feats.get('NUM')!r} for {text!r}"
            )
            assert f.feats.get("LEMMA") == "bata"


# === Cardinal in DAT position =============================================


class TestCardinalInDat:
    """DAT-marked cardinal-modified NP appears as a DAT adjunct
    (the LMT classifier defaults sa-NPs to ADJ today; see plan
    §12.4 / docs/diagnostics.md §3.3)."""

    def test_pumunta_sa_tatlong_kuwarto(self) -> None:
        # ``Pumunta ako sa tatlong kuwarto.`` "I went to three rooms."
        # DAT NPs surface as members of the matrix ADJUNCT set
        # (the LMT classifier defaults sa-NPs to adjunct; see
        # docs/diagnostics.md §3.3 and plan §12.4).
        rs = parse_text("Pumunta ako sa tatlong kuwarto.", n_best=10)
        assert rs, "no parse"
        found = False
        for _, f, _, _ in rs:
            adj = f.feats.get("ADJUNCT")
            if adj is None:
                continue
            members = (
                list(adj) if isinstance(adj, (set, frozenset, list))
                else [adj]
            )
            for m in members:
                if (isinstance(m, FStructure)
                        and m.feats.get("CARDINAL_VALUE") == "3"
                        and m.feats.get("LEMMA") == "kuwarto"):
                    found = True
                    break
            if found:
                break
        assert found, "no parse with cardinal-modified DAT NP"


# === Negative fixtures (per Phase 5f §11.2 convention) ====================


class TestCardinalNegative:
    """Per Phase 5f §11.2 negative-fixture convention: each commit
    ships ≥1 starred ungrammatical surface asserted not to parse
    (or to parse only with blocking diagnostics)."""

    def test_no_linker_fails(self) -> None:
        # ``*Kumain ako ng isa bata.`` — missing the linker between
        # cardinal and N. The cardinal-NP-modifier rule requires
        # PART[LINK=...]; without it, no rule consumes the
        # ``isa bata`` sequence as an N.
        rs = parse_text("Kumain ako ng isa bata.", n_best=5)
        # Either no parse, or all parses have blocking diagnostics.
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), (
                "ungrammatical *isa bata produced a non-blocking parse: "
                f"{[ (f.feats.get('PRED'), f.feats.get('OBJ')) for _, f, _, _ in rs ]}"
            )

    def test_chained_cardinals_blocked(self) -> None:
        # ``*Kumain ako ng tatlong dalawang bata.`` — a single N
        # cannot carry two cardinal modifiers. Blocked by the
        # constraint ``¬ (↓3 CARDINAL_VALUE)`` on the cardinal
        # NP-modifier rule.
        rs = parse_text("Kumain ako ng tatlong dalawang bata.", n_best=5)
        if rs:
            assert all(
                any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), "chained cardinals produced a non-blocking parse"


# === Regressions ==========================================================


class TestCardinalRegressions:
    """Existing constructions are unaffected by the new cardinal rule."""

    def test_bare_n_still_parses(self) -> None:
        # ``Kumain ang bata.`` — bare N, no cardinal.
        rs = parse_text("Kumain ang bata.")
        assert rs
        f = rs[0][1]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("CARDINAL_VALUE") is None

    def test_dem_modified_n_still_parses(self) -> None:
        # ``Kumain itong bata.`` — pre-modifier dem from
        # Phase 5e Commit 16; cardinal rule is parallel but
        # at N level, not NP level.
        rs = parse_text("Kumain itong bata.")
        assert rs
        f = rs[0][1]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("DEIXIS") == "PROX"

    def test_av_transitive_unchanged(self) -> None:
        # Plain AV transitive without any cardinal — regression
        # check against the new rule introducing parse changes
        # to existing constructions.
        rs = parse_text("Kumain ang bata ng isda.")
        assert rs
        f = rs[0][1]
        assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"


# === LMT diagnostics clean ================================================


class TestCardinalLmtClean:
    """Each cardinal-modified surface produces at least one parse
    with no blocking diagnostics."""

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumain ako ng isang isda.",
            "Kumain ako ng dalawang isda.",
            "Kumain ako ng tatlong isda.",
            "Kumain ako ng apat na isda.",
            "Kumain ako ng anim na isda.",
            "Kumain ako ng siyam na isda.",
            "Kumain ako ng sampung isda.",
            "Kumakanta ang dalawang bata.",
            "Tumakbo ang apat na aso.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
