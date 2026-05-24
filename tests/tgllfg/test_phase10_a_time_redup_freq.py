# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.A — TIME-N → FREQ-ADV bare X-X paradigm cell.

Promotes the previously-static ``arawaraw`` (LEMMA ``araw-araw``)
and ``tauntaon`` (LEMMA ``taun-taon``) particles to productive
derivation via the new ``time_redup_freq`` paradigm cell in
``data/tgl/paradigms.yaml`` (``base_pos: NOUN, pos: ADV``, single
``redup_root`` op, ``lemma_redup_hyphen: true``). Four TIME-N
roots opt in via ``affix_class: [time_redup_freq]`` in
``data/tgl/nouns.yaml``:

* ``araw`` "day, sun" — ``araw-araw`` "every day"
* ``gabi`` "night" — ``gabi-gabi`` "every night"
* ``oras`` "hour, time" — ``oras-oras`` "every hour"
* ``taon`` "year" — ``taun-taon`` "every year" (via
  ``sandhi_flags: [redup_o_raise]``, first-copy /o/→/u/ raising)

The cell sets ``ADV_TYPE=FREQUENCY`` and the new
``FREQ_VALUE=DISTRIBUTIVE`` value (distinct from existing OCCASIONAL
/ HABITUAL / HIGH / SOMETIMES) — the "every X" reading flows through
the existing Phase 5f S-rule ``S → S AdvP[FREQUENCY]`` without
grammar change.

Engineering scaffolding:

* New ``ParadigmCell.lemma_redup_hyphen`` field (Phase 10.A) opts
  the cell into canonical-hyphenated LEMMA, parallel to the
  always-on behavior in ``_index_particle_paradigms`` for
  particle-base ``redup_root`` cells (``paminsanminsan`` / LEMMA
  ``paminsan-minsan``). Without the opt-in the LEMMA would default
  to ``root.citation`` — conflicting with the established FREQ-ADV
  convention.
* New per-root ``redup_o_raise`` sandhi flag (Phase 10.A) extends
  the /o/→/u/ raising rule (S&O 1972 §4.21) to the first copy of
  a ``redup_root`` derivation. Used on ``taon`` so the canonical
  ``taun-taon`` surface (with first-copy raising) is generated.
  Opt-in (not default) so existing wh-PRON redup
  (``anoano`` / ``sinosino`` — both per the Phase 5n.C.3 Commit 6
  ``test_redup_root_no_o_raising_on_wh`` invariant) stays
  unchanged pending a separate canonical-form review (S&O lists
  ``anu-ano`` / ``sinu-sino`` as canonical; the current cell
  generates the unraised forms).
* The previously-static ``arawaraw`` (Phase 9.X.post-3) and
  ``tauntaon`` entries in ``data/tgl/particles.yaml`` are removed
  in favor of the productive derivation; ``manakanaka`` stays
  static (its base ``manaka`` is not a NOUN root in the lex).
"""

import pytest

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


# === Productive analyses are indexed =====================================


@pytest.mark.parametrize("surface,lemma", [
    ("arawaraw",  "araw-araw"),
    ("gabigabi",  "gabi-gabi"),
    ("orasoras",  "oras-oras"),
    ("tauntaon",  "taun-taon"),   # /o/→/u/ raising on first copy
])
def test_time_redup_freq_indexed_with_hyphenated_lemma(
    surface: str, lemma: str,
) -> None:
    """The productive cell indexes each TIME-N redup surface as ADV
    with the canonical hyphenated LEMMA, ADV_TYPE=FREQUENCY, and
    the new FREQ_VALUE=DISTRIBUTIVE."""
    analyses = _get_default()._index.particles.get(surface, [])
    redup = [
        a for a in analyses
        if a.pos == "ADV"
        and a.feats.get("ADV_TYPE") == "FREQUENCY"
        and a.feats.get("FREQ_VALUE") == "DISTRIBUTIVE"
    ]
    assert len(redup) == 1, (
        f"expected exactly one DISTRIBUTIVE FREQUENCY ADV analysis "
        f"for {surface!r}, got {len(redup)} (full analyses={analyses!r})"
    )
    a = redup[0]
    assert a.lemma == lemma
    assert a.feats.get("LEMMA") == lemma


def test_taon_o_raising_only_on_first_copy() -> None:
    """The ``redup_o_raise`` sandhi flag raises the first copy's
    stem-final /o/ to /u/ but leaves the second copy (the appended
    ``root.citation``) unchanged. Confirms the joined surface is
    ``tauntaon`` (not ``taontaon`` and not ``tauntaun``)."""
    idx = _get_default()._index
    assert "tauntaon" in idx.particles, (
        "expected productive 'tauntaon' (raised first copy + "
        "unraised second copy) in particles index"
    )
    assert "taontaon" not in idx.particles, (
        "did NOT expect unraised 'taontaon' — the redup_o_raise "
        "flag on taon should rewrite the first copy"
    )
    assert "tauntaun" not in idx.particles, (
        "did NOT expect double-raised 'tauntaun' — the second copy "
        "is the literal citation, not subject to the raising rule"
    )


# === Other TIME-N roots are NOT spuriously redup'd =======================


@pytest.mark.parametrize("surface", [
    "umagaumaga",     # umaga "morning" — no opt-in
    "hapunhapon",     # hapon "afternoon" — no opt-in (and no raising)
    "linggolinggo",   # linggo "week, Sunday" — no opt-in
    "buwanbuwan",     # buwan "moon, month" — no opt-in
    "sandalisandali", # sandali "moment" — no opt-in
    "minutominuto",   # minuto "minute" — no opt-in
])
def test_opt_in_is_required(surface: str) -> None:
    """The cell only fires on roots that explicitly carry
    ``affix_class: [time_redup_freq]``. Other TIME-class nouns are
    not productively redup'd by default — adding them is a one-line
    lex edit. Defensive: keeps the cell tight to audit-attested
    members (Phase 10 plan §2.2)."""
    idx = _get_default()._index
    # No productive FREQ-ADV analysis for opted-out roots.
    analyses = idx.particles.get(surface, [])
    distr = [
        a for a in analyses
        if a.pos == "ADV"
        and a.feats.get("FREQ_VALUE") == "DISTRIBUTIVE"
    ]
    assert len(distr) == 0, (
        f"unexpected DISTRIBUTIVE FREQUENCY ADV for {surface!r}: "
        f"{distr!r}"
    )


# === Hyphenated input flows through merge_hyphen_compounds ==============


@pytest.mark.parametrize("hyphenated,joined", [
    ("araw-araw",  "arawaraw"),
    ("gabi-gabi",  "gabigabi"),
    ("oras-oras",  "orasoras"),
    ("taun-taon",  "tauntaon"),
])
def test_hyphenated_input_parses_via_merge(
    hyphenated: str, joined: str,
) -> None:
    """Canonical hyphenated input (``araw-araw`` / ``taun-taon``
    etc.) tokenizes via the Phase 5f Commit 14
    ``merge_hyphen_compounds`` pre-pass to the joined surface
    that the productive cell generates."""
    sent = f"Kumakain ako {hyphenated}."
    parses = parse_text(sent)
    assert len(parses) >= 1, f"expected ≥1 parse for {sent!r}"
    _ct, fs, _astr, _diags = parses[0]
    adj = fs.feats.get("ADJUNCT") or []
    freqs = [
        m for m in adj
        if hasattr(m, "feats")
        and m.feats.get("ADV_TYPE") == "FREQUENCY"
        and m.feats.get("FREQ_VALUE") == "DISTRIBUTIVE"
    ]
    assert len(freqs) == 1, (
        f"expected exactly one DISTRIBUTIVE FREQUENCY adjunct in "
        f"matrix ADJUNCT for {sent!r}; got ADJUNCT={adj!r}"
    )
    assert freqs[0].feats.get("LEMMA") == hyphenated


# === End-to-end clausal use ============================================


def test_so1972_canonical_sentence() -> None:
    """``Nagluluto ng pagkain ang nanay araw-araw.`` "Mother cooks
    food every day." From Schachter & Otanes 1972 (Tagalog-
    Reference-Grammar, p.107). The clause-final ``araw-araw`` AdvP
    attaches as a matrix ADJUNCT via the existing Phase 5f S-rule
    ``S → S AdvP[FREQUENCY]``."""
    parses = parse_text("Nagluluto ng pagkain ang nanay araw-araw.")
    assert len(parses) >= 1
    _ct, fs, _astr, _diags = parses[0]
    adj = fs.feats.get("ADJUNCT") or []
    freqs = [
        m for m in adj
        if hasattr(m, "feats")
        and m.feats.get("LEMMA") == "araw-araw"
    ]
    assert len(freqs) == 1
    assert freqs[0].feats.get("ADV_TYPE") == "FREQUENCY"
    assert freqs[0].feats.get("FREQ_VALUE") == "DISTRIBUTIVE"


def test_audit_wave1_ang_manok_sent38() -> None:
    """Wave 1 audit fixture (ANG MANOK sent-38, rg81 transcription)
    ``Siguro mangingitlog ito ng dalawa araw-araw.`` ("Maybe it
    will lay two [eggs] every day.") — closed pre-Phase-10 via the
    static ``arawaraw`` entry; remains parseable via the
    productive ``time_redup_freq`` cell."""
    parses = parse_text(
        "Siguro mangingitlog ito ng dalawa araw-araw."
    )
    assert len(parses) >= 1, (
        "Phase 10.A must not regress the wave-1 ANG MANOK sent-38 "
        "closure originally landed in Phase 9.X.post-3"
    )


def test_audit_wave1_panahon_sent21() -> None:
    """Wave 1 audit fixture (PANAHON sent-21, rg81 transcription)
    ``Mula sampu hanggang dalawampung bagyo ang dumarating sa
    Pilipinas taun-taon.`` ("From ten to twenty typhoons arrive
    in the Philippines every year.") — exercises the
    ``redup_o_raise`` first-copy raising on ``taon``."""
    parses = parse_text(
        "Mula sampu hanggang dalawampung bagyo "
        "ang dumarating sa Pilipinas taun-taon."
    )
    assert len(parses) >= 1, (
        "Phase 10.A must not regress the wave-1 PANAHON sent-21 "
        "closure originally landed via the static tauntaon entry"
    )


# === Regression: redup_intens_adj (ADJ→ADJ, no opt-in) stays unchanged ===


def test_redup_intens_adj_lemma_unchanged() -> None:
    """The Phase 5n.C.3 Commit 7 ``redup_intens_adj`` cell does NOT
    opt into ``lemma_redup_hyphen``, so its derived intensives
    (``magandaganda`` etc.) keep ``lemma == root.citation`` (i.e.,
    ``ganda``, not ``maganda-ganda``). Guard against the Phase 10.A
    opt-in mechanism accidentally generalizing to existing cells."""
    idx = _get_default()._index
    analyses = idx.adjectives.get("magandaganda", [])
    intens = [
        a for a in analyses
        if a.pos == "ADJ" and a.feats.get("INTENS") == "MILD"
    ]
    assert len(intens) >= 1
    assert intens[0].lemma == "ganda", (
        f"expected redup_intens_adj to preserve root-citation LEMMA "
        f"(ganda); got {intens[0].lemma!r}. The Phase 10.A "
        f"lemma_redup_hyphen opt-in must NOT generalize to cells "
        f"that haven't explicitly opted in."
    )
