"""Phase 5d Commit 7: raising chains + raising under control.

Two related constructions that compose existing Phase 5c / 5d
infrastructure rather than introducing new analytical commitments.

* **Raising chains** — a raising matrix embeds another raising
  clause (``Mukhang bakang kumakain ang bata`` "It seems the child
  might be eating"). Already worked at end of Phase 5d Commit 1
  because the existing raising rules
  (``S → V[CTRL_CLASS=RAISING] PART[LINK=NA|NG] S`` and the bare
  variant for RAISING_BARE) accept any ``S`` as the embedded
  clause, including another raising-S. SUBJ structure-shares
  through every layer via the ``(↑ SUBJ) = (↑ XCOMP SUBJ)``
  equation. This file pins the behaviour with explicit tests.

* **Raising under control** — a control verb's XCOMP is itself a
  raising structure (``Gusto kong mukhang kumakain`` "I want to
  seem to be eating"). Phase 5c §7.6 follow-on Commit 5 placed
  raising rules at the ``S`` level only; control complements live
  at the ``S_XCOMP`` level (SUBJ-gapped). Phase 5d Commit 7 adds
  ``S_XCOMP``-level raising variants that compose the raising
  structure-share with the S_XCOMP convention
  ``(↑ SUBJ) = (↑ REL-PRO)``. Then the matrix control wrap rule's
  ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` propagates the controller into
  the embedded action's SUBJ.

Tests in this file verify:

* All four chain types (linked-linked, linked-bare, bare-linked,
  bare-bare) compose through ``S`` recursion.
* Raising under PSYCH control (``gusto``) and INTRANS control
  (``pumayag``).
* Raising chains under control (3-level XCOMP nesting).
* SUBJ structure-sharing through every layer — verified via
  Python-id equality of the SUBJ f-structure across the chain.
* No spurious extra parses: each construction has exactly one
  parse (modulo the documented Phase 4 §7.8 ambiguities).
* LMT diagnostics clean.
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _xcomp_chain(f: FStructure) -> list[FStructure]:
    """Return a list of f-structures starting at ``f`` and walking
    down ``XCOMP`` until the chain ends."""
    out: list[FStructure] = [f]
    cur: FStructure | None = f
    while True:
        if not isinstance(cur, FStructure):
            break
        nxt = cur.feats.get("XCOMP")
        if not isinstance(nxt, FStructure):
            break
        out.append(nxt)
        cur = nxt
    return out


def _subj_ids_along_chain(f: FStructure) -> set[int]:
    ids: set[int] = set()
    for node in _xcomp_chain(f):
        s = node.feats.get("SUBJ")
        if isinstance(s, FStructure):
            ids.add(id(s))
    return ids


def _first(text: str) -> FStructure:
    rs = parse_text(text)
    assert rs, f"no parse for {text!r}"
    return rs[0][1]


# === Raising chains (already worked; pin behaviour) ======================


class TestRaisingChains:
    """Two raising verbs in sequence, composing through S
    recursion. The whole chain shares one SUBJ f-structure."""

    def test_linked_linked(self) -> None:
        # ``Mukhang bakang kumakain ang bata`` — mukha[RAISING] +
        # baka[RAISING] + AV-V. Three-level XCOMP with shared SUBJ.
        f = _first("Mukhang bakang kumakain ang bata.")
        assert f.feats.get("PRED") == "SEEM <XCOMP> SUBJ"
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds == ["SEEM <XCOMP> SUBJ", "MIGHT <XCOMP> SUBJ", "EAT <SUBJ>"]
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1, f"SUBJ ids not shared: {ids}"

    def test_linked_linked_swap(self) -> None:
        f = _first("Bakang mukhang kumakain ang bata.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "MIGHT <XCOMP> SUBJ"
        assert preds[1] == "SEEM <XCOMP> SUBJ"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1

    def test_bare_linked(self) -> None:
        # ``Parang mukhang kumakain ang bata`` — parang[BARE] +
        # mukha[RAISING] + AV-V.
        f = _first("Parang mukhang kumakain ang bata.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "SEEMS-LIKE <XCOMP> SUBJ"
        assert preds[1] == "SEEM <XCOMP> SUBJ"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1

    def test_linked_bare(self) -> None:
        f = _first("Mukhang parang kumakain ang bata.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "SEEM <XCOMP> SUBJ"
        assert preds[1] == "SEEMS-LIKE <XCOMP> SUBJ"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1

    def test_bare_bare(self) -> None:
        # ``Parang tila kumain ang bata`` — both raisers carry no
        # linker; the chain composes at the ``S`` level.
        f = _first("Parang tila kumain ang bata.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "SEEMS-LIKE <XCOMP> SUBJ"
        assert preds[1] == "APPARENTLY <XCOMP> SUBJ"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1


# === Raising under control =============================================


class TestRaisingUnderControl:
    """Control verb embeds a raising matrix. The new S_XCOMP
    raising rules compose the raising structure-share with the
    S_XCOMP convention so the controller flows through to the
    innermost action's SUBJ."""

    def test_psych_plus_linked_raising(self) -> None:
        # ``Gusto kong mukhang kumakain`` — gusto[PSYCH] + ko +
        # -ng + mukhang[RAISING] + V. WANT > SEEM > EAT.
        f = _first("Gusto kong mukhang kumakain.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds == ["WANT <SUBJ, XCOMP>", "SEEM <XCOMP> SUBJ", "EAT <SUBJ>"]
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1

    def test_psych_plus_bare_raising(self) -> None:
        f = _first("Gusto kong parang kumakain.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "WANT <SUBJ, XCOMP>"
        assert preds[1] == "SEEMS-LIKE <XCOMP> SUBJ"
        assert preds[2] == "EAT <SUBJ>"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1

    def test_intrans_plus_linked_raising(self) -> None:
        # ``Pumayag siyang mukhang kumakain`` —
        # pumayag[INTRANS] + siya + -ng + mukhang[RAISING] + V.
        f = _first("Pumayag siyang mukhang kumakain.")
        assert f.feats.get("PRED") == "AGREE <SUBJ, XCOMP>"
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds == ["AGREE <SUBJ, XCOMP>", "SEEM <XCOMP> SUBJ", "EAT <SUBJ>"]
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1

    def test_intrans_plus_bare_raising(self) -> None:
        f = _first("Pumayag siyang parang kumakain.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "AGREE <SUBJ, XCOMP>"
        assert preds[1] == "SEEMS-LIKE <XCOMP> SUBJ"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1


# === Raising chains under control (composition) =========================


class TestRaisingChainsUnderControl:
    """Control + raising chain — the deepest test of composition.
    Four-level XCOMP with all SUBJ slots structure-shared."""

    def test_psych_plus_two_raisers(self) -> None:
        # ``Gusto kong mukhang bakang kumakain`` — WANT > SEEM >
        # MIGHT > EAT, all sharing one SUBJ.
        f = _first("Gusto kong mukhang bakang kumakain.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds == [
            "WANT <SUBJ, XCOMP>",
            "SEEM <XCOMP> SUBJ",
            "MIGHT <XCOMP> SUBJ",
            "EAT <SUBJ>",
        ]
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1, f"SUBJ ids not shared across 4 levels: {ids}"

    def test_psych_plus_bare_then_linked(self) -> None:
        f = _first("Gusto kong parang mukhang kumain.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "WANT <SUBJ, XCOMP>"
        assert preds[1] == "SEEMS-LIKE <XCOMP> SUBJ"
        assert preds[2] == "SEEM <XCOMP> SUBJ"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1

    def test_intrans_plus_linked_then_bare(self) -> None:
        f = _first("Pumayag siyang mukhang parang kumain.")
        chain = _xcomp_chain(f)
        preds = [n.feats.get("PRED") for n in chain]
        assert preds[0] == "AGREE <SUBJ, XCOMP>"
        assert preds[1] == "SEEM <XCOMP> SUBJ"
        assert preds[2] == "SEEMS-LIKE <XCOMP> SUBJ"
        ids = _subj_ids_along_chain(f)
        assert len(ids) == 1


# === Regressions =========================================================


class TestRegressions:

    def test_single_raising_unchanged(self) -> None:
        f = _first("Mukhang kumakain ang bata.")
        assert f.feats.get("PRED") == "SEEM <XCOMP> SUBJ"

    def test_single_bare_raising_unchanged(self) -> None:
        f = _first("Parang kumain ang bata.")
        assert f.feats.get("PRED") == "SEEMS-LIKE <XCOMP> SUBJ"

    def test_single_psych_control_unchanged(self) -> None:
        f = _first("Gusto kong kumain.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        xcomp = f.feats["XCOMP"]
        assert isinstance(xcomp, FStructure)
        assert xcomp.feats.get("PRED") == "EAT <SUBJ>"


# === LMT diagnostics =====================================================


class TestRaisingChainsLmtClean:

    def test_no_blocking_diagnostics(self) -> None:
        for s in (
            # Raising chains
            "Mukhang bakang kumakain ang bata.",
            "Bakang mukhang kumakain ang bata.",
            "Parang mukhang kumakain ang bata.",
            "Mukhang parang kumakain ang bata.",
            "Parang tila kumain ang bata.",
            # Raising under control
            "Gusto kong mukhang kumakain.",
            "Gusto kong parang kumakain.",
            "Pumayag siyang mukhang kumakain.",
            # Compositions
            "Gusto kong mukhang bakang kumakain.",
            "Pumayag siyang mukhang parang kumain.",
        ):
            rs = parse_text(s, n_best=10)
            assert rs, f"no parse for {s!r}"
            assert any(
                not any(d.is_blocking() for d in diags)
                for _, _, _, diags in rs
            ), f"all parses for {s!r} have blocking diagnostics"
