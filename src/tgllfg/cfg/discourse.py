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
    # of N. The constraining equation ``(↓2 DIGIT_FORM) =c 'YES'``
    # restricts to digit-form numerics (a word-form numeric like
    # ``noong sandaan-siyamnapung`` "in 190" is theoretically
    # parseable but isn't the natural register and isn't exercised
    # by the seed corpus). The CARDINAL_VALUE lifts to ``YEAR`` on
    # the matrix PP. (Phase 5f closing deferral, 2026-05-04.)
    rules.append(Rule(
        "PP",
        ["PART", "NUM[CARDINAL=YES]"],
        [
            "(↑) = ↓1",
            "(↑ YEAR) = ↓2 CARDINAL_VALUE",
            "(↓1 TIME_FRAME)",
            "(↓2 DIGIT_FORM) =c 'YES'",
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
    # rule (``ADV → PART[LEMMA=kahit] ADV[WH=YES]``), which
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
    # (ADP[CASE=DAT, DEIXIS=PROX, DEM=YES, LEMMA=dito]).
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
        ["PART", "ADP[CASE=DAT, DEIXIS=PROX, DEM=YES]"],
        [
            "(↑ DISCOURSE) = 'ALSO'",
            "(↑ DISCOURSE_POS) = 'SENTENCE_INITIAL'",
            "(↑ LEMMA) = 'bukod_dito'",
            "(↓1 LEMMA) =c 'bukod'",
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
