# Functional-uncertainty evaluation

Phase 6.B design appendix per `.claude/plans/tgllfg-phase-6.md`
§5.2 C1. This document captures the regex-path semantics tgllfg
adopts for **functional uncertainty (FU)** equations, the FSA-
based decision procedure, the binding-vs-constraining contract,
and the Tagalog-specific calibrations. C2 onwards implement what's
specified here.

Cross-references:

- `docs/references/KZ89.pdf` — Kaplan & Zaenen 1989, "Long-Distance
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

A regex-path is a concatenation of these elements:
`(↑ F G* {H | I} J)` parses to a `Designator` with
`path = (Feature("F"), StarFeature("G"), AltFeature(("H","I")), Feature("J"))`.
Every element optionally carries off-path constraints (§6).

**Out of scope for 6.B:**

- **Set complement** (K&Z eq. 39's `(GF-COMP)` notation, "any GF
  except COMP"). The AST does not currently parse it. Corpus
  pressure may surface a need in Phase 6.D / 6.F; we defer the
  syntax extension until then.
- **Defining with regex on LHS**, e.g., `(↑ COMP* FOO) = 'X'`.
  The unifier would have to invent intermediate nodes for the
  unbounded `COMP*` traversal — semantically ill-defined in
  standard LFG. See §5.
- **Kleene applied to alternation** (`{F | G}*` / `{F | G}+`).
  The equation grammar treats `AltFeature` as a single
  `PathElement` and doesn't compose it with `*` / `+`. K&Z 1989
  eqs. 38 / 39 use this construction in their body alternations
  (e.g., `{COMP, XCOMP}*`); the Phase 6.B K&Z fixtures
  (`tests/tgllfg/test_fu_evaluation.py::TestKZFixturesParametrized`)
  approximate with single-feature bodies (`COMP*` / `XCOMP*`).
  AST extension is well-scoped but not motivated by any current
  Tagalog construction. See `tgllfg-out-of-scope.md` §18.1.3.

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
broader `{COMP, XCOMP}*` body is corpus-blocked pending real
data — we have not yet seen a Tagalog sentence requiring
cross-COMP relativization that isn't structurally ambiguous with
indirect speech.

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
- K&Z eq. 39 (English topicalization): the `{COMP, XCOMP}*` body
  pattern. (Sanity check.)

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
  in LFG*, CSLI Lecture Notes.) `docs/references/KZ89.pdf`.
- **Kaplan & Maxwell 1988.** "An Algorithm for Functional
  Uncertainty." Proceedings of COLING-88.
- **Dalrymple 2001.** *Lexical Functional Grammar*. CSLI
  Publications. Ch. 14 (FU and LDD).
- **Schachter & Otanes 1972.** *Tagalog Reference Grammar*.
  University of California Press.
- **Ramos 1971.** *Tagalog Structures*. University of Hawaii Press.
- **Kroeger 1993.** *Phrase Structure and Grammatical Relations
  in Tagalog*. CSLI.
- **R&B 1986** — `data/tgl/dictionaries/` (per
  `reference_tagalog_pdf_resources` memory).

---

**Status:** design appendix, awaiting user sign-off per Phase 6
plan §8.4 + `feedback_tgllfg_effort_protocol`. C2 onwards (FSA
implementation, wire-in, off-path eval, binding context, tests)
begin after sign-off.
