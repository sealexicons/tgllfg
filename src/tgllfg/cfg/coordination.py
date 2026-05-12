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

    # --- Phase 5n.A Commit 19: 4+-conjunct flat NP coord (§18 L85) ---
    #
    # The Phase 5k Commit 4 3-conjunct rules above produce a flat
    # CONJUNCTS set only for exactly-3 conjuncts. This commit adds a
    # left-recursive ``NP_LONG_LIST_<case>`` non-terminal that
    # accumulates 3+ NPs separated by commas into one CONJUNCTS set,
    # then a wrap rule that consumes the list + ``at`` + final NP to
    # form a flat n-conjunct NP. The wrap fires cleanly for n=4
    # (using the base 3-NP list); for n≥5 the recursive list builds
    # correctly (visible in fragments) but the wrap doesn't compose
    # to a top-level S due to a parser-level interaction (see below).
    #
    # **Targeted CONJUNCTS sharing**: ``(↑ CONJUNCTS) = (↓1 CONJUNCTS)``
    # is a defining equation that unifies the matrix's CONJUNCTS
    # feature with the recursive daughter's CONJUNCTS. Both ends
    # become the same set node; adding to one adds to the other.
    # This avoids the full-f-struct sharing (``(↑) = ↓1``) that
    # would conflict with matrix CASE/COORD/NUM equations.
    #
    # **5+-conjunct still 0-parses** despite the recursive rules
    # being present and the recursive list being built correctly.
    # Root cause (per drill-down): the parser's category-pattern
    # matcher is non-conflict — at high N, every binary parse path
    # ambiguously matches the Phase 5m mismo NP-emphatic rule
    # (``NP → NP PART``) on each NP+PART adjacency. All 14 binary
    # parses for 5-NP fail well-formedness with mismo constraint
    # failures (or the 2P clitic absorption rule's CLITIC_CLASS=2P
    # failure). 4-NP succeeds because at least one of its 5
    # parses survives. The fix requires either parser-level
    # support for **defining** category-pattern constraints (rather
    # than non-conflict + late constraining) or per-rule narrower
    # category constraints across the grammar — both broader scope
    # than this single L85 closure.
    #
    # The 5+-conjunct case stays pinned in tests as the trigger for
    # the parser-level / grammar-wide tightening work.
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
        # 4+-conjunct wrap (Oxford comma form): list + comma + at + NP
        rules.append(Rule(
            f"NP[CASE={case}]",
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
            f"NP[CASE={case}]",
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
            "N",
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
    rules.append(Rule(
        "PART[COORD=OR]",
        ["PART", "PART"],
        [
            "(↑ COORD) = 'OR'",
            "(↑ UNCERTAIN) = true",
            "(↑ LEMMA) = 'o_kaya'",
            "(↓1 LEMMA) =c 'o'",
            "(↓2 LEMMA) =c 'kaya'",
        ],
    ))
    # ``at saka`` — conjunctive sequence
    rules.append(Rule(
        "PART[COORD=AND]",
        ["PART", "PART"],
        [
            "(↑ COORD) = 'AND'",
            "(↑ SEQUENCE) = true",
            "(↑ LEMMA) = 'at_saka'",
            "(↓1 LEMMA) =c 'at'",
            "(↓2 LEMMA) =c 'saka'",
        ],
    ))
    # ``at nang`` — conjunctive consequence
    rules.append(Rule(
        "PART[COORD=AND]",
        ["PART", "PART"],
        [
            "(↑ COORD) = 'AND'",
            "(↑ RESULT) = 'YES'",
            "(↑ LEMMA) = 'at_nang'",
            "(↓1 LEMMA) =c 'at'",
            "(↓2 LEMMA) =c 'nang'",
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
