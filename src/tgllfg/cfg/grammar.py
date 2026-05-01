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

        # --- Phase 4 §7.8: NP-internal possessive ---
        #
        # ``ang aklat ng bata`` ("the child's book") and pronominal
        # ``ang aklat ko`` ("my book"). The GEN-NP modifier attaches
        # at the right edge of the head NP and rides into the head's
        # f-structure as ``POSS``. Recursive: ``ang aklat ng pamilya
        # ng bata`` ("the child's family's book") — but the binding
        # is left-associative: each layer of POSS sits above the
        # previous head NP.
        for case in ("NOM", "GEN", "DAT"):
            rules.append(Rule(
                f"NP[CASE={case}]",
                [f"NP[CASE={case}]", "NP[CASE=GEN]"],
                ["(↑) = ↓1", "(↑ POSS) = ↓2"],
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
        rules.append(Rule(
            "NP[CASE=NOM]",
            ["DET[CASE=NOM]", "Q", "NP[CASE=GEN]"],
            ["(↑) = ↓1", "(↑ PRED) = ↓3 PRED", "(↑ QUANT) = ↓2 QUANT"],
        ))
        rules.append(Rule(
            "NP[CASE=GEN]",
            ["ADP[CASE=GEN]", "Q", "NP[CASE=GEN]"],
            ["(↑) = ↓1", "(↑ PRED) = ↓3 PRED", "(↑ QUANT) = ↓2 QUANT"],
        ))
        rules.append(Rule(
            "NP[CASE=DAT]",
            ["ADP[CASE=DAT]", "Q", "NP[CASE=GEN]"],
            ["(↑) = ↓1", "(↑ PRED) = ↓3 PRED", "(↑ QUANT) = ↓2 QUANT"],
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
                "(↑ PRED) = 'NOUN(↑ FORM)'",
                "(↑ LEMMA) = ↓1 LEMMA",
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
        rules.append(Rule(
            "S",
            ["PART[POLARITY=NEG]", "S"],
            ["(↑) = ↓2", "(↑ POLARITY) = 'NEG'"],
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
        # slot would be ``OBJ-CAUSER``; APPL=CONVEY on IV
        # discriminates against IV-BEN multi-GEN frames.
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
            ["V[VOICE=IV, APPL=CONVEY]", "NP[CASE=NOM]"],
            _eqs(
                "(↑ SUBJ) = ↓2",
                "(↑ OBJ-AGENT) = (↑ REL-PRO)",
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

        # --- Phase 5d Commit 6: possessive-linker RC wrap rule ---
        #
        # ``aklat kong binasa`` ("the book that I read"): a
        # construction parallel to relativization where the
        # pronominal actor of the RC's non-AV verb surfaces as a
        # possessor of the head NP, joined by the bound ``-ng``
        # linker. The pre-parse Wackernagel pass keeps PRON in
        # place when followed by ``PART[LINK=NG]`` (see
        # ``_is_pre_linker_pron``), so the four tokens (head NP,
        # PRON, ``-ng``, V) reach the parser in surface order.
        #
        # The pronoun plays a dual role: it is the head NP's
        # ``POSS`` AND the RC's ``OBJ-AGENT``. The wrap rule binds
        # both via ``(↑ POSS) = ↓2`` and ``(↓4 OBJ-AGENT) = ↓2``.
        # REL-PRO sharing follows the standard relativization
        # pattern — anaphoric (PRED + CASE atomic-path copies, not
        # full identity) so the unifier's occurs-check stays happy.
        #
        # Three head-case variants (NOM / GEN / DAT) covering the
        # construction in any NP position.
        for case in ("NOM", "GEN", "DAT"):
            np_cat = f"NP[CASE={case}]"
            rules.append(Rule(
                np_cat,
                [np_cat, "PRON[CASE=GEN]", "PART[LINK=NG]", "S_GAP_NA"],
                [
                    "(↑) = ↓1",
                    "(↑ POSS) = ↓2",
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

        return Grammar(rules)
