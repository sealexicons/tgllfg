# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-8.3: NP-internal sa-PRON modifier gate relaxation.

Third implementation sub-PR in the post-8.[1-5] arc.

**Survey misdiagnosis correction** (second one in this arc): the
post-8 survey claimed `Iba ang katungkulan at ang pagkakakilala`
ZPF'd due to a missing two-`ang`-NP coord chart rule. That diagnosis
was wrong — the rule already existed at ``coordination.py:84-99``
(Phase 5k Commit 3: `NP[CASE=X, COORD=AND] → NP[CASE=X] PART[COORD=AND]
NP[CASE=X]` for X ∈ {NOM, GEN, DAT}). The probe showed that the
isolated form `Iba ang aklat at ang papel.` parses fine.

The **actual** gap surfaced by deeper probing: the NP-internal
sa-PP modifier rule (``nominal.py:1110-1120``, 9.X.c8) carried a
PRED existential gate on the modifier (``(↓2 PRED)``) that
blocked PRON-projected NP[DAT] modifiers. Pre-PR:

* ``Maganda ang aklat sa mesa.``       ✓ (sa-N modifier — PRED gate passes)
* ``Maganda ang aklat sa kanya.``      ✗ (sa-PRON modifier — PRED gate fails)
* ``Iba ang aklat at ang papel sa kanya.``   ✗ (NP-coord + sa-PRON modifier — same gate)

The gate's stated purpose was to block ``*ka kanino`` (PRON-head
+ PRON-modifier as NP). But the head-side gate ``(↓1 PRED)``
alone preserves that blocking effect (PRON-head ↓1 fails the
head gate regardless of ↓2). The modifier-side gate was
over-restrictive — it also blocked the legitimate ``[N-head +
PRON-modifier]`` pattern (``ang aklat sa kanya`` "the book for
him").

Fix: drop the ``(↓2 PRED)`` modifier gate in ``nominal.py``.

Audit-corpus reach (vs ``tmp/audit-baseline-post-8-2/``):

* **wave-1 PANAHON sent-10** (first wave-1 close of post-8.X arc):
  ``Ang ina naman ang bahala sa bahay at sa pag-aalaga ng mga bata.``
  (originally tagged Cluster J in the post-8 survey — different
  cluster than the gate-relaxation target, but the relaxation
  unblocks a parse path the chart was using).
* wave-2 rg-intermediate +3 (`Panay yata ang bisita ni Bernie sa
  inyo.` / `Panay ang tingin sa iyo ni Bernie.` / `Ano ang
  inihanda sa inyo?`).
* wave-3 so1972 +1 (`Siya ang pinakamatalinong tao sa kanila.`).
* wave-4 kroeger1991 +1 (`Itinago ng asawa ni Maria sa kaniya ang
  pera.`).

10 bucket-only PS-1 → PS-N shifts — expected: the relaxed rule
introduces an additional reading on sentences that already parsed
(e.g., ``Ibigay mo ang libro sa kanya.`` now admits both the
canonical "give the book to him" parse AND the "give the
book-for-him" NP-internal-modifier parse). Both readings are
linguistically grammatical per the rule's own comment.

**Unresolved transcription typo (not addressed in this PR)**:
the wave-1 ANG PAMILYA/sent-3 source text says `pagkakaklala`,
but the canonical Tagalog form is `pagkakakilala` (pag-CV-ka-X
NOM of `kilala`). With the canonical spelling, the sentence
``Dito ay iba ang kanyang katungkulan at ang pagkakakilala sa
kanya.`` parses cleanly post-PR. The source is in the user's
hand-transcribed ``rg81-excerpts.md`` — needs verification
against the R&G 1981 PDF before fixing the .txt + JSONL (per
the OCR-eyeball discipline). Routes to post-9 OCR cleanup or
a dedicated user-verified fix.
"""

from tgllfg.core.pipeline import parse_text


class TestNpInternalSaPron:
    """post-8.3: NP-internal sa-PRON modifier (the gate-relaxation
    target). All variants pre-PR ZPF; post-PR parse."""

    def test_iba_ang_aklat_sa_kanya(self) -> None:
        """``Iba ang aklat sa kanya.`` — bare ADJ-pred + N-head +
        sa-PRON modifier. Pre-PR ZPF."""
        parses = parse_text("Iba ang aklat sa kanya.", n_best=2)
        assert len(parses) >= 1

    def test_maganda_ang_aklat_sa_kanya(self) -> None:
        """``Maganda ang aklat sa kanya.`` — different ADJ, same
        pattern."""
        parses = parse_text("Maganda ang aklat sa kanya.", n_best=2)
        assert len(parses) >= 1

    def test_iba_np_coord_sa_kanya(self) -> None:
        """``Iba ang aklat at ang papel sa kanya.`` — two-ang-NP
        coord with sa-PRON modifier on the second conjunct (or
        on the coord NP as a whole). Pre-PR ZPF."""
        parses = parse_text("Iba ang aklat at ang papel sa kanya.", n_best=2)
        assert len(parses) >= 1

    def test_pamilya_sent3_canonical_spelling(self) -> None:
        """PAMILYA/sent-3 with the canonical ``pagkakakilala``
        spelling (the source text has ``pagkakaklala`` which is
        ``_UNK`` — likely transcription typo; the canonical-
        spelling version parses post-PR)."""
        parses = parse_text(
            "Dito ay iba ang kanyang katungkulan at ang pagkakakilala sa kanya.",
            n_best=2,
        )
        assert len(parses) >= 1


class TestPamilyaSent10:
    """post-8.3: PANAHON / ANG PAMILYA sent-10 — wave-1 closure
    side effect of the gate relaxation. Originally tagged Cluster
    J in the survey (NP-naman-NP equational + PP-PP coord
    post-predicate)."""

    def test_pamilya_sent10_closes(self) -> None:
        """``Ang ina naman ang bahala sa bahay at sa pag-aalaga
        ng mga bata.`` — first wave-1 close of the post-8.X arc."""
        parses = parse_text(
            "Ang ina naman ang bahala sa bahay at sa pag-aalaga ng mga bata.",
            n_best=2,
        )
        assert len(parses) >= 1


class TestAntiRegression:
    """post-8.3: the head-side ``(↓1 PRED)`` gate alone preserves
    the blocking effect on PRON-head + PRON-modifier
    ``*ka kanino`` over-generation. Plus existing sa-N modifier
    + V-frame paths preserved."""

    def test_pron_head_pron_modifier_still_blocked(self) -> None:
        """``Mahaba siya sa kanya.`` — PRON-head + sa-PRON-modifier
        as NP-internal coord must still ZPF. The head ``siya`` is
        PRON-projected (no PRED), so the ``(↓1 PRED)`` gate fails
        regardless of ↓2."""
        parses = parse_text("Mahaba siya sa kanya.", n_best=2)
        assert len(parses) == 0, (
            "PRON-head + sa-PRON-modifier (NP-internal) must remain "
            "blocked — only the modifier gate was dropped"
        )

    def test_sa_n_modifier_still_works(self) -> None:
        """``Maganda ang aklat sa mesa.`` — N-head + sa-N modifier,
        the pre-PR-working path (no regression from relaxation)."""
        parses = parse_text("Maganda ang aklat sa mesa.", n_best=2)
        assert len(parses) >= 1

    def test_v_predicate_sa_pron_still_works(self) -> None:
        """``Pumunta siya sa kanya.`` — V-predicate + sa-PRON
        adjunct (different chart path than NP-internal modifier).
        Pre-PR-working; should still work."""
        parses = parse_text("Pumunta siya sa kanya.", n_best=2)
        assert len(parses) >= 1

    def test_existing_two_ang_np_coord_preserved(self) -> None:
        """``Iba ang aklat at ang papel.`` — the original survey-
        claimed target (Cluster C two-ang-NP coord). Already
        worked pre-PR via ``coordination.py:84-99``; should
        continue to work."""
        parses = parse_text("Iba ang aklat at ang papel.", n_best=2)
        assert len(parses) >= 1

    def test_pp_fronted_sa_kanya_preserved(self) -> None:
        """``Sa kanya ay iba ang aklat.`` — PP-fronted-ay variant
        works via the post-7.x ay-fronting split (unaffected by
        the gate relaxation)."""
        parses = parse_text("Sa kanya ay iba ang aklat.", n_best=2)
        assert len(parses) >= 1
