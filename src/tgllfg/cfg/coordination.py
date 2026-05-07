# tgllfg/cfg/coordination.py

"""Coordination rules: NP-level + clausal binary coordination.

After the post-Phase-5f grammar split (see
``docs/refactor-grammar-package.md``) this module owns every rule
that participates in coordination — at, o, pero, ngunit, subalit,
kaya, asymmetric (Si Maria, hindi si Juan), multi-conjunct (Oxford
comma + at). Phase 5k Commit 3 lands the binary NP-level baseline;
Commits 4-8 extend with multi-conjunct / clausal / adversative /
consequence / asymmetric forms.

Analytical commitments (Phase 5k plan-of-record §2):

* Coordinators are PART-typed clause / NP-typers (Commit 1 lex),
  lifting COORD onto the matrix without introducing a coord-PRED.
* Coord matrix structure is a set-valued ``CONJUNCTS`` feature
  re-using the Phase 5j ``↓N ∈ (↑ SET)`` operator. Each conjunct's
  f-structure is a member of CONJUNCTS; non-distributive features
  (COORD, NUM=PL for additive, CASE) live on the matrix.
* NP-level CASE agreement is enforced by parallel category-pattern
  daughters (``NP[CASE=NOM]`` × 2 for the NOM-coord rule, etc.);
  mismatched-CASE conjuncts simply don't match any rule and so
  fail to compose at the chart layer.
* Additive ``at`` forces NUM=PL on the matrix (semantically
  two-or-more); disjunctive ``o`` percolates NUM from the first
  conjunct (``Maria o si Juan`` is sg-with-disjunct).

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
after control and before discourse — see the plan's "Migration
strategy" §H.
"""

from __future__ import annotations

from .grammar import Rule

_NP_CASES: tuple[str, ...] = ("NOM", "GEN", "DAT")


def register_rules(rules: list[Rule]) -> None:
    """Append the coordination-area rules in source order."""
    # --- Phase 5k Commit 3: binary NP coordination ---
    #
    # ``NP[CASE=X] → NP[CASE=X] PART[COORD=Y] NP[CASE=X]`` for each
    # case X ∈ {NOM, GEN, DAT} and each coord value Y ∈ {AND, OR}.
    # Six rules total = 3 cases × 2 coord values. Both conjuncts must
    # share CASE — enforced by the parallel category-pattern daughters
    # (no equation needed).
    #
    # Equations (additive, NOM example):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓3 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'AND'
    #   (↑ CASE) = 'NOM'
    #   (↑ NUM) = 'PL'
    #   (↓2 COORD) =c 'AND'
    #
    # The matrix is a fresh f-structure: neither conjunct IS the
    # matrix (no ``(↑) = ↓N`` lift) — both are ELEMENTS of the
    # CONJUNCTS set. Non-distributive features (COORD, NUM, CASE)
    # land on the matrix; per-conjunct features (PRED, LEMMA,
    # POSSESSOR, modifier sets) stay on each conjunct's f-structure.
    #
    # The ``(↓2 COORD) =c 'Y'`` belt-and-braces constraint matches
    # the precedent set by Phase 5j (existential / locative /
    # modal control wrap rules) — the daughter category pattern
    # already restricts to ``PART[COORD=Y]`` but the constraining
    # equation guards against any future shape regression where
    # the pattern's specificity loosens.
    #
    # NUM behavior differs between additive and disjunctive:
    # ``Si Maria at si Juan`` is plural (semantically two referents);
    # ``Si Maria o si Juan`` is singular-with-disjunct (one
    # underspecified referent). The plan-of-record §2 / §5.2 specs
    # the AND-forces-PL / OR-percolates-NUM split.
    for case in _NP_CASES:
        # Additive (at) — NUM forced to PL.
        rules.append(Rule(
            f"NP[CASE={case}]",
            [
                f"NP[CASE={case}]",
                "PART[COORD=AND]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓2 COORD) =c 'AND'",
            ],
        ))
        # Disjunctive (o) — NUM percolates from the first conjunct.
        rules.append(Rule(
            f"NP[CASE={case}]",
            [
                f"NP[CASE={case}]",
                "PART[COORD=OR]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'OR'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = ↓1 NUM",
                "(↓2 COORD) =c 'OR'",
            ],
        ))
