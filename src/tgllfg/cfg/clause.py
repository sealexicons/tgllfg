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
