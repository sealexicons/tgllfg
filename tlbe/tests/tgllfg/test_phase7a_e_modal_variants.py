# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 7a.E: modal-rule variants (§18.1.1 items 6 + 7).

Two coordinated closures extending the Phase 5j modal-control
rule (``cfg/control.py:488-524``):

* **§3.5 — Full-NP SUBJ inside embedded clause.** Surface:
  ``Dapat na kumain si Maria.`` "Maria should eat." The Phase 5j
  rule required the matrix SUBJ NP between modal and linker
  (``Dapat si Maria na kumain.`` — marked / rare order). The
  new variants ``S → V[MODAL] PART[LINK=NA|NG] S`` accept a
  regular S as embedded daughter and structure-share matrix
  SUBJ with embedded SUBJ.

* **§3.6 — No-linker colloquial.** Surface:
  ``Hindi ka dapat kumain.`` Colloquial Tagalog drops the
  linker between modal and embedded V. Two new rule variants
  (clitic-NP via ``NP[CASE=NOM] + S_XCOMP``; full-NP via
  ``S`` daughter) tag the matrix with
  ``REGISTER='COLLOQUIAL'`` so downstream consumers can
  filter — addressing Phase 5j Commit 7's silent-drop concern.

References: S&O 1972 §5.30, R&G 1981 ch. 6 (modal
constructions).
"""

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


# === §3.5 — full-NP SUBJ inside embedded clause ======================


class TestFullNPModalLinker:
    """``S → V[MODAL] PART[LINK=NA|NG] S`` with raising-style
    SUBJ binding. Embedded S can be any regular clause; matrix
    SUBJ shares with embedded SUBJ."""

    @pytest.mark.parametrize(
        "sentence,modal_lemma,expected_subj_lemma",
        [
            ("Dapat na kumain si Maria.",       "dapat",     "maria"),
            ("Pwedeng kumain si Maria.",        "puwede",    "maria"),
            ("Maaaring kumain si Maria.",       "maaari",    "maria"),
            ("Dapat na kumain ang bata.",       "dapat",     "bata"),
        ],
    )
    def test_full_np_subj_modal_parses(
        self,
        sentence: str,
        modal_lemma: str,
        expected_subj_lemma: str,
    ) -> None:
        parses = parse_text(sentence)
        # Filter to modal-PRED parses (other readings may exist for
        # some lemmas, e.g., kailangan as a noun "need").
        modal_parses = [
            p for p in parses
            if "<SUBJ" in str(p[1].feats.get("PRED", ""))
            and modal_lemma.upper() in str(p[1].feats.get("PRED", "")).upper()
        ]
        assert modal_parses, (
            f"{sentence!r} should produce a modal parse with PRED "
            f"containing {modal_lemma.upper()}"
        )
        fs = modal_parses[0][1]
        subj = fs.feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("LEMMA") == expected_subj_lemma


# === §3.6 — no-linker colloquial =====================================


class TestNoLinkerColloquialModal:
    """No-linker variants of the modal rule emit
    ``REGISTER='COLLOQUIAL'`` on the matrix."""

    def test_hindi_ka_dapat_kumain(self) -> None:
        # `Hindi ka dapat kumain.` — clitic-NP, no linker, under
        # negation. The Phase 5j Commit 7 deliberate-zero-parse
        # case, now closed by Phase 7a.E §3.6.
        parses = parse_text("Hindi ka dapat kumain.")
        assert parses, "no-linker modal should parse"
        colloquial = [
            p for p in parses
            if p[1].feats.get("REGISTER") == "COLLOQUIAL"
        ]
        assert colloquial, (
            "at least one parse should carry REGISTER=COLLOQUIAL"
        )

    def test_dapat_kumain_si_maria(self) -> None:
        # Full-NP no-linker: `Dapat kumain si Maria.` "Maria
        # should eat" (colloquial). Combines §3.5 full-NP with
        # §3.6 no-linker.
        parses = parse_text("Dapat kumain si Maria.")
        assert parses, "no-linker full-NP modal should parse"
        colloquial = [
            p for p in parses
            if p[1].feats.get("REGISTER") == "COLLOQUIAL"
        ]
        assert colloquial, (
            "Dapat kumain si Maria. should produce a "
            "REGISTER=COLLOQUIAL parse"
        )

    def test_hindi_dapat_kumain_si_maria(self) -> None:
        # `Hindi dapat kumain si Maria.` — full-NP, no linker,
        # under negation. Closure of the §3.5 + §3.6 combined
        # case with POLARITY=NEG wrap from the Phase 4 hindi
        # rule.
        parses = parse_text("Hindi dapat kumain si Maria.")
        assert parses, (
            "no-linker full-NP modal under negation should parse"
        )


# === Regression: Phase 5j canonical forms unaffected =================


class TestPhase5jModalRegression:
    """The pre-Phase-7a.E modal rule variants (clitic-NP + linker)
    still produce their canonical parses."""

    @pytest.mark.parametrize(
        "sentence",
        [
            "Dapat akong kumain.",
            "Dapat kang kumain.",
            "Hindi ka dapat na kumain.",
        ],
    )
    def test_canonical_clitic_linker_form_parses(
        self, sentence: str
    ) -> None:
        parses = parse_text(sentence)
        assert parses, (
            f"Phase 5j canonical {sentence!r} should still parse"
        )
        # The canonical form does NOT carry REGISTER=COLLOQUIAL;
        # verify at least one parse is formal-register (no
        # REGISTER feat or REGISTER ≠ COLLOQUIAL).
        formal_parses = [
            p for p in parses
            if p[1].feats.get("REGISTER") != "COLLOQUIAL"
        ]
        assert formal_parses, (
            f"{sentence!r} should produce at least one formal "
            f"(non-COLLOQUIAL) parse"
        )
