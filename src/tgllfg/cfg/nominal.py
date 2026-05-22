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
    # Phase 6.G Commit 2: SHARE+SHARE pattern (L32). The NP's
    # f-structure unifies with BOTH the case-marker daughter (↓1)
    # and the N daughter (↓2) — propagating CASE/MARKER/DEM from
    # the marker and PRED/LEMMA/SEM_CLASS/SEASON/any-N-internal-
    # modifier-feats from N onto the matrix NP, without empty-
    # f-node pollution. The explicit ``(↑ PRED) = ↓2 PRED`` and
    # ``(↑ LEMMA) = ↓2 LEMMA`` lifts become implicit via the
    # share — dropped. See ``docs/analysis-choices.md`` "Phase
    # 6.G Commit 1" for the empty-f-node analysis.
    #
    # **N-level-RC exclusion** (``¬ (↓2 N_RC)``). The Phase
    # 5n.A C8 N-level RC rule (``cfg/extraction.py``: ``N → N
    # PART[LINK] S_GAP``) was added for existential bare-N RCs
    # (``May bahay na nasa bundok``). Under SHARE+SHARE its
    # output N would feed the simple NP rule, producing a parse
    # that duplicates the canonical NP-level RC wrap (Phase 4
    # §7.5). The N-level RC marks its output with ``N_RC = true``
    # (a binary feat declared in ``core/feats.py BINARY_FEATS``);
    # this simple NP rule's ``¬ (↓2 N_RC)`` blocks it from
    # consuming N-level-RC'd Ns, leaving the NP-level RC path as
    # the unique surface route for case-marked NP-headed RCs.
    # (Negative-existential on a tag feat works at pass-2 because
    # the tag feat is set by the N-level RC's own defining
    # equation; the canonical path's NP-level RC adds ADJ but
    # never N_RC, so the two paths are distinguishable at pass 2.)
    # Additional N-level-modifier exclusion: the N-level cardinal
    # rule below (``N → NUM[CARDINAL] PART[LINK] N``, Phase 5f
    # Commit 1 companion) and other N-modifier compositions
    # produce an N with the modifier's value feat already lifted
    # (``CARDINAL_VALUE`` on N for cardinal; ``DISTRIB`` on N for
    # tig-distrib via paradigm). Under SHARE+SHARE, that N's
    # value feat would propagate to NP via the simple rule —
    # duplicating the dedicated NP-level cardinal / distrib /
    # etc. rules (Phase 5f Commits 1 / 19). The negative-
    # existential guards block the simple NP rule from consuming
    # such pre-modified Ns, leaving the dedicated NP-level rules
    # as the unique surface route for case-marked modifier NPs.
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["DET[CASE=NOM]", "N"],
        [
            "(↑) = ↓1",
            "(↑) = ↓2",
            "¬ (↓2 N_RC)",
            "¬ (↓2 CARDINAL_VALUE)",
            "¬ (↓2 MGA_INTERNAL)",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["ADP[CASE=GEN]", "N"],
        [
            "(↑) = ↓1",
            "(↑) = ↓2",
            "¬ (↓2 N_RC)",
            "¬ (↓2 CARDINAL_VALUE)",
            "¬ (↓2 MGA_INTERNAL)",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT]", "N"],
        [
            "(↑) = ↓1",
            "(↑) = ↓2",
            "¬ (↓2 N_RC)",
            "¬ (↓2 CARDINAL_VALUE)",
            "¬ (↓2 MGA_INTERNAL)",
        ],
    ))


    # --- Phase 7a.A: NP-internal ``mga`` plural marker -----------
    #
    # Closes §18.1.1 #11 (``mga`` plural marker on regular nouns).
    # Surface: ``ang mga aklat`` "the books"; ``ng mga aklat`` "of
    # the books"; ``sa mga aklat`` "to the books". The construction
    # was promoted to formal §18.1.1 by Phase 6.H closing notes;
    # Phase 7a.A closes it via a three-daughter case-parallel
    # extension of the existing simple-NP rules above.
    #
    # Rule shape:
    #
    #   NP[CASE=X] → CASE-MARKER[CASE=X] PART N
    #     (↑) = ↓1                      share f-struct with case-marker
    #     (↑) = ↓3                      share f-struct with head N
    #     (↑ NUM) = 'PL'                set plural number on matrix NP
    #     (↓2 PLURAL_MARKER) =c true    gate the PART daughter to ``mga``
    #     ¬ (↓3 N_RC)                   mirror simple-NP exclusion
    #     ¬ (↓3 CARDINAL_VALUE)         mirror simple-NP exclusion
    #
    # The ``(↑ NUM) = 'PL'`` defining equation feeds the Phase 6.H
    # floated-Q DUAL-rule's constraining equation
    # ``(↑ SUBJ NUM) =c 'PL'`` (``cfg/clitic.py``) — closing the
    # canonical ``Kumain ang mga bata pareho.`` "The children ate
    # together" case probed but not closed during Phase 6.H.
    #
    # Negative existentials mirror the simple-NP rules (N_RC,
    # CARDINAL_VALUE). The N_RC guard prevents this rule from
    # consuming an N-level RC's output (which would duplicate the
    # canonical NP-level RC path; Phase 5n.A C8 / Phase 6.G C1).
    # The CARDINAL_VALUE guard prevents consuming a cardinal-
    # modified N (which would duplicate the dedicated NP-level
    # cardinal-modifier rule; Phase 5f Commit 1).
    #
    # **Ambiguity with Phase 5f approximator rules** (intentional).
    # The Phase 5f time-approximator (``N → PART N[SEM_CLASS=TIME]``)
    # and cardinal-approximator (``NUM[CARDINAL] → PART NUM[CARDINAL]``)
    # also consume ``mga`` but produce DIFFERENT outputs (N and NUM
    # respectively) with APPROX=true rather than NUM=PL. For
    # non-time, non-cardinal Ns like ``aklat`` only this new rule
    # fires. For time Ns like ``oras``, both paths fire and produce
    # distinct f-structures (NUM=PL vs APPROX=true) — both
    # linguistically valid readings of ``mga oras``. For cardinal
    # NUMs like ``sampu`` only the approximator path fires (this
    # rule's ↓3 expects N, not NUM). Ambiguity for time Ns is
    # accepted; the readings are genuinely distinct.
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["DET[CASE=NOM]", "PART", "N"],
        [
            "(↑) = ↓1",
            "(↑) = ↓3",
            "(↑ NUM) = 'PL'",
            "(↓2 PLURAL_MARKER) =c true",
            "¬ (↓3 N_RC)",
            "¬ (↓3 CARDINAL_VALUE)",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["ADP[CASE=GEN]", "PART", "N"],
        [
            "(↑) = ↓1",
            "(↑) = ↓3",
            "(↑ NUM) = 'PL'",
            "(↓2 PLURAL_MARKER) =c true",
            "¬ (↓3 N_RC)",
            "¬ (↓3 CARDINAL_VALUE)",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT]", "PART", "N"],
        [
            "(↑) = ↓1",
            "(↑) = ↓3",
            "(↑ NUM) = 'PL'",
            "(↓2 PLURAL_MARKER) =c true",
            "¬ (↓3 N_RC)",
            "¬ (↓3 CARDINAL_VALUE)",
        ],
    ))


    # --- Phase 8.E: NP-internal ``mga`` plural marker + DEM head -----
    #
    # Closes ``ang mga ito`` "these (ones)" / ``ang mga iyan``
    # "those (ones)" / ``ang mga iyon`` "those distal (ones)". The
    # construction is the substantive-DEM (pronominal-DEM)
    # pluralization. Audit-driven scoping: corpus shows 10 candidates
    # across 5342 exemplars, all NOM-form (no GEN/DAT corpus
    # pressure), so this commit lands the NOM variant only. GEN/DAT
    # variants (``ng mga nito`` / ``sa mga doon``) can opt in later
    # if corpus pressure surfaces.
    #
    # Sibling to Phase 7a.A ``mga`` + N rule (same shape with N head)
    # and Phase 4 §7.8 standalone-DEM NP rule (DEM head without
    # ``mga``). The third daughter is a DEM-marked DET; the matrix
    # gets a synthesized ``PRED='PRO'`` like the standalone-DEM rule,
    # with NUM=PL and DEIXIS lifted from the DEM.
    #
    # Rule shape:
    #
    #   NP[CASE=NOM] → DET[CASE=NOM] PART DET[CASE=NOM, DEM]
    #     (↑)            = ↓1               share with case-marker
    #     (↑ PRED)       = 'PRO'            synthesized DEM-PRED
    #     (↑ NUM)        = 'PL'             mga marks plural
    #     (↑ DEIXIS)     = ↓3 DEIXIS        lift DEM's deixis
    #     (↓2 PLURAL_MARKER) =c true        gate ↓2 to ``mga``
    #
    # References: Schachter & Otanes 1972 §6 (mga plural marker);
    # R&G 1981 §2 (demonstrative pronouns).
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["DET[CASE=NOM]", "PART", "DET[CASE=NOM, DEM]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = 'PRO'",
            "(↑ NUM) = 'PL'",
            "(↑ DEIXIS) = ↓3 DEIXIS",
            "(↓2 PLURAL_MARKER) =c true",
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
    # rules admit ``ng + PRON[WH]`` → NP[CASE=GEN] and
    # ``sa/kay + PRON[WH]`` → NP[CASE=DAT].
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
    # consumers can read ``(↑ WH) = true`` off any in-situ wh-NP
    # without traversing into the PRON daughter.
    #
    # The matrix-level Q_TYPE lift (marking the whole sentence as a
    # wh-Q when any in-situ wh-NP appears) is deferred — it requires
    # either a post-parse f-structure walk or a defining equation in
    # every V-headed S frame; the latter is invasive. For Commit 3
    # the in-situ form parses; Q_TYPE percolation lands as a Phase 5i
    # follow-on if corpus pressure demands it.
    # LHS advertises ``WH=true`` so the Phase 5n.B Commit 9
    # sa-kanino cleft rule (which expects ``NP[CASE=DAT, WH]``)
    # admits the in-situ wh-PRON-in-NP shell under the Phase 6.C
    # graph-constraint matcher. ``(↑ WH) = ↓2 WH`` already
    # propagates WH=true on the f-graph (the PRON daughter has
    # WH=true).
    rules.append(Rule(
        "NP[CASE=GEN, WH=true]",
        ["ADP[CASE=GEN]", "PRON[WH]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = 'WH-PRO'",
            "(↑ WH) = ↓2 WH",
            "(↑ WH_LEMMA) = ↓2 LEMMA",
            "(↓2 WH) =c true",
        ],
    ))
    rules.append(Rule(
        "NP[CASE=DAT, WH=true]",
        ["ADP[CASE=DAT]", "PRON[WH]"],
        [
            "(↑) = ↓1",
            "(↑ PRED) = 'WH-PRO'",
            "(↑ WH) = ↓2 WH",
            "(↑ WH_LEMMA) = ↓2 LEMMA",
            "(↓2 WH) =c true",
        ],
    ))

    # --- Phase 5n.B Commit 14: sa + non-wh DAT-PRON shell ---
    #
    # ``sa kanya`` "to/for him/her" — explicit DAT-marker over a
    # non-wh DAT-PRON. Parallel to the Phase 5i C3 wh-PRON rule
    # above but for non-wh PRONs (kanya / akin / iyo / atin /
    # amin / inyo / kanila). Without this rule, ``sa kanya`` does
    # not form NP[CASE=DAT] — only the bare ``kanya`` does (which
    # carries CASE=DAT inherently). The explicit-DAT form is
    # required to parse plan-of-record §4.2 Commit 14 target
    # ``Magkano ito sa kanya?``.
    #
    # ``¬ (↓2 WH)`` keeps this rule disjoint from the Phase 5i
    # C3 wh-PRON rule above (which fires on PRON[WH]). The
    # two paths are mutually exclusive on the WH feat.
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT]", "PRON[CASE=DAT]"],
        [
            "(↑) = ↓1",
            "(↑) = ↓2",
            "¬ (↓2 WH)",
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
        ["DET[CASE=NOM, DEM]"],
        ["(↑) = ↓1", "(↑ PRED) = 'PRO'"],
    ))
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["ADP[CASE=GEN, DEM]"],
        ["(↑) = ↓1", "(↑ PRED) = 'PRO'"],
    ))
    rules.append(Rule(
        "NP[CASE=DAT]",
        ["ADP[CASE=DAT, DEM]"],
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
                "DET[CASE=NOM, DEM]",
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
                "ADP[CASE=GEN, DEM]",
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
                "ADP[CASE=DAT, DEM]",
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
                "DET[CASE=NOM, DEM]",
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
                "ADP[CASE=GEN, DEM]",
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
                "ADP[CASE=DAT, DEM]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑) = ↓1",
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
            ],
        ))


    # --- Phase 9.X.c28: manner-DEM pre-N modifier ``ganitong N`` -----
    #
    # ``ganitong pagkakaayos``  "this kind of arrangement"
    #                            (PANAHON sent-39)
    # ``ganitong panahon``       "this kind of weather"
    # ``ganong tao``             "that kind of person" (MED)
    # ``gayong gawain``          "that kind of work" (DIST)
    #
    # The manner-DEM family (``ganito`` PROX / ``ganon`` MED /
    # ``gayon`` DIST) marks "this/that kind of X". Structurally it
    # pre-modifies the head N via the linker. Unlike the Phase 5e
    # Commit 16 pre-mod DEM rule (which expects DET[CASE=X, DEM]),
    # the manner-DEMs are PART with LEMMA-only feats (particles.yaml).
    #
    # Three LEMMA-gated rules per linker (NA / NG), six total. The
    # matrix N inherits PRED + LEMMA from the head N (↓3); the
    # manner-DEM rides as a DEM-modifier in ADJUNCT.
    #
    # Closes the sent-39 missing piece (``ganitong pagkakaayos``
    # inside a dahil-PP); the c28 ``iba`` / ``Pilipino`` ADJ POS-flips
    # close the matrix predicate.
    for lemma in ("ganito", "ganon", "gayon"):
        for link in ("NA", "NG"):
            rules.append(Rule(
                "N",
                [
                    "PART",
                    f"PART[LINK={link}]",
                    "N",
                ],
                [
                    "(↑) = ↓3",
                    "↓1 ∈ (↑ ADJUNCT)",
                    f"(↓1 LEMMA) =c '{lemma}'",
                ],
            ))


    # --- Phase 9.X.c24: NUM range expression ``Mula X hanggang Y`` ---
    #
    # ``Mula sampu hanggang dalawampung bagyo``  "from ten to
    # twenty storms"  (PANAHON sent-21)
    # ``Mula isa hanggang lima``                 "from one to five"
    #
    # Closes the explicitly-noted Phase 5e Commit 3 deferral
    # (cfg/discourse.py: "mula-sa-NP can also appear in range
    # expressions like ``mula X hanggang Y``") — a four-token
    # fixed-frame construction composing
    # ``PREP[mula] + NUM[CARDINAL] + PART[hanggang] +
    # NUM[CARDINAL]`` into a virtual range-NUM that feeds the
    # Phase 5f Commit 1 cardinal-NP-modifier rules below.
    #
    # F-structure: matrix NUM lifts the HI bound's f-structure
    # (CARDINAL_VALUE, NUM, PRED, LEMMA) so downstream consumers
    # see a normal CARDINAL. The LO bound rides at ``RANGE_LO``
    # as a sub-attr; downstream semantics can read both endpoints
    # via ``RANGE_LO`` and the matrix.
    #
    # Gates: ↓1 LEMMA="mula" + PREP_TYPE="SOURCE" narrow to the
    # SOURCE preposition; the alternative-LEMMA ``mula`` is
    # excluded by category (only PREP at this rule's slot 1).
    # ↓3 LEMMA="hanggang" locks the bracket — the alternative
    # ``hanggang`` (COMP_TYPE=TEMP_UNTIL) continues to head its
    # own clause-level until-subordinator rules. CARDINAL gates
    # on ↓2 / ↓4 ensure both endpoints are bona fide cardinals,
    # not ordinals or other NUM-typed forms.
    rules.append(Rule(
        "NUM[CARDINAL]",
        [
            "PREP",
            "NUM[CARDINAL]",
            "PART",
            "NUM[CARDINAL]",
        ],
        [
            "(↑) = ↓4",
            "(↑ RANGE_LO) = ↓2",
            "(↓1 LEMMA) =c 'mula'",
            "(↓1 PREP_TYPE) =c 'SOURCE'",
            "(↓3 LEMMA) =c 'hanggang'",
        ],
    ))


    # --- Phase 9.X.c30: bare cardinal as NP head ----------------------
    #
    # ``ang dalawa`` "the two", ``ang isa`` "the one (of them)",
    # ``ng tatlo`` "of three" — a cardinal directly heads the NP
    # without an N daughter, denoting the cardinal-quantified set.
    # PANAHON sent-13 (``Kapag naghalo ang dalawa ...``) — the
    # ``ang dalawa`` refers to "the two (typhoons)" from the prior
    # context.
    #
    # Three rules (one per case), parallel to the Phase 5f Commit 1
    # cardinal-NP-modifier rules above but with no LINK+N tail. The
    # matrix NP lifts the cardinal's f-structure entirely
    # (``(↑) = ↓2``) so CARDINAL_VALUE / NUM / APPROX / DISTRIB
    # ride to the matrix; the case marker contributes CASE/MARKER.
    # No PRED — the cardinal-as-NP-head has no head-noun referent
    # (downstream consumers treat the NP as a pronominal-like
    # reference to a contextually-given count of entities).
    for case, marker in _cardinal_case_marker.items():
        rules.append(Rule(
            f"NP[CASE={case}]",
            [
                marker,
                "NUM[CARDINAL]",
            ],
            [
                "(↑) = ↓1",
                "(↑ NUM) = ↓2 NUM",
                "(↑ CARDINAL_VALUE) = ↓2 CARDINAL_VALUE",
                "(↓2 CARDINAL) =c true",
                # Exclude DISTRIB cardinals (``tig-`` prefix) — those
                # must compose with a head N via the cardinal-N
                # modifier rule below (``*Bumili ako ng tigisa.``;
                # asserted in test_distributive.py).
                "¬ (↓2 DISTRIB)",
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
    # standalone ``na`` after a NUM[CARDINAL] is
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
    # Phase 6.G C3: APPROX + DISTRIB lift onto cardinal-modified
    # NP. The Phase 5f Commit 16 approximator-wrap rule
    # (``NUM[CARDINAL=true] → PART[APPROX=true] NUM``) sets
    # ``(↑ APPROX) = true`` on its NUM output; the Phase 5n.C.3
    # ``tig_distrib`` paradigm sets ``(↑ DISTRIB) = true`` on its
    # NUM output (e.g., ``tigisa``). The cardinal-NP rule consumes
    # those NUMs as ↓2; the Phase 6.G L32-closure extension adds
    # explicit ``(↑ APPROX) = ↓2 APPROX`` and ``(↑ DISTRIB) = ↓2
    # DISTRIB`` lifts so the modifier feats surface on the matrix
    # NP. For non-APPROX / non-DISTRIB cardinals (bare ``isang
    # aklat``), the lifts create empty f-nodes at ``NP.APPROX`` /
    # ``NP.DISTRIB``; downstream consumers checking the value as
    # ``is True`` skip the empty case naturally.
    for case, marker in _cardinal_case_marker.items():
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [
                    marker,
                    "NUM[CARDINAL]",
                    f"PART[LINK={link}]",
                    "N",
                ],
                [
                    "(↑) = ↓1",
                    "(↑ PRED) = ↓4 PRED",
                    "(↑ LEMMA) = ↓4 LEMMA",
                    "(↑ NUM) = ↓2 NUM",
                    "(↑ CARDINAL_VALUE) = ↓2 CARDINAL_VALUE",
                    "(↑ APPROX) = ↓2 APPROX",
                    "(↑ DISTRIB) = ↓2 DISTRIB",
                    "¬ (↓4 CARDINAL_VALUE)",
                    # Constraining: enforce the daughter is actually
                    # CARDINAL=YES, not just any NUM. Without this,
                    # ORDINAL=YES NUMs (Phase 5f Commit 7) match by
                    # non-conflict (no shared CARDINAL key) and
                    # produce empty CARDINAL_VALUE fstructs on the
                    # matrix NP. Same fix-pattern as Commit 6's
                    # PART[DECIMAL_SEP] constraint.
                    "(↓2 CARDINAL) =c true",
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
                "NUM[CARDINAL]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ NUM) = ↓1 NUM",
                "(↑ CARDINAL_VALUE) = ↓1 CARDINAL_VALUE",
                "¬ (↓3 CARDINAL_VALUE)",
                "(↓1 CARDINAL) =c true",
            ],
        ))


    # --- Phase 9.X.c40: ADJ + cardinal-N stacked NP-level rule ----
    #
    # ``Ang natitirang limang buwan ay naroong maghati sa init at ulan.``
    #     "The remaining five months share between heat and rain."
    #                                              (PANAHON sent-3)
    #
    # The Phase 5f Commit 1 cardinal-NP rule (line 651) admits
    # ``DET + NUM[CARDINAL] + linker + N`` but does not extend
    # to a leading attributive ADJ + linker (``natitirang limang
    # buwan`` "remaining five months"). The N-level cardinal-N +
    # ADJ-modifier rules produce an N carrying BOTH ``CARDINAL_VALUE``
    # and ``ADJ-MOD``, but the simple NP-from-N rule (lines 101–133)
    # explicitly excludes ``CARDINAL_VALUE`` Ns to keep parses
    # unique with the bare cardinal-NP rule.
    #
    # This rule covers the gap: a 6-daughter direct rule that admits
    # ``CASE-MARKER + ADJ + linker + NUM[CARDINAL] + linker + N``,
    # mirroring the cardinal-NP rule with a leading ADJ-modifier
    # slot. Direct rule shape (not existence-constraints) so the
    # chart filters spurious matches at compile time, not at
    # tree-solving time.
    #
    # 12 rules: 3 cases × 2 outer linkers × 2 inner linkers.
    for case, marker in _cardinal_case_marker.items():
        for adj_link in ("NA", "NG"):
            for num_link in ("NA", "NG"):
                rules.append(Rule(
                    f"NP[CASE={case}]",
                    [
                        marker,
                        "ADJ",
                        f"PART[LINK={adj_link}]",
                        "NUM[CARDINAL]",
                        f"PART[LINK={num_link}]",
                        "N",
                    ],
                    [
                        "(↑) = ↓1",
                        "(↑ PRED) = ↓6 PRED",
                        "(↑ LEMMA) = ↓6 LEMMA",
                        "(↑ NUM) = ↓4 NUM",
                        "(↑ CARDINAL_VALUE) = ↓4 CARDINAL_VALUE",
                        "(↑ APPROX) = ↓4 APPROX",
                        "(↑ DISTRIB) = ↓4 DISTRIB",
                        "↓2 ∈ (↑ ADJ-MOD)",
                        "¬ (↓6 CARDINAL_VALUE)",
                        "¬ (↓2 STATIVE_PRED)",
                        "(↓4 CARDINAL) =c true",
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
                    "NUM[ORDINAL]",
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
                    # ``(↓2 CARDINAL) =c true`` — the non-conflict
                    # matcher would otherwise match CARDINAL=YES
                    # NUMs and create empty ORDINAL_VALUE fstructs).
                    "(↓2 ORDINAL) =c true",
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

    # --- 9.X.c8: NP-internal sa-PP locative/oblique modifier ---
    #
    # ``Ang panahon sa isang bansang tropiko ay kakatwa.`` "The
    # weather in a tropical country is strange" (R&G 1981 PANAHON
    # sent-1). ``ang bahay sa bukid`` "the house on the farm" (R&G
    # ``ang manok``). ``Bihira ang bagyo sa mga buwang ito.``
    # "Typhoons are rare in these months" (PANAHON sent-37). A
    # DAT-NP attaches at the right edge of the head NP as an
    # ADJUNCT member, projecting locative or oblique modification
    # onto the head N.
    #
    # Parallel to the §7.8 NP-internal possessive rule directly
    # above (``NP[CASE=X] → NP[CASE=X] NP[CASE=GEN]``) — same
    # right-edge attachment shape, but the inner NP is DAT-marked
    # and rides into ADJUNCT (set-valued) rather than POSS.
    #
    # No linker between head N and the sa-PP: Tagalog sa-PPs do
    # not take pre-PP linkers (cf. ``ang panahon **sa** isang
    # bansang tropiko`` — no ``na`` / ``-ng`` between ``panahon``
    # and ``sa``). This contrasts with N + ADJ modification which
    # does require a linker (``ang **magandang** panahon``).
    #
    # **PRED existential gates** on both daughters (``(↓1 PRED)`` /
    # ``(↓2 PRED)``) restrict the rule to N-projected NPs on both
    # head and modifier. PRON-projected NPs (``siya`` / ``ka`` /
    # bare DAT wh-PRON ``kanino``) carry no ``PRED`` on the lex
    # entry — their NP-projection f-structure is featureless for
    # ``PRED``. The gates block the over-generation
    # ``[PRON + bare-DAT-PRON]`` (e.g., ``*ka kanino`` as NP) that
    # would otherwise spawn from rule application onto pronominal
    # daughters where the construction is ungrammatical.
    #
    # Ambiguity note: this rule introduces PP-attachment
    # ambiguity with existing clause-level DAT-NP attachments
    # (e.g., ``Pumunta ang bata sa kalye`` admits both readings:
    # "The child went to the street" with sa-DAT as goal, and
    # "The child in the street went" with sa-DAT as N-modifier).
    # Both readings are linguistically grammatical; the grammar
    # produces parses for both. The audit-coverage gate verifies
    # no full-sentence loss from the added ambiguity.
    #
    # Reference: R&G 1981 §6.6 (NP modification with prepositional
    # phrases); R&G 1981 PANAHON essay.
    for case in ("NOM", "GEN", "DAT"):
        rules.append(Rule(
            f"NP[CASE={case}]",
            [f"NP[CASE={case}]", "NP[CASE=DAT]"],
            [
                "(↑) = ↓1",
                "↓2 ∈ (↑ ADJUNCT)",
                "(↓1 PRED)",
                "(↓2 PRED)",
            ],
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


    # --- Phase 9.P: NP-appositive proper-name attachment ---
    #
    # S&O 1972 §3.16(c) "Personal noun as second component;
    # personal-noun marker": when the first element of an NP
    # modification construction is a nominal, an appositive
    # personal-name-marked NP serves as a modifier of the head:
    #
    #   ang kaibigan niyang si Flor   "his/her friend Flor" (8.I pin)
    #   ang kapatid kong si Kathy     "my sister Kathy"
    #   ang senador na si Mr. Cruz    "the senator (named) Mr. Cruz"
    #
    # Rule shape (NP-level — operates after NP-possessive at 658):
    #
    #   NP[CASE=X] → NP[CASE=X]  PART[LINK=N{A,G}]  NP[CASE=NOM]
    #     (↑) = ↓1                  head supplies PRED, CASE, MARKER
    #     ↓3 ∈ (↑ APP)              appositive sits in the head's APP set
    #     (↓3 MARKER) =c 'SI'       gate to si-personal-name-marked NPs
    #
    # The outer case marker (ang/ng/sa) on the head NP determines
    # the construction's role in the matrix clause, per S&O — the
    # ``si`` before the personal noun does NOT mark the whole NP
    # nominative; it just signals personal-name appositive.
    #
    # The optional possessor case (``kaibigan niyang si Flor``)
    # falls out of the existing Phase 4 §7.8 NP-possessive rule
    # (immediately above) applying first to produce
    # ``[NP kaibigan niya]`` with POSS=niya, then this appositive
    # rule applying to that NP.
    #
    # Empirical scope: 2 audit-corpus hits closed by this rule
    # (8.I R&G Intermediate ``kaibigan niyang si Flor`` and the
    # 8.O R&G Intermediate ``kapatid kong si Kathy``). Construction
    # class extends naturally to N-head + linker + si-PROP with
    # any common/relational N as head and any GEN possessor.
    #
    # **No conflict with existing rules**: the only other NP-level
    # ``PART[LINK=N{A,G}]`` patterns in the grammar are the RC
    # wraps in ``cfg/extraction.py`` (3rd daughter = S_GAP or
    # S_XCOMP, not NP), so the category structure is disjoint.
    for case in ("NOM", "GEN", "DAT"):
        for link in ("NA", "NG"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [f"NP[CASE={case}]", f"PART[LINK={link}]", "NP[CASE=NOM]"],
                [
                    "(↑) = ↓1",
                    "↓3 ∈ (↑ APP)",
                    "(↓3 MARKER) =c 'SI'",
                ],
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
    # constraining equation ``(↓2 VAGUE) =c true`` enforces
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
                    "(↑ VAGUE) = true",
                    "¬ (↓4 VAGUE)",
                    "(↓2 VAGUE) =c true",
                ],
            ))

    # N-level companion rule (parang etc.). Mirrors the Phase 5f
    # Commit 1 N-level cardinal rule — produces N (not NP) for
    # consumers that compose at N level (e.g., the Phase 5e
    # Commit 26 ``parang isang aso`` rule selects an N
    # daughter). Chained-vague-Q blocking via ``¬ (↓3 VAGUE)``
    # parallel to the NP-level rule.
    #
    # **Phase 5n.B Commit 2 (§18 L43) tightening**: ``¬ (↓1 WH)``
    # excludes wh-Q daughters from this non-wh companion rule.
    # Pre-tightening, ``aling bata`` (Q[WH] daughter) fired
    # both this rule (producing N without WH) AND the Phase 5i
    # Commit 6 wh-Q+N companion (producing N[WH]). The non-WH
    # output then leaked into the new Phase 5n.B Commit 2
    # predicative-N clause rule (S → N NP[CASE=NOM]) because the
    # ``¬ (↓1 WH)`` constraint there was satisfied (WH was
    # already stripped by this rule). Tightening here closes the
    # leak at its source: wh-Qs go through the Phase 5i Commit 6
    # path only, non-wh Qs through this rule only.
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
                "(↑ VAGUE) = true",
                "¬ (↓3 VAGUE)",
                "(↓1 VAGUE) =c true",
                "¬ (↓1 WH)",
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
    # This wh-Q variant constrains on ``Q[VAGUE, WH]`` so
    # it fires only on Phase 5i wh-Q heads (``alin`` / ``ilan``-WH
    # / ``magkano``). The matrix N gets WH=YES + WH_LEMMA from the
    # Q daughter, on top of the QUANT / VAGUE lifts the non-wh rule
    # already provides. Phase 5i Commit 6's wh-N-cleft rule (in
    # cfg/clause.py) consumes the resulting N[WH].
    # LHS advertises ``WH=true, VAGUE=true`` so the Phase 5i Commit 6
    # wh-N cleft rule in cfg/clause.py (``S → N[WH] NP[CASE=NOM]``)
    # admits this N at completion time under the Phase 6.C
    # graph-constraint matcher.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N[WH=true, VAGUE=true]",
            [
                "Q[VAGUE, WH]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ QUANT) = ↓1 QUANT",
                "(↑ VAGUE) = true",
                "(↑ WH) = true",
                "(↑ WH_LEMMA) = ↓1 LEMMA",
                "¬ (↓3 VAGUE)",
                "(↓1 VAGUE) =c true",
                "(↓1 WH) =c true",
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
    # (``DET/ADP[CASE=X] Q[UNIV] N``) plus 1 bare-NOM
    # variant (``Q[UNIV] N``). The bare-NOM rule covers
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
                "(↑ UNIV) = true",
                "¬ (↓3 UNIV)",
                "(↓2 UNIV) =c true",
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
            "(↑ UNIV) = true",
            "(↑ CASE) = 'NOM'",
            "¬ (↓2 UNIV)",
            "(↓1 UNIV) =c true",
        ],
    ))


    # --- Phase 5n.C Commit 7.5: universal Q + NUM composition --
    #
    # Closes the Phase 5f Commit 20 deferred Q + NUM piece per
    # Phase 5n.C anti-deferral discipline. Adds parallel rules
    # mirroring the Q + N family above, with a NUM[CARDINAL]
    # complement instead of a bare N. Surfaces:
    #
    #   bawat isa       "every one / each one"
    #   bawat dalawa    "every two / each pair"
    #   kada isa        "every one (colloquial)"
    #   ang bawat isa   "the every one"
    #   sa bawat isa    "to every one"
    #
    # The Q-of-NUM construction names a quantifier scope over a
    # numerically-specified group ("each pair") or over each
    # individual ("each one") — semantically distributive, just
    # like Q + N. Once the NP composes, the Phase 5n.C Commit 7
    # L81 distributive-Q topic rule fires on it transparently
    # (its daughter pattern is ``NP[CASE=NOM]`` gated on
    # UNIV=YES, which both Q + N and Q + NUM produce).
    #
    # Rule shape mirrors Q + N:
    #
    # 4 rules total: 3 case-marked variants
    # (``DET/ADP[CASE=X] Q[UNIV] NUM[CARDINAL]``) plus
    # 1 bare-NOM variant (``Q[UNIV] NUM[CARDINAL]``).
    # CARDINAL_VALUE percolates from the NUM daughter so
    # downstream consumers can read the count
    # (``bawat dalawa`` carries CARDINAL_VALUE=2).
    #
    # The NUM bracket constraint ``[CARDINAL]`` restricts the
    # rule to genuine cardinals (``isa`` / ``dalawa`` / ``tatlo``
    # / ...) rather than firing on any NUM token (e.g.,
    # ordinals, vague numerics). The constraining equation
    # ``(↓last CARDINAL) =c 'YES'`` is the belt-and-braces
    # companion (matching the cardinal / ordinal / vague-Q
    # rules' positive constraint convention).
    for case, marker in _cardinal_case_marker.items():
        rules.append(Rule(
            f"NP[CASE={case}]",
            [marker, "Q", "NUM[CARDINAL]"],
            [
                "(↑) = ↓1",
                "(↑ PRED) = ↓3 PRED",
                "(↑ LEMMA) = ↓3 LEMMA",
                "(↑ QUANT) = ↓2 QUANT",
                "(↑ UNIV) = true",
                "(↑ CARDINAL_VALUE) = ↓3 CARDINAL_VALUE",
                "¬ (↓3 UNIV)",
                "(↓2 UNIV) =c true",
                "(↓3 CARDINAL) =c true",
            ],
        ))

    # Bare-NOM rule (parallel to the Q + N bare-NOM rule).
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["Q", "NUM[CARDINAL]"],
        [
            "(↑ PRED) = ↓2 PRED",
            "(↑ LEMMA) = ↓2 LEMMA",
            "(↑ QUANT) = ↓1 QUANT",
            "(↑ UNIV) = true",
            "(↑ CASE) = 'NOM'",
            "(↑ CARDINAL_VALUE) = ↓2 CARDINAL_VALUE",
            "¬ (↓2 UNIV)",
            "(↓1 UNIV) =c true",
            "(↓2 CARDINAL) =c true",
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
    # ``(↓2 DISTRIB_POSS) =c true`` gates the rule to
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
                    "(↑ DISTRIB_POSS) = true",
                    "¬ (↓4 DISTRIB_POSS)",
                    "(↓2 DISTRIB_POSS) =c true",
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
                "(↑ DISTRIB_POSS) = true",
                "(↑ CASE) = 'NOM'",
                "¬ (↓3 DISTRIB_POSS)",
                "(↓1 DISTRIB_POSS) =c true",
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
    # ``(↓2 WHOLE) =c true`` gates the rule to ``buo``;
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
                    "(↑ WHOLE) = true",
                    "¬ (↓4 WHOLE)",
                    "(↓2 WHOLE) =c true",
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
                "(↑ WHOLE) = true",
                "(↑ CASE) = 'NOM'",
                "¬ (↓3 WHOLE)",
                "(↓1 WHOLE) =c true",
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
    # The constraining equation ``(↓1 MEASURE) =c true`` gates
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
                "(↑ MEASURE) = true",
                "(↓1 MEASURE) =c true",
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
    # ``NUM[CARDINAL]`` so the existing cardinal-NP-modifier
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
        "NUM[CARDINAL]",
        [
            "NUM[CARDINAL]",
            "PART[DECIMAL_SEP]",
            "NUM[CARDINAL]",
        ],
        [
            "(↑) = ↓1",
            "(↑ FRACTIONAL_VALUE) = ↓3 CARDINAL_VALUE",
            "(↑ DECIMAL) = true",
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
            "(↓2 DECIMAL_SEP) =c true",
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
    #   (↓1 PLURAL_MARKER) =c true   — particle is mga
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
            "(↑ APPROX) = true",
            "(↓1 PLURAL_MARKER) =c true",
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
    # 1. ``NUM → PART[APPROX] NUM[CARDINAL]`` wraps a
    #    cardinal NUM. Output is NUM (preserving CARDINAL=YES
    #    + CARDINAL_VALUE), so the matrix-NP cardinal-modifier
    #    rule (Phase 5f Commit 1) consumes it directly:
    #    ``Bumili ako ng halos sampung aklat.`` parses as
    #    ``[halos sampu]ng aklat`` with CARDINAL_VALUE=10 +
    #    APPROX=YES on the matrix NP.
    # 2. ``Q → PART[APPROX] Q`` wraps a quantifier. Output
    #    is Q (preserving QUANT + VAGUE), so the existing
    #    Phase 5b partitive (``Q + NP[GEN]``) and Phase 5f
    #    Commit 15 vague-Q-modifier rules consume it:
    #    ``halos lahat ng bata`` partitive,
    #    ``halos maraming bata`` linker form.
    # 3. ``NUM → PART[PLURAL_MARKER] NUM[CARDINAL]``
    #    extends the Phase 5f Commit 13 mga rule from TIME
    #    NOUNs to cardinal NUMs. ``mga sampu`` "around ten"
    #    is the target; same surface uses the same lex entry,
    #    different rule.
    #
    # The constraining equation ``(↓1 APPROX) =c true`` (rules
    # 1 + 2) gates the daughter to actual approximator PARTs
    # (``halos`` / ``humigitkumulang``); ``(↓1 PLURAL_MARKER)
    # =c 'YES'`` (rule 3) gates to ``mga``. The
    # ``(↓2 CARDINAL) =c true`` constraint on rules 1 + 3
    # enforces the daughter is a genuinely cardinal NUM
    # (parallel to Commit 1's cardinal NP-modifier rule).
    # LHS advertises ``CARDINAL=true`` on the NUM-output rules so
    # downstream cardinal-NP-modifier rules (which expect
    # ``NUM[CARDINAL]``) admit these approximated NUMs under the
    # Phase 6.C graph-constraint matcher.
    rules.append(Rule(
        "NUM[CARDINAL=true]",
        ["PART", "NUM"],
        [
            "(↑) = ↓2",
            "(↑ APPROX) = true",
            "(↓1 APPROX) =c true",
            "(↓2 CARDINAL) =c true",
        ],
    ))
    rules.append(Rule(
        "Q",
        ["PART", "Q"],
        [
            "(↑) = ↓2",
            "(↑ APPROX) = true",
            "(↓1 APPROX) =c true",
        ],
    ))
    rules.append(Rule(
        "NUM[CARDINAL=true]",
        ["PART", "NUM"],
        [
            "(↑) = ↓2",
            "(↑ APPROX) = true",
            "(↓1 PLURAL_MARKER) =c true",
            "(↓2 CARDINAL) =c true",
        ],
    ))


    # --- Phase 5f Commit 17: numeric comparatives (Group H1
    # item 3) -----------------------------------------------------
    #
    # ``higit sa sampu`` "more than ten", ``kulang sa sampu``
    # "less than ten", ``hindi bababa sa sampu`` "no less than
    # ten / at least ten", ``hindi hihigit sa sampu`` "no more
    # than ten / at most ten". Four idiomatic phrase patterns
    # that wrap a NUM[CARDINAL] standard via the DAT marker
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
    # ``PART ADP[CASE=DAT] NUM[CARDINAL]``. Negated
    # patterns (hindi bababa / hindi hihigit): 4 daughters
    # ``PART[POLARITY=NEG] PART ADP[CASE=DAT] NUM[CARDINAL]``.
    #
    # Constraints follow the established Phase 5f pattern:
    # ``(↓N COMP_PHRASE) =c 'X'`` gates each rule to its
    # specific lex tag; ``(↓ CASE) =c 'DAT'`` enforces ``sa``
    # rather than ``ng`` / ``ang``; ``(↓ CARDINAL) =c true``
    # enforces a genuinely cardinal NUM (parallel to Commit 1
    # / 16's cardinal gate).
    # LHS advertises CARDINAL=true so downstream NP-from-NUM
    # projection rules (which expect ``NUM[CARDINAL]``) admit
    # these comparator NUMs under the Phase 6.C graph-constraint
    # matcher. ``(↑) = ↓3`` / ``(↑) = ↓4`` propagates CARDINAL=true
    # from the daughter cardinal NUM, so the LHS advertisement
    # matches the runtime state.
    for comp_lex, comp_value in (("HIGIT", "GT"), ("KULANG", "LT")):
        rules.append(Rule(
            "NUM[CARDINAL=true]",
            ["PART", "ADP", "NUM"],
            [
                "(↑) = ↓3",
                f"(↑ COMP) = '{comp_value}'",
                f"(↓1 COMP_PHRASE) =c '{comp_lex}'",
                "(↓2 CASE) =c 'DAT'",
                "(↓3 CARDINAL) =c true",
            ],
        ))
    for comp_lex, comp_value in (("BABABA", "GE"), ("HIHIGIT", "LE")):
        rules.append(Rule(
            "NUM[CARDINAL=true]",
            ["PART", "PART", "ADP", "NUM"],
            [
                "(↑) = ↓4",
                f"(↑ COMP) = '{comp_value}'",
                "(↓1 POLARITY) =c 'NEG'",
                f"(↓2 COMP_PHRASE) =c '{comp_lex}'",
                "(↓3 CASE) =c 'DAT'",
                "(↓4 CARDINAL) =c true",
            ],
        ))


    # --- Phase 8.R: clock-time hour construction (`alas` + Spanish-NUM)
    #
    # ``alas singko`` "5 o'clock", ``alas dose`` "12 o'clock". The
    # Spanish-loan PART ``alas`` (lex'd in particles.yaml with
    # ``CLOCK_MARKER=true``) combines with a Spanish cardinal numeral
    # to form an N[SEM_CLASS=TIME] suitable as a temporal NP head.
    #
    # Two rule variants accommodate both attested spellings:
    #   (a) space-separated: ``alas singko``
    #   (b) hyphenated:      ``alas-singko`` / ``alas-tres``
    #
    # The hyphenated variant consumes the orthographic hyphen
    # PUNCT[PUNCT_CLASS=HYPHEN] entry registered in particles.yaml
    # (parallel to PUNCT[PUNCT_CLASS=COMMA] for the comma). The
    # ``-`` token (Unicode HYPHEN-MINUS, U+002D) is polysemous —
    # the lex has two readings: PART[OP=MINUS] for arithmetic and
    # PUNCT[PUNCT_CLASS=HYPHEN] for compound-joining. The chart
    # picks by rule context; arithmetic ``5 - 3`` consumes the PART
    # reading via NUM-bracketed paths, and ``Alas-tres`` consumes
    # the PUNCT reading via this rule.
    #
    # Output feeds the Phase 5f Commit 12 minute-composition rules
    # (``alas otso y medya``), the Phase 5f Commit 14 ``mga``
    # approximation rule (``mga alas otso``), the standard NP wrappers
    # (``sa alas singko``, ``ng alas sais``), and bare-N predication
    # (``Alas singko.``) via the Phase 8.R impersonal-S rule.
    #
    # F-structure shape:
    #   SEM_CLASS  = 'TIME'
    #   TIME_VALUE = the Spanish numeral's CARDINAL_VALUE
    #   LEMMA      = 'alas' (carries through for downstream
    #                identification; the canonical surface form is
    #                the multi-token compound)
    rules.append(Rule(
        "N",
        ["PART[CLOCK_MARKER=true]", "NUM[CARDINAL]"],
        [
            "(↑ SEM_CLASS) = 'TIME'",
            "(↑ TIME_VALUE) = ↓2 CARDINAL_VALUE",
            "(↑ LEMMA) = ↓1 LEMMA",
            "(↓1 CLOCK_MARKER) =c true",
            "(↓2 CARDINAL) =c true",
        ],
    ))
    rules.append(Rule(
        "N",
        [
            "PART[CLOCK_MARKER=true]",
            "PUNCT[PUNCT_CLASS=HYPHEN]",
            "NUM[CARDINAL]",
        ],
        [
            "(↑ SEM_CLASS) = 'TIME'",
            "(↑ TIME_VALUE) = ↓3 CARDINAL_VALUE",
            "(↑ LEMMA) = ↓1 LEMMA",
            "(↓1 CLOCK_MARKER) =c true",
            "(↓2 PUNCT_CLASS) =c 'HYPHEN'",
            "(↓3 CARDINAL) =c true",
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
    # (NUM[CARDINAL] for cardinal minutes,
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
    #   (↓3 CARDINAL) =c true OR     — third daughter is right type
    #   (↓3 SEM_CLASS) =c 'FRACTION'
    for op in ("Y", "MENOS"):
        # Cardinal-minute version: ``alasotso y singko``
        rules.append(Rule(
            "N",
            ["N", "PART", "NUM[CARDINAL]"],
            [
                "(↑) = ↓1",
                "(↑ MINUTE_VALUE) = ↓3 CARDINAL_VALUE",
                f"(↑ MINUTE_OP) = '{op}'",
                "(↓1 SEM_CLASS) =c 'TIME'",
                f"(↓2 MINUTE_OP) =c '{op}'",
                "(↓3 CARDINAL) =c true",
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
    # Constraining ``(↓2 DIGIT_FORM) =c true`` restricts the
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
        ["N", "NUM[CARDINAL]"],
        [
            "(↑) = ↓1",
            "(↑ DAY_OF_MONTH) = ↓2 CARDINAL_VALUE",
            "(↓1 SEM_CLASS) =c 'MONTH'",
            "(↓2 DIGIT_FORM) =c true",
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
        # Phase 9.O.3 ``¬ (↓1 STATIVE_PRED)`` constraint: stative-
        # passive ADJs (``kilala`` / ``mahal``) carry STATIVE_PRED
        # for the predicate-with-GEN-actor reading. They must NOT
        # participate as prenominal modifiers — when a single
        # surface has both V/PSYCH (``gustong`` linker form) and
        # ADJ/STATIVE_PRED analyses, the ADJ-modifier path
        # spuriously competes with the control-XCOMP path
        # (Phase 6 LDD test ``test_psych_av_inner``); excluding
        # STATIVE_PRED ADJs from the modifier role resolves the
        # ambiguity without breaking the bare-predicate STATIVE_PRED
        # rule. ``STATIVE_PRED-flagged`` ADJs only fire in
        # predicate position (S-level), not modifier position.
        rules.append(Rule(
            "N",
            ["ADJ", f"PART[LINK={link}]", "N"],
            [
                "(↑) = ↓3",
                "↓1 ∈ (↑ ADJ-MOD)",
                "¬ (↓1 STATIVE_PRED)",
            ],
        ))
        # Post-N: the head N comes first.
        rules.append(Rule(
            "N",
            ["N", f"PART[LINK={link}]", "ADJ"],
            [
                "(↑) = ↓1",
                "↓3 ∈ (↑ ADJ-MOD)",
                "¬ (↓3 STATIVE_PRED)",
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
    # LHS advertises ``PREDICATIVE=true, COMP_DEGREE=COMPARATIVE`` so
    # the Phase 5g Commit 3 predicative-ADJ-S rule
    # (``S → ADJ[PREDICATIVE] NP[CASE=NOM]``) admits the mas-wrapped
    # ADJ under the Phase 6.C graph-constraint matcher. Per
    # roadmap §12.1, all ma- ADJ lex entries carry PREDICATIVE=true,
    # so ``(↑) = ↓2`` (which shares the inner ADJ's f-structure)
    # always produces a wrapped ADJ with PREDICATIVE=true on the
    # f-graph; the LHS advertisement matches that runtime state.
    rules.append(Rule(
        "ADJ[PREDICATIVE=true, COMP_DEGREE=COMPARATIVE]",
        ["PART[COMP_DEGREE=COMPARATIVE]", "ADJ"],
        [
            "(↑) = ↓2",
            "(↑ COMP_DEGREE) = 'COMPARATIVE'",
            "(↓1 COMP_DEGREE) =c 'COMPARATIVE'",
        ],
    ))


    # --- Phase 5n.B Commit 5: formal ``nang higit`` ADJ-wrapper (§18 L41) ---
    #
    # ``Nang higit matalino si Maria.``
    #     "Maria is more intelligent." (formal register)
    # ``Nang higit maganda ang bata.``
    #     "The child is more beautiful."
    # ``Nang higit matalino si Maria kaysa kay Juan.``
    #     "Maria is more intelligent than Juan." (formal +
    #     existing kaysa wrap)
    #
    # Closes §18 L41 (formal ``nang higit`` comparison; carried
    # forward from Phase 5h §9.2 — ``mas`` is the standard /
    # colloquial comparative, ``nang higit`` is the formal
    # alternative). Per the §18.2 detail, two resolution paths
    # were available: a clausal rule shape ``S → S PART[nang]
    # PART[higit] ADJ``, or extending the Phase 5h Commit 3
    # ``mas`` wrapper to admit the multi-word ``nang higit``
    # particle sequence.
    #
    # **Resolution path chosen**: the wrapper-rule path. ``nang
    # higit + ADJ`` produces an ADJ[COMP_DEGREE=COMPARATIVE]
    # parallel to the ``mas + ADJ`` wrapper output, so the
    # existing Phase 5g Commit 3 predicative-ADJ clause rule and
    # the Phase 5h Commit 4 kaysa wrap consume the result
    # unchanged. This keeps the comparative semantics in one
    # place (the ADJ-wrapper layer) and avoids a separate clausal
    # rule that would duplicate the mas / kaysa composition logic.
    #
    # **Equation analysis** (mirrors Phase 5h Commit 3):
    #
    # * ``(↑) = ↓3`` shares the inner ADJ's f-structure with the
    #   wrapped output (PRED, PREDICATIVE, ADJ_LEMMA percolate).
    # * ``(↑ COMP_DEGREE) = 'COMPARATIVE'`` writes COMPARATIVE
    #   onto the matrix ADJ. Unification with an inner ADJ
    #   already carrying SUPERLATIVE (``pinakamatalino``) fails
    #   — ``*nang higit pinakamatalino`` correctly ungrammatical.
    # * ``(↑ REGISTER) = 'FORMAL'`` marks the formal register
    #   distinguishing this from the colloquial ``mas`` form.
    # * ``(↓1 LEMMA) =c 'nang'`` constrains daughter 1 to the
    #   ``nang`` PART (existing temporal-since lex entry — its
    #   ``COMP_TYPE=TEMP_SINCE`` doesn't leak because ``(↑) =
    #   ↓3`` doesn't share daughter 1's f-structure).
    # * ``(↓2 COMP_PHRASE) =c 'HIGIT'`` constrains daughter 2 to
    #   the ``higit`` PART (Phase 5f Commit 17 numeric-comparator
    #   lex entry). Same lex polysemy — the comparative-clause
    #   path here is gated by the trailing ADJ.
    # * ``(↓3 PREDICATIVE) =c true`` belt-and-braces on the
    #   ADJ daughter (matches Phase 5h Commit 3 / 5 convention).
    #
    # Polysemy safety: ``nang higit + ADJ`` and ``higit sa N``
    # (Phase 5f Commit 17 numeric comparator) don't conflict —
    # ``higit sa N`` requires a NUM head and a DAT-NP standard;
    # ``nang higit + ADJ`` requires an ADJ daughter. The two
    # paths are structurally disjoint.
    # Same LHS advertise as the mas / intensifier ADJ-wrappers
    # above so the Phase 5g predicative-ADJ-S rule admits the
    # ``nang higit``-wrapped ADJ under the Phase 6.C graph-
    # constraint matcher.
    rules.append(Rule(
        "ADJ[PREDICATIVE=true, COMP_DEGREE=COMPARATIVE]",
        ["PART[LEMMA=nang]", "PART[COMP_PHRASE=HIGIT]", "ADJ"],
        [
            "(↑) = ↓3",
            "(↑ COMP_DEGREE) = 'COMPARATIVE'",
            "(↑ REGISTER) = 'FORMAL'",
            "(↓1 LEMMA) =c 'nang'",
            "(↓2 COMP_PHRASE) =c 'HIGIT'",
            "(↓3 PREDICATIVE) =c true",
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
    # * ``(↑ INTENSIFIER) = true`` and ``(↓1 INTENSIFIER) =c true``
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
    # ::matches), so ``PART[INTENSIFIER]`` matches any PART
    # without an INTENSIFIER feature by absorption, and similarly
    # ``PART[LINK=NA]`` matches any PART without LINK. Without the
    # explicit constraining equations, ``Lubos na mas matalino
    # siya`` would parse: ``mas`` (PART[COMP_DEGREE=COMPARATIVE],
    # no LINK) would absorb the ``PART[LINK=NA]`` slot. The two
    # ``=c`` equations close the leak — same pattern as Phase 5h
    # Commit 3's ``(↓1 POLARITY) =c 'NEG'`` fix on the hindi-
    # negation rule.
    # LHS advertises ``PREDICATIVE=true, INTENSIFIER=true,
    # COMP_DEGREE=INTENSIVE`` so the Phase 5g predicative-ADJ-S rule
    # admits the wrapped ADJ under the Phase 6.C graph-constraint
    # matcher. ``(↑) = ↓3`` shares the inner ADJ's f-structure;
    # per roadmap §12.1 ADJ lex entries carry PREDICATIVE=true,
    # so the wrapped output reliably has PREDICATIVE=true on the
    # f-graph.
    for link in ("NA", "NG"):
        rules.append(Rule(
            "ADJ[PREDICATIVE=true, INTENSIFIER=true, COMP_DEGREE=INTENSIVE]",
            [
                "PART[INTENSIFIER]",
                f"PART[LINK={link}]",
                "ADJ",
            ],
            [
                "(↑) = ↓3",
                "(↑ INTENSIFIER) = true",
                "(↑ COMP_DEGREE) = 'INTENSIVE'",
                "(↑ INTENSITY) = ↓1 INTENSITY",
                "(↓1 INTENSIFIER) =c true",
                f"(↓2 LINK) =c '{link}'",
            ],
        ))

    # --- 9.X.c17: N-level intensifier wrap (parallel to ADJ form) ----
    #
    # ``masyadong pansin`` "(too much) attention" (R&G 1981 PANAHON
    # sent-40 — ``Hindi niya masyadong pansin ang paglipas nito``).
    # ``lubhang ginhawa`` "(extreme) comfort" — generic parallel.
    #
    # Mirrors the Phase 5h Commit 3 ADJ-intensifier-wrap directly
    # above (``ADJ → PART[INTENSIFIER] PART[LINK] ADJ``) but at the
    # N level for intensified nominal heads. Used in nominal-
    # predicate constructions where the intensifier scopes over
    # the N (``Hindi niya masyadong pansin ang X`` "She doesn't
    # give too much attention to X").
    #
    # The matrix N is tagged ``INTENSIFIER=true`` and inherits
    # ``INTENSITY`` from the wrapping PART. The inner-N's
    # f-structure shares with the matrix via ``(↑) = ↓3`` so the
    # downstream nominal-pred rules (``S → N NP[CASE=NOM]`` /
    # ``S → N NP[CASE=GEN] NP[CASE=NOM]``) admit the wrapped N.
    #
    # Reference: S&O 1972 §3.13 (intensifier modification on
    # nouns); R&G 1981 PANAHON essay (sent-40).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "N",
            [
                "PART[INTENSIFIER]",
                f"PART[LINK={link}]",
                "N",
            ],
            [
                "(↑) = ↓3",
                "(↑ INTENSIFIER) = true",
                "(↑ INTENSITY) = ↓1 INTENSITY",
                "(↓1 INTENSIFIER) =c true",
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
        # Same LHS advertise as the with-linker variant above.
        "ADJ[PREDICATIVE=true, INTENSIFIER=true, COMP_DEGREE=INTENSIVE]",
        ["PART[INTENSITY=MODERATE]", "ADJ"],
        [
            "(↑) = ↓2",
            "(↑ INTENSIFIER) = true",
            "(↑ COMP_DEGREE) = 'INTENSIVE'",
            "(↑ INTENSITY) = ↓1 INTENSITY",
            "(↓1 INTENSITY) =c 'MODERATE'",
            "(↓1 INTENSIFIER) =c true",
        ],
    ))


    # --- Phase 5h Commit 7: comparative Q-wrapper ---------------
    #
    # ``mas maraming aklat`` "more books" — comparative quantification
    # over the existing Phase 5f vague-Q heads. The Phase 5h Commit 3
    # ``mas`` PART (lex feat ``COMP_DEGREE: COMPARATIVE``) wraps a
    # ``Q[VAGUE]`` head (``marami``, ``kaunti``, ``konti``,
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
    # * ``(↓2 VAGUE) =c true`` belt-and-braces constraint on the
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
    # LHS advertises ``VAGUE=true, COMP_DEGREE=COMPARATIVE`` so the
    # Phase 5n.B Commit 1 predicative-Q clause rule (which expects
    # ``Q[VAGUE]``) admits the mas-wrapped Q under the Phase 6.C
    # graph-constraint matcher. ``(↑) = ↓2`` already shares the
    # inner Q's f-structure (including VAGUE=true), so the LHS
    # advertisement matches what the rule produces.
    rules.append(Rule(
        "Q[VAGUE=true, COMP_DEGREE=COMPARATIVE]",
        ["PART[COMP_DEGREE=COMPARATIVE]", "Q[VAGUE]"],
        [
            "(↑) = ↓2",
            "(↑ COMP_DEGREE) = 'COMPARATIVE'",
            "(↓1 COMP_DEGREE) =c 'COMPARATIVE'",
            "(↓2 VAGUE) =c true",
        ],
    ))

    # === Phase 5m Commit 8: indefinite ``kahit`` + wh productive =====
    #
    # ``kahit sino`` "anyone", ``kahit ano`` "anything",
    # ``kahit saan`` "anywhere", ``kahit kailan`` "anytime".
    # Productive composition of the Phase 5l ``kahit`` (PART
    # [COMP_TYPE=CONC]) with the Phase 5i wh-PRON / wh-ADV
    # inventory (``sino`` / ``ano`` / ``alin`` / ``saan`` /
    # ``kailan`` / ``bakit`` / ``paano``).
    #
    # Two parallel rules:
    #
    #   PRON → PART[LEMMA=kahit] PRON[WH]   (IndefPRON)
    #   ADV  → PART[LEMMA=kahit] ADV[WH]    (IndefADV)
    #
    # Each builds an indefinite PRON / ADV by overlaying
    # ``INDEF=YES`` onto the inner wh-element's f-structure
    # (``(↑) = ↓2``). The ``kahit`` daughter joins the matrix's
    # ADJUNCT set as a member, preserving the c-structure
    # provenance. The ``LEMMA=kahit`` constraint excludes other
    # CONC particles (``bagaman``) from firing as indefinite-
    # builders.
    #
    # Disambiguation with Phase 5l concessive ``kahit S``:
    # the daughter category (S vs PRON/ADV) deterministically
    # picks the right rule. ``Kahit umulan, …`` builds a
    # SubordClause; ``Kahit sino …`` builds a PRON.
    #
    # Reference: R&G 1981 §6.6.
    # Two sibling rule shapes:
    #
    # 1. Bare-PRON LHS — retained for Phase 5m / 5n compatibility:
    #    legacy non-conflict matcher allowed the wrapped PRON to
    #    project to any-case NP via the bare LHS, so e.g.,
    #    ``Kumain siya kahit ano.`` could fit ``kahit ano`` into
    #    the OBJ (CASE=GEN) slot even though ``ano`` is lex'd
    #    CASE=NOM. The lex doesn't carry GEN/DAT variants for the
    #    wh-PRONs, so without this fallback that cross-case usage
    #    0-parses.
    # 2. Per-CASE parameterized LHS — added in Phase 6.C C3d for
    #    the graph-constraint matcher. Advertises CASE so the
    #    NP-from-PRON projection (``NP[CASE=X] → PRON[CASE=X]``)
    #    admits the wrapped PRON under strict matching for the
    #    same-case slot.
    rules.append(Rule(
        "PRON",
        ["PART", "PRON"],
        [
            "(↑) = ↓2",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↑ INDEF) = 'YES'",
            "(↓1 LEMMA) =c 'kahit'",
            "(↓2 WH) =c true",
        ],
    ))
    for case in ("NOM", "GEN", "DAT"):
        rules.append(Rule(
            f"PRON[INDEF=YES, CASE={case}]",
            ["PART", f"PRON[CASE={case}]"],
            [
                "(↑) = ↓2",
                "↓1 ∈ (↑ ADJUNCT)",
                "(↑ INDEF) = 'YES'",
                "(↓1 LEMMA) =c 'kahit'",
                "(↓2 WH) =c true",
                f"(↓2 CASE) =c '{case}'",
            ],
        ))

    # Phase 7a.G (§18.1.1 item 10): NP-level projection of
    # `kahit + wh-PRON` directly into case-marked NPs for
    # non-NOM argument slots (GEN-OBJ, DAT-OBL/recipient).
    #
    # Background: the Phase 6.C C3d case-parameterized IndefPRON
    # rules above only fire when the daughter wh-PRON's lex CASE
    # matches the matrix output CASE. But `sino` / `ano` / `alin`
    # are lex'd as CASE=NOM only (the analyzer indexes pronouns
    # by surface in a dict-of-single, so multiple CASE variants
    # of the same surface collide). The plan-of-record §3.8
    # outlines two paths: (a) lex variants (blocked by the
    # analyzer-indexing limitation) or (b) an any-case wh-indef
    # projection rule. This implements (b).
    #
    # Two rules mirror the Phase 5i C3 in-situ wh-PRON shell
    # rules (nominal.py:172-193) but replace the ADP daughter
    # with a bare PART (gated to `kahit`):
    #
    #   NP[CASE=GEN, WH=true] → PART PRON[WH]
    #   NP[CASE=DAT, WH=true] → PART PRON[WH]
    #
    # The bare PRON daughter need not have matching CASE (the
    # matrix's CASE is set by the LHS LHS atom), so the NOM-only
    # `sino` / `ano` / `alin` lex entries can fill these projections.
    for case in ("GEN", "DAT"):
        rules.append(Rule(
            f"NP[CASE={case}, WH=true]",
            ["PART", "PRON[WH]"],
            [
                "(↑ PRED) = 'WH-PRO'",
                "(↑ INDEF) = 'YES'",
                "(↑ WH) = ↓2 WH",
                "(↑ LEMMA) = ↓2 LEMMA",
                "(↑ WH_LEMMA) = ↓2 LEMMA",
                "↓1 ∈ (↑ ADJUNCT)",
                "(↓1 LEMMA) =c 'kahit'",
                "(↓2 WH) =c true",
                # Gate to NOM-source wh-PRONs only. The DAT-source
                # `kanino` already has a CASE=DAT lex variant that
                # the Phase 6.C C3d DAT-IndefPRON rule handles
                # natively; this rule's purpose is the cross-case
                # projection for NOM-only wh-PRONs (ano/sino/alin).
                "(↓2 CASE) =c 'NOM'",
            ],
        ))
    rules.append(Rule(
        "ADV[INDEF=YES]",
        ["PART", "ADV"],
        [
            "(↑) = ↓2",
            "↓1 ∈ (↑ ADJUNCT)",
            "(↑ INDEF) = 'YES'",
            "(↓1 LEMMA) =c 'kahit'",
            "(↓2 WH) =c true",
        ],
    ))

    # === Phase 5n.B Commit 22: productive wh + man → neg-indef PRON ===
    #
    # ``Walang ano man.``     "There is nothing." (productive form
    #                         of ``Walang anuman.``)
    # ``Walang sino man.``    (rare productive form of ``Walang
    #                         sinuman.``)
    #
    # Closes part of §18.1 deferral L46 + L102. The rule composes
    # a wh-PRON with the ``man`` 2P-clitic (PART[ADV=EVEN, LEMMA=
    # man]) into a virtual ``PRON[INDEF=NEG_INDEF]``. The existing
    # Phase 5m C9 negative-existential rule then fires on the
    # produced PRON without modification, parallel to the closure
    # path for ``Walang sinuman.`` / ``Walang anuman.``
    # (lexicalized contracted forms).
    #
    # The lexicalized contracted forms (``sinuman`` / ``anuman``)
    # cover the common cases by direct lex (``data/tgl/pronouns.yaml``);
    # this rule covers the productive non-contracted spelling
    # (``ano man``) plus any wh-PRON where the contracted form
    # isn't lexicalized.
    #
    # The ``LEMMA=man`` constraint excludes other 2P-clitics
    # (na / pa / daw / rin / lang / nga / ba / ho / po / kasi /
    # ...) — only ``man`` (the EVEN/CONCESSIVE particle) functions
    # as a productive negative-indef builder.
    # LHS advertises ``INDEF=NEG_INDEF`` so the Phase 5j Commit 9
    # negative-existential rule (which expects
    # ``PRON[INDEF=NEG_INDEF]``) admits this productive wh+man
    # PRON under the Phase 6.C graph-constraint matcher.
    rules.append(Rule(
        "PRON[INDEF=NEG_INDEF]",
        ["PRON", "PART"],
        [
            "(↑) = ↓1",
            "(↓1 WH) =c true",
            "(↓2 ADV) =c 'EVEN'",
            "(↓2 LEMMA) =c 'man'",
            "(↑ INDEF) = 'NEG_INDEF'",
        ],
    ))

    # === Phase 5m Commit 7: emphatic ``mismo`` post-N attachment =====
    #
    # ``Maria mismo`` "Maria herself", ``ang bata mismo`` "the child
    # himself". The PART ``mismo`` (Commit 1 lex, EMPHATIC,
    # LEMMA=mismo) attaches as an ADJUNCT member of the NP it
    # follows. Distribution: post-NP only — pre-NP attachment is
    # ungrammatical in Tagalog (cf. Spanish ``mismo Juan`` is valid
    # but the Tagalog calque inverts position).
    #
    # The constraining equations gate on ``EMPHATIC=YES`` AND
    # ``LEMMA=mismo`` — the latter prevents cross-fire from other
    # EMPHATIC=YES particles (the existing ``nga`` is EMPHATIC but
    # is a 2P clitic, not a post-N modifier; the LEMMA constraint
    # ensures only ``mismo`` fires here). The matrix-NP overlay
    # ``(↑ EMPHATIC) = true`` exposes the emphatic marker at the
    # NP top level for downstream consumers.
    #
    # Reference: R&G 1981 §7.3.
    #
    # Phase 5n.A Commit 19 (§18 L85 follow-on): tightened the daughter
    # category from bare ``PART`` to ``PART[LEMMA=mismo, EMPHATIC]``.
    # The bare PART version was too permissive — every NP-PART
    # adjacency in the input (e.g., ``si Jose .`` with period PUNCT,
    # or ``Ana at`` in coord-NP contexts) spawned a failed mismo
    # parse path, polluting the Earley chart and blocking 5+-NP
    # coord at the well-formedness pass. The category-level
    # constraint adds defining-equation pressure on the predicted
    # daughter so the parser can prune at predict-time rather than
    # generate-and-filter at unification-time.
    # LHS parameterized over CASE so matrix rules expecting
    # ``NP[CASE=X]`` admit the mismo-attached NP under the
    # Phase 6.C graph-constraint matcher. ``(↑) = ↓1`` already
    # propagates CASE on the f-graph; the LHS pattern advertises
    # it.
    for case in ("NOM", "GEN", "DAT"):
        rules.append(Rule(
            f"NP[CASE={case}]",
            [f"NP[CASE={case}]", "PART[LEMMA=mismo, EMPHATIC]"],
            [
                "(↑) = ↓1",
                "↓2 ∈ (↑ ADJUNCT)",
                "(↓2 EMPHATIC) =c true",
                "(↓2 LEMMA) =c 'mismo'",
                "(↑ EMPHATIC) = true",
            ],
        ))

    # === 9.X.c21: post-NP topic-marker ``naman`` attachment ============
    #
    # ``Ang ulan naman na kasama nito ay nagpapabaha.`` (R&G 1981
    # PANAHON sent-23). ``naman`` after a NOUN-headed NP functions
    # as a topic-contrast discourse marker ("the rain, however / on
    # the other hand"). Pre-9.X.c21 this surface was blocked
    # because the homophone disambiguator (correctly) selects the
    # non-clitic ``naman`` after a NOUN host, but no NP-internal
    # attachment rule existed to consume it — so it stayed in
    # place between the topic NP and the subsequent linker / ay.
    #
    # Rule shape mirrors the Phase 5m C7 ``mismo`` post-NP rule
    # directly above — set-valued ADJUNCT membership rather than a
    # scalar slot, since topic-contrast is a sentential-discourse
    # marker that scopes over the matrix proposition via its
    # attachment to the topic NP.
    #
    #   NP[CASE=X] → NP[CASE=X] PART[LEMMA=naman]
    #     (↑) = ↓1                head NP supplies CASE / PRED / etc.
    #     ↓2 ∈ (↑ ADJUNCT)       naman joins ADJUNCT set
    #     (↓2 LEMMA) =c 'naman'   lemma gate (excludes other PARTs)
    #
    # Disambiguation: the existing CLITIC_CLASS=2P ``naman`` entry
    # (post-V Wackernagel reading) is morphologically distinct —
    # the disambiguator (``clitics/placement.py``) selects the
    # non-clitic entry when ``naman`` follows a NOUN, and that's
    # the entry this rule consumes.
    #
    # Reference: R&G 1981 §7.3 (topic-contrast naman); R&G 1981
    # PANAHON essay (sent-23).
    for case in ("NOM", "GEN", "DAT"):
        rules.append(Rule(
            f"NP[CASE={case}]",
            [f"NP[CASE={case}]", "PART"],
            [
                "(↑) = ↓1",
                "↓2 ∈ (↑ ADJUNCT)",
                "(↓2 LEMMA) =c 'naman'",
            ],
        ))

    # === Phase 5n.A Commit 7: depictive ``mag-isa`` post-PRON via linker (§18 L62+L63) =====
    #
    # ``Nakatira siyang mag-isa sa bahay.`` "He lives by himself in the
    # house" — R&G "Ang Manok" simple #3. The ``siyang mag-isa``
    # constituent is a SUBJ NP: PRON[CASE=NOM] head + bound ``-ng``
    # linker + depictive ADV ``mag-isa`` ("alone / by oneself"). The
    # ADV functions as a depictive secondary predicate over the PRON
    # SUBJ, attaching as an ADJUNCT member of the NP.
    #
    # Distribution: scoped to ``mag-isa`` only via the
    # ``(↓3 MAGISA) =c true`` constraining equation (matches the
    # MAGISA flag set on the ``magisa`` lex entry — Phase 5n.A
    # Commit 5). Future depictive ADVs (e.g., ``siyang mabilis`` "him
    # being-quick", ``siyang madalas`` "him often") would either need
    # additional rules or a more general ``DEPICTIVE=YES`` feat — both
    # deferred until corpus pressure surfaces additional tokens.
    #
    # The matrix-NP overlay ``(↑ MAGISA) = true`` exposes the
    # depictive marker at the NP top level for downstream consumers.
    #
    # Reference: S&O 1972 §3.5 (depictive secondary predicates); R&G
    # 1981 §6.6 (combined "Ang Manok" essay-paragraph).
    rules.append(Rule(
        "NP[CASE=NOM]",
        ["PRON[CASE=NOM]", "PART", "ADV"],
        [
            "(↑) = ↓1",
            "↓3 ∈ (↑ ADJUNCT)",
            "(↓2 LINK) =c 'NG'",
            "(↓3 MAGISA) =c true",
            "(↑ MAGISA) = true",
        ],
    ))

    # === Phase 5n.A Commit 8: depictive ``mag-isa`` post-ADJ via linker (§18 L64) =====
    #
    # ``May isang mamang matanda na nakatirang mag-isa sa maliit na
    # bahay na nasa tuktok ng mataas na bundok sa bukid.`` — R&G "Ang
    # Manok" combined essay-paragraph (R&G p. 482). The
    # ``mamang ... nakatirang mag-isa`` constituent is N + linker +
    # ADJ-with-depictive: the resultative ADJ ``nakatira`` is itself
    # modified by the depictive ADV ``mag-isa`` ("alone"). The
    # ADJ-internal composition is structurally parallel to the
    # Phase 5n.A Commit 7 PRON-internal version
    # (``NP[CASE=NOM] → PRON[CASE=NOM] PART[LINK=NG] ADV[MAGISA]``)
    # but at the ADJ level so the result feeds back into the existing
    # Phase 5g Commit 2 NP-internal ADJ-modifier rules
    # (``N → N PART[LINK=N{A,G}] ADJ``).
    #
    # Both linker variants admitted; same ``MAGISA=YES`` gate
    # narrowly scopes the rule to the mag-isa lex (Commit 5).
    #
    # Reference: S&O 1972 §3.5 (depictive secondary predicates); R&G
    # 1981 p. 482 (combined essay-paragraph).
    for link in ("NA", "NG"):
        rules.append(Rule(
            "ADJ",
            ["ADJ", f"PART[LINK={link}]", "ADV"],
            [
                "(↑) = ↓1",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↓3 MAGISA) =c true",
                "(↑ MAGISA) = true",
            ],
        ))
