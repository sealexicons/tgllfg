# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

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
  ``tag-init`` precedent). The LEMMA preserving the canonical
  hyphenated user-visible form.

  Phase 6.I Commit 3 (§18.1.2 L105 close) migrated ``paminsan-
  minsan`` from a static lex entry to **productive derivation**
  via the ``adv_redup`` paradigm cell (``data/tgl/paradigms.yaml``)
  + the analyzer's ``_index_particle_paradigms`` method. The
  ``minsan`` lex entry carries ``affix_class: [adv_redup]`` to
  opt into the derivation; the productive surface, feats, and
  hyphenated LEMMA are identical to the previous static analysis.

The existing Phase 5f rule constrains on ``ADV_TYPE=FREQUENCY``
and lifts the AdvP into the matrix's ADJUNCT set. No matrix-level
lift of FREQ_VALUE — downstream consumers iterate ADJUNCT for
the marker.
"""

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
        """Phase 6.I Commit 3 (§18.1.2 L105 close): verifies the
        productive ``adv_redup`` paradigm cell produces exactly
        one analysis for the hyphen-merged surface
        ``paminsanminsan``, with no spurious double-parse from a
        residual static-entry / productive overlap or from the
        bare ``minsan`` reading.

        Pre-Phase-6.I this assertion exercised a static
        ``paminsanminsan`` lex entry; post-6.I the analysis is
        generated by the analyzer's ``_index_particle_paradigms``
        method from the ``minsan`` base with ``affix_class:
        [adv_redup]``. The single-parse invariant is unchanged."""
        parses = parse_text("Pumupunta ako paminsan-minsan.")
        assert len(parses) == 1


class TestPaminsanMinsanProductive:
    """Phase 6.I Commit 3 (§18.1.2 L105 close): the productive
    ``adv_redup`` paradigm cell now derives the ``paminsan-minsan``
    surface analysis from the ``minsan`` base. The pre-Phase-6.I
    static ``paminsanminsan`` lex entry has been removed."""

    def test_productive_analysis_matches_baseline(self) -> None:
        """The productive analysis carries the canonical hyphenated
        LEMMA, FREQ_VALUE=OCCASIONAL, and ADV_TYPE=FREQUENCY —
        identical to the previous static entry."""
        from tgllfg.morph.analyzer import _get_default
        analyses = _get_default()._index.particles.get(
            "paminsanminsan", []
        )
        assert len(analyses) == 1, (
            f"expected exactly one analysis for 'paminsanminsan', "
            f"got {len(analyses)}"
        )
        a = analyses[0]
        assert a.lemma == "paminsan-minsan"
        assert a.pos == "ADV"
        assert a.feats.get("ADV_TYPE") == "FREQUENCY"
        assert a.feats.get("FREQ_VALUE") == "OCCASIONAL"
        assert a.feats.get("LEMMA") == "paminsan-minsan"

    def test_bare_minsan_unaffected(self) -> None:
        """The bare ``minsan`` analysis (FREQ_VALUE=SOMETIMES)
        continues to index unchanged via the existing particle-
        loading loop; the affix_class addition is purely for
        paradigm cell matching."""
        from tgllfg.morph.analyzer import _get_default
        analyses = _get_default()._index.particles.get("minsan", [])
        assert len(analyses) >= 1
        adv_minsan = [
            a for a in analyses
            if a.pos == "ADV" and a.feats.get("FREQ_VALUE") == "SOMETIMES"
        ]
        assert len(adv_minsan) == 1
        assert adv_minsan[0].lemma == "minsan"
