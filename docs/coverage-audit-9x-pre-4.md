# Phase 9.X.pre-4 — closure snapshot

> **Phase 9.X.pre-4 closure**: paradigm-cell engineering sub-PR.
> Closed 2026-05-19 across 8 commits.

## Headline

| Metric | Pre-pre-4 baseline | Post-pre-4 | Delta |
| --- | ---: | ---: | ---: |
| **Cumulative seeded parse rate** | 589 / 2327 (25.31%) | 633 / 2327 (27.20%) | **+44 abs / +1.89pp** |
| New paradigm cells | — | 8 | +8 |
| New affix_class declarations | — | 3 (paki / ma_soc / pag_gerund) | +3 |
| Engine fixes / extensions | — | 3 (a_deletion sandhi, m-initial -in- fix, VERB→NOUN POS-flip) | +3 |
| OOV-frequency unique tokens | 1776 | 1715 | −61 |

## Per-wave

| Wave | Pre | Post | Δ abs | Δ rate |
| --- | ---: | ---: | ---: | ---: |
| Wave 1 — rg81 transcriptions | 44 (37.29%) | 45 (38.14%) | +1 | +0.85pp |
| Wave 2 — R&C 1990 | 85 (17.00%) | 95 (19.00%) | **+10** | +2.00pp |
| Wave 2 — R&G Intermediate | 86 (17.20%) | 90 (18.00%) | +4 | +0.80pp |
| Wave 2 — Ramos 1971 | 53 (25.36%) | 65 (31.10%) | **+12** | **+5.74pp** |
| Wave 3 — S&O 1972 | 110 (22.00%) | 117 (23.40%) | +7 | +1.40pp |
| Wave 3 — R&G Conversational | 211 (42.20%) | 221 (44.20%) | +10 | +2.00pp |

Ramos 1971 carries the largest single-wave gain (+12) — Ramos's
dictionary-style entries are dense with bare imperative / hortative
forms (IV-i, DV-an, paki-) that pre-4's new SOC bare-form cells
unlock. R&C 1990 and R&G Conversational tie at +10 each — both
dialog-heavy corpora with frequent paki-, ma-, and pag- gerund
usage.

## Commit map

<!-- markdownlint-disable MD013 -->

| Commit | Subject | Engineering | Yield |
| --- | --- | --- | ---: |
| 9.X.pre-4.1 | i_oblig/an_oblig CTPL SOC bare cells | 2 new paradigm cells | itapon (6) / ituro (4) / hugasan (4) |
| 9.X.pre-4.2 | a_deletion sandhi flag for a-final stems + -in | new sandhi flag + analyzer wiring | gawin (10) / gagawin (10) |
| 9.X.pre-4.3 | m-initial -in- infix fix | engine fix in `infix_after_first_consonant` | minamahal + 9 other m-initial paradigm cell deltas |
| 9.X.pre-4.4 | ma_adj plural CV-redup | new adjective cell | maliliit (3) + 63 other ma_adj-class plurals |
| 9.X.pre-4.5 | paki- request paradigm | new affix_class + 4 root opt-ins (abot/sara/putol + new bura entry) | pakiabot (4) / pakisara (1) / pakiputol (1) / pakibura (1) |
| 9.X.pre-4.6 | ma_soc opt-in affix_class | new affix_class + una opt-in | mauna (1) |
| 9.X.pre-4.7 | pag- gerund (VERB→NOUN POS-flip) | engine extension + 2 cells + 10 root opt-ins | pagdating (5) / pag-aaral (4) / pagtatanim (2) / pagsasabi (2) / pagtulong / pagkatok / pagpunta / pagkanta / pagtawa / pagtingin |
| 9.X.pre-4.8 | iyak + mag affix_class | lex tweak | nag-iiyak (4) |

<!-- markdownlint-enable MD013 -->

## Engineering achievements

* **a_deletion sandhi** (c2) — a third per-root sandhi variant
  alongside `high_vowel_deletion` (Phase 2C) for the low-vowel
  variant of Schachter & Otanes 1972 §4.21 suffix sandhi.
  Suffix-specific: only fires on `-in` to keep DV `-an` and
  IV `i-` paradigms unaffected.
* **m-initial -in- infix correction** (c3) — fixes a systematic
  bug across all 4 m-initial in_oblig/an_oblig roots
  (`mahal` / `maneho` / `marka` / `masid`). `/m/` is excluded
  from the sonorant ni-prefix variant; patterns with regular
  obstruent-initial bases for -in- infixation.
* **VERB→NOUN POS-flip routing** (c7) — extends
  `_index_paradigm_via_base_pos` to handle VERB-root → NOUN-output
  paradigm cells, mirroring Phase 8.C's NOUN-root → ADJ-output
  pattern (`pinakapuno`). Mechanism is reusable for future
  nominalization paradigms (ka- "fellow X-er", pang- instrument,
  mam- agent, etc.).
* **3 new per-root opt-in affix_classes**: `paki` (polite
  request), `ma_soc` (bare ma- hortative), `pag_gerund`
  (nominalization). Each gated on explicit lex-level opt-in to
  avoid spurious analyses on non-applicable roots (especially
  ma_adj-coexisting ADJ predicative roots like
  `mainit` / `masaya` / `maingay`).

## Files touched

* `data/tgl/paradigms.yaml` (+~80 lines across 5 commits — new
  paradigm cells)
* `data/tgl/adj_paradigms.yaml` (+19 lines — c4 plural CV-redup)
* `data/tgl/verbs.yaml` (+15 affix_class extensions across
  c2/c5/c7/c8 + 1 new `bura` lex entry)
* `src/tgllfg/morph/sandhi.py` (+10 lines — c2 a_deletion + c3
  m-initial fix)
* `src/tgllfg/morph/analyzer.py` (+5 lines — c2 a_deletion wiring,
  c7 POS-flip routing extension)
* 5 test-fixture updates (c2 propagation + c3 m-initial fixture +
  c2 OOV-probe pin chain advance + c2 8.F gagawin pin flip + c2
  Phase 4 coverage corpus update)

## Test gate

All 8 commits passed `hatch run test-both` cleanly. Test count
stable at 8815 throughout — no new tests added (pre-4 is engine
work that's covered by the existing paradigm and feature tests).

| Commit | Wall time |
| --- | ---: |
| 9.X.pre-4.1 | 111.41s |
| 9.X.pre-4.2 | 117.11s |
| 9.X.pre-4.3 | 108.15s |
| 9.X.pre-4.4 | 110.36s |
| 9.X.pre-4.5 | 115.04s |
| 9.X.pre-4.6 | 116.35s |
| 9.X.pre-4.7 | 106.46s |
| 9.X.pre-4.8 | 109.98s |

## Remaining paradigm-cell gaps (deferred)

Three named pre-1 OOV-probe pin chain items remain open:

* **`kunin` (count 5)** — `kuha` irregular alternation
  (`h` → `n` substitution + `/a/`-deletion). Stem alternation
  beyond the standard sandhi machinery; needs either an
  irregular-form mechanism on Root, a second `kuha` lex entry
  with explicit `kun-` stem, or a custom paradigm op.
* **`hiwain` (count 3)** — `hiwa` no-h-epenthesis variant.
  A third a-final pattern alongside default h-epenthesis
  (`basa → basahin`) and a-deletion (`gawa → gawin` from c2).
  Needs a `no_h_epenthesis` sandhi flag or per-root opt-in
  saying "concatenate, no /h/".
* **`naging` (count 3-4)** — irregular PFV of `maging`
  ("become"). Separate `maging` / `naging` / `magiging`
  paradigm; lex special-case probably simpler than a paradigm
  cell.

Higher-yield audit-attested paradigm forms still uncovered:

| Surface | Count | Gap |
| --- | ---: | --- |
| `magagawa` | 4 | `gawa` + ma-CV-redup ability/future |
| `makakabili` | 4 | `bili` + makaka- ability-future |
| `pinaalis` | 4 | `alis` + pa-causative-passive |
| `kakanin` | 3 | `kain` CTPL vs lexicalized NOUN ("snacks") |
| `nagtratrabaho` | 3 | `trabaho` Spanish-loan + mag- IPFV |
| `manood` | 4 | `nood` + mang- with nasal substitution |
| `saakin` | 4 | `sa + akin` word-merge (extractor/transcription) |
| `nasaan` | 4 | wh-locative special form (lex) |
| `nagkaroon` | 4 | `magkaroon` ("to have") compound paradigm |

The 3 new per-root opt-in affix_classes (paki / ma_soc /
pag_gerund) cover only audit-attested roots at present.
Generalizing them productively — every VERB root automatically
unlocking all three — would be an engine extension worth
scoping for a future phase.

## What's next

Phase 9.X follow-ons (pre-1 / pre-2 / pre-3 / pre-4) close out
with pre-4. Phase 9.X main work continues:

* **9.X** — PANAHON 24-row cluster diagnostic + closure
  (closes Cluster G `'y` clitic) — B5 bucket.
* **9.Y** — Kroeger 1991 exemplar harvest — B6 bucket.
* **9.Z** — Naturalistic-tier regression fixture — B6 bucket.

## Cumulative Phase 9.X tier-by-tier impact

| Sub-PR | Seeded Δ | Cumulative seeded |
| --- | ---: | ---: |
| Pre-1 (lex sweep) | +133 | 391 → 524 (16.80% → 22.52%) |
| Pre-2 (proper names + EN loans) | +50 | 524 → 574 (22.52% → 24.67%) |
| Pre-3 (OCR cleanup) | +15 | 574 → 589 (24.67% → 25.31%) |
| Pre-4 (paradigm-cell engineering) | **+44** | 589 → 633 (25.31% → 27.20%) |
| **Cumulative pre-1..pre-4** | **+242 abs / +10.40pp** | **391 → 633** |

Per-entry yield is best for pre-2 (proper names — 0.68
sents/entry) since proper names sit in dense audit sentences;
pre-4 yields ~5.5 sents/commit (44/8) which is healthy for
engineering work where each commit unlocks a productive
paradigm class.
