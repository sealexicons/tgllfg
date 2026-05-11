"""Phase 5n.A Commit 10 — Existential as RC head (§18 L66).

The §18.1 L66 entry asked: can ``Mayroon akong aklat na binili ko.``
"I have a book that I bought" parse with the RC modifying the
existential-head NP (the possessed N), not the matrix? The §18.2
resolution noted "the RC machinery already exists; the composition
is the analytical question."

Commit 10 audit finding: the canonical sentence + sibling
HAVE-internal-clitic + RC patterns now parse via the Phase 5n.A
Commit 8 N-level RC wrap rule (``N → N PART[LINK=N{A,G}] S_GAP``).
The Phase 5j Commit 5 HAVE rules produce a Mayroon-NP with the
possessed N as the SUBJ-NP daughter; Commit 8's N-level RC wrap
attaches the RC to that N. The resulting f-structure has the RC
in ``SUBJ ADJ`` (correct attachment to the existence-asserted N,
not the matrix S).

This commit closes L66 by adding the regression net + dedicated
documentation. No new source rules — the integration was effectively
delivered by Commit 8.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Canonical L66 target =================================================


class TestL66CanonicalTarget:
    """``Mayroon akong aklat na binili ko.`` "I have a book that I
    bought" parses with the RC under the existence-asserted N's ADJ
    set."""

    def test_canonical_sentence_parses(self) -> None:
        parses = parse_text("Mayroon akong aklat na binili ko.")
        assert len(parses) >= 1

    def test_rc_attaches_to_subj_n(self) -> None:
        """The RC modifies the existence-asserted N (the SUBJ
        daughter), not the matrix S. Verified by walking the
        f-structure: the RC's REL-PRO PRED equals the SUBJ N's
        PRED, and the RC sits in SUBJ ADJ (not matrix ADJ)."""
        parses = parse_text("Mayroon akong aklat na binili ko.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # HAVE flag is set
        assert fs.feats.get("HAVE") is True
        # SUBJ has ADJ containing an RC
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        adj = subj.feats.get("ADJ")
        assert adj is not None
        rc = next(iter(adj))
        # RC's REL-PRO PRED matches the SUBJ N's PRED
        rel_pro = rc.feats.get("REL-PRO")
        assert rel_pro is not None
        assert rel_pro.feats.get("PRED") == subj.feats.get("PRED")
        # RC's V is OV PFV "BUY <SUBJ, OBJ-AGENT>"
        assert rc.feats.get("PRED") == "BUY <SUBJ, OBJ-AGENT>"
        assert rc.feats.get("VOICE") == "OV"


# === Sibling HAVE-with-RC patterns ========================================


class TestHaveRcSiblings:
    """The L66 closure generalises to sibling patterns:
    HAVE + clitic + N + RC across V-headed RCs, ADJ-modifier RCs,
    and nasa-headed RCs."""

    @pytest.mark.parametrize("sentence", [
        # V-headed RC (the canonical):
        "Mayroon akong aklat na binili ko.",
        # ADJ-modifier (Phase 5g N-internal):
        "Mayroon akong aklat na malaki.",
        "Mayroon akong libro na malaki.",
        "Mayroon akong bahay na maliit.",
        # nasa-headed RC (Commit 8's S_GAP variant):
        "Mayroon akong bahay na nasa bundok.",
        # Multi-clitic in RC:
        "May aklat na binili ko si Maria.",
        "May aklat na malaki si Maria.",
        # Negative HAVE + V-headed RC:
        "Walang aklat na binili ko.",
    ])
    def test_have_with_rc(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1


# === Regression: Phase 5j HAVE patterns unchanged =========================


class TestPhase5jHaveBaseline:
    """The Phase 5j Commit 5 HAVE rules (positive / negative ×
    postposed / internal-clitic) must continue to work as before."""

    @pytest.mark.parametrize("sentence", [
        "May aklat ako.",          # 5a positive postposed PRON
        "May aklat si Maria.",     # 5a positive postposed N
        "May akong aklat.",        # 5b positive internal clitic
        "Walang aklat ako.",       # 5c negative postposed PRON
        "Walang aklat si Maria.",  # 5c negative postposed N
        "Wala akong aklat.",       # 5d negative internal clitic (no linker on wala)
        "Mayroon akong aklat.",    # mayroon variant of 5b
    ])
    def test_phase5j_have_baseline(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
