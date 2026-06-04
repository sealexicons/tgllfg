<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Functional-uncertainty evaluation

Phase 6.B design appendix per `.claude/plans/tgllfg-phase-6.md`
§5.2 C1. This document captures the regex-path semantics tgllfg
adopts for **functional uncertainty (FU)** equations, the FSA-
based decision procedure, the binding-vs-constraining contract,
and the Tagalog-specific calibrations. C2 onwards implement what's
specified here.

Cross-references:

- `data/tgl/references/Kaplan-Zaenen-1989-LSS-CStruct-FU.pdf` — Kaplan & Zaenen 1989, "Long-Distance
  Dependencies, Constituent Structure, and Functional Uncertainty",
  in *Formal Issues in Lexical-Functional Grammar* (ed. Dalrymple
  et al.), ch. 3.
- Kaplan & Maxwell 1988, "An Algorithm for Functional Uncertainty",
  Proceedings of COLING-88. (Provides the satisfiability algorithm
  underlying §2.2 decidability.)
- Dalrymple 2001, *Lexical Functional Grammar*, ch. 14
  (secondary reference; the same FU machinery in modern LFG dress).
- `.claude/plans/tgllfg-phase-6.md` §5.2 (commit ledger for the
  implementation).
- `src/tgllfg/fstruct/equations.py:Feature` / `StarFeature` /
  `PlusFeature` / `AltFeature` — the AST is already parsed; this
  phase adds evaluation.

## 1. Goal

Replace the `"deferred"` informational diagnostic currently emitted
at `src/tgllfg/fstruct/unify.py::_path_features` (lines 230–249)
with an actual FU evaluator. After Phase 6.B, equations of the form

```text
(↑ TOPIC) = (↑ COMP* OBJ)
(↑ REL-PRO) =c (↑ {COMP, XCOMP}* SUBJ)
(↑ SUBJ) =c (↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)
```

evaluate against the live `FGraph`: the RHS regex-path enumerates
zero-or-more endpoints reached by paths matching the regular
expression, and the equation is satisfied (constraining) or
established (binding) against each well-formed endpoint.

6.B is foundation for the L-numbered §18.1.2 closures that depend
on FU evaluation:

- 6.D / L47 — long-distance wh-extraction relativization.
- 6.E / L93 — free relative `kung sino` / `kung ano` as DP.
- 6.F / L104 — `sarili` anaphora via inside-out binding.

## 2. Foundations: Kaplan & Zaenen 1989 + Kaplan & Maxwell 1988

K&Z 1989 §3 extends the LFG function-application notation
`(f s) = v` (K&Z eq. 27) to allow the argument position to denote
a (possibly infinite) set of strings drawn from a regular
language. With `α` a regular language over GF names, the
interpretation is:

```text
(f α) = v  iff  ((f s) Suff(s, α)) = v  for some symbol s
```

(K&Z eq. 29). This is the **regex-path semantics** at the heart
of FU. Concretely, the topicalization equation in K&Z eq. 30:

```text
(↑ TOPIC) = (↑ COMP* OBJ)
```

reads: the value of `TOPIC` is identified with the `OBJ` reached
by zero-or-more `COMP` traversals from the current f-structure.
The K&Z paper develops two further canonical examples:

- **English topicalization** (K&Z eq. 39):
  `(↑ TOPIC) = (↑ {COMP, XCOMP}* (GF-COMP))`. The body
  `{COMP, XCOMP}*` says the topic-binding path threads through
  zero or more complement clauses; the bottom `(GF-COMP)`
  ("any GF except COMP") selects the actual role being topicalized.
- **Icelandic adjunct island** (K&Z eq. 38):
  `(↑ TOPIC) = (↑ (GF-ADJ)* GF)`. The body excludes adjuncts —
  Icelandic does not topicalize out of adjuncts.

K&Z prove three decidability results in §3 (with details in
Kaplan & Maxwell 1988):

1. **Membership** is decidable. A given f-structure has finitely
   many function-application sequences from any node; each is
   testable against the regular-set membership of the regex.
2. **Satisfiability** is decidable. Two FU equations whose
   languages overlap are transformed into a finite disjunction of
   non-uncertainty equations via state-decomposition of the FSAs
   representing the two regular languages.
3. **Minimality.** When multiple regex strings reach valid
   endpoints, the f-structure assigned to a sentence uses the
   **shortest** path realizing each uncertainty (K&Z 1989 §3, last
   subsection).

The K&M 1988 algorithm is the practical mechanization: compile
the regex into an FSA and traverse the f-graph in lock-step,
producing the set of endpoints. tgllfg adopts this approach.

## 3. Regex-path subset supported

The `src/tgllfg/fstruct/equations.py` AST already parses the
following path elements (the equation grammar accepts them today;
6.B adds evaluation):

| Element | Surface syntax | AST node |
| --- | --- | --- |
| Literal | `F` | `Feature(name="F")` |
| Kleene star | `F*` | `StarFeature(name="F")` |
| Kleene plus | `F+` | `PlusFeature(name="F")` |
| Alternation | `{F \| G}` | `AltFeature(names=("F","G"))` |
| Kleene-on-alternation star (Phase 10.L) | `{F \| G}*` | `StarAltFeature(names=("F","G"))` |
| Kleene-on-alternation plus (Phase 10.L) | `{F \| G}+` | `PlusAltFeature(names=("F","G"))` |

A regex-path is a concatenation of these elements:
`(↑ F G* {H | I} J)` parses to a `Designator` with
`path = (Feature("F"), StarFeature("G"), AltFeature(("H","I")), Feature("J"))`.
Every element optionally carries off-path constraints (§6).

K&Z 1989 eq. 39's canonical English-topicalization body
`(↑ TOPIC) = (↑ {COMP | XCOMP}* (GF-COMP))` now parses through to
a `StarAltFeature(names=("COMP","XCOMP"))` element followed by the
bottom (the set-complement bottom `(GF-COMP)` remains out of scope
— see below). The Phase 6.B K&Z fixtures
(`tests/tgllfg/test_fu_evaluation.py::TestKZ1989Fixtures`) now carry
a `test_eq39_topic_equals_comp_xcomp_star_gf_kleene` companion
exercising the canonical body; the single-step approximation is
retained as a contrast.

**Out of scope for 6.B:**

- **Set complement** (K&Z eq. 39's `(GF-COMP)` notation, "any GF
  except COMP"). The AST does not currently parse it. Corpus
  pressure may surface a need in Phase 6.D / 6.F; we defer the
  syntax extension until then.
- **Defining with regex on LHS**, e.g., `(↑ COMP* FOO) = 'X'`.
  The unifier would have to invent intermediate nodes for the
  unbounded `COMP*` traversal — semantically ill-defined in
  standard LFG. See §5.

## 4. Evaluation algorithm

### 4.1 FSA construction

Compile the regex-path AST into a finite-state automaton:

- **`Feature(F)`** → single transition on label `F`.
- **`StarFeature(F)`** → a state with a self-loop on label `F` and
  an ε-transition that allows zero iterations.
- **`PlusFeature(F)`** → like `Star` but the ε is post-loop: at
  least one `F` consumed before the FSA can advance.
- **`AltFeature(F | G | ...)`** → branching transitions, one
  per name.
- **`StarAltFeature(F | G | ...)`** (Phase 10.L) → like `Star`
  but with parallel self-loops, one per name in the alternation.
  Same ε-transition handles the zero-iteration case.
- **`PlusAltFeature(F | G | ...)`** (Phase 10.L) → like `Plus`
  but with parallel `cur --Fi--> mid` transitions on entry and
  parallel `mid --Fi--> mid` self-loops, one per name.
- **Concatenation** → standard FSA concatenation.

The FSA is small (typically 2-5 states per path element). It is
compiled once per equation and cached for re-evaluation.

### 4.2 Graph traversal

Inputs: `(graph: FGraph, base: NodeId, fsa)`.

Maintain a worklist of `(node, fsa_state)` configurations:

```text
worklist  = [(base, fsa.start)]
visited   = {}        # set of (node_root, fsa_state)
endpoints = []        # list of (depth, NodeId) for minimality ordering
```

At each step pop a configuration:

1. **Cycle check.** Canonicalize the node via `graph.find(node)`.
   If `(root, fsa_state) ∈ visited`, drop and continue.
2. **Accept.** If `fsa_state` is an accept state, append
   `(depth, root)` to `endpoints`.
3. **ε-transitions.** For each ε-transition out of `fsa_state`,
   push `(root, next_state)` with unchanged depth.
4. **Label transitions.** For each labeled transition
   `(label, next_state)`:
   - Look up `label` in the current node's `ComplexValue.attrs`
     (via `graph.value(root)`). If the node is unset, has a
     non-Complex value, or the label is missing, skip.
   - **Off-path** check (§6): if the transition carries off-path
     constraints, evaluate them against `root` before pushing the
     successor. Failure prunes this branch silently — off-path
     constraints filter the path enumeration, they do not
     surface diagnostics for individual paths.
   - Push `(graph.find(attrs[label]), next_state)` with
     `depth + 1`.

Termination is guaranteed: the FSA has finitely many states; the
graph has finitely many nodes; `visited` has finite cardinality.
The worklist runs out after at most `|nodes| × |fsa_states|`
iterations.

### 4.3 Endpoint selection (minimality)

After traversal, `endpoints` is the sorted list of `(depth, NodeId)`
pairs. The **canonical endpoint** is the one with minimum depth.
On ties (same depth, distinct nodes), the resolver returns the
whole tied set — disambiguation is a higher-level concern (the
caller decides whether to fail, treat as ambiguity, or pick the
deterministically-first NodeId).

K&Z 1989 §3 minimality clause is consistent with this: f-structures
prefer the shortest path. tgllfg's resolver returns the shortest
endpoints; callers (constraining-eq evaluator, binding-eq
evaluator) commit to one or surface a diagnostic.

## 5. Binding vs. constraining contract

Per `.claude/plans/tgllfg-phase-6.md` §5.2 (the constraint carried
forward from §13.2): **regex paths are permitted in constraining
and binding contexts only; defining-on-regex is forbidden.**

### 5.1 Constraining (`=c`)

```text
(↑ SUBJ) =c (↑ XCOMP* SUBJ)
```

Both sides resolve as reads: the LHS via `_resolve_for_read` (no
regex; today's `lookup_path` path); the RHS via the new
`_resolve_regex_for_read`. The equation holds iff the LHS node
is `equiv` to some endpoint returned by the RHS resolver. On no
endpoints, or on no endpoint matching the LHS, emit a
`constraint-failed` diagnostic.

### 5.2 Binding (`=`)

```text
(↑ REL-PRO) = (↑ COMP* SUBJ)
```

Defining equation, but the RHS is a regex. Strict reading of the
LFG `=` operator is "unify the LHS endpoint with the RHS endpoint".
With regex on RHS:

- Resolve RHS via `_resolve_regex_for_read` to get
  `endpoints: list[NodeId]`.
- Apply K&Z minimality: select the shortest-depth endpoint.
- Call `graph.unify(lhs_node, endpoint)`.

Ties at the minimum depth surface as a `constraint-failed`
diagnostic ("FU binding ambiguous: N endpoints at depth D");
the caller must disambiguate via additional constraining
equations or report failure.

The key conceptual point: **binding equations write via
`graph.unify` between existing nodes; they never extend a path.**
The "write" is the unification link, not new structure. This is
why binding-with-regex is safe (and supported) but defining-with-
regex-on-LHS is not.

### 5.2.1 Deferred re-pass for FU binding equations (Phase 10.M)

Defining-equations with FU on the RHS evaluate during pass 1
(the **defining pass**), which walks the c-tree parent-first.
This means an FU binding equation on a parent c-node may fire
**before** the sibling or descendant equations that build the
regex-path target. The resolver returns no endpoint and, pre-10.M,
the equation failed with `constraint-failed`.

Phase 6.D L47 worked around this by rewriting the canonical K&Z
1989 §3 eq. 39 binding form
`(↓3 REL-PRO) = (↓3 XCOMP* SUBJ)` as a constraining equation
`(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)` — which evaluates in pass 2
after the entire defining pass has built the f-structure. The
combination of (a) the body's `(↑ SUBJ) = (↑ REL-PRO)` defining
equation creating the reentrancy + (b) the wrap rule's `=c` FU
equation verifying that the reentrancy holds along an XCOMP* path
delivers the same semantic outcome, but not the canonical K&Z form.

Phase 10.M lifts the limitation. The orchestrator's defining pass:

1. When an FU binding equation reports no endpoint, the resolver
   tags the diagnostic with the transient kind `fu-no-endpoint`
   (rather than `constraint-failed`).
2. `_pass_defining` intercepts `fu-no-endpoint` diagnostics and
   **queues** the equation with its context (`up`, `children`,
   parsed equation, source string, c-node label) instead of
   appending the diagnostic to the global list.
3. After the full c-tree walk completes, `_repass_deferred_fu`
   iterates a bounded fixpoint loop:
   - Each pass re-evaluates every queued equation against the
     post-pass-1 graph.
   - A successful retry drops the equation from the queue (and
     may extend the graph, unblocking other queued items).
   - A retry that produces a non-`fu-no-endpoint` diagnostic
     (e.g., an `atom-mismatch` from `graph.unify`) emits
     immediately — that failure is genuine, not a path-build
     order artifact.
   - The loop terminates when no progress is made in a pass or
     when the queue is empty.
4. Survivors of the re-pass emit a legacy `constraint-failed`
   diagnostic with a "no endpoint after deferred re-pass" message —
   matching pre-10.M behavior for genuinely unsatisfiable
   FU defining equations.

The mechanism is **additive**: FU bindings that already worked
under pass-1 order continue to fire at their original site (the
queue stays empty in the common case). The re-pass only activates
when an FU binding genuinely depended on a not-yet-built path.

The `=c` constraining form remains the recommended idiom when the
binding is semantically a verification (the path's existence is the
constraint). The canonical defining `=` form is now available when
the binding **creates the reentrancy** (e.g., inside-out binding
for `sarili`, cross-clausal non-control extraction, or other
constructions where the FU equation must *establish* the link
rather than verify it).

**Phase 11.B.1 — first chart consumer (2026-06-04).** The L47
long-distance relativization wraps (`cfg/extraction.py:2566` for
the S_GAP-bodied wrap and `:2611` for the S_XCOMP-bodied wrap)
migrate from the Phase 6.D constraining `=c` workaround to the
canonical K&Z 1989 §3 eq. 39 defining `=` form. The S_XCOMP wrap
also narrows its daughter to `S_XCOMP[SUBJ_GAP=true]` — see
`docs/fu-extension-audit.md` §2.1 for the gap-category split that
makes the defining form safe under Kroeger 1993's SUBJ-only
relativization restriction. Both wraps now express the binding in
its canonical LFG form; the re-pass machinery handles the
parent-first evaluation order transparently. Twelve chart rules
(3 head cases × 2 linkers × 2 wrap variants) updated; +13
audit-corpus closures across waves 1–5 (no regressions). See
`docs/fu-extension-audit.md` §2.1 (Candidate A shipping outcome).

### 5.3 Defining with regex on LHS (out of scope)

```text
(↑ COMP* FOO) = 'X'      ; NOT SUPPORTED in 6.B
```

If permitted, the resolver would have to invent intermediate
COMP nodes for every depth. The K&Z paper does not entertain this
construction (FU is fundamentally about reaching existing
structure). 6.B's `_resolve_regex_for_write` is **not
implemented** — `_path_features` returns an error diagnostic when
asked to write through a regex-path.

If corpus pressure surfaces a real need, revisit in a later phase
with explicit bounds (e.g., max-depth=1) and a clear motivation.

## 6. Off-path constraints

An off-path constraint restricts intermediate nodes during FSA
traversal:

```text
(↑ XCOMP*<(→ TENSE) =c 'PAST'> SUBJ)
```

reads: the path threads through zero or more `XCOMP` nodes, each
of which must satisfy `(→ TENSE) =c 'PAST'`, then accesses the
`SUBJ` of the deepest XCOMP.

The `→` metavariable refers to the **current intermediate node**
during traversal — distinct from `↑` (the matrix f-structure) and
`↓` (the daughter's f-structure). It binds dynamically: each step
through an off-path-bearing element evaluates the constraint
against the node just entered.

### 6.1 Evaluation rule

At each FSA transition consuming an element with non-empty
`off_path`:

1. Bind `→` to the post-transition node (the canonical root of
   `attrs[label]`).
2. Evaluate each off-path equation in turn, against the f-graph,
   in the constraining-equation regime (no mutations).
3. If any off-path equation fails, **prune this traversal branch
   silently**: do not push the successor onto the worklist.
4. If all off-path equations succeed, push the successor.

Off-path constraints filter the enumeration — they do not produce
per-step diagnostics. If the entire enumeration empties because
of off-path constraints, the regex-path resolves to no endpoints
and the outer equation surfaces the appropriate failure (a
`constraint-failed` for a constraining context; an
`existential-failed` for a binding context with no other
endpoints).

### 6.2 Off-path on Kleene operators

For `F*` and `F+`, the off-path constraint applies **at every
intermediate node**. The FSA's self-loop transition re-evaluates
the constraint each iteration. This is exactly the K&Z 1989
behavior: off-path constraints "live on the intermediate nodes
themselves".

For `F` (single step), the off-path constraint applies once, to
the post-step node.

## 7. Tagalog adaptation

K&Z's English / Icelandic / Japanese examples translate to
Tagalog with two caveats: the voice system and the role of
`SUBJ` in the body / bottom partition.

### 7.1 Voice and the bottom role

Tagalog's pivot (`ang`-NP) is uniformly the SUBJ. Topicalization
and relativization target the pivot. In a relative clause like

```text
ang bata-ng kumain ng isda  "the child who ate the fish"
       └────────────────────┘
       relative clause
```

the head `bata` is the SUBJ of the embedded relative clause; the
relativization equation is

```text
(↑ REL-PRO) = (↑ SUBJ)            ; local relativization
```

For cross-clausal relativization, where the head's role is in an
embedded XCOMP:

```text
Ang bata-ng gusto kong kainin _ ng isda
"The child whom I want _ to eat the fish"
```

the relativized `bata` is the SUBJ of the embedded XCOMP at
depth 2 (`gusto` is the matrix, `kainin` is the XCOMP). FU
captures this:

```text
(↑ REL-PRO) = (↑ XCOMP* SUBJ)
```

This is Phase 6.D's main payload. The body element `XCOMP*`
encodes "zero or more XCOMP traversals"; the bottom `SUBJ` is the
relativized role.

### 7.2 COMP vs. XCOMP in Tagalog

K&Z's English `(↑ TOPIC) = (↑ {COMP, XCOMP}* (GF-COMP))` body
includes both COMP and XCOMP. In Tagalog:

- **COMP** is the finite complement (e.g., reported-Q `sabi niya
  na ...` "he said that..."); subjects are independent.
- **XCOMP** is the non-finite open complement (e.g., modal
  `gusto kong kumain` "I want to eat"); subject is shared with
  the matrix (functional control).

For Phase 6.D the canonical relativization body is `XCOMP*`. The
broader `{COMP | XCOMP}*` body is corpus-blocked pending real
data — we have not yet seen a Tagalog sentence requiring
cross-COMP relativization that isn't structurally ambiguous with
indirect speech. Phase 10.L lifted the engine limitation (the
AST + FSA now compile `StarAltFeature(("COMP","XCOMP"))`); chart
rules can opt in to the broader body when audit-corpus pressure
surfaces the need.

### 7.3 Sarili binding (6.F)

The reflexive `sarili` follows an inside-out designator:

```text
(↓ POSS) = (↑ SUBJ)             ; local-domain binding
```

binds the possessor of `sarili` to the matrix SUBJ. Cross-clausal
sarili reach (across XCOMP) uses FU:

```text
(↓ POSS) = (↑ XCOMP* SUBJ)
```

— with binding selecting the shortest-depth `SUBJ` (typically the
nearest XCOMP, not the matrix).

### 7.4 Free relative `kung sino` / `kung ano` (6.E)

The free-relative head `kung sino` "the one who" is a wh-clause
realized as a DP argument:

```text
Galit ako sa kung sino ang nag-record.
"I'm angry at whoever recorded it."
```

The internal wh-PRO of the `kung-S` connects to the matrix
argument slot via an FU binding. The Phase 6.E design (§5.5)
will calibrate the specific equation shape against R&B 1986 §6
free-relative examples.

### 7.4.1 Inside-out designators (Phase 10.N)

Dalrymple 2001 ch. 14 / 15 inside-out designators
`(FEAT INNER_DESIGNATOR)` are now supported by the equation
grammar (parser + AST) and the resolver (`_resolve_base` +
`FGraph.parents_via` reverse-lookup). The surface form means
"find the node N such that N has the inner-resolved target as its
FEAT".

Surface examples:

```text
(SUBJ ↑)          ; find the f-structure that has ↑ as its SUBJ
((SUBJ ↑) GF)     ; that f-structure's GF
(SUBJ (XCOMP ↑))  ; nested: find F with F.XCOMP = ↑; then find N
                  ; with N.SUBJ = F
```

Motivating use case (Dalrymple 2001 §14): non-local binding for
reflexives — `sarili`'s antecedent in cross-clausal contexts
where the binder is **outside** the embedded clause and the
embedded c-node's ↑ doesn't see it directly. The Phase 6.F L104
binding rules placed all binding equations on matrix S rules
(where ↑ is the matrix and the binder is directly accessible);
cross-clausal sarili was pinned at `TestCrossClausalDeferred` in
`tests/tgllfg/test_phase5m_reflexive_sarili.py`.

The 10.N prototype delivers the engine extension; chart consumers
opt in when corpus pressure surfaces a Tagalog construction
needing the canonical inside-out form. The Phase 6.F matrix-rule
pattern remains the recommended idiom when binding is local.

**Reverse-lookup implementation** (FGraph.parents_via):

```text
parents_via(target, feat) -> [canonical_root]
```

O(N + sum-of-set-sizes) scan over the live store, iterating in
deterministic insertion order. Sufficient for a prototype; a
materialized reverse index can replace this if corpus pressure on
inside-out designators surfaces (typical sentence f-graphs have
≤50 ComplexValue nodes and small set-valued slots, so scan cost
is negligible).

**Multiple parents**: when the inner target is structure-shared
across f-structures (e.g., a SUBJ shared between matrix and
XCOMP via functional control, or an ADJUNCT shared across
multiple clauses), `parents_via` returns all of them. The
resolver picks the **first** parent in deterministic insertion
order. K&Z 1989 §3 minimality on inside-out resolution is
documented as future work — gated on corpus pressure.

**Phase 11.B.4.eng — set-valued feat extension (2026-06-04).**
The 10.N prototype scanned `ComplexValue.attrs` direct edges
only. Phase 11.B.4.eng extends the scan to set-valued feats:
when `v.attrs[feat]` points to a `SetValue`, the target may be a
member of that set rather than the direct edge endpoint. The
extension is additive — existing direct-edge consumers (Phase
11.B.2's sarili NP-layer rules) see no behavior change. Unblocks
Phase 11.B.3 (purposive PRO via `((ADJ ↑) SUBJ)`) and Phase
11.B.4.chart (coordination CONJUNCTS via
`((CONJUNCTS ↑) SUBJ)`). Canonical fixture:
`tests/tgllfg/test_fu_evaluation.py::TestParentsViaSetValued`.
Audit doc: `docs/fu-extension-audit.md` §B.1 (shipped).

**Failure mode**: when no parent has the named feat pointing at
the inner target, the resolver returns a diagnostic with kind
`inside-out-no-parent`. The kind is not in `NON_BLOCKING_KINDS` —
inside-out failures block the parse with the same semantics as
`constraint-failed` for binding-related failures.

**Phase 11.B.2 — first chart consumer (2026-06-04).** The sarili
anaphora binding (Phase 6.F L104) migrates from 24 matrix-rule
variants in `cfg/control.py:1097-1186` to 4 NP-layer rules in
`cfg/nominal.py` parallel to the canonical NP-possessor rule.
The NOM-sarili variant uses
`(↑ ANTECEDENT) = ((SUBJ ↑) {OBJ | OBJ-AGENT | OBJ-CAUSER})`
(combining inside-out + RHS outside-in alternation); 3 GEN-sarili
variants use `(↑ ANTECEDENT) = ((<feat> ↑) SUBJ)` for `<feat>` ∈
`{OBJ, OBJ-AGENT, OBJ-CAUSER}` (one per possible matrix-consumer
feat, since the InsideOut AST node holds a single feat name). Net
rule-count delta: -20. Closes Candidate B (24→4 collapse) and
Candidate C (cross-clausal sarili — productively binds via
inside-out + XCOMP functional control structure-sharing) in
`docs/fu-extension-audit.md` §2.2 / §2.3. See those sections for
the shipping outcome and the two blockers (LHS-regex `=c` not
implemented; dual unconditional bindings clash with occurs-check)
that ruled out the audit-proposed matrix-rule mechanism.

### 7.5 Source citations

- **Schachter & Otanes 1972** ch. 5 (voice system).
- **Ramos 1971** (binding domains; secondary).
- **R&B 1986** (the project's primary fielded grammar).
- **Kroeger 1993** ch. 2 (Tagalog as a clear case of subject-
  prominence; the OBJ-uniform analysis already adopted).

## 8. Implementation map

### 8.1 Touched code

- `src/tgllfg/fstruct/equations.py`: **no AST changes**. The
  existing `Feature` / `StarFeature` / `PlusFeature` / `AltFeature`
  nodes are sufficient. Set-complement (out of scope per §3)
  would require an AST extension; not in 6.B.
- `src/tgllfg/fstruct/unify.py`:
  - `_path_features` (lines 230–249): removed in 6.B C2. The
    `"deferred"` short-circuit is replaced by branching on
    whether the path contains regex elements.
  - `_resolve_for_read` and `_resolve_for_write` refactor:
    plain-feature paths continue to use `lookup_path` /
    `resolve_path`. Regex-bearing paths route to new helpers.
  - **New** `_resolve_regex_for_read(graph, designator, up,
    children) -> tuple[list[NodeId], Diagnostic | None]`:
    compiles the regex, traverses the graph, returns the
    minimality-sorted endpoint list. (See §4.)
  - `_eval_constraining_eq` (lines 332–384): 6.B C3 wires the
    regex resolver in. If LHS or RHS contains regex, route
    through `_resolve_regex_for_read`.
  - **New binding-equation branch** in `_eval_defining_eq` (6.B C5):
    detect regex on RHS, resolve, unify LHS with minimality-
    selected endpoint.
- **No grammar (`src/tgllfg/cfg/*.py`) changes in 6.B.** The
  grammar rules that produce regex-bearing equations land in
  6.D / 6.E / 6.F.

### 8.2 Module layout decision

The FSA compiler and traverser are non-trivial. Two options for
placement:

- **Inline in `unify.py`** — keep all FU machinery in one place;
  ~150-200 LOC additions.
- **New module `src/tgllfg/fstruct/fu.py`** — keep `unify.py`
  focused on orchestration; export the resolver.

**Decision: new module `src/tgllfg/fstruct/fu.py`.** Rationale:
the FSA machinery is orthogonal to the two-pass solver; carving
it out lets `unify.py` stay readable as the orchestration entry
point, and the FU module can grow (set-complement, defining-on-
regex if ever revisited) without crowding `unify.py`. The module
exports `resolve_regex_for_read(graph, designator, up, children)`;
`unify.py` consumes it.

Per `feedback_no_code_in_init`: `fstruct/__init__.py` re-exports
only; the new module's contents live in `fstruct/fu.py`.

### 8.3 Diagnostic kinds

No new diagnostic kinds needed; existing ones cover all cases:

- `constraint-failed` — regex resolution returns no endpoint, or
  the LHS doesn't match any endpoint.
- `existential-failed` — for `(↑ regex-path)` as a bare
  existential constraint, no endpoint found.
- The current `"deferred"` diagnostic for regex paths is
  **removed** in 6.B C2.

## 9. Test strategy

Three layers per `.claude/plans/tgllfg-testing-and-risks.md` §15
plus the Phase 6 plan §7.

### 9.1 Unit (FSA + resolver)

- FSA construction per element (literal, star, plus, alternation,
  concatenation).
- Traversal with synthetic FGraphs: single-step path, multi-step
  path, no-endpoint case, multiple-endpoint case.
- Visited-set termination on cyclic graphs (reentrant
  ComplexValues).
- Minimality: shortest-depth selection is deterministic.

### 9.2 Integration (K&Z fixtures)

- K&Z eq. 30: `(↑ TOPIC) = (↑ COMP* OBJ)` against synthetic
  embeddings at depths 1, 2, 3.
- K&Z eq. 38 (Icelandic adjunct island): demonstrate the body's
  filtering effect — paths through ADJ are blocked. (Not a
  Tagalog construction; sanity check of the FSA mechanism.)
- K&Z eq. 39 (English topicalization): the `{COMP | XCOMP}* SUBJ`
  body pattern — exercised via ``StarAltFeature(("COMP","XCOMP"))``
  (Phase 10.L); both the pre-10.L single-step approximation and
  the canonical Kleene form are kept as parallel fixtures to make
  the distinction explicit.

Tagalog integration tests land in 6.D (L47 LDD relativization),
6.E (L93 kung-S DP), 6.F (L104 sarili). 6.B's tests use synthetic
constructed FGraphs, not the parser.

### 9.3 Test-deferral flips

`tests/tgllfg/test_unification.py:488-491`:

- `test_star_path_emits_deferred`: flip from
  `assert any(d.kind == "deferred")` to asserting actual
  endpoint resolution.
- `test_plus_feature`: same flip.

The `"deferred"` diagnostic is removed from the legal `DiagKind`
inventory in 6.B C2 — no caller emits it after the FU resolver
lands. The `"deferred"` kind is repurposed-or-removed at C2's
discretion (likely removed; corpus has no other deferred path).

### 9.4 Property tests (Hypothesis)

Per plan §7.4:

- **Termination.** Every regex evaluation against a finite (even
  cyclic) FGraph terminates.
- **Minimality.** Shortest-string selection is canonical and
  deterministic.
- **Symmetry under rollback** (uses 6.A atomic unify). For
  binding equations: `unify(lhs, endpoint)` then rollback returns
  the graph to the pre-binding state; the resolver re-run yields
  the same endpoint list.

Property tests land in `tests/tgllfg/test_fu_evaluation.py`
(new file in 6.B C7).

## 10. References

- **Kaplan & Zaenen 1989.** "Long-Distance Dependencies,
  Constituent Structure, and Functional Uncertainty." In M.
  Baltin & A. Kroch (eds.), *Alternative Conceptions of Phrase
  Structure*. (Reprinted in Dalrymple et al. 1995, *Formal Issues
  in LFG*, CSLI Lecture Notes.) `data/tgl/references/Kaplan-Zaenen-1989-LSS-CStruct-FU.pdf`.
- **Kaplan & Maxwell 1988.** "An Algorithm for Functional
  Uncertainty." Proceedings of COLING-88.
- **Dalrymple 2001.** *Lexical Functional Grammar*. CSLI
  Publications. Ch. 14 (FU and LDD).
- **Schachter & Otanes 1972.** *Tagalog Reference Grammar*.
  University of California Press.
- **Ramos 1971.** *Tagalog Structures*. University of Hawaii Press.
- **Kroeger 1993.** *Phrase Structure and Grammatical Relations
  in Tagalog*. CSLI.
- **R&B 1986** — `data/tgl/references/` (per
  `reference_tagalog_pdf_resources` memory).

---

## 11. Post-implementation status (Phase 6.B → 6.J)

**Status: implemented and load-bearing across Phase 6.B–6.I.**

The design captured in §§1–9 landed in Phase 6.B (PR #38
``dad22c4``) as the FSA-based regex-path resolver in
``src/tgllfg/fstruct/fu.py`` with property tests in
``tests/tgllfg/test_fu_evaluation.py``. Phase 6.B's C5
binding-equation context (regex RHS + reentrant LHS) is the
load-bearing primitive used by:

- **Phase 6.D L47** — Long-distance relativization via
  ``(↓3 REL-PRO) =c (↓3 XCOMP* SUBJ)`` on the new
  S_XCOMP-bodied RC wraps in ``cfg/extraction.py``.
  Constraining-form (``=c``) implementation; defining-form
  was attempted but blocked by parent-first defining-pass
  timing (the body's ``(↑ SUBJ) = (↑ REL-PRO)`` hasn't run
  yet at the wrap's pass). Deferred-defining-FU recorded as
  Phase 7+ unifier extension.
- **Phase 6.E L93** — Free relative ``kung sino`` / ``kung
  ano`` as DPs uses an atomic-path lift (``(↑ WH_LEMMA) =
  ↓2 WH_LEMMA``) at depth 0, not FU. The Phase-6 dependency
  for 6.E is the Phase 6.C strict matcher, not the FU
  resolver.
- **Phase 6.F L104** — Reflexive ``sarili`` binding uses
  binding equations on matrix S rules (where ``↑`` is the
  matrix and the binder is directly accessible); inside-out
  FU designators (Dalrymple 2001 ch. 14) are not yet
  supported by ``resolve_regex_for_read`` and were deferred
  as Phase 7+ unifier extension.

The FSA resolver supports concatenation, ``F*``, ``F+``,
``F | G`` alternation, and off-path constraints as designed.
One out-of-scope item surfaced during 6.B C6: ``{F | G}*``
(Kleene on alternation) — not present in the current Tagalog
applications, parked as Phase 7+ AST extension (see
``tgllfg-out-of-scope.md`` §18.1.3).

K&Z 1989 §3 minimality clause is enforced (shortest-path
endpoint selection) and verified by property tests against
synthesized cyclic and acyclic f-graphs.

After Phase 6.J merges, the FU evaluator has been
load-bearing in production for ~6 weeks across 5 sub-PRs with
no performance regression or correctness issues.

**Phase 7+ unifier extensions** parked during Phase 6
(documented in ``tgllfg-out-of-scope.md`` §18.1.3):

- ~~FU deferred defining-equation evaluation~~ — closed by
  Phase 10.M via the re-pass mechanism described in §5.2.1.
- ~~FU inside-out designators~~ — closed by Phase 10.N via the
  ``FGraph.parents_via`` reverse-lookup + ``InsideOut`` base
  resolution described in §7.4.1.
- FU resolver-side cyclic-endpoint pruning (from 6.F).
- ``{F | G}*`` Kleene on alternation (from 6.B C6).
