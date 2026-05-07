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

    # === Phase 5l Commit 6: temporal SubordClause builders =============
    # — bago "before" / pagkatapos "after"
    #
    # ``SubordClause → PART[COMP_TYPE=TEMP_BEFORE] S``  for ``bago``
    # ``SubordClause → PART[COMP_TYPE=TEMP_AFTER] S``   for ``pagkatapos``
    #
    # Each TEMP_<X> SUBORD_TYPE marks the temporal relation between
    # the matrix and the embedded clause. The matrix attachment rules
    # (a) and (b) above are SUBORD_TYPE-agnostic — temporal
    # SubordClauses attach via the same rules as conditional /
    # concessive SubordClauses. No new attachment rule needed.
    #
    # Commit 7 adds the remaining three temporal builders
    # (habang TEMP_WHILE, hanggang TEMP_UNTIL, ``mula nang`` TEMP_SINCE).
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=TEMP_BEFORE]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'TEMP_BEFORE'",
            "(↓1 COMP_TYPE) =c 'TEMP_BEFORE'",
        ],
    ))
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=TEMP_AFTER]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'TEMP_AFTER'",
            "(↓1 COMP_TYPE) =c 'TEMP_AFTER'",
        ],
    ))

    # === Phase 5l Commit 7: temporal SubordClause builders =============
    # — habang "while" / hanggang "until" / mula nang "since"
    #
    # Three more temporal builders complete the temporal-subord set:
    #
    # ``SubordClause → PART[COMP_TYPE=TEMP_WHILE] S``  for ``habang``
    # ``SubordClause → PART[COMP_TYPE=TEMP_UNTIL] S``  for ``hanggang``
    # ``SubordClause → PREP[PREP_TYPE=SOURCE] PART[COMP_TYPE=TEMP_SINCE] S``
    #     for ``mula nang`` (multi-word lexicalised subordinator)
    #
    # ``mula nang`` reuses the existing Phase 5e ``mula``
    # PREP[PREP_TYPE=SOURCE] entry (no new lex needed for ``mula``)
    # combined with the Phase 5l Commit 1 ``nang`` PART[COMP_TYPE=
    # TEMP_SINCE] entry. PREP_TYPE=SOURCE uniquely identifies mula
    # among PREPs (other PREPs are BENEFICIARY / TOPIC / REASON).
    # The chart admits ``mula sa NP`` (PP) and ``mula nang S``
    # (SubordClause) via different structural shapes — no
    # interference.
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=TEMP_WHILE]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'TEMP_WHILE'",
            "(↓1 COMP_TYPE) =c 'TEMP_WHILE'",
        ],
    ))
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=TEMP_UNTIL]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'TEMP_UNTIL'",
            "(↓1 COMP_TYPE) =c 'TEMP_UNTIL'",
        ],
    ))
    rules.append(Rule(
        "SubordClause",
        [
            "PREP[PREP_TYPE=SOURCE]",
            "PART[COMP_TYPE=TEMP_SINCE]",
            "S",
        ],
        [
            "(↑) = ↓3",
            "(↑ SUBORD_TYPE) = 'TEMP_SINCE'",
            "(↓1 PREP_TYPE) =c 'SOURCE'",
            "(↓2 COMP_TYPE) =c 'TEMP_SINCE'",
        ],
    ))

    # === Phase 5l Commit 8: purpose SubordClause builder ==============
    # — para / upang "in order to"
    #
    # ``SubordClause → PART[COMP_TYPE=PURP] S``
    #
    # Both purpose PARTs (para / upang — Commit 1 lex) feed this
    # one builder. ``upang`` carries REGISTER=FORMAL on its PART
    # f-structure (Commit 1); the register feat percolates onto
    # the SubordClause f-structure via ``(↑) = ↓2``.
    #
    # ``para`` is polysemous with the Phase 5e PREP[BENEFICIARY]
    # entry (``para sa NP`` "for X"). The chart resolves by
    # immediate constituent — PREP path takes a DAT-NP; PART path
    # takes an S. The two contexts don't overlap structurally.
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=PURP]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'PURP'",
            "(↓1 COMP_TYPE) =c 'PURP'",
        ],
    ))

    # === Phase 5l Commit 9: reason SubordClause builder ================
    # — dahil "because"
    #
    # ``SubordClause → PART[COMP_TYPE=REAS] S``
    #
    # ``dahil`` is polysemous with the Phase 5e PREP[REASON] entry
    # (``dahil sa NP`` "because of X"). Same disambiguation
    # mechanic as ``para`` (Commit 8) — chart picks per immediate
    # constituent: PREP path takes a DAT-NP, PART path takes an S.
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=REAS]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'REAS'",
            "(↓1 COMP_TYPE) =c 'REAS'",
        ],
    ))

    # === Phase 5l Commit 13: ay-fronted SubordClause topic ============
    #
    # ``S → SubordClause PART[LINK=AY] S``
    #
    # Discourse-level fronting of a SubordClause as the matrix
    # TOPIC, parallel to Phase 4 §7.4 NP ay-fronting
    # (``Si Maria ay kumain.``). The fronted SubordClause is the
    # TOPIC of the matrix AND a member of ADJUNCT — the
    # f-structure shape matches the non-fronted post-matrix
    # attachment (Commit 2 rule (b)) plus the TOPIC marker.
    #
    # Equations:
    #   (↑) = ↓3                   # matrix is the post-ay S
    #   (↑ TOPIC) = ↓1             # fronted SubordClause is TOPIC
    #   ↓1 ∈ (↑ ADJUNCT)          # also lands in ADJUNCT for
    #                                consistency with non-fronted
    #                                subord shape
    #   (↓2 LINK) =c 'NA' OR ...   # ay-particle is structurally
    #                                consumed (no daughter equation)
    #
    # End-to-end: ``Kung uulan ay hindi ako pupunta.`` "If it
    # rains, then I won't go." — the fronted kung-clause is
    # marked as discourse topic.
    rules.append(Rule(
        "S",
        ["SubordClause", "PART[LINK=AY]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))
