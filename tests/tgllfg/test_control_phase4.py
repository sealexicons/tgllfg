"""Phase 4 §7.6: control & raising — control half (raising deferred).

Three control verb classes, all using SUBJ-control over an XCOMP
complement clause:

* **Psych** (gusto / ayaw / kaya): GEN-marked experiencer is matrix
  SUBJ — the deviation from the otherwise-uniform NOM→SUBJ mapping.
  Uninflected pseudo-verbs seeded under particles.yaml.
* **Intransitive** (pumayag): NOM-marked agent is matrix SUBJ;
  AV-only inflection.
* **Transitive** (pinilit OV / inutusan DV): NOM-marked pivot
  (forcee / orderee) is matrix SUBJ; GEN-marked agent is matrix OBJ.

In all three, the control equation is identical:
``(↑ SUBJ) = (↑ XCOMP REL-PRO)``. Inside the embedded ``S_XCOMP``
the gap is bound by ``(↑ SUBJ) = (↑ REL-PRO)``, so the composition
makes ``matrix.SUBJ`` and ``matrix.XCOMP.SUBJ`` the same f-node.
``S_XCOMP`` is voice-restricted to ``V[VOICE=AV]`` — the canonical
"controlled = actor → AV pivot" pattern.

These tests cover:

* All three control patterns parsing positively.
* Voice / aspect / polarity independence between matrix and XCOMP.
* Negation composition: outer (``Hindi gusto kong kumain``) and
  inner (``Gusto kong hindi kumain``).
* Control binding: matrix.SUBJ shares the f-node id of
  XCOMP.SUBJ.
* Negative cases: bare control verb without complement (coherence
  failure); non-AV embedded clause (out of S_XCOMP scope).
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text


def _first(text: str) -> FStructure:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0][1]


def _xcomp(f: FStructure) -> FStructure:
    xcomp = f.feats.get("XCOMP")
    assert isinstance(xcomp, FStructure), f"no XCOMP on {f.feats}"
    return xcomp


def _subj(f: FStructure) -> FStructure:
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure), f"no SUBJ on {f.feats}"
    return subj


# === Psych control (gusto / ayaw / kaya) ==================================


def test_gusto_intransitive_complement() -> None:
    """``Gusto kong kumain``: GEN experiencer ``ko`` is matrix SUBJ;
    intransitive AV complement controlled by SUBJ."""
    f = _first("Gusto kong kumain.")
    assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
    xcomp = _xcomp(f)
    assert xcomp.feats.get("PRED") == "EAT <SUBJ>"
    assert xcomp.feats.get("VOICE") == "AV"


def test_gusto_transitive_complement() -> None:
    """``Gusto kong kumain ng isda``: transitive AV complement, OBJ
    inside XCOMP."""
    f = _first("Gusto kong kumain ng isda.")
    xcomp = _xcomp(f)
    assert xcomp.feats.get("PRED") == "EAT <SUBJ, OBJ>"
    assert "OBJ" in xcomp.feats


def test_ayaw_psych() -> None:
    """``Ayaw nilang tumakbo``: ayaw with 3pl experiencer."""
    f = _first("Ayaw nilang tumakbo.")
    assert f.feats.get("PRED") == "DISLIKE <SUBJ, XCOMP>"
    assert _xcomp(f).feats.get("PRED") == "TAKBO <SUBJ>"


def test_kaya_psych() -> None:
    """``Kaya kong tumakbo``: kaya = "be able to"."""
    f = _first("Kaya kong tumakbo.")
    assert f.feats.get("PRED") == "ABLE <SUBJ, XCOMP>"


def test_gusto_subj_is_gen_marked() -> None:
    """Psych predicates' SUBJ is GEN-case (the experiencer)."""
    f = _first("Gusto kong kumain.")
    subj = _subj(f)
    assert subj.feats.get("CASE") == "GEN"


# === Intransitive control (pumayag) =======================================


def test_pumayag_intransitive() -> None:
    """``Pumayag siyang kumain ng isda``: AV-intransitive matrix,
    NOM agent, transitive AV complement."""
    f = _first("Pumayag siyang kumain ng isda.")
    assert f.feats.get("PRED") == "AGREE <SUBJ, XCOMP>"
    assert f.feats.get("VOICE") == "AV"
    subj = _subj(f)
    # NOM-marked SUBJ for intransitive control (canonical mapping).
    assert subj.feats.get("CASE") == "NOM"


# === Transitive control (pinilit / inutusan) ==============================


def test_pinilit_ov() -> None:
    """``Pinilit ng nanay ang batang kumain ng isda``: OV transitive
    matrix; pivot ``bata`` (forcee) is matrix SUBJ; ``nanay`` (forcer)
    is matrix OBJ-AGENT (typed under the Phase 5b
    OBJ-θ-in-grammar alignment)."""
    f = _first("Pinilit ng nanay ang batang kumain ng isda.")
    assert f.feats.get("PRED") == "FORCE <SUBJ, OBJ-AGENT, XCOMP>"
    assert f.feats.get("VOICE") == "OV"
    subj = _subj(f)
    assert subj.feats.get("CASE") == "NOM"
    obj = f.feats.get("OBJ-AGENT")
    assert isinstance(obj, FStructure)
    assert obj.feats.get("CASE") == "GEN"


def test_inutusan_dv() -> None:
    """``Inutusan ng nanay si Maria na umuwi``: DV transitive matrix;
    pivot ``Maria`` (orderee) is SUBJ."""
    f = _first("Inutusan ng nanay si Maria na umuwi.")
    assert f.feats.get("PRED") == "ORDER <SUBJ, OBJ-AGENT, XCOMP>"
    assert f.feats.get("VOICE") == "DV"
    assert _xcomp(f).feats.get("PRED") == "UWI <SUBJ>"


# === Control binding ======================================================


def test_control_binding_psych() -> None:
    """Matrix SUBJ and XCOMP.SUBJ share the same f-node (control)."""
    f = _first("Gusto kong kumain ng isda.")
    matrix_subj = _subj(f)
    xcomp_subj = _xcomp(f).feats.get("SUBJ")
    assert isinstance(xcomp_subj, FStructure)
    assert matrix_subj.id == xcomp_subj.id


def test_control_binding_intransitive() -> None:
    f = _first("Pumayag siyang kumain ng isda.")
    matrix_subj = _subj(f)
    xcomp_subj = _xcomp(f).feats.get("SUBJ")
    assert isinstance(xcomp_subj, FStructure)
    assert matrix_subj.id == xcomp_subj.id


def test_control_binding_transitive() -> None:
    """For pinilit OV, the pivot (forcee = matrix SUBJ) controls
    XCOMP.SUBJ — the persuadee is the eater."""
    f = _first("Pinilit ng nanay ang batang kumain ng isda.")
    matrix_subj = _subj(f)
    xcomp_subj = _xcomp(f).feats.get("SUBJ")
    assert isinstance(xcomp_subj, FStructure)
    assert matrix_subj.id == xcomp_subj.id


# === Voice / aspect / polarity independence ===============================


def test_xcomp_aspect_independent_of_matrix() -> None:
    """Matrix gusto (psych, no aspect) + IPFV complement: XCOMP
    ASPECT=IPFV regardless of matrix."""
    f = _first("Gusto kong kumakain ng isda.")
    assert _xcomp(f).feats.get("ASPECT") == "IPFV"


def test_outer_negation_in_control() -> None:
    """``Hindi gusto kong kumain``: outer NEG attaches at matrix
    via the regular S → PART[NEG] S rule. XCOMP unchanged."""
    f = _first("Hindi gusto kong kumain.")
    assert f.feats.get("POLARITY") == "NEG"
    xcomp = _xcomp(f)
    # XCOMP itself has no POLARITY=NEG.
    assert xcomp.feats.get("POLARITY") != "NEG"


def test_inner_negation_in_control() -> None:
    """``Gusto kong hindi kumain``: inner NEG via
    S_XCOMP → PART[NEG] S_XCOMP. Matrix POLARITY unchanged;
    XCOMP carries POLARITY=NEG."""
    f = _first("Gusto kong hindi kumain.")
    # Matrix is not negated.
    assert f.feats.get("POLARITY") != "NEG"
    xcomp = _xcomp(f)
    assert xcomp.feats.get("POLARITY") == "NEG"


# === Negative cases =======================================================


def test_bare_control_verb_rejected() -> None:
    """``Gusto ng bata`` (no complement clause): coherence failure
    because the PRED ``WANT <SUBJ, XCOMP>`` requires XCOMP, which
    no parse can supply without the linker + S_XCOMP."""
    results = parse_text("Gusto ng bata.")
    assert not results, "bare control verb should not parse"


def test_psych_predicate_subject_condition_satisfied() -> None:
    """Psych predicates have GEN-NP=SUBJ so the Subject Condition
    holds: PRED ``WANT <SUBJ, XCOMP>`` and matrix has SUBJ."""
    f = _first("Gusto kong kumain.")
    assert "SUBJ" in f.feats
    assert f.feats.get("PRED") == "WANT <SUBJ, XCOMP>"
