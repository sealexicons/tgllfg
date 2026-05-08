"""Phase 5m Commit 2: politeness ``po`` / ``ho`` 2P-clitic absorption.

Roadmap §12.1 / plan-of-record §5.1. The Phase 5m Commit 1 lex
entries for ``po`` (REGISTER=POLITE) and ``ho`` (REGISTER=
COLLOQUIAL_POLITE) are 2P clitics that must compose with the
matrix S via a politeness-specific absorption rule. This commit
adds **Rule D** in ``cfg/clitic.py``, mirroring Rule B (``ba``
Q_TYPE lift) and Rule C (``sana`` COUNTERFACTUAL lift):

    S → S PART[CLITIC_CLASS=2P, REGISTER=POLITE]
        (↑) = ↓1
        ↓2 ∈ (↑ ADJ)
        (↓2 REGISTER) =c 'POLITE'
        (↑ REGISTER) = 'POLITE'

A parallel rule fires on ``REGISTER=COLLOQUIAL_POLITE``. Rule A
(generic 2P absorption) is updated with ``¬ (↓2 REGISTER)`` so
the four paths (A generic, B ba, C sana, D po/ho) are mutually
exclusive — no double-fire from po/ho.

Coverage:
* Clause-medial position (``Pumupunta po siya``).
* Clause-final-after-V position (``Pumupunta po``) — exercises 2P
  Wackernagel on a one-word clause.
* Clause-final-after-PRON position (``Pumupunta siya po``,
  ``Pumupunta ako po``).
* Single-parse-only verification: Rule D and Rule A don't
  double-fire.
* Fragment-host limitation pinned: ``Salamat po`` / ``Oo po`` /
  ``Hindi po`` 0-parse because Phase 4 has no fragment-answer
  matrix-S infrastructure. Closure depends on Phase 5n debt-
  clearing or beyond.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Po-politeness clause-medial / clause-final-after-V ================


PO_CLAUSE_MEDIAL = [
    # (sentence, expected_pred_prefix)
    ("Pumupunta po siya.", "PUNTA"),
    ("Pumupunta po ako.", "PUNTA"),
    ("Kumakain po siya.", "EAT"),
]


class TestPoPoliteness:
    """``po`` lifts REGISTER=POLITE to the matrix S via Rule D."""

    @pytest.mark.parametrize("sent,pred_prefix", PO_CLAUSE_MEDIAL)
    def test_clause_medial_po(self, sent: str, pred_prefix: str) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        assert fs.feats.get("REGISTER") == "POLITE", (
            f"expected matrix REGISTER=POLITE for {sent!r}; got "
            f"{fs.feats.get('REGISTER')!r}"
        )

    def test_clause_final_after_pronoun_po(self) -> None:
        parses = parse_text("Pumupunta siya po.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        assert fs.feats.get("REGISTER") == "POLITE"

    def test_po_member_in_adj_set(self) -> None:
        """``po`` appears as a member of the matrix's ADJ set with
        its own REGISTER feat preserved (the lift to matrix is
        a copy, not a move)."""
        parses = parse_text("Pumupunta po siya.")
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJ") or []
        po_members = [
            m for m in adj
            if m.feats.get("LEMMA") == "po"
            and m.feats.get("REGISTER") == "POLITE"
        ]
        assert len(po_members) == 1


# === Ho-colloquial-polite ==============================================


HO_CLAUSE_MEDIAL = [
    ("Pumupunta ho siya.", "PUNTA"),
    ("Kumakain ho siya.", "EAT"),
]


class TestHoColloquialPolite:
    """``ho`` lifts REGISTER=COLLOQUIAL_POLITE via parallel Rule D."""

    @pytest.mark.parametrize("sent,pred_prefix", HO_CLAUSE_MEDIAL)
    def test_clause_medial_ho(self, sent: str, pred_prefix: str) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        assert fs.feats.get("REGISTER") == "COLLOQUIAL_POLITE"

    def test_ho_member_in_adj_set(self) -> None:
        parses = parse_text("Pumupunta ho siya.")
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJ") or []
        ho_members = [
            m for m in adj
            if m.feats.get("LEMMA") == "ho"
            and m.feats.get("REGISTER") == "COLLOQUIAL_POLITE"
        ]
        assert len(ho_members) == 1


# === Single-parse / non-double-fire ====================================


class TestNoDoubleFire:
    """Rule A (generic 2P) and Rule D (REGISTER lift) must be
    mutually exclusive. A sentence with ``po`` produces exactly
    one parse, not two (one via Rule A, one via Rule D)."""

    def test_po_single_parse(self) -> None:
        parses = parse_text("Pumupunta po siya.")
        assert len(parses) == 1, (
            f"expected exactly 1 parse for 'Pumupunta po siya.'; "
            f"got {len(parses)}"
        )

    def test_ho_single_parse(self) -> None:
        parses = parse_text("Pumupunta ho siya.")
        assert len(parses) == 1


# === Rule A regression check ===========================================


class TestRuleAUnchanged:
    """Rule A's existing 2P-clitic absorption is preserved — adding
    ``¬ (↓2 REGISTER)`` doesn't break the existing ``na`` / ``pa``
    / ``daw`` / etc. clitics, none of which carry REGISTER."""

    def test_na_clitic_still_absorbs(self) -> None:
        """``na`` (ASPECT_PART=ALREADY) is the canonical Rule A
        absorption case."""
        parses = parse_text("Kumain na siya.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith("EAT")

    def test_sana_counterfactual_still_lifts(self) -> None:
        """Rule C (Phase 5l) is unchanged — sana still lifts
        COUNTERFACTUAL=YES."""
        parses = parse_text("Pumupunta sana ako.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COUNTERFACTUAL") == "YES"
        # And REGISTER is NOT set (sana is not a politeness clitic).
        assert fs.feats.get("REGISTER") is None


# === Fragment-host deferral ============================================


FRAGMENT_HOSTS = [
    "Salamat po.",
    "Oo po.",
    "Hindi po.",
]


class TestFragmentHostDeferred:
    """Fragment-host position (``Salamat po``, ``Oo po``,
    ``Hindi po``) does NOT parse: there is no Phase 4 fragment-
    answer matrix-S infrastructure that admits these as input
    to the 2P clitic absorption rule. Pinned at 0-parse so
    closure during Phase 5n debt-clearing (or fragment-answer
    phase, whichever lands first) is detectable as an
    unintended flip.
    """

    @pytest.mark.parametrize("sent", FRAGMENT_HOSTS)
    def test_fragment_host_zero_parse(self, sent: str) -> None:
        parses = parse_text(sent)
        assert len(parses) == 0, (
            f"{sent!r} parsed unexpectedly — fragment-answer "
            f"infrastructure has landed; close the deferral and "
            f"un-pin this test."
        )
