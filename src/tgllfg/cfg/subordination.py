# tgllfg/cfg/subordination.py

"""Subordination rules: subordinate-clause embeddings.

After the post-Phase-5f grammar split (see
``docs/refactor-grammar-package.md``) this module owns every rule
that participates in subordination — conditional (kung / kapag /
pag / sakali), concessive (kahit / bagaman), temporal
(bago / pagkatapos / habang / hanggang / ``mula nang``), purpose
(para / upang), reason (dahil), and the matrix-attachment rules
that lift a SubordClause onto a matrix S as an ADJUNCT member.

Phase 5l Commit 2 lands the foundation:

* The ``SubordClause`` non-terminal that wraps an inner S with a
  COMP-typed PART head and overlays SUBORD_TYPE on its f-structure.
* The two SUBORD_TYPE-agnostic matrix-attachment rules (post-matrix
  without comma, pre-matrix with comma) that join a SubordClause
  to its matrix as an ``ADJUNCT`` member.
* The conditional family (COMP_TYPE=COND): one SubordClause
  builder that fires for any of kung / kapag / pag / sakali.

Subsequent commits (4-9) add more SubordClause-builder rules for
the remaining COMP_TYPEs (CONC, TEMP_*, PURP, REAS); the matrix
attachers from this commit lift all of them.

Analytical commitments (Phase 5l plan-of-record §2):

* **Subord clause as ADJUNCT.** The subord clause is a member of
  the matrix's ``ADJUNCT`` set (``↓N ∈ (↑ ADJUNCT)``). The matrix
  S's f-structure is identical to its inner clause's (PRED / SUBJ /
  OBJ all from the inner clause); the SubordClause f-structure
  joins ADJUNCT.
* **SubordClause f-structure = inner-clause f-structure + overlay.**
  ``(↑) = ↓2`` makes the SubordClause f-structure structurally
  identical to its inner S. ``(↑ SUBORD_TYPE) = '<X>'`` overlays
  the subord-type marker. The inner clause's PRED / SUBJ / etc.
  are visible on the SubordClause f-structure (so a downstream
  consumer walking the matrix's ADJUNCT set can dive into a
  subord-clause member and read its predicate).
* **Pre-matrix and post-matrix subord clauses produce identical
  f-structures.** Only c-tree differs: pre-matrix has
  ``S → SubordClause PUNCT[COMMA] S``; post-matrix has
  ``S → S SubordClause``. The Phase 5k comma lex
  (``PUNCT[PUNCT_CLASS=COMMA]``) is the structural daughter for
  the pre-matrix form.

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
after coordination and before discourse — see the plan's
"Migration strategy" §H.
"""

from __future__ import annotations

from .grammar import Rule


def register_rules(rules: list[Rule]) -> None:
    """Append the subordination-area rules in source order."""
    # === Phase 5l Commit 2: matrix attachment + conditional ==============
    #
    # Two SUBORD_TYPE-agnostic matrix attachers + one conditional
    # SubordClause builder. Subsequent Phase 5l commits add more
    # SubordClause-builder rules for the other COMP_TYPEs; the
    # attachers stay generic.

    # --- (a) Conditional SubordClause builder -------------------------
    #
    # ``SubordClause → PART[COMP_TYPE=COND] S``
    #
    # Equations:
    #   (↑) = ↓2                       # f-structure identity with inner
    #   (↑ SUBORD_TYPE) = 'COND'      # subord-type overlay
    #   (↓1 COMP_TYPE) =c 'COND'      # belt-and-braces (matches the
    #                                   non-conflict category-pattern
    #                                   matcher's restriction)
    #
    # All four conditional PART entries (kung / kapag / pag / sakali —
    # Phase 5l Commit 1 lex) feed the same builder; the chart picks
    # the right entry from the input token. The Phase 5i
    # ``COMP_TYPE=INTERROG`` reading of ``kung`` does NOT fire here
    # because the daughter category pattern requires COMP_TYPE=COND.
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=COND]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'COND'",
            "(↓1 COMP_TYPE) =c 'COND'",
        ],
    ))

    # --- (b) Post-matrix attachment (no comma) ------------------------
    #
    # ``S → S SubordClause``
    #
    # Equations:
    #   (↑) = ↓1                       # matrix f-structure is the
    #                                   matrix S's inner f-structure
    #   ↓2 ∈ (↑ ADJUNCT)              # SubordClause joins ADJUNCT set
    #
    # SUBORD_TYPE-agnostic — any well-formed SubordClause attaches.
    rules.append(Rule(
        "S",
        ["S", "SubordClause"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
        ],
    ))

    # --- (c) Pre-matrix attachment (with comma) -----------------------
    #
    # ``S → SubordClause PUNCT[PUNCT_CLASS=COMMA] S``
    #
    # Equations:
    #   (↑) = ↓3                       # matrix is the post-comma S
    #   ↓1 ∈ (↑ ADJUNCT)              # SubordClause joins ADJUNCT set
    #
    # The comma is structurally consumed (Phase 5k Commit 1 lex'd
    # ``,`` as ``PUNCT[PUNCT_CLASS=COMMA]``); pre-matrix subord
    # without a comma is not in scope (corpus convention is the
    # comma boundary is part of the construction).
    rules.append(Rule(
        "S",
        ["SubordClause", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))

    # === Phase 5l Commit 4: concessive SubordClause builder ============
    #
    # ``SubordClause → PART[COMP_TYPE=CONC] S``
    #
    # Equations:
    #   (↑) = ↓2                       # f-structure identity
    #   (↑ SUBORD_TYPE) = 'CONC'      # subord-type overlay
    #   (↓1 COMP_TYPE) =c 'CONC'      # belt-and-braces
    #
    # Both concessive PARTs (kahit / bagaman — Commit 1 lex) feed
    # this builder. ``bagaman`` carries ``REGISTER=FORMAL`` on its
    # PART f-structure (Commit 1); the register feat percolates
    # onto the SubordClause f-structure via the ``(↑) = ↓2`` lift
    # if any future code wants to tell the variants apart.
    #
    # The matrix attachment rules (a) and (b) above are SUBORD_TYPE-
    # agnostic — concessive SubordClauses attach to their matrix
    # via the same post-matrix / pre-matrix-comma rules as
    # conditional SubordClauses. No new attachment rule needed.
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=CONC]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'CONC'",
            "(↓1 COMP_TYPE) =c 'CONC'",
        ],
    ))
