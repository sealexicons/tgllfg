# LexicalEntry YAML schema (Phase 5n.C.4 Commit 11)

This document specifies the YAML schema for the `data/tgl/lexicon/`
tree that will replace the in-Python `BASE` dict in
`src/tgllfg/core/lexicon.py`. The migration unblocks linguists who
need to add lex entries without editing Python source, and brings
the verb-frame inventory into agreement with the rest of the lex
data (verbs, particles, pronouns, paradigms, etc. all live under
`data/tgl/`).

C11 (this commit) is doc-only; C12 lands the loader and unit
fixtures; C13–C16 migrate the existing 29 `BASE` keys (94 entries)
out of Python into per-voice YAML files.

## Goals

1. **Move authoring out of Python source.** `BASE` currently mixes
   `_entry()` helper calls and direct `LexicalEntry(...)` calls for
   bespoke shapes. After the migration, every entry is a YAML record
   that the loader produces a `LexicalEntry` from.
2. **Keep the LMT intrinsic-profile constants in Python.** The
   `_AV_TR_AGENT_PATIENT` / `_OV_TR_AGENT_PATIENT` / `_DV_CAUS_DIRECT_THREE_ARG`
   etc. tables are *language-universal* Bresnan–Kanerva
   classifications, not Tagalog-specific lex content. YAML records
   reference them by symbolic name; the Python module stays the
   source of truth.
3. **Preserve every `morph_constraints` invariant** auto-filled by
   `_entry()`: `CAUS=NONE` by default, `APPL=CONVEY` for IV-bare,
   `APPL=NONE` otherwise, `TR=TR` for transitive entries.
4. **Round-trip-compatible:** YAML record → loader → `LexicalEntry`
   must match the existing `_entry()` / `LexicalEntry(...)` output
   for every current BASE entry. The migration is checked by a
   per-commit parity test (Commit 12) that compares loader output
   against `BASE` row-by-row until the BASE dict is removed.

## File layout

```text
data/tgl/lexicon/
  intransitive_av.yaml   — bare-AV intransitive entries (~25)
  plain_transitive.yaml  — AV / OV transitive entries (~80)
  applicative.yaml       — DV / IV / BV / LV entries (~50)
  causative.yaml         — pa- / magpa- causative entries + control
                           verbs + miscellany (~20)
```

The split is by **voice class**, mirroring the natural clusters in
the current `BASE` dict. The loader concatenates all four files into
a single `dict[str, list[LexicalEntry]]`, keyed by lemma, in
declaration order. (Order within a key matters for the analyzer:
the first entry whose `morph_constraints` match a MorphAnalysis is
chosen.)

## Record schema

A YAML file is a top-level **list** of LexicalEntry records.

```yaml
- lemma: kain
  voice: AV
  pred: "EAT <SUBJ>"
  a_structure: [ACTOR]
  gf_defaults:
    ACTOR: SUBJ
  transitive: false
  intrinsic: AV_INTR_ACTOR
```

### Required fields

| field | type | notes |
| --- | --- | --- |
| `lemma` | string | The bare root (`kain`, `bili`, `sigaw`). |
| `pred` | string | LFG PRED template. `EAT <SUBJ, OBJ>`. |
| `a_structure` | list[string] | Theta-role order. `[AGENT, PATIENT]`. |
| `gf_defaults` | map[string, string] | Role → GF default. `{AGENT: SUBJ, PATIENT: OBJ}`. |

### Optional fields

| field | type | default | notes |
| --- | --- | --- | --- |
| `voice` | enum | none | `AV`, `OV`, `DV`, `IV`, `BV`, `LV`. See note D below. |
| `transitive` | bool | `true` | When `false`, `morph_constraints` omits `TR`. |
| `intrinsic` | symbolic name | none | Reference to a Python intrinsic-profile constant. |
| `intrinsic_classification` | map[role, [±r, ±o]] | empty | Inline alternative; see note A below. |
| `extra_constraints` | map[string, string] | empty | Adds keys to auto-filled `morph_constraints`; see note B below. |
| `morph_constraints` | map[string, string] | none | Full override of auto-fill; see note C below. |

**Note A — `intrinsic_classification`:** inline alternative for one-off
shapes when no named profile fits. Tuples are `["+", "+"]` (`[+r, +o]`),
`["-", "-"]`, `["~", "~"]` (`(None, None)` — unspecified). At most
one of `intrinsic` / `intrinsic_classification` may be set.

**Note B — `extra_constraints`:** mag-…-an reciprocals use
`MOOD: SOC`; pa- causatives use `CAUS: DIRECT`; applicatives use
`APPL: BEN` / `APPL: INSTR` / `APPL: REASON`. Keys override the
auto-filled defaults below.

**Note C — `morph_constraints` (full override):** when present,
replaces the auto-fill entirely — the loader emits exactly the
keys listed here (plus the `VOICE` field when `voice` is
present, which must agree). Used by BEN / INSTR / REASON
applicative entries originally authored as bare
`LexicalEntry(...)` in `BASE` that intentionally under-specify
`CAUS` / `TR` for a looser analyzer match, and by pseudo-verb
control entries (gusto / ayaw / kaya / …) that carry no
morphological voice. Mutually exclusive with `extra_constraints`.

**Note D — `voice` is conditionally required.** Required when
`morph_constraints` is **absent** (the auto-fill path needs it).
Optional (and often omitted) when `morph_constraints` is
**present** — pseudo-verb control entries author the morph-
constraints directly with only `CTRL_CLASS` and have no
morphological voice to declare.

### Auto-filled `morph_constraints`

The loader emits a `morph_constraints` dict identical to what
`_entry()` produces today:

* `VOICE` = the `voice` field.
* `CAUS` = `NONE` by default; overridden by `extra_constraints`.
* `APPL` = `CONVEY` if `voice == "IV"` else `NONE`; overridden by
  `extra_constraints`.
* `TR` = `"TR"` if `transitive` (the default); omitted otherwise.
* Any keys in `extra_constraints` override or extend the above.

This keeps the YAML records terse — the bookkeeping that every
`_entry()` call repeats lives in the loader, not the data file.

## Intrinsic profile references

Phase 5 §8 LMT intrinsic profiles are language-universal Bresnan–
Kanerva `[±r, ±o]` patterns. The full set lives in
`src/tgllfg/core/lexicon.py` as module-level constants. YAML records
reference them by **symbolic name** (the constant's name minus the
leading underscore):

| YAML `intrinsic` value | Python constant | Description |
| --- | --- | --- |
| `AV_TR_AGENT_PATIENT` | `_AV_TR_AGENT_PATIENT` | AV transitive: AGENT pivot, PATIENT typed OBJ. |
| `AV_TR_AGENT_THEME` | `_AV_TR_AGENT_THEME` | AV transitive: AGENT pivot, THEME typed OBJ. |
| `OV_TR_AGENT_PATIENT` | `_OV_TR_AGENT_PATIENT` | OV transitive: PATIENT pivot, AGENT typed OBJ-AGENT. |
| `OV_TR_AGENT_THEME` | `_OV_TR_AGENT_THEME` | OV transitive: THEME pivot, AGENT typed OBJ-AGENT. |
| `DV_TR_AGENT_RECIPIENT` | `_DV_TR_AGENT_RECIPIENT` | DV transitive: RECIPIENT pivot. |
| `DV_TR_AGENT_PATIENT_RECIPIENT_THREE_ARG` | same | 3-arg DV ditransitive. |
| `IV_TR_AGENT_CONVEYED` | `_IV_TR_AGENT_CONVEYED` | IV transitive: CONVEYED pivot. |
| `IV_BEN_AGENT_BENEFICIARY` | `_IV_BEN_AGENT_BENEFICIARY` | IV benefactive. |
| `IV_BEN_AGENT_PATIENT_BENEFICIARY` | same | 3-arg IV benefactive. |
| `IV_INSTR_AGENT_INSTRUMENT` | `_IV_INSTR_AGENT_INSTRUMENT` | IV instrumental. |
| `IV_INSTR_AGENT_PATIENT_INSTRUMENT` | same | 3-arg IV instrumental. |
| `IV_REASON_AGENT_REASON` | `_IV_REASON_AGENT_REASON` | IV reason / cause. |
| `IV_REASON_AGENT_PATIENT_REASON` | same | 3-arg IV reason. |
| `AV_INTR_ACTOR` | `_AV_INTR_ACTOR` | AV intransitive, ACTOR pivot. |
| `AV_INTR_AGENT` | `_AV_INTR_AGENT` | AV intransitive, AGENT pivot. |
| `AV_INTR_ACTOR_LOCATION` | `_AV_INTR_ACTOR_LOCATION` | AV motion verb with sa-LOC. |
| `OV_CAUS_DIRECT` | `_OV_CAUS_DIRECT` | pa- OV direct causative. |
| `OV_CAUS_DIRECT_THREE_ARG` | same | 3-arg pa- OV causative. |
| `DV_CAUS_DIRECT` | `_DV_CAUS_DIRECT` | pa-…-an DV causative. |
| `DV_CAUS_DIRECT_THREE_ARG` | same | 3-arg pa-DV causative. |
| `AV_CAUS_INDIRECT` | `_AV_CAUS_INDIRECT` | magpa- indirect (biclausal) causative. |
| `PSYCH_CONTROL` | `_PSYCH_CONTROL` | Psych predicate control verb. |
| `INTRANS_CONTROL` | `_INTRANS_CONTROL` | Intransitive control verb. |
| `OV_TRANS_CONTROL` | `_OV_TRANS_CONTROL` | Transitive control verb (OV). |
| `DV_TRANS_CONTROL` | `_DV_TRANS_CONTROL` | Transitive control verb (DV). |

The loader looks up `intrinsic` by name in the lexicon module
(`getattr(lexicon, f"_{name}", None)`); an unknown name is a load-time
error pointing at the YAML record's file path and index.

## Worked examples

### Simple AV-intransitive + AV-transitive + OV-transitive

The `kain` "eat" lemma currently in `BASE`:

```yaml
- lemma: kain
  voice: AV
  pred: "EAT <SUBJ>"
  a_structure: [ACTOR]
  gf_defaults: {ACTOR: SUBJ}
  transitive: false
  intrinsic: AV_INTR_ACTOR

- lemma: kain
  voice: AV
  pred: "EAT <SUBJ, OBJ>"
  a_structure: [AGENT, PATIENT]
  gf_defaults: {AGENT: SUBJ, PATIENT: OBJ}
  intrinsic: AV_TR_AGENT_PATIENT

- lemma: kain
  voice: OV
  pred: "EAT <SUBJ, OBJ-AGENT>"
  a_structure: [AGENT, PATIENT]
  gf_defaults: {PATIENT: SUBJ, AGENT: OBJ-AGENT}
  intrinsic: OV_TR_AGENT_PATIENT
```

### mag-…-an reciprocal with extra `MOOD: SOC`

```yaml
- lemma: kain
  voice: AV
  pred: "EAT-TOGETHER <SUBJ>"
  a_structure: [ACTOR]
  gf_defaults: {ACTOR: SUBJ}
  transitive: false
  extra_constraints:
    MOOD: SOC
  intrinsic: AV_INTR_ACTOR
```

### pa- causative with explicit `CAUS: DIRECT`

```yaml
- lemma: kain
  voice: OV
  pred: "FEED <SUBJ, OBJ-CAUSER>"
  a_structure: [CAUSER, CAUSEE]
  gf_defaults: {CAUSEE: SUBJ, CAUSER: OBJ-CAUSER}
  extra_constraints:
    CAUS: DIRECT
  intrinsic: OV_CAUS_DIRECT
```

### IV benefactive with explicit `APPL: BEN`

```yaml
- lemma: bili
  voice: IV
  pred: "BUY <SUBJ, OBJ-AGENT>"
  a_structure: [AGENT, BENEFICIARY]
  gf_defaults: {BENEFICIARY: SUBJ, AGENT: OBJ-AGENT}
  extra_constraints:
    APPL: BEN
  intrinsic: IV_BEN_AGENT_BENEFICIARY
```

### Explicit `morph_constraints` override (looser match)

The BEN / INSTR / REASON applicatives in `BASE` were originally
authored as bare `LexicalEntry(...)` calls (not via the `_entry()`
helper) with minimal `morph_constraints = {VOICE: IV, APPL: BEN}`
— deliberately under-specified so the analyzer matches any CAUS
and any TR value:

```yaml
- lemma: bili
  voice: IV
  pred: "BUY-FOR <SUBJ, OBJ-AGENT>"
  a_structure: [AGENT, BENEFICIARY]
  gf_defaults: {BENEFICIARY: SUBJ, AGENT: OBJ-AGENT}
  morph_constraints:
    APPL: BEN
  intrinsic: IV_BEN_AGENT_BENEFICIARY
```

The loader emits `{VOICE: IV, APPL: BEN}` exactly — no auto-fill.
Mutually exclusive with `extra_constraints`.

### Pseudo-verb control entry (no `voice`)

Control verbs like `gusto` "want" have no morphological voice —
they're uninflected pseudo-verbs. The YAML record omits `voice`
entirely and authors `morph_constraints` directly with only the
`CTRL_CLASS` distinguisher:

```yaml
- lemma: gusto
  pred: "WANT <SUBJ, XCOMP>"
  a_structure: [EXPERIENCER, COMPLEMENT]
  gf_defaults: {EXPERIENCER: SUBJ, COMPLEMENT: XCOMP}
  morph_constraints:
    CTRL_CLASS: PSYCH
  intrinsic: PSYCH_CONTROL
```

The loader emits exactly `{CTRL_CLASS: PSYCH}` — no auto-filled
VOICE / CAUS / APPL / TR keys, matching the analyzer's
expectation for psych pseudo-verbs.

### Inline intrinsic for a one-off shape

When no named profile fits (rare; the inventory above covers
everything currently in `BASE`):

```yaml
- lemma: someverb
  voice: AV
  pred: "FOO <SUBJ>"
  a_structure: [EXPERIENCER]
  gf_defaults: {EXPERIENCER: SUBJ}
  transitive: false
  intrinsic_classification:
    EXPERIENCER: ["-", "-"]
```

## Loader contract (C12)

* New module: `src/tgllfg/core/lexicon_loader.py`.
* Public API: `load_lex_entries(data_dir: Path | None = None) -> dict[str, list[LexicalEntry]]`.
* Reads the four YAML files in deterministic order (intransitive →
  plain → applicative → causative); within each file, declaration
  order is preserved.
* Per-record validation:
  * All required fields present; missing fields raise `ValueError`
    with file path + record index.
  * `voice` is one of the legal enum values.
  * At most one of `intrinsic` / `intrinsic_classification`.
  * `intrinsic` (if given) resolves to a known profile constant.
  * `a_structure` matches `gf_defaults` keys exactly (every theta
    role gets a default; no orphan defaults).
* Returns a dict keyed by lemma; each value is a list of
  `LexicalEntry` records in source order.

## Migration parity check (C12)

A new postgres-free test asserts:

```python
from tgllfg.core.lexicon import BASE
from tgllfg.core.lexicon_loader import load_lex_entries

loaded = load_lex_entries()
for lemma, base_entries in BASE.items():
    yaml_entries = loaded.get(lemma, [])
    assert yaml_entries == base_entries, lemma
```

The test starts empty (no YAML entries yet); each per-voice
migration commit (C13–C16) moves entries out of `BASE` and into
the YAML files, and the parity test grows naturally as the YAML
covers more lemmas. The test passes when every BASE entry has a
YAML counterpart and the two outputs match row-by-row.

## Migration scope (C13–C16)

Current `BASE` has 29 lemma keys with 94 entries total
(`grep -c "_entry(" lexicon.py` = 34 + `grep -c "LexicalEntry("` = 57,
ignoring the synthesize fallback at the bottom).

| Commit | Voice class | Approximate count |
| --- | --- | --- |
| C13 | intransitive AV (`payag`, `pilit`, `lakad`, etc.) | ~25 |
| C14 | plain transitive AV / OV (`kain`, `bili`, `sulat`, `tapon`, `sigaw`, `tawag`, `gawa`, `basa`, …) | ~40 |
| C15 | applicative DV / IV / BV / LV (`bigay`, `sulat-DV`, `sulat-IV`, `bili-IV`, …) | ~20 |
| C16 | causative pa- / magpa- + control + miscellany | ~15 |

Counts are approximate — the migration script in each commit
emits a per-file count for the commit body.

## Open question: control verbs

The control-verb entries (`gusto`, `ayaw`, `kaya`, `puwede`,
`maaari`, `kailangan`, `payag`, `pilit`, …) currently live in
`BASE` even though some are pseudo-verbs with no inflection (seeded
under `particles.yaml` for the surface-level lookup but with their
`LexicalEntry` shape pinned in `BASE`). Open question: should the
psych pseudo-verbs migrate to `lexicon/causative.yaml` alongside
the morphologically-inflected control verbs, or to a dedicated
`lexicon/control.yaml`?

**Recommendation:** dedicated `lexicon/control.yaml` — it isolates
the SUBJ-control / XCOMP shape from the causative inventory, and
keeps the audit trail intact (the control-verb section in `BASE`
is already a contiguous block that can move whole-cloth).

## Forward-looking notes

* **Per-sense feats integration.** Phase 5n.C.4 introduced
  `lemma_sense.feats` on the DB side. A future enhancement could
  let YAML records key on `(lemma, sense_index)` so that polysemous
  entries (`kuwarto` ROOM vs. FRACTION) get sense-specific lex
  entries. Out of scope for C11–C16; in scope for a Phase 6+
  follow-on.
* **Loader strictness vs. tolerance.** The loader rejects unknown
  fields by default. Linguists adding new entries get a clear
  parser error rather than a silent ignore. This is a deliberate
  contract — silent ignores have bitten the codebase before
  (`yes`/`true` collation in YAML 1.1, etc.).
