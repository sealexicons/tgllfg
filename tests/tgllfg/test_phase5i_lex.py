"""Phase 5i Commit 1: wh-word lex inventory.

Roadmap §12.1 / plan-of-record §4.1-4.4. Eleven new lex entries
spanning four sub-clusters:

* Pronominal wh (``data/tgl/pronouns.yaml``): ``sino`` /
  ``ano`` / ``kanino`` / ``alin`` — PRON[WH=YES] with case
  feats. Ride the existing Phase 4 NP-from-PRON shells unchanged.
* Adverbial wh (``data/tgl/particles.yaml``): ``saan`` / ``kailan``
  / ``bakit`` / ``paano`` / ``papaano`` — ADV[WH=YES] with per-wh
  ADV_TYPE classification (LOCATION / TIME / REASON / MANNER).
* Quantitative + selectional wh (``particles.yaml``): ``magkano``
  / ``aling`` / ``alin`` (polysemy with PRON entry) / ``ilan``
  (polysemy with the Phase 5f Commit 15 vague-Q reading) —
  Q[WH=YES, VAGUE=YES] heads.
* Complementizer + tag (``particles.yaml``): ``kung``
  PART[COMP_TYPE=INTERROG] for indirect questions; ``di``
  PART[NEG_TAG=YES] for ``di ba?`` tag-Q.

This commit is lex-only — no grammar / analyzer code changes.
The Phase 5i wh-fronting rules (Commit 2) and adverbial-wh
fronting rules (Commit 4) constrain on ``WH=YES`` to fire on
these surfaces.

Pre-state (verified 2026-05-06): all eleven new surfaces were
``_UNK`` (except ``ilan`` which had its non-WH Q reading from
Phase 5f Commit 15). The parser's ``_strip_non_content``
silently dropped them, producing bogus parses for some wh-
fronted sentences (e.g., ``Saan ka pumunta?`` parsed by
silently dropping ``saan``). Once these entries land, the strip
stops firing.

**Critical confirmed flip-risk**: ``Saan ka pumunta?`` parses
1→0 after this commit (the silent-drop residue ``Pumunta ka.``
no longer fires because ``saan`` is now a known PART). Audit
confirmed: zero baseline corpus entries contain any wh-word, so
no baseline flips. Commit 4's adverbial-wh fronting rule will
restore the parse path.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


# === Pronominal wh =====================================================


PRONOMINAL_WH = [
    # (surface, case, human, lemma)
    ("sino",    "NOM", True,  "sino"),
    ("ano",     "NOM", False, "ano"),
    ("kanino",  "DAT", True,  "kanino"),
]


class TestPronominalWh:
    """Each pronominal wh-word indexes as PRON with WH=YES + the
    right case / HUMAN feats."""

    @pytest.mark.parametrize("surface,case,human,lemma", PRONOMINAL_WH)
    def test_indexed_as_pron(
        self, surface: str, case: str, human: bool, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        prons = [a for a in out if a.pos == "PRON"]
        assert len(prons) == 1, (
            f"expected exactly one PRON analysis for {surface!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    @pytest.mark.parametrize("surface,case,human,lemma", PRONOMINAL_WH)
    def test_carries_wh_and_case(
        self, surface: str, case: str, human: bool, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        pron = next(
            a for a in analyzer.analyze_one(_tok(surface)) if a.pos == "PRON"
        )
        assert pron.feats.get("WH") == "YES"
        assert pron.feats.get("CASE") == case
        assert pron.feats.get("LEMMA") == lemma
        if human:
            assert pron.feats.get("HUMAN") is True
        else:
            assert pron.feats.get("HUMAN") is None


# === Adverbial wh =====================================================


ADVERBIAL_WH = [
    # (surface, adv_type, lemma)
    ("saan",    "LOCATION", "saan"),
    ("kailan",  "TIME",     "kailan"),
    ("bakit",   "REASON",   "bakit"),
    ("paano",   "MANNER",   "paano"),
    ("papaano", "MANNER",   "papaano"),
]


class TestAdverbialWh:
    """Each adverbial wh-word indexes as ADV with WH=YES + the right
    ADV_TYPE classification."""

    @pytest.mark.parametrize("surface,adv_type,lemma", ADVERBIAL_WH)
    def test_indexed_as_adv(
        self, surface: str, adv_type: str, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        advs = [a for a in out if a.pos == "ADV"]
        assert len(advs) == 1, (
            f"expected exactly one ADV analysis for {surface!r}; "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )

    @pytest.mark.parametrize("surface,adv_type,lemma", ADVERBIAL_WH)
    def test_carries_wh_and_adv_type(
        self, surface: str, adv_type: str, lemma: str
    ) -> None:
        analyzer = Analyzer.from_default()
        adv = next(
            a for a in analyzer.analyze_one(_tok(surface)) if a.pos == "ADV"
        )
        assert adv.feats.get("WH") == "YES"
        assert adv.feats.get("ADV_TYPE") == adv_type
        assert adv.feats.get("LEMMA") == lemma


# === Quantitative + selectional wh ====================================


class TestQuantitativeWh:
    """`magkano` is a Q-WH for amount-questions; ``aling`` is the
    pre-N selector with bound -ng linker; ``alin`` and ``ilan`` are
    polysemous between WH and non-WH Q readings."""

    def test_magkano(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("magkano"))
        qs = [a for a in out if a.pos == "Q"]
        assert len(qs) == 1
        q = qs[0]
        assert q.feats.get("WH") == "YES"
        assert q.feats.get("QUANT") == "HOW_MUCH"
        assert q.feats.get("VAGUE") == "YES"

    def test_aling_pre_n_selector_via_split(self) -> None:
        """``aling`` is the bound-``-ng`` form for pre-N use. Phase
        5i Commit 6 dropped the standalone ``aling`` lex entry so
        ``split_linker_ng`` splits it into ``alin`` (Q-WH) + ``-ng``
        (PART[LINK=NG]). This is a smoke check for the split.
        ``aling`` standalone (no split) returns _UNK; the split is
        enacted at the pre-parse stage."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("aling"))
        # Without the pre-parse split, aling is _UNK now.
        # The split happens in split_linker_ng before analysis.
        assert all(a.pos == "_UNK" for a in out), (
            f"expected aling as bare token to be _UNK after Phase 5i "
            f"Commit 6 (split_linker_ng splits to alin + -ng); "
            f"got {[(a.pos, a.lemma, dict(a.feats)) for a in out]}"
        )


class TestAlinPolysemy:
    """``alin`` has two readings: PRON[WH=YES, CASE=NOM] (standalone
    "which one") and Q[WH=YES, VAGUE=YES] (selectional, polysemy
    partner with the PRON entry). Both indexed by the analyzer; rule
    context disambiguates."""

    def test_alin_two_readings(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("alin"))
        by_pos = {a.pos: a for a in out}
        assert "PRON" in by_pos, (
            f"expected PRON reading; got {[a.pos for a in out]}"
        )
        assert "Q" in by_pos, (
            f"expected Q reading; got {[a.pos for a in out]}"
        )
        # PRON: standalone NOM wh
        pron = by_pos["PRON"]
        assert pron.feats.get("WH") == "YES"
        assert pron.feats.get("CASE") == "NOM"
        assert pron.lemma == "alin"
        # Q: selectional pre-N
        q = by_pos["Q"]
        assert q.feats.get("WH") == "YES"
        assert q.feats.get("VAGUE") == "YES"
        assert q.lemma == "alin"


class TestIlanPolysemy:
    """``ilan`` has two readings: the Phase 5f Commit 15 vague-Q
    (``Q[QUANT=FEW, VAGUE=YES]``) for "a few" / "some" usage, and
    the new Phase 5i wh-Q (``Q[WH=YES, QUANT=HOW_MANY, VAGUE=YES]``)
    for count-question usage. Same surface, different feats; rule
    context disambiguates between ``ilan ng aklat`` (vague — "a few
    books") and ``Ilan ang aklat?`` (wh — "how many books?")."""

    def test_ilan_two_q_readings(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("ilan"))
        qs = [a for a in out if a.pos == "Q"]
        assert len(qs) == 2, (
            f"expected exactly two Q readings for 'ilan'; "
            f"got {[(a.pos, dict(a.feats)) for a in qs]}"
        )
        # Identify by feats
        wh = next(q for q in qs if q.feats.get("WH") == "YES")
        non_wh = next(q for q in qs if q.feats.get("WH") != "YES")
        assert wh.feats.get("QUANT") == "HOW_MANY"
        assert wh.feats.get("VAGUE") == "YES"
        assert non_wh.feats.get("QUANT") == "FEW"
        assert non_wh.feats.get("VAGUE") == "YES"


# === Complementizer + tag particle ====================================


class TestComplementizerKung:
    """``kung`` is the indirect-question complementizer. Phase 5i
    Commit 8 builds the ``XCOMP → PART[COMP_TYPE=INTERROG] S[Q_TYPE=WH]``
    rule that consumes it."""

    def test_kung_indexed_as_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("kung"))
        parts = [a for a in out if a.pos == "PART"]
        assert len(parts) == 1
        part = parts[0]
        assert part.feats.get("COMP_TYPE") == "INTERROG"
        assert part.lemma == "kung"


class TestTagParticleDi:
    """``di`` is the colloquial shortening of ``hindi`` used in the
    sentence-final ``di ba?`` tag-Q construction. Phase 5i Commit 7
    builds the tag-Q rule that combines ``di + ba``."""

    def test_di_indexed_as_part(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("di"))
        parts = [a for a in out if a.pos == "PART"]
        assert len(parts) == 1
        part = parts[0]
        assert part.feats.get("NEG_TAG") == "YES"
        assert part.lemma == "di"


# === No collisions with existing lex ==================================


class TestNoCollisions:
    """The new wh-word entries must not perturb existing pronouns or
    particles. Sanity check on a few high-frequency lex items."""

    @pytest.mark.parametrize("surface,expected_pos", [
        ("ang",  "DET"),
        ("siya", "PRON"),
        ("ako",  "PRON"),
        ("ka",   "PRON"),
        ("ba",   "PART"),
        ("hindi", "PART"),
        # Phase 5h baselines
        ("mas",  "PART"),
        ("kaysa", "PART"),
        # Phase 5g baseline
        ("maganda", "ADJ"),
        # Phase 5f baseline
        ("marami", "Q"),
    ])
    def test_existing_lex_unchanged(
        self, surface: str, expected_pos: str
    ) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok(surface))
        positions = [a.pos for a in out]
        assert expected_pos in positions, (
            f"expected {expected_pos!r} POS for {surface!r}; "
            f"got {positions}"
        )


# === Strict: o (Phase 5k dependency) is still _UNK ====================


class TestOStillUnk:
    """The alternative-Q coordinator ``o`` "or" depends on Phase 5k
    coordination work. Phase 5i lex commit does NOT add ``o``;
    confirm it remains _UNK."""

    def test_o_remains_unk(self) -> None:
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("o"))
        assert all(a.pos == "_UNK" for a in out), (
            f"unexpected non-_UNK analysis for 'o'; "
            f"got {[(a.pos, a.lemma) for a in out]}"
        )
