<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Binary feats audit (Phase 5n.C.4 Commit 2)

This audit underpins the YES/NO → bool sentinel migration that lands
across Phase 5n.C.4 commits C3-C8. It identifies which f-structure
feats are *truly binary* (and therefore migration targets) versus
*enum-valued* (and therefore must be preserved as strings).

## Methodology

A scan over `data/tgl/*.yaml`, `src/tgllfg/**/*.py`, and
`tests/**/*.py` collected the value-set of every all-caps feat name
that takes at least one of `{YES, NO, true, True, false, False}`.
Each feat was then categorized:

* **binary** — the observed value-set is a subset of
  `{YES, NO, true, false}`. These are migration targets.
* **enum-with-binary** — the value-set includes one of the binary
  literals *and* other non-binary values (e.g., `INDEF` takes both
  `YES` and `NEG_INDEF`). These need manual inspection.
* **enum** — non-binary values only (e.g., `Q_TYPE` takes `YES_NO`,
  `WH`, `TAG`, etc.; the literal `YES` never appears as a standalone
  value). Preserved.

False positives from the audit regex were filtered by hand
inspection: comment text containing capitalized words followed by
`:` or `=` can match the pattern (e.g., `WH: polysemy` from a
`# wh-Q polysemy ...` comment), and prefix-matching artifacts
(`RESULT` matched a value `result` from prose) are dropped.

## The 55 binary feats — migration targets

Subsequent phases extended the inventory: 9.O.3 (+1), 9.O.4 (+1),
9.O.5 (+1), 9.X.c11 (+1), 9.X.c19 (+1), 9.X.c22 (+1), 9.X.c49 (+1),
9.X.post-2 (+1), 10.E.1 (+1), 10.G (+1) → 65 total.
Each extension is documented inline below.

Every entry below is migrated from string-sentinel `YES`/`NO` to
Python `True`/`False`. Grammar rule patterns use the `[X]` shorthand
for `[X=true]` (LFG-canonical) and explicit `[X=false]` for the
negative.

| feat | role |
| --- | --- |
| `APPROX` | NP is an approximator (e.g., `mga`) |
| `ASK_CLASS` | verb is in the "ask"-class for indirect Q complementizer |
| `CARDINAL` | NUM is a cardinal numeral |
| `CF` | clause is counterfactual (subj of `sakali` / `kahit pa`) |
| `CLOCK_MARKER` | PART is the clock-time hour marker (`alas`) |
| `COMPARATIVE` | ADJ is comparative-marked (`mas`) |
| `COPULA` | V is a copular verb (`maging` / `naging`; gates `V[COPULA] N/ADJ NP[NOM]` clause rule, Phase 9.X.post-2) |
| `CORREL` | particle is correlative (`pa` / `pa-rin` paired use) |
| `COUNTERFACTUAL` | post-pass conditional inference |
| `DECIMAL` | NUM is decimal-form |
| `DECIMAL_SEP` | particle is a decimal separator (point/comma) |
| `DEM` | particle/PRON is demonstrative (`ito` / `iyan` / ...) |
| `DEPICTIVE` | secondary predicate is depictive-licensed |
| `DIGIT_FORM` | NUM surfaces as digit form (`1` vs `isa`) |
| `DISCOURSE_EMPH` | discourse-emphasis marker |
| `DISTRIB` | NUM/Q is distributive (`tig-`) |
| `DISTRIB_POSS` | distributive possessive (`kanya-kanya`) |
| `DUAL` | dual marker (`pareho`, `dalawa`) |
| `ELLIPSIS` | clause has elided / contextually-recoverable subject (`Wala pa.`; 9.X.c22 bare wala) |
| `EMPHATIC` | clause carries emphasis |
| `EQUATIVE` | ADJ is equative (`kasingganda`) |
| `EXCLAM` | `ang`-exclamative predication (`Ang ganda-ganda mo!`) — Phase 10.E.1 |
| `EXISTENTIAL` | clause is existential (`may`, `mayroon`) |
| `EXTRACTED` | NP-of-extraction marker |
| `FOCUS_NEG` | Ni-focus-negation construction marker (Phase 8.V) |
| `FRAGMENT_HOST` | clause licenses NP-fragment answers |
| `FREE_REL` | NP is a free-relative kung-S head (Phase 6.E) |
| `GAPPING` | matrix carries a gapping conjunction |
| `HAVE` | possessive predicate marker |
| `HUMAN` | NP/PRON is human-class |
| `IMPERSONAL` | predicate licenses bare-S with synth PRO SUBJ (weather `umulan`; atmospheric ADJs `mainit`; 9.X.c49) |
| `INTENSIFIER` | particle is an intensifier (`talagang`) |
| `INTERJ` | element is an interjection |
| `KA_PRED` | N is a ka-N companion-predicate (`kasama` / `kasabay`; 9.X.c19; gates ka-N S_GAP rule) |
| `KASING_N` | ADJ surface derives from a NOUN via `kasing-` (Phase 8.L) |
| `KITA` | special clitic pronoun `kita` |
| `LEXICALIZED` | surface is a frozen / lexicalized reduplication, not productively derived (Phase 10.G) |
| `LOC_EXISTENTIAL` | locative existential reading |
| `MAGISA` | "alone" emphatic predicate |
| `MEASURE` | NP is a measure phrase |
| `MGA_INTERNAL` | N is marked by `mga` via the N-level rule (9.X.c11; simple-NP-rule disambiguation tag) |
| `MIRATIVE` | particle is mirative |
| `MODAL` | clause carries a modal head |
| `MODAL_STANDALONE` | modal is non-complement-taking standalone |
| `N_RC` | N is an N-level-RC head (Phase 6.G; tag for the simple-NP-rule disambiguation) |
| `NEG_TAG` | clause is a negative tag-Q |
| `ORDINAL` | NUM is ordinal (`pang-`) |
| `ORTHOGRAPHIC_TERMINATOR` | sentence-final punctuation |
| `PANG_DERIVED` | NOUN is `pang-` derived |
| `PLURAL_MARKER` | particle is plural marker (`mga`) |
| `PREDICATIVE` | ADJ is in predicative position |
| `QUESTION` | particle is a question marker (`ba`) |
| `RECP` | verb is reciprocal |
| `RESULTATIVE` | ADJ is resultative |
| `SAY_CLASS` | verb is in the "say"-class |
| `SEQUENCE` | clause is in a temporal sequence |
| `SYMBOLIC` | particle is symbolic (mathematical operator) |
| `UNCERTAIN` | particle carries uncertainty (`siguro`, `marahil`) |
| `UNIV` | universal Q (`bawat`, `lahat`) |
| `VAGUE` | Q is vague (`ilang`) |
| `WH` | element is wh-marked |
| `WHOLE` | NP-of-the-whole reading |

## Enum feats — preserved as strings

These feats carry one of multiple enum values and must **not** be
migrated. The migration tooling rejects shorthand `[X]` on these
feats and preserves any quoted `"YES"` occurrences as enum strings.

| feat | sample values | notes |
| --- | --- | --- |
| `INDEF` | `YES`, `NEG_INDEF` | see note A below |
| `PRED` | `EAT`, `BE-N`, `YES`, `EXIST`, …(20+) | see note B below |
| `Q_TYPE` | `YES_NO`, `WH`, `TAG` | Q-type enum. `YES_NO` is one value, not "boolean YES_NO". |
| `NUM` | `SG`, `PL`, `DU` | grammatical number |
| `CASE` | `NOM`, `GEN`, `DAT` | grammatical case |
| `ASPECT` | `PFV`, `IPFV`, `PROSP`, `IRR` | grammatical aspect |
| `MOOD` | `IND`, `IMP`, `SUB`, `SOC` | grammatical mood |
| `VOICE` | `AV`, `OV`, `DV`, `IV`, `BV`, `LV` | LFG voice / LMT applicative |
| `CARDINAL_VALUE` | `"1"` / `"2"` / ... | numeric string payload |
| `REGISTER` | `POLITE`, `COLLOQUIAL_POLITE`, `LITERARY` | register tag |

**Note A — `INDEF`:** `YES` here is a generic-indefinite *enum tag*,
not a boolean. Future refactor candidate: rename `YES` → `PLAIN` for
clarity, but out of scope for this migration.

**Note B — `PRED`:** LFG predicate names. `PRED: "YES"` on the
affirmative-answer PRONs (`oo`, `opo`, `oho`) is the literal English
predicate "yes", not a boolean.

## False positives filtered out

* `RESULT` — regex artifact; the real feat is `RESULTATIVE`.
* `WH: polysemy` — comment-word artifact; `WH` is binary.

## Migration mechanics (forward reference)

* **C3** — grammar compiler accepts `true`/`false` bool literals in
  category patterns and constraining equations. Adds the `[X]`
  shorthand for `X` in `BINARY_FEATS`; rejects shorthand on enum
  feats. Keeps `YES`/`NO` as temporary aliases.
* **C4** — `src/` analyzer/placement/pipeline switches to `True` /
  `False` Python bools.
* **C5** — `cfg/*.py` rule strings migrate (`PART[X=YES]` →
  `PART[X]`, `=c 'YES'` → `=c true`).
* **C6** — YAML data sweep (~465 occurrences). Scripted, gated by
  `BINARY_FEATS`; mismatches halt the script.
* **C7** — tests sweep (~286 occurrences). Scripted with hand
  audit.
* **C8** — `YES`/`NO` aliases removed from the compiler. Bool-only
  contract.

The machine-readable counterpart of this audit lives at
`src/tgllfg/core/feats.py`.
