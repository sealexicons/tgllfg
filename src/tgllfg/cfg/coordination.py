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
_BINARY_CLAUSAL_COORDS: tuple[str, ...] = ("AND", "OR", "BUT")


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

    # --- Phase 5k Commit 4: multi-conjunct NP coord (3-flat) ---
    #
    # Two surface variants per case, six rules total:
    #
    #   Oxford comma form ("Si Maria, si Juan, at si Pedro"):
    #     NP[CASE=X] → NP[CASE=X] PUNCT[COMMA] NP[CASE=X]
    #                  PUNCT[COMMA] PART[COORD=AND] NP[CASE=X]
    #
    #   Non-Oxford form  ("Si Maria, si Juan at si Pedro"):
    #     NP[CASE=X] → NP[CASE=X] PUNCT[COMMA] NP[CASE=X]
    #                  PART[COORD=AND] NP[CASE=X]
    #
    # for each case X ∈ {NOM, GEN, DAT}. Both Oxford and non-Oxford
    # comma conventions are attested in modern Tagalog written
    # practice; both rules produce the same flat 3-element
    # CONJUNCTS set. PUNCT[COMMA] daughters are syncategorematic
    # (no equation refers to them); the matrix carries COORD=AND,
    # NUM=PL, and the per-case CASE.
    #
    # Equations (Oxford NOM example, 6 daughters):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓3 ∈ (↑ CONJUNCTS)
    #   ↓6 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'AND'
    #   (↑ CASE) = 'NOM'
    #   (↑ NUM) = 'PL'
    #   (↓5 COORD) =c 'AND'
    #
    # Equations (non-Oxford NOM example, 5 daughters):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓3 ∈ (↑ CONJUNCTS)
    #   ↓5 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'AND'
    #   (↑ CASE) = 'NOM'
    #   (↑ NUM) = 'PL'
    #   (↓4 COORD) =c 'AND'
    #
    # Restricted to AND only — disjunctive ``Maria, Juan, o
    # Pedro`` is structurally rare in Tagalog and deferred to a
    # Phase 5k follow-on if corpus pressure surfaces.
    #
    # Restricted to 3 conjuncts only — 4+ conjuncts would compose
    # via the binary rule wrapping a 3-conjunct sub-NP, which
    # produces a NESTED CONJUNCTS structure (not a flat 4-element
    # set). Right-recursive ``NP_COMMA_LIST`` for arbitrary arity
    # is deferred per plan-of-record §5.3 / §9.2 until corpus
    # pressure shows ≥4-conjunct sentences.
    #
    # PUNCT[COMMA] daughter consumption: the comma is now lex'd
    # (Phase 5k Commit 1 added PUNCT[PUNCT_CLASS=COMMA]) so it
    # survives ``_strip_non_content``. The 3-conjunct rules here
    # are the primary structural consumer of comma daughters in
    # Phase 5k; the asymmetric coord rule (Commit 8) is the
    # second.
    for case in _NP_CASES:
        # Oxford-comma form (6 daughters).
        rules.append(Rule(
            f"NP[CASE={case}]",
            [
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                "PART[COORD=AND]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                "↓6 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓5 COORD) =c 'AND'",
            ],
        ))
        # Non-Oxford form (5 daughters).
        rules.append(Rule(
            f"NP[CASE={case}]",
            [
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"NP[CASE={case}]",
                "PART[COORD=AND]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                "↓5 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓4 COORD) =c 'AND'",
            ],
        ))

    # --- Phase 5k Commit 5: binary clausal coordination ---
    #
    # ``S → S PART[COORD=Y] S`` for each coord value Y ∈ {AND, OR}.
    # Two rules total. Same shape as the Commit 3 binary NP-coord
    # rules but at the S level: each conjunct clause is its own
    # f-structure (with its own PRED, SUBJ, voice/aspect/mood),
    # and the matrix coord-S carries a flat 2-element CONJUNCTS
    # set + a COORD value, with NO PRED of its own.
    #
    # No PRED on the matrix coord-S is the canonical LFG analysis
    # for non-asymmetric coordination — the matrix doesn't
    # introduce a second-order predication; it merely organizes
    # its conjuncts. The LMT subject-condition check skips
    # PRED-less f-structures, so the matrix is admitted without
    # complaint.
    #
    # Equations (additive, S-level):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓3 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'AND'
    #   (↓2 COORD) =c 'AND'
    #
    # The OR variant percolates COORD='OR'. The Phase 5k Commit 6
    # adversative variant (pero / ngunit / subalit — all
    # PART[COORD=BUT]) and Commit 7 consequence variant (kaya —
    # PART[COORD=SO]) extend this binary shape via additional
    # COORD values in :data:`_BINARY_CLAUSAL_COORDS`. The three
    # adversative lex surfaces all carry COORD=BUT (Commit 1 lex);
    # one rule covers all three.
    #
    # Negation × clausal coord (Commit 8 tests): the existing
    # Phase 4 §7.2 hindi-wrap composes with the inner conjunct S
    # unchanged — local-scoping reading. ``Hindi kumain si Maria
    # at uminom si Juan.`` parses as
    # ``[hindi kumain si Maria] AND [uminom si Juan]`` with
    # POLARITY=NEG only on the first conjunct. Cross-conjunct
    # negation scoping (``Hindi [si Maria at si Juan] kumain.``
    # "Neither X nor Y") is a separate rule deferred per plan §9.2.
    for coord in _BINARY_CLAUSAL_COORDS:
        rules.append(Rule(
            "S",
            [
                "S",
                f"PART[COORD={coord}]",
                "S",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                f"(↑ COORD) = '{coord}'",
                f"(↓2 COORD) =c '{coord}'",
            ],
        ))
