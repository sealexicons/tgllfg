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


class Grammar:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules: list[Rule] = list(rules)

    @staticmethod
    def load_default() -> "Grammar":
        # Deferred import: ``np_rules`` re-imports ``Rule`` from this
        # module, so it must be loaded after ``Rule`` is defined.
        from . import (
            clause_rules,
            clitic_rules,
            control_rules,
            extraction_rules,
            negation_rules,
            np_rules,
        )

        rules: list[Rule] = []

        np_rules.register_rules(rules)
        clause_rules.register_rules(rules)
        clitic_rules.register_rules(rules)
        negation_rules.register_rules(rules)
        extraction_rules.register_rules(rules)
        control_rules.register_rules(rules)

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

        return Grammar(rules)
