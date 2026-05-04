"""Phase 5f Commit 21: distributive-possessive ``kani-kaniya`` /
``kanya-kanya`` (Group H3 item 7).

Adds 2 ``Q[DISTRIB_POSS="YES", QUANT=EACH_OWN]`` lex entries
(``kanikaniya``, ``kanyakanya``) and 7 new grammar rules — 6
case-marked variants (3 cases × 2 linker variants) plus 1
bare-NOM variant. Existing Phase 5b ``Q + NP[GEN]`` partitive
rules gain ``¬ (↓2 DISTRIB_POSS)`` so distributive-possessive
Qs only take the linker-N form.

Lex (data/tgl/particles.yaml):

* ``kanikaniya`` — Q[QUANT=EACH_OWN, DISTRIB_POSS="YES"].
                   Reduplication of ``kaniya``.
* ``kanyakanya`` — Q[QUANT=EACH_OWN, DISTRIB_POSS="YES"].
                   Full reduplication of ``kanya``.

Both forms are functionally equivalent; the orthographic
distinction reflects the two attested reduplication patterns.
Single-token forms per the precedent set in Phase 5f Commits
14 / 16 / 18 / 19; canonical hyphenated ``kani-kaniya`` /
``kanya-kanya`` awaits a tokenizer pre-pass.

Grammar (src/tgllfg/cfg/nominal.py):

* 6 case-marked NP rules:
    NP[CASE=X] → DET/ADP[CASE=X] Q[DISTRIB_POSS=YES]
                 PART[LINK] N
  (3 cases × 2 linker variants).
* 1 bare-NOM NP rule:
    NP[CASE=NOM] → Q[DISTRIB_POSS=YES] PART[LINK] N

The constraining equation ``(↓2 DISTRIB_POSS) =c 'YES'`` is
the load-bearing piece — non-distributive-possessive Q heads
(lahat / iba / vague / universal) match by absence on
DISTRIB_POSS without it. ``¬ (↓4 DISTRIB_POSS)`` blocks
chained distributive-possessives.

Tests cover:

* Morph: kanikaniya + kanyakanya analyse as Q with
  DISTRIB_POSS="YES" + QUANT=EACH_OWN.
* Case-marked NP composition (GEN OBJ, DAT ADJUNCT): the
  matrix NP rides DISTRIB_POSS="YES" + QUANT=EACH_OWN +
  LEMMA from N.
* Bare-NOM composition with ay-fronting:
  ``Kanyakanyang aklat ay binili nila.``
* Negative (per §11.2): ``*kanikaniyang kanyakanyang aklat``
  (chained), ``*ng kanyakanya ng aklat`` (DISTRIB_POSS in
  GEN-NP partitive blocked by new gate).
* Regression: lahat partitive, lahat float, vague linker,
  universal bawat, cardinal NP-modifier all unchanged.
* LMT diagnostics clean.

Out of scope (deferred follow-on commits):

* Standalone use (``Kanya-kanya na lang.`` "It's each one's
  own now.") — idiomatic; needs separate handling.
* Productive reduplication of arbitrary pronouns
  (``akin-akin``, ``inyo-inyo``) — restricted in standard
  Tagalog to 3rd-person; per-form lex sufficient.
* Generic preposed-possessor construction (``kanyang
  aklat`` "his/her book", ``aking aklat`` "my book") —
  additive but structurally distinct (PRON[DAT] + LINK + N
  rather than Q + LINK + N). Defer.
* DISTRIB_POSS percolation depth — same NP-from-N
  projection limitation as VAGUE / UNIV / etc. The matrix
  NP gets DISTRIB_POSS via the rule's explicit equation;
  inner attribute walking unnecessary.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.pipeline import parse_text
from tgllfg.text import tokenize


def _distrib_poss() -> list[str]:
    return ["kanikaniya", "kanyakanya"]


def _first_obj(text: str) -> FStructure | None:
    rs = parse_text(text)
    if not rs:
        return None
    _, f, _, _ = rs[0]
    obj = f.feats.get("OBJ")
    return obj if isinstance(obj, FStructure) else None


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


class TestDistribPossMorph:

    def test_all_distrib_poss_analyze(self) -> None:
        for lemma in _distrib_poss():
            toks = tokenize(lemma)
            ml = analyze_tokens(toks)
            cands = [c for c in ml[0] if c.pos == "Q"]
            assert cands, f"no Q analysis for {lemma!r}"
            ma = cands[0]
            assert ma.feats.get("DISTRIB_POSS") == "YES", (
                f"{lemma}: DISTRIB_POSS expected 'YES', got "
                f"{ma.feats.get('DISTRIB_POSS')!r}"
            )
            assert ma.feats.get("QUANT") == "EACH_OWN"


# === Case-marked NP composition ===========================================


class TestDistribPossCaseMarked:
    """``ng kanyakanyang aklat`` (GEN OBJ), ``sa kanyakanyang
    bahay`` (DAT ADJ). The case-marked rule
    ``NP[CASE=X] → DET/ADP[CASE=X] Q[DISTRIB_POSS=YES]
    PART[LINK] N`` fires; matrix NP carries DISTRIB_POSS=YES +
    QUANT=EACH_OWN + LEMMA from N."""

    def test_kanyakanya_in_gen_obj(self) -> None:
        obj = _first_obj("Bumili ako ng kanyakanyang aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("CASE") == "GEN"
        assert obj.feats.get("DISTRIB_POSS") == "YES"
        assert obj.feats.get("QUANT") == "EACH_OWN"

    def test_kanikaniya_in_gen_obj(self) -> None:
        obj = _first_obj("Bumili ako ng kanikaniyang aklat.")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "aklat"
        assert obj.feats.get("DISTRIB_POSS") == "YES"
        assert obj.feats.get("QUANT") == "EACH_OWN"

    def test_kanyakanya_in_dat_adjunct(self) -> None:
        adj = _adjunct_with_lemma(
            "Pumunta ako sa kanyakanyang bahay.", "bahay"
        )
        assert adj is not None
        assert adj.feats.get("CASE") == "DAT"
        assert adj.feats.get("DISTRIB_POSS") == "YES"
        assert adj.feats.get("QUANT") == "EACH_OWN"


# === Bare-NOM composition =================================================


class TestDistribPossBareNom:
    """``Kanyakanyang aklat ay binili nila.`` "Their own books
    were what they bought." — bare-NOM rule fires (Q +
    PART[LINK] + N → NP[CASE=NOM]); the resulting NP slots
    into the ay-inversion TOPIC position."""

    def test_kanyakanyang_aklat_ay_fronted(self) -> None:
        rs = parse_text("Kanyakanyang aklat ay binili nila.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        topic = f.feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        assert topic.feats.get("LEMMA") == "aklat"
        assert topic.feats.get("DISTRIB_POSS") == "YES"
        assert topic.feats.get("QUANT") == "EACH_OWN"

    def test_kanikaniyang_aklat_ay_fronted(self) -> None:
        rs = parse_text("Kanikaniyang aklat ay binili nila.", n_best=5)
        assert rs
        _, f, _, _ = rs[0]
        topic = f.feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        assert topic.feats.get("DISTRIB_POSS") == "YES"


# === Negative fixtures (per §11.2) ========================================


class TestDistribPossNegative:

    def test_chained_distrib_poss_blocked(self) -> None:
        # ``*kanikaniyang kanyakanyang aklat`` — chained
        # distributive-possessives blocked by ``¬ (↓4
        # DISTRIB_POSS)``.
        rs = parse_text(
            "Bumili ako ng kanikaniyang kanyakanyang aklat.",
            n_best=10,
        )
        assert rs == [], (
            f"chained distributive-possessives not blocked: "
            f"got {len(rs)} parses"
        )

    def test_distrib_poss_partitive_blocked(self) -> None:
        # ``*ng kanyakanya ng aklat`` — DISTRIB_POSS in GEN-NP
        # partitive blocked by new ``¬ (↓2 DISTRIB_POSS)`` gate.
        rs = parse_text("Bumili ako ng kanyakanya ng aklat.", n_best=10)
        assert rs == [], (
            f"DISTRIB_POSS partitive not blocked: got {len(rs)} parses"
        )


# === Regression ===========================================================


class TestDistribPossRegressions:

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

    def test_cardinal_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tatlong aklat.", n_best=5)
        assert rs

    def test_collective_unchanged(self) -> None:
        rs = parse_text(
            "Bumili ako ng isang dosenang itlog.", n_best=5
        )
        assert rs

    def test_distributive_unchanged(self) -> None:
        rs = parse_text("Bumili ako ng tigisang aklat.", n_best=5)
        assert rs


# === LMT diagnostics clean ================================================


class TestDistribPossLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            "Bumili ako ng kanyakanyang aklat.",
            "Bumili ako ng kanikaniyang aklat.",
            "Pumunta ako sa kanyakanyang bahay.",
            "Kanyakanyang aklat ay binili nila.",
            "Kanikaniyang aklat ay binili nila.",
        ):
            rs = parse_text(s, n_best=5)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
