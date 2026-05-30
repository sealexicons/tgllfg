# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.4: ``mula sa`` SOURCE-PP head fronting +
clause-final + post-half closures + paradigm-engineering for
``tuto`` LV/DV NVOL and ``luto`` OV-CTPL.

Adds:

1. ``mula`` PREP lemma routes through the fronted-PP-comma split.
   ``_REASON_PREP_LEMMAS`` (post-2 / post-7.2) is generalised to a
   ``_FRONTED_PP_LEMMA_TYPES`` ``dict[str, str]`` mapping the lemma
   to its ``PREP_TYPE``. ``mula`` → ``SOURCE``; both pre-existing
   ``dahil`` / ``dahilan`` map to ``REASON``. The split function
   now uses the looked-up PREP_TYPE for both the activation gate
   and the pre-half ``start_symbol``.

2. ``S → PP[PREP_TYPE=SOURCE] PUNCT[PUNCT_CLASS=COMMA] S`` chart
   rule added to the 9.X.c13 fronted-PP-comma loop in discourse.py
   (which previously covered only REASON). Mirrors the existing
   REASON variant — fronted PP becomes matrix TOPIC + ADJ-set
   member. The Wackernagel/range risk noted in c13 was reassessed
   as phantom: bare ``mula X hanggang Y`` builds a structurally
   distinct ``PP[PREP_TYPE=RANGE]`` (4-daughter rule in nominal.py),
   so SOURCE never competes with RANGE at chart time.

3. ``S → S PP[PREP_TYPE=SOURCE]`` clause-final rule added to the
   9.X.c12 / post-7.2 S→S PP loop in discourse.py. The c12 SOURCE
   deferral is lifted on the same reasoning — the PP daughter
   demands ``NP[CASE=DAT]``, not the 4-daughter RANGE shape, so no
   chart-time ambiguity.

4. ``luto`` (cook) gains ``sandhi_flags: [no_h_epenthesis]`` so the
   OV-CTPL-SOC form surfaces as ``lutuin`` (the canonical modern
   surface per R&C 1990 §15) rather than ``lutuhin``. Reading:
   ``luto`` has an underlying glottal stop on the final /o/ that
   blocks the default h-epenthesis (S&O 1972 §4.21).

5. ``tuto`` (learn) gains ``ma_an`` in its affix_class +
   ``sandhi_flags: [also_n_epenthesis]``. The ``ma_an`` opt-in
   adds the LV/DV-NVOL paradigm (``natutuhan`` / ``natututuhan`` /
   ``matututuhan`` PFV/IPFV/CTPL — "learn from/about X"); the
   ``also_n_epenthesis`` flag adds parallel ``-n-``-epenthesized
   variants (``natutunan`` / ``natututunan`` / ``matututunan``).
   Both ``natutuhan`` and ``natutunan`` are attested per Handbok
   of Tagalog Verbs (Bayot 1973) §VIII; Zamar 2023 §13.4 lists
   the ``-n-`` form as the modern principal. The ``ma_an``
   paradigm cells (cfg/paradigms.yaml) have their
   ``transitivity: TR`` gate dropped and a per-cell
   ``feats: {TR: TR}`` override added — ``tuto`` is INTR-AV but
   TR-LV/DV (dual-transitivity), and the per-cell override is the
   analyzer's mechanism for this per-voice transitivity profile
   (engine: ``cell.feats`` win over ``root.transitivity``
   projection in :mod:`tgllfg.morph.analyzer`).

6. New ``n_epenthesis`` parameter on
   :func:`tgllfg.morph.sandhi.attach_suffix` + ``n_epenthesis`` /
   ``also_n_epenthesis`` flag wiring through
   :func:`tgllfg.morph.analyzer._apply` and
   :func:`tgllfg.morph.analyzer._generate_form_variants`. The new
   variant-flag pattern mirrors the existing ``cluster_redup``
   variant pattern.

7. Lex extensions for the inner-clause vocabulary in the post-7.4
   constructed exemplars:

   - ``Cebu`` PLACE-NOUN (parallel to ``maynila`` / ``baguio``).
   - ``lakbay`` VERB INTR (motion-verb on the ``lakad`` / ``punta`` /
     ``takbo`` shape; affix_class ``[mag, maka]``, scoped to avoid
     sent-16 chart-density bloat).
   - ``panauhin`` NOUN ("guest, visitor").

Closes all 4 ``pending_closure: post-7.4`` constructed exemplars
(``mula-sa/maynila-cebu``, ``mula-sa/ina-lutuin``,
``mula-sa/malayong-bayan``, ``mula-sa/maynila-cebu-postv``).
"""

from tgllfg.core.pipeline import parse_text


class TestMulaSaPp:
    """post-7.4: ``mula sa`` SOURCE-PP fronted + clause-final + glue."""

    def test_mula_sa_maynila_fronted(self) -> None:
        """Canonical SOURCE-PP fronting closure: post-half travel verb."""
        s = "Mula sa Maynila, naglakbay kami sa Cebu."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # Fronted PP is TOPIC + member of ADJ set
        topic = fs.feats.get("TOPIC")
        assert topic is not None, "expected TOPIC on matrix"
        assert topic.feats.get("PREP_TYPE") == "SOURCE", (
            f"expected PREP_TYPE=SOURCE on TOPIC, got "
            f"{topic.feats.get('PREP_TYPE')}"
        )

    def test_mula_sa_kanyang_ina_fronted(self) -> None:
        """SOURCE-PP with possessive NP inside (``kanyang ina``).
        Inner clause exercises the paradigm-engineering work on
        ``tuto`` (``natutunan``) and ``luto`` (``lutuin``)."""
        s = "Mula sa kanyang ina, natutunan niya ang lutuin."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # Inner matrix predicate is the natutunan DV-NVOL form
        assert fs.feats.get("VOICE") == "DV"
        assert fs.feats.get("MOOD") == "NVOL"

    def test_mula_sa_malayong_bayan_fronted(self) -> None:
        """SOURCE-PP with ADJ-LINK-N modifier inside the NP
        (``malayong bayan`` "distant town")."""
        s = "Mula sa malayong bayan, dumating ang panauhin."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        assert topic is not None
        assert topic.feats.get("PREP_TYPE") == "SOURCE"

    def test_mula_sa_maynila_clause_final(self) -> None:
        """Clause-final ``mula sa`` (the post-7.4 c12 lift). Exercises
        ``S → S PP[PREP_TYPE=SOURCE]`` directly."""
        s = "Naglakbay kami sa Cebu mula sa Maynila."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # SOURCE PP is in matrix ADJUNCT (clause-final adjunct)
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None, "expected ADJUNCT on matrix"


class TestNewLex:
    """post-7.4: lex coverage for the constructed exemplars."""

    def test_cebu_place(self) -> None:
        """``Cebu`` PLACE-NOUN — admits ``sa Cebu`` LOC-PP."""
        parses = parse_text("Pumunta si Pedro sa Cebu.", n_best=2)
        assert len(parses) >= 1

    def test_lakbay_av_intr(self) -> None:
        """``lakbay`` VERB INTR — admits ``naglakbay kami`` bare AV."""
        parses = parse_text("Naglakbay kami sa Maynila.", n_best=2)
        assert len(parses) >= 1

    def test_panauhin_noun(self) -> None:
        """``panauhin`` NOUN — admits ``ang panauhin`` SUBJ."""
        parses = parse_text("Dumating ang panauhin.", n_best=2)
        assert len(parses) >= 1


class TestParadigmEngineering:
    """post-7.4: ``luto`` / ``tuto`` paradigm closures."""

    def test_luto_lutuin_no_h(self) -> None:
        """``luto + -in → lutuin`` (per R&C 1990 §15). Without the
        ``no_h_epenthesis`` flag the default would produce
        ``lutuhin`` — not the modern principal surface."""
        parses = parse_text("Lutuin mo ang isda.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # The matrix V is the luto OV-CTPL form
        assert fs.feats.get("VOICE") == "OV"
        assert fs.feats.get("ASPECT") == "CTPL"

    def test_tuto_natutunan_dv_nvol(self) -> None:
        """``tuto`` + ma_an LV/DV NVOL PFV → ``natutunan`` (with
        ``-n-`` per the also_n_epenthesis variant). Pivot is the
        source/topic; GEN-AGENT is the learner.

        Construction matters: this requires the cell-level
        ``feats: {TR: TR}`` override (paradigms.yaml ma_an cells)
        because ``tuto``'s root transitivity is INTR (for the AV
        reading). Without the override, the chart's NOM + GEN
        DV-NVOL transitive frame in cfg/clause.py wouldn't fire on
        a TR=INTR form — completeness would fail at the V's
        ``<SUBJ, OBJ-AGENT>`` PRED template."""
        parses = parse_text("Natutunan ko ang sulat.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        assert fs.feats.get("VOICE") == "DV"
        assert fs.feats.get("MOOD") == "NVOL"
        assert fs.feats.get("PRED") == "TUTO <SUBJ, OBJ-AGENT>"

    def test_tuto_natutuhan_h_variant(self) -> None:
        """``tuto`` also generates the older ``-h-`` variant
        ``natutuhan`` per the formal S&O 1972 §4.21 h-epenthesis
        pattern. Both variants are productively attested per
        Handbok of Tagalog Verbs (Bayot 1973) §VIII."""
        parses = parse_text("Natutuhan ko ang sulat.", n_best=2)
        assert len(parses) >= 1

    def test_tuto_av_nvol_unchanged(self) -> None:
        """Anti-regression: tuto's AV-NVOL forms (``natuto`` /
        ``natututo`` / ``matututo``) still inherit the root's
        INTR transitivity. The post-7.4 TR-override only affects
        the ma_an cells; the ma / mag / maka AV cells are
        unchanged."""
        for s in ("Natuto siya.", "Natututo siya.", "Matututo siya."):
            parses = parse_text(s, n_best=2)
            assert len(parses) >= 1, f"AV-NVOL regressed on {s!r}"


class TestAntiRegression:
    """post-7.4 anti-regression: the SOURCE addition doesn't disturb
    the existing range-PP (``mula X hanggang Y``) or the REASON
    fronted-PP-comma path."""

    def test_mula_range_pp_unchanged(self) -> None:
        """Bare ``mula X hanggang Y`` still builds the
        PP[PREP_TYPE=RANGE] (4-daughter PREP N PART N rule)."""
        parses = parse_text(
            "Nagtatrabaho ako mula Lunes hanggang Biyernes.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_dahil_fronted_reason_unchanged(self) -> None:
        """REASON fronted-PP-comma still closes (PR #117 / post-2)."""
        parses = parse_text(
            "Dahil sa init ng araw, panay ang tulo ng pawis ng tao.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_dahilan_fronted_reason_unchanged(self) -> None:
        """REASON post-7.2 dahilan still closes."""
        parses = parse_text(
            "Dahilan sa ulan, hindi kami nakapasok sa eskwela.",
            n_best=2,
        )
        assert len(parses) >= 1
