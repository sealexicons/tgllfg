# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.3: ``alalaong baga`` REFORM discourse-marker.

Adds:

1. ``alalaong`` PART + ``baga`` PART (LEMMA-only entries in
   particles.yaml § (d) "Discourse connective heads — multi-word
   components"), parallel to ``gayon`` / ``ganon`` / ``bukod``.

2. Phrasal builder ``PART[DISCOURSE_POS=SENTENCE_INITIAL] → PART PART``
   in cfg/discourse.py for the ``alalaong + baga`` fixed idiom,
   with ``(↑ DISCOURSE) = 'REFORM'`` (reformulation marker).
   Mirrors the Phase 5m Commit 11 ``gayon din`` / ``ganon din``
   builders. The virtual PART then feeds the existing Phase 9.V.4b
   comma-variant rule ``S → PART[DISCOURSE_POS=SENTENCE_INITIAL]
   PUNCT[COMMA] S`` to yield the matrix.

3. ``masungit`` ADJ "grumpy" (ma_adj) for the post-comma half of
   the alalaong-1 exemplar.

4. Chart rule ``S → V[COPULA] NP[CASE=NOM] ADJ[PREDICATIVE]`` in
   cfg/clause.py for the Wackernagel-reordered shape of
   ``Naging ADJ PRON`` constructions. The canonical
   ``V[COPULA] ADJ[PREDICATIVE] NP[CASE=NOM]`` rule (line 1807)
   handles V-ADJ-NP order; Wackernagel reorders 2P PRON-clitics
   past the ADJ to second-position past the COPULA verb, so the
   chart actually sees the V-NP-ADJ shape. Without this companion
   rule ``Naging masungit siya.`` and parallels ZPF.

Closes 1 of 2 ``pending_closure: post-7.3`` constructed exemplars:

- ✓ ``alalaong-baga/masungit``  — ``Alalaong baga, naging masungit na siya.``
- ✗ ``alalaong-baga/marami-dapat-gawin`` — ``Alalaong baga, marami pa
  tayong dapat gawin.`` — DEFERRED to ``post-7.3.1``. The inner
  clause exposes an independent Q-existential-possessive + dapat-V-
  cluster construction-class gap that is beyond REFORM-marker scope:
  ``Marami tayong dapat gawin.`` / ``Maraming dapat gawin.`` /
  ``Marami akong aklat.`` all ZPF independent of the alalaong-baga
  marker. The post-7.3.1 follow-on will tackle the Q-have-RC
  construction.
"""

from tgllfg.core.pipeline import parse_text


class TestAlalaongBagaReform:
    """post-7.3: ``alalaong baga`` REFORM discourse marker."""

    def test_alalaong_baga_masungit_closes(self) -> None:
        """The canonical alalaong-1 exemplar — closes cleanly via the
        REFORM phrasal builder + the new V[COPULA]+PRON+ADJ rule +
        the new ``masungit`` ADJ."""
        s = "Alalaong baga, naging masungit na siya."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # Matrix matches the BECOME-ADJ predicate (post-comma half)
        assert fs.feats.get("PRED") == "BECOME-ADJ <SUBJ>", (
            f"expected BECOME-ADJ PRED, got {fs.feats.get('PRED')!r}"
        )
        assert fs.feats.get("ADJ_LEMMA") == "sungit"
        # REFORM marker sits in ADJUNCT
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None and len(adj) >= 1, (
            "expected REFORM marker in ADJUNCT set"
        )
        discourse_marker = next(
            (a for a in adj if a.feats.get("DISCOURSE") == "REFORM"),
            None,
        )
        assert discourse_marker is not None, (
            f"no REFORM marker in ADJUNCT; saw {list(adj)}"
        )
        assert discourse_marker.feats.get("LEMMA") == "alalaong_baga"
        assert discourse_marker.feats.get("DISCOURSE_POS") == (
            "SENTENCE_INITIAL"
        )

    def test_alalaong_baga_minimal(self) -> None:
        """Minimal REFORM + comma + simpler post-half (already-parsing
        inner clause) — isolates the marker from inner-clause work."""
        s = "Alalaong baga, mabait siya."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJUNCT")
        assert adj is not None
        types = {a.feats.get("DISCOURSE") for a in adj}
        assert "REFORM" in types


class TestNagingAdjPron:
    """post-7.3: ``S → V[COPULA] NP[CASE=NOM] ADJ[PREDICATIVE]`` rule
    for Wackernagel-reordered ``Naging ADJ PRON`` constructions.

    Before post-7.3, the canonical ``V[COPULA] ADJ NP[NOM]`` rule
    only fired for full NPs (``Naging mabait ang bata.``) because
    Wackernagel reorders 2P PRON-clitics past the ADJ to second
    position past the COPULA verb — leaving the chart with
    ``V[COPULA] PRON ADJ`` which the canonical rule didn't match.
    """

    def test_naging_adj_pron_basic(self) -> None:
        """Multiple known ADJ + NOM-PRON combinations close."""
        for s in (
            "Naging masungit siya.",
            "Naging mabait siya.",
            "Naging maganda siya.",
            "Naging masaya siya.",
            "Naging mayaman siya.",
        ):
            parses = parse_text(s, n_best=2)
            assert len(parses) >= 1, f"failed: {s!r}"

    def test_naging_adj_full_np_unchanged(self) -> None:
        """Anti-regression: the canonical V-ADJ-NP rule (full NP)
        continues to parse — the new rule is strictly additive."""
        for s in (
            "Naging mabait ang bata.",
            "Naging masaya ang bata.",
        ):
            parses = parse_text(s, n_best=2)
            assert len(parses) >= 1, f"V-ADJ-NP regressed: {s!r}"

    def test_naging_noun_pron_unchanged(self) -> None:
        """Anti-regression: V[COPULA] + N + PRON still parses (the
        canonical V-N-NP rule applies — Wackernagel doesn't reorder
        PRON past NOUN)."""
        for s in (
            "Naging tamad ito.",
            "Naging guro siya.",
            "Naging pagod siya.",
        ):
            parses = parse_text(s, n_best=2)
            assert len(parses) >= 1, f"V-N-PRON regressed: {s!r}"


class TestSungitAdj:
    """post-7.3 lex addition — ``sungit`` ROOT → ``masungit`` ADJ."""

    def test_masungit_predicate(self) -> None:
        """Bare ADJ-predicate."""
        parses = parse_text("Masungit siya.", n_best=2)
        assert len(parses) >= 1

    def test_masungit_in_naging(self) -> None:
        """Naging + masungit + PRON — exercises both the lex add and
        the new chart rule."""
        parses = parse_text("Naging masungit siya.", n_best=2)
        assert len(parses) >= 1


class TestDeferredInnerClause:
    """post-7.3.1 (PR #154) closed the alalaong-2 inner-clause
    construction class (Q-existential-possessive + dapat-V-cluster).
    The smoke test that previously asserted ZPF now asserts the
    closure — flipped from ``len(parses) == 0`` to ``len(parses) >= 1``.
    Retained as a regression guard.
    """

    def test_marami_q_have_rc_closes(self) -> None:
        """Q + PRON-LINK + dapat + V[OV] cluster closes via the
        post-7.3.1 ``S → Q PRON[CASE=NOM] PART[LINK=NG]
        V[CTRL_CLASS=MODAL] V[VOICE=OV]`` rule. Regression guard
        for that closure."""
        parses = parse_text("Marami pa tayong dapat gawin.", n_best=2)
        assert len(parses) >= 1, (
            "post-7.3.1 closure regressed — Q-existential-possessive "
            "+ dapat-V-cluster should parse"
        )
