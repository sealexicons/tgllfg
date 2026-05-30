# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/cfg/discourse.py

"""Discourse-level adjuncts: clause-final ADJUNCT (PP, AdvP, etc.).

Holds the rules that admit clause-final discourse-level adjuncts —
phrases that attach to a fully formed S as members of its
``ADJUNCT`` set rather than participating in the verb's argument
frame. After the post-Phase-5f grammar split (see
``docs/refactor-grammar-package.md``) this module owns:

* Phase 5f Commit 13 temporal-frame PP — clause-level
  ``noong`` / ``tuwing`` PPs that establish a temporal frame
  (``Tumakbo si Juan tuwing Lunes``, "Juan ran every Monday").
* Phase 5f Commit 5 clause-final FREQUENCY AdvP — adverbial
  phrases of frequency (``palagi``, ``minsan``, ``madalas``)
  attached as a clause-final ADJUNCT.

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
last, after np / clause / clitic / negation / extraction / control
— see the plan's "Migration strategy" §H. The discourse module is
the natural home for future clause-final ADJUNCT constructions
(modal particles, vocatives, etc.).
"""

from .grammar import Rule


# Phase 10.I: per-span emission budget for the recursive ``S → S PP``
# adjunct-attachment rules below. The five rules (TIME_FRAME / EXCEPTIVE /
# BENEFICIARY / TOPIC / GOAL) share the ``S → S PP`` c-structure and are
# the dominant forest-density driver: on ANG MANOK sent-29
# (``Pinakain niya ang manok ng isang tasang palay.``) one span emits
# 1736 alternative subtrees, burying the lone valid V[CAUS=DIRECT] 4-arg
# parse at forest position #8684 — past the default
# ``max_tree_iterations=5000`` cap, so it was a 0-parse. The canonical
# parse attaches ``ng isang tasang palay`` as the verb's GEN-theme
# argument, NOT via ``S → S PP``, so capping this rule's per-span fan-out
# prunes the junk without touching the canonical reading: the budget
# pulls sent-29's parse to #1004 (forest 10206 → 2526), closing it within
# the existing 5000 cap with no global-cap raise. 200 is far above any
# legitimate per-span PP-adjunct ambiguity in real text, so cheap
# sentences are unaffected. See docs/diagnostics.md §6.2.
_SS_PP_BUDGET = 200


def register_rules(rules: list[Rule]) -> None:
    """Append the discourse-area rules in source order."""
    # --- Phase 5f Commit 13: temporal-frame PP (Group F item 5)
    #
    # ``tuwing Lunes`` "every Monday", ``noong Pebrero`` "in
    # February", ``noong umaga`` "this morning". The temporal-
    # frame PARTs (``tuwing`` / ``noong``) introduce a bare-N
    # complement (no DAT marker, unlike standard PPs).
    #
    # F-structure:
    #   PP[TIME_FRAME=PERIODIC|PAST, OBJ={N}]
    #
    # The PP shares with PART (``(↑) = ↓1``), pulling
    # TIME_FRAME up to the matrix PP. The N becomes OBJ.
    #
    # Four SEM_CLASS variants (DAY / TIME / MONTH / SEASON)
    # gate the rule to genuinely temporal NOUNs only —
    # ``*tuwing bata`` ("every child"?) doesn't compose because
    # ``bata`` has no SEM_CLASS. The constraining equations
    # ``(↓1 TIME_FRAME)`` (existential — PART has TIME_FRAME)
    # and ``(↓2 SEM_CLASS) =c '<X>'`` enforce both. The SEASON
    # variant was added in Phase 5f Commit 14 (Group G) to cover
    # ``tuwing tagulan`` "every rainy season" and ``noong
    # taginit`` "during the dry season".
    for sem_class in ("DAY", "TIME", "MONTH", "SEASON"):
        rules.append(Rule(
            "PP",
            ["PART", "N"],
            [
                "(↑) = ↓1",
                "(↑ OBJ) = ↓2",
                "(↓1 TIME_FRAME)",
                f"(↓2 SEM_CLASS) =c '{sem_class}'",
            ],
        ))

    # --- Phase 5f closing deferral: year expression PP -----------
    #
    # ``noong 1990`` "in 1990", ``tuwing 2026`` "every 2026" — a
    # temporal-frame PART followed by a digit-form NUM. Parallels
    # the four SEM_CLASS variants above but admits a NUM in place
    # of N. The constraining equation ``(↓2 DIGIT_FORM) =c true``
    # restricts to digit-form numerics (a word-form numeric like
    # ``noong sandaan-siyamnapung`` "in 190" is theoretically
    # parseable but isn't the natural register and isn't exercised
    # by the seed corpus). The CARDINAL_VALUE lifts to ``YEAR`` on
    # the matrix PP. (Phase 5f closing deferral, 2026-05-04.)
    rules.append(Rule(
        "PP",
        ["PART", "NUM[CARDINAL]"],
        [
            "(↑) = ↓1",
            "(↑ YEAR) = ↓2 CARDINAL_VALUE",
            "(↓1 TIME_FRAME)",
            "(↓2 DIGIT_FORM) =c true",
        ],
    ))

    # Clause-final temporal-frame PP attachment:
    # ``Pumunta ako tuwing Lunes.`` "I went every Monday."
    # ``Pumunta kami noong Pebrero.`` "We went in February."
    #
    # Closes part of the Phase 5e Commit 3 deferral on bare PP
    # placement — scoped to TIME_FRAME PPs only via the
    # existential constraint ``(↓2 TIME_FRAME)``. The
    # ``para sa X`` / ``tungkol sa X`` / ``mula sa X`` /
    # ``dahil sa X`` PPs (Phase 5e Commit 3 PREP entries) don't
    # have TIME_FRAME, so this rule doesn't fire on them — they
    # remain restricted to ay-fronting position. (Same scoped-
    # lift pattern as Phase 5f Commit 5's
    # ``S → S AdvP[FREQUENCY]``.)
    rules.append(Rule(
        "S",
        ["S", "PP"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 TIME_FRAME)",
        ],
        budget=_SS_PP_BUDGET,
    ))

    # --- Phase 9.X.c51: clause-final bare time-N adjunct ---
    #
    # ``Natutulog ang mga tao pagkapananghalian.``
    #     "People sleep after-lunch (= in the early afternoon)."
    # ``Natutulog ako umaga.``    "I sleep mornings."
    # ``Natutulog ang mga tao pagkapananghalian hanggang ikatlo o
    #   ikaapat ng hapon.``   (PANAHON sent-14)
    #
    # Tagalog admits bare N[SEM_CLASS=TIME] in clause-final position
    # as a temporal adjunct without a preposition, parallel to ADV
    # time-adverbials (``kahapon`` / ``bukas``). The
    # N[SEM_CLASS=TIME] entries (``umaga`` / ``hapon`` /
    # ``pagkapananghalian`` / months) project as bare time-adverbials
    # alongside their N-as-predicate use (the existing N → S
    # ``BE-TIME`` rule).
    #
    # **TimeAdv non-terminal design.** The straightforward
    # ``S → S N[SEM_CLASS=TIME]`` shape fails to fire in Earley —
    # the bracket pattern doesn't gate the predicted N at chart
    # time. Using a fresh ``TimeAdv`` non-terminal decouples the
    # SEM_CLASS check: ``TimeAdv → N`` with the constraining
    # equation gates which N entries can project to TimeAdv, and
    # the S-level rule predicts only the TimeAdv slot. This
    # avoids the over-generation that ``S → S N`` would introduce
    # (which broke collective measure-N constructions like
    # ``isang dosenang itlog`` by spuriously feeding ``itlog`` to
    # the time-adjunct rule's SEM_CLASS=TIME constraint check).
    #
    # Reference: Schachter & Otanes 1972 §6.5 (bare time-noun
    # adverbials); R&G 1981 PANAHON sent-14.
    rules.append(Rule(
        "TimeAdv",
        ["N"],
        [
            "(↑) = ↓1",
            "(↓1 SEM_CLASS) =c 'TIME'",
        ],
    ))
    rules.append(Rule(
        "S",
        ["S", "TimeAdv"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
        ],
    ))

    # --- Phase 5n.A Commit 18 (§18 L80): clause-final EXCEPTIVE PP ---
    #
    # ``Kumain si Maria bukod sa Juan.`` "Maria ate besides Juan."
    # ``Bumili ako ng aklat maliban sa lapis.`` "I bought a book
    # except a pencil."
    #
    # Parallel to the TIME_FRAME PP rule above but gated on
    # ``PREP_TYPE=EXCEPTIVE`` (the new ``bukod`` / ``maliban`` PREP
    # entries in particles.yaml). The other Phase 5e Commit 3 PPs
    # (BENEFICIARY / TOPIC / SOURCE / REASON) remain restricted to
    # ay-fronting position — exceptive PPs are the natural extension
    # that admits clause-final attachment because the exception
    # semantically modifies the matrix proposition (parallel to
    # temporal-frame PPs).
    rules.append(Rule(
        "S",
        ["S", "PP"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 PREP_TYPE) =c 'EXCEPTIVE'",
        ],
        budget=_SS_PP_BUDGET,
    ))

    # --- 9.X.c13: sentence-initial REASON PP fronted with comma -----
    #
    # ``Dahil sa init ng araw, panay ang tulo ng pawis ng tao.``
    #     "Because of the heat of the sun, the flow of human sweat
    #     is continuous." (R&G 1981 PANAHON sent-12).
    # ``Dahil sa ganitong pagkakaayos ng panahon, iba ang kamalayang
    #     Pilipino tungkol sa oras.`` (PANAHON sent-39 fronted part).
    #
    # Adds a fronted-PP-with-comma S rule for REASON PPs (``dahil
    # sa X``). Parallels the existing ay-fronted-PP rule
    # (extraction.py: ``S → PP PART[LINK=AY] S``) and the
    # SubordClause-with-comma rule
    # (subordination.py: ``S → SubordClause PUNCT[COMMA] S``).
    #
    # Rule shape:
    #
    #   S → PP PUNCT[PUNCT_CLASS=COMMA] S
    #     (↑) = ↓3                       matrix is the post-comma S
    #     (↑ TOPIC) = ↓1                 fronted PP is TOPIC
    #     ↓1 ∈ (↑ ADJ)                  also sits in matrix ADJ set
    #     (↓1 PREP_TYPE) =c 'REASON'    restrict to dahil-PP
    #
    # The REASON gate matches the SOURCE / BENEFICIARY / TOPIC /
    # EXCEPTIVE deferral pattern — we add construction support one
    # PREP_TYPE at a time as corpus pressure surfaces it. REASON-
    # fronted-with-comma is a frequent R&G construction; SOURCE
    # has Wackernagel interaction with range expressions and stays
    # deferred.
    #
    # Reference: R&G 1981 §7.7 (sentence-fronted adjunct PP); R&G
    # 1981 PANAHON essay (sent-12 + sent-39).
    # Phase 10.J.post-2 narrowing: the PP daughter's bracket gate
    # ``PP[PREP_TYPE=REASON]`` pushes the REASON check from
    # solve-time to chart time. The generic PP rule in
    # extraction.py now advertises ``PREP_TYPE`` on its LHS
    # (one rule per value), so the chart's prediction at this
    # position predicts only the REASON variant — pruning the
    # spurious chart states the un-gated rule produced.
    #
    # Phase 10.J.post-7.4 extends the loop to include SOURCE
    # (``mula sa X``). The fronted-PP-comma rule shape is identical
    # across PREP_TYPEs (TOPIC binding + ADJ-set membership); only
    # the chart-time daughter gate differs. SOURCE-fronted
    # constructions like ``Mula sa Maynila, naglakbay kami sa Cebu.``
    # (R&G 1981 §7.7-style sentence-fronted adjunct PP) close on this
    # extension. The phantom Wackernagel/range risk noted in 9.X.c13
    # was reassessed: bare ``mula X hanggang Y`` builds a structurally
    # distinct ``PP[PREP_TYPE=RANGE]`` (4-daughter rule in
    # nominal.py), so the SOURCE branch (3-daughter ``PREP NP[DAT]``)
    # never competes.
    for prep_type in ("REASON", "SOURCE"):
        rules.append(Rule(
            "S",
            [f"PP[PREP_TYPE={prep_type}]", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "↓1 ∈ (↑ ADJ)",
            ],
        ))

    # --- 9.X.c12: clause-final BENEFICIARY + TOPIC PPs ---------------
    #
    # ``Inihahanda nila ang lupa para sa binhi.`` "They prepare the
    # land for the seed" (R&G 1981 PANAHON sent-32).
    # ``Iba ang kamalayang Pilipino tungkol sa oras.`` "The Filipino
    # awareness about time is different" (PANAHON sent-39 tail).
    #
    # Lifts the Phase 5n.A Commit 18 deferral note for BENEFICIARY
    # (``para sa``) and TOPIC (``tungkol sa``) PPs — admits them
    # clause-finally, parallel to TIME_FRAME and EXCEPTIVE rules
    # directly above. Both PREP_TYPEs scope semantically over the
    # matrix proposition (benefactive: "for X" / topical: "about
    # X"), so clause-final attachment matches the prior reasoning
    # used for EXCEPTIVE.
    #
    # The SOURCE (``mula sa``) and REASON (``dahil sa``) PREP_TYPEs
    # were originally NOT lifted here. SOURCE had a posited
    # Wackernagel interaction risk (``mula-sa-NP`` can also appear in
    # range expressions like ``mula X hanggang Y``); REASON
    # (``dahil sa``) admitted both PP and subordinate-clause
    # complements and the disambiguation was construction-class work.
    # Both restrictions have since been lifted (REASON in post-7.2,
    # SOURCE in post-7.4) — the c12 chart rule predicts the
    # ``S [S PP]`` daughter sequence only after a complete S, and
    # the SOURCE PP[PREP_TYPE=SOURCE] daughter requires the
    # 3-daughter ``PREP NP[DAT]`` shape (not the 4-daughter
    # ``PP[PREP_TYPE=RANGE]``), so no chart-time ambiguity remains.
    #
    # Reference: R&G 1981 §7.6 (clause-final adjunct PPs); R&G 1981
    # PANAHON essay (sent-32 + sent-39 tail).
    #
    # Phase 9.X.c29 extends the loop to include GOAL (``tungo sa X``
    # "toward X") for PANAHON sent-31 ``... tungo sa bukid`` —
    # semantically parallel to BENEFICIARY / TOPIC (a thematic
    # role scoping the matrix proposition), structurally identical
    # via the same ``S → S PP`` rule.
    #
    # Phase 10.J.post-7.2 lifts the c12 deferral on REASON
    # (``dahil sa`` / ``dahilan sa``). The original deferral cited
    # "PP-vs-SubordClause complement disambiguation" — but at chart
    # level the PP daughter requires ``NP[CASE=DAT]`` (no S
    # complement possible), and the post-7 ``SubordClause →
    # PART[COMP_TYPE=REAS] S`` rule (subordination.py:471) already
    # routes the bare-S complement case through a distinct
    # SubordClause category. No chart-time ambiguity remains, so
    # adding REASON to this loop is safe. Closes ``Hindi kami
    # nakapasok sa eskwela dahilan sa ulan.`` (post-7.2 dahilan-4-postv)
    # and the parallel ``dahil sa ulan`` clause-final exemplar.
    #
    # Phase 10.J.post-7.4 lifts the c12 deferral on SOURCE
    # (``mula sa``). The originally-posited Wackernagel risk
    # (``mula X hanggang Y`` range expressions) is structurally
    # distinct: bare ``mula X hanggang Y`` parses as
    # ``PP[PREP_TYPE=RANGE]`` (4-daughter ``PREP N PART N`` rule
    # in nominal.py), not as ``PP[PREP_TYPE=SOURCE]`` (3-daughter
    # ``PREP NP[CASE=DAT]``). The chart's PREP_TYPE LHS
    # advertisement (post-2) ensures the two PP variants are
    # disambiguated at chart time — no cross-product blow-up. Closes
    # ``Naglakbay kami sa Cebu mula sa Maynila.`` (post-7.4 mula-sa-4-postv).
    for prep_type in ("BENEFICIARY", "TOPIC", "GOAL", "REASON", "SOURCE"):
        rules.append(Rule(
            "S",
            ["S", "PP"],
            [
                "(↑) = ↓1",
                "↓2 ∈ (↑ ADJUNCT)",
                f"(↓2 PREP_TYPE) =c '{prep_type}'",
            ],
            budget=_SS_PP_BUDGET,
        ))


    # --- Phase 5f Commit 5: clause-final FREQUENCY AdvP ---------
    #
    # ``Kumain ako makalawa.`` "I ate twice."
    # ``Tumakbo siya makasampu.`` "He ran ten times."
    #
    # Closes part of the Phase 5e Commit 3 deferral on bare AdvP
    # placement — scoped here to FREQUENCY adverbs only via the
    # constraining equation ``(↓2 ADV_TYPE) =c 'FREQUENCY'``.
    # The TIME / location / manner deferrals stay in force because
    # those adverb types interact with the Wackernagel cluster
    # and quantifier-float in ways that require separate
    # analytical work; FREQUENCY adverbs are clausal modifiers
    # with no such interaction.
    #
    # The AdvP attaches as a member of the matrix's ADJUNCT set
    # (parallel to how the existing intransitive-V S rules treat
    # GEN-NP adjuncts). The constraining equation prevents the
    # rule from firing on TIME / SPATIAL / MANNER AdvPs (which
    # would over-cover and trigger the deferred interactions).
    rules.append(Rule(
        "S",
        ["S", "AdvP"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 ADV_TYPE) =c 'FREQUENCY'",
        ],
    ))

    # --- Phase 5n.B Commit 19: clause-final indefinite AdvP -------
    #
    # ``Pupunta ako kahit saan.``    "I'll go anywhere."
    # ``Kakain ako kahit kailan.``   "I'll eat anytime."
    # ``Kumain ako kahit saan.``     "I ate anywhere."
    #
    # Closes §18.1 deferral L99. Sibling to the Phase 5f C5
    # FREQUENCY AdvP rule above; same daughter shape (S + AdvP),
    # but gated to indefinite ADVs via ``(↓2 INDEF) =c 'YES'``.
    # Indefinite ADVs are produced by the Phase 5m C8 IndefADV
    # rule (``ADV → PART[LEMMA=kahit] ADV[WH]``), which
    # composes ``kahit`` with the wh-ADV inventory (saan / kailan
    # / paano / bakit). The INDEF=YES gate keeps the plain-LOCATION
    # / plain-TIME deferrals (Phase 5f C5 closing note) in force —
    # only the kahit-X variants are admitted here.
    #
    # **Scope note**: per plan-of-record §4.2 Commit 19 the target
    # surfaces are LOCATION (kahit saan) and TIME (kahit kailan).
    # The INDEF=YES gate also admits MANNER (kahit paano) and
    # REASON (kahit bakit) which are equally natural and pose no
    # additional ambiguity risk.
    rules.append(Rule(
        "S",
        ["S", "AdvP"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 INDEF) =c 'YES'",
        ],
    ))

    # --- Phase 9.W Cluster A/H: clause-final TIME AdvP -----------
    #
    # ``Sasayaw siya bukas ng gabi.`` "She will dance tomorrow
    # evening." (S&O 1972 p.441 / sent-676)
    # ``Kakain siya bukas.``           "She'll eat tomorrow."
    # ``Pumunta siya kahapon.``        "She went yesterday."
    #
    # Phase 5f Commit 5 closed clause-final FREQUENCY AdvP; Phase
    # 5n.B Commit 19 closed clause-final INDEF AdvP. The TIME case
    # was the original Phase 5e Commit 3 deferral noted in the
    # Phase 5f closing comment — held back due to anticipated
    # interaction with Wackernagel cluster + quantifier-float.
    # Phase 9.W lifts it: the post-9.O grammar's clitic-pass +
    # quantifier-float work has matured enough that the interaction
    # doesn't surface as ambiguity in audit-corpus testing.
    #
    # Gated on ``ADV_TYPE=TIME`` to keep MANNER/LOCATION/SPATIAL
    # adverbs (still deferred) from firing here. The AdvP's
    # f-structure inherits TIME / DEIXIS_TIME / LEMMA from the
    # head ADV via the existing ``AdvP → ADV`` lift rule. The
    # compound ``bukas ng gabi`` "tomorrow evening" composes via
    # the new compound TIME-AdvP rule below.
    rules.append(Rule(
        "S",
        ["S", "AdvP"],
        [
            "(↑) = ↓1",
            "↓2 ∈ (↑ ADJUNCT)",
            "(↓2 ADV_TYPE) =c 'TIME'",
        ],
    ))


    # --- Phase 5m Commit 4: sentence-initial sentential ADV --------
    #
    # ``Siguro pumupunta siya.`` "Maybe he's going."
    # ``Marahil hindi siya kakain.`` "Perhaps he won't eat."
    # ``Samakatuwid kumain siya.`` "Therefore he ate." (Commit 10)
    # ``Bukod dito kumain siya.`` "Moreover he ate." (Commit 11)
    #
    # A single sentence-initial PART rule covers two construction
    # families: epistemic-modal particles (``siguro`` / ``marahil``,
    # EPISTEMIC=PROBABLY) and discourse connectives (``samakatuwid``
    # / ``gayunpaman``, DISCOURSE=THEREFORE / HOWEVER, plus the
    # multi-word connectives ``gayon din`` / ``ganon din`` / ``bukod
    # dito`` from Commit 11). Both families carry the marker feat
    # ``DISCOURSE_POS=SENTENCE_INITIAL``, which gates the rule and
    # excludes other PARTs (linkers, polarity, 2P clitics) from
    # occupying this c-structure slot.
    #
    # F-structure shape: matrix S inherits the inner S's f-structure
    # (PRED, SUBJ, OBJ, ASPECT, etc.) via ``(↑) = ↓2``; the
    # sentence-initial PART joins the matrix's ADJUNCT set as a
    # daughter member, carrying its own EPISTEMIC / DISCOURSE marker.
    # No matrix-level lift of EPISTEMIC / DISCOURSE — downstream
    # consumers iterate ADJUNCT to detect the modal / discourse
    # marker. (Contrast with Phase 5l Rule C / Phase 5m Rule D which
    # lift COUNTERFACTUAL / REGISTER to the matrix because those are
    # clausal-mood properties; epistemic and discourse markers are
    # inherently adjunct-scoped.)
    # Phase 10.J.post-2 narrowing: the bracket gate on the PART
    # daughter pushes the ``DISCOURSE_POS=SENTENCE_INITIAL`` check
    # from solve time to **chart time**. Lex entries for
    # discourse-initial connectives (``at`` / ``kaya`` /
    # ``samakatuwid`` / ``gayunpaman`` / ``siguro`` / ``marahil`` /
    # …) carry the feat on the PART category pattern; non-connective
    # PARTs (linkers, polarity, 2P clitics) don't. Without the
    # bracket gate the chart predicted this rule wherever ``S``
    # was expected and admitted any PART token there, multiplying
    # ``(PART-token × S-parse)`` combinations into the packed
    # forest — the 10.I-style fan-out probe (``tmp/probe_10i_fanout
    # .py PANAHON/sent-39``) ranked this rule first at span_max
    # 38880 emissions / span, dominating sent-39's tree-iteration
    # budget so the canonical 9.X.c13 fronted-Dahil-PP parse sat
    # past cap 5000.
    rules.append(Rule(
        "S",
        ["PART[DISCOURSE_POS=SENTENCE_INITIAL]", "S"],
        [
            "(↑) = ↓2",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))


    # --- Phase 5m Commit 11: multi-word discourse connectives ------
    #
    # ``Gayon din kumain ang bata.``  "Likewise, the child ate."
    # ``Ganon din kumain ang bata.``  (colloquial variant of gayon din)
    # ``Bukod dito kumain ang bata.`` "Moreover, the child ate."
    #
    # Three multi-word lexicalized rules building virtual PART
    # nodes from two-token sequences. Each emitted virtual PART
    # carries DISCOURSE + DISCOURSE_POS=SENTENCE_INITIAL so it
    # feeds the Commit 4 sentence-initial PART rule above; the
    # composition surfaces uniformly with single-word connectives
    # (Commit 10 ``samakatuwid`` / ``gayunpaman``).
    #
    # Heads (``gayon`` / ``ganon`` / ``bukod``) are Commit 1 lex
    # entries with LEMMA only — no DISCOURSE feat at the lex level
    # so they don't fire as sentence-initial connectives standalone.
    # Tails are existing entries with LEMMA added in this commit:
    # ``din`` (PART[ADV=ALSO, LEMMA=din]) and ``dito``
    # (ADP[CASE=DAT, DEIXIS=PROX, DEM, LEMMA=dito]).
    #
    # The bukod-dito rule has mixed-POS daughters (PART + ADP)
    # because ``dito`` is the locative DEM, not a PART. Other
    # multi-word entries use PART + PART daughters.
    #
    # Same precedent as Phase 5l ``mula nang`` (multi-word
    # subordinator composing PREP[mula] + PART[nang]).
    #
    # Reference: R&B 1986 §15.7.
    #
    # Phase 10.J.post-2: LHS advertises ``DISCOURSE_POS=SENTENCE_INITIAL``
    # as a chart-side feat so the Phase 5m C4 rule above
    # (``S → PART[DISCOURSE_POS=SENTENCE_INITIAL] S``) can bracket-
    # gate on it without re-running the solve-time check. Bare-PART
    # parents still match because the matcher takes
    # ``expected=PART`` as feature-empty.
    #
    # gayon din → DISCOURSE=LIKEWISE
    rules.append(Rule(
        "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
        ["PART", "PART"],
        [
            "(↑ DISCOURSE) = 'LIKEWISE'",
            "(↑ DISCOURSE_POS) = 'SENTENCE_INITIAL'",
            "(↑ LEMMA) = 'gayon_din'",
            "(↓1 LEMMA) =c 'gayon'",
            "(↓2 LEMMA) =c 'din'",
        ],
    ))
    # ganon din → DISCOURSE=LIKEWISE (colloquial variant)
    rules.append(Rule(
        "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
        ["PART", "PART"],
        [
            "(↑ DISCOURSE) = 'LIKEWISE'",
            "(↑ DISCOURSE_POS) = 'SENTENCE_INITIAL'",
            "(↑ LEMMA) = 'ganon_din'",
            "(↓1 LEMMA) =c 'ganon'",
            "(↓2 LEMMA) =c 'din'",
        ],
    ))
    # bukod dito → DISCOURSE=ALSO (mixed PART + ADP daughters).
    # The dito daughter is identified by its unique DAT/DEM/PROX
    # feat combo via category-pattern constraints rather than by
    # LEMMA — adding LEMMA to the existing dito ADP entry conflicts
    # with the ``(↑ LEMMA) = ↓3 LEMMA`` equation in the Phase 5g
    # pre-mod demonstrative NP rule (cfg/nominal.py:286), which
    # would double-assign matrix LEMMA when ``ditong palengke``
    # parses. The category-pattern matcher handles the YAML-1.1
    # ``DEM: YES`` → Python ``True`` correctly (whereas an
    # ``=c`` equation would compare against the string ``'YES'``
    # and silently fail to match).
    rules.append(Rule(
        "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
        ["PART", "ADP[CASE=DAT, DEIXIS=PROX, DEM]"],
        [
            "(↑ DISCOURSE) = 'ALSO'",
            "(↑ DISCOURSE_POS) = 'SENTENCE_INITIAL'",
            "(↑ LEMMA) = 'bukod_dito'",
            "(↓1 LEMMA) =c 'bukod'",
        ],
    ))

    # --- Phase 10.J.post-7.3: ``alalaong baga`` REFORM marker ---------
    #
    # ``Alalaong baga, naging masungit na siya.``
    #     "In other words, he has become grumpy."
    # ``Alalaong baga, marami pa tayong dapat gawin.``
    #     "That is to say, we still have a lot to do." (inner clause
    #     deferred to post-7.3.post-1 — Q-existential-possessive +
    #     dapat-V-cluster construction)
    #
    # Two-token phrasal discourse marker building a virtual PART
    # node with DISCOURSE_POS=SENTENCE_INITIAL + DISCOURSE=REFORM
    # (reformulation marker). The fixed idiom means "in other words"
    # / "that is to say" — a metalinguistic reformulation operator
    # paralleling Spanish ``es decir`` / English ``i.e.``.
    #
    # Heads (``alalaong`` / ``baga``) are LEMMA-only PARTs added in
    # particles.yaml § (d). Neither composes to REFORM on its own;
    # only the fixed two-token sequence fires this rule. The
    # daughters are matched by LEMMA constraining equations
    # (parallel to Phase 5m Commit 11's ``gayon din`` / ``ganon din``
    # builders).
    #
    # Once built, this virtual PART feeds the existing Phase 9.V.4b
    # comma-variant rule at the end of this function
    # (``S → PART[DISCOURSE_POS=SENTENCE_INITIAL] PUNCT[COMMA] S``)
    # to yield the comma-fronted matrix shape.
    #
    # Reference: S&O 1972 §3.5 discourse-connective inventory; user-
    # verified via GT 2026-05-29 for post-7.3 constructed exemplars.
    rules.append(Rule(
        "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
        ["PART", "PART"],
        [
            "(↑ DISCOURSE) = 'REFORM'",
            "(↑ DISCOURSE_POS) = 'SENTENCE_INITIAL'",
            "(↑ LEMMA) = 'alalaong_baga'",
            "(↓1 LEMMA) =c 'alalaong'",
            "(↓2 LEMMA) =c 'baga'",
        ],
    ))

    # --- Phase 9.V.4a: "Una sa lahat" multi-word discourse marker -----
    #
    # ``Una sa lahat, ang isang Pilipino ay bahagi ng kanyang pamilya.``
    #     "First of all, a Filipino is part of his family."
    #     (R&C 1990 ANG PAMILYA sent-1 — 9.U Cluster B audit hit)
    #
    # Three-token phrasal discourse marker building a virtual PART
    # node with DISCOURSE_POS=SENTENCE_INITIAL. The component parts
    # are independently in the lex but don't compose to a
    # discourse-initial reading on their own:
    #
    #   * ``una`` — NUM[ORDINAL=true, ORDINAL_VALUE='1']
    #   * ``sa``  — ADP[CASE=DAT]
    #   * ``lahat`` — Q[QUANT=ALL]
    #
    # The phrasal idiom means "first of all" / "above all" — a
    # primary-ranking discourse connective parallel to 5m C10's
    # ``samakatuwid`` ("therefore") and 5m C11's ``gayon din``
    # ("likewise"). Once built, it feeds the comma-variant of the
    # 5m C4 sentence-initial PART rule below.
    rules.append(Rule(
        "PART[DISCOURSE_POS=SENTENCE_INITIAL]",
        ["NUM[ORDINAL=true]", "ADP[CASE=DAT, MARKER=SA]", "Q[QUANT=ALL]"],
        [
            "(↑ DISCOURSE) = 'PRIMARY_RANKING'",
            "(↑ DISCOURSE_POS) = 'SENTENCE_INITIAL'",
            "(↑ LEMMA) = 'una_sa_lahat'",
            "(↓1 ORDINAL_VALUE) =c '1'",
            "(↓3 LEMMA) =c 'lahat'",
        ],
    ))

    # --- Phase 9.V.4b: comma-variant of 5m C4 sentence-initial PART ---
    #
    # ``Una sa lahat, ang isang Pilipino ay bahagi ng kanyang pamilya.``
    #     (closes the 9.V.4a phrasal-PART output as a comma-fronted
    #      discourse topic.)
    #
    # Companion to the 5m C4 rule above (``S → PART S`` for
    # sentence-initial discourse markers without comma). The
    # comma variant admits the parallel pattern where the
    # discourse marker is followed by a comma boundary (a natural
    # intonation break in the audit corpus). Same equation set as
    # 5m C4 but with PUNCT[COMMA] consumed between the PART and
    # the matrix S.
    #
    # Generalization: this rule also lets single-word connectives
    # like ``samakatuwid`` ("therefore"), ``siguro`` ("maybe"),
    # ``bukod dito`` ("moreover") appear with a comma — natural in
    # written register. Pre-9.V they had to appear without comma
    # (the 8.D2 INTERJ-comma rule only matched INTERJ=true PARTs).
    # Phase 10.J.post-2 narrowing: the PART daughter's bracket gate
    # ``PART[DISCOURSE_POS=SENTENCE_INITIAL]`` pushes the check
    # from solve time to chart time. Both single-word connective
    # lex entries and the multi-word PART-LHS rules above
    # advertise the feat — so the chart admits only connective
    # PARTs at this slot.
    rules.append(Rule(
        "S",
        ["PART[DISCOURSE_POS=SENTENCE_INITIAL]", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "↓1 ∈ (↑ ADJUNCT)",
        ],
    ))


    # --- Phase 5n.B Commit 24: narrative-opener idiom (§18 L30) -------
    #
    # ``Nang isang beses, may isang manok.``  "Once, there was a
    #                                          chicken."
    # ``Nang isang beses, kumain ang bata.``  "Once, the child ate."
    #
    # Closes §18.1 deferral L30 (and §18.2 lines 204-215). A fixed-
    # phrase idiom: the literal sequence ``Nang isang beses ,``
    # introduces a narrative clause-initial frame, followed by an
    # arbitrary inner clause. The matrix carries
    # ``DISCOURSE='NARRATIVE_OPENER'``; the inner clause's
    # f-structure is lifted via ``(↑) = ↓4``.
    #
    # The ``isang`` cardinal modifier collapses with ``beses`` into
    # a matrix-N daughter (Phase 5f cardinal-internal-modifier rule
    # builds ``isa + -ng + beses → N``); we constrain ↓2 to be that
    # specific N via ``LEMMA=beses`` and ``SEM_CLASS=FREQUENCY``
    # (both set by the existing ``beses`` lex entry). The literal-
    # lemma constraint on ↓1 (``LEMMA=nang``) and the comma-PUNCT
    # constraint on ↓3 lock the rule to the exact idiomatic surface.
    #
    # Non-idiom uses of nang / isa / beses (e.g., ``Kumain ako nang
    # marami``, ``isang aklat``) continue to parse via their
    # existing rules — the 4-daughter N-required pattern doesn't
    # match those shapes.
    rules.append(Rule(
        "S",
        [
            "PART",       # nang
            "NUM",        # isa
            "PART",       # -ng linker
            "N",          # beses
            "PUNCT[PUNCT_CLASS=COMMA]",  # ,
            "S",          # inner clause
        ],
        [
            "(↑) = ↓6",
            "(↑ DISCOURSE) = 'NARRATIVE_OPENER'",
            "(↓1 LEMMA) =c 'nang'",
            "(↓2 CARDINAL_VALUE) =c '1'",
            "(↓3 LINK) =c 'NG'",
            "(↓4 LEMMA) =c 'beses'",
            "(↓4 SEM_CLASS) =c 'FREQUENCY'",
            "(↓5 PUNCT_CLASS) =c 'COMMA'",
        ],
    ))


    # --- Phase 9.X.c22: "Kung minsan" idiomatic time adverb ----------
    #
    # ``Kung minsan ay wala pa.``  "Sometimes there's still none."
    #                              (PANAHON sent-5)
    #
    # Two-token fixed idiom composing the conditional-conjunction
    # ``kung`` with the FREQUENCY ADV ``minsan`` ("sometimes / once")
    # to yield a virtual ADV with ADV_TYPE=TIME (frame-setting time
    # adverbial). Once built, the existing Phase 5e ``AdvP → ADV``
    # lift in cfg/extraction.py promotes it to AdvP, which then feeds:
    #
    #   * The Phase 5e ay-fronted AdvP rule
    #     (cfg/extraction.py: ``S → AdvP PART[LINK=AY] S``) — for the
    #     ``Kung minsan ay X`` surface.
    #   * The Phase 8.D2 comma-fronted AdvP rule
    #     (cfg/clause.py: ``S → AdvP PUNCT[COMMA] S``) — for the
    #     ``Kung minsan, X`` surface.
    #
    # ``kung`` is independently the COND-conjunction (PART[COMP_TYPE=
    # COND]); the COMP_TYPE gate on ↓1 narrows this rule to the
    # conditional ``kung``, leaving the INTERROG ``kung`` (indirect-Q
    # complementizer) free to fire its own rules. ``minsan`` is the
    # FREQUENCY ADV (ADV_TYPE=FREQUENCY, FREQ_VALUE=SOMETIMES) — the
    # ADV_TYPE gate on ↓2 keeps the rule from accidentally firing on
    # other ADVs that share LEMMA="minsan".
    #
    # The matrix ADV adopts ADV_TYPE=TIME (rather than FREQUENCY)
    # because the idiom semantically frames a time-of-occasion ("at
    # times") rather than a frequency-of-occurrence; this lets it
    # feed the clause-initial frame-setting rules above that gate on
    # ADV_TYPE=TIME. FREQ_VALUE=SOMETIMES is preserved as a sub-feat
    # for downstream consumers.
    rules.append(Rule(
        "ADV",
        ["PART", "ADV"],
        [
            "(↑ ADV_TYPE) = 'TIME'",
            "(↑ FREQ_VALUE) = 'SOMETIMES'",
            "(↑ LEMMA) = 'kung_minsan'",
            "(↓1 LEMMA) =c 'kung'",
            "(↓1 COMP_TYPE) =c 'COND'",
            "(↓2 LEMMA) =c 'minsan'",
            "(↓2 ADV_TYPE) =c 'FREQUENCY'",
        ],
    ))


    # --- Phase 9.X.c25: em-dash clause-final appositive ``S -- XP`` -
    #
    # ``Ang tawag nila rito'y siyesta -- isang kaugaliang nakuha
    #  nila sa Kastila.``
    #     "What they call it is siesta — a custom they took from
    #      the Castilians."  (PANAHON sent-15)
    #
    # User suggestion 2026-05-20: treat ``--`` like an em-dash —
    # semantically a comma-equivalent that introduces a parenthetical
    # or appositive. The Phase 9.X.c25 tokenizer pre-pass
    # (``text/tokenizer.py``) merges consecutive ``-`` characters
    # into a single ``--`` token; the Phase 9.X.c25 lex entry in
    # particles.yaml surfaces it as ``PUNCT[PUNCT_CLASS=DASH]``.
    #
    # Two rules cover the audit-corpus em-dash uses (sent-15,
    # sent-41):
    #
    #   (a) NP appositive  ``S -- N``   — clause-final bare N or
    #       cardinal-N (no case marker; Tagalog indefinite NP
    #       surfaces). The cardinal-modified-N rule builds N (not
    #       NP[CASE=NOM] which requires a marker), so this rule
    #       consumes N to admit both bare and cardinal-modified
    #       appositives.
    #   (b) Clause appositive  ``S -- S``  — a continuation clause
    #       that elaborates on the matrix (used in sent-41 for
    #       ``na ang ibig sabihin ay laging huli``).
    #
    # F-structure: matrix S inherits the pre-dash clause's
    # f-structure via ``(↑) = ↓1``; the post-dash XP rides as ``APP``
    # set-membership (parallel to the Phase 9.X.c20 ``lalo na``-
    # mediated GEN-NP appositive). No CLAUSE_TYPE shift — the
    # pre-dash clause's clause-type continues to govern.
    rules.append(Rule(
        "S",
        ["S", "PUNCT[PUNCT_CLASS=DASH]", "N"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ APP)",
        ],
    ))
    rules.append(Rule(
        "S",
        ["S", "PUNCT[PUNCT_CLASS=DASH]", "S"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ APP)",
        ],
    ))


    # --- Phase 9.X.c26: clause-final colon appositive ``S : XP`` ----
    #
    # User note 2026-05-20: mid-sentence ``:`` introduces a
    # consequence, result, or enumeration — semantically parallel
    # to em-dash and comma as a soft clause-final boundary
    # admitting an appositive or continuation.
    #
    # Three rules per punct class (DASH and COLON), covering the
    # three observed appositive shapes:
    #
    #   (N)        — bare-N or cardinal-N enumeration head
    #                (``May tatlong prutas -- mangga, papaya at
    #                 pakwan.``)
    #   (NP[NOM])  — ang-marked NP enumeration head
    #                (PANAHON sent-2 / sent-9 post-colon shape:
    #                ``ang panahon ng tag-init mula Abril ...``;
    #                ``ang mangga, bayabas, ..., at pakwan``)
    #   (S)        — consequence / result / continuation clause
    #                (``Maganda ang ulan: malakas ito.``)
    #
    # The (NP[NOM]) variants were retro-extended to DASH in c26
    # for symmetry — the c25 DASH-only rules had N + S, this
    # commit completes the appositive-daughter class to N +
    # NP[NOM] + S for both punct classes. (The c25 commit message
    # noted the N daughter as the audit-corpus shape; c26's review
    # showed audit-corpus colons take ang-marked NP[NOM], and
    # parallel dash uses are plausible enough to warrant the
    # symmetric rule even without a current PANAHON match.)
    #
    # Audit-corpus uses include sent-2 (NP-internal range
    # modifiers over months) and sent-9 (headless OV-RC + ADV-
    # initial); both need additional construction-class closures
    # beyond the colon boundary itself, so c26 is foundational
    # rather than PANAHON-closing on its own.
    #
    # F-structure: matrix S inherits the pre-colon clause via
    # ``(↑) = ↓1``; the post-colon XP rides as ``APP``
    # set-membership (parallel to the DASH appositive rules above).
    rules.append(Rule(
        "S",
        ["S", "PUNCT[PUNCT_CLASS=DASH]", "NP[CASE=NOM]"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ APP)",
        ],
    ))
    rules.append(Rule(
        "S",
        ["S", "PUNCT[PUNCT_CLASS=COLON]", "N"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ APP)",
        ],
    ))
    rules.append(Rule(
        "S",
        ["S", "PUNCT[PUNCT_CLASS=COLON]", "NP[CASE=NOM]"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ APP)",
        ],
    ))
    rules.append(Rule(
        "S",
        ["S", "PUNCT[PUNCT_CLASS=COLON]", "S"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ APP)",
        ],
    ))
