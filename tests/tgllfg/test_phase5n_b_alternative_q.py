"""Phase 5n.B Commit 7: Alternative-Q (§18 L45).

Closes §18.1 deferral L45 (``Tao ka o multo?``) by extending
the existing Phase 5k Commit 5 binary OR-clausal-coord rule to
lift ``Q_TYPE=ALTERNATIVE`` onto the matrix as the structural
marker for Alternative-Q. The rule shape is unchanged
(``S → S PART[COORD=OR] S``); the matrix simply gains a Q_TYPE
feat in addition to the existing COORD=OR.

Pragmatic disambiguation between declarative OR-coord and
Alternative-Q is signaled in writing by ``?`` (currently
silently dropped pre-parse) and in speech by intonation —
neither is in the grammar's purview. Both readings share the
same syntactic structure in Tagalog; the syntax annotates the
ALTERNATIVE potentiality and downstream consumers interpret.
"""

from __future__ import annotations

from tgllfg.core.pipeline import parse_text


def _alt_q_parse(text: str):
    parses = parse_text(text, n_best=10)
    for p in parses:
        if p[1].feats.get("Q_TYPE") == "ALTERNATIVE":
            return p
    return None


# === Alternative-Q clausal (no comma) ================================


class TestAlternativeQClausal:
    """``Doktor si Maria o estudyante si Juan?`` "Is Maria a
    doctor or is Juan a student?" — Alternative-Q with full-S
    conjuncts. Q_TYPE=ALTERNATIVE rides on the matrix."""

    def test_predicative_n_alt_q(self) -> None:
        result = _alt_q_parse("Doktor si Maria o estudyante si Juan.")
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("COORD") == "OR"
        assert fs.feats.get("Q_TYPE") == "ALTERNATIVE"
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2

    def test_v_clausal_alt_q(self) -> None:
        # Verbal clausal conjuncts.
        result = _alt_q_parse("Kumain si Maria o tumakbo si Juan.")
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("COORD") == "OR"
        assert fs.feats.get("Q_TYPE") == "ALTERNATIVE"


# === Alternative-Q with comma ========================================


class TestAlternativeQComma:
    """The comma-marked form ``S, o S`` also lifts
    Q_TYPE=ALTERNATIVE."""

    def test_comma_alt_q(self) -> None:
        result = _alt_q_parse(
            "Kumain si Maria, o tumakbo si Juan."
        )
        assert result is not None
        _ct, fs, _astr, _diags = result
        assert fs.feats.get("COORD") == "OR"
        assert fs.feats.get("Q_TYPE") == "ALTERNATIVE"


# === Other coords don't lift Q_TYPE ==================================


class TestOtherCoordsDoNotLiftQType:
    """The Q_TYPE=ALTERNATIVE lift is gated on COORD=OR. AND /
    BUT / SO clausal coords do NOT carry Q_TYPE."""

    def test_at_coord_no_q_type(self) -> None:
        parses = parse_text("Kumain si Maria at tumakbo si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "AND"
        assert fs.feats.get("Q_TYPE") is None

    def test_pero_coord_no_q_type(self) -> None:
        parses = parse_text("Kumain si Maria pero tumakbo si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "BUT"
        assert fs.feats.get("Q_TYPE") is None


# === Existing OR-coord behavior preserved ============================


class TestOrCoordPreserved:
    """The Phase 5k Commit 5 ``len(parses) == 1`` invariant for
    OR-clausal coord persists — the Q_TYPE lift is added to the
    same rule, not a parallel rule, so no duplicate parses are
    introduced."""

    def test_or_coord_single_parse(self) -> None:
        parses = parse_text("Kumain si Maria o tumakbo si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("COORD") == "OR"
