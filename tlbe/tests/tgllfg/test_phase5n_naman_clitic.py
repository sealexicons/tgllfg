# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.A Commit 22 — free-standing naman 2P enclitic (§18 L88).

Closes the §18 L88 deferral. The Phase 5k Commit 7 ``naman`` lex
entry was non-clitic (consumed structurally by the ``kaya naman``
two-word coord rule). This commit adds a SECOND ``naman`` entry as
a 2P clitic with ADV=ALSO, parallel to ``din`` / ``rin``, enabling
free-standing forms like ``Kumain naman ako.`` "I ate too".

Surface examples:

    Kumain naman ako.    "I ate too."
    Kumain naman siya.   "He/she ate too."
    Pumunta naman ako.   "I went too."
    Pumunta naman siya.  "He/she went too."

The two ``naman`` entries are differentiated by ``is_clitic``:
* Non-clitic (Phase 5k): ADV=ALSO; consumed by the kaya-naman rule
  via structural context (sandwiched between Ss with leading kaya).
* Clitic (Phase 5n.A): ADV=ALSO + CLITIC_CLASS=2P; consumed by the
  generic 2P-clitic absorption rule
  (``S → S PART[CLITIC_CLASS=2P]``), reordered by ``reorder_clitics``
  to a verbal host's 2P slot.

Neither entry crossfires into the other's structural context: the
clitic entry's reorder pass moves it next to a verbal host
(incompatible with kaya-naman's between-Ss adjacency), while the
non-clitic entry has no CLITIC_CLASS so the absorption rule's =c
constraint rejects it.
"""

import pytest

from tgllfg.core.pipeline import parse_text


# === Free-standing naman with V-host ================================


class TestFreeStandingNamanWithVerb:
    """``Kumain naman ako.`` — free-standing naman as 2P enclitic
    after a verb host. ADV=ALSO surfaces on the absorbed PART in
    the matrix ADJ set."""

    @pytest.mark.parametrize("sentence", [
        "Kumain naman ako.",
        "Kumain naman siya.",
        "Pumunta naman ako.",
        "Pumunta naman siya.",
    ])
    def test_free_standing_naman_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJ")
        assert adj is not None
        adj_lemmas = {a.feats.get("LEMMA") for a in adj}
        assert "naman" in adj_lemmas

    def test_naman_carries_adv_also(self) -> None:
        parses = parse_text("Kumain naman ako.")
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJ")
        assert adj is not None
        naman_entries = [
            a for a in adj if a.feats.get("LEMMA") == "naman"
        ]
        assert len(naman_entries) == 1
        assert naman_entries[0].feats.get("ADV") == "ALSO"

    def test_no_kaya_naman_crossfire(self) -> None:
        """Free-standing naman shouldn't trigger the kaya-naman
        coord matrix (no leading kaya, no second S)."""
        parses = parse_text("Kumain naman ako.")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("COORD") != "SO"


# === Composition with other 2P clitics ==============================


class TestNamanCompositions:
    """naman composes with other 2P clitics in the standard
    Wackernagel cluster (e.g., naman + ako)."""

    def test_naman_with_clitic_pron_subject(self) -> None:
        """``Kumain naman ako.`` — both naman (PART) and ako
        (PRON) are 2P clitics in the same cluster."""
        parses = parse_text("Kumain naman ako.")
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        # ako is the SUBJ; naman lives in ADJ.
        adj = fs.feats.get("ADJ")
        assert adj is not None
        assert any(a.feats.get("LEMMA") == "naman" for a in adj)


# === kaya-naman regression (Phase 5k Commit 7) ======================


class TestKayaNamanRegression:
    """The Phase 5k Commit 7 ``kaya naman`` two-word coord rule
    continues to fire after the Commit 22 clitic-naman addition."""

    @pytest.mark.parametrize("sentence", [
        "Pumunta siya kaya naman kumain ako.",
        "Pumunta siya, kaya naman kumain ako.",
    ])
    def test_kaya_naman_still_parses(self, sentence: str) -> None:
        parses = parse_text(sentence)
        # Look for a parse with COORD=SO (the kaya-naman matrix).
        so_parses = [
            p for p in parses if p[1].feats.get("COORD") == "SO"
        ]
        assert len(so_parses) >= 1, (
            f"{sentence!r} no longer yields a COORD=SO parse — "
            "kaya-naman rule may be crossfired by the new clitic "
            "naman entry."
        )
        _ct, fs, _astr, _diags = so_parses[0]
        assert fs.feats.get("DISCOURSE_EMPH") is True
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2


# === din / rin baseline regression (existing 2P ALSO clitics) =======


class TestDinRinRegression:
    """``din`` / ``rin`` (existing 2P ALSO clitics) continue to
    fire after the parallel naman addition."""

    @pytest.mark.parametrize("sentence,particle", [
        ("Kumain din ako.",  "din"),
        ("Kumain rin siya.", "rin"),
    ])
    def test_din_rin_still_parse(
        self, sentence: str, particle: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJ")
        assert adj is not None
        assert any(a.feats.get("LEMMA") == particle for a in adj)
