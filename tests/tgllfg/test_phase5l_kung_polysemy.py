"""Phase 5l Commit 3: kung polysemy resolution (COND vs INTERROG).

Roadmap §12.1 / plan-of-record §2 (analytical commitment) /
§6 Commit 3. No grammar rules land in this commit — the polysemy
resolution is a structural property of the lex × grammar
interaction, not a new rule:

* ``kung[COMP_TYPE=INTERROG]`` (Phase 5i lex) is consumed only by
  ``cfg/control.py`` ``S_INTERROG_COMP`` (whose daughter pattern
  is ``PART[COMP_TYPE=INTERROG]`` and whose inner S must have
  ``Q_TYPE=WH``).
* ``kung[COMP_TYPE=COND]`` (Phase 5l Commit 1 lex) is consumed
  only by ``cfg/subordination.py`` ``SubordClause`` (whose
  daughter pattern is ``PART[COMP_TYPE=COND]``).

The two paths fire in disjoint syntactic contexts: INTERROG
needs a wh-inner clause AND a KNOW-class matrix verb that wraps
``S_INTERROG_COMP``; COND needs a subord-clause environment
adjacent to a complete matrix S. There is no known sentence
that produces both a COND and an INTERROG parse — when a sentence
matches one, it does not match the other.

This commit pins the polysemy invariants with parse-count and
f-structure assertions. If a future change introduces a
cross-fire path (e.g., relaxing ``S_INTERROG_COMP``'s
Q_TYPE=WH constraint, or adding a non-finite SubordClause that
overlaps with the indirect-Q shape), these tests flag it.
"""

from __future__ import annotations

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer
from tgllfg.core.pipeline import parse_text


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


def _adjunct_with_subord_type(fs, subord_type: str):
    adjuncts = fs.feats.get("ADJUNCT")
    if adjuncts is None:
        return None
    for adj in adjuncts:
        if adj.feats.get("SUBORD_TYPE") == subord_type:
            return adj
    return None


# === Both lex entries surface ========================================


class TestBothLexEntries:
    """Both ``kung[COND]`` and ``kung[INTERROG]`` must surface
    in the morph analyzer's output for the bare ``kung`` token —
    the chart picks at parse time per rule context."""

    def test_kung_carries_both_comp_types(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kung"))
        comp_types = {
            a.feats.get("COMP_TYPE") for a in out
            if a.pos == "PART"
        }
        assert "COND" in comp_types
        assert "INTERROG" in comp_types

    def test_no_third_kung_entry(self) -> None:
        """Two PART entries exactly — guard against accidental
        third lex entry that would muddy disambiguation."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kung"))
        parts = [a for a in out if a.pos == "PART"]
        assert len(parts) == 2


# === COND-only contexts =============================================


class TestCondOnlyContexts:
    """Sentences that match the COND path produce exactly one
    parse, with a COND adjunct on the matrix and no INTERROG
    artifact anywhere on the f-structure."""

    def test_pre_matrix_unique_parse(self) -> None:
        parses = parse_text("Kung kumain si Maria, pumunta si Juan.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        # No INTERROG marker leaks onto the matrix or the COND f-struct.
        assert fs.feats.get("COMP_TYPE") != "INTERROG"
        assert cond.feats.get("COMP_TYPE") != "INTERROG"

    def test_post_matrix_unique_parse(self) -> None:
        parses = parse_text("Pumunta si Juan kung kumain si Maria.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        cond = _adjunct_with_subord_type(fs, "COND")
        assert cond is not None
        assert fs.feats.get("COMP_TYPE") != "INTERROG"


# === INTERROG-only contexts =========================================


class TestInterrogOnlyContexts:
    """The Phase 5i indirect-Q path produces exactly one parse,
    consuming the kung[INTERROG] lex entry. No COND adjunct
    appears on the matrix because the inner kung-clause is
    consumed by S_INTERROG_COMP, not by SubordClause."""

    def test_indirect_q_unique_parse(self) -> None:
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        # No COND adjunct on the matrix.
        assert _adjunct_with_subord_type(fs, "COND") is None

    def test_indirect_q_carries_interrog_comp(self) -> None:
        """The Phase 5i path lands ``COMP_TYPE=INTERROG`` on the
        complement f-structure. Pin that the marker is present."""
        parses = parse_text("Alam ko kung sino ang kumain.")
        _ct, fs, _astr, _diags = parses[0]
        # The S_INTERROG_COMP rule sets COMP_TYPE=INTERROG on the
        # complement f-structure (cfg/control.py:482). Walk the
        # f-structure to find it — typically as ``COMP`` or
        # similar, depending on how the matrix wrap projects it.
        # For now, just assert that some part of the f-structure
        # tree carries COMP_TYPE=INTERROG.
        assert _has_feat_value_anywhere(fs, "COMP_TYPE", "INTERROG"), (
            "expected COMP_TYPE=INTERROG somewhere in the f-structure "
            "for an indirect-Q parse"
        )


def _has_feat_value_anywhere(fs, feat: str, value: str, _seen=None) -> bool:
    """Walk an f-structure tree (avoiding cycles) looking for
    ``(_ FEAT) = value``. Used to verify COMP_TYPE=INTERROG
    appears somewhere in an indirect-Q parse — the exact GF
    name varies by phase."""
    if _seen is None:
        _seen = set()
    if id(fs) in _seen:
        return False
    _seen.add(id(fs))
    if fs.feats.get(feat) == value:
        return True
    for v in fs.feats.values():
        if hasattr(v, "feats"):
            if _has_feat_value_anywhere(v, feat, value, _seen):
                return True
        elif isinstance(v, (list, tuple, set, frozenset)):
            for item in v:
                if hasattr(item, "feats") and _has_feat_value_anywhere(
                    item, feat, value, _seen
                ):
                    return True
    return False


# === Phase 5i pinned 0-parses preserved =============================


class TestPinnedZeroParsesPreserved:
    """Phase 5i pinned two 0-parse sentences — declarative inner
    and yes/no inner inside ``Alam ko kung X``. The Phase 5l
    SubordClause rule must NOT introduce a parse path that
    flips these to 1+ parses (which would happen if ``Alam ko``
    parsed as a standalone S that could host a COND adjunct;
    in our grammar, KNOW verbs don't appear without their
    complement, so the 0-parse pin holds)."""

    def test_declarative_inner_still_zero(self) -> None:
        parses = parse_text("Alam ko kung kumain ang aso.")
        assert len(parses) == 0

    def test_yes_no_inner_still_zero(self) -> None:
        parses = parse_text("Alam ko kung kumain ka ba.")
        assert len(parses) == 0


# === Nested cross-phase composition =================================


class TestNestedCondInsideInterrog:
    """A wh-Q indirect clause can host its own COND adjunct —
    ``Alam ko kung sino ang kumain kung kumain ang aso.`` "I
    know who ate if the dog ate". The outer kung is INTERROG;
    the inner kung is COND. Both readings of kung fire in the
    same sentence."""

    def test_nested_kungs_parse(self) -> None:
        # Use ``ang aso`` (NOM dog) for the inner conditional's
        # SUBJ, since ``kumain ang aso`` is a clean intransitive
        # AV PFV form and ``aso`` is in the noun lex.
        parses = parse_text(
            "Alam ko kung sino ang kumain kung kumain ang aso."
        )
        # We expect at least 1 parse with the nested polysemy
        # resolution: outer = INTERROG, inner = COND.
        assert len(parses) >= 1, (
            "expected nested-kung composition to parse — "
            "outer kung[INTERROG] wraps wh-inner; inner "
            "kung[COND] adjoins to the wh-inner clause as a "
            "post-matrix conditional"
        )
        _ct, fs, _astr, _diags = parses[0]
        # The nested COND lives somewhere inside the indirect-Q
        # complement.
        assert _has_feat_value_anywhere(fs, "SUBORD_TYPE", "COND"), (
            "expected SUBORD_TYPE=COND somewhere in the nested "
            "f-structure"
        )
        assert _has_feat_value_anywhere(fs, "COMP_TYPE", "INTERROG"), (
            "expected COMP_TYPE=INTERROG somewhere in the nested "
            "f-structure (the outer indirect-Q wrap)"
        )
