# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.V: Cluster B closures — sentence-initial fronted topic +
COMMA/ay + main S construction class (per Phase 9.U Cluster B
recommendation).

Four NO-OOV audit hits in the 9-12 word bucket close here:

* **9.V.1** — sent-689 (S&O 1972 p.447):
  ``Kahapon ay sumulat ng liham kay Maria si Juan.``
  New rule: 4-element ``V[VOICE=AV] NP[GEN] NP[DAT] NP[NOM]`` —
  SUBJ-trailing AV-TR with DAT-adjunct.

* **9.V.2** — sent-661 (R&C 1990 Ch5 Transition Phrases):
  ``Bago ko malimutan, nakita mo ba si Jonathan sa miting?``
  Lex flag: ``AV_ABSOL: true`` on ``limot`` + new DV-NVOL
  absolutive rule + INTR-style lex synthesis for DV-NVOL+
  AV_ABSOL roots.

* **9.V.3** — sent-767 (S&O 1972 p.480):
  ``Kung dinadalaw ko siya, palagi akong nagdadala ng regalo.``
  New rules: ``S → ADV[FREQUENCY] NP[NOM] PART[LINK=NG] V[AV]
  (NP[GEN])?`` for sentence-initial FREQUENCY ADV + clitic-2P
  SUBJ-PRON + linker + V matrix (intrans + trans variants).

* **9.V.4** — sent-1 (R&C 1990 ANG PAMILYA):
  ``Una sa lahat, ang isang Pilipino ay bahagi ng kanyang pamilya.``
  Three new rules: (a) ay-fronted predicate-N + GEN-complement
  ``S → NP[NOM] PART[LINK=AY] N NP[GEN]``;  (b) multi-word
  phrasal discourse marker ``PART → NUM[ORDINAL=true]
  ADP[CASE=DAT, MARKER=SA] Q[QUANT=ALL]`` for ``Una sa lahat``;
  (c) comma-variant of the 5m C4 sentence-initial PART rule
  ``S → PART PUNCT[COMMA] S`` gated by
  ``DISCOURSE_POS=SENTENCE_INITIAL``.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _has_parse(text: str, n: int = 3) -> int:
    return len(parse_text(text, n_best=n))


# === 9.V.1 — VOS-order 3-arg AV (sent-689) ==========================


class TestPhase9v1VosAvTrWithDat:
    """``S → V[VOICE=AV] NP[GEN] NP[DAT] NP[NOM]`` — SUBJ-trailing
    4-element AV-TR rule (V + OBJ + DAT-adj + SUBJ)."""

    def test_audit_pin_sent_689_matrix(self) -> None:
        """The audit-pin matrix shape: V + GEN-OBJ + DAT-OBL +
        NOM-SUBJ (SUBJ trailing). Pre-9.V.1 this failed."""
        assert _has_parse(
            "Sumulat ng liham kay Maria si Juan."
        ) >= 1

    def test_audit_pin_sent_689_full(self) -> None:
        """The full 9.U sent-689 audit hit — ``Kahapon ay`` +
        the matrix above. The fronted-ADV ay-pattern was already
        in place; 9.V.1 closes the inner matrix shape."""
        assert _has_parse(
            "Kahapon ay sumulat ng liham kay Maria si Juan."
        ) >= 1

    def test_existing_vso_unchanged(self) -> None:
        """V S O sa (canonical VSO order) still parses — the new
        rule doesn't disturb the existing ordering."""
        assert _has_parse(
            "Sumulat si Juan ng liham kay Maria."
        ) >= 1

    def test_fstructure_shape(self) -> None:
        """SUBJ = Juan; OBJ = liham; Maria in ADJUNCT (oblique
        recipient)."""
        parses = parse_text(
            "Sumulat ng liham kay Maria si Juan.", n_best=2,
        )
        assert parses
        _ct, f, _astr, _diags = parses[0]
        subj = f.feats.get("SUBJ")
        assert subj is not None
        assert str(subj.feats.get("LEMMA")) == "juan"
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert str(obj.feats.get("LEMMA")) == "liham"


# === 9.V.2 — DV-NVOL absolutive (limot) =============================


class TestPhase9v2DvNvolAbsolutive:
    """Lex flag ``AV_ABSOL: true`` on ``limot`` + new DV-NVOL
    absolutive S-rule + DV-NVOL INTR synthesis path in
    ``core/lexicon.py``."""

    @pytest.mark.parametrize("text", [
        "Malimutan ko.",
        "Nalimutan ko.",
        "Malimutan ng lalaki.",
        "Nalimutan ng lalaki.",
    ])
    def test_dv_nvol_absolutive_parses(self, text: str) -> None:
        """Bare DV-NVOL form with GEN-PRON / GEN-NP — the
        experiencer is the sole argument (SUBJ in the absolutive
        reading)."""
        assert _has_parse(text) >= 1

    def test_audit_pin_sent_661_full(self) -> None:
        """The full 9.U sent-661 audit hit — fronted bago-S
        SubordClause with clitic-fronted experiencer + main S.
        Pre-9.V.2 the SubordClause body failed; the bago-builder
        couldn't form."""
        assert _has_parse(
            "Bago ko malimutan, nakita mo ba si Jonathan sa miting?"
        ) >= 1

    def test_existing_two_arg_unchanged(self) -> None:
        """2-arg form with overt OBJ still parses — the new
        INTR synthesis adds entries without removing the TR
        ones."""
        assert _has_parse("Malimutan ko ito.") >= 1
        assert _has_parse("Nalimutan ko ito.") >= 1


# === 9.V.3 — sentence-initial FREQUENCY ADV + clitic SUBJ (sent-767) ==


class TestPhase9v3FreqAdvCliticSubj:
    """New rules: ``S → ADV[ADV_TYPE=FREQUENCY] NP[CASE=NOM]
    PART[LINK=NG] V[VOICE=AV] (NP[CASE=GEN])?`` — sentence-initial
    FREQUENCY ADV + clitic-2P NOM-PRON SUBJ + linker + V (with
    optional GEN-OBJ)."""

    @pytest.mark.parametrize("text", [
        "Palagi akong umaalis.",
        "Madalas akong kumain.",
        "Lagi akong kumakain.",
    ])
    def test_intransitive_variant(self, text: str) -> None:
        """The 4-daughter intransitive variant."""
        assert _has_parse(text) >= 1

    @pytest.mark.parametrize("text", [
        "Palagi akong nagdadala ng regalo.",
        "Madalas akong kumakain ng kanin.",
    ])
    def test_transitive_variant(self, text: str) -> None:
        """The 5-daughter transitive variant with GEN-OBJ."""
        assert _has_parse(text) >= 1

    def test_audit_pin_sent_767_full(self) -> None:
        """The full 9.U sent-767 audit hit — kung-S +
        COMMA + the 9.V.3 matrix."""
        assert _has_parse(
            "Kung dinadalaw ko siya, "
            "palagi akong nagdadala ng regalo."
        ) >= 1


# === 9.V.4 — ay-fronted predicate-N with GEN-complement + sent-1 ====


class TestPhase9v4AyFrontedPredicateNGen:
    """New rule: ``S → NP[CASE=NOM] PART[LINK=AY] N NP[CASE=GEN]``
    — ay-fronted predicate-N with GEN-NP possessor / specifier."""

    @pytest.mark.parametrize("text", [
        "Si Juan ay bahagi ng pamilya.",
        "Ang lalaki ay bahagi ng pamilya.",
        "Ang isang lalaki ay bahagi ng pamilya.",
    ])
    def test_ay_fronted_predicate_n_with_gen(self, text: str) -> None:
        """``X ay PRED-N ng Y`` — ay-fronted predicate-N + GEN
        possessor of the predicate noun."""
        assert _has_parse(text) >= 1

    def test_existing_bare_predicate_n_unchanged(self) -> None:
        """The bare ``X ay PRED-N`` form (no GEN-complement)
        still parses."""
        assert _has_parse("Si Juan ay bahagi.") >= 1
        assert _has_parse("Siya ay bahagi.") >= 1

    def test_audit_pin_sent_1_matrix(self) -> None:
        """The matrix-only form of sent-1 — pre-9.V.4 this
        failed because the predicate-N + GEN ay-fronted rule
        wasn't there."""
        assert _has_parse(
            "Ang isang Pilipino ay bahagi ng kanyang pamilya."
        ) >= 1

    def test_fstructure_shape(self) -> None:
        """PRED='BE-N <SUBJ>', N_LEMMA='bahagi',
        PRED-NP-POSS=the GEN-NP."""
        parses = parse_text(
            "Si Juan ay bahagi ng pamilya.", n_best=2,
        )
        assert parses
        _ct, f, _astr, _diags = parses[0]
        assert f.feats.get("PRED") == "BE-N <SUBJ>"
        assert f.feats.get("N_LEMMA") == "bahagi"
        assert f.feats.get("PRED-NP-POSS") is not None


class TestPhase9v4UnaSaLahat:
    """Multi-word phrasal discourse marker ``Una sa lahat`` plus
    the comma-variant of the 5m C4 sentence-initial PART rule."""

    def test_audit_pin_sent_1_full(self) -> None:
        """The full 9.U sent-1 audit hit — ``Una sa lahat,``
        topic + matrix."""
        assert _has_parse(
            "Una sa lahat, ang isang Pilipino ay bahagi "
            "ng kanyang pamilya."
        ) >= 1

    def test_una_sa_lahat_with_simpler_matrix(self) -> None:
        """The 9.V.4a phrasal marker + 9.V.4b comma-S variant
        compose for any matrix S."""
        assert _has_parse(
            "Una sa lahat, kumain si Juan."
        ) >= 1
        assert _has_parse(
            "Una sa lahat, umalis siya."
        ) >= 1

    def test_existing_discourse_markers_now_admit_comma(self) -> None:
        """The 9.V.4b comma-variant of 5m C4 generalizes: existing
        single-word discourse-initial PARTs (samakatuwid / siguro /
        marahil) now also parse with comma."""
        assert _has_parse("Samakatuwid, kumain si Juan.") >= 1
        assert _has_parse("Siguro, kumain si Juan.") >= 1


# === Regressions =====================================================


class TestPhase9vRegressions:
    """The new rules don't break canonical AV-TR, AV-INTR,
    OV-IMPRF, BE-N, or DV-NVOL-with-OBJ parses."""

    @pytest.mark.parametrize("text", [
        # Canonical AV-TR (VSO)
        "Sumulat si Juan ng liham.",
        "Kumain si Juan ng tinapay.",
        # AV-INTR
        "Kumain si Juan.",
        # OV-IMPRF with OBJ
        "Kinain ko ang tinapay.",
        # DV-NVOL with overt OBJ (limot 2-arg)
        "Nalimutan ko ang aklat.",
        # Bare predicate-N
        "Bahagi siya.",
        "Doktor siya.",
        # 9.O AV-NVOL absolutive (Nakita ko)
        "Nakita ko.",
        # Existing sentence-initial discourse-PART (no comma)
        "Samakatuwid kumain si Juan.",
        "Siguro pumupunta siya.",
    ])
    def test_regression_holds(self, text: str) -> None:
        assert _has_parse(text) >= 1, f"regression on {text!r}"
