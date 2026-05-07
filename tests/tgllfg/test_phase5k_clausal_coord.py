"""Phase 5k Commit 5: binary clausal coordination.

Roadmap §12.1 / plan-of-record §5.4, §6 Commit 5. Two new rules
in ``cfg/coordination.py``:

    S → S PART[COORD=AND] S
    S → S PART[COORD=OR]  S

Each conjunct clause is its own f-structure (with its own PRED,
SUBJ, voice/aspect/mood); the matrix coord-S carries a flat
2-element CONJUNCTS set + a COORD value, with NO PRED of its own.

No PRED on the matrix coord-S is the canonical LFG analysis for
non-asymmetric coordination. The legacy LMT (lmt/legacy.py) was
extended to handle PRED-less f-structures by returning an empty
AStructure rather than crashing on ``.split()[0]`` of an empty
string.

Adversatives (Phase 5k Commit 6 — pero / ngunit / subalit,
COORD=BUT) and consequence (Commit 7 — kaya, COORD=SO) reuse the
binary clausal-coord shape with different COORD values.

End-to-end target sentences:

    Kumain si Maria at pumunta si Juan.   "Maria ate and Juan went."
    Kumain si Maria o tumakbo si Juan.    "Maria ate or Juan ran."
"""

from __future__ import annotations

from tgllfg.core.pipeline import parse_text


# === Additive clausal coord ==========================================


class TestAdditiveClausalCoord:
    """``Kumain si Maria at pumunta si Juan.`` — two verbal
    clauses joined by ``at``."""

    def test_basic_at_clausal(self) -> None:
        parses = parse_text("Kumain si Maria at pumunta si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "AND"
        # Matrix has NO PRED — coord is non-predicational.
        assert fs.feats.get("PRED") is None
        # SUBJ on the matrix is also unset; SUBJ lives on each
        # conjunct.
        assert fs.feats.get("SUBJ") is None

    def test_two_conjunct_clauses(self) -> None:
        parses = parse_text("Kumain si Maria at pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        # Each conjunct has its own PRED + SUBJ.
        preds = {(c.feats.get("PRED") or "").split("<")[0].strip() for c in conjuncts}
        assert "EAT" in preds
        assert "PUNTA" in preds
        for c in conjuncts:
            subj = c.feats.get("SUBJ")
            assert subj is not None

    def test_each_conjunct_retains_voice_aspect(self) -> None:
        """Per-conjunct voice / aspect feats stay on the conjunct
        f-structure; the matrix doesn't carry them."""
        parses = parse_text("Kumain si Maria at pumunta si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        for c in conjuncts:
            assert c.feats.get("VOICE") == "AV"
            assert c.feats.get("ASPECT") in ("PFV", "IPFV", "CTPL")
        # Matrix has no VOICE / ASPECT.
        assert fs.feats.get("VOICE") is None
        assert fs.feats.get("ASPECT") is None


# === Disjunctive clausal coord =======================================


class TestDisjunctiveClausalCoord:
    """``Kumain si Maria o tumakbo si Juan.`` — two verbal
    clauses joined by ``o``."""

    def test_basic_o_clausal(self) -> None:
        parses = parse_text("Kumain si Maria o tumakbo si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "OR"

    def test_two_conjunct_clauses(self) -> None:
        parses = parse_text("Kumain si Maria o tumakbo si Juan.")
        _ct, fs, _astr, _diags = parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        preds = {(c.feats.get("PRED") or "").split("<")[0].strip() for c in conjuncts}
        assert "EAT" in preds
        assert "TAKBO" in preds


# === Same-verb same-VOICE coord ======================================


class TestSameVerbCoord:
    """``Kumain si Maria at kumain si Juan.`` — same V, different
    SUBJs. Composes via the binary clausal-coord rule unchanged."""

    def test_same_verb_two_subjs(self) -> None:
        parses = parse_text("Kumain si Maria at kumain si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        subj_lemmas = {
            c.feats.get("SUBJ").feats.get("LEMMA")
            for c in conjuncts
            if c.feats.get("SUBJ") is not None
        }
        assert subj_lemmas == {"maria", "juan"}


# === Negation × clausal coord =======================================


class TestNegationXClausalCoord:
    """Phase 4 §7.2 hindi-wrap composes with the inner conjunct S
    unchanged — local-scoping reading. ``Hindi kumain si Maria at
    pumunta si Juan.`` parses as ``[hindi kumain si Maria] AND
    [pumunta si Juan]`` with POLARITY=NEG only on the first
    conjunct.

    Cross-conjunct scoping (``Hindi [si Maria at si Juan] kumain.``
    "Neither X nor Y") is a deferred follow-on (plan §9.2)."""

    def test_local_negation_first_conjunct(self) -> None:
        parses = parse_text(
            "Hindi kumain si Maria at pumunta si Juan."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Look for the COORD=AND parse (negation may admit both
        # local-and-cross scoping — pick the local one).
        coord_parses = [
            p for p in parses if p[1].feats.get("COORD") == "AND"
        ]
        assert len(coord_parses) >= 1
        _ct, fs, _astr, _diags = coord_parses[0]
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2
        # Per-conjunct POLARITY: first conjunct is NEG, second POS.
        polarities = sorted(
            (c.feats.get("PRED") or "").split("<")[0].strip()
            + ":" + str(c.feats.get("POLARITY") or "POS")
            for c in conjuncts
        )
        assert "EAT:NEG" in polarities
        assert "PUNTA:POS" in polarities


# === C-tree shape ===================================================


class TestClausalCoordCTreeShape:
    """The binary clausal-coord rule yields a 3-daughter c-tree at
    the coord-S level: S + PART + S."""

    def test_three_daughters(self) -> None:
        parses = parse_text("Kumain si Maria at pumunta si Juan.")
        ctree, _fs, _astr, _diags = parses[0]
        assert ctree.label == "S"
        assert len(ctree.children) == 3
        assert ctree.children[0].label == "S"
        assert ctree.children[1].label.startswith("PART")
        assert ctree.children[2].label == "S"


# === COORD value disambiguation =====================================


class TestClausalCoordValueDisambiguation:
    """``=c 'AND'`` / ``=c 'OR'`` constraints + daughter category
    patterns ensure each rule fires on its own coordinator only —
    no cross-fire."""

    def test_at_does_not_yield_or_clausal_coord(self) -> None:
        parses = parse_text("Kumain si Maria at pumunta si Juan.")
        _ct, fs, _, _ = parses[0]
        assert fs.feats.get("COORD") == "AND"

    def test_o_does_not_yield_and_clausal_coord(self) -> None:
        parses = parse_text("Kumain si Maria o tumakbo si Juan.")
        _ct, fs, _, _ = parses[0]
        assert fs.feats.get("COORD") == "OR"


# === LMT robustness on PRED-less coord matrix =======================


class TestLmtRobustnessOnCoordMatrix:
    """The legacy LMT (lmt/legacy.py) previously crashed with
    ``IndexError`` on PRED-less f-structures (``.split()[0]`` of
    empty string). Phase 5k Commit 5 extends apply_lmt to return
    an empty AStructure for PRED-less matrices. This test pins
    the no-crash behavior."""

    def test_no_crash_on_clausal_coord(self) -> None:
        parses = parse_text("Kumain si Maria at pumunta si Juan.")
        # If LMT crashed, parse_text would propagate the error.
        # Reaching here (with a parse) confirms graceful handling.
        assert len(parses) >= 1
        _ct, _fs, astr, _diags = parses[0]
        # The matrix's a-structure is empty (no roles, no mapping)
        # because the matrix has no PRED.
        assert astr.pred == ""
        assert astr.roles == []


# === Three-clause chain via right-recursion =========================


class TestThreeClauseChain:
    """Three S-conjuncts via two binary applications of the rule:
    ``[Kumain si Maria] [at [pumunta si Juan] [at [tumakbo si Pedro]]]``
    or left-associative. Both produce nested CONJUNCTS, not flat;
    the flat-3 form is left as a Phase 5k follow-on (deferred).

    For now this just confirms three-clause chains parse, with
    the binary-nesting structure."""

    def test_three_conjunct_clausal_parses(self) -> None:
        parses = parse_text(
            "Kumain si Maria at pumunta si Juan at tumakbo si Pedro."
        )
        assert len(parses) >= 1
        # Whichever associativity the parser picks, the matrix
        # carries COORD=AND.
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "AND"
