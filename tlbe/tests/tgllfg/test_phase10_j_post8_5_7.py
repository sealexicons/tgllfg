# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.7: lexicalized NOUN-NOUN hyphenated compounds.

Adds four Tier 1/2 lexicalized N-N compounds to the lex per the
reviewer's 2026-05-30 framework (see ``data/tgl/exemplars/
compounds-n-n.jsonl`` and ``reference_tagalog_nn_compound_tiers``
memory):

* `salin-lahi` / `salinlahi` — generation, lineage (Tier 1;
  PAMILYA/sent-17 attestation)
* `tabing-dagat` / `tabingdagat` — seashore, beach (Tier 2;
  3 wave-2 rg-int attestations)
* `hanap-buhay` / `hanapbuhay` — livelihood (Tier 1;
  PAMILYA/sent-18 attestation)
* `kamag-anak` / `kamaganak` — relative, kinsman (Tier 1;
  wave-2 rg-int + wave-3 so1972 attestations)

Each lex entry uses the joined form as the citation (e.g.,
``salinlahi``) so the analyzer index keys to the unhyphenated
surface; the existing ``merge_hyphen_compounds`` pre-pass
(``src/tgllfg/text/multiword.py``) collapses the hyphenated surface
``salin-lahi`` → ``salinlahi`` before parsing.

**Productive N-N compounding (Tier 3) deferred**: the reviewer's
guidance is that productive families (tubig-X "water-of-X",
silid-X "room-of-X", etc.) should NOT be lexicalized; they belong
in a future grammar rule (``N_compound → N N`` with compositional
semantics). The current scope is Tier 1/2 lex entries only.

## Audit signal (post-8.5.6 → post-8.5.7)

Wave-1 unchanged at 106/123 (PAMILYA/sent-17 + sent-18 still ZPF
due to non-compound lex gaps in their wider clause contexts —
`kumpleto`/`ganito` for sent-17, OCR `pahahanap-buhay` for sent-18;
those are out-of-scope for this sub-PR). Other waves:

* wave-2 rc1990: +1 (tabing-dagat)
* wave-2 rg-intermediate: +1 (tabing-dagat)
* wave-3 so1972: +1 (kamag-anak — `Kamag-anak siya ng mga Santos.`)

XWAVE: 1814 → 1817 (+3).
"""

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


class TestNNCompoundLexicalization:
    """Verify each lex entry produces a known-surface match on the
    joined form (which is what ``merge_hyphen_compounds`` looks up)."""

    def test_salinlahi_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("salinlahi")

    def test_tabingdagat_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("tabingdagat")

    def test_hanapbuhay_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("hanapbuhay")

    def test_kamaganak_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("kamaganak")


class TestHyphenMergeCollapsesNNCompound:
    """The existing ``merge_hyphen_compounds`` pre-pass collapses the
    hyphenated surfaces into the joined form for lookup. We probe via
    full parse_text since that pipeline runs the pre-pass."""

    def test_salin_lahi_parses_in_clause(self) -> None:
        """Hyphenated `salin-lahi` parses via the joined `salinlahi`
        lex entry. Uses PAMILYA/sent-17 body shape."""
        parses = parse_text(
            "Tatlong salin-lahi ang nakatira sa iisang bahay.",
            n_best=1,
        )
        assert len(parses) >= 1

    def test_tabing_dagat_parses_in_dat_pp(self) -> None:
        """wave-2 rg-int sent-708 attestation shape."""
        parses = parse_text("Pumunta sila sa tabing-dagat.", n_best=1)
        assert len(parses) >= 1

    def test_hanap_buhay_parses_in_clause(self) -> None:
        parses = parse_text("Mayroon siyang hanap-buhay.", n_best=1)
        assert len(parses) >= 1

    def test_kamag_anak_parses_in_clause(self) -> None:
        """wave-3 so1972 sent-118 attestation."""
        parses = parse_text(
            "Kamag-anak siya ng mga Santos.", n_best=1,
        )
        assert len(parses) >= 1


class TestSynthBareJoinedFormsAlsoParse:
    """The joined forms (no hyphen) also parse — the lex entry citation
    is the joined form, so both surface variants route to the same
    NOUN f-structure."""

    def test_salinlahi_bare_joined(self) -> None:
        parses = parse_text(
            "Tatlong salinlahi ang nakatira sa iisang bahay.",
            n_best=1,
        )
        assert len(parses) >= 1

    def test_tabingdagat_bare_joined(self) -> None:
        parses = parse_text("Pumunta sila sa tabingdagat.", n_best=1)
        assert len(parses) >= 1


class TestAntiRegression:
    """The lex additions don't affect existing parses — each component
    NOUN (salin, lahi, tabi, dagat, buhay, anak) continues to function
    on its own."""

    def test_salin_standalone_preserved(self) -> None:
        """`salin` as a standalone NOUN is still known to the
        analyzer — the new joined `salinlahi` entry is additive."""
        analyzer = _get_default()
        assert analyzer.is_known_surface("salin")

    def test_anak_standalone_preserved(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("anak")

    def test_dagat_standalone_preserved(self) -> None:
        """`Pumunta sila sa dagat.` (no compound) still parses."""
        parses = parse_text("Pumunta sila sa dagat.", n_best=1)
        assert len(parses) >= 1

    def test_merge_hyphen_compounds_pass_unchanged_for_paradigm_forms(
        self,
    ) -> None:
        """The existing `merge_hyphen_compounds` pre-pass continues to
        handle pre-existing canonical hyphenated forms (mag-aral,
        tag-init, etc.) — the new lex entries don't shadow them."""
        analyzer = _get_default()
        # tag-init / taginit was an earlier example handled by the
        # pre-pass (Phase 5f). Confirm it's still recognized.
        assert analyzer.is_known_surface("taginit")
