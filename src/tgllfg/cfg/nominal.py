# tgllfg/cfg/nominal.py

"""NP rules: determiners, possessives, demonstratives, quantifiers.

Holds every grammar rule whose left-hand side is an ``NP[CASE=...]``
or ``N`` non-terminal. After the post-Phase-5f grammar split (see
``docs/refactor-grammar-package.md``) this module owns:

* NP shells (case from determiner / personal-name marker; demonstrative
  deixis lift)
* Standalone demonstrative pronouns
* Post-modifier and pre-modifier demonstratives
* Cardinal / ordinal NP-internal modifiers
* NP-internal possessive (``ng``-NP wrap)
* Pre-NP partitive (``Q + NP[GEN]``)
* Vague-cardinal / universal (``bawat`` / ``kada``) /
  distributive-possessive / wholes (``buo`` / ``buong``) modifiers
* Measure-N (Group H2 item 4)
* Decimal-cardinal NUM rule
* ``mga`` time approximation
* Approximators (Group H1 item 2)
* Numeric-comparator frames (Group H1 item 3)
* Minute composition (Group E item 4)
* N from NOUN (toy PRED projection)

The ``register_rules`` function appends rules in source order. The
composer in :mod:`tgllfg.cfg.grammar` calls this registrar first
(before clause / clitic / negation / extraction / control / discourse
registrars) — see the plan's "Migration strategy" §H.

The private ``_cardinal_case_marker`` dict is consumed by six
NP-modifier rule groups (cardinal Commit 1, ordinal Commit 7,
vague-Q Commit 15, universal Commit 20, distrib-poss Commit 21,
whole Commit 22). Promoted from a local in the original cardinal
section to a module-level constant per the plan's risk note.
"""

from __future__ import annotations

from ._helpers import _eqs
from .grammar import Rule

# Used by six NP-modifier rule groups — promoted from a local
# definition in the original cardinal section.
_cardinal_case_marker: dict[str, str] = {
    "NOM": "DET[CASE=NOM]",
    "GEN": "ADP[CASE=GEN]",
    "DAT": "ADP[CASE=DAT]",
}


def register_rules(rules: list[Rule]) -> None:
    """Append the NP-area rules in source order."""
    # --- NP shells (case from determiner / personal-name marker) ---
    #
    # Phase 4 §7.8: ``(↑) = ↓1`` shares the NP's f-structure with
    # the determiner / case-marker token, so the DET/ADP's lex
    # features (CASE, MARKER, DEIXIS for demonstratives) all
    # surface on the NP. The toy noun PRED is overlaid via the
    # explicit PRED equation. This is a no-op for non-demonstrative
    # determiners (no DEIXIS feature; CASE/MARKER stay consistent
    # with the rule's case constraint) and lifts demonstrative
    # deixis onto the matrix without per-deixis rule explosion.
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["DET[CASE=NOM]", "N"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = ↓2 PRED",
            "(↑ LEMMA) = ↓2 LEMMA",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["ADP[CASE=GEN]", "N"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = ↓2 PRED",
            "(↑ LEMMA) = ↓2 LEMMA",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT]", "N"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = ↓2 PRED",
            "(↑ LEMMA) = ↓2 LEMMA",
        ],
    ))


    # --- Phase 5i Commit 3: in-situ wh-PRON in case-marked NP ---
    #
    # ``Kumain ka ng ano?``    "You ate (some) what?" (echo / casual)
    # ``Bumili ka ng ano?``    "You bought (some) what?"
    # ``Sumulat ka kay kanino?`` "You wrote to whom?"
    #
    # The Phase 5i Commit 1 wh-PRONs (``sino`` / ``ano`` / ``alin`` /
    # ``kanino``) carry their lex-declared CASE (NOM for the first
    # three; DAT for kanino). Cleft-style fronting (Commit 2) consumes
    # them in NOM-pivot position; in-situ wh appears in case-marked
    # argument position, requiring an ADP wrapper. These two shell
    # rules admit ``ng + PRON[WH=YES]`` → NP[CASE=GEN] and
    # ``sa/kay + PRON[WH=YES]`` → NP[CASE=DAT].
    #
    # Without these rules, ``Kumain ka ng ano?`` fails: the existing
    # NP[CASE=GEN] shell expects an N (NOUN-headed) daughter, not a
    # PRON; and the PRON-only shell ``NP[CASE=NOM] → PRON[CASE=NOM]``
    # produces NOM, not GEN. The wh-PRONs are NP-fillers in disguise
    # — case-flexible when wrapped with the appropriate marker.
    #
    # F-structure shape: matrix shares the ADP's f-structure
    # (``(↑) = ↓1`` so CASE comes from the wrapper); matrix gets a
    # synthesized PRED (parallels Phase 4 §7.8 standalone-dem PRED:
    # 'PRO'). The wh-feature lifts onto the matrix so downstream
    # consumers can read ``(↑ WH) = 'YES'`` off any in-situ wh-NP
    # without traversing into the PRON daughter.
    #
    # The matrix-level Q_TYPE lift (marking the whole sentence as a
    # wh-Q when any in-situ wh-NP appears) is deferred — it requires
    # either a post-parse f-structure walk or a defining equation in
    # every V-headed S frame; the latter is invasive. For Commit 3
    # the in-situ form parses; Q_TYPE percolation lands as a Phase 5i
    # follow-on if corpus pressure demands it.
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["ADP[CASE=GEN]", "PRON[WH=YES]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = 'WH-PRO'",
            "(↑ WH) = ↓2 WH",
            "(↑ WH_LEMMA) = ↓2 LEMMA",
            "(↓2 WH) =c 'YES'",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT]", "PRON[WH=YES]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = 'WH-PRO'",
            "(↑ WH) = ↓2 WH",
            "(↑ WH_LEMMA) = ↓2 LEMMA",
            "(↓2 WH) =c 'YES'",
        ],
    ))


    # --- Phase 4 §7.8: standalone demonstrative pronouns ---
    #
    # ``Kumain iyon`` ("That one ate"). The demonstrative serves
    # as a pronominal NP without a head noun. ``DEM=YES`` on the
    # token (set in particles.yaml) gates these rules so plain
    # determiners (``ang``, ``ng``, ``sa``, ``si``, ``ni``,
    # ``kay``) don't accidentally form a bare NP. The PRED is
    # synthesized as ``'PRO'`` so the resulting f-structure
    # passes completeness when the demonstrative serves as SUBJ
    # / OBJ of a verb.
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["DET[CASE=NOM, DEM=YES]"],
        ["(↑) = ↓1", "(↑ PRED) = 'PRO'"],
    ))
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["ADP[CASE=GEN, DEM=YES]"],
        ["(↑) = ↓1", "(↑ PRED) = 'PRO'"],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT, DEM=YES]"],
        ["(↑) = ↓1", "(↑ PRED) = 'PRO'"],
    ))


    # --- Phase 5d Commit 3: post-modifier demonstrative -----------
    #
    # ``ang batang ito`` ("this child"). The demonstrative
    # follows the head NP via the linker (`-ng` after vowel-
    # final hosts, `na` after consonant-final). Three case
    # variants × two linker variants. The demonstrative agrees
    # with the head in case: NOM-marked dems are DET (ito,
    # iyan, iyon); GEN/DAT are ADP (nito/dito, niyan/diyan,
    # niyon/doon). The matrix shares the head NP's f-structure
    # via ``(↑) = ↓1``; the demonstrative's DEIXIS feature is
    # copied via ``(↑ DEIXIS) = ↓3 DEIXIS``. PRED stays the
    # head noun's PRED — the demonstrative modifies, doesn't
    # supplant.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "NP[CASE=NOM]",
            [
                "NP[CASE=NOM]",
                f"PART[LINK={link}]",
                "DET[CASE=NOM, DEM=YES]",
            ],
            _eqs(
                "(↑) = ↓1",
                "(↑ DEIXIS) = ↓3 DEIXIS",
            ),
        ))
        rules.append(Rule(
            "NP[CASE=GEN]",
            [
                "NP[CASE=GEN]",
                f"PART[LINK={link}]",
                "ADP[CASE=GEN, DEM=YES]",
            ],
            _eqs(
                "(↑) = ↓1",
                "(↑ DEIXIS) = ↓3 DEIXIS",
            ),
        ))
        rules.append(Rule(
            "NP[CASE=DAT]",
            [
                "NP[CASE=DAT]",
                f"PART[LINK={link}]",
                "ADP[CASE=DAT, DEM=YES]",
            ],
            _eqs(
                "(↑) = ↓1",
                "(↑ DEIXIS) = ↓3 DEIXIS",
            ),
        ))


    # --- Phase 5e Commit 16: pre-modifier demonstrative -----------
    #
    # ``itong bata`` ("this child"). The demonstrative
    # precedes the head N via the linker. PROX dems
    # (``ito`` / ``nito`` / ``dito``) are vowel-final and
    # take the bound ``-ng`` linker (``itong`` is split by
    # ``split_linker_ng`` into ``ito`` + ``-ng``); MED dems
    # (``iyan`` / ``niyan`` / ``diyan``) and DIST dems
    # (``iyon`` / ``niyon`` / ``doon``) are consonant-final
    # and take the standalone ``na`` linker. Three cases ×
    # two linker variants = six rules.
    #
    # Unlike the post-modifier rule (where the head NP
    # carries its own case marker like ``ang``), the pre-
    # modifier dem replaces the case marker — the dem itself
    # is the determiner. The matrix shares the dem's
    # f-structure via ``(↑) = ↓1`` (CASE / MARKER / DEIXIS
    # percolate); the head's PRED + LEMMA project from N via
    # ``(↑ PRED) = ↓3 PRED`` and ``(↑ LEMMA) = ↓3 LEMMA``.
    # This is structurally the mirror of Phase 5d Commit 3.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "NP[CASE=NOM]",
            [
                "DET[CASE=NOM, DEM=YES]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑) = ↓1",
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
            ],
        ))
        rules.append(Rule(
            "NP[CASE=GEN]",
            [
                "ADP[CASE=GEN, DEM=YES]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑) = ↓1",
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
            ],
        ))
        rules.append(Rule(
            "NP[CASE=DAT]",
            [
                "ADP[CASE=DAT, DEM=YES]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑) = ↓1",
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
            ],
        ))


    # --- Phase 5f Commit 1: cardinal NP-internal modifier --------
    #
    # ``ang isang bata`` ("the one child"), ``ng tatlong libro``
    # ("of three books"), ``sa apat na bata`` ("to four
    # children"). The cardinal sits between the case marker and
    # the head N via the linker — bound ``-ng`` after vowel-final
    # cardinals (split off by ``split_linker_ng`` once the
    # cardinal stems are known surfaces) or standalone ``na``
    # after consonant-final cardinals (apat, anim, siyam). The
    # standalone ``na`` after a NUM[CARDINAL=YES] is
    # disambiguated as the linker (not the ALREADY enclitic) by
    # ``disambiguate_homophone_clitics`` — see
    # ``src/tgllfg/clitics/placement.py``.
    #
    # 6 rules total = 3 cases × 2 linker variants. Each rule
    # produces NP directly so the cardinal's NUM and
    # CARDINAL_VALUE land on the matrix NP without needing to
    # widen the bare ``NP[CASE=X] → DET/ADP[CASE=X] N``
    # projection (which would create empty f-structs for the
    # bare-N path).
    #
    # Chained cardinals (``*ng tatlong dalawang bata``) are
    # blocked by the rule shape — the rightmost daughter is N,
    # not NP, so a second cardinal cannot wrap a cardinal-
    # modified NP. (Cardinal coordination is a separate
    # construction; lands with Group C mixed numbers / Phase 5k.)
    for case, marker in _cardinal_case_marker.items():
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [
                    marker,
                    "NUM[CARDINAL=YES]",
                    f"PART[LINK={link}]",
                    "N",
                ],
                [
                    "(↑) = ↓1",
                    "(↑ PRED) = ↓4 PRED",
                    "(↑ LEMMA) = ↓4 LEMMA",
                    "(↑ NUM) = ↓2 NUM",
                    "(↑ CARDINAL_VALUE) = ↓2 CARDINAL_VALUE",
                    "¬ (↓4 CARDINAL_VALUE)",
                    # Constraining: enforce the daughter is actually
                    # CARDINAL=YES, not just any NUM. Without this,
                    # ORDINAL=YES NUMs (Phase 5f Commit 7) match by
                    # non-conflict (no shared CARDINAL key) and
                    # produce empty CARDINAL_VALUE fstructs on the
                    # matrix NP. Same fix-pattern as Commit 6's
                    # PART[DECIMAL_SEP=YES] constraint.
                    "(↓2 CARDINAL) =c 'YES'",
                ],
            ))
    # An N-level companion rule for bare cardinal-N use
    # (no case marker): the parang-comparative standard
    # (``parang isang aso`` "like one dog" — Phase 5e Commit 26)
    # and future predicative-cardinal contexts (Phase 5f Group A
    # item 4) consume bare N. The N-level rule shares head N's
    # PRED + LEMMA into the matrix N; CARDINAL_VALUE rides on
    # this matrix N and is visible to consumers (parang's OBJ).
    # The chained-cardinal block lives here as
    # ``¬ (↓3 CARDINAL_VALUE)`` since this rule allows recursive
    # composition; the NP-level rules above are structurally
    # blocked because their head daughter is N (not NP), but a
    # bare-N chain would otherwise compose without the explicit
    # constraint.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N",
            [
                "NUM[CARDINAL=YES]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ NUM) = ↓1 NUM",
                "(↑ CARDINAL_VALUE) = ↓1 CARDINAL_VALUE",
                "¬ (↓3 CARDINAL_VALUE)",
                "(↓1 CARDINAL) =c 'YES'",
            ],
        ))


    # --- Phase 5f Commit 7: ordinal NP-internal modifier ---------
    #
    # ``ang unang anak`` ("the first child"), ``ng ikalawang
    # libro`` ("of the second book"), ``sa ikaapat na bahay``
    # ("at the fourth house"). Structurally parallel to the
    # Commit 1 cardinal-NP-modifier rules: 6 NP-level rules
    # (3 cases × 2 linker variants). The ordinal contributes
    # ``ORDINAL_VALUE`` to the matrix NP; PRED and LEMMA
    # percolate from the head N. Unlike cardinals, ordinals do
    # NOT contribute ``NUM`` — ordinal value is independent of
    # noun number agreement (``ang unang aklat`` 1st-SG;
    # ``ang unang mga aklat`` 1st-PL with mga marker).
    #
    # The constraint ``¬ (↓4 ORDINAL_VALUE)`` blocks chained
    # ordinals (``*ang unang ikalawang aklat``) parallel to
    # the cardinal chained-blocking. Mixed ordinal + cardinal
    # (``ang unang dalawang aklat`` "the first two books") is
    # likewise blocked at NP level by the rule shape — the
    # head daughter is bare N, not a cardinal-modified N.
    # That construction is grammatically valid in Tagalog but
    # requires an ordinal-of-cardinal stacking rule; deferred.
    for case, marker in _cardinal_case_marker.items():
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [
                    marker,
                    "NUM[ORDINAL=YES]",
                    f"PART[LINK={link}]",
                    "N",
                ],
                [
                    "(↑) = ↓1",
                    "(↑ PRED) = ↓4 PRED",
                    "(↑ LEMMA) = ↓4 LEMMA",
                    "(↑ ORDINAL_VALUE) = ↓2 ORDINAL_VALUE",
                    "¬ (↓4 ORDINAL_VALUE)",
                    # Constraining: enforce daughter is actually
                    # ORDINAL=YES (parallel to the cardinal rule's
                    # ``(↓2 CARDINAL) =c 'YES'`` — the non-conflict
                    # matcher would otherwise match CARDINAL=YES
                    # NUMs and create empty ORDINAL_VALUE fstructs).
                    "(↓2 ORDINAL) =c 'YES'",
                ],
            ))


    # --- Phase 4 §7.8: NP-internal possessive ---
    #
    # ``ang aklat ng bata`` ("the child's book") and pronominal
    # ``ang aklat ko`` ("my book"). The GEN-NP modifier attaches
    # at the right edge of the head NP and rides into the head's
    # f-structure as ``POSS``. Recursive: ``ang aklat ng pamilya
    # ng bata`` ("the child's family's book") — but the binding
    # is left-associative: each layer of POSS sits above the
    # previous head NP.
    #
    # **Constraint**: ``¬ (↑ POSS-EXTRACTED)`` blocks this rule
    # from firing on an NP whose POSS slot was already filled by
    # the Phase 5d Commit 6 / Phase 5e Commit 18 dual-binding
    # wrap rule (``aklat ko na kinain``), where the pronominal
    # actor of an embedded RC was hoisted out as POSS. Without
    # the guard, surfaces like ``Tumakbo ang bata ko na kinain
    # ng aso`` produce a spurious parse where this rule fires on
    # ``[bata ko na kinain] ng aso``, unifying ``ko`` and
    # ``aso`` into a hybrid POSS=OBJ-AGENT fstruct (``ko`` has
    # no LEMMA so ``aso``'s LEMMA wins; ``aso`` has no NUM so
    # ``ko``'s NUM=SG wins; CASE=GEN matches). The wrap rule
    # marks its output with POSS-EXTRACTED=YES; the constraint
    # rejects the NP-poss extension on such NPs. Legitimate
    # iterated possessives are right-associative (the inner
    # NP-poss application doesn't set POSS-EXTRACTED), so
    # ``aklat ng bata ng pamilya`` is unaffected.
    for case in ("NOM", "GEN", "DAT"):
        rules.append(Rule(
            f"NP[CASE={case}]",
            [f"NP[CASE={case}]", "NP[CASE=GEN]"],
            ["(↑) = ↓1", "(↑ POSS) = ↓2", "¬ (↑ POSS-EXTRACTED)"],
        ))

    # Pronominal NPs: case carried on PRON itself.
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["PRON[CASE=NOM]"],
        ["(↑) = ↓1"],
    ))
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["PRON[CASE=GEN]"],
        ["(↑) = ↓1"],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["PRON[CASE=DAT]"],
        ["(↑) = ↓1"],
    ))


    # --- Phase 5b §7.8 follow-on: pre-NP partitive (Q + NP[GEN]) ---
    #
    # ``ang lahat ng bata`` ("all of the children"). The
    # quantifier ``lahat`` (or ``iba``) sits between the outer
    # case marker and the inner GEN-marked complement; the
    # complement supplies the head's PRED, the outer marker
    # supplies CASE, and the Q rides as a ``QUANT`` atom on
    # the resulting NP. Phase 4 §7.8 deferred this form
    # ("Pre-NP partitive usage ... needs a QP non-terminal");
    # the cleaner solution turned out to be a flat 3-child rule
    # rather than a separate QP non-terminal, since the inner
    # NP[GEN] already exists in the grammar.
    #
    # The equation pattern ``(↑) = ↓1`` shares the outer NP's
    # f-structure with the DET/ADP (so CASE + MARKER come from
    # the outer marker); ``(↑ PRED) = ↓3 PRED`` overlays the
    # head from the inner NP; ``(↑ QUANT) = ↓2 QUANT`` lifts
    # the quantifier atom onto the NP. The inner NP[GEN] is
    # preserved as its own sub-projection (CASE=GEN there,
    # CASE=NOM on the outer); only its PRED value is borrowed.
    #
    # Phase 5f Commit 15 follow-on: ``¬ (↓2 VAGUE)`` blocks the
    # vague cardinals (``marami``, ``ilan``, etc.) from this
    # GEN-NP partitive — they take the linker form only
    # (``maraming bata``, not ``*marami ng bata``). The DAT-NP
    # partitive variant of vague cardinals (``marami sa
    # kanila`` "many of them") is a separate construction
    # deferred for now.
    #
    # Phase 5f Commit 20 follow-on: ``¬ (↓2 UNIV)`` similarly
    # blocks the universals (``bawat``, ``kada``) — they take
    # a bare-N complement, not GEN-NP. (``*ang bawat ng bata``
    # is non-standard.)
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["DET[CASE=NOM]", "Q", "NP[CASE=GEN]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = ↓3 PRED",
            "(↑ QUANT) = ↓2 QUANT",
            "¬ (↓2 VAGUE)",
            "¬ (↓2 UNIV)",
            "¬ (↓2 DISTRIB_POSS)",
            "¬ (↓2 WHOLE)",
            "¬ (↓2 DUAL)",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["ADP[CASE=GEN]", "Q", "NP[CASE=GEN]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = ↓3 PRED",
            "(↑ QUANT) = ↓2 QUANT",
            "¬ (↓2 VAGUE)",
            "¬ (↓2 UNIV)",
            "¬ (↓2 DISTRIB_POSS)",
            "¬ (↓2 WHOLE)",
            "¬ (↓2 DUAL)",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT]", "Q", "NP[CASE=GEN]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = ↓3 PRED",
            "(↑ QUANT) = ↓2 QUANT",
            "¬ (↓2 VAGUE)",
            "¬ (↓2 UNIV)",
            "¬ (↓2 DISTRIB_POSS)",
            "¬ (↓2 WHOLE)",
            "¬ (↓2 DUAL)",
        ],
    ))


    # --- Phase 5f Commit 15: vague cardinal NP-internal modifier ---
    #
    # ``ang maraming bata`` "many children", ``ng kaunting
    # tubig`` "of a little water", ``sa iilan na aklat`` "to a
    # few books". The vague-cardinal Q sits between the case
    # marker and the head N via the linker, mirroring the
    # Phase 5f Commit 1 cardinal-NP-modifier rule (the plan
    # §11.1 Group H description literally calls Group H rules
    # "the Group A cardinal-NP-modifier rule generalised to any
    # NUM / Q head" — this commit lands the Q variant).
    #
    # Unlike the cardinal rule, the daughter doesn't contribute
    # CARDINAL_VALUE; it contributes ``QUANT`` (MANY / FEW /
    # VERY_FEW / MOST) and ``VAGUE=YES`` rides up to the matrix
    # NP for the LMT classifier and downstream consumers. The
    # constraining equation ``(↓2 VAGUE) =c 'YES'`` enforces
    # the daughter is actually a vague Q (lahat / iba would
    # otherwise match by non-conflict on the absence of CARDINAL
    # / ORDINAL / VAGUE).
    #
    # 6 NP-level rules = 3 cases × 2 linker variants. Chained
    # vague Qs (``*ang maraming maraming bata``) are blocked by
    # ``¬ (↓4 VAGUE)`` parallel to the cardinal rule's
    # ``¬ (↓4 CARDINAL_VALUE)``.
    for case, marker in _cardinal_case_marker.items():
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [
                    marker,
                    "Q",
                    f"PART[LINK={link}]",
                    "N",
                ],
                [
                    "(↑) = ↓1",
                    "(↑ PRED) = ↓4 PRED",
                    "(↑ LEMMA) = ↓4 LEMMA",
                    "(↑ QUANT) = ↓2 QUANT",
                    "(↑ VAGUE) = 'YES'",
                    "¬ (↓4 VAGUE)",
                    "(↓2 VAGUE) =c 'YES'",
                ],
            ))

    # N-level companion rule (parang etc.). Mirrors the Phase 5f
    # Commit 1 N-level cardinal rule — produces N (not NP) for
    # consumers that compose at N level (e.g., the Phase 5e
    # Commit 26 ``parang isang aso`` rule selects an N
    # daughter). Chained-vague-Q blocking via ``¬ (↓3 VAGUE)``
    # parallel to the NP-level rule.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N",
            [
                "Q",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ QUANT) = ↓1 QUANT",
                "(↑ VAGUE) = 'YES'",
                "¬ (↓3 VAGUE)",
                "(↓1 VAGUE) =c 'YES'",
            ],
        ))


    # --- Phase 5i Commit 6: wh-Q + N companion (wh-N for cleft) ---
    #
    # ``aling bata`` "which child" — wh-Q-modified N. The Phase 5f
    # Commit 15 vague-Q N-level companion above lifts QUANT and
    # VAGUE but not WH; non-wh Qs (lahat / iba / marami / etc.)
    # don't carry WH so a single rule with ``(↑ WH) = ↓1 WH`` would
    # create an empty FStructure on matrix WH for them (same
    # baseline-perturbation pattern Phase 5i Commit 5 closed by
    # splitting into two parallel rules).
    #
    # This wh-Q variant constrains on ``Q[VAGUE=YES, WH=YES]`` so
    # it fires only on Phase 5i wh-Q heads (``alin`` / ``ilan``-WH
    # / ``magkano``). The matrix N gets WH=YES + WH_LEMMA from the
    # Q daughter, on top of the QUANT / VAGUE lifts the non-wh rule
    # already provides. Phase 5i Commit 6's wh-N-cleft rule (in
    # cfg/clause.py) consumes the resulting N[WH=YES].
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N",
            [
                "Q[VAGUE=YES, WH=YES]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ QUANT) = ↓1 QUANT",
                "(↑ VAGUE) = 'YES'",
                "(↑ WH) = 'YES'",
                "(↑ WH_LEMMA) = ↓1 LEMMA",
                "¬ (↓3 VAGUE)",
                "(↓1 VAGUE) =c 'YES'",
                "(↓1 WH) =c 'YES'",
            ],
        ))


    # --- Phase 5f Commit 20: universal `bawat` / `kada`
    # NP-internal modifier (Group H2 item 6) ---------------------
    #
    # ``bawat bata`` "every child", ``kada bata`` "every child"
    # (colloquial), ``ang bawat bata`` "the every child", ``sa
    # bawat bata`` "to every child". Universal Q heads take a
    # bare N complement (no linker, no DET between Q and N).
    # Plan §11.1 Group H item 6 (S&O 1972 §4.7).
    #
    # 4 rules total: 3 case-marked variants
    # (``DET/ADP[CASE=X] Q[UNIV=YES] N``) plus 1 bare-NOM
    # variant (``Q[UNIV=YES] N``). The bare-NOM rule covers
    # ``Bawat bata ay kumakain.`` "Every child eats." style
    # surfaces where bawat itself functions as the determiner-
    # equivalent.
    #
    # The constraining equation ``(↓N UNIV) =c 'YES'`` gates
    # the rule to universal Q heads — non-universal Qs
    # (``lahat`` / ``iba`` / vague) match this rule's daughter
    # by non-conflict on the absence of UNIV unless gated.
    # Same fix-pattern as the cardinal / ordinal / vague-Q
    # rules' positive constraint on the daughter feature.
    # ``¬ (↓last UNIV)`` blocks chained universals
    # (``*bawat bawat bata``).
    for case, marker in _cardinal_case_marker.items():
        rules.append(Rule(
            f"NP[CASE={case}]",
            [marker, "Q", "N"],
            [
                "(↑) = ↓1",
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ QUANT) = ↓2 QUANT",
                "(↑ UNIV) = 'YES'",
                "¬ (↓3 UNIV)",
                "(↓2 UNIV) =c 'YES'",
            ],
        ))

    # Bare-NOM rule (universals can stand alone as NPs without
    # a DET — bawat / kada act as their own determiner).
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["Q", "N"],
        [
            "(↑ PRED) = ↓2 PRED",
            "(↑ LEMMA) = ↓2 LEMMA",
            "(↑ QUANT) = ↓1 QUANT",
            "(↑ UNIV) = 'YES'",
            "(↑ CASE) = 'NOM'",
            "¬ (↓2 UNIV)",
            "(↓1 UNIV) =c 'YES'",
        ],
    ))


    # --- Phase 5f Commit 21: distributive-possessive
    # `kani-kaniya` / `kanya-kanya` (Group H3 item 7) ------------
    #
    # ``kanikaniyang ganda`` "each one's beauty",
    # ``kanyakanyang aklat`` "each their own book". A
    # reduplicated possessive Q with distributive force takes a
    # linker + N complement, producing an NP marked with
    # ``DISTRIB_POSS=YES``. Plan §11.1 Group H item 7 (S&O 1972
    # §6.13).
    #
    # Rule shape mirrors Phase 5f Commit 15 vague-Q-modifier:
    # ``DET/ADP Q PART[LINK] N``. The constraining equation
    # ``(↓2 DISTRIB_POSS) =c 'YES'`` gates the rule to
    # kanikaniya / kanyakanya; non-distributive-possessive Q
    # heads (lahat / iba / vague / universal) match by absence
    # without it.
    #
    # Three case-marked variants (NOM / GEN / DAT) × 2 linker
    # variants (NA / NG) = 6 NP-level rules. Plus 1 bare-NOM
    # variant (``Kanyakanyang aklat sila.`` "They each have
    # their own book.") for surfaces where the distributive-
    # possessive Q functions as the determiner-equivalent.
    for case, marker in _cardinal_case_marker.items():
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [marker, "Q", f"PART[LINK={link}]", "N"],
                [
                    "(↑) = ↓1",
                    "(↑ PRED) = ↓4 PRED",
                    "(↑ LEMMA) = ↓4 LEMMA",
                    "(↑ QUANT) = ↓2 QUANT",
                    "(↑ DISTRIB_POSS) = 'YES'",
                    "¬ (↓4 DISTRIB_POSS)",
                    "(↓2 DISTRIB_POSS) =c 'YES'",
                ],
            ))

    # Bare-NOM rule (distributive-possessive Q can stand alone
    # as an NP without a DET — kanyakanya acts as its own
    # determiner-equivalent in the distributive-possessive
    # construction).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "NP[CASE=NOM]",
            ["Q", f"PART[LINK={link}]", "N"],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ QUANT) = ↓1 QUANT",
                "(↑ DISTRIB_POSS) = 'YES'",
                "(↑ CASE) = 'NOM'",
                "¬ (↓3 DISTRIB_POSS)",
                "(↓1 DISTRIB_POSS) =c 'YES'",
            ],
        ))


    # --- Phase 5f closing deferral: generic preposed-possessor
    # (``kanyang aklat`` / ``aking aklat`` / ``kanilang aklat``) -----
    #
    # Common Tagalog NP-internal possessive surface form: a DAT
    # pronoun pre-modifies the head noun via the linker
    # (``kanyang aklat`` "his/her book", ``aming bahay`` "our
    # house", ``kanilang sapatos`` "their shoes"). Structurally
    # parallel to Phase 5f Commit 21 distributive-possessive
    # (``kanikaniyang aklat``) but with a regular DAT pronoun in
    # place of the reduplicated possessive Q. The matrix NP
    # carries ``POSS = ↓2``, mirroring the Phase 4 §7.8 post-N
    # possessive rule's POSS slot for the GEN-NP possessor (cf.
    # ``aklat ng nanay`` "the mother's book").
    #
    # The 1sg / 1pl.excl / 1pl.incl forms (``aking`` /
    # ``aming`` / ``ating``) involve an irregular n-deletion
    # sandhi before the bound ``-ng`` linker; the
    # :func:`split_linker_ng` n-restoration fallback (in
    # ``text/clitics.py``) reconstructs the underlying ``akin`` /
    # ``amin`` / ``atin`` PRON before this rule fires.
    #
    # Three case-marked variants × 2 linker variants = 6 rules,
    # following the Phase 5f Commit 15 vague-Q-modifier template.
    # No bare-NOM variant (the canonical preposed-possessor
    # surface always has a host N which itself needs a determiner
    # in argument position — ``Aking aklat ito.`` is a predicative
    # construction handled by the existing predicative-NP rules).
    for case, marker in _cardinal_case_marker.items():
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [marker, "PRON[CASE=DAT]", f"PART[LINK={link}]", "N"],
                [
                    "(↑) = ↓1",
                    "(↑ PRED) = ↓4 PRED",
                    "(↑ LEMMA) = ↓4 LEMMA",
                    "(↑ POSS) = ↓2",
                    "¬ (↑ POSS-EXTRACTED)",
                ],
            ))


    # --- Phase 5f Commit 22: wholes `buo` / `buong`
    # (Group H3 item 8) -----------------------------------------
    #
    # ``buong bata`` "whole / entire child", ``buong araw``
    # "whole day", ``buong pamilya`` "entire family". A
    # totality Q head takes a linker + N complement, producing
    # an NP marked with ``WHOLE=YES``. Plan §11.1 Group H item
    # 8 (S&O 1972 §4.7).
    #
    # Rule shape mirrors Phase 5f Commit 15 vague-Q-modifier
    # and Commit 21 distributive-possessive: ``DET/ADP Q
    # PART[LINK] N``. The constraining equation
    # ``(↓2 WHOLE) =c 'YES'`` gates the rule to ``buo``;
    # non-WHOLE Q heads (lahat / iba / vague / universal /
    # distributive-possessive) match by absence on WHOLE
    # without it.
    #
    # 6 case-marked variants (3 cases × 2 linker variants —
    # ``buo`` is vowel-final so only the NG variant fires in
    # practice; the NA variant is included for symmetry and
    # to support any future consonant-final WHOLE entries).
    # Plus 2 bare-NOM variants for surfaces like ``Buong araw
    # ay nag-aral siya.``
    for case, marker in _cardinal_case_marker.items():
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [marker, "Q", f"PART[LINK={link}]", "N"],
                [
                    "(↑) = ↓1",
                    "(↑ PRED) = ↓4 PRED",
                    "(↑ LEMMA) = ↓4 LEMMA",
                    "(↑ QUANT) = ↓2 QUANT",
                    "(↑ WHOLE) = 'YES'",
                    "¬ (↓4 WHOLE)",
                    "(↓2 WHOLE) =c 'YES'",
                ],
            ))

    # Bare-NOM rule (totality Q can stand alone as an NP
    # without a DET — ``buong araw`` standalone in ay-fronted
    # position, etc.).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "NP[CASE=NOM]",
            ["Q", f"PART[LINK={link}]", "N"],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ QUANT) = ↓1 QUANT",
                "(↑ WHOLE) = 'YES'",
                "(↑ CASE) = 'NOM'",
                "¬ (↓3 WHOLE)",
                "(↓1 WHOLE) =c 'YES'",
            ],
        ))


    # --- Phase 5f Commit 18: measure-N rule (Group H2 item 4) ---
    #
    # ``dosenang itlog`` "a dozen eggs", ``pares na sapatos``
    # "pair of shoes" (uncardinal), ``daandaan na aklat``
    # "hundreds of books", ``libulibong tao`` "thousands of
    # people". A measure / collective NOUN attaches to a
    # measured-N complement via the linker, producing N. The
    # output's PRED + LEMMA come from the measured (right-
    # hand) N; the measure NOUN's lemma rides as
    # ``MEASURE_HEAD``. ``MEASURE='YES'`` propagates upward
    # for downstream consumers.
    #
    # Plan §11.1 Group H item 4: pares takes a GEN-NP
    # complement (``isang pares ng sapatos``) AND a linker
    # complement; dosena uses the linker form
    # (``isang dosenang itlog``); reduplicated daandaan /
    # libulibo are described as taking a GEN complement.
    # The GEN form composes via existing rules (Phase 5f
    # Commit 1 cardinal NP-modifier + Phase 4 §7.8 NP-internal
    # possessive); this commit's measure-N rule covers the
    # linker form, which is more idiomatic for native speakers.
    #
    # The constraining equation ``(↓1 MEASURE) =c 'YES'`` gates
    # the rule to measure NOUNs only — generic ``bata na
    # aklat`` ("child book"?) doesn't compose because ``bata``
    # has no MEASURE feature. ``¬ (↓3 MEASURE)`` blocks chained
    # measures (parallel to the cardinal rule's
    # ``¬ (↓4 CARDINAL_VALUE)``).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N",
            [
                "N",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ MEASURE_HEAD) = ↓1 LEMMA",
                "(↑ MEASURE) = 'YES'",
                "(↓1 MEASURE) =c 'YES'",
                "¬ (↓3 MEASURE)",
            ],
        ))


    # --- N from NOUN (toy PRED; Phase 5 will lexicalise properly) ---
    # Phase 5c §8 follow-on (Commit 6): also expose the noun's
    # ``LEMMA`` (always set by the noun analyzer) so the multi-OBL
    # classifier can look up semantic class. Optional ``SEM_CLASS``
    # rides through too when the root declares it in its
    # ``feats`` block (PLACE / ANIMATE / etc.). Both are unified
    # at the N-projection and propagate to the NP via the
    # NP → DET/ADP N rule's per-feature pass-through below.
    rules.append(Rule(
        "N",
        ["NOUN"],
        [
            # Phase 5f Commit 12: share N's f-structure with the
            # NOUN lex token entirely (was: only PRED + LEMMA
            # projected). This propagates SEM_CLASS / TIME_VALUE
            # / etc. up to N so downstream rules can constrain on
            # them — the minute-composition rule needs
            # ``(↓1 SEM_CLASS) =c 'TIME'`` on the head N. PRED is
            # set explicitly because the lex equations don't
            # provide one for nouns (only the lex-entry-derived
            # PRED is set when a LexicalEntry exists, which is
            # rare for nouns in the seed lex). LEMMA percolates
            # automatically via the shared structure.
            "(↑) = ↓1",
            "(↑ PRED) = 'NOUN(↑ FORM)'",
        ],
    ))


    # --- Phase 5f Commit 6: decimal cardinal --------------------
    #
    # ``dos punto singko`` "2.5", ``apat punto lima`` "4.5".
    # Spanish-borrowed ``punto`` joins the integer-part cardinal
    # to the fractional-part cardinal. The output is itself a
    # ``NUM[CARDINAL=YES]`` so the existing cardinal-NP-modifier
    # rules (Commit 1) and predicative-cardinal rule (Commit 4)
    # accept it unchanged.
    #
    # Equations: ``(↑) = ↓1`` shares all of the integer NUM's
    # f-structure with the matrix (so CARDINAL_VALUE, CARDINAL,
    # NUM all percolate from the integer part); the fractional
    # part is recorded as ``FRACTIONAL_VALUE`` (its own
    # CARDINAL_VALUE), and ``DECIMAL=YES`` marks the matrix as
    # a decimal value. CARDINAL_VALUE stays the integer part —
    # the LFG equation language doesn't have string concatenation
    # to construct a "2.5" literal, so we keep the parts separate.
    # Downstream consumers that need the full numeric value
    # combine ``CARDINAL_VALUE`` and ``FRACTIONAL_VALUE`` with
    # the ``DECIMAL`` marker.
    rules.append(Rule(
        "NUM[CARDINAL=YES]",
        [
            "NUM[CARDINAL=YES]",
            "PART[DECIMAL_SEP=YES]",
            "NUM[CARDINAL=YES]",
        ],
        [
            "(↑) = ↓1",
            "(↑ FRACTIONAL_VALUE) = ↓3 CARDINAL_VALUE",
            "(↑ DECIMAL) = 'YES'",
            # Constraining equation: enforce that the middle PART
            # daughter actually has DECIMAL_SEP=YES (i.e., is
            # ``punto``). Without this, the non-conflict pattern
            # matcher accepts any PART (including the LINK=NG /
            # LINK=NA linker particles) because ``LINK`` and
            # ``DECIMAL_SEP`` are different feature keys — this
            # is the same pitfall Phase 5e Commit 25 hit with
            # ``hindi`` vs ``huwag`` (and Commit 26 with
            # ``parang`` vs ``tila``). The constraining
            # equation rejects spurious matches at f-unification.
            "(↓2 DECIMAL_SEP) =c 'YES'",
        ],
    ))


    # --- Phase 5f Commit 13 (bundled): mga time approximation
    # (Group E item 3) -------------------------------------------
    #
    # ``mga alasotso`` "around 8 o'clock", ``mga alauna``
    # "around 1 o'clock", ``sa mga alastres`` "at around 3
    # o'clock". The ``mga`` particle (PLURAL_MARKER=YES in
    # particles.yaml) takes a TIME-class N and produces an
    # approximated time N (with APPROX=YES feature).
    #
    # Output is N (same category as the head clock-time
    # NOUN), so ``sa mga alasotso`` composes via existing
    # NP-from-N rules into NP[CASE=DAT] without further
    # grammar additions.
    #
    # The constraining equations enforce:
    #   (↓1 PLURAL_MARKER) =c 'YES'   — particle is mga
    #   (↓2 SEM_CLASS) =c 'TIME'      — head is clock-time
    #
    # Plural marking on regular nouns (``ang mga aklat`` "the
    # books") is a separate construction; deferred. Cardinal
    # approximation (``mga sampu`` "around ten") was deferred
    # in Commit 13 and is lifted by the parallel NUM rule
    # below in Phase 5f Commit 16 (Group H1 item 2).
    rules.append(Rule(
        "N",
        ["PART", "N"],
        [
            "(↑) = ↓2",
            "(↑ APPROX) = 'YES'",
            "(↓1 PLURAL_MARKER) =c 'YES'",
            "(↓2 SEM_CLASS) =c 'TIME'",
        ],
    ))


    # --- Phase 5f Commit 16: approximators (Group H1 item 2) ----
    #
    # ``halos sampu`` "almost ten", ``halos lahat`` "almost
    # all", ``halos maraming bata`` "almost many children",
    # ``humigitkumulang sampu`` "approximately ten", and
    # ``mga sampu`` "around ten" — a closed-class set of
    # approximator pre-modifiers wrap a NUM (CARDINAL=YES) or
    # Q head and add ``APPROX=YES`` to the result.
    #
    # Three rules total:
    #
    # 1. ``NUM → PART[APPROX=YES] NUM[CARDINAL=YES]`` wraps a
    #    cardinal NUM. Output is NUM (preserving CARDINAL=YES
    #    + CARDINAL_VALUE), so the matrix-NP cardinal-modifier
    #    rule (Phase 5f Commit 1) consumes it directly:
    #    ``Bumili ako ng halos sampung aklat.`` parses as
    #    ``[halos sampu]ng aklat`` with CARDINAL_VALUE=10 +
    #    APPROX=YES on the matrix NP.
    # 2. ``Q → PART[APPROX=YES] Q`` wraps a quantifier. Output
    #    is Q (preserving QUANT + VAGUE), so the existing
    #    Phase 5b partitive (``Q + NP[GEN]``) and Phase 5f
    #    Commit 15 vague-Q-modifier rules consume it:
    #    ``halos lahat ng bata`` partitive,
    #    ``halos maraming bata`` linker form.
    # 3. ``NUM → PART[PLURAL_MARKER=YES] NUM[CARDINAL=YES]``
    #    extends the Phase 5f Commit 13 mga rule from TIME
    #    NOUNs to cardinal NUMs. ``mga sampu`` "around ten"
    #    is the target; same surface uses the same lex entry,
    #    different rule.
    #
    # The constraining equation ``(↓1 APPROX) =c 'YES'`` (rules
    # 1 + 2) gates the daughter to actual approximator PARTs
    # (``halos`` / ``humigitkumulang``); ``(↓1 PLURAL_MARKER)
    # =c 'YES'`` (rule 3) gates to ``mga``. The
    # ``(↓2 CARDINAL) =c 'YES'`` constraint on rules 1 + 3
    # enforces the daughter is a genuinely cardinal NUM
    # (parallel to Commit 1's cardinal NP-modifier rule).
    rules.append(Rule(
        "NUM",
        ["PART", "NUM"],
        [
            "(↑) = ↓2",
            "(↑ APPROX) = 'YES'",
            "(↓1 APPROX) =c 'YES'",
            "(↓2 CARDINAL) =c 'YES'",
        ],
    ))
    rules.append(Rule(
        "Q",
        ["PART", "Q"],
        [
            "(↑) = ↓2",
            "(↑ APPROX) = 'YES'",
            "(↓1 APPROX) =c 'YES'",
        ],
    ))
    rules.append(Rule(
        "NUM",
        ["PART", "NUM"],
        [
            "(↑) = ↓2",
            "(↑ APPROX) = 'YES'",
            "(↓1 PLURAL_MARKER) =c 'YES'",
            "(↓2 CARDINAL) =c 'YES'",
        ],
    ))


    # --- Phase 5f Commit 17: numeric comparatives (Group H1
    # item 3) -----------------------------------------------------
    #
    # ``higit sa sampu`` "more than ten", ``kulang sa sampu``
    # "less than ten", ``hindi bababa sa sampu`` "no less than
    # ten / at least ten", ``hindi hihigit sa sampu`` "no more
    # than ten / at most ten". Four idiomatic phrase patterns
    # that wrap a NUM[CARDINAL=YES] standard via the DAT marker
    # ``sa`` and modify a NUM head with COMP feature.
    #
    # Per plan §11.1 Group H item 3: "These compose existing
    # constituents (negation hindi, the NEG-headed copula in
    # bababa / hihigit, DAT-NP sa NUM) plus a small frame rule
    # for the NUM modifier." The "small frame rule" is realised
    # here as four parallel rules each gated on a specific
    # COMP_PHRASE lex tag.
    #
    # Each rule's output is NUM (preserving CARDINAL=YES,
    # CARDINAL_VALUE, NUM=PL/SG via shared-fstruct ``(↑) = ↓N``
    # on the inner NUM daughter) plus a new ``COMP`` feature
    # set explicitly to GT / LT / GE / LE — the ``hindi
    # bababa`` / ``hindi hihigit`` patterns set GE / LE
    # respectively because the negation flips the underlying
    # head's semantics. The matrix-NP cardinal-modifier rule
    # (Phase 5f Commit 1) then consumes the wrapped NUM
    # unchanged.
    #
    # Solo patterns (higit / kulang): 3 daughters
    # ``PART ADP[CASE=DAT] NUM[CARDINAL=YES]``. Negated
    # patterns (hindi bababa / hindi hihigit): 4 daughters
    # ``PART[POLARITY=NEG] PART ADP[CASE=DAT] NUM[CARDINAL=YES]``.
    #
    # Constraints follow the established Phase 5f pattern:
    # ``(↓N COMP_PHRASE) =c 'X'`` gates each rule to its
    # specific lex tag; ``(↓ CASE) =c 'DAT'`` enforces ``sa``
    # rather than ``ng`` / ``ang``; ``(↓ CARDINAL) =c 'YES'``
    # enforces a genuinely cardinal NUM (parallel to Commit 1
    # / 16's cardinal gate).
    for comp_lex, comp_value in (("HIGIT", "GT"), ("KULANG", "LT")):
        rules.append(Rule(
            "NUM",
            ["PART", "ADP", "NUM"],
            [
                "(↑) = ↓3",
                f"(↑ COMP) = '{comp_value}'",
                f"(↓1 COMP_PHRASE) =c '{comp_lex}'",
                "(↓2 CASE) =c 'DAT'",
                "(↓3 CARDINAL) =c 'YES'",
            ],
        ))
    for comp_lex, comp_value in (("BABABA", "GE"), ("HIHIGIT", "LE")):
        rules.append(Rule(
            "NUM",
            ["PART", "PART", "ADP", "NUM"],
            [
                "(↑) = ↓4",
                f"(↑ COMP) = '{comp_value}'",
                "(↓1 POLARITY) =c 'NEG'",
                f"(↓2 COMP_PHRASE) =c '{comp_lex}'",
                "(↓3 CASE) =c 'DAT'",
                "(↓4 CARDINAL) =c 'YES'",
            ],
        ))


    # --- Phase 5f Commit 12: minute composition (Group E item 4)
    #
    # ``alasotso y singko`` "8:05" (cardinal minutes added),
    # ``alasotso y medya`` "8:30" (fractional minute = half),
    # ``alasotso y kuwarto`` "8:15" (fractional = quarter),
    # ``alasotso menos singko`` "7:55" (cardinal minutes
    # subtracted, backward-counting).
    #
    # Two operator PARTs (``y`` for forward-counting,
    # ``menos`` for backward) × two minute-daughter types
    # (NUM[CARDINAL=YES] for cardinal minutes,
    # N[SEM_CLASS=FRACTION] for fractional minutes) = 4 rules.
    #
    # Output is N (the same category as the head clock-time
    # NOUN), so the result composes via existing NP-from-N
    # rules into NP[CASE=DAT] / NP[CASE=NOM] / etc. without
    # any further grammar additions.
    #
    # F-structure on the matrix N:
    #   ... (everything from the head clock-time, via (↑) = ↓1)
    #   MINUTE_OP        = 'Y' | 'MENOS'
    #   MINUTE_VALUE     = the cardinal minute count (for NUM
    #                      daughter)
    #   MINUTE_FRACTION  = the fraction's LEMMA (for FRACTION
    #                      daughter — 'medya' = 30 min,
    #                      'kuwarto' = 15 min, 'kapat' = 15 min,
    #                      'kalahati' = 30 min)
    #
    # Constraining equations enforce that:
    #   (↓1 SEM_CLASS) =c 'TIME'      — head is a clock time
    #   (↓2 MINUTE_OP) =c '<OP>'      — middle PART is y or menos
    #   (↓3 CARDINAL) =c 'YES' OR     — third daughter is right type
    #   (↓3 SEM_CLASS) =c 'FRACTION'
    for op in ("Y", "MENOS"):
        # Cardinal-minute version: ``alasotso y singko``
        rules.append(Rule(
            "N",
            ["N", "PART", "NUM[CARDINAL=YES]"],
            [
                "(↑) = ↓1",
                "(↑ MINUTE_VALUE) = ↓3 CARDINAL_VALUE",
                f"(↑ MINUTE_OP) = '{op}'",
                "(↓1 SEM_CLASS) =c 'TIME'",
                f"(↓2 MINUTE_OP) =c '{op}'",
                "(↓3 CARDINAL) =c 'YES'",
            ],
        ))
        # Fractional-minute version: ``alasotso y medya``
        rules.append(Rule(
            "N",
            ["N", "PART", "N"],
            [
                "(↑) = ↓1",
                "(↑ MINUTE_FRACTION) = ↓3 LEMMA",
                f"(↑ MINUTE_OP) = '{op}'",
                "(↓1 SEM_CLASS) =c 'TIME'",
                f"(↓2 MINUTE_OP) =c '{op}'",
                "(↓3 SEM_CLASS) =c 'FRACTION'",
            ],
        ))

    # --- Phase 5f closing deferral: day-of-month form (Mayo 5) ----
    #
    # ``Mayo 5`` "May 5" — a MONTH NOUN compounded with a DOM
    # digit. Composed via this N-internal rule; the resulting N
    # projects ``SEM_CLASS=MONTH`` from the head so the existing
    # temporal-frame PP rule (``PP → PART N`` with
    # ``(↓2 SEM_CLASS) =c 'MONTH'`` from ``cfg/discourse.py``)
    # admits ``tuwing Mayo 5`` "every May 5" and
    # ``noong Mayo 5`` "on May 5" unchanged.
    #
    # The DOM digit lifts to ``DAY_OF_MONTH`` on the matrix N.
    # Constraining ``(↓2 DIGIT_FORM) =c 'YES'`` restricts the
    # rule to digit-form DOM (``Mayo 5``); a word-form DOM
    # (``Mayo lima``) is grammatical but rare and not exercised
    # by the seed corpus — the digit form is the canonical
    # written register for dates.
    #
    # Companion to the year-expression PP rule in
    # ``cfg/discourse.py`` (Phase 5f closing deferral). The
    # combined ``noong Mayo 5, 1990`` "on May 5, 1990" is
    # deferred — comma tokenization not yet supported.
    rules.append(Rule(
        "N",
        ["N", "NUM[CARDINAL=YES]"],
        [
            "(↑) = ↓1",
            "(↑ DAY_OF_MONTH) = ↓2 CARDINAL_VALUE",
            "(↓1 SEM_CLASS) =c 'MONTH'",
            "(↓2 DIGIT_FORM) =c 'YES'",
        ],
    ))


    # --- Phase 5g Commit 2: NP-internal ADJ modifier ------------
    #
    # Pre-N (``maganda na bata`` / ``magandang bata``) and post-N
    # (``bata na maganda`` / ``batang maganda``) adjective
    # modifiers, both linker-mediated. Four rules total:
    #
    #   N → ADJ PART[LINK=NA] N    pre-N, consonant-final adj
    #   N → ADJ PART[LINK=NG] N    pre-N, vowel-final adj (-ng)
    #   N → N PART[LINK=NA] ADJ    post-N, consonant-final N
    #   N → N PART[LINK=NG] ADJ    post-N, vowel-final N (-ng)
    #
    # Multi-modifier composition (``mabilis na maganda na bata``
    # "quick beautiful child") falls out of right-recursion in
    # the pre-N rules: the rightmost daughter is N, and an
    # adj-modified N is itself N. The two adjectives both end
    # up in the matrix N's ``ADJ-MOD`` set.
    #
    # **Why ``ADJ-MOD`` rather than the canonical ``ADJ``
    # attribute.** This codebase uses ``ADJ`` as a set-valued
    # f-attribute for clausal adjuncts (adverbial clitics in
    # ``cfg/clitic.py``, sentential PP/AdvP fronting in
    # ``cfg/extraction.py``) and as the host slot for relative
    # clauses on NPs. Lifting the head N's adjunct set to the
    # matrix NP via ``(↑ ADJ) = ↓2 ADJ`` would pre-create an
    # empty AVM on every NP whose head N has no modifier — and
    # subsequent ``↓ ∈ (↑ ADJ)`` set-adds (e.g., from the RC
    # wrap rule) would then clash with that empty AVM at the
    # ``add_to_set`` call. Using a Phase-5g-specific attribute
    # name (``ADJ-MOD``) sidesteps the clash because no other
    # rule writes to it. Tests for NP-internal adj modifiers
    # check ``feats["ADJ-MOD"]`` rather than ``feats["ADJ"]``.
    #
    # The category ``ADJ`` in the rule's RHS is the lex
    # preterminal POS (the analyzer's ``MorphAnalysis.pos`` for
    # ADJ-class roots), entirely separate from the f-attribute
    # ``ADJ`` / ``ADJ-MOD`` namespace.
    #
    # The N-level rule (no NP / no case) lets the existing
    # NP-from-N projection at lines 64-90 case-mark adj-modified
    # Ns freely (``ang magandang bata`` / ``ng magandang bata``
    # / ``sa magandang bata``). Avoids the 6-NP-rule explosion
    # that the cardinal NP-modifier (Phase 5f Commit 1) used.
    for link in ("NA", "NG"):
        # Pre-N: the adjective sits before the head N.
        rules.append(Rule(
            "N",
            ["ADJ", f"PART[LINK={link}]", "N"],
            [
                "(↑) = ↓3",
                "↓1 ∈ (↑ ADJ-MOD)",
            ],
        ))
        # Post-N: the head N comes first.
        rules.append(Rule(
            "N",
            ["N", f"PART[LINK={link}]", "ADJ"],
            [
                "(↑) = ↓1",
                "↓3 ∈ (↑ ADJ-MOD)",
            ],
        ))


    # --- Phase 5h Commit 3: comparative ``mas`` ADJ-wrapper -----
    #
    # ``Mas matalino siya.`` "She is more intelligent."
    # ``Mas mabilis ang kabayo.`` "The horse is faster."
    # ``mas matalinong bata`` "more intelligent child" (NP-modifier).
    #
    # The PART ``mas`` (lex feat ``COMP_DEGREE: COMPARATIVE`` —
    # added in particles.yaml in this commit) wraps an ADJ to
    # produce another ADJ marked ``COMP_DEGREE: COMPARATIVE``. The
    # output is itself an ADJ, so the same Phase 5g rules consume
    # it: the predicative-adj clause rule fires on
    # ``Mas matalino siya``; the NP-internal modifier rules fire on
    # ``mas matalinong bata``. No new clause / NP rules.
    #
    # **Equation analysis**:
    #
    # * ``(↑) = ↓2`` shares the inner ADJ's f-structure with the
    #   wrapped output. The inner ADJ's PRED, PREDICATIVE,
    #   ADJ_LEMMA, and any per-cell feats all percolate to the
    #   matrix.
    # * ``(↑ COMP_DEGREE) = 'COMPARATIVE'`` writes COMPARATIVE
    #   onto the shared f-structure. If the inner ADJ already
    #   carries a different COMP_DEGREE (e.g.,
    #   ``pinakamaganda`` carries SUPERLATIVE), unification fails —
    #   ``*mas pinakamaganda`` "more most beautiful" is correctly
    #   ungrammatical.
    # * ``(↓1 COMP_DEGREE) =c 'COMPARATIVE'`` constrains the PART
    #   daughter. Belt-and-braces with the category-pattern
    #   ``PART[COMP_DEGREE=COMPARATIVE]``; the category matcher
    #   already filters, but the explicit constraint matches
    #   the Phase 5e parang / Phase 5g predicative-adj convention.
    #
    # **Why this rule is in nominal.py rather than its own
    # ``cfg/degree.py``**: the wrapped ADJ is consumed by both
    # NP-modifier rules (above this block) and the Phase 5g
    # predicative-adj clause rule. ADJ-wrapping rules sit in the
    # nominal area as a category-rewrite that feeds both clausal
    # and nominal contexts. Phase 5h Commit 5's intensifier-ADJ
    # wrapper joins this same area; if the wrapper-rule cluster
    # grows beyond ~3-4 rules, a dedicated ``cfg/degree.py``
    # split is reasonable.
    #
    # **Top-1 flip risk** (Phase 5h plan §7.2): pre-state probe
    # showed ``Mas matalino siya.`` parsed today via
    # ``_strip_non_content`` silently dropping ``mas`` (a _UNK
    # token); after this commit, the same surface parses with
    # ``mas`` consumed by the new wrapper, producing a richer
    # f-structure (matrix carries COMP_DEGREE: COMPARATIVE).
    # Audit before merging: none of the 1229 baseline corpus
    # entries contain ``mas`` (verified by grep on
    # tests/tgllfg/data/coverage_corpus.yaml).
    rules.append(Rule(
        "ADJ",
        ["PART[COMP_DEGREE=COMPARATIVE]", "ADJ"],
        [
            "(↑) = ↓2",
            "(↑ COMP_DEGREE) = 'COMPARATIVE'",
            "(↓1 COMP_DEGREE) =c 'COMPARATIVE'",
        ],
    ))


    # --- Phase 5h Commit 5: particle-intensifier ADJ-wrappers ----
    #
    # ``Sobrang maganda ang bata.``     "The child is too beautiful."
    # ``Talagang maganda ang bata.``    "The child is really beautiful."
    # ``Lubos na maganda ang bata.``    "The child is completely beautiful."
    # ``Masyadong mainit ang sopas.``   "The soup is too hot."
    # ``Medyo maganda ang bata.``       "The child is somewhat beautiful."
    #
    # Five new PARTs (sobra / medyo / talaga / lubos / masyado —
    # added in particles.yaml in this commit) each carry
    # ``INTENSIFIER: YES`` plus a per-particle ``INTENSITY`` tag
    # (EXCESSIVE / MODERATE / EMPHATIC / COMPLETE / EXCESSIVE
    # respectively). Each takes the linker (NA or bound -ng) and
    # an ADJ complement; ``medyo`` colloquially also appears without
    # a linker.
    #
    # **Equation analysis** (mirrors the Phase 5h Commit 3
    # comparative-mas wrapper — same shape, plus an
    # ``INTENSITY``-lift that carries the per-particle semantic
    # tag onto the wrapped ADJ):
    #
    # * ``(↑) = ↓3`` shares the inner ADJ's f-structure with the
    #   wrapped output (same as Phase 5g manner-adverb / Commit 3
    #   comparative wrapper).
    # * ``(↑ COMP_DEGREE) = 'INTENSIVE'`` writes INTENSIVE onto
    #   the matrix. Unification clash on already-degree-marked
    #   ADJs handles ``*sobrang pinakamaganda`` (more most beautiful)
    #   correctly. Note: if inner is ``napakaganda`` (also INTENSIVE),
    #   identity write succeeds → ``Sobrang napakaganda ang bahay``
    #   parses as a "double intensifier" (attested colloquially).
    # * ``(↑ INTENSITY) = ↓1 INTENSITY`` lifts the particle's
    #   semantic tag onto the matrix.
    # * ``(↑ INTENSIFIER) = 'YES'`` and ``(↓1 INTENSIFIER) =c 'YES'``
    #   — defining + constraining belt-and-braces (matches the
    #   Phase 5g convention).
    #
    # **Why both NA and NG link variants**: identical to Phase 5g
    # manner-adverb / NP-modifier link handling. Vowel-final
    # particles (``sobra``, ``talaga``, ``masyado``, ``medyo``) take
    # the bound ``-ng`` (split by ``split_linker_ng`` at the
    # pre-parse stage); consonant-final particles (``lubos``) take
    # the free ``na``. The bound-``-ng`` and free-``na`` forms both
    # surface as ``PART[LINK=NG]`` and ``PART[LINK=NA]`` after
    # the pre-pass, so the rule is parameterised over both link
    # variants.
    #
    # **Top-1 flip risk** (Phase 5h plan §7.2): pre-state probes
    # showed ``Sobrang maganda ang bata`` / ``Talagang maganda
    # ang bata`` / ``Lubos na maganda ang bata`` parsing today by
    # silently dropping the _UNK intensifier. After this commit
    # the same surfaces parse with the intensifier consumed by
    # the new wrapper, producing a richer f-structure (matrix
    # carries INTENSIFIER=YES, COMP_DEGREE=INTENSIVE,
    # INTENSITY=<tag>). Audit before merging: none of the 1229
    # baseline corpus entries contain the surfaces ``sobra``,
    # ``sobrang``, ``medyo``, ``talaga``, ``talagang``, ``lubos``,
    # ``masyado``, or ``masyadong`` (verified by grep).
    # **Belt-and-braces ``=c`` constraints on both PART daughters**:
    # the category-pattern matcher is non-conflict (compile.py
    # ::matches), so ``PART[INTENSIFIER=YES]`` matches any PART
    # without an INTENSIFIER feature by absorption, and similarly
    # ``PART[LINK=NA]`` matches any PART without LINK. Without the
    # explicit constraining equations, ``Lubos na mas matalino
    # siya`` would parse: ``mas`` (PART[COMP_DEGREE=COMPARATIVE],
    # no LINK) would absorb the ``PART[LINK=NA]`` slot. The two
    # ``=c`` equations close the leak — same pattern as Phase 5h
    # Commit 3's ``(↓1 POLARITY) =c 'NEG'`` fix on the hindi-
    # negation rule.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "ADJ",
            [
                "PART[INTENSIFIER=YES]",
                f"PART[LINK={link}]",
                "ADJ",
            ],
            [
                "(↑) = ↓3",
                "(↑ INTENSIFIER) = 'YES'",
                "(↑ COMP_DEGREE) = 'INTENSIVE'",
                "(↑ INTENSITY) = ↓1 INTENSITY",
                "(↓1 INTENSIFIER) =c 'YES'",
                f"(↓2 LINK) =c '{link}'",
            ],
        ))


    # --- Phase 5h Commit 5: ``medyo`` zero-linker variant ---------
    #
    # ``Medyo maganda ang bata.`` "The child is somewhat beautiful."
    #
    # Per S&O 1972 / Schachter 1985: ``medyo`` colloquially appears
    # WITHOUT a linker (in addition to the with-linker form covered
    # by the rule above). The zero-linker variant is restricted to
    # ``INTENSITY=MODERATE`` (the medyo-specific feature) so the
    # ``sobra`` / ``talaga`` / ``lubos`` / ``masyado`` paths still
    # require the linker — this avoids overgeneralising to
    # ``*sobra ganda`` (without linker) which is ungrammatical.
    #
    # The constraining ``(↓1 INTENSITY) =c 'MODERATE'`` filters to
    # ``medyo`` only at the equation layer; the category pattern
    # ``PART[INTENSITY=MODERATE]`` filters at the matcher layer
    # (belt-and-braces).
    rules.append(Rule(
        "ADJ",
        ["PART[INTENSITY=MODERATE]", "ADJ"],
        [
            "(↑) = ↓2",
            "(↑ INTENSIFIER) = 'YES'",
            "(↑ COMP_DEGREE) = 'INTENSIVE'",
            "(↑ INTENSITY) = ↓1 INTENSITY",
            "(↓1 INTENSITY) =c 'MODERATE'",
            "(↓1 INTENSIFIER) =c 'YES'",
        ],
    ))


    # --- Phase 5h Commit 7: comparative Q-wrapper ---------------
    #
    # ``mas maraming aklat`` "more books" — comparative quantification
    # over the existing Phase 5f vague-Q heads. The Phase 5h Commit 3
    # ``mas`` PART (lex feat ``COMP_DEGREE: COMPARATIVE``) wraps a
    # ``Q[VAGUE=YES]`` head (``marami``, ``kaunti``, ``konti``,
    # ``kakaunti``, ``ilan``, ``iilan``) to produce a comparative-Q.
    # The wrapped Q rides into the existing Phase 5f Commit 15
    # vague-Q NP-modifier rule unchanged: ``mas maraming aklat``
    # parses as ``NP → Q[COMP_DEGREE=COMPARATIVE] PART[LINK] N``.
    #
    # **Equation analysis** (mirrors the Phase 5h Commit 3
    # comparative-ADJ wrapper):
    #
    # * ``(↑) = ↓2`` shares the inner Q's f-structure with the
    #   wrapped output (PRED, LEMMA, QUANT, VAGUE all percolate).
    # * ``(↑ COMP_DEGREE) = 'COMPARATIVE'`` writes COMPARATIVE
    #   onto the matrix.
    # * ``(↓1 COMP_DEGREE) =c 'COMPARATIVE'`` belt-and-braces
    #   constraint on the PART daughter (matches Commit 3
    #   convention).
    # * ``(↓2 VAGUE) =c 'YES'`` belt-and-braces constraint on the
    #   Q daughter — closes the same kind of non-conflict-matcher
    #   leak Commits 3 and 5 closed (without it, a Q without
    #   VAGUE would absorb the slot).
    #
    # **Why a sibling rule rather than overloading the Commit 3
    # ADJ-wrapper**: the Q and ADJ wrappers have different
    # downstream consumers — Q feeds the NP-modifier and the (not-
    # yet-built) predicative-Q rule; ADJ feeds the predicative-adj
    # clause rule and the NP-internal ADJ-modifier rules. Modest
    # rule duplication is preferable to category-pattern
    # overloading.
    #
    # **What's NOT in scope this commit**: predicative-Q clause
    # (``Mas marami ang aklat.`` "There are more books.") — would
    # need a new clausal rule analogous to the Phase 5f Commit 4
    # predicative-cardinal rule (``Tatlo ang aklat.``). Cardinal
    # comparison via ``mas`` (``*Mas tatlo``) is correctly
    # ungrammatical: cardinals carry ``CARDINAL: YES``, not
    # ``VAGUE: YES``, so the rule's category-pattern + ``=c``
    # constraint does not fire on them.
    rules.append(Rule(
        "Q",
        ["PART[COMP_DEGREE=COMPARATIVE]", "Q[VAGUE=YES]"],
        [
            "(↑) = ↓2",
            "(↑ COMP_DEGREE) = 'COMPARATIVE'",
            "(↓1 COMP_DEGREE) =c 'COMPARATIVE'",
            "(↓2 VAGUE) =c 'YES'",
        ],
    ))
