# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-12.2: negative-existential pre-N modifier RC.

Sub-PR in the post-12.N stack (close all remaining wave-1 ZPFs).
Target: PAMILYA/sent-16 ``Kung minsa'y kapisan din ang wala pang
asawang kapatid ng ama o ina.`` ("Sometimes the unmarried sibling
of the father or mother also comes together.")

The full sentence does NOT close in this PR — it remains
``parse-timeout`` due to forest density on the combined
``Kung minsa'y`` + ``din`` + wala-pa modifier + GEN-OR-coord. But
the **underlying mechanism** (existential clause as pre/post-N
modifier with proper Wackernagel-domain handling for ``pa``) is
in place. Five core sub-cases close, including:

* ``Kapisan din ang wala pang asawang kapatid.`` (matrix ``din`` +
  embedded ``pa``)
* ``Kapisan din ang walang asawang kapatid ng ama o ina.`` (without
  ``pa``, with GEN-OR-coord — was failing before this PR)

PAMILYA/sent-16 itself parks as ``pending_closure: post-12.2.X``;
the chart-density issue is documented but distinct from the
structural mechanism shipped here.

## Two-layer architectural fix (user 2026-05-31 direction)

**Layer A** (`cfg/extraction.py`) — new N-modifier rules:

* Pre-N: ``N → S[CLAUSE_TYPE=EXISTENTIAL, POLARITY=NEG] PART[LINK]
  N`` — admits ``walang X-ng N`` and ``wala pang X-ng N`` as
  pre-N modifier.
* Post-N: ``N → N PART[LINK] S[CLAUSE_TYPE=EXISTENTIAL,
  POLARITY=NEG]`` — admits ``N na walang X`` post-mod.

Daughter category-pattern ``S[CLAUSE_TYPE=EXISTENTIAL,
POLARITY=NEG]`` gates at the **chart level**, not just at FU-solve
time. This avoids forest-density blow-up on positive-existential
sentences like ``Masasabing may dalang malas at suwerte ang
panahong ito.`` (PANAHON/sent-33). The earlier broad ``["S", LINK,
N]`` pattern would expand chart states for every S in the chart
and push borderline sentences over the 5000-tree iteration cap;
the narrowed pattern only expands when the daughter is a
negative-existential.

Matrix N tagged ``(↓3 EXIST_NEG_PREMOD) = true`` for downstream
NP-shell consumers to detect (anti-duplication via marker, per
user's "guards document chart pathology; budgets hide it"
principle).

**Layer B** (`cfg/clause.py`) — existential S category-feat LHS:

* The 3-daughter rule (``walang X``) and the new 4-daughter rule
  (``wala pang X``) project as ``S[CLAUSE_TYPE=EXISTENTIAL,
  POLARITY=NEG]`` (LHS carries category-feats so chart-level
  consumers see them).

**Layer C** (`cfg/clause.py`) — new 4-daughter S rule:

* ``S → PART[wala] PART[pa] PART[LINK=NG] N`` directly admits
  ``wala pang X`` as a complete S, with ``pa`` as ADJ
  aspect-particle. Required when the placement gate keeps ``pa``
  adjacent to ``wala`` (embedded NP context).

**Layer D** (`clitics/placement.py`) — narrow adjacency gate +
existential-as-inner-anchor:

* New helpers: ``_is_existential_head``,
  ``_looks_like_existential_nominal_complement``,
  ``_is_post_existential_pa``.
* ``_is_post_existential_pa`` adjacency gate added to ``adv_indices``
  filter. Keeps ``pa`` adjacent to its existential head when (a)
  preceded by DET upstream (NP-embedded context) AND (b) followed
  by LINK[NG] + N (nominal complement). Standalone ``Wala pang
  asawa.`` doesn't trigger the gate (no DET upstream).
* ``_enclosing_anchor_for_clitic`` Layer-1 fix: even under
  verbless matrix anchor, existential head can be an inner anchor
  for its aspect-clitic ``pa``. The pre-Phase-10.J.post-12.2
  short-circuit ("if matrix anchor is not VERB, return matrix
  anchor") was too strong.

## Trace evidence

The placement diagnosis is in ``tmp/trace_placement_walapa.py``.
For ``Kapisan din ang wala pang asawang kapatid.``:

* Without the gate: ``pa`` moves to clause-end (separated from
  ``wala`` by 4+ tokens), breaking embedded existential composition.
* With the gate: ``pa`` stays adjacent at position 3 (after
  ``wala`` at position 2), enabling the new 4-daughter S rule to
  compose ``[wala, pa, -ng, asawa]`` as S.

## Audit (post-12.1 → post-12.2)

* Wave 1 exemplars      : 108/123 → 108/123 (sent-17 preserved;
                          sent-16 from ZPF to parse-timeout —
                          chart finds candidate paths but cap-hit
                          on full surface)
* Wave 2 ramos1971      :  78/209 unchanged
* Wave 2 rc1990         : 219/1022 → 220/1022 (+1)
* Wave 2 rg-intermediate: 476/1919 unchanged
* Wave 3 rg-conversational: 322/666 unchanged
* Wave 3 so1972         : 314/1265 unchanged
* Wave 4 kroeger1991    :  58/215 unchanged
* Wave 5 zamar2023      : 151/498 unchanged
* Unattributed          : 145/145 unchanged
* XWAVE TOTAL           : 1871 → 1872 (+1)
* True regressions (text-keyed): 0
"""

from tgllfg.core.pipeline import parse_text


class TestEmbeddedWalaPangModifier:
    """Embedded negative-existential as pre/post-N modifier."""

    def test_maganda_wala_pang_modifier(self) -> None:
        """``Maganda ang wala pang asawang kapatid.`` — bare ADJ-pred
        with wala-pa modifier."""
        assert parse_text(
            "Maganda ang wala pang asawang kapatid.", n_best=1,
        )

    def test_kapisan_wala_pang_modifier(self) -> None:
        """``Kapisan ang wala pang asawang kapatid.`` — ka-N
        predicate with wala-pa modifier."""
        assert parse_text(
            "Kapisan ang wala pang asawang kapatid.", n_best=1,
        )

    def test_kapisan_din_wala_pang_modifier(self) -> None:
        """``Kapisan din ang wala pang asawang kapatid.`` — matrix
        ``din`` clitic + embedded ``pa`` clitic. The two clitics
        belong to different Wackernagel domains (din to matrix,
        pa to the embedded existential)."""
        assert parse_text(
            "Kapisan din ang wala pang asawang kapatid.", n_best=1,
        )

    def test_walang_pre_modifier(self) -> None:
        """``Maganda ang walang asawang kapatid.`` — walang (no
        pa) pre-N modifier."""
        assert parse_text(
            "Maganda ang walang asawang kapatid.", n_best=1,
        )

    def test_walang_post_modifier(self) -> None:
        """``Maganda ang kapatid na walang asawa.`` — post-N
        modifier order."""
        assert parse_text(
            "Maganda ang kapatid na walang asawa.", n_best=1,
        )


class TestGENPossessorOnModifiedN:
    """GEN possessor on a wala-modified N (the sent-16 sub-pattern)."""

    def test_walang_with_gen(self) -> None:
        """``Kapisan din ang walang asawang kapatid ng ama.``"""
        assert parse_text(
            "Kapisan din ang walang asawang kapatid ng ama.",
            n_best=1,
        )

    def test_walang_with_gen_or_coord(self) -> None:
        """``Kapisan din ang walang asawang kapatid ng ama o ina.``
        — GEN with OR-coord on possessor. This is the closest
        sub-case to PAMILYA/sent-16 that does close."""
        assert parse_text(
            "Kapisan din ang walang asawang kapatid ng ama o ina.",
            n_best=1,
        )

    def test_wala_pang_with_gen(self) -> None:
        """``Kapisan ang wala pang asawang kapatid ng ama.`` —
        wala-pa modifier with GEN (no din, no OR)."""
        assert parse_text(
            "Kapisan ang wala pang asawang kapatid ng ama.",
            n_best=1,
        )


class TestStandalonePreserved:
    """The placement gate is narrowly scoped — must NOT touch the
    standalone existential paths."""

    def test_wala_pang_asawa_standalone(self) -> None:
        """``Wala pang asawa.`` — standalone existential with pa
        clitic. The narrow adjacency gate doesn't fire (no DET
        upstream); pa moves to clause-end via standard reorder."""
        assert parse_text("Wala pang asawa.", n_best=1)

    def test_wala_pang_asawa_si_juan(self) -> None:
        """``Wala pang asawa si Juan.`` — standalone with overt
        NOM-NP."""
        assert parse_text("Wala pang asawa si Juan.", n_best=1)

    def test_walang_asawa_standalone(self) -> None:
        """``Walang asawa.`` — bare neg-existential."""
        assert parse_text("Walang asawa.", n_best=1)

    def test_walang_asawa_ang_kapatid(self) -> None:
        """``Walang asawa ang kapatid.`` — neg-existential
        possession ("the sibling has no spouse")."""
        assert parse_text("Walang asawa ang kapatid.", n_best=1)


class TestAntiRegression:
    """Phase 10.J.post-12.1 (sent-17) preserved + PANAHON
    positive-existential modifier preserved (sent-33)."""

    def test_pamilya_sent17_preserved(self) -> None:
        """Phase 10.J.post-12.1 PAMILYA/sent-17 still parses."""
        assert parse_text(
            "Kapag ganitong kumpleto ang pamilya'y tatlong "
            "salin-lahi ang nakatira sa iisang bahay.",
            n_best=1,
        )

    def test_panahon_sent33_positive_existential_preserved(self) -> None:
        """``Masasabing may dalang malas at suwerte ang panahong
        ito.`` — POSITIVE existential modifier (``may dalang``).
        Must NOT regress: the chart-level category-feat gating
        on the new modifier rule prevents it from over-exploring
        positive-existential sentences."""
        assert parse_text(
            "Masasabing may dalang malas at suwerte ang panahong ito.",
            n_best=1,
        )

    def test_pamilya_sent14_preserved(self) -> None:
        """Phase 10.J.post-8.5.5.1 PAMILYA/sent-14 still parses."""
        assert parse_text(
            "Kasama rin sa pag-aalala ng pamilya ang lolo at lola, "
            "ang mga kapatid ng ama at ina, lalo na't ang mga ito'y "
            "nakababata.",
            n_best=1,
        )
