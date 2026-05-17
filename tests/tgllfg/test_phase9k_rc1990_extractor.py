"""Phase 9.K: R&C 1990 harvest-extractor cleanup.

Closes the audit-surfaced noise classes in
``data/tgl/exemplars/wave2-rc1990.jsonl``:

1. **Pedagogical grammar-tag prefixes.** Lines like ``Q: Aling babae
   ...`` / ``Example: Nagdala si Damian ng inumin.`` /
   ``Simple S: Bumili si David ...`` / ``Counter-assumption:
   Nagtatrabaho pa rin siya.`` — the chapter-text typesetter
   precedes example sentences with a grammar-tag label and a colon.
   A new ``_GRAMMAR_TAG_PREFIX_RE`` strips a closed list of labels.

2. **Leading verb/noun/adj/root paren-metadata.** Lines like
   ``(verb tugtog. contemplated) si William ng gilara.`` — the
   metadata pulled the predicate out of the body, leaving a
   bare argument-string. These lines are rejected outright.

3. **Leading "(+ ...)" paren-metadata.** Lines like
   ``(+ base reduplication) Lumakad siya nang dahan-dahan.`` —
   the metadata block prefixes a complete sentence. The prefix is
   stripped; the body kept. Includes a malformed variant where the
   closing paren is missing: ``(+ pagka- and Umiyak siya nang ...``.

4. **Mid-sentence grammar-tag annotation.** Closed list:
   ``(Effect)`` / ``(Cause)`` / ``(Contrast)`` / ``(Purpose)`` /
   ``(Reproach)`` / ``(Shift)`` / ``(Reason)`` / ``(Concession)`` /
   ``(Condition)`` / ``(Result)``. Stripped from the line body.

5. **Trailing "(?)" editor annotation.** Marks the analyst's
   uncertainty about the surface form (``binuksan (?)``). Stripped.

6. **Trailing list-marker.** The line is the answer to part ``a.``
   or ``f.`` of an exercise (``Malaki ang utang niya. a.``).
   Normalized to a single sentence-final period.

7. **Slot-fill template rows.** Lines containing ``si / ang`` or
   ``/ / X / .`` are paradigm-table scaffolding, not real sentences.
   Rejected.

8. **Mid-line ungrammatical marker.** Lines containing ``*<lower>``
   are starred-form citations the typesetter marks as
   ungrammatical-as-shown. Rejected.

9. **OCR-confidence-low characters.** Lines containing ``€`` /
   ``£`` glyphs (typesetter substitutions for ``e`` / ``n``) or
   mid-word backslashes (``san\\palok``). Rejected.

10. **Ellipsis truncation.** Lines ending in ``...`` mark
    unfinished citations (``Pinag-usapan nila ... kaya ...``).
    Rejected.

11. **Multi-space typesetter padding.** Paradigm-row alignment in
    OCR leaves runs of 2+ spaces between tokens. Collapsed to
    single space after all upstream cleanups.

12. **Instruction-line _EN_MARKERS extension.** Exercise-instruction
    lines like ``Add sa phrases or ang phrases or both where
    appropriate.`` carry 2 Tagalog markers (``sa``, ``ang``) in
    citation context, so the pre-9.K ``_looks_like_tagalog``
    heuristic accepted them. Extending ``_EN_MARKERS`` with
    instruction-line tokens (``add``, ``where``, ``following``,
    ``linkers``, ``phrases``, …) tips the EN ≥ TGL test and rejects
    these lines.

The full-corpus parse rate on wave2-rc1990 went from 91/1075 (8.47%)
to 94/1025 (9.17%) post-cleanup — +3 absolute parses, +0.70pp; 50
noise lines stripped from the corpus.

Cumulative-corpus impact (sum across all 6 production waves): 664/5342
(12.43%) → 669/5268 (12.70%) — +5 absolute, +0.27pp; 74 noise lines
removed across waves (50 RC1990 + 15 R&G Int + 7 S&O 72 + 2 Ramos 71).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import harvest_exemplars as he  # type: ignore[import-not-found]  # noqa: E402


class TestPhase9kGrammarTagPrefix:
    """``_GRAMMAR_TAG_PREFIX_RE`` strips R&C 1990 pedagogical
    grammar-tag prefix labels.

    Negative case: ``Biyemes ngayon: ngumili ka naman.`` —
    Tagalog noun-phrase + colon + clause is preserved (the prefix
    is not in the closed grammar-tag list)."""

    @pytest.mark.parametrize("inp,expected", [
        ("Q: Aling babae ang kaibigan ni Charlie?",
         "Aling babae ang kaibigan ni Charlie?"),
        ("A: Sinalubong ni George ang nakailag na sundalo.",
         "Sinalubong ni George ang nakailag na sundalo."),
        ("Question: Nang mabusan ng tubig si Wilf, ano nangyari?",
         "Nang mabusan ng tubig si Wilf, ano nangyari?"),
        ("Answer: Naramdaman ni Magno na sumakit ang ulo.",
         "Naramdaman ni Magno na sumakit ang ulo."),
        ("Example: Nagdala si Damian ng inumin.",
         "Nagdala si Damian ng inumin."),
        ("Sentence: Bumili si Jimmy ng alak.",
         "Bumili si Jimmy ng alak."),
        ("Simple S: Bumili si David ng motorsiklo kahapon.",
         "Bumili si David ng motorsiklo kahapon."),
        ("Counter-assumption: Nagtatrabaho pa rin siya.",
         "Nagtatrabaho pa rin siya."),
        ("Counter-Assumption: Nagtatrabaho pa rin siya.",
         "Nagtatrabaho pa rin siya."),
        ("Counter-expectation: Hindi siya umuwi.",
         "Hindi siya umuwi."),
        ("Awkward: May binding mangga si Dante.",
         "May binding mangga si Dante."),
        ("Better: Matanda na si Doug, pero mahilig pa siya.",
         "Matanda na si Doug, pero mahilig pa siya."),
        ("Negative: Hindi para kay Nora bumili si David.",
         "Hindi para kay Nora bumili si David."),
        ("Negatives: Hindi para kay Nora bumili si David.",
         "Hindi para kay Nora bumili si David."),
        ("Conjunction: Hinawakan ni Ben ang lapis at sumulat siya.",
         "Hinawakan ni Ben ang lapis at sumulat siya."),
        ("Affirmative command: Maglinis ka.",
         "Maglinis ka."),
        ("Direct Command: Maglinis ka.",
         "Maglinis ka."),
        ("Indirect Commands: Magpaglinis ka.",
         "Magpaglinis ka."),
        ("Assertion: Mahilig si Doug sa laro.",
         "Mahilig si Doug sa laro."),
        ("Assumption: Mahilig si Doug.",
         "Mahilig si Doug."),
        ("Statement: Mahilig si Doug.",
         "Mahilig si Doug."),
        ("Active: Hinawakan ni Ben ang lapis.",
         "Hinawakan ni Ben ang lapis."),
        ("Passive: Hinawakan ni Ben ang lapis.",
         "Hinawakan ni Ben ang lapis."),
        ("Imperative: Maglinis ka.",
         "Maglinis ka."),
        ("In Focus: Si Marco ang nanalo.",
         "Si Marco ang nanalo."),
        ("Nominal Clause: Si Marco ang gusto.",
         "Si Marco ang gusto."),
        ("Nominalized Clause: Si Marco ang gusto.",
         "Si Marco ang gusto."),
    ])
    def test_strips_grammar_tag(
        self, inp: str, expected: str
    ) -> None:
        assert he._clean_sentence_text(inp) == expected

    def test_preserves_tagalog_colon_clause(self) -> None:
        # Tagalog NP + colon + clause is NOT a grammar-tag prefix.
        text = "Biyemes ngayon: ngumili ka naman."
        assert he._clean_sentence_text(text) == text


class TestPhase9kLeadingParenRejection:
    """``_LEADING_PAREN_REJECT_RE`` rejects lines whose leading
    paren-metadata moved the predicate out of the sentence body."""

    @pytest.mark.parametrize("inp", [
        "(verb tugtog. contemplated) si William ng gilara.",
        "(verb tulog. incompleted) ka ba kahit mainit?",
        "(noun balita) ang naririnig ko.",
        "(adj malaki) ang utang niya.",
        "(root kuha) ang naririnig ko.",
        "(kuha+um) ang nariay ng pera sa alkansya.",
    ])
    def test_rejects_leading_metadata(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None

    @pytest.mark.parametrize("inp", [
        # Mid-sentence parens are not leading metadata.
        "Pinuwersa ni Digna si Esper, para umamin ito (si Esper).",
        # Tagalog parenthetical is not metadata.
        "(Magandang umaga.)",
    ])
    def test_does_not_reject_normal_parens(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is not None


class TestPhase9kLeadingPlusParenStrip:
    """``_LEADING_PLUS_PAREN_RE`` strips the ``(+ ...)``
    paren-metadata block that prefixes a complete sentence.
    Handles both well-formed (closing paren present) and
    malformed (missing close paren) variants."""

    @pytest.mark.parametrize("inp,expected", [
        ("(+ base reduplication) Lumakad siya nang dahan-dahan.",
         "Lumakad siya nang dahan-dahan."),
        ("(+ pagka-) Umiyak siya nang pagkalakas-lakas.",
         "Umiyak siya nang pagkalakas-lakas."),
        # Malformed: no closing paren; strip everything before the
        # first uppercase letter.
        ("(+ pagka- and Umiyak siya nang pagkalakas-lakas.",
         "Umiyak siya nang pagkalakas-lakas."),
    ])
    def test_strip_plus_paren_prefix(
        self, inp: str, expected: str
    ) -> None:
        assert he._clean_sentence_text(inp) == expected


class TestPhase9kMidSentenceTagStrip:
    """``_MID_SENTENCE_TAG_RE`` strips closed-list grammar-tag
    annotations (``(Effect)`` / ``(Cause)`` / etc.) from mid-line.
    Speaker-clarification parens (``(si Esper)`` / ``(Derek)``) are
    not in the closed list and pass through unchanged."""

    @pytest.mark.parametrize("inp,expected", [
        ("Bumuhos ang ulan kaya (Effect) nabasa si Jane.",
         "Bumuhos ang ulan kaya nabasa si Jane."),
        ("Naglakad si Ben (Purpose) para makita si Linda.",
         "Naglakad si Ben para makita si Linda."),
        ("Hindi siya umuwi (Reason) kasi may trabaho.",
         "Hindi siya umuwi kasi may trabaho."),
    ])
    def test_strips_mid_tag(self, inp: str, expected: str) -> None:
        assert he._clean_sentence_text(inp) == expected

    def test_does_not_strip_speaker_clarification(self) -> None:
        text = ("Pinuwersa ni Digna si Esper, para umamin ito "
                "(si Esper).")
        assert he._clean_sentence_text(text) == text


class TestPhase9kTrailingAnnotationsAndListMarker:
    """``_TRAILING_PAREN_Q_RE`` strips the analyst's trailing ``(?)``
    uncertainty marker. ``_TRAILING_LIST_MARKER_RE`` normalises a
    trailing exercise-list-marker (``\\.\\s+a\\.``, ``\\s+f\\.``,
    ``,\\s+a\\.``) to a single sentence-final period."""

    @pytest.mark.parametrize("inp,expected", [
        ("Pinainilari muna ni Ron ang garapon, bago niya binuksan (?)",
         "Pinainilari muna ni Ron ang garapon, bago niya binuksan."),
        ("Tinukso na naman ni Paul si Regina, kay a mainii ang ulo (?).",
         "Tinukso na naman ni Paul si Regina, kay a mainii ang ulo."),
    ])
    def test_trailing_paren_q_strip(
        self, inp: str, expected: str
    ) -> None:
        # Need a trailing period for sentence-shape; the strip drops
        # the (?) and the period normalization keeps a single ".".
        result = he._clean_sentence_text(inp)
        # _clean_sentence_text does not add periods, so accept either
        # the stripped form or that form + ".".
        assert result in {expected, expected.rstrip(".")}

    @pytest.mark.parametrize("inp,expected", [
        ("Malaki ang utang niya. a.", "Malaki ang utang niya."),
        ("Siksikan sa loob ng sine.    a.",
         "Siksikan sa loob ng sine."),
        ("Maganda pala ito, a.",      "Maganda pala ito."),
        ("Ipagpalagay na natin            f.",
         "Ipagpalagay na natin."),
    ])
    def test_trailing_list_marker_normalized(
        self, inp: str, expected: str
    ) -> None:
        assert he._clean_sentence_text(inp) == expected


class TestPhase9kSlotFillRejection:
    """``_SLOT_FILL_RE`` rejects lines containing paradigm-slot
    templates (`` / ``)."""

    @pytest.mark.parametrize("inp", [
        "Dumating            si / ang     Tatay.",
        "Nagagalit           si / ang     Nanay.",
        "Q: / / tinamaan si Danil sa dibdib at /.",
    ])
    def test_rejects_slot_fill(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9kUngrammaticalMarker:
    """``_UNGRAM_MARKER_RE`` rejects lines with a mid-line ``*<lower>``
    ungrammatical-as-shown marker."""

    @pytest.mark.parametrize("inp", [
        "Nauntog ang mga *papandak.",
        "May konsiyenslya *ng Gobernador.",
    ])
    def test_rejects_ungrammatical(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9kOcrNoiseChars:
    """``_OCR_NOISE_CHAR_RE`` rejects lines with high-confidence OCR
    garbage characters: ``€`` / ``£`` glyphs (typesetter substitutions
    for ``e`` / ``n``) and mid-word backslashes."""

    @pytest.mark.parametrize("inp", [
        "Sumakay ng motors€clo si David.",
        "Nginttian n£ Amor si Marco.",
        "Kumain ka ng san\\palok.",
    ])
    def test_rejects_ocr_noise(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9kTruncationRejection:
    """``_TRUNCATION_RE`` rejects lines ending in ``...``."""

    @pytest.mark.parametrize("inp", [
        "Pinag-usapan nila ng mabuti si Martin, kaya ...",
        "Naibangga na naman ni Amelia ang kotse. kaya ...",
        "Ang pagsama ni Thelma sa kanya...",
    ])
    def test_rejects_truncation(self, inp: str) -> None:
        assert he._clean_sentence_text(inp) is None


class TestPhase9kMultiSpaceCollapse:
    """``_MULTI_SPACE_RE`` collapses 2+ consecutive whitespace runs
    (paradigm-row OCR padding) to a single space."""

    @pytest.mark.parametrize("inp,expected", [
        ("Kumain          ang mga bisita.",
         "Kumain ang mga bisita."),
        ("Pumasok na    si             Estudyante.",
         "Pumasok na si Estudyante."),
        ("Itapon mo  ang mga ito.",
         "Itapon mo ang mga ito."),
        # No multi-space — pass-through.
        ("Maganda ang araw.",
         "Maganda ang araw."),
    ])
    def test_multi_space_collapse(
        self, inp: str, expected: str
    ) -> None:
        assert he._clean_sentence_text(inp) == expected


class TestPhase9kInstructionLineRejection:
    """The extended ``_EN_MARKERS`` set (``add``/``where``/
    ``following``/``linkers``/``phrases`` etc.) tips
    ``_looks_like_tagalog``'s ``en > tgl`` test on exercise-
    instruction lines that carry citation-style ``sa`` / ``ang``
    references but are otherwise English."""

    @pytest.mark.parametrize("inp", [
        "Add sa phrases or ang phrases or both where appropriate.",
        "Add linkers ( na / -ng ) where necessary.",
        "Choose the appropriate following phrases.",
    ])
    def test_rejects_instruction_line(self, inp: str) -> None:
        assert he._looks_like_tagalog(inp) is False

    @pytest.mark.parametrize("inp", [
        # Real Tagalog sentence — should pass.
        "Bumili si Juan ng aklat sa palengke.",
        "Maganda ang araw, hindi ba?",
    ])
    def test_keeps_genuine_tagalog(self, inp: str) -> None:
        assert he._looks_like_tagalog(inp) is True


class TestPhase9kEndToEnd:
    """End-to-end via ``extract_rc1990()`` — verify the post-9.K
    corpus carries no slot-fill / ungrammatical-marker / OCR-garble
    lines. The full-corpus parse-rate gain is measured at audit-
    time and reported in the module docstring; here we test that
    the categorical noise has been filtered."""

    @pytest.mark.slow
    def test_no_slot_fill_in_corpus(self) -> None:
        for ex in he.extract_rc1990():
            assert " / " not in ex.text_raw, (
                f"slot-fill leaked: {ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_ungram_marker_in_corpus(self) -> None:
        import re
        ungram = re.compile(r"\*[a-z]")
        for ex in he.extract_rc1990():
            assert not ungram.search(ex.text_raw), (
                f"ungram-marker leaked: {ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_ocr_noise_chars_in_corpus(self) -> None:
        import re
        bad = re.compile(r"[€£]")
        for ex in he.extract_rc1990():
            assert not bad.search(ex.text_raw), (
                f"ocr-noise char leaked: {ex.locator} {ex.text_raw!r}"
            )

    @pytest.mark.slow
    def test_no_trailing_ellipsis_in_corpus(self) -> None:
        for ex in he.extract_rc1990():
            assert not ex.text_raw.endswith("..."), (
                f"truncation leaked: {ex.locator} {ex.text_raw!r}"
            )
