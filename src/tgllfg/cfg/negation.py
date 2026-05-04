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

from __future__ import annotations

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
