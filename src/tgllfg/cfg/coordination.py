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

    # --- Phase 5n.A Commit 19: 4-conjunct flat NP coord (§18 L85) ---
    #
    # The Phase 5k Commit 4 3-conjunct rules above produce a flat
    # CONJUNCTS set only for exactly-3 conjuncts. This commit adds
    # explicit 4-conjunct rules (Oxford + non-Oxford × NOM/GEN/DAT)
    # producing flat 4-member CONJUNCTS sets.
    #
    # Tried two approaches before settling on explicit 4-conjunct:
    #
    # 1. Right-recursive ``NP_LONG_LIST_<case>`` non-terminal (per
    #    the §18 plan). The wrap rule's ``(↑) = ↓1`` equation didn't
    #    fire cleanly with the recursive list — the parser built the
    #    n-element list correctly (visible in fragments) but the wrap
    #    didn't compose to a top-level S.
    # 2. Explicit 5-conjunct rules (9 / 10 daughters). Loaded by the
    #    grammar (verified) but didn't fire on attested 5-conjunct
    #    surfaces — possibly an Earley state-explosion interaction
    #    with the Phase 5m mismo NP-emphatic rule that ambiguously
    #    matches ``Ana at`` as ``NP + PART``. Out of L85 scope to
    #    debug.
    #
    # 5+-conjunct surfaces remain 0-parse for now (pinned in tests as
    # the trigger for follow-on work). The §18 entry's "4+" target
    # is partially closed: 4-conjunct works flat; 5+-conjunct is a
    # separate follow-on item (right-recursive non-terminal or
    # parser-level disambiguation).
    #
    # Reference: S&O 1972 §6.7 (multi-conjunct enumeration); R&G
    # 1981 §6.6.
    for case in _NP_CASES:
        # 4-conjunct Oxford-comma form (8 daughters):
        # NP, NP, NP, NP, at NP — wait, that's 5 NPs.
        # Actually 4 conjuncts means 4 NPs total: A, B, C, at D.
        # Daughters: A COMMA B COMMA C COMMA at D = 8 elements
        # (with Oxford comma before "at"); non-Oxford = 7.
        rules.append(Rule(
            f"NP[CASE={case}]",
            [
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
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
                "↓5 ∈ (↑ CONJUNCTS)",
                "↓8 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓7 COORD) =c 'AND'",
            ],
        ))
        # 4-conjunct non-Oxford form (7 daughters):
        # A COMMA B COMMA C at D
        rules.append(Rule(
            f"NP[CASE={case}]",
            [
                f"NP[CASE={case}]",
                "PUNCT[PUNCT_CLASS=COMMA]",
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
                "↓7 ∈ (↑ CONJUNCTS)",
                "(↑ COORD) = 'AND'",
                f"(↑ CASE) = '{case}'",
                "(↑ NUM) = 'PL'",
                "(↓6 COORD) =c 'AND'",
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
    for coord in _BINARY_CLAUSAL_COORDS:
        # No-comma form (3 daughters).
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
        # Comma-marked form (4 daughters; PUNCT syncategorematic).
        rules.append(Rule(
            "S",
            [
                "S",
                "PUNCT[PUNCT_CLASS=COMMA]",
                f"PART[COORD={coord}]",
                "S",
            ],
            [
                "↓1 ∈ (↑ CONJUNCTS)",
                "↓4 ∈ (↑ CONJUNCTS)",
                f"(↑ COORD) = '{coord}'",
                f"(↓3 COORD) =c '{coord}'",
            ],
        ))

    # --- Phase 5k Commit 7: `kaya naman` two-word consequence ---
    #
    # ``S → S PART[COORD=SO] PART[ADV=ALSO] S``
    #
    # Equations:
    #   ↓1 ∈ (↑ CONJUNCTS)
    #   ↓4 ∈ (↑ CONJUNCTS)
    #   (↑ COORD) = 'SO'
    #   (↑ DISCOURSE_EMPH) = 'YES'
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
            "(↑ DISCOURSE_EMPH) = 'YES'",
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
            "(↑ DISCOURSE_EMPH) = 'YES'",
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
            f"NP[CASE={case}]",
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
    #   (``S → PART[EXISTENTIAL=YES] N NP[CASE=NOM]``) takes
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
            "(↑ CORREL) = 'YES'",
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
            "(↑ CORREL) = 'YES'",
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

    # ``o kaya`` — disjunctive uncertainty
    rules.append(Rule(
        "PART",
        ["PART", "PART"],
        [
            "(↑ COORD) = 'OR'",
            "(↑ UNCERTAIN) = 'YES'",
            "(↑ LEMMA) = 'o_kaya'",
            "(↓1 LEMMA) =c 'o'",
            "(↓2 LEMMA) =c 'kaya'",
        ],
    ))
    # ``at saka`` — conjunctive sequence
    rules.append(Rule(
        "PART",
        ["PART", "PART"],
        [
            "(↑ COORD) = 'AND'",
            "(↑ SEQUENCE) = 'YES'",
            "(↑ LEMMA) = 'at_saka'",
            "(↓1 LEMMA) =c 'at'",
            "(↓2 LEMMA) =c 'saka'",
        ],
    ))
    # ``at nang`` — conjunctive consequence
    rules.append(Rule(
        "PART",
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
    # ``NUM[CARDINAL=YES] PART[COORD=AND] NUM[CARDINAL=YES]``.
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
    # The rule produces NUM[CARDINAL=YES] so the existing NP-cardinal-
    # modifier rule (Phase 5f Commit 1) consumes the coordinated
    # cardinal as if it were a single NUM, allowing
    # ``apatnapu't limang aklat`` to parse as a quantified NP.
    #
    # Reference: S&O 1972 §4 (numeral coordination); R&G 1981
    # dialogue corpus.
    rules.append(Rule(
        "NUM[CARDINAL=YES]",
        [
            "NUM[CARDINAL=YES]",
            "PART[COORD=AND]",
            "NUM[CARDINAL=YES]",
        ],
        [
            "(↑ CARDINAL) = 'YES'",
            "(↑ NUM) = 'PL'",
            "(↑ COORD_OP) = 'SUM'",
            "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
            "(↑ OPERAND_2) = ↓3 CARDINAL_VALUE",
            "(↓2 COORD) =c 'AND'",
            "(↓1 CARDINAL) =c 'YES'",
            "(↓3 CARDINAL) =c 'YES'",
        ],
    ))
