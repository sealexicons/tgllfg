<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# FU-extension consumer audit (Phase 11.A)

<!-- markdownlint-disable-file MD013 -->

This document is the deliverable of Phase 11.A. It surveys the existing
chart-rule corpus for opportunities to opt into the three FU-extension
engine forms shipped during Phase 10.L / 10.M / 10.N, and produces a
prioritized backlog for Phase 11.B+ consumer sub-PRs.

Cross-references:

- 10.L Kleene-on-alternation `{F | G}* / {F | G}+` —
  `src/tgllfg/fstruct/equations.py:StarAltFeature` /
  `PlusAltFeature`; design captured in
  `docs/fu-evaluation.md` §3 / §4.1 / §7.2.
- 10.M deferred defining-equation re-pass —
  `src/tgllfg/fstruct/unify.py:_repass_deferred_fu`; design captured in
  `docs/fu-evaluation.md` §5.2.1.
- 10.N inside-out designators `(FEAT INNER)` —
  `src/tgllfg/fstruct/equations.py:InsideOut` +
  `src/tgllfg/fstruct/graph.py:FGraph.parents_via`; design captured in
  `docs/fu-evaluation.md` §7.4.1.
- Phase 11 plan-of-record: `.claude/plans/tgllfg-phase-11.md`.
- Source FU contract: `docs/fu-evaluation.md` (Phase 6.B design appendix).

## 1. Framing

Phase 10's gate is **closure-driven** (≥80% naturalistic). Phase 11 is
**engineering-driven**: the 10.L / 10.M / 10.N engine extensions
shipped as U-bucket prototypes with no chart consumer, by design. The
chart-layer opt-in is a separate work item per the U-bucket cadence
established by [[project_phase10_l_progress]] / `_m_` / `_n_`.

Phase 11 opens that work item. 11.A's job is to **identify** the
candidates and prioritize them — no chart-rule rewrites here. 11.B+
implements per the priorities below.

The gating discipline carried forward from prior phases:

- Every candidate must articulate either (a) a named workaround it
  removes, or (b) a pinned fixture it unblocks, or (c) a measurable
  maintenance-burden reduction. Speculative consolidation without an
  artifact stays parked under **future ideas** (§4).
- The 10.L / 10.M / 10.N **engine-correctness anchors** (the canonical
  K&Z / Dalrymple fixtures shipped alongside each U-bucket prototype)
  are the regression guards for the chart rewrites. Per
  `docs/fu-evaluation.md`: `test_eq39_topic_equals_comp_xcomp_star_gf_kleene`
  (10.L), `TestFuDefiningDeferredRepass` (10.M),
  `TestInsideOutDesignators` (10.N).
- The audit-corpus regression fixture (Phase 9.Z, PR #120) catches any
  closure regression on the seeded 51-entry sample.

## 2. Audit scope

Six candidate areas surveyed plus a baseline-FU sweep. Four
candidates were named in the plan-of-record; two surfaced during the
10.L/M/N cross-cutting catchall grep; the baseline-FU sweep
(§2.7) was added per a 2026-06-04 review note to ensure the
audit covers the full FU contract, not just the new 10.L/M/N forms:

| ID | Candidate area | Form | Source |
| --- | --- | --- | --- |
| **A** | `cfg/extraction.py` L47 RC wrap `=c` → `=` swap | 10.M | plan-of-record |
| **B** | `cfg/control.py` 24-rule sarili binding collapse | 10.N | plan-of-record |
| **C** | `TestCrossClausalDeferred` xfail flip | 10.N | plan-of-record |
| **D** | `cfg/coordination.py` `((CONJUNCTS ↑) SUBJ)` | 10.N + engine ext | catchall |
| **E** | `cfg/subordination.py` purposive PRO binding | 10.N | catchall |
| **F** | `cfg/clause.py` `{COMP \| XCOMP}*` body collapse | 10.L | plan-of-record |
| **G** | baseline FU sweep (pre-10 forms) — §2.7 | `F*` / `F+` / `{F\|G}` / off-path | review note |

Sections 2.1-2.6 below give the per-candidate analysis. Section 2.7
captures the baseline FU sweep. Section 3 collates the active
candidates into a prioritized backlog. Section 4 captures the
future-ideas pile.

### 2.1 Candidate A — L47 RC `=c` → `=` swap (extraction.py)

**Form**: 10.M deferred defining-equation re-pass.

**Current shape** at `src/tgllfg/cfg/extraction.py:2555-2568` (S_GAP
wrap) and `:2600-2613` (S_XCOMP wrap):

```python
for case in ("NOM", "GEN", "DAT"):
    np_cat = f"NP[CASE={case}]"
    for link in ("NA", "NG"):
        rules.append(Rule(
            np_cat,
            [np_cat, f"PART[LINK={link}]", "S_XCOMP"],
            [
                "(↑) = ↓1",
                "↓3 ∈ (↑ ADJ)",
                "(↓3 REL-PRO PRED) = (↓1 PRED)",
                "(↓3 REL-PRO CASE) = (↓1 CASE)",
                "(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)",   # constraining
            ],
        ))
```

The workaround rationale is documented inline at
`extraction.py:2527-2540` and matches the Phase 10.M re-pass design
captured in `docs/fu-evaluation.md` §5.2.1: pre-10.M, the wrap's
defining-FU equation fired before the S_XCOMP body's
`(↑ SUBJ) = (↑ REL-PRO)` reentrancy was built, so the regex path had
no endpoint and the equation failed with `constraint-failed`. The
workaround uses (a) the body's defining equation to create the
reentrancy and (b) a constraining FU to verify it along an XCOMP*
path. Equivalent K&Z semantics; not the canonical `=` defining form.

**Proposed shape** post-10.M:

```python
"(↓3 REL-PRO) = (↓3 XCOMP* SUBJ)",   # defining, via 10.M re-pass
```

Same on both the S_GAP and S_XCOMP wraps (lines 2566 and 2611).

**Body equation analysis**. The S_GAP body's
`(↑ SUBJ) = (↑ REL-PRO)` defining equation (clause.py around the
S_GAP rule family) and the S_XCOMP body's parallel typed-actor
defining equations (control.py `S_XCOMP` section) do **only one job**:
set up the SUBJ=REL-PRO reentrancy that the wrap's `=c` form
verifies. They are not carrying BAR-SUBJ agreement, voice routing, or
feature percolation — those live on separate equations. With the
swap, the body reentrancy remains (the FU equation establishes the
link between REL-PRO and the deepest SUBJ; the body's local
`(↑ SUBJ) = (↑ REL-PRO)` is still required at each XCOMP depth to
thread the gap). The wrap's role transitions from **verifier** to
**linker**, but the body's role is unchanged.

**Engine-correctness check**.

- **Depth 1 (S_GAP wrap)**. The body's reentrancy fires during the
  same pass-1 c-tree walk that visits the wrap. Whether the body's
  equation has fired by the time the wrap's defining-FU equation
  fires depends on the c-tree visit order; if it has, the FU
  resolves at depth-0 immediately and the queue stays empty; if not,
  the FU returns `fu-no-endpoint`, the equation queues, and the
  re-pass picks it up post-walk. Both paths converge to the same
  result.
- **Depths 2+ (S_XCOMP wrap)**. The wrap fires parent-first, before
  the embedded S_XCOMP body has been walked. The defining-FU is
  guaranteed to queue with `fu-no-endpoint`. The re-pass loop picks
  it up after the full c-tree walk completes (all nested S_XCOMP
  bodies have established their per-depth SUBJ-REL-PRO reentrancies);
  the regex enumerates SUBJ at every level of the chain; K&Z 1989
  §3 minimality selects the depth-0 endpoint; `graph.unify` links
  REL-PRO and SUBJ.

The mechanism is **additive** per `docs/fu-evaluation.md` §5.2.1: FU
bindings that already work under pass-1 order continue to fire at
their original site. The re-pass activates only when an FU binding
genuinely depended on a not-yet-built path.

**Expected rule-count delta**: **0 rules added/removed** — semantic
upgrade only. The 12-rule rule family (3 cases × 2 linkers × 2 wrap
variants) stays at 12 rules; only the FU operator changes.

**Expected behavioral delta**: **simplification only, no audit-corpus
closures**. The pre-10.M and post-10.M forms produce semantically
equivalent f-structures per `docs/fu-evaluation.md` §5.2.1. The win
is the canonical K&Z form — easier to read against the K&Z 1989 §3
text, easier to extend (e.g., adding a body-side off-path constraint
on each XCOMP node), and one less inline comment block explaining a
workaround.

**Regression risk**: **low**. Test coverage is comprehensive — the
LDD-relativization test family covers depths 1 through 4 across
NOM/GEN/DAT cases and both linkers (NA/NG). The 10.M re-pass mechanism
is itself covered by `TestFuDefiningDeferredRepass` (7 cases in
`tests/tgllfg/test_fu_evaluation.py`). Spike-probe step before
committing: parse the 4 canonical depth-{1,2,3,4} fixtures and
verify the f-structure is identical to the pre-swap baseline.

**Priority**: **P0 — clear win, low risk**.

**Phase 11.B.1 shipping outcome (2026-06-04)**. The initial
full-pair swap (both wraps) failed `test-both` with **3 regressions**,
all OBJ-AGENT-relativization rejection cases (e.g., `Tumakbo ang
batang kinain ang isda.` from `test_relativization_ay_phase4.py`
and `test_coverage_phase4.py` sent-566 / sent-567). Root cause:
the audit's "semantic-equivalent" claim was correct for `S_GAP`
but wrong for `S_XCOMP`. The divergence is body-overload:

- **All `S_GAP` body variants** (AV / OV-NVOL / OV-AV_ABSOL / IV /
  DAT-PRON-actor — `cfg/extraction.py:52-220`) bind
  `(↑ SUBJ) = (↑ REL-PRO)`. The wrap's FU equation is vacuous at
  depth 1, and `=` / `=c` produce identical f-structures.
- **`S_XCOMP` non-AV body rules** (`cfg/control.py:94-235`) bind
  `(↑ OBJ-AGENT) = (↑ REL-PRO)` (or `OBJ-CAUSER` for pa-OV / pa-DV)
  — *not* `SUBJ`. The body's local `SUBJ` is the overt NOM pivot
  (e.g., `ang isda` in `kinain ang isda`), distinct from `REL-PRO`.

The wrap's `=c (↓3 XCOMP* SUBJ)` was implicitly enforcing
**Kroeger 1993 SUBJ-only relativization** — depth-0 `SUBJ ≢ REL-PRO`
under non-AV bodies, so the constraint failed and the parse was
rejected. Switching to defining `=` *creates* the binding via
atom-compatible unification (`PRED='NOUN(↑ FORM)'`, `CASE='NOM'`
both match), silently letting OBJ-AGENT-relativization through and
producing an f-structure where `SUBJ ≡ OBJ-AGENT ≡ REL-PRO ≡ pivot`
(not head).

Linguistic status: the unconstrained `=` IS the correct K&Z 1989 §3
eq. 39 form for Tagalog SUBJ-only relativization. The unsoundness is
*structural* — `S_XCOMP` is overloaded as both control-complement
body (legitimate non-AV consumer) and RC body (illegitimate non-AV
consumer). The `=c` form accidentally compensated for the overload;
it didn't fix Tagalog.

**Resolution — gap-category feat split (Option 3, 2026-06-04
per user direction).** The SUBJ-only restriction is encoded at the
c-structure level via a new `SUBJ_GAP=true` binary feat (added to
`BINARY_FEATS` in `core/feats.py`):

- The 15 SUBJ-gap S_XCOMP rules (4 AV plain at `control.py:50-83`,
  8 nested PSYCH / INTRANS / MODAL / TRANS at `:251-322`, and 3
  raising at `:358-380`) carry the LHS `S_XCOMP[SUBJ_GAP=true]`.
- The 10 non-AV S_XCOMP rules (`control.py:94-235`) keep the bare
  `S_XCOMP` LHS.
- The L47 RC S_XCOMP wrap (`extraction.py:2611`) consumes
  `S_XCOMP[SUBJ_GAP=true]` and uses the canonical K&Z defining
  `=` form.
- All other S_XCOMP consumers (control wraps, NEG passthrough,
  coord rules, BE-N equational) continue to consume bare
  `S_XCOMP` — bare-daughter match semantics admits both feat
  variants per `cfg/compile.py:matches`.

No passthrough rule needed. The feat propagates via the standard
chart-feat mechanism. Total chart-side change: 15 rule LHSs gain
the feat, 1 wrap daughter spec narrowed, 1 BINARY_FEATS entry.

**Shipped scope of 11.B.1**: full closure of Candidate A (both
wraps migrated to defining `=`).

- **S_GAP wrap** (`extraction.py:2566`): swap `=c` → `=`. Six
  rules. Semantic-equivalent for S_GAP (all bodies bind
  `SUBJ = REL-PRO`); the FU equation is vacuous at depth 1.
- **S_XCOMP wrap** (`extraction.py:2611`): swap `=c` → `=` AND
  narrow daughter to `S_XCOMP[SUBJ_GAP=true]`. Six rules.

**Audit-corpus delta**: +13 closures across waves (wave-1 +2,
wave-2 rg-intermediate +3, wave-3 conversational +1, wave-3 so1972
+1, wave-4 +3, wave-5 +3); 0 regressions across all 9 waves
(8 source corpora + unattributed-constructions). The closures are
indirect — the canonical K&Z defining form admits a few legitimate
SUBJ-gap RC bodies that the `=c` form rejected via narrow path
matching. Sub-PR ≈ engineering-driven win.

**Sub-PR shape (11.B.1 as shipped)**: 3 commits.

- Commit 1: swap `=c` → `=` on the S_GAP wrap (`extraction.py:2566`),
  add `SUBJ_GAP=true` LHS feat to the 15 SUBJ-gap S_XCOMP rules
  (`control.py:50-83`, `:251-322`, `:358-380`), narrow L47 S_XCOMP
  wrap daughter to `S_XCOMP[SUBJ_GAP=true]` and swap its `=c` → `=`
  (`extraction.py:2611`), register `SUBJ_GAP` in `core/feats.py`,
  and update inline comment blocks. Also bump the BINARY_FEATS
  count in `tests/tgllfg/test_phase5n_c4_feats_audit.py`.
- Commit 2: update `docs/fu-evaluation.md` §5.2.1 to cite the
  L47 swap as the first concrete chart consumer of the re-pass
  mechanism. Update `docs/analysis-choices.md` "Phase 6.D
  Commit 2" / "Implementation note: constraining-form
  realization" with the Phase 11.B.1 post-script. Update
  `docs/feats-binary-audit.md` with the new SUBJ_GAP entry and
  count (74→75).
- Commit 3: update this audit doc §2.1 with the shipping
  outcome and the gap-category feat split decision; update
  `.claude/plans/tgllfg-phase-11.md` §3.1 / §3.8 ledger.

**Five paths surveyed for the S_XCOMP migration** (only Option 3
was implemented; the others are documented for future reference):

1. **LEMMA discriminator on the wrap** (~3-line change, but with
   silent-rejection risk on legitimate non-AV cross-clausal RCs;
   would need a designed test set first). Add
   `(↓3 REL-PRO LEMMA) = (↓1 LEMMA)` so the body's overt
   SUBJ-NP clashes with the head-derived REL-PRO LEMMA.
2. **Off-path voice gate on the FU regex** (depth ≥ 2 only;
   doesn't help depth-1 cases). Use Phase 6.C off-path:
   `(↓3 REL-PRO) = (↓3 XCOMP*<(→ VOICE) =c 'AV'> SUBJ)`.
3. **Gap-category feat split** — add `SUBJ_GAP=true` LHS feat
   to SUBJ-gap S_XCOMP rules; L47 wrap consumes
   `S_XCOMP[SUBJ_GAP=true]`. Architecturally cleanest;
   small refactor (15 LHS feats + 1 wrap daughter spec).
   The defining `=` becomes safe by construction.
   **Chosen and shipped (2026-06-04).**
4. **New parallel category** (`S_RC_SUBJGAP`) consumed only by
   L47. Cleaner separation but rule duplication; no payoff
   over option 3.
5. **Engine extension — defining-FU with provenance tracking**.
   Extend the FU resolver to track which defining equation
   produced each endpoint and reject defining-FU bindings whose
   endpoint provenance contradicts the binding direction.
   Multi-PR engine work; not needed once option 3 lifted the
   pressure but remains a clean architectural alternative if
   future constructions need provenance-gated binding without a
   gap-category split.

### 2.2 Candidate B — Sarili binding 24-rule collapse (control.py)

**Form**: 10.N inside-out designators.

**Current shape** at `src/tgllfg/cfg/control.py:1110-1158`. The
binding-rule block uses a double loop over the 6-entry
`voice_specs` table (defined at `:1021-1032`) crossed with 2
binding-directions × 2 NP-orders = **24 rules**:

```python
voice_specs = [
    ("AV", "OBJ", []),
    ("OV", "OBJ-AGENT", [("CAUS", "NONE")]),
    ("OV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
    ("DV", "OBJ-AGENT", [("CAUS", "NONE")]),
    ("DV", "OBJ-CAUSER", [("CAUS", "DIRECT")]),
    ("IV", "OBJ-AGENT", []),
]
for voice, obj_target, extras in voice_specs:
    # ... 4 rule variants per voice_spec ...
    # sarili at SUBJ → binds to obj_target (2 NP-orders)
    rules.append(Rule("S", [v_cat, "NP[CASE=NOM]", "NP[CASE=GEN]"],
        _eqs("(↑ SUBJ) = ↓2", f"(↑ {obj_target}) = ↓3",
             "(↑ SUBJ LEMMA) =c 'sarili'",
             f"(↑ SUBJ ANTECEDENT) = (↑ {obj_target}))")))
    # ... + 3 more variants (GEN-NOM order; sarili-at-obj_target × 2) ...
```

**Underlying pattern**. Every one of the 24 rules expresses
exactly **one** binding shape, varying only in which GF slot
carries sarili and which carries the binder:

```text
(↑ <reflexive_slot> LEMMA) =c 'sarili'
(↑ <reflexive_slot> ANTECEDENT) = (↑ <binder_slot>)
```

where `<reflexive_slot>` ∈ {SUBJ, OBJ, OBJ-AGENT, OBJ-CAUSER} and
`<binder_slot>` is the complementary actor position (per Kroeger
1993 §2.3 — the binder is the actor, not the pivot). The variation
across the 24 rules is entirely **mechanical**: voice → obj_target
mapping, NP-order surface variant, sarili-position vs binder-position.

**Inside-out collapse candidate**. The 10.N inside-out form lets the
binding equation reference the binder *via* the reflexive's own
position in the f-structure, rather than via a position-specific
equation on a position-specific rule:

```text
(↑ <self> ANTECEDENT) = ((<self> ↑) <actor_role>)
```

where `(<self> ↑)` resolves to the f-structure that has the
reflexive's f-structure as its `<self>` feat — i.e., the matrix
f-structure. This collapses the position dimension but **does not
directly collapse the voice dimension**: the actor role
(`OBJ` for AV vs `OBJ-AGENT` for OV/DV plain vs `OBJ-CAUSER` for
pa-OV/pa-DV) is still voice-dependent.

A realistic collapse target is **~6 template rules** (one per
voice_spec, holding both sarili-at-SUBJ and sarili-at-actor as a
single rule each via alternation on the LEMMA gate) **× 2 NP-orders =
~12 rules**. A more aggressive collapse using LMT-style actor-feat
unification could reach **~6 rules** total, but that's a larger
redesign and out of scope for an audit-driven opt-in.

**Expected rule-count delta**: **~24 → ~12** (realistic, single-PR
scope) or **~24 → ~6** (aggressive, multi-PR). The realistic target
is a 2× reduction; the aggressive target is a 4× reduction. The
aggressive collapse depends on the §B.2 cyclic-endpoint pruning
engine extension (see `tgllfg-out-of-scope.md` §18.1.3): with
pruning, `{SUBJ | obj_target}` alternation in the binder slot
becomes feasible and the two binding-directions collapse into
a single rule.

**Expected behavioral delta**: **simplification + 1 closure (the
xfail flip in Candidate C)**. The realistic 24→12 collapse is
simplification only; the aggressive 24→6 collapse may surface latent
binding cases (e.g., DV-causative with sarili at OBJ-CAUSER, which
has no test today).

**Test coverage and regression risk**. Test coverage is **incomplete**
per the audit:

- `tests/tgllfg/test_phase5m_reflexive_sarili.py` exercises
  AV-SUBJ-sarili (5 cases), AV-OBJ-sarili (3 cases), OV-SUBJ-sarili
  (3 cases). **3 of 6 voice_specs are pinned** (AV, OV-plain).
- OV-causative, DV-plain, DV-causative, IV — **0 tests**.
- Silent regression is possible on the untested voice variants.

**Mitigation**: before any rewrite, expand test coverage to all 6
voice_specs (a one-commit prereq). Property tests using the K&Z
1989 §3 minimality anchor and `TestInsideOutDesignators` as engine
correctness reference.

**Regression risk**: **medium** — load-bearing for 3 voices, silent
gaps on the other 3. Mitigated by the prereq test-coverage commit.

**Priority**: **P1 — medium-effort consolidation; prereq test sweep
required**.

**Sub-PR shape (probable 11.B.2; bundles Candidate C)**: 4-6 commits.

- Commit 1 (prereq): test-coverage expansion. Add fixtures for
  OV-causative, DV-plain, DV-causative, IV sarili binding. Goal: 6 of
  6 voice_specs pinned.
- Commit 2: spike-probe the realistic 24→12 collapse against the
  expanded test base. Document the rule generator change.
- Commit 3: implement the collapse on a feature branch; run
  audit-corpus regression (Phase 9.Z fixture). Verify no closure
  delta.
- Commit 4: bundle Candidate C (TestCrossClausalDeferred flip) by
  adding the inside-out binding equation to the relevant S_XCOMP
  rules (see §2.3 below).
- Commit 5-6: docs (`docs/fu-evaluation.md` §7.4.1 update; new
  callout about chart consumer #1); cross-references.

**Phase 11.B.2 shipping outcome (2026-06-04)**. Shipped as a
**24→4 collapse** via **NP-layer 10.N inside-out**, not as the
audit-proposed matrix-rule 24→12 alternation collapse. Two blockers
surfaced during the spike that made the audit's matrix-rule
mechanism infeasible without engine work:

1. **LHS regex on `=c` is silently deferred.** `unify.py:684`
   dispatches only RHS regex through `resolve_regex_for_read`; the
   LHS path goes through `_resolve_for_read` → `_path_features`,
   which emits a `"deferred"` diagnostic for any regex element
   (alternation, Kleene). `docs/fu-evaluation.md` §8.1 promised
   "If LHS or RHS contains regex, route through
   `_resolve_regex_for_read`" but the LHS dispatch never landed
   (§5.1 design says LHS is "no regex; today's lookup_path path",
   matching the actual implementation). Probe:
   `(↑ {SUBJ | OBJ-AGENT} LEMMA) =c 'sarili'` evaluates as
   vacuously-true (constraint silently ignored).
2. **Dual unconditional bindings between sibling GFs trigger
   occurs-check cycles.** Even with the LHS-regex extension,
   emitting both `(↑ SUBJ ANTECEDENT) = (↑ OBJ)` AND
   `(↑ OBJ ANTECEDENT) = (↑ SUBJ)` from a single rule clashes
   with the atomic-unify occurs-check (the 2-cycle through
   ANTECEDENT edges is detected and rejected). Verified
   independently of the gate.

The audit's matrix-rule mechanism required either an engine
extension (LHS-regex `=c` dispatch) plus a conditional-equation
language feature tgllfg does not have (off-path-on-binding-equation
silent-skip semantics). Both are out of scope for an audit-driven
opt-in. Instead, the shipped mechanism uses ONLY shipped engine
forms (10.N inside-out + 6.B outside-in alternation).

**Mechanism (as shipped).** Move binding from 24 matrix rules to
**4 NP-layer rules** parallel to the canonical NP-possessor rule
at `cfg/nominal.py:1216`. Tagalog reflexives always carry a
possessor pronoun (`sarili niya`, etc.) per Schachter & Otanes
1972 §3.5, so the POSS rule is the c-structure path through which
every sarili NP composes. The 4 sarili-aware variants:

```python
# NOM-sarili at SUBJ (depth-1 alternation picks the existing actor
# slot per voice — AV→OBJ, OV-plain/DV-plain/IV→OBJ-AGENT,
# OV-CAUS/DV-CAUS→OBJ-CAUSER):
rules.append(Rule(
    "NP[CASE=NOM]",
    ["NP[CASE=NOM]", "NP[CASE=GEN]"],
    [
        "(↑) = ↓1", "(↑ POSS) = ↓2",
        "¬ (↑ POSS-EXTRACTED)", "¬ (↓2 MEASURE)",
        "(↑ LEMMA) =c 'sarili'",
        "(↑ ANTECEDENT) = ((SUBJ ↑) {OBJ | OBJ-AGENT | OBJ-CAUSER})",
    ],
))
# GEN-sarili: 3 variants per possible matrix-consumer feat
# (InsideOut AST holds a single feat name in the shipped engine).
for feat in ("OBJ", "OBJ-AGENT", "OBJ-CAUSER"):
    rules.append(Rule(
        "NP[CASE=GEN]",
        ["NP[CASE=GEN]", "NP[CASE=GEN]"],
        [
            "(↑) = ↓1", "(↑ POSS) = ↓2",
            "¬ (↑ POSS-EXTRACTED)", "¬ (↓2 MEASURE)",
            "(↑ LEMMA) =c 'sarili'",
            f"(↑ ANTECEDENT) = (({feat} ↑) SUBJ)",
        ],
    ))
```

The 24 matrix rules in `cfg/control.py:1097-1186` are removed
(only the 12 non-binding matrix transitive rules remain, handling
the matrix GF assignments unchanged). The binding now fires at
the reflexive NP's own f-structure via inside-out ANTECEDENT
binding — the canonical Dalrymple 2001 §14-15 reflexive idiom.

**Wrap-pattern dead-end**. The initial spike attempted a generic
`NP[CASE=X] → NP[CASE=X]` wrap with `¬ (↑ ANTECEDENT)` re-wrap
guard. Earley per-edge dedup prevented chart-level re-firing, but
`_iter_cnodes` forest enumeration recursed infinitely on the
NP→NP loop (`RecursionError`). The POSS-rule-parallel design
(daughter pattern is NP+NP, not NP) avoids the cycle by being
c-structurally distinct from its own LHS.

**Rule-count delta (as shipped)**: -20 (24 matrix rules removed;
4 NP-layer rules added). The audit's projected ~24→~12 became
**~24→~4** because moving to the NP layer collapses BOTH the
position dimension AND the NP-order dimension (NP rules don't
depend on the matrix's NP order — the POSS-rule composition is
order-independent). The aggressive 24→6 collapse path (audit
§B.2 cyclic-endpoint pruning, scheduled as 11.B.5) is now moot —
the realistic delivery exceeds it.

**Behavioral delta**: simplification + **closes Candidate C as a
side effect** (see §2.3 below). The NP-layer mechanism's
`((OBJ ↑) SUBJ)` inside-out at an embedded sarili NP finds the
XCOMP f-structure; under functional control, XCOMP.SUBJ is
structure-shared with matrix.SUBJ, so the binding resolves to
the matrix actor unambiguously. Cross-clausal sarili (e.g.,
`Gusto kong kumain ng sarili ko.`) productively binds without
any S_XCOMP-specific rule.

**Audit corpus**: no closure delta in either direction (the
matrix-rule and NP-layer mechanisms produce semantically
equivalent f-structures for sarili-containing audit-corpus
sentences). The test-coverage prereq (commit 1; 8 new cases
across the 4 previously-untested voice_specs) verifies the
collapse preserves all 24 binding paths.

**Sub-PR shape (as shipped)**: 2 commits, not the 4-6 originally
planned. The architectural simplification of NP-layer over
matrix-layer compressed the work:

- **Commit 1** (chart + tests): `cfg/nominal.py` adds 4 sarili
  NP rules; `cfg/control.py` removes the 24 matrix rules and
  the comment block (≈100 LOC); `tests/tgllfg/test_phase5m_reflexive_sarili.py`
  adds `TestSariliBindingAllVoiceSpecs` (the 8-case voice-coverage
  prereq) and flips `TestCrossClausalDeferred` →
  `TestCrossClausalProductive` (the side-effect closure of
  Candidate C).
- **Commit 2** (docs): this §2.2 outcome + §2.3 closure note +
  `docs/fu-evaluation.md` §7.4.1 first-chart-consumer update +
  `docs/analysis-choices.md` Phase 6.F architectural note +
  `.claude/plans/tgllfg-phase-11.md` §3.2 and §3.8.

**Test gates**: `hatch run test-both` 10115/10115 in 174.89s
(was 10107 pre-11.B.2; +8 voice-coverage cases, 0 regressions,
+0 net from the flipped test).

### 2.3 Candidate C — TestCrossClausalDeferred xfail flip

**Form**: 10.N inside-out designators.

**Current shape** at
`tests/tgllfg/test_phase5m_reflexive_sarili.py:239-276`. The test
class `TestCrossClausalDeferred` pins the deferral:

```python
class TestCrossClausalDeferred:
    """**Deferred (Phase 7+ / corpus pressure).** Cross-clausal
    binding — where ``sarili`` is inside an XCOMP body and the
    binder is at the matrix level — is not handled by the Phase 6.F
    matrix-rule binding equations. ..."""

    def test_cross_clausal_no_binding_today(self) -> None:
        parses = parse_text("Gusto kong kumain ng sarili ko.")
        assert parses, "cross-clausal surface should parse"
        bound = []
        for _, fs, _, _ in parses:
            xcomp = fs.feats.get("XCOMP")
            if isinstance(xcomp, FStructure):
                obj = xcomp.feats.get("OBJ")
                if isinstance(obj, FStructure) and obj.feats.get("ANTECEDENT"):
                    bound.append(fs)
        assert not bound, (
            "cross-clausal binding now fires — flip this test "
            "and remove the TestCrossClausalDeferred docstring deferral"
        )
```

The test asserts the **absence** of binding on the embedded sarili;
the failure message says "flip this test" — i.e., when cross-clausal
binding starts firing, the assertion inversion is the closure stamp.

**Required chart change**. The binding equation needs to live on the
**S_XCOMP rule** (the embedded clause), using the 10.N inside-out
form to reach back through the matrix:

```text
(↑ OBJ LEMMA) =c 'sarili'
(↑ OBJ ANTECEDENT) = ((SUBJ ↑) SUBJ)
```

The `(SUBJ ↑)` segment resolves to "the f-structure that has my
own f-structure as its SUBJ" — i.e., the matrix f-structure under
functional control. The outer `SUBJ` selects the matrix SUBJ. Per
`docs/fu-evaluation.md` §7.4.1, `FGraph.parents_via` returns all
parents; the resolver picks the first in deterministic insertion
order. Under XCOMP functional control, the matrix and embedded SUBJs
are structure-shared — the inside-out resolves to the matrix
unambiguously.

**Ambiguity analysis**. Per the §7.4.1 multiple-parent caveat: when
the inner target is structure-shared, `parents_via` returns multiple
parents. For cross-clausal sarili under XCOMP control:

- The embedded f-structure's SUBJ is shared with the matrix SUBJ
  (control threading).
- `parents_via(target=<embedded_f>, feat=SUBJ)` returns f-structures
  that have `<embedded_f>` as their SUBJ. Only the matrix f-structure
  matches. **One parent. No ambiguity.**

Different from the SUBJ structure-sharing concern: there, the SUBJ
node is shared; here, we're asking for the parent that has
`<embedded_f>` (the whole embedded clause) as a feat — which is
only the matrix.

**Expected behavioral delta**: **+1 xfail flip**. Productively closes
cross-clausal sarili across the audit corpus (currently 0
attestations in audit-corpus wave 1-5; future waves may surface).

**Regression risk**: **low** if scoped to AV-control cases initially.
The S_XCOMP rule changes are gated on the LEMMA constraining equation
(only fires when the inner NP head is `sarili`). Non-sarili XCOMP
sentences are unaffected.

**Priority**: **P1 — bundle with Candidate B**. The candidate uses
the same 10.N inside-out form and touches the same control.py rule
set. Bundling keeps the 11.B.2 sub-PR coherent.

**Sub-PR shape**: bundled into 11.B.2 above (Candidate B Commit 4).

**Alternative path (parked)**. Per `tgllfg-out-of-scope.md`
§18.1.3 line 62, a parallel approach to cross-clausal sarili is
**per-XCOMP binding rules** lifted to the embedded S_XCOMP body
with constraining traversals back to the matrix. This was the
pre-10.N option; it is voluminous (mirrors the matrix transitive
loop into the embedded body) and would not collapse via FU. The
10.N inside-out approach via `((SUBJ ↑) SUBJ)` is preferred for
this candidate because the engine extension is already shipped
and the chart-side cost is small. The per-XCOMP alternative
remains parked as a fallback if the inside-out approach surfaces
unexpected ambiguity.

**Phase 11.B.2 shipping outcome (2026-06-04)**. Closed **as a
side effect** of the §2.2 Candidate B NP-layer collapse, not
via the planned S_XCOMP-rule change. The 4 NP-layer sarili
rules use `((<feat> ↑) SUBJ)` for GEN-sarili variants and
`((SUBJ ↑) {OBJ | OBJ-AGENT | OBJ-CAUSER})` for the NOM
variant. When the sarili NP is embedded inside an XCOMP body
(e.g., `Gusto kong kumain ng sarili ko.` — the embedded
`ng sarili ko` is the XCOMP's OBJ), the GEN-OBJ variant fires
with `((OBJ ↑) SUBJ)`:

- `(OBJ ↑)` finds the f-structure F such that F.OBJ = sarili
  NP. F is the embedded XCOMP (`kumain ng sarili ko`).
- F.SUBJ — XCOMP's SUBJ. Under functional control (matrix
  PSYCH-control sets `(↑ XCOMP SUBJ) = (↑ SUBJ)`), the
  embedded SUBJ is structure-shared with the matrix SUBJ.
  So XCOMP.SUBJ ≡ matrix.SUBJ ≡ the GEN-PRON `ko` (the
  matrix actor).
- Binding writes `↑.ANTECEDENT = matrix.SUBJ` — exactly the
  desired cross-clausal binding.

The Phase 6.F matrix-rule mechanism only fired on standalone
clauses (the matrix rule literally didn't see the embedded
sarili). The NP-layer mechanism makes this work transparently:
the binding equation lives at the reflexive NP's own
c-structure, so it fires regardless of how deeply the NP is
embedded, as long as the inside-out designator can find the
appropriate parent.

**Test transition**: `TestCrossClausalDeferred` (pre-11.B.2:
asserts no binding fires) → `TestCrossClausalProductive`
(post-11.B.2: asserts binding fires and is reentrant with the
matrix SUBJ). No S_XCOMP-specific rule changes were needed —
the audit's planned binding equation `(↑ OBJ ANTECEDENT) =
((SUBJ ↑) SUBJ)` on the embedded S_XCOMP rule is replaced by
the §2.2 GEN-OBJ NP-layer rule which produces the same
f-structure with broader applicability (not S_XCOMP-specific —
any embedded sarili-OBJ position).

### 2.4 Candidate D — Coordination CONJUNCTS inside-out (coordination.py)

**Form**: 10.N inside-out designators **+ engine extension to
`parents_via` for set-valued features**.

**Scope (revised 2026-06-04)**: the §A rule-by-rule audit of
`coordination.py` (53 rules) found **4 rule families** with explicit
per-conjunct cross-binding fan-outs that would collapse via this
form, not just the single `S_XCOMP_BARE_COORD` case originally
flagged in the source comment. The original self-flag (at lines
382-390) calls out the SUBJ-sharing variant; the broader set is:

| Coord rule | Fan-out | File:line |
| --- | --- | --- |
| `S_XCOMP` binary REL-PRO chain | `(↑ REL-PRO) = ↓1 REL-PRO` + `(↑ REL-PRO) = ↓3 REL-PRO` | `coordination.py:302-317` |
| `S_XCOMP` 3-conjunct REL-PRO chain | + `(↑ REL-PRO) = ↓5 REL-PRO` | `coordination.py:319-338` |
| `S_XCOMP_BARE_COORD` binary (REL-PRO + SUBJ) | `(↑ REL-PRO) = ↓N REL-PRO` AND `(↑ SUBJ) = ↓N SUBJ` for N=1,3 | `coordination.py:464-481` |
| `S_XCOMP_BARE_COORD` 3-conjunct | same, N=1,3,5 | `coordination.py:483-505` |

All four collapse via body-level equations on the underlying
`S_XCOMP` / `S_XCOMP_BARE` rule:

```text
(↑ REL-PRO) = ((CONJUNCTS ↑) REL-PRO)
(↑ SUBJ)    = ((CONJUNCTS ↑) SUBJ)
```

These are placed on the conjunct body (S_XCOMP / S_XCOMP_BARE),
not on the coord rule. The coord rule reduces to set-membership
declarations + `(↑ COORD) = '...'` overlay.

The original self-flag in the source comment:

```python
# **FU/Kleene consideration** (10.L–10.N U-bucket extensions):
# An attractive alternative per-conjunct equation would be the
# inside-out designator ``(↑ SUBJ) = ((CONJUNCTS ↑) SUBJ)`` — each
# conjunct independently asks "what is the SUBJ of the parent
# whose CONJUNCTS contains me?". This requires
# :meth:`FGraph.parents_via` to handle set-valued features
# (current impl is direct-edge only). Flagged as candidate for
# Phase 11.A audit / consumer-opt-in; the explicit equations
# below are pragmatic and well-understood.
```

**Engine blocker**. Per `src/tgllfg/fstruct/graph.py:698-739`,
`FGraph.parents_via` iterates `self._store.items()`, filters
`isinstance(v, ComplexValue)`, then reads `v.attrs.get(feat)` — i.e.,
it scans **direct-edge** `ComplexValue.attrs` only. `SetValue` parents
(where the target appears as a member of a set-valued feat like
`CONJUNCTS`) are not scanned.

A set-valued extension is straightforward:

```python
for n, v in self._store.items():
    if isinstance(v, ComplexValue):
        # ... existing direct-edge scan ...
    elif isinstance(v, SetValue):
        # NEW: if target is a member, n's parents (whose attrs
        # point at n) need to be enumerated. But SetValues don't
        # have attrs themselves — what we want is to find any
        # ComplexValue parent whose attrs[feat] = this SetValue
        # AND whose SetValue contains target.
        ...
```

The semantics need careful design — `(<self> ↑)` over a set-valued
feat means "the parent whose `<self>` set contains me", which is
disjunctive when multiple parents have the same set member. K&Z 1989
§3 minimality doesn't directly apply (sets aren't ordered).

**Current workaround quality**. The explicit per-conjunct equation
`(↑ SUBJ) = ↓N SUBJ` is **fully equivalent and clearer**. The
inside-out form is a syntactic preference, not a semantic gain.

**Expected behavioral delta**: **0** — explicit equations and the
inside-out form produce the same f-structure.

**Expected rule-count delta**: **small simplification** — bare-V
coord rules currently chain 2-3 per-conjunct equations; the
inside-out form would replace those with a single body equation per
S_XCOMP_BARE rule.

**Priority**: **P2 — engine extension required, value is low**.

The engine extension is well-defined but not trivial (set-valued
semantics, minimality unclear). The chart-side value is
simplification only. Defer until either (a) a different candidate
also needs the set-valued `parents_via` extension, or (b) the
coordination rules grow enough that the per-conjunct equation
maintenance burden becomes meaningful.

**Sub-PR shape (probable 11.B.4, deferred)**: 2 sub-PRs.

- 11.B.4.eng: engine extension to `parents_via` for set-valued
  features; new test class `TestParentsViaSetValued`; canonical
  Dalrymple 2001 §14 set-valued binding fixture.
- 11.B.4.chart: chart opt-in on the bare-V coord rules.

### 2.5 Candidate E — Purposive PRO placeholder (subordination.py)

**Form**: 10.N inside-out designators.

**Source**: `src/tgllfg/cfg/subordination.py:446-450` carries an
explicit self-flag in a comment:

```python
# LFG analysis: the SubordClause f-structure has the bare V's
# PRED and a synthesized ``SUBJ PRED = 'PRO'`` placeholder. The
# control relation between matrix and purposive SUBJ is
# established at the f-graph by future inside-out designators
# (Phase 7+); for now the PRO is a discourse-bound placeholder.
```

**Current shape** at `subordination.py:458-470`:

```python
for mood in ("SOC", "NVOL"):
    rules.append(Rule(
        "SubordClause",
        ["PART[COMP_TYPE=PURP]", f"V[VOICE=AV, MOOD={mood}, TR=INTR]"],
        [
            "(↑) = ↓2",
            "(↑ SUBJ PRED) = 'PRO'",        # discourse-bound placeholder
            "(↑ SUBORD_TYPE) = 'PURP'",
            "(↓1 COMP_TYPE) =c 'PURP'",
        ],
    ))
```

The purposive `para` / `upang` PART takes a bare AV verb whose SUBJ
is controlled by the matrix SUBJ ("Kumain ako para makatapos." → the
unexpressed SUBJ of `makatapos` is the matrix `ako`). Today's
placeholder synthesizes a `SUBJ PRED = 'PRO'` slot but doesn't link
it to the matrix.

**Proposed shape** post-10.N:

```python
"(↑ SUBJ) = ((ADJ ↑) SUBJ)",   # inside-out: matrix-as-parent-via-ADJ
```

The `(ADJ ↑)` segment asks for the parent whose `ADJ` feat contains
the SubordClause f-structure. SubordClauses are attached as ADJ
members of the matrix (per the canonical Tagalog adverbial-purposive
analysis); the inside-out resolves to the matrix.

**Set-valued caveat**. `ADJ` is set-valued (multiple adjuncts per
clause), so this candidate **also needs the set-valued `parents_via`
extension** from §2.4. The two candidates share the engine prereq.

**R&B 1986 §6.6 semantic check**. The matrix-as-binder pattern is
canonical for purposive `para` / `upang` per R&B 1986 §6.6. The
control reading ("I ate so that I could finish") is preferred over
the discourse reading ("I ate so that someone could finish"). The
inside-out binding is semantically correct.

**Expected behavioral delta**: **simplification + correctness**. The
PRO placeholder is currently inert (it doesn't surface in the
f-structure in a useful way); the inside-out binding makes the
control relation explicit on the f-graph. May enable downstream
binding into the SubordClause (e.g., reflexive into purposive body,
analogous to Candidate C).

**Regression risk**: **medium**. The current PRO placeholder is
covered by purposive-clause test fixtures; flipping to inside-out
changes the f-structure shape (SUBJ becomes a real link instead of a
synthesized atom). Tests that check `subord.feats["SUBJ"].feats["PRED"]
== "PRO"` will fail; tests need to be updated to check the binding
instead.

**Priority**: **P1 — clean candidate; depends on 11.B.4.eng**.

Bundle with Candidate D's engine extension. Once `parents_via`
handles set-valued features, both candidates D and E open at once.

**Sub-PR shape (probable 11.B.5, after 11.B.4.eng)**: 2-3 commits.

- Commit 1: implement inside-out binding on the SubordClause
  purposive rules (3 variants per the existing rule family).
- Commit 2: update purposive-clause test fixtures to assert binding
  instead of PRO placeholder.
- Commit 3: docs (`docs/fu-evaluation.md` §7.4.1 update; cross-ref
  this audit doc).

### 2.6 Candidate F — `{COMP | XCOMP}*` body collapse (clause.py)

**Form**: 10.L Kleene-on-alternation.

**Inventory finding**. Across `cfg/*.py`, the audit found:

- `extraction.py:2566` and `:2611` — two `(↓3 XCOMP* SUBJ)` instances
  (single-feat Kleene; pre-10.L baseline).
- `extraction.py:2523` — a comment-only reference to the plan-skeleton
  form `(↑ {COMP, XCOMP}* SUBJ)`, **narrowed to `XCOMP*` in Phase 6.D**.

**Zero existing chart consumers of `{F | G}*`**. No twin rules
(parallel `COMP*` + `XCOMP*` rule pairs that would collapse). No
control predicates that need cross-COMP relativization. The
narrative at `extraction.py:2522-2525` explicitly justifies the
narrowing:

```python
# The broader plan-skeleton form
# ``(↑ {COMP, XCOMP}* SUBJ)`` is narrowed to XCOMP* in 6.D —
# Tagalog COMP-internal SUBJs aren't reachable under the
# SUBJ-only restriction, so widening would overgenerate.
```

This matches the §7.2 corpus-blocked note in `docs/fu-evaluation.md`:
Tagalog SUBJ-prominence + voice-morphology-driven relativization
obviate cross-COMP extraction.

**Speculative future motivators**. The audit identified two
hypothetical Tagalog constructions that *could* surface a need:

- **Reported topicalization**: a TOPIC arg threading through a
  reported-COMP boundary (e.g., `"Sinasabi niya na ang aso ang kumain"`
  with cross-COMP topic). No corpus attestation; structurally
  ambiguous with the canonical indirect-speech reading.
- **Nested reported clauses**: cross-clausal binding across multiple
  COMP layers. No corpus attestation; rare even in
  English-style reported speech.

**Priority**: **P2 — future-ideas; no consumer**.

Demote from the active backlog per the audit-before-scheduling
discipline (memory:
[[feedback_audit_before_scheduling]]). Re-evaluate when wave-2/3/5
corpus work or post-Phase-10 naturalistic harvest surfaces a
construction requiring the broader body.

The 10.L engine extension is **load-bearing as an engine-correctness
anchor**: `test_eq39_topic_equals_comp_xcomp_star_gf_kleene` exercises
the canonical K&Z eq. 39 body and is the regression guard for any
future chart consumer. Phase 10.L was a valid U-bucket prototype even
without a chart consumer.

### 2.7 Candidate G — baseline FU sweep (pre-10 forms)

**Forms**: the four baseline FU primitives shipped in Phase 6.B
and available in chart equations since:

- `F*` / `F+` — single-feat Kleene over a single GF name.
- `{F | G}` — single-step alternation (one feat from a set).
- Off-path constraints — `<(→ FEAT) =c 'X'>` attached to a path
  element; filters the FSA enumeration at each transition.
- FU on RHS of `=c` constraining and `=` binding (with the pre-10.M
  pass-1 ordering caveat the L47 wraps work around).

The known baseline-FU consumer is the L47 RC wrap (Candidate A
above; `(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`). The audit question
for §2.7: are there **other** places where hand-rolled per-depth
equations or other ad-hoc patterns could collapse to a baseline-FU
equation?

**Patterns swept**:

1. **Per-depth XCOMP equations** — hand-rolled cascades along the
   lines of `(↑ XCOMP SUBJ) = X` and `(↑ XCOMP XCOMP SUBJ) = X` and
   `(↑ XCOMP XCOMP XCOMP SUBJ) = X` that would collapse to
   `(↑ XCOMP* SUBJ) = X` via `F*`.
   *grep result*: `\(↑ XCOMP XCOMP` and `\(↑ COMP COMP` — **empty**
   across all `src/tgllfg/cfg/*.py`. No hand-rolled per-depth
   cascades exist; control nesting is handled by **rule recursion**
   (each S_XCOMP rule rewrites to a smaller S_XCOMP), with each
   rule's `(↑ SUBJ) = (↑ XCOMP SUBJ)` and `(↑ SUBJ) = (↑ REL-PRO)`
   establishing the single-step link. The composition produces the
   correct cross-depth structure-sharing without any FU regex.
2. **Per-depth COMP equations** — same shape on the finite-complement
   branch. *grep result*: **empty**. Tagalog's
   SUBJ-only-relativization restriction (Kroeger 1993) makes
   COMP-internal SUBJ access uninteresting; clause.py's KNOW-class
   complement rules pass the COMP as an opaque argument.
3. **Per-depth ADJ-set traversal** — hand-rolled enumerations
   through nested adjunct sets. *grep result*: **empty**. Both
   coordination.py and subordination.py use explicit set membership
   (`↓N ∈ (↑ ADJUNCT)`) and per-conjunct equations, not regex-based
   set traversal. (The coordination CONJUNCTS inside-out form
   discussed in §2.4 is the 10.N candidate, not a baseline-FU
   candidate — it requires reverse-lookup, not forward Kleene.)
4. **Twin rules for `{F | G}` single-step** — pairs of rules
   differing only in one path element along a FU path that could
   collapse to a single `{F | G}` alternation. *grep result*:
   no `{` alternation use in any cfg file. Rule families are
   expanded over voice / case / linker / NP-order via Python
   loops; the variant dimensions are categorical (different rule
   shapes), not single-step FU alternations along a shared path.
5. **Off-path constraints** — places where a traversal is guarded
   by an intermediate-node constraint that today lives outside the
   FU path (as a separate `=c` equation) but would belong inline as
   `<(→ FEAT) =c 'X'>` attached to a path element. *grep result*:
   the off-path syntax `<(→ ...) =c ...>` is documented at
   `docs/fu-evaluation.md` §6 but has **zero chart consumers**. The
   only FU path in the chart (L47 `XCOMP*`) carries no intermediate
   constraint — every level of the control chain shares SUBJ via
   functional control, so a per-level off-path check is redundant.
6. **Multi-rule fan-outs over the same FU shape** — rule families
   where each variant carries its own version of an equation that
   could collapse to a single FU equation. *Inspected*: the
   sarili-binding family (24 rules) is the only large fan-out; its
   collapse is via 10.N inside-out (Candidate B), not baseline FU.

**Other equation-RHS contexts swept** (added per 2026-06-04 review):

The patterns above cover FU on the RHS of `=` defining and `=c`
constraining equations. The equation grammar also permits FU paths
in three other RHS contexts; each was swept:

- **Set-membership RHSes (`↓N ∈ (↑ regex-path)`)**: 275 instances of
  `∈ (↑ ...)` across `cfg/*.py`, all single-segment
  (`(↑ ADJUNCT)`, `(↑ ADJ)`, etc.). Zero FU-bearing paths. (A
  hypothetical use would be `↓N ∈ (↑ XCOMP* ADJUNCT)` — "↓N is
  a member of any ADJUNCT set along the XCOMP chain" — but this
  has zero motivation in the current corpus and would also
  require `F*`-on-set semantics that the engine doesn't yet
  specify.)
- **Bare-existential FU constraints**
  (`(↑ regex-path)` standalone): zero instances. Existential
  constraints in `cfg/` are all single-segment.
- **Off-path constraints (`<(→ FEAT) =c 'X'>` inline)**: zero
  instances anywhere in `src/tgllfg/` — confirmed by re-grep of
  `<(→` syntax. Already in §2.7 patterns #5 above.

**Equation LHS FU**: explicitly out of scope per
`docs/fu-evaluation.md` §5.3 (defining-on-regex on the LHS would
require the unifier to invent intermediate nodes for unbounded
path elements; K&Z 1989 does not entertain this construction;
`_resolve_regex_for_write` is not implemented). No audit needed.

**Verification greps** (also added per 2026-06-04 review):

- `grep -rnE '\(↓[0-9]+ [A-Z][A-Z_-]+\*' src/tgllfg/cfg/` — returns
  the two L47 rule instances at `extraction.py:2566` / `:2611`
  plus 3 documentation-comment references in the same file. No
  other downward FU paths.
- `grep -rnE '\(↑ [A-Z][A-Z_-]+\*' src/tgllfg/cfg/` — empty. Zero
  upward FU paths anywhere.
- `grep -rnE '\(↑ \{[A-Z]' src/tgllfg/cfg/` — one comment-only
  reference to the K&Z plan-skeleton `(↑ {COMP, XCOMP}* SUBJ)` at
  `extraction.py:2523`, narrated as "narrowed to XCOMP* in 6.D".
  No live alternation paths.

**Finding**: **zero baseline-FU candidates beyond the known L47
case**, across **all** equation-RHS contexts permitted by the
equation grammar (`=` / `=c` / `∈` / bare-existential / off-path,
upward / downward, single-feat / alternation / Kleene). The
existing chart-rule corpus uses single-step FU only (the L47
`XCOMP*` instance), no off-path constraints anywhere, no
alternations anywhere. The voice / case / linker / NP-order rule
expansions are categorical and not collapsible to FU.

**Why this matters**:

- It bounds the audit. The Phase 11.B+ backlog (Candidates A through
  E) covers every actionable FU-consumer opportunity surfaced by the
  audit, both for the new 10.L/M/N forms and for the pre-10
  baseline.
- It confirms that **rule-recursion is the canonical idiom for
  control-chain nesting**, not FU-regex enumeration. The L47 wrap
  uses FU because the relativized SUBJ is a single endpoint at an
  *unknown* depth in the chain — FU enumerates and picks the
  shortest. Within the chain itself, per-rule single-step equations
  are the right tool.
- It validates the §6.2 off-path documentation as a future
  feature rather than a live primitive: the syntax exists in the
  AST and FSA, but no chart construction needs it yet.

**Speculative future motivators** (not backlog items):

- A construction requiring `(↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)`
  — an XCOMP-chain SUBJ access filtered by TENSE on each intermediate
  XCOMP. Hypothetical only; no Tagalog attestation.
- Cross-clausal set membership over ADJUNCT (e.g.,
  `↓N ∈ (↑ XCOMP* ADJUNCT)`) — would require `F*`-on-set
  semantics; engine support is unclear.

**Priority**: **none — null finding**. No sub-PR scheduled. The
sweep itself is the deliverable; future audits can re-run the same
greps to verify the assertion still holds.

### 2.8 Candidate H — broader PRO-placeholder sweep (added 2026-06-04)

**Form**: 10.N inside-out designators (subset of candidates only).

**Trigger**: a 2026-06-04 review note pointed out that §2.5
(Candidate E — purposive PRO) covered only one of many PRO-placeholder
sites in `cfg/`. A whole-cfg sweep found **53 instances** of
`= 'PRO'` placeholder equations across `cfg/*.py`:

```text
grep -n "= 'PRO'" src/tgllfg/cfg/*.py | wc -l
→ 53
```

Distribution (by file):

| File | Instances | Notes |
| --- | --- | --- |
| `clause.py` | ~14 | predicative-ADJ tough; standalone modal; modal+OV imperative; ADJ-pred + V-INF tough; existential NEG; HAVE-with-RC; ang-exclamative; etc. |
| `extraction.py` | ~9 | relativization with PRO-filled OBJ-AGENT or REL-PRO; AV-OBJ-drop; tough-RC variants |
| `nominal.py` | 3 | standalone demonstrative pronouns (`iyon` / `iyan` / `nito` as bare NP) |
| `subordination.py` | 1 | purposive `para` / `upang` — Candidate E |
| `control.py` | 3 | standalone modal SUBJ + XCOMP; modal-imper variants |
| `coordination.py` / `discourse.py` / `clitic.py` / `negation.py` | 0 | no PRO placeholders |

(Counts are approximate from the grep; per-instance classification
is part of 11.B.3 prereq work — see below.)

**Three semantic classes** by inspecting representative rules:

**Class 1 — Impersonal PRO** (no antecedent exists).

Examples:

- `control.py:481-482` — standalone modal `Hindi puwede.` ("not
  permitted") with `(↑ SUBJ PRED) = 'PRO'` and `(↑ XCOMP PRED)
  = 'PRO'`. Both arguments are impersonal; nothing to bind to.
- `clause.py:5219` — negative existential `Walang nang kumain.`
  with `(↑ SUBJ PRED) = 'PRO'`. The SUBJ is existentially-negated;
  no antecedent.
- `nominal.py:453 / :458 / :463` — standalone demonstrative
  pronouns `iyon` / `iyan` etc. as bare NP. PRO synthesized for
  completeness; the demonstrative is itself the referring
  expression.
- `clause.py:4498` — MODAL+OV bare imperative; matrix SUBJ is
  impersonal.

**Inside-out applicability**: **none**. No antecedent means no
structural binding to express.

**Class 2 — Anaphoric / discourse-bound PRO** (antecedent exists
in discourse but the chart analysis deliberately avoids structural
binding).

Examples:

- `clause.py:5282-5299` — negative HAVE with V[OV] RC body
  (`Wala siyang kinakausap.` "She has no one to talk to."). The
  inline comment at `:5263-5265` is explicit: "treated as
  discourse-recoverable at the f-structure level rather than via
  direct unification — avoids spurious CASE-conflict on NOM
  possessor vs GEN actor". The PRO is intentionally not
  structurally bound; switching to inside-out would re-introduce
  the CASE-conflict the workaround avoids.
- `clause.py:1514 / :1527 / :1540` — tough-construction generic
  PRO. The V-INF inside `Mahirap kumain ng aso.` has an
  unspecified SUBJ (generic "for anyone to eat dogs"). The DAT
  experiencer (`sa kanya`) is an ADJUNCT, not a controller — the
  current analysis is anaphoric.

**Inside-out applicability**: **case-by-case**. Some Class-2
instances might be promotable to structural binding via inside-out
(if the discourse antecedent IS structurally accessible from the
PRO site), but the current decision to keep them anaphoric is
typically motivated by avoiding feature-clashes or semantic
overreach. Each requires a linguistic-judgment call against the
reference works (R&B 1986, Kroeger 1993, S&O 1972).

**Class 3 — Controlled PRO** (antecedent is structurally accessible
via a chart relationship; inside-out would express the binding
canonically).

Examples:

- `subordination.py:446-450` — purposive `para` / `upang` PRO,
  already captured as Candidate E.
- Possibly some of the tough-RC / extraction-with-PRO-fill cases
  in `extraction.py` if the relativized head is the canonical
  binder. Per-case verification required.

**Inside-out applicability**: **yes — these are the inside-out
candidates**. Each substitutes `(↑ <slot> PRED) = 'PRO'` with
`(↑ <slot>) = ((<containing-feat> ↑) <binder-slot>)`-style
binding.

**Estimated per-class counts** (rough, pre-per-instance audit):

| Class | Estimate | Inside-out candidate? |
| --- | --- | --- |
| Class 1 (impersonal) | ~30-35 | no |
| Class 2 (anaphoric / discourse) | ~10-15 | case-by-case |
| Class 3 (controlled) | ~5-10 (including Candidate E) | yes |

**Expected delta**: in the Class-3 cases, the inside-out form
replaces the PRO placeholder with a real f-structure link. The
parse trees become more accurate (the binder is named on the
f-graph instead of synthesized as a string atom). No audit-corpus
closures expected — these are simplification + correctness moves,
not coverage moves. Some downstream consumers of the SUBJ slot
(e.g., agreement, reflexive binding inside the controlled clause)
may begin to fire correctly where they previously couldn't, which
could produce **incidental closures** worth tracking.

**Regression risk**: **medium**. The PRO placeholder is
load-bearing for completeness (XCOMP-completeness checks
require the SUBJ slot to be filled); replacing it with a binding
must produce an f-structure that still satisfies completeness. The
Class-1 and Class-2 cases must stay as PRO; misclassifying a
Class-2 instance as Class-3 would re-introduce the feature-clashes
the workarounds were designed to avoid.

**Engine prereqs**: depends on which `<containing-feat>` is needed
for each Class-3 instance. The purposive case (E) uses `ADJ`
which is set-valued — needs the same `parents_via` set-valued
extension as Candidate D. Other Class-3 cases might use
direct-edge feats (e.g., `XCOMP`, `OBJ`) which the current
`parents_via` already handles.

**Priority**: **P1 — sequencing under 11.B.3**.

The 11.B.3 sub-PR (currently scoped to Candidate E alone) should
be expanded to cover the full Class-3 subset. Per-instance
classification is the prereq commit; only Class-3 instances are
rewritten.

**Sub-PR shape** (revised 11.B.3): 4-6 commits.

- Commit 1 (prereq): per-instance classification of all 53 PRO
  placeholders into Classes 1, 2, 3. Output: a table in
  `docs/fu-extension-audit.md` (or a dedicated appendix doc).
- Commit 2: depends on 11.B.4.eng (set-valued `parents_via`) for
  Class-3 instances using set-valued containing feats; lands
  after 11.B.4.eng.
- Commit 3: implement inside-out binding for each Class-3
  instance.
- Commit 4: update affected test fixtures (any test asserting
  the PRO-placeholder shape needs to update to the binding shape).
- Commit 5-6: docs + cross-references.

**Anti-goals**:

- Do not flip Class-1 / Class-2 instances to inside-out binding
  unless the per-instance analysis confirms a structural binding
  is correct. The current PRO placeholder is the right idiom for
  impersonal and discourse-anaphoric cases.
- Do not assume all controlled-looking instances are Class 3.
  Some control structures (e.g., MODAL+OV imperative at
  `clause.py:4516-4518`) carry PRO at the matrix SUBJ but
  immediately structure-share with `(↑ XCOMP SUBJ) = (↑ SUBJ)`.
  The PRO is the controller, not the controllee — inside-out
  isn't needed.

## 3. Prioritized backlog

| Sub-PR | Priority | Candidate | Form | Effort | Engine prereq |
| --- | --- | --- | --- | --- | --- |
| **11.B.1** | **P0** | A: L47 `=c` → `=` swap | 10.M re-pass | 2-3 commits | none |
| **11.B.2** | **P1** | B: Sarili 24-rule collapse + C: TestCrossClausalDeferred flip | 10.N inside-out | 4-6 commits | none |
| **11.B.3** | **P1** | E: Purposive PRO binding + H-Class-3 subset | 10.N inside-out | 4-6 commits | 11.B.4.eng |
| **11.B.4** | **P2** | D: Coordination CONJUNCTS inside-out | 10.N + set-valued `parents_via` | 2 sub-PRs (eng + chart) | self |
| **11.B.5** | **P2** | §B.2: Cyclic-endpoint pruning (engine + canonical fixture) | U-bucket prototype | 2-3 commits | none |
| **11.X** | **P2** | §3.5: Bare `Huwag + V[AV]` PRO injection (Phase 10 carry-forward) | PRO machinery design (non-FU) | 2-4 commits | none |
| **11.final** | **P3** | Closure docs + explicit declines (§B.5 set complement, §B.6 defining-on-regex LHS) | docs-only | 1 commit | none |
| (future) | — | F: `{COMP \| XCOMP}*` body | 10.L K-on-A | n/a — no consumer | n/a |

**Scheduling notes**:

- **11.B.1 first**. P0, no engine prereq, no rule-count delta, zero
  closure risk. Validates the 10.M re-pass mechanism as a chart
  consumer and lifts the first named workaround.
- **11.B.2 second**. P1, no engine prereq, ~24→~12 rule collapse
  (realistic) or ~24→~6 (aggressive, gated on 11.B.5 cyclic-endpoint
  pruning). Largest single-PR win on the backlog. Prereq:
  test-coverage expansion to all 6 voice_specs. **Internal
  decision** (out-of-scope §18.1.3 line 62): default to 10.N
  inside-out for cross-clausal sarili; the per-XCOMP binding-rules
  alternative stays as a fallback only if inside-out surfaces
  unexpected ambiguity (unlikely per 10.N validation).
- **11.B.4.eng → 11.B.3 + 11.B.4.chart**. The engine extension
  (set-valued `parents_via`) unblocks both 11.B.3 (purposive PRO
  plus H-Class-3) and 11.B.4.chart (coordination). Engine ships
  first; chart consumers follow.
- **11.B.5**. Engine-only U-bucket prototype matching the 10.L/M/N
  cadence: AST/resolver extension + canonical fixture; no chart
  consumer in the same sub-PR. Enables a follow-on aggressive
  Candidate B 24→~6 collapse (either bundled with 11.B.2 if
  sequenced after 11.B.5, or as a separate 11.B.2.post-1 if
  11.B.2 shipped the realistic collapse first).
- **11.X**. Non-FU carry-forward from `tgllfg-out-of-scope.md`
  §18.1.4 line 77. Bare-V form (`Huwag kumain.`) needs PRO SUBJ
  injection to satisfy completeness; design choice between
  impersonal-PRO and discourse-anchored addressee. Not on the
  FU backlog but on the Phase 11 roadmap.
- **11.final**. Standard closure docs PLUS explicit decline
  decisions for §B.5 (set complement: zero Tagalog need per audit)
  and §B.6 (defining-on-regex LHS: out-of-scope per K&Z, parked
  indefinitely). Migrating both `tgllfg-out-of-scope.md` §18.1.3
  lines 59 + 60 from "parked" to "explicitly declined for v1".
- **Candidate F**: no consumer; stays parked under future ideas.

**Cumulative expected delta**:

- **Rule count**: -12 to -18 chart rules across 11.B.1 through
  11.B.4 (mostly from B's sarili collapse). Aggressive
  collapse (via 11.B.5) adds another -6.
- **Workarounds removed**: 3 named (extraction.py L47 `=c`
  rationale block; subordination.py PRO placeholder;
  control.py sarili equation-side exclusion if 11.B.5 enables
  the aggressive collapse).
- **Closures**: +1 (TestCrossClausalDeferred flip), plus
  incidental closures from H Class-3 inside-out binding (TBD).
  No audit-corpus-targeted closures — the engineering-driven
  discipline decouples from the closure-driven Phase 10 gate.
- **Doc updates**: `docs/fu-evaluation.md` §5.2.1 (first 10.M
  chart consumer), §7.4.1 (first 10.N chart consumers), §11
  (cyclic-endpoint pruning closure); cross-references from
  `docs/analysis-choices.md`.

## 3.5 Phase 11 carry-forward items NOT on the FU audit backlog

Per `.claude/plans/tgllfg-out-of-scope.md` §18.1.4 ("Phase
10-surfaced, carry forward into Phase 11"), three items inherit
into Phase 11 that are **adjacent to but not direct candidates
for** the FU-extension consumer audit. Each is scheduled
explicitly:

- **Bare `Huwag + V[VOICE=AV]`** (e.g. `Huwag kumain.`,
  `Huwag manigarilyo.`) — needs PRO SUBJ injection to satisfy
  the V's a-structure completeness check. Canonical Tagalog 2nd-
  person imperatives use the addressee-explicit form
  (`Huwag kang kumain.` — closed by Phase 10.final.pre-1
  Variant A) or an OBJ-bearing form (matrix-NEG rule when `ng X`
  is the only argument). The bare-V form is sign-language /
  prohibition-sign style (S&O 1972 §8.2). Structurally adjacent
  to Candidate H Class-1 impersonal (the PRO has no antecedent in
  the bare-V case; the addressee is discourse-level). **Not a
  10.N inside-out candidate**, because there is no f-structural
  antecedent to bind to. **Scheduled as Phase 11.X** (non-FU
  sub-PR; see §3 backlog row).
- **`v_iter_redup` for curse-VERB `mura`** — morphology,
  not FU. Audit-attestation-gated per
  [[feedback_audit_before_scheduling]]. **Stays
  audit-attestation-gated** (not on the active Phase 11
  schedule; if a `mura-mura` curse-iter form appears in
  wave-2-5+ harvest, schedule as a one-off lex+sentry sub-PR).
- **Naturalistic ≥80% on the broader wave-2/3/5 corpora** —
  closure-driven engineering, not FU-related. The original
  Phase 9 §7.10 target was set against wave-1; the expanded
  corpora raise the bar. **Tracked as a separate Phase 11 work
  stream** (not a single sub-PR but an ongoing closure-driven
  effort across whichever sub-PRs surface wave-2/3/5
  attestations). Phase 11's FU-extension backlog above is one
  contributor; lex / morph / chart work outside the FU theme
  will continue alongside.

These items are documented here to make the boundary explicit:
they exist in Phase 11 scope but do **not** belong on the
FU-extension consumer backlog. The Phase 11 plan-of-record
(`.claude/plans/tgllfg-phase-11.md` §1) carries the
authoritative bucket table that includes 11.X alongside
11.B.1–11.B.5.

## 4. Future ideas

Items parked here have either no consumer or no clear path. They are
not Phase 11 backlog; they are anchors for future audits.

- **Candidate F**: `{COMP | XCOMP}*` body for cross-COMP
  relativization. No Tagalog construction surfaced; would
  overgenerate per SUBJ-only restriction (Kroeger 1993). Re-evaluate
  on future audit-corpus waves.
- **Reciprocal binding** (Dalrymple 2001 §15.2). Similar inside-out
  reach to sarili but with set-valued binders. Tagalog reciprocal
  `mag-…` is morphological, not anaphoric — no chart consumer
  expected.
- **Unbounded scope quantifiers**. `(((GF ↑) GF) ↑)` chains for
  quantifier scope ambiguity (Dalrymple 2001 §14). tgllfg's semantic
  representation is scope-flat today; would need a new feat
  inventory.
- **K&Z 1989 §3 minimality on inside-out resolution**. Currently
  `parents_via` returns parents in deterministic insertion order;
  the resolver picks the first. A formal minimality rule (shortest
  upward path) is documented as future work in
  `docs/fu-evaluation.md` §7.4.1. Gated on a chart consumer
  surfacing ambiguity in practice.
- **Materialized reverse index for `parents_via`**. Today's O(N)
  scan is sufficient for prototype scale; replace with a maintained
  reverse index when (a) corpus pressure on inside-out designators
  grows or (b) the set-valued extension lands and the scan complexity
  grows.

## 5. Anti-goals (carried forward from 11.A's framing)

- **Do not implement chart-rule rewrites in 11.A**. This audit is
  pure discovery. The first chart rewrite ships in 11.B.1.
- **Do not speculate beyond named workarounds / pinned fixtures /
  measurable maintenance burden**. The future-ideas section above
  captures speculation; it is not the backlog.
- **Do not flip 11.A into a phase-10-style closure-driven
  effort**. Phase 11's discipline is engineering-driven. Opt-ins
  ship for rule-consolidation value, even if zero audit-corpus
  closures.

## Appendix A — Per-module rule-by-rule audit

Added 2026-06-04 in response to a review note: "It would be worth
doing a rule-by-rule audit for all `cfg/*.py` modules". Sections
§A.1 through §A.9 audit each module. Six Explore subagents
processed the modules in parallel; the main loop verified key
findings.

**Methodology** (per agent):

1. Read the module's rule definitions in full.
2. For each `rules.append(Rule(...))` call (counting loop expansions
   as separate rules), classify into:
   - **F**: already an FU consumer (today)
   - **C-baseline**: could use pre-10 baseline FU
     (`F*` / `F+` / `{F | G}` / off-path)
   - **C-10L**: could use Kleene-on-alternation `{F | G}*`
   - **C-10M**: could use deferred defining-equation re-pass
   - **C-10N**: could use inside-out designators `(FEAT INNER)`
   - **N**: not FU-relevant (categorical / structural / lex-gated)
3. Report per-rule classification + per-module summary + any new
   candidates beyond §2's A-H.

### A.0 Aggregate findings

| Module | Total rules\* | F | C-baseline | C-10L | C-10M | C-10N | N |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `control.py` | 106 | 0 | 0 | 0 | 0 | 24 | 82 |
| `extraction.py` | 96 | 12 | 0 | 0 | 0 | 0 | 84 |
| `coordination.py` | 53 | 0 | 0 | 0 | 0 | 4 | 49 |
| `nominal.py` | 102 | 0 | 7 | 0 | 0 | 3 | 92 |
| `clause.py` | 161 | 0 | 0 | 0 | 0 | ~14 | 147 |
| `discourse.py` | 26 | 0 | 3 | 0 | 0 | 0 | 23 |
| `subordination.py` | 25 | 0 | 0 | 0 | 0 | 1 | 24 |
| `clitic.py` | 14 | 0 | 5 | 0 | 0 | 0 | 9 |
| `negation.py` | 6 | 0 | 0 | 0 | 0 | 0 | 6 |
| **TOTAL** | **589** | **12** | **15** | **0** | **0** | **~46** | **~516** |

\* "Total rules" expands loop bodies (each iteration counts as one
rule). Raw `rules.append(Rule(` call count is ~534; the 589 figure
counts each voice/case/linker variant emitted by a loop.

**Net result**: zero genuinely new FU candidates beyond A-H. The
audit confirms:

- Only one chart-level FU consumer today (Candidate A; 12 rule
  instances counting loop expansion).
- All C-10N candidates collapse into Candidates B (sarili),
  C (TestCrossClausalDeferred), D (coord CONJUNCTS — broader scope
  than originally captured; see §2.4 update), E (purposive PRO),
  H (PRO-placeholder sweep).
- C-baseline finds are all **speculative** — recursive composition
  patterns (POSS chains, ADJ-MOD stacking) that are corpus-bounded
  at depth ≤ 2 or explicitly anti-chaining-blocked, and `=c`-based
  feat gates in discourse.py / clitic.py that are standard LFG
  practice (not FU-dependent).
- Zero C-10L and C-10M candidates anywhere.

### A.1 control.py (106 rules)

| Class | Count | Notes |
| --- | --- | --- |
| F | 0 | No FU consumers in control.py (L47 wraps live in extraction.py) |
| C-10N | 24 | 22 = Candidate B sarili (lines 1110-1158); 2 = Candidate H "TRANS PRO-NOM-pivot" at lines 950-964 (impersonal SUBJ, Class-1-or-3 per follow-on audit) |
| N | 82 | Categorical voice/case/linker/NP-order variants; control nesting via rule recursion, not FU regex |

Key finding: control-chain nesting is handled by **rule recursion**
(each `S_XCOMP` rule rewrites to a smaller `S_XCOMP`), with each
rule's `(↑ SUBJ) = (↑ XCOMP SUBJ)` and `(↑ SUBJ) = (↑ REL-PRO)`
establishing the single-step link. No hand-rolled depth cascades.

New candidates beyond A-H: **none**.

### A.2 extraction.py (96 rules)

| Class | Count | Notes |
| --- | --- | --- |
| F | 12 | L47 RC wraps at `:2566` (S_GAP variant, 6 rule instances) + `:2611` (S_XCOMP variant, 6 rule instances). All carry `(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`. Candidate A consumer. |
| C-10N | 0 (per-file) | The ~9 PRO-placeholder instances in extraction.py are anaphoric REL-PRO/CASE copy boilerplate — Candidate H Class-2 (intentionally not structurally bound to avoid CASE-conflict). |
| N | 84 | Categorical case/voice/linker/NP-order variants across S_GAP / S_GAP_OBJ / S_GAP_OBJ_AGENT / S_GAP_OBL families; ay-fronting / ni-focus / paired-Ni / kahit-X variants |

Key finding: extraction.py is the **sole** chart-level FU consumer
today. The 12 F-class instances all collapse to one canonical
pattern (the L47 RC wrap) — Candidate A's `=c` → `=` swap applies
to all 12.

New candidates beyond A-H: **none**. The multi-daughter (5+) rules
at `:1851-1928` (paired-Ni focus correlatives) are categorical
fan-outs over focus-position × voice, not FU-collapsible.

### A.3 coordination.py (53 rules)

| Class | Count | Notes |
| --- | --- | --- |
| C-10N | 4 | All Candidate D scope: 2 `S_XCOMP` REL-PRO-chain rules (binary + ternary), 2 `S_XCOMP_BARE_COORD` dual-binding rules (binary + ternary). See §2.4 revised scope. |
| N | 49 | NP-coord (binary + N-LONG-LIST recursive), N-coord, clausal coord (`kaya naman` / comma / colon / dash variants), ADJ-coord, correlatives, multi-word coord particles, gapping, cardinal arithmetic |

Key finding: per-conjunct fan-out is concentrated in 4 rules within
coordination.py. Other coord rules use set-membership without
per-conjunct cross-binding (so no FU candidate). The shared
engine prereq (set-valued `parents_via`) is justified by these 4
rules plus Candidate E's purposive ADJ membership.

New candidates beyond A-H: **none** (D's scope expanded; see §2.4).

### A.4 nominal.py (102 rules)

| Class | Count | Notes |
| --- | --- | --- |
| C-baseline | 7 | Recursive POSS chains (3 rules; depth-2 corpus-bounded), ADJ-MOD stacking (4 rules; right-recursive idiom). All **speculative** — no named workaround or pinned fixture; deferred to future-ideas. |
| C-10N | 3 | Standalone demonstrative pronouns `iyon`/`iyan`/`nito` as bare NPs at `:453-463`. Candidate H Class-1 impersonal (discourse-anaphoric, no structural binder). Not actionable. |
| N | 92 | Categorical NP-projection / numeral / Q / DEM / ADJ-modifier / wh-PRON / partitive / possessive variants. Anti-chaining guards (`¬ (↓N FEAT)`) explicitly bound recursive composition. |

Key finding: nominal.py's recursion (POSS, ADJ-MOD, vague-Q) is
**bounded by explicit anti-reapply guards** or by corpus depth (2).
No FU-collapse motivation surfaces.

New candidates beyond A-H: **none**.

### A.5 clause.py (161 rules)

| Class | Count | Notes |
| --- | --- | --- |
| C-10N | ~14 | All PRO-placeholder instances (Candidate H). Per-class split: ~6-8 Class-1 impersonal (weather V, MODAL standalone, ADJ-pred + temporal ADV), ~3-4 Class-2 anaphoric (tough generic, neg-HAVE CASE workaround), ~2-3 Class-3 controlled. |
| N | 147 | Categorical voice/case/linker/NP-order / control wrap / ay-fronting / cleft / wh-question / existential / negative-existential / HAVE / SUBORD-attachment / cardinal-arithmetic / predicative-ADJ-ADV / parang-comparative / cleft / wh-cleft / discourse-particle / interjection / topic-drop / clitic-absorption variants |

Key finding: clause.py has **zero non-PRO FU candidates**. The K-on-A
audit (Candidate F null) and the per-depth XCOMP cascade audit (§2.7
null) are both confirmed by the rule-by-rule walkthrough. The PRO
sweep (Candidate H) is the only FU-relevant pattern, and most are
Class-1 impersonal (not actionable).

New candidates beyond A-H: **none**.

### A.6 discourse.py (26 rules)

| Class | Count | Notes |
| --- | --- | --- |
| C-baseline | 3 | AdvP gating via `(↓2 ADV_TYPE) =c '<X>'` (FREQUENCY/TIME) + `(↓2 INDEF) =c 'YES'`. **Speculative-only** — standard LFG constraining-equation idiom; not FU candidates. |
| N | 23 | Clause-final PP/AdvP/TimeAdv/SubordClause adjunct attachment; sentence-initial discourse PART; multi-word lexicalized discourse particles; appositive (em-dash, colon) variants |

Key finding: discourse.py is uniformly N-class. The 3 C-baseline
items are categorical feat gates that fit standard LFG idioms.

New candidates beyond A-H: **none**.

### A.7 subordination.py (25 rules)

| Class | Count | Notes |
| --- | --- | --- |
| C-10N | 1 | Purposive `para` / `upang` PRO at `:458-502` (the 4 sub-variants of Candidate E's rule family). |
| N | 24 | Conditional / concessive / temporal (bago / pagkatapos / habang / hanggang / mula nang / nang) / reason (dahil / sapagkat / dahil sa) / cause / purpose SubordClause builders + matrix attachment rules + topic-drop apodosis variants |

Key finding: Candidate E is the **only** structural-control PRO
in subordination.py. Other subord types (conditional, concessive,
temporal, reason) either embed a full S (with explicit SUBJ) or
use anaphoric PRO that's correctly kept as-is.

New candidates beyond A-H: **none**.

### A.8 clitic.py (14 rules)

| Class | Count | Notes |
| --- | --- | --- |
| C-baseline | 5 | 2P-clitic absorption via `(↓2 CLITIC_CLASS) =c '2P'` + variant feats (QUESTION / COUNTERFACTUAL / REGISTER). **Speculative-only** — standard LFG idiom. |
| N | 9 | Floated quantifier rules; clause-initial DUAL-Q + V variants (intransitive / transitive / ditransitive); kita clitic fusion (3 variants). |

Key finding: clitic.py uses explicit per-rule equations for clitic
placement. KITA fusion (the 1SG.2SG portmanteau) uses atomic
PERS/NUM/CASE equations on the SUBJ + typed-OBJ slots, not
structural binding.

New candidates beyond A-H: **none**.

### A.9 negation.py (6 rules)

| Class | Count | Notes |
| --- | --- | --- |
| N | 6 | Hindi declarative wrap; huwag imperative-negation; huwag + addressee + linker + V/ADJ; huwag + GEN-actor + linker + S (non-AV variants); wide-scope hindi + NP[NOM, COORD] + V[AV] |

Key finding: negation.py is uniformly N-class. No FU patterns; the
wide-scope NEG-over-coord rules use explicit verb percolation, not
FU paths.

New candidates beyond A-H: **none**.

### A.10 Aggregate reconciliation with §2 candidates

The rule-by-rule audit confirms each §2 candidate against ground
truth:

- **Candidate A** (L47 RC wraps): 12 F-class instances confirmed
  at `extraction.py:2566` + `:2611`. Same FU pattern across 12.
- **Candidate B** (sarili collapse): 22 C-10N instances confirmed
  at `control.py:1110-1158`.
- **Candidate C** (TestCrossClausalDeferred flip): test-level
  candidate; no chart rule today (the test asserts absence of
  binding). Bundled with B in 11.B.2.
- **Candidate D** (coord CONJUNCTS): scope expanded from 1 sub-case
  to **4 rule families** in coordination.py — see §2.4 update.
- **Candidate E** (purposive PRO): 1 C-10N instance at
  `subordination.py:458-502`. Confirmed.
- **Candidate F** (`{COMP | XCOMP}*`): zero candidates anywhere;
  null finding confirmed.
- **Candidate G** (baseline FU sweep): zero candidates beyond
  Candidate A; null finding confirmed.
- **Candidate H** (PRO-placeholder sweep): 53 instances
  distributed across `clause.py` (~14), `extraction.py` (~9
  REL-PRO/CASE boilerplate, Class-2), `control.py` (3), `nominal.py`
  (3, Class-1 demonstratives), `subordination.py` (1 = Candidate E),
  `discourse.py` / `clitic.py` / `negation.py` / `coordination.py`
  (0). Per-class breakdown: most are Class-1 impersonal (not
  actionable); ~3-5 are Class-3 controlled (inside-out candidates,
  to be implemented in 11.B.3 alongside E).

**No new candidates beyond A-H**. The audit is complete.

## Appendix B — Unimplemented FU engine extensions surfaced by the audit

Added 2026-06-04 in response to a review note: "If your audit has
identified other (unimplemented) FU extensions that would be
beneficial, then note that in the audit." Phase 10.L/M/N closed the
three named §18.1.3 deferrals from Phase 6.B/D/F. This appendix
catalogs **further** engine extensions that surfaced (or are
re-confirmed) during the audit. They are not chart-consumer
candidates (which belong in §2); they are engine-side primitives or
capabilities. Where an extension is **required** to unblock a §3
backlog item, it is called out; the rest are documented for
completeness.

### B.1 Set-valued `parents_via` extension (SHIPPED in 11.B.4.eng)

**Status**: **shipped 2026-06-04** in Phase 11.B.4.eng. The
`FGraph.parents_via` scan was extended to descend into
`SetValue` members when `v.attrs[feat]` points to a SetValue.
Existing direct-edge consumers (Phase 11.B.2 sarili NP-layer
rules) unaffected. Implementation matches the proposed shape
below (modulo minor cleanups: per-iteration the `child_value`
is fetched once via `self._store.get(self.find(child))` rather
than relying on raw `child` type, since `v.attrs.get(feat)`
returns a `NodeId`, not the `FValue` itself). Canonical fixture:
`tests/tgllfg/test_fu_evaluation.py::TestParentsViaSetValued`
(6 cases: set-member match / no-match / outside-in-composition
/ atom-mismatch / multi-parent / direct-edge backward-compat).
`docs/fu-evaluation.md` §7.4.1 updated with the set-valued
extension note. Unblocks Phase 11.B.3 (purposive PRO) and
Phase 11.B.4.chart (coordination CONJUNCTS).

**Pre-shipping status** (preserved below for the historical
audit record):

**Current behavior** (`src/tgllfg/fstruct/graph.py:698-739`):

```python
def parents_via(self, target: NodeId, feat: str) -> list[NodeId]:
    """Phase 10.N: reverse-lookup for inside-out designators."""
    target_root = self.find(target)
    seen: set[NodeId] = set()
    result: list[NodeId] = []
    for n, v in self._store.items():
        if not isinstance(v, ComplexValue):    # ← scans ComplexValue.attrs only
            continue
        child = v.attrs.get(feat)
        if child is None:
            continue
        if self.find(child) == target_root:
            n_root = self.find(n)
            if n_root not in seen:
                seen.add(n_root)
                result.append(n_root)
    return result
```

The current implementation **only scans `ComplexValue.attrs`**
(direct-edge `feat → child` mappings). For set-valued feats like
`CONJUNCTS`, `ADJUNCT`, `ADJ`, where the target appears as a
*member* of a `SetValue` rather than as a direct edge, the scan
returns no parents — even though semantically those parents exist.

**Motivating candidates** (from §2 + §A audit):

- **Candidate D** (§2.4): `S_XCOMP_BARE_COORD` per-conjunct binding
  collapse via `((CONJUNCTS ↑) SUBJ)` / `((CONJUNCTS ↑) REL-PRO)`.
  `CONJUNCTS` is set-valued. 4 rule families in coordination.py
  affected.
- **Candidate E** (§2.5): purposive `para` / `upang` PRO binding
  via `((ADJ ↑) SUBJ)`. `ADJ` is set-valued (a SubordClause is
  a member of the matrix's ADJ set).
- **Candidate H Class-3 subset** (§2.8): any controlled PRO whose
  containing feat is set-valued (most via ADJ / ADJUNCT).

**Proposed shape** of the extension:

```python
def parents_via(self, target: NodeId, feat: str) -> list[NodeId]:
    """Phase 11.B.4.eng: extended for set-valued feats."""
    target_root = self.find(target)
    seen: set[NodeId] = set()
    result: list[NodeId] = []
    for n, v in self._store.items():
        if not isinstance(v, ComplexValue):
            continue
        child = v.attrs.get(feat)
        if child is None:
            continue
        if isinstance(child, SetValue):
            # NEW: target is a member of n's set-valued feat
            for member in child.elems:
                if self.find(member) == target_root:
                    n_root = self.find(n)
                    if n_root not in seen:
                        seen.add(n_root)
                        result.append(n_root)
                    break
        else:
            # Existing direct-edge behavior
            if self.find(child) == target_root:
                n_root = self.find(n)
                if n_root not in seen:
                    seen.add(n_root)
                    result.append(n_root)
    return result
```

The extension is additive (existing direct-edge consumers are
unaffected) and matches the documented multiple-parents semantics
of inside-out: when the target is in a set of size N, the
parent is uniquely the f-structure holding the set; there is no
fan-out at the parent level.

**Sub-PR**: **11.B.4.eng** — engine extension + canonical
Dalrymple 2001 §15 set-valued binding fixture in
`test_fu_evaluation.py`. ~3-5 commits.

**Priority**: **P1** — unblocks Candidates D + E + the
set-valued-containing-feat subset of Candidate H Class-3.

### B.2 FU resolver-side cyclic-endpoint pruning (Phase 7+ engine extension)

**Status**: documented in `docs/fu-evaluation.md` §11 (the Phase
7+ extensions list) and `.claude/plans/tgllfg-out-of-scope.md`
§18.1.3 line 61. Phase 6.F C2 workaround motivator. Not required
by current audit; relevant to **Candidate B**.

**Today**: K&Z 1989 §3 minimality picks the shortest-depth
endpoint of an FU regex enumeration. If the canonical endpoint
causes a cyclic unification — e.g., a reflexive's binder
enumeration that includes the reflexive itself at depth 1 — the
resolver returns that endpoint and `graph.unify` fails with a
cyclic-unification diagnostic.

**Phase 6.F C2 workaround**. The sarili binding equations
(Candidate B at `control.py:1110-1158`) use **equation-side
exclusion**: separate rule variants for "sarili at SUBJ binds to
obj_target" vs "sarili at obj_target binds to SUBJ" rather than a
single alternation form `(↑ <self> ANTECEDENT) = (↑ {SUBJ |
obj_target})`. The alternation form would over-enumerate (the
reflexive's own position is reachable at depth 0/1), triggering
cyclic unification at the reflexive's own f-node.

**Proposed extension**: resolver-side filtering that prunes
endpoints whose canonical root is the same as (or already in the
unification chain of) the LHS being bound. With pruning, the
`{SUBJ | obj_target}` alternation correctly skips the cyclic
endpoint and selects the non-reflexive complement.

**Relevance to Candidate B**: today's collapse target is ~24
→ ~12 rules (the realistic per-NP-order pairing). With
cyclic-endpoint pruning + `{SUBJ | obj_target}` alternation +
inside-out designators, the aggressive collapse target ~24 → ~6
becomes feasible (one rule per voice_spec, alternation handles
both binding directions). This raises Candidate B's compression
ratio from 2× to 4×.

**Audit findings on motivation**: zero **additional** chart
consumers beyond Candidate B (no reciprocal binding, no
multi-binder constraints anywhere in `cfg/`). The extension is
Phase 7+ per `tgllfg-out-of-scope.md` §18.1.3; revisit when:

- A construction surfaces that requires the alternation form
  (e.g., reciprocals `magkaibigan`-style if Tagalog adopts
  productive reciprocal binding, or multi-binder constraints).
- Or, Phase 11.B.2 chooses to attempt the aggressive 24→~6
  Candidate B collapse rather than the realistic 24→~12.

**Priority**: **P2 — scheduled as 11.B.5** (updated 2026-06-04).
U-bucket cadence engine extension matching 10.L/M/N pattern:
ship the resolver-side filtering + canonical fixture; chart
consumer (aggressive Candidate B 24→~6 collapse via
`{SUBJ | obj_target}` alternation) is a follow-on (either
bundled with 11.B.2 if sequenced after 11.B.5, or as
11.B.2.post-1 if 11.B.2 shipped the realistic collapse first).
The Phase 6.F equation-side workaround continues to work
unchanged regardless.

**Cross-reference**: `tgllfg-out-of-scope.md` §18.1.3 line 61
(the deferral entry; will be marked "scheduled in 11.B.5" when
the sub-PR ships).

### B.3 K&Z 1989 §3 minimality on inside-out resolution (documented future work)

**Status**: documented in `docs/fu-evaluation.md` §7.4.1; not
required by current audit.

**Today**: when `parents_via(target, feat)` returns multiple
parents (typically because the inner target is structure-shared
across f-structures, e.g., a SUBJ shared between matrix and XCOMP
via functional control), the inside-out resolver picks the **first
in deterministic insertion order**. This is a sufficient prototype
behavior but not formally minimal.

**K&Z 1989 §3 minimality** prefers the **shortest** upward path —
the inside-out analog of the outside-in shortest-depth endpoint
selection. tgllfg's outside-in resolver already enforces minimality
(see §4.3 of `docs/fu-evaluation.md`); the inside-out side does
not yet.

**Audit findings on motivation**: zero. Per §A.3 + §A.7, Candidates
D and E both produce **unambiguous** single-parent resolutions.
Candidate C (cross-clausal sarili) is also unambiguous under XCOMP
functional control (the matrix is the unique parent that has the
embedded f-structure as a feat). No corpus pressure has surfaced
inside-out ambiguity that K&Z minimality would resolve differently
than insertion-order does.

**Priority**: **P3 / parked** — implement when a chart consumer
surfaces an ambiguous case where insertion-order gives the wrong
answer.

### B.4 Materialized reverse index for `parents_via` (performance only)

**Status**: documented in `docs/fu-evaluation.md` §7.4.1; not
required by current audit.

**Today**: `parents_via` is an O(N) scan over the live store. For
typical sentence f-graphs (≤50 ComplexValue nodes per
`docs/fu-evaluation.md` §7.4.1), the scan cost is negligible.

**Future motivator**: chart consumers that invoke `parents_via`
many times per parse, or sentence sizes that grow N significantly.
The B.1 set-valued extension adds a per-set inner loop, increasing
the constant factor (but not the asymptotic complexity).

**Replacement design**: a `ComplexValue` → `ComplexValue` reverse
edge maintained alongside `attrs` mutations; lookup becomes O(1)
per (target, feat) pair.

**Priority**: **P3 / scale-driven** — implement when audit-corpus
parsing surfaces measurable `parents_via` overhead.

### B.5 Set complement in regex paths (K&Z eq. 39 notation)

**Status**: documented as out-of-scope in `docs/fu-evaluation.md`
§3; not motivated by current audit.

K&Z 1989 eq. 39's English-topicalization body uses
`(↑ {COMP | XCOMP}* (GF-COMP))` — the `(GF-COMP)` bottom is the
**set complement** "any GF except COMP". The AST does not parse
this. tgllfg's Tagalog corpus uses `XCOMP*` bodies (single-feat
Kleene) without set complement.

**Audit findings on motivation**: zero (Candidate F null finding;
§2.6 confirms no Tagalog construction needs the K&Z eq. 39 body
shape, let alone the set complement bottom).

**Priority**: **P4 — scheduled as 11.final explicit decline**
(updated 2026-06-04). Audit found zero motivation; the v1
Tagalog grammar will not implement set-complement notation.
Migrating `tgllfg-out-of-scope.md` §18.1.3 line 59 from
"parked, revisit if surfaces" to "explicitly declined for v1
per Phase 11.A audit". Re-evaluate only if wave 6+ corpus
harvest or a future Tagalog dialect-coverage extension surfaces
a non-XCOMP relativization construction.

### B.6 Defining-equations on regex-LHS (out of scope per §5.3)

**Status**: explicitly out of scope in `docs/fu-evaluation.md`
§5.3; K&Z 1989 does not entertain.

`(↑ COMP* FOO) = 'X'` would require the resolver to invent
intermediate COMP nodes for unbounded depths — semantically
ill-defined in standard LFG. tgllfg's `_resolve_regex_for_write` is
deliberately unimplemented.

**Audit findings on motivation**: zero. No rule expresses
defining-on-regex; no construction would benefit.

**Priority**: **P5 — scheduled as 11.final explicit decline**
(updated 2026-06-04). Out-of-scope per K&Z 1989 design;
fu-evaluation.md §5.3 explicitly forbids. Migrating
`tgllfg-out-of-scope.md` §18.1.3 line 60 from
"declined-by-design for Phase 6.B" to "explicitly declined for
v1 — confirmed by Phase 11.A audit". This is a permanent
out-of-scope decision absent a substantial K&Z-style design
extension.

### B.7 Inside-out designators with off-path constraints (speculative)

**Status**: not documented anywhere; surfaced as a hypothetical
during the audit.

The current AST allows off-path constraints `<(→ FEAT) =c 'X'>`
on path elements via `PathElement.off_path`. The inside-out
designator `InsideOut(feat, inner)` is a *base*, not a path
element, and does not currently accept off-path constraints.

A hypothetical use:
`((SUBJ ↑) <(→ TENSE) =c 'PAST'> GF)` — "find the f-structure F
such that F has my f-structure as its SUBJ, AND F's TENSE is PAST;
then access F's GF". Useful for restricting inside-out resolution
to parents satisfying an additional constraint.

**Audit findings on motivation**: zero. No candidate in §2 or §A
needs constrained inside-out resolution.

**Priority**: **P4 / parked** — implement only when a chart
consumer surfaces a needed disambiguation that the bare inside-out
form cannot express.

### B.8 Multi-target inside-out (speculative)

**Status**: not documented; hypothetical.

The current inside-out resolver returns the **first** parent in
insertion order (per the multiple-parents caveat in
`docs/fu-evaluation.md` §7.4.1). A hypothetical "all parents"
variant would return the full list and allow downstream operations
(e.g., requiring all parents to satisfy a property).

**Audit findings on motivation**: zero. The audit's §A
classifications all involve single-parent inside-out resolution.

**Priority**: **P5 / speculative** — no chart consumer; no clear
LFG-canonical semantics in the literature.

### B.9 Aggregate priority (updated 2026-06-04 with Phase 11 schedule)

| Extension | Priority | Phase 11 disposition | Sub-PR | LOC scale |
| --- | --- | --- | --- | --- |
| **B.1 Set-valued `parents_via`** | **P1** | **Scheduled** — unblocks Candidates D + E + H-Class-3 | **11.B.4.eng** | ~20-40 LOC |
| **B.2 Cyclic-endpoint pruning** | **P2** | **Scheduled** — U-bucket engine + canonical fixture; enables aggressive Candidate B 24→~6 collapse | **11.B.5** | ~30-60 LOC |
| B.3 K&Z minimality on inside-out | P3 | Parked — no ambiguity surfaced | — | ~30-60 LOC |
| B.4 Materialized reverse index | P3 | Parked — perf-scale-driven | — | ~50-100 LOC |
| **B.5 Set complement** | **P4** | **Explicit decline** — v1 confirmed; no Tagalog construction needs it | **11.final** | n/a |
| **B.6 Defining-on-regex LHS** | **P5** | **Explicit decline** — out-of-scope per K&Z (permanent) | **11.final** | n/a |
| B.7 Inside-out + off-path | P4 | Parked — no consumer | — | ~30 LOC |
| B.8 Multi-target inside-out | P5 | Speculative — no consumer | — | ~10-20 LOC |

**Net engine work for Phase 11**: **B.1 + B.2 scheduled**.
B.1 is required (P1) for the consumer ladder; B.2 ships as a
standalone U-bucket prototype (P2) enabling the aggressive
Candidate B collapse follow-on. B.5 + B.6 receive **explicit
decline decisions** in 11.final (migrating from "parked" to
"declined for v1"). B.3 / B.4 / B.7 / B.8 stay parked with
documented priorities, ready for future re-evaluation if
corpus pressure or chart consumers surface.

The full inventory reconciles against `tgllfg-out-of-scope.md`
§18.1.3 ("Other future work dependent" — items at lines 59 / 60
/ 61) and `docs/fu-evaluation.md` §11 (Phase 7+ extensions list).
B.4 / B.5 / B.6 / B.7 / B.8 are documented in fu-evaluation.md
only; B.2 / B.5 / B.6 also appear in tgllfg-out-of-scope.md
§18.1.3. Phase 11 scheduling closes the four §18.1.3 items
(line 61 → 11.B.5; lines 59 + 60 → 11.final explicit decline;
line 62 → bundled into 11.B.2 spike-probe) plus §18.1.4 line 77
→ 11.X (non-FU carry-forward).

## 6. Cross-references

- Plan-of-record: `.claude/plans/tgllfg-phase-11.md`.
- Out-of-scope ledger: `.claude/plans/tgllfg-out-of-scope.md`
  §18.1.3 (FU-related Phase 7+ items: set-complement at line 59,
  defining-on-regex-LHS at line 60, resolver-side cyclic-endpoint
  pruning at line 61, per-XCOMP cross-clausal sarili at line 62);
  §18.1.4 (Phase 10-surfaced, Phase 11 carry-forward: bare
  `Huwag + V[AV]` at line 77, U-bucket chart consumers at line
  78 — the master directive this audit operationalizes).
- FU contract: `docs/fu-evaluation.md` (Phase 6.B design appendix)
  §3 / §4.1 / §5.2.1 / §7.2 / §7.4.1.
- Phase 10.L progress: [[project_phase10_l_progress]] (PR #195).
- Phase 10.M progress: [[project_phase10_m_progress]] (PR #196).
- Phase 10.N progress: [[project_phase10_n_progress]] (PR #197).
- Phase 6.D L47 motivator: `src/tgllfg/cfg/extraction.py:2510-2613`
  (rationale block + the two `=c` instances).
- Phase 6.F L104 motivator: `src/tgllfg/cfg/control.py:1070-1158`
  (rationale block + the 24 binding rules).
- TestCrossClausalDeferred pinned fixture:
  `tests/tgllfg/test_phase5m_reflexive_sarili.py:239-276`.
- Coordination CONJUNCTS self-flag:
  `src/tgllfg/cfg/coordination.py:382-390`.
- Purposive PRO self-flag: `src/tgllfg/cfg/subordination.py:446-450`.
- Engine source: `src/tgllfg/fstruct/equations.py` (AST),
  `src/tgllfg/fstruct/unify.py` (re-pass), `src/tgllfg/fstruct/fu.py`
  (FSA resolver), `src/tgllfg/fstruct/graph.py:parents_via`
  (reverse-lookup, lines 698-739).
