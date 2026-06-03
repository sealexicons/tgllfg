# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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

from .grammar import Rule

_NP_CASES: tuple[str, ...] = ("NOM", "GEN", "DAT")
_BINARY_CLAUSAL_COORDS: tuple[str, ...] = ("AND", "OR", "BUT", "SO")


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
        # Additive (at) — NUM forced to PL. LHS advertises
        # ``COORD=AND`` for the Phase 6.C graph-constraint matcher
        # (parent rules like the L78 wide-scope hindi rule and the
        # L83 fragment-S rule expect ``NP[..., COORD=AND]``).
        rules.append(Rule(
            f"NP[CASE={case}, COORD=AND]",
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
            f"NP[CASE={case}, COORD=OR]",
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

    # --- Phase 10.J.post-12.8: NP-coord with discourse marker + comma ---
    #
    # ``Sa panahon ding ito dinaraos ang mga piyesta at siyempre pa,
    #   ang Mahal na Araw para sa mga Kristiyano.``
    #     "At this very time the fiestas are held, and of course also,
    #      the Holy Week for the Christians." (PANAHON/sent-10)
    #
    # Variant of the Phase 5k Commit 3 NP-coord rule that admits a
    # sentence-initial discourse marker + comma between the coordinator
    # and the second conjunct: ``NP at DISC, NP`` for ``at`` / ``o``.
    #
    # The discourse marker (``siyempre`` / ``samakatuwid`` / ``gayon din``
    # / ``alalaong baga`` / etc.) is the same chart-level
    # ``PART[DISCOURSE_POS=SENTENCE_INITIAL]`` symbol used by Phase 5m
    # C4's ``S → PART[DISCOURSE_POS=SENTENCE_INITIAL] S`` and Phase
    # 9.V.4b's comma variant. Lex-listed single-word PARTs (siyempre,
    # samakatuwid, ...) and rule-built multi-word PARTs (gayon din,
    # bukod dito, una sa lahat, alalaong baga) both feed this slot.
    #
    # The ``pa`` clitic in ``siyempre pa,`` is handled by
    # ``reorder_clitics``: as a 2P clitic with no anchor in the
    # narrow-adjacency exception list, it hoists to clause-final
    # before chart construction, leaving ``at siyempre , NP`` at the
    # chart's input. The discourse marker stays in coord-medial
    # position because ``DISCOURSE_POS=SENTENCE_INITIAL`` is treated
    # by the placement engine as a non-clitic anchor (see
    # ``_is_sentence_initial_particle``).
    #
    # Each conjunct goes into ``CONJUNCTS`` (set-valued) per the
    # Phase 5k matrix-pattern; the discourse PART lands in
    # ``ADJUNCT`` (set-valued) of the matrix, paralleling the
    # Phase 5m C4 rule's ``↓1 ∈ (↑ ADJUNCT)`` treatment of the
    # sentence-initial PART.
    for case in _NP_CASES:
        # Additive (at) variant
        rules.append(Rule(
            f"NP[CASE={case}, COORD=AND]",
            [
                f"NP[CASE={case}]",
                "PART[COORD=AND]",
                "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓5 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓2 COORD) =c 'AND'",
            ],
        ))
        # Disjunctive (o) variant
        rules.append(Rule(
            f"NP[CASE={case}, COORD=OR]",
            [
                f"NP[CASE={case}]",
                "PART[COORD=OR]",
                "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓5 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ COORD) = 'OR'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = ↓1 NUM",
                "(↓2 COORD) =c 'OR'",
            ],
        ))

    # (Phase 10.J.post-1 binary comma+at coord moved to pipeline-level
    # synthesis — see _try_comma_at_np_split in core/pipeline.py)
    #
    # (Phase 10.J.post-8.5.5.1 chart-level bare-comma 2-way NP-coord
    # was prototyped but dropped: an attributed-exemplar scan found
    # ZERO standalone ``<pred> ang X, ang Y`` bare-comma 2-way
    # attestations across waves 1-5; the only attested case is
    # PAMILYA/sent-14's ``<pred> NP1, NP2, lalo na't S`` (always with
    # discourse continuation). A general chart rule would require
    # corpus-tuned gates ``¬ (↓3 COORD)`` etc. that have no clear
    # linguistic anchor outside that specific shape. Moved to
    # pipeline-level synthesis in core/pipeline.py — see
    # ``_try_lalo_nat_split`` and its SUBJ-bare-comma fallback.)
    #
    # **Future corpus pressure to watch**: if attested exemplars of
    # standalone ``<pred> ang X, ang Y.`` (bare-comma 2-way without
    # any discourse continuation) emerge in future audit waves, the
    # decision point would be (a) extend the pipeline-level synthesis
    # to recognize end-of-sentence as a discourse-continuation
    # surrogate, or (b) revisit a chart rule with cleaner gates. The
    # current corpus scan (post-8.5.5.1 development, 6036-sent
    # baseline) leaves the construction unattested.


    # --- Phase 10.J.post-8.5.2: V-at-V coord under ang headless-RC -----
    #
    # ``Siya ang nasusunod at nagpapasya para sa pamilya.``
    #     "She is the one followed and (the one who) decides for the family."
    #     (PAMILYA/sent-7)
    # ``Siya ang kumakain at uminom.``  "She is the one eating and drinking."
    # ``Ang nasusunod at nagpapasya``   "the one followed and deciding"
    #
    # The existing headless-RC wrap ``NP[CASE=X] → DET[CASE=X] S_GAP``
    # (extraction.py:1697) admits a single S_GAP body — typically a bare
    # ``V[VOICE=AV]`` (extraction.py:65-69). For multi-V coordination
    # under a single ``ang`` (the pseudo-cleft / equational headless-NP
    # construction), we need ``S_GAP`` to itself support coord:
    #
    #     S_GAP → S_GAP PART[COORD=AND] S_GAP
    #     S_GAP → S_GAP PART[COORD=OR]  S_GAP
    #
    # Each conjunct is a SUBJ-gapped clause; the matrix headless-RC
    # wrap binds the matrix NP to ``S_GAP REL-PRO``. By unifying both
    # conjuncts' REL-PRO with the matrix REL-PRO, both V daughters
    # share their SUBJ pivot with the matrix NP (the canonical
    # "single referent who does V1 and V2" reading).
    #
    # Mirrors the NP-coord pattern above (CONJUNCTS set, ``COORD``
    # advertised on the LHS, ``=c`` constraint on the conjunction
    # daughter). The OR variant covers ``ang nasusunod o nagpapasya``
    # "the one followed or deciding" — same SUBJ-sharing semantics.
    #
    # Anti-deferral closure (Phase 10.J.post-8.5.2 in-PR): the
    # `Nasusunod ang batas.`-style standalone gap was a structural
    # symptom; the actual wave-1 yield is PAMILYA/sent-7 once paired
    # with ``pasya`` ``AV_ABSOL=true`` and ``sunod`` ``ma`` cell.
    for coord in ("AND", "OR"):
        # Bare S_GAP LHS so the existing headless-RC wrap
        # (NP[CASE=X] → DET[CASE=X] S_GAP) admits the coord output
        # without itself needing a COORD-aware variant. The matrix
        # inherits f-structure from the first conjunct (matches the
        # Phase 5g manner-style ADJ+LK+S rule's pattern). Both
        # conjuncts share the matrix's SUBJ — when the headless-RC
        # wrap later binds matrix SUBJ to the head NP, both V
        # daughters see it as their pivot.
        rules.append(Rule(
            "S_GAP",
            [
                "S_GAP",
                f"PART[COORD={coord}]",
                "S_GAP",
            ],
            [
                "(↑) = ↓1",
                "↓3 ∈ (↑ CONJUNCTS)",
                "(↓3 SUBJ) = (↑ SUBJ)",
                f"(↓2 COORD) =c '{coord}'",
            ],
        ))


    # --- Phase 10.J.post-12.11: S_XCOMP coord (binary + 3-conjunct) -----
    #
    # ``Sa kabilang dako ay tungkulin niyang pakainin, bigyan ng
    #   matitirhan at pag-aralin ang mga miyembro ng kanyang pamilya.``
    #     (PAMILYA/sent-8 — V-V-V coord embedded under the N-predicate
    #     control wrap added in cfg/clause.py)
    # ``Tungkulin niyang aralin at pag-aralin si Pedro.`` "His duty is
    #     to teach Pedro and (cause to) study him." (constructed binary)
    #
    # Parallel to the Phase 10.J.post-8.5.2 S_GAP coord rule above:
    # each conjunct is an S_XCOMP (control complement); the coord
    # joins them at the S_XCOMP level so the matrix N-predicate-control
    # wrap can lift the coord output as a single XCOMP. Two shapes:
    #
    # Binary (``V1 at V2``): ``S_XCOMP → S_XCOMP PART[COORD=Y] S_XCOMP``
    # 3-conjunct non-Oxford (``V1, V2 at V3``):
    #     ``S_XCOMP → S_XCOMP PUNCT[COMMA] S_XCOMP PART[COORD=Y] S_XCOMP``
    #
    # CONJUNCTS / COORD propagation mirrors the NP-coord pattern at
    # lines 79-115. Each conjunct's REL-PRO unifies with the matrix
    # REL-PRO so the outer control wrap's `(↑ SUBJ) = (↑ XCOMP REL-PRO)`
    # binding propagates through coord to each conjunct — every V in
    # the coord shares its actor-gap with the matrix SUBJ.
    #
    # 3-conjunct Oxford (``V1, V2, at V3``) deferred — no audit-corpus
    # attestation. The non-Oxford form is what PAMILYA/sent-8 uses.
    for coord in ("AND", "OR"):
        # Binary S_XCOMP coord
        rules.append(Rule(
            "S_XCOMP",
            [
                "S_XCOMP",
                f"PART[COORD={coord}]",
                "S_XCOMP",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                f"(↑ COORD) = '{coord}'",
                f"(↓2 COORD) =c '{coord}'",
                "(↑ REL-PRO) = ↓1 REL-PRO",
                "(↑ REL-PRO) = ↓3 REL-PRO",
            ],
        ))
        # 3-conjunct non-Oxford (V1, V2 at V3)
        rules.append(Rule(
            "S_XCOMP",
            [
                "S_XCOMP",
                "PUNCT[PUNCT_CLASS=COMMA]",
                "S_XCOMP",
                f"PART[COORD={coord}]",
                "S_XCOMP",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                "↓5 ∈ (↑ CONJUNCTS)",
                f"(↑ COORD) = '{coord}'",
                f"(↓4 COORD) =c '{coord}'",
                "(↑ REL-PRO) = ↓1 REL-PRO",
                "(↑ REL-PRO) = ↓3 REL-PRO",
                "(↑ REL-PRO) = ↓5 REL-PRO",
            ],
        ))


    # --- Phase 5k Commit 4 + Phase 5n.A Commit 20: 3-flat coord ---
    #
    # Two surface variants per case × two coord values, twelve rules
    # total:
    #
    #   Oxford comma form ("Si Maria, si Juan, at si Pedro"):
    #     NP[CASE=X] → NP[CASE=X] PUNCT[COMMA] NP[CASE=X]
    #                  PUNCT[COMMA] PART[COORD=Y] NP[CASE=X]
    #
    #   Non-Oxford form  ("Si Maria, si Juan at si Pedro"):
    #     NP[CASE=X] → NP[CASE=X] PUNCT[COMMA] NP[CASE=X]
    #                  PART[COORD=Y] NP[CASE=X]
    #
    # for each case X ∈ {NOM, GEN, DAT} and each coord
    # Y ∈ {AND, OR}. Both Oxford and non-Oxford comma conventions
    # are attested in modern Tagalog written practice; both rules
    # produce the same flat 3-element CONJUNCTS set. PUNCT[COMMA]
    # daughters are syncategorematic (no equation refers to them);
    # the matrix carries the per-case CASE and per-coord COORD.
    #
    # NUM behaviour mirrors the binary forms (lines 78–112 above):
    # AND forces ``(↑ NUM) = 'PL'`` (semantically n referents);
    # OR percolates ``(↑ NUM) = ↓1 NUM`` (one underspecified
    # referent — same as the binary disjunction). The Phase 5n.A
    # Commit 20 disjunctive form closes the §18 L86 deferral and
    # supersedes the prior "Restricted to AND only" note from
    # Commit 4.
    #
    # Equations (Oxford NOM AND example, 6 daughters):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓3 ∈ (↑ CONJUNCTS)
    #   ↓6 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'AND'
    #   (↑ CASE) = 'NOM'
    #   (↑ NUM) = 'PL'
    #   (↓5 COORD) =c 'AND'
    #
    # Equations (non-Oxford NOM AND example, 5 daughters):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓3 ∈ (↑ CONJUNCTS)
    #   ↓5 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'AND'
    #   (↑ CASE) = 'NOM'
    #   (↑ NUM) = 'PL'
    #   (↓4 COORD) =c 'AND'
    #
    # 4+ conjuncts: see the recursive ``NP_LONG_LIST`` infrastructure
    # in Commit 19 / 19a below. The 3-conjunct rules here are the
    # primary structural consumer of comma daughters in Phase 5k;
    # the asymmetric coord rule (Commit 8) is the second.
    #
    # PUNCT[COMMA] daughter consumption: the comma is now lex'd
    # (Phase 5k Commit 1 added PUNCT[PUNCT_CLASS=COMMA]) so it
    # survives ``_strip_non_content``.
    _3CONJ_NUM_BY_COORD = {"AND": "'PL'", "OR": "↓1 NUM"}
    for case in _NP_CASES:
        for coord, num_rhs in _3CONJ_NUM_BY_COORD.items():
            # Oxford-comma form (6 daughters). LHS advertises COORD
            # for the Phase 6.C graph-constraint matcher.
            rules.append(Rule(
                f"NP[CASE={case}, COORD={coord}]",
                [
                    f"NP[CASE={case}]",
                    "PUNCT[PUNCT_CLASS=COMMA]",
                    f"NP[CASE={case}]",
                    "PUNCT[PUNCT_CLASS=COMMA]",
                    f"PART[COORD={coord}]",
                    f"NP[CASE={case}]",
                ],
                [
                    "↓1 ∈ (↑ CONJUNCTS)",
                    "↓3 ∈ (↑ CONJUNCTS)",
                    "↓6 ∈ (↑ CONJUNCTS)",
                    f"(↑ COORD) = '{coord}'",
                    f"(↑ CASE) = '{case}'",
                    f"(↑ NUM) = {num_rhs}",
                    f"(↓5 COORD) =c '{coord}'",
                ],
            ))
            # Non-Oxford form (5 daughters).
            rules.append(Rule(
                f"NP[CASE={case}, COORD={coord}]",
                [
                    f"NP[CASE={case}]",
                    "PUNCT[PUNCT_CLASS=COMMA]",
                    f"NP[CASE={case}]",
                    f"PART[COORD={coord}]",
                    f"NP[CASE={case}]",
                ],
                [
                    "↓1 ∈ (↑ CONJUNCTS)",
                    "↓3 ∈ (↑ CONJUNCTS)",
                    "↓5 ∈ (↑ CONJUNCTS)",
                    f"(↑ COORD) = '{coord}'",
                    f"(↑ CASE) = '{case}'",
                    f"(↑ NUM) = {num_rhs}",
                    f"(↓4 COORD) =c '{coord}'",
                ],
            ))

    # --- Phase 5n.A Commit 19 + Phase 6.C: N-conjunct flat NP coord ---
    # (§18 L85, L85+)
    #
    # The Phase 5k Commit 4 3-conjunct rules above produce a flat
    # CONJUNCTS set only for exactly-3 conjuncts. This block adds a
    # left-recursive ``NP_LONG_LIST_<case>`` non-terminal that
    # accumulates 3+ NPs separated by commas into one CONJUNCTS set,
    # then wrap rules (Oxford + non-Oxford) that consume the list +
    # ``at`` + final NP to form a flat N-conjunct NP. Under the
    # Phase 6.C graph-constraint matcher the wrap composes for all
    # N ≥ 4 — 6/7-conjunct stress fixtures live in
    # ``tests/tgllfg/test_phase5n_4conj_coord.py``.
    #
    # **Targeted CONJUNCTS sharing**: ``(↑ CONJUNCTS) = (↓1 CONJUNCTS)``
    # is a defining equation that unifies the matrix's CONJUNCTS
    # feature with the recursive daughter's CONJUNCTS. Both ends
    # become the same set node; adding to one adds to the other.
    # This avoids the full-f-struct sharing (``(↑) = ↓1``) that
    # would conflict with matrix CASE/COORD/NUM equations.
    #
    # **Why N≥5 needed the strict matcher**: under the legacy
    # non-conflict matcher the 4+-wrap LHS (bare ``NP``) collided
    # with every parent NP expectation — including those that
    # demanded mutually-exclusive features like CASE=GEN or
    # COORD={OR,BUT}. Each high-N parse fanned out into binary
    # readings the Phase 5m mismo rule (``NP → NP PART``) latched
    # onto, then died at well-formedness on mismo / 2P clitic
    # constraint failures. The Phase 6.C strict matcher requires
    # parents to spell out the features they demand and parents'
    # rules to advertise the features they supply (here
    # ``COORD=AND``), pruning the spurious binary fanout at predict
    # time and freeing the wrap to compose. The 4-conjunct case
    # squeaked through under the old matcher because it had only
    # one recursive step; n≥5 added two or more steps, multiplying
    # the spurious paths past the parser's tolerance.
    #
    # The Phase 5k 3-conjunct rules continue to fire on exactly-3-
    # conjunct surfaces (which have ``at`` between conjunct 2 and 3);
    # NP_LONG_LIST has no ``at`` until the wrap, so the two patterns
    # don't collide.
    #
    # Reference: S&O 1972 §6.7 (multi-conjunct enumeration); R&G
    # 1981 §6.6.
    for case in _NP_CASES:
        # NP_LONG_LIST base: exactly 3 NPs separated by commas.
        rules.append(Rule(
            f"NP_LONG_LIST_{case}",
            [
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                "↓5 ∈ (↑ CONJUNCTS)",
            ],
        ))
        # NP_LONG_LIST recursive: list + comma + NP, accumulating via
        # targeted CONJUNCTS sharing.
        rules.append(Rule(
            f"NP_LONG_LIST_{case}",
            [
                f"NP_LONG_LIST_{case}",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"NP[CASE={case}]",
            ],
            [
                "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
            ],
        ))
        # 4+-conjunct wrap (Oxford comma form): list + comma + at + NP.
        # LHS advertises COORD=AND so matrix consumers (S frames,
        # wide-scope NEG, L83 fragment, etc.) admit the wrap under
        # the Phase 6.C graph-constraint matcher — same convention
        # as the binary / 3-conjunct coord rules above.
        rules.append(Rule(
            f"NP[CASE={case}, COORD=AND]",
            [
                f"NP_LONG_LIST_{case}",
                "PUNCT[PUNCT_CLASS=COMMA]",
                "PART[COORD=AND]",
                f"NP[CASE={case}]",
            ],
            [
                "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
                "↓4 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓3 COORD) =c 'AND'",
            ],
        ))
        # 4+-conjunct wrap (non-Oxford form): list + at + NP
        rules.append(Rule(
            f"NP[CASE={case}, COORD=AND]",
            [
                f"NP_LONG_LIST_{case}",
                "PART[COORD=AND]",
                f"NP[CASE={case}]",
            ],
            [
                "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓2 COORD) =c 'AND'",
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
    # Two surface forms per coord value — without a separating
    # comma (``Kumain si Maria at pumunta si Juan.``) and with one
    # (``Kumain si Maria, at pumunta si Juan.`` — comma-marked, the
    # more common written form for clausal coord). Both are
    # attested in modern Tagalog. The comma-form lands here in
    # Commit 7 to support the canonical ``Pumunta siya, kaya
    # kumain ako.`` form; symmetric for AND / OR / BUT / SO so the
    # parametrization stays uniform.
    # Phase 5n.B Commit 7 (§18 L45): Alternative-Q matrix lift for the
    # OR-clausal variant. ``S → S PART[o] S`` syntactically supports
    # the Alternative-Q reading (``Tao ka o multo?`` "Are you a person
    # or a ghost?"); per §18 L45 the rule lifts ``Q_TYPE=ALTERNATIVE``
    # unconditionally onto the matrix as the structural marker for
    # the Alt-Q construction. Pragmatic disambiguation between
    # declarative OR-coord and Alternative-Q (signalled in writing by
    # ``?`` and in speech by intonation) is left to downstream
    # consumers — both readings share the same syntactic structure
    # in Tagalog. The matrix continues to carry ``COORD=OR`` so
    # existing OR-coord consumers are unaffected.
    for coord in _BINARY_CLAUSAL_COORDS:
        no_comma_eqs = [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓3 ∈ (↑ CONJUNCTS)",
            f"(↑ COORD) = '{coord}'",
            f"(↓2 COORD) =c '{coord}'",
        ]
        comma_eqs = [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓4 ∈ (↑ CONJUNCTS)",
            f"(↑ COORD) = '{coord}'",
            f"(↓3 COORD) =c '{coord}'",
        ]
        if coord == "OR":
            no_comma_eqs.append("(↑ Q_TYPE) = 'ALTERNATIVE'")
            comma_eqs.append("(↑ Q_TYPE) = 'ALTERNATIVE'")
        # No-comma form (3 daughters).
        rules.append(Rule(
            "S",
            [
                "S",
                f"PART[COORD={coord}]",
                "S",
            ],
            no_comma_eqs,
        ))
        # Comma-marked form (4 daughters; PUNCT syncategorematic).
        rules.append(Rule(
            "S",
            [
                "S",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"PART[COORD={coord}]",
                "S",
            ],
            comma_eqs,
        ))

    # --- Phase 5k Commit 7: `kaya naman` two-word consequence ---
    #
    # ``S → S PART[COORD=SO] PART[ADV=ALSO] S``
    #
    # Equations:
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓4 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'SO'
    #   (↑ DISCOURSE_EMPH) = true
    #   (↓2 COORD) =c 'SO'
    #   (↓3 ADV) =c 'ALSO'
    #
    # ``kaya naman`` is a discourse-emphatic variant of plain
    # ``kaya``: "and so / and therefore" with extra emphasis. The
    # ``naman`` 2P enclitic (PART[ADV=ALSO]) sits between ``kaya``
    # and the second conjunct, but unlike most 2P clitics it does
    # not get reordered to a host's post-position — the two-word
    # ``kaya naman`` is a fixed lexicalised construction. The
    # rule consumes ``naman`` as a structural daughter rather
    # than letting clitic placement absorb it.
    #
    # The lifted ``DISCOURSE_EMPH`` feature on the matrix
    # distinguishes ``kaya naman`` from plain ``kaya`` for
    # downstream consumers (translation / register / ranker
    # heuristics).
    #
    # Polysemy disambiguation: the existing Phase 4 §7.6
    # VERB[CTRL_CLASS=PSYCH] ``kaya`` ("be able to") fires only on
    # contexts with a GEN-experiencer + linker + XCOMP-V; it does
    # NOT match a S-headed context. The new PART[COORD=SO] entry
    # (Commit 1 lex) fires only when sandwiched between two
    # complete S clauses. Rule context disambiguates without any
    # cross-fire risk; corpus audit (2026-05-07) confirmed all
    # pre-existing ``kaya`` corpus entries (~16 PSYCH control
    # fixtures) are 4-token forms ``Kaya <pron>ng V`` that never
    # match the binary-S-coord shape.
    # No-comma form: ``Pumunta siya kaya naman kumain ako.``
    rules.append(Rule(
        "S",
        [
            "S",
            "PART[COORD=SO]",
            "PART[ADV=ALSO]",
            "S",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓4 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'SO'",
            "(↑ DISCOURSE_EMPH) = true",
            "(↓2 COORD) =c 'SO'",
            "(↓3 ADV) =c 'ALSO'",
        ],
    ))
    # Comma-marked form: ``Pumunta siya, kaya naman kumain ako.``
    rules.append(Rule(
        "S",
        [
            "S",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "PART[COORD=SO]",
            "PART[ADV=ALSO]",
            "S",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓5 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'SO'",
            "(↑ DISCOURSE_EMPH) = true",
            "(↓3 COORD) =c 'SO'",
            "(↓4 ADV) =c 'ALSO'",
        ],
    ))

    # --- Phase 5k Commit 8: asymmetric NP coordination ---
    #
    # ``NP[CASE=X] → NP[CASE=X] PUNCT[COMMA] PART[POLARITY=NEG] NP[CASE=X]``
    # for each case X ∈ {NOM, GEN, DAT}. Three rules total.
    #
    # ``Si Maria, hindi si Juan.`` "Maria, not Juan" — a comma-
    # separated coord with the second conjunct headed by ``hindi``,
    # producing a contrast-with-rejection reading. Distinct from
    # symmetric ``at`` / ``o`` / ``pero`` coord because:
    #
    #   * The second conjunct is the NEGATED alternative — the
    #     speaker asserts the first and rejects the second.
    #   * No symmetric coord PART (``at``, ``o``, etc.) is present;
    #     ``hindi`` itself fills the connective slot.
    #   * The matrix carries COORD=BUT_NOT (asymmetric value
    #     distinct from BUT used for symmetric adversative
    #     pero/ngunit/subalit).
    #
    # Equations (NOM example):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓4 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'BUT_NOT'
    #   (↑ CASE) = 'NOM'
    #   (↑ NUM) = ↓1 NUM
    #   (↓3 POLARITY) =c 'NEG'
    #   (↓4 POLARITY) = 'NEG'
    #
    # NUM percolates from the first (asserted) conjunct rather
    # than forcing PL — semantically the matrix asserts ONE
    # referent (the first); the second is contrasted-and-rejected.
    # Marking the second conjunct's POLARITY=NEG is a defining
    # equation that flags the rejection on the conjunct's own
    # f-structure for downstream consumers.
    #
    # The rule structurally overlaps with the Commit 4
    # multi-conjunct rule (``NP COMMA NP AND NP``, also 5
    # daughters). Non-conflict category-pattern matching admits
    # both rules for ``Si Maria, hindi si Juan`` (PART[POLARITY=
    # NEG] and PART[COORD=AND] share no keys with hindi's
    # morph feats); the constraining equations
    # ``(↓3 POLARITY) =c 'NEG'`` here and ``(↓4 COORD) =c 'AND'``
    # in the multi-conjunct rule discriminate at the unifier
    # layer — only one fires per input.
    for case in _NP_CASES:
        rules.append(Rule(
            # LHS advertises COORD=BUT_NOT so parent rules expecting
            # ``NP[CASE=X, COORD=BUT_NOT]`` (notably the Phase 5n.C
            # Commit 5 L83 fragment-S rule in cfg/clause.py) admit
            # this LHS at completion time under the Phase 6.C
            # graph-constraint matcher.
            f"NP[CASE={case}, COORD=BUT_NOT]",
            [
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
                "PART[POLARITY=NEG]",
                f"NP[CASE={case}]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓4 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'BUT_NOT'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = ↓1 NUM",
                "(↓3 POLARITY) =c 'NEG'",
                "(↓4 POLARITY) = 'NEG'",
            ],
        ))

    # --- Phase 5k Commit 9: N-level binary coord ---
    #
    # ``N → N PART[COORD=Y] N`` for Y ∈ {AND, OR}. Two rules
    # total. Same shape as the Commit 3 NP-level binary rules but
    # at the bare-N level — for contexts that consume bare N as a
    # daughter rather than NP[CASE=X]. The primary consumer is
    # the Phase 5j HAVE construction:
    #
    #   ``May aklat at lapis si Maria.`` "Maria has a book and a
    #   pencil" — the Phase 5j HAVE rule
    #   (``S → PART[EXISTENTIAL] N NP[CASE=NOM]``) takes
    #   bare N as the existence-asserted entity. Without an
    #   N-level coord rule the coord-N ``aklat at lapis`` cannot
    #   parse as a single N, and HAVE × coord 0-parses.
    #
    # Equations (additive, NOM-N example):
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓3 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'AND'
    #   (↑ NUM) = 'PL'
    #   (↓2 COORD) =c 'AND'
    #
    # No CASE on the matrix N — bare N is case-less by design.
    # Consumed by HAVE (which sets EXISTENTIAL/CLAUSE_TYPE on
    # its own matrix), or by the case-marker → NP projection
    # (``ng aklat at lapis`` "of book and pencil") where the case
    # marker contributes CASE.
    #
    # Ambiguity note: with N-level coord enabled,
    # ``ng aklat at ng lapis`` admits TWO parses — one where each
    # case-marker + N is its own NP and they NP-coord (Commit 3),
    # and one where ``aklat at lapis`` is N-coord and only one
    # ``ng`` is needed... but the second ``ng`` is then orphaned
    # so the second reading fails to compose. Only the original
    # NP-level reading survives. ``ng aklat at lapis`` (single
    # case marker) — IS admitted via the new N-level rule.
    for coord in ("AND", "OR"):
        rules.append(Rule(
            # LHS advertises COORD for the Phase 6.C graph-constraint
            # matcher — same convention as the NP-coord rules above.
            f"N[COORD={coord}]",
            [
                "N",
                f"PART[COORD={coord}]",
                "N",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                f"(↑ COORD) = '{coord}'",
                "(↑ NUM) = 'PL'" if coord == "AND" else "(↑ NUM) = ↓1 NUM",
                f"(↓2 COORD) =c '{coord}'",
                # Phase 10.J.post-7.7: reject already-coordinated N
                # daughters. Without these gates the post-7.7 bare-
                # comma wrap's N[COORD=AND] output could form the
                # first/last conjunct of a binary ``N at N`` coord,
                # producing nested-coord ambiguity (e.g., PANAHON
                # sent-9's 6-N enumeration could bracket as
                # ``(mangga, bayabas, santol, abokado, melon)
                # at pakwan``).
                "¬ (↓1 COORD)",
                "¬ (↓3 COORD)",
            ],
        ))

    # --- Phase 10.J.post-12.16: comma-joined OR-pair N-coord -----------
    #
    # ``ama o anak, pamangkin o apo``
    #     "father or son, niece/nephew or grandchild"  (PAMILYA/sent-2)
    # ``ama o anak, pamangkin o apo, lolo o lola``     (extensible)
    #
    # Tagalog admits a comma-asyndetic join of two (or more) binary
    # OR-coord NPs as a single coord constituent — naming a series of
    # alternative-pair options. Per the user's bracketing of
    # PAMILYA/sent-2: ``[ama o anak, pamangkin o apo]`` is treated as
    # one constituent role-coord.
    #
    # The narrow constraint ``N[COORD=OR]`` on BOTH daughters
    # distinguishes this from the wider N_LONG_LIST 3+ pattern (bare-N
    # listing with no OR sub-coords); this rule fires only when both
    # sides are pre-formed OR pairs joined by comma.
    #
    # The two pairs go into the matrix CONJUNCTS as nested coord-
    # f-structures (preserving the inner OR pairings); a downstream
    # consumer can flatten if needed.
    rules.append(Rule(
        "N[COORD=OR]",
        [
            "N[COORD=OR]",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "N[COORD=OR]",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓3 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'OR'",
            "(↑ NUM) = 'PL'",
            "(↓1 COORD) =c 'OR'",
            "(↓3 COORD) =c 'OR'",
        ],
    ))

    # --- 9.X.c11: N-level mga marker for coord contexts ----------------
    #
    # ``ng bahay, gusali at mga tanim`` "of houses, buildings and
    # plants" (R&G 1981 PANAHON sent-22) — three Ns sharing one
    # ``ng`` case marker, where the LAST conjunct carries ``mga``.
    # The existing NP-level mga rule
    # (``NP[CASE=X] → CASE-MARKER PART[PLURAL_MARKER] N``) only
    # admits ``mga`` immediately after the case marker on the WHOLE
    # NP — it cannot mark individual conjuncts inside an N-level
    # coord.
    #
    # This rule lifts ``mga`` to the N level so it can appear on
    # any conjunct of an N-level coord:
    #
    #   N → PART[PLURAL_MARKER] N
    #     (↑) = ↓2                  inherit head N's features
    #     (↑ NUM) = 'PL'            plural-mark the N
    #     (↑ MGA_INTERNAL) = true   tag (see below)
    #     (↓1 PLURAL_MARKER) =c true
    #
    # **MGA_INTERNAL tag** prevents the simple NP rule
    # (``NP[CASE=X] → CASE-MARKER N``) from consuming an N-mga'd
    # output — that would duplicate the canonical NP-level
    # mga path (``NP[CASE=X] → CASE-MARKER PART[PLURAL] N``). The
    # tag is rejected by the simple NP rule via ``¬ (↓2
    # MGA_INTERNAL)``, leaving the N-mga path scoped to coord
    # contexts where the NP-level mga rule doesn't reach
    # (non-leading conjuncts).
    #
    # Reference: R&G 1981 PANAHON essay (sent-22).
    # Phase 10.K commit 4: ↓1 chart-symbol gated to
    # ``PART[PLURAL_MARKER=true]``. The original bare ``PART`` daughter
    # let the rule fire on every PART + N pair (every linker, every
    # discourse particle, every coord conjunction), then the
    # ``(↓1 PLURAL_MARKER) =c true`` solve-time gate rejected non-mga
    # candidates. Chart-symbol gating prunes the fan-out at chart
    # construction — only ``mga`` (the sole ``PLURAL_MARKER=true`` PART
    # in the lex) enters the rule.
    rules.append(Rule(
        "N",
        ["PART[PLURAL_MARKER=true]", "N"],
        [
            "(↑) = ↓2",
            "(↑ NUM) = 'PL'",
            "(↑ MGA_INTERNAL) = true",
        ],
    ))

    # --- 9.X.c11: N-level 3+-conjunct flat coord via N_LONG_LIST ------
    #
    # ``ng bahay, gusali at mga tanim`` "of houses, buildings and
    # plants" (R&G 1981 PANAHON sent-22) — three Ns with one
    # comma + ``at`` (non-Oxford), sharing a single ``ng`` case
    # marker. The existing N-level binary rule above (Phase 5k
    # Commit 9) handles 2-conjunct N coord; this block adds the
    # 3+-conjunct N-level form via a left-recursive ``N_LONG_LIST``
    # non-terminal that accumulates Ns separated by commas, plus
    # wrap rules that close the list with ``at + N``. Mirrors the
    # NP-level ``NP_LONG_LIST_<case>`` infrastructure (line 260
    # above) but at the case-less N level for shared-marker
    # contexts.
    #
    # Architecture:
    #
    #   N_LONG_LIST → N COMMA N                       (base: 2 Ns)
    #   N_LONG_LIST → N_LONG_LIST COMMA N             (recursive: +1)
    #
    #   N[COORD=AND] → N_LONG_LIST PART[COORD=AND] N         (non-Oxford)
    #   N[COORD=AND] → N_LONG_LIST COMMA PART[COORD=AND] N   (Oxford)
    #
    # The base requires exactly 2 Ns + 1 comma, encoding ≥1
    # iteration of ``(COMMA N)`` after the first N — the ``+``
    # quantifier in EBNF terms. The wrap rules close with
    # ``[COMMA?] AT N``, so the matrix N[COORD=AND] covers all
    # **3+ conjuncts** uniformly (3-conjunct case: base + wrap;
    # 4+ conjunct case: base + recursive iterations + wrap).
    # No separate per-arity rules are needed.
    #
    # **Design note vs. NP_LONG_LIST.** The NP_LONG_LIST base
    # requires exactly 3 NPs, with separate explicit rules for
    # the 3-conjunct case (lines 172-215). N_LONG_LIST starts at
    # 2 because (a) the construction is structurally simpler at
    # the case-less N level — no per-CASE rule explosion to
    # justify the split — and (b) starting at 2 lets one rule
    # family (LONG_LIST + wrap) cover all 3+ conjuncts uniformly,
    # which is closer to the ``(COMMA N)+`` quantifier semantics
    # the construction expresses.
    #
    # **AND-only scope.** Mirrors NP_LONG_LIST. Multi-conjunct OR
    # at the N level is rare in attested usage and the NUM
    # percolation (``↓1 NUM`` for OR) doesn't carry cleanly
    # through the recursive accumulator; can be added if needed.
    #
    # As with the binary N-coord rule, no CASE on the matrix N —
    # bare N is case-less by design. The construction's primary
    # consumer is the case-marker → NP projection (``ng bahay,
    # gusali at tanim`` where ``ng`` distributes over all three Ns
    # via the single-case-marker NP rule).
    #
    # PUNCT[COMMA] daughters are syncategorematic. Targeted
    # ``CONJUNCTS`` sharing via ``(↑ CONJUNCTS) = (↓1 CONJUNCTS)``
    # in the recursive and wrap rules unifies the accumulator's
    # set with the matrix's, avoiding full-f-struct sharing that
    # would conflict with matrix COORD/NUM equations.
    #
    # Reference: S&O 1972 §6.7 (multi-conjunct enumeration); R&G
    # 1981 PANAHON essay (sent-22).

    # N_LONG_LIST base: exactly 2 Ns separated by 1 comma.
    # Phase 10.J.post-7.7 added ``¬ (↓ COORD)`` gates on each N
    # daughter to reject pre-coordinated Ns from joining the list —
    # the post-7.7 bare-comma wrap `N[COORD=AND] → N_LONG_LIST_3PLUS`
    # produces N[COORD=AND], and without these gates the chart found
    # spurious recursive bracketings on at-wrapped enumerations
    # (PANAHON sent-9's 6-N ``mangga, bayabas, santol, abokado, melon
    # at pakwan``).
    rules.append(Rule(
        "N_LONG_LIST",
        [
            "N",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "N",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓3 ∈ (↑ CONJUNCTS)",
            "¬ (↓1 COORD)",
            "¬ (↓3 COORD)",
        ],
    ))
    # N_LONG_LIST recursive: list + comma + N, accumulating via
    # targeted CONJUNCTS sharing.
    rules.append(Rule(
        "N_LONG_LIST",
        [
            "N_LONG_LIST",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "N",
        ],
        [
            "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
            "↓3 ∈ (↑ CONJUNCTS)",
            "¬ (↓3 COORD)",
        ],
    ))
    # 3+-conjunct wrap (non-Oxford form): list + at + N.
    rules.append(Rule(
        "N[COORD=AND]",
        [
            "N_LONG_LIST",
            "PART[COORD=AND]",
            "N",
        ],
        [
            "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
            "↓3 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'AND'",
            "(↑ NUM) = 'PL'",
            "(↓2 COORD) =c 'AND'",
        ],
    ))
    # 3+-conjunct wrap (Oxford form): list + comma + at + N.
    rules.append(Rule(
        "N[COORD=AND]",
        [
            "N_LONG_LIST",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "PART[COORD=AND]",
            "N",
        ],
        [
            "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
            "↓4 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'AND'",
            "(↑ NUM) = 'PL'",
            "(↓3 COORD) =c 'AND'",
        ],
    ))

    # --- Phase 10.J.post-7.7: bare-comma N coord (no final ``at``) -------
    #
    # ``mangga, bayabas, santol`` (3-item) / ``mangga, bayabas, santol,
    # melon, pakwan`` (5-item) — bare-comma N enumeration with no
    # final ``at`` coordinator. Attested in colon-list constructions
    # (``Ang inaani ay mga prutas: mangga, bayabas, santol.``) and
    # in informal modern Filipino written practice. Pre-7.7 these
    # only parsed via the at-wrapped variants above; bare-comma
    # enumerations 0-parsed.
    #
    # The new infrastructure mirrors the existing ``N_LONG_LIST`` /
    # at-wrap pattern but uses a parallel ``N_LONG_LIST_3PLUS``
    # accumulator with an EXPLICIT 3-N base (no recursive 2-N step).
    # This prevents the bare-comma wrap from over-firing on 2-N
    # comma sequences (``X, Y`` without ``at`` is degenerate as a
    # complete coord in modern Tagalog — it would over-generate
    # chart-state on every internal-comma context).
    #
    # Architecture:
    #
    #   N_LONG_LIST_3PLUS → N COMMA N COMMA N        (base: exactly 3)
    #   N_LONG_LIST_3PLUS → N_LONG_LIST_3PLUS COMMA N (recursive: +1)
    #
    #   N[COORD=AND] → N_LONG_LIST_3PLUS             (bare-comma wrap)
    #
    # The wrap fires on lists of 3+ Ns; with the case-marker → NP
    # rule (``NP[CASE=X] → CASE-MARKER N``) it composes into a
    # full NP[CASE=X, COORD=AND] when an ``ang`` / ``ng`` / ``sa``
    # leads the list. Without a case marker, the bare N[COORD=AND]
    # serves the colon-split's ``N`` post-colon category
    # (pipeline._POST_COLON_CATEGORIES) for appositive enumeration
    # like ``... prutas: mangga, bayabas, santol.``.
    #
    # Reference: S&O 1972 §6.7 (multi-conjunct enumeration); modern
    # journalistic / casual practice.

    # N_LONG_LIST_3PLUS base: exactly 3 Ns separated by 2 commas.
    # Each N daughter rejects ``COORD`` via ``¬ (↓ COORD)`` — the
    # N daughters must be uncoordinated bare Ns, not already-
    # coordinated ``N[COORD=AND]`` outputs from this same rule.
    # Without these gates the chart finds spurious bracketings on
    # longer at-wrapped enumerations (e.g., PANAHON sent-9's 6-N
    # ``mangga, bayabas, santol, abokado, melon at pakwan``) where
    # sub-3-N lists could wrap to N[COORD=AND] and then participate
    # as N daughters in another LONG_LIST step.
    rules.append(Rule(
        "N_LONG_LIST_3PLUS",
        [
            "N",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "N",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "N",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓3 ∈ (↑ CONJUNCTS)",
            "↓5 ∈ (↑ CONJUNCTS)",
            "¬ (↓1 COORD)",
            "¬ (↓3 COORD)",
            "¬ (↓5 COORD)",
        ],
    ))
    # N_LONG_LIST_3PLUS recursive: list + comma + N, accumulating
    # via targeted CONJUNCTS sharing. Same ``¬ (↓3 COORD)`` gate
    # on the appended N daughter.
    rules.append(Rule(
        "N_LONG_LIST_3PLUS",
        [
            "N_LONG_LIST_3PLUS",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "N",
        ],
        [
            "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
            "↓3 ∈ (↑ CONJUNCTS)",
            "¬ (↓3 COORD)",
        ],
    ))
    # Bare-comma wrap: list alone produces the matrix N[COORD=AND].
    # No final ``at`` daughter — distinguishes from the Oxford /
    # non-Oxford wraps above.
    rules.append(Rule(
        "N[COORD=AND]",
        [
            "N_LONG_LIST_3PLUS",
        ],
        [
            "(↑ CONJUNCTS) = (↓1 CONJUNCTS)",
            "(↑ COORD) = 'AND'",
            "(↑ NUM) = 'PL'",
        ],
    ))

    # --- 9.X.c20: ``lalo na`` GEN-NP emphatic appositive -----------
    #
    # ``simula ng pagtatanim lalo na ng palay`` "the start of
    # planting, especially of rice" (R&G 1981 PANAHON sent-30 — the
    # ``ng palay`` GEN-NP is an emphasized appositive on the
    # preceding ``ng pagtatanim`` head-NP).
    #
    # ``lalo na`` is a fixed-phrase emphatic discourse marker
    # ("especially / particularly"). The grammar pairs it with a
    # companion change in ``clitics/placement.py``
    # (``disambiguate_homophone_clitics``): when ``na`` follows
    # ``lalo``, it's the linker (LINK=NA) regardless of right
    # context — without that, the reorder pass moves ``na`` to
    # clause-final position and the LINK=NA reading is lost (which
    # is why pre-9.X.c20 the rule wouldn't fire even with the
    # c-tree shape correctly defined).
    #
    # Rule:
    #
    #   NP[CASE=GEN] → NP[CASE=GEN] PART[INTENSIFIER] PART[LINK=NA]
    #                  NP[CASE=GEN]
    #     (↑) = ↓1                       matrix is the head GEN-NP
    #     ↓4 ∈ (↑ APP)                  emphasized GEN-NP joins APP set
    #     (↓2 LEMMA) =c 'lalo'           gate to lalo only
    #     (↓2 INTENSIFIER) =c true
    #     (↓3 LINK) =c 'NA'
    #
    # The ``APP`` attachment parallels the existing Phase 9.P
    # si-personal-name appositive rule (``cfg/nominal.py``): the
    # appositive sits in the head's APP set rather than ADJUNCT —
    # it's a referential narrowing, not a modifier.
    #
    # Reference: S&O 1972 §6 (emphatic apposition with ``lalo na``);
    # R&G 1981 PANAHON essay (sent-30).
    rules.append(Rule(
        "NP[CASE=GEN]",
        [
            "NP[CASE=GEN]",
            "PART[INTENSIFIER]",
            "PART[LINK=NA]",
            "NP[CASE=GEN]",
        ],
        [
            "(↑) = ↓1",
            "↓4 ∈ (↑ APP)",
            "(↓2 LEMMA) =c 'lalo'",
            "(↓2 INTENSIFIER) =c true",
            "(↓3 LINK) =c 'NA'",
        ],
    ))

    # --- Phase 6.C C3c: predicative-ADJ coordination ---------------
    #
    # ``Matanda at maganda si Maria.`` "Maria is old and beautiful"
    # — two predicative-ADJ heads conjoined by ``at`` / ``o``, with
    # a shared SUBJ provided by the matrix predicative-ADJ-S rule.
    #
    # Pre-Phase-6.C this surface admitted a spurious parse via the
    # Phase 5g manner-adverb rule (``S → ADJ PART[LINK=NA/NG] S``):
    # the non-conflict matcher silently let ``at`` (PART[COORD=AND])
    # fill the ``PART[LINK=NA/NG]`` slot since the two patterns
    # shared no keys. The Phase 6.C graph-constraint matcher
    # correctly rejects that path. This rule replaces the spurious
    # path with a proper ADJ-coord structure: a coord-ADJ
    # advertising ``PREDICATIVE=true, COORD=AND/OR`` so the existing
    # Phase 5g predicative-ADJ-S rule
    # (``S → ADJ[PREDICATIVE] NP[CASE=NOM]``) consumes it unchanged.
    #
    # F-structure (additive example):
    #
    #   ADJ_LEMMA   — undefined on the matrix coord-ADJ (each
    #                 conjunct ADJ keeps its own ADJ_LEMMA in
    #                 CONJUNCTS)
    #   CONJUNCTS   — {↓1, ↓3}
    #   COORD       — 'AND'
    #   PREDICATIVE — true (lifted from daughters; both must be
    #                 predicative)
    #
    # Both daughters are constrained to PREDICATIVE=true to keep
    # the rule from firing on adjuncts (NP-internal ADJs that have
    # the predicative ``maganda`` surface but no PREDICATIVE feat).
    for coord in ("AND", "OR"):
        rules.append(Rule(
            f"ADJ[PREDICATIVE=true, COORD={coord}]",
            [
                "ADJ[PREDICATIVE]",
                f"PART[COORD={coord}]",
                "ADJ[PREDICATIVE]",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓3 ∈ (↑ CONJUNCTS)",
                f"(↑ COORD) = '{coord}'",
                "(↑ PREDICATIVE) = true",
                "(↓1 PREDICATIVE) =c true",
                "(↓3 PREDICATIVE) =c true",
                f"(↓2 COORD) =c '{coord}'",
            ],
        ))

    # === Phase 5l Commit 14: correlative coordination ==================
    # — ``hindi lang … kundi pati`` "not only … but also"
    #
    # Discontinuous clausal coord: a NEG + lang-marked first
    # clause paired with a kundi-introduced second clause.
    # Three structural variants:
    #
    # 1. ``S , kundi pati S``  — canonical (comma + both PARTs)
    # 2. ``S kundi pati S``    — no comma
    # 3. ``S , kundi S``       — no pati
    #
    # The first clause is admitted as any S — typically a
    # negated clause with a ``lang``-enclitic absorbed into
    # ADJ (Phase 4 §7.3 + Phase 5e hindi negation), but the
    # rules don't constrain on the NEG / lang shape; tighter
    # gating can be added later if corpus pressure demands.
    #
    # The matrix carries ``COORD=BUT_NOT`` (sharing the value
    # used for Phase 5k asymmetric coord ``X, hindi Y``) plus
    # ``CORREL=YES`` to distinguish correlative from asymmetric.
    # Both clauses become members of CONJUNCTS, mirroring the
    # Phase 5k binary clausal coord f-structure.
    #
    # ``pati`` (Phase 5k Commit 1 lex: ``PART[ADV=ALSO_INCL]``)
    # is consumed structurally — its ALSO_INCL marker doesn't
    # propagate onto the matrix. The lex entry already exists;
    # this commit just wires the grammar to consume it.

    # Rule (a): canonical — comma + kundi + pati (5 daughters)
    rules.append(Rule(
        "S",
        [
            "S",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "PART[COORD=BUT_NOT]",
            "PART[ADV=ALSO_INCL]",
            "S",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓5 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'BUT_NOT'",
            "(↑ CORREL) = true",
            "(↓3 COORD) =c 'BUT_NOT'",
            "(↓4 ADV) =c 'ALSO_INCL'",
        ],
    ))

    # Rule (b): no comma — kundi + pati (4 daughters)
    rules.append(Rule(
        "S",
        [
            "S",
            "PART[COORD=BUT_NOT]",
            "PART[ADV=ALSO_INCL]",
            "S",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓4 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'BUT_NOT'",
            "(↑ CORREL) = true",
            "(↓2 COORD) =c 'BUT_NOT'",
            "(↓3 ADV) =c 'ALSO_INCL'",
        ],
    ))

    # Rule (c): comma + kundi (no pati) — 4 daughters
    rules.append(Rule(
        "S",
        [
            "S",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "PART[COORD=BUT_NOT]",
            "S",
        ],
        [
            "↓1 ∈ (↑ CONJUNCTS)",
            "↓4 ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'BUT_NOT'",
            "(↓3 COORD) =c 'BUT_NOT'",
        ],
    ))

    # === Phase 8.T: kundi-introduced phrasal correction ====================
    #
    # ``Hindi si Juan ang darating kundi si Pedro.``
    #     "It's not Juan who's coming but (rather) Pedro."
    # ``Walang tao doon kundi si Ben.``
    #     "There's no one there but Ben."
    # ``Wala siyang pera kundi sasampung sentimo.``
    #     "She has no money but ten centavos."
    #
    # Cited per S&O 1972 §7.20 (``kundi`` "but, except"). Distinct
    # from the Phase 5l Commit 14 correlative-clausal-coord
    # ``hindi lang … kundi pati S`` (which coordinates two clauses);
    # this is phrasal correction — ``kundi`` introduces an NP/PP
    # corrective alternative to whatever was negated in the matrix.
    #
    # Audit-hit shape (S&O 1972 page 656 / sent-1290): NEG-cleft
    # matrix with kundi-NP at the right edge.
    #
    # Analytical commitment: the corrective NP/PP rides on the
    # matrix's ADJUNCT set with ``ROLE: CORRECTION`` — mirroring the
    # Phase 5h Commit 6 ``EQUATIVE_STANDARD`` convention and the
    # Phase 5h Commit 3 ``kaysa`` STANDARD adjunct. The matrix
    # f-structure is inherited from the negated clause via
    # ``(↑) = ↓1``; the kundi-NP is the corrective alternative to
    # the negated focus, identifiable by walking the ADJUNCT set
    # for ROLE=CORRECTION.
    #
    # Gate: ``(↓1 POLARITY) =c 'NEG'`` — only NEG-marked matrix
    # clauses admit a kundi correction. Both ``hindi``-negated
    # clefts and ``wala``-existentials carry POLARITY=NEG, so the
    # same gate covers both audit-attested shapes. Affirmative
    # matrix S + ``kundi NP`` is blocked (kundi requires a negated
    # antecedent to correct).
    #
    # Two parallel rules — NP and PP correction:
    #
    #   S → S[POLARITY=NEG]  PART[COORD=BUT_NOT]  NP   (NP correction)
    #   S → S[POLARITY=NEG]  PART[COORD=BUT_NOT]  PP   (PP correction)
    #
    # Sentence-medial PP-correction (audit hit sent-1289:
    # ``Hindi dito kundi sa bayan ang pulong.``) needs a locative-
    # cleft analysis that 8.T doesn't land — pinned for a future
    # PP-cleft sub-PR. The right-edge PP-correction
    # (``Wala siyang pera kundi sa bayan.``) is covered by the
    # second rule below.

    # Rule (a): kundi-NP correction
    rules.append(Rule(
        "S",
        [
            "S",
            "PART[COORD=BUT_NOT]",
            "NP",
        ],
        [
            "(↑) = ↓1",
            "(↓1 POLARITY) =c 'NEG'",
            "(↓2 COORD) =c 'BUT_NOT'",
            "(↓3 ROLE) = 'CORRECTION'",
            "↓3 ∈ (↑ ADJUNCT)",
        ],
    ))

    # Rule (b): kundi-PP correction
    rules.append(Rule(
        "S",
        [
            "S",
            "PART[COORD=BUT_NOT]",
            "PP",
        ],
        [
            "(↑) = ↓1",
            "(↓1 POLARITY) =c 'NEG'",
            "(↓2 COORD) =c 'BUT_NOT'",
            "(↓3 ROLE) = 'CORRECTION'",
            "↓3 ∈ (↑ ADJUNCT)",
        ],
    ))

    # === Phase 5n.A Commit 16: multi-word coord particles (§18 L76 + L82) ====
    #
    # Three multi-word coord phrases combine two existing PARTs into a
    # single virtual PART that the existing Phase 5k binary clausal /
    # NP coord rules consume unchanged:
    #
    #   ``o kaya``  → COORD=OR  + UNCERTAIN=YES  ("or maybe / or perhaps")
    #   ``at saka`` → COORD=AND + SEQUENCE=YES   ("and also / and then")
    #   ``at nang`` → COORD=AND + RESULT=YES     ("and so / and so that")
    #
    # Same combining mechanic as Phase 5m Commit 11 (``gayon din`` /
    # ``ganon din`` / ``bukod dito`` discourse connectives). The
    # virtual PART carries the basic COORD value (OR / AND) so the
    # existing ``S → S PART[COORD=Y] S`` and ``NP → NP PART[COORD=Y] NP``
    # rules fire unchanged; the secondary discriminator
    # (UNCERTAIN / SEQUENCE / RESULT) rides for downstream consumers
    # without affecting structural composition.
    #
    # Lex (Phase 5k Commit 1 + Phase 5n.A Commit 16): ``o`` / ``at``
    # exist as PART[COORD=OR] / PART[COORD=AND]; ``kaya`` exists as
    # PART[COORD=SO] (homonym — the o-kaya rule constrains by lemma,
    # not COORD); ``saka`` is added in this commit; ``nang`` exists
    # as PART[COMP_TYPE=TEMP_SINCE] (the at-nang rule constrains by
    # lemma).
    #
    # Reference: S&O 1972 §6.7; R&G 1981 §6.6.

    # ``o kaya`` — disjunctive uncertainty. LHS pattern advertises
    # COORD=OR so parent rules expecting ``PART[COORD=OR]`` admit
    # this rule's LHS at completion time under the Phase 6.C
    # graph-constraint matcher; the ``(↑ COORD) = 'OR'`` defining
    # equation below is redundant under that matcher but kept for
    # explicitness.
    # Phase 10.K commit 4: daughters gated to PART[LEMMA=<word>] —
    # chart-time gating replaces the original solve-time LEMMA
    # constraining gates. The bare-PART daughters previously
    # let every PART + PART pair in the input fire these rules,
    # producing doomed candidates rejected at solve. For sentences
    # with many PART positions (e.g., PAMILYA/sent-16's
    # ``Kung minsa'y kapisan din ang wala pa ng asawa ng kapatid ng
    # ama o ina .``), the fan-out compounded across the 6+ multi-PART
    # rule variants — each contributing ~7 advances at the longest
    # spans. The chart-symbol gating prunes these at chart time.
    rules.append(Rule(
        "PART[COORD=OR]",
        ["PART[LEMMA=o]", "PART[LEMMA=kaya]"],
        [
            "(↑ COORD) = 'OR'",
            "(↑ UNCERTAIN) = true",
            "(↑ LEMMA) = 'o_kaya'",
        ],
    ))
    # ``at saka`` — conjunctive sequence
    rules.append(Rule(
        "PART[COORD=AND]",
        ["PART[LEMMA=at]", "PART[LEMMA=saka]"],
        [
            "(↑ COORD) = 'AND'",
            "(↑ SEQUENCE) = true",
            "(↑ LEMMA) = 'at_saka'",
        ],
    ))
    # ``at nang`` — conjunctive consequence
    rules.append(Rule(
        "PART[COORD=AND]",
        ["PART[LEMMA=at]", "PART[LEMMA=nang]"],
        [
            "(↑ COORD) = 'AND'",
            "(↑ RESULT) = 'YES'",
            "(↑ LEMMA) = 'at_nang'",
        ],
    ))

    # === Phase 5n.A Commit 17: coordinated cardinals (§18 L79) ================
    #
    # ``apatnapu't lima`` (45) = 40 + 5; ``isang daa't dalawampu`` (120)
    # = 100 + 20; etc. The bound ``'t`` clitic (Phase 5k Commit 2
    # ``split_apostrophe_t``) synthesises ``at`` between the two
    # cardinal operands, so the input reaches the grammar as
    # ``NUM[CARDINAL] PART[COORD=AND] NUM[CARDINAL]``.
    #
    # The unifier's equation language (src/tgllfg/fstruct/equations.py)
    # has no arithmetic primitive — Atom and Designator are the only
    # value types. So this rule cannot compute the sum on the matrix
    # CARDINAL_VALUE directly. Instead it follows the Phase 5f Commit 9
    # arithmetic-predicate precedent and records OPERAND_1 / OPERAND_2 +
    # COORD_OP=SUM; downstream consumers compute 40 + 5 = 45 from
    # the operand feats. (A computed CARDINAL_VALUE would require either
    # an equation-language extension or a post-unification projection
    # pass; both are larger scope than this single L79 closure.)
    #
    # The rule produces NUM[CARDINAL] so the existing NP-cardinal-
    # modifier rule (Phase 5f Commit 1) consumes the coordinated
    # cardinal as if it were a single NUM, allowing
    # ``apatnapu't limang aklat`` to parse as a quantified NP.
    #
    # Reference: S&O 1972 §4 (numeral coordination); R&G 1981
    # dialogue corpus.
    rules.append(Rule(
        "NUM[CARDINAL]",
        [
            "NUM[CARDINAL]",
            "PART[COORD=AND]",
            "NUM[CARDINAL]",
        ],
        [
            "(↑ CARDINAL) = true",
            "(↑ NUM) = 'PL'",
            "(↑ COORD_OP) = 'SUM'",
            "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
            "(↑ OPERAND_2) = ↓3 CARDINAL_VALUE",
            "(↓2 COORD) =c 'AND'",
            "(↓1 CARDINAL) =c true",
            "(↓3 CARDINAL) =c true",
        ],
    ))

    # === Phase 5n.C.2 Commit 5: L77 gapping in coord (PRED-sharing) =========
    #
    # Closes §18.1 L77. Canonical pattern: `<V> <agent1> <args1> at
    # <agent2> <args2>` where the verb is shared across conjuncts
    # (`Kumain si Maria ng kanin at si Juan ng tinapay.` "Maria ate
    # rice and Juan bread"). Design appendix in
    # docs/analysis-choices.md "Phase 5n.C.2 Commit 4: L77
    # PRED-sharing gapping in coord".
    #
    # Mechanism per LFG convention (Bresnan 2001 §6, Dalrymple 2001 §4):
    # the matrix S has `COORD=AND` + `GAPPING=YES` + `CONJUNCTS={c1, c2}`
    # where conjunct1 is V's f-structure (with SUBJ/OBJ from the first
    # NP pair) and conjunct2 is a new sub-f-structure (↑.CONJ2) with
    # PRED reentrant to V's PRED + SUBJ/OBJ from the second NP pair.
    #
    # The matrix has no PRED of its own — parallel to Phase 5k clausal
    # coord (lines 381+). The `GAPPING=YES` marker distinguishes real
    # gapping from spurious recursive NP-coord parses (Commit 3
    # tripwire pinning) and from biclausal coord (which has
    # COORD=AND but no shared PRED).
    #
    # Scope per design appendix:
    # - 2-conjunct AV transitive (canonical): rule [1] below
    # - 2-conjunct DV transitive: rule [2] (case-marking flipped:
    #   GEN-agent + NOM-pivot)
    # - 2-conjunct DV ditransitive: rule [3] (GEN + NOM + GEN frame)
    # - 3-conjunct AV transitive (Oxford comma form): rule [4]
    #
    # OBJ-only gapping, mixed-voice gapping, and adjunct-only gap
    # remain deferred per the design appendix.
    #
    # The non-conflict matcher (project_parser_nonconflict_matcher
    # memory) admits spurious NP-coord parses alongside the new
    # gapping parses; the ranker prefers the gapping analysis on
    # meaningful structure. Phase 6 parser is expected to eliminate
    # spurious parses via feature-compatibility at predict time.

    # [1] 2-conjunct AV transitive.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
            "PART[COORD=AND]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
        ],
        [
            # Conjunct 1: V's f-structure becomes conjunct1; add
            # SUBJ + OBJ from first NP pair.
            "(↓1 SUBJ) = ↓2",
            "(↓1 OBJ) = ↓3",
            "↓1 ∈ (↑ CONJUNCTS)",
            # Conjunct 2: fresh sub-f-structure with PRED + voice/
            # aspect/mood reentrant to V; SUBJ + OBJ from second
            # NP pair.
            "(↑ CONJ2 PRED) = (↓1 PRED)",
            "(↑ CONJ2 VOICE) = (↓1 VOICE)",
            "(↑ CONJ2 ASPECT) = (↓1 ASPECT)",
            "(↑ CONJ2 MOOD) = (↓1 MOOD)",
            "(↑ CONJ2 SUBJ) = ↓5",
            "(↑ CONJ2 OBJ) = ↓6",
            "(↑ CONJ2) ∈ (↑ CONJUNCTS)",
            # Matrix
            "(↑ COORD) = 'AND'",
            "(↑ GAPPING) = true",
            "(↓4 COORD) =c 'AND'",
        ],
    ))

    # [2] 2-conjunct DV transitive.
    #
    # DV pattern: V[VOICE=DV] NP[CASE=GEN]_agent NP[CASE=NOM]_pivot.
    # Both conjuncts share the GEN agent + NOM pivot frame.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=DV]",
            "NP[CASE=GEN]",
            "NP[CASE=NOM]",
            "PART[COORD=AND]",
            "NP[CASE=GEN]",
            "NP[CASE=NOM]",
        ],
        [
            # Conjunct 1: V + OBJ-AGENT (GEN) + SUBJ (NOM).
            "(↓1 OBJ-AGENT) = ↓2",
            "(↓1 SUBJ) = ↓3",
            "↓1 ∈ (↑ CONJUNCTS)",
            # Conjunct 2: PRED + voice/aspect/mood reentrant; new
            # OBJ-AGENT + SUBJ from second pair.
            "(↑ CONJ2 PRED) = (↓1 PRED)",
            "(↑ CONJ2 VOICE) = (↓1 VOICE)",
            "(↑ CONJ2 ASPECT) = (↓1 ASPECT)",
            "(↑ CONJ2 MOOD) = (↓1 MOOD)",
            "(↑ CONJ2 OBJ-AGENT) = ↓5",
            "(↑ CONJ2 SUBJ) = ↓6",
            "(↑ CONJ2) ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'AND'",
            "(↑ GAPPING) = true",
            "(↓4 COORD) =c 'AND'",
        ],
    ))

    # [3] 2-conjunct DV ditransitive.
    #
    # 3-arg DV (e.g., `Binigayan ni Maria si Juan ng aklat at si
    # Pedro ng panulat`): V[DV] GEN-agent NOM-pivot GEN-theme +
    # at + NOM-pivot GEN-theme. The GEN-agent is shared across
    # conjuncts (Maria gives both Juan and Pedro). Requires a
    # 3-arg DV LexicalEntry for the verb (`bigay` / `sulat` /
    # similar — added/extended in `core/lexicon.py` for L29 + L77).
    rules.append(Rule(
        "S",
        [
            "V[VOICE=DV]",
            "NP[CASE=GEN]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
            "PART[COORD=AND]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
        ],
        [
            # Conjunct 1: V + OBJ-AGENT (GEN-1) + SUBJ (NOM-1) +
            # OBJ-PATIENT (GEN-2).
            "(↓1 OBJ-AGENT) = ↓2",
            "(↓1 SUBJ) = ↓3",
            "(↓1 OBJ-PATIENT) = ↓4",
            "↓1 ∈ (↑ CONJUNCTS)",
            # Conjunct 2: shared PRED + voice/aspect/mood +
            # OBJ-AGENT (Maria is the agent in both); new SUBJ +
            # OBJ-PATIENT from the second NP pair.
            "(↑ CONJ2 PRED) = (↓1 PRED)",
            "(↑ CONJ2 VOICE) = (↓1 VOICE)",
            "(↑ CONJ2 ASPECT) = (↓1 ASPECT)",
            "(↑ CONJ2 MOOD) = (↓1 MOOD)",
            "(↑ CONJ2 OBJ-AGENT) = (↓1 OBJ-AGENT)",
            "(↑ CONJ2 SUBJ) = ↓6",
            "(↑ CONJ2 OBJ-PATIENT) = ↓7",
            "(↑ CONJ2) ∈ (↑ CONJUNCTS)",
            "(↑ COORD) = 'AND'",
            "(↑ GAPPING) = true",
            "(↓5 COORD) =c 'AND'",
        ],
    ))

    # [4] 3-conjunct AV transitive (Oxford comma form).
    #
    # `Kumain si Maria ng kanin, si Juan ng tinapay, at si Lola ng
    # isda.` — three conjuncts with comma separators and `at`
    # before the final conjunct. Daughters 4 and 8 are syncategorematic
    # commas; daughter 9 is the conjunction particle.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "PART[COORD=AND]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
        ],
        [
            # Conjunct 1 (V + first NP pair)
            "(↓1 SUBJ) = ↓2",
            "(↓1 OBJ) = ↓3",
            "↓1 ∈ (↑ CONJUNCTS)",
            # Conjunct 2 (second NP pair)
            "(↑ CONJ2 PRED) = (↓1 PRED)",
            "(↑ CONJ2 VOICE) = (↓1 VOICE)",
            "(↑ CONJ2 ASPECT) = (↓1 ASPECT)",
            "(↑ CONJ2 MOOD) = (↓1 MOOD)",
            "(↑ CONJ2 SUBJ) = ↓5",
            "(↑ CONJ2 OBJ) = ↓6",
            "(↑ CONJ2) ∈ (↑ CONJUNCTS)",
            # Conjunct 3 (third NP pair)
            "(↑ CONJ3 PRED) = (↓1 PRED)",
            "(↑ CONJ3 VOICE) = (↓1 VOICE)",
            "(↑ CONJ3 ASPECT) = (↓1 ASPECT)",
            "(↑ CONJ3 MOOD) = (↓1 MOOD)",
            "(↑ CONJ3 SUBJ) = ↓9",
            "(↑ CONJ3 OBJ) = ↓10",
            "(↑ CONJ3) ∈ (↑ CONJUNCTS)",
            # Matrix
            "(↑ COORD) = 'AND'",
            "(↑ GAPPING) = true",
            "(↓8 COORD) =c 'AND'",
        ],
    ))


    # === Phase 9.X.c47: AV V-coord with right-conjunct SUBJ sharing =====
    #
    # ``Naglalabasan ang mga bata at naglalaro sa kalye.``
    #     "The children come out and play in the street."
    # ``Naglalabasan ang mga bata at naglalaro sa tubig na umaapaw
    #     sa kalye.`` (PANAHON sent-25 main clause)
    # ``Kumain at uminom ang lalaki.`` -- SUBJ-final variant (out of
    #     scope here; this rule fires only with SUBJ between V1 and
    #     ``at``).
    #
    # Right-conjunct subject sharing: ``V1 SUBJ at V2 ...`` where V2
    # shares its SUBJ with V1 (the SUBJ is overtly expressed only
    # once, between V1 and the coordinator). LFG convention: both
    # V1 and V2 are conjuncts of a single matrix S with shared SUBJ
    # f-structure.
    #
    # Three rule variants for V2's argument structure (AV INTR
    # only, no overt OBJ — sufficient for sent-25 closure;
    # other voices and OBJ variants deferred):
    #
    #   1. ``V1 NP[NOM] PART[COORD=AND] V2`` (bare V2)
    #   2. ``V1 NP[NOM] PART[COORD=AND] V2 NP[CASE=DAT]`` (V2 with
    #      sa-PP adjunct; closes PANAHON sent-25)
    #   3. ``V1 NP[NOM] PART[COORD=AND] V2 NP[CASE=GEN]`` (V2 with
    #      GEN-OBJ)
    #
    # Both Vs go into CONJUNCTS; matrix SUBJ is shared between V1
    # and V2 via direct binding. AND-coord only (the SO/BUT/OR
    # variants would need separate analysis).
    for v2_extras_label, v2_extras_daughters, v2_extras_eqs in [
        ("bare", [], []),
        ("with sa-PP", ["NP[CASE=DAT]"], ["↓5 ∈ (↓4 ADJUNCT)"]),
        ("with GEN", ["NP[CASE=GEN]"], ["(↓4 OBJ) = ↓5"]),
    ]:
        rules.append(Rule(
            "S",
            [
                "V[VOICE=AV]",
                "NP[CASE=NOM]",
                "PART[COORD=AND]",
                "V[VOICE=AV]",
            ] + v2_extras_daughters,
            [
                "(↑ SUBJ) = ↓2",
                "(↓1 SUBJ) = ↓2",
                "(↓4 SUBJ) = ↓2",
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓4 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                "(↓3 COORD) =c 'AND'",
            ] + v2_extras_eqs,
        ))


    # --- Phase 10.J.post-1: binary NP coord with leading comma ---
    #
    # ``ang panahon ng tag-init mula Abril hanggang Hunyo, at ang
    # panahon ng tag-ulan mula Hulyo hanggang Oktubre`` — the two
    # appositive NPs in PANAHON sent-2's post-colon enumeration.
    #
    # **Moved to pipeline-level synthesis** in
    # :func:`tgllfg.core.pipeline._try_comma_at_np_split`. A chart
    # rule with this shape was tried first (``NP[CASE=X, COORD=AND]
    # → NP[CASE=X] PUNCT[COMMA] PART[COORD=AND] NP[CASE=X]``) but
    # increased chart-state count enough to push the canonical
    # short-c-tree parse of ``Bumili ng dalawang malalaking aklat
    # at ng tatlong maliliit na lapis si Maria`` past the default
    # 5000-tree iteration cap — even with ``budget=1`` and
    # registered-last placement (chart-state count is independent
    # of forest-emission budget). The pipeline-level synthesis
    # avoids chart competition entirely: it activates only when the
    # caller explicitly parses a segment as ``NP[CASE=NOM]`` (the
    # colon-split fast path's post-half) and the text contains
    # ``, at ``. Outside that context the chart is unchanged.
