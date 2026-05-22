# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 22: wh-as-indefinites + Walang ano man
(§18 L46 + L102).

Closes §18.1 deferrals L46 (wh-as-indefinites general) and L102
(``Walang ano man.``). Target sentences:

    Walang anuman.        "There is nothing." (lexicalized)
    Walang ano man.       "There is nothing." (productive form)
    Walang sino man.      (productive negative-indef of ``sinuman``)
    Walang anumang dumating.   "Nothing came." (lex + RC)
    Walang ano mang dumating.  "Nothing came." (productive + RC)

Three changes:

* ``data/tgl/pronouns.yaml``: add ``anuman`` PRON entry parallel
  to the existing ``sinuman`` entry, with
  ``INDEF=NEG_INDEF, PRED=SOMETHING_NEG_INDEF``. Composes
  immediately with the Phase 5m C9 negative-existential rule
  (``Walang anuman.``) and the Phase 5n.B C21 PRON-headed RC
  (``Walang anumang dumating.``) — no new grammar needed for
  the lexicalized form.

* ``data/tgl/particles.yaml``: add ``LEMMA: man`` to the
  existing ``man`` PART entry. The grammar's
  ``(↓2 LEMMA) =c 'man'`` constraint and the placement engine's
  ``_is_post_wh_pron_man`` exception both consult this feat.

* ``src/tgllfg/cfg/nominal.py``: new productive rule

      PRON → PRON[WH=YES] PART[ADV=EVEN, LEMMA=man]
                      with ↑.INDEF = 'NEG_INDEF'

  composing a wh-PRON with the ``man`` 2P-clitic into a virtual
  ``PRON[INDEF=NEG_INDEF]``. The Phase 5m C9 negative-existential
  rule and the Phase 5n.B C21 PRON-headed RC rule then fire on
  the produced PRON without modification.

* ``src/tgllfg/clitics/placement.py``: new
  ``_is_post_wh_pron_man`` placement exception. ``man`` is a
  2P-clitic that the placement engine normally moves to clause-
  final. When ``man`` immediately follows a wh-PRON (the
  productive indef-builder context), the exception keeps it
  adjacent so the new grammar rule can fire. Other 2P-clitic
  uses of ``man`` (after V or other heads) are unaffected.

Test cleanup:

* ``tests/tgllfg/test_phase5m_negative_indefinite.py``: drop
  the ``test_walang_ano_man_zero_parse`` pin — closed by C22.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _exist_neg_parse(text: str):
    """Return the parse with PRED='EXIST <SUBJ>' and POLARITY=NEG."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        feats = p[1].feats
        if (
            feats.get("PRED") == "EXIST <SUBJ>"
            and feats.get("POLARITY") == "NEG"
        ):
            return p
    return None


# === Lexicalized anuman ==============================================


class TestAnumanLex:
    """``anuman`` (lexicalized contracted form) parses parallel
    to ``sinuman``."""

    def test_walang_anuman_bare(self) -> None:
        result = _exist_neg_parse("Walang anuman.")
        assert result is not None
        _ct, fs, _astr, _diags = result
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "anuman"
        assert subj.feats.get("INDEF") == "NEG_INDEF"

    @pytest.mark.parametrize("sentence", [
        "Walang anumang dumating.",
        "Walang anumang kumain.",
        "Walang anumang tumakbo.",
    ])
    def test_walang_anumang_with_rc(self, sentence: str) -> None:
        result = _exist_neg_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "anuman"


# === Productive wh + man =============================================


class TestProductiveWhMan:
    """The productive ``wh-PRON + man`` form composes via the new
    ``PRON → PRON[WH=YES] PART[man,ADV=EVEN]`` rule."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Walang ano man.",   "ano"),
        ("Walang sino man.",  "sino"),
    ])
    def test_walang_wh_man_bare(
        self, sentence: str, wh_lemma: str
    ) -> None:
        result = _exist_neg_parse(sentence)
        assert result is not None, (
            f"{sentence!r} did not produce a neg-existential parse"
        )
        _ct, fs, _astr, _diags = result
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        # The productive PRON inherits LEMMA from the wh-PRON head
        # via (↑) = ↓1.
        assert subj.feats.get("LEMMA") == wh_lemma
        assert subj.feats.get("INDEF") == "NEG_INDEF"
        assert subj.feats.get("WH") is True


# === Productive wh + man + RC ========================================


class TestProductiveWhManWithRc:
    """The productive form composes with the Phase 5n.B C21
    PRON-headed RC: ``ano mang dumating`` parses as
    productively-indef PRON + RC."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Walang ano mang dumating.",   "ano"),
        ("Walang sino mang dumating.",  "sino"),
        ("Walang ano mang kumain.",     "ano"),
    ])
    def test_walang_wh_man_with_rc(
        self, sentence: str, wh_lemma: str
    ) -> None:
        result = _exist_neg_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == wh_lemma
        assert subj.feats.get("INDEF") == "NEG_INDEF"


# === Sinuman / sinuman regression =====================================


class TestExistingSinumanUnchanged:
    """The pre-existing ``sinuman`` (Phase 5m C9 / 5n.B C21) paths
    continue to fire — the C22 changes don't disturb them."""

    @pytest.mark.parametrize("sentence", [
        "Walang sinuman.",
        "Walang sinumang dumating.",
    ])
    def test_sinuman_unchanged(self, sentence: str) -> None:
        result = _exist_neg_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("LEMMA") == "sinuman"


# === man as plain 2P-clitic (non-wh) =================================


class TestManAfterNonWhUnchanged:
    """``man`` after a non-wh host (e.g., a V) continues to be
    placed by the standard 2P-clitic engine — the new placement
    exception is gated to wh-PRON predecessors only."""

    def test_man_after_v_clitic_position(self) -> None:
        # ``Kumain ako man.`` — man after V+SUBJ; the standard 2P
        # placement moves it to clause-final position. The
        # productive-indef rule does not fire because the host
        # isn't a wh-PRON.
        parses = parse_text("Kumain ako man.")
        # No exception should fire; man is placed at clause-final.
        # This sentence may parse via the standard 2P-clitic
        # absorption rule.
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # The parse should NOT be neg-existential (no walang).
        assert fs.feats.get("PRED") != "EXIST <SUBJ>"
