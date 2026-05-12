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
    # The constraining equation ``(↓1 COMPARATIVE) =c true``
    # restricts to ``parang`` only — the category-pattern
    # matcher (``compile.py::matches``) is non-conflict, so
    # ``V[COMPARATIVE, CTRL_CLASS=RAISING_BARE]`` would
    # also match ``tila`` (RAISING_BARE without COMPARATIVE) by
    # absorption without the explicit constraint.
    #
    # The existing evidential rule (Phase 5d Commit 1) for
    # ``parang + clause`` continues to fire on ``Parang kumain
    # ang bata`` (parang followed by V, not bare N) — different
    # rule shape, no competition.
    rules.append(Rule(
        "S",
        ["V[COMPARATIVE, CTRL_CLASS=RAISING_BARE]", "N", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'LIKE <SUBJ, OBJ>'",
            "(↑ OBJ) = ↓2",
            "(↑ SUBJ) = ↓3",
            "(↓1 COMPARATIVE) =c true",
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
    # evidential parang) but with NUM[CARDINAL] as the
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
        ["NUM[CARDINAL]", "NP[CASE=NOM]"],
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
    # Constraining ``(↓1 DISTRIB) =c true`` restricts the rule
    # to genuinely distributive cardinals (``tigisa`` /
    # ``tigdalawa`` / ...) rather than firing on plain cardinals
    # (``isa`` / ``dalawa`` / ...) which would overgenerate to
    # ``Isang aklat sila.`` with no distributive reading.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "NUM[CARDINAL]",
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
                "(↑ DISTRIB) = true",
                "(↓1 CARDINAL) =c true",
                "(↓1 DISTRIB) =c true",
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
    # pattern as Commit 6's PART[DECIMAL_SEP] constraint).
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
                "NUM[CARDINAL]",
                "PART",
                "NUM[CARDINAL]",
                "PART[LINK=AY]",
                "NUM[CARDINAL]",
            ],
            [
                "(↑ PRED) = 'ARITHMETIC'",
                f"(↑ OP) = '{op_name}'",
                "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
                "(↑ OPERAND_2) = ↓3 CARDINAL_VALUE",
                "(↑ RESULT) = ↓5 CARDINAL_VALUE",
                f"(↓2 OP) =c '{op_name}'",
                "(↓1 CARDINAL) =c true",
                "(↓3 CARDINAL) =c true",
                "(↓5 CARDINAL) =c true",
            ],
        ))
    # Division: ``X hati sa Y ay Z``. 6 daughters; the divisor
    # carries DAT case via ``sa``.
    rules.append(Rule(
        "S",
        [
            "NUM[CARDINAL]",
            "PART",
            "ADP[CASE=DAT]",
            "NUM[CARDINAL]",
            "PART[LINK=AY]",
            "NUM[CARDINAL]",
        ],
        [
            "(↑ PRED) = 'ARITHMETIC'",
            "(↑ OP) = 'DIVIDE'",
            "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
            "(↑ OPERAND_2) = ↓4 CARDINAL_VALUE",
            "(↑ RESULT) = ↓6 CARDINAL_VALUE",
            "(↓2 OP) =c 'DIVIDE'",
            "(↓1 CARDINAL) =c true",
            "(↓4 CARDINAL) =c true",
            "(↓6 CARDINAL) =c true",
        ],
    ))
    # Symbolic division: ``X / Y = Z``. Parallel 5-daughter rule
    # for the ``/`` PART form (no DAT marker before the divisor).
    # Companion to the ``+`` / ``-`` / ``*`` / ``=`` symbolic
    # operators added in particles.yaml under the digit
    # tokenization closing deferral; those three slot into the
    # word-form 5-daughter rule above unchanged. The constraining
    # ``(↓2 SYMBOLIC) =c true`` keeps this rule from firing on
    # word-form ``hati`` (which lacks ``SYMBOLIC=YES``); ``hati``
    # without ``sa`` is ungrammatical Tagalog and the existing
    # negative test ``*Anim hati dalawa ay tatlo`` confirms it
    # shouldn't parse. (Phase 5f closing deferral, 2026-05-04.)
    rules.append(Rule(
        "S",
        [
            "NUM[CARDINAL]",
            "PART",
            "NUM[CARDINAL]",
            "PART[LINK=AY]",
            "NUM[CARDINAL]",
        ],
        [
            "(↑ PRED) = 'ARITHMETIC'",
            "(↑ OP) = 'DIVIDE'",
            "(↑ OPERAND_1) = ↓1 CARDINAL_VALUE",
            "(↑ OPERAND_2) = ↓3 CARDINAL_VALUE",
            "(↑ RESULT) = ↓5 CARDINAL_VALUE",
            "(↓2 OP) =c 'DIVIDE'",
            "(↓2 SYMBOLIC) =c true",
            "(↓1 CARDINAL) =c true",
            "(↓3 CARDINAL) =c true",
            "(↓5 CARDINAL) =c true",
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

    # --- Phase 5n.A Commit 27: OV-with-finite-S complement (§18 L89.2) ---
    #
    # SAY-class verbs in OV admit a finite-S complement bound to
    # SUBJ. The said-thing is a full clause rather than a NOM-NP;
    # the actor is a clitic GEN-PRON and the complementizer is
    # ``na``. Per LFG completeness/coherence, the OV a-structure
    # of ``sabi`` is ``<AGENT, THEME>`` with THEME mapped to SUBJ
    # (Phase 4 LMT); the finite-S fills the THEME-as-SUBJ slot.
    #
    #   ``Sinabi niya na pumunta si Maria.`` "She said that Maria
    #                                         went."
    #   ``Sasabihin nila na bumili kami ng aklat.``
    #                                  "They will say that we'll
    #                                   buy a book."
    #   + 10 more in tests/tgllfg/data/coverage_corpus.yaml
    #     under the Phase 5n.A Commit 26 banner.
    #
    # Gating choices (per plan-of-record §3.5 Commit 27 drill-down):
    #
    # * **SAY_CLASS=YES** on ↓1 — narrow gate that preserves Phase 4
    #   SUBJ-as-NOM-NP default for non-SAY-class OV verbs. Only
    #   ``sabi`` carries SAY_CLASS=YES in the seed lex (Phase 5l
    #   Commit 10); other OV verbs continue to require NOM-NP SUBJ.
    #
    # * **PRON[CASE=GEN]** actor (not full NP) — sidesteps the
    #   existing N-headed RC-linker ``na`` path which misanalyzes
    #   ``Sinabi ng lalaki na pumunta si Maria.`` as
    #   ``[ng lalaki] [na pumunta]`` (RC-modified GEN-NP, with
    #   Maria as the matrix SUBJ via the regular OV-2NP frame).
    #   PRONs don't take RC linkers, so the new rule fires
    #   unambiguously when the actor is a clitic-PRON. Full-NP
    #   actor support is deferred (would require a tighter
    #   constraint on the RC path).
    #
    # * **PART[LINK=NA]** for the complementizer — the standalone
    #   ``na`` particle (which also has an ALREADY-clitic reading
    #   that is rejected by the LINK=NA constraint, and a
    #   bound-linker LINK=NG variant from ``-ng`` that doesn't
    #   apply here). The non-conflict matcher accepts the
    #   clitic-``na`` analysis too (since CLITIC_CLASS doesn't
    #   conflict with LINK=NA's absence of CLITIC_CLASS), but
    #   the constraining ``(↓3 LINK) =c 'NA'`` rejects it.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=OV, SAY_CLASS]",
            "PRON[CASE=GEN]",
            "PART[LINK=NA]",
            "S",
        ],
        _eqs(
            "(↑ OBJ-AGENT) = ↓2",
            "(↑ SUBJ) = ↓4",
            "(↓1 SAY_CLASS) =c true",
            "(↓3 LINK) =c 'NA'",
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
    # The constraining equation ``(↓1 PREDICATIVE) =c true`` is
    # belt-and-braces — the rule's RHS already filters on
    # ``ADJ[PREDICATIVE]`` at the category-pattern level — but
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
        ["ADJ[PREDICATIVE]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
            # Phase 5n.C.3 Commit 7 (§18 L37): lift INTENS from the
            # ADJ daughter to the matrix so downstream consumers
            # see the reduplicated-intensive reading on the matrix
            # S. The Phase 5n.C.3 ``redup_intens_adj`` paradigm
            # cell tags ADJ surfaces with ``INTENS: MILD``;
            # daughter ADJs without INTENS leave the matrix INTENS
            # undefined (no-op via unification semantics).
            "(↑ INTENS) = ↓1 INTENS",
        ],
    ))


    # --- Phase 5n.B Commit 1: predicative-Q clause (§18 L42 + L52) ---
    #
    # ``Marami ang aklat.``       "There are many books."
    # ``Konti ang isda.``         "There are few fish."
    # ``Mas marami ang aklat.``   "There are more books." (Phase 5h
    #                              Commit 7 mas-wrapped Q)
    #
    # Closes §18 deferrals L42 (``Mas marami ang aklat.`` —
    # surfaced during Phase 5h Commit 7 implementation, pinned at
    # 0-parse) and L52 (``Marami ang aklat.`` — non-wh predicative-
    # Q identified during Phase 5i Commit 9 implementation). Per
    # plan ``tgllfg-phase-5n.md`` §4.1 Commit 1 the two resolutions
    # land in a single rule.
    #
    # Structurally analogous to the Phase 5g Commit 3 predicative-
    # ADJ rule (S → ADJ[PREDICATIVE] NP[CASE=NOM]) and the
    # Phase 5f Commit 4 predicative-cardinal rule (S → NUM
    # [CARDINAL] NP[CASE=NOM]) above; the same shape with a
    # vague-Q head as the matrix predicate.
    #
    # F-structure shape:
    #
    #   PRED        = 'Q-PREDICATIVE <SUBJ>'
    #   Q_LEMMA     = the Q's lemma (``marami``, ``konti``,
    #                  ``kakaunti``, ``ilan`` — both polysemy
    #                  partners — and ``karamihan``)
    #   QUANT       = the Q's QUANT (MANY / FEW / VERY_FEW / MOST)
    #   PREDICATIVE = 'YES'
    #   SUBJ        = the NOM-NP / NOM-PRON pivot
    #
    # The PRED template ``Q-PREDICATIVE <SUBJ>`` parallels other
    # predicative rules' literal-PRED convention (``ADJ <SUBJ>`` for
    # Phase 5g predicative-adj; ``CARDINAL <SUBJ>`` for Phase 5f
    # predicative-cardinal; ``LIKE <SUBJ, OBJ>`` for Phase 5e
    # parang). The Q's identity rides on the matrix via ``Q_LEMMA``
    # rather than plain ``LEMMA`` (parallel to ``ADJ_LEMMA`` for
    # the predicative-adj rule).
    #
    # **Disambiguation against the Phase 5i Commit 9 (a) wh-Q cleft**.
    # The wh-Q cleft fires on ``Q[WH]`` (e.g., ``Magkano ang
    # isda?``, ``Ilan ang aklat?`` wh reading) and produces ``PRED='WH
    # <SUBJ>'`` / ``Q_TYPE=WH``. The new predicative-Q rule must NOT
    # fire on wh-Qs to avoid ambiguity blowup with two distinct PREDs
    # on the same surface. The ``¬ (↓1 WH)`` neg-existential constraint
    # enforces this — the rule fires only when WH is undefined on
    # the Q daughter (i.e., bare ``marami`` / ``konti`` and the
    # mas-wrapped / pinaka-wrapped variants, which inherit
    # ``(↑) = ↓2`` from the wrapped vague-Q with no WH feat).
    #
    # **Polysemy partners**: ``ilan`` is double-lex'd as Q[WH,
    # QUANT=HOW_MANY, VAGUE] (wh use) and Q[QUANT=FEW,
    # VAGUE=YES] (non-wh "a few" reading). The wh entry feeds the
    # cleft; the FEW entry feeds this predicative-Q rule.
    #
    # **Belt-and-braces** ``(↓1 VAGUE) =c true`` mirrors the Phase
    # 5h Commit 7 wrapper convention — closes the same kind of
    # non-conflict-matcher leak by constraining the f-structure
    # daughter explicitly (rather than relying on the c-tree
    # category-pattern alone).
    #
    # Cardinal contrast — ``Tatlo ang aklat.`` parses via the Phase
    # 5f Commit 4 predicative-cardinal rule (NUM[CARDINAL] head),
    # which has no VAGUE feat and so does not fire this rule. Each
    # predicative shape (vague-Q, cardinal, ADJ) has its own clause
    # rule with disjoint head categories.
    rules.append(Rule(
        "S",
        ["Q[VAGUE]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'Q-PREDICATIVE <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_LEMMA) = ↓1 LEMMA",
            "(↑ QUANT) = ↓1 QUANT",
            "(↑ PREDICATIVE) = true",
            "(↓1 VAGUE) =c true",
            "¬ (↓1 WH)",
        ],
    ))


    # --- Phase 5n.B Commit 2: predicative-N clause (§18 L43) ---
    #
    # ``Doktor ako.``                "I am a doctor."
    # ``Estudyante si Maria.``       "Maria is a student."
    # ``Lider siya.``                "He is the leader."
    # ``Mas maraming aklat ako.``    "I have more books." (lit.
    #                                 "more-books I am")
    # ``Maliit na bahay ito.``       "This is a small house."
    #
    # Closes §18 deferral L43 (``Mas maraming aklat ako.`` —
    # surfaced during Phase 5h Commit 9 corpus expansion). Tagalog
    # admits bare-NP predication with no copula; the predicate
    # is an N-headed phrase (bare N or N modified by ADJ / Q via
    # the existing N-level modifier rules) and the SUBJ is a
    # NOM-NP / NOM-PRON pivot.
    #
    # Structurally analogous to the Phase 5g Commit 3 predicative-
    # ADJ rule (S → ADJ[PREDICATIVE] NP[CASE=NOM]), the Phase
    # 5f Commit 4 predicative-cardinal rule (S → NUM[CARDINAL]
    # NP[CASE=NOM]), and the Phase 5n.B Commit 1 predicative-Q
    # rule above (S → Q[VAGUE] NP[CASE=NOM]). Each predicative
    # head category has its own clause rule; this one covers the
    # N-headed predicate.
    #
    # F-structure shape:
    #
    #   PRED        = 'BE-N <SUBJ>'
    #   N_LEMMA     = the predicate noun's lemma (the "what" of
    #                  the predication — ``doktor`` / ``estudyante``
    #                  / ``lider`` / ``aklat`` / ...)
    #   PREDICATIVE = 'YES'
    #   SUBJ        = the NOM-NP / NOM-PRON pivot
    #
    # The PRED template ``BE-N <SUBJ>`` parallels other predicative
    # rules' literal-PRED convention. Tagalog does not formally
    # distinguish equational ("I am a doctor") from possessive
    # ("I have more books") readings of bare-NP predication —
    # both surface identically and the disambiguation is semantic /
    # contextual. The single PRED template captures both.
    #
    # **Gating**: the rule fires only on N-headed left daughters
    # without ``WH`` to avoid colliding with the Phase 5i Commit 6
    # wh-N cleft (S → N[WH] NP[CASE=NOM]). The ``¬ (↓1 WH)``
    # neg-existential constraint excludes ``Aling bata si Maria?``
    # (which fires the wh-cleft) from also producing a predicative-
    # N parse with PRED='BE-N <SUBJ>'.
    #
    # **N category**: the left daughter is the bare ``N``
    # category (not ``NP``), which matches both:
    #   - bare nouns (``doktor`` directly out of the morph analyzer);
    #   - N-modified-by-ADJ via Phase 5g Commit 2 (``magandang
    #     bata``);
    #   - N-modified-by-Q via Phase 5f Commit 15 N-level companion
    #     rule (``maraming aklat``);
    #   - N-modified by mas-comparative via the wrapper percolation
    #     (``mas maraming aklat``).
    # NPs (DET-marked, CASE-bearing) do NOT match — a left-edge
    # ``ang doktor`` does not fire this rule, which keeps two-NP
    # equational surfaces (``Ang lalaki ang doktor.``) out of
    # scope. Those remain as out-of-scope until corpus pressure
    # surfaces them.
    rules.append(Rule(
        "S",
        ["N", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-N <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ N_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "¬ (↓1 WH)",
        ],
    ))


    # --- Phase 5h Commit 6: equative two-NP standard frames -----
    #
    # ``Kasingganda ni Maria si Ana.``
    #     "Ana is as beautiful as Maria."
    # ``Kasingganda ng bahay mo ang bahay ko.``
    #     "My house is as beautiful as your house."
    # ``Kasingganda si Maria si Ana.``
    #     "Maria is as beautiful as Ana." (two-NOM colloquial form)
    #
    # The kasing- / sing- equative cells (Phase 5h Commit 2) produce
    # ADJ surfaces with ``COMP_DEGREE: EQUATIVE``. The Phase 5g
    # predicative-adj clause rule (above) handles single-NP
    # predicatives (``Kasingganda ang bahay``); these three rules
    # handle the two-NP standard-of-comparison construction where
    # the comparee is NOM-marked and the standard is GEN- or NOM-
    # marked.
    #
    # **Why three rules**: Tagalog freely permits the two NPs to
    # appear in either order (NOM-then-GEN or GEN-then-NOM), and
    # the two-NOM variant is a separate pattern. Rule duplication
    # is preferred over a single permissive rule because the
    # SUBJ ↔ NP mapping is order-dependent (the comparee is the
    # NOM-NP regardless of position; the standard is whichever
    # daughter is non-comparee).
    #
    # **Standard NP analysis**: the comparison standard rides on
    # the matrix's ADJUNCT set with ``ROLE: EQUATIVE_STANDARD``.
    # This parallels Phase 5h Commit 4's ``kaysa`` rule, which uses
    # ``ROLE: STANDARD`` on the kaysa-NP. The two ROLE values are
    # distinct because the constructions are analytically separate:
    # ``kaysa`` introduces an oblique standard for graded comparison
    # (with ``mas``), while the equative standard sits directly in
    # the predicate's argument position without an oblique marker.
    #
    # **Constraining equation** ``(↓1 COMP_DEGREE) =c 'EQUATIVE'``
    # restricts these rules to equative-marked ADJ heads
    # (``kasingganda``, ``singganda``, ``pareho``, ``magkapareho``,
    # ``magkaiba``). Other-degree-marked ADJs (SUPERLATIVE,
    # COMPARATIVE, INTENSIVE, CONTRASTIVE) parse the single-NP
    # predicative form via the Phase 5g rule above; the two-NP
    # frames do not fire on them.
    #
    # **Why not a NP[CASE=DAT] standard variant**: the
    # ``Kasingganda kay Maria si Ana`` (DAT-standard) form is
    # marginal in modern Tagalog per S&O 1972 / R&B 1986; GEN
    # standard is canonical, two-NOM is colloquial. If corpus
    # pressure surfaces DAT-standard usage, a fourth rule lands
    # as a Phase 5h follow-on.

    # NOM comparee + GEN standard: ``Pareho ng sapatos ni Maria
    # ang sapatos ni Ana`` — "Ana's shoes are the same as Maria's
    # shoes". Order (NOM, GEN) variant.
    rules.append(Rule(
        "S",
        [
            "ADJ[COMP_DEGREE=EQUATIVE]",
            "NP[CASE=NOM]",
            "NP[CASE=GEN]",
        ],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
            "(↓1 COMP_DEGREE) =c 'EQUATIVE'",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↓3 ROLE) = 'EQUATIVE_STANDARD'",
        ],
    ))

    # GEN standard + NOM comparee: ``Kasingganda ni Maria si Ana`` —
    # canonical Schachter-Otanes shape. Order (GEN, NOM) variant.
    rules.append(Rule(
        "S",
        [
            "ADJ[COMP_DEGREE=EQUATIVE]",
            "NP[CASE=GEN]",
            "NP[CASE=NOM]",
        ],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
            "(↓1 COMP_DEGREE) =c 'EQUATIVE'",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 ROLE) = 'EQUATIVE_STANDARD'",
        ],
    ))

    # Two-NOM: ``Kasingganda si Maria si Ana`` — colloquial form
    # where both arguments take the NOM proper-noun marker. The
    # plan §5.6 first-NP-as-comparee convention applies: ↓2 is
    # the SUBJ, ↓3 is the standard.
    rules.append(Rule(
        "S",
        [
            "ADJ[COMP_DEGREE=EQUATIVE]",
            "NP[CASE=NOM]",
            "NP[CASE=NOM]",
        ],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
            "(↓1 COMP_DEGREE) =c 'EQUATIVE'",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↓3 ROLE) = 'EQUATIVE_STANDARD'",
        ],
    ))

    # --- Phase 5n.B Commit 6: equative DAT-standard variant (§18 L44) ---
    #
    # ``Kasingganda kay Maria si Ana.``
    #     "Ana is as beautiful as Maria." (DAT-standard, formal /
    #     marginal alternative to the GEN-standard canonical form)
    #
    # Closes §18 L44 (carried forward from Phase 5h §9.2 / Commit
    # 6 audit). The GEN-standard form (``Kasingganda ni Maria si
    # Ana``) is canonical per S&O 1972 / R&B 1986 and lives in
    # the third equative rule above. The DAT-standard alternative
    # (``Kasingganda kay Maria si Ana``) is marginal in modern
    # Tagalog but attested; this fourth rule lands it.
    #
    # Mirrors the GEN-standard rule (``ADJ NP[CASE=GEN]
    # NP[CASE=NOM]``) one-for-one with ``CASE=DAT`` substituting
    # for ``CASE=GEN``. Daughter 2 is the standard; daughter 3 is
    # the comparee (NOM-marked SUBJ pivot). Same ``ADJUNCT`` set
    # membership + ``ROLE: EQUATIVE_STANDARD`` convention as the
    # other equative rules above so consumers walking the
    # ADJUNCT set find the comparison standard uniformly across
    # GEN / NOM / DAT shapes.
    rules.append(Rule(
        "S",
        [
            "ADJ[COMP_DEGREE=EQUATIVE]",
            "NP[CASE=DAT]",
            "NP[CASE=NOM]",
        ],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
            "(↓1 COMP_DEGREE) =c 'EQUATIVE'",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 ROLE) = 'EQUATIVE_STANDARD'",
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


    # --- Phase 5i Commit 2: cleft-style wh-fronting (NOM pivot) ---
    #
    # ``Sino ang kumain?``           "Who ate?"
    # ``Sino ang kumain ng kanin?``  "Who ate the rice?"
    # ``Ano ang kinain mo?``         "What did you eat?"
    # ``Alin ang kinain mo?``        "Which one did you eat?"
    #
    # The wh-PRON is the matrix predicate; the NOM-NP is a
    # headless relative clause functioning as the matrix SUBJ
    # (``ang kumain ng kanin`` "the one who ate the rice"). This
    # is the canonical Tagalog wh-Q analysis per S&O 1972 §6 and
    # R&B 1986: a verbless cleft with the wh-PRON as the
    # cleft-pivot.
    #
    # F-structure shape:
    #
    #   PRED       = 'WH <SUBJ>'
    #   SUBJ       = the headless-RC NP[CASE=NOM]
    #   Q_TYPE     = 'WH'                    (matrix flagged as wh-Q)
    #   WH_LEMMA   = the wh-PRON's LEMMA     (sino / ano / alin)
    #
    # Structurally analogous to:
    #   - Phase 5e Commit 26 ``parang`` comparative (literal-PRED
    #     predicative with two NP-class daughters)
    #   - Phase 5f Commit 4 predicative cardinal (``Tatlo ang
    #     aklat`` — literal-PRED with NOM-NP pivot)
    #   - Phase 5g Commit 3 predicative-adj (``Maganda ang bata``
    #     — literal-PRED with PREDICATIVE-feature head)
    #
    # The category-pattern ``PRON[WH, CASE=NOM]`` filters the
    # head to NOM-marked wh-PRONs (sino / ano / alin). Restricting
    # to NOM keeps DAT-marked ``kanino`` "to whom" out of this
    # rule — a separate DAT-pivot frame is needed for that
    # construction (deferred to a Phase 5i follow-on commit if
    # corpus pressure surfaces).
    #
    # Belt-and-braces ``=c`` on the WH feature is the same leak-
    # closing pattern Phase 5h established (Commits 3 / 5 / 7):
    # the category-pattern matcher is non-conflict, so a PRON
    # without WH would absorb the slot via shared-key absence.
    # ``(↓1 WH) =c true`` makes the WH constraint binding.
    #
    # **Top-1 flip risk** (plan §7.2): Pre-Phase-5i probes showed
    # the cleft-style sentences (``Sino ang kumain?`` etc.) all
    # parsing 0 today (the wh-PRONs were _UNK; the strip dropped
    # them; the residue ``Ang kumain?`` failed to parse without
    # a verb-headed clause). After Commits 1 + 2, these sentences
    # parse 1+. The 1251-entry baseline corpus contains zero
    # wh-questions (audit confirmed at Commit 1), so no baseline
    # entries flip.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["PRON[WH, CASE=NOM]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'WH <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "(↓1 WH) =c true",
        ],
    ))


    # --- Phase 5n.B Commit 10: bare-form colloquial indirect-Q (§18 L53) ---
    #
    # ``Sino kumain.``               "Who ate?" (bare-form)
    # ``Alam ko kung sino kumain.``  "I know who ate." (canonical
    #                                  embedded use)
    #
    # Closes §18 L53. The colloquial Tagalog indirect-Q drops
    # ``ang`` from the canonical wh-cleft form (``Sino ang
    # kumain.``); the residue is a wh-PRON-as-SUBJ + bare-V
    # construction.
    #
    # Same f-structure shape as the Phase 5i Commit 2 wh-cleft
    # but the inner clause is the bare V-headed S (rather than a
    # headless-RC NP[CASE=NOM]). The rule fires on AV
    # intransitive verbs only — multi-argument frames (transitive
    # AV / OV) require additional rule shapes that are deferred
    # to a future commit if corpus pressure surfaces them.
    #
    # **Order**: PRON + V is the colloquial bare-form order
    # (mirroring the canonical wh-cleft surface `wh-PRON [ang] V`
    # with `ang` dropped). The PRON is the matrix SUBJ; the V
    # daughter contributes PRED / VOICE / ASPECT / MOOD via
    # ``(↑) = ↓2`` share.
    #
    # **Over-firing risk**: the rule admits standalone bare-form
    # surfaces (``Sino kumain.``) outside indirect-Q contexts as
    # well. Per §18 L53 detail, the bare-form is colloquially
    # well-formed in standalone use too; the rule is left open.
    # The ``Q_TYPE=WH`` lift correctly marks it as a wh-Q surface.
    #
    # Composition with Phase 5i Commit 8 indirect-Q wrap
    # (``Alam ko kung S[Q_TYPE=WH]``): the bare-form S produces
    # ``Q_TYPE=WH`` on its f-structure, satisfying the
    # S_INTERROG_COMP rule's constraint. So embedded bare-form
    # composes seamlessly.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["PRON[WH, CASE=NOM]", "V[VOICE=AV]"],
        [
            "(↑) = ↓2",
            "(↑ SUBJ) = ↓1",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "(↓1 WH) =c true",
            "(↓2 VOICE) =c 'AV'",
            "¬ (↓1 INDEF)",
        ],
    ))


    # --- Phase 5i Commit 6: cleft-style wh-N pivot --------------
    #
    # ``Aling bata ang kumain?``       "Which child ate?"
    # ``Aling aklat ang kinain mo?``   "Which book did you eat?"
    # ``Aling lalaki ang bumili ng aklat?``
    #     "Which man bought the book?"
    #
    # Sibling to Commit 2's PRON cleft. The wh-pivot here is an
    # N (``aling bata`` etc.) produced by the Phase 5i Commit 6
    # wh-Q companion rule in cfg/nominal.py. The N's WH=YES +
    # WH_LEMMA features (lifted from the Q daughter) gate this
    # rule. Same Q_TYPE=WH + WH_LEMMA matrix-feature pattern as
    # the PRON cleft.
    #
    # Why N (not NP) at the predicate slot: the Phase 5i Commit 6
    # wh-Q companion produces an N (matching the Phase 5f Commit
    # 15 N-level companion's category); there's no NP shell that
    # admits wh-N standalone (no case marker). The cleft rule
    # takes N directly. The headless-RC SUBJ is NP[CASE=NOM] as
    # in the PRON cleft.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["N[WH]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'WH <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 WH_LEMMA",
            "(↓1 WH) =c true",
        ],
    ))


    # --- Phase 5i Commit 9: predicative-Q cleft + DAT-pivot cleft -
    #
    # Two further cleft variants for Q-headed and DAT-marked
    # wh-pivots, sibling to Commits 2 and 6.
    #
    # (a) Predicative-Q cleft for amount / count wh:
    #
    #   ``Magkano ang isda?``     "How much is the fish?"
    #   ``Ilan ang aklat?``       "How many are the books?"
    #   ``Alin ang aklat?``       (Q reading; PRON reading via Commit 2)
    #
    # The cleft-pivot is a Q[WH] head (magkano /
    # ilan-WH / alin-Q). The headless-RC NP[CASE=NOM] is the SUBJ.
    # Same f-structure shape as Commit 2's PRON cleft —
    # PRED=``WH <SUBJ>``, Q_TYPE=WH, WH_LEMMA from the Q's LEMMA
    # field. The polysemy partner ``ilan`` Q[QUANT=FEW, VAGUE]
    # (no WH=YES) is excluded by the ``=c 'YES'`` constraint;
    # non-conflict matching at the chart level is closed by the
    # f-structure unifier.
    #
    # The Q-cleft and the PRON-cleft (Commit 2) cannot both fire
    # on the same surface, since wh-PRONs and wh-Qs have
    # disjoint POS in the lex (PRON vs Q). ``alin`` is the only
    # surface lexed as both (Commit 1 polysemy); it produces two
    # parses — one via PRON-cleft, one via Q-cleft — which
    # share the same f-structure (both write
    # ``PRED='WH <SUBJ>'``, ``WH_LEMMA='alin'``). Tests admit
    # ``>= 1`` parses for ``Alin ang aklat?``.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["Q[WH]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'WH <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "(↓1 WH) =c true",
        ],
    ))

    # --- Phase 5n.B Commit 14: predicative-Q cleft + trailing DAT-NP ADJUNCT
    #
    # ``Magkano ito sa kanya?``        "How much is it for him?"
    # ``Magkano ang isda sa palengke?``"How much is the fish at the market?"
    # ``Magkano ang aklat sa bata?``   "How much is the book for the child?"
    #
    # Closes §18 deferral L58. Sibling to the (a) wh-Q cleft above
    # (Phase 5i Commit 9 (a)); same f-structure shape with an
    # additional DAT-NP daughter folded into the matrix's
    # ADJUNCT set. The DAT-NP carries locative ("at the market")
    # or dative ("for him") semantics — the existing PRED='WH
    # <SUBJ>' covers both readings; the lexical content of the
    # adjunct disambiguates downstream.
    #
    # Although ``Magkano`` is the primary motivation (per plan-of-
    # record §4.2 Commit 14), the rule generalises to any
    # Q[WH] with a trailing DAT-NP — the structural pattern
    # is identical for ``Ilan`` and other amount/count wh-Qs.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["Q[WH]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
        [
            "(↑ PRED) = 'WH <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "(↓1 WH) =c true",
            "↓3 ∈ (↑ ADJUNCT)",
        ],
    ))

    # (b) DAT-pivot cleft for ``kanino``:
    #
    #   ``Kanino ang aklat?``     "Whose is the book?" / "To whom
    #                              does the book belong?"
    #
    # The cleft-pivot is a DAT-marked wh-PRON; the headless-RC
    # NP[CASE=NOM] is the SUBJ. Same shape as Commit 2's NOM-PRON
    # cleft, but with CASE=DAT discriminating against sino / ano
    # / alin (CASE=NOM) — those continue to fire only the
    # NOM-PRON cleft. The semantics of the DAT cleft is
    # possessor / recipient wh; we don't lexicalise this in the
    # PRED template (still ``WH <SUBJ>``) — the WH_LEMMA carries
    # the lexical content (kanino vs sino).
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["PRON[WH, CASE=DAT]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'WH <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "(↓1 WH) =c true",
            "(↓1 CASE) =c 'DAT'",
        ],
    ))

    # --- Phase 5n.B Commit 15: kanino + possessed-N + NOM-NP cleft ---
    #
    # ``Kanino kaibigan ito?``      "Whose friend is this?"
    # ``Kanino aklat ito?``         "Whose book is this?"
    # ``Kanino bahay ang malaki?``  "Whose house is the big one?"
    #
    # Closes §18.1 deferral L59. Sibling to the Phase 5i C9 (b)
    # bare DAT-cleft above; same DAT-PRON pivot but with an
    # additional N daughter as the predicate-N's possessed head.
    # The NOM-NP is the matrix SUBJ (the possessee referent).
    #
    # F-structure shape mirrors the Phase 5n.B C2 predicative-N
    # rule (PRED='BE-N <SUBJ>', N_LEMMA from the predicate-N) plus
    # a POSS slot carrying the wh-PRON possessor and the wh
    # markers (Q_TYPE, WH_LEMMA) for downstream consumers.
    #
    # **Structural disambiguation from bare DAT-cleft**: the
    # 3-daughter shape (with the N between PRON and NOM-NP) is
    # distinct from the 2-daughter bare cleft above
    # (``Kanino ang aklat?``) — different daughter counts; no
    # cross-firing.
    #
    # **Coexistence with Phase 5i C9 wh-fronting** (the
    # ``S → PRON[WH, CASE=DAT] S`` rule below): the wh-fronting
    # rule also fires on this surface (``kaibigan ito`` parses as
    # an S via the C2 predicative-N rule). Both parses surface,
    # with different f-structures — the wh-fronting parse holds
    # kanino in ADJUNCT; this rule's parse holds it in POSS. Tests
    # accept ``>= 1`` parse with the POSS-slot shape.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["PRON[WH, CASE=DAT]", "N", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-N <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ N_LEMMA) = ↓2 LEMMA",
            "(↑ POSS) = ↓1",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 WH) =c true",
            "(↓1 CASE) =c 'DAT'",
        ],
    ))

    # --- Phase 5n.B Commit 9: sa-DAT NP cleft (§18 L51) -----------
    #
    # ``Sa kanino ang aklat?``  "Whose is the book?" (with
    #                            explicit DAT marker)
    # ``Sa sino ang aklat?``    (variant — DAT marker over the
    #                            NOM-by-default wh-PRON)
    #
    # Closes §18 L51. Phase 5i Commit 9 (b) above admits the bare
    # DAT-PRON pivot (``Kanino ang aklat?`` — bare ``kanino``); the
    # explicit DAT-marked NP form (``Sa kanino ang aklat?``) is
    # structurally an NP[CASE=DAT, WH] built by the Phase 5i
    # Commit 3 in-situ wh-PRON-in-DAT-NP shell ``NP[CASE=DAT] →
    # ADP[CASE=DAT] PRON[WH]`` — distinct from the bare-PRON
    # NP shell (Phase 4 §7.8 ``NP[CASE=DAT] → PRON[CASE=DAT]``)
    # which lifts only the PRON's f-structure unchanged.
    #
    # **Disambiguation gate** ``(↓1 PRED) =c 'WH-PRO'``: the
    # Phase 5i Commit 3 explicit-DAT path explicitly sets ``(↑
    # PRED) = 'WH-PRO'`` on the matrix NP; the Phase 4 §7.8
    # bare-PRON path uses ``(↑) = ↓1`` share, exposing the bare
    # PRON's f-structure (which has no ``PRED`` — wh-PRON lex
    # entries don't declare one). Constraining ``PRED='WH-PRO'``
    # gates this rule to the explicit-DAT path only — the
    # bare-PRON cleft (Phase 5i Commit 9 (b)) remains the canonical
    # path for ``Kanino ang aklat?``.
    #
    # Same f-structure shape as the bare-PRON cleft above —
    # ``PRED='WH <SUBJ>'`` / ``Q_TYPE=WH`` / ``WH_LEMMA``
    # propagated from the matrix NP.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["NP[CASE=DAT, WH]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'WH <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 WH_LEMMA",
            "(↓1 WH) =c true",
            "(↓1 CASE) =c 'DAT'",
            "(↓1 PRED) =c 'WH-PRO'",
        ],
    ))


    # --- Phase 5i Commit 7: tag question `di ba?` ----------------
    #
    # ``Maganda ang bata, di ba?``    "The child is beautiful, isn't it?"
    # ``Kumain ka, di ba?``           "You ate, didn't you?"
    # ``Mas matalino siya, di ba?``   "She's more intelligent, isn't she?"
    #
    # The sentence-final tag ``di ba`` is the canonical Tagalog
    # tag-question marker, asking the addressee to confirm the
    # preceding statement. ``di`` is the colloquial shortening of
    # ``hindi`` (negation); ``ba`` is the yes/no Q clitic. Together
    # they form a fixed sentence-final tag with QUESTION + NEG_TAG
    # semantics.
    #
    # Tokenization: the comma is consumed as a structural daughter
    # (PUNCT[PUNCT_CLASS=COMMA]). Pre-Phase-5k Commit 1 the comma was
    # silently dropped by ``_strip_non_content`` (no lex entry → all
    # ``_UNK`` → strip), and this rule had three daughters. Phase 5k
    # Commit 1 added a ``,`` PUNCT lex entry to support multi-conjunct
    # coordination (``Maria, Juan, at Pedro`` — Commit 4) and
    # asymmetric coordination (``Si Maria, hindi si Juan`` — Commit
    # 8); commas no longer fall through as ``_UNK``. The tag-Q rule
    # is correspondingly updated to consume the comma daughter (no
    # equation refers to it — purely syncategorematic, signalling
    # the matrix-tag boundary). ``ba``'s 2P-clitic placement is a
    # no-op here (it's already at clause-final position post-comma).
    #
    # Single combined rule (rather than two rules `S → S PART[di]`
    # + Phase 5i Commit 5 ba-Q rule): the two-rule alternative
    # would either chain (creating Q_TYPE clash on the matrix when
    # both fire) or each fire independently (leaving `di` orphaned
    # if only the ba rule matched). Combining both clitics into
    # one rule with Q_TYPE=TAG cleanly subsumes the construction.
    #
    # The yes/no Q-rule in cfg/clitic.py would otherwise match
    # `ba` here and write Q_TYPE=YES_NO; the matrix-Q_TYPE clash
    # rejects that parse (TAG ≠ YES_NO at the unifier), leaving
    # only the tag-Q reading as the surviving parse.
    # Two-rule split: the comma-marked form (canonical orthography)
    # and the no-comma form (admitted as orthographically marginal
    # but attested). Pre-Phase-5k Commit 1 a single 3-daughter rule
    # covered both because commas were silent-dropped pre-parse;
    # post-Commit-1 the two forms diverge structurally and need
    # separate rules.
    rules.append(Rule(
        "S[Q_TYPE=TAG]",
        [
            "S",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "PART[NEG_TAG]",
            "PART[QUESTION, CLITIC_CLASS=2P]",
        ],
        [
            "(↑) = ↓1",
            "↓4 ∈ (↑ ADJ)",
            "(↑ Q_TYPE) = 'TAG'",
            "(↓3 NEG_TAG) =c true",
            "(↓4 QUESTION) =c true",
        ],
    ))
    rules.append(Rule(
        "S[Q_TYPE=TAG]",
        [
            "S",
            "PART[NEG_TAG]",
            "PART[QUESTION, CLITIC_CLASS=2P]",
        ],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ ADJ)",
            "(↑ Q_TYPE) = 'TAG'",
            "(↓2 NEG_TAG) =c true",
            "(↓3 QUESTION) =c true",
        ],
    ))


    # --- Phase 5i Commit 4: adverbial wh fronting ----------------
    #
    # ``Saan ka pumunta?``    "Where did you go?"
    # ``Kailan ka kumain?``   "When did you eat?"
    # ``Bakit ka kumain?``    "Why did you eat?"
    # ``Paano ka kumain?``    "How did you eat?"
    #
    # Sentence-initial wh-ADV (saan / kailan / bakit / paano /
    # papaano) marks the matrix as a wh-Q whose interrogated
    # constituent is an adjunct of the underlying clause. The
    # wh-ADV adjoins to the matrix S's ADJUNCT set; the inner S
    # is the residue verbal clause.
    #
    # Parallels Phase 5g Commit 5 manner-adverb (``mabilis na
    # tumakbo``) — same shape ``S → ADV-like S`` with the ADV
    # lifted into ADJUNCT — but without the linker daughter (wh-
    # ADVs are sentence-initial particles, not linker-bound
    # modifiers).
    #
    # F-structure shape:
    #
    #   PRED         = inner S's PRED (verbal predicate)
    #   SUBJ / OBJ   = inner S's GFs
    #   Q_TYPE       = 'WH'                 (matrix flagged as wh-Q)
    #   WH_LEMMA     = the wh-ADV's LEMMA   (saan / kailan / ...)
    #   ADJUNCT      ⊇ {<wh-ADV f-struct with ADV_TYPE>}
    #
    # The wh-ADV's ``ADV_TYPE`` (LOCATION / TIME / REASON /
    # MANNER) percolates onto the ADJUNCT member's f-structure
    # via the lex feats; consumers (ranker / classifier) can
    # read it off the adjunct without traversing back to the
    # c-tree.
    #
    # **Top-1 flip-risk closure**: pre-Phase-5i probes (Commit 1
    # plan-of-record §3) showed ``Saan ka pumunta?`` parsing
    # today (1 parse — silently dropping ``saan`` and parsing
    # the residue ``Pumunta ka.``). After Commit 1's lex add,
    # the strip stopped firing and the sentence returned 0
    # parses. This commit's rule restores the parse path with
    # the proper wh-Q matrix. Audit confirmed: zero baseline
    # corpus entries contain any wh-ADV (Commit 1 audit), so no
    # baseline flips.
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["ADV[WH]", "S"],
        [
            "(↑) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↓1 WH) =c true",
        ],
    ))

    # Phase 5i Commit 9: DAT-wh fronting (sibling to Commit 4).
    #
    #   ``Kanino ka pumunta?``        "To whom did you go?"
    #   ``Kanino ka bumili ng aklat?`` "From whom did you buy a book?"
    #
    # ``kanino`` is a DAT-marked wh-PRON; when sentence-initial
    # over a residue clause it's an ADJUNCT wh-fronting (mirror of
    # adverbial-wh fronting). The matrix carries Q_TYPE=WH +
    # WH_LEMMA=kanino; the wh-PRON joins the matrix ADJUNCT set.
    #
    # No conflict with the Commit 9 DAT-pivot cleft above: the
    # cleft requires ``NP[CASE=NOM]`` as the second daughter (the
    # headless RC), and ``ang aklat`` (a bare NP) does not parse
    # as ``S`` — verified pre-state. The fronting rule fires only
    # when the residue is a verb-headed clause with its own SUBJ
    # (e.g., ``ka pumunta``).
    rules.append(Rule(
        "S[Q_TYPE=WH]",
        ["PRON[WH, CASE=DAT]", "S"],
        [
            "(↑) = ↓2",
            "(↑ Q_TYPE) = 'WH'",
            "(↑ WH_LEMMA) = ↓1 LEMMA",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↓1 WH) =c true",
            "(↓1 CASE) =c 'DAT'",
        ],
    ))

    # --- Phase 5j Commit 2: positive existential clause ---------
    #
    #   ``May aklat.``               "There is a book."
    #   ``May tao sa labas.``        "There's someone outside."
    #   ``Mayroong tao sa labas.``   "There's someone outside."
    #                                (mayroon + bound -ng linker
    #                                 split pre-parse)
    #
    # Per roadmap §12.1: ``may`` / ``mayroon`` are clause-typing
    # predicates, NOT V-headed verbal frames. They head a dedicated
    # existential clause-type with their own constituent shape
    # (existential PART + bare-N). No voice / aspect / mood —
    # these clause-typers carry no verbal morphology, paralleling
    # the Phase 5g predicative-ADJ clause and Phase 5f Commit 4
    # predicative-cardinal: a non-V matrix predicate carrying a
    # literal PRED template.
    #
    # The daughter is bare ``N`` (NOUN-headed projection from
    # nominal.py's ``N → NOUN`` rule), NOT a determiner-marked
    # ``NP[CASE=...]``. Tagalog existentials take indefinite bare
    # nominals — ``*May ang aklat`` is ungrammatical (the ang-
    # determiner forces definiteness, which clashes with the
    # existential's indefinite-introducer semantics). Adjective-
    # modified Ns (``May matandang aklat``, "there's an old
    # book") fall out via the Phase 5g NP-internal modifier
    # rules at ``nominal.py:1299-1317`` which project to ``N``.
    #
    # F-structure shape:
    #
    #   PRED         = 'EXIST <SUBJ>'
    #   SUBJ         = the existence-asserted N (with PRED /
    #                  LEMMA projected from the head NOUN)
    #   CLAUSE_TYPE  = 'EXISTENTIAL'
    #   POLARITY     = 'POS'
    #
    # SUBJ-not-THEME on the PRED template: this codebase's PRED
    # templates list GFs (SUBJ / OBJ / OBL), not thematic roles
    # (THEME / AGENT / etc.) — thematic roles live in the
    # a-structure projection (Phase 4 architecture). Mirrors
    # Phase 5g predicative-ADJ ``'ADJ <SUBJ>'`` and Phase 5f
    # Commit 4 ``'CARDINAL <SUBJ>'``. The Subject Condition
    # (LMT step 6, ``check_subject_condition``) requires every
    # PRED-bearing f-structure to have a SUBJ; treating the
    # existence-asserted N as SUBJ satisfies this without a
    # special-case carve-out for existentials.
    #
    # Locative-PP composition (``May tao sa labas``) falls out of
    # this rule + the existing Phase 4 §7.7 sa-PP-as-ADJUNCT
    # machinery: the matrix S consumed by sa-PP attachment lifts
    # the locative-PP to the matrix ADJUNCT set. No dedicated
    # locative-PP rule needed for ``may`` (cf. ``nasa`` in
    # Commit 4 which is a separate clause-type with the locative
    # ground promoted to LOCATION argument).
    #
    # The constraining equations ``(↓1 EXISTENTIAL) =c true`` and
    # ``(↓1 POLARITY) =c 'POS'`` are belt-and-braces — the rule's
    # category-pattern matchers already filter on
    # ``PART[EXISTENTIAL, POLARITY=POS]`` — but make the
    # analytical commitment explicit and guard against future PART
    # entries with the same EXISTENTIAL flag but different POLARITY
    # (e.g., a hypothetical INTERROG-existential).
    rules.append(Rule(
        "S",
        ["PART[EXISTENTIAL, POLARITY=POS]", "N"],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'POS'",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'POS'",
        ],
    ))

    # Linker variant: vowel-final ``mayroon`` carries bound ``-ng``
    # before its complement (``Mayroong tao``). After
    # ``split_linker_ng`` strips the bound linker, the structural
    # shape is ``mayroon`` + ``-ng`` + ``N``. Same f-structure as
    # the base rule above; the linker daughter is a syntactic
    # carrier with no semantic content (parallels Phase 5h's
    # particle-intensifier-with-linker rule pattern).
    #
    # ``may`` is consonant-final and never takes the bound linker —
    # ``*Mayng tao`` is ungrammatical — so the rule's
    # ``(↓1 LEMMA) =c 'mayroon'`` constraint isn't strictly needed
    # (``may`` would never appear before a PART[LINK=NG] in well-
    # formed input). The linker variant fires opportunistically.
    rules.append(Rule(
        "S",
        ["PART[EXISTENTIAL, POLARITY=POS]", "PART[LINK=NG]", "N"],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'POS'",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'POS'",
            "(↓2 LINK) =c 'NG'",
        ],
    ))

    # --- Phase 5j Commit 3: negative existential clause ---------
    #
    #   ``Walang aklat.``         "There's no book."
    #   ``Walang tao.``           "There's no one."
    #   ``Walang tao sa labas.``  "There's no one outside."
    #
    # Negative-polarity counterpart of the Commit 2 positive
    # existential. ``wala`` is vowel-final and ALWAYS takes bound
    # ``-ng`` before its complement (``*Wala aklat.`` is ungrammatical
    # in the existential reading; the bound-linker form ``Walang
    # aklat.`` is the canonical surface). After ``split_linker_ng``
    # strips the bound linker, the structural shape is ``wala``
    # + ``-ng`` + ``N`` — so the linker variant is the primary
    # entry point for ``wala``.
    #
    # The bare-N variant (``S → PART[EXISTENTIAL, POLARITY=NEG]
    # N``) is included for parity with Commit 2's positive base
    # rule and to admit edge cases where ``wala`` appears without
    # the linker (e.g., ``Wala.`` standalone, "There is none.")
    # when followed by a non-NP complement). For well-formed
    # ``wala`` + N input, the linker variant always fires; the
    # bare-N variant is benign.
    #
    # F-structure shape mirrors the positive existential exactly,
    # with ``POLARITY = 'NEG'`` instead of POS. The matrix
    # CLAUSE_TYPE='EXISTENTIAL' makes the Phase 5j Commit 2 clause-
    # final DAT-lift rule (``S → S NP[CASE=DAT]`` with
    # ``(↓1 CLAUSE_TYPE) =c 'EXISTENTIAL'``) compose with negative
    # existentials too — no separate locative rule needed.
    rules.append(Rule(
        "S",
        ["PART[EXISTENTIAL, POLARITY=NEG]", "N"],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'NEG'",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'NEG'",
        ],
    ))

    # Linker variant for ``wala`` + bound ``-ng`` + N (the canonical
    # negative-existential surface ``Walang aklat`` etc.).
    rules.append(Rule(
        "S",
        ["PART[EXISTENTIAL, POLARITY=NEG]", "PART[LINK=NG]", "N"],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'NEG'",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'NEG'",
            "(↓2 LINK) =c 'NG'",
        ],
    ))

    # Phase 5m Commit 9: negative-indefinite-PRON variant —
    # ``Walang sinuman.`` "There is no one." Mirrors the linker-
    # variant N rule above with PRON[INDEF=NEG_INDEF] in the
    # SUBJ slot. The Commit 1 lex-entry for ``sinuman`` carries
    # INDEF=NEG_INDEF; the constraint here scopes the rule
    # tightly so generic PRONs (siya / niya / etc.) don't fire.
    #
    # Coverage: ``Walang sinuman.``, ``Walang sinumang dumating.``
    # (sinuman + linker + V — the second daughter swallows the
    # bound -ng, then the relative-clause grammar handles
    # ``sinumang dumating``).
    #
    # Plan-of-record §1 had said "Phase 5m only adds the lex
    # entry for sinuman; no new grammar". That was wrong — the
    # existing Phase 5j walang-N rule constrains specifically on
    # ``N`` daughter and doesn't admit PRONs. This new rule is
    # the minimum delta to compose ``walang sinuman``.
    rules.append(Rule(
        "S",
        [
            "PART[EXISTENTIAL, POLARITY=NEG]",
            "PART[LINK=NG]",
            "PRON[INDEF=NEG_INDEF]",
        ],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'NEG'",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'NEG'",
            "(↓2 LINK) =c 'NG'",
            "(↓3 INDEF) =c 'NEG_INDEF'",
        ],
    ))

    # --- Phase 5j Commit 4: locative existential (nasa) -----------
    #
    #   ``Nasa labas ang aso.``         "The dog is outside."
    #   ``Nasa bundok ang bahay.``      "The house is on the
    #                                    mountain." (R&G simple #5)
    #   ``Nasa bahay si Maria.``        "Maria is at the house."
    #   ``Nasa tuktok ng bundok ang bahay.``
    #                                   "The house is on top of the
    #                                    mountain." (R&G simple #7)
    #
    # ``nasa`` is etymologically ``na`` + ``sa`` (locative case
    # marker) but synchronically a fixed locative-existential
    # clause-typer. The first internal slot is the locative ground
    # (the entity at which the figure is located); the second is
    # the NOM-NP pivot (the figure / theme being located).
    #
    # F-structure shape:
    #
    #   PRED         = 'LOC <SUBJ>'
    #   SUBJ         = the NOM-NP figure (the post-ground daughter)
    #   LOCATION     = the locative ground N (with optional GEN-NP
    #                  possessor — ``tuktok ng bundok``)
    #   CLAUSE_TYPE  = 'LOC_EXISTENTIAL'
    #
    # Two rules: a base form for bare-N grounds (``Nasa labas
    # ang aso``) and a possessor variant for N + GEN-NP grounds
    # (``Nasa tuktok ng bundok ang bahay``). The two-rule split is
    # preferred over a single rule with optional GEN-NP because the
    # parser's category-pattern matching can't express "optional"
    # daughters; the alternative would be a recursive intermediate
    # non-terminal, which is more invasive than necessary for a
    # phase-local construction. Mirrors the V-headed-frame
    # convention of explicit per-shape rules.
    #
    # PRED is ``'LOC <SUBJ>'`` (one-place over the figure) — same
    # GF-named-PRED-template convention as Phase 5g
    # ``'ADJ <SUBJ>'`` and Phase 5j Commit 2 ``'EXIST <SUBJ>'``.
    # The locative ground rides on a dedicated ``LOCATION``
    # feature (not in the PRED's argument list) because ``nasa``
    # is structurally a clause-typer, not a binary predicate
    # over the LFG GF inventory; the LOCATION feature mirrors the
    # Phase 5h Commit 4 ``ROLE='STANDARD'`` convention for
    # comparison standards.
    rules.append(Rule(
        "S",
        ["PART[LOC_EXISTENTIAL]", "N", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'LOC <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ LOCATION) = ↓2",
            "(↑ CLAUSE_TYPE) = 'LOC_EXISTENTIAL'",
            "(↓1 LOC_EXISTENTIAL) =c true",
        ],
    ))

    # Possessor-of-ground variant: ``Nasa tuktok ng bundok ang
    # bahay`` — locative ground is N + GEN-NP (left-associative
    # possessor); the GEN-NP rides on the ground's POSS feature.
    rules.append(Rule(
        "S",
        ["PART[LOC_EXISTENTIAL]", "N", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'LOC <SUBJ>'",
            "(↑ SUBJ) = ↓4",
            "(↑ LOCATION) = ↓2",
            "(↓2 POSS) = ↓3",
            "(↑ CLAUSE_TYPE) = 'LOC_EXISTENTIAL'",
            "(↓1 LOC_EXISTENTIAL) =c true",
        ],
    ))

    # --- Phase 5j Commit 5: HAVE construction --------------------
    #
    # Tagalog has no separate HAVE verb. The HAVE reading is the
    # existential predicate (Commit 2 / 3) + a possessor-NP that
    # binds to the existence-asserted N's POSSESSOR feature.
    #
    # Surface patterns (4 rules total):
    #
    # Positive HAVE — postposed possessor (no internal linker):
    #   ``May aklat ako.``        "I have a book."  (clitic-PRON)
    #   ``May aklat si Maria.``   "Maria has a book."  (full-NP)
    #
    # Positive HAVE — internal clitic possessor (with bound -ng):
    #   ``May akong aklat.``      "I have a book."
    #
    # Negative HAVE — postposed possessor (wala + bound -ng):
    #   ``Walang aklat ako.``     "I don't have a book."
    #   ``Walang aklat si Maria.`` "Maria doesn't have a book."
    #
    # Negative HAVE — internal clitic possessor:
    #   ``Wala akong aklat.``     "I don't have a book."
    #
    # The asymmetry between positive (no bound -ng on may) and
    # negative (bound -ng on wala) is surface-level: ``may`` is
    # consonant-final and never takes the bound linker; ``wala``
    # is vowel-final and ALWAYS takes it before its complement.
    # The internal-clitic and postposed patterns reflect different
    # surface positions of the possessor — Tagalog admits both.
    #
    # Possessor binding via ``(↑ SUBJ POSSESSOR) = ↓X`` rather
    # than via OBLIQUE thematic role: Tagalog HAVE is structurally
    # an existential ("exists X possessed by Y"), not a transitive
    # ("Y has X"). The POSSESSOR feature on the SUBJ N captures
    # this while keeping the matrix CLAUSE_TYPE as EXISTENTIAL
    # and the matrix PRED as the literal ``'EXIST <SUBJ>'``.
    # ``(↑ HAVE) = true`` lifts the HAVE-reading flag for
    # downstream consumers.
    #
    # Internal-clitic rules constrain the possessor daughter to
    # PRON (not NP[CASE=NOM]) — full-NP-with-internal-linker
    # patterns like ``*May Mariang aklat`` are marginal in modern
    # Tagalog and would compete with NP-internal POSS rules.
    # The PRON gate avoids this cross-fire.

    # Commit 5a: positive HAVE — postposed possessor.
    rules.append(Rule(
        "S",
        ["PART[EXISTENTIAL, POLARITY=POS]", "N", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ SUBJ POSSESSOR) = ↓3",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'POS'",
            "(↑ HAVE) = true",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'POS'",
        ],
    ))

    # Commit 5b: positive HAVE — internal clitic possessor.
    rules.append(Rule(
        "S",
        [
            "PART[EXISTENTIAL, POLARITY=POS]",
            "PRON[CASE=NOM]",
            "PART[LINK=NG]",
            "N",
        ],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓4",
            "(↑ SUBJ POSSESSOR) = ↓2",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'POS'",
            "(↑ HAVE) = true",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'POS'",
            "(↓3 LINK) =c 'NG'",
        ],
    ))

    # Commit 5c: negative HAVE — postposed possessor (wala + bound -ng).
    rules.append(Rule(
        "S",
        [
            "PART[EXISTENTIAL, POLARITY=NEG]",
            "PART[LINK=NG]",
            "N",
            "NP[CASE=NOM]",
        ],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ SUBJ POSSESSOR) = ↓4",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'NEG'",
            "(↑ HAVE) = true",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'NEG'",
            "(↓2 LINK) =c 'NG'",
        ],
    ))

    # Commit 5d: negative HAVE — internal clitic possessor.
    rules.append(Rule(
        "S",
        [
            "PART[EXISTENTIAL, POLARITY=NEG]",
            "PRON[CASE=NOM]",
            "PART[LINK=NG]",
            "N",
        ],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓4",
            "(↑ SUBJ POSSESSOR) = ↓2",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'NEG'",
            "(↑ HAVE) = true",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'NEG'",
            "(↓3 LINK) =c 'NG'",
        ],
    ))

    # --- Phase 5n.A Commit 21: positive HAVE with leading linker (§18 L87) ---
    #
    # ``mayroon`` is the vowel-final variant of ``may`` and ALWAYS
    # takes bound ``-ng`` before its complement (parallel to ``wala``
    # in 5c / 5d above). Commits 5a / 5b above cover the consonant-
    # final ``may`` shape (no leading linker); the ``mayroon`` HAVE
    # readings need parallel rules with the leading PART[LINK=NG]
    # daughter consumed structurally between the existential and
    # the possessor / N.
    #
    # Surface patterns (closes §18 L87):
    #
    #   ``Mayroong aklat si Maria.``  "Maria has a book."
    #                                 (postposed possessor)
    #   ``Mayroong aklat ako.``        "I have a book."
    #                                 (postposed clitic possessor)
    #   ``Mayroong akong aklat.``     "I have a book."
    #                                 (internal clitic possessor —
    #                                  two LINK=NG daughters)
    #
    # 5e mirrors 5c (negative postposed with linker) with POS
    # polarity; 5f mirrors 5b (positive internal clitic) with the
    # extra leading linker daughter that ``mayroon`` requires. The
    # ``(↓1 LEMMA) =c 'mayroon'`` constraint isn't strictly needed
    # — ``may`` is consonant-final and never appears before
    # PART[LINK=NG] in well-formed input — so the rules fire
    # opportunistically, mirroring the Phase 5j Commit 2 linker-
    # existential rule's analogous treatment.

    # Commit 5e: positive HAVE — postposed possessor (mayroon + bound -ng).
    rules.append(Rule(
        "S",
        [
            "PART[EXISTENTIAL, POLARITY=POS]",
            "PART[LINK=NG]",
            "N",
            "NP[CASE=NOM]",
        ],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ SUBJ POSSESSOR) = ↓4",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'POS'",
            "(↑ HAVE) = true",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'POS'",
            "(↓2 LINK) =c 'NG'",
        ],
    ))

    # Commit 5f: positive HAVE — internal clitic possessor with
    # leading linker (mayroon + bound -ng + PRON + bound -ng + N).
    rules.append(Rule(
        "S",
        [
            "PART[EXISTENTIAL, POLARITY=POS]",
            "PART[LINK=NG]",
            "PRON[CASE=NOM]",
            "PART[LINK=NG]",
            "N",
        ],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ) = ↓5",
            "(↑ SUBJ POSSESSOR) = ↓3",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'POS'",
            "(↑ HAVE) = true",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'POS'",
            "(↓2 LINK) =c 'NG'",
            "(↓4 LINK) =c 'NG'",
        ],
    ))

    # Clause-final DAT-NP ADJUNCT lift, gated on existential
    # clauses. ``May tao sa labas`` / ``Mayroong tao sa labas`` —
    # the locative-PP composes by adjoining a clause-final
    # NP[CASE=DAT] to an existential matrix S as an ADJUNCT
    # member.
    #
    # The constraining equation ``(↓1 CLAUSE_TYPE) =c
    # 'EXISTENTIAL'`` gates the rule to existential matrices
    # only — V-headed frames already embed their DAT-NP daughters
    # explicitly (each V-frame in this file includes
    # ``NP[CASE=DAT]`` as a daughter and adds it to ADJUNCT), so a
    # general ``S → S NP[CASE=DAT]`` rule would create spurious
    # ambiguity (``Kumain ang aso sa labas`` would have two parses:
    # the V-frame's embedded DAT and a wrap parse on top of a
    # smaller V-only matrix). The EXISTENTIAL gate prevents that
    # cross-fire.
    rules.append(Rule(
        "S",
        ["S", "NP[CASE=DAT]"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓1 CLAUSE_TYPE) =c 'EXISTENTIAL'",
        ],
    ))

    # === Phase 5m Commit 3: fragment-answer interjection clause ==========
    #
    # ``Opo.`` "Yes (polite)", ``Oho.`` "Yes (colloquial-polite)",
    # ``Oo.`` "Yes", ``Hindi.`` "No" form one-word answer clauses.
    # PRON entries with ``INTERJ=YES`` and ``ANSWER`` ∈ {AFFIRM, NEG}
    # project as a complete matrix S via this rule; PRON-level feats
    # (REGISTER, ANSWER) percolate to the matrix S via ``(↑) = ↓1``.
    # CLAUSE_TYPE=FRAGMENT_ANSWER tags the matrix as a fragment-answer
    # clause for downstream consumers.
    #
    # Constraints:
    # * ``(↑ INTERJ) =c true`` — gates to interjection PRONs only.
    # * ``(↑ ANSWER)`` (existential) — requires the ANSWER feat to
    #   be defined (no value constraint), admitting both AFFIRM
    #   (Oo / Opo / Oho) and NEG (Hindi). Phase 5n.B Commit 17
    #   relaxed this from ``=c 'AFFIRM'`` when adding the
    #   PRON entries for ``oo`` / ``hindi`` (§18 L97).
    #
    # ``hindi`` has both a PART[POLARITY=NEG] entry (particles.yaml,
    # used by the hindi-wrap negation rule) and a PRON[INTERJ,
    # ANSWER=NEG] entry (pronouns.yaml, used by this rule). Rule
    # context disambiguates: the fragment-answer rule fires on a
    # single PRON with no trailing tokens, while hindi-wrap requires
    # an inner S as second daughter — no cross-firing.
    #
    # The Phase 5n.B C16 NOUN-host fragment path (``Salamat po.``)
    # uses CLAUSE_TYPE=FRAGMENT (no ANSWER) via ``S → N`` gated on
    # FRAGMENT_HOST=YES — distinct path, distinct CLAUSE_TYPE value.
    rules.append(Rule(
        "S",
        ["PRON"],
        [
            "(↑) = ↓1",
            "(↑ INTERJ) =c true",
            "(↑ ANSWER)",
            "(↑ CLAUSE_TYPE) = 'FRAGMENT_ANSWER'",
        ],
    ))

    # === Phase 5n.B Commit 16: fragment-host NOUN clause (§18 L96) ========
    #
    # ``Salamat.``       "Thanks."
    # ``Salamat po.``    "Thank you (polite)."
    # ``Salamat ho.``    "Thank you (colloquial-polite)."
    #
    # Closes §18.1 deferral L96 for the NOUN-host path. A single-
    # token NOUN gated by ``FRAGMENT_HOST=YES`` projects as a
    # complete matrix S; the existing Phase 5m clitic-absorption
    # rule (``S → S PART[CLITIC_CLASS=2P, REGISTER=POLITE]``,
    # ``cfg/clitic.py``) then attaches the 2P-politeness clitic
    # (po / ho / opo / oho) on top.
    #
    # ``FRAGMENT_HOST=YES`` is set in the lex (``data/tgl/nouns.yaml``
    # — currently only ``salamat`` qualifies) so the rule does NOT
    # admit arbitrary noun fragments (``Aklat.`` does not parse as
    # a one-word S — the constraint gates it out). Future fragment-
    # host nouns (greetings, exclamations) can opt in via the same
    # lex feat without grammar changes.
    #
    # Companion deferral L97 (standalone ``Oo.`` / ``Hindi.`` answer
    # clauses) closes in Phase 5n.B Commit 17 — that path uses new
    # ``PRON[INTERJ, ANSWER=...]`` lex entries plus an
    # ``S_ANSWER`` rule, distinct from this NOUN-host path.
    rules.append(Rule(
        "S",
        ["N"],
        [
            "(↑) = ↓1",
            "(↑ FRAGMENT_HOST) =c true",
            "(↑ CLAUSE_TYPE) = 'FRAGMENT'",
        ],
    ))

    # === Phase 5n.C Commit 5 (§18 L83): asymmetric NP-coord fragment ====
    #
    # ``Si Maria, hindi si Juan.`` "Maria, not Juan" — the bare
    # asymmetric-coord-NP fragment, lifted to a complete matrix S.
    # The Phase 5k Commit 8 asymmetric NP-coord rule
    # (``cfg/coordination.py:493``) already builds an
    # ``NP[CASE=NOM, COORD=BUT_NOT]`` from the daughter shape
    # ``NP COMMA PART[POLARITY=NEG] NP``; this rule wraps that NP
    # as a fragment-S.
    #
    # Daughter shape: ``NP[CASE=NOM, COORD=BUT_NOT]`` — restricted
    # to the asymmetric coord shape specifically. ``COORD=BUT_NOT``
    # is set only by Phase 5k Commit 8 (no other producer in the
    # grammar), so this serves as the structural discriminator
    # without needing a new feat. Bare singular NPs (``Si Maria.``)
    # do NOT carry ``COORD=BUT_NOT`` and continue to 0-parse as
    # sentences. AND-coord (``Si Maria at si Juan.``) and OR-coord
    # (``Si Maria o si Juan.``) NPs carry ``COORD=AND`` / ``OR``
    # and also do not match — bare additive / disjunctive coord-NP
    # fragments are not attested as canonical sentence fragments
    # in Tagalog (per S&O 1972 §10).
    #
    # F-structure shape:
    #
    #   PRED       = 'NP-FRAG <SUBJ>'   (synthetic fragment predicate)
    #   SUBJ       = ↓1                 (the asymmetric coord-NP)
    #   CLAUSE_TYPE = 'FRAGMENT'         (downstream-consumer marker)
    #
    # The synthetic ``PRED='NP-FRAG <SUBJ>'`` is a one-place
    # placeholder predicate. The asymmetric coord-NP itself has no
    # head ``PRED`` (its conjuncts each carry proper-name PREDs;
    # the coord-NP holds ``CONJUNCTS`` / ``COORD`` / ``CASE`` /
    # ``NUM`` only), so we cannot inherit PRED via ``(↑) = ↓1`` as
    # the L96 fragment-host NOUN rule above does. Synthesis is
    # unavoidable. The L97 fragment-answer rule
    # (``cfg/clause.py``, search "fragment-answer") similarly
    # uses ``(↑) = ↓1`` because its lex-host (``Oo``/``Hindi`` PRONs
    # with INTERJ=YES) carries PRED — L83 is the first fragment-S
    # rule whose host is a constructed structure without head PRED.
    #
    # The ``NP-FRAG`` placeholder is intentionally minimal-
    # commitment: Phase 6+ Glue / discourse-semantics work can
    # interpret it as "BE", "FOCUS-CONTRAST", or "ASSERT-AND-
    # REJECT" depending on the construction's pragmatics; this
    # layer just admits the fragment structurally.
    #
    # Coexistence with V-headed S rules: the same
    # ``NP[CASE=NOM, COORD=BUT_NOT]`` can serve as SUBJ of a
    # V-headed S (``Kumain si Maria, hindi si Juan.`` — Phase 5k
    # Commit 8 unchanged) OR as the sole daughter of this
    # fragment-S rule (``Si Maria, hindi si Juan.``). For surfaces
    # where both paths apply, the ranker picks per Phase 4 §7.9
    # heuristics — the V-headed reading is naturally preferred
    # because it has a real verbal PRED rather than the synthetic
    # NP-FRAG placeholder.
    #
    # Reference: Schachter & Otanes 1972 §10 (asymmetric contrast
    # construction); Ramos & Bautista 1986 ch.16 (NP coordination);
    # Phase 5n.B Commit 16 L96 fragment-host NOUN precedent (same
    # CLAUSE_TYPE=FRAGMENT marker, lex-feat gating);
    # ``docs/analysis-choices.md`` "Phase 5n.C Commit 4" design
    # appendix.
    rules.append(Rule(
        "S",
        ["NP[CASE=NOM, COORD=BUT_NOT]"],
        [
            "(↑ PRED) = 'NP-FRAG <SUBJ>'",
            "(↑ SUBJ) = ↓1",
            "(↑ CLAUSE_TYPE) = 'FRAGMENT'",
            "(↓1 COORD) =c 'BUT_NOT'",
        ],
    ))

    # === Phase 5n.C Commit 7 (§18 L81): distributive-Q topic ============
    #
    # ``Bawat bata, kumain.`` "Each child ate" — a fronted
    # universal-Q-NP topic, separated by a comma from an AV-
    # intransitive verb, producing a distributive-scope reading.
    # The matrix S carries ``DISTRIB=YES`` to mark the distributive
    # operator scope; the topic-NP becomes the matrix ``SUBJ``
    # (filling the AV verb's required argument).
    #
    # Daughter shape:
    #
    #   NP[CASE=NOM] PART[PUNCT_CLASS=COMMA] V[VOICE=AV]
    #     ↓1 = topic-NP (must be UNIV-marked, see (↓1 UNIV) =c)
    #     ↓2 = comma
    #     ↓3 = AV-intransitive verb (head; verb percolation from ↓3)
    #
    # Verb percolation is from ↓3 (the V is in third position; the
    # canonical ``_VERB_PERCOLATION`` helper from ``_helpers.py``
    # assumes ↓1 so equations are written explicitly here, mirroring
    # the Phase 5n.C Commit 2 L78 wide-scope hindi rule's pattern).
    #
    # ``(↓1 UNIV) =c true`` constraining equation gates the topic
    # to universal-Q-headed NPs (``bawat`` / ``kada`` per Phase 5f
    # Commit 20 lex; the universal-Q + bare-N rule in
    # ``cfg/nominal.py:696`` sets ``(↑ UNIV) = true`` on the
    # composed NP). Bare proper-name topics
    # (``Si Maria, kumain.``) lack UNIV and don't match. Non-
    # universal Qs (``lahat`` / ``iba`` / vague) also lack UNIV
    # and don't match. ``(↓2 PUNCT_CLASS) =c 'COMMA'`` is belt-
    # and-braces — the daughter pattern already restricts to
    # COMMA, but the constraining equation guards against any
    # future shape regression.
    #
    # Analysis chosen: each-distributive operator (rejected:
    # distributive coord-elaboration). The Q-NP raises to a
    # distributive operator scope position; the matrix is marked
    # with ``DISTRIB=YES`` for downstream consumers / Phase 6+
    # Glue work to interpret. Cited basis: S&O 1972 §10
    # (quantifier scope); R&B 1986 ch.16 (universal
    # quantification); Bresnan 2001 §6 + Dalrymple 2001 §6 on
    # LFG scope-feat marking.
    #
    # ``(↑ DISTRIB) = true`` re-uses the established matrix-scope
    # marker convention from Phase 5f Commit 19 predicative
    # distributive-cardinal rule (``cfg/clause.py:188`` —
    # ``Tigisang aklat sila.``); same feat name, same value, same
    # purpose: "this clause has a distributive reading." A
    # downstream consumer that filters on DISTRIB=YES picks up
    # both the cardinal-distributive and Q-distributive paths
    # uniformly.
    #
    # Scope: AV-intransitive only for this commit. Transitive
    # variants (``Bawat bata, kumain ng kanin.``) would need
    # parallel rules with V + GEN-NP / V + DAT-NP frames; defer
    # to a follow-on if corpus pressure surfaces. ``Bawat isa,
    # kumain.`` (Q + NUM) is also out of scope — Phase 5f Commit
    # 20 deferred Q + NUM composition (``bawat isa`` 0-parses as
    # an NP today), so the daughter pattern can't match.
    #
    # Disambiguation:
    #
    # * From the Phase 4 §7.4 ay-fronting rule: ay-fronted
    #   ``Bawat bata ay kumain.`` parses today and does NOT
    #   carry DISTRIB=YES — ay-fronting is general topicalization
    #   without the distributive-scope reading. The new comma+S
    #   rule is a distinct path that specifically marks the
    #   distributive scope.
    # * From the Phase 5n.C Commit 5 L83 fragment-NP-coord rule:
    #   structurally distinct (L83 has 1 daughter, this rule has
    #   3); the comma in L83 is *inside* the coord-NP daughter
    #   while the comma here is a *top-level* daughter. No
    #   structural overlap.
    #
    # Reference: Schachter & Otanes 1972 §10 (quantifier scope);
    # Ramos & Bautista 1986 ch.16 (universal quantification);
    # Phase 5f Commit 19 distributive-cardinal precedent
    # (``cfg/clause.py:188`` — ``DISTRIB=YES`` matrix marker);
    # Phase 5f Commit 20 universal-Q + bare-N rule
    # (``cfg/nominal.py:696`` — sole producer of NP[UNIV]);
    # ``docs/analysis-choices.md`` "Phase 5n.C Commit 6" design
    # appendix.
    rules.append(Rule(
        "S",
        [
            "NP[CASE=NOM]",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "V[VOICE=AV]",
        ],
        [
            "(↑ PRED) = ↓3 PRED",
            "(↑ VOICE) = ↓3 VOICE",
            "(↑ ASPECT) = ↓3 ASPECT",
            "(↑ MOOD) = ↓3 MOOD",
            "(↑ LEX-ASTRUCT) = ↓3 LEX-ASTRUCT",
            "(↑ DISTRIB) = true",
            "(↑ SUBJ) = ↓1",
            "(↓1 UNIV) =c true",
            "(↓2 PUNCT_CLASS) =c 'COMMA'",
        ],
    ))


    # === Phase 5n.C Commit 7.6 (§18 L81): transitive variants ===========
    #
    # Closes the L81 transitive deferral surfaced in user review of
    # Commit 7 (anti-deferral discipline per
    # ``tgllfg-phase-5n-c.md`` §8). Adds three parallel rules to the
    # Commit 7 intransitive rule above, mirroring the Phase 4 §7.1
    # canonical AV clause shapes (``cfg/clause.py:48-58``):
    #
    #   intransitive + DAT ADJUNCT:
    #     NP[CASE=NOM] PUNCT[COMMA] V[VOICE=AV] NP[CASE=DAT]
    #
    #   transitive (GEN OBJ):
    #     NP[CASE=NOM] PUNCT[COMMA] V[VOICE=AV] NP[CASE=GEN]
    #
    #   transitive + DAT ADJUNCT:
    #     NP[CASE=NOM] PUNCT[COMMA] V[VOICE=AV] NP[CASE=GEN]
    #     NP[CASE=DAT]
    #
    # Surfaces (sample):
    #
    #   Bawat bata, tumakbo sa parke.       (intrans + DAT)
    #   Bawat bata, kumain ng kanin.        (transitive)
    #   Bawat isa, bumili ng aklat.         (Q + NUM via Commit 7.5)
    #   Bawat bata, kumain ng kanin sa kusina. (trans + DAT)
    #
    # All variants share the same matrix-equation pattern as the
    # Commit 7 intransitive rule: verb percolation from ↓3,
    # ``(↑ DISTRIB) = true``, ``(↑ SUBJ) = ↓1``, ``(↓1 UNIV) =c
    # 'YES'``. The transitive variants add ``(↑ OBJ) = ↓4`` for
    # GEN-OBJ; the DAT-ADJUNCT variants add ``↓N ∈ (↑ ADJUNCT)`` for
    # the trailing DAT-NP. Same anti-overgeneration constraint
    # (``(↓1 UNIV) =c true``) — only universal-Q-headed topics
    # admit, preserving the bare-proper-name rejection from Commit 7.
    #
    # Ditransitive (3-arg DAT) variants and 2-DAT-ADJUNCT shapes
    # mirroring ``cfg/clause.py:578-606`` are deferred — corpus
    # pressure has not surfaced ditransitive distributive-Q topics.
    # If they appear, the same parameterised pattern extends
    # mechanically (add ``NP[CASE=DAT]`` daughters and corresponding
    # ADJUNCT membership equations).

    # Intransitive + DAT ADJUNCT.
    rules.append(Rule(
        "S",
        [
            "NP[CASE=NOM]",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "V[VOICE=AV]",
            "NP[CASE=DAT]",
        ],
        [
            "(↑ PRED) = ↓3 PRED",
            "(↑ VOICE) = ↓3 VOICE",
            "(↑ ASPECT) = ↓3 ASPECT",
            "(↑ MOOD) = ↓3 MOOD",
            "(↑ LEX-ASTRUCT) = ↓3 LEX-ASTRUCT",
            "(↑ DISTRIB) = true",
            "(↑ SUBJ) = ↓1",
            "↓4 ∈ (↑ ADJUNCT)",
            "(↓1 UNIV) =c true",
            "(↓2 PUNCT_CLASS) =c 'COMMA'",
        ],
    ))

    # Transitive (GEN OBJ).
    rules.append(Rule(
        "S",
        [
            "NP[CASE=NOM]",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "V[VOICE=AV]",
            "NP[CASE=GEN]",
        ],
        [
            "(↑ PRED) = ↓3 PRED",
            "(↑ VOICE) = ↓3 VOICE",
            "(↑ ASPECT) = ↓3 ASPECT",
            "(↑ MOOD) = ↓3 MOOD",
            "(↑ LEX-ASTRUCT) = ↓3 LEX-ASTRUCT",
            "(↑ DISTRIB) = true",
            "(↑ SUBJ) = ↓1",
            "(↑ OBJ) = ↓4",
            "(↓1 UNIV) =c true",
            "(↓2 PUNCT_CLASS) =c 'COMMA'",
        ],
    ))

    # Transitive + DAT ADJUNCT.
    rules.append(Rule(
        "S",
        [
            "NP[CASE=NOM]",
            "PUNCT[PUNCT_CLASS=COMMA]",
            "V[VOICE=AV]",
            "NP[CASE=GEN]",
            "NP[CASE=DAT]",
        ],
        [
            "(↑ PRED) = ↓3 PRED",
            "(↑ VOICE) = ↓3 VOICE",
            "(↑ ASPECT) = ↓3 ASPECT",
            "(↑ MOOD) = ↓3 MOOD",
            "(↑ LEX-ASTRUCT) = ↓3 LEX-ASTRUCT",
            "(↑ DISTRIB) = true",
            "(↑ SUBJ) = ↓1",
            "(↑ OBJ) = ↓4",
            "↓5 ∈ (↑ ADJUNCT)",
            "(↓1 UNIV) =c true",
            "(↓2 PUNCT_CLASS) =c 'COMMA'",
        ],
    ))
