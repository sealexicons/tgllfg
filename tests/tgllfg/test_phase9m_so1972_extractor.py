"""Phase 9.M: S&O 1972 harvest-extractor cleanup.

Targets noise patterns in wave3-so1972.jsonl (1289 lines pre-9.M;
the largest harvest wave by line count) per plan §B2.C:

1. **Two-letter focus/voice abbreviation prefix** — S&O uses
   ``AF:`` / ``OF:`` / ``LF:`` / ``BF:`` / ``IF:`` / etc. (and the
   ``IV`` / ``OV`` / ``LV`` / ``DV`` variants spelled out as
   "Voice"). 65 hits in wave3-so1972. The Phase 9.K
   ``_GRAMMAR_TAG_PREFIX_RE`` (originally for R&C 1990's spelled-
   out ``Question:`` / ``Example:`` / ``Counter-assumption:``)
   is extended with these 2-letter abbreviations.

2. **Pedagogical-transformation arrows** ``→`` / ``➔`` — S&O uses
   these inside example lines to show pre→post-rule transformations
   (``Winawalisan mo ang sahig. ➔ Walisan mo ang sahig.``). Both
   halves are typically valid Tagalog example sentences. The
   ``_split_sentences`` function is updated to normalize the
   arrow to a sentence boundary so each half is emitted as a
   separate exemplar. 9 hits in wave3-so1972 + 1 in wave2-rg-
   intermediate.

3. **``(cf. ...`` paren-leading lines** — pedagogical "compare
   with" markers wrapping a partially-OCR'd example sentence.
   The embedded Tagalog is uniformly heavily OCR-garbled (often
   ``l`` substituted for capital ``I``, e.g., ``lbinili`` for
   ``Ibinili``). 8 hits in wave3-so1972. ``_CF_PAREN_LEADING_RE``
   rejects.

4. **English-paren-leading lines** — pedagogical commentary in
   parens beginning with English function words (``(Underlying
   sentence: ...)`` / ``(Some speakers...`` / ``(The same
   meanings...`` / ``(Not all unaffixed adjectives...``).
   Linguistic asides, not natural Tagalog sentences. 7 hits in
   wave3-so1972 + 1 in wave3-rg-conversational.
   ``_ENGLISH_PAREN_LEADING_RE`` rejects.

5. **``§`` section-reference lines** — text containing the
   section-mark glyph is always linguistics pedagogical prose.
   2 hits in wave3-so1972. ``_SECTION_REF_RE`` rejects.

Corpus impact: wave3-so1972 1289 → 1260 lines (-29 net; 38
filtered − 9 added from arrow splits). Other waves: wave2-rg-
intermediate 1918 → 1919 (+1 from RG-Int's 1 arrow line splitting),
wave3-rg-conversational 667 → 666 (-1 from English-paren-leading).

Full-corpus parse-rate impact: S&O 156/1289 (12.10%) →
156/1260 (12.38%), 0 absolute / +0.28pp. RG-Conv 194/667 →
193/666, -1 abs / -0.11pp. Cumulative 668/5226 (12.78%) →
667/5197 (12.83%), -1 abs / +0.05pp.

The -1 absolute is a quality improvement (3 false-positive parses
eliminated: 2 ``(Underlying sentence: …)`` lines in S&O where
the parser treated the English prefix as unknown tokens and
parsed the embedded Tagalog clause, +1 English-paren-leading in
RG-Conv) offset by +2 real parses from arrow-split halves
(``Mayroon ka bang kotse?`` / ``Wala ka bang kotse?``). Two of
the 4 originally-projected arrow-split parses (``Mayroon ngang
bahay doon.`` / ``Wala ngang bahay doon.``) don't reach the
corpus because the post-split halves carry only 1 Tagalog marker
each (``mayroon``/``wala`` only; ``ngang`` is a linker-suffix
form not in ``_TGL_MARKERS``), failing ``_looks_like_tagalog``'s
``len(tgl) >= 2`` gate.

Yield analysis: AF:/OF: prefix-strip alone yields 0 new parses
(of 65 prefix-lines, parser already tolerates the prefix as
unknown leading tokens and parses the body for 4 of them; the
strip just shortens the canonical text). The "EXAMPLE/QUESTION/
SENTENCE glossing tags" mentioned in plan §B2.C don't appear in
the current S&O corpus (already covered by Phase 9.K's
``_GRAMMAR_TAG_PREFIX_RE`` for the spelled-out forms). The
"`pa` paradigm-affix discussions emitting standalone `pa`
tokens" mentioned in the plan turn out not to be filterable
extractor-side — those are content lines, not noise.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


class TestPhase9mFocusVoiceAbbreviationPrefix:
    """The extended ``_GRAMMAR_TAG_PREFIX_RE`` strips S&O 1972's
    two-letter focus/voice abbreviations (``AF:``/``OF:``/etc.)."""

    @pytest.mark.parametrize("inp,expected", [
        ("AF: Naligo siya ng mainit na tubig.",
         "Naligo siya ng mainit na tubig."),
        ("OF: Aawitin nila sa inyo ang kundiman.",
         "Aawitin nila sa inyo ang kundiman."),
        ("LF: Hinugasan ng bata ang pinggan.",
         "Hinugasan ng bata ang pinggan."),
        ("BF: Ibinili niya ng bigas.",
         "Ibinili niya ng bigas."),
        ("IF: Ipinakilala niya si Maria.",
         "Ipinakilala niya si Maria."),
        ("GF: Naabot ng bata ang aklat.",
         "Naabot ng bata ang aklat."),
        ("DF: Ipinarating niya ang sulat.",
         "Ipinarating niya ang sulat."),
        ("CF: Ipinaluto ni Ben kay Maria ang adobo.",
         "Ipinaluto ni Ben kay Maria ang adobo."),
        ("RF: Nag-utusan sila.",
         "Nag-utusan sila."),
        ("PF: Pinaaway niya sila.",
         "Pinaaway niya sila."),
        ("IV: Ipinasok ko ang aklat.",
         "Ipinasok ko ang aklat."),
        ("OV: Sinunog niya ang papel.",
         "Sinunog niya ang papel."),
        ("LV: Hinuhugasan ng bata ang pinggan.",
         "Hinuhugasan ng bata ang pinggan."),
        ("RV: Naghampas-tampalan sila.",
         "Naghampas-tampalan sila."),
    ])
    def test_strips_focus_voice_prefix(
        self, inp: str, expected: str
    ) -> None:
        assert he._clean_sentence_text(inp) == expected


class TestPhase9mArrowSplit:
    """``_split_sentences`` normalizes pedagogical-transformation
    arrows ``→`` / ``➔`` to a sentence boundary so each half is
    emitted separately."""

    @pytest.mark.parametrize("inp,expected", [
        ("Winawalisan mo ang sahig. ➔ Walisan mo ang sahig.",
         ["Winawalisan mo ang sahig.", "Walisan mo ang sahig."]),
        ("Mayroon ka bang kotse? ➔ Wala ka bang kotse?",
         ["Mayroon ka bang kotse?", "Wala ka bang kotse?"]),
        ("May singsing sa daliri niya. ➔ Walang singsing sa daliri niya.",
         ["May singsing sa daliri niya.",
          "Walang singsing sa daliri niya."]),
        # → variant
        ("Mayroon akong dadalawin ngayon. → Wala akong dadalawin ngayon.",
         ["Mayroon akong dadalawin ngayon.",
          "Wala akong dadalawin ngayon."]),
        # Arrow without preceding terminal — synthesize one.
        ("Mayroon ka bang kotse ➔ Wala ka bang kotse",
         ["Mayroon ka bang kotse.", "Wala ka bang kotse"]),
        # No arrow → no split
        ("Maganda ang araw.",
         ["Maganda ang araw."]),
    ])
    def test_arrow_split(
        self, inp: str, expected: list[str]
    ) -> None:
        assert he._split_sentences(inp) == expected


class TestPhase9mCfParenLeading:
    """``_CF_PAREN_LEADING_RE`` rejects ``(cf. ...`` paren-leading
    lines, which are pedagogical "compare with" markers wrapping
    heavily OCR-garbled example sentences."""

    @pytest.mark.parametrize("inp", [
        "(cf. lbinili niya ng bigas sa groseri ang pamilya.",
        "(cf. ltatanong niy:i sa akin ang dahilan.",
        "(cf. lsisigaw niya s:i akin ang utos.",
        # No-space variant (``cf.J<Cap>``) — OCR-joined.
        "(cf.JPupunta ba kayo sa palengke?)",
        # Capitalized Cf
        "(Cf. Pupunta ba kayo sa palengke?)",
    ])
    def test_rejects_cf_paren(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9mEnglishParenLeading:
    """``_ENGLISH_PAREN_LEADING_RE`` rejects lines that begin with
    an open paren and an English function word — pedagogical
    commentary wrapping an embedded example."""

    @pytest.mark.parametrize("inp", [
        "(Underlying sentence: Nakita ko si Juan.)",
        "(Underlying sentence: Ginawa ni Juan ang trabaho.",
        "(Some speakers allow the replacement of the ang phrase.",
        "(The same meanings may be expressed by clauses.",
        "(Not all unaffixed adjectives may occur as bases.",
        "(However, the speaker may use the ng phrase.",
        "(When the affix is added, the form changes.",
        "(There is no agreement here.",
        "(Note that the linker is not used.",
        "(Compare the following examples.",
        "(For meaning distinctions, see §3.4.",
    ])
    def test_rejects_english_paren(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None

    @pytest.mark.parametrize("inp", [
        # Tagalog paren-leading is preserved.
        "(Magandang umaga.) Maganda po naman.",
        "(Hindi ko alam.) Sa kanya ka magtanong.",
        # Speaker-clarification paren (not at line start)
        "Pinuwersa ni Digna si Esper, para umamin ito (si Esper).",
    ])
    def test_preserves_tagalog_paren(self, inp: str) -> None:
        # The line should not be rejected by _ENGLISH_PAREN_LEADING_RE
        # (other filters may or may not clean it; we only verify
        # the new filter doesn't fire).
        assert not he._ENGLISH_PAREN_LEADING_RE.match(inp)


class TestPhase9mSectionReferenceReject:
    """``_SECTION_REF_RE`` rejects any line containing ``§``."""

    @pytest.mark.parametrize("inp", [
        "When a,,o is used as a modifier, it precedes na/-ng (cf. §3.1).",
        "(for meaning distinctions cf. §3.4 ).",
        "See §5.2 for the full discussion.",
        "Compare with the example in §7.1.",
    ])
    def test_rejects_section_ref(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9mPreserveLegitimateLines:
    """Verify 9.M filters don't reject clean Tagalog or
    pre-existing legitimate-line shapes."""

    @pytest.mark.parametrize("inp", [
        "Naligo siya ng mainit na tubig.",
        "Aawitin nila sa inyo ang kundiman.",
        "Maganda ang araw.",
        "Bumili si Juan ng aklat sa palengke.",
        "Mayroon ka bang kotse?",
        "Wala ka bang kotse?",
    ])
    def test_preserves_clean_line(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) == inp


class TestPhase9mEndToEndCorpus:
    """End-to-end via ``extract_so1972()`` — verify the post-9.M S&O
    corpus carries no leakage of the rejected categories."""

    @pytest.mark.slow
    def test_no_focus_voice_prefix_in_corpus(self) -> None:
        import re
        bad = re.compile(
            r"^(AF|OF|LF|BF|IF|GF|RF|DF|CF|PF|"
            r"IV|DV|RV|LV|BV|CV|PV)\s*:\s"
        )
        for ex in he.extract_so1972():
            assert not bad.match(ex.text_raw), (
                f"focus/voice prefix leaked: "
                f"{ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_arrow_in_corpus(self) -> None:
        for ex in he.extract_so1972():
            assert "→" not in ex.text_raw and "➔" not in ex.text_raw, (
                f"arrow leaked: {ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_cf_paren_leading_in_corpus(self) -> None:
        import re
        bad = re.compile(r"^\(\s*cf\.", re.IGNORECASE)
        for ex in he.extract_so1972():
            assert not bad.match(ex.text_raw), (
                f"(cf. leaked: {ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_section_ref_in_corpus(self) -> None:
        for ex in he.extract_so1972():
            assert "§" not in ex.text_raw, (
                f"§ leaked: {ex.locator} {ex.text_raw!r}"
            )
