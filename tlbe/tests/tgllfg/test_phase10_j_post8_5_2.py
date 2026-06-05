# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.5.2: affix_class extensions on existing roots +
NEW ma-X-in disposition paradigm cell + V-at-V coord under ang.

Second sub-PR in the post-8.5.N series. Three lex/paradigm closures
plus two anti-deferral additions (one chart rule, one lex feat):

(a) ``pintas`` VERB gains ``ma_an`` → ``mapintasan`` (ma-X-an LV
    NVOL "to be criticized") lex's via existing Phase 5e cells.
    PAG-AARAL/sent-5 prerequisite.

(b) ``sunod`` VERB gains ``ma`` → ``nasusunod`` (ma-NVOL AV IPFV
    "is being followed/obeyed") via existing ma- AV-NVOL cells.
    PAMILYA/sent-7 prerequisite.

(c) NEW ``ma_X_in`` disposition paradigm cell in
    ``adj_paradigms.yaml`` + ``hiya`` ADJ opt-in +
    ``no_h_epenthesis`` sandhi flag. Produces ``mahiyain``
    "shy-tempered, easily-embarrassed" (PAG-AARAL/sent-3 target).
    New ``DISPOSITION`` feat in BINARY_FEATS registry (65 → 66).

(d) Anti-deferral × 1: ``pasya`` VERB gains ``AV_ABSOL: true``
    (parallel to post-8.1 ``sunod`` / ``kilala``); the implicit-
    OBJ decision verb works in narrative contexts
    (``Siya ang nagpapasya.`` "She is the one deciding").
    PAMILYA/sent-7 prerequisite.

(e) Anti-deferral × 2: NEW ``S_GAP → S_GAP PART[COORD=X] S_GAP``
    chart rule in ``cfg/coordination.py`` (X ∈ {AND, OR}). Admits
    the productive V-at-V coord under the headless-RC wrap (``ang
    nasusunod at nagpapasya`` "the one followed and deciding").
    Bindings: matrix inherits f-struct from first conjunct
    (``(↑) = ↓1``); second conjunct shares SUBJ with matrix; both
    join CONJUNCTS via ``↓3 ∈ (↑ CONJUNCTS)``. Parallel to the
    Phase 5g manner-style ADJ rule's f-structure inheritance
    pattern.

(f) Anti-deferral × 3: ``inom`` VERB gains ``AV_ABSOL: true``
    (parallel to ``pasya`` / ``sunod``). Surfaced by V-coord
    testing — ``inom`` (drink) freely drops the OBJ in informal
    contexts. Closes wave-2 rc1990 sent-900 (``Nagdala si Damian
    ng inumin.``) and wave-5 zamar2023 page-174/sent-2
    (``Nasaan ang mga inumin?``).

Audit signal (post-8.5.1 → post-8.5.2):

| Wave | Pre | Post | Δ |
| --- | --- | --- | --- |
| wave1-exemplars       | 99/123    | **102/123 (82.93%)** | **+3** |
| wave2-rc1990          | 215/1022  | 216/1022  | +1 |
| wave2-rg-intermediate | 459/1919  | 460/1919  | +1 |
| wave5-zamar2023       | 148/498   | 149/498   | +1 |
| **XWAVE**             | 1767/6015 | **1773/6015** | **+6** |

Net: 6 closures, 0 regressions, 5 bucket-only PS-1→PS-N shifts
(additional readings from the new lex/cell additions on
``Uminom`` / ``Umiinom`` family).

Wave-1 closures:

* PAG-AARAL/sent-3 — ``Ang nahihirapan ay mga taong mahiyain
  at mahina ang loob.``
* PAMILYA/sent-7 — ``Siya ang nasusunod at nagpapasya para sa
  pamilya.``
* PAMILYA/sent-9 — ``Kaya siya ang nagtratrabaho at kumikita ng
  pera.`` (V-coord rule + existing trabaho/kita lex)

Drop from original scope: ``tama`` adj_redup (survey misdiagnosis
#5 — ``tamang-tama`` already parses via the existing nominal.py:2728
``ADJ + LINK + PUNCT[HYPHEN] + ADJ`` doubled-ADJ rule; no
adj_redup opt-in needed).
"""

from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import _get_default


class TestPintasMaAn:
    """post-8.5.2 (a): ``pintas`` + ``ma_an`` → ``mapintasan``."""

    def test_mapintasan_is_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("mapintasan")

    def test_mapintasan_predicative(self) -> None:
        parses = parse_text("Mapintasan ang aklat.", n_best=1)
        assert len(parses) >= 1


class TestSunodMa:
    """post-8.5.2 (b): ``sunod`` + ``ma`` → ``nasusunod`` (PAMILYA
    sent-7 prerequisite)."""

    def test_nasusunod_is_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("nasusunod")

    def test_nasusunod_av_ipfv_nvol(self) -> None:
        analyzer = _get_default()
        forms = analyzer._index.verb_forms.get("nasusunod", [])
        target = [a for a in forms if a.lemma == "sunod"]
        assert target, "expected sunod-rooted nasusunod"
        assert target[0].feats.get("VOICE") == "AV"
        assert target[0].feats.get("ASPECT") == "IPFV"
        assert target[0].feats.get("MOOD") == "NVOL"


class TestMahiyainCell:
    """post-8.5.2 (c): NEW ``ma_X_in`` disposition cell +
    ``hiya`` opt-in + ``no_h_epenthesis`` flag."""

    def test_mahiyain_is_known(self) -> None:
        analyzer = _get_default()
        assert analyzer.is_known_surface("mahiyain")

    def test_mahiyain_predicative(self) -> None:
        parses = parse_text("Mahiyain siya.", n_best=1)
        assert len(parses) >= 1

    def test_no_h_epenthesis_variant_not_produced(self) -> None:
        """``mahiyahin`` (the default ``-h-`` epenthesis form)
        should NOT be generated because ``hiya`` opts into
        ``sandhi_flags: [no_h_epenthesis]``."""
        analyzer = _get_default()
        assert not analyzer.is_known_surface("mahiyahin")

    def test_disposition_feat_in_binary_registry(self) -> None:
        """``DISPOSITION`` feat must be in BINARY_FEATS for the
        cell to compile (it's set as ``DISPOSITION: true`` on the
        derived ADJ surface)."""
        from tgllfg.core.feats import BINARY_FEATS
        assert "DISPOSITION" in BINARY_FEATS


class TestPasyaAvAbsol:
    """post-8.5.2 (d) anti-deferral: ``pasya`` ``AV_ABSOL=true``
    enables the bare AV+NOM-pivot reading."""

    def test_nagpapasya_with_nom_only(self) -> None:
        """``Nagpapasya siya.`` — AV-IPFV + NOM-pivot, no overt OBJ.
        Pre-PR this ZPF'd (TR required OBJ); AV_ABSOL admits it."""
        parses = parse_text("Nagpapasya siya.", n_best=1)
        assert len(parses) >= 1

    def test_headless_nagpapasya(self) -> None:
        """``Siya ang nagpapasya.`` — headless-RC pseudo-cleft."""
        parses = parse_text("Siya ang nagpapasya.", n_best=1)
        assert len(parses) >= 1


class TestVAtVCoordUnderAng:
    """post-8.5.2 (e) anti-deferral: NEW ``S_GAP → S_GAP PART[COORD]
    S_GAP`` chart rule admits V-at-V coord under the headless-RC
    wrap. Closes PAMILYA/sent-7 (the post-10 wave-2 OCR-exposure
    follow-on)."""

    def test_pamilya_sent7(self) -> None:
        """``Siya ang nasusunod at nagpapasya para sa pamilya.``"""
        parses = parse_text(
            "Siya ang nasusunod at nagpapasya para sa pamilya.",
            n_best=1,
        )
        assert len(parses) >= 1

    def test_pamilya_sent9(self) -> None:
        """``Kaya siya ang nagtratrabaho at kumikita ng pera.``
        — bonus closure: existing trabaho/kita lex + new V-coord
        rule together close PAMILYA/sent-9."""
        parses = parse_text(
            "Kaya siya ang nagtratrabaho at kumikita ng pera.",
            n_best=1,
        )
        assert len(parses) >= 1

    def test_basic_kumakain_at_kumakanta(self) -> None:
        """``Siya ang kumakain at kumakanta.`` — two AV-IPFV-INTR
        verbs under ang headless-RC."""
        parses = parse_text(
            "Siya ang kumakain at kumakanta.",
            n_best=1,
        )
        assert len(parses) >= 1


class TestInomAvAbsol:
    """post-8.5.2 (f) anti-deferral: ``inom`` ``AV_ABSOL=true``
    enables bare AV+NOM-pivot drink reading."""

    def test_siya_ang_uminom(self) -> None:
        parses = parse_text("Siya ang uminom.", n_best=1)
        assert len(parses) >= 1

    def test_kumakain_at_uminom(self) -> None:
        """``Siya ang kumakain at uminom.`` — TR + TR V-coord with
        both having AV_ABSOL semantics."""
        parses = parse_text(
            "Siya ang kumakain at uminom.",
            n_best=1,
        )
        assert len(parses) >= 1


class TestPagAaralSent3:
    """post-8.5.2: PAG-AARAL/sent-3 wave-1 closure (full
    sentence end-to-end)."""

    def test_full_sentence(self) -> None:
        parses = parse_text(
            "Ang nahihirapan ay mga taong mahiyain at mahina ang loob.",
            n_best=1,
        )
        assert len(parses) >= 1


class TestAntiRegression:
    """post-8.5.2 anti-regression — existing paradigms / chart
    rules unchanged."""

    def test_pintasan_existing(self) -> None:
        """``Pintasan natin ang aklat.`` — the existing
        ``an_oblig`` ``pintasan`` LV form (pre-post-8.5.2) still
        parses."""
        parses = parse_text("Pintasan natin ang aklat.", n_best=1)
        assert len(parses) >= 1

    def test_sumusunod_existing(self) -> None:
        """``Sumusunod siya.`` — the existing AV-IPFV ``sunod``
        form preserved by adding ``ma`` to affix_class."""
        parses = parse_text("Sumusunod siya.", n_best=1)
        assert len(parses) >= 1

    def test_mahiya_adj_preserved(self) -> None:
        """``mahiya`` ADJ from the existing ``ma_adj`` cell still
        analyzes — adding ``ma_X_in`` is additive."""
        analyzer = _get_default()
        adj = analyzer._index.adjectives.get("mahiya", [])
        assert any(a.lemma == "hiya" for a in adj)

    def test_tamang_tama_via_existing_rule(self) -> None:
        """``Tamang-tama ang oras.`` — closed by the existing Phase
        5h doubled-ADJ rule (nominal.py:2728), NOT by post-8.5.2.
        Confirms no adj_redup opt-in needed on ``tama`` (survey
        misdiagnosis #5 — drop from scope)."""
        parses = parse_text("Tamang-tama ang oras.", n_best=1)
        assert len(parses) >= 1

    def test_single_v_headless_rc_preserved(self) -> None:
        """``Siya ang kumakain.`` — single-V headless RC still
        parses (the existing ``S_GAP → V[VOICE=AV]`` path remains
        active alongside the new coord rule)."""
        parses = parse_text("Siya ang kumakain.", n_best=1)
        assert len(parses) >= 1
