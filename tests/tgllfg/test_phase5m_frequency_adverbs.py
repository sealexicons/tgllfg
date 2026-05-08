"""Phase 5m Commit 5: frequency adverbs at the clause level.

Roadmap §12.1 / plan-of-record §1 / §4.2. The Commit 1 ADV[
ADV_TYPE=FREQUENCY] lex entries route through the existing Phase
5f Commit 5 sentential-FREQ rule (``S → S AdvP[FREQUENCY]`` in
cfg/discourse.py:131-139) without any new grammar:

* ``madalas`` "often" — FREQ_VALUE=HIGH.
* ``palagi`` "always" — FREQ_VALUE=HABITUAL.
* ``lagi`` "always (clitic-host variant)" — FREQ_VALUE=HABITUAL.
* ``minsan`` "sometimes / once" — FREQ_VALUE=SOMETIMES.
* ``paminsan-minsan`` "occasionally" — FREQ_VALUE=OCCASIONAL.
  Hyphenated reduplication; the parse pipeline's merger collapses
  ``paminsan`` ``-`` ``minsan`` into the joined form
  ``paminsanminsan`` for analyzer lookup (Phase 5f Commit 14
  ``tag-init`` precedent), with the LEMMA preserving the canonical
  hyphenated user-visible form.

The existing Phase 5f rule constrains on ``ADV_TYPE=FREQUENCY``
and lifts the AdvP into the matrix's ADJUNCT set. No matrix-level
lift of FREQ_VALUE — downstream consumers iterate ADJUNCT for
the marker.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Per-adverb sentence parses =======================================


FREQUENCY_SENTENCES = [
    # (sentence, expected_pred_prefix, expected_lemma, expected_freq_value)
    ("Kumakain ako madalas.",          "EAT",   "madalas",          "HIGH"),
    ("Kumakain ako palagi.",           "EAT",   "palagi",           "HABITUAL"),
    ("Tumakbo ang bata lagi.",         "TAKBO", "lagi",             "HABITUAL"),
    ("Pumupunta siya minsan.",         "PUNTA", "minsan",           "SOMETIMES"),
    ("Pumupunta ako paminsan-minsan.", "PUNTA", "paminsan-minsan",  "OCCASIONAL"),
]


def _frequency_adjunct(fs):
    """Return the unique ADJUNCT member with ADV_TYPE=FREQUENCY,
    or None."""
    adj = fs.feats.get("ADJUNCT") or []
    freqs = [
        m for m in adj
        if hasattr(m, "feats")
        and m.feats.get("ADV_TYPE") == "FREQUENCY"
    ]
    return freqs[0] if len(freqs) == 1 else None


class TestFrequencyAdverbs:
    """Each frequency adverb adjoins clause-finally with the
    expected FREQ_VALUE. The matrix S's PRED is from the inner
    verb; the AdvP joins the matrix ADJUNCT set."""

    @pytest.mark.parametrize(
        "sent,pred_prefix,lemma,freq_value", FREQUENCY_SENTENCES,
    )
    def test_clause_final_frequency(
        self, sent: str, pred_prefix: str,
        lemma: str, freq_value: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        freq = _frequency_adjunct(fs)
        assert freq is not None, (
            f"expected exactly one FREQUENCY ADJUNCT for {sent!r}; "
            f"got ADJUNCT={fs.feats.get('ADJUNCT')!r}"
        )
        assert freq.feats.get("LEMMA") == lemma
        assert freq.feats.get("FREQ_VALUE") == freq_value


# === Compositional checks =============================================


class TestFrequencyComposition:
    """Frequency adverbs compose with other clause-level constructions
    without conflict — the new lex entries don't cross-fire."""

    def test_freq_with_negation(self) -> None:
        """``Hindi kumakain ang bata madalas.`` "The child doesn't
        eat often." — Phase 4 negation + Phase 5f FREQ adjunct
        compose. (FREQ must be clause-final, after the NP[CASE=NOM];
        FREQ between V and NP[CASE=NOM] doesn't compose under the
        existing Phase 4 V-frame rules.)"""
        parses = parse_text("Hindi kumakain ang bata madalas.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("POLARITY") == "NEG"
        freq = _frequency_adjunct(fs)
        assert freq is not None
        assert freq.feats.get("LEMMA") == "madalas"

    def test_freq_with_modal_particle(self) -> None:
        """``Siguro pumupunta siya palagi.`` "Maybe he always
        goes." — Phase 5m Commit 4 sentence-initial siguro +
        clause-final FREQ adverb."""
        parses = parse_text("Siguro pumupunta siya palagi.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJUNCT") or []
        # Both siguro and palagi appear as ADJUNCT members.
        lemmas = {m.feats.get("LEMMA") for m in adj if hasattr(m, "feats")}
        assert "siguro" in lemmas
        assert "palagi" in lemmas


# === Single-parse / non-double-fire ===================================


class TestSingleParse:
    """The new frequency adverbs produce exactly one parse — no
    spurious ambiguity from interactions with the existing makaisa /
    makalawa entries that share ADV_TYPE=FREQUENCY."""

    def test_madalas_single_parse(self) -> None:
        parses = parse_text("Kumakain ako madalas.")
        assert len(parses) == 1

    def test_paminsan_minsan_single_parse(self) -> None:
        """Verifies the merger emits a single token, no
        spurious double-parse from the bare ``minsan`` reading."""
        parses = parse_text("Pumupunta ako paminsan-minsan.")
        assert len(parses) == 1
