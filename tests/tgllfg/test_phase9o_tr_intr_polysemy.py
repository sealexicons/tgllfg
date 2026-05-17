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

    def test_single_entry_for_ov_tr_with_absol(self) -> None:
        """AV_ABSOL only triggers for AV voice; OV/DV/IV/LF emit
        the canonical TR entry."""
        from tgllfg.core.common import MorphAnalysis
        from tgllfg.core.lexicon import _synthesize_verb_entries
        ma = MorphAnalysis(
            lemma="tingin", pos="VERB",
            feats={"VOICE": "OV", "ASPECT": "PFV",
                   "MOOD": "IND", "TR": "TR", "AV_ABSOL": True},
        )
        entries = _synthesize_verb_entries(ma)
        assert len(entries) == 1
        assert "<SUBJ, OBJ-AGENT>" in entries[0].pred


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


# ---- Negative cases (still failing — documents the gap front) ----------


class TestStillFailing:
    """Document the construction-class gaps that 9.O does NOT
    close. Each is pinned with len==0 so future sub-PRs can flip
    when they land."""

    def test_kilala_with_gen_actor_still_fails(self) -> None:
        """``Kilala ko si Maria.`` ("I know Maria.") — bare-ADJ-
        with-GEN-actor is a separate "stative-predicative-with-
        actor" construction class. The ADJ entry doesn't carry an
        OBJ-AGENT slot; the GEN clitic has no host. Deferred to
        a predicative-V/ADJ-with-actor sub-PR."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Kilala ko si Maria.", n_best=2)
        assert len(parses) == 0

    def test_naalala_av_absolutive_still_fails(self) -> None:
        """``Naalala ko.`` (no overt patient) — ``naalala`` is
        OV-NVOL-PFV (not AV), so AV_ABSOL doesn't apply. The OV-
        absolutive ("remembered [it]" with implicit patient) would
        require a different design (OV-with-optional-patient).
        Deferred — 0 audit-corpus hits for this pattern."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Naalala ko.", n_best=2)
        assert len(parses) == 0

    def test_mangyaring_polite_imperative_still_fails(self) -> None:
        """``Mangyaring umalis kayo.`` ("Kindly leave.") — uses
        mangyari + linker -ng + embedded V (umalis) + SUBJ (kayo).
        Polite-imperative with embedded clause is a separate
        construction class; the bare mangyari surface is generated
        (verified by TestMangyariBareCtpl) but the linker + embedded
        clause doesn't compose."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Mangyaring umalis kayo.", n_best=2)
        assert len(parses) == 0
