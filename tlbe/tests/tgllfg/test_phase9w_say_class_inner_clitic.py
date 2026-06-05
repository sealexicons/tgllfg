# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 9.W Cluster E: SAY-class V + ``na``-S OBJ profile —
inner-clause clitic anchoring + plain AV-SAY rule + ``na``-linker
disambiguation with intervening clitic-PRON.

Closes R&C 1990 sent-866 ``Nagpasabi ang boss ko na hindi siya
papasok sa trabaho.`` (also pinned as sent-909 in 8.O).

Three coordinated changes in this slice:

* ``clitics/placement.py:_next_content_is_verb`` — extended to
  skip clitic-PRONs in the look-ahead (sat between NEG and V at
  the inner-clause source surface). The ``na``-disambiguator's
  post-noun-PRON-with-V-following branch now fires correctly,
  classifying ``na`` after ``ang boss ko`` as the linker.

* ``clitics/placement.py:reorder_clitics`` — per-anchor grouping
  via new ``_enclosing_anchor_for_clitic``. Inner-clause
  clitic-PRONs (those crossed from the matrix anchor by a
  disambiguated ``na``-linker) anchor to the inner V instead of
  being hoisted to the matrix V. ADV-clitics in inner clauses
  flush at clause-final punct rather than at sentence-final.

* ``cfg/clause.py`` — new plain AV-SAY rule ``V[VOICE=AV,
  SAY_CLASS] NP[CASE=NOM] PART[LINK=NA] S`` paralleling the 8.O
  AV-CAUS-INDIRECT-SAY rule but without the CAUS=INDIRECT gate.
  Required because ``nagsabi``'s morph cell sets CAUS=NONE
  (string atom), so the 8.O rule's ``CAUS=INDIRECT`` constraint
  excludes plain ``nagsabi`` cases — and the existing 5n.A OV-SAY
  rule only covers OV voice + GEN-PRON actor.
"""

import pytest

from tgllfg.core.pipeline import parse_text


def _has_parse(text: str, n: int = 3) -> int:
    return len(parse_text(text, n_best=n))


# === 9.W.E.1 — sent-866 audit pin =====================================


class TestPhase9wE1AuditPin:
    """sent-866 / sent-909 (R&C 1990): ``Nagpasabi ang boss ko na
    hindi siya papasok sa trabaho.`` — the matrix V is the 8.O AV-
    CAUS-INDIRECT SAY-class form; the inner-S has a fronted-NEG +
    2P-clitic-PRON + V shape. The audit pin was originally
    attributed to ``papasok`` TR/INTR polysemy, but the real
    blockers were the clitic-placement pass + the ``na``-
    disambiguator."""

    def test_audit_pin_sent_866(self) -> None:
        assert _has_parse(
            "Nagpasabi ang boss ko na hindi siya papasok sa trabaho."
        ) >= 1

    def test_audit_pin_minus_locative(self) -> None:
        assert _has_parse(
            "Nagpasabi ang boss ko na hindi siya papasok."
        ) >= 1

    def test_audit_pin_minus_possessor(self) -> None:
        assert _has_parse(
            "Nagpasabi si Juan na hindi siya papasok sa trabaho."
        ) >= 1

    def test_audit_pin_minimal(self) -> None:
        assert _has_parse(
            "Nagpasabi si Juan na hindi siya papasok."
        ) >= 1


# === 9.W.E.2 — plain AV-SAY (no CAUS) =================================


class TestPhase9wE2PlainAvSay:
    """``V[VOICE=AV, SAY_CLASS] NP[CASE=NOM] PART[LINK=NA] S`` —
    plain AV-SAY (no CAUS) reported-clause rule paralleling 8.O
    AV-CAUS-INDIRECT-SAY without the CAUS=INDIRECT gate. Gated on
    ``(↓1 CAUS) =c 'NONE'`` so the rule doesn't double-fire with
    8.O on AV-CAUS-INDIRECT forms."""

    @pytest.mark.parametrize("text", [
        "Nagsabi si Maria na kumain si Juan.",
        "Nagsabi siya na kumain si Juan.",
        "Nagsabi si Juan na umalis si Maria.",
        "Nagsabi si Juan na hindi siya papasok.",
        "Nagsabi si Juan na hindi siya papasok sa trabaho.",
    ])
    def test_plain_av_say_parses(self, text: str) -> None:
        assert _has_parse(text) >= 1

    def test_disambiguation_with_8o(self) -> None:
        """``Nagpasabi`` (AV-CAUS-INDIRECT-SAY) still routes through
        the 8.O rule, not the new plain AV-SAY rule. Both rules
        produce a parse — verify exactly one fires by ASTRUCT
        invariance (8.O's PRED is SABI with CAUS recorded on the V
        head; plain AV-SAY has CAUS=NONE on the V head)."""
        parses = parse_text(
            "Nagpasabi si Maria na kumain si Juan.", n_best=3,
        )
        assert parses
        # No double-firing — should still be exactly one parse.
        assert len(parses) == 1


# === 9.W.E.3 — inner-clause clitic anchoring ==========================


class TestPhase9wE3InnerClitic:
    """The reorder pass anchors inner-clause clitic-PRONs to the
    inner V, not the matrix V. Verifies that source-surface
    ``... na hindi siya V ...`` parses (where ``siya`` is the
    inner SUBJ, not a matrix argument)."""

    @pytest.mark.parametrize("text", [
        # Matrix subject ≠ inner subject (referent split)
        "Nagsabi si Juan na hindi siya kumain.",
        "Nagsabi si Maria na hindi siya papasok.",
        "Nagsabi si Pedro na hindi siya pumasok.",
        # OV-SAY + inner clitic
        "Sinabi niya na hindi siya kumain.",
        "Sinabi ko na hindi siya papasok sa trabaho.",
    ])
    def test_inner_clitic_pron_parses(self, text: str) -> None:
        assert _has_parse(text) >= 1


# === Regressions ======================================================


class TestPhase9wRegressions:
    """The clitic-placement refactor doesn't break canonical
    Wackernagel placement, verbless N/ADJ-anchor clauses, or
    existing SAY-class / OV-SAY parses."""

    @pytest.mark.parametrize("text", [
        # Canonical Wackernagel
        "Hindi siya papasok.",
        "Hindi siya kumain.",
        "Kumain siya.",
        # Verbless ADJ-PRED with aspectual `na` (ALREADY)
        "Maganda na ka ba.",
        # 8.O AV-CAUS-INDIRECT-SAY (existing)
        "Nagpasabi si Maria na kumain si Juan.",
        # 5n.A OV-SAY (existing)
        "Sinabi niya na pumunta si Maria.",
        "Sinabi niya na kumain si Maria.",
        # NEG + plain inner-S
        "Nagsabi si Juan na hindi kumakain si Maria.",
        # canonical V S inner (PRON at clause-end)
        "Nagsabi si Juan na hindi papasok siya.",
    ])
    def test_regression_holds(self, text: str) -> None:
        assert _has_parse(text) >= 1, f"regression on {text!r}"
