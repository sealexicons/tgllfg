# Phase 9.X.pre-3 — closure snapshot

> **Phase 9.X.pre-3 closure**: OCR-source cleanup. Closed
> 2026-05-18 — engineering-class sub-PR; no lex changes.

## Headline

| Metric | Pre-pre-3 baseline | Post-pre-3 | Delta |
| --- | ---: | ---: | ---: |
| **Cumulative seeded parse rate** | 574 / 2327 (24.67%) | 589 / 2327 (25.31%) | **+15 abs / +0.64pp** |
| OCR-error fixes applied | — | ~70 | — |
| OOV-frequency unique tokens | 1790 | 1776 | −14 (OCR garble dropped out) |

## Per-wave

| Wave | Pre | Post | Δ abs | Δ rate |
| --- | ---: | ---: | ---: | ---: |
| Wave 1 — rg81 transcriptions | 44 (37.29%) | 44 (37.29%) | +0 | +0.00pp |
| Wave 2 — R&C 1990 | 84 (16.80%) | 85 (17.00%) | +1 | +0.20pp |
| Wave 2 — R&G Intermediate | 86 (17.20%) | 86 (17.20%) | +0 | +0.00pp |
| Wave 2 — Ramos 1971 | 53 (25.36%) | 53 (25.36%) | +0 | +0.00pp |
| Wave 3 — S&O 1972 | 101 (20.20%) | 110 (22.00%) | **+9** | **+1.80pp** |
| Wave 3 — R&G Conversational | 206 (41.20%) | 211 (42.20%) | +5 | +1.00pp |

S&O 1972 carries +9 of the +15 absolute gain — S&O is the OCR-dirtiest
of the six corpora (Acrobat OCR on a heavily-typeset 1972 reference
grammar with extensive linguistic notation), so cleanup yield is
concentrated there.

The smaller-than-pre-1/pre-2 absolute gain reflects pre-3's nature:
many OCR fixes target sentences outside the per-wave 500-sentence
seeded sample (Wave 2 R&C 1990 has 1022 total but the audit samples
500), so the seeded baseline can't show the full denominator-quality
improvement. Wave 2 R&G Intermediate notably grew from 1893 → 1919
total sentences post-extract (+26 more sentences not noise-rejected)
without affecting the seeded baseline.

## What was fixed

Approximately **70 OCR-error corrections** applied across the
licensed-reference `.txt` files (gitignored — not part of this PR's
commit footprint). Categories:

### Letter-substitution OCR errors

* `l ↔ i`: `motorslklo`→`motorsiklo` (6x), `baltta`→`balita`,
  `siua`/`stya`→`siya`, `sl`→`si`, `nl`→`ni`, `ilo`→`ito`,
  `AlelL`→`Aleli`, `Mabills`→`Mabilis` (intentionally left as
  printed-PDF typo `Mabills` per user verification on S&O 1972
  sent-1133).
* `rn ↔ m`: `burnhin`→`burahin`, `ikurnusta`→`ikumusta`,
  `tikrnan`→`tikman`, `turnulong`→`tumulong`, `burnuti`→`bumuti`,
  `gumarnot`→`gumamot`, `miyernbro`→`miyembro`,
  `turning`→`tuwing` (rn→wi), `Pupunla`→`Pupunta`.
* `0 ↔ 6`: `lumik6`→`lumiko` (2x).
* `c ↔ e`: `Puwedcng`→`Puwedeng`, `kusincra`→`kusinera`.
* `iii ↔ ili`: `bumiii`→`bumili`, `piiipinas`→`Pilipinas`,
  `humallli`→`humalili`, `magllllnls`→`maglinis`,
  `ngumingtti`→`ngumingiti` (tt→it).
* `rv ↔ nd`: `tirvdahan`→`tindahan`.
* `nv ↔ m`: `hunvusay`→`humusay`.
* `Dukas → Bukas` (B↔D OCR): 13 occurrences across S&O 1972.

### Word-merge OCR errors (lost spaces)

* S&O 1972: `bibilhinko`→`bibilhin ko`, `biniliko`→`binili ko`,
  `mgabata`→`mga bata` (5x), `maynilakung`→`Maynila kung`,
  `ruwisenyorna`→`ruwisenyor na`, `Masisipagna`→`Masisipag na`,
  `angpinapangingisdaan`→`ang pinapangingisdaan`,
  `Dukasay`/`Dukaska`/`Dukasdin`/`Dukasba'y`→`Bukas <space>...`,
  `maaarltayong`→`maaari tayong`.

### Digit-cluster OCR garbage

* `rn11ngga`→`mangga`, `eagkain`→`pagkain`,
  `Of-:`→`OF:`, `kapat{d`→`kapatid` (R&C 1990).

### User-PDF-verified medium-confidence cases (10 batched)

User eyeball-verified canonical readings via the source PDFs for 10
heavily-garbled sentences I flagged as medium-confidence. R&C 1990
fixes 1-5 applied by user directly; S&O 1972 fixes 6-10 applied by
me per user's supplied readings:

1. R&C 1990 Ch5 Conjoining sent-577: `mooring gawin`→`maaring gawin`.
2. R&C 1990 Ch5 Exercises sent-392: `Iiniiin`→`Iinitin` (root: `init`).
3. R&C 1990 Ch5 Clause-Invertibility sent-644: `nary`→`nang`.
4. R&C 1990 Ch5 Embedding sent-836: `pimdaan`→`pinulaan` (not my
   guess `pinadaan`).
5. R&C 1990 Ch5 Exercise sent-740: `Marmie`→`Mannie` (not `Mamie`).
6. S&O 1972 page-588 sent-1071: heavily garbled →
   `Porke tumanggap siya ng mabuting marka, hindi na siya
   nakikipag-usap sa atin.` (brace-alt picked first inline).
7. S&O 1972 page-610 sent-1133: heavily garbled →
   `Mabills na lumalapit ang bagyo sa Maynila.` (`Mabills`
   preserved per printed PDF typo).
8. S&O 1972 page-608 sent-1122: heavily garbled →
   `Bukas ng alas otso ng gabi daw siya aalis.` (brace-alt picked
   first inline).
9. S&O 1972 page-582 sent-1058: heavily garbled →
   `Magpapakamatay ako oras na maging di-matapat sa akin ang
   mangingibig ko.` (`om`→`oras`).
10. S&O 1972 page-283 sent-374: `PIIRASES`→`PHRASES` in three
    section-heading positions.

## Brace-alternative notation deferral

S&O 1972 uses brace-alternation notation `{alt1 | alt2 | ...}` in
printed example sentences to denote word-order alternatives (see
items 6 and 8 above for examples).

The current S&O 1972 extractor (`scripts/harvest_exemplars.py` line
841) **rejects any line containing `{` or `}`** to filter out the
phonetic-notation pattern OCR'd as `{ko·tseh{` etc. This filter
also drops legitimate brace-alternative example sentences.

For pre-3, brace-alternative sentences were encoded with **one
alternative picked inline** (per items 6 and 8 above). A proper
extractor extension that recognizes `{a | b | c}` alternation
syntax and expands each into a separate exemplar — while still
rejecting phonetic-notation false positives — is parked as future
engineering work outside pre-3 scope.

## Files touched

* `data/tgl/references/901132785-Modern-Tagalog.txt` (R&C 1990) —
  ~18 letter-sub fixes (gitignored; user-applied medium-confidence
  items 1-5 plus my high-confidence batch).
* `data/tgl/references/814610085-Conversational-Tagalog-a-Functional-Situational-Approach.txt`
  (R&G Conv) — ~6 fixes.
* `data/tgl/references/Intermediate-Tagalog-developing-cultural-awareness-through-language_compress.txt`
  (R&G Int) — user-applied 2 fixes (ikurnusta, tikrnan).
* `data/tgl/references/746927054-OceanofPDF-com-Tagalog-Dictionary-Teresita-v-Ramos.txt`
  (Ramos 1971) — 1 fix (humallli).
* `data/tgl/references/Tagalog-Reference-Grammar-Schachter-Otanes.txt`
  (S&O 1972) — ~40 fixes (highest concentration; OCR-dirtiest
  corpus).
* `data/tgl/references/transcriptions/rg81-excerpts.md` (Wave 1) —
  1 fix (miyernbro).

All `.txt` edits are local-only — `data/tgl/references/` is
gitignored (licensed reference works). The PR's commit footprint
is just this closure doc and the auto-regenerated
`docs/coverage-audit-2026-05-post-phase8.md` cross-wave snapshot.

## Test gate

Per CLAUDE.md docs-only convention: no pytest, no `hatch run check`;
`markdownlint` clean on both modified docs.

## What's next

Per the plan ledger:

* **9.X.pre-4** — paradigm-cell engineering (~700-900
  paradigm-cell gaps; `gawin` / `kunin` / `hiwain` / `itapon` /
  `ituro` / `hugasan` / `nasaan` / `pag-aaral` / `maliliit` /
  `naging` / `minamahal` / `mauna` class — paradigm-engine
  extension work, not lex work).

Then main Phase 9 work continues with **9.X** (PANAHON 24-row
cluster B5), **9.Y** (Kroeger 1991 harvest B6), **9.Z**
(naturalistic-tier regression fixture B6).
