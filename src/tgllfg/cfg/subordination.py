# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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

    # --- Phase 9.W Cluster A/H: pag + bare-N[TIME] + ALREADY body -----
    #
    # ``SubordClause → PART[COMP_TYPE=COND, LEMMA=pag]
    #                  N[SEM_CLASS=TIME] PART[ASPECT_PART=ALREADY]``
    #
    # Closes the temporal-conditional body shape in R&G Intermediate
    # sent-53 ``... pag tanghali na.`` "... when it's already noon."
    # The body is a bare-N temporal-predicate (``tanghali`` "noon")
    # plus the ALREADY aspectual ``na`` — together they form the
    # subordinate clause's "predicate," tense-anchored at ALREADY.
    #
    # The existing rule (a) above admits ``pag S`` where ``S`` is a
    # full clause (or verbless N/ADJ-PRED via Phase 5e Commit 22's
    # anchor). The audit shape doesn't form a full S because the
    # standalone verbless ``Tanghali na.`` fails — the Phase 5e
    # anchor handles bare N-PRED but not N-PRED + ALREADY-clitic
    # cluster (no rule absorbs the trailing clitic when the anchor
    # is a NOUN). Phase 9.W lifts the gap with a dedicated builder
    # that pairs the COND particle directly with N[SEM_CLASS=TIME]
    # + ALREADY, projecting the matrix temporal-pred PRED+ASPECT.
    #
    # Gating:
    # * ``LEMMA = pag`` on ↓1 — narrows to the bare-N temporal
    #   conditional (kung/kapag/sakali don't take this shape; only
    #   ``pag`` admits the bare-N body per S&O 1972 §7.18.5).
    # * ``SEM_CLASS = TIME`` on ↓2 — restricts to temporal-class
    #   nouns (tanghali / umaga / hapon / gabi / etc.), avoiding
    #   false matches against entity-class nouns.
    # * ``ASPECT_PART = ALREADY`` on ↓3 — selects the aspectual
    #   ``na``, not the linker (the disambiguator now keeps both
    #   readings at clause boundaries — see
    #   :func:`tgllfg.clitics.placement._is_post_noun_na_at_clause_boundary`).
    #
    # Projected matrix f-structure: PRED = 'TIME-OF-DAY <SUBJ>'
    # synthesized from the N daughter; ASPECT = PFV (already-state
    # has perfective force); SUBORD_TYPE = TEMP_WHEN (re-tagging
    # for downstream attachment) but admits via the existing
    # COND-attachment rules (since LEMMA=pag is COMP_TYPE=COND).
    rules.append(Rule(
        "SubordClause",
        [
            "PART[COMP_TYPE=COND]",
            # Phase 10.F: bare ``N`` (not the dead c-structure bracket
            # ``N[SEM_CLASS=TIME]`` — ``N`` is a projection non-terminal
            # via ``N → NOUN`` and carries no lexical SEM_CLASS on its
            # category pattern). The TIME gate is the constraining
            # equation ``(↓2 SEM_CLASS) =c 'TIME'`` below.
            "N",
            "PART[ASPECT_PART=ALREADY]",
        ],
        [
            "(↑ SUBORD_TYPE) = 'TEMP_WHEN'",
            "(↑ PRED) = 'TIME-OF-DAY <SUBJ>'",
            "(↑ ASPECT) = 'PFV'",
            "(↑ TIME-N) = ↓2",
            "(↓1 COMP_TYPE) =c 'COND'",
            "(↓1 LEMMA) =c 'pag'",
            "(↓2 SEM_CLASS) =c 'TIME'",
            "(↓3 ASPECT_PART) =c 'ALREADY'",
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

    # --- (d) Post-matrix attachment WITH comma ------------------------
    #
    # ``S → S PUNCT[PUNCT_CLASS=COMMA] SubordClause``
    #
    # Equations:
    #   (↑) = ↓1                       # matrix is the pre-comma S
    #   ↓3 ∈ (↑ ADJUNCT)              # SubordClause joins ADJUNCT set
    #
    # Phase 8.M-bundled Phase 5l completion (anti-deferral). The
    # existing Phase 5l rules cover pre-matrix-with-comma (rule c)
    # and post-matrix-no-comma (rule b), but the post-matrix-WITH-
    # comma shape ``S, kapag/nang/habang/bago/... S`` was missing.
    # Audit-driven corpus pressure: 68 candidates across all
    # temporal/causal/concessive subords (bago=15, para=13,
    # kung=8, kahit=7, habang=7, dahil=6, kasi=4, hanggang=3,
    # pagkatapos=3, nang=2). Directly closes 2 ``nang`` corpus
    # targets (``Nasa daan na si Max, nang bumuhos...``, ``At
    # lumiwanag ang langit, nang huminto...``); the remaining 66
    # candidates fire if their orthogonal OOV/clitic-glue blockers
    # also close.
    rules.append(Rule(
        "S",
        ["S", "PUNCT[PUNCT_CLASS=COMMA]", "SubordClause"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ ADJUNCT)",
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

    # --- Phase 10.J.post-8.5.5: Kahit-ADJ-comma-S concessive ----------
    #
    # ``Kahi't balubaluktot, pinipilit nilang magsalita.``
    #     "Even crookedly, they force themselves to speak."
    #     (R&G 1981 PAG-AARAL/sent-8)
    # ``Kahit malaki, kumain siya.``
    #     "Even though big, he ate."
    #
    # The existing SubordClause builder `PART[CONC] S` requires a
    # FULL inner S with overt SUBJ — `Kahit malaki ka, kumain ka.`
    # parses. The PRO-pivot variant `Kahit ADJ, S` (where the ADJ
    # subject is discourse-recoverable from the matrix clause) is a
    # productive concessive idiom. This rule admits it directly:
    # bare predicative ADJ inside the concessive clause + comma +
    # matrix S.
    #
    # Matrix inherits f-structure from the main clause (`(↑) = ↓4`);
    # the ADJ joins the matrix ADJUNCT set (semantically concessive
    # — "even-X-ly"). PART[LEMMA=kahit] gates this to the specific
    # particle (bagaman / bagamat are too formal for the comma-bare
    # variant; they take full inner S).
    #
    # Closes PAG-AARAL/sent-8 (paired with the PRO-NOM-pivot
    # TRANS-control rule in control.py).
    for link_part_lemma in ("kahit",):
        rules.append(Rule(
            "S",
            [
                f"PART[LEMMA={link_part_lemma}]",
                "ADJ[PREDICATIVE]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                "S",
            ],
            [
                "(↑) = ↓4",
                "↓2 ∈ (↑ ADJUNCT)",
                "(↓1 COMP_TYPE) =c 'CONC'",
                "(↓2 PREDICATIVE) =c true",
                "(↓3 PUNCT_CLASS) =c 'COMMA'",
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

    # === Phase 8.M: TEMP_WHEN SubordClause builder ====================
    # — ``nang`` "when (X happened)"
    #
    # ``SubordClause → PART[COMP_TYPE=TEMP_WHEN] S``  for bare ``nang``
    #
    # Distinct from the Phase 5l C7 ``mula nang`` TEMP_SINCE rule above,
    # which requires the PREP[SOURCE] ``mula`` daughter. The bare-``nang``
    # form heads the audit-named ``Nang dumating si Ben, ...`` (S&O 1972
    # p.196) / ``Nang tamaan siya ng baseball...`` (R&C 1990) class.
    # The ``nang`` PART has TWO lex entries (Phase 8.M particles.yaml):
    # ``TEMP_SINCE`` (only fires composed with ``mula``) and
    # ``TEMP_WHEN`` (fires bare). The chart's =c constraints route each
    # rule to its matching lex variant without spurious ambiguity.
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=TEMP_WHEN]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'TEMP_WHEN'",
            "(↓1 COMP_TYPE) =c 'TEMP_WHEN'",
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

    # === Phase 9.X.c50: bare-V purposive (control SUBJ) ================
    #
    # ``Kumain ako para makatapos.``   "I ate so I could finish."
    # ``Kumain ako para makatapos ng trabaho.``
    #     "I ate so I could finish (some) work."
    # ``Para makatapos ng trabaho, kumain ako.``  (fronted)
    # ``Karaniwan nang gumigising nang maagang-maaga ang mga
    #   Pilipino para makatapos ng trabaho ...``  (PANAHON sent-16)
    #
    # The purposive ``para`` / ``upang`` PART takes a bare V[VOICE=AV,
    # MOOD=NVOL] body without an overt NP-SUBJ — the SUBJ is
    # controlled by the matrix SUBJ (functional-control reading).
    # Three variants:
    #
    #   (a) ``para + V[NVOL]``           — INTR or no overt OBJ
    #   (b) ``para + V[NVOL] + GEN-NP``  — V-TR with overt OBJ
    #   (c) ``para + V[NVOL] + DAT-NP``  — V with sa-PP adjunct
    #
    # LFG analysis: the SubordClause f-structure has the bare V's
    # PRED and a synthesized ``SUBJ PRED = 'PRO'`` placeholder. The
    # control relation between matrix and purposive SUBJ is
    # established at the f-graph by future inside-out designators
    # (Phase 7+); for now the PRO is a discourse-bound placeholder.
    #
    # Variant (b) binds the GEN-NP to the V's OBJ via ``(↓2 OBJ) =
    # ↓3`` (same pattern as the Phase 4 V-TR-OBJ rules); variant (c)
    # rides the DAT-NP into V's ADJUNCT.
    #
    # Reference: Schachter & Otanes 1972 §6.6 (purposive ``para`` /
    # ``upang`` with control reading); R&G 1981 PANAHON sent-16.
    for mood in ("SOC", "NVOL"):
        rules.append(Rule(
            "SubordClause",
            ["PART[COMP_TYPE=PURP]", f"V[VOICE=AV, MOOD={mood}, TR=INTR]"],
            [
                "(↑) = ↓2",
                "(↑ SUBJ PRED) = 'PRO'",
                "(↑ SUBORD_TYPE) = 'PURP'",
                "(↓1 COMP_TYPE) =c 'PURP'",
            ],
        ))
        rules.append(Rule(
            "SubordClause",
            ["PART[COMP_TYPE=PURP]", f"V[VOICE=AV, MOOD={mood}, TR=TR]"],
            [
                "(↑) = ↓2",
                "(↑ SUBJ PRED) = 'PRO'",
                "(↑ OBJ PRED) = 'PRO'",
                "(↑ SUBORD_TYPE) = 'PURP'",
                "(↓1 COMP_TYPE) =c 'PURP'",
            ],
        ))
        rules.append(Rule(
            "SubordClause",
            ["PART[COMP_TYPE=PURP]", f"V[VOICE=AV, MOOD={mood}]", "NP[CASE=GEN]"],
            [
                "(↑) = ↓2",
                "(↑ SUBJ PRED) = 'PRO'",
                "(↑ OBJ) = ↓3",
                "(↑ SUBORD_TYPE) = 'PURP'",
                "(↓1 COMP_TYPE) =c 'PURP'",
            ],
        ))
        rules.append(Rule(
            "SubordClause",
            ["PART[COMP_TYPE=PURP]", f"V[VOICE=AV, MOOD={mood}]", "NP[CASE=DAT]"],
            [
                "(↑) = ↓2",
                "(↑ SUBJ PRED) = 'PRO'",
                "↓3 ∈ (↑ ADJUNCT)",
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

    # --- Phase 9.X.c49: ``sapagkat`` cause subordinator --------------
    #
    # ``Sapagka't umulan, basa ang lupa.``
    #     "Because it rained, the ground is wet."
    # ``At sapagka't kung umulan man ay di gaanong malakas, marami
    #     ring kapistahan sa panahong ito.``   (PANAHON sent-35)
    #
    # Parallel to the Phase 5l Commit 9 ``dahil`` reason-subordinator
    # rule above. ``sapagkat`` (PART[SUBORDINATOR=true,
    # COMP_TYPE=CAUSE, LEMMA=sapagkat]) heads a SubordClause taking
    # an S body. The tokenizer's ``split_apostrophe_t`` normalizes
    # surface ``sapagka't`` to lemma ``sapagkat``.
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=CAUSE]", "S"],
        [
            "(↑) = ↓2",
            "(↑ SUBORD_TYPE) = 'CAUSE'",
            "(↓1 COMP_TYPE) =c 'CAUSE'",
        ],
    ))

    # --- 9.X.c15: compound ``dahil sa + clause`` subordinator ---------
    #
    # ``Dahil sa tuyo ang lupa ay makapal ang alikabok.``
    #     "Because the ground is dry, the dust is thick"
    #     (R&G 1981 PANAHON sent-11).
    #
    # Tagalog admits two variants of the reason-subordinator:
    #
    #   ``dahil [S]``          — bare PART + S (Phase 5l C9 rule above)
    #   ``dahil sa [S]``       — PART + ``sa`` marker + S (this commit)
    #
    # The ``sa`` is treated as a structural marker introducing the
    # cause clause; it is structurally consumed (no equation refers
    # to ↓2). Compositionally this parallels the PREP-form ``dahil
    # sa NP`` (PREP+NP[DAT]) but the daughter is a clausal S
    # instead of an NP, taking the SubordClause path.
    #
    # Disambiguation against the PREP path is automatic: the PREP
    # rule (``PP → PREP NP[CASE=DAT]``) requires an NP daughter,
    # while this SubordClause rule requires an S daughter. The
    # chart picks per immediate constituent.
    #
    # Reference: R&G 1981 §6.6 (compound subordinators); R&G 1981
    # PANAHON essay (sent-11).
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=REAS]", "ADP[CASE=DAT]", "S"],
        [
            "(↑) = ↓3",
            "(↑ SUBORD_TYPE) = 'REAS'",
            "(↓1 COMP_TYPE) =c 'REAS'",
            "(↓1 LEMMA) =c 'dahil'",
            "(↓2 MARKER) =c 'SA'",
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

    # === Phase 9.X.c49: SubordClause ay [bare ADJ-pred] (topic-drop apodosis) ===
    #
    # ``Kung umulan man ay di gaanong malakas, ...``
    #     "Even if it rains, it isn't so strong, ..." (R&G 1981
    #     PANAHON sent-35).
    # ``Kapag malakas ay tatakbo.``  (constructed)
    #
    # When a SubordClause is ay-fronted as TOPIC and the apodosis
    # is a bare ADJ-pred without overt NP-SUBJ, the apodosis's
    # SUBJ is bound by the discourse-set context (the SubordClause
    # itself supplies the referent). LFG analysis: synthesize
    # ``SUBJ PRED = 'PRO'`` on the matrix; the PRO is contextually
    # bound to the discourse-supplied entity from the SubordClause.
    #
    # Two variants: bare apodosis (``ay malakas``) and NEG-wrapped
    # apodosis (``ay di malakas``, ``ay di gaanong malakas``). The
    # NEG variant absorbs the ``di`` particle directly into the
    # rule rather than chaining through the generic NEG-wrap
    # (since the inner ADJ-pred isn't itself a complete S without
    # this rule firing first).
    #
    # Reference: R&G 1981 PANAHON sent-35; Schachter & Otanes 1972
    # §9.4 (topic-drop and discourse-bound zero anaphora).
    rules.append(Rule(
        "S",
        ["SubordClause", "PART[LINK=AY]", "ADJ[PREDICATIVE]"],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ ADJ_LEMMA) = ↓3 LEMMA",
            "(↑ SUBJ PRED) = 'PRO'",
            "(↑ PREDICATIVE) = true",
            "(↓3 PREDICATIVE) =c true",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))
    rules.append(Rule(
        "S",
        ["SubordClause", "PART[LINK=AY]", "PART[POLARITY=NEG]", "ADJ[PREDICATIVE]"],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ ADJ_LEMMA) = ↓4 LEMMA",
            "(↑ SUBJ PRED) = 'PRO'",
            "(↑ PREDICATIVE) = true",
            "(↑ POLARITY) = 'NEG'",
            "(↓3 POLARITY) =c 'NEG'",
            "(↓4 PREDICATIVE) =c true",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))
