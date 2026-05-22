# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.B Commit 11: yes/no indirect-Q (§18 L54).

Closes §18.1 deferral L54 (``Alam ko kung kumain ang aso.``
"I know whether the dog ate.") by adding two sibling
S_INTERROG_COMP rules in ``cfg/control.py``:

    (a) S_INTERROG_COMP → PART[COMP_TYPE=INTERROG] S[Q_TYPE=YES_NO]
        (with-ba case)
    (b) S_INTERROG_COMP → PART[COMP_TYPE=INTERROG] S
        (bare-declarative case, with ``¬ (↓2 Q_TYPE)`` gate)

alongside the existing wh-Q variant (Phase 5i Commit 8). All
three rules write ``COMP_TYPE='INTERROG'`` on the matrix COMP
to satisfy the wrap rule's ``=c 'INTERROG'`` constraint
uniformly; the new yes/no variants additionally write
``COMP_QTYPE='YES_NO'`` to distinguish them from the wh case.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _know_parse(text: str):
    parses = parse_text(text, n_best=10)
    for p in parses:
        if (p[1].feats.get("PRED") or "").startswith("KNOW"):
            return p
    return None


# === Bare declarative inner ==========================================


class TestBareDeclarativeInner:
    """``Alam ko kung kumain ang aso.`` "I know whether the dog
    ate." — bare declarative inside ``kung``, no Q_TYPE on inner.
    The Phase 5n.B Commit 11 (b) rule fires."""

    @pytest.mark.parametrize("sentence", [
        "Alam ko kung kumain ang aso.",
        "Alam ko kung pumunta si Maria.",
        "Alam ko kung tumakbo ang bata.",
    ])
    def test_bare_declarative(self, sentence: str) -> None:
        result = _know_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"
        assert comp.feats.get("COMP_QTYPE") == "YES_NO"


# === With-ba inner ===================================================


class TestWithBaInner:
    """``Alam ko kung kumain ka ba.`` "I know whether you ate." —
    inner clause has ``ba`` (Q_TYPE=YES_NO). The Phase 5n.B Commit
    11 (a) rule fires (alongside the matrix-scope ba parse)."""

    def test_with_ba_inner(self) -> None:
        parses = parse_text("Alam ko kung kumain ka ba.")
        # At least one KNOW parse with COMP_QTYPE=YES_NO on COMP.
        yn_parses = []
        for p in parses:
            if not (p[1].feats.get("PRED") or "").startswith("KNOW"):
                continue
            comp = p[1].feats.get("COMP")
            if comp and comp.feats.get("COMP_QTYPE") == "YES_NO":
                yn_parses.append(p)
        assert len(yn_parses) >= 1


# === Wh inner unchanged ==============================================


class TestWhInnerUnchanged:
    """The existing wh-Q variant (Phase 5i Commit 8) continues to
    fire on wh inner clauses; matrix COMP carries
    ``COMP_TYPE=INTERROG`` and no ``COMP_QTYPE``."""

    @pytest.mark.parametrize("sentence,wh_lemma", [
        ("Alam ko kung sino ang kumain.",  "sino"),
        ("Alam ko kung saan pumunta siya.", "saan"),
    ])
    def test_wh_inner(self, sentence: str, wh_lemma: str) -> None:
        result = _know_parse(sentence)
        assert result is not None
        _ct, fs, _astr, _diags = result
        comp = fs.feats.get("COMP")
        assert comp is not None
        assert comp.feats.get("COMP_TYPE") == "INTERROG"
        # No COMP_QTYPE on the wh path (only on yes/no path).
        assert comp.feats.get("COMP_QTYPE") is None
