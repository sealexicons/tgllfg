"""Phase 5b §7.8 follow-on: pre-NP partitive (lahat ng bata).

Phase 4 §7.8 deferred the pre-NP partitive form
(``ang lahat ng bata`` "all of the children") with the note that
"this form needs a QP non-terminal." The implementation chose a
flat 3-child NP rule instead, since the inner ``NP[CASE=GEN]``
already exists in the grammar:

    NP[CASE=X] → DET-or-ADP[CASE=X] Q NP[CASE=GEN]

The outer marker supplies CASE/MARKER, the inner NP[GEN] supplies
the head's PRED, and the Q rides as a ``QUANT`` atom on the
resulting NP.

The pre-existing floated-quantifier rule (``Kumain ang bata
lahat``) is unaffected — it operates at the S level, not within
an NP.
"""

from __future__ import annotations

from typing import Any

from tgllfg.common import AStructure, FStructure
from tgllfg.fstruct import Diagnostic
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[Any, FStructure, AStructure, list[Diagnostic]]:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0]


# === NOM partitive — pivot of an AV-intransitive ===========================


class TestNomPartitive:

    def test_lahat_ng_bata_as_subj(self) -> None:
        # "Kumain ang lahat ng bata" — "All of the children ate."
        # The partitive NP fills the SUBJ slot.
        _, f, _, diags = _first("Kumain ang lahat ng bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        # CASE inherited from outer ang.
        assert subj.feats.get("CASE") == "NOM"
        assert subj.feats.get("MARKER") == "ANG"
        # QUANT lifted from lahat.
        assert subj.feats.get("QUANT") == "ALL"
        # PRED supplied by inner head bata.
        pred = subj.feats.get("PRED")
        assert pred and "NOUN" in str(pred).upper()
        # No spurious diagnostics.
        assert not any(d.is_blocking() for d in diags)

    def test_iba_ng_bata_as_subj(self) -> None:
        # "Kumain ang iba ng bata" — "Some of the children ate."
        # Same shape, different quantifier.
        _, f, _, _ = _first("Kumain ang iba ng bata.")
        subj = f.feats["SUBJ"]
        assert subj.feats.get("QUANT") == "OTHER"
        assert subj.feats.get("CASE") == "NOM"


# === GEN partitive — non-pivot of a transitive ============================


class TestGenPartitive:
    """The partitive can also fill non-pivot ng-NP slots. In OV,
    ``ng lahat ng bata`` is the AGENT — typed ``OBJ-AGENT`` in the
    f-structure under the Phase 5b OBJ-θ-in-grammar alignment."""

    def test_lahat_ng_bata_as_ov_non_pivot(self) -> None:
        # "Kinain ng lahat ng bata ang isda" — "All of the children
        # ate the fish." The AGENT slot (ng-non-pivot in OV) gets
        # the partitive structure.
        _, f, _, _ = _first("Kinain ng lahat ng bata ang isda.")
        obj = f.feats.get("OBJ-AGENT")
        assert isinstance(obj, FStructure)
        assert obj.feats.get("CASE") == "GEN"
        assert obj.feats.get("MARKER") == "NG"
        assert obj.feats.get("QUANT") == "ALL"


# === DAT partitive — sa-marked complement =================================


class TestDatPartitive:

    def test_sa_lahat_ng_bata_as_adjunct(self) -> None:
        # "Lumakad sa lahat ng bata" — "Walked to all of the
        # children." The DAT partitive surfaces as ADJUNCT (or
        # OBL-LOC if the lex entry has a locative role; lakad's
        # locative entry is a Phase 5 §8 BASE addition).
        _, f, _, _ = _first("Lumakad ang bata sa lahat ng bata.")
        # Find the DAT partitive — either in ADJUNCT or OBL-LOC
        # depending on which lex entry won the rank.
        partitive_candidates: list[FStructure] = []
        for key in ("ADJUNCT", "OBL-LOC"):
            value = f.feats.get(key)
            if isinstance(value, frozenset):
                partitive_candidates.extend(
                    m for m in value if isinstance(m, FStructure)
                )
            elif isinstance(value, FStructure):
                partitive_candidates.append(value)
        partitive = next(
            (c for c in partitive_candidates
             if c.feats.get("QUANT") == "ALL"),
            None,
        )
        assert partitive is not None, (
            f"no partitive in ADJUNCT or OBL-LOC; "
            f"feats={sorted(f.feats.keys())}"
        )
        assert partitive.feats.get("CASE") == "DAT"
        assert partitive.feats.get("MARKER") == "SA"


# === Floated quantifier still works (no regression) =======================


class TestFloatedQuantifierUnchanged:
    """The pre-existing floated-quantifier rule (``S → S Q``) is
    unrelated to the partitive rules — it puts Q in the matrix's
    ADJ set, not inside an NP. Both forms parse cleanly without
    competing."""

    def test_floated_lahat_at_clause_end(self) -> None:
        # "Kumain ang bata lahat" — "All the children ate" with
        # lahat floated to clause-final.
        _, f, _, _ = _first("Kumain ang bata lahat.")
        # The SUBJ should NOT have QUANT (lahat isn't inside the NP).
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("QUANT") is None
        # ADJ should contain the floated Q.
        adj = f.feats.get("ADJ")
        assert isinstance(adj, frozenset)
        q_in_adj = next(
            (m for m in adj if isinstance(m, FStructure)
             and m.feats.get("QUANT") == "ALL"),
            None,
        )
        assert q_in_adj is not None


# === Plain NPs unaffected =================================================


class TestPlainNpsUnaffected:
    """The new partitive rules are flat 3-child rules. Plain NPs
    (DET + N, det+N+possessor) shouldn't fire them spuriously."""

    def test_plain_det_n_unchanged(self) -> None:
        # "Kumain ang bata" — bare NP, no quantifier. Should not
        # fire the partitive rule (which requires Q in position 2).
        _, f, _, _ = _first("Kumain ang bata.")
        subj = f.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert "QUANT" not in subj.feats

    def test_possessive_unchanged(self) -> None:
        # "Kumain ang bata ng nanay" — has two parses:
        # - transitive AV: SUBJ=bata, OBJ=nanay (the child ate mother)
        # - intransitive with possessive: SUBJ=bata.POSS=nanay
        #   (the mother's child ate)
        # Find the intransitive parse and check the possessive
        # structure is still emitted by the §7.8 rule. No Q in the
        # sentence, so the partitive rule doesn't fire.
        results = parse_text("Kumain ang bata ng nanay.")
        possessive = next(
            (p for p in results
             if "POSS" in p[1].feats.get("SUBJ", FStructure()).feats),
            None,
        )
        assert possessive is not None, (
            "the §7.8 possessive parse for 'Kumain ang bata ng nanay' "
            "is missing"
        )
        _, f, _, _ = possessive
        subj = f.feats["SUBJ"]
        assert "POSS" in subj.feats
        # No QUANT on subj or its possessor (no quantifier in the
        # sentence).
        assert subj.feats.get("QUANT") is None
        poss = subj.feats["POSS"]
        assert isinstance(poss, FStructure)
        assert poss.feats.get("QUANT") is None
