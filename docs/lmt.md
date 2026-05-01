# Lexical Mapping Theory (Phase 5)

The `tgllfg.lmt` package implements a Bresnan–Kanerva 1989 LMT
engine that derives the role-to-grammatical-function mapping for a
verb from its intrinsic `[±r, ±o]` profile plus voice morphology.
It replaces the Phase 4 voice-aware heuristic in
`src/tgllfg/lmt/legacy.py` (still kept for the no-lex-entry edge
case) with a principled per-step computation:

1. The lex entry supplies intrinsic classifications per role.
2. Voice morphology supplies additional `[±r, ±o]` constraints.
3. Default classifications fill unspecified features.
4. Subject Mapping picks the SUBJ role.
5. Remaining arguments map by feature compatibility.
6. Subject Condition: every PRED-bearing f-structure has a SUBJ.
7. Biuniqueness: each role maps to one GF; each GF receives at
   most one role.

Each step is one named function in `tgllfg.lmt.principles`; the
orchestrator `compute_mapping` chains them. The pipeline-facing
wrapper `apply_lmt_with_check` locates the matrix lex entry by
PRED + percolated features, runs the engine, runs the post-solve
oblique classifier, compares the predicted GF set against the
parsed f-structure, and surfaces typed diagnostics.

## Components

| Module | Purpose |
|---|---|
| `tgllfg/lmt/common.py` | Data types (`Role`, `IntrinsicFeatures`, `IntrinsicClassification`, `MappingResult`); typed-GF helpers (`obj_theta`, `obl_theta`); the canonical-intrinsic table (`default_intrinsics`); lex-entry bridges (`intrinsics_for`, `stipulated_gfs_for`). |
| `tgllfg/lmt/principles.py` | The seven BK 1989 principles as named pure functions, plus the orchestrator `compute_mapping` and the `ROLE_HIERARCHY` ordering. |
| `tgllfg/lmt/oblique_classifier.py` | Post-solve mutation that reclassifies `ADJUNCT` members with `CASE=DAT` into typed `OBL-θ` slots based on the engine's mapping. |
| `tgllfg/lmt/check.py` | Pipeline-facing `lmt_check` / `apply_lmt_with_check`. Locates the matrix lex entry, runs engine + classifier, surfaces diagnostics. |
| `tgllfg/lmt/legacy.py` | Phase 4 voice-aware heuristic. Used only when `find_matrix_lex_entry` returns `None` (defensive fallback). |

## Data types

### `Role`

The role inventory unions the plan §8.1 core (`AGENT`, `PATIENT`,
`THEME`, `GOAL`, `RECIPIENT`, `BENEFICIARY`, `INSTRUMENT`,
`LOCATION`, `EXPERIENCER`, `STIMULUS`) with Tagalog augmentation:

| Augmentation role | Why it's separate |
|---|---|
| `ACTOR` | Intransitive AV pivot. Synonymous with `AGENT` thematically but kept distinct for the synthesizer-fallback path that emits `[ACTOR]` when transitivity is unspecified. |
| `CONVEYED` | IV-pivot for transferred entities (`itinapon`, `ibinili`, `isinulat`). Behaves like `THEME` in the truth table but voice-marked differently. |
| `CAUSER` / `CAUSEE` | §7.7 causative frames. `CAUSER` is agent-like, `CAUSEE` patient-like in monoclausal `pa-` direct causatives; in biclausal `magpa-` the causee surfaces as the embedded XCOMP's SUBJ. |
| `EVENT` | The caused event in `magpa-` indirect causatives; XCOMP-bound (off the truth table). |
| `COMPLEMENT` | Open-complement target for §7.6 control verbs (`gusto`, `payag`, `pilit`, `utos`); XCOMP-bound. |
| `REASON` | Pivot of the `ika-` reason applicative (Phase 5c §7.7 follow-on, Commit 4). Patterns like `INSTRUMENT` — non-volitional, secondary-topic capable; default intrinsic `(r=None, o=False)`. |

`Role.gf_suffix` returns the short tag used in typed-GF strings —
`LOC` (LOCATION), `BEN` (BENEFICIARY), `INSTR` (INSTRUMENT), `RECIP`
(RECIPIENT). Other roles use the bare role name.

### `IntrinsicFeatures`

The `[±r, ±o]` feature pair as ternary booleans. `True` =
`+`, `False` = `-`, `None` = unspecified. The truth table:

| `(r, o)` | Maps to |
|---|---|
| `(False, False)` | `SUBJ` |
| `(False, True)` | `OBJ` (bare) |
| `(True, True)` | `OBJ-θ` (typed: `OBJ-<role.gf_suffix>`) |
| `(True, False)` | `OBL-θ` (typed: `OBL-<role.gf_suffix>`) |

`merged_with(other)` lets voice morphology layer constraints on
top of lexical intrinsics; raises `ValueError` on conflict.

### `IntrinsicClassification`

A `(role, intrinsics)` pair. Lex entries store a list of these
as `LexicalEntry.intrinsic_classification`, keyed by role-name
string for JSONB compatibility.

### `MappingResult`

The output of `compute_mapping`: `mapping: dict[Role, str]` plus
`diagnostics: tuple[Diagnostic, ...]`.

## The seven principles

### Step 1 — lex entry intrinsics

Happens at the call site. The lexicon (`src/tgllfg/lexicon.py`
`BASE` and `_synthesize_verb_entry`) attaches a per-voice profile
to each entry. Each profile pins exactly one role at `[-r, -o]`
(the pivot for that voice form); non-pivot ng-NPs are `[+r, +o]`
(typed `OBJ-θ`) and non-pivot sa-NPs are `[+r, -o]` (typed
`OBL-θ`).

### Step 2 — `apply_voice_constraints`

Layers voice-imposed `[±r, ±o]` stamps on top of the lex
profile. For Tagalog this is usually a no-op (each voice form has
its own lex entry row), but the function exists so the seven-step
pipeline is explicit.

### Step 3 — `fill_defaults`

Fills remaining `None` slots:

* If no role currently has `o=False`, the highest-hierarchy role
  with `o=None` gets `o=False` (so step 4 has at least one
  SUBJ candidate).
* All remaining `None` `o` components default to `True`.
* All remaining `None` `r` components default to `True`.

For lex entries that already supply complete profiles, this is a
no-op.

### Step 4 — `subject_mapping`

Three-tier cascade:

1. Highest-hierarchy role with `[-r, -o]` (full SUBJ-eligibility).
2. Else highest-hierarchy role with `o=False` (the plan's
   "compatible with [-o]").
3. Else highest-hierarchy role with `r=False`.
4. `None` (Subject Condition will fail).

The `[-r, -o]` tier dominates so IV-CONVEY's `CONVEYED [-r, -o]`
wins over its `GOAL [+r, -o]` co-argument.

### Step 5 — `non_subject_mapping`

The truth table above. Raises `ValueError` if called on a `[-r,
-o]` role (the orchestrator catches this and surfaces as a
biuniqueness violation).

### Step 6 — `check_subject_condition`

Emits `subject-condition-failed` if no role maps to SUBJ. The
diagnostic kind already exists in `tgllfg.fstruct` as part of
the §4.4 well-formedness inventory.

### Step 7 — `check_biuniqueness`

Emits `lmt-biuniqueness-violated` when two roles share a
fully-qualified GF string. Typed forms `OBJ-AGENT` and
`OBJ-PATIENT` are distinct GFs and don't clash.

## Worked examples per voice

Each example shows the lex entry's intrinsic profile, the engine's
output, and notes on the f-structure interaction.

### AV transitive (`kumain ng isda`)

```
profile: AGENT (-r, -o), PATIENT (-r, +o)
mapping: AGENT → SUBJ, PATIENT → OBJ
```

Bare `OBJ` from the truth table. Engine and Phase 4 grammar agree
on both slots; no diagnostic fires.

### OV transitive (`kinain ng aso ang isda`)

```
profile: AGENT (+r, +o), PATIENT (-r, -o)
mapping: AGENT → OBJ-AGENT, PATIENT → SUBJ
```

The engine produces typed `OBJ-AGENT` per the upgrade decision.
Phase 4 grammar still emits bare `OBJ`; the disagreement surfaces
as informational `lmt-mismatch`.

### DV transitive (`sinulatan ng bata ang ina`)

```
profile: AGENT (+r, +o), RECIPIENT (-r, -o)
mapping: AGENT → OBJ-AGENT, RECIPIENT → SUBJ
```

The lex entry uses `RECIPIENT` (the actual thematic role of
sulat's pivot in DV); the legacy heuristic hard-coded `GOAL`.

### IV-CONVEY (`itinapon ng bata ang basura`)

```
profile: AGENT (+r, +o), CONVEYED (-r, -o)
mapping: AGENT → OBJ-AGENT, CONVEYED → SUBJ
```

### IV-BEN applicative (`ipinaggawa niya ako`)

```
profile: AGENT (+r, +o), BENEFICIARY (-r, -o)
mapping: AGENT → OBJ-AGENT, BENEFICIARY → SUBJ
```

### `pa-` direct causative (`pinakain niya ang bata`)

```
profile: CAUSER (+r, +o), CAUSEE (-r, -o)
mapping: CAUSER → OBJ-CAUSER, CAUSEE → SUBJ
```

Monoclausal: the embedded eventuality is folded into the matrix
PRED (`CAUSE-EAT <SUBJ, OBJ>`).

### `magpa-` indirect causative (`nagpakain ang nanay na kumain`)

```
profile: CAUSER (-r, -o), EVENT (None, None)
stipulated: {EVENT: XCOMP}
mapping: CAUSER → SUBJ, EVENT → XCOMP
```

Biclausal: `EVENT` bypasses the truth table via `stipulated_gfs`
(supplied from the lex entry's `gf_defaults`). The causee surfaces
inside the embedded XCOMP's SUBJ slot.

### Psych control (`gusto kong kumain`)

```
profile: EXPERIENCER (-r, -o), COMPLEMENT (None, None)
stipulated: {COMPLEMENT: XCOMP}
mapping: EXPERIENCER → SUBJ, COMPLEMENT → XCOMP
```

The `EXPERIENCER → SUBJ` mapping deviates from the
NOM→SUBJ default — the `gusto` lex entry's GEN-experiencer is
the matrix SUBJ, encoded via the `[-r, -o]` intrinsic profile.

### Intransitive control (`pumayag siyang kumain`)

```
profile: AGENT (-r, -o), COMPLEMENT (None, None)
stipulated: {COMPLEMENT: XCOMP}
mapping: AGENT → SUBJ, COMPLEMENT → XCOMP
```

### Transitive control — OV (`pinilit siyang kumain`)

```
profile: AGENT (+r, +o), PATIENT (-r, -o), COMPLEMENT (None, None)
stipulated: {COMPLEMENT: XCOMP}
mapping: AGENT → OBJ-AGENT, PATIENT → SUBJ, COMPLEMENT → XCOMP
```

The matrix lex's analysis is independent of the embedded clause's
voice. Phase 5c §7.6 follow-on lifts the AV-only restriction on
`S_XCOMP` so the embedded clause can be OV / DV / IV — e.g.,
`pinilit ko siyang kakainin ang isda` ("I forced him to eat the
fish", with OV embedded). The matrix wrap rule
`(↑ SUBJ) = (↑ XCOMP REL-PRO)` is unchanged; under non-AV embedded
the gap routes to `OBJ-AGENT` (the actor's typed GF), so the
matrix `PATIENT/SUBJ` still controls the embedded actor. The
Phase 5b embedded-clause LMT check then validates the embedded
clause against its own lex's intrinsic profile.

### AV motion with sa-locative (`lumakad ang bata sa palengke`)

```
profile: ACTOR (-r, -o), LOCATION (+r, -o)
mapping: ACTOR → SUBJ, LOCATION → OBL-LOC
```

The post-solve oblique classifier moves the sa-NP from `ADJUNCT`
into the `OBL-LOC` slot. The locative entry parse coexists with
the bare-intransitive parse (the sa-NP is a setting locative);
both are linguistically valid.

## sa-NP → typed OBL-θ classification

The Phase 4 grammar binds `NP[CASE=DAT]` into the matrix
f-structure's `ADJUNCT` set via `↓N ∈ (↑ ADJUNCT)` equations,
regardless of whether the sa-NP is an argument (locative goal,
recipient, beneficiary) or a modifier (setting locative,
temporal adjunct). Phase 5 reclassifies the argument cases:

`tgllfg.lmt.oblique_classifier.classify_oblique_slots` is a
post-solve mutation. After `solve()` produces the f-structure
and the engine produces a mapping, the classifier:

1. Walks `f.feats["ADJUNCT"]`.
2. Identifies sa-NP members (those with `feats["CASE"] == "DAT"`).
3. For each `OBL-θ` GF in the engine's mapping, moves a sa-NP
   from `ADJUNCT` into the typed slot.
4. Members without `CASE=DAT` (adverbial enclitics from §7.3,
   embedded clauses) are left in `ADJUNCT`.

Why post-solve mutation, not grammar-rule rewrite: the §7.5
relativization, §7.3 clitic placement, §7.4 ay-inversion, and
§7.8 quantifier float all consume the parser's c-tree and the
same `↓N ∈ (↑ ADJUNCT)` equations. Rewriting the grammar to emit
`OBL-X` directly would require duplicating each rule per
verb-class and fighting the non-conflict matcher. Post-solve
mutation contains the blast radius.

Multi-OBL ambiguity (multiple `OBL-θ` roles competing for
multiple sa-NPs) is out of scope. The classifier matches in stable
order — a-structure for roles, `FStructure.id` for sa-NPs — and
emits an `lmt-mismatch` diagnostic on cardinality mismatch.

## Diagnostic policy

| Source | Kind | Routing |
|---|---|---|
| Engine predicts SUBJ but f-structure has none | `subject-condition-failed` | **Blocking** |
| Engine emits `lmt-biuniqueness-violated` | `lmt-biuniqueness-violated` | **Blocking** |
| Engine emits `subject-condition-failed` (lex-only) | dropped | Structural well-formedness catches the case where the f-structure also lacks SUBJ |
| GF-set differences (OBJ ⇄ OBJ-θ, OBL classification leftovers) | `lmt-mismatch` | Informational (in `NON_BLOCKING_KINDS`) |

`lmt-mismatch` carries `detail = {"expected": [...], "actual":
[...], "pred": "..."}` so downstream consumers can inspect the
specific GFs that disagreed.

## Open issues / Phase 5b stretch

* **Multi-GEN-NP applicative / causative frames.** A 3-arg
  `ipinaggawa niya ng silya ang kapatid niya` ("he made a chair
  for his sibling") would have `AGENT [+r, +o]`, `PATIENT [+r,
  +o]`, `BENEFICIARY [-r, -o]` — two distinct OBJ-θ slots
  (`OBJ-AGENT`, `OBJ-PATIENT`). The LMT engine handles such
  profiles cleanly (see the deferred tests in
  `tests/tgllfg/test_lmt_voice_mappings.py::TestMultiGenFramesDeferred`),
  but no Phase 4 BASE entry currently emits them and the grammar
  rules need a second-GEN-NP slot.

* **Multi-OBL semantic disambiguation.** When two `OBL-θ` roles
  compete for two sa-NPs, the classifier matches positionally.
  Real disambiguation needs semantic context (which sa-NP is
  `BEN` vs `LOC`); deferred.

* **Embedded-clause LMT (lifted in Phase 5b).** Phase 5
  `lmt_check` only validated the matrix f-structure. Phase 5b
  extended :func:`apply_lmt_with_check` to recursively walk
  ``XCOMP`` / ``COMP`` slots and run :func:`lmt_check` on each
  embedded f-structure that has its own ``PRED``. Embedded-clause
  diagnostics carry the f-structure path (e.g., ``XCOMP`` /
  ``XCOMP.XCOMP``) so the user can see where they came from.

* **OBJ-θ in the grammar (lifted in Phase 5b).** The Phase 4
  grammar emitted bare `OBJ` for non-AV ng-non-pivots while the
  engine produced `OBJ-θ` — informational `lmt-mismatch` flagged
  the divergence. Phase 5b aligned the grammar to emit typed
  `OBJ-AGENT` / `OBJ-CAUSER` directly per voice/verb class,
  eliminating the diagnostic noise.

## See also

* `~/.claude/plans/tgllfg-evolution.md` §8 — the plan section
  that motivated this implementation.
* `docs/analysis-choices.md` — Phase 5 §8 LMT entry for the
  analytical decisions (OBJ-θ upgrade, role-inventory augmentation,
  OBL-X classification approach, diagnostic promotion policy).
* `tests/tgllfg/test_lmt_voice_mappings.py` — the per-voice
  regression corpus.
