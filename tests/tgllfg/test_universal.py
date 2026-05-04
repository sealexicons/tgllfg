"""Phase 5f Commit 20: universal ``bawat`` / ``kada`` (Group H2 item 6).

Adds 2 ``Q[UNIV="YES"]`` lex entries (``bawat``, ``kada``) and 4
new grammar rules (3 case-marked + 1 bare-NOM) for the
universal-quantifier construction. Closes Group H2.

Lex (data/tgl/particles.yaml):

* ``bawat`` — Q[QUANT=EVERY, UNIV="YES"]. The native universal
  quantifier (S&O 1972 §4.7).
* ``kada``  — Q[QUANT=EVERY, UNIV="YES"]. Spanish-borrowed
  colloquial synonym of ``bawat``. Same f-structure shape.

Grammar (src/tgllfg/cfg/grammar.py):

* 3 case-marked NP rules:
    NP[CASE=X] → DET/ADP[CASE=X] Q[UNIV=YES] N
  (3 cases: NOM, GEN, DAT).
* 1 bare-NOM NP rule:
    NP[CASE=NOM] → Q[UNIV=YES] N
  (covers ``Bawat bata ay kumakain.`` style surfaces where
  bawat itself functions as the determiner-equivalent.)

The existing Phase 5b ``Q + NP[GEN]`` partitive rules gain
``¬ (↓2 UNIV)`` so universals only take the bare-N form.

This is the third Q-distribution Phase 5f has now covered:

  Q + NP[GEN]              partitive (lahat / iba; Phase 5b)
  Q + PART[LINK] + N        vague-Q-modifier (Phase 5f Commit 15)
  Q + N                    universal (this commit)

Tests cover:

* Morph: bawat + kada analyse as Q with UNIV="YES" + QUANT=EVERY.
* Case-marked NP composition (NOM / GEN / DAT): ``ang bawat
  bata`` (NOM SUBJ), ``ng bawat aklat`` (GEN OBJ), ``sa bawat
  bata`` (DAT ADJ).
* Bare-NOM composition: ``Bawat bata ay kumakain.`` (subject
  fronted via ay-inversion).
* Both lex items: ``ang bawat bata`` and ``ang kada bata``.
* Negatives (per §11.2): ``*ang bawat kada bata`` (chained
  universals blocked), ``*ang bawat ng bata`` (universal in
  GEN-NP partitive blocked by the new gate).
* Regression: lahat partitive, lahat float, vague linker,
  cardinal NP-modifier, ordinal, distributive all unchanged.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* ``bawat isa`` / ``bawat dalawa`` (Q + NUM as quantifier
  over a number) — needs a parallel Q + NUM rule.
* Q-quantification over a non-N head (``bawat sa kanila``
  "every of them") — additive but structurally distinct.
* Floated universals — not idiomatic for ``bawat``; the
  existing Phase 4 §7.8 ``S → S Q`` float rule would fire
  mechanically but the result isn't natural.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _universals() -> list[str]:
    return ["bawat", "kada"]


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


class TestUniversalMorph:

    def test_all_universals_analyze(self) -> None:
        for lemma in _universals():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "Q"]
            assert cands, f"no Q analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("UNIV") == "YES", (
                f"{lemma}: UNIV expected 'YES', got "
                f"{ma.feats.get('UNIV')!r}"
            )
            assert ma.feats.get("QUANT") == "EVERY"


# === Case-marked NP composition ===========================================


class TestUniversalCaseMarked:
    """``ang bawat bata`` (NOM), ``ng bawat aklat`` (GEN), ``sa
    bawat bata`` (DAT). The case-marked rule
    ``NP[CASE=X] → DET/ADP[CASE=X] Q[UNIV=YES] N`` fires;
    matrix NP carries QUANT=EVERY + UNIV=YES + LEMMA from N."""

    def test_bawat_in_nom_subj(self) -> None:
        subj = _first_subj("Kumakain ang bawat bata.")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("QUANT") == "EVERY"
        assert subj.feats.get("UNIV") == "YES"

    def test_bawat_in_gen_obj(self) -> None:
        obj = _first_obj("Kumain ako ng bawat aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CASE") == "GEN"
        assert obj.feats.get("QUANT") == "EVERY"
        assert obj.feats.get("UNIV") == "YES"

    def test_bawat_in_dat_adjunct(self) -> None:
        # Intransitive ``pumunta`` routes the DAT-NP to ADJUNCT.
        adj = _adjunct_with_lemma("Pumunta ako sa bawat bata.", "bata")
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"
        assert adj.feats.get("QUANT") == "EVERY"
        assert adj.feats.get("UNIV") == "YES"

    def test_kada_in_nom_subj(self) -> None:
        # kada is the colloquial Spanish-borrowed synonym; same
        # f-structure shape.
        subj = _first_subj("Kumakain ang kada bata.")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "bata"
        assert subj.feats.get("QUANT") == "EVERY"


# === Bare-NOM composition =================================================


class TestUniversalBareNom:
    """``Bawat bata ay kumakain.`` "Every child eats." — bawat
    standalone in the SUBJ slot, ay-fronted to TOPIC. The bare-
    NOM rule (``NP[CASE=NOM] → Q[UNIV=YES] N``) fires."""

    def test_bawat_bata_ay_fronted(self) -> None:
        rs = parse_text("Bawat bata ay kumakain.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        topic = f.feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bata"
        assert topic.feats.get("QUANT") == "EVERY"
        assert topic.feats.get("UNIV") == "YES"

    def test_kada_bata_ay_fronted(self) -> None:
        rs = parse_text("Kada bata ay kumakain.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        topic = f.feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "bata"
        assert topic.feats.get("QUANT") == "EVERY"


# === Negative fixtures (per §11.2) ========================================


class TestUniversalNegative:

    def test_chained_universals_blocked(self) -> None:
        # ``*ang bawat kada bata`` — chained universals blocked
        # by ``¬ (↓3 UNIV)`` on the case-marked rule (parallel
        # to the cardinal rule's ``¬ (↓4 CARDINAL_VALUE)``).
        rs = parse_text("Kumakain ang bawat kada bata.", n_best=10)
        assert rs == [], (
            f"chained universals not blocked: got {len(rs)} parses"
        )

    def test_universal_partitive_blocked(self) -> None:
        # ``*ang bawat ng bata`` — universal in GEN-NP partitive
        # blocked by the new ``¬ (↓2 UNIV)`` gate on the
        # existing Phase 5b partitive rule.
        rs = parse_text("Kumakain ang bawat ng bata.", n_best=10)
        assert rs == [], (
            f"universal-Q partitive not blocked: got {len(rs)} parses"
        )


# === Regression ============================================================


class TestUniversalRegressions:

    def test_lahat_partitive_unchanged(self) -> None:
        rs = parse_text("Kumakain ang lahat ng bata.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("QUANT") == "ALL"

    def test_lahat_float_unchanged(self) -> None:
        rs = parse_text("Kumain ang bata lahat.", n_best=5)
        assert rs

    def test_vague_linker_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng maraming aklat.", n_best=5)
        assert rs

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=5)
        assert rs

    def test_ordinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng unang aklat.", n_best=5)
        assert rs

    def test_distributive_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tigisang aklat.", n_best=5)
        assert rs

    def test_collective_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng isang dosenang itlog.", n_best=5
        )
        assert rs


# === LMT diagnostics clean ================================================


class TestUniversalLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Kumakain ang bawat bata.",
            "Kumain ako ng bawat aklat.",
            "Pumunta ako sa bawat bata.",
            "Bawat bata ay kumakain.",
            "Kumakain ang kada bata.",
            "Kada bata ay kumakain.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
