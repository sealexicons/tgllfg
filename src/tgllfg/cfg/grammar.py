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
~200 individual rule appends live in seven per-area modules
colocated in ``cfg/`` — :mod:`np_rules`, :mod:`clause_rules`,
:mod:`clitic_rules`, :mod:`negation_rules`, :mod:`extraction_rules`,
:mod:`control_rules`, :mod:`discourse_rules`. Each exports a single
``register_rules(rules)`` function; ``Grammar.load_default`` calls
them in order. Per-area linguistic context (negation overlays, the
``S_GAP`` / ``S_XCOMP`` gap-category designs, etc.) lives in the
respective module's docstring.
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
            clause_rules,
            clitic_rules,
            control_rules,
            discourse_rules,
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
        discourse_rules.register_rules(rules)

        return Grammar(rules)
