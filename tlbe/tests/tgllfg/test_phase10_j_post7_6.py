# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.6: ``tungkol sa`` TOPIC-PP head fronting +
clause-final + post-half closures.

Adds:

1. ``tungkol`` PREP lemma routes through the fronted-PP-comma
   split. ``_FRONTED_PP_LEMMA_TYPES`` (post-7.4) extended with
   ``tungkol → TOPIC``. Final dict: ``dahil`` / ``dahilan`` →
   REASON (post-2 / post-7.2); ``mula`` → SOURCE (post-7.4);
   ``tungo`` → GOAL (post-7.5); ``tungkol`` → TOPIC (post-7.6).

2. ``S → PP[PREP_TYPE=TOPIC] PUNCT[PUNCT_CLASS=COMMA] S`` chart
   rule added to the 9.X.c13 fronted-PP-comma loop in discourse.py
   (which previously covered REASON, SOURCE, GOAL). ``tungkol`` is
   unambiguously PREP[PREP_TYPE=TOPIC] (no competing NOUN reading).
   The clause-final ``S → S PP[PREP_TYPE=TOPIC]`` rule was already
   in place (added 9.X.c12 — the original PANAHON sent-39 ``...
   tungkol sa oras.`` closure target).

3. Lex extensions for the inner-clause vocabulary:

   - ``kuwento`` (and orthographic variant ``kwento``) VERB gains
     ``feats: {AV_ABSOL: true}`` so ``Masaya silang magkuwento.``
     "They (are) happy to tell stories" parses via the ADJ-LINK-
     V[INF] control construction without an overt OBJ. The
     ``kwento`` variant carries ``LEMMA: kuwento`` so the
     f-structure surfaces the canonical lemma regardless of which
     spelling was used.
   - ``nayon`` NOUN ("village, hamlet").
   - ``pasalamat`` NOUN ("gratitude, thanks").

Closes all 4 ``pending_closure: post-7.6`` constructed exemplars
(``tungkol-sa/oras-kamalayan``, ``tungkol-sa/pamilya-magkwento``,
``tungkol-sa/pista-pasalamat``, ``tungkol-sa/oras-kamalayan-postv``).
"""

from tgllfg.core.pipeline import parse_text


class TestTungkolSaPp:
    """post-7.6: ``tungkol sa`` TOPIC-PP fronted + clause-final."""

    def test_tungkol_sa_oras_fronted(self) -> None:
        """Canonical TOPIC-PP fronting — the post-7.6 audit
        exemplar #1. Inverse of the PANAHON sent-39 tail."""
        s = "Tungkol sa oras, iba ang kamalayan ng mga Pilipino."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        assert topic is not None, "expected TOPIC on matrix"
        assert topic.feats.get("PREP_TYPE") == "TOPIC", (
            f"expected PREP_TYPE=TOPIC, got "
            f"{topic.feats.get('PREP_TYPE')}"
        )

    def test_tungkol_sa_kanilang_pamilya_fronted(self) -> None:
        """TOPIC-PP with possessive-PRON inside (``kanilang
        pamilya``). Post-half ``masaya silang magkwento`` exercises
        the ADJ-LINK-V[INF] control + the kwento orthographic
        variant + AV_ABSOL feat on kuwento/kwento."""
        s = "Tungkol sa kanilang pamilya, masaya silang magkwento."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1

    def test_tungkol_sa_pista_fronted(self) -> None:
        """TOPIC-PP + post-half ``malaki ang pasalamat ng nayon``
        exercises the new pasalamat and nayon NOUNs."""
        s = "Tungkol sa pista, malaki ang pasalamat ng nayon."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        topic = fs.feats.get("TOPIC")
        assert topic is not None
        assert topic.feats.get("PREP_TYPE") == "TOPIC"

    def test_tungkol_sa_oras_clause_final(self) -> None:
        """Clause-final ``tungkol sa oras`` — exercises the
        pre-existing 9.X.c12 TOPIC clause-final S→S PP rule
        (PANAHON sent-39 tail shape)."""
        s = "Iba ang kamalayan ng mga Pilipino tungkol sa oras."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None


class TestNewLex:
    """post-7.6: lex coverage for the exemplar inner-clauses."""

    def test_kuwento_av_absol(self) -> None:
        """``kuwento`` gains AV_ABSOL=true so AV bare-OBJ parses."""
        parses = parse_text("Nagkuwento sila.", n_best=2)
        assert len(parses) >= 1

    def test_kwento_orthographic_variant(self) -> None:
        """``kwento`` is the colloquial spelling of ``kuwento``.
        ``magkwento`` / ``nagkwento`` etc. surface via the variant
        root's paradigm; the f-structure carries the canonical
        LEMMA=kuwento."""
        parses = parse_text("Nagkwento sila.", n_best=2)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # PRED uses the canonical lemma
        pred = fs.feats.get("PRED")
        assert pred is not None
        assert "KUWENTO" in str(pred) or "kuwento" in str(pred).lower(), (
            f"expected canonical kuwento in PRED, got {pred!r}"
        )

    def test_masaya_linker_v_inf_control(self) -> None:
        """ADJ-LINK-V[INF] control: ``Masaya silang magkuwento.``
        Requires AV_ABSOL on kuwento (so the V[INF] doesn't demand
        an explicit OBJ in the control complement)."""
        parses = parse_text("Masaya silang magkuwento.", n_best=2)
        assert len(parses) >= 1

    def test_nayon_noun(self) -> None:
        """``nayon`` NOUN."""
        parses = parse_text("Malaki ang nayon.", n_best=2)
        assert len(parses) >= 1

    def test_pasalamat_noun(self) -> None:
        """``pasalamat`` NOUN."""
        parses = parse_text("Malaki ang pasalamat.", n_best=2)
        assert len(parses) >= 1


class TestAntiRegression:
    """post-7.6 anti-regression: the TOPIC addition doesn't break
    existing PP-fronting / clause-final constructions."""

    def test_dahil_fronted_reason_unchanged(self) -> None:
        """REASON fronted-PP (post-2)."""
        parses = parse_text(
            "Dahil sa init ng araw, panay ang tulo ng pawis ng tao.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_mula_fronted_source_unchanged(self) -> None:
        """SOURCE fronted-PP (post-7.4)."""
        parses = parse_text(
            "Mula sa Maynila, naglakbay kami sa Cebu.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_tungo_fronted_goal_unchanged(self) -> None:
        """GOAL fronted-PP (post-7.5)."""
        parses = parse_text(
            "Tungo sa paaralan, naglakad ang mga bata.",
            n_best=2,
        )
        assert len(parses) >= 1

    def test_kuwento_with_obj_unchanged(self) -> None:
        """Anti-regression: ``Nagkuwento sila ng masayang kwento.``
        (with explicit OBJ) still parses — AV_ABSOL=true is the
        absolutive-licensing flag, not a constraint."""
        parses = parse_text("Nagkuwento sila ng kuwento.", n_best=2)
        assert len(parses) >= 1
