# tgllfg/cfg/grammar.py

"""Default Tagalog grammar.

The grammar is V-initial. Sentences are flat ``S → V (NP)*`` rules
that distinguish:

* the verb's voice (``AV`` / ``OV`` / ``DV`` / ``IV``);
* the case of each post-verbal NP (``NOM`` / ``GEN`` / ``DAT``);
* the relative order of the post-verbal NPs (Tagalog freely permits
  ``ang``-NP and ``ng``-NP in either order).

The grammar's case→GF mapping is uniform across all four voices —
``ang``-NP (``NOM``) is SUBJ; ``ng``-NP (``GEN``) is OBJ; ``sa``-NP
(``DAT``) attaches as a member of the f-structure's ``ADJUNCT`` set.
The OBJ analysis of the *ng*-non-pivot in transitive non-AV is
established in Phase 1; Phase 4 generalises it to DV and IV
(``docs/analysis-choices.md`` "ng-non-pivot in transitive non-AV →
OBJ" + "Phase 4 §7.1: voice and case extensions").

``OBL-LOC`` / ``OBL-GOAL`` / ``OBL-BEN`` classification of *sa*-NPs
is deferred to Phase 5 (LMT-driven mapping); for now they ride
through the f-structure as a non-governable ``ADJUNCT`` set, which
sidesteps coherence by design.

The argument-structure secondary features ``APPL ∈ {INSTR, BEN,
REASON, CONVEY, ∅}`` and ``CAUS ∈ {DIRECT, INDIRECT, ∅}`` are
recognised by the grammar (lex_entry templates may carry them), but
no Phase 4 grammar rule consumes them yet — applicatives and
causatives proper land in §7.7.

Phase 4 §7.2 adds clausal negation: ``hindi`` (declarative
``POLARITY=NEG``) and ``huwag`` (imperative ``POLARITY=NEG, MOOD=IMP``)
attach as a left-edge particle to a full ``S``. The matrix
f-structure inherits ``PRED``/``VOICE``/``ASPECT``/``SUBJ``/``OBJ``
from the inner clause and overlays ``POLARITY`` (and, for ``huwag``,
``MOOD=IMP``) from the particle.

Phase 4 §7.4 (ay-inversion) and §7.5 (relativization) introduce a
SUBJ-gapped non-terminal ``S_GAP``: a clause whose surface is
``V (NP[CASE=GEN])* (NP[CASE=DAT])*`` — i.e. an inner S without the
NOM-marked SUBJ argument. Each S_GAP rule binds its missing SUBJ to
``REL-PRO`` via ``(↑ SUBJ) = (↑ REL-PRO)``; an enclosing wrap rule
then sets ``REL-PRO`` from the displaced phrase (the ay-fronted
topic, or the head NP of a relative clause). The SUBJ-only
restriction on relativization is enforced by the wrap rule's
constraining equation ``(↓3 REL-PRO) =c (↓3 SUBJ)``: vacuous today
because S_GAP only has SUBJ-gapped frames, but ready for the
non-SUBJ-gap variants that would arise under §7.6 long-distance or
§7.8 non-pivot ay-fronting.

Phase 4 §7.6 (control & raising) adds ``S_XCOMP``: a separate
SUBJ-gapped non-terminal restricted to ``V[VOICE=AV]`` frames. The
distinction from ``S_GAP`` is voice-coverage: relativization can
have OV / DV / IV embedded clauses (pivot-relativization works in
any voice), but control complements canonically only license AV
embedded clauses (the controllee is the actor, which is SUBJ in AV
only). Control wrap rules attach ``S_XCOMP`` to a control verb plus
its arguments and bind matrix SUBJ to ``XCOMP REL-PRO``. The
control verb's class is discriminated by ``CTRL_CLASS ∈ {PSYCH,
INTRANS, TRANS}`` carried on the V's morph analysis (per-root
``feats`` field on inflected verbs; particles.yaml entry on
uninflected psych predicates).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class Rule:
    lhs: str
    rhs: list[str]          # nonterminals/terminals with feature labels like NP[CASE=NOM]
    equations: list[str]    # LFG equations using ↑ and ↓i (i = child index, 1-based)


# Equations every clausal rule emits to percolate verb features up
# to the matrix f-structure. ``↓1`` is always the verb in our
# V-initial rules.
_VERB_PERCOLATION: tuple[str, ...] = (
    "(↑ PRED) = ↓1 PRED",
    "(↑ VOICE) = ↓1 VOICE",
    "(↑ ASPECT) = ↓1 ASPECT",
    "(↑ MOOD) = ↓1 MOOD",
    "(↑ LEX-ASTRUCT) = ↓1 LEX-ASTRUCT",
)


def _eqs(*extras: str) -> list[str]:
    """Build an equation list: verb percolation followed by extras."""
    return [*_VERB_PERCOLATION, *extras]


class Grammar:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules: list[Rule] = list(rules)

    @staticmethod
    def load_default() -> "Grammar":
        rules: list[Rule] = []

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
        _cardinal_case_marker = {
            "NOM": "DET[CASE=NOM]",
            "GEN": "ADP[CASE=GEN]",
            "DAT": "ADP[CASE=DAT]",
        }
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

        # --- Phase 4 §7.8: floated quantifier ---
        #
        # ``Kumain ang bata lahat`` ("all the children ate", with
        # ``lahat`` floated to clause-final). The quantifier rides
        # into the matrix's ADJ set as a sub-f-structure carrying
        # ``QUANT``; a binding equation links it to SUBJ. Pre-NP
        # partitive usage (``lahat ng bata``) is deferred — that
        # form needs a QP non-terminal.
        rules.append(Rule(
            "S",
            ["S", "Q"],
            ["(↑) = ↓1", "↓2 ∈ (↑ ADJ)", "(↓2 ANTECEDENT) = (↑ SUBJ)"],
        ))

        # --- Phase 4 §7.3: adverbial enclitics as clausal ADJ members ---
        #
        # The pre-parse clitic-placement pass moves adverbial enclitics
        # (``na``, ``pa``, ``ba``, ``daw``/``raw``, ``din``/``rin``,
        # ``lang``, ``nga``, ``pala``, ``kasi``, ...) to the end of the
        # sentence in priority order. This recursive rule absorbs each
        # one as a member of the matrix f-structure's ADJ set; the
        # particle's own f-structure (carrying ASPECT_PART, EVID, etc.)
        # rides into ADJ as a sub-structure.
        #
        # ``CLITIC_CLASS=2P`` distinguishes Wackernagel enclitics from
        # the other PART tokens (linkers, the ``hindi`` negation
        # particle).
        rules.append(Rule(
            "S",
            ["S", "PART[CLITIC_CLASS=2P]"],
            ["(↑) = ↓1", "↓2 ∈ (↑ ADJ)"],
        ))

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
        rules.append(Rule(
            "S",
            ["PART[POLARITY=NEG]", "S"],
            [
                "(↑) = ↓2",
                "(↑ POLARITY) = 'NEG'",
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
        # (with addressee + linker + verb) needs a different wrap
        # rule and is deferred — see "Out-of-scope" in the
        # ``docs/analysis-choices.md`` "Phase 5e Commit 25" entry.
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

        # --- Phase 4 §7.4 + §7.5: SUBJ-gapped clauses (S_GAP) ---
        #
        # ``S_GAP`` is the inner clause of an ay-inversion or a
        # relative clause: a V-initial S with the NOM-marked SUBJ
        # argument absent. The missing SUBJ is bound to ``REL-PRO``
        # via the equation ``(↑ SUBJ) = (↑ REL-PRO)``; an enclosing
        # wrap rule (ay-inversion or NP-relativization) sets REL-PRO
        # to the displaced phrase, which transitively fills SUBJ.
        #
        # These rules duplicate the regular S frames but omit the
        # NOM NP. ``S_GAP`` never appears at the top level (the start
        # symbol is ``S``, not ``S_GAP``); it is reachable only via
        # the wrap rules below.
        rules.append(Rule(
            "S_GAP",
            ["V[VOICE=AV]"],
            _eqs("(↑ SUBJ) = (↑ REL-PRO)"),
        ))
        # S_GAP transitive frames mirror the matrix transitive frames'
        # OBJ-θ-in-grammar split: AV binds the ng-NP to bare OBJ
        # (PATIENT/THEME), non-AV binds to typed OBJ-θ.
        gap_voice_specs = [
            ("AV", "OBJ", []),
            ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
            ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
            ("DV", "OBJ-AGENT", []),
            ("IV", "OBJ-AGENT", []),
        ]
        for voice, obj_target, extras in gap_voice_specs:
            feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
            v_cat = f"V[{', '.join(feat_strs)}]"
            rules.append(Rule(
                "S_GAP",
                [v_cat, "NP[CASE=GEN]"],
                _eqs(
                    f"(↑ {obj_target}) = ↓2",
                    "(↑ SUBJ) = (↑ REL-PRO)",
                ),
            ))
            rules.append(Rule(
                "S_GAP",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=DAT]"],
                _eqs(
                    f"(↑ {obj_target}) = ↓2",
                    "↓3 ∈ (↑ ADJUNCT)",
                    "(↑ SUBJ) = (↑ REL-PRO)",
                ),
            ))

        # Negation inside a SUBJ-gapped clause: ``hindi kumain``
        # under ay-inversion or relativization. The recursion mirrors
        # the regular ``S → PART[POLARITY=NEG] S`` rule so negation
        # composes the same way through gapped clauses.
        rules.append(Rule(
            "S_GAP",
            ["PART[POLARITY=NEG]", "S_GAP"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # --- Phase 5d Commit 5: non-pivot ay-fronting gap-categories ---
        #
        # Phase 4 §7.4 admitted only SUBJ-pivot ay-fronting via
        # ``S_GAP``. S&O §6 and Kroeger 1993 describe topicalization-
        # style ay-fronting of non-pivot phrases (OBJ-θ in any voice
        # plus DAT-marked obliques). Three new gap-category non-
        # terminals parallel ``S_GAP``, each with its own REL-PRO
        # binding to a different GF in the inner clause:
        #
        #   * ``S_GAP_OBJ``       — AV with bare OBJ extracted.
        #   * ``S_GAP_OBJ_AGENT`` — non-AV with typed OBJ-AGENT
        #     (the actor) extracted; the inner SUBJ pivot is overt.
        #   * ``S_GAP_OBL``       — any voice with a DAT-marked
        #     ADJUNCT member extracted.
        #
        # Like ``S_GAP``, none of these are top-level start symbols;
        # they are reachable only via the corresponding wrap rules
        # added below the existing ay-inversion rule, so an unbound
        # REL-PRO never escapes to the matrix.

        # === S_GAP_OBJ: AV with OBJ extracted ===
        # Inner SUBJ overt; OBJ is the gap. Two frames cover plain
        # AV-transitive and AV-transitive-with-DAT-adjunct shapes.
        rules.append(Rule(
            "S_GAP_OBJ",
            ["V[VOICE=AV]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBJ",
            ["V[VOICE=AV]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ OBJ) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBJ",
            ["PART[POLARITY=NEG]", "S_GAP_OBJ"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # === S_GAP_OBJ_AGENT: non-AV with OBJ-AGENT extracted ===
        # Inner NOM pivot overt; the GEN-marked actor is the gap,
        # bound to ``OBJ-AGENT`` (the typed slot under Phase 5b's
        # OBJ-θ-in-grammar alignment). The voice-specific extras
        # (CAUS=NONE on OV / DV) discriminate against pa-OV / pa-DV
        # (CAUS=DIRECT) where the typed slot would be ``OBJ-CAUSER``;
        # IV is admitted without an APPL constraint so any IV
        # applicative (-CONVEY / -INSTR / -REASON) can have its
        # actor fronted.
        nonav_obj_agent_specs = [
            ("OV", [("CAUS", "NONE")]),
            ("DV", [("CAUS", "NONE")]),
            ("IV", []),
        ]
        for voice, extras in nonav_obj_agent_specs:
            feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
            v_cat = f"V[{', '.join(feat_strs)}]"
            rules.append(Rule(
                "S_GAP_OBJ_AGENT",
                [v_cat, "NP[CASE=NOM]"],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    "(↑ OBJ-AGENT) = (↑ REL-PRO)",
                ),
            ))
            rules.append(Rule(
                "S_GAP_OBJ_AGENT",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=DAT]"],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    "↓3 ∈ (↑ ADJUNCT)",
                    "(↑ OBJ-AGENT) = (↑ REL-PRO)",
                ),
            ))
        rules.append(Rule(
            "S_GAP_OBJ_AGENT",
            ["PART[POLARITY=NEG]", "S_GAP_OBJ_AGENT"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # === S_GAP_OBL: any voice with DAT-marked OBL extracted ===
        # The fronted DAT-NP joins ``ADJUNCT`` via set membership
        # (``(↑ REL-PRO) ∈ (↑ ADJUNCT)``); remaining core arguments
        # stay overt. Both NP orders are admitted to mirror the
        # regular S frames' free post-V order.
        # AV intransitive (DAT was the only adjunct).
        rules.append(Rule(
            "S_GAP_OBL",
            ["V[VOICE=AV]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
            ),
        ))
        # AV transitive (OBJ retained; DAT extracted).
        rules.append(Rule(
            "S_GAP_OBL",
            ["V[VOICE=AV]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ) = ↓3",
                "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBL",
            ["V[VOICE=AV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓3",
                "(↑ OBJ) = ↓2",
                "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
            ),
        ))
        # Non-AV transitive (OBJ-AGENT retained; DAT extracted) per
        # voice spec, both NP orders.
        nonav_obl_specs = [
            ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
            ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
            ("IV", "OBJ-AGENT", []),
        ]
        for voice, obj_target, extras in nonav_obl_specs:
            feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
            v_cat = f"V[{', '.join(feat_strs)}]"
            rules.append(Rule(
                "S_GAP_OBL",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    f"(↑ {obj_target}) = ↓3",
                    "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
                ),
            ))
            rules.append(Rule(
                "S_GAP_OBL",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
                _eqs(
                    "(↑ SUBJ) = ↓3",
                    f"(↑ {obj_target}) = ↓2",
                    "(↑ REL-PRO) ∈ (↑ ADJUNCT)",
                ),
            ))
        rules.append(Rule(
            "S_GAP_OBL",
            ["PART[POLARITY=NEG]", "S_GAP_OBL"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # --- Phase 5e Commit 1: pa-OV / pa-DV (CAUS=DIRECT) actor-fronting ---
        #
        # Phase 5d Commit 5's ``S_GAP_OBJ_AGENT`` admits non-AV
        # actor-fronting only when the V carries ``CAUS=NONE`` — the
        # constraint deliberately excludes pa-OV / pa-DV (CAUS=DIRECT)
        # because in monoclausal direct causatives the actor's typed
        # GF is ``OBJ-CAUSER``, not ``OBJ-AGENT``. Phase 5e Commit 1
        # fills in the parallel ``OBJ-CAUSER`` extraction path:
        #
        #   ``Ng nanay ay pinakain ang bata.``
        #     "It was mother who fed the child."
        #   ``Ng nanay ay pinakain ang bata ng kanin.``
        #     "It was mother who fed the child rice." (3-arg pa-OV)
        #   ``Ng nanay ay pinakainan ang bata.``
        #     "It was mother who fed [the food to] the child." (pa-DV)
        #
        # The fronted GEN-NP is the CAUSER (demoted from actor under
        # pa-causation); the inner clause's NOM pivot is the CAUSEE
        # (pa-OV) or LOCATION/RECIPIENT (pa-DV) and stays overt.
        # Wrap-rule disambiguation works the same as the Commit 5
        # cases: the parser explores every ``NP[CASE=GEN] PART[LINK=AY]
        # S_GAP_*`` wrap rule, and only the one whose inner gap-
        # category matches the V's voice + CAUS features produces a
        # valid parse.

        # === S_GAP_OBJ_CAUSER: pa-OV / pa-DV (CAUS=DIRECT) with
        # OBJ-CAUSER extracted ===
        # 2-arg pa-OV (causee pivot + gap-causer); the patient is
        # absent on the surface (lex 2-arg PRED `<SUBJ, OBJ-CAUSER>`).
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            ["V[VOICE=OV, CAUS=DIRECT]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # 2-arg pa-OV with a DAT adjunct retained.
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            [
                "V[VOICE=OV, CAUS=DIRECT]",
                "NP[CASE=NOM]",
                "NP[CASE=DAT]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # 3-arg pa-OV (causee + patient retained, gap-causer); both
        # NP orders mirror the top-level multi-GEN-NP and the
        # Phase 5d Commit 8 S_XCOMP rules.
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            [
                "V[VOICE=OV, CAUS=DIRECT]",
                "NP[CASE=NOM]",
                "NP[CASE=GEN]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-PATIENT) = ↓3",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            [
                "V[VOICE=OV, CAUS=DIRECT]",
                "NP[CASE=GEN]",
                "NP[CASE=NOM]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓3",
                "(↑ OBJ-PATIENT) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # 2-arg pa-DV (location/recipient pivot + gap-causer); the
        # Phase 5d Commit 2 ``pa-...-an`` lex profile starts at
        # 2-arg. Phase 5e Commit 10 adds the 3-arg variants below.
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            ["V[VOICE=DV, CAUS=DIRECT]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            [
                "V[VOICE=DV, CAUS=DIRECT]",
                "NP[CASE=NOM]",
                "NP[CASE=DAT]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # Phase 5e Commit 10: 3-arg pa-DV ay-fronting (CAUSER
        # extracted, OBJ-PATIENT retained as overt GEN-NP). Both
        # NP orders, mirroring the 3-arg pa-OV variants above.
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            [
                "V[VOICE=DV, CAUS=DIRECT]",
                "NP[CASE=NOM]",
                "NP[CASE=GEN]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-PATIENT) = ↓3",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            [
                "V[VOICE=DV, CAUS=DIRECT]",
                "NP[CASE=GEN]",
                "NP[CASE=NOM]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓3",
                "(↑ OBJ-PATIENT) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # Negation recursion mirrors the other gap categories.
        rules.append(Rule(
            "S_GAP_OBJ_CAUSER",
            ["PART[POLARITY=NEG]", "S_GAP_OBJ_CAUSER"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # --- Phase 5e Commit 2: multi-GEN-NP ay-fronting ---
        #
        # Phase 5b multi-GEN-NP frames (IV-BEN / IV-INSTR / IV-REASON
        # 3-arg, pa-OV-direct 3-arg) bind two GEN-marked non-pivots
        # to typed ``OBJ-θ`` slots positionally:
        #
        #   * IV (any APPL): first GEN → OBJ-AGENT, second → OBJ-PATIENT.
        #   * pa-OV CAUS=DIRECT: first GEN → OBJ-CAUSER, second → OBJ-PATIENT.
        #
        # Fronting one of the two GEN-NPs leaves the inner clause
        # with one NOM (pivot) plus one retained GEN-NP. The remaining
        # GEN-NP's binding can no longer be purely positional — it
        # depends on which role was extracted.
        #
        # Phase 5d Commit 5 handled the 2-arg cases (no second GEN
        # in the inner clause) only. Phase 5e Commit 1 added the 3-arg
        # pa-OV ``S_GAP_OBJ_CAUSER`` with OBJ-PATIENT retained
        # (CAUSER fronted). Phase 5e Commit 2 fills in the remaining
        # 3-arg multi-GEN extractions:
        #
        #   * 3-arg IV with OBJ-AGENT extracted (OBJ-PATIENT retained).
        #     New ``S_GAP_OBJ_AGENT`` IV-3arg variants.
        #   * 3-arg multi-GEN with OBJ-PATIENT extracted, in either
        #     IV (OBJ-AGENT retained) or pa-OV-direct (OBJ-CAUSER
        #     retained). New ``S_GAP_OBJ_PATIENT`` non-terminal.
        #
        # When two readings exist for the same surface (e.g.,
        # ``Ng nanay ay ipinaggawa ang kapatid ng silya`` could be
        # AGENT-front + PATIENT-retained OR PATIENT-front +
        # AGENT-retained), both parses surface and the existing
        # ranker plus animacy/lexical semantics resolves; tests
        # accept the natural reading among the n-best.

        # === S_GAP_OBJ_AGENT IV 3-arg variants ===
        # The 2-arg IV S_GAP_OBJ_AGENT rule from Phase 5d Commit 5
        # only matches V[VOICE=IV] NP[NOM] (no second GEN). The
        # 3-arg variant adds a retained OBJ-PATIENT GEN-NP in either
        # post-V order; the gap remains OBJ-AGENT.
        rules.append(Rule(
            "S_GAP_OBJ_AGENT",
            ["V[VOICE=IV]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-PATIENT) = ↓3",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_GAP_OBJ_AGENT",
            ["V[VOICE=IV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓3",
                "(↑ OBJ-PATIENT) = ↓2",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))

        # === S_GAP_OBJ_PATIENT: any 3-arg multi-GEN frame with
        # OBJ-PATIENT extracted ===
        # Two voice/feature combinations are admitted, mirroring the
        # top-level multi-GEN-NP rules:
        #
        #   * V[VOICE=IV] (any APPL): retained GEN-NP is OBJ-AGENT.
        #   * V[VOICE=OV, CAUS=DIRECT]: retained GEN-NP is OBJ-CAUSER.
        #
        # Both NP orders are admitted per voice; PART[POLARITY=NEG]
        # recursion at the bottom handles inner negation.
        # Phase 5e Commit 10 adds pa-DV (CAUS=DIRECT) once the
        # 3-arg pa-DV lex profile lands, so DV mirrors OV here.
        patient_gap_specs = [
            # (voice features, retained-GEN-NP target GF)
            ("V[VOICE=IV]", "OBJ-AGENT"),
            ("V[VOICE=OV, CAUS=DIRECT]", "OBJ-CAUSER"),
            ("V[VOICE=DV, CAUS=DIRECT]", "OBJ-CAUSER"),
        ]
        for v_cat, retained_gf in patient_gap_specs:
            # NOM-GEN order: retained GEN follows pivot.
            rules.append(Rule(
                "S_GAP_OBJ_PATIENT",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    f"(↑ {retained_gf}) = ↓3",
                    "(↑ OBJ-PATIENT) = (↑ REL-PRO)",
                ),
            ))
            # GEN-NOM order: retained GEN before pivot.
            rules.append(Rule(
                "S_GAP_OBJ_PATIENT",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
                _eqs(
                    "(↑ SUBJ) = ↓3",
                    f"(↑ {retained_gf}) = ↓2",
                    "(↑ OBJ-PATIENT) = (↑ REL-PRO)",
                ),
            ))
        # Negation recursion.
        rules.append(Rule(
            "S_GAP_OBJ_PATIENT",
            ["PART[POLARITY=NEG]", "S_GAP_OBJ_PATIENT"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # --- Phase 5d Commit 6: possessive-linker RC gap-category ---
        #
        # Construction: ``aklat kong binasa`` ("the book that I read").
        # The pronominal actor of the RC's non-AV verb is hoisted out
        # of the RC and surfaces as a possessor of the head NP, joined
        # by the bound linker ``-ng``. Distinct from standard
        # relativization (``aklat na binasa ko``) where the actor
        # stays inside the RC as a GEN-NP.
        #
        # ``S_GAP_NA`` (no-overt-actor) is a SUBJ-gapped non-AV V
        # frame that takes no GEN-NP. The actor (``OBJ-AGENT`` under
        # Phase 5b OBJ-θ-in-grammar) is supplied externally by the
        # wrap rule via ``(↓N OBJ-AGENT) = pronoun``. Voice / feature
        # constraints follow the existing S_GAP pattern: OV / DV
        # require ``CAUS=NONE`` to keep pa-OV / pa-DV out of the
        # actor-extraction path; IV is admitted without an APPL
        # constraint so any applicative variant can host the
        # construction.
        nonav_na_specs = [
            ("OV", [("CAUS", "NONE")]),
            ("DV", [("CAUS", "NONE")]),
            ("IV", []),
        ]
        for voice, extras in nonav_na_specs:
            feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
            v_cat = f"V[{', '.join(feat_strs)}]"
            rules.append(Rule(
                "S_GAP_NA",
                [v_cat],
                _eqs("(↑ SUBJ) = (↑ REL-PRO)"),
            ))
            rules.append(Rule(
                "S_GAP_NA",
                [v_cat, "NP[CASE=DAT]"],
                _eqs(
                    "(↑ SUBJ) = (↑ REL-PRO)",
                    "↓2 ∈ (↑ ADJUNCT)",
                ),
            ))
        rules.append(Rule(
            "S_GAP_NA",
            ["PART[POLARITY=NEG]", "S_GAP_NA"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # --- Phase 4 §7.6: control complement (S_XCOMP) ---
        #
        # ``S_XCOMP`` is the SUBJ-gapped clause that serves as the
        # XCOMP of a control verb. The original Phase 4 frames are
        # AV-only: the controllee is the actor, which is SUBJ in AV.
        # Phase 5c §7.6 follow-on adds non-AV variants where the
        # controllee is the actor's *typed* GF — ``OBJ-AGENT`` under
        # the Phase 5b OBJ-θ-in-grammar alignment. The matrix wrap
        # rule's ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` is unchanged; only
        # the embedded clause's REL-PRO routing differs per voice.
        #
        # AV frames: REL-PRO routes to SUBJ.
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=AV]"],
            _eqs("(↑ SUBJ) = (↑ REL-PRO)"),
        ))
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=AV]", "NP[CASE=GEN]"],
            _eqs("(↑ OBJ) = ↓2", "(↑ SUBJ) = (↑ REL-PRO)"),
        ))
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=AV]", "NP[CASE=GEN]", "NP[CASE=DAT]"],
            _eqs(
                "(↑ OBJ) = ↓2",
                "↓3 ∈ (↑ ADJUNCT)",
                "(↑ SUBJ) = (↑ REL-PRO)",
            ),
        ))
        # Phase 5c §7.6 follow-on: non-AV embedded clauses, where
        # REL-PRO routes to ``OBJ-AGENT`` (the actor's typed GF in
        # OV / DV / IV). The patient / recipient / theme NOM-pivot
        # is overt; the actor is the gap. CAUS=NONE on OV
        # discriminates against pa-OV (CAUS=DIRECT) where the typed
        # slot would be ``OBJ-CAUSER``. IV is admitted without an
        # APPL constraint (Phase 5d Commit 9) so any applicative —
        # CONVEY (bare i-) / BEN (ipag-) / INSTR (ipang-) /
        # REASON (ika-) — fires; the actor is OBJ-AGENT in all
        # variants.
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=OV, CAUS=NONE]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=DV]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=IV]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
        # Phase 5d Commit 9: IV multi-GEN (3-arg) under control.
        # Phase 5b admitted top-level multi-GEN-NP IV-BEN frames
        # (``Ipinaggawa ng nanay ng silya ang kapatid``) with three
        # NPs: pivot (BENEFICIARY) + AGENT + PATIENT. Under control,
        # the actor (OBJ-AGENT, the agent slot) is the gap; the
        # surface form has SUBJ pivot + GEN-PATIENT and the
        # GEN-AGENT is suppressed. Both NP orders admitted.
        # Generalises across IV-BEN / IV-INSTR / IV-REASON because
        # the existing top-level multi-GEN rules at
        # ``v_iv = "V[VOICE=IV]"`` (no APPL filter) already do.
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=IV]", "NP[CASE=NOM]", "NP[CASE=GEN]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-PATIENT) = ↓3",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=IV]", "NP[CASE=GEN]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓3",
                "(↑ OBJ-PATIENT) = ↓2",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
            ),
        ))
        # Phase 5d Commit 8: pa-OV / pa-DV (CAUS=DIRECT) embedded
        # under control. In monoclausal direct causatives the actor
        # is the typed ``OBJ-CAUSER`` slot (not ``OBJ-AGENT``), so
        # under control the controllee is OBJ-CAUSER. The Phase 5c
        # non-AV S_XCOMP rules above explicitly require ``CAUS=NONE``
        # to keep them out of the actor-extraction path; this block
        # adds the parallel ``CAUS=DIRECT`` variants that route
        # REL-PRO to OBJ-CAUSER.
        #
        # Two-argument pa-OV (causee + gap-causer) — the patient is
        # absent on the surface (lex entry's a-structure permits
        # this).
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=OV, CAUS=DIRECT]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # Three-argument pa-OV (causee + patient + gap-causer);
        # NP-order is free post-V so both orders.
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[VOICE=OV, CAUS=DIRECT]",
                "NP[CASE=NOM]",
                "NP[CASE=GEN]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-PATIENT) = ↓3",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[VOICE=OV, CAUS=DIRECT]",
                "NP[CASE=GEN]",
                "NP[CASE=NOM]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓3",
                "(↑ OBJ-PATIENT) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # Two-argument pa-DV (location/recipient pivot + gap-causer)
        # — Phase 5d Commit 2's pa-...-an cells. Pivot is the
        # location (ang nanay = "to mom"), causer is gap. The
        # patient is absent from the embedded clause's surface.
        rules.append(Rule(
            "S_XCOMP",
            ["V[VOICE=DV, CAUS=DIRECT]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # Phase 5e Commit 10: three-argument pa-DV under control.
        # Mirrors the three-argument pa-OV S_XCOMP rules above, but
        # with the pa-DV pivot (LOCATION) at NOM and an overt
        # OBJ-PATIENT GEN-NP retained. Both NP orders.
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[VOICE=DV, CAUS=DIRECT]",
                "NP[CASE=NOM]",
                "NP[CASE=GEN]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-PATIENT) = ↓3",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        rules.append(Rule(
            "S_XCOMP",
            [
                "V[VOICE=DV, CAUS=DIRECT]",
                "NP[CASE=GEN]",
                "NP[CASE=NOM]",
            ],
            _eqs(
                "(↑ SUBJ) = ↓3",
                "(↑ OBJ-PATIENT) = ↓2",
                "(↑ OBJ-CAUSER) = (↑ REL-PRO)",
            ),
        ))
        # Phase 5c §7.6 follow-on (Commit 3): nested control
        # complements (long-distance control). When a control verb
        # is itself embedded inside another control verb's XCOMP,
        # its SUBJ is the gap (= the outer controller), so the
        # NOM- or GEN-marked SUBJ NP that the matrix wrap rule
        # would supply is absent. The OBJ-AGENT in TRANS remains
        # overt — it's the controller (forcer/orderer), not the
        # controllee. Each nested S_XCOMP rule:
        #   - binds its own SUBJ to its own REL-PRO (it is the gap);
        #   - chains its XCOMP slot to the inner S_XCOMP;
        #   - propagates the controller from its SUBJ to the inner
        #     XCOMP's REL-PRO.
        # Composing these equations across depth-N gives a single
        # f-node shared across SUBJ slots at every level — finite-
        # depth control without functional uncertainty.
        for link in ("NA", "NG"):
            # PSYCH nested: V[CTRL_CLASS=PSYCH] PART S_XCOMP
            rules.append(Rule(
                "S_XCOMP",
                [
                    "V[CTRL_CLASS=PSYCH]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ SUBJ) = (↑ REL-PRO)",
                    "(↑ XCOMP) = ↓3",
                    "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                ),
            ))
            # INTRANS nested: V[CTRL_CLASS=INTRANS] PART S_XCOMP
            rules.append(Rule(
                "S_XCOMP",
                [
                    "V[CTRL_CLASS=INTRANS]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ SUBJ) = (↑ REL-PRO)",
                    "(↑ XCOMP) = ↓3",
                    "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                ),
            ))
            # TRANS nested: V[CTRL_CLASS=TRANS] NP[CASE=GEN] PART
            # S_XCOMP. The GEN-NP is the forcer / orderer, mapped
            # to OBJ-AGENT (the typed slot since Phase 5b
            # OBJ-θ-in-grammar). The NOM-marked forcee that the
            # matrix wrap rule would supply is the gap.
            rules.append(Rule(
                "S_XCOMP",
                [
                    "V[CTRL_CLASS=TRANS]",
                    "NP[CASE=GEN]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ OBJ-AGENT) = ↓2",
                    "(↑ SUBJ) = (↑ REL-PRO)",
                    "(↑ XCOMP) = ↓4",
                    "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                ),
            ))
        # Inner negation under control: ``Gusto kong hindi kumain``
        # — the embedded clause is negated. Mirrors the S / S_GAP
        # negation rule shape.
        rules.append(Rule(
            "S_XCOMP",
            ["PART[POLARITY=NEG]", "S_XCOMP"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
        ))

        # --- Phase 5d Commit 7: raising inside a control complement ---
        #
        # ``Gusto kong mukhang kumakain`` ("I want to seem to be
        # eating"): a control verb's XCOMP is itself a raising
        # structure. The Phase 5c §7.6 follow-on (Commit 5) raising
        # rules sit at the ``S`` level; control complements are at
        # the ``S_XCOMP`` level (SUBJ-gapped). This block adds the
        # ``S_XCOMP``-level raising variants so the matrix control
        # wrap rule's ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` propagates the
        # controller through the raising chain into the embedded
        # action's SUBJ.
        #
        # Equations compose three identifications at this S_XCOMP
        # level:
        #
        #   * ``(↑ XCOMP) = ↓N`` — the inner clause is the raising
        #     verb's XCOMP.
        #   * ``(↑ SUBJ) = (↑ XCOMP SUBJ)`` — raising structure-share.
        #   * ``(↑ SUBJ) = (↑ REL-PRO)`` — S_XCOMP convention so the
        #     matrix control rule's REL-PRO routing fires.
        #
        # Together: outer.SUBJ = THIS.REL-PRO = THIS.SUBJ
        # = THIS.XCOMP.SUBJ = innermost-action.SUBJ. Recursing
        # through ``S_XCOMP`` lets raising chains compose under
        # control (``Gusto kong mukhang bakang kumakain``).
        for link in ("NA", "NG"):
            rules.append(Rule(
                "S_XCOMP",
                [
                    "V[CTRL_CLASS=RAISING]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ XCOMP) = ↓3",
                    "(↑ SUBJ) = (↑ XCOMP SUBJ)",
                    "(↑ SUBJ) = (↑ REL-PRO)",
                ),
            ))
        rules.append(Rule(
            "S_XCOMP",
            ["V[CTRL_CLASS=RAISING_BARE]", "S_XCOMP"],
            _eqs(
                "(↑ XCOMP) = ↓2",
                "(↑ SUBJ) = (↑ XCOMP SUBJ)",
                "(↑ SUBJ) = (↑ REL-PRO)",
            ),
        ))

        # --- Phase 4 §7.4: ay-inversion ---
        #
        # ``Si Maria ay kumain ng isda``: the topic phrase moves to
        # clause-initial position, separated from the inner clause by
        # the linker particle ``ay``. The fronted phrase is the SUBJ
        # of the inner clause; per Phase 4 §7.4 scope, only pivot
        # (SUBJ) fronting is admitted. Non-pivot ay-fronting is
        # deferred to §7.8 (``docs/analysis-choices.md`` "Phase 4
        # §7.4: ay-inversion").
        #
        # The wrap rule:
        #   - sets ``TOPIC`` on the matrix f-structure to the fronted
        #     NP;
        #   - sets the inner clause's ``REL-PRO`` to the same NP, so
        #     that S_GAP's ``(↑ SUBJ) = (↑ REL-PRO)`` fills SUBJ;
        #   - constrains REL-PRO to equal SUBJ (vacuous now; pins
        #     SUBJ-only fronting structurally).
        rules.append(Rule(
            "S",
            ["NP[CASE=NOM]", "PART[LINK=AY]", "S_GAP"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "(↓3 REL-PRO) = ↓1",
                "(↓3 REL-PRO) =c (↓3 SUBJ)",
            ],
        ))

        # --- Phase 5d Commit 5: non-pivot ay-fronting wrap rules ---
        #
        # The fronted NP's case marker disambiguates which gap-
        # category the inner clause uses; the V's voice + features
        # then select the right S_GAP_X frame. The wrap-rule pattern
        # mirrors the SUBJ-fronting rule above: matrix and inner
        # clause share an f-structure, the fronted NP becomes
        # ``TOPIC`` and ``REL-PRO``, and a constraining equation
        # pins the fronted GF in the inner clause (vacuous given
        # each S_GAP_X's binding equation, but kept for symmetry
        # and structural documentation).

        # Non-pivot OBJ-fronting (AV, GEN-marked topic):
        # ``Ng isda ay kumain si Maria.``
        rules.append(Rule(
            "S",
            ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "(↓3 REL-PRO) = ↓1",
                "(↓3 REL-PRO) =c (↓3 OBJ)",
            ],
        ))

        # Non-pivot OBJ-AGENT-fronting (non-AV, GEN-marked topic):
        # ``Ni Maria ay kinain ang isda.``
        rules.append(Rule(
            "S",
            ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ_AGENT"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "(↓3 REL-PRO) = ↓1",
                "(↓3 REL-PRO) =c (↓3 OBJ-AGENT)",
            ],
        ))

        # Non-pivot OBL-fronting (any voice, DAT-marked topic):
        # ``Sa bahay ay kumain si Maria.`` The fronted phrase joins
        # ADJUNCT via S_GAP_OBL's set-membership equation; no scalar
        # constraining equation since ADJUNCT is a set, not a GF.
        rules.append(Rule(
            "S",
            ["NP[CASE=DAT]", "PART[LINK=AY]", "S_GAP_OBL"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "(↓3 REL-PRO) = ↓1",
            ],
        ))

        # Phase 5e Commit 1: pa-OV / pa-DV (CAUS=DIRECT) actor-fronting.
        # The fronted GEN-NP is the CAUSER (demoted from actor under
        # pa-causation); the inner clause is a pa-causative S_GAP_OBJ_CAUSER
        # which routes REL-PRO to the typed ``OBJ-CAUSER`` slot.
        # Disambiguation against S_GAP_OBJ_AGENT happens via the inner
        # V's CAUS feature (DIRECT vs NONE), so both wrap rules can
        # coexist without cross-firing.
        rules.append(Rule(
            "S",
            ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ_CAUSER"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "(↓3 REL-PRO) = ↓1",
                "(↓3 REL-PRO) =c (↓3 OBJ-CAUSER)",
            ],
        ))

        # Phase 5e Commit 2: multi-GEN-NP ay-fronting — OBJ-PATIENT-
        # extracted variant. The fronted GEN-NP is the PATIENT;
        # the inner clause is a 3-arg multi-GEN frame
        # (S_GAP_OBJ_PATIENT) where the retained GEN-NP binds to
        # OBJ-AGENT (under IV) or OBJ-CAUSER (under pa-OV-direct).
        # Coexists with the OBJ_AGENT and OBJ_CAUSER wrap rules:
        # for a 3-arg multi-GEN inner clause, multiple gap-categories
        # match (e.g., AGENT-front + PATIENT-retained, OR PATIENT-
        # front + AGENT-retained); the resulting parses surface in
        # n-best and the ranker plus lexical semantics picks. The
        # constraining equation pins which fronted GF this wrap rule
        # represents.
        rules.append(Rule(
            "S",
            ["NP[CASE=GEN]", "PART[LINK=AY]", "S_GAP_OBJ_PATIENT"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "(↓3 REL-PRO) = ↓1",
                "(↓3 REL-PRO) =c (↓3 OBJ-PATIENT)",
            ],
        ))

        # --- Phase 5e Commit 3: AdvP / PP categorial inventory + fronting ---
        #
        # Phase 4 §7.4's ``Out-of-scope`` list flagged AdvP / PP
        # ay-fronting as "deferred until the categorial inventory
        # expands". This commit lifts the deferral with the smallest
        # categorial expansion that unblocks the construction:
        #
        #   * Two new POS values (``ADV``, ``PREP``) seeded in
        #     ``data/tgl/particles.yaml`` for a handful of temporal
        #     adverbs (``kahapon`` / ``ngayon`` / ``bukas`` /
        #     ``mamaya``) and compound prepositions (``para`` /
        #     ``tungkol`` / ``mula`` / ``dahil``).
        #   * Two new non-terminals: ``AdvP`` (single-word) and
        #     ``PP`` (PREP + sa-NP).
        #   * Two new ay-fronting wrap rules.
        #
        # The non-fronted placement of AdvP / PP (clause-final or as
        # an unmarked sentential adjunct) is **not** added in this
        # commit — the scoped goal is ay-fronting only. Adding bare
        # placement would interact with the Phase 4 §7.3 Wackernagel
        # cluster and the Phase 4 §7.8 quantifier-float rule and is
        # deferred to a separate commit.

        # AdvP: a single ADV word lifts to AdvP. ADV is a closed-
        # class POS so a flat single-child rule is sufficient; the
        # AdvP's f-structure inherits the ADV's atomic features
        # (LEMMA, ADV_TYPE, DEIXIS_TIME, ...).
        rules.append(Rule(
            "AdvP",
            ["ADV"],
            _eqs("(↑) = ↓1"),
        ))

        # PP: PREP + NP[CASE=DAT]. The compound prepositions in
        # particles.yaml all subcategorise for a sa-NP complement
        # (``para sa bata``, ``tungkol sa nanay``, ``mula sa
        # Maynila``, ``dahil sa gutom``). The PP's f-structure
        # inherits PREP_TYPE from the head and exposes the
        # complement NP as ``OBJ`` for downstream consumers
        # (analogous to how a clause's V exposes its NP arguments).
        rules.append(Rule(
            "PP",
            ["PREP", "NP[CASE=DAT]"],
            _eqs(
                "(↑) = ↓1",
                "(↑ OBJ) = ↓2",
            ),
        ))

        # ay-fronting an AdvP. The fronted phrase is BOTH the matrix
        # TOPIC and a member of the matrix's ADJ set (sentential
        # adjunct semantics). The inner clause is a complete S
        # (no gap) — AdvP isn't an argument of any voice/aspect
        # frame, so there's nothing to extract from the inner
        # clause's GF inventory.
        rules.append(Rule(
            "S",
            ["AdvP", "PART[LINK=AY]", "S"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "↓1 ∈ (↑ ADJ)",
            ],
        ))

        # ay-fronting a PP. Same shape as AdvP fronting: matrix
        # TOPIC + ADJ membership. The PP's internal structure (PREP
        # head + sa-NP complement) is independent of the
        # ay-construction.
        rules.append(Rule(
            "S",
            ["PP", "PART[LINK=AY]", "S"],
            [
                "(↑) = ↓3",
                "(↑ TOPIC) = ↓1",
                "↓1 ∈ (↑ ADJ)",
            ],
        ))

        # --- Phase 5e Commit 5: headless / free relatives ---
        #
        # ``ang kumain`` "the one who ate"; ``ang kumain ng isda``
        # "the one who ate fish"; ``ang kinain ng aso`` "the one
        # eaten by the dog". A relative clause used directly as an
        # NP, with no overt head noun. The "head" is a phonologically
        # null PRO interpreted as the gap-filler (REL-PRO).
        #
        # Structure: ``DET[CASE=X, DEM=NO] S_GAP``. The bare case
        # marker (``ang`` / ``ng`` / ``sa`` / ``si`` / ``ni`` /
        # ``kay``) plus a SUBJ-gapped inner clause forms the headless
        # NP. The DEM=NO constraint prevents the rule from firing on
        # demonstratives (``ito`` / ``iyan`` / ``iyon`` etc., which
        # carry DEM=YES); demonstrative NPs use the standalone-
        # demonstrative rule above, not headless RCs.
        #
        # Equations parallel the standalone-demonstrative rule
        # (PRED='PRO' for the implicit head) and the head-initial
        # relativization rule (S_GAP attaches as ADJ; REL-PRO PRED
        # and CASE are anaphorically shared from the head).
        for case in ("NOM", "GEN", "DAT"):
            # NOM uses DET (ang / si); GEN / DAT use ADP
            # (ng / sa / ni / kay).
            head_cat = (
                f"DET[CASE={case}, DEM=NO]"
                if case == "NOM"
                else f"ADP[CASE={case}, DEM=NO]"
            )
            rules.append(Rule(
                f"NP[CASE={case}]",
                [head_cat, "S_GAP"],
                [
                    "(↑ PRED) = 'PRO'",
                    f"(↑ CASE) = '{case}'",
                    "(↑ MARKER) = ↓1 MARKER",
                    "↓2 ∈ (↑ ADJ)",
                    "(↓2 REL-PRO PRED) = 'PRO'",
                    f"(↓2 REL-PRO CASE) = '{case}'",
                    "(↓2 REL-PRO) =c (↓2 SUBJ)",
                ],
            ))

        # --- Phase 4 §7.5: relativization ---
        #
        # ``ang batang kumain ng isda`` ("the child that ate fish"):
        # head-initial NP relativization. The head NP is followed by
        # the linker (``na`` after consonant-final hosts, the bound
        # ``-ng`` after vowel-final hosts) and a SUBJ-gapped inner
        # clause. SUBJ-only relativization is the well-known Tagalog
        # restriction (Kroeger 1993): only the ang-NP can be
        # relativized.
        #
        # **Anaphoric REL-PRO** (not structure-sharing). The canonical
        # LFG analysis equates the head NP with the RC's REL-PRO
        # via full identity ``(↓3 REL-PRO) = ↓1``. That creates a
        # cyclic f-structure (head NP ⊇ ADJ ⊇ RC ⊇ REL-PRO = head NP)
        # which our unifier's occurs-check rejects. We instead share
        # the head NP's salient features (``PRED``, ``CASE``) with
        # REL-PRO via individual atomic-path equations, and bind the
        # RC's SUBJ to REL-PRO inside S_GAP. The constraining
        # equation ``(↓3 REL-PRO) =c (↓3 SUBJ)`` still pins the
        # SUBJ-only restriction (vacuous today, non-vacuous under
        # §7.6 non-SUBJ S_GAP frames). Documented in
        # ``docs/analysis-choices.md`` "Phase 4 §7.5".
        #
        # Six wrap rules (3 head cases × 2 linker variants) — the
        # head NP's case percolates to the matrix; both linkers (NA
        # standalone, NG bound enclitic) carry the same f-equations.
        for case in ("NOM", "GEN", "DAT"):
            np_cat = f"NP[CASE={case}]"
            for link in ("NA", "NG"):
                rules.append(Rule(
                    np_cat,
                    [np_cat, f"PART[LINK={link}]", "S_GAP"],
                    [
                        "(↑) = ↓1",
                        "↓3 ∈ (↑ ADJ)",
                        "(↓3 REL-PRO PRED) = (↓1 PRED)",
                        "(↓3 REL-PRO CASE) = (↓1 CASE)",
                        "(↓3 REL-PRO) =c (↓3 SUBJ)",
                    ],
                ))

        # --- Phase 5d Commit 6 + Phase 5e Commits 18 & 19:
        # possessive-linker RC wrap rule ---
        #
        # ``aklat kong binasa`` ("the book that I read"): a
        # construction parallel to relativization where the
        # actor of the RC's non-AV verb surfaces as a possessor
        # of the head NP, joined by a linker.
        #
        # **Three lifts of the same construction shape:**
        #
        # * **Phase 5d Commit 6** — vowel-final PRON + bound
        #   ``-ng`` linker (``aklat kong binasa``, fused ``Vng``
        #   form split by ``split_linker_ng``).
        # * **Phase 5e Commit 18** — consonant-final PRON +
        #   standalone ``na`` linker (``aklat namin na binasa``);
        #   plus the LINK=NA variant for vowel-final PRON
        #   (``aklat ko na binasa``).
        # * **Phase 5e Commit 19** — non-pronominal (NOUN /
        #   proper-noun) possessor (``aklat ng batang binasa``,
        #   ``aklat ni Juan na binasa``). Unified with the PRON
        #   case by widening the second daughter from
        #   ``PRON[CASE=GEN]`` to ``NP[CASE=GEN]`` — the
        #   ``NP[CASE=GEN] → PRON[CASE=GEN]`` rule already in the
        #   grammar makes this a strict generalization that
        #   subsumes the PRON case.
        #
        # **Wackernagel placement** — already in place from prior
        # commits and reused unchanged:
        #
        # * Vowel-final PRON + ``-ng``: PRON kept adjacent to its
        #   split-out bound linker by ``_is_pre_linker_pron``
        #   (Phase 5d Commit 6).
        # * Consonant-final PRON + ``na``: PRON kept in place by
        #   the older ``_is_post_noun_pron`` exception (Phase 5c
        #   §7.8 lift).
        # * NOUN possessor: NOUNs aren't clitic-pass-eligible, so
        #   they sit in surface order without help.
        #
        # **``na`` linker disambiguation** — the post-PRON ``na``
        # is preserved as the linker (rather than hoisted as the
        # 2P aspectual ``ALREADY``) by the third left-context
        # exception in ``disambiguate_homophone_clitics`` (Phase
        # 5e Commit 6). Doesn't apply to the NOUN case because
        # the NOUN-then-``na`` sequence is already preserved by
        # the first branch (``na`` after NOUN → linker reading).
        #
        # The possessor plays a dual role: it is the head NP's
        # ``POSS`` AND the RC's ``OBJ-AGENT``. The wrap rule binds
        # both via ``(↑ POSS) = ↓2`` and ``(↓4 OBJ-AGENT) = ↓2``.
        # REL-PRO sharing follows the standard relativization
        # pattern — anaphoric (PRED + CASE atomic-path copies, not
        # full identity) so the unifier's occurs-check stays happy.
        #
        # Six wrap rules: 3 head cases × 2 linker variants.
        #
        # **Constraints**:
        #
        # * ``(↑ LEMMA)`` (existential) requires the head NP to be
        #   NOUN-headed (NOUNs / proper nouns carry LEMMA in their
        #   f-structure; PRONs and headless-RC NPs do not). Without
        #   this guard, the widened ``NP[CASE=GEN]`` second-daughter
        #   slot (Phase 5e Commit 19) would let the rule fire on
        #   surfaces like ``Kumain ako ng batang kinain niya``,
        #   wrongly treating ``ako`` (PRON-NOM) as the possessable
        #   head NP and ``ng bata`` as its dual-bound possessor.
        #   The construction ``possessor + linker + RC`` only makes
        #   sense with a NOUN head; pronouns aren't possessable in
        #   this shape.
        # * The output NP is marked ``POSS-EXTRACTED=YES`` so the
        #   standard NP-poss rule cannot fire on it again — without
        #   this guard, a trailing GEN-NP (e.g., ``ng aso`` in ``bata
        #   ko na kinain ng aso``) would unify with the already-bound
        #   POSS, producing a spurious hybrid POSS=OBJ-AGENT. See
        #   the §7.8 NP-poss rule above for the full comment on the
        #   guard.
        for case in ("NOM", "GEN", "DAT"):
            np_cat = f"NP[CASE={case}]"
            for link in ("NA", "NG"):
                rules.append(Rule(
                    np_cat,
                    [np_cat, "NP[CASE=GEN]", f"PART[LINK={link}]", "S_GAP_NA"],
                    [
                        "(↑) = ↓1",
                        "(↑ POSS) = ↓2",
                        "(↑ POSS-EXTRACTED) = 'YES'",
                        "(↓1 LEMMA)",
                        "↓4 ∈ (↑ ADJ)",
                        "(↓4 OBJ-AGENT) = ↓2",
                        "(↓4 REL-PRO PRED) = (↓1 PRED)",
                        "(↓4 REL-PRO CASE) = (↓1 CASE)",
                        "(↓4 REL-PRO) =c (↓4 SUBJ)",
                    ],
                ))

        # --- Phase 4 §7.6: control wrap rules ---
        #
        # Three control patterns, all using SUBJ-control: the matrix
        # SUBJ binds the embedded SUBJ via the wrap rule's
        # ``(↑ SUBJ) = (↑ XCOMP REL-PRO)`` equation. Inside S_XCOMP,
        # the gap is bound by ``(↑ SUBJ) = (↑ REL-PRO)``, so the
        # composition makes matrix.SUBJ = matrix.XCOMP.SUBJ. No
        # cycle — matrix and XCOMP are sibling f-nodes; the shared
        # SUBJ is referenced from both but doesn't contain either.
        #
        # The control verb's class is selected by ``CTRL_CLASS`` on
        # the V token (set by the morph analyzer from the root's
        # per-root feats / from the particles.yaml entry).
        #
        # **Psych predicates** (gusto, ayaw, kaya): GEN-marked
        # experiencer is matrix SUBJ. PRED ``WANT <SUBJ, XCOMP>``.
        # The deviation from the otherwise-uniform NOM→SUBJ mapping
        # is documented in docs/analysis-choices.md "Phase 4 §7.6".
        for link in ("NA", "NG"):
            rules.append(Rule(
                "S",
                [
                    "V[CTRL_CLASS=PSYCH]",
                    "NP[CASE=GEN]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    "(↑ XCOMP) = ↓4",
                    "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                ),
            ))

        # **Intransitive control** (payag): NOM-marked agent is
        # matrix SUBJ; AV verb. PRED ``AGREE <SUBJ, XCOMP>``.
        for link in ("NA", "NG"):
            rules.append(Rule(
                "S",
                [
                    "V[CTRL_CLASS=INTRANS]",
                    "NP[CASE=NOM]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    "(↑ XCOMP) = ↓4",
                    "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                ),
            ))

        # **Transitive control** (pilit OV, utos DV): NOM-marked
        # pivot is matrix SUBJ (forcee / orderee); GEN-marked agent
        # is matrix OBJ-AGENT (typed under the Phase 5b
        # OBJ-θ-in-grammar alignment). The pivot controls XCOMP.
        # PRED ``FORCE <SUBJ, OBJ-AGENT, XCOMP>``. Both NOM-GEN and
        # GEN-NOM orderings are admitted, mirroring the regular
        # transitive frames' freedom.
        for link in ("NA", "NG"):
            # GEN-NOM order
            rules.append(Rule(
                "S",
                [
                    "V[CTRL_CLASS=TRANS]",
                    "NP[CASE=GEN]",
                    "NP[CASE=NOM]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ OBJ-AGENT) = ↓2",
                    "(↑ SUBJ) = ↓3",
                    "(↑ XCOMP) = ↓5",
                    "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                ),
            ))
            # NOM-GEN order
            rules.append(Rule(
                "S",
                [
                    "V[CTRL_CLASS=TRANS]",
                    "NP[CASE=NOM]",
                    "NP[CASE=GEN]",
                    f"PART[LINK={link}]",
                    "S_XCOMP",
                ],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    "(↑ OBJ-AGENT) = ↓3",
                    "(↑ XCOMP) = ↓5",
                    "(↑ SUBJ) = (↑ XCOMP REL-PRO)",
                ),
            ))

        # Phase 5c §7.6 follow-on (Commit 5): raising verbs.
        # ``Mukhang kumakain ang bata`` "the child seems to be
        # eating". The matrix has no thematic SUBJ; its SUBJ is
        # structure-shared with the embedded clause's SUBJ. Surface
        # shape: V[CTRL_CLASS=RAISING] + linker + full embedded S
        # (the embedded clause is a complete clause with its own
        # SUBJ — distinct from the control case where the embedded
        # clause has a SUBJ-gap). The raising binding equation
        # ``(↑ SUBJ) = (↑ XCOMP SUBJ)`` lifts the embedded SUBJ to
        # the matrix.
        for link in ("NA", "NG"):
            rules.append(Rule(
                "S",
                [
                    "V[CTRL_CLASS=RAISING]",
                    f"PART[LINK={link}]",
                    "S",
                ],
                _eqs(
                    "(↑ XCOMP) = ↓3",
                    "(↑ SUBJ) = (↑ XCOMP SUBJ)",
                ),
            ))
        # Phase 5d Commit 1: no-linker raising. ``parang`` and
        # ``tila`` are evidential raising verbs that don't take a
        # following linker (``Parang kumain ang bata``, ``Tila
        # umuulan``). They carry CTRL_CLASS=RAISING_BARE — a
        # distinct value from mukha / baka's CTRL_CLASS=RAISING —
        # so the bare wrap rule below doesn't cross-fire on
        # mukhang / bakang sentences (the existing
        # PART[POLARITY=NEG] negation rule's non-conflict matcher
        # would otherwise let the linker `-ng` slip into a bare-
        # raising parse alongside the linked-raising parse,
        # producing a duplicate). The bare rule's binding mirrors
        # the linked rule's: matrix.SUBJ structure-shares with
        # embedded.SUBJ.
        rules.append(Rule(
            "S",
            ["V[CTRL_CLASS=RAISING_BARE]", "S"],
            _eqs(
                "(↑ XCOMP) = ↓2",
                "(↑ SUBJ) = (↑ XCOMP SUBJ)",
            ),
        ))

        # Transitive frames per voice, two NP orderings each, with and
        # without a trailing sa-oblique (ADJUNCT). The ng-non-pivot
        # binds to a typed ``OBJ-θ`` slot for non-AV voices (per the
        # Phase 5b OBJ-θ-in-grammar alignment); AV keeps bare ``OBJ``
        # because PATIENT/THEME [-r, +o] maps to bare OBJ in the BK
        # truth table. The voice + CAUS feature filter splits plain
        # OV (CAUS=NONE → OBJ-AGENT) from pa-OV-direct (CAUS=DIRECT
        # → OBJ-CAUSER) so each lex entry's PRED template (with its
        # specific role name in the typed OBJ-θ) finds a matching
        # grammar rule.
        voice_specs = [
            # (voice, OBJ-target, extra V-feature constraints)
            ("AV", "OBJ", []),
            ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
            ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
            # Phase 5d Commit 2: explicit CAUS=NONE on DV plain
            # mirrors the OV split, preventing cross-firing on the
            # new DV CAUS=DIRECT pa-...-an forms (where the GEN-NP
            # is the CAUSER, not the AGENT).
            ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
            ("DV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
            ("IV", "OBJ-AGENT", []),
        ]
        for voice, obj_target, extras in voice_specs:
            feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
            v_cat = f"V[{', '.join(feat_strs)}]"
            # NOM-GEN order
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
                _eqs("(↑ SUBJ) = ↓2", f"(↑ {obj_target}) = ↓3"),
            ))
            # GEN-NOM order
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
                _eqs("(↑ SUBJ) = ↓3", f"(↑ {obj_target}) = ↓2"),
            ))
            # NOM-GEN-DAT
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=DAT]"],
                _eqs(
                    "(↑ SUBJ) = ↓2",
                    f"(↑ {obj_target}) = ↓3",
                    "↓4 ∈ (↑ ADJUNCT)",
                ),
            ))
            # GEN-NOM-DAT
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
                _eqs(
                    "(↑ SUBJ) = ↓3",
                    f"(↑ {obj_target}) = ↓2",
                    "↓4 ∈ (↑ ADJUNCT)",
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

        # --- Phase 5e Commit 20: kita clitic fusion ---
        #
        # Tagalog has a special second-position clitic ``kita`` that
        # fuses the 1sg-GEN actor and 2sg-NOM SUBJ of a non-AV verb
        # into a single token: ``Kinain kita`` "I ate you",
        # ``Sinulatan kita ng liham`` "I wrote you a letter",
        # ``Pinakain kita ng kanin`` "I fed you rice",
        # ``Hindi kita kinain`` "I didn't eat you" (with kita
        # hoisted to the post-V cluster by the Wackernagel pass).
        # The fusion is obligatory — *``Kinain ko ka`` is
        # ungrammatical in modern Tagalog (Schachter & Otanes 1972
        # §3.2; Kroeger 1993 §2.2).
        #
        # Lex: ``data/tgl/pronouns.yaml`` carries a single entry
        # ``kita`` with feats ``{KITA: YES, is_clitic: True}``. The
        # grammar rules here build out the SUBJ and 1sg-actor
        # f-structures from atomic-value equations, since the lex
        # loader doesn't support nested feats.
        #
        # The dual binding sets:
        #
        # * ``(↑ SUBJ PERS) = '2'``, ``(↑ SUBJ NUM) = 'SG'``,
        #   ``(↑ SUBJ CASE) = 'NOM'`` — the 2sg-NOM SUBJ (CAUSEE
        #   in pa- variants; PATIENT / RECIPIENT / THEME in plain
        #   variants).
        # * ``(↑ <obj_target> PERS) = '1'``, ``(↑ <obj_target> NUM)
        #   = 'SG'``, ``(↑ <obj_target> CASE) = 'GEN'`` — the
        #   1sg-GEN actor. The typed slot follows the same
        #   per-voice spec used by the standard non-AV S frames:
        #   OBJ-AGENT for plain non-AV; OBJ-CAUSER for pa-OV /
        #   pa-DV (CAUS=DIRECT).
        #
        # Three frame variants per voice spec:
        #
        # 1. **Bare** (``V kita``): the simplest case, e.g.
        #    ``Kinain kita`` (OV), ``Binasahan kita`` (DV),
        #    ``Ipinaggawa kita`` (IV-BEN), ``Pinakain kita``
        #    (pa-OV: "I fed you").
        # 2. **With overt PATIENT** (``V kita NP[GEN]``): used by
        #    3-arg DV / IV / pa-OV constructions, e.g.
        #    ``Sinulatan kita ng liham`` "I wrote you a letter",
        #    ``Pinakain kita ng kanin`` "I fed you rice".
        # 3. **With DAT adjunct** (``V kita NP[DAT]``): a peripheral
        #    location / recipient adjunct.
        #
        # Note on paradigm coverage: the canonical example
        # ``Nakita kita`` "I saw you" requires an OV-NVOL form of
        # ``kita`` (na- prefix on the transitive root). The current
        # ma-class paradigm only emits AV-NVOL forms; ``nakita``
        # analyses as AV-NVOL only, so the kita-fusion rule doesn't
        # fire for it. Tracked as a paradigm-coverage TBD alongside
        # the DV PFV gap from Phase 5e Commit 18 (see plan §18).
        kita_voice_specs = [
            # (voice, obj_target, extras) — mirrors the standard
            # voice_specs above so the typed actor-slot per voice
            # matches the lexicon's expected PRED.
            ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
            ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
            ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
            ("DV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
            ("IV", "OBJ-AGENT", []),
        ]
        kita_subj_eqs = [
            "(↑ SUBJ PERS) = '2'",
            "(↑ SUBJ NUM) = 'SG'",
            "(↑ SUBJ CASE) = 'NOM'",
        ]
        for voice, obj_target, extras in kita_voice_specs:
            feat_strs = [f"VOICE={voice}"] + [f"{k}={v}" for k, v in extras]
            v_cat = f"V[{', '.join(feat_strs)}]"
            actor_eqs = [
                f"(↑ {obj_target} PERS) = '1'",
                f"(↑ {obj_target} NUM) = 'SG'",
                f"(↑ {obj_target} CASE) = 'GEN'",
            ]
            # Bare frame: V kita (no further args). Covers 2-arg
            # constructions and intransitive-feeling causatives.
            rules.append(Rule(
                "S",
                [v_cat, "PRON[KITA=YES]"],
                _eqs(*kita_subj_eqs, *actor_eqs),
            ))
            # With-PATIENT frame: V kita NP[GEN]. Covers 3-arg
            # ditransitives and 3-arg pa-causatives (where the GEN-NP
            # is the OBJ-PATIENT — the third role beyond actor and
            # SUBJ).
            rules.append(Rule(
                "S",
                [v_cat, "PRON[KITA=YES]", "NP[CASE=GEN]"],
                _eqs(
                    *kita_subj_eqs,
                    *actor_eqs,
                    "(↑ OBJ-PATIENT) = ↓3",
                ),
            ))
            # With-DAT frame: V kita NP[DAT]. The DAT-NP rides into
            # ADJUNCT.
            rules.append(Rule(
                "S",
                [v_cat, "PRON[KITA=YES]", "NP[CASE=DAT]"],
                _eqs(
                    *kita_subj_eqs,
                    *actor_eqs,
                    "↓3 ∈ (↑ ADJUNCT)",
                ),
            ))

        return Grammar(rules)
