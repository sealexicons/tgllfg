<!--
Copyright (c) 2025-2026 G & R Associates LLC
SPDX-License-Identifier: MIT OR Apache-2.0
-->

# Root YAML metadata fields (Phase 9.C.pre)

Root entries in `data/tgl/nouns.yaml`, `verbs.yaml`, `adjectives.yaml`
carry per-entry metadata that doesn't drive parsing but supports
auditing, documentation, and downstream tooling. Phase 9.C.pre
formalises four metadata fields that previously lived in gloss
parentheticals as free text.

The loader (`src/tgllfg/morph/loader.py:_load_roots`) reads and
validates these fields against closed enums; typos fail-fast with
a `ValueError` quoting the file + record index.

## Fields

### `subclass:` — list of orthogonal-axis tags

Two axes, each optional:

- **Named-entity** (at most one): `PERSON` / `SURNAME` / `PLACE` /
  `LANGUAGE` / `NATIONAL`. Applies to proper / place / language /
  nationality nouns.
- **Gender** (at most one): `MALE` / `FEMALE`. Used only when
  morphology actually distinguishes (Spanish-loan `-o`/`-a` pairs).

Always emitted as a YAML list, even singletons (matches the
existing `affix_class:` convention).

```yaml
subclass: [PERSON, MALE]      # Western personal name, male
subclass: [PERSON, FEMALE]    # personal name, female
subclass: [PLACE]             # place name (no gender)
subclass: [NATIONAL, FEMALE]  # gendered nationality
subclass: [LANGUAGE]          # language name
```

Omit for common nouns.

### `source:` — short-code citation

Closed enum:

- `S&O-1972` — Schachter & Otanes 1972
- `R&C-1990` — Ramos & Cena 1990
- `R&G-Intermediate` — Ramos & Goulet 1981 *Intermediate Tagalog*
- `R&G-Conversational` — Ramos & Goulet 1981 *Conversational Tagalog*
- `Ramos-1971` — Ramos 1971 dictionary
- `rg81-transcriptions` — hand-transcribed R&G 1981 excerpts
- `audit-corpus` — generic Phase 8/9 audit harvest attribution
- `ref-grammar` — generic Tagalog-grammar attribution for entries
  with no audit-corpus pressure

Section anchors (e.g., `§7.20`) are dropped — git blame + the
source-grammar PDF/transcription serve as the canonical locator.

Omit for entries with no specific provenance.

### `loan:` — loan-source language

Closed enum: `SPANISH` / `ENGLISH`. Extensible (CHINESE, MALAY,
ARABIC plausibly future). Omit for native Tagalog.

```yaml
loan: SPANISH    # relos "watch", kuwarto "quarter", amerikana
loan: ENGLISH    # boss, party
```

### `orth_variants:` — list of alternate surfaces / OCR variants

Strings indexed by the analyzer as alternate surfaces pointing at
the canonical lemma (`citation:`). Mirrors the orthographic-variant
LEMMA-pointer pattern documented in
`.claude/projects/.../feedback_orthographic_variants.md`.

```yaml
- citation: blas
  pos: NOUN
  gloss: Blas
  subclass: [PERSON, MALE]
  source: R&C-1990
  orth_variants: [bias]    # OCR'd form

- citation: tita
  pos: NOUN
  gloss: aunt
  orth_variants: [tiya]    # spelling variant
```

## Register annotations

Register annotations (FORMAL / INFORMAL / COLLOQUIAL / AFFECTIVE)
go in the existing `feats:` mapping under the `REGISTER` key, not
as a separate field. REGISTER is grammatically operative (Phase 7a
added `REGISTER=COLLOQUIAL` for `po`/`ho`/`opo` discourse-particle
parses); FORMAL / AFFECTIVE values are new in 9.C.pre.

```yaml
- citation: ama
  pos: NOUN
  gloss: father
  feats: {REGISTER: FORMAL}

- citation: itay
  pos: NOUN
  gloss: father
  feats: {REGISTER: AFFECTIVE}

- citation: eskwela
  pos: NOUN
  gloss: school
  feats: {REGISTER: COLLOQUIAL}
  synonyms: [paaralan]
```

## Polysemy: split into multiple entries

Polysemous lemmas where senses have distinct sub-classes get one
entry per sense. The lex loader supports multi-entry citations
already — `kuwarto` has two entries differing only by
`SEM_CLASS` feat (general "quarter" vs clock-time fraction).
When a new audit hit attests a distinct sense for an existing
lemma, add a second entry rather than overloading the first.

Add new sense-split entries only when the sense is audit-attested
(`feedback_audit_before_scheduling` discipline). Speculative
senses go in the follow-on backlog.

## Gloss content rule

The `gloss:` field carries the bare English translation only.
Metadata that used to live in parentheticals (proper-name flag,
source citation, loanword status, register) migrates into the
structured fields above. Genuine disambiguation in the gloss
(e.g., `fly (insect)`, `nail (finger / toe)`) stays — those are
semantic specifications, not metadata.

## Schema validation

The loader validates:

- `subclass:` atoms are in the named-entity ∪ gender enum.
- At most one named-entity tag and at most one gender tag per
  entry (no `[PERSON, PLACE]` or `[MALE, FEMALE]` combinations).
- `source:` is in the source short-code enum.
- `loan:` is in the loan-language enum.
- `orth_variants:` is a list.

Any violation raises `ValueError` with the file path and record
index. To extend an enum, edit the corresponding `frozenset` in
`src/tgllfg/morph/loader.py` (`_SUBCLASS_NAMED_ENTITY`,
`_SUBCLASS_GENDER`, `_SOURCE_ALLOWED`, `_LOAN_ALLOWED`).

## Scope

Phase 9.C.pre migrated the 74 `data/tgl/nouns.yaml` entries
with parenthetical metadata. `adjectives.yaml`, `verbs.yaml`,
`particles.yaml`, `pronouns.yaml` retain their previous conventions
until a future sub-PR migrates them — the loader accepts the new
fields uniformly, so future migrations don't need loader changes.
