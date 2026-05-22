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
    # Phase 8.V free-word-order companion to the V-SUBJ-DAT rule
    # above. Tagalog admits both V-SUBJ-DAT (``Pumunta si Juan sa
    # bahay.``) and V-DAT-SUBJ (``Pumunta sa bahay si Juan.``)
    # orderings; the latter was missing. CASE markers distinguish
    # the two NPs (NOM=ang/si, DAT=sa) so no spurious ambiguity
    # arises against the V-SUBJ-DAT rule. Required for closing the
    # 8.V audit hit ``Ni si Juan ay hindi nakapunta doon.`` whose
    # S_GAP residue (``nakapunta doon``) carries a locative
    # DAT-adjunct after a SUBJ-extracted AV-INTR verb.
    rules.append(Rule(
        "S",
        ["V[VOICE=AV]", "NP[CASE=DAT]", "NP[CASE=NOM]"],
        _eqs("(↑ SUBJ) = ↓3", "↓2 ∈ (↑ ADJUNCT)"),
    ))

    # --- Phase 9.V.1: SUBJ-trailing 4-element AV-TR (GEN-DAT-NOM) ------
    #
    # ``Kahapon ay sumulat ng liham kay Maria si Juan.``
    #     "Yesterday Juan wrote a letter to Maria."
    #     (S&O 1972 page 447 sent-689 matrix — 9.U Cluster B audit hit)
    #
    # Existing 4-element AV-TR rules cover NOM-GEN-DAT (canonical
    # VSO + DAT-adjunct) and GEN-NOM-DAT (free-word-order alt). The
    # SUBJ-trailing variant ``V GEN DAT NOM`` (V + OBJ + DAT-adj +
    # SUBJ) was missing — and surfaces naturally when a fronted-
    # ADV ay-pattern (``Kahapon ay ...``) deprioritizes the SUBJ to
    # clause-final position.
    #
    # Same equation set as rule 442 (GEN-NOM-DAT) but with the SUBJ
    # daughter index shifted to ↓4. CASE markers fully distinguish
    # the three NPs (NOM=ang/si, GEN=ng/ni, DAT=sa/kay) so no
    # spurious ambiguity arises against the canonical orderings.
    rules.append(Rule(
        "S",
        ["V[VOICE=AV]", "NP[CASE=GEN]", "NP[CASE=DAT]", "NP[CASE=NOM]"],
        _eqs(
            "(↑ SUBJ) = ↓4",
            "(↑ OBJ) = ↓2",
            "↓3 ∈ (↑ ADJUNCT)",
        ),
    ))

    # --- Phase 9.O.5: mangyari polite-imperative wrap ------------------
    #
    # ``Mangyaring umalis kayo.``    "Kindly leave."
    # ``Mangyaring kumain kayo.``    "Please eat."
    # ``Mangyaring magluto si Maria.``  "May Maria please cook."
    #
    # The discourse-particle / polite-marker ``mangyari`` (= "may
    # it happen / please") wraps a complete S via the ``-ng``
    # linker. The embedded S is fully formed (V + arguments); the
    # wrap lifts it to the matrix level and tags it with
    # ``POLITE_MARKER`` for downstream consumers.
    #
    # F-structure shape: the outer S IS the inner S (full lift via
    # ``(↑) = ↓3``), with an added ``POLITE_MARKER`` feat. No new
    # SUBJ binding, no XCOMP — ``mangyari`` is structurally a
    # politeness-marker wrap, not a control verb.
    #
    # Restricted to the bare-CTPL ``mangyari`` form via
    # ``POLITE_MARKER`` (set on the Phase 9.O ``mang_retain`` bare
    # CTPL cell); the PFV ``nangyari`` ("happened") and other
    # forms continue to function as regular ``yari`` verbs without
    # the politeness reading.
    rules.append(Rule(
        "S",
        ["V[POLITE_MARKER=true]", "PART[LINK=NG]", "S"],
        [
            "(↑) = ↓3",
            "(↑ POLITE_MARKER) = true",
        ],
    ))


    # --- Phase 9.T.4: nang V-DUPLICATE intensifier (S-level) ---
    #
    # ``Tumawa nang tumawa si Juan.``      "Juan laughed and laughed."
    # ``Lumalakad nang lumalakad ang kartero.``
    #                                       "The mailman walked and walked."
    # ``Kumain nang kumain si Pedro.``      "Pedro ate and ate."
    #
    # 8.H ``test_nang_v_duplicate_idiom`` pin (S&O 1972 p.410
    # sent-593). The ``V nang V`` reduplication is an intensifier
    # / continuative-aspectual idiom — the same V form appears
    # before and after the ``nang`` particle, expressing repeated
    # or continuous action ("X-ing and X-ing").
    #
    # Rule shape (S-level direct — a V-wrap would lose the head
    # daughter's VOICE feature on the wrapped V, breaking the
    # parent rule's ``V[VOICE=AV]`` expectation):
    #
    #   S → V[VOICE=AV]  PART  V[VOICE=AV]  NP[CASE=NOM]
    #     (↑) = ↓1                       matrix f-structure shared
    #                                    with first V (head)
    #     (↓2 LEMMA) =c 'nang'           gate the middle particle
    #     (↓3 LEMMA) = (↓1 LEMMA)        lemma-match
    #     (↓3 ASPECT) = (↓1 ASPECT)      aspect-match
    #     (↑ SUBJ) = ↓4                  SUBJ binds to the NOM-NP
    #     (↑ INTENSIFIER) = true         intensifier marker on matrix
    #
    # AV-only scope: the audit hits are all AV-intransitive
    # (`Tumawa`, `Lumalakad`, `Tumakbo`, `Kumain` — all AV). The
    # bare-N V-DUP variant (`Lakad nang lakad ang kartero.`) and
    # transitive variants (OV/DV/IV) defer to follow-ons if audit
    # pressure surfaces them.
    #
    # Disambiguates against the existing TEMP_SINCE / TEMP_WHEN
    # `nang` subordinator rules — those take an S complement, not
    # a V duplicate; the daughter-3 V shape is mutually exclusive.
    rules.append(Rule(
        "S",
        ["V[VOICE=AV]", "PART", "V[VOICE=AV]", "NP[CASE=NOM]"],
        _eqs(
            "(↑) = ↓1",
            "(↓2 LEMMA) =c 'nang'",
            "(↓3 LEMMA) = (↓1 LEMMA)",
            "(↓3 ASPECT) = (↓1 ASPECT)",
            "(↑ SUBJ) = ↓4",
            "(↑ INTENSIFIER) = true",
        ),
    ))

    # 9.T.4 companion: V-DUP with 3-arg AV-CAUS-INDIRECT-FLAT
    # shape (8.H ``test_nang_v_duplicate_idiom`` pin verbatim
    # — S&O 1972 p.410 sent-593):
    #
    #   ``Nagpapakain sila nang nagpapakain ng kendi sa kanila.``
    #
    # Order: V NOM nang V GEN DAT — the SUBJ surfaces between
    # the two V tokens, with the GEN-OBJ (PATIENT) + DAT-OBL
    # (CAUSEE) trailing the duplicated V.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV, CAUS=INDIRECT]", "NP[CASE=NOM]",
            "PART", "V[VOICE=AV, CAUS=INDIRECT]",
            "NP[CASE=GEN]", "NP[CASE=DAT]",
        ],
        _eqs(
            "(↑) = ↓1",
            "(↓3 LEMMA) =c 'nang'",
            "(↓4 LEMMA) = (↓1 LEMMA)",
            "(↓4 ASPECT) = (↓1 ASPECT)",
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓5",
            "(↑ OBL-CAUSEE) = ↓6",
            "(↑ INTENSIFIER) = true",
        ),
    ))


    # --- Phase 9.O.4: AV-NVOL absolutive (Naalala ko) ------------------
    #
    # ``Naalala ko.``    "I (NVOL-)remembered."
    # ``Naalala niya.``  "He/she (NVOL-)remembered."
    #
    # Colloquial NVOL-with-implicit-pivot construction. The
    # ``ma-`` prefix produces VOICE=AV, MOOD=NVOL surfaces
    # (``naalala``, ``natulog``, ``naupo``) that semantically
    # invert agent/patient case (the GEN-clitic is the
    # experiencer/actor, the NOM-NP is the stimulus/patient when
    # present). The absolutive use drops the NOM patient pivot
    # entirely — the GEN actor stands alone.
    #
    # Restricted to verbs flagged ``AV_ABSOL=true`` (Phase 9.O B3.A
    # lex feat) and MOOD=NVOL so this rule doesn't loosen
    # canonical AV case-marking. The synth path's AV-absolutive
    # INTR entry (``<SUBJ>`` 1-arg, ACTOR→SUBJ) supplies the
    # predicate; this rule binds the GEN-NP to SUBJ in absolutive
    # context.
    rules.append(Rule(
        "S",
        ["V[VOICE=AV, MOOD=NVOL, AV_ABSOL=true]", "NP[CASE=GEN]"],
        _eqs("(↑ SUBJ) = ↓2"),
    ))

    # --- Phase 9.V.2: DV-NVOL absolutive (limot family) ----------------
    #
    # ``Malimutan ko.``       "I (will) forget (it)."
    # ``Nalimutan ko.``       "I forgot (it)."
    # ``Bago ko malimutan, nakita mo ba si Jonathan sa miting?``
    #     "Before I forget, did you see Jonathan at the meeting?"
    #     (R&C 1990 Ch5 Transition Phrases sent-661 — 9.U Cluster B
    #      audit hit; the SubordClause body ``ko malimutan`` is the
    #      experiencer-clitic-fronted form of ``Malimutan ko.`` with
    #      ``ko`` host-moved to the subordinator.)
    #
    # Parallel to the 9.O AV-NVOL absolutive rule above, but for
    # DV-NVOL forms (``malimutan`` / ``nalimutan`` — the ma+-an
    # paradigm cell on AV_ABSOL-flagged roots). Morph analyzer
    # produces ``malimutan`` as V[VOICE=DV, ASPECT=CTPL, MOOD=NVOL,
    # AV_ABSOL=true]; the AV-NVOL rule's VOICE=AV constraint
    # excludes it, so this sibling rule admits the parallel
    # DV-NVOL absolutive parse where the GEN-PRON experiencer
    # surfaces as the matrix SUBJ.
    rules.append(Rule(
        "S",
        ["V[VOICE=DV, MOOD=NVOL, AV_ABSOL=true]", "NP[CASE=GEN]"],
        _eqs("(↑ SUBJ) = ↓2"),
    ))


    # --- Phase 9.X.c42 + c44 + c45: impersonal non-AV voice ----------
    #
    # ``Sinulat ang aklat.``       "The book was written." (OV-IND)
    # ``Kinain ang pagkain.``      "The food was eaten." (OV-IND)
    # ``Dinaraos ang mga piyesta.``  "The festivals were held."
    #                                (OV-IND; PANAHON sent-10)
    # ``Masaklolohan ang mga napinsalaan.``
    #                              "The damaged ones can be helped."
    #                              (DV-NVOL; PANAHON sent-27)
    # ``Sisimulan ang ikalawang pagtatanim.``
    #                              "The second planting will be
    #                              started." (DV-IND; PANAHON sent-36)
    # ``Itinanim ang palay noong Hunyo.``
    #                              "The rice was planted in June."
    #                              (IV-IND)
    #
    # Tagalog non-AV voices (OV / DV / IV) freely drop the AGENT for
    # an agent-absorbed (discourse-generic) reading — Kroeger 1993 /
    # Schachter & Otanes 1972 §9.2 (focus-construction patterns).
    # The canonical Phase 5b 2-NP / 3-NP rules (``V NP[GEN] NP[NOM]``
    # / ``V NP[NOM] NP[GEN] NP[GEN]`` / etc.) require an overt GEN-NP
    # AGENT, so the agent-absorbed case failed completeness at the
    # V's ``<SUBJ, OBJ-AGENT>`` PRED frame.
    #
    # Parallel to the 9.X.c41 impersonal-modal SAY rule: SUBJ binds
    # to the NOM-NP (= the PATIENT / GOAL / CONVEYED mapped to SUBJ
    # by the non-AV voice); OBJ-AGENT is filled with a generic PRO
    # placeholder. No MOOD restriction — impersonal is broadly
    # available across all aspect/mood combinations.
    #
    # History:
    #   * c42 (2026-05-21): introduced for DV-NVOL only (gated
    #     MOOD=NVOL); closed sent-17 (``matapatan ang oras``).
    #   * c44 (2026-05-21): extended to OV (any MOOD); closed
    #     ``Sinulat ang aklat`` etc.
    #   * c45 (2026-05-21): consolidated as voice-loop covering
    #     OV / DV / IV (any MOOD); closes ``Sisimulan ang ikalawang
    #     pagtatanim`` (DV-IND) and ``Itinanim ang palay`` (IV-IND).
    for voice in ("OV", "DV", "IV"):
        rules.append(Rule(
            "S",
            [f"V[VOICE={voice}]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-AGENT PRED) = 'PRO'",
            ),
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


    # --- Phase 8.U: comparative `parang` with NP standard ---
    #
    # Companion to the Phase 5e Commit 26 rule above. The bare-N
    # variant of `parang` admits standards like ``parang aso``,
    # ``parang malaking aso`` — bare-N or modified-N. Audit-named
    # target ``Parang kayo ako.`` ("I'm like you") uses a PRON as
    # the standard, which doesn't project to N (it builds as
    # NP[CASE=NOM] via the standalone-PRON-as-NP path). This
    # parallel rule admits any NP[CASE=NOM]-shaped standard —
    # bare PRON (``kayo``, ``ako``), proper-name NP
    # (``si Juan``), or case-marked NP (``ang lalaki``) — with
    # the same equation set.
    #
    # No double-firing risk on the existing bare-N targets
    # (``Parang aso ang bata.``) because bare ``aso`` projects
    # only to N, not NP[CASE=NOM] — the case-less N→NP wrap is
    # intentionally absent (Phase 5f Commit 1 design note).
    #
    # References: Schachter & Otanes 1972 §13 (similative
    # comparison); R&G 1981 §6 (parang and tila evidentials/
    # comparatives).
    rules.append(Rule(
        "S",
        [
            "V[COMPARATIVE, CTRL_CLASS=RAISING_BARE]",
            "NP[CASE=NOM]",
            "NP[CASE=NOM]",
        ],
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

    # --- Phase 8.H: AV-CAUS-INDIRECT flat 3-arg matrix wrap --------
    #
    # ``Nagpapakain sila ng kendi sa kanila.``
    #     "They are feeding them candy."
    #     (S&O 1972 page 410 / sent-593 — without the
    #     ``nang nagpapakain`` reduplication idiom)
    #
    # Companion to the biclausal AV-CAUS-INDIRECT analysis
    # (``cfg/control.py`` Phase 4 §7.6 intransitive control wrap
    # — ``V[CTRL_CLASS=INTRANS] NP[CASE=NOM] PART[LINK] S_XCOMP``).
    # S&O 1972 §10.4 documents both shapes for ``magpa-``: (a)
    # biclausal with overt embedded V; (b) flat where the
    # embedded event's arguments surface directly as NP daughters
    # of the matrix. The flat form lacks an XCOMP daughter.
    #
    # Matched by a new lex entry in ``data/tgl/lexicon/causative.yaml``
    # with PRED ``CAUSE-EAT <SUBJ, OBJ, OBL-CAUSEE>`` and
    # ``intrinsic: AV_CAUS_INDIRECT_FLAT`` (parallel to the
    # existing biclausal entry ``intrinsic: AV_CAUS_INDIRECT``).
    # The LMT matcher disambiguates by visible
    # ``morph_constraints`` overlap with most-specific-wins;
    # 8.H's flat entry is selected when no S_XCOMP daughter is
    # present.
    #
    # Three arg slots map to NP daughters: CAUSER (matrix SUBJ;
    # NOM-marked), PATIENT (the caused-to-be-V'd thing; GEN-
    # marked OBJ), CAUSEE (the one made to V; DAT-marked
    # OBL-CAUSEE). Audit-shape canonical order is NOM-GEN-DAT;
    # other orderings deferred to future sub-PRs if corpus
    # pressure surfaces them.
    v_av_caus_ind = "V[VOICE=AV, CAUS=INDIRECT]"
    rules.append(Rule(
        "S",
        [v_av_caus_ind, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=DAT]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓3",
            "(↑ OBL-CAUSEE) = ↓4",
        ),
    ))

    # --- Phase 9.T.3: 2-arg AV-CAUS-INDIRECT --------------------
    #
    # ``Nagpakain siya ng kendi.`` (8.H ``test_two_arg_av_caus_indirect``
    # pin) — CAUSER + PATIENT only, no overt CAUSEE. The CAUSEE is
    # implicit/recoverable from context but not syntactically
    # realized.
    #
    # Two-daughter rule (CAUSER NP[CASE=NOM] + PATIENT NP[CASE=GEN])
    # paired with the new ``AV_CAUS_INDIRECT_2ARG`` lex profile
    # (causative.yaml ``kain`` entry; intrinsic
    # ``AV_CAUS_INDIRECT_2ARG``). The LMT matcher selects between
    # this 2-arg entry, the 8.H flat 3-arg entry, and the
    # biclausal AV_CAUS_INDIRECT entry by argument-count overlap
    # with the surface NP daughters.
    #
    # No conflict with the 3-arg flat rule above (different
    # daughter count, mutually exclusive on c-structure match).
    rules.append(Rule(
        "S",
        [v_av_caus_ind, "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓3",
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

    # --- Phase 8.O: AV-CAUS-INDIRECT SAY-class reported clause -----
    #
    # ``Nagpasabi si Maria na kumain si Juan.``
    #     "Maria sent word that Juan ate."
    # ``Nagpasabi si Emmanuel na magdala ka ng mga CDs sa party.``
    #     "Emmanuel sent word for you to bring CDs to the party."
    #     (R&C 1990 sent-899 — verbatim with proper-name lex add)
    # ``Nagpasabi ang boss ko na hindi siya papasok sa trabaho.``
    #     "My boss sent word that he wouldn't come to work."
    #     (R&C 1990 sent-909 — verbatim with proper-name lex add)
    #
    # Phase 5n.A Commit 26 closed the OV reported-clause variant
    # (``Sinabi niya na pumunta si Maria.`` — OV-SAY rule above).
    # The audit-named target for 8.O is the AV-CAUS-INDIRECT form
    # ``nagpasabi`` — "sent word that / had told". The morph cell
    # produces V[VOICE=AV, CAUS=INDIRECT, CTRL_CLASS=INTRANS,
    # SAY_CLASS=true] with PRED template ``SABI <SUBJ, OBJ>`` (the
    # TR-class [AGENT, THEME] mapping with THEME → OBJ in AV).
    #
    # The biclausal control wrap (Phase 4 §7.6
    # ``V[CTRL_CLASS=INTRANS] NP[CASE=NOM] PART[LINK] S_XCOMP``)
    # binds the reported clause to XCOMP, but the lex template
    # expects OBJ — so LMT coherence-fails on the XCOMP / OBJ
    # mismatch. This rule consumes the reported clause as a bare
    # S (not S_XCOMP) and binds it to OBJ directly. Mirrors the
    # Phase 5n.A C26 OV-SAY rule with daughter-index shift (NOM-
    # NP at ↓2 here vs. GEN-PRON at ↓2 there) and an added
    # CAUS=INDIRECT gate to keep the rule narrowly applied to the
    # SAY-class indirect-causative subset.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV, CAUS=INDIRECT, SAY_CLASS]",
            "NP[CASE=NOM]",
            "PART[LINK=NA]",
            "S",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓4",
            "(↓1 SAY_CLASS) =c true",
            "(↓1 CAUS) =c 'INDIRECT'",
            "(↓3 LINK) =c 'NA'",
        ),
    ))


    # --- Phase 9.W: plain AV SAY-class reported clause -----
    #
    # ``Nagsabi si Maria na kumain si Juan.``
    #     "Maria said that Juan ate."
    # ``Nagsabi siya na hindi siya papasok.``
    #     "He said he wouldn't come in."
    #
    # The Phase 8.O AV-CAUS-INDIRECT-SAY rule above closes the
    # ``nagpasabi`` "sent word that" sub-case. The audit pile also
    # has bare ``nagsabi`` "said that" forms whose morph cell
    # produces V[VOICE=AV, SAY_CLASS=true] with no CAUS feature
    # (CAUS=NONE per the morph probe). The plain AV-SAY rule
    # mirrors the 8.O shape minus the CAUS=INDIRECT constraint,
    # binding the ``na``-introduced reported clause to OBJ.
    rules.append(Rule(
        "S",
        [
            "V[VOICE=AV, SAY_CLASS]",
            "NP[CASE=NOM]",
            "PART[LINK=NA]",
            "S",
        ],
        _eqs(
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓4",
            "(↓1 SAY_CLASS) =c true",
            "(↓1 CAUS) =c 'NONE'",
            "(↓3 LINK) =c 'NA'",
        ),
    ))


    # --- Phase 9.X.c41: impersonal-modal SAY (NVOL + bound -ng) ----
    #
    # ``Masasabing may dalang malas at suwerte ang panahong ito.``
    #     "It can be said that this season brings both bad luck and
    #      good luck." (PANAHON sent-33)
    #
    # The AV-NVOL ``masasabi`` "(it) can be said" is the
    # impersonal-modal sub-class of SAY: no overt SUBJ (generic /
    # impersonal actor), bound ``-ng`` linker (not the standalone
    # ``na`` complementizer used by 5n.A C26 / 8.O / 9.W explicit-
    # SUBJ SAY rules), and the asserted proposition surfaces as
    # an OBJ-clause.
    #
    # LFG analysis: matrix predicate is the SAY-class V (PRED
    # template ``SABI <SUBJ, OBJ>`` from morph synth); the embedded
    # clause binds to OBJ; SUBJ is filled with a generic / impersonal
    # PRO placeholder (an open f-node with PRED bound to a sentinel).
    # The 9.W explicit-SUBJ rule above can't fire here because
    # there's no overt NOM-NP to bind SUBJ. This rule mirrors 9.W
    # minus the NOM-NP daughter and with the SUBJ filled by PRO
    # internally.
    #
    # Gating:
    #   * ``V[VOICE=AV, SAY_CLASS]`` — SAY-class only.
    #   * ``(↓1 MOOD) =c 'NVOL'`` — non-volitional mood (maka-prefix)
    #     is what licenses the impersonal reading; volitional
    #     ``magsabi`` / ``sasabihin`` require an overt SUBJ via
    #     the 9.W / 5n.A C26 rules above.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "V[VOICE=AV, SAY_CLASS]",
                f"PART[LINK={link}]",
                "S",
            ],
            _eqs(
                "(↑) = ↓1",
                "(↑ OBJ) = ↓3",
                "(↑ SUBJ PRED) = 'PRO'",
                "(↓1 SAY_CLASS) =c true",
                "(↓1 MOOD) =c 'NVOL'",
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
            # Phase 8.L Commit 1: parallel lift of DISTRIB so the
            # ``magkasing-`` distributive-equative reading is
            # visible at clause level (consumers reading off
            # DISTRIB can branch on plural-subject licensing).
            # Daughter ADJs without DISTRIB leave matrix DISTRIB
            # undefined (no-op via unification semantics).
            "(↑ DISTRIB) = ↓1 DISTRIB",
            # Phase 8.L Commit 3: parallel lift of KASING_N for
            # the NOUN-derived ``kasing-`` equative cell
            # (paradigms.yaml ``kasing_n_eq``). Marks the surface
            # as originating from a NOUN base so downstream
            # consumers can distinguish ADJ-derived vs NOUN-
            # derived equatives. No-op when daughter lacks the
            # feat.
            "(↑ KASING_N) = ↓1 KASING_N",
        ],
    ))

    # --- Phase 9.X.c7: predicative-ADV clause ------------------------
    #
    # ``Bigla ang pagdating ng tag-ulan.`` "The arrival of the rainy
    #     season is sudden." (PANAHON sent-19)
    # ``Bihira ang bagyo sa mga buwang ito.`` "Typhoons are rare in
    #     these months." (PANAHON sent-37)
    # ``Manakanaka lamang ang ulan.`` "The rain is only occasional."
    #     (PANAHON sent-4 — after merge_hyphen_compounds rejoins
    #     ``manaka-naka`` → ``manakanaka``)
    # ``Taun-taon ang bagyo.`` "Typhoons (come) every year."
    #     (similar to PANAHON sent-21)
    #
    # ADV-as-predicate: many Tagalog ADVs predicate a NOM-NP subject
    # with the same shape as the Phase 5g ADJ-predicate rule.
    # FREQUENCY ADVs (``bihira`` / ``kadalasan`` / ``manakanaka`` /
    # ``tauntaon``), MANNER ADVs (``bigla`` / ``agad``), TIME ADVs
    # (``kahapon`` / ``ngayon``) can all serve as predicates.
    #
    # F-structure shape parallels ADJ-predicate:
    #
    #   PRED         = 'ADV <SUBJ>'
    #   ADV_LEMMA    = the adverb's lemma
    #   ADV_TYPE     = lifted from the ADV daughter (FREQUENCY /
    #                  MANNER / TIME / LOCATION / etc.)
    #   PREDICATIVE  = true
    #   SUBJ         = the NOM-NP pivot
    #
    # No VOICE / ASPECT / MOOD: an adverbial predicate is verbless
    # and stative-like, parallel to the ADJ-predicate analytical
    # commitment.
    rules.append(Rule(
        "S",
        ["ADV", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'ADV <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ ADV_LEMMA) = ↓1 LEMMA",
            "(↑ ADV_TYPE) = ↓1 ADV_TYPE",
            "(↑ PREDICATIVE) = true",
        ],
    ))

    # --- Phase 9.O.3: stative-passive ADJ with GEN-actor ----------------
    #
    # ``Kilala ko si Maria.``  "Maria is known by me." / "I know Maria."
    # ``Kilala mo ba si Steve?``  "Do you know Steve?"
    # ``Kilala niya sila.``  "He/she knows them."
    #
    # Bare-form ADJs flagged with ``STATIVE_PRED: true`` (Phase 9.O
    # follow-on, see ``data/tgl/adjectives.yaml`` entry for
    # ``kilala``) license a GEN-actor argument alongside the NOM
    # pivot. Structurally parallel to OV V-predicates: the ADJ
    # acts as a stative-passive participle, the GEN-NP is the
    # implicit AGENT, the NOM-NP is the patient pivot/SUBJ.
    #
    # F-structure shape:
    #
    #   PRED        = 'ADJ <SUBJ, OBJ-AGENT>'
    #   ADJ_LEMMA   = the adjective's lemma
    #   PREDICATIVE = true
    #   STATIVE_PRED = true
    #   SUBJ        = the NOM-NP pivot (the "known one")
    #   OBJ-AGENT   = the GEN-NP (the "knower")
    #
    # Two ordering variants:
    #   - GEN before NOM (canonical): ``Kilala ko si Maria.``
    #   - NOM before GEN: ``Kilala si Maria ko.`` (rare; not pinned)
    #
    # 2P clitic absorption (``ba``/``ka``/``naman``) attaches at
    # the S level via the existing ``S → S PART[CLITIC_CLASS=2P]``
    # rule, so ``Kilala mo ba si Steve?`` parses by first building
    # the bare 2-arg S and then absorbing ``ba``.
    rules.append(Rule(
        "S",
        ["ADJ[STATIVE_PRED]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'ADJ <SUBJ, OBJ-AGENT>'",
            "(↑ SUBJ) = ↓3",
            "(↑ OBJ-AGENT) = ↓2",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↑ STATIVE_PRED) = true",
            "(↓1 STATIVE_PRED) =c true",
            "(↓1 PREDICATIVE) =c true",
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
    # Cardinal contrast — ``Tatlo ang aklat.`` parses via the Phase
    # 5f Commit 4 predicative-cardinal rule (NUM[CARDINAL] head),
    # which has no VAGUE feat and so does not fire this rule. Each
    # predicative shape (vague-Q, cardinal, ADJ) has its own clause
    # rule with disjoint head categories.
    #
    # Phase 6.H Commit 4 (§18.1.2 cleanup): the previously-present
    # belt-and-braces ``(↓1 VAGUE) =c true`` is redundant under the
    # post-6.C strict matcher (``expected.keys() ⊆ candidate.keys()``
    # + shared-key compat). The ``Q[VAGUE]`` daughter pattern in the
    # RHS list already gates the candidate's VAGUE feat. Dropped as
    # one of the two explicitly-tagged non-conflict-matcher-leak
    # sites per the Phase 6.H plan §5.8 C3.
    rules.append(Rule(
        "S",
        ["Q[VAGUE]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'Q-PREDICATIVE <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ Q_LEMMA) = ↓1 LEMMA",
            "(↑ QUANT) = ↓1 QUANT",
            "(↑ PREDICATIVE) = true",
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

    # --- 9.X.c19: ka-N companion S_GAP for RC bodies --------------
    #
    # ``Ang ulan na kasama nito ay nagpapabaha.`` "The rain that
    # accompanies this causes flooding" (R&G 1981 PANAHON sent-23
    # — closes when the topic-NP ``naman`` attachment is separately
    # addressed).
    #
    # Parallel to the c17 matrix S form (``S → N NP[GEN]
    # NP[CASE=NOM]``) but as an ``S_GAP`` for relative-clause
    # bodies. The SUBJ is the gap (``REL-PRO``) bound by the
    # enclosing NP-RC wrap; the GEN-NP names the companion.
    #
    #   S_GAP → N NP[CASE=GEN]
    #     (↑ PRED) = 'BE-N <SUBJ>'
    #     (↑ SUBJ) = (↑ REL-PRO)
    #     (↑ N_LEMMA) = ↓1 LEMMA
    #     (↑ POSS) = ↓2
    #     (↑ PREDICATIVE) = true
    #     (↓1 KA_PRED) =c true     ← scope gate
    #     ¬ (↓1 WH)
    #
    # The ``KA_PRED=c true`` constraint scopes the rule to ka-
    # prefixed companion nominals lex'd with ``KA_PRED=true``
    # (Phase 9.X.c19 lex updates to ``kasama`` / ``kasabay``).
    # Without this gate the rule competed with ordinary POSS-NPs
    # inside DAT contexts (``kaysa sa kapatid niya`` admits a
    # competing S_GAP parse where ``kapatid niya`` is misread as
    # an N-pred); the gate keeps the rule scoped to true companion
    # nominals only.
    #
    # ``KA_PRED`` is a new binary feat (BINARY_FEATS 59 → 60);
    # declared in ``core/feats.py`` and documented in
    # ``docs/feats-binary-audit.md``.
    #
    # Reference: R&G 1981 §7.1 (nominal predication, RC variant);
    # R&G 1981 PANAHON essay (sent-23).
    rules.append(Rule(
        "S_GAP",
        ["N", "NP[CASE=GEN]"],
        [
            "(↑ PRED) = 'BE-N <SUBJ>'",
            "(↑ SUBJ) = (↑ REL-PRO)",
            "(↑ N_LEMMA) = ↓1 LEMMA",
            "(↑ POSS) = ↓2",
            "(↑ PREDICATIVE) = true",
            "(↓1 KA_PRED) =c true",
            "¬ (↓1 WH)",
        ],
    ))

    # --- 9.X.c17: N-predicate + GEN-NP + ang-NP SUBJ ---------------
    #
    # ``Kasabay ng bagyo ang pagpatak ng monsoon.`` "Together with
    # the storm is the falling of the monsoon" (R&G 1981 PANAHON
    # sent-28 — closes when the SUBJ NP nominalization gap is
    # separately addressed).
    # ``Kasama ng aso ang pusa.`` "The cat is together with the dog."
    # ``Pansin niya ang aklat.`` "She notices the book."
    #
    # Extends the bare N-predicate clause (rule directly above,
    # ``S → N NP[CASE=NOM]``) to admit a GEN-NP between the
    # predicate-N and the ang-NP SUBJ. Two construction families
    # use this shape:
    #
    # 1. ka-N companion nominals (``kasabay`` / ``kasama`` /
    #    ``katabi``): the GEN-NP names the companion party.
    # 2. Nominal-headed transitive-like predicates (``pansin`` /
    #    ``tiwala``): the GEN-NP names the actor of the verbal-noun
    #    predicate.
    #
    # Both families bind the GEN-NP as ``POSS`` on the matrix
    # f-structure — semantically loose (POSS covers both companion
    # and actor roles in Tagalog nominal predication) but
    # structurally uniform.
    #
    # No special gating beyond ``¬ (↓1 WH)`` (mirrors the bare
    # N-pred rule). The construction is structurally disjoint from
    # V-headed clauses (V ≠ N), so cross-firing with the various
    # V-frame rules is excluded by the daughter category.
    #
    # **S_GAP variant deferred.** A parallel ``S_GAP → N
    # NP[CASE=GEN]`` rule would let the construction appear inside
    # a relative clause (``ang ulan na kasama nito`` PANAHON
    # sent-23), but it's ambiguous with ordinary POSS-NPs inside
    # DAT contexts (``kaysa sa kapatid niya`` admits a competing
    # S_GAP parse where ``kapatid niya`` is an N-pred). Future
    # commit can revisit with a lemma gate (``KA_PRED`` feat or
    # explicit lemma whitelist) to scope the S_GAP variant.
    #
    # Reference: R&G 1981 §7.1 (nominal predication with GEN
    # complement); R&G 1981 PANAHON essay.
    rules.append(Rule(
        "S",
        ["N", "NP[CASE=GEN]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-N <SUBJ>'",
            "(↑ SUBJ) = ↓3",
            "(↑ N_LEMMA) = ↓1 LEMMA",
            "(↑ POSS) = ↓2",
            "(↑ PREDICATIVE) = true",
            "¬ (↓1 WH)",
        ],
    ))


    # --- Phase 8.R: impersonal clock-time predication --------------
    #
    # ``Alas singko ngayon.``           "It's 5 o'clock now."
    # ``Alas tres pa lang.``            "It's only 3 o'clock."
    # ``Alas singko ba?``               "Is it 5 o'clock?"
    #
    # Clock-time predications are impersonal — no SUBJ on the
    # surface. Distinct from Phase 5n.B C2 (``Doktor ako.`` — N-pred
    # + NOM-pivot) and Phase 8.X C1 (``Ito ang aklat.`` — DEM-pivot).
    # The Phase 5n.B rule above REQUIRES a NOM-NP/NOM-PRON pivot;
    # this rule fires when the predicate is a clock-time N
    # (SEM_CLASS=TIME from the Phase 8.R alas+NUM rule in
    # cfg/nominal.py) and there is no pivot daughter.
    #
    # Gating: ``(↓1 SEM_CLASS) =c 'TIME'`` constrains the rule to
    # clock-time N heads, preventing spurious-ambiguity with other
    # bare-N surfaces (where Phase 5n.B C2 with a NOM-pivot is the
    # canonical analysis).
    #
    # 2P clitic absorption attaches afterward via the existing
    # Phase 4 §7.3 rules — ``Alas singko ba?`` builds as this S
    # plus ``ba`` (QUESTION) clitic. Sentence-final temporal/
    # locative adjuncts (``ngayon``, ``sa LA``) attach via the
    # existing post-matrix adjunct rules. The ``na`` ALREADY 2P
    # clitic fails to absorb on impersonal-S — this is a
    # pre-existing chart issue also affecting ``Marami ito na.``
    # (Q-pred + DEM-pivot), documented in 8.R out-of-scope pins
    # for a separate diagnostic.
    #
    # F-structure shape:
    #   PRED        = 'BE-TIME'
    #   TIME_VALUE  = the clock-time N's TIME_VALUE
    #   PREDICATIVE = true
    rules.append(Rule(
        "S",
        ["N"],
        [
            "(↑ PRED) = 'BE-TIME'",
            "(↑ TIME_VALUE) = ↓1 TIME_VALUE",
            "(↑ PREDICATIVE) = true",
            "(↓1 SEM_CLASS) =c 'TIME'",
        ],
    ))


    # --- Phase 8.X Commit 1: DEM-pivot clause ------------------
    #
    # ``Ito ang aklat.``       "This is the book."
    # ``Ito ang tatay ko.``    "This is my dad."
    # ``Iyan ang bahay.``      "That is the house."
    # ``Iyon ang trabaho ni Juan.``
    #                          "That is Juan's job."
    #
    # Closes the Phase 8.X audit gap surfaced in
    # docs/coverage-audit-2026-05.md §15 (R&G Conversational
    # construction-gap rows: ``Ito ang tatay ko.`` / ``Ito ang
    # bahay ko.``). The Wave 3 diagnostic showed both Wave-3
    # sources contain naturalistic DEM-pivot predications that
    # the grammar didn't license — the N-pivot rule above only
    # accepts bare-N left daughters, and the wh-cleft rule (§5i)
    # only accepts wh-PRONs.
    #
    # Demonstratives are categorized as ``DET[CASE=NOM, DEM]``
    # by the morph analyzer (see particles.yaml / cfg/nominal.py
    # Phase 4 §7.8 — the same category that wraps to ``NP[CASE=
    # NOM]`` via the standalone-DEM rule). Here the bare DET[DEM]
    # serves as the predicate; the ang-NP is the subject.
    #
    # F-structure shape (mirroring the N-pivot rule):
    #
    #   PRED        = 'BE-DEM <SUBJ>'
    #   DEIXIS      = lifted from the DEM (PROX / MED / DIST) —
    #                 uniquely identifies the demonstrative;
    #                 ``ito`` → PROX, ``iyan`` → MED, ``iyon`` → DIST.
    #   PREDICATIVE = true
    #   SUBJ        = the NOM-NP subject
    #
    # DEM_LEMMA is NOT lifted: per ``data/tgl/pronouns.yaml`` the
    # DEM determiner entries (and similarly the non-wh PRON
    # entries) do not register LEMMA as a feature — the
    # ``MorphAnalysis.lemma`` attribute exists but does not flow
    # through to f-structure (cf. the wh-PRON ``sino`` entry which
    # does include ``LEMMA: sino`` and thus supports ``(↑ WH_LEMMA)
    # = ↓1 LEMMA``). DEIXIS provides equivalent identification.
    rules.append(Rule(
        "S",
        ["DET[CASE=NOM, DEM]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-DEM <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ DEIXIS) = ↓1 DEIXIS",
            "(↑ PREDICATIVE) = true",
        ],
    ))


    # --- Phase 8.X Commit 2: non-wh PRON-pivot clause ---------
    #
    # ``Ako ang guro.``        "I am the teacher."
    # ``Siya ang kaibigan ko.``
    #                          "He/she is my friend."
    # ``Kami ang nanalo.``     "We are the winners."
    #
    # Closes the noun-pivot subset of Phase 8.S (pronominal-
    # pivot clefts) surfaced in docs/coverage-audit-2026-05.md
    # §15. The diagnostic for 8.X also surfaced this gap — the
    # N-pivot rule above accepts ``Aklat ito.`` (bare-N pivot)
    # but not ``Ako ang guro.`` (bare-PRON pivot), and the
    # wh-PRON cleft (§5i Commit 2) only fires when ``WH=true``.
    #
    # **Scope vs Phase 8.S**: this rule closes the simple
    # ``PRON[NOM] + NP[NOM-headed-by-N]`` case (e.g. ``Ako ang
    # guro``). The remaining 8.S residual is the VP-pivot variant
    # where the pivot's ang-NP is a verb-headed nominalization
    # (``Tayo ang lumakad`` = "It's us who walked") and the
    # DAT-PRON possessive-pivot variant (``Akin ang tinapay``
    # = "The bread is mine"). Those need separate analysis and
    # remain in Phase 8.S.
    #
    # **Gating**: ``¬ (↓1 WH)`` excludes wh-PRONs (``sino``,
    # ``ano``, ``alin``) from firing this rule and producing a
    # spurious non-wh parse for wh-cleft sentences.
    #
    # F-structure shape:
    #
    #   PRED        = 'BE-PRON <SUBJ>'
    #   NUM / CLUSV = lifted from the pronoun (string atoms in
    #                 ``data/tgl/pronouns.yaml``; propagate cleanly)
    #   PREDICATIVE = true
    #   SUBJ        = the NOM-NP subject
    #
    # PRON_LEMMA and PERS are NOT lifted: the non-wh PRON entries
    # in ``data/tgl/pronouns.yaml`` do not register LEMMA as a
    # feature, and ``PERS`` is registered as a Python ``int`` which
    # does not currently propagate to f-structure (NUM and CLUSV
    # are strings and do propagate). NUM + CLUSV jointly
    # distinguish 1sg / 2sg / 3sg / 1pl-inclusive / 1pl-exclusive /
    # 2pl / 3pl up to person, which is sufficient for downstream
    # consumers in scope today. A future engineering pass on the
    # integer-feature path would re-enable the PERS lift.
    rules.append(Rule(
        "S",
        ["PRON[CASE=NOM]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-PRON <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ NUM) = ↓1 NUM",
            "(↑ CLUSV) = ↓1 CLUSV",
            "(↑ PREDICATIVE) = true",
            "¬ (↓1 WH)",
        ],
    ))

    # --- Phase 8.S: DAT-PRON possessive-pivot cleft ----------------
    #
    # ``Akin ang tinapay.``    "The bread is mine."
    # ``Akin ang lapis.``      "The pencil is mine."
    # ``Sa akin ang lapis.``   "The pencil is mine." (sa-PP variant)
    # ``Iyo ang aklat.``       "The book is yours."
    # ``Kanila ang bahay.``    "The house is theirs."
    #
    # The Phase 8.X docstring above (line 1005-1012) explicitly
    # named this remaining 8.S residual: the DAT-PRON possessive-
    # pivot variant. Audit corpus surfaces five hits from S&O 1972
    # / R&G Intermediate (page 42 sent-3 ``Akin ang tinapay.``,
    # page 145 sent-169 ``Akin ang lapis.``, page 284 sent-397
    # ``Akin ang relos.``, page 220 sent-1535 ``Akin ang
    # bulaklak.``, page 44 sent-310 ``Akin ang bahay.``).
    #
    # The construction: a bare DAT-PRON (``Akin``, ``Iyo``,
    # ``Kanila``, ...) or sa+DAT-PRON (``Sa akin``, ``Sa iyo``,
    # ...) serves as the possessive predicate; the ang-NP is the
    # NOM-pivot SUBJ (the possessed item). Cited per S&O 1972
    # §4.2 / R&G 1981 §10 (DAT-PRON possessive predication).
    #
    # **Single rule with feat-gating**: both ``Akin`` and ``Sa
    # akin`` wrap as ``NP[CASE=DAT]`` (bare DAT-PRON via
    # standalone-PRON-as-NP, sa-PP via ADP+PRON). The rule fires
    # on ``NP[CASE=DAT]`` with two gates:
    #
    # * ``¬ (↓1 PRED)`` — excludes NOUN-headed DAT-NPs (NOUN
    #   wraps carry ``PRED='NOUN(↑ FORM)'``; PRON wraps don't
    #   define PRED at the NP[DAT] level). This keeps the
    #   locative ``Sa bahay ang lapis.`` reading out — that
    #   construction needs a separate locative-cleft rule.
    # * ``¬ (↓1 WH)`` — excludes wh-DAT-PRON (``kanino``,
    #   ``saan``) — those route through the Phase 5i wh-cleft
    #   rules and would double-parse without this gate.
    #
    # F-structure shape:
    #
    #   PRED        = 'BE-DAT <SUBJ>'
    #   SUBJ        = ↓2 (the ang-NP — the possessed item)
    #   POSSESSOR   = ↓1 (the DAT-NP — bare PRON or sa-PP)
    #   PREDICATIVE = true
    rules.append(Rule(
        "S",
        ["NP[CASE=DAT]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-DAT <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ POSSESSOR) = ↓1",
            "(↑ PREDICATIVE) = true",
            "¬ (↓1 PRED)",
            "¬ (↓1 WH)",
        ],
    ))


    # --- Phase 9.Q: locative cleft (B3.D) -----------------------
    #
    # ``Sa bahay ang lapis.``       "The pencil is at home." (8.S pin)
    # ``Sa kotse ang gulong.``      "The tire is in the car."
    # ``Sa Nanay ang relos.``       "The watch is Mother's." (locative-as-possessive)
    # ``Sa Sabado ang parada.``     "The parade is on Saturday." (temporal)
    # ``Sa harap ng sine ang tindahan.``
    #                               "The store is in front of the cinema."
    # ``Dito ang dating ng tren.``   "The train arrives here."
    #                                  (DEM-locative variant)
    #
    # S&O 1972 §4.2 / R&G 1981 §10.5 locative-existential cleft —
    # a DAT-marked NP (the ground / location) serves as a copular
    # locative predicate; the NOM-pivot is the figure being located.
    # Structurally parallel to the Phase 8.S DAT-PRON possessive
    # cleft above; differs in semantic role (LOC instead of
    # POSSESSOR) and in admitting NOUN-headed / DEM-headed DAT-NPs.
    #
    # F-structure shape:
    #
    #   PRED         = 'BE-LOC <SUBJ>'
    #   SUBJ         = ↓2 (the ang-NP — figure / theme being located)
    #   LOC          = ↓1 (the DAT-NP — ground / location)
    #   PREDICATIVE  = true
    #   CLAUSE_TYPE  = 'LOCATIVE_CLEFT'
    #
    # **Complementary gate to 8.S** (above): 8.S uses ``¬ (↓1 PRED)``
    # to admit only PRON-headed DAT-NPs (`Sa akin`/`Akin`); 9.Q uses
    # ``(↓1 PRED)`` (existence check) to admit only NOUN-headed
    # (``Sa bahay`` carries PRED='NOUN(↑ FORM)') or DEM-headed
    # (``dito`` carries PRED='PRO'). The two rules partition the
    # NP[CASE=DAT] daughter space cleanly — no double-firing.
    #
    # **No conflict with Phase 5i wh-cleft** (`Sa kanino ang aklat?`):
    # ``¬ (↓1 WH)`` blocks wh-DAT-PRON, which routes via the wh-
    # cleft rule with its dedicated wh-specific PRED.
    #
    # **Composition with NEG-wrap**: ``Hindi sa bahay ang lapis.``
    # falls out of the existing ``S → PART[POLARITY=NEG] S`` rule
    # in cfg/negation.py applying to the cleft S.
    #
    # **Distinction from Phase 5j C4 ``nasa`` locative-existential**
    # (clause.py ~2566): ``nasa`` uses a dedicated ``LOC_EXISTENTIAL``
    # particle + bare-N ground (no sa-ADP wrap) and asserts existence
    # (CLAUSE_TYPE=EXISTENTIAL semantically); 9.Q uses ``sa`` ADP +
    # NP and asserts location (CLAUSE_TYPE=LOCATIVE_CLEFT). The two
    # surface forms are near-synonyms in usage (``Nasa bahay ang
    # lapis.`` ↔ ``Sa bahay ang lapis.``) but structurally distinct.
    rules.append(Rule(
        "S",
        ["NP[CASE=DAT]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-LOC <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ LOC) = ↓1",
            "(↑ PREDICATIVE) = true",
            "(↑ CLAUSE_TYPE) = 'LOCATIVE_CLEFT'",
            "(↓1 PRED)",
            "¬ (↓1 WH)",
        ],
    ))


    # --- Phase 9.Q: NEG'd locative cleft + sentence-medial kundi-PP correction ---
    #
    # ``Hindi dito kundi sa bayan ang pulong.``  (8.T pin, S&O 1972
    #     page 656 / sent-1289)
    #     "The meeting is not here but in town."
    #
    # Structural shape:
    #
    #   S → PART[NEG]  NP[CASE=DAT]  PART[COORD=BUT_NOT]
    #         NP[CASE=DAT]  NP[CASE=NOM]
    #
    # where:
    #
    #   - ↓1 ``Hindi``         clausal negation
    #   - ↓2 the negated PP    (``dito`` / ``sa X``) — what's being corrected
    #   - ↓3 ``kundi``         "but instead" — phrasal correction particle
    #   - ↓4 the corrective PP (``sa bayan``) — the actual location
    #   - ↓5 the NOM-pivot     (``ang pulong``) — the figure
    #
    # F-structure shape (locative cleft semantic + correction
    # adjunct):
    #
    #   PRED         = 'BE-LOC <SUBJ>'
    #   SUBJ         = ↓5
    #   LOC          = ↓4                   (the corrective PP — actual location)
    #   POLARITY     = 'NEG'
    #   ADJUNCT      ⊇ {↓2}                 (negated alternative)
    #     ↓2 ROLE    = 'NEG_CORRECTION'
    #   CLAUSE_TYPE  = 'LOCATIVE_CLEFT'
    #
    # **Why a sentence-level 5-daughter rule rather than an NP-DAT
    # wrap**: the kundi-correction is gated on a NEG matrix
    # (per S&O 1972 §7.20 — ``kundi`` requires a negative
    # antecedent). Gating an NP-level wrap on parent-S polarity
    # isn't expressible in LFG-equation form, so an explicit rule
    # at the S level keeps the gate local to ↓1's POLARITY=NEG.
    # The Phase 8.T kundi-NP / kundi-PP correction rules in
    # cfg/coordination.py handle sentence-FINAL corrections
    # (``Walang tao kundi sa bayan.``); this rule handles
    # sentence-MEDIAL corrections inside the locative-cleft scope
    # (``Hindi dito kundi sa bayan ang pulong.``).
    #
    # Mirrors the 9.Q simple locative-cleft rule above for the
    # semantic PRED / GF assignment; adds the NEG-correction
    # adjunct slot following the Phase 8.T phrasal-correction
    # convention (ROLE='NEG_CORRECTION' parallels the Phase 8.T
    # ROLE='CORRECTION' on right-edge kundi).
    rules.append(Rule(
        "S",
        [
            "PART[POLARITY=NEG]",
            "NP[CASE=DAT]",
            "PART[COORD=BUT_NOT]",
            "NP[CASE=DAT]",
            "NP[CASE=NOM]",
        ],
        [
            "(↑ PRED) = 'BE-LOC <SUBJ>'",
            "(↑ SUBJ) = ↓5",
            "(↑ LOC) = ↓4",
            "(↑ POLARITY) = 'NEG'",
            "(↑ PREDICATIVE) = true",
            "(↑ CLAUSE_TYPE) = 'LOCATIVE_CLEFT'",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 ROLE) = 'NEG_CORRECTION'",
            "(↓1 POLARITY) =c 'NEG'",
            "(↓3 COORD) =c 'BUT_NOT'",
            "¬ (↓2 WH)",
            "¬ (↓4 WH)",
        ],
    ))


    # --- Phase 8.Y Commit 1: ay-inverted N-pivot predication ----
    #
    # ``Ito ay aklat.``       "This is a book."
    # ``Ako ay guro.``        "I am a teacher."
    # ``Iyon ay tatay ko.``   "That is my dad."
    #
    # Closes the 8.Y near-miss surfaced during 8.X probing
    # (docs/analysis-choices.md "Phase 8.X" entry). The Phase 5n.B
    # Commit 2 N-pivot rule (``S → N NP[CASE=NOM]``) accepts
    # ``Aklat ito.`` "This is a book" (N-pivot, DEM-subject). The
    # mirror ay-inverted form ``Ito ay aklat.`` topicalizes the
    # DEM subject to sentence-initial position — the same predicat-
    # ional content, different surface order.
    #
    # The Phase 4 §7.4 family of ay-fronting rules covers V-headed
    # clauses (``S → NP[NOM] ay S_GAP``), predicative-ADJ clauses
    # (``S → NP[NOM] ay S_GAP_PREDADJ``), and SubordClause topics
    # (``S → SubordClause ay S``). This rule adds the N-headed
    # predication variant without a parallel ``S_GAP_PREDN`` gap
    # non-terminal — the equation set is small enough that direct
    # construction is simpler than threading a gap clause.
    #
    # F-structure shape (mirrors the N-pivot rule but with SUBJ
    # bound to the fronted ↓1 daughter instead of the right-side
    # ↓2):
    #
    #   PRED        = 'BE-N <SUBJ>'
    #   SUBJ        = ↓1 (the fronted NP — DEM, PRON, or other NOM-NP)
    #   TOPIC       = ↓1 (LFG discourse function for ay-fronting)
    #   N_LEMMA     = the predicate noun's lemma
    #   PREDICATIVE = true
    #
    # The right daughter ``N`` covers bare N, ADJ-modified N
    # (``maliit na bahay``), Q-modified N (``maraming aklat``),
    # and mas-comparative-modified N — same as the Phase 5n.B
    # N-pivot rule's left daughter.
    rules.append(Rule(
        "S",
        ["NP[CASE=NOM]", "PART[LINK=AY]", "N"],
        [
            "(↑ PRED) = 'BE-N <SUBJ>'",
            "(↑ SUBJ) = ↓1",
            "(↑ TOPIC) = ↓1",
            "(↑ N_LEMMA) = ↓3 LEMMA",
            "(↑ PREDICATIVE) = true",
            "¬ (↓3 WH)",
        ],
    ))

    # --- Phase 9.X.c30: SubordClause-topic + ay + N predicate -------
    #
    # ``Kapag naghalo ang dalawa ay malaking hirap.``  "When the
    # two mix together (it) is a big difficulty."
    #                                                  (PANAHON sent-13)
    #
    # Parallel to the Phase 5n.B ``S → NP[CASE=NOM] PART[LINK=AY] N``
    # rule above (ay-fronted predicate-N with NOM-NP topic), but
    # with a SubordClause topic instead of an NP. The SubordClause
    # is the discourse subject of an impersonal N-pred — "when X
    # happens, (it) is N" — and binds to the matrix's SUBJ slot.
    #
    # Mirrors the Phase 4 §7.4 ``S → SubordClause PART[LINK=AY] S``
    # rule (V-headed body) for the N-headed body case. Same logic
    # as the Phase 9.X.c9 SubordClause + ay + main-S composition
    # but with N as the post-ay body daughter.
    #
    # F-structure shape mirrors the NP-topic predicate-N rule
    # above: PRED='BE-N <SUBJ>', SUBJ and TOPIC both bound to the
    # SubordClause topic, N_LEMMA from the predicate noun,
    # PREDICATIVE=true. No WH gate (SubordClauses don't carry WH).
    rules.append(Rule(
        "S",
        ["SubordClause", "PART[LINK=AY]", "N"],
        [
            "(↑ PRED) = 'BE-N <SUBJ>'",
            "(↑ SUBJ) = ↓1",
            "(↑ TOPIC) = ↓1",
            "(↑ N_LEMMA) = ↓3 LEMMA",
            "(↑ PREDICATIVE) = true",
        ],
    ))

    # --- Phase 9.X.c32: psych-pred ADJ + experiencer + CP complement ----
    #
    # ``Tiwala ang mga magsasaka na hindi masasalanta ang kanilang
    # palay.``  "The farmers trust that their rice won't be
    # destroyed."  (PANAHON sent-38)
    #
    # Tagalog bare-root psychological-state ADJs (``tiwala``
    # "confident", and parallel forms ``galit`` "angry", ``tuwa``
    # "glad", ``takot`` "afraid") can take an experiencer NP[NOM]
    # plus a complement clause introduced by the linker
    # (``-ng`` after vowel-final hosts; ``na`` after consonant-
    # final hosts). Same structural shape as the Phase 5i C8 /
    # 5n.B C11 ``V[CTRL_CLASS=KNOW] + GEN-NP + LINK + S_DECL_COMP``
    # rule (cfg/control.py) but with an ADJ-pred head and an
    # NP[NOM] experiencer instead of a GEN-NP experiencer.
    #
    # Gated on the matrix ADJ's LEMMA (``tiwala`` to start; broaden
    # to a per-feat ``PSYCH_PRED`` gate when audit shows more
    # psych-ADJs joining this construction). The narrow lemma gate
    # prevents the rule from accidentally firing on attributive
    # ADJ-modifiers — ``maganda ang aklat na pula`` continues to
    # parse via the existing N+linker+ADJ modifier path, not via
    # this new ADJ + NP + linker + CP rule.
    #
    # F-structure shape mirrors the V[KNOW] rule: matrix's SUBJ
    # bound to the experiencer NP, matrix's COMP bound to the CP.
    # PRED is the ADJ's standard one-place template
    # ``'ADJ <SUBJ>'`` (Phase 5g convention) with the COMP riding
    # as an auxiliary attribute.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            [
                "ADJ[PREDICATIVE]",
                "NP[CASE=NOM]",
                f"PART[LINK={link}]",
                "S_DECL_COMP",
            ],
            [
                "(↑) = ↓1",
                "(↑ SUBJ) = ↓2",
                "(↑ COMP) = ↓4",
                "(↓1 LEMMA) =c 'tiwala'",
                f"(↓3 LINK) =c '{link}'",
                "(↓4 COMP_TYPE) =c 'DECLARATIVE'",
            ],
        ))

    # --- Phase 9.V.4: ay-fronted predicate-N with GEN-NP complement ----
    #
    # ``Si Juan ay bahagi ng pamilya.``  "Juan is part of the family."
    # ``Ang isang Pilipino ay bahagi ng kanyang pamilya.``
    #     "A Filipino is part of his family."
    #     (R&C 1990 ANG PAMILYA sent-1 matrix — 9.U Cluster B audit
    #      hit; the ay-fronted variant of the existing predicate-N
    #      `Bahagi siya ng pamilya.` "He is part of the family." that
    #      already parses.)
    #
    # Companion to the predicate-N rule above (bare ``N`` daughter);
    # this rule admits a trailing GEN-NP that serves as the
    # possessor / specifier of the predicate noun (``bahagi ng X``
    # "part of X", ``doktor ng nayon`` "doctor of the village",
    # etc.). The GEN-NP attaches inside the predicate's f-structure
    # as ``PRED-NP-POSS`` (parallel to the standalone predicate-N's
    # possessor binding in non-ay-fronted clauses).
    #
    # F-structure shape mirrors the bare predicate-N rule plus:
    #
    #   PRED-NP-POSS  = ↓4  (the GEN-NP possessor of the predicate
    #                        noun, accessible to consumers that
    #                        need the possessor's identity)
    rules.append(Rule(
        "S",
        ["NP[CASE=NOM]", "PART[LINK=AY]", "N", "NP[CASE=GEN]"],
        [
            "(↑ PRED) = 'BE-N <SUBJ>'",
            "(↑ SUBJ) = ↓1",
            "(↑ TOPIC) = ↓1",
            "(↑ N_LEMMA) = ↓3 LEMMA",
            "(↑ PRED-NP-POSS) = ↓4",
            "(↑ PREDICATIVE) = true",
            "¬ (↓3 WH)",
        ],
    ))


    # --- Phase 8.Y Commit 2 / Phase 8.Z: NP-pivot two-NP equational -----
    #
    # ``Si Juan ito.``           "This is Juan."
    # ``Si Maria iyan.``         "That is Maria."
    # ``Si Juan ang doktor.``    "Juan is the doctor."
    # ``Ang lalaki ang doktor.`` "The man is the doctor."  (Phase 8.Z)
    # ``Ang nanay ang nagluto.`` "The mother is the one who cooked."
    #                             (pseudo-cleft equational; Phase 8.Z)
    #
    # The Phase 5n.B N-pivot rule's docstring originally deferred
    # two-NP equational ("Those remain as out-of-scope until corpus
    # pressure surfaces them"). 8.Y closed the Si-pivot subset
    # after the Wave 3 audit surfaced ``Si Juan ito.``. 8.Z (this
    # commit) drops the SI gate: the user verified ``Ang lalaki
    # ang doktor.`` as the natural reading ("The man is the
    # doctor."), so the fully-general two-NP equational case is
    # closed here too.
    #
    # **Original concern about pseudo-cleft ambiguity, resolved**:
    # Phase 8.Y's first draft kept the SI gate citing potential
    # ambiguity with pseudo-cleft (``Ang nanay ang nagluto.``).
    # Diagnostic probing for 8.Z confirmed pseudo-cleft was itself
    # zero-parsing under the pre-existing grammar — so the gate
    # was preventing closure of one construction class without
    # benefit to another. The 8.Z rule subsumes both: when the
    # right-side NP is a headless RC (``ang nagluto``), the same
    # equational f-structure obtains, and the topicalization /
    # focus distinction between pseudo-cleft and equational
    # readings is information-structural rather than truth-
    # conditional in Tagalog (S&O 1972 §6.2 / Kroeger 1993 §2.5).
    #
    # F-structure shape:
    #
    #   PRED        = 'BE-NP <SUBJ>'
    #   SUBJ        = ↓2 (the right-side NOM-NP subject)
    #   PRED-NP     = ↓1 (the predicate NP, preserved as a sub-
    #                  fstructure for consumers that need the
    #                  pivot's identity / lemma / MARKER)
    #   PREDICATIVE = true
    rules.append(Rule(
        "S",
        ["NP[CASE=NOM]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'BE-NP <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ PRED-NP) = ↓1",
            "(↑ PREDICATIVE) = true",
            # Gate on the pivot — keep wh-PRONs (``Sino`` /
            # ``Ano`` / ``Alin``) routing through the Phase 5i
            # Commit 2 wh-PRON cleft (``S → PRON[WH, CASE=NOM]
            # NP[CASE=NOM]``) as the canonical wh path; otherwise
            # ``Sino ang kumain?`` would get a spurious BE-NP
            # parse in addition to the wh-cleft parse.
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
            "(↑ INTENS) = ↓1 INTENS",
            "(↑ DISTRIB) = ↓1 DISTRIB",
            "(↑ KASING_N) = ↓1 KASING_N",
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
            "(↑ INTENS) = ↓1 INTENS",
            "(↑ DISTRIB) = ↓1 DISTRIB",
            "(↑ KASING_N) = ↓1 KASING_N",
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
            "(↑ INTENS) = ↓1 INTENS",
            "(↑ DISTRIB) = ↓1 DISTRIB",
            "(↑ KASING_N) = ↓1 KASING_N",
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
            "(↑ INTENS) = ↓1 INTENS",
            "(↑ DISTRIB) = ↓1 DISTRIB",
            "(↑ KASING_N) = ↓1 KASING_N",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 ROLE) = 'EQUATIVE_STANDARD'",
        ],
    ))

    # --- Phase 8.L Commit 4: subject-pro-drop equative + GEN-standard ----
    #
    # ``Kasing-edad pala ni Nadette.``
    #     "(She's) the same age, no less, as Nadette."
    #     (Wave 2/3 audit hit — R&G Intermediate page 238)
    # ``Kasingganda ni Maria.``
    #     "(Someone is) as beautiful as Maria."
    #
    # Tagalog routinely drops the NOM subject when contextually
    # clear; the equative + GEN-standard frame admits this directly.
    # The PRED still takes ``<SUBJ>`` (so LMT's PRED-arg accounting
    # is satisfied) but SUBJ is realized as a synthesised ``PRED:
    # 'PRO'`` matching the convention used by ``cfg/extraction.py``
    # free-relative wrap (Phase 6.E) and ``cfg/nominal.py`` for
    # standalone-DEM (Phase 5n.B.6).
    #
    # The rule mirrors the GEN-standard equative rule above with
    # SUBJ pro-dropped. It carries the same ``INTENS / DISTRIB /
    # KASING_N`` lifts so the NOUN-base ``kasing_n_eq`` cell (Phase
    # 8.L Commit 3) surfaces the equative-attribute construction
    # correctly. The audit-canonical surface is the hyphen-joined
    # ``Kasing-edad`` (handled by the left-flanker carve-out in
    # ``split_linker_ng`` — Phase 8.L Commit 4 multiword fix).
    rules.append(Rule(
        "S",
        [
            "ADJ[COMP_DEGREE=EQUATIVE]",
            "NP[CASE=GEN]",
        ],
        [
            "(↑ PRED) = 'ADJ <SUBJ>'",
            "(↑ SUBJ PRED) = 'PRO'",
            "(↑ ADJ_LEMMA) = ↓1 LEMMA",
            "(↑ PREDICATIVE) = true",
            "(↓1 PREDICATIVE) =c true",
            "(↓1 COMP_DEGREE) =c 'EQUATIVE'",
            "(↑ INTENS) = ↓1 INTENS",
            "(↑ DISTRIB) = ↓1 DISTRIB",
            "(↑ KASING_N) = ↓1 KASING_N",
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


    # --- Phase 9.X.c40: deictic LOC_EXISTENTIAL pre-V modifier ----
    #
    # ``Ang natitirang limang buwan ay naroong maghati sa init at ulan.``
    #     "The remaining five months share between heat and rain."
    #                                              (PANAHON sent-3)
    #
    # The deictic locative-existentials (``narito`` / ``naroon`` /
    # ``nariyan``) can compose with a following linker + V to add
    # locative-existential meaning to the matrix verb — the same
    # "be-there V-ing" pattern that English uses with
    # "there + V-ing".
    #
    # Parallel to the c39 FREQ-ADV pre-V rule: matrix S inherits
    # the inner clause's f-structure (PRED, SUBJ, ASPECT) via
    # ``(↑) = ↓3``, and the LOC_EXISTENTIAL PART joins ADJ as a
    # locative modifier. The DEIXIS check narrows this to the
    # deictic forms (not ``nasa``).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            ["PART[LOC_EXISTENTIAL]", f"PART[LINK={link}]", "S"],
            [
                "(↑) = ↓3",
                "↓1 ∈ (↑ ADJ)",
                "(↓1 LOC_EXISTENTIAL) =c true",
                "(↓1 DEIXIS)",
            ],
        ))


    # --- Phase 9.X.c39: FREQUENCY-ADV pre-V modifier --------------
    #
    # ``Ang silangang Pilipinas ay laging dinadalaw ng mga bagyo.``
    #     "The eastern Philippines is often visited by storms."
    #                                              (PANAHON sent-35)
    #
    # Parallel to the Phase 5g manner-ADJ rule above, but with a
    # FREQUENCY-class ADV (``lagi`` / ``palagi`` / ``madalas`` etc.)
    # in modifier position. The clause-final FREQUENCY AdvP rule
    # (Phase 5f Commit 5) covers post-V placement; this rule covers
    # pre-V (clause-medial-with-linker) placement.
    #
    # ``ADV`` is the analyzer's category for FREQUENCY-class roots
    # like ``lagi`` and ``madalas`` (despite their YAML ``pos: PART``,
    # the analyzer reclassifies them as ADV via the ADV_TYPE feat;
    # see ``morph/analyzer.py``). The corresponding ADJ-headed
    # adverbial use (``karaniwang masarap ...``) already composes
    # via the line-2240 ADJ + linker + S rule because ``karaniwan``
    # is lexed as ADJ.
    #
    # The ADV joins the matrix S's ADJ set; the matrix inherits the
    # inner S's f-structure (PRED, SUBJ, ASPECT, etc.) via
    # ``(↑) = ↓3``. ``(↓1 ADV_TYPE) =c 'FREQUENCY'`` keeps non-
    # frequency ADVs (TIME, MANNER, LOCATION — handled by other
    # clause-final rules) out of this slot.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S",
            ["ADV", f"PART[LINK={link}]", "S"],
            [
                "(↑) = ↓3",
                "↓1 ∈ (↑ ADJ)",
                "(↓1 ADV_TYPE) =c 'FREQUENCY'",
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

    # Phase 7a.D: wh-ADV with linker fronting (§18.1.1 item 5).
    #
    # `Paanong kumain ang aso?` "How would the dog eat?" — wh-ADV
    # + linker (na / -ng) + S. The plan-of-record §3.4 calls out
    # `paano` specifically, but the rule's structure is generic
    # over ADV[WH] — the Phase 5i Commit 4 bare variant above is
    # also generic, and modern Tagalog permits the linker-bound
    # form across all wh-ADVs (paano / papaano / saan / kailan /
    # bakit). The linker variant adds emphasis or interrogative
    # particle force to the wh-fronting.
    #
    # Equations mirror the bare variant exactly except daughter
    # indices shift by one (S is ↓3 vs ↓2). No new feats are
    # introduced: Q_TYPE=WH + WH_LEMMA identifies the question
    # type; downstream consumers dispatch on WH_LEMMA when they
    # need to distinguish manner / place / time / reason questions.
    # The plan's `(↑ ASK_MANNER) = true` equation is dropped (no
    # parallel ASK_* feats exist for the other wh-types; adding
    # one paano-specific atom would be inconsistent with the
    # established convention).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "S[Q_TYPE=WH]",
            ["ADV[WH]", f"PART[LINK={link}]", "S"],
            [
                "(↑) = ↓3",
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

    # === Phase 8.R-class follow-on (8.F): V-headed existential =========
    #
    # ``May binalak siya.``               "He had a plan."
    # ``May nakita siya.``                "He saw something."
    # ``May naisip ang mama.``            "Mom thought of something."
    # ``May gagawin ako sa Sabado.``      "I have something to do on Saturday."
    # ``May ginagawa si Jose.``           "Jose has something he's doing."
    #
    # Tagalog `may` admits a V-headed nominalized complement in
    # addition to the bare-N variant above. Semantics: the V denotes
    # a thing (result of action, plan, thought, etc.) that the NOM-
    # pivot possesses. The closest English gloss is "X has a Y"
    # where Y is the V-as-nominalization. See R&C 1990 / R&G
    # Conversational corpus; 8 of 11 corpus candidates close via
    # this rule (Wave 2 + Wave 3 audit).
    #
    # Rule (a): possessive shape `may + V + NOM-pivot`
    # The NOM-NP/NOM-PRON is the possessor of the V's nominalized
    # form (the result / patient / action denoted by the V used as
    # a deverbal noun). Avoid lifting the V's f-structure directly
    # into matrix SUBJ — the V carries a transitive PRED template
    # (e.g., `BALAK <SUBJ, OBJ>`) whose argument slots aren't
    # realized in this construction (the V is functioning as a
    # noun). Capture only the V's LEMMA and the voice/aspect
    # signature, and mark SUBJ as NOMINALIZED.
    for voice in ("AV", "OV", "RV", "LF", "DV", "IV", "BV"):
        rules.append(Rule(
            "S",
            [
                "PART[EXISTENTIAL, POLARITY=POS]",
                f"V[VOICE={voice}]",
                "NP[CASE=NOM]",
            ],
            [
                "(↑ PRED) = 'EXIST <SUBJ>'",
                "(↑ SUBJ NOMINALIZED) = true",
                "(↑ SUBJ V_VOICE) = ↓2 VOICE",
                "(↑ SUBJ V_ASPECT) = ↓2 ASPECT",
                "(↑ SUBJ V_PRED) = ↓2 PRED",
                "(↑ SUBJ POSSESSOR) = ↓3",
                "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
                "(↑ POLARITY) = 'POS'",
                "(↑ HAVE) = true",
                "(↓1 EXISTENTIAL) =c true",
                "(↓1 POLARITY) =c 'POS'",
            ],
        ))

    # Rule (b): agentive shape `may + V[AV] + GEN-NP`
    #
    # ``May nagdala ng kape.``     "Someone brought coffee."
    # ``May nagdala ng magagandang banig.``  (R&G Conv)
    #
    # The V is AV (the existence-asserted entity is the agent /
    # actor); the GEN-NP is the V's OBJ. Headless-RC reading:
    # "there is someone-who-brought coffee". The empty SUBJ slot of
    # the V is the existence-asserted entity.
    rules.append(Rule(
        "S",
        [
            "PART[EXISTENTIAL, POLARITY=POS]",
            "V[VOICE=AV]",
            "NP[CASE=GEN]",
        ],
        [
            "(↑ PRED) = 'EXIST <SUBJ>'",
            "(↑ SUBJ NOMINALIZED) = true",
            "(↑ SUBJ V_VOICE) = ↓2 VOICE",
            "(↑ SUBJ V_ASPECT) = ↓2 ASPECT",
            "(↑ SUBJ V_PRED) = ↓2 PRED",
            "(↑ SUBJ OBJ) = ↓3",
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

    # --- Phase 9.X.c22: bare elliptical wala (no SUBJ) ----------
    #
    # ``Wala.``                "There is none. / Not."
    # ``Wala pa.``             "Not yet. / Still none."
    #                          (PANAHON sent-5 inner clause)
    # ``Kung minsan ay wala pa.``  "Sometimes there's still none."
    #
    # The Phase 5j Commit 3 wala rules above require an N or PRON
    # daughter to fill SUBJ; an "edge case" exception was promised
    # in the C3 docstring but never implemented. This rule closes
    # that gap: a bare ``wala`` (optionally followed by a 2P
    # clitic via the existing Phase 4 clitic absorption) is itself
    # a complete clause with elliptical / contextually-recoverable
    # subject. The 2P-clitic absorption rule
    # (cfg/clitic.py: ``S → S PART[CLITIC_CLASS=2P]``) supplies
    # the ``pa`` ASPECT_TYPE=NOT_YET adjunct.
    #
    # F-structure: zero-arity PRED (``EXIST <>``) since there is
    # no overt SUBJ in this surface. CLAUSE_TYPE='EXISTENTIAL'
    # and POLARITY='NEG' carry through to satisfy any downstream
    # consumers that gate on existential / negative-existential
    # clause type. The ELLIPSIS feat is diagnostic-only and marks
    # the elliptical nature for downstream consumers.
    rules.append(Rule(
        "S",
        ["PART[EXISTENTIAL, POLARITY=NEG]"],
        [
            "(↑ PRED) = 'EXIST <>'",
            "(↑ CLAUSE_TYPE) = 'EXISTENTIAL'",
            "(↑ POLARITY) = 'NEG'",
            "(↑ ELLIPSIS) = true",
            "(↓1 EXISTENTIAL) =c true",
            "(↓1 POLARITY) =c 'NEG'",
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

    # --- Phase 9.X.c27: deictic LOC_EXISTENTIAL (no N daughter) -----
    #
    # ``Narito ang bata.``   "The child is here."
    # ``Naroon ang aklat.``  "The book is there (away from us)."
    # ``Nariyan si Maria.``  "Maria is there (near you)."
    #
    # The Phase 5j Commit 4 rules above require an N daughter for
    # the locative ground (``nasa labas``, ``nasa tuktok ng
    # bundok``). The deictic locative-existentials
    # ``narito`` / ``naroon`` / ``nariyan`` are inherently
    # complete — the deixis (PROX / DIST / MED) embeds the
    # location semantically, so no N daughter is needed. The lex
    # entries (particles.yaml) carry ``DEIXIS=PROX|DIST|MED``
    # alongside ``LOC_EXISTENTIAL=true``; the DEIXIS existential
    # constraint on ↓1 narrows this rule to the deictic forms,
    # preventing it from accidentally firing on ``nasa`` (which
    # has LOC_EXISTENTIAL but no DEIXIS).
    #
    # F-structure: same shape as the canonical nasa-rules above
    # but with the LOC_EXISTENTIAL PART itself acting as the
    # LOCATION (no separate N ground). The DEIXIS feat rides on
    # the matrix LOCATION for downstream semantic consumption.
    rules.append(Rule(
        "S",
        ["PART[LOC_EXISTENTIAL]", "NP[CASE=NOM]"],
        [
            "(↑ PRED) = 'LOC <SUBJ>'",
            "(↑ SUBJ) = ↓2",
            "(↑ LOCATION) = ↓1",
            "(↑ CLAUSE_TYPE) = 'LOC_EXISTENTIAL'",
            "(↓1 LOC_EXISTENTIAL) =c true",
            "(↓1 DEIXIS)",
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


    # === Phase 8.D: comma-fronted topic NP =============================
    #
    # ``S → NP PUNCT[COMMA] S``
    #
    # General topic-fronting of an NP by sentence-initial comma,
    # parallel to the Phase 5l Commit 13 ay-fronted SubordClause topic
    # (``cfg/subordination.py``) and the Phase 4 §7.4 ay-fronted NP
    # rule. The fronted NP serves as both matrix TOPIC (discourse
    # function) and a member of ADJUNCT (grammatical function for the
    # temporal / setting / contrastive interpretation).
    #
    # Example (Wave 1 audit target — rg81 ANG MANOK ch.):
    #
    #   ``Isang araw, nagbubunot siya ng damo.``
    #   "One day, he was pulling weeds."
    #
    # F-structure shape:
    #
    #   ↑          = ↓3                  matrix = the post-comma S
    #   ↑ TOPIC    = ↓1                  fronted NP is discourse topic
    #   ↓1 ∈ ↑ ADJUNCT                   also in adjunct set
    #
    # The fronted NP daughter is unconstrained for CASE — the
    # construction admits bare NPs (``Isang araw``, ``Kahapon``,
    # ``Bukas``), case-marked NPs in some registers, and DP-headed
    # constituents (``Sa simula``). The interpretation is uniformly
    # temporal-/setting-frame "TOPIC".
    #
    # Disambiguation from Phase 5n.C Commit 6 / 7.6 universal-Q
    # distributive (``Bawat bata, kumain.``): that family's right
    # daughter is a bare ``V[VOICE=AV]`` (with optional GEN/DAT-NP
    # daughters), whereas this rule's right daughter is a full S
    # already covering matrix structure. Distinct daughter shape →
    # no structural overlap; both rules can coexist without
    # ambiguity-induced spurious parses for the canonical inputs
    # of each.
    #
    # Disambiguation from Phase 4 §7.4 ay-fronted NP: ay-fronting
    # uses an overt ``PART[LINK=AY]`` particle between fronted NP
    # and matrix; comma-fronting uses PUNCT[COMMA]. Different
    # surface tokens → no overlap.
    #
    # References: Schachter & Otanes 1972 §13 (topicalization);
    # Kroeger 1993 ch.2 (Tagalog topic-comment structure);
    # Phase 5l Commit 13 sibling rule (subord-clause topicalization).
    rules.append(Rule(
        "S",
        ["NP", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))

    # Companion variant for bare-N topics (no case marker). The
    # Phase 5f Commit 1 cardinal-NP rule requires a CASE marker
    # daughter to build NP[CASE=X]; bare cardinal-modified N
    # (``Isang araw`` "one day") thus surfaces as ``N``, not ``NP``.
    # The audit-target sentence ``Isang araw, nagbubunot siya ng
    # damo.`` (rg81 ANG MANOK) uses exactly this shape — temporal-
    # frame topic-N without case marking. This companion rule
    # admits the N-shaped daughter; equations are identical to the
    # NP-variant above.
    rules.append(Rule(
        "S",
        ["N", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))


    # === Phase 8.D2: comma-fronted topic siblings ======================
    #
    # In-Phase-8 anti-deferral follow-on to 8.D. The 8.D
    # ``TestPhase8dOutOfScope`` block pinned three sibling
    # construction-class gaps surfaced during 8.D probing
    # (``Bukas, kumain siya.``, ``Sa simula, ...``,
    # ``Oo, kumain siya.``). 8.D2 closes them as scheduled in the
    # plan-of-record `.claude/plans/tgllfg-phase-8.md` §1 ledger.
    #
    # Discovery during 8.D2 probing: the PP-fronted case
    # (``Sa simula, ...``) was NOT a structural gap — the 8.D
    # NP-variant rule already admits ``NP[CASE=DAT]`` (which is what
    # ``sa simula`` builds as). The only blocker was the OOV noun
    # ``simula``. The pin in 8.D was based on a wrong premise
    # (probing with an OOV noun gives 0 parses even when the
    # construction works); 8.D2 closes it via lex addition only,
    # plus flipping the negative pin to a positive assertion.
    #
    # The remaining two pins (ADV-fronted, PART-fronted) ARE
    # structural gaps and need new rules.

    # --- Phase 9.V.3: sentence-initial FREQUENCY AdvP + clitic SUBJ ---
    #
    # ``Palagi akong nagdadala ng regalo.``
    #     "I always bring a gift."
    #     (R&C 1990 Ch5 sent-767 matrix — 9.U Cluster B audit hit)
    # ``Palagi akong umaalis.``       "I always leave."
    # ``Madalas akong kumain.``       "I often eat."
    # ``Lagi akong nagdadala ...``    same shape as palagi.
    #
    # Mirrors the Phase 5j Commit 7 modal-control wrap shape:
    #
    #   S → V[CTRL_CLASS=MODAL] NP[CASE=NOM] PART[LINK=NG] S_XCOMP
    #
    # with FREQUENCY AdvP at the matrix head instead of a modal V.
    # The clitic NOM-PRON SUBJ sits in Wackernagel 2P after the
    # AdvP, with the ``-ng`` ligature from ``akong`` / ``kong``
    # stripped to a standalone PART[LINK=NG] daughter (Phase 5k C1
    # split_linker_ng pre-pass).
    #
    # The matrix S inherits PRED / VOICE / ASPECT / MOOD / LEX-
    # ASTRUCT from the V daughter (↓4); the AdvP joins ADJUNCT;
    # the SUBJ binds to the clitic NOM-PRON at ↓2. Unlike the
    # modal-control wrap there is no XCOMP — the FREQ-ADV is a
    # simple sentential adjunct.
    #
    # Two arities: V[AV] alone (intransitive) or V[AV] + NP[GEN]
    # (transitive with GEN-OBJ). Both gated by ``(↓3 LINK) =c 'NG'``
    # to match only the ligature variant and not random PART
    # daughters. The FREQUENCY gate on ↓1 keeps the rule narrowly
    # applied to the palagi / madalas / lagi family — other ADV
    # types (TIME / MANNER / etc.) have separate placement rules.
    rules.append(Rule(
        "S",
        [
            "ADV[ADV_TYPE=FREQUENCY]",
            "NP[CASE=NOM]",
            "PART[LINK=NG]",
            "V[VOICE=AV]",
        ],
        [
            "(↑ PRED) = ↓4 PRED",
            "(↑ VOICE) = ↓4 VOICE",
            "(↑ ASPECT) = ↓4 ASPECT",
            "(↑ MOOD) = ↓4 MOOD",
            "(↑ LEX-ASTRUCT) = ↓4 LEX-ASTRUCT",
            "(↑ SUBJ) = ↓2",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↓3 LINK) =c 'NG'",
        ],
    ))
    rules.append(Rule(
        "S",
        [
            "ADV[ADV_TYPE=FREQUENCY]",
            "NP[CASE=NOM]",
            "PART[LINK=NG]",
            "V[VOICE=AV]",
            "NP[CASE=GEN]",
        ],
        [
            "(↑ PRED) = ↓4 PRED",
            "(↑ VOICE) = ↓4 VOICE",
            "(↑ ASPECT) = ↓4 ASPECT",
            "(↑ MOOD) = ↓4 MOOD",
            "(↑ LEX-ASTRUCT) = ↓4 LEX-ASTRUCT",
            "(↑ SUBJ) = ↓2",
            "(↑ OBJ) = ↓5",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↓3 LINK) =c 'NG'",
        ],
    ))


    # --- 8.D2 ADV-variant: ``S → AdvP PUNCT[COMMA] S`` ----------------
    #
    # Closes ``Bukas, kumain siya.`` ("Tomorrow, he ate.") where
    # ``bukas`` is registered as ADV-only in particles.yaml
    # (ADV_TYPE=TIME, DEIXIS_TIME=FUT). The N-variant doesn't fire
    # (no NOUN entry for ``bukas``) so the AdvP-variant is needed.
    # ``kahapon`` "yesterday" works in 8.D via its dual NOUN+ADV
    # registration; this rule additionally admits the ADV-only
    # forms.
    #
    # The AdvP non-terminal already exists in ``cfg/extraction.py``
    # as ``AdvP → ADV`` (Phase 4 ay-AdvP-fronting infrastructure);
    # 8.D2 reuses it as the first daughter of the comma variant.
    # Equation set is identical to the 8.D NP/N variants.
    rules.append(Rule(
        "S",
        ["AdvP", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))

    # --- 8.D2 PART-variant: ``S → PART[INTERJ=true] PUNCT[COMMA] S`` --
    #
    # Closes discourse-particle-fronted topics like
    # ``Oo, kumain siya.`` ("Yes, he ate.") /
    # ``Eto, kumain siya.`` ("Here [it is], he ate.") /
    # ``Opo, kumain siya.`` (polite-affirmation variant of ``Oo``).
    # The fronted PART is an affirmation / negation / deictic
    # interjection occupying its own intonation phrase (signalled
    # by the comma).
    #
    # The Phase 5m Commit 4 sentence-initial PART rule
    # (``cfg/discourse.py`` line 224) handles connectives like
    # ``samakatuwid`` and modal particles like ``siguro`` — those
    # are gated by ``DISCOURSE_POS=SENTENCE_INITIAL`` and have NO
    # comma daughter. The 8.D2 interjection-comma variant is
    # structurally distinct (separate intonation, comma daughter)
    # and gated by ``INTERJ=true`` so it fires only on the
    # affirmation / negation / deictic interjections registered
    # with that feat (8.D2 lex addition: ``oo`` / ``eto`` /
    # ``opo``).
    rules.append(Rule(
        "S",
        ["PART", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↓1 INTERJ) =c true",
        ],
    ))
