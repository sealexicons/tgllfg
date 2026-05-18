# Phase 9.X.pre-1 — lex-sweep closure snapshot

> **Status:** Phase 9.X.pre-1 closure snapshot. Lex-only sweep
> against the **seeded 2327-sentence audit baseline** carried over
> from Phase 9.W. No grammar/parser changes (apart from the c19
> harvester engineering and the c21 orth-variants migration —
> both lex-loader-internal); all parse-rate gains here trace to
> additional lex entries that close OOV-blocked sentences.

## 1. Headline numbers

| | Pre-9.X.pre-1 (post-9.W) | Post-9.X.pre-1.30 | Delta |
| --- | ---: | ---: | ---: |
| Seeded xwave (2327 sents) | **391 / 2327 = 16.80%** | **524 / 2327 = 22.52%** | **+133 abs / +5.72pp** |

Per-wave breakdown:

| Wave | Pre | Post | Δ abs | Δ pp |
| --- | ---: | ---: | ---: | ---: |
| Wave 1 (rg81 transcriptions, 118 sents) | 40 (33.90%) | 44 (37.29%) | +4 | +3.39pp |
| Wave 2 — R&C 1990 (500 sents) | 58 (11.60%) | 66 (13.20%) | +8 | +1.60pp |
| Wave 2 — R&G Intermediate (500 sents) | 64 (12.80%) | 77 (15.40%) | +13 | +2.60pp |
| Wave 2 — Ramos 1971 (209 sents) | 45 (21.53%) | 51 (24.40%) | +6 | +2.87pp |
| Wave 3 — S&O 1972 (500 sents) | 95 (19.00%) | 99 (19.80%) | +4 | +0.80pp |
| Wave 3 — R&G Conversational (500 sents) | 174 (34.80%) | 187 (37.40%) | +13 | +2.60pp |
| **Cumulative** | **391 (16.80%)** | **524 (22.52%)** | **+133** | **+5.72pp** |

Largest single-wave gains: R&G Intermediate and R&G Conversational
(+13 abs each — both prose-heavy waves where common-Tagalog lex
inventory dominates the OOV pool). Smallest: S&O 1972 (+4 abs —
already had higher pre-sweep baseline; remaining failure mass is
grammar/paradigm-cell-bound).

## 2. Scope and motivation

Phase 9.U's diagnostic deep-dive flagged commit-9.X.pre-1 as
"optional" — projected yield was a handful of single-OOV
closures (gitna / ibabaw / halaga / ilaw / masama / samantalang).
The actual scope grew substantially during execution as the
audit OOV pool revealed a much broader common-Tagalog inventory
gap: **~525 new lex entries** across 29 commits over 2 sessions
spanning 2026-05-17 evening through 2026-05-18 afternoon.

The scope grew because the seeded 2327-sentence audit corpus is
prose-heavy across R&G / R&C / Ramos / S&O sources — and once the
top-100 OOV terms were closed (commits 1-18), additional 1-2-sent
items still added measurable parse-rate yield from the broader
naturalistic-tier prose.

## 3. Commit map

29 commits land lex / engineering changes; commit numbering has
a gap at c20 (bundled into c21).

<!-- markdownlint-disable MD013 -->

| # | Type | Entries | Body |
| --- | --- | ---: | --- |
| c1 | NOUN | 13 | ADJ-root NOUN parallels (13 entries) |
| c2 | NOUN | 28 | common-Tagalog NOUN batch 1 |
| c3 | NOUN | 30 | common-Tagalog NOUN batch 2 |
| c4 | NOUN | 44 | common-Tagalog NOUN batch 3 |
| c5 | NOUN | 41 | common-Tagalog NOUN batch 4 |
| c6 | NOUN | 29 | food + everyday NOUN sweep |
| c7 | NOUN | 11 | more Filipino food NOUNs |
| c8 | ADJ | 16 | common-Tagalog ADJ new roots |
| c9 | VERB | 10 | common-Tagalog VERB new roots (galit revert per 5n.A C1) |
| c10 | VERB | 19 | VERB batch 2 |
| c11 | PART/ADV | 11 | discourse + adverbial particles |
| c12 | VERB | 20 | VERB batch 3 |
| c13 | VERB | 25 | VERB batch 4 |
| c14 | NOUN | 15 | abstract / conceptual NOUNs |
| c15 | NOUN+ADJ | 11 | NOUN + bare-form ADJ mix |
| c16 | VERB | 17 | VERB batch 5 |
| c17 | VERB | 13 | VERB batch 6 |
| c18 | mixed | 22 | abstract NOUNs + VERBs + ADJs; first audit re-measurement (`391 → 476` post-c18) |
| c19 | engineering | — | harvester per-item SIGALRM timeout + live monitoring |
| c20 (bundled) | NOUN | 9 | honorifics + NOUN parallels (binibini / ginang / ginoo / misis / mister / mr / mrs / punla / sabi) — landed inside c21 |
| c21 | engineering | — | orth-variants migration: `feats: {LEMMA: X}` sole canonical; dead `orth_variants` field removed from `Root` + loader + tests |
| c22 | mixed | 5 | maghapon / tapat / nais / kumbidado / tahimik + OOV-pin re-anchor (kumbidado → gawin) |
| c23 | VERB | 14 | VERB-root tail batch 7 — 9 new-root + 5 POS-flip (gulat/hirap/palagay/punla/ulan) |
| c24 | VERB | 14 | VERB-root tail batch 8 — 8 affix-class extensions + 4 new-root + 2 POS-flip (ani/pinsala); 1 pin flip in 8.F naisip |
| c25 | VERB | 11 | VERB-root tail batch 9 — 9 affix-class extensions + 2 new-root (mahal/una); 1 test fixture swap (kain→dating um-only) |
| c26 | NOUN | 30 | NOUN tail batch 1 |
| c27 | NOUN | 29 | NOUN tail batch 2 (10 strict-audit + 19 defensive — scope clarified mid-review) |
| c28 | NOUN | 1 | purok follow-on (distinct lexeme from c27 pook per review) |
| c29 | NOUN | 17 | NOUN tail batch 3 — strict-audit + purok gloss enrichment (postal-addressing usage) |
| c30 | ADJ + PART | 22 | ADJ + PART/ADV tail (16 ADJ + 6 PART/ADV; ma_adj inventory 58 → 64) |

<!-- markdownlint-enable MD013 -->

**Total**: ~525 new lex entries across the four YAML files plus
the c19 / c21 engineering changes.

## 4. Files touched

Per file:

- **`data/tgl/nouns.yaml`** — ~245 new NOUN entries; tightening of
  4 metadata fields (`source: audit-corpus`, `loan: SPANISH|ENGLISH`,
  `feats: {LEMMA: X}` for orth-variants); duplicate `kuwarto` noted
  but not addressed (out of scope for pre-1).
- **`data/tgl/verbs.yaml`** — ~115 new VERB entries (across 9
  numbered VERB batches in c9 / c10 / c12 / c13 / c16 / c17 / c23
  / c24 / c25) plus 17 affix-class extensions on existing entries
  (c24 + c25).
- **`data/tgl/adjectives.yaml`** — ~30 new ADJ entries (c8 + c30);
  ma_adj-opting inventory grew from 48 → 64 across pre-1 (c8 added
  9, c18 added 1 sagana, c30 added 6).
- **`data/tgl/particles.yaml`** — 17 new PART/ADV/INTERJ entries
  (c11 added 11; c30 added 6).
- **`scripts/harvest_exemplars.py`** — c19 engineering: SIGALRM
  per-item timeout (`ITEM_TIMEOUT_S=10s`), `latency_s` field on
  `ParseRecord`, live monitoring at `/tmp/audit_monitor.log`,
  hang-detection via `/tmp/audit_monitor.last_item`. Per-25-item
  progress logging with min/avg/max latency.
- **`src/tgllfg/morph/paradigms.py`** — c21: removed dead
  `orth_variants` field from `Root` dataclass.
- **`src/tgllfg/morph/loader.py`** — c21: removed
  `orth_variants_raw` load path; added rejection error if any
  remaining YAML uses the `orth_variants:` key (migration check).
- **`tests/tgllfg/test_phase5g_adj_inventory.py`** — ma_adj count
  bumps: 48 → 57 (c8 +9) → 58 (c18 +sagana) → 64 (c30 +6).
- **`tests/tgllfg/test_phase9c_pre_nouns_metadata.py`** — c21
  test-class migration: `TestOrthVariants` rewritten to check
  `feats.LEMMA` on variant root entries; `test_orth_variants_must_be_list`
  → `test_orth_variants_field_removed` (now asserts rejection).
- **`tests/tgllfg/test_phase8q_oov_probe.py`** — c22 OOV-probe
  anti-deferral pin chain extended: kumbidado → **gawin** (the
  in_oblig imperative cell on `gawa` is a paradigm-cell gap; the
  pin re-anchors on a surface that pre-4 will close).
- **`tests/tgllfg/test_morph.py`** — c25: swap um-only test
  example from `kain` (no longer um-only after c25's kain+mag
  extension) to `dating` (still um-only).
- **`tests/tgllfg/test_phase8f_may_v_headed.py`** — c24 pin flip:
  `test_oov_verb_form_naisip` flipped from "OOV / zero parse" to
  "≥1 parse" after the c24 isip+ma affix-class extension closes
  the `naisip` surface.

## 5. Audit-OOV pool dynamics

Pre-1 entry numbers and OOV-pool numbers don't match 1-to-1
because:

1. Most c2-c18 entries were drawn from the top-200 OOV by
   frequency; the highest-frequency entries (≥4 sents) cleared
   first, with diminishing per-entry yield as the sweep moved
   into the 1-2-sent tail.
2. c27 contained 19 defensive entries that weren't audit-attested
   (called out in review). C29 and later returned to strict
   audit-attestation discipline.
3. ~50 of the ~525 entries are POS-flip / affix-class extensions
   that close audit surfaces without adding a new root citation
   per se — e.g. `gulat(ADJ) + gulat(VERB)` pattern.

Three audit-OOV categories were split off as follow-on tasks:

- **9.X.pre-2** — proper names + English-loan handling (~30 proper
  names + 25 English loans). Defensive lex inventory + grammar
  decisions on code-switch handling.
- **9.X.pre-3** — OCR-source cleanup (~60 OCR-artifact OOVs;
  resolution by fixing source `.txt` transcriptions rather than
  polluting the lex). Per `feedback_ocr_eyeball_pdf` convention.
- **9.X.pre-4** — paradigm-cell engineering (~700-900 paradigm-cell
  gaps where roots ARE in lex but specific inflection cells
  don't generate the surface). Examples: `gawin` /
  `kunin` / `hiwain` / `itapon` / `ituro` / `hugasan` / `pakiabot`
  / `nasaan` / `pag-aaral` / `maliliit` / `naging` / `minamahal`
  (m-initial `-in-` infix bug) / `mauna` (bare-IMP cell on ma-
  affix). Paradigm-engine extension work, not lex work; pre-1
  anchors the OOV-probe pin chain at `gawin` so this work stays
  visible in pre-1 test output.

## 6. Conventions tightened during pre-1

The 30-commit sweep surfaced (and the user-flagged review
process reinforced) several lex conventions worth recording
here for future sub-PRs:

- **Audit-attestation as the lex-add gate.** When in doubt, an
  audit-OOV hit is the green light; speculative inventory adds
  belong in a different scope. (See c27 review.)
- **Orthographic variants** use `feats: {LEMMA: <canonical>}`
  pointers on a separate root entry. The `orth_variants:` field
  was a loader-validated dead end (analyzer never consulted it);
  c21 deletes it. Parenthetical "variant of X" glosses are
  noise; use entry-level comments only for tokenizer-normalization
  context.
- **Loan field convention**: `loan: SPANISH | ENGLISH`,
  uppercase. Lower-case `spanish` errors on load.
- **POS-flips coexist with prior POS entries** at the same
  citation (e.g. `pansin(VERB+NOUN)`, `usap(VERB+NOUN)`,
  `dali(VERB+ADJ)`, `taas(VERB+ADJ)`). Each `- citation: X /
  pos: P` block is a separate Root in `md.roots`.
- **ma_adj inventory test** (`test_forty_one_ma_adj_roots`)
  needs a count bump every time a `[ma_adj]`-opting ADJ root
  lands. (c8 / c18 / c30 each touched it.)
- **OOV-probe pin chain** in `test_phase8q_oov_probe.py`
  re-anchors whenever a closure invalidates the previous
  anchor — pandanggo → mahusay → kilala → kumbidado → gawin
  (current; will move forward when pre-4 lands paradigm-cell
  fixes).
- **Anti-deferral discipline**: when audit-OOV conflicts with a
  prior analytical commitment (the `galit` collision in c9
  versus Phase 5n.A C1 stative-pruning), respect the prior
  commitment and revert.

## 7. Tail metrics

After pre-1:

- ~1750 unique lemma-candidates remain in the audit OOV pool
  (down from ~2120 pre-sweep).
- The top of the OOV distribution is now dominated by
  **paradigm-cell gaps** (gawin / gagawin / kunin / hiwain /
  nasaan / pakiabot / pupunla / itapon / ituro / hugasan / etc.)
  — exactly the surface pattern that 9.X.pre-4 will address.
- The remaining ~1750 splits roughly: ~700-900 paradigm-cell
  gaps → pre-4, ~30 proper names → pre-2, ~60 OCR artifacts →
  pre-3, ~750 long-tail 1-sent items (mix of dictionary-once
  vocabulary, audit-source rare words, and inflected-form
  variants of known roots) — to be triaged in future Phase 9
  / Phase 10 lex work.

## 8. Test gate

`hatch run test-both`: **8815 passed in ~106-110s** wall-clock
(consistent across c23-c30 measurements). `hatch run check`:
clean throughout.

## 9. References

- Pre-1 plan-of-record (gitignored): `.claude/plans/tgllfg-phase-9.md`
  (table row `9.X.pre-1`).
- Pre-9.X.pre-1 baseline snapshot: `docs/coverage-audit-2026-05-post-phase8.md`.
- 9.U diagnostic that originally scoped pre-1: `docs/coverage-audit-9u-long-sentence-diagnostic.md`.
- Harvester script (c19 engineering surface):
  `scripts/harvest_exemplars.py` (`cmd_parse` entry point;
  `/tmp/audit_monitor.log` runtime log).
