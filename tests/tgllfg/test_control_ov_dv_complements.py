"""Phase 5c §7.6 follow-on: non-AV control complements.

Phase 4 §7.6 restricted ``S_XCOMP`` to ``V[VOICE=AV]``: the
controllee was the actor, which is SUBJ in AV. Phase 5c lifts that
restriction by adding three new ``S_XCOMP`` variants for OV / DV /
IV embedded clauses, where the controllee is the actor's typed GF
``OBJ-AGENT`` under the Phase 5b OBJ-θ-in-grammar alignment. The
matrix wrap rule is unchanged — ``(↑ SUBJ) = (↑ XCOMP REL-PRO)``
still binds the matrix controller; only the embedded clause's
internal REL-PRO routing differs per voice.

Tests cover:

* All three non-AV embedded variants under each control class
  (psych, intransitive, transitive) where the matrix supports the
  combination.
* Control binding: matrix.SUBJ and embedded.OBJ-AGENT share the
  same f-node id.
* Inner negation under non-AV control (recursion through
  ``S_XCOMP → PART[NEG] S_XCOMP``).
* Phase 5b embedded-clause LMT check fires no diagnostics.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> tuple[FStructure, list]:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    _, f, _, diags = results[0]
    return f, diags


def _xcomp(f: FStructure) -> FStructure:
    xc = f.feats.get("XCOMP")
    assert isinstance(xc, FStructure), f"no XCOMP on {f.feats}"
    return xc


def _subj(f: FStructure) -> FStructure:
    s = f.feats.get("SUBJ")
    assert isinstance(s, FStructure), f"no SUBJ on {f.feats}"
    return s


# === Psych control + non-AV embedded =====================================


class TestPsychControlOvDvIv:
    """``Gusto`` (psych) + non-AV embedded clause. Matrix
    GEN-experiencer is SUBJ; embedded actor is the gap, routed to
    ``OBJ-AGENT`` via the new S_XCOMP rules."""

    def test_psych_with_ov_embedded(self) -> None:
        # "Gusto kong kakainin ang isda" — "I want to eat the fish"
        # Embedded kakainin is OV CTPL (cv-redup + -in suffix).
        f, _ = _first("Gusto kong kakainin ang isda.")
        assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
        xc = _xcomp(f)
        assert xc.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
        assert xc.feats.get("VOICE") == "OV"

    def test_psych_with_dv_embedded(self) -> None:
        # "Gusto niyang susulatan ang nanay" — "He wants to write to mother"
        f, _ = _first("Gusto niyang susulatan ang nanay.")
        xc = _xcomp(f)
        assert xc.feats.get("PRED") == "WRITE <SUBJ, OBJ-AGENT>"
        assert xc.feats.get("VOICE") == "DV"

    def test_psych_with_iv_embedded(self) -> None:
        # "Gusto niyang itatapon ang basura" — "He wants to throw the trash"
        f, _ = _first("Gusto niyang itatapon ang basura.")
        xc = _xcomp(f)
        assert xc.feats.get("PRED") == "THROW <SUBJ, OBJ-AGENT>"
        assert xc.feats.get("VOICE") == "IV"


# === Transitive control + non-AV embedded ================================


class TestTransitiveControlOvDvEmbedded:
    """``Pinilit`` (OV transitive control) + non-AV embedded. The
    matrix forcee (NOM SUBJ) controls the embedded actor
    (OBJ-AGENT)."""

    def test_pinilit_with_ov_embedded(self) -> None:
        # "Pinilit ko siyang kakainin ang isda" — "I forced him to
        # eat the fish".
        f, _ = _first("Pinilit ko siyang kakainin ang isda.")
        assert f.feats.get("PRED") == "FORCE <SUBJ, OBJ-AGENT, XCOMP>"
        xc = _xcomp(f)
        assert xc.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
        assert xc.feats.get("VOICE") == "OV"

    def test_pinilit_with_dv_embedded(self) -> None:
        # "Pinilit ko siyang susulatan ang nanay" — "I forced him
        # to write to mother".
        f, _ = _first("Pinilit ko siyang susulatan ang nanay.")
        xc = _xcomp(f)
        assert xc.feats.get("PRED") == "WRITE <SUBJ, OBJ-AGENT>"
        assert xc.feats.get("VOICE") == "DV"


# === Control binding (matrix.SUBJ ≡ embedded.OBJ-AGENT) ==================


class TestControlBindingNonAv:
    """The matrix wrap rule binds ``matrix.SUBJ = matrix.XCOMP.REL-PRO``;
    the embedded S_XCOMP rule binds ``embedded.OBJ-AGENT = embedded.REL-PRO``.
    Composition: ``matrix.SUBJ`` and ``embedded.OBJ-AGENT`` are the
    same f-node — i.e., the controller IS the controllee."""

    def test_psych_ov_binding(self) -> None:
        f, _ = _first("Gusto kong kakainin ang isda.")
        m_subj = _subj(f)
        x_obj_agent = _xcomp(f).feats.get("OBJ-AGENT")
        assert isinstance(x_obj_agent, FStructure)
        assert m_subj.id == x_obj_agent.id

    def test_psych_dv_binding(self) -> None:
        f, _ = _first("Gusto niyang susulatan ang nanay.")
        m_subj = _subj(f)
        x_obj_agent = _xcomp(f).feats.get("OBJ-AGENT")
        assert isinstance(x_obj_agent, FStructure)
        assert m_subj.id == x_obj_agent.id

    def test_transitive_ov_binding(self) -> None:
        # The OV-transitive matrix's NOM-pivot (forcee) controls the
        # embedded OBJ-AGENT — the persuadee is the eater.
        f, _ = _first("Pinilit ko siyang kakainin ang isda.")
        m_subj = _subj(f)
        x_obj_agent = _xcomp(f).feats.get("OBJ-AGENT")
        assert isinstance(x_obj_agent, FStructure)
        assert m_subj.id == x_obj_agent.id


# === Voice / aspect independence between matrix and XCOMP ================


class TestVoiceAspectIndependence:
    """The matrix's voice doesn't constrain the embedded clause's
    voice — psych (no voice) admits OV / DV / IV, OV-transitive
    admits OV / DV / IV. Aspect on embedded is independent of
    matrix."""

    def test_pfv_ov_embedded(self) -> None:
        # "Gusto kong kinain ang isda" — PFV OV embedded.
        f, _ = _first("Gusto kong kinain ang isda.")
        xc = _xcomp(f)
        assert xc.feats.get("VOICE") == "OV"
        assert xc.feats.get("ASPECT") == "PFV"

    def test_ipfv_ov_embedded(self) -> None:
        # "Gusto kong kinakain ang isda" — IPFV OV embedded.
        f, _ = _first("Gusto kong kinakain ang isda.")
        xc = _xcomp(f)
        assert xc.feats.get("ASPECT") == "IPFV"

    def test_ctpl_ov_embedded(self) -> None:
        # "Gusto kong kakainin ang isda" — CTPL OV embedded.
        f, _ = _first("Gusto kong kakainin ang isda.")
        xc = _xcomp(f)
        assert xc.feats.get("ASPECT") == "CTPL"


# === Inner negation under non-AV control =================================


class TestInnerNegationNonAv:
    """The negation rule ``S_XCOMP → PART[POLARITY=NEG] S_XCOMP``
    is voice-agnostic (it recurses on S_XCOMP regardless of which
    voice frame the inner S_XCOMP expands to). Inner negation
    composes with the new non-AV embedded variants."""

    def test_inner_neg_ov_embedded(self) -> None:
        # "Gusto kong hindi kakainin ang isda" — embedded OV is
        # negated; matrix is not.
        f, _ = _first("Gusto kong hindi kakainin ang isda.")
        assert f.feats.get("POLARITY") != "NEG"
        xc = _xcomp(f)
        assert xc.feats.get("POLARITY") == "NEG"
        assert xc.feats.get("VOICE") == "OV"


# === LMT diagnostics: clean ==============================================


class TestEmbeddedLmtClean:
    """Phase 5b's ``apply_lmt_with_check`` walks ``XCOMP`` slots
    and runs ``lmt_check`` on each embedded f-structure with its own
    PRED. The new non-AV variants must pass that check: the embedded
    lex entry's intrinsic profile predicts SUBJ + OBJ-AGENT and the
    grammar emits exactly that pair."""

    def test_ov_embedded_no_lmt_mismatch(self) -> None:
        _, diags = _first("Gusto kong kakainin ang isda.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_dv_embedded_no_lmt_mismatch(self) -> None:
        _, diags = _first("Gusto niyang susulatan ang nanay.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_iv_embedded_no_lmt_mismatch(self) -> None:
        _, diags = _first("Gusto niyang itatapon ang basura.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)

    def test_transitive_with_ov_embedded_no_lmt_mismatch(self) -> None:
        _, diags = _first("Pinilit ko siyang kakainin ang isda.")
        assert not any(d.is_blocking() for d in diags)
        assert not any(d.kind == "lmt-mismatch" for d in diags)
