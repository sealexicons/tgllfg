"""Phase 5n.B Commit 3: ay-inversion of comparative ADJ (§18 L39).

Closes §18.1 deferral L39 (``Si Maria ay mas matalino kaysa kay
Juan.``) by adding a parallel gap non-terminal ``S_GAP_PREDADJ``
and an ay-fronting wrap rule

    S → NP[CASE=NOM] PART[LINK=AY] S_GAP_PREDADJ
        (↑) = ↓3
        (↑ TOPIC) = ↓1
        (↓3 REL-PRO) = ↓1
        (↓3 REL-PRO) =c (↓3 SUBJ)

in ``cfg/extraction.py``, parallel to the Phase 4 §7.4 V-pivot
ay-fronting wrap (which uses ``S_GAP``).

Three S_GAP_PREDADJ shapes cover the predicative-ADJ residue:

* Bare predicative-ADJ (``maganda`` / ``mas matalino`` /
  ``pinakamatalino`` / ``kasingganda``).
* Equative + GEN-standard (``kasingganda ni Ana``).
* Recursive negation (``hindi maganda``).

The kaysa-PP attachment (``mas matalino kaysa kay Juan``) is
handled by the existing Phase 5h Commit 4 kaysa wrap rule
composing on top of the bare ay-fronted predicative-ADJ S; no
new rule needed.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _ay_adj_parse(text: str) -> FStructure | None:
    """Find a parse with PRED='ADJ <SUBJ>' and a TOPIC."""
    parses = parse_text(text, n_best=10)
    for _ct, fs, _astr, _diags in parses:
        if (
            fs.feats.get("PRED") == "ADJ <SUBJ>"
            and fs.feats.get("TOPIC") is not None
        ):
            return fs
    return None


def _topic_lemma(fs: FStructure) -> str | None:
    topic = fs.feats.get("TOPIC")
    if isinstance(topic, FStructure):
        v = topic.feats.get("LEMMA")
        return v if isinstance(v, str) else None
    return None


# === Bare predicative-ADJ ay-fronted =================================


class TestBareAyFronted:
    """``Si Maria ay maganda.`` "Maria is beautiful." — bare
    predicative-ADJ ay-fronted."""

    @pytest.mark.parametrize("sentence,topic,adj_lemma", [
        ("Si Maria ay maganda.",   "maria", "ganda"),
        ("Si Juan ay matalino.",   "juan",  "talino"),
        ("Si Ana ay matanda.",     "ana",   "tanda"),
    ])
    def test_bare_ay_fronted(
        self, sentence: str, topic: str, adj_lemma: str
    ) -> None:
        fs = _ay_adj_parse(sentence)
        assert fs is not None, f"no ay-fronted-ADJ parse for {sentence!r}"
        assert _topic_lemma(fs) == topic
        assert fs.feats.get("ADJ_LEMMA") == adj_lemma
        assert fs.feats.get("PREDICATIVE") == "YES"


# === Comparative ADJ ay-fronted ======================================


class TestComparativeAyFronted:
    """``Si Maria ay mas matalino.`` and ``Si Maria ay mas matalino
    kaysa kay Juan.`` — mas-wrapped comparative ADJ ay-fronted.
    The kaysa-PP attaches via the existing Phase 5h Commit 4 wrap
    on top of the bare ay-fronted S."""

    def test_mas_matalino(self) -> None:
        fs = _ay_adj_parse("Si Maria ay mas matalino.")
        assert fs is not None
        assert _topic_lemma(fs) == "maria"
        assert fs.feats.get("ADJ_LEMMA") == "talino"

    def test_mas_matalino_kaysa(self) -> None:
        fs = _ay_adj_parse(
            "Si Maria ay mas matalino kaysa kay Juan."
        )
        assert fs is not None
        assert _topic_lemma(fs) == "maria"
        # kaysa-PP joins ADJUNCT with ROLE=STANDARD
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None
        standard = [
            m for m in adj if m.feats.get("ROLE") == "STANDARD"
        ]
        assert len(standard) == 1


# === Superlative ADJ ay-fronted ======================================


class TestSuperlativeAyFronted:
    """``Si Maria ay pinakamatalino.`` — paradigm-derived
    superlative ADJ ay-fronted."""

    def test_pinaka_ay_fronted(self) -> None:
        fs = _ay_adj_parse("Si Maria ay pinakamatalino.")
        assert fs is not None
        assert _topic_lemma(fs) == "maria"
        assert fs.feats.get("ADJ_LEMMA") == "talino"


# === Equative ADJ ay-fronted =========================================


class TestEquativeAyFronted:
    """``Si Maria ay kasingganda ni Ana.`` — equative ADJ +
    GEN-standard ay-fronted (uses S_GAP_PREDADJ equative variant)."""

    def test_kasingganda_with_gen_standard(self) -> None:
        fs = _ay_adj_parse("Si Maria ay kasingganda ni Ana.")
        assert fs is not None
        assert _topic_lemma(fs) == "maria"
        assert fs.feats.get("ADJ_LEMMA") == "ganda"
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None
        standard = [
            m for m in adj
            if m.feats.get("ROLE") == "EQUATIVE_STANDARD"
        ]
        assert len(standard) == 1

    def test_kasingganda_bare(self) -> None:
        # ``Si Maria ay kasingganda.`` — bare equative without a
        # standard NP. Fires the bare-ADJ S_GAP_PREDADJ shape.
        fs = _ay_adj_parse("Si Maria ay kasingganda.")
        assert fs is not None
        assert fs.feats.get("ADJ_LEMMA") == "ganda"


# === Negation under ay-fronted ADJ ===================================


class TestAyFrontedNegation:
    """``Si Maria ay hindi maganda.`` — recursive
    ``S_GAP_PREDADJ → PART[POLARITY=NEG] S_GAP_PREDADJ`` lifts
    POLARITY=NEG onto the ay-fronted predicative-ADJ matrix."""

    def test_hindi_maganda(self) -> None:
        fs = _ay_adj_parse("Si Maria ay hindi maganda.")
        assert fs is not None
        assert _topic_lemma(fs) == "maria"
        assert fs.feats.get("ADJ_LEMMA") == "ganda"
        assert fs.feats.get("POLARITY") == "NEG"


# === Disambiguation: V-pivot ay-fronting unaffected ==================


class TestVPivotAyFrontingUnaffected:
    """The existing Phase 4 §7.4 V-pivot ay-fronting (S_GAP)
    continues to fire on V-headed inner clauses; the new rule
    targets S_GAP_PREDADJ which is disjoint."""

    def test_v_pivot_ay_fronted(self) -> None:
        parses = parse_text("Si Maria ay kumain ng isda.")
        assert len(parses) >= 1
        v_parses = [
            p for p in parses
            if (p[1].feats.get("PRED") or "").startswith("EAT")
        ]
        assert len(v_parses) == 1


# === Regression: non-fronted predicative-ADJ unaffected ==============


class TestNonFrontedPredAdjUnaffected:
    """``Maganda si Maria.`` continues to parse via the Phase 5g
    Commit 3 predicative-ADJ rule without TOPIC."""

    def test_maganda_no_ay(self) -> None:
        parses = parse_text("Maganda si Maria.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "ADJ <SUBJ>"
        # No TOPIC on the non-ay-fronted form
        assert fs.feats.get("TOPIC") is None
