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
