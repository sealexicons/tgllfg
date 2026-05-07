"""Phase 5k Commit 8: asymmetric NP coord + negation × coord tests.

Roadmap §12.1 / plan-of-record §5.7, §5.8, §6 Commit 8.

Asymmetric NP coordination: three new rules in
``cfg/coordination.py`` for each case X ∈ {NOM, GEN, DAT}:

    NP[CASE=X] → NP[CASE=X] PUNCT[COMMA] PART[POLARITY=NEG] NP[CASE=X]

``Si Maria, hindi si Juan.`` "Maria, not Juan" — comma-separated
coord with the second conjunct headed by ``hindi``, producing a
contrast-with-rejection reading. The matrix carries
COORD=BUT_NOT (asymmetric value distinct from BUT used for
symmetric adversative pero/ngunit/subalit).

Equations:

  ↓1 ∈ (↑ CONJUNCTS)
  ↓4 ∈ (↑ CONJUNCTS)
  (↑ COORD) = 'BUT_NOT'
  (↑ CASE) = X
  (↑ NUM) = ↓1 NUM
  (↓3 POLARITY) =c 'NEG'
  (↓4 POLARITY) = 'NEG'

NUM percolates from the first (asserted) conjunct; the matrix
asserts ONE referent. Marking the second conjunct's POLARITY=NEG
flags the rejection on its own f-structure for downstream
consumers.

Negation × clausal coord (plan §5.8): no new rule — Phase 4 §7.2
hindi-wrap composes with the inner conjunct S unchanged
(local-scoping reading). ``Hindi kumain si Maria at pumunta si
Juan.`` parses with POLARITY=NEG only on the first conjunct.
Cross-conjunct scoping (``Hindi [si Maria at si Juan] kumain.``
"Neither X nor Y") is a deferred follow-on (plan §9.2).
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Asymmetric NP-coord — SUBJ position ============================


class TestAsymmetricNomCoord:
    """``Kumain si Maria, hindi si Juan.`` "Maria, not Juan,
    ate" — NOM-coord with COORD=BUT_NOT on the SUBJ."""

    def test_basic_nom_asymmetric(self) -> None:
        parses = parse_text("Kumain si Maria, hindi si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "BUT_NOT"
        assert subj.feats.get("CASE") == "NOM"

    def test_two_conjuncts_with_polarity(self) -> None:
        parses = parse_text("Kumain si Maria, hindi si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        conjuncts = subj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        # Find the negated conjunct (POLARITY=NEG); only one should
        # carry it.
        neg_conjuncts = [
            c for c in conjuncts if c.feats.get("POLARITY") == "NEG"
        ]
        assert len(neg_conjuncts) == 1
        # The negated conjunct is Juan (the rejected alternative).
        assert neg_conjuncts[0].feats.get("LEMMA") == "juan"


# === Asymmetric NP-coord — OBJ / ADJUNCT positions ==================


class TestAsymmetricGenCoord:
    """GEN-coord variant: ``Kumain ng aklat, hindi ng lapis si
    Maria.`` "Maria ate the book, not the pencil"."""

    def test_gen_asymmetric_object(self) -> None:
        parses = parse_text(
            "Kumain ng aklat, hindi ng lapis si Maria."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("COORD") == "BUT_NOT"
        assert obj.feats.get("CASE") == "GEN"
        conjuncts = obj.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        lemmas = {c.feats.get("LEMMA") for c in conjuncts}
        assert lemmas == {"aklat", "lapis"}


class TestAsymmetricDatCoord:
    """DAT-coord variant: ``Pumunta si Maria sa palengke, hindi
    sa bahay.`` "Maria went to the market, not to the house"."""

    def test_dat_asymmetric_adjunct(self) -> None:
        parses = parse_text(
            "Pumunta si Maria sa palengke, hindi sa bahay."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adjuncts = fs.feats.get("ADJUNCT")
        assert adjuncts is not None
        coord_adjuncts = [
            a for a in adjuncts if a.feats.get("COORD") == "BUT_NOT"
        ]
        assert len(coord_adjuncts) == 1
        coord = coord_adjuncts[0]
        assert coord.feats.get("CASE") == "DAT"
        conjuncts = coord.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2


# === Composition with predicative-ADJ ===============================


class TestAsymmetricPlusPredAdj:
    """``Matanda si Maria, hindi si Juan.`` "Maria is old,
    not Juan." — predicative-ADJ + asymmetric NOM coord SUBJ."""

    def test_pred_adj_asymmetric(self) -> None:
        parses = parse_text("Matanda si Maria, hindi si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Matrix is ADJ-predicative.
        assert (fs.feats.get("PRED") or "").startswith("ADJ")
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "BUT_NOT"


# === COORD value distinct from BUT (symmetric adversative) ==========


class TestButNotDistinctFromBut:
    """The asymmetric COORD=BUT_NOT is a separate value from the
    symmetric COORD=BUT (used for ``pero`` / ``ngunit`` /
    ``subalit``). The two readings are structurally distinct: BUT
    is a clausal-S coord with its own connective PART; BUT_NOT is
    an NP-internal coord with hindi as the connective."""

    def test_asymmetric_is_but_not_not_but(self) -> None:
        parses = parse_text("Kumain si Maria, hindi si Juan.")
        _ct, fs, _, _ = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("COORD") == "BUT_NOT"
        assert subj.feats.get("COORD") != "BUT"

    def test_pero_is_but_not_but_not(self) -> None:
        parses = parse_text("Kumain si Maria pero pumunta si Juan.")
        _ct, fs, _, _ = parses[0]
        assert fs.feats.get("COORD") == "BUT"
        assert fs.feats.get("COORD") != "BUT_NOT"


# === C-tree shape ==================================================


class TestAsymmetricCTreeShape:
    """The asymmetric coord rule yields a 4-daughter c-tree at
    the coord-NP level: NP + PUNCT[COMMA] + PART[hindi] + NP."""

    def test_four_daughters(self) -> None:
        parses = parse_text("Kumain si Maria, hindi si Juan.")
        ctree, _fs, _astr, _diags = parses[0]

        def find_coord_np(n):
            if (
                n.label.startswith("NP[CASE=NOM]")
                and len(n.children) == 4
            ):
                labels = [c.label for c in n.children]
                if (
                    labels[1].startswith("PUNCT")
                    and labels[2].startswith("PART")
                ):
                    return n
            for c in n.children:
                got = find_coord_np(c)
                if got is not None:
                    return got
            return None

        coord_np = find_coord_np(ctree)
        assert coord_np is not None, (
            "expected a 4-daughter coord-NP node "
            "(NP + PUNCT + PART + NP)"
        )


# === Negation × clausal coord — local-scoping ======================


class TestNegationXClausalCoordLocalScoping:
    """Phase 4 §7.2 hindi-wrap composes with the inner conjunct
    S unchanged — local-scoping reading. ``Hindi kumain si Maria
    at pumunta si Juan.`` parses with POLARITY=NEG only on the
    first conjunct.

    Cross-conjunct scoping (``Hindi [si Maria at si Juan]
    kumain.`` "Neither X nor Y") is a deferred follow-on (plan
    §9.2)."""

    def test_neg_first_conjunct_local_scope(self) -> None:
        parses = parse_text(
            "Hindi kumain si Maria at pumunta si Juan."
        )
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "AND"
        ]
        assert len(coord_parses) >= 1
        _ct, fs, _astr, _diags = coord_parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        # Per-conjunct POLARITY: first conjunct is NEG, second POS.
        per_pred_pol = {
            (c.feats.get("PRED") or "").split("<")[0].strip(): c.feats.get("POLARITY")
            for c in conjuncts
        }
        assert per_pred_pol.get("EAT") == "NEG"
        assert per_pred_pol.get("PUNTA") in (None, "POS")

    def test_neg_second_conjunct_local_scope(self) -> None:
        """``Kumain si Maria at hindi pumunta si Juan.`` — NEG
        only on the second conjunct."""
        parses = parse_text(
            "Kumain si Maria at hindi pumunta si Juan."
        )
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "AND"
        ]
        assert len(coord_parses) >= 1
        _ct, fs, _astr, _diags = coord_parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        per_pred_pol = {
            (c.feats.get("PRED") or "").split("<")[0].strip(): c.feats.get("POLARITY")
            for c in conjuncts
        }
        assert per_pred_pol.get("EAT") in (None, "POS")
        assert per_pred_pol.get("PUNTA") == "NEG"

    @pytest.mark.parametrize("conj", ["at", "o", "pero"])
    def test_neg_first_with_various_coordinators(
        self, conj: str
    ) -> None:
        sentence = f"Hindi kumain si Maria {conj} pumunta si Juan."
        parses = parse_text(sentence)
        # Should have a coord parse with NEG on the first conjunct.
        coord_parses = [
            p for p in parses
            if p[1].feats.get("COORD") in ("AND", "OR", "BUT")
        ]
        assert len(coord_parses) >= 1
        _ct, fs, _astr, _diags = coord_parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        # First-conjunct POLARITY=NEG (in any conjunct order
        # because the coord set is unordered).
        pols = {c.feats.get("POLARITY") for c in conjuncts}
        assert "NEG" in pols


# === Pinned 0-parses (deferred to Phase 5k follow-on) ==============


class TestDeferredAsymmetricForms:
    """Standalone NP-coord without verbal head and the no-comma
    asymmetric form are deferred. Pin the 0-parse state so future
    follow-on work flips the assertion."""

    @pytest.mark.parametrize("sentence", [
        # Standalone NP-coord (no verbal head).
        "Si Maria, hindi si Juan.",
        # No-comma asymmetric — comma is structurally required.
        "Kumain si Maria hindi si Juan.",
    ])
    def test_deferred_form_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"{sentence!r} now parses — Phase 5k follow-on may have "
            f"landed standalone-NP-coord support or a no-comma "
            f"asymmetric variant. Update this test and add positive "
            f"tests for the new construction."
        )
