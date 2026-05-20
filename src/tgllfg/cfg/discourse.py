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

from __future__ import annotations

from .grammar import Rule


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
    rules.append(Rule(
        "S",
        ["PP", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "(↑ TOPIC) = ↓1",
            "↓1 ∈ (↑ ADJ)",
            "(↓1 PREP_TYPE) =c 'REASON'",
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
    # are NOT lifted here. SOURCE has Wackernagel interaction risk
    # (mula-sa-NP can also appear in range expressions like ``mula
    # X hanggang Y``); REASON (``dahil sa``) admits both PP and
    # subordinate-clause complements and the disambiguation is
    # construction-class work. Both remain restricted to ay-
    # fronting position pending audit-driven justification.
    #
    # Reference: R&G 1981 §7.6 (clause-final adjunct PPs); R&G 1981
    # PANAHON essay (sent-32 + sent-39 tail).
    for prep_type in ("BENEFICIARY", "TOPIC"):
        rules.append(Rule(
            "S",
            ["S", "PP"],
            [
                "(↑) = ↓1",
                "↓2 ∈ (↑ ADJUNCT)",
                f"(↓2 PREP_TYPE) =c '{prep_type}'",
            ],
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
    rules.append(Rule(
        "S",
        ["PART", "S"],
        [
            "(↑) = ↓2",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↓1 DISCOURSE_POS) =c 'SENTENCE_INITIAL'",
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
    # gayon din → DISCOURSE=LIKEWISE
    rules.append(Rule(
        "PART",
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
        "PART",
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
        "PART",
        ["PART", "ADP[CASE=DAT, DEIXIS=PROX, DEM]"],
        [
            "(↑ DISCOURSE) = 'ALSO'",
            "(↑ DISCOURSE_POS) = 'SENTENCE_INITIAL'",
            "(↑ LEMMA) = 'bukod_dito'",
            "(↓1 LEMMA) =c 'bukod'",
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
        "PART",
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
    rules.append(Rule(
        "S",
        ["PART", "PUNCT[PUNCT_CLASS=COMMA]", "S"],
        [
            "(↑) = ↓3",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↓1 DISCOURSE_POS) =c 'SENTENCE_INITIAL'",
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
