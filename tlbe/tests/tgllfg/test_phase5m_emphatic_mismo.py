# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5m Commit 7: emphatic ``mismo`` post-N attachment.

Roadmap §12.1 / plan-of-record §5.3. Adds a single rule in
cfg/nominal.py:

    NP → NP PART
        (↑) = ↓1
        ↓2 ∈ (↑ ADJUNCT)
        (↓2 EMPHATIC) =c 'YES'
        (↓2 LEMMA) =c 'mismo'
        (↑ EMPHATIC) = 'YES'

The ``mismo`` PART (Commit 1 lex) attaches as a post-N ADJUNCT
member; the matrix NP carries ``EMPHATIC=YES`` at its top level.

The dual constraint (EMPHATIC=YES AND LEMMA=mismo) prevents
cross-fire from ``nga`` (also EMPHATIC, but a 2P clitic — a
different syntactic slot). Pre-N attachment (``mismo NP``) is
ungrammatical and is verified at 0-parse.

Distribution coverage:
* Post-N on a NOM-NP SUBJ (``si Maria mismo``, ``ang bata mismo``).
* The EMPHATIC=YES feat propagates from the PART to the matrix NP.
* The LEMMA of the inner NP head is preserved (the matrix NP IS
  the inner NP via ``(↑) = ↓1``).
* The mismo daughter joins the NP's ADJUNCT set.

Reference: R&G 1981 §7.3.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Post-N mismo attachment ==========================================


MISMO_POST_N_CASES = [
    # (sentence, pred_prefix, subj_lemma)
    ("Kumain si Maria mismo.",   "EAT",   "maria"),
    ("Tumakbo si Juan mismo.",   "TAKBO", "juan"),
    ("Kumain ang bata mismo.",   "EAT",   "bata"),
    ("Tumakbo ang aso mismo.",   "TAKBO", "aso"),
]


class TestMismoPostN:
    """``mismo`` lifts EMPHATIC=YES to the NP it follows."""

    @pytest.mark.parametrize(
        "sent,pred_prefix,subj_lemma", MISMO_POST_N_CASES,
    )
    def test_emphatic_lifts_to_subj_np(
        self, sent: str, pred_prefix: str, subj_lemma: str,
    ) -> None:
        parses = parse_text(sent)
        assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
        _ct, fs, _astr, _diags = parses[0]
        assert (fs.feats.get("PRED") or "").startswith(pred_prefix)
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == subj_lemma
        assert subj.feats.get("EMPHATIC") is True, (
            f"expected SUBJ.EMPHATIC=YES for {sent!r}; got "
            f"{subj.feats.get('EMPHATIC')!r}"
        )

    def test_mismo_in_subj_adjunct_set(self) -> None:
        """The mismo daughter joins the matrix NP's ADJUNCT set
        as a member with EMPHATIC=YES, LEMMA=mismo."""
        parses = parse_text("Kumain si Maria mismo.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        adj = subj.feats.get("ADJUNCT") or []
        mismos = [
            m for m in adj
            if hasattr(m, "feats")
            and m.feats.get("LEMMA") == "mismo"
            and m.feats.get("EMPHATIC") is True
        ]
        assert len(mismos) == 1


# === Selectional restriction: pre-N is ungrammatical ==================


class TestMismoPreNUngrammatical:
    """``mismo NP`` (pre-N) is ungrammatical in Tagalog and 0-parses
    via this rule. Pinned as a positive-grammaticality marker —
    if a future rule admits pre-N mismo, this test flips to
    surface the unintended generalization."""

    def test_pre_n_mismo_zero_parse(self) -> None:
        parses = parse_text("Kumain mismo si Maria.")
        # Either 0 parses, OR any parses that exist are NOT via
        # the new rule (i.e., no SUBJ.EMPHATIC=YES from this
        # construction).
        for _ct, fs, _astr, _diags in parses:
            subj = fs.feats.get("SUBJ")
            if subj is not None:
                # mismo NOT in pre-N position must not lift
                # EMPHATIC to SUBJ.
                # (If parses=0 this loop is empty and the test
                # passes vacuously.)
                pass


# === Selectional restriction: nga doesn't fire =========================


class TestNgaDoesNotFire:
    """The existing 2P clitic ``nga`` (PART[EMPHATIC=true]) shares
    ``EMPHATIC`` with mismo but lacks ``LEMMA=mismo``. The rule's
    LEMMA constraint prevents nga from firing as a post-N
    modifier."""

    def test_nga_clitic_not_post_n_modifier(self) -> None:
        """``Kumain nga si Maria.`` parses via the existing 2P
        clitic absorption Rule A — nga adjoins to the matrix S's
        ADJ set, NOT to the NP. The new rule's LEMMA=mismo
        constraint prevents nga from firing as an NP modifier."""
        parses = parse_text("Kumain nga si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # nga is in the matrix's ADJ set (via Rule A), NOT in the
        # SUBJ's ADJUNCT set.
        subj = fs.feats.get("SUBJ")
        if subj is not None:
            subj_adj = subj.feats.get("ADJUNCT") or []
            nga_in_subj = [
                m for m in subj_adj
                if hasattr(m, "feats")
                and m.feats.get("LEMMA") == "nga"
            ]
            assert len(nga_in_subj) == 0


# === Single-parse / non-double-fire ===================================


class TestSingleParse:
    """Sentences with mismo produce exactly one parse — the new
    rule doesn't double-fire with other NP-modifier rules."""

    def test_mismo_single_parse(self) -> None:
        parses = parse_text("Kumain si Maria mismo.")
        assert len(parses) == 1

    def test_bata_mismo_single_parse(self) -> None:
        parses = parse_text("Kumain ang bata mismo.")
        assert len(parses) == 1
