# tgllfg/cfg/grammar.py

"""Default Tagalog grammar — entry point and composer.

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
recognised by the grammar (lex_entry templates may carry them).

Module organisation (post-Phase-5f split, see
``docs/refactor-grammar-package.md``): ``grammar.py`` defines the
``Rule`` dataclass and the ``Grammar`` composer class. The
individual rule appends live in eight per-area modules colocated
in ``cfg/`` — :mod:`nominal`, :mod:`clause`, :mod:`clitic`,
:mod:`negation`, :mod:`extraction`, :mod:`control`,
:mod:`discourse`, :mod:`coordination` (Phase 5k). Each exports a
single ``register_rules(rules)`` function; ``Grammar.load_default``
calls them in order. Per-area linguistic context (negation
overlays, the ``S_GAP`` / ``S_XCOMP`` gap-category designs, etc.)
lives in the respective module's docstring.
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
        # Deferred import: every per-area registrar module re-imports
        # ``Rule`` from this module, so they must be loaded after
        # ``Rule`` is defined.
        from . import (
            clause,
            clitic,
            control,
            coordination,
            discourse,
            extraction,
            negation,
            nominal,
        )

        rules: list[Rule] = []

        nominal.register_rules(rules)
        clause.register_rules(rules)
        clitic.register_rules(rules)
        negation.register_rules(rules)
        extraction.register_rules(rules)
        control.register_rules(rules)
        coordination.register_rules(rules)
        discourse.register_rules(rules)

        return Grammar(rules)
