"""Phase 4 §7.4 + §7.5: ay-inversion and relativization.

Both constructions share a SUBJ-gapped inner clause (``S_GAP``) whose
missing SUBJ is bound to ``REL-PRO`` via ``(↑ SUBJ) = (↑ REL-PRO)``.

* **§7.4 ay-inversion** wraps the gapped clause with a fronted topic
  NP and the linker ``ay``: ``S → NP[CASE=NOM] PART[LINK=AY] S_GAP``.
  Full identity ``(↓3 REL-PRO) = ↓1`` makes TOPIC, REL-PRO, and the
  RC's SUBJ all point to the head NP — there's no cycle because the
  inner clause IS the matrix and the head sits at TOPIC.
* **§7.5 relativization** wraps the gapped clause with a head NP and
  a linker (``na`` / ``-ng``): ``NP[CASE=X] → NP[CASE=X] PART[LINK=NA|NG]
  S_GAP``. The RC sits in head NP's ADJ, which would create a
  cyclic f-structure under full identity; we use **anaphoric**
  REL-PRO sharing instead — REL-PRO inherits PRED and CASE from the
  head NP via path-equation copies, but isn't structurally identical.
* The bound linker ``-ng`` is split off vowel-final hosts at
  pre-morph time (``batang`` → ``bata`` + ``-ng``) by
  :func:`tgllfg.text.split_linker_ng`. The split is informed by the
  morph index — known full forms like ``bumibilang`` (122 attested
  ``Vng`` verb forms) are not split.

These tests cover:

* ay-inversion: AV-intransitive and transitive across voices;
  voice / aspect / polarity preserved on the inner clause; TOPIC
  feature appears on the matrix.
* Relativization: ``-ng`` allomorphy after vowel-final hosts; ``na``
  standalone after consonant-final hosts; SUBJ-only restriction
  (OBJ-relativization is rejected).
* Linker tokenization: ``-ng`` splits when the stem is a known noun
  / verb / pronoun; bare ``Vng`` words (``bumibilang``,
  ``darating``, ...) stay intact.
"""

from __future__ import annotations

from tgllfg.common import FStructure
from tgllfg.pipeline import parse_text
from tgllfg.text import split_linker_ng, tokenize


def _first(text: str) -> FStructure:
    results = parse_text(text)
    assert results, f"no parse for {text!r}"
    return results[0][1]


def _find_with_rc(
    text: str, rc_pred: str
) -> FStructure:
    """Find the parse whose SUBJ.ADJ contains an RC with PRED=rc_pred.
    Phase 4 §7.8 added a possessive rule that creates competing
    parses for sequences like ``head-NP-with-RC + ng-NP``; this
    helper picks the relativization reading explicitly. Uses
    ``n_best=10`` so the desired parse isn't truncated by the
    default top-5 cap."""
    results = parse_text(text, n_best=10)
    assert results, f"no parse for {text!r}"
    for _, f, _, _ in results:
        subj = f.feats.get("SUBJ")
        if not isinstance(subj, FStructure):
            continue
        adj = subj.feats.get("ADJ")
        if adj is None:
            continue
        if any(
            isinstance(m, FStructure) and m.feats.get("PRED") == rc_pred
            for m in adj  # type: ignore[union-attr]
        ):
            return f
    msg_preds = [
        str(f.feats.get("SUBJ").feats.get("ADJ")) if isinstance(f.feats.get("SUBJ"), FStructure) else None  # type: ignore[union-attr]
        for _, f, _, _ in results
    ]
    raise AssertionError(
        f"no parse with RC PRED={rc_pred!r}; got {msg_preds}"
    )


def _members(adj: object) -> list[FStructure]:
    if adj is None:
        return []
    assert hasattr(adj, "__iter__"), f"ADJ value not iterable: {type(adj)}"
    return [m for m in adj if isinstance(m, FStructure)]  # type: ignore[attr-defined]


# === Linker tokenization (split_linker_ng) ================================


def test_split_linker_ng_vowel_final_known_stem() -> None:
    """``batang`` → ``bata`` + ``-ng``: vowel-final stem is known."""
    out = split_linker_ng(tokenize("batang"))
    assert [t.surface for t in out] == ["bata", "-ng"]


def test_split_linker_ng_known_full_form_intact() -> None:
    """``bumibilang`` is a known imperfective AV form; do not split."""
    out = split_linker_ng(tokenize("bumibilang"))
    assert [t.surface for t in out] == ["bumibilang"]


def test_split_linker_ng_short_function_word_intact() -> None:
    """``ang`` is a known case marker; would yield unknown stem ``a``
    if split — therefore no split."""
    out = split_linker_ng(tokenize("ang"))
    assert [t.surface for t in out] == ["ang"]


def test_split_linker_ng_unknown_word_intact() -> None:
    """Unknown surfaces with no known stem fall through unchanged."""
    out = split_linker_ng(tokenize("xyzang"))
    assert [t.surface for t in out] == ["xyzang"]


def test_split_linker_ng_pronoun_host() -> None:
    """``niyang`` (= ``niya`` + ``-ng``): pronoun stem is known."""
    out = split_linker_ng(tokenize("niyang"))
    assert [t.surface for t in out] == ["niya", "-ng"]


# === Ay-inversion (§7.4) ==================================================


def test_ay_inversion_av_intransitive() -> None:
    """``Ang aso ay tumakbo`` — pivot SUBJ fronted, intransitive AV
    inner clause. TOPIC, REL-PRO, and SUBJ all share the head NP."""
    f = _first("Ang aso ay tumakbo.")
    assert f.feats.get("PRED") == "TAKBO <SUBJ>"
    assert f.feats.get("VOICE") == "AV"
    topic = f.feats.get("TOPIC")
    subj = f.feats.get("SUBJ")
    assert isinstance(topic, FStructure)
    assert isinstance(subj, FStructure)
    # Full identity holds in ay-inversion (no cycle): TOPIC IS SUBJ.
    assert topic.id == subj.id


def test_ay_inversion_transitive_av() -> None:
    """``Ang aso ay kumain ng isda`` — AV transitive with pivot SUBJ
    fronted. The ``ng``-NP is OBJ in the inner clause."""
    f = _first("Ang aso ay kumain ng isda.")
    assert f.feats.get("PRED") == "EAT <SUBJ, OBJ>"
    assert f.feats.get("VOICE") == "AV"
    assert "TOPIC" in f.feats
    assert "SUBJ" in f.feats
    assert "OBJ" in f.feats


def test_ay_inversion_transitive_ov() -> None:
    """``Ang isda ay kinain ng bata`` — OV transitive with pivot
    (theme) SUBJ fronted. The agent ``ng``-NP is OBJ-AGENT (typed
    under the Phase 5b OBJ-θ-in-grammar alignment)."""
    f = _first("Ang isda ay kinain ng bata.")
    assert f.feats.get("VOICE") == "OV"
    assert f.feats.get("PRED") == "EAT <SUBJ, OBJ-AGENT>"
    assert "TOPIC" in f.feats


def test_ay_inversion_aspect_preserved() -> None:
    """The inner clause's ASPECT survives the wrap."""
    f = _first("Ang aso ay kumakain ng isda.")  # IPFV
    assert f.feats.get("ASPECT") == "IPFV"


def test_ay_inversion_with_negation() -> None:
    """``Si Maria ay hindi kumain`` — clausal NEG composes with
    ay-inversion. The negation rule applies to the matrix S after
    ay-wrap."""
    results = parse_text("Si Maria ay hindi kumain.")
    assert results, "no parse"
    matches = [
        f for _, f, _, _ in results
        if f.feats.get("POLARITY") == "NEG" and "TOPIC" in f.feats
    ]
    assert matches, f"no NEG+TOPIC parse; feats={[r[1].feats for r in results]}"


# === Relativization (§7.5) ================================================


def test_rel_ng_intransitive_subj_gap() -> None:
    """``Tumakbo ang batang kumain``: AV-intransitive RC, gap=SUBJ."""
    f = _first("Tumakbo ang batang kumain.")
    assert f.feats.get("PRED") == "TAKBO <SUBJ>"
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    members = _members(subj.feats.get("ADJ"))
    rcs = [m for m in members if "PRED" in m.feats and m.feats.get("VOICE") == "AV"]
    assert rcs, f"no RC in head ADJ; members={[m.feats for m in members]}"
    assert rcs[0].feats.get("PRED") == "EAT <SUBJ>"


def test_rel_ng_transitive_subj_gap() -> None:
    """``Tumakbo ang batang kumain ng isda``: AV-transitive RC,
    gap=SUBJ (the actor pivot), OBJ=isda inside the RC. Phase 4
    §7.8 introduces possessive ambiguity (the NP-final ``ng isda``
    can also parse as a possessor of the relativized head); pick
    the RC-with-OBJ parse explicitly."""
    f = _find_with_rc("Tumakbo ang batang kumain ng isda.", "EAT <SUBJ, OBJ>")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    members = _members(subj.feats.get("ADJ"))
    rcs = [m for m in members if m.feats.get("PRED") == "EAT <SUBJ, OBJ>"]
    assert rcs[0].feats.get("OBJ") is not None


def test_rel_ng_ov_voice_relativization() -> None:
    """``Kumain ng isda ang batang tumakbo``: AV-intransitive RC
    relativizing the agent pivot of the matrix verb. The relativized
    NP head is ``bata`` (matrix's SUBJ); the RC is ``tumakbo``."""
    f = _first("Kumain ng isda ang batang tumakbo.")
    assert f.feats.get("VOICE") == "AV"
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    members = _members(subj.feats.get("ADJ"))
    rcs = [m for m in members if m.feats.get("PRED") == "TAKBO <SUBJ>"]
    assert rcs, f"no RC; members={[m.feats for m in members]}"


def test_rel_na_consonant_final_host() -> None:
    """``Tumakbo ang libro na binasa ng bata``: ``libro`` ends in a
    vowel but the test verifies the standalone ``na`` linker also
    triggers relativization. (Allomorphy is host-driven; test covers
    the LINK=NA grammar branch.)

    Note: ``libro`` is vowel-final so canonical orthography is
    ``librong`` — but the standalone ``na`` form is grammatical and
    the grammar admits both LINK=NA and LINK=NG wrap variants."""
    f = _first("Tumakbo ang libro na binasa ng bata.")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    members = _members(subj.feats.get("ADJ"))
    rcs = [m for m in members if m.feats.get("VOICE") == "OV"]
    assert rcs, f"no OV RC; members={[m.feats for m in members]}"


def test_rel_subj_only_obj_relativization_rejected() -> None:
    """``*ang batang kinain ang isda`` (gap = OBJ in OV; the agent of
    OV is OBJ): rejected because S_GAP rules don't admit a NOM-NP
    inside the relative clause."""
    results = parse_text("Tumakbo ang batang kinain ang isda.")
    assert not results, f"unexpected parse: {results[0][1].feats if results else None}"


def test_rel_subj_only_obj_relativization_av_rejected() -> None:
    """``*ang isdang kumain ang bata`` (gap = OBJ in AV; the patient
    of AV is OBJ): rejected by the same SUBJ-only restriction."""
    results = parse_text("Tumakbo ang isdang kumain ang bata.")
    assert not results, f"unexpected parse: {results[0][1].feats if results else None}"


def test_rel_head_features_share_with_rc_subj() -> None:
    """The RC's SUBJ inherits the head NP's CASE via the anaphoric
    REL-PRO sharing equations ``(↓3 REL-PRO PRED) = (↓1 PRED)`` and
    ``(↓3 REL-PRO CASE) = (↓1 CASE)``."""
    f = _find_with_rc("Tumakbo ang batang kumain ng isda.", "EAT <SUBJ, OBJ>")
    subj = f.feats.get("SUBJ")
    assert isinstance(subj, FStructure)
    members = _members(subj.feats.get("ADJ"))
    rcs = [m for m in members if m.feats.get("PRED") == "EAT <SUBJ, OBJ>"]
    rc = rcs[0]
    rc_subj = rc.feats.get("SUBJ")
    assert isinstance(rc_subj, FStructure)
    # Anaphoric sharing: RC.SUBJ.CASE matches head NP's CASE.
    assert rc_subj.feats.get("CASE") == "NOM"


def test_rel_in_object_position() -> None:
    """``Kinain ng batang tumakbo ang isda``: relativization works
    on a ``ng``-NP head (the ``bata`` is OBJ-AGENT in OV under the
    Phase 5b OBJ-θ-in-grammar alignment; relativized clause
    ``tumakbo`` modifies the OBJ-AGENT)."""
    f = _first("Kinain ng batang tumakbo ang isda.")
    obj = f.feats.get("OBJ-AGENT")
    assert isinstance(obj, FStructure)
    members = _members(obj.feats.get("ADJ"))
    rcs = [m for m in members if m.feats.get("PRED") == "TAKBO <SUBJ>"]
    assert rcs, f"no RC in OBJ-AGENT ADJ; members={[m.feats for m in members]}"
