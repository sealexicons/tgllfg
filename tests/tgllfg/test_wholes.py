"""Phase 5f Commit 22: wholes ``buo`` / ``buong`` (Group H3 item 8).

Adds 1 ``Q[WHOLE="YES", QUANT=WHOLE]`` lex entry (``buo``) and
8 new grammar rules — 6 case-marked variants (3 cases × 2 linker
variants) plus 2 bare-NOM variants. Existing Phase 5b
``Q + NP[GEN]`` partitive rules gain ``¬ (↓2 WHOLE)`` so wholes
only take the linker-N form. The bound ``-ng`` linker form
``buong`` is produced by the existing Phase 4 split_linker_ng
pre-pass once ``buo`` is a known surface.

Lex (data/tgl/particles.yaml):

* ``buo`` — Q[QUANT=WHOLE, WHOLE="YES"]. Citation form;
  vowel-final, the bound ``-ng`` linker form ``buong``
  fires automatically via split_linker_ng.

POS choice — Q rather than ADJ — reflects:

* Semantic role: totality quantifier (quantifies over the
  entirety of an entity), not a property like color or size.
* Plan grouping: §11.1 Group H quantifiers.
* Linker-modifier distribution matches the established Q
  template (Phase 5f Commits 15 / 20 / 21).
* Predicate-Adj path doesn't exist yet (Phase 5g).

Grammar (src/tgllfg/cfg/nominal.py):

* 6 case-marked NP rules:
    NP[CASE=X] → DET/ADP[CASE=X] Q[WHOLE=YES] PART[LINK] N
  (3 cases × 2 linker variants).
* 2 bare-NOM NP rules:
    NP[CASE=NOM] → Q[WHOLE=YES] PART[LINK] N
  (2 linker variants).

The existing Phase 5b ``Q + NP[GEN]`` partitive rules gain
``¬ (↓2 WHOLE)`` (parallel to the existing VAGUE / UNIV /
DISTRIB_POSS gates).

Tests cover:

* Morph: ``buo`` analyses as Q with WHOLE="YES" + QUANT=WHOLE.
* Case-marked NP composition (NOM SUBJ, GEN OBJ, DAT ADJUNCT):
  ``ang buong bata`` (NOM), ``ng buong araw`` (GEN), ``sa
  buong pamilya`` (DAT). Matrix NP rides WHOLE="YES" +
  QUANT=WHOLE + LEMMA from N.
* Bare-NOM composition with ay-fronting: ``Buong pamilya ay
  kumakain.``
* Negatives (per §11.2): ``*ang buong buong bata`` (chained),
  ``*ang buo ng bata`` (WHOLE in GEN-NP partitive blocked by
  new gate).
* Regression: lahat partitive, lahat float, vague linker,
  universal bawat, distributive-possessive, cardinal, ordinal
  all unchanged.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* Predicative use (``Buo ang bata.`` "The child is whole /
  intact") — would parse via a future predicate-Q rule.
* Floated ``buo`` (``Kumain ang bata buo``) — mechanically
  fires via the existing Phase 4 §7.8 ``S → S Q`` float rule
  but not idiomatic for ``buo``.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


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


class TestWholeMorph:

    def test_buo_analyzes(self) -> None:
        toks = tokenize("buo")
        ml = analyze_tokens(toks)
        cands = [c for c in ml[0] if c.pos == "Q"]
        assert cands, "no Q analysis for buo"
        ma = cands[0]
        assert ma.feats.get("WHOLE") == "YES"
        assert ma.feats.get("QUANT") == "WHOLE"


# === Case-marked NP composition ===========================================


class TestWholeCaseMarked:
    """``ang buong bata`` (NOM SUBJ), ``ng buong araw`` (GEN
    OBJ), ``sa buong pamilya`` (DAT ADJ). The case-marked rule
    fires; matrix NP carries WHOLE=YES + QUANT=WHOLE + LEMMA
    from N."""

    def test_buong_in_nom_subj(self) -> None:
        subj = _first_subj("Kumakain ang buong bata.")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("WHOLE") == "YES"
        assert subj.feats.get("QUANT") == "WHOLE"

    def test_buong_in_gen_obj(self) -> None:
        obj = _first_obj("Kumain ako ng buong araw.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "araw"
        assert obj.feats.get("CASE") == "GEN"
        assert obj.feats.get("WHOLE") == "YES"
        assert obj.feats.get("QUANT") == "WHOLE"

    def test_buong_in_dat_adjunct(self) -> None:
        adj = _adjunct_with_lemma(
            "Pumunta ako sa buong pamilya.", "pamilya"
        )
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"
        assert adj.feats.get("WHOLE") == "YES"
        assert adj.feats.get("QUANT") == "WHOLE"


# === Bare-NOM composition =================================================


class TestWholeBareNom:
    """``Buong pamilya ay kumakain.`` "The whole family eats."
    — bare-NOM rule (Q + PART[LINK] + N → NP[CASE=NOM]) fires;
    the NP slots into the ay-inversion TOPIC position."""

    def test_buong_pamilya_ay_fronted(self) -> None:
        rs = parse_text("Buong pamilya ay kumakain.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        topic = f.feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "pamilya"
        assert topic.feats.get("WHOLE") == "YES"
        assert topic.feats.get("QUANT") == "WHOLE"

    def test_buong_bata_ay_fronted(self) -> None:
        rs = parse_text("Buong bata ay kumakain.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        topic = f.feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        assert topic.feats.get("WHOLE") == "YES"


# === Negative fixtures (per §11.2) ========================================


class TestWholeNegative:

    def test_chained_whole_blocked(self) -> None:
        # ``*ang buong buong bata`` — chained wholes blocked by
        # ``¬ (↓4 WHOLE)`` constraint.
        rs = parse_text("Kumakain ang buong buong bata.", n_best=10)
        assert rs == [], (
            f"chained wholes not blocked: got {len(rs)} parses"
        )

    def test_whole_partitive_blocked(self) -> None:
        # ``*ang buo ng bata`` — WHOLE in GEN-NP partitive
        # blocked by new ``¬ (↓2 WHOLE)`` gate on the existing
        # Phase 5b partitive rules.
        rs = parse_text("Kumakain ang buo ng bata.", n_best=10)
        assert rs == [], (
            f"WHOLE partitive not blocked: got {len(rs)} parses"
        )


# === Regression ===========================================================


class TestWholeRegressions:

    def test_lahat_partitive_unchanged(self) -> None:
        rs = parse_text("Kumakain ang lahat ng bata.", n_best=5)
        assert rs

    def test_lahat_float_unchanged(self) -> None:
        rs = parse_text("Kumain ang bata lahat.", n_best=5)
        assert rs

    def test_vague_linker_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng maraming aklat.", n_best=5)
        assert rs

    def test_universal_unchanged(self) -> None:
        rs = parse_text("Kumakain ang bawat bata.", n_best=5)
        assert rs

    def test_distrib_poss_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng kanyakanyang aklat.", n_best=5
        )
        assert rs

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=5)
        assert rs

    def test_ordinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng unang aklat.", n_best=5)
        assert rs

    def test_collective_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng isang dosenang itlog.", n_best=5
        )
        assert rs


# === LMT diagnostics clean ================================================


class TestWholeLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumakain ang buong bata.",
            "Kumain ako ng buong araw.",
            "Pumunta ako sa buong pamilya.",
            "Buong pamilya ay kumakain.",
            "Buong bata ay kumakain.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
