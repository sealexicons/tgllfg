"""Phase 5n.B Commit 12: additional KNOW-class predicates (§18 L55).

Closes §18.1 deferral L55 (``Akala / isip / naririnig / naaalala``
KNOW-class) by adding four new uninflected pseudo-verb lex entries
that pattern syntactically like ``alam`` (Phase 5i Commit 8):

    Akala ko kung kumain ang aso.        BELIEVE
    Isip ko kung sino kumain.            THINK
    Naririnig ko kung sino ang kumain.   HEAR
    Naaalala ko kung saan pumunta siya.  REMEMBER

Each new predicate carries ``CTRL_CLASS=KNOW`` (so the existing
Phase 5i indirect-Q wrap rule fires) and a distinct ``PRED``
template (BELIEVE / THINK / HEAR / REMEMBER) so downstream
consumers can distinguish the matrix predicate.

This commit is purely additive lex — no new grammar rules. The
existing ``S → V[CTRL_CLASS=KNOW] NP[CASE=GEN] S_INTERROG_COMP``
wrap from ``cfg/control.py`` (Phase 5i C8 + 5n.B C11) handles all
four predicates uniformly.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


def _matrix_pred(text: str, prefix: str):
    """Return the parse whose matrix PRED starts with ``prefix``,
    or None if no such parse exists."""
    parses = parse_text(text, n_best=10)
    for p in parses:
        if (p[1].feats.get("PRED") or "").startswith(prefix):
            return p
    return None


# === Each predicate × wh indirect-Q ====================================


class TestWhIndirectQ:
    """Each new KNOW-class predicate parses an indirect wh-Q
    complement (mirroring the existing ``alam`` Phase 5i C8 path).
    The matrix PRED uniquely identifies the predicate, and COMP
    carries ``COMP_TYPE=INTERROG`` from the ``kung`` complementizer."""

    @pytest.mark.parametrize("sentence,pred_prefix", [
        ("Akala ko kung sino ang kumain.",     "BELIEVE"),
        ("Isip ko kung sino ang kumain.",      "THINK"),
        ("Naririnig ko kung sino ang kumain.", "HEAR"),
        ("Naaalala ko kung sino ang kumain.",  "REMEMBER"),
    ])
    def test_wh_indirect_q_parses(
        self, sentence: str, pred_prefix: str
    ) -> None:
        result = _matrix_pred(sentence, pred_prefix)
        assert result is not None, (
            f"{sentence!r} did not produce a parse with PRED "
            f"starting with {pred_prefix!r}"
        )
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"


# === Each predicate × yes/no indirect-Q ===============================


class TestYesNoIndirectQ:
    """Each new KNOW-class predicate also admits a yes/no inner
    clause via the Phase 5n.B Commit 11 rule. The matrix COMP
    carries ``COMP_QTYPE=YES_NO`` to distinguish from the wh path."""

    @pytest.mark.parametrize("sentence,pred_prefix", [
        ("Akala ko kung kumain ang aso.",      "BELIEVE"),
        ("Isip ko kung pumunta si Maria.",     "THINK"),
        ("Naririnig ko kung tumakbo si Juan.", "HEAR"),
        ("Naaalala ko kung kumain ang bata.",  "REMEMBER"),
    ])
    def test_yes_no_indirect_q_parses(
        self, sentence: str, pred_prefix: str
    ) -> None:
        result = _matrix_pred(sentence, pred_prefix)
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"
        assert comp.feats.get("COMP_QTYPE") == "YES_NO"


# === Each predicate × adverbial-wh indirect-Q =========================


class TestAdverbialWhIndirectQ:
    """Each new KNOW-class predicate also admits adverbial-wh inner
    clauses (saan / kailan / paano / bakit) via the existing Phase 5i
    machinery. Validates the wrap rule fires uniformly across PRED."""

    @pytest.mark.parametrize("sentence,pred_prefix", [
        ("Akala ko kung saan pumunta siya.",     "BELIEVE"),
        ("Isip ko kung kailan kumain ang aso.",  "THINK"),
        ("Naririnig ko kung paano kumain siya.", "HEAR"),
        ("Naaalala ko kung bakit kumain ako.",   "REMEMBER"),
    ])
    def test_adverbial_wh_indirect_q(
        self, sentence: str, pred_prefix: str
    ) -> None:
        result = _matrix_pred(sentence, pred_prefix)
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"


# === Phase 5i alam regression preserved ==============================


class TestAlamUnchanged:
    """The original ``alam`` KNOW-class lex entry (Phase 5i C8)
    continues to fire unchanged — adding the four new entries
    doesn't introduce ambiguity or regressions on the canonical
    Phase 5i indirect-Q surfaces."""

    def test_alam_wh_indirect_q(self) -> None:
        result = _matrix_pred("Alam ko kung sino ang kumain.", "KNOW")
        assert result is not None
        _ct, fs, _astr, _diags = result
        # Single canonical parse per Phase 5l Commit 3 polysemy pin.
        assert fs.feats.get("PRED") == "KNOW <SUBJ, COMP>"
