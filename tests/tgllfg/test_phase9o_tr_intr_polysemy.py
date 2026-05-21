"""Phase 9.O B3.A + B3.B + newly-possible follow-ons.

**B3.A — TR/INTR polysemy lex-design pass.** Verb roots with both TR
and INTR (AV-absolutive) senses needed a way to encode both
argument shapes without losing the TR parse. Resolved via a new
``AV_ABSOL: true`` root-level feat in ``data/tgl/verbs.yaml``;
``_synthesize_verb_entries`` (replaces single-entry
``_synthesize_verb_entry``) emits *both* the TR ``<SUBJ, OBJ>``
and the INTR ``<SUBJ>``-only entries when the analysis is AV+TR
and the root carries ``AV_ABSOL: true``. The parser tries both
and picks whichever leads to a complete parse — TR for
``Tumitingin siya sa aklat.`` (with overt OBJ-locative), INTR
for ``Tumingin siya.`` (no overt OBJ). For non-AV voices (OV, DV,
IV, LF) the flag has no effect; only the canonical TR entry is
synthesized as before.

Closes the 8.I + 8.O carryovers (alala / pasok) plus the six 9.D
N-V zero-conversion pairs (laro / regalo / sakit / tanong /
tingin — ``tabi`` was already INTR-coded). Anti-deferral pin
flips: 8.I ``Nag-aalala si Minda.`` (now parses), 9.D
``TestVRootNoRegression`` parametrize extended to 6 absolutive
forms.

**B3.B — ``ma_an`` paradigm cell.** ``malimutan`` ("be-able-to-
forget") and other LF-NVOL forms of ``limot``-class roots were
unanalyzable because no ``ma_an`` paradigm cell existed. Added
4 cells: PFV (``na+root+an`` → ``nalimutan``), IPFV (``na+redup+
an`` → ``nalilimutan``), CTPL with redup (``ma+redup+an`` →
``malilimutan``), and bare CTPL without redup (``ma+root+an`` →
``malimutan``, used in subord/modal-XCOMP/hortative contexts).
The bare-CTPL cell parallels Phase 5n.A's bare OV ``kainin``
cell. ``limot``'s affix_class extended to include ``ma_an``.

**Newly-possible follow-ons** (per "no deferrals" directive):

* **``mang_retain`` bare CTPL cell** — added to ``paradigms.yaml``;
  produces ``mangyari`` (IMP/INF form of ``yari``-class roots).
  9.E deferral note ("``mangyari`` (IMP/INF) form is still missing
  — no IMP-aspect paradigm cell — deferred to 9.O / paradigm-
  cell-add work") closes here.
* **Bare ADJ ``kilala``** — added to ``adjectives.yaml`` with
  ``affix_class: []`` for the predicative use (``Kilala si Maria.``
  / ``Kilala ang dalaga.``). V root in ``verbs.yaml`` continues to
  generate inflected forms (``kinilala``, ``magkikilala``,
  ``nakakilala``); bare-form predicative is a coexisting ADJ
  reading. 8.Q ``test_real_oov_still_reported`` anti-deferral
  pin repins from ``kilala`` to ``kumbidado``.

Audit-corpus impact: full-corpus 666/5186 (12.84%) → 679/5186
(13.09%), **+13 absolute parses / +0.25pp**. Per wave: RC1990
93→94 (+1), RG-Int 176→186 (+10), RG-Conv 193→195 (+2). The
RG-Int +10 is mostly AV-absolutive uses of the named verbs
(tingin / laro / tanong / etc.) in dialog.
"""

from __future__ import annotations

import pytest


# ---- B3.A: TR/INTR polysemy via AV_ABSOL --------------------------------


class TestAvAbsolutiveBasic:
    """AV-absolutive uses of TR verbs now parse via the synth
    path's second (INTR-style) entry."""

    @pytest.mark.parametrize("sentence", [
        # 9.D N-V pairs (5 TR verbs; tabi was already INTR)
        "Tumingin siya.",            # tingin AV-PFV
        "Naglaro siya.",             # laro AV-PFV
        "Naglaro ang mga bata.",     # laro AV-PFV plural SUBJ
        "Nagtanong siya.",           # tanong AV-PFV
        "Sumakit ang ulo.",          # sakit AV-PFV (psych pred)
        # 8.I + 8.O carryovers
        "Nag-aalala si Minda.",      # alala AV-IPFV (8.I pin)
        "Pumasok siya.",             # pasok AV-PFV (8.O pin)
        "Pumasok siya sa kuwarto.",  # pasok AV + locative OBL
    ])
    def test_av_absolutive_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"AV-absolutive failed: {sentence!r}"


class TestAvTrStillParses:
    """Adding the AV_ABSOL flag must NOT regress TR parses with
    overt OBJ. The synth path emits both entries; the parser picks
    whichever fits."""

    @pytest.mark.parametrize("sentence", [
        # AV-TR with overt OBJ / locative-PP
        "Tumitingin siya sa aklat.",        # tingin AV-IPFV + locative
        "Naglalaro ang bata ng bola.",      # laro AV-IPFV + OBJ
        "Nagregalo siya ng aklat kay Maria.",  # regalo AV + OBJ + IO
        # OV-TR (AV_ABSOL flag has no effect)
        "Inalala ko ang mga bata.",         # alala OV
        "Naalala ko ito.",                  # alala NVOL-OV-PFV
    ])
    def test_tr_form_still_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"TR regression: {sentence!r}"


class TestSynthEntries:
    """``_synthesize_verb_entries`` (the multi-entry refactor)
    returns multiple LexicalEntry objects for the AV+TR+AV_ABSOL
    case; one for other cases."""

    def test_single_entry_for_intr(self) -> None:
        from tgllfg.core.common import MorphAnalysis
        from tgllfg.core.lexicon import _synthesize_verb_entries
        ma = MorphAnalysis(
            lemma="alis", pos="VERB",
            feats={"VOICE": "AV", "ASPECT": "PFV",
                   "MOOD": "IND", "TR": "INTR"},
        )
        entries = _synthesize_verb_entries(ma)
        assert len(entries) == 1
        assert "<SUBJ>" in entries[0].pred

    def test_single_entry_for_av_tr_without_absol(self) -> None:
        from tgllfg.core.common import MorphAnalysis
        from tgllfg.core.lexicon import _synthesize_verb_entries
        ma = MorphAnalysis(
            lemma="bili", pos="VERB",
            feats={"VOICE": "AV", "ASPECT": "PFV",
                   "MOOD": "IND", "TR": "TR"},
        )
        entries = _synthesize_verb_entries(ma)
        assert len(entries) == 1
        assert "<SUBJ, OBJ>" in entries[0].pred

    def test_two_entries_for_av_tr_with_absol(self) -> None:
        from tgllfg.core.common import MorphAnalysis
        from tgllfg.core.lexicon import _synthesize_verb_entries
        ma = MorphAnalysis(
            lemma="tingin", pos="VERB",
            feats={"VOICE": "AV", "ASPECT": "PFV",
                   "MOOD": "IND", "TR": "TR", "AV_ABSOL": True},
        )
        entries = _synthesize_verb_entries(ma)
        assert len(entries) == 2
        preds = sorted(e.pred for e in entries)
        # TR entry: <SUBJ, OBJ>; INTR entry: <SUBJ>
        assert preds == [
            "TINGIN <SUBJ, OBJ>",
            "TINGIN <SUBJ>",
        ]

    def test_two_entries_for_ov_tr_with_absol(self) -> None:
        """Phase 9.X.c36: OV+TR+AV_ABSOL also synthesizes an INTR
        variant (PATIENT → SUBJ) for the headless-RC ``ang
        inaani`` "the (thing) being harvested" construction.
        Parallel to the AV path (9.O B3.A) and DV path (9.V.2)."""
        from tgllfg.core.common import MorphAnalysis
        from tgllfg.core.lexicon import _synthesize_verb_entries
        ma = MorphAnalysis(
            lemma="ani", pos="VERB",
            feats={"VOICE": "OV", "ASPECT": "PFV",
                   "MOOD": "IND", "TR": "TR", "AV_ABSOL": True},
        )
        entries = _synthesize_verb_entries(ma)
        assert len(entries) == 2
        preds = sorted(e.pred for e in entries)
        # TR entry: <SUBJ, OBJ-AGENT>; INTR entry: <SUBJ>
        assert preds == [
            "ANI <SUBJ, OBJ-AGENT>",
            "ANI <SUBJ>",
        ]


# ---- B3.B: ma_an paradigm cell -----------------------------------------


class TestMaAnParadigm:
    """4 new ma_an cells generate the LF-NVOL surfaces for
    ``limot``-class roots."""

    @pytest.mark.parametrize("surface", [
        "nalimutan",     # PFV: na + root + an
        "nalilimutan",   # IPFV: na + redup + an
        "malilimutan",   # CTPL: ma + redup + an
        "malimutan",     # bare CTPL: ma + root + an
    ])
    def test_surface_generated(self, surface: str) -> None:
        from tgllfg.morph.analyzer import _get_default
        analyzer = _get_default()
        assert analyzer.is_known_surface(surface), (
            f"{surface} should be a generated surface post-9.O"
        )

    @pytest.mark.parametrize("sentence", [
        "Malimutan ko ito.",        # bare CTPL
        "Nalimutan ko ito.",        # PFV realis
        "Malilimutan ko ito.",      # CTPL with redup
    ])
    def test_ma_an_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"ma_an parse failed: {sentence!r}"


# ---- Follow-on: mang_retain bare CTPL ----------------------------------


class TestMangyariBareCtpl:
    """``mang_retain`` bare CTPL cell (no cv-redup) produces
    ``mangyari`` — closes 9.E's deferral."""

    def test_mangyari_surface_generated(self) -> None:
        from tgllfg.morph.analyzer import _get_default
        analyzer = _get_default()
        assert analyzer.is_known_surface("mangyari"), (
            "mangyari should be generated by mang_retain bare CTPL"
        )

    def test_nangyari_still_works(self) -> None:
        """PFV form (existing cell) preserved."""
        from tgllfg.morph.analyzer import _get_default
        analyzer = _get_default()
        assert analyzer.is_known_surface("nangyari")

    def test_mangyari_parses(self) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Mangyari ito.", n_best=2)
        assert len(parses) >= 1


# ---- Follow-on: bare ADJ kilala ----------------------------------------


class TestKilalaBareAdj:
    """Bare-ADJ ``kilala`` added to adjectives.yaml for predicative
    use. V root in verbs.yaml continues to generate inflected forms."""

    def test_kilala_known_surface(self) -> None:
        from tgllfg.morph.analyzer import _get_default
        analyzer = _get_default()
        assert analyzer.is_known_surface("kilala"), (
            "kilala should be analyzable post-9.O ADJ add"
        )

    @pytest.mark.parametrize("sentence", [
        "Kilala si Maria.",         # pure predicative
        "Kilala ang dalaga.",       # SUBJ pivot
        "Kilala ang Maria.",        # alt
    ])
    def test_predicative_use_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, f"kilala pred failed: {sentence!r}"

    def test_kinilala_inflected_still_parses(self) -> None:
        """V-root paradigm forms continue to route through the V
        entry (the ADJ bare-form coexists, doesn't override)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kinilala niya ako.", n_best=2)
        assert len(parses) >= 1


# ---- 9.O.3: STATIVE_PRED bare-ADJ + GEN-actor --------------------------


class TestStativePredAdj:
    """Phase 9.O.3: bare-ADJ entries flagged ``STATIVE_PRED: true``
    license a GEN-actor argument via the new
    ``S → ADJ[STATIVE_PRED] NP[CASE=GEN] NP[CASE=NOM]`` rule.
    The ADJ acts as a stative-passive participle (GEN agent +
    NOM patient pivot)."""

    @pytest.mark.parametrize("sentence", [
        # kilala (known by X)
        "Kilala ko si Maria.",
        "Kilala mo si Pedro.",
        "Kilala niya ang dalaga.",
        # mahal (loved by X) — polysemous with "expensive"
        "Mahal ko si Maria.",
        "Mahal niya ako.",
        "Mahal mo ba si Maria?",
    ])
    def test_stative_pred_with_gen_actor_parses(
        self, sentence: str
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, (
            f"STATIVE_PRED + GEN + NOM failed: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        # Pure predicative (1-arg) readings still parse for both ADJs.
        "Mahal ang aklat.",         # expensive (no GEN)
        "Kilala si Maria.",         # known (no GEN)
    ])
    def test_pure_predicative_still_parses(
        self, sentence: str
    ) -> None:
        """The 1-arg ADJ[PREDICATIVE] + NP[CASE=NOM] rule still
        fires on the same ADJ surfaces; STATIVE_PRED licenses the
        2-arg reading additively, not exclusively."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1

    def test_pred_carries_obj_agent(self) -> None:
        """The 2-arg parse's PRED is ``ADJ <SUBJ, OBJ-AGENT>``;
        the GEN-NP is bound to OBJ-AGENT, the NOM-NP to SUBJ."""
        from tgllfg.core.pipeline import parse_text_with_fragments
        r = parse_text_with_fragments(
            "Kilala ko si Maria.", n_best=1
        )
        assert r.parses
        _, fs, _, _ = r.parses[0]
        pred_str = str(fs.feats.get("PRED", ""))
        assert "<SUBJ, OBJ-AGENT>" in pred_str, (
            f"unexpected PRED: {pred_str}"
        )
        assert "OBJ-AGENT" in fs.feats
        assert "SUBJ" in fs.feats


# ---- 9.O.4: AV-NVOL absolutive ----------------------------------------


class TestAvNvolAbsolutive:
    """Phase 9.O.4: ``Naalala ko.`` (NVOL with implicit pivot).
    The ``ma-`` prefix produces VOICE=AV, MOOD=NVOL surfaces that
    semantically invert case (GEN actor / NOM patient). The
    absolutive use drops the patient entirely; the new grammar
    rule binds the GEN-NP to SUBJ in this context. Restricted to
    AV_ABSOL=true verbs + MOOD=NVOL."""

    @pytest.mark.parametrize("sentence", [
        "Naalala ko.",          # alala AV-NVOL-PFV
        "Naalala niya.",
        "Naalala nila.",
        "Nakita ko.",           # kita AV-NVOL-PFV
        "Nakita niya.",
        "Nakikita ko.",         # kita AV-NVOL-IPFV
    ])
    def test_av_nvol_absolutive_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, (
            f"AV-NVOL absolutive failed: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        # Canonical 2-arg AV-NVOL (GEN actor + NOM patient) still works
        "Naalala ko ito.",
        "Nakita ko ang aklat.",
        "Naalala niya ang aklat.",
    ])
    def test_two_arg_av_nvol_still_parses(self, sentence: str) -> None:
        """The 2-arg canonical AV-NVOL form continues to parse
        (the rule restriction to AV_ABSOL=true + NVOL only fires
        the new 1-arg rule when no NOM patient is present)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1

    @pytest.mark.parametrize("sentence", [
        # Canonical AV (non-NVOL) with GEN actor should still
        # fail — only NVOL admits the GEN-to-SUBJ mapping.
        "Tumingin ko.",            # tingin AV-PFV (not NVOL)
        "Tumakbo ko.",             # takbo AV-PFV (not NVOL)
    ])
    def test_canonical_av_with_gen_still_fails(
        self, sentence: str
    ) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) == 0, (
            f"AV (non-NVOL) with GEN should not parse: {sentence!r}"
        )


# ---- 9.O.5: mangyari polite-imperative wrap ----------------------------


class TestMangyariPoliteWrap:
    """Phase 9.O.5: ``mangyari`` polite-imperative wrap.
    ``Mangyaring + S`` lifts the embedded S to matrix level with
    a POLITE_MARKER flag. Only the bare-CTPL ``mangyari`` carries
    POLITE_MARKER (set on the 9.O ``mang_retain`` bare CTPL cell);
    other ``yari``-forms (``nangyari``, ``nangyayari``,
    ``mangyayari``) function as regular ``yari`` verbs."""

    @pytest.mark.parametrize("sentence", [
        "Mangyaring umalis kayo.",
        "Mangyaring kumain kayo.",
        "Mangyaring tumakbo siya.",
    ])
    def test_polite_imperative_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=2)
        assert len(parses) >= 1, (
            f"polite-imperative failed: {sentence!r}"
        )

    def test_polite_marker_lifted_to_matrix(self) -> None:
        """The wrap rule lifts the embedded S to matrix and adds
        POLITE_MARKER=true. PRED comes from the embedded clause."""
        from tgllfg.core.pipeline import parse_text_with_fragments
        r = parse_text_with_fragments(
            "Mangyaring umalis kayo.", n_best=1
        )
        assert r.parses
        _, fs, _, _ = r.parses[0]
        assert fs.feats.get("POLITE_MARKER") is True
        # PRED comes from the embedded V (umalis = alis-AV-PFV).
        pred_str = str(fs.feats.get("PRED", ""))
        assert "ALIS" in pred_str.upper()

    def test_nangyari_unaffected_by_polite_marker(self) -> None:
        """PFV ``nangyari`` (= "happened") is NOT polite-marked.
        POLITE_MARKER is set only on the bare-CTPL cell."""
        from tgllfg.core.pipeline import parse_text_with_fragments
        r = parse_text_with_fragments("Nangyari ito.", n_best=1)
        assert r.parses
        _, fs, _, _ = r.parses[0]
        assert not fs.feats.get("POLITE_MARKER")


# ---- Negative cases (still failing — documents the gap front) ----------


class TestStillFailing:
    """Document the construction-class gaps that 9.O does NOT
    close. Each is pinned with len==0 so future sub-PRs can flip
    when they land."""

    def test_kilala_with_gen_actor_closed_in_9o(self) -> None:
        """``Kilala ko si Maria.`` ("I know Maria.") — bare-ADJ-
        with-GEN-actor construction. Pre-9.O.3 this was deferred
        (pinned ``len == 0``). 9.O.3 closes via a new STATIVE_PRED
        feat on the ``kilala`` ADJ entry + a new grammar rule
        ``S → ADJ[STATIVE_PRED] NP[CASE=GEN] NP[CASE=NOM]``
        emitting PRED ``ADJ <SUBJ, OBJ-AGENT>``. The ADJ acts as
        a stative-passive participle, the GEN-NP is the implicit
        AGENT, the NOM-NP is the patient pivot/SUBJ. Also extended
        to ``mahal`` (love sense: ``Mahal ko si Maria.``)."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kilala ko si Maria.", n_best=2)
        assert len(parses) >= 1, (
            "Kilala ko si Maria. should parse via STATIVE_PRED rule"
        )

    def test_naalala_av_absolutive_closed_in_9o(self) -> None:
        """``Naalala ko.`` (no overt patient) — phase 9.O.4 closes
        via a new grammar rule ``S → V[VOICE=AV, MOOD=NVOL,
        AV_ABSOL=true] NP[CASE=GEN]`` that binds the GEN-clitic
        actor to SUBJ in absolutive context. ``naalala`` is the
        AV-NVOL form of ``alala`` (carrying AV_ABSOL=true from 9.O
        B3.A); the synth path's INTR variant supplies the 1-arg
        predicate. Same closure for ``Nakita ko.`` once ``kita``
        gets ``AV_ABSOL: true``."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Naalala ko.", n_best=2)
        assert len(parses) >= 1, (
            "Naalala ko. should parse via 9.O.4 AV-NVOL absolutive rule"
        )

    def test_mangyaring_polite_imperative_closed_in_9o(self) -> None:
        """``Mangyaring umalis kayo.`` ("Kindly leave.") —
        mangyari + linker -ng + embedded S construction. Phase
        9.O.5 closes via:
          - ``POLITE_MARKER: true`` feat on the bare-CTPL
            ``mang_retain`` cell (paradigms.yaml).
          - New CFG rule ``S → V[POLITE_MARKER=true] PART[LINK=NG]
            S`` in cfg/clause.py with full-lift equation
            ``(↑) = ↓3`` and ``(↑ POLITE_MARKER) = true``.
        The wrap is structurally a politeness-marker lift, not a
        control verb — ``mangyari`` doesn't have its own SUBJ;
        the embedded S's SUBJ stays put."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Mangyaring umalis kayo.", n_best=2)
        assert len(parses) >= 1, (
            "Mangyaring umalis kayo. should parse via 9.O.5 "
            "polite-imperative wrap rule"
        )
