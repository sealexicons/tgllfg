"""Phase 5i Commit 9: kanino / magkano / ilan-WH integration.

Roadmap §12.1 / plan-of-record §6 Commit 9. Three new clause-
level rules in ``cfg/clause.py``:

1. **Predicative-Q cleft** (``S → Q[WH=YES] NP[CASE=NOM]``) for
   amount / count wh-Qs::

       Magkano ang isda?     "How much is the fish?"
       Ilan ang aklat?       "How many books are there?"
       Alin ang aklat?       (Q reading; PRON reading via Commit 2)

   Sibling to Commit 2 PRON-cleft. The wh-Q is the matrix
   predicate; the headless-RC NP[CASE=NOM] is the SUBJ. PRED
   template ``WH <SUBJ>``, Q_TYPE=WH, WH_LEMMA from the Q's
   LEMMA.

2. **DAT-pivot cleft** (``S → PRON[WH=YES, CASE=DAT] NP[CASE=NOM]``)
   for ``kanino`` "whose / to whom"::

       Kanino ang aklat?     "Whose is the book?"

   Sibling to Commit 2 NOM-cleft, but with CASE=DAT
   discriminating against sino / ano / alin (NOM-marked).

3. **DAT-wh fronting** (``S → PRON[WH=YES, CASE=DAT] S``) — the
   wh-PRON adjoins to the matrix S as an ADJUNCT member,
   parallel to Commit 4 adverbial-wh fronting (``ADV[WH=YES]
   S``)::

       Kanino ka pumunta?    "To whom did you go?"

   Q_TYPE=WH lifted onto the matrix; the residue clause
   provides the verbal predicate.

Lex inventory (from Commit 1, no change here):

* ``kanino`` — PRON[WH=YES, CASE=DAT, HUMAN=True]
* ``magkano`` — Q[WH=YES, QUANT=HOW_MUCH, VAGUE=YES]
* ``ilan`` — both Q[QUANT=FEW, VAGUE=YES] (vague) and
  Q[WH=YES, QUANT=HOW_MANY, VAGUE=YES] (wh) — polysemy from
  Commit 1.
* ``alin`` — both PRON[WH=YES, CASE=NOM] and Q[WH=YES,
  VAGUE=YES] — polysemy from Commit 1.

**Out of scope this commit**:

* In-situ wh Q_TYPE matrix lift (the wh-PRON inside an OBJ /
  ADJUNCT NP doesn't surface Q_TYPE on the matrix). Consumers
  can detect Q-ness by traversing the f-structure; see plan
  §5.2.
* ``Sa kanino ang aklat?`` (explicit DAT marker `sa kanino`
  with cleft) — no rule yet for predicate-NP[CASE=DAT] in
  cleft position. Defer.
* Non-wh predicative-Q (``Marami ang aklat.``
  "Many are the books") — Phase 5f deferral, separate work.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Predicative-Q cleft for magkano (amount-wh) ======================


class TestMagkanoPredicativeCleft:
    """``Magkano ang X?`` "How much is X?" — Q-headed cleft."""

    @pytest.mark.parametrize("sentence", [
        "Magkano ang isda?",
        "Magkano ang aklat?",
        "Magkano ang kotse?",
    ])
    def test_magkano_cleft(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("Q_TYPE") == "WH"
        assert fs.feats.get("WH_LEMMA") == "magkano"

    def test_magkano_with_demonstrative(self) -> None:
        # Demonstrative SUBJ: ``Magkano ito?`` "How much is this?"
        parses = parse_text("Magkano ito?")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("Q_TYPE") == "WH"
        assert fs.feats.get("WH_LEMMA") == "magkano"


# === Predicative-Q cleft for ilan-WH (count-wh) =======================


class TestIlanWhPredicativeCleft:
    """``Ilan ang X?`` "How many X?" — uses the WH polysemy of
    ``ilan`` (Commit 1: WH variant has QUANT=HOW_MANY)."""

    @pytest.mark.parametrize("sentence", [
        "Ilan ang aklat?",
        "Ilan ang bata?",
        "Ilan ang kabayo?",
    ])
    def test_ilan_wh_cleft(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("Q_TYPE") == "WH"
        assert fs.feats.get("WH_LEMMA") == "ilan"


# === DAT-pivot cleft for kanino =======================================


class TestKaninoDatPivotCleft:
    """``Kanino ang X?`` "Whose is X?" — DAT-PRON pivot cleft."""

    @pytest.mark.parametrize("sentence", [
        "Kanino ang aklat?",
        "Kanino ang aso?",
        "Kanino ang bahay?",
    ])
    def test_kanino_cleft(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("PRED") == "WH <SUBJ>"
        assert fs.feats.get("WH_LEMMA") == "kanino"


# === DAT-wh fronting (kanino over a residue S) ========================


class TestKaninoFronting:
    """``Kanino ka pumunta?`` — kanino fronted over the residue
    verbal clause; ADJUNCT lift + matrix Q_TYPE=WH."""

    def test_kanino_fronting_basic(self) -> None:
        parses = parse_text("Kanino ka pumunta?")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        # Verbal PRED on inner clause percolates.
        assert (fs.feats.get("PRED") or "").startswith("PUNTA")
        assert fs.feats.get("Q_TYPE") == "WH"
        assert fs.feats.get("WH_LEMMA") == "kanino"
        # kanino is in the ADJUNCT set.
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None
        kanino_in_adj = any(
            (m.feats.get("LEMMA") == "kanino"
             and m.feats.get("WH") == "YES")
            for m in adj
        )
        assert kanino_in_adj

    def test_kanino_fronting_with_obj(self) -> None:
        # Verbal clause with full GEN-obj: kanino fronted.
        parses = parse_text("Kanino ka bumili ng aklat?")
        assert len(parses) >= 1
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == "kanino"


# === In-situ kanino — f-structure has WH=YES inside ADJUNCT ===========


class TestKaninoInSitu:
    """``Pumunta ka kanino?`` — kanino in-situ (DAT-NP fills the
    DAT-ADJUNCT slot). The matrix doesn't carry Q_TYPE=WH (no
    matrix lift), but the wh-PRON is inspectable inside the
    ADJUNCT set."""

    def test_kanino_in_situ_in_adjunct(self) -> None:
        parses = parse_text("Pumunta ka kanino?")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        # No matrix Q_TYPE for in-situ (matrix lift deferred).
        # Either None or WH is acceptable; testing the wh-PRON
        # is detectable inside the ADJUNCT.
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None
        kanino_in_adj = any(
            (m.feats.get("LEMMA") == "kanino"
             and m.feats.get("WH") == "YES")
            for m in adj
        )
        assert kanino_in_adj


# === alin polysemy preserved (PRON + Q both fire) =====================


class TestAlinPolysemy:
    """``Alin ang aklat?`` admits two parses post-Commit-9:
    one via Commit 2 PRON-cleft, one via Commit 9 Q-cleft. Both
    produce the same f-structure (PRED='WH <SUBJ>',
    WH_LEMMA='alin'), so the redundancy is harmless. This test
    documents the polysemy as expected behaviour."""

    def test_alin_two_parses(self) -> None:
        parses = parse_text("Alin ang aklat?")
        assert len(parses) >= 1
        # All parses should agree on Q_TYPE + WH_LEMMA.
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") == "WH"
            assert fs.feats.get("WH_LEMMA") == "alin"


# === ilan polysemy: vague vs WH disambiguates by context ==============


class TestIlanPolysemy:
    """``Ilan`` has two readings: vague (Q[QUANT=FEW, VAGUE=YES])
    pre-existing from Phase 5f, and WH (Q[WH=YES, QUANT=HOW_MANY])
    added in Commit 1. The Q-cleft only matches the WH reading;
    the vague reading continues to fire only as an NP-modifier
    (e.g., ``ilang aklat`` after split_linker_ng splits the
    bound -ng linker)."""

    def test_ilan_pre_n_uses_wh_reading(self) -> None:
        # ``Ilang aklat ang kinain mo?`` "How many books did you eat?"
        # The split_linker_ng splits ``ilang`` → ``ilan`` + ``-ng``;
        # the wh-Q + N companion (Commit 6) lifts WH onto the N;
        # the wh-N-cleft fires.
        parses = parse_text("Ilang aklat ang kinain mo?")
        assert len(parses) >= 1
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "WH"
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == "ilan"


# === Q-cleft with vague-Q (no WH) does NOT fire =======================


class TestQCleftDoesNotMatchVagueQ:
    """The Q-cleft constrains on ``Q[WH=YES]`` (with =c
    constraint). Non-wh vague Qs (marami / kaunti / tatlo cardinal)
    do NOT fire the cleft. Phase 5f's predicative-cardinal rule
    handles ``Tatlo ang aklat.`` via a different path; the
    new Q-cleft must not interfere with it."""

    def test_marami_does_not_fire_q_cleft(self) -> None:
        # ``Marami ang aklat.`` — vague-Q reading. Non-wh; the
        # new Q-cleft must not write Q_TYPE=WH. Currently this
        # produces 0 parses (no rule for non-wh predicative
        # vague-Q exists; Phase 5f deferral). The acceptance
        # criterion: NO parse with Q_TYPE=WH.
        parses = parse_text("Marami ang aklat.")
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "WH"

    def test_tatlo_predicative_unchanged(self) -> None:
        # ``Tatlo ang aklat.`` — Phase 5f Commit 4 predicative
        # cardinal. Should continue to parse with PRED='THREE
        # <SUBJ>' (or equivalent), no Q_TYPE=WH leak.
        parses = parse_text("Tatlo ang aklat.")
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "WH"


# === Earlier Phase 5i constructions preserved =========================


class TestPhase5iEarlierCommitsPreserved:
    """The new cleft / fronting rules must not perturb Commits
    1-8."""

    @pytest.mark.parametrize("sentence,q_type,wh_lemma", [
        ("Sino ang kumain?",                "WH",     "sino"),
        ("Ano ang kinain mo?",              "WH",     "ano"),
        ("Saan ka pumunta?",                "WH",     "saan"),
        ("Bakit ka kumain?",                "WH",     "bakit"),
        ("Aling bata ang kumain?",          "WH",     "alin"),
    ])
    def test_wh_q_preserved(
        self, sentence: str, q_type: str, wh_lemma: str
    ) -> None:
        parses = parse_text(sentence)
        wh_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == q_type
        ]
        assert len(wh_parses) >= 1
        _ct, fs, _astr, _diags = wh_parses[0]
        assert fs.feats.get("WH_LEMMA") == wh_lemma

    def test_yes_no_q_preserved(self) -> None:
        parses = parse_text("Kumain ka ba ng kanin?")
        yn_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "YES_NO"
        ]
        assert len(yn_parses) >= 1

    def test_tag_q_preserved(self) -> None:
        parses = parse_text("Maganda ang bata, di ba?")
        tag_parses = [
            p for p in parses if p[1].feats.get("Q_TYPE") == "TAG"
        ]
        assert len(tag_parses) >= 1

    def test_indirect_q_preserved(self) -> None:
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) == 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("PRED") == "KNOW <SUBJ, COMP>"


class TestEarlierPhaseBaselinePreserved:
    """Phase 4 / 5c / 5h declaratives unchanged — no phantom
    Q_TYPE=WH on non-Q sentences."""

    @pytest.mark.parametrize("sentence", [
        "Maganda ang bata.",
        "Kumain ang aso ng isda.",
        "Hindi maganda ang bata.",
        "Mas matalino siya.",
        "Pinakamaganda ang bahay.",
        "Tatlo ang aklat.",
    ])
    def test_no_phantom_wh(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("Q_TYPE") != "WH"
