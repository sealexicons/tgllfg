# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.B — PLACE-N → distributive-LOC ADV bare X-X paradigm cell.

Adds the productive ``place_redup_distr`` paradigm cell in
``data/tgl/paradigms.yaml`` (sibling of the Phase 10.A
``time_redup_freq`` cell; same structure: ``base_pos: NOUN,
pos: ADV``, single ``redup_root`` op, ``lemma_redup_hyphen:
true``). Five PLACE-N roots opt in via ``affix_class:
[place_redup_distr]`` in ``data/tgl/nouns.yaml``:

* ``bahay`` "house" — ``bahay-bahay`` "house to house"
* ``pinto`` "door" — ``pinto-pinto`` "door to door"
* ``bayan`` "town" — ``bayan-bayan`` "town to town"
* ``bundok`` "mountain" — ``bundok-bundok`` "mountain after mountain"
* ``bukid`` "field/countryside" — ``bukid-bukid`` "from farm to farm"

The cell stamps ``ADV_TYPE=LOCATION`` (existing value, consumed
by the wh-LOC ``saan`` / ``nasaan`` entries) plus the cross-
cutting Phase 10 morphological feats ``REDUP=FULL`` +
``REDUP_SEM=DISTR`` (introduced with this cell, retrofitted to
the Phase 10.A ``time_redup_freq`` cell with ``REDUP_SEM=FREQ``).

Audit-corpus presence: zero direct attestations. Reference
support: the external-reviewer 100-form Phase 10 reduplication
typology (archived in [[project_phase10_a_progress]]) explicitly
attests ``bahay-bahay`` / ``pinto-pinto`` / ``bayan-bayan`` /
``bundok-bundok`` / ``bukid-bukid`` as productive distributive
locatives. S&O 1972 / Ramos 1971 / R&G transcriptions don't
enumerate the pattern (consistent with the reviewer's note that
PLACE-N → distributive redup is "productive with semantic
restrictions, not a closed lexical list" — refs typically
illustrate via specific examples rather than enumerate).

No ``redup_o_raise``: per the reviewer's typology
``pinto-pinto`` (not ``pintu-pinto``) and ``bundok-bundok``
(not ``bunduk-bundok``) are the canonical surfaces. Stem-final
/o/ raising under redup is per-root opt-in (Phase 10.A
introduced the flag, used only by ``taon`` so far).

**Scope limit (morphology-only)**: the cell productizes the
lex surface but does NOT add a clause-final ``S → S
AdvP[LOCATION]`` attachment rule. Per
``src/tgllfg/cfg/discourse.py`` §5f-C5 closing comment +
Phase 9.W Cluster A/H precedent, clause-final LOCATION /
MANNER AdvPs are still in the deferral block (Wackernagel-
cluster + quantifier-float interaction risk). The reviewer
endorsed keeping productive redup machinery in
morphology/lex rather than CFG syntax. Grammar-side
attachment is a follow-on (Phase 10.B.post-N or Phase 11+
depending on audit pressure).
"""

import pytest

from tgllfg.morph.analyzer import _get_default


# === Productive analyses are indexed =====================================


@pytest.mark.parametrize("surface,lemma", [
    ("bahaybahay",   "bahay-bahay"),
    ("pintopinto",   "pinto-pinto"),
    ("bayanbayan",   "bayan-bayan"),
    ("bundokbundok", "bundok-bundok"),
    ("bukidbukid",   "bukid-bukid"),
])
def test_place_redup_distr_indexed_with_hyphenated_lemma(
    surface: str, lemma: str,
) -> None:
    """The productive cell indexes each PLACE-N redup surface as
    ADV with the canonical hyphenated LEMMA, ADV_TYPE=LOCATION,
    REDUP=FULL, REDUP_SEM=DISTR."""
    analyses = _get_default()._index.particles.get(surface, [])
    redup = [
        a for a in analyses
        if a.pos == "ADV"
        and a.feats.get("ADV_TYPE") == "LOCATION"
        and a.feats.get("REDUP_SEM") == "DISTR"
    ]
    assert len(redup) == 1, (
        f"expected exactly one DISTR LOCATION ADV analysis for "
        f"{surface!r}, got {len(redup)} (full analyses={analyses!r})"
    )
    a = redup[0]
    assert a.lemma == lemma
    assert a.feats.get("LEMMA") == lemma
    assert a.feats.get("REDUP") == "FULL"


def test_bundok_no_first_copy_o_raise() -> None:
    """The Phase 10.A ``redup_o_raise`` sandhi flag is per-root
    opt-in; ``bundok`` does NOT opt in (per the reviewer's
    canonical ``bundok-bundok``, not ``bunduk-bundok``).
    Confirms the joined surface is ``bundokbundok`` and the
    raised candidate ``bundukbundok`` is not indexed."""
    idx = _get_default()._index
    assert "bundokbundok" in idx.particles, (
        "expected productive 'bundokbundok' in particles index"
    )
    assert "bundukbundok" not in idx.particles, (
        "did NOT expect raised 'bundukbundok' — bundok does not "
        "opt into redup_o_raise (canonical surface is "
        "bundok-bundok per reviewer typology)"
    )


def test_pinto_no_first_copy_o_raise() -> None:
    """Same as bundok: ``pinto`` does NOT opt into
    ``redup_o_raise``. Canonical surface is ``pinto-pinto``,
    not ``pintu-pinto``."""
    idx = _get_default()._index
    assert "pintopinto" in idx.particles
    assert "pintupinto" not in idx.particles


# === Bare PLACE-N analyses unchanged ===================================


@pytest.mark.parametrize("citation", [
    "bahay", "pinto", "bayan", "bundok", "bukid",
])
def test_bare_place_n_unchanged(citation: str) -> None:
    """The bare PLACE-N citation continues to analyze as NOUN —
    the new ``place_redup_distr`` opt-in only adds the derived
    ADV reading; it must not shadow the underlying NOUN."""
    a = _get_default()
    nouns = a._index.nouns.get(citation, [])
    noun_readings = [r for r in nouns if r.pos == "NOUN"]
    assert len(noun_readings) >= 1, (
        f"expected ≥1 NOUN analysis for bare {citation!r}; got {nouns!r}"
    )


# === Opt-in discipline =================================================


@pytest.mark.parametrize("surface", [
    "kalyekalye",       # kalye "street" — no opt-in
    "kuwartokuwarto",   # kuwarto "room" — no opt-in
    "silidsilid",       # silid "room" — no opt-in
    "simbahansimbahan", # simbahan "church" — no opt-in
    "paaralanpaaralan", # paaralan "school" — no opt-in
    "lugarlugar",       # lugar "place" — no opt-in (reviewer
                        # caveat: "many roots would sound odd
                        # without contextual motivation")
])
def test_opt_in_is_required(surface: str) -> None:
    """The cell only fires on roots that explicitly carry
    ``affix_class: [place_redup_distr]``. Other PLACE-class nouns
    are not productively redup'd by default — per the external-
    reviewer caveat, productivity is semantically constrained,
    not unrestricted. Adding a new opt-in is a one-line lex edit."""
    idx = _get_default()._index
    analyses = idx.particles.get(surface, [])
    distr = [
        a for a in analyses
        if a.pos == "ADV"
        and a.feats.get("REDUP_SEM") == "DISTR"
    ]
    assert len(distr) == 0, (
        f"unexpected DISTR LOCATION ADV for {surface!r}: {distr!r}"
    )


# === REDUP_SEM disambiguates from 10.A =================================


def test_redup_sem_distinguishes_distr_from_freq() -> None:
    """The cross-cutting REDUP_SEM feat distinguishes the
    distributive-locative reading (10.B PLACE-N → DISTR) from
    the distributive-frequency reading (10.A TIME-N → FREQ).
    Both are ``REDUP=FULL`` derivations of the same shape
    (single redup_root op); REDUP_SEM is the discriminator."""
    idx = _get_default()._index
    bahay = idx.particles.get("bahaybahay", [])
    araw = idx.particles.get("arawaraw", [])

    bahay_distr = [a for a in bahay if a.feats.get("REDUP_SEM") == "DISTR"]
    bahay_freq  = [a for a in bahay if a.feats.get("REDUP_SEM") == "FREQ"]
    araw_distr  = [a for a in araw  if a.feats.get("REDUP_SEM") == "DISTR"]
    araw_freq   = [a for a in araw  if a.feats.get("REDUP_SEM") == "FREQ"]

    assert len(bahay_distr) == 1
    assert len(bahay_freq) == 0
    assert len(araw_distr) == 0
    assert len(araw_freq) == 1

    # Both share REDUP=FULL (morphological structure) but differ
    # in REDUP_SEM (semantic class).
    assert bahay_distr[0].feats.get("REDUP") == "FULL"
    assert araw_freq[0].feats.get("REDUP") == "FULL"


# === Regression flip: redup_intens_adj retrofitted by Phase 10.E.1 =====


def test_redup_intens_adj_retrofitted_phase10e1() -> None:
    """Phase 10.E.1 retrofits the Phase 5n.C.3 Commit 7
    ``redup_intens_adj`` cell (``magandaganda`` "rather beautiful")
    with the cross-cutting ``REDUP=FULL`` + ``REDUP_SEM=ATTEN``
    feats. ATTEN, not INTENS: the ma-X-X form is moderate
    ("fairly / tolerably X") per the informant ruling 2026-05-25 —
    genuine intensification is the linker form (``mabait na mabait``,
    Phase 10.E.2). The legacy ``INTENS=MILD`` feat is retained.
    (This guard formerly asserted the retrofit was deferred past
    Phase 10.B; 10.E.1 flips it.)"""
    idx = _get_default()._index
    analyses = idx.adjectives.get("magandaganda", [])
    intens = [
        a for a in analyses
        if a.pos == "ADJ" and a.feats.get("INTENS") == "MILD"
    ]
    assert len(intens) >= 1
    assert intens[0].feats.get("REDUP") == "FULL"
    assert intens[0].feats.get("REDUP_SEM") == "ATTEN"
