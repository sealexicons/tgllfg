# tgllfg/cfg/clause.py

"""Clausal rules: V-initial S frames + predicative clauses.

Holds every grammar rule whose left-hand side is ``S`` and whose
right-hand side is a verb (or copula-like predicative head) plus
its argument NPs / cardinal predicate. After the post-Phase-5f
grammar split (see ``docs/refactor-grammar-package.md``) this
module owns:

* Phase 4 §7.1 V-initial S frames — the canonical AV / OV / DV / IV
  voice templates for transitive and intransitive clauses, plus the
  ``ng``-non-pivot OBJ analysis and the basic ADJUNCT attachment of
  ``sa``-NPs.
* Phase 5e Commit 26 ``parang`` comparative — predicative
  comparison clauses (``parang aso ang bata``, "the child is like a
  dog").
* Phase 5f Commit 4 predicative cardinal — cardinal-as-predicate
  clauses (``Tatlo ang aso``, "the dogs are three").
* Phase 5f Commit 9 arithmetic predicates (Group D) — equality,
  addition, etc. with cardinal arguments.
* Phase 5b multi-GEN-NP applicative frames (IV-BEN) — extended V-S
  templates for benefactive applicatives.
* Phase 5b multi-GEN-NP causative frames (pa-OV / pa-DV direct) —
  extended templates for direct causatives in OV / DV voices.
* Phase 5e Commit 11 multi-GEN-NP plain DV — extended template for
  plain (non-causative) DV with two GEN arguments.

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
second, immediately after :mod:`tgllfg.cfg.nominal` and before the
clitic / negation / extraction / control / discourse registrars —
see the plan's "Migration strategy" §H.
"""

from __future__ import annotations

from ._helpers import _eqs
from .grammar import Rule


def register_rules(rules: list[Rule]) -> None:
    """Append the clausal-area rules in source order."""
    # --- Sentential rules: V-initial, flat ---
    #
    # SUBJ ← NP[CASE=NOM]; OBJ ← NP[CASE=GEN]. ADJUNCT ∋ NP[CASE=DAT].
    # Both post-verbal NP orders are admitted (Tagalog free order).

    # AV intransitive (no OBJ).
    rules.append(Rule(
        "S",
        ["V[VOICE=AV]", "NP[CASE=NOM]"],
        _eqs("(↑ SUBJ) = ↓2"),
    ))
    rules.append(Rule(
        "S",
        ["V[VOICE=AV]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
        _eqs("(↑ SUBJ) = ↓2", "↓3 ∈ (↑ ADJUNCT)"),
    ))


    # --- Phase 5e Commit 26: comparative `parang` ---
    #
    # ``Parang aso ang bata.`` "The child is like a dog." The
    # comparative reading of `parang` is structurally distinct
    # from the evidential reading (`Parang umuulan` "It seems
    # like it's raining" — Phase 5d Commit 1). The comparative
    # form takes a bare nominal as the standard of comparison
    # and an ang-NP as the comparee.
    #
    # F-structure shape:
    #
    #   PRED = 'LIKE <SUBJ, OBJ>'
    #   SUBJ = the comparee (the ang-NP)
    #   OBJ  = the standard (the bare N)
    #
    # The bare N projects PRED + LEMMA via the existing
    # ``N → NOUN`` rule, so OBJ ends up with the NOUN's lemma
    # and a NOUN-style PRED.
    #
    # ``parang`` and ``tila`` are typed as ``V`` (per
    # ``particles.yaml`` ``pos: VERB``); the existing Phase 5d
    # Commit 1 evidential rule uses ``V[CTRL_CLASS=RAISING_BARE]``,
    # so this rule mirrors that category.
    #
    # The constraining equation ``(↓1 COMPARATIVE) =c 'YES'``
    # restricts to ``parang`` only — the category-pattern
    # matcher (``compile.py::matches``) is non-conflict, so
    # ``V[COMPARATIVE=YES, CTRL_CLASS=RAISING_BARE]`` would
    # also match ``tila`` (RAISING_BARE without COMPARATIVE) by
    # absorption without the explicit constraint.
    #
    # The existing evidential rule (Phase 5d Commit 1) for
    # ``parang + clause`` continues to fire on ``Parang kumain
    # ang bata`` (parang followed by V, not bare N) — different
    # rule shape, no competition.
    rules.append(Rule(
        "S",
        ["V[COMPARATIVE=YES, CTRL_CLASS=RAISING_BARE]", "N", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'LIKE <SUBJ, OBJ>'",
            "(↑ OBJ) = ↓2",
            "(↑ SUBJ) = ↓3",
            "(↓1 COMPARATIVE) =c 'YES'",
        ],
    ))


    # --- Phase 5f Commit 4: predicative cardinal -----------------
    #
    # ``Dalawa sila.`` "There are two of them."
    # ``Tatlo ang anak ko.`` "I have three children" (lit.
    # "three the child of-mine").
    # ``Sandaan ang aklat.`` "A hundred books."
    #
    # The cardinal serves as the matrix predicate with a NOM-NP
    # pivot. Structurally analogous to the Phase 5e Commit 26
    # comparative parang rule above (and the Phase 5d Commit 1
    # evidential parang) but with NUM[CARDINAL=YES] as the
    # predicate instead of V.
    #
    # F-structure shape:
    #
    #   PRED            = 'CARDINAL <SUBJ>'
    #   CARDINAL_VALUE  = the count from the cardinal
    #   NUM             = the cardinal's NUM (SG for isa/uno;
    #                     PL for the rest)
    #   SUBJ            = the NOM-NP pivot
    #
    # The PRED template ``CARDINAL <SUBJ>`` parallels other
    # predicative rules' literal-PRED convention. The semantic
    # interpretation "X is N in count" is downstream; the parser
    # delivers the structure.
    #
    # No VOICE / ASPECT / MOOD: a numeric predicate isn't a
    # verb and doesn't carry verbal morphology. Consumers
    # (LMT classifier, ranker) recognise the PRED shape.
    rules.append(Rule(
        "S",
        ["NUM[CARDINAL=YES]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'CARDINAL <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ CARDINAL_VALUE) = ↓1 CARDINAL_VALUE",
            "(↑ NUM) = ↓1 NUM",
        ],
    ))


    # --- Phase 5f closing deferral: predicative distributive cardinal ---
    #
    # ``Tigisang aklat sila.`` "they each have one book" — a
    # distributive cardinal predicating a possessed-N relation
    # over a NOM pronoun. Companion to the clause-initial dual Q
    # rule in ``cfg/clitic.py`` (covers both Phase 5f Commits 19 +
    # 23 plan §18 deferrals). The float-form alternant
    # ``Bumili sila ng tigisang aklat.`` already parses via the
    # NP-modifier rules.
    #
    # F-structure shape:
    #
    #   PRED            = 'CARDINAL <SUBJ, OBJ>'
    #   SUBJ            = the NOM-pivot pronoun (the possessors)
    #   OBJ             = the bare N (the per-possessor count)
    #   CARDINAL_VALUE  = the count from the cardinal
    #   DISTRIB         = 'YES'
    #   NUM             = the cardinal's NUM
    #
    # Constraining ``(↓1 DISTRIB) =c 'YES'`` restricts the rule
    # to genuinely distributive cardinals (``tigisa`` /
    # ``tigdalawa`` / ...) rather than firing on plain cardinals
    # (``isa`` / ``dalawa`` / ...) which would overgenerate to
    # ``Isang aklat sila.`` with no distributive reading.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "NUM[CARDINAL=YES]",
                f"PART[LINK={link}]",
                "N",
                "NP[CASE=NOM]",
            ],
            [
                "(↑ PRED) = 'CARDINAL <SUBJ, OBJ>'",
                "(↑ SUBJ) = ↓4",
                "(↑ OBJ) = ↓3",
                "(↑ CARDINAL_VALUE) = ↓1 CARDINAL_VALUE",
                "(↑ NUM) = ↓1 NUM",
                "(↑ DISTRIB) = 'YES'",
                "(↓1 CARDINAL) =c 'YES'",
                "(↓1 DISTRIB) =c 'YES'",
            ],
        ))


    # --- Phase 5f Commit 9: arithmetic predicates (Group D) -----
    #
    # Word-form arithmetic: ``Dalawa dagdag tatlo ay lima``
    # "2+3=5", ``Sampu bawas tatlo ay pito`` "10-3=7",
    # ``Dalawa beses tatlo ay anim`` "2*3=6", ``Anim hati sa
    # dalawa ay tatlo`` "6/2=3". The PART operators (dagdag /
    # bawas / beses / hati) are added in particles.yaml with
    # an ``OP`` feature.
    #
    # F-structure shape (matrix S):
    #   PRED       = 'ARITHMETIC <SUBJ>'
    #   OP         = 'PLUS' | 'MINUS' | 'TIMES' | 'DIVIDE'
    #   OPERAND_1  = the first cardinal's CARDINAL_VALUE
    #   OPERAND_2  = the second cardinal's CARDINAL_VALUE
    #   RESULT     = the result cardinal's CARDINAL_VALUE
    #
    # The constraining equation ``(↓2 OP) =c '...'`` enforces
    # that the operator daughter actually has the right OP
    # value (without the constraint, the non-conflict pattern
    # matcher would accept any PART since OP / LINK /
    # ASPECT_PART / DECIMAL_SEP don't share keys — same fix-
    # pattern as Commit 6's PART[DECIMAL_SEP=YES] constraint).
    #
    # Plus / minus / times share a 5-daughter shape; division
    # has 6 daughters because ``hati`` takes a ``sa``-marked
    # divisor (``hati sa dalawa`` "divided by two"). The
    # division operator's ``sa`` is a real DAT case marker, so
    # the rule's third daughter is ``ADP[CASE=DAT]``.
    for op_name in ("PLUS", "MINUS", "TIMES"):
        rules.append(Rule(
            "S",
            [
                "NUM[CARDINAL=YES]",
                "PART",
                "NUM[CARDINAL=YES]",
                "PART[LINK=AY]",
                "NUM[CARDINAL=YES]",
            ],
            [
                "(↑ PRED) = 'ARITHMETIC'",
                f"(↑ OP) = '{op_name}'",
                "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
                "(↑ OPERAND_2) = ↓3 CARDINAL_VALUE",
                "(↑ RESULT) = ↓5 CARDINAL_VALUE",
                f"(↓2 OP) =c '{op_name}'",
                "(↓1 CARDINAL) =c 'YES'",
                "(↓3 CARDINAL) =c 'YES'",
                "(↓5 CARDINAL) =c 'YES'",
            ],
        ))
    # Division: ``X hati sa Y ay Z``. 6 daughters; the divisor
    # carries DAT case via ``sa``.
    rules.append(Rule(
        "S",
        [
            "NUM[CARDINAL=YES]",
            "PART",
            "ADP[CASE=DAT]",
            "NUM[CARDINAL=YES]",
            "PART[LINK=AY]",
            "NUM[CARDINAL=YES]",
        ],
        [
            "(↑ PRED) = 'ARITHMETIC'",
            "(↑ OP) = 'DIVIDE'",
            "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
            "(↑ OPERAND_2) = ↓4 CARDINAL_VALUE",
            "(↑ RESULT) = ↓6 CARDINAL_VALUE",
            "(↓2 OP) =c 'DIVIDE'",
            "(↓1 CARDINAL) =c 'YES'",
            "(↓4 CARDINAL) =c 'YES'",
            "(↓6 CARDINAL) =c 'YES'",
        ],
    ))
    # Symbolic division: ``X / Y = Z``. Parallel 5-daughter rule
    # for the ``/`` PART form (no DAT marker before the divisor).
    # Companion to the ``+`` / ``-`` / ``*`` / ``=`` symbolic
    # operators added in particles.yaml under the digit
    # tokenization closing deferral; those three slot into the
    # word-form 5-daughter rule above unchanged. The constraining
    # ``(↓2 SYMBOLIC) =c 'YES'`` keeps this rule from firing on
    # word-form ``hati`` (which lacks ``SYMBOLIC=YES``); ``hati``
    # without ``sa`` is ungrammatical Tagalog and the existing
    # negative test ``*Anim hati dalawa ay tatlo`` confirms it
    # shouldn't parse. (Phase 5f closing deferral, 2026-05-04.)
    rules.append(Rule(
        "S",
        [
            "NUM[CARDINAL=YES]",
            "PART",
            "NUM[CARDINAL=YES]",
            "PART[LINK=AY]",
            "NUM[CARDINAL=YES]",
        ],
        [
            "(↑ PRED) = 'ARITHMETIC'",
            "(↑ OP) = 'DIVIDE'",
            "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
            "(↑ OPERAND_2) = ↓3 CARDINAL_VALUE",
            "(↑ RESULT) = ↓5 CARDINAL_VALUE",
            "(↓2 OP) =c 'DIVIDE'",
            "(↓2 SYMBOLIC) =c 'YES'",
            "(↓1 CARDINAL) =c 'YES'",
            "(↓3 CARDINAL) =c 'YES'",
            "(↓5 CARDINAL) =c 'YES'",
        ],
    ))


    # --- Phase 5b: multi-GEN-NP applicative frames (IV-BEN) ---
    #
    # Three-argument applicatives like ``Ipinaggawa niya ng silya
    # ang kapatid`` ("he made a chair for his sibling") have two
    # ng-marked non-pivots (AGENT + PATIENT) plus the ang-marked
    # pivot (BENEFICIARY). The Phase 5 LMT engine produces typed
    # ``OBJ-AGENT`` and ``OBJ-PATIENT`` for the two ng-NPs (per
    # the [+r, +o] truth-table cell); these are distinct GFs
    # under :func:`is_governable_gf` and don't clash by
    # biuniqueness.
    #
    # Word-order convention: the first ng-NP after V is AGENT,
    # the second is PATIENT (Schachter & Otanes 1972 §6.5;
    # Kroeger 1993 §3.3 on post-V positioning). When the pivot
    # ang-NP intervenes, the AGENT/PATIENT order across the
    # ang-NP is preserved (i.e., the two ng-NPs that flank or
    # follow the ang-NP are still AGENT-then-PATIENT in surface
    # order).
    #
    # Scope: IV-BEN only in this commit. pa-OV-direct three-arg
    # causatives use the same shape and lift trivially with new
    # grammar rules + lex entries; deferred until commit 2 so
    # this commit's analytical commitment can be reviewed
    # against the IV-BEN corpus first.
    v_iv = "V[VOICE=IV]"
    # NOM-GEN-GEN: pivot first, AGENT, PATIENT.
    rules.append(Rule(
        "S",
        [v_iv, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-AGENT) = ↓3",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-NOM-GEN: AGENT, pivot, PATIENT.
    rules.append(Rule(
        "S",
        [v_iv, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-AGENT) = ↓2",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-GEN-NOM: AGENT, PATIENT, pivot.
    rules.append(Rule(
        "S",
        [v_iv, "NP[CASE=GEN]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓4",
            "(↑ OBJ-AGENT) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
        ),
    ))


    # --- Phase 5b: multi-GEN-NP causative frames (pa-OV direct) ---
    #
    # Three-argument direct causatives like ``Pinakain niya ng
    # kanin ang bata`` ("he fed the child rice") have two
    # ng-marked non-pivots (CAUSER + PATIENT) plus the
    # ang-marked pivot (CAUSEE). Same architectural shape as
    # the IV-BEN multi-GEN rules above; the difference is the
    # role names — CAUSER replaces AGENT, CAUSEE replaces
    # BENEFICIARY — so the grammar binds to typed OBJ-CAUSER
    # rather than OBJ-AGENT.
    #
    # Word-order convention is identical: first ng-NP after V
    # is CAUSER (the agentive instigator), second is PATIENT
    # (the affected entity).
    #
    # Rules are matched on V[VOICE=OV, CAUS=DIRECT] specifically
    # so they don't fire for plain OV transitives (which have
    # no third role). The non-conflict matcher requires the
    # default ``CAUS=NONE`` on plain OV V analyses to keep
    # them from spuriously matching.
    v_pa_ov = "V[VOICE=OV, CAUS=DIRECT]"
    # NOM-GEN-GEN: pivot first, CAUSER, PATIENT.
    rules.append(Rule(
        "S",
        [v_pa_ov, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-CAUSER) = ↓3",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-NOM-GEN: CAUSER, pivot, PATIENT.
    rules.append(Rule(
        "S",
        [v_pa_ov, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-CAUSER) = ↓2",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-GEN-NOM: CAUSER, PATIENT, pivot.
    rules.append(Rule(
        "S",
        [v_pa_ov, "NP[CASE=GEN]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓4",
            "(↑ OBJ-CAUSER) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
        ),
    ))


    # --- Phase 5e Commit 11: multi-GEN-NP plain DV (CAUS=NONE) ---
    #
    # Three-argument DV ditransitives like
    # ``Sinulatan ng nanay ng letra ang anak`` ("Mother wrote a
    # letter to the child") have two ng-marked non-pivots
    # (AGENT + PATIENT) plus the ang-marked pivot (RECIPIENT —
    # DV's broad voice category covers location / recipient /
    # dative; for animate pivots like ``ang anak`` the reading
    # is recipient).
    #
    # Same structural shape as the Phase 5b multi-GEN-NP pa-OV
    # and Phase 5e Commit 10 multi-GEN-NP pa-DV rules above,
    # with CAUS=NONE matching plain (non-causative) DV.
    # First ng-NP is AGENT; second is PATIENT — same Phase 5b
    # positional convention.
    v_dv_plain = "V[VOICE=DV, CAUS=NONE]"
    # NOM-GEN-GEN: pivot first, AGENT, PATIENT.
    rules.append(Rule(
        "S",
        [v_dv_plain, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-AGENT) = ↓3",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-NOM-GEN: AGENT, pivot, PATIENT.
    rules.append(Rule(
        "S",
        [v_dv_plain, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-AGENT) = ↓2",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-GEN-NOM: AGENT, PATIENT, pivot.
    rules.append(Rule(
        "S",
        [v_dv_plain, "NP[CASE=GEN]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓4",
            "(↑ OBJ-AGENT) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
        ),
    ))


    # --- Phase 5e Commit 10: multi-GEN-NP causative frames (pa-DV direct) ---
    #
    # Three-argument direct DV causatives like
    # ``Pinakainan ng nanay ng kanin ang bata`` ("Mother fed
    # rice to the child") have two ng-marked non-pivots
    # (CAUSER + PATIENT) plus the ang-marked pivot (LOCATION /
    # recipient / dative — the role label that DV's broad
    # voice category covers). Same structural shape as the
    # Phase 5b multi-GEN-NP pa-OV-direct rules above; the
    # difference is the SUBJ-mapped role (LOCATION instead of
    # CAUSEE) and the lex profile.
    #
    # Word-order convention is identical to pa-OV: first ng-NP
    # after V is CAUSER (the agentive instigator), second is
    # PATIENT (the affected entity). The pivot ang-NP can
    # intervene at any of the three permutations.
    v_pa_dv = "V[VOICE=DV, CAUS=DIRECT]"
    # NOM-GEN-GEN: pivot first, CAUSER, PATIENT.
    rules.append(Rule(
        "S",
        [v_pa_dv, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ-CAUSER) = ↓3",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-NOM-GEN: CAUSER, pivot, PATIENT.
    rules.append(Rule(
        "S",
        [v_pa_dv, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-CAUSER) = ↓2",
            "(↑ OBJ-PATIENT) = ↓4",
        ),
    ))
    # GEN-GEN-NOM: CAUSER, PATIENT, pivot.
    rules.append(Rule(
        "S",
        [v_pa_dv, "NP[CASE=GEN]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓4",
            "(↑ OBJ-CAUSER) = ↓2",
            "(↑ OBJ-PATIENT) = ↓3",
        ),
    ))

    # Phase 5c §8 follow-on (Commit 6): AV transitive frame
    # with two trailing sa-NPs — exercises the multi-OBL
    # semantic-disambiguation classifier. Both NP[CASE=DAT]
    # land in ADJUNCT; ``classify_oblique_slots`` then moves
    # them into typed ``OBL-RECIP`` / ``OBL-LOC`` slots based
    # on each sa-NP's head-noun semantic class. Two NP order
    # variants (NOM-GEN and GEN-NOM); the two sa-NPs can
    # appear in either order — the classifier disambiguates
    # by lemma class, not surface order.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
            "NP[CASE=DAT]",
            "NP[CASE=DAT]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓3",
            "↓4 ∈ (↑ ADJUNCT)",
            "↓5 ∈ (↑ ADJUNCT)",
        ),
    ))
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV]",
            "NP[CASE=GEN]",
            "NP[CASE=NOM]",
            "NP[CASE=DAT]",
            "NP[CASE=DAT]",
        ],
        _eqs(
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ) = ↓2",
            "↓4 ∈ (↑ ADJUNCT)",
            "↓5 ∈ (↑ ADJUNCT)",
        ),
    ))


    # --- Phase 5g Commit 3: predicative adjective clause ---------
    #
    # ``Maganda ang bata.`` "The child is beautiful."
    # ``Matanda siya.`` "She is old."   (R&G 1981 §12.9 benchmark)
    # ``Maliit ang bahay.`` "The house is small."   (R&G 1981 §12.9)
    # ``Mataas ang bundok.`` "The mountain is high."   (R&G 1981 §12.9)
    #
    # Verbless adj-pred clause: an ADJ head with intrinsic
    # ``PREDICATIVE=YES`` (set by the analyzer's adjective indexer
    # for all forms produced by the productive ``ma-`` paradigm)
    # plus a NOM-NP / NOM-PRON pivot. Structurally analogous to
    # the Phase 5e Commit 26 ``parang`` comparative and the
    # Phase 5f Commit 4 predicative-cardinal: a non-V matrix
    # predicate selecting a SUBJ ang-NP.
    #
    # F-structure shape:
    #
    #   PRED         = 'ADJ <SUBJ>'
    #   ADJ_LEMMA    = the adjective's lemma (bare root —
    #                  ``ganda``, ``tanda``, ``talino``, ...)
    #   PREDICATIVE  = 'YES'
    #   SUBJ         = the NOM-NP / NOM-PRON pivot
    #
    # The PRED template ``ADJ <SUBJ>`` parallels other predicative
    # rules' literal-PRED convention (``CARDINAL <SUBJ>`` for
    # predicative cardinals, ``LIKE <SUBJ, OBJ>`` for parang). The
    # adjective's identity is preserved on the matrix via
    # ``ADJ_LEMMA`` (a Phase-5g-specific attribute name to avoid
    # the ambiguity of plain ``LEMMA`` on a clausal f-structure).
    #
    # The constraining equation ``(↓1 PREDICATIVE) =c 'YES'`` is
    # belt-and-braces — the rule's RHS already filters on
    # ``ADJ[PREDICATIVE=YES]`` at the category-pattern level — but
    # makes the analytical commitment explicit and guards against
    # future lex entries with PREDICATIVE=NO (modifier-only
    # adjectives, if introduced).
    #
    # No VOICE / ASPECT / MOOD: an adjective predicate isn't a
    # verb and doesn't carry verbal morphology (the analytical
    # commitment of roadmap §12.1 — ``*pumagmaganda`` etc. are
    # ungrammatical).
    rules.append(Rule(
        "S",
        ["ADJ[PREDICATIVE=YES]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = 'YES'",
            "(↓1 PREDICATIVE) =c 'YES'",
        ],
    ))


    # --- Phase 5g Commit 5: manner-adverb (S-level) -----------
    #
    # ``Mabilis na tumakbo siya.`` "She ran quickly."
    # ``Magandang kumain ang bata.`` "The child ate beautifully."
    # ``Malakas na sumigaw siya.`` "He shouted loudly."
    #
    # The same lex / linker machinery that drives NP-internal
    # adjective modification (Phase 5g Commit 2) also produces the
    # manner-adverb form: an adjective + linker + verbal clause
    # where the adjective modifies the verb's manner. Per roadmap
    # §12.1: "Manner adverb form (``mabilis na tumakbo`` "ran
    # quickly") is the predicative-adj surface used adverbially;
    # the same lex / linker machinery covers it."
    #
    # **S-level attachment.** The rule wraps the inner verbal S
    # with an outer S that adds the adjective as an adjunct of
    # the matrix proposition. ``(↑) = ↓3`` shares the inner S's
    # f-structure (so VOICE / ASPECT / MOOD / SUBJ / OBJ / etc.
    # all percolate to the matrix); ``↓1 ∈ (↑ ADJ)`` adds the
    # manner adjective as a member of the matrix S's adjunct set.
    # The rule does NOT add a V-level non-terminal (``V →
    # ADJ PART V``) because V is currently a lex preterminal and
    # introducing a V-LHS rule would break the parser's SCAN
    # (categories that ever appear as a rule LHS become
    # non-terminals; tokens with ``pos: VERB`` would no longer
    # match SCAN's V slot in V-headed clausal frames).
    #
    # Two link variants — ``na`` for consonant-final adjectives
    # (``mabilis na``) and the bound ``-ng`` for vowel-final
    # adjectives (``magandang``, split by ``split_linker_ng``).
    #
    # The adjective sits on the matrix S's ``ADJ`` set alongside
    # any 2P clitic adjuncts (``na`` ALREADY, ``pa`` STILL,
    # ``ba`` Q-PARTICLE) and sentential PP / AdvP adjuncts. This
    # is the same slot the relativization wrap rules use for RC
    # attachment — adjuncts of the matrix proposition.
    #
    # No PRED override: the matrix S's PRED comes from the inner
    # S (the verbal predicate). The manner-adverb's identity is
    # accessible by traversing the matrix's ADJ adjunct set.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            ["ADJ", f"PART[LINK={link}]", "S"],
            [
                "(↑) = ↓3",
                "↓1 ∈ (↑ ADJ)",
            ],
        ))


    # --- Phase 5h Commit 4: kaysa comparison-complement -------
    #
    # ``Mas matalino siya kaysa kay Maria.``
    #     "She is more intelligent than Maria."
    # ``Mas mabilis ang kabayo kaysa sa aso.``
    #     "The horse is faster than the dog."
    # ``Mas maganda ang bahay kaysa sa kapatid niya.``
    #     "Her house is more beautiful than her sibling's."
    #
    # The PART ``kaysa`` (lex feat ``COMP_PHRASE: KAYSA`` — added in
    # particles.yaml in this commit) heads a comparison-complement
    # phrase that adjoins to the matrix S as an ADJUNCT member with
    # ``ROLE: STANDARD``. The DAT-NP daughter is structured by the
    # existing Phase 4 ``kay`` (HUMAN) / ``sa`` (default) ADP
    # machinery, so ``kaysa kay Maria`` and ``kaysa sa kapatid``
    # are both well-formed without new NP rules.
    #
    # Structurally analogous to the Phase 5f Commit 17 numeric
    # comparator family (``higit sa N`` / ``kulang sa N`` /
    # ``bababa sa N`` / ``hihigit sa N``) — same ``COMP_PHRASE``
    # feature namespace, same wrap-an-NP-in-DAT-case pattern. The
    # difference is the comparison domain: numeric comparators
    # wrap a NUM head's standard, kaysa wraps the comparative-ADJ
    # clause's standard.
    #
    # **Equation analysis**:
    #
    # * ``(↑) = ↓1`` — matrix S inherits the inner S's f-structure
    #   (PRED, SUBJ, ADJ_LEMMA, COMP_DEGREE, etc., all percolate
    #   through). The kaysa-headed adjunct rides on top of this
    #   shared f-structure.
    # * ``↓3 ∈ (↑ ADJUNCT)`` — the standard NP joins the matrix's
    #   ADJUNCT set. The grammar's ranker / classifier can find
    #   the comparison standard by walking the ADJUNCT set looking
    #   for ROLE=STANDARD members.
    # * ``(↓3 ROLE) = 'STANDARD'`` — the standard NP carries
    #   ROLE: STANDARD on its f-structure so it's distinguishable
    #   from other ADJUNCT members (locative DAT-NPs, manner
    #   adverbs, etc.).
    # * ``(↓2 COMP_PHRASE) =c 'KAYSA'`` — belt-and-braces
    #   constraint on the PART daughter (matches the Phase 5f
    #   Commit 17 / Phase 5h Commit 3 ``=c`` pattern).
    #
    # The plan does NOT constrain the inner S to carry
    # ``COMP_DEGREE: COMPARATIVE``. Tagalog usage typically pairs
    # ``kaysa`` with ``mas``, but bare comparisons
    # (``Matalino si Maria kaysa kay Juan``) are attested
    # colloquially; the permissive rule accepts both. Tightening
    # would need COMP_DEGREE to be lifted onto the matrix S by
    # the Phase 5g predicative-adj clause rule (which currently
    # keeps it on the ADJ daughter); deferred.
    rules.append(Rule(
        "S",
        ["S", "PART[COMP_PHRASE=KAYSA]", "NP[CASE=DAT]"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↓3 ROLE) = 'STANDARD'",
            "(↓2 COMP_PHRASE) =c 'KAYSA'",
        ],
    ))
