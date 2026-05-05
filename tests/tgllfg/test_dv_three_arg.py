"""Phase 5e Commit 11: 3-argument plain DV (CAUS=NONE).

Phase 5b's multi-GEN-NP rules covered IV-BEN three-arg
applicatives. Phase 5d Commit 4 extended to IV-INSTR / IV-REASON.
Phase 5e Commit 10 added 3-arg pa-DV (CAUS=DIRECT). The remaining
gap was **plain DV (CAUS=NONE) ditransitives** — sentences like
``Sinulatan ng nanay ng liham ang anak`` "Mother wrote a letter
to the child", where the AGENT and PATIENT are GEN-marked
non-pivots and the RECIPIENT is the NOM-marked DV pivot.

Phase 5e Commit 11 adds:

* New intrinsic profile ``_DV_TR_AGENT_PATIENT_RECIPIENT_THREE_ARG``
  — AGENT and PATIENT both [+r, +o] (typed OBJ-θ), RECIPIENT
  [-r, -o] (the SUBJ pivot).
* New ``sulat`` DV BASE entry with PRED
  ``WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>``. The "-TO" suffix
  mirrors the pa-DV "-AT" convention to distinguish 3-arg DV
  from the 2-arg form.
* Three new top-level multi-GEN-NP grammar rules for
  ``V[VOICE=DV, CAUS=NONE]``, parallel to the Phase 5b pa-OV
  and Phase 5e Commit 10 pa-DV rules. All three NP-order
  permutations admitted.

Sentences enabled:

* ``Sinulatan ng nanay ng liham ang anak.`` (GEN-GEN-NOM)
* ``Sinulatan ang anak ng nanay ng liham.`` (NOM-GEN-GEN)
* ``Sinulatan ng nanay ang anak ng liham.`` (GEN-NOM-GEN)
"""

from __future__ import annotations

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _find(
    text: str,
    *,
    pred: str,
    subj_lemma: str | None = None,
    agent_lemma: str | None = None,
    patient_lemma: str | None = None,
) -> FStructure | None:
    rs = parse_text(text, n_best=15)
    for _, f, _, _ in rs:
        if f.feats.get("PRED") != pred:
            continue
        if subj_lemma is not None:
            s = f.feats.get("SUBJ")
            if not (isinstance(s, FStructure) and s.feats.get("LEMMA") == subj_lemma):
                continue
        if agent_lemma is not None:
            oa = f.feats.get("OBJ-AGENT")
            if not (isinstance(oa, FStructure) and oa.feats.get("LEMMA") == agent_lemma):
                continue
        if patient_lemma is not None:
            op = f.feats.get("OBJ-PATIENT")
            if not (isinstance(op, FStructure) and op.feats.get("LEMMA") == patient_lemma):
                continue
        return f
    return None


# === Top-level 3-arg plain DV ============================================


class TestThreeArg:
    """All three NP-order permutations of 3-arg DV-sulat parse
    with the same role bindings (AGENT first ng-NP, PATIENT
    second ng-NP, RECIPIENT pivot)."""

    def test_gen_gen_nom_order(self) -> None:
        f = _find(
            "Sinulatan ng nanay ng liham ang anak.",
            pred="WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            subj_lemma="anak",
            agent_lemma="nanay",
            patient_lemma="liham",
        )
        assert f is not None

    def test_nom_gen_gen_order(self) -> None:
        f = _find(
            "Sinulatan ang anak ng nanay ng liham.",
            pred="WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            subj_lemma="anak",
            agent_lemma="nanay",
            patient_lemma="liham",
        )
        assert f is not None

    def test_gen_nom_gen_order(self) -> None:
        f = _find(
            "Sinulatan ng nanay ang anak ng liham.",
            pred="WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            subj_lemma="anak",
            agent_lemma="nanay",
            patient_lemma="liham",
        )
        assert f is not None

    def test_aspect_ipfv(self) -> None:
        """IPFV form ``sinusulatan`` parses with the 3-arg PRED."""
        f = _find(
            "Sinusulatan ng nanay ng liham ang anak.",
            pred="WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            subj_lemma="anak",
            agent_lemma="nanay",
            patient_lemma="liham",
        )
        assert f is not None

    def test_negation(self) -> None:
        f = _find(
            "Hindi sinulatan ng nanay ng liham ang anak.",
            pred="WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>",
            subj_lemma="anak",
        )
        assert f is not None
        assert f.feats.get("POLARITY") == "NEG"


# === Regression: 2-arg DV-sulat unchanged ===============================


class TestRegression2Arg:
    """The Phase 4 §7.1 2-arg DV-sulat reading still parses."""

    def test_2arg_dv(self) -> None:
        f = _find(
            "Sinulatan ng nanay ang anak.",
            pred="WRITE <SUBJ, OBJ-AGENT>",
            subj_lemma="anak",
            agent_lemma="nanay",
        )
        assert f is not None


# === Coexistence: both lex profiles fire on 3-NP shape ==================


class TestCoexistence:
    """When the surface admits a possessive reading on the GEN-GEN
    cluster (e.g., ``ng nanay ng liham`` could be 'mother's
    letter'), the 2-arg DV reading also surfaces alongside the
    3-arg one. Both parses are linguistically valid; the n-best
    list contains both."""

    def test_3_NP_ambiguity_includes_3arg(self) -> None:
        """The 3-arg parse (with overt OBJ-PATIENT) is among the
        n-best."""
        rs = parse_text(
            "Sinulatan ng nanay ng liham ang anak.", n_best=10
        )
        preds = {str(f.feats.get("PRED")) for _, f, _, _ in rs}
        assert "WRITE-TO <SUBJ, OBJ-AGENT, OBJ-PATIENT>" in preds


# === LMT diagnostics ====================================================


class TestLmtDiagnostics:
    """No blocking LMT diagnostics on the new 3-arg DV
    construction."""

    def test_no_blocking(self) -> None:
        rs = parse_text(
            "Sinulatan ng nanay ng liham ang anak.", n_best=5
        )
        for _, _f, _c, diags in rs:
            blocking = [d for d in diags if d.kind != "lmt-mismatch"]
            assert blocking == [], f"unexpected blocking diags: {blocking}"
