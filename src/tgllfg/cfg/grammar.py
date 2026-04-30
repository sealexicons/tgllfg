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
        rules.append(Rule(
            "NP[CASE=NOM]",
            ["DET[CASE=NOM]", "N"],
            ["(↑ CASE) = 'NOM'", "(↑ PRED) = ↓2 PRED"],
        ))
        rules.append(Rule(
            "NP[CASE=GEN]",
            ["ADP[CASE=GEN]", "N"],
            ["(↑ CASE) = 'GEN'", "(↑ PRED) = ↓2 PRED"],
        ))
        rules.append(Rule(
            "NP[CASE=DAT]",
            ["ADP[CASE=DAT]", "N"],
            ["(↑ CASE) = 'DAT'", "(↑ PRED) = ↓2 PRED"],
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

        # --- N from NOUN (toy PRED; Phase 5 will lexicalise properly) ---
        rules.append(Rule(
            "N",
            ["NOUN"],
            ["(↑ PRED) = 'NOUN(↑ FORM)'"],
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
        for voice in ("AV", "OV", "DV", "IV"):
            v_cat = f"V[VOICE={voice}]"
            rules.append(Rule(
                "S_GAP",
                [v_cat, "NP[CASE=GEN]"],
                _eqs("(↑ OBJ) = ↓2", "(↑ SUBJ) = (↑ REL-PRO)"),
            ))
            rules.append(Rule(
                "S_GAP",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=DAT]"],
                _eqs(
                    "(↑ OBJ) = ↓2",
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

        # Transitive frames per voice, two NP orderings each, with and
        # without a trailing sa-oblique (ADJUNCT).
        for voice in ("AV", "OV", "DV", "IV"):
            v_cat = f"V[VOICE={voice}]"
            # NOM-GEN order
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
                _eqs("(↑ SUBJ) = ↓2", "(↑ OBJ) = ↓3"),
            ))
            # GEN-NOM order
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]"],
                _eqs("(↑ SUBJ) = ↓3", "(↑ OBJ) = ↓2"),
            ))
            # NOM-GEN-DAT
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]", "NP[CASE=DAT]"],
                _eqs("(↑ SUBJ) = ↓2", "(↑ OBJ) = ↓3", "↓4 ∈ (↑ ADJUNCT)"),
            ))
            # GEN-NOM-DAT
            rules.append(Rule(
                "S",
                [v_cat, "NP[CASE=GEN]", "NP[CASE=NOM]", "NP[CASE=DAT]"],
                _eqs("(↑ SUBJ) = ↓3", "(↑ OBJ) = ↓2", "↓4 ∈ (↑ ADJUNCT)"),
            ))

        return Grammar(rules)
