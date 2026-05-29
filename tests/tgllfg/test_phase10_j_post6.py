# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-6: ay-fronted two-NP equational construction.

Adds the chart rule ``S → NP[CASE=NOM] PART[LINK=AY] NP[CASE=NOM]``
mirroring the Phase 8.Y/8.Z bare two-NP equational, but with the
fronted topic-NP binding to SUBJ + TOPIC (parallel to the ay-fronted
predicative-N rule of Phase 5n.B). Plus six lex additions surfaced
by the audit-corpus closure work:

- ``tradisyonal`` (ADJ, Spanish loan) — wave-2 rg-intermediate
- ``putahe``      (NOUN, Spanish loan) — wave-2 rg-intermediate
- ``luto``        (NOUN sense; verb sense pre-existed in verbs.yaml)
- ``alaga``       (NOUN) — unattributed-corpus pred-n/alaga-hayop-2item
- ``labrador``    (NOUN, English loan) — pred-n/aso-hayop-labrador
- ``espanyol``    (NOUN, Spanish loan) — pred-n/regalo-libro-3coord
"""

import pytest

from tgllfg.core.pipeline import parse_text


class TestEquationalAyFronted:
    """Phase 10.J.post-6 chart rule ``S → NP[CASE=NOM] PART[LINK=AY]
    NP[CASE=NOM]`` (ay-fronted two-NP equational).
    """

    @pytest.mark.parametrize(
        "text",
        [
            # PANAHON ANG PAMILYA sent-5 (was 9.B-pinned, now closed).
            "Ang pinakaubod ng pamilyang Pilipino ay ang ama, ina at "
            "mga anak.",
            # wave-2 rg-intermediate (closes with ``tradisyonal`` +
            # ``putahe`` lex additions).
            "Ang tradisyonal na putahe sa pista ay ang litson.",
            # ``luto`` NOUN sense — was VERB-only in verbs.yaml.
            "Ang gulay ay ang luto ng nanay.",
            # Canonical short forms (constructed; will land in
            # unattributed-constructions.jsonl).
            "Si Juan ay ang doktor.",
            "Ang doktor ay si Juan.",
        ],
    )
    def test_equational_ay_parses(self, text: str) -> None:
        parses = parse_text(text, n_best=2)
        assert len(parses) >= 1, f"equational ay-fronted ZPF: {text!r}"

    def test_equational_ay_fstructure_shape(self) -> None:
        """The matrix carries ``PRED='BE-NP <SUBJ>'``, ``SUBJ=↓1``,
        ``TOPIC=↓1``, ``PRED-NP=↓3``, ``PREDICATIVE=true``."""
        s = "Si Juan ay ang doktor."
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "BE-NP <SUBJ>"
        assert fs.feats.get("PREDICATIVE") is True
        # TOPIC and SUBJ both point to the fronted ``Si Juan``
        # — identity equation, not just structure equality.
        topic = fs.feats.get("TOPIC")
        subj = fs.feats.get("SUBJ")
        pred_np = fs.feats.get("PRED-NP")
        assert topic is not None and subj is not None
        assert pred_np is not None
        assert topic.id == subj.id
        # ↓3 (the predicate NP) is distinct.
        assert pred_np.id != subj.id

    def test_equational_ay_subj_lemma(self) -> None:
        """For ``Si Juan ay ang doktor.``, the SUBJ has LEMMA=juan
        (the fronted topic); the PRED-NP has LEMMA=doktor."""
        s = "Si Juan ay ang doktor."
        parses = parse_text(s, n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        subj = fs.feats["SUBJ"]
        assert subj.feats.get("LEMMA") == "juan"
        pred_np = fs.feats["PRED-NP"]
        assert pred_np.feats.get("LEMMA") == "doktor"


class TestEquationalAyRegressions:
    """Anti-regression: existing ay-fronting cases (predicative-V,
    predicative-N, ADJ-predicative, AdvP/PP, SubordClause) must
    continue to parse without the new rule producing spurious
    additional analyses.
    """

    @pytest.mark.parametrize(
        "text",
        [
            # Predicative-N (Phase 5n.B / 9.V.4 rules)
            "Si Juan ay guro.",
            "Si Juan ay bahagi ng pamilya.",
            # Predicative-V (existing pipeline NP+ay+S_GAP path)
            "Sila ay nagluto.",
            # AdvP-front (Phase 5e chart rule)
            "Kahapon ay umulan.",
            # PP-front (Phase 5e chart rule)
            "Sa bahay ay nagluto ang nanay.",
            # ADJ-predicative-front (existing path)
            "Si Juan ay maganda.",
        ],
    )
    def test_existing_ay_paths_still_work(self, text: str) -> None:
        parses = parse_text(text, n_best=2)
        assert len(parses) >= 1, f"regression on {text!r}"

    def test_no_spurious_equational_for_predicative_n(self) -> None:
        """``Si Juan ay guro.`` (predicative-N, ↓3 is bare ``N``)
        must NOT also get an equational reading — the equational
        rule's ↓3 is ``NP[CASE=NOM]``, and bare ``N`` does not match.
        Confirm parse count remains 1 (no doubling)."""
        parses = parse_text("Si Juan ay guro.", n_best=4)
        assert len(parses) == 1, (
            f"expected single parse (predicative-N), got {len(parses)}"
        )
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "BE-N <SUBJ>"


class TestNewLexEntries:
    """Phase 10.J.post-6 lex additions — sanity checks."""

    @pytest.mark.parametrize(
        "text,pos_check",
        [
            ("Maganda ang putahe.", "putahe-noun"),
            ("Si Juan ay tradisyonal.", "tradisyonal-adj"),
            ("Masarap ang luto ni nanay.", "luto-noun"),
            ("Maganda ang alaga ko.", "alaga-noun"),
            ("Si Juan ay si Bob.", "control-lex-untouched"),
        ],
    )
    def test_new_lex_parses(self, text: str, pos_check: str) -> None:
        parses = parse_text(text, n_best=2)
        assert len(parses) >= 1, (
            f"{pos_check}: {text!r} should parse with new lex"
        )
