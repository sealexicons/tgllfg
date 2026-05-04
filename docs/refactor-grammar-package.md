# Refactor plan: split `src/tgllfg/cfg/grammar.py` into per-area modules

**Status:** planned (engineering, post-Phase-5f). **Surfaced:**
2026-05-03 external review. **Tracked:** plan §18 entry "Refactor
``src/tgllfg/cfg/grammar.py`` into a package with smaller modules".

## Why

Phase 5f closed with ``src/tgllfg/cfg/grammar.py`` at 3250 lines
and 201 ``Rule`` appends inside a single ``Grammar.__init__``.
Per-section comment headers (``# --- Phase 5f Commit N: ...``)
make the file navigable but the size is becoming a liability for:

* **Code review.** PRs that touch one Phase 5f construction read
  as a 100-line diff in a 3250-line file; reviewers spend
  effort relocating the change in context.
* **Bisect / blame.** Multi-commit changes (the partitive's
  growing list of negative-Q-feature gates: VAGUE / UNIV /
  DISTRIB_POSS / WHOLE / DUAL across Commits 15 / 20 / 21 / 22
  / 23) all touch the same lines, hurting blame precision.
* **Cognitive load.** New contributors (or future-Claude in a
  new session) need to scan more than necessary to find the
  rule for a given construction.
* **Test isolation.** A future test pass that exercises a
  specific grammar module benefits from a smaller import
  surface.

Pure code reorganisation — no rule semantics change, no
f-structure changes, no test-suite expectations change.

## What

Per the 2026-05-03 reviewer's recommendation, split into per-area
modules colocated in ``src/tgllfg/cfg/`` (NOT a subpackage —
``grammar.py`` stays as the entry point and composer). External
imports (``from tgllfg.cfg.grammar import Grammar``) keep working
unchanged. The existing ``cfg/compile.py`` (grammar compilation:
``CategoryPattern``, ``CompiledGrammar``, ``compile_grammar``,
``parse_pattern``, ``matches``, ``merge_features``) is already
factored out and stays as-is.

```
src/tgllfg/cfg/
├── __init__.py             # re-exports Grammar / Rule / compile API
│                            # (unchanged surface)
├── compile.py              # grammar compilation (existing, unchanged)
├── _helpers.py             # shared utilities: _eqs, _cardinal_case_marker,
│                            # other constants used across rule modules
├── grammar.py              # composes Grammar; calls per-module registrars
├── np_rules.py             # determiners, possessives, demonstratives,
│                            # quantifiers (cardinal / ordinal / vague-Q /
│                            # universal / distrib-poss / whole / measure-N
│                            # / mga / approximator / numeric-comparator
│                            # frames / decimal NUM); ADJ rules land here
│                            # in Phase 5g+
├── clause_rules.py         # V-initial S frames + predicative clauses
│                            # (parang comparative, predicative-cardinal,
│                            # arithmetic predicates)
├── clitic_rules.py         # 2P clitic absorption (S → S PART[CLITIC_CLASS=
│                            # 2P]); float (S → S Q for lahat / pareho /
│                            # kapwa)
├── negation_rules.py       # hindi clausal negation (§7.2) + huwag
│                            # MOOD=IMP lift (Commit 25)
├── extraction_rules.py     # ay-inversion + S_GAP_* + relativization +
│                            # AdvP / PP fronting; Phase 6 FU/LDD lands
│                            # here
├── control_rules.py        # control complement (S_XCOMP) + control wrap
│                            # rules + raising inside control
└── discourse_rules.py      # clause-final ADJUNCTs (FREQUENCY AdvP from
                             # Commit 5; temporal-frame PP from Commit 13;
                             # future discourse-level constructions)
```

Tests continue to live under ``tests/tgllfg/`` — no test code
under ``src/``. New per-module tests (if added) go under
``tests/tgllfg/cfg/`` mirroring the source layout.

### Shared utilities (`_helpers.py`)

The current ``grammar.py`` has two private helpers used across
many rules:

* **``_eqs(*extras: str) -> list[str]``** (line 91 of current
  grammar.py) — appears 100+ times in the existing rules,
  primarily wrapping repetitive equation lists. Move to
  ``_helpers.py`` and import where needed.
* **``_cardinal_case_marker``** (line 306, currently local to
  ``Grammar.__init__``) — a 3-entry dict mapping ``CASE`` to
  the case-marker pattern, used by 6 NP-modifier rules
  (cardinal Commit 1, ordinal Commit 7, vague-Q Commit 15,
  universal Commit 20, distrib-poss Commit 21, whole Commit
  22). Promote to ``_helpers.py`` as a module-level constant.

Other private helpers may surface during the migration; add to
``_helpers.py`` rather than scattering across rule modules.

### When to sub-split a module

The reviewer's listing keeps each per-area module flat (no
subpackages) for the initial refactor. Sub-splitting along
domain boundaries (e.g., ``np_rules/det.py`` /
``np_rules/quant.py`` / ``np_rules/adj.py`` once Phase 5g
adjective work lands) is a follow-up if and when:

* A module exceeds ~1000 lines, OR
* A module has > ~50 ``Rule`` appends in distinct sub-domains
  that don't share constraining-equation infrastructure, OR
* Phase 5g+ lands a substantial new construction class
  (adjective inventory, clausal nominalisation, etc.) that
  more than doubles a module.

For the initial refactor, only ``np_rules.py`` is at risk
(estimated ~95 rules); explicit deferred follow-up.

The ``extraction_rules.py`` (estimated ~50 rules) is just
under the threshold; if Phase 6 FU/LDD adds substantially,
sub-split into ``extraction/ay.py`` /
``extraction/gap.py`` / ``extraction/rc.py`` /
``extraction/fronting.py``.

### Where each Phase 5f rule lands

| Rule (representative) | Source file |
|------------------------|--------------|
| Cardinal NP-modifier (Commit 1) | np_rules.py |
| Ordinal NP-modifier (Commit 7) | np_rules.py |
| Predicative cardinal (Commit 4) | clause_rules.py |
| Decimal NUM rule (Commit 6) | np_rules.py |
| Arithmetic predicate (Commit 9) | clause_rules.py |
| Clock-time NOUNs / time-of-day (Commits 10 / 11) | (lex only — no grammar) |
| Minute composition (Commit 12) | np_rules.py |
| Temporal-frame PP (Commit 13) | discourse_rules.py |
| ``mga`` time approximation (Commit 13 bundled) | np_rules.py |
| Seasons (Commit 14) | (lex only) + np_rules.py SEM_CLASS=SEASON variant of the Commit 13 PP rule, in discourse_rules.py |
| Vague-Q-modifier (Commit 15) | np_rules.py |
| Approximator wraps (Commit 16) | np_rules.py |
| Numeric-comparator frames (Commit 17) | np_rules.py |
| Measure-N rule (Commit 18) | np_rules.py |
| Distributive ``tig-`` (Commit 19) | (lex only — no grammar) |
| Universal ``bawat`` / ``kada`` (Commit 20) | np_rules.py |
| Distributive-possessive (Commit 21) | np_rules.py |
| Wholes ``buo`` (Commit 22) | np_rules.py |
| Dual ``pareho`` / ``kapwa`` (Commit 23) | (lex only; consumes float in clitic_rules.py) |
| FREQUENCY AdvP clause-final (Commit 5) | discourse_rules.py |

### Where each pre-Phase-5f rule lands

* **Phase 4 §7.1 V-initial S frames** → clause_rules.py
* **Phase 4 §7.2 negation** → negation_rules.py
* **Phase 4 §7.3 adverbial enclitics** → clitic_rules.py
* **Phase 4 §7.4 ay-inversion** → extraction_rules.py
* **Phase 4 §7.5 SUBJ-gapped clauses + relativization** → extraction_rules.py
* **Phase 4 §7.6 control complement + control wrap** → control_rules.py
* **Phase 4 §7.8 NP shells / dems / NP-poss / float / pre-NP partitive** → np_rules.py (NP rules) + clitic_rules.py (float)
* **Phase 5b §7.8 follow-on partitive** → np_rules.py
* **Phase 5d Commit 3 post-modifier dem** → np_rules.py
* **Phase 5d Commit 5 non-pivot ay-fronting** → extraction_rules.py
* **Phase 5d Commit 6 possessive-linker RC** → extraction_rules.py
* **Phase 5d Commit 7 raising inside control** → control_rules.py
* **Phase 5e Commit 1 pa-OV / pa-DV ay-fronting** → extraction_rules.py
* **Phase 5e Commit 2 multi-GEN-NP ay-fronting** → extraction_rules.py
* **Phase 5e Commit 3 AdvP / PP categorial inventory + fronting** → extraction_rules.py
* **Phase 5e Commit 5 headless / free relatives** → extraction_rules.py
* **Phase 5e Commits 16 / 17 pre-modifier dem** → np_rules.py
* **Phase 5e Commit 18 / 19 dual-binding wrap** → extraction_rules.py
* **Phase 5e Commit 25 huwag MOOD lift** → negation_rules.py
* **Phase 5e Commit 26 parang comparative** → clause_rules.py

### Rough rule counts (post-decomposition)

| Module | Rule count | Notes |
|--------|-----------:|-------|
| np_rules | ~95 | densest (most NP + Phase 5f Q-modifier rules) |
| extraction_rules | ~50 | S_GAP_* + ay-fronting + relativization |
| control_rules | ~20 | XCOMP + control wrap + raising |
| clause_rules | ~15 | V-initial + predicative clauses |
| discourse_rules | ~10 | clause-final ADJUNCT (PP, AdvP, etc.) |
| clitic_rules | ~5 | 2P clitics + float |
| negation_rules | ~5 | hindi + huwag |
| **grammar.py** | 0 (composer) | calls registrars in order |
| **total** | **~200** | matches current 201 |

Counts are approximate; the migration may surface candidates for
re-grouping. ``np_rules.py`` is the largest single module — if it
exceeds ~1000 lines after migration, consider splitting along
distribution boundaries (``np_rules/det.py``, ``np_rules/quant.py``,
etc.) in a follow-up. Initial migration keeps it as one file.

## How

### Migration strategy (incremental, single PR)

1. **Cut a ``feature/refactor-grammar-package`` branch** from
   main after Phase 5f's H3 PR (#18) merges.

2. **Capture the parse baseline.** Add ``scripts/check_parses_unchanged.py``
   that pickles the ranker's top-1 parse for every sentence in
   ``tests/tgllfg/data/coverage_corpus.yaml`` to
   ``tests/tgllfg/data/parses.baseline.pkl``. Run once on main
   to produce the baseline; commit it.

3. **Define the registrar protocol.** Each ``*_rules.py`` module
   exports a single function:

   ```python
   def register_rules(rules: list[Rule]) -> None:
       """Append rules for this module's domain to ``rules``."""
       rules.append(Rule(...))
       ...
   ```

   ``grammar.py``'s ``Grammar.__init__`` becomes a thin composer
   that instantiates the rule list and calls each registrar in
   the established order:

   ```python
   from . import (
       clause_rules,
       clitic_rules,
       control_rules,
       discourse_rules,
       extraction_rules,
       negation_rules,
       np_rules,
   )

   class Grammar:
       def __init__(self) -> None:
           rules: list[Rule] = []
           np_rules.register_rules(rules)
           clause_rules.register_rules(rules)
           clitic_rules.register_rules(rules)
           negation_rules.register_rules(rules)
           extraction_rules.register_rules(rules)
           control_rules.register_rules(rules)
           discourse_rules.register_rules(rules)
           self.rules = rules
   ```

   Order matters — see "Risk considerations" below.

4. **Per-module extraction, one commit each.** For each module,
   in order ``np_rules`` → ``clause_rules`` → ``clitic_rules`` →
   ``negation_rules`` → ``extraction_rules`` → ``control_rules``
   → ``discourse_rules``:

   1. Create the new ``*_rules.py`` file with a stub
      ``register_rules`` function.
   2. Move the relevant ``rules.append(Rule(...))`` calls (with
      their per-section comment headers intact) from
      ``grammar.py`` into the new module's ``register_rules``.
   3. Update ``grammar.py``'s ``Grammar.__init__`` to call the
      new module's registrar.
   4. Run the test suite. Run ``check_parses_unchanged.py``.
      Both must show zero diff.
   5. Commit per-module.

5. **Final cleanup commit.** Once all modules extracted,
   ``grammar.py`` should be ~30 lines (Grammar class +
   imports + composer). Any rule that doesn't fit a clean
   module stays in clause_rules.py (the catch-all for clausal
   defaults) or grammar.py if it's truly cross-cutting.

6. **PR ``Engineering — split grammar.py into per-area
   modules``.** Single PR with ~9 commits (one per module +
   baseline + final cleanup). Description focuses on the
   engineering rationale and the zero-diff invariant.

### Test-suite invariants (across the refactor)

* **Zero pytest diff.** Every commit in the refactor PR must
  pass the full pytest suite with the same test count and
  outcomes as the previous commit. ``hatch run pytest -q`` ≡
  identical output.
* **Zero coverage-corpus diff.** ``hatch run python
  scripts/generate_coverage_corpus.py`` produces byte-identical
  output before and after.
* **Zero ranker-output diff.** ``scripts/check_parses_unchanged.py``
  diffs the ranker's top-1 parse for each sentence in
  ``tests/tgllfg/data/coverage_corpus.yaml`` against the
  baseline pickle. Run as the first step (capture baseline) and
  again after the final commit (confirm zero diff). Spot-check
  with the per-construction test files to catch any
  regressions the corpus might miss.
* **No new test files in this PR.** New per-module unit tests
  are nice-to-have but defer to follow-up commits; the
  refactor PR's purpose is reorganisation, not test
  expansion. Tests live under ``tests/tgllfg/`` (NOT under
  ``src/``).

### Risk considerations

* **Rule order matters.** The Earley parser doesn't depend on
  registration order, but the ranker's tie-breaker may. The
  migration preserves order by appending in the registrar-call
  order in ``grammar.py``. The composer's ``register_rules``
  call sequence MUST match the order rules appeared in the
  pre-refactor ``grammar.py``.

* **Cross-module references.** Some constants are shared:
  * ``_cardinal_case_marker`` (used in Commits 1 / 7 / 15 / 20
    / 21 / 22) → move to a private module-level constant in
    ``np_rules.py`` (the only consumer); export if other
    modules surface a need.
  * ``_eqs`` helper (if it exists) → keep in ``grammar.py`` or
    move to a private utilities module ``cfg/_helpers.py``.

* **Comment provenance.** The current per-section comments
  (``# --- Phase 5f Commit N: ...``) are dense linguistic
  references. They MUST migrate intact to the new modules —
  the per-construction analysis-choices.md cross-references
  the line numbers indirectly via section headers, so the
  comments need to move with the rules.

* **Bisect compatibility.** The per-module commits should be
  bisectable: each commit is a self-contained "extract module
  X" step that leaves the test suite passing. A tester running
  ``git bisect`` on a regression after the refactor should be
  able to pinpoint a specific extraction.

* **np_rules.py size.** This module gets the largest share
  (~95 rules). If it grows past ~1000 lines as new
  constructions land in Phase 5g+ (adjectives), revisit a
  sub-split (``np_rules/det.py``, ``np_rules/quant.py``,
  ``np_rules/adj.py``). Initial refactor keeps it monolithic.

## When

The plan §18 entry suggests "between Phase 5f close and Phase
5g start as a dedicated refactor PR." Concretely:

* **Triggering condition:** when the user is ready to start
  Phase 5g and wants the grammar module reorganised first.
* **Effort estimate:** ~4-6 hours of focused work.
  Mechanically straightforward (no rule semantics change), but
  requires careful per-commit testing to maintain the zero-diff
  invariant.
* **Effort level:** ``high`` per the §19 table — pure
  engineering, but touches every Phase 4 / 5 / 5b-5f rule, so
  needs care.

## Out of scope (for the refactor PR)

* **Rule semantics changes.** No new rules, no rule shape
  changes, no constraining-equation changes. Pure
  reorganisation.
* **Test additions.** New per-module unit tests are a follow-up
  PR; the refactor PR's purpose is reorganisation.
* **Plan §18 cleanup.** Other Phase 5f deferrals (hyphenation
  tokenizer, productive paradigms, ``(lemma, pos)`` polysemy,
  digit tokenization, NP-from-N projection) are separate;
  not bundled.
* **Renames of existing rule features.** No renaming of
  ``CARDINAL=YES`` to ``IS_CARDINAL`` etc. Keep all surface
  feature names as-is.
* **Type-hint upgrades.** No type-hint changes beyond what
  module split requires.
* **Sub-splitting np_rules.py** along det/quant/adj boundaries
  — defer until size demands it.
