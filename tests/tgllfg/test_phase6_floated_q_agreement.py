"""Phase 6.H Commit 2: floated-Q number agreement (§18 L33).

The Phase 4 §7.8 base float rule (``cfg/clitic.py:48-79``) and
the Phase 5f Commit 23 clause-initial dual-Q rules
(``cfg/clitic.py:90-181``) attach ``Q[DUAL=true]`` (``pareho`` /
``kapwa``) to NOM antecedents. Before Phase 6.H the rules
lacked any NUM agreement check between the DUAL Q and its
antecedent SUBJ, so the SG-SUBJ + DUAL-Q surfaces overgenerated:

* ``*Kumain siya pareho.`` (SG SUBJ + DUAL Q): 1 → 0 parses
* ``*Pareho siyang kumain.`` (SG SUBJ + DUAL Q): the dual-Q
  reading goes from 1 to 0; the predicative-ADJ polysemy
  (``pareho`` as equative-identity ADJ from
  ``adjectives.yaml``) survives. Filter on the dual-Q reading
  via the ``ADJ`` set membership.

The fix:

* The base float rule splits into two variants: bare-Q (no DUAL)
  and ``Q[DUAL=true]``. The DUAL variant adds
  ``(↑ SUBJ NUM) =c 'PL'``.
* Each of the 6 Phase 5f Commit 23 clause-initial rules (3
  AV-arity frames × 2 linker variants) gains ``(↑ SUBJ NUM) =c
  'PL'``.

Non-DUAL Q's (``lahat`` / ``marami`` / ``konti`` etc.) compose
with SG and PL antecedents unchanged — the bare-Q rule has no
NUM constraint.
"""

from __future__ import annotations

import pytest

from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text


def _has_dual_q_reading(parses: list, q_lemma: str) -> bool:
    """Return True if any parse has a DUAL-Q with ``LEMMA == q_lemma``
    bound into the matrix's ADJ set (the float-rule / clause-initial
    Q-floated reading, distinct from the predicative-ADJ polysemy)."""
    for _ct, fs, _astr, _diags in parses:
        adj = fs.feats.get("ADJ")
        if not adj:
            continue
        for member in adj:
            if not isinstance(member, FStructure):
                continue
            if (
                member.feats.get("LEMMA") == q_lemma
                and member.feats.get("DUAL") is True
            ):
                return True
    return False


def _count_dual_q_parses(parses: list, q_lemma: str) -> int:
    """Count parses where the matrix's ADJ contains a DUAL-Q with the
    given lemma (the Q-floated reading)."""
    n = 0
    for _ct, fs, _astr, _diags in parses:
        adj = fs.feats.get("ADJ")
        if not adj:
            continue
        for member in adj:
            if not isinstance(member, FStructure):
                continue
            if (
                member.feats.get("LEMMA") == q_lemma
                and member.feats.get("DUAL") is True
            ):
                n += 1
                break
    return n


# === Float-rule variant (S → S Q[DUAL]) ================================


class TestFloatRuleDualAgreement:
    """The Phase 4 §7.8 base float rule's Q[DUAL=true] variant
    requires the matrix SUBJ to be PL."""

    @pytest.mark.parametrize("q_lemma", ["pareho", "kapwa"])
    def test_pl_subj_dual_q_parses(self, q_lemma: str) -> None:
        parses = parse_text(f"Kumain sila {q_lemma}.")
        assert _has_dual_q_reading(parses, q_lemma), (
            f"PL SUBJ + DUAL Q {q_lemma!r} should have the dual-Q "
            f"reading via the float rule"
        )

    @pytest.mark.parametrize("q_lemma", ["pareho", "kapwa"])
    def test_sg_subj_dual_q_zero_parses(self, q_lemma: str) -> None:
        parses = parse_text(f"Kumain siya {q_lemma}.")
        assert not _has_dual_q_reading(parses, q_lemma), (
            f"SG SUBJ + DUAL Q {q_lemma!r} should NOT have the "
            f"dual-Q reading (L33 agreement closure)"
        )

    def test_full_sentence_total_count(self) -> None:
        # Sanity: ``Kumain sila pareho.`` parses (1 via float rule);
        # ``Kumain siya pareho.`` zero-parses (the float-rule path
        # was the only one — no predicative-ADJ polysemy for this
        # surface because pareho is clause-final).
        assert len(parse_text("Kumain sila pareho.")) == 1
        assert len(parse_text("Kumain siya pareho.")) == 0


# === Clause-initial dual-Q rules =======================================


class TestClauseInitialDualAgreement:
    """The Phase 5f Commit 23 clause-initial dual-Q rules require the
    matrix SUBJ pronoun to be PL via ``(↑ SUBJ NUM) =c 'PL'``."""

    @pytest.mark.parametrize("q_lemma", ["pareho", "kapwa"])
    def test_pl_subj_clause_initial_parses(self, q_lemma: str) -> None:
        # AV intransitive: ``Pareho silang kumain.``
        parses = parse_text(f"{q_lemma.capitalize()} silang kumain.")
        assert _has_dual_q_reading(parses, q_lemma), (
            f"PL SUBJ + clause-initial DUAL Q {q_lemma!r} should "
            f"have the dual-Q reading"
        )

    @pytest.mark.parametrize("q_lemma", ["pareho", "kapwa"])
    def test_sg_subj_clause_initial_zero_dual_q(self, q_lemma: str) -> None:
        # AV intransitive with SG: ``*Pareho siyang kumain.``
        # The predicative-ADJ polysemy survives, but the dual-Q
        # reading must not.
        parses = parse_text(f"{q_lemma.capitalize()} siyang kumain.")
        assert not _has_dual_q_reading(parses, q_lemma), (
            f"SG SUBJ + clause-initial DUAL Q {q_lemma!r} should "
            f"NOT have the dual-Q reading (L33 closure)"
        )

    def test_av_transitive_pl(self) -> None:
        # ``Pareho silang kumain ng isda.``
        parses = parse_text("Pareho silang kumain ng isda.")
        assert _has_dual_q_reading(parses, "pareho")

    def test_av_transitive_sg_zero_dual_q(self) -> None:
        # ``*Pareho siyang kumain ng isda.`` — the AV-transitive
        # dual-Q rule must zero-parse for SG; predicative-ADJ
        # polysemy survives.
        parses = parse_text("Pareho siyang kumain ng isda.")
        assert not _has_dual_q_reading(parses, "pareho")

    def test_av_ditransitive_pl(self) -> None:
        # ``Pareho silang kumain ng isda sa palengke.``
        parses = parse_text("Pareho silang kumain ng isda sa palengke.")
        assert _has_dual_q_reading(parses, "pareho")

    def test_av_ditransitive_sg_zero_dual_q(self) -> None:
        parses = parse_text("Pareho siyang kumain ng isda sa palengke.")
        assert not _has_dual_q_reading(parses, "pareho")


# === Non-DUAL Q regression =============================================


class TestNonDualQUnaffected:
    """The bare-Q float-rule variant (no DUAL constraint) composes
    with SG and PL antecedents alike — non-DUAL Q's like ``lahat`` /
    ``marami`` / ``konti`` are unaffected by the L33 fix."""

    @pytest.mark.parametrize("pronoun", ["siya", "sila"])
    def test_lahat_floats_on_both_sg_and_pl(self, pronoun: str) -> None:
        parses = parse_text(f"Kumain {pronoun} lahat.")
        assert parses, f"lahat float should parse with {pronoun!r}"

    def test_lahat_floats_on_bata(self) -> None:
        # The Phase 4 §7.8 baseline example.
        parses = parse_text("Kumain ang bata lahat.")
        assert parses

    @pytest.mark.parametrize("q", ["lahat"])
    def test_dual_q_count_unaffected_for_lahat(self, q: str) -> None:
        # ``lahat`` is QUANT=ALL, not DUAL; never reads as dual-Q.
        parses = parse_text(f"Kumain sila {q}.")
        assert _count_dual_q_parses(parses, q) == 0


# === Parse-count regression ============================================


class TestParseCountStability:
    """Pinned regression on the dual-Q reading count. Pre-Phase-6.H:
    the SG variant produced 1 (float) / 3 (clause-initial) parses
    including the dual-Q reading. Post-Phase-6.H: 0 dual-Q-reading
    parses for SG; PL count unchanged."""

    def test_pl_float_kumain_dual_q_count(self) -> None:
        parses = parse_text("Kumain sila pareho.")
        assert _count_dual_q_parses(parses, "pareho") == 1

    def test_sg_float_kumain_dual_q_count(self) -> None:
        parses = parse_text("Kumain siya pareho.")
        assert _count_dual_q_parses(parses, "pareho") == 0

    def test_pl_clause_initial_dual_q_count_at_least_one(self) -> None:
        # Multiple paths through linker variants — assert at least 1.
        parses = parse_text("Pareho silang kumain.")
        assert _count_dual_q_parses(parses, "pareho") >= 1

    def test_sg_clause_initial_dual_q_count(self) -> None:
        parses = parse_text("Pareho siyang kumain.")
        assert _count_dual_q_parses(parses, "pareho") == 0
