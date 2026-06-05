# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/cfg/negation.py

"""Clausal negation rules: ``hindi`` declarative + ``huwag`` imperative.

Holds the rules that overlay POLARITY (and, for ``huwag``, MOOD=IMP)
onto a full inner ``S``. After the post-Phase-5f grammar split (see
``docs/refactor-grammar-package.md``) this module owns:

* Phase 4 §7.2 ``hindi`` clausal negation — the left-edge particle
  rule that wraps any well-formed inner S, percolates its
  PRED / VOICE / ASPECT / SUBJ / OBJ to the matrix, and overlays
  ``POLARITY=NEG``.
* Phase 5e Commit 25 ``huwag`` MOOD=IMP lift — the imperative
  variant: ``huwag`` overlays both ``POLARITY=NEG`` and
  ``MOOD=IMP`` onto the matrix, lifting imperative force to the
  outer clause when the inner verb may not carry imperative
  morphology.

The composer in :mod:`tgllfg.cfg.grammar` calls this registrar
fourth, after :mod:`tgllfg.cfg.nominal` /
:mod:`tgllfg.cfg.clause` / :mod:`tgllfg.cfg.clitic`,
and before extraction / control / discourse — see the plan's
"Migration strategy" §H.
"""

from .grammar import Rule


def register_rules(rules: list[Rule]) -> None:
    """Append the negation-area rules in source order."""
    # --- Phase 4 §7.2: clausal negation ---
    #
    # `hindi` is a declarative-negation particle (POLARITY=NEG).
    # `huwag` is an imperative-negation particle (POLARITY=NEG,
    # MOOD=IMP on the particle's lex feats).
    #
    # Single grammar rule: the matrix S inherits the inner S's
    # f-structure wholesale via ``(↑) = ↓2`` and overlays
    # POLARITY=NEG. Selectively projecting individual GFs
    # (PRED, SUBJ, OBJ, ...) was tried first but creates phantom
    # OBJ slots for intransitive inner clauses, tripping the
    # coherence check.
    #
    # The huwag-specific MOOD=IMP override is NOT lifted to the
    # matrix MOOD in Phase 4 §7.2 — the inner clause's verb
    # already projects MOOD=IND, and overriding from the particle
    # would clash. The particle's MOOD=IMP rides on its own
    # f-structure for now; full imperative-mood lifting is left
    # to a Phase 4 §7.3 / §7.6 follow-up that integrates clitic
    # placement and irrealis-form selection. Documented in
    # ``docs/analysis-choices.md`` "Phase 4 §7.2".
    # Phase 5e Commit 25 split: the existing rule restricts to
    # particles WITHOUT a MOOD feature (= ``hindi``, the
    # declarative negator). The huwag-specific rule below then
    # handles ``huwag`` (PART[MOOD=IMP, POLARITY=NEG]) without
    # rule competition.
    # Phase 5h Commit 3 follow-on: the original rule relied solely on
    # the category pattern ``PART[POLARITY=NEG]`` to filter the
    # particle daughter. Per ``compile.py::matches``, category-pattern
    # matching is non-conflict — a particle without a ``POLARITY``
    # feature absorbs the constraint and matches inappropriately. So
    # ``halos`` (PART[APPROX]) / ``tuwing`` (PART[TIME_FRAME=PERIODIC])
    # / new Phase 5h ``mas`` (PART[COMP_DEGREE=COMPARATIVE]) all
    # silently triggered phantom negation parses (``Halos kumain ang
    # bata`` parsed with POLARITY=NEG). Adding the explicit
    # ``(↓1 POLARITY) =c 'NEG'`` constraining equation closes the leak
    # — same belt-and-braces pattern Phase 5g Commit 3 used on the
    # predicative-adj rule's ``PREDICATIVE`` filter.
    rules.append(Rule(
        "S",
        ["PART[POLARITY=NEG]", "S"],
        [
            "(↑) = ↓2",
            "(↑ POLARITY) = 'NEG'",
            "(↓1 POLARITY) =c 'NEG'",
            "¬ (↓1 MOOD)",
        ],
    ))


    # --- Phase 5e Commit 25: huwag MOOD=IMP lifted to matrix ---
    #
    # The Phase 4 §7.2 limitation: the negation rule's
    # ``(↑) = ↓2`` propagates the inner verb's MOOD=IND, so
    # overlaying ``(↑ MOOD) = 'IMP'`` from huwag would clash with
    # IND (unifier rejects). Phase 5e Commit 25 lifts the
    # imperative reading via the **feature-architecture** path
    # (one of two options the Phase 4 limitation flagged):
    # introduce a ``CLAUSE-MOOD`` feature for clausal mood,
    # distinct from the verb's morphological ``MOOD``.
    #
    # * ``MOOD`` (existing): the verb's morphological mood —
    #   IND (default), ABIL (maka- abilitative), NVOL (ma-
    #   non-volitional), SOC (Phase 5e Commit 21 hortative
    #   and Phase 5e Commit 12 reciprocal). Always projected
    #   from the verb's lex equations.
    # * ``CLAUSE-MOOD`` (new in this commit): the sentential /
    #   speech-act mood — IMP for negative imperatives via
    #   ``huwag`` (and, in principle, declaratives could mark
    #   IND, but we leave that unset to avoid ceremony for the
    #   common case).
    #
    # The huwag rule below uses ``(↑) = ↓2`` (so PRED, SUBJ,
    # OBJ, etc. propagate from inner) AND sets matrix
    # ``CLAUSE-MOOD = IMP``. No conflict with inner's MOOD=IND
    # because the two features live on separate paths.
    #
    # The selective-projection alternative (the other option
    # flagged in §7.2) would require enumerating GFs to project
    # while excluding MOOD. That works in principle but creates
    # phantom GF slots for undefined features (``(↑ X) = (↓2 X)``
    # via get-or-create semantics) and tests would still need a
    # way to distinguish the imperative reading from the
    # declarative — which is what CLAUSE-MOOD is for. Choosing
    # feature-architecture is cleaner and more LFG-canonical
    # (Bresnan 2001 §3.5 distinguishes f-structural mood from
    # morphological mood).
    #
    # The matrix-NEG style ``Huwag kumain ang bata.`` is what
    # this rule covers. The control-style ``Huwag kang kumain.``
    # (with addressee + linker + verb) is closed by the new rule
    # right below (Phase 10.final.pre-1).
    rules.append(Rule(
        "S",
        ["PART[MOOD=IMP, POLARITY=NEG]", "S"],
        [
            "(↑) = ↓2",
            "(↑ POLARITY) = 'NEG'",
            "(↑ CLAUSE-MOOD) = 'IMP'",
            # The category pattern matcher is non-conflict
            # (compile.py::matches) — ``PART[MOOD=IMP, POLARITY=NEG]``
            # matches a candidate without MOOD by absorption. Add an
            # explicit constraining equation to actually require
            # MOOD=IMP on the particle (excludes ``hindi``, which
            # has no MOOD).
            "(↓1 MOOD) =c 'IMP'",
        ],
    ))


    # --- Phase 10.final.pre-1: huwag + addressee + linker + AV-V ---
    #
    # Closes the Phase 5e Commit 25 deferral noted above. The
    # explicit-addressee negated-imperative shape
    # ``Huwag kang magmura.`` "Don't swear." was directly
    # provided by the 2026-06-03 native-informant panel as the
    # canonical AV-imperative form (S&O 1972 §8 also documents
    # the linker-fused PRON pattern, e.g., ``Huwag kang umalis.``,
    # as the standard variant; the no-linker form ``Huwag ka
    # kumain.`` is licit but less natural).
    #
    # Daughter shape (4 daughters after ``split_linker_ng`` runs
    # in the text-prep pipeline and decomposes ``kang`` → ``ka`` +
    # ``-ng``):
    #
    #   PART[MOOD=IMP, POLARITY=NEG]  PRON[CASE=NOM]  PART[LINK=NG]  V[VOICE=AV]
    #     ↓1 = huwag                  ↓2 = addressee   ↓3 = linker    ↓4 = head V
    #
    # Verb percolation is from ↓4 — the AV verb provides PRED +
    # a-structure. The addressee PRON becomes matrix SUBJ via
    # ``(↑ SUBJ) = ↓2`` (the imperative subject IS the addressee
    # in 2nd-person imperatives). The linker daughter carries no
    # f-structure content. ``CLAUSE-MOOD=IMP`` + ``POLARITY=NEG``
    # mirror the matrix-NEG rule above; ``(↓1 MOOD) =c 'IMP'``
    # excludes ``hindi`` (which has no MOOD).
    #
    # AV-only restriction: Tagalog 2nd-person imperatives use the
    # bare AV form (``um-`` or ``mag-`` INF / CTPL), not OV/DV/IV
    # forms — the addressee-controlled SUBJ slot aligns with AV
    # actor-pivot. OV imperatives (``Murahin mo siya.``) use a
    # different surface shape (``mo`` for 2sg.GEN, no ``huwag``).
    rules.append(Rule(
        "S",
        [
            "PART[MOOD=IMP, POLARITY=NEG]",
            "PRON[CASE=NOM]",
            "PART[LINK=NG]",
            "V[VOICE=AV]",
        ],
        [
            "(↑) = ↓4",
            "(↑ POLARITY) = 'NEG'",
            "(↑ CLAUSE-MOOD) = 'IMP'",
            "(↑ SUBJ) = ↓2",
            "(↓1 MOOD) =c 'IMP'",
            "(↓3 LINK) =c 'NG'",
        ],
    ))


    # --- Phase 10.final.pre-1: huwag-imperative paradigm fills ---
    #
    # User directive 2026-06-03 (anti-deferral + add unattested
    # constructs): close all the related huwag-imperative variants
    # that came up while shipping the curse-`mura` paradigm + the
    # addressee-NOM-AV rule above. Per S&O 1972 §8 these all
    # belong to the same negated-imperative paradigm family.
    #
    # Variant A: huwag + addressee-NOM + linker + ADJ-predicative.
    # ``Huwag kang malungkot.`` "Don't be sad." / ``Huwag kang
    # masama.`` "Don't be bad." — the addressee is told not to BE
    # a certain way. Same shape as the V[VOICE=AV] rule above but
    # with the predicate slot filled by an ADJ[PREDICATIVE].
    rules.append(Rule(
        "S",
        [
            "PART[MOOD=IMP, POLARITY=NEG]",
            "PRON[CASE=NOM]",
            "PART[LINK=NG]",
            "ADJ[PREDICATIVE]",
        ],
        [
            "(↑) = ↓4",
            "(↑ POLARITY) = 'NEG'",
            "(↑ CLAUSE-MOOD) = 'IMP'",
            "(↑ SUBJ) = ↓2",
            "(↓1 MOOD) =c 'IMP'",
            "(↓3 LINK) =c 'NG'",
        ],
    ))


    # --- Phase 11.X: bare ``Huwag + V[VOICE=AV]`` PRO injection ---
    #
    # Closes the bare-imperative form (e.g. ``Huwag kumain.``,
    # ``Huwag manigarilyo.``, ``Huwag kumain ng aso.``). The
    # bare-V form is the sign-language / prohibition-sign style
    # documented in S&O 1972 §8.2 — addressee is implicit (no
    # overt ``ka`` / ``kayo``).
    #
    # **Design choice** (audit doc §3.5 alternative (a)): impersonal
    # PRO ``(↑ SUBJ PRED) = 'PRO'`` synthesizes a generic addressee
    # placeholder. Mirrors the Class-1 impersonal pattern from
    # ``docs/fu-extension-audit.md`` Appendix C (per-instance PRO
    # classification). The discourse-anchored-addressee alternative
    # (b) would require a new discourse-level f-structure machinery
    # not currently in tgllfg — out of scope.
    #
    # Two rule variants:
    #
    #   (a) Bare V[AV]: ``Huwag kumain.``, ``Huwag manigarilyo.``,
    #       ``Huwag kumanta.``. Both INTR verbs (manigarilyo) and
    #       TR verbs used absolutively (kumain) qualify — the V's
    #       a-structure completeness is satisfied for INTR by the
    #       SUBJ=PRO injection, and for TR by AV's absolutive
    #       reading (the OBJ slot stays absorbed at the LMT layer,
    #       per the same convention as standalone-V imperatives).
    #   (b) V[AV] + GEN-OBJ: ``Huwag kumain ng aso.`` — the GEN-NP
    #       binds to OBJ; SUBJ still PRO.
    #
    # **No DAT/sa-OBL variant** — pre-existing gap in the bare-V
    # frame (``Pumunta sa Maynila.`` doesn't parse standalone
    # either), out of scope for 11.X.
    #
    # **Reference**: Schachter & Otanes 1972 §8.2 (negative
    # imperatives without overt addressee); ``docs/fu-extension-
    # audit.md`` §3.5 (Phase 11 carry-forward backlog).
    rules.append(Rule(
        "S",
        [
            "PART[MOOD=IMP, POLARITY=NEG]",
            "V[VOICE=AV]",
        ],
        [
            "(↑) = ↓2",
            "(↑ POLARITY) = 'NEG'",
            "(↑ CLAUSE-MOOD) = 'IMP'",
            "(↑ SUBJ PRED) = 'PRO'",
            "(↓1 MOOD) =c 'IMP'",
        ],
    ))
    rules.append(Rule(
        "S",
        [
            "PART[MOOD=IMP, POLARITY=NEG]",
            "V[VOICE=AV]",
            "NP[CASE=GEN]",
        ],
        [
            "(↑) = ↓2",
            "(↑ POLARITY) = 'NEG'",
            "(↑ CLAUSE-MOOD) = 'IMP'",
            "(↑ SUBJ PRED) = 'PRO'",
            "(↑ OBJ) = ↓3",
            "(↓1 MOOD) =c 'IMP'",
        ],
    ))


    # Variant B: huwag + GEN-actor + linker + S (with inner V[OV]).
    # ``Huwag mong murahin si Maria.`` "Don't curse Maria." —
    # the negated OV imperative, parallel to the positive OV
    # imperative ``Murahin mo siya.`` (which already parses as a
    # standalone S). The matrix wrap supplies the GEN-actor via
    # ``(↑ OBJ-AGENT) = ↓2`` and inherits the inner S's PRED +
    # SUBJ (the NOM-patient already bound inside). The ``=c``
    # voice constraint excludes AV inner (AV's actor is already
    # the SUBJ, not an OBJ-AGENT slot — that case is handled by
    # the NOM-addressee variant above).
    for non_av in ("OV", "DV", "IV"):
        rules.append(Rule(
            "S",
            [
                "PART[MOOD=IMP, POLARITY=NEG]",
                "PRON[CASE=GEN]",
                "PART[LINK=NG]",
                "S",
            ],
            [
                "(↑) = ↓4",
                "(↑ OBJ-AGENT) = ↓2",
                "(↑ POLARITY) = 'NEG'",
                "(↑ CLAUSE-MOOD) = 'IMP'",
                "(↓1 MOOD) =c 'IMP'",
                "(↓3 LINK) =c 'NG'",
                f"(↓4 VOICE) =c '{non_av}'",
            ],
        ))


    # --- Phase 5n.C Commit 2 (§18 L78): wide-scope hindi over coord-NP ---
    #
    # ``Hindi [si Maria at si Juan] kumain.`` "Neither Maria nor Juan
    # ate" — ``hindi`` at the matrix left edge takes scope over a
    # coordinated NOM SUBJ that precedes the AV-intransitive verb.
    # The reading is wide-scope: ``¬(eat(M) ∧ eat(J))`` for AND-coord,
    # ``¬(eat(M) ∨ eat(J))`` for OR-coord — both equivalent to
    # "neither one" by De Morgan.
    #
    # Two rules generated (parameterized over COORD value): the
    # AND-coord variant fires on ``si Maria at si Juan``-style
    # coord-SUBJ, the OR-coord variant on ``si Maria o si Juan``.
    # Both produce ``NEG_SCOPE=WIDE`` on the matrix S to mark the
    # wide reading (per design appendix in
    # ``docs/analysis-choices.md`` — Phase 5n.C Commit 1).
    #
    # Daughter shape:
    #
    #   PART[POLARITY=NEG] NP[CASE=NOM, COORD=Y] V[VOICE=AV]
    #     ↓1 = hindi (POLARITY=NEG, no MOOD — excludes huwag)
    #     ↓2 = coord-SUBJ (matrix SUBJ; binds via ``(↑ SUBJ) = ↓2``)
    #     ↓3 = AV-intransitive verb (head; verb percolation from ↓3)
    #
    # Verb percolation is from ↓3 here (not ↓1 as in the canonical
    # ``_VERB_PERCOLATION`` shape from ``_helpers.py``) — the
    # PART-NP-V daughter order has the verb in third position. The
    # ``(↑ NEG_SCOPE) = 'WIDE'`` equation marks the matrix
    # explicitly; downstream consumers / Phase 6+ Glue work pattern-
    # match on this to derive the wide-scope semantics. The default
    # narrow-scope reading (Phase 4 §7.2 hindi-wrap above) leaves
    # NEG_SCOPE absent on the matrix, encoding "default narrow / no
    # relevant coord interaction" without explicit marker.
    #
    # ``(↓2 COORD) =c '<value>'`` is the chart-level filter that
    # selects the coord-SUBJ; ``(↓1 POLARITY) =c 'NEG'`` excludes
    # non-NEG PARTs (mismo, etc.) per the Phase 5h Commit 3 belt-
    # and-braces convention; ``¬ (↓1 MOOD)`` excludes ``huwag``
    # (which carries MOOD=IMP) — wide-scope imperative-negation
    # over coord-NP is a separate construction and not in scope
    # for this commit.
    #
    # Phase 5k Commit 8 asymmetric coord (``Si Maria, hindi si
    # Juan``) is structurally distinct: ``hindi`` appears in
    # third position as the asymmetric connective, not at left
    # edge, and produces ``COORD=BUT_NOT`` on the coord-NP. The
    # new wide-scope rule fires only on ``COORD=AND`` / ``OR``,
    # so no overlap.
    #
    # Reference: Schachter & Otanes 1972 §10 (negation × coord);
    # Ramos & Bautista 1986 ch.18; ``docs/analysis-choices.md``
    # "Phase 5n.C Commit 1" design appendix.
    for coord_value in ("AND", "OR"):
        rules.append(Rule(
            "S",
            [
                "PART[POLARITY=NEG]",
                f"NP[CASE=NOM, COORD={coord_value}]",
                "V[VOICE=AV]",
            ],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ VOICE) = ↓3 VOICE",
                "(↑ ASPECT) = ↓3 ASPECT",
                "(↑ MOOD) = ↓3 MOOD",
                "(↑ LEX-ASTRUCT) = ↓3 LEX-ASTRUCT",
                "(↑ POLARITY) = 'NEG'",
                "(↑ NEG_SCOPE) = 'WIDE'",
                "(↑ SUBJ) = ↓2",
                "(↓1 POLARITY) =c 'NEG'",
                "¬ (↓1 MOOD)",
                f"(↓2 COORD) =c '{coord_value}'",
            ],
        ))
