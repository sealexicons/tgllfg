"""Phase 8.Q: regression test for the harvest script's OOV probe.

The OOV probe in ``scripts/harvest_exemplars.py`` underpins
the Wave 3 audit's lex-OOV signal. Before 8.Q, the probe applied
only ``tokenize`` + ``analyze_tokens`` — missing the
``split_linker_ng`` step that the real parser pipeline runs (Phase
4 §7.5). As a result, vowel-final clitic-glued surfaces like
``akong``, ``bang``, ``anong``, ``magandang`` were reported as OOV
even though the parser pipeline correctly splits them into base +
``-ng`` linker.

8.Q fixes the probe to mirror the parser pipeline. This test pins
the corrected behavior so a regression on either ``split_linker_ng``
or the probe wiring is caught.

The probe is also re-promoted to module-level so it can be imported
for this test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add the scripts directory to sys.path so the harvest script is
# importable. (The script is at ``scripts/harvest_exemplars.py``;
# treating it as a one-off audit driver rather than a package.)
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from harvest_exemplars import oov_probe  # type: ignore[import-not-found]  # noqa: E402


class TestOovProbeCliticGlue:
    """Forms that ``split_linker_ng`` decomposes should NOT appear in
    the OOV probe's output.

    Coverage:
    - NOM-PRON + ``-ng``: ``akong`` (ako+ng), ``kong`` (ko+ng),
      ``mong`` (mo+ng), ``siyang`` (siya+ng), ``kanyang``,
      ``kanilang``.
    - Q particle + ``-ng``: ``bang`` (ba+ng).
    - Wh-PRON + ``-ng``: ``anong`` (ano+ng).
    - N-deletion sandhi DAT-PRONs: ``aking`` (akin+ng with stem-
      final n-deletion).
    - ADJ + ``-ng``: ``magandang`` (maganda+ng).
    - Adverb + ``-ng``: ``gustong`` (gusto+ng).
    - NUM + ``-ng``: ``isang`` (isa+ng).
    """

    @pytest.mark.parametrize("text,expected_not_in_oov", [
        ("Akong kumain ng saging.",       "Akong"),
        ("Kong nakita ng bata.",          "Kong"),
        ("Bang gusto mo?",                "Bang"),
        ("Anong gusto mo?",               "Anong"),
        ("Siyang nagluto.",               "Siyang"),
        ("Magandang aklat ito.",          "Magandang"),
        ("Isang lalaki ang doktor.",      "Isang"),
        ("Aking aklat ito.",              "Aking"),
        ("Gustong matulog.",              "Gustong"),
    ])
    def test_clitic_glue_not_in_oov(
        self, text: str, expected_not_in_oov: str
    ) -> None:
        """The clitic-glued surface should not appear in the probe's
        OOV output — ``split_linker_ng`` splits it into base + ``-ng``
        and both halves analyze to known categories."""
        oov = oov_probe(text)
        # Compare case-insensitively (the probe preserves original
        # casing; the audit's downstream lowercases).
        oov_lower = {tok.lower() for tok in oov}
        assert expected_not_in_oov.lower() not in oov_lower, (
            f"clitic-glued surface {expected_not_in_oov!r} unexpectedly "
            f"reported as OOV in {text!r}; probe OOV = {oov!r}"
        )


class TestOovProbeLinkerArtifactNotInOov:
    """The synthetic ``-ng`` token emitted by ``split_linker_ng``
    must not leak into the OOV output. It's a parser-internal
    artifact for category dispatch; reporting it as OOV would
    massively inflate the lex-gap signal."""

    def test_synthetic_linker_not_in_oov(self) -> None:
        oov = oov_probe("Magandang aklat ito.")
        # The synthetic linker token's surface is ``-ng``.
        assert "-ng" not in oov


class TestOovProbeRealOov:
    """Words that are genuinely OOV in the analyzer (Wave 3 audit
    examples) should still be reported. The 8.Q fix doesn't change
    the real-OOV reporting; it just removes the false positives on
    clitic-glued surfaces."""

    def test_real_oov_still_reported(self) -> None:
        # Anti-deferral pin chain — keeps the assertion on a real
        # current-OOV token, repinned whenever the previous anchor
        # is closed by a lex-add or paradigm sub-PR:
        # pandanggo (8.Q-orig) → closed-in-9.C → mahusay → closed-in-9.F
        # → bare ``kilala`` → closed-in-9.O (added as bare ADJ in
        # adjectives.yaml) → ``kumbidado`` → closed in 9.X.pre-1.22
        # (added as Spanish-loan bare ADJ in adjectives.yaml) →
        # ``gawin`` → closed in 9.X.pre-4.2 (new ``a_deletion``
        # sandhi flag on ``gawa`` root) → ``kunin`` (current).
        # ``kunin`` is the OV-imperative paradigm form of root
        # ``kuha`` (which IS in the lex). Its non-generation
        # involves an irregular stem alternation (kuha → kun- via
        # /h/ → /n/ substitution + /a/-deletion) that the current
        # ``in_oblig`` paradigm engine doesn't handle — a
        # paradigm-cell gap the lex sweep can't close.
        oov = oov_probe("Kunin mo ang aklat.")
        oov_lower = {tok.lower() for tok in oov}
        assert "kunin" in oov_lower

    def test_real_ng_ending_oov_still_reported(self) -> None:
        # ``huling`` (final / last — bare ``huli`` is the ADJ root)
        # is a real lex gap that happens to end in -ng. Since its
        # stem ``huli`` is not a known surface either, the
        # ``split_linker_ng`` splitter doesn't fire (the rule only
        # decomposes -ng-glued forms when the stem is a known
        # surface), and the morph analyzer reports the full
        # ``huling`` form as _UNK.
        # (Originally pinned on ``tulong``; closed-in-9.C and
        # repinned on ``tanong``; ``tanong`` closed-in-9.D and
        # repinned on ``huling``. Note: ``tabing`` would not work
        # as a pin target post-9.D because ``tabi`` is now a known
        # surface, so the splitter does decompose ``tabing`` →
        # ``tabi`` + -ng.)
        oov = oov_probe("Sa huling oras.")
        oov_lower = {tok.lower() for tok in oov}
        assert "huling" in oov_lower


class TestOovProbeEdgeCases:
    """Edge cases the pre-8.Q probe handled correctly; pin them so
    the refactor to module-level doesn't regress."""

    def test_empty_text(self) -> None:
        assert oov_probe("") == []

    def test_punctuation_only(self) -> None:
        assert oov_probe(". , ! ?") == []

    def test_single_char_tokens_filtered(self) -> None:
        # Single-char tokens are filtered as likely OCR character-
        # spacing artifacts. The probe should drop them even when
        # they're _UNK.
        oov = oov_probe("a b c d e f")
        assert all(len(tok) >= 2 for tok in oov)
