"""Phase 5l Commit 10: indirect speech — SAY_CLASS lex tagging.

Roadmap §12.1 / plan-of-record §5.7, §6 Commit 10.

**Scope reduction note.** The plan §1 / §2 assumed that the
existing Phase 4 ``na``-linker complement pattern admits a
finite-S complement of report-class verbs (``Sinabi niya na
pumunta si Maria.`` "He said that Maria went."). Recon during
this commit revealed no such grammar rule exists today —
``Sinabi niya na pumunta si Maria.`` returns 0 parses. Building
the OV-with-na-S complement rule requires non-trivial
interaction work with the OV verb's a-structure (the said-thing
fills the SUBJ slot but is a finite-S, not the typical NOM-NP),
which is bigger than this commit's scope.

This commit therefore delivers what's safely deliverable:

* **SAY_CLASS=YES** lex tagging on report-class verbs in
  ``data/tgl/verbs.yaml``. Today's commit tags ``sabi`` (one
  representative); follow-on can extend to additional verbs
  (``balita``, ``sumagot``, etc.) once the parsing rule lands.
* The diagnostic feat **propagates onto inflected forms**
  via the paradigm engine — ``sinabi`` (OV PFV) and
  ``sasabihin`` (OV CTPL) both carry ``SAY_CLASS=YES``.
* The pinned 0-parse for the canonical indirect-speech
  sentence (``Sinabi niya na pumunta si Maria.``) is recorded
  as a known limitation; a future Phase 5l follow-on or Phase
  6 (functional uncertainty) will land the OV-with-na-S
  complement rule.

This makes the SAY_CLASS infrastructure available for the
follow-on without committing to a half-built parsing path.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer
from tgllfg.core.pipeline import parse_text


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === SAY_CLASS lex tagging ============================================


class TestSayClassLexTagging:
    """The ``sabi`` lemma carries ``feats: {SAY_CLASS: "YES"}`` in
    ``data/tgl/verbs.yaml``. The feat propagates onto inflected
    forms via the paradigm engine for selected cells."""

    def test_sinabi_carries_say_class(self) -> None:
        """``sinabi`` (OV PFV) — the canonical indirect-speech
        matrix verb form."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sinabi"))
        say = [a for a in out if a.feats.get("SAY_CLASS") == "YES"]
        assert len(say) == 1
        assert say[0].lemma == "sabi"
        assert say[0].feats.get("VOICE") == "OV"
        assert say[0].feats.get("ASPECT") == "PFV"

    def test_sasabihin_carries_say_class(self) -> None:
        """``sasabihin`` (OV CTPL) — future indirect-speech form."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("sasabihin"))
        say = [a for a in out if a.feats.get("SAY_CLASS") == "YES"]
        assert len(say) == 1
        assert say[0].lemma == "sabi"

    def test_say_class_does_not_leak_to_other_verbs(self) -> None:
        """SAY_CLASS is absent on non-report verbs (kumain, pumunta).
        Pin to guard against accidental over-tagging."""
        analyzer = Analyzer.from_default()
        for surf in ("kumain", "pumunta", "tumakbo"):
            out = analyzer.analyze_one(_tok(surf))
            for a in out:
                assert a.feats.get("SAY_CLASS") is None, (
                    f"SAY_CLASS unexpectedly present on {surf!r} "
                    f"analysis (lemma={a.lemma})"
                )


# === Pinned indirect-speech 0-parse (deferred) =======================


class TestIndirectSpeechParseDeferred:
    """The canonical indirect-speech sentence
    ``Sinabi niya na pumunta si Maria.`` does not parse today.
    This pin tracks the gap; flipping the assertion to
    ``len(parses) >= 1`` is the trigger for the follow-on
    parsing work.

    Phase 5n.A Commit 26 (§18 L89.1) extended the pin from one
    canonical sentence to 12 corpus fixtures spanning OV PFV /
    IPFV / CTPL × varied actor PRONs × AV-intransitive /
    AV-transitive embeds (with one negation case). All 12 are
    currently 0-parse-pinned; Commit 27 lands the
    OV-with-na-S complement rule and flips them to positive."""

    def test_canonical_indirect_speech_zero_parse(self) -> None:
        parses = parse_text("Sinabi niya na pumunta si Maria.")
        assert len(parses) == 0, (
            "Indirect-speech parsing is now possible — Phase 5l "
            "follow-on or Phase 6 may have landed the OV-with-na-S "
            "complement rule. Update this test and add positive "
            "tests for the new shape."
        )

    @pytest.mark.parametrize("sentence", [
        # PFV (sinabi)
        "Sinabi niya na pumunta si Maria.",
        "Sinabi mo na pumunta si Pedro.",
        "Sinabi ko na kumain si Maria.",
        "Sinabi nila na bumili si Maria ng aklat.",
        "Sinabi niya na pumunta sila.",
        # IPFV (sinasabi)
        "Sinasabi niya na pumunta si Maria.",
        "Sinasabi mo na kumain ako.",
        "Sinasabi nila na bumili kami ng aklat.",
        # CTPL (sasabihin)
        "Sasabihin niya na pumunta si Maria.",
        "Sasabihin ko na kumain ako bukas.",
        "Sasabihin nila na bumili kami ng aklat.",
        # PFV with embed transitive
        "Sinabi niya na bumili si Maria ng aklat.",
    ])
    def test_phase5n_corpus_zero_parse(self, sentence: str) -> None:
        """Phase 5n.A Commit 26 corpus fixtures — all 12 currently
        0-parse. Commit 27 lands the OV-with-na-S complement rule
        and flips this to ``len(parses) >= 1``."""
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"{sentence!r} now parses — Phase 5n.A Commit 27 may "
            "have landed the OV-with-na-S complement rule. Update "
            "this test and add positive tests for the new shape."
        )
