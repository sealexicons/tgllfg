# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.C — NUM → distributive-count ADV bare X-X paradigm cell.

Adds the productive ``num_redup_distr`` paradigm cell in
``data/tgl/paradigms.yaml`` (third sibling of the Phase 10.A
``time_redup_freq`` + Phase 10.B ``place_redup_distr`` cells).
Derives distributive-count adverbials ("X at a time / by Xs /
one by one") from the cardinal-NUM roots:

* ``isa`` → ``isa-isa`` "one by one"
* ``dalawa`` → ``dalawa-dalawa`` "two at a time"
* ``tatlo`` → ``tatlo-tatlo`` "three at a time"
* ... through ``sampu`` → ``sampu-sampu`` "by tens"

All ten cardinal roots (1-10) in ``data/tgl/numerals.yaml`` opt
in via ``affix_class: [..., num_redup_distr]`` — distributive
count is productive across the full cardinal series (S&O 1972
§4 + Phase 10 external-reviewer typology).

Routing: the cardinals are NUM *roots* in numerals.yaml (the
paradigm-engine inputs; the bare-NUM analyses come from the
separate particles.yaml entries). The cell fires via
``_index_paradigm_via_base_pos`` (the NOUN/ADJ/NUM-root indexer
that also drives ``tig_distrib`` / ``approx_redup``), POS-flips
NUM→ADV, and routes the derived surface into the particles
index. ``lemma_redup_hyphen: true`` gives the canonical
hyphenated LEMMA.

Feats: ``ADV_TYPE=MANNER``, ``DISTRIB=true`` (same binary feat
``tig_distrib`` sets), ``REDUP=FULL`` + ``REDUP_SEM=DISTR``
(Phase 10.B cross-cutting feats). ``CARDINAL=false`` overrides
the inherited ``CARDINAL=true`` — the derived form is
categorially an adverb, not a cardinal numeral.
``CARDINAL_VALUE`` is retained from the root.

No ``redup_o_raise``: per the reviewer typology ``tatlo-tatlo``
(not ``tatlu-tatlo``); /o/-final cardinals take no first-copy
raising in this use.

**Scope limit (morphology-only)**: like 10.B, no clause-final
``S → S AdvP[MANNER]`` / ``nang`` + distributive-ADV attachment
rule. MANNER AdvPs are in the discourse.py §5f-C5 deferral
block alongside LOCATION; grammar-side attachment is a follow-on
gated on audit pressure. Audit-corpus presence: zero direct
attestations across all four waves.
"""

import pytest

from tgllfg.morph.analyzer import _get_default


# === Productive analyses are indexed =====================================


@pytest.mark.parametrize("surface,lemma,value", [
    ("isaisa",         "isa-isa",         "1"),
    ("dalawadalawa",   "dalawa-dalawa",   "2"),
    ("tatlotatlo",     "tatlo-tatlo",     "3"),
    ("apatapat",       "apat-apat",       "4"),
    ("limalima",       "lima-lima",       "5"),
    ("animanim",       "anim-anim",       "6"),
    ("pitopito",       "pito-pito",       "7"),
    ("walowalo",       "walo-walo",       "8"),
    ("siyamsiyam",     "siyam-siyam",     "9"),
    ("sampusampu",     "sampu-sampu",     "10"),
])
def test_num_redup_distr_indexed(surface: str, lemma: str, value: str) -> None:
    """Each cardinal 1-10 derives a distributive-count ADV with the
    canonical hyphenated LEMMA, ADV_TYPE=MANNER, DISTRIB=true,
    REDUP=FULL, REDUP_SEM=DISTR, CARDINAL=false (override of the
    inherited NUM-root CARDINAL=true), and CARDINAL_VALUE retained."""
    analyses = _get_default()._index.particles.get(surface, [])
    redup = [
        a for a in analyses
        if a.pos == "ADV"
        and a.feats.get("REDUP_SEM") == "DISTR"
        and a.feats.get("DISTRIB") is True
    ]
    assert len(redup) == 1, (
        f"expected exactly one DISTR distributive-count ADV for "
        f"{surface!r}, got {len(redup)} (full analyses={analyses!r})"
    )
    a = redup[0]
    assert a.lemma == lemma
    assert a.feats.get("LEMMA") == lemma
    assert a.feats.get("ADV_TYPE") == "MANNER"
    assert a.feats.get("REDUP") == "FULL"
    assert a.feats.get("CARDINAL_VALUE") == value
    # The derived adverb is NOT a cardinal numeral.
    assert a.feats.get("CARDINAL") is False, (
        f"expected CARDINAL=false on the distributive-count ADV "
        f"{surface!r} (override of inherited NUM-root CARDINAL=true); "
        f"got {a.feats.get('CARDINAL')!r}"
    )


def test_o_final_cardinals_no_first_copy_raise() -> None:
    """The /o/-final cardinals (tatlo / pito / walo) do NOT raise
    the first copy's /o/→/u/ — per the reviewer typology
    ``tatlo-tatlo``, not ``tatlu-tatlo``. ``num_redup_distr`` uses
    the bare ``redup_root`` op with no ``redup_o_raise`` opt-in."""
    idx = _get_default()._index
    for joined, raised in (
        ("tatlotatlo", "tatlutatlo"),
        ("pitopito",   "pitupito"),
        ("walowalo",   "waluwalo"),
    ):
        assert joined in idx.particles, f"expected productive {joined!r}"
        assert raised not in idx.particles, (
            f"did NOT expect raised {raised!r} — cardinals don't opt "
            f"into redup_o_raise"
        )


# === No spurious cardinal-NP-modifier reading ==========================


def test_distributive_count_is_not_a_cardinal_num() -> None:
    """The joined ``isaisa`` surface has only the ADV reading — no
    NUM[CARDINAL] analysis that the cardinal-NP-modifier rule could
    consume. The POS-flip to ADV plus the CARDINAL=false override
    both ensure ``isa-isa`` does not behave as a bare cardinal."""
    analyses = _get_default()._index.particles.get("isaisa", [])
    num_cardinals = [
        a for a in analyses
        if a.pos == "NUM" and a.feats.get("CARDINAL") is True
    ]
    assert len(num_cardinals) == 0, (
        f"unexpected NUM[CARDINAL] analysis for 'isaisa': "
        f"{num_cardinals!r}"
    )


# === Regression: sibling NUM-paradigm cells unchanged ===================


def test_tig_distrib_sibling_unchanged() -> None:
    """Adding ``num_redup_distr`` to the cardinal roots' affix_class
    list must not disturb the existing ``tig_distrib`` derivation:
    ``tigisa`` "one each" stays a NUM[CARDINAL, DISTRIB] with
    lemma ``isa``."""
    analyses = _get_default()._index.particles.get("tigisa", [])
    tig = [
        a for a in analyses
        if a.pos == "NUM"
        and a.feats.get("DISTRIB") is True
        and a.feats.get("CARDINAL") is True
    ]
    assert len(tig) == 1
    assert tig[0].lemma == "isa"
    assert tig[0].feats.get("CARDINAL_VALUE") == "1"
    # tig_distrib does NOT carry the Phase 10 REDUP feats.
    assert tig[0].feats.get("REDUP") is None


def test_approx_redup_sibling_unchanged() -> None:
    """The ``approx_redup`` CV-reduplication (``iisa`` "about one")
    stays a NUM[CARDINAL, APPROX] — distinct surface (CV-redup, not
    full-redup) and distinct semantics from the distributive count."""
    analyses = _get_default()._index.particles.get("iisa", [])
    approx = [
        a for a in analyses
        if a.pos == "NUM" and a.feats.get("APPROX") is True
    ]
    assert len(approx) == 1
    assert approx[0].lemma == "isa"
    assert approx[0].feats.get("REDUP") is None


def test_bare_cardinal_unchanged() -> None:
    """The bare cardinal ``isa`` (from particles.yaml) is unchanged
    by the numerals.yaml root affix_class addition — still a
    NUM[CARDINAL=true, CARDINAL_VALUE=1, NUM=SG]."""
    analyses = _get_default()._index.particles.get("isa", [])
    bare = [
        a for a in analyses
        if a.pos == "NUM"
        and a.feats.get("CARDINAL") is True
        and a.feats.get("CARDINAL_VALUE") == "1"
        and a.feats.get("DISTRIB") is None
        and a.feats.get("REDUP") is None
    ]
    assert len(bare) >= 1, (
        f"expected the plain cardinal 'isa' NUM analysis to survive; "
        f"got {analyses!r}"
    )


# === Cross-family REDUP_SEM consistency ================================


def test_redup_full_shared_across_distr_cells() -> None:
    """The 10.B place_redup_distr (bahay-bahay) and 10.C
    num_redup_distr (isa-isa) cells both stamp REDUP=FULL +
    REDUP_SEM=DISTR — the distributive sub-family shares both
    feats. The 10.A time_redup_freq (araw-araw) shares REDUP=FULL
    but differs in REDUP_SEM=FREQ."""
    idx = _get_default()._index

    def _redup_feats(surface: str) -> tuple[object, object]:
        for a in idx.particles.get(surface, []):
            if a.feats.get("REDUP") == "FULL":
                return a.feats.get("REDUP"), a.feats.get("REDUP_SEM")
        return (None, None)

    assert _redup_feats("isaisa") == ("FULL", "DISTR")
    assert _redup_feats("bahaybahay") == ("FULL", "DISTR")
    assert _redup_feats("arawaraw") == ("FULL", "FREQ")
