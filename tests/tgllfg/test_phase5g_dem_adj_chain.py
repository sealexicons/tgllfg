"""Phase 5g Commit 6: demonstrative × adj-modified N composition.

Phase 5e Commit 16 added the pre-modifier demonstrative rules
(``NP → DET[CASE=X, DEM=YES] PART[LINK] N`` for PROX / MED / DIST
× three cases × two linker variants — see ``cfg/nominal.py`` lines
~155-225). Phase 5d Commit 3 had earlier added the post-modifier
demonstrative rules (``NP → NP PART[LINK] DET[DEM=YES]``).

Both rule families took bare ``N`` (or bare ``NP``) at their head
slot. The Phase 5g Commit 2 NP-internal modifier rules
(``N → ADJ PART N``, ``N → N PART ADJ``) are right-recursive — an
adj-modified N is itself N — so the dem rules should chain
through adj modifiers unchanged.

This commit verifies the composition empirically and patches the
one disambiguator gap that surfaced (ADJ + ``na`` + DEM-DET
right-context: the linker for post-modifier dem on adj-modified
heads, e.g., ``ang batang mabait na ito``). The disambiguator's
right-context check now admits four linker-licensing targets:

* NOUN / N / ADJ (Commit 2 NP-internal modifier).
* VERB (Commit 5 manner-adverb).
* DET / ADP with ``DEM=YES`` (Commit 6 post-modifier dem on
  adj-modified head).

Plain DET / ADP / PRON / clause-end right contexts continue to
fall through and let the placement pass treat ``na`` as the
ALREADY 2P clitic (predicative-adj clauses ``Maganda na ka.`` /
``Maganda na ang bata.``).
"""

from __future__ import annotations

import pytest

from tgllfg.common import FStructure
from tgllfg.morph import analyze_tokens
from tgllfg.text import tokenize, split_enclitics, split_linker_ng
from tgllfg.clitics import disambiguate_homophone_clitics
from tgllfg.pipeline import parse_text


def _first_parse(text: str) -> FStructure | None:
    parses = parse_text(text, n_best=1)
    if not parses:
        return None
    return parses[0][1]


# === Pre-modifier dem chains through adj-modifier ========================


class TestPreModDemAdjChain:
    """Phase 5e Commit 16 pre-modifier dems consume an N daughter.
    The Phase 5g modifier rule produces N from
    ``ADJ PART[LINK] N`` (recursive), so the pre-mod dem chains
    unchanged."""

    def test_prox_vowel_adj(self) -> None:
        # `itong` = `ito + -ng` (PROX-NOM dem + bound -ng linker).
        # `magandang bata` = vowel-final adj + bound -ng linker + N.
        # Composition: itong [magandang bata]
        f = _first_parse("Kumain itong magandang bata.")
        assert f is not None

    def test_med_consonant_adj(self) -> None:
        # `iyan na` = MED-NOM dem + standalone na linker.
        # `mabilis na bata` = consonant-final adj + standalone na linker + N.
        f = _first_parse("Kumain iyan na mabilis na bata.")
        assert f is not None

    def test_dist_consonant_adj(self) -> None:
        f = _first_parse("Kumain iyon na mabilis na bata.")
        assert f is not None

    def test_prox_obj_position(self) -> None:
        # `nitong` = niTo + -ng, GEN-PROX dem, -ng linker.
        # Need an explicit NOM SUBJ for the AV verb to bind;
        # otherwise the bare GEN-NP can't satisfy the SUBJ slot.
        f = _first_parse("Bumili ako nitong magandang bata.")
        assert f is not None

    def test_prox_dat_position(self) -> None:
        # `ditong` would be the DAT dem with bound -ng linker.
        f = _first_parse("Pumunta ako ditong magandang bahay.")
        assert f is not None


# === Pre-modifier dem with multi-modifier under it =======================


class TestPreModDemMultiModifier:
    """Multi-modifier composition under a pre-modifier dem
    (``itong mabilis na magandang bata`` "this quick beautiful
    child")."""

    def test_two_mod_under_prox(self) -> None:
        f = _first_parse("Kumain itong mabilis na magandang bata.")
        assert f is not None

    def test_two_mod_under_med(self) -> None:
        f = _first_parse("Kumain iyan na mabilis na magandang bata.")
        assert f is not None


# === Post-modifier dem on adj-modified head ===============================


class TestPostModDemOnAdjModifiedHead:
    """Phase 5d Commit 3 post-modifier dem rule wraps an inner NP
    with `linker + DEM-DET`. The inner NP can now have an
    adj-modified head (Phase 5g Commit 2)."""

    def test_pre_n_adj_under_post_mod_prox(self) -> None:
        # Inner: `ang [mabilis na bata]` (consonant-adj pre-N).
        # Outer: `[ang mabilis na bata] + ng + ito` — bata is
        # vowel-final at the right edge → bound -ng linker.
        f = _first_parse("Kumain ang mabilis na batang ito.")
        assert f is not None

    def test_post_n_vowel_adj_under_post_mod_prox(self) -> None:
        # Inner: `ang [batang maganda]` (vowel-adj post-N).
        # Outer linker on rightmost word `maganda` (vowel-final)
        # → bound -ng → `magandang ito`.
        f = _first_parse("Kumain ang batang magandang ito.")
        assert f is not None

    def test_post_n_consonant_adj_under_post_mod_prox(self) -> None:
        # Inner: `ang [batang mabait]` (consonant-final adj
        # post-N). Outer linker on rightmost word `mabait`
        # (consonant-final) → standalone na → `mabait na ito`.
        # This is the case the Commit 6 disambiguator extension
        # unblocks (ADJ + na + DEM-DET right context).
        f = _first_parse("Kumain ang batang mabait na ito.")
        assert f is not None


# === Disambiguator: ADJ + na + DEM-DET ===================================


class TestDisambiguatorAdjNaDem:
    """The Phase 5g Commit 6 disambiguator extension admits
    DEM-DET right-context as a linker target after ADJ + ``na``.
    Without this, the placement pass would hoist ``na`` to clause-
    end as the ALREADY clitic and the post-modifier-dem composition
    on a consonant-final adj would fail."""

    def test_adj_na_dem_det_picks_linker(self) -> None:
        toks = split_linker_ng(
            split_enclitics(tokenize("Kumain ang batang mabait na ito."))
        )
        ml = disambiguate_homophone_clitics(analyze_tokens(toks))
        # Find the `na` between `mabait` and `ito` and verify the
        # clitic reading was dropped.
        na_indices = [
            i for i, t in enumerate(toks) if t.surface.lower() == "na"
        ]
        # There may be more than one `na` in pathological inputs; the
        # one we care about is the last one (right before `ito`).
        last_na = na_indices[-1]
        kinds = {ma.feats.get("is_clitic") is True for ma in ml[last_na]}
        assert True not in kinds, (
            "ADJ + na + DEM-DET should select linker reading"
        )

    def test_adj_na_plain_det_keeps_both(self) -> None:
        # ``Maganda na ang bata.`` — ADJ + na + plain DET (DEM=NO).
        # The disambiguator falls through; placement treats ``na``
        # as ALREADY. Verified in Phase 5g Commit 5 tests; pin
        # again here as a no-regression for the Commit 6 extension.
        toks = split_linker_ng(
            split_enclitics(tokenize("Maganda na ang bata."))
        )
        ml = disambiguate_homophone_clitics(analyze_tokens(toks))
        na_idx = next(
            i for i, t in enumerate(toks) if t.surface.lower() == "na"
        )
        kinds = {ma.feats.get("is_clitic") is True for ma in ml[na_idx]}
        assert True in kinds, "ADJ + na + plain DET keeps clitic reading"


# === No regression: predicative-adj surfaces still work =================


class TestNoPredicativeRegression:
    """Phase 5g Commit 6 disambiguator extension only adds
    DEM-DET to the right-context whitelist; PRON / plain-DET
    contexts continue to keep both readings."""

    @pytest.mark.parametrize("text,expected_pred", [
        ("Maganda na ka.",            "ADJ <SUBJ>"),
        ("Maganda na ang bata.",      "ADJ <SUBJ>"),
        ("Matanda na siya.",          "ADJ <SUBJ>"),
        ("Hindi maganda ang bata.",   "ADJ <SUBJ>"),
    ])
    def test_predicative_adj_still_parses(
        self, text: str, expected_pred: str
    ) -> None:
        f = _first_parse(text)
        assert f is not None
        assert f.feats.get("PRED") == expected_pred


# === No regression: pre-modifier dem on bare N ===========================


class TestPreModDemBareNRegression:
    """Pre-modifier dem on a bare (unmodified) N continues to
    parse via Phase 5e Commit 16 unchanged. The Phase 5g changes
    don't disturb the existing behaviour."""

    @pytest.mark.parametrize("text", [
        "Kumain itong bata.",
        "Kumain iyan na bata.",
        "Kumain iyon na bata.",
    ])
    def test_pre_mod_dem_bare_n(self, text: str) -> None:
        f = _first_parse(text)
        assert f is not None
