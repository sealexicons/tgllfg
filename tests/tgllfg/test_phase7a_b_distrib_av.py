# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 7a.B: magsi + magpa-an distributive AV affixes (§18.1.1 #2).

Two new affix classes in `data/tgl/paradigms.yaml`:

* `magsi` plural-actor AV prefix (S&O 1972 §5.15) — `nagsikanta`
  "sang (pl.)" etc. Emits DISTRIB=true.
* `magpa_an` reciprocal-distributive causative circumfix —
  `nagpatawagan` "called one another" etc. Emits DISTRIB=true,
  RECP=true, MOOD=SOC.

Per the Phase 7a.B Commit 1 design entry in
``docs/analysis-choices.md``: the locative-distributive subtype of
``magpa-…-an`` was investigated via GT (2026-05-14) and found NOT
productive in modern Tagalog (4 negative tests vs 1 positive
reciprocal-distributive). Phase 7a.B implements reciprocal-
distributive only.

Tests pin:

* Morphology: surfaces generate via `analyze_tokens()` with
  the expected lex-level feats.
* Clause parsing: clauses with the new verb forms parse via
  the existing AV (magsi) and AV-SOC (magpa_an) clause frames.
* Regression: the existing `mag`, `mag_an`, and `magpa` paradigms
  still produce their canonical surfaces (no double-firing).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph import analyze_tokens
from tgllfg.text import tokenize


def _verb_analyses(surface: str) -> list:
    """Return all VERB-pos analyses for a surface."""
    toks = tokenize(surface)
    return [a for a in analyze_tokens(toks)[0] if a.pos == "VERB"]


def _has_feat(analyses: list, lemma: str, **feats) -> bool:
    """True if any analysis has the given lemma and feat values."""
    for a in analyses:
        if a.lemma != lemma:
            continue
        if all(a.feats.get(k) == v for k, v in feats.items()):
            return True
    return False


# === magsi morphology (S&O §5.15) ====================================


class TestMagsiMorphology:
    """`magsi-` plural-actor AV prefix — three aspect cells (PFV/IPFV/
    CTPL) on -um- verbs. Emits DISTRIB=true."""

    @pytest.mark.parametrize(
        "surface,lemma,aspect",
        [
            ("nagsikanta", "kanta", "PFV"),
            ("nagsisikanta", "kanta", "IPFV"),
            ("magsisikanta", "kanta", "CTPL"),
            ("nagsikain", "kain", "PFV"),
            ("nagsisikain", "kain", "IPFV"),
            ("magsisikain", "kain", "CTPL"),
            ("nagsibasa", "basa", "PFV"),
            ("nagsisibasa", "basa", "IPFV"),
            ("nagsiinom", "inom", "PFV"),
            ("nagsisulat", "sulat", "PFV"),
        ],
    )
    def test_magsi_surface(
        self, surface: str, lemma: str, aspect: str
    ) -> None:
        analyses = _verb_analyses(surface)
        assert _has_feat(
            analyses,
            lemma,
            VOICE="AV",
            ASPECT=aspect,
            DISTRIB=True,
        ), f"{surface!r} should analyze as {lemma}/AV/{aspect}/DISTRIB"


# === magpa_an morphology =============================================


class TestMagpaAnMorphology:
    """`magpa-…-an` circumfix — three aspect cells (PFV/IPFV/CTPL).
    Emits MOOD=SOC, RECP=true, DISTRIB=true. Locative-distributive
    subtype dropped per GT evidence (see analysis-choices.md)."""

    @pytest.mark.parametrize(
        "surface,lemma,aspect",
        [
            ("nagpatawagan", "tawag", "PFV"),
            ("nagpapatawagan", "tawag", "IPFV"),
            ("magpapatawagan", "tawag", "CTPL"),
            ("nagpakainan", "kain", "PFV"),
            ("nagpapakainan", "kain", "IPFV"),
            ("magpapakainan", "kain", "CTPL"),
            ("nagpahiraman", "hiram", "PFV"),
            ("nagpapahiraman", "hiram", "IPFV"),
            ("magpapahiraman", "hiram", "CTPL"),
            ("nagpaupuhan", "upo", "PFV"),
            ("nagpapaupuhan", "upo", "IPFV"),
            ("magpapaupuhan", "upo", "CTPL"),
        ],
    )
    def test_magpa_an_surface(
        self, surface: str, lemma: str, aspect: str
    ) -> None:
        analyses = _verb_analyses(surface)
        assert _has_feat(
            analyses,
            lemma,
            VOICE="AV",
            ASPECT=aspect,
            MOOD="SOC",
            RECP=True,
            DISTRIB=True,
        ), (
            f"{surface!r} should analyze as "
            f"{lemma}/AV/{aspect}/SOC/RECP/DISTRIB"
        )


# === Clause-level parsing ============================================


class TestMagsiClause:
    """`magsi-` clauses parse via the existing AV-IND clause frames
    (the verb's MOOD=IND, so no special grammar needed)."""

    def test_nagsikanta_intrans(self) -> None:
        # `Nagsikanta ang mga bata.` "The children sang (pl.)."
        parses = parse_text("Nagsikanta ang mga bata.")
        assert parses, "magsi intransitive clause should parse"

    def test_nagsikain_trans(self) -> None:
        # `Nagsikain sila ng kanin.` "They ate rice (pl.)."
        parses = parse_text("Nagsikain sila ng kanin.")
        assert parses, "magsi transitive clause should parse"


class TestMagpaAnReciprocalClause:
    """`magpa-…-an` reciprocal-distributive clauses parse via the
    existing AV-SOC mag_an clause frame (MOOD=SOC, RECP=true).
    GT-confirmed productive readings."""

    def test_nagpatawagan_sila(self) -> None:
        # GT-confirmed: "They called each other."
        parses = parse_text("Nagpatawagan sila.")
        assert parses, "Nagpatawagan sila. should parse"
        fs = parses[0][1]
        assert fs.feats.get("MOOD") == "SOC"
        assert fs.feats.get("VOICE") == "AV"

    def test_nagpakainan_mga_bata(self) -> None:
        # `Nagpakainan ang mga bata.` "The children fed each other."
        parses = parse_text("Nagpakainan ang mga bata.")
        assert parses, "Nagpakainan ang mga bata. should parse"
        fs = parses[0][1]
        assert fs.feats.get("MOOD") == "SOC"

    def test_nagpahiraman_sila_aklat(self) -> None:
        # `Nagpahiraman sila ng aklat.` "They lent each other books."
        parses = parse_text("Nagpahiraman sila ng aklat.")
        assert parses, "Nagpahiraman sila ng aklat. should parse"
        fs = parses[0][1]
        assert fs.feats.get("MOOD") == "SOC"


# === Regression: existing paradigms unchanged ========================


class TestExistingParadigmsUnchanged:
    """Pre-Phase-7a.B paradigms still analyze their canonical
    surfaces. The new cells don't perturb the existing mag /
    mag_an / magpa paradigms."""

    def test_kumain_um_pfv(self) -> None:
        # Pre-existing -um- PFV.
        analyses = _verb_analyses("kumain")
        assert _has_feat(
            analyses, "kain", VOICE="AV", ASPECT="PFV"
        )

    def test_nagkainan_mag_an_pfv(self) -> None:
        # Pre-existing mag_an reciprocal PFV (Phase 5e Commit 12).
        analyses = _verb_analyses("nagkainan")
        assert _has_feat(
            analyses, "kain", MOOD="SOC", RECP=True
        )

    def test_nagpakain_magpa_pfv(self) -> None:
        # Pre-existing magpa biclausal causative PFV (Phase 4 §7.7).
        analyses = _verb_analyses("nagpakain")
        assert _has_feat(
            analyses, "kain", CAUS="INDIRECT"
        )

    def test_nagkainan_clause_still_parses(self) -> None:
        # Phase 5e mag_an clause unaffected.
        parses = parse_text("Nagkainan sila.")
        assert parses, "Phase 5e mag_an clause should still parse"
