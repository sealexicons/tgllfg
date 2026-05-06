"""Phase 5i Commit 4: adverbial wh fronting.

Roadmap §12.1 / plan-of-record §5.3, §6 Commit 4. New clause
rule in ``cfg/clause.py``:

    S → ADV[WH=YES] S

The wh-ADV (saan / kailan / bakit / paano / papaano) is sentence-
initial; the inner S is the residue verbal clause. The matrix
shares the inner S's f-structure (PRED, SUBJ, etc., all
percolate); the wh-ADV joins ADJUNCT and the matrix gets
Q_TYPE=WH + WH_LEMMA=<wh's lemma>.

Parallels Phase 5g Commit 5 manner-adverb (``S → ADJ PART[LINK]
S`` lifting the manner ADJ into the matrix's ADJ set) — same
pattern but with a wh-ADV directly (no linker daughter) and
with the matrix Q_TYPE flag set.

End-to-end target sentences:

    Saan ka pumunta?       "Where did you go?"     (LOCATION)
    Kailan ka kumain?      "When did you eat?"     (TIME)
    Bakit ka kumain?       "Why did you eat?"      (REASON)
    Paano ka kumain?       "How did you eat?"      (MANNER)
    Papaano ka kumain?     (MANNER, formal variant)

Closes the flip-risk introduced by Commit 1: ``Saan ka pumunta?``
parsed today by silently dropping ``saan`` (1 → 0 after Commit
1's lex add); this commit's rule restores 1 parse with the
proper wh-Q matrix.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


# === Each wh-ADV produces a wh-Q matrix ================================


WH_ADV_INVENTORY = [
    # (sentence, wh_lemma, adv_type)
    ("Saan ka pumunta?",   "saan",    "LOCATION"),
    ("Kailan ka kumain?",  "kailan",  "TIME"),
    ("Bakit ka kumain?",   "bakit",   "REASON"),
    ("Paano ka kumain?",   "paano",   "MANNER"),
    ("Papaano ka kumain?", "papaano", "MANNER"),
]


class TestAdverbialWhPredicative:
    """Sentence-initial wh-ADV with PRON-as-clitic SUBJ. The
    classical Tagalog wh-Q form."""

    @pytest.mark.parametrize("sentence,wh_lemma,_adv_type", WH_ADV_INVENTORY)
    def test_q_type_wh_on_matrix(
        self, sentence: str, wh_lemma: str, _adv_type: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"expected at least one parse for {sentence!r}; got 0"
        )
        # At least one parse should be the wh-fronting rule.
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1, (
            f"expected at least one wh-Q parse for {sentence!r}"
        )
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma

    @pytest.mark.parametrize("sentence,_wh_lemma,adv_type", WH_ADV_INVENTORY)
    def test_inner_verbal_pred_propagates(
        self, sentence: str, _wh_lemma: str, adv_type: str
    ) -> None:
        """The inner S's PRED (verbal) percolates to the matrix
        unchanged (`(↑) = ↓2` shares f-structure)."""
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        # PRED should be the verbal (EAT or PUNTA), not 'WH <SUBJ>'
        # (that's the cleft-style PRED from Commit 2).
        pred = fs.feats.get("PRED")
        assert pred is not None
        assert "<" in pred  # verbal-PRED template


# === Wh-ADV with NOM-NP subject ========================================


class TestAdverbialWhWithNomNp:
    """Wh-ADV with explicit NOM-NP SUBJ (instead of clitic PRON)."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Saan pumunta ang bata?",   "saan"),
        ("Kailan kumain ang bata?",  "kailan"),
        ("Bakit kumain ang bata?",   "bakit"),
        ("Paano kumain ang bata?",   "paano"),
    ])
    def test_with_nom_np_subj(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma


# === Wh-ADV in ADJUNCT set =============================================


class TestWhAdvInAdjunctSet:
    """The wh-ADV rides the matrix's ADJUNCT set as an f-structure
    member with WH=YES + ADV_TYPE."""

    def test_saan_in_adjunct_with_location(self) -> None:
        parses = parse_text("Saan ka pumunta?")
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None
        wh_adv_members = [
            m for m in adjunct
            if isinstance(m, FStructure)
            and m.feats.get("WH") == "YES"
            and m.feats.get("ADV_TYPE") == "LOCATION"
        ]
        assert len(wh_adv_members) >= 1, (
            f"expected one ADJUNCT member with WH=YES + "
            f"ADV_TYPE=LOCATION; got {fs.feats.get('ADJUNCT')}"
        )

    @pytest.mark.parametrize("sentence,adv_type", [
        ("Saan ka pumunta?",  "LOCATION"),
        ("Kailan ka kumain?", "TIME"),
        ("Bakit ka kumain?",  "REASON"),
        ("Paano ka kumain?",  "MANNER"),
    ])
    def test_adv_type_preserved_in_adjunct(
        self, sentence: str, adv_type: str
    ) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None
        assert any(
            isinstance(m, FStructure)
            and m.feats.get("ADV_TYPE") == adv_type
            for m in adjunct
        )


# === Wh-ADV with OBJ ===================================================


class TestWhAdvWithObj:
    """Wh-ADV at the front + transitive verb with explicit OBJ."""

    def test_bakit_ka_kumain_ng_kanin(self) -> None:
        parses = parse_text("Bakit ka kumain ng kanin?")
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == "bakit"
        # Should have OBJ (kanin)
        assert fs.feats.get("OBJ") is not None


# === Composition with negation =========================================


class TestAdverbialWhWithNegation:
    """``Bakit hindi ka kumain?`` "Why didn't you eat?" composes
    via wh-fronting wrapping a hindi-negated S. Multiple parses
    are expected (Phase 5e AdvP-fronting and Phase 5i wh-fronting
    both fire); at least one is the wh-fronting reading."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Bakit hindi ka kumain?",    "bakit"),
        ("Saan hindi ka pumunta?",    "saan"),
        ("Kailan hindi ka kumain?",   "kailan"),
    ])
    def test_negation_plus_wh_adv(
        self, sentence: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1, (
            f"expected at least one wh-fronting parse for {sentence!r}; "
            f"got {[p[1].feats for p in parses]}"
        )
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma
        assert fs.feats.get("POLARITY") == "NEG"


# === Earlier Phase 5i + earlier-phase baselines preserved ==============


class TestPhase5iEarlierCommitsPreserved:
    """Commits 1-3 work continues unchanged."""

    @pytest.mark.parametrize("sentence,q_type,wh_lemma", [
        # Commit 2 cleft-style
        ("Sino ang kumain?",     "WH",  "sino"),
        ("Ano ang kinain mo?",   "WH",  "ano"),
    ])
    def test_cleft_unchanged(
        self, sentence: str, q_type: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == q_type
        ]
        assert len(wh_parses) >= 1
        _, fs, _, _ = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma

    @pytest.mark.parametrize("sentence", [
        # Commit 3 in-situ
        "Kumain ka ng ano?",
        "Bumili ka ng ano?",
    ])
    def test_in_situ_unchanged(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


class TestEarlierPhaseBaselinePreserved:
    """Phase 5g / 5h baselines unchanged. Sanity check on a few
    high-frequency constructions."""

    @pytest.mark.parametrize("sentence", [
        "Maganda ang bata.",
        "Mas matalino siya.",
        "Pinakamaganda ang bahay.",
        "Kasingganda si Maria si Ana.",
        "Kumain ka ba ng kanin?",
        "Hindi maganda ang bata.",
    ])
    def test_baseline_no_phantom_wh(self, sentence: str) -> None:
        """The new wh-ADV rule must not give phantom Q_TYPE=WH to
        existing constructions."""
        parses = parse_text(sentence)
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "WH"
