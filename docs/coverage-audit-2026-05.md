# Coverage audit — Wave 1 (transcriptions + R&B 1986)

> **Status:** Wave 1 pilot snapshot (2026-05-14). See
> ``.claude/plans/tgllfg-harvest-audit.md`` for the plan-of-record.
> Wave 2 (R&G Intermediate + R&C 1990 + Ramos 1971) and Wave 3
> (S&O 1972 + R&G Conversational) follow.

## Wave 1 sources

- ``data/tgl/references/transcriptions/rg81-excerpts.md`` —
  hand-transcribed excerpts from Ramos & Goulet 1981
  *Intermediate Tagalog*, four chapters (ANG MANOK, ANG
  PAG-AARAL NG ISANG WIKA, PANAHON, ANG PAMILYA). Skipped:
  Talasalitan vocab tables and the ``Uncorrected continuation``
  subsection per user directive 2026-05-14.
- ``data/tgl/references/HandbokOfTagalogVerbs.txt`` —
  Ramos & Bautista 1986 *Handbook of Tagalog Verbs*; used for
  verb-base inventory only (paradigm-cell extraction deferred;
  OCR splits forms across lines too irregularly for Wave 1).

## Sentence-parse buckets (rg81 transcriptions)

Total sentences parsed: **118**.

| Bucket | Count | Share |
| --- | ---: | ---: |
| zero-parse-fragment | 75 | 63.6% |
| zero-parse-no-fragment | 22 | 18.6% |
| parse-success-1 | 19 | 16.1% |
| parse-success-N | 2 | 1.7% |

### Per-chapter breakdown

| Chapter | parse-success-1 | parse-success-N | zero-parse-fragment | zero-parse-no-fragment | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| ANG MANOK | 18 | 2 | 26 | 5 | 51 |
| ANG PAG-AARAL NG ISANG WIKA | 0 | 0 | 10 | 3 | 13 |
| ANG PAMILYA | 0 | 0 | 10 | 3 | 13 |
| PANAHON | 1 | 0 | 29 | 11 | 41 |

## Zero-parse examples (top 30)

<!-- markdownlint-disable MD013 -->

| Locator | Text | Bucket | OOV tokens | Diagnostic |
| --- | --- | --- | --- | --- |
| `ANG MANOK/sent-10` | Kinakain niya ang mga ito. | zero-parse-fragment | — | — |
| `ANG MANOK/sent-11` | Isang araw, nagbubunot siya ng damo. | zero-parse-fragment | — | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-12` | May nakita siya. | zero-parse-fragment | — | Diagnostic(kind='completeness-failed', message="PRED 'KITA' requires 'OBJ' but i |
| `ANG MANOK/sent-14` | Bagong ani ang palay. | zero-parse-fragment | ani | Diagnostic(kind='constraint-failed', message="constraining equation does not hol |
| `ANG MANOK/sent-16` | Ipinasok niya ito sa kulungan. | zero-parse-fragment | kulungan | — |
| `ANG MANOK/sent-17` | Nasa ilalim ng bintana niya ang kulungan. | zero-parse-fragment | ilalim, kulungan | — |
| `ANG MANOK/sent-18` | May binalak siya. | zero-parse-fragment | — | — |
| `ANG MANOK/sent-19` | Kakanin niya ang manok sa almusal. | zero-parse-fragment | Kakanin, almusal | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-20` | Sumapit ang kinabukasan. | zero-parse-no-fragment | kinabukasan | — |
| `ANG MANOK/sent-21` | Maaga noon. | zero-parse-no-fragment | Maaga, noon | — |
| `ANG MANOK/sent-22` | May ingay na gumising sa mama. | zero-parse-no-fragment | ingay | — |
| `ANG MANOK/sent-25` | May nakita siyang itlog. | zero-parse-fragment | — | Diagnostic(kind='existential-failed', message='path is not defined: (↓2 TIME_FRA |
| `ANG MANOK/sent-27` | May naisip ang mama. | zero-parse-fragment | naisip | — |
| `ANG MANOK/sent-28` | Kakanin niya ang itlog sa almusal. | zero-parse-fragment | Kakanin, almusal | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-29` | Pinakain niya ang manok ng isang tasang palay. | zero-parse-fragment | — | Diagnostic(kind='coherence-failed', message="governable GF 'OBJ-PATIENT' is pres |
| `ANG MANOK/sent-30` | Kinausap siya ng manok. | zero-parse-fragment | Kinausap | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-31` | Kinausap niya ang manok. | zero-parse-fragment | Kinausap | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-32` | Lumipas ang araw. | zero-parse-fragment | Lumipas | — |
| `ANG MANOK/sent-33` | May naisip siya. | zero-parse-fragment | naisip | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-34` | Papakainin niya ng mas marami ang manok. | zero-parse-fragment | Papakainin | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-35` | Papakainin niya ito ng dalawang tasang palay. | zero-parse-fragment | Papakainin | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-36` | Papakainin niya ito sa umaga. | zero-parse-fragment | Papakainin | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-37` | Papakainin niya ito sa gabi. | zero-parse-fragment | Papakainin | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-38` | Siguro mangingitlog ito ng dalawa araw-araw. | zero-parse-fragment | mangingitlog | — |
| `ANG MANOK/sent-41` | Naging tamad ito. | zero-parse-no-fragment | Naging, tamad | — |
| `ANG MANOK/sent-42` | Lagi itong natutulog. | zero-parse-no-fragment | — | — |
| `ANG MANOK/sent-43` | Hindi ito nangitlog. | zero-parse-fragment | nangitlog | — |
| `ANG MANOK/sent-44` | Nagalit ang mama. | zero-parse-fragment | Nagalit | — |
| `ANG MANOK/sent-47` | Inalmusal niya ito. | zero-parse-fragment | Inalmusal | Diagnostic(kind='constraint-failed', message='constraining equation lhs is undef |
| `ANG MANOK/sent-50` | Wala na siyang kinakausap. | zero-parse-fragment | kinakausap | Diagnostic(kind='atom-mismatch', message="cannot bind atom 'YES': node already b |

<!-- markdownlint-enable MD013 -->

## OOV-token frequency (top 30)

| Token | Count |
| --- | ---: |
| `bagyo` | 7 |
| `panahon` | 6 |
| `pilipino` | 5 |
| `papakainin` | 4 |
| `aaral` | 4 |
| `tag` | 4 |
| `loob` | 3 |
| `kulungan` | 2 |
| `kakanin` | 2 |
| `almusal` | 2 |
| `maaga` | 2 |
| `naisip` | 2 |
| `kinausap` | 2 |
| `nahihirapan` | 2 |
| `nadadalian` | 2 |
| `magkamali` | 2 |
| `maling` | 2 |
| `makipagkaibigan` | 2 |
| `mag` | 2 |
| `masasabing` | 2 |
| `natitirang` | 2 |
| `bukirin` | 2 |
| `siyesta` | 2 |
| `karaniwan` | 2 |
| `nagtratrabaho` | 2 |
| `gaanong` | 2 |
| `pagtatanim` | 2 |
| `magsasaka` | 2 |
| `panahong` | 2 |
| `tungkulin` | 2 |

## R&B 1986 verb-base inventory

Extracted: **194** verb entries (one per `(base, gloss)` pair).

### Lex coverage

- In our lex: **170**
- Not in our lex: **24**
- Coverage: **87.6%**

### Missing-from-lex (top 50)

| Base | Gloss | Affix class |
| --- | --- | --- |
| `asso` | converse with | `maki-` |
| `galit` | use | `-um- -in -an` |
| `gulat` | be surprised | `ma- ika-` |
| `gutom` | be hungry | `ma- ika-` |
| `haba` | lengthen | `-an` |
| `lari` | become big | `-um- ika-` |
| `lari` | make big | `-an` |
| `linot` | forget | `-um- -in / ka- -an` |
| `paalam` | say good-bye | `mag-` |
| `pagbili` | sell | `m- i- -an` |
| `pagkaroon` | have, exist | `m-` |
| `pakamatay` | commit suicide | `mag-` |
| `pakinig` | listen | `m- -an` |
| `pakiusap` | request | `m- -an` |
| `pakiusap` | return home | `-um-` |
| `pakiusap` | bring home | `mag- i- -an` |
| `palari` | rear a child | `mag- -in` |
| `paligo` | bathe | `mag- -an` |
| `panalo` | win | `m- -an` |
| `pangyari` | happen | `m-` |
| `parilala` | introduce | `mag- i-` |
| `patingin` | be examined | `mag- -an` |
| `patuloy` | continue | `mag- ipag-` |
| `puno` | become full | `ma- ika-` |

## Next steps

1. Eyeball the top-30 zero-parse rows above; cluster by
   construction class (manual triage).
2. Triage the OOV-token list against the lex sources in
   `data/tgl/lexicon/`; many will be proper nouns or
   names of places (e.g. ``Pilipinas``).
3. Triage the R&B-1986-missing verb list; identify productive
   bases that are missing from `verbs.yaml`.
4. Proceed to Wave 2 if signal-to-noise is acceptable.
