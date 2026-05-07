"""Phase 5l Commit 5: counterfactual ``sana`` enclitic.

Roadmap §12.1 / plan-of-record §5.6, §6 Commit 5. ``sana`` is a
2P enclitic (NOT a subordinator) that marks the matrix S as
counterfactual / unrealized — ``Pumunta sana ako`` "I would
have gone".

Lex (Commit 1):

* ``data/tgl/particles.yaml``: ``PART[is_clitic=true,
  CLITIC_CLASS=2P, COUNTERFACTUAL="YES", LEMMA=sana]`` (this
  commit adds CLITIC_CLASS=2P).
* ``data/tgl/clitics.yaml``: priority 195 (between ``man`` 190
  and ``yata`` 200).

Grammar (this commit):

* ``cfg/clitic.py`` Rule A — generic 2P-clitic absorption:
  tightened with ``¬ (↓2 COUNTERFACTUAL)`` to prevent firing
  on sana (which would absorb without lifting COUNTERFACTUAL).
* ``cfg/clitic.py`` Rule C — counterfactual lift (NEW):
  ``S → S PART[CLITIC_CLASS=2P, COUNTERFACTUAL=YES]`` with
  ``(↑ COUNTERFACTUAL) = 'YES'`` literal lift. Mirrors Rule B
  (``ba`` Q_TYPE lift); same shape, different lifted feature.

Tests in this file pin:

1. ``COUNTERFACTUAL=YES`` lifts onto the matrix S.
2. ``sana`` lands in the matrix S's ADJ set (LEMMA visible).
3. The composition with negation, subord, and other 2P clitics
   yields the expected matrix-level COUNTERFACTUAL marking.

Spurious-ambiguity note: clitic-placement reordering can produce
multiple parse paths for the same sana sentence (e.g.,
``Hindi sana pumunta si Maria`` → 2 parses, both with CF=YES
and POLARITY=NEG on the matrix). Tests accept ``len(parses) >= 1``
and verify the FEATURES, not the count, since the alternative
parses are functionally equivalent.
"""

from __future__ import annotations

from tgllfg.core.pipeline import parse_text


# === Basic counterfactual lift =========================================


class TestSanaBasic:
    """``sana`` in a simple intransitive AV-PFV sentence lifts
    COUNTERFACTUAL=YES onto the matrix S."""

    def test_pumunta_sana(self) -> None:
        parses = parse_text("Pumunta sana ako.")
        assert len(parses) >= 1
        # At least one parse has matrix COUNTERFACTUAL=YES.
        assert any(
            fs.feats.get("COUNTERFACTUAL") == "YES"
            for _ct, fs, _astr, _diags in parses
        )

    def test_kumain_sana(self) -> None:
        parses = parse_text("Kumain sana si Maria.")
        assert len(parses) >= 1
        assert any(
            fs.feats.get("COUNTERFACTUAL") == "YES"
            for _ct, fs, _astr, _diags in parses
        )

    def test_tumakbo_sana(self) -> None:
        parses = parse_text("Tumakbo sana siya.")
        assert len(parses) >= 1
        assert any(
            fs.feats.get("COUNTERFACTUAL") == "YES"
            for _ct, fs, _astr, _diags in parses
        )


# === sana lands in ADJ set ============================================


class TestSanaInAdjSet:
    """The ``sana`` clitic's f-structure (carrying its LEMMA and
    CLITIC_CLASS) is a member of the matrix S's ``ADJ`` set,
    parallel to other 2P-clitic absorptions (Phase 4 §7.3)."""

    def test_sana_in_adj_with_lemma(self) -> None:
        parses = parse_text("Pumunta sana ako.")
        _ct, fs, _astr, _diags = parses[0]
        adj = fs.feats.get("ADJ")
        assert adj is not None
        sana_members = [
            a for a in adj if a.feats.get("LEMMA") == "sana"
        ]
        assert len(sana_members) == 1
        assert sana_members[0].feats.get("COUNTERFACTUAL") == "YES"
        assert sana_members[0].feats.get("CLITIC_CLASS") == "2P"


# === sana × negation =================================================


class TestSanaWithNegation:
    """``sana`` composes orthogonally with ``hindi`` negation —
    the matrix S carries both ``POLARITY=NEG`` (from hindi) and
    ``COUNTERFACTUAL=YES`` (from sana)."""

    def test_hindi_sana_negation_and_counterfactual(self) -> None:
        parses = parse_text("Hindi sana pumunta si Maria.")
        assert len(parses) >= 1
        # At least one parse has both feats on the matrix.
        good = [
            (fs.feats.get("POLARITY"), fs.feats.get("COUNTERFACTUAL"))
            for _ct, fs, _astr, _diags in parses
        ]
        assert any(
            pol == "NEG" and cf == "YES" for pol, cf in good
        )


# === No counterfactual leak ===========================================


class TestNoCFLeakWithoutSana:
    """A sentence without ``sana`` must NOT have
    ``COUNTERFACTUAL=YES`` on its matrix. Pin this against any
    future regression where the lift rule fires too liberally."""

    def test_no_sana_no_cf(self) -> None:
        parses = parse_text("Pumunta ako.")
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("COUNTERFACTUAL") is None

    def test_other_2p_clitic_no_cf(self) -> None:
        # ``rin`` (Phase 4 §7.3 enclitic — "also") is a 2P clitic
        # without COUNTERFACTUAL. Its sentence must not leak CF.
        parses = parse_text("Pumunta rin ako.")
        assert len(parses) >= 1
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("COUNTERFACTUAL") is None


# === Phase 5i Q_TYPE lift unaffected =================================


class TestBaQTypeLiftStillWorks:
    """Phase 5i Rule B (``ba`` Q_TYPE=YES_NO lift) must continue to
    fire — the new Rule C (sana CF lift) is a parallel rule, not a
    replacement. Pin the ba lift to guard against accidental
    regression in the multi-clitic absorption family."""

    def test_kumain_ka_ba_q_type(self) -> None:
        parses = parse_text("Kumain ka ba?")
        assert len(parses) >= 1
        # At least one parse has Q_TYPE=YES_NO on the matrix.
        assert any(
            fs.feats.get("Q_TYPE") == "YES_NO"
            for _ct, fs, _astr, _diags in parses
        )


# === sana + other 2P clitic in cluster ===============================


class TestSanaWithOther2PClitic:
    """``sana`` + ``rin`` ("also") — both are 2P enclitics; the
    cluster reorders by priority. ``rin`` priority 140; ``sana``
    priority 195. Both should be absorbed; matrix has CF=YES."""

    def test_sana_and_rin(self) -> None:
        # Surface: ``Pumunta rin sana ako`` — both clitics in
        # the cluster after V. Cluster ordering is rin(140) <
        # sana(195), so the canonical surface is rin first.
        parses = parse_text("Pumunta rin sana ako.")
        assert len(parses) >= 1
        # At least one parse has CF=YES on the matrix.
        assert any(
            fs.feats.get("COUNTERFACTUAL") == "YES"
            for _ct, fs, _astr, _diags in parses
        )


# === sana doesn't cross-fire on subord ================================


class TestSanaNotInterpretedAsSubord:
    """``sana`` has ``pos=PART`` and ``CLITIC_CLASS=2P`` but no
    ``COMP_TYPE``. The subord-clause builder rules
    (``SubordClause → PART[COMP_TYPE=X] S``) require COMP_TYPE
    to fire, so sana cannot be interpreted as a subordinator
    even structurally."""

    def test_sana_followed_by_s_not_subord(self) -> None:
        # ``Sana pumunta ako`` — sentence-initial sana would be
        # a subord-style structure if cross-fire were possible.
        # The current grammar may or may not accept this surface
        # (sentence-initial 2P clitic violates Wackernagel
        # convention); whatever it accepts must NOT produce a
        # COMP_TYPE-based subord parse.
        parses = parse_text("Sana pumunta ako.")
        for _ct, fs, _astr, _diags in parses:
            # No COND / CONC / TEMP / PURP / REAS adjunct from
            # treating sana as a subordinator.
            adjuncts = fs.feats.get("ADJUNCT") or []
            for adj in adjuncts:
                assert adj.feats.get("SUBORD_TYPE") is None
