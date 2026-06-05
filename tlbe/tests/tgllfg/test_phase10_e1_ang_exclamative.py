# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.E.1 — bare-ADJ X-X reduplication + the ``ang``-exclamative.

Two pieces:

* **Morphology** — the ``adj_redup`` paradigm cell
  (``data/tgl/paradigms.yaml``) produces bare adjectival full
  reduplication (``ganda → gandaganda``, ``payat → payatpayat``,
  ``puti → putiputi``) as an ADJ carrying ``REDUP=FULL`` with the
  degree left **underspecified** (no ``REDUP_SEM``; the construction
  or root class fixes it — informant 2026-05-25). Per-root opt-in on
  the gradable scalars ganda / payat / puti / init / pula. The
  additive-class indexer fix keeps simple adjectives (``pula`` /
  ``puti``) surfacing bare alongside the reduplication.

* **Grammar** — the Schachter & Otanes 1972 §4 ``ang``-exclamative
  (``Ang ganda-ganda mo!`` "you're so beautiful!"): three head
  variants (``ADJ[REDUP=FULL]`` / ``ADJ[PREDICATIVE]`` / ``QualityN``)
  over a GEN possessor, projecting ``EXCLAM=true``; the redup variant
  forces ``REDUP_SEM=INTENS``. Closes rg-int sent-655/656/1068/1069.

Also guards the ``redup_intens_adj`` retrofit (REDUP=FULL +
REDUP_SEM=ATTEN) and the ``Ang bahay mo`` gating non-match.
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Morphology: adj_redup bare X-X ====================================


@pytest.mark.parametrize(
    "surface,lemma",
    [
        ("gandaganda", "ganda"),
        ("payatpayat", "payat"),
        ("putiputi", "puti"),
        ("initinit", "init"),
        ("pulapula", "pula"),
    ],
)
def test_adj_redup_produces_underspecified_full_redup(
    surface: str, lemma: str
) -> None:
    """Each opted-in scalar produces an ADJ X-X surface with
    ``REDUP=FULL`` and the degree left underspecified (no
    ``REDUP_SEM``, no ``PREDICATIVE`` — the cell feeds only the
    exclamative via ``ADJ[REDUP=FULL]``)."""
    idx = _get_default()._index
    redup = [
        a for a in idx.adjectives.get(surface, [])
        if a.pos == "ADJ" and a.feats.get("REDUP") == "FULL"
    ]
    assert len(redup) == 1, f"expected one REDUP=FULL ADJ for {surface!r}"
    a = redup[0]
    assert a.lemma == lemma
    assert a.feats.get("REDUP_SEM") is None  # underspecified by design
    assert a.feats.get("PREDICATIVE") is None


@pytest.mark.parametrize("surface", ["bilisbilis", "lakilaki", "liitliit"])
def test_adj_redup_opt_in_required(surface: str) -> None:
    """ADJ roots NOT opted into ``adj_redup`` (bilis / laki / liit are
    ma_adj but not adj_redup) do not produce a bare X-X REDUP=FULL
    surface — the per-root opt-in gate holds."""
    idx = _get_default()._index
    redup = [
        a for a in idx.adjectives.get(surface, [])
        if a.pos == "ADJ" and a.feats.get("REDUP") == "FULL"
    ]
    assert len(redup) == 0, f"{surface!r} should not redup (not opted in)"


@pytest.mark.parametrize("simple", ["pula", "puti"])
def test_additive_class_keeps_bare_adjective(simple: str) -> None:
    """The additive ``adj_redup`` class must not suppress the bare-ADJ
    surface of a simple adjective. Regression: ``pula`` was
    ``affix_class: []`` (bare ADJ); adding adj_redup must keep it, and
    the new ``puti`` must surface bare too."""
    idx = _get_default()._index
    adj = [
        a for a in idx.adjectives.get(simple, [])
        if a.pos == "ADJ" and a.feats.get("PREDICATIVE") is True
    ]
    assert len(adj) >= 1, f"{simple!r} must surface bare as ADJ[PREDICATIVE]"


def test_redup_intens_adj_retrofit_atten() -> None:
    """The ma-X-X ``redup_intens_adj`` cell (``magandaganda``) now
    carries ``REDUP=FULL`` + ``REDUP_SEM=ATTEN`` (moderate "rather X"
    per the informant ruling), with the legacy ``INTENS=MILD``
    retained. INTENS proper is the linker form (Phase 10.E.2)."""
    idx = _get_default()._index
    intens = [
        a for a in idx.adjectives.get("magandaganda", [])
        if a.pos == "ADJ" and a.feats.get("INTENS") == "MILD"
    ]
    assert len(intens) >= 1
    assert intens[0].feats.get("REDUP") == "FULL"
    assert intens[0].feats.get("REDUP_SEM") == "ATTEN"


# === Grammar: ang-exclamative (redup variant) ==========================


@pytest.mark.parametrize(
    "sent",
    [
        "Ang ganda-ganda mo naman.",   # rg-int sent-1069
        "Bakit ang payat-payat mo?",   # rg-int sent-656
        "Ang ganda-ganda mo.",         # bare core
        "Ang payat-payat mo.",
    ],
)
def test_redup_exclamatives_parse(sent: str) -> None:
    """The redup ``ang``-exclamative audit sentences close (≥1 parse).
    ``naman`` and a fronted ``Bakit`` compose over the matrix S via
    the existing enclitic / wh-question machinery."""
    assert len(parse_text(sent)) >= 1, f"expected ≥1 parse for {sent!r}"


def test_redup_exclamative_fstructure() -> None:
    """``Ang ganda-ganda mo.`` projects the exclamative f-structure:
    ``EXCLAM=true``, ``REDUP=FULL``, ``REDUP_SEM=INTENS`` (forced by
    the frame), ``PRED='ADJ <SUBJ>'``, ``ADJ_LEMMA=ganda``, and the
    GEN possessor as SUBJ."""
    parses = parse_text("Ang ganda-ganda mo.")
    assert len(parses) >= 1
    _ct, fs, _astr, _diags = parses[0]
    assert fs.feats.get("EXCLAM") is True
    assert fs.feats.get("REDUP") == "FULL"
    assert fs.feats.get("REDUP_SEM") == "INTENS"
    assert fs.feats.get("PRED") == "ADJ <SUBJ>"
    assert fs.feats.get("ADJ_LEMMA") == "ganda"
    subj = fs.feats.get("SUBJ")
    assert subj is not None and subj.feats.get("CASE") == "GEN"


# === Grammar: ang-exclamative (non-redup variants) =====================


@pytest.mark.parametrize(
    "sent",
    [
        "Ang ganda mo.",   # variant N (quality-NOUN head, via QualityN)
        "Ang payat mo.",   # variant N
        "Ang puti mo.",    # variant A (simple-ADJ head, ADJ[PREDICATIVE])
        "Ang pula mo.",    # variant A
    ],
)
def test_nonredup_exclamatives_parse(sent: str) -> None:
    """Non-redup exclamatives close: quality-NOUN heads via the
    ``QualityN`` wrapper, simple-ADJ heads via ``ADJ[PREDICATIVE]``.
    ``EXCLAM`` set; no ``REDUP_SEM`` (no reduplication present)."""
    parses = parse_text(sent)
    assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
    _ct, fs, _astr, _diags = parses[0]
    assert fs.feats.get("EXCLAM") is True
    assert fs.feats.get("REDUP_SEM") is None


def test_exclamative_ng_phrase_possessor() -> None:
    """The possessor slot accepts a full ``ni``/``ng``-phrase
    ``NP[CASE=GEN]``, not only the clitic GEN-PRON ``mo``."""
    assert len(parse_text("Ang ganda-ganda ni Maria.")) >= 1


def test_exclamative_gating_blocks_plain_possessed_np() -> None:
    """``Ang bahay mo.`` must NOT license an exclamative S — ``bahay``
    is neither a quality-NOUN (``SEM_CLASS=QUALITY``) nor an ADJ, so
    the ``QualityN`` gating holds and the construction doesn't
    overgenerate onto ordinary possessed NPs."""
    assert len(parse_text("Ang bahay mo.")) == 0


# === Regression guards =================================================


def test_predicative_adj_unaffected() -> None:
    """The Phase 5g predicative-ADJ clause still parses."""
    assert len(parse_text("Maganda si Rosa.")) >= 1


def test_phase10d_ma_x_x_moderate_comparative_regression() -> None:
    """The pre-existing ma-X-X moderate comparative still parses (the
    ``redup_intens_adj`` path is intact under the ATTEN retrofit)."""
    assert len(parse_text("Mas maganda-ganda si Rosa kaysa kay Maria.")) >= 1
