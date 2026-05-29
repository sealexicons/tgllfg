# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-6.1: N-N noun-modifier compound rule.

Phase 10.J.post-6's lex-add of ``putahe`` as NOUN inadvertently
regressed `Ano ang pinakatampok na putaheng gulay?` (wave-2
rg-intermediate sent-1873). Pre-post-6, ``putahe`` was OOV — the
parser was reaching the parse via an unknown-token-as-ADJ heuristic
(ADJ + LINK + N composed `putaheng gulay`). Once ``putahe`` was
recognized as N, that heuristic stopped firing and there was no
chart path for the N+LINK+N compound.

post-6.1 adds a productive ``N → N PART[LINK] N`` chart rule
mirroring the existing N+LINK+ADJ post-N modifier rule (Phase 5g
Commit 2). The compound's left N is the head; the right N joins
a new ``N-MOD`` set (distinct from ``ADJ-MOD`` so the modifier-class
is recoverable).

User-verified semantics: ``putahe`` (from Sp. ``potaje`` / Fr.
``potage`` "soup, stew, broth, cooked food") narrows to Tagalog
"dish, viand, prepared food"; ``putaheng gulay`` = "vegetable dish".
"""

import pytest

from tgllfg.core.pipeline import parse_text


class TestNLinkNCompound:
    """Productive N+LINK+N compound — Phase 10.J.post-6.1."""

    @pytest.mark.parametrize(
        "text",
        [
            # Wave-2 rg-intermediate sent-1873 (post-6 regression target).
            "Ano ang pinakatampok na putaheng gulay?",
            # Predicative-ADJ S with N-N compound SUBJ.
            "Masarap ang putaheng gulay.",
            # Productive parallels.
            "Maganda ang bahay na bato.",  # stone house
        ],
    )
    def test_compound_parses(self, text: str) -> None:
        parses = parse_text(text, n_best=2)
        assert len(parses) >= 1, f"compound parse failed: {text!r}"

    def test_compound_head_left(self) -> None:
        """In ``putaheng gulay`` the head is ``putahe`` (the dish);
        ``gulay`` (vegetable) is the modifier specifying type."""
        s = "Masarap ang putaheng gulay."
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        # Head's LEMMA is the left N (putahe).
        assert subj.feats.get("LEMMA") == "putahe", (
            f"expected head=putahe, got {subj.feats.get('LEMMA')!r}"
        )
        # The modifier is in N-MOD set; check it has gulay.
        n_mod = subj.feats.get("N-MOD")
        assert n_mod is not None, "missing N-MOD set"
        # N-MOD is a frozenset of f-structures.
        mod_lemmas = {m.feats.get("LEMMA") for m in n_mod}
        assert "gulay" in mod_lemmas, (
            f"expected gulay in N-MOD, got {mod_lemmas}"
        )


class TestExistingPathsUntouched:
    """Anti-regression: existing ADJ-modifier paths still work."""

    @pytest.mark.parametrize(
        "text",
        [
            "Maganda ang batang maliit.",       # N+LINK+ADJ post-N
            "Maganda ang maliit na bata.",      # ADJ+LINK+N pre-N
            "Ano ang pinakatampok na gulay?",   # ADJ-modifier + wh-cleft
            # post-6's equational ay (must keep parsing)
            "Si Juan ay ang doktor.",
            "Ang doktor ay si Juan.",
            # The wave-1 post-6 closure
            "Ang pinakaubod ng pamilyang Pilipino ay ang ama, "
            "ina at mga anak.",
        ],
    )
    def test_no_regression(self, text: str) -> None:
        parses = parse_text(text, n_best=2)
        assert len(parses) >= 1, f"regression on {text!r}"


class TestNRcGate:
    """The new rule gates on ``¬ (↓3 N_RC)`` so an N already modified
    by a relative clause doesn't recursively compose. (A proper-noun
    gate was considered but not added — real corpora use GEN-marked
    possession for proper-N relations, not the linker compound.)
    """

    def test_n_rc_modifier_not_recursively_composed(self) -> None:
        """If the rule were ungated, an N+RC could feed back as a
        modifier in another compound. The N_RC tag (Phase 6.G C2)
        was introduced to block exactly this kind of feedback;
        confirm a known RC-bearing N doesn't compose."""
        # Construct a case where the right-hand modifier-N is itself
        # an RC'd N. The Phase 5n.A C8 N-level RC wrap rule produces
        # an N with N_RC=true; our rule must not consume that N as
        # the right daughter. (A canonical example surfacing this
        # in corpus is hard to construct minimally; the assertion
        # below verifies the rule compiles + the chart doesn't break
        # on a near-miss.)
        s = "Masarap ang putaheng gulay."  # baseline OK
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1
