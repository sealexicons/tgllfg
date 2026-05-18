# Phase 9.X.pre-2 — closure snapshot

> **Phase 9.X.pre-2 closure**: proper-name + English-loan lex
> sweep. Closed 2026-05-18 in 3 commits.

## Headline

| Metric | Pre-pre-2 baseline | Post-pre-2 | Delta |
| --- | ---: | ---: | ---: |
| **Cumulative seeded parse rate** | 524 / 2327 (22.52%) | 574 / 2327 (24.67%) | **+50 abs / +2.15pp** |
| Lex entries added | — | 74 | +74 |
| OOV-frequency unique tokens | 1871 | 1790 | −81 (proper names dropped out) |

## Per-wave

| Wave | Pre | Post | Δ abs | Δ rate |
| --- | ---: | ---: | ---: | ---: |
| Wave 1 — rg81 transcriptions | 44 (37.29%) | 44 (37.29%) | +0 | +0.00pp |
| Wave 2 — R&C 1990 | 66 (13.20%) | 84 (16.80%) | **+18** | **+3.60pp** |
| Wave 2 — R&G Intermediate | 77 (15.40%) | 86 (17.20%) | +9 | +1.80pp |
| Wave 2 — Ramos 1971 | 51 (24.40%) | 53 (25.36%) | +2 | +0.96pp |
| Wave 3 — S&O 1972 | 99 (19.80%) | 101 (20.20%) | +2 | +0.40pp |
| Wave 3 — R&G Conversational | 187 (37.40%) | 206 (41.20%) | **+19** | **+3.80pp** |

R&C 1990 and R&G Conversational together carry +37 of the +50
absolute gain — both corpora are dialog-heavy (R&C exercises and
R&G Conversational chapters), with proper names as `si <Name>` /
`ni <Name>` pivots in nearly every sentence.

## Commit map

<!-- markdownlint-disable MD013 -->

| Commit | Subject | Entries | Files |
| --- | --- | ---: | --- |
| 9.X.pre-2.1 | add 66 audit-attested proper-name NOUNs + alphabetize taon/taongbahay | 66 | data/tgl/nouns.yaml |
| 9.X.pre-2.2 | add 4 audit-attested PLACE proper-name NOUNs | 4 | data/tgl/nouns.yaml |
| 9.X.pre-2.3 | add 4 audit-attested English code-switch NOUNs | 4 | data/tgl/nouns.yaml |
| 9.X.pre-2.4 | closure snapshot + plan / memory updates | — | docs/coverage-audit-9x-pre-2.md |

<!-- markdownlint-enable MD013 -->

## Inventory delta

* `subclass: [PERSON, <GENDER>]`: 63 new first-name entries
  (gender-tagged).
* `subclass: [PERSON]` only (no gender atom): 3 new surname
  entries — `cruz`, `peczon`, `reyes`. Surnames appear in
  `si <Surname>` / `si Title <Surname>` patterns without
  gender disambiguation.
* `subclass: [PLACE]`: 4 new entries — `baguio`, `hawaii`,
  `honolulu`, `rizal`. PLACE inventory grows from 3
  (amerika / maynila / pilipinas) to 7.
* `loan: ENGLISH` NOUN (no subclass): 4 new entries — `tour`,
  `movies`, `interview`, `announcer`. All are unaltered
  English code-switches in genuine Tagalog matrix text.

Also fixed: one pre-existing out-of-alphabetical-order pair
(`taongbahay` previously preceded `taon`). After pre-2.1, file
ordering is fully alphabetical end-to-end.

## Files touched

* `data/tgl/nouns.yaml` (+74 entries across 3 commits; +445 / −4
  cumulative)
* `docs/coverage-audit-9x-pre-2.md` (new; this file)

No engineering / test-fixture changes — pre-2 is pure lex YAML.

## Test gate

All three commits passed `hatch run test-both` cleanly. Test count
stable at 8815 throughout (no new proper-name regressions, no
inventory-count test bumps needed since none of the new entries
participate in metadata-test count assertions).

| Commit | Wall time |
| --- | ---: |
| 9.X.pre-2.1 | 113.47s |
| 9.X.pre-2.2 | 102.01s |
| 9.X.pre-2.3 | 110.70s |

## Filtering decisions reinforced

Pre-2 filtered out the following heuristic-flagged tokens
(`NOUN(proper)?` or `ENGLISH?` per `scripts/oov_hit_list.py`):

* **VERB false positives** — `kunin`, `gawin`, `nagkaroon`,
  `natoon`: title-case in sentence-initial position; paradigm-cell
  gaps belong to **9.X.pre-4**.
* **OCR artifacts** — `maynilakung` (= "Maynila kung"),
  `piirases` (= "phrases"), `eagkain` (= "pagkain"): fix at-source
  per `feedback_ocr_eyeball_pdf`, **9.X.pre-3** territory.
* **English glosses / translations** — `you`, `your`, `beautiful`,
  `discourses`, `means`, `need`, `youngest`, `interviewees`,
  `it`, `how`, `new`, `york`, `math`: bilingual-corpus noise
  (English alongside Tagalog translation), not code-switches in
  Tagalog matrix.
* **Multi-token compounds** — `New York`, `Ala Moana`: pending
  multi-word-expression machinery. Single-token `ala` / `moana`
  / `new` / `york` alone are not useful standalone proper-name
  atoms.
* **Honorific abbreviations** — `gng` (= Mrs./Ginang): separate
  semantic class from proper names. Pre-2 follow-on.
* **Ambiguous ethnonyms** — `filipino`: noun-vs-adjective and
  ethnonym-vs-common-noun ambiguity needs analysis pass.

Per the Phase 9.X.pre-1 c27 audit-attestation lesson: every
candidate must be eyeball-verified in its audit sample-text as a
real proper-name occurrence in Tagalog text. No speculative entries.

## What's next

Per the plan ledger:

* **9.X.pre-3** — OCR-source cleanup (~60 OCR-artifact OOVs);
  fix source `.txt` transcriptions rather than polluting lex.
* **9.X.pre-4** — paradigm-cell engineering (~700-900
  paradigm-cell gaps; `gawin` / `kunin` / `hiwain` / `itapon` /
  `ituro` / `hugasan` / `nasaan` / `pag-aaral` / `maliliit` /
  `naging` / `minamahal` / `mauna` class).

Then main Phase 9 work continues with **9.X** (PANAHON 24-row
cluster), **9.Y** (Kroeger 1991 harvest), **9.Z** (naturalistic-
tier regression fixture).
