"""Phase 5n.C Commit 7 — L81 distributive-Q topic.

Closes the syntactic side of §18 L81 (distributive coord readings).
The new rule in ``cfg/clause.py`` admits ``Bawat bata, kumain.``
"Each child ate" — a fronted universal-Q-NP topic separated by a
comma from an AV-intransitive verb — producing a parse with
``DISTRIB=YES`` on the matrix S to mark the distributive operator
scope. The topic-NP becomes the matrix ``SUBJ`` (filling the AV
verb's required argument).

The rule's daughter pattern is
``NP[CASE=NOM] PUNCT[PUNCT_CLASS=COMMA] V[VOICE=AV]`` with the
constraining equation ``(↓1 UNIV) =c 'YES'`` gating the topic to
universal-Q-headed NPs (``bawat`` / ``kada`` per Phase 5f Commit
20). Bare proper-name topics (``Si Maria, kumain.``) and non-
universal-Q topics (``Ang aklat, kumain.``) lack ``UNIV`` and
do not match.

Quantifier-scope semantics (the Glue derivation interpreting the
operator as universally distributive) stays Phase 6+ work
(``tgllfg-out-of-scope.md`` §5.5 L19); this commit closes the
syntactic side only.

Design appendix: ``docs/analysis-choices.md`` Phase 5n.C Commit 6.
Reference: Schachter & Otanes 1972 §10; Ramos & Bautista 1986
ch.16.
"""

from __future__ import annotations

import pytest

from tgllfg.core.pipeline import parse_text


# === Distributive scope marker on canonical bawat / kada topics ========


class TestDistributiveScopeMarker:
    """``Bawat bata, kumain.`` and similar bawat / kada-headed
    topic-NP fragments parse with ``DISTRIB=YES`` on the matrix S."""

    @pytest.mark.parametrize("sentence,verb_pred", [
        ("Bawat bata, kumain.",  "EAT <SUBJ>"),
        ("Bawat tao, kumain.",   "EAT <SUBJ>"),
        ("Bawat bata, tumakbo.", "TAKBO <SUBJ>"),
        ("Kada bata, kumain.",   "EAT <SUBJ>"),
        ("Kada tao, tumakbo.",   "TAKBO <SUBJ>"),
    ])
    def test_distrib_marker_on_matrix(
        self, sentence: str, verb_pred: str
    ) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1, (
            f"L81 distributive-Q topic should parse: {sentence!r}"
        )
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("DISTRIB") == "YES"
        assert fs.feats.get("PRED") == verb_pred
        # Topic-NP fills the verb's SUBJ slot.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") == "YES"
        assert subj.feats.get("CASE") == "NOM"


# === Non-universal topics rejected ====================================


class TestNonUniversalTopicRejected:
    """The L81 rule's ``(↓1 UNIV) =c 'YES'`` constraining equation
    rejects topics whose NP head is not universal-marked. Bare proper
    names, plain NOM-NPs (``ang aklat``), and other non-Q-headed NPs
    do not produce a parse via the L81 rule."""

    @pytest.mark.parametrize("sentence", [
        "Si Maria, kumain.",
        "Si Pedro, tumakbo.",
        "Ang aklat, kumain.",
        "Ang bata, kumain.",
    ])
    def test_non_universal_topic_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 0, (
            f"non-UNIV topic must not parse via L81 rule: {sentence!r}"
        )


# === Comma is structurally required ==================================


class TestCommaRequired:
    """The L81 rule's daughter pattern includes
    ``PUNCT[PUNCT_CLASS=COMMA]``. Without the comma, the rule does
    not fire — bawat-NP + V without comma must not produce a
    distributive-scope reading via this rule."""

    @pytest.mark.parametrize("sentence", [
        "Bawat bata kumain.",
        "Bawat tao tumakbo.",
        "Kada bata kumain.",
    ])
    def test_no_comma_zero_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        # The bawat-NP-without-comma surface might not parse at all
        # in the existing grammar, OR might parse via some other path
        # that doesn't carry DISTRIB=YES. The L81 rule specifically
        # must not fire — confirm by checking no parse carries
        # DISTRIB=YES.
        for _ct, fs, _astr, _diags in parses:
            assert fs.feats.get("DISTRIB") != "YES"


# === Coexistence: ay-fronting unaffected ==============================


class TestAyFrontingUnaffected:
    """The existing Phase 4 §7.4 ay-fronting rule continues to admit
    ``Bawat bata ay kumain.`` "Every child eats" without DISTRIB=YES
    — ay-fronting is general topicalization, not distributive-scope
    marking. The new L81 rule is a distinct comma+S construction;
    the two rules don't compete for ay-fronted surfaces (which
    have ay, not comma)."""

    @pytest.mark.parametrize("sentence", [
        "Bawat bata ay kumain.",
        "Kada bata ay kumain.",
    ])
    def test_ay_fronting_no_distrib_marker(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # ay-fronted bawat-NP parses; SUBJ has UNIV=YES from the
        # bawat-NP, but the matrix has NO DISTRIB=YES because the
        # comma+S rule is the only DISTRIB-marker producer.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") == "YES"
        assert fs.feats.get("DISTRIB") is None


# === Coexistence: canonical V-S unaffected ============================


class TestCanonicalVSUnaffected:
    """The canonical V-S rule (Phase 4 §7.1) continues to admit
    ``Kumain ang bawat bata.`` — the universal-Q-NP serves as a
    post-V SUBJ via ang-marking. No DISTRIB=YES on the matrix
    because the L81 comma+S rule doesn't fire (no comma daughter)."""

    @pytest.mark.parametrize("sentence", [
        "Kumain ang bawat bata.",
        "Tumakbo ang bawat bata.",
    ])
    def test_canonical_v_s_no_distrib(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Canonical V-S parse; SUBJ is the bawat-NP, but matrix
        # carries no DISTRIB feat.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        assert subj.feats.get("UNIV") == "YES"
        assert fs.feats.get("DISTRIB") is None


# === Disambiguation from L83 fragment-NP-coord =======================


class TestL83Disambiguation:
    """The L83 fragment-NP-coord rule (Phase 5n.C Commit 5) and the
    new L81 distributive-Q rule are structurally distinct: L83's
    daughter is a single ``NP[COORD=BUT_NOT]``; L81's is
    ``NP + COMMA + V``. Different daughter counts; no rule
    competition. Verify the L83 surface still produces a fragment
    parse with no DISTRIB marker."""

    def test_l83_fragment_no_distrib(self) -> None:
        parses = parse_text("Si Maria, hindi si Juan.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("CLAUSE_TYPE") == "FRAGMENT"
        assert fs.feats.get("DISTRIB") is None


# === Disambiguation from L78 wide-scope hindi ========================


class TestL78Disambiguation:
    """The L78 wide-scope-hindi rule (Phase 5n.C Commit 2) and the
    new L81 distributive-Q rule are structurally distinct: L78's
    daughter shape is ``PART[POLARITY=NEG] NP[COORD=AND/OR] V``;
    L81's is ``NP[UNIV=YES] COMMA V``. Different daughter
    categories. Verify L78 still produces NEG_SCOPE=WIDE."""

    def test_l78_wide_scope_no_distrib(self) -> None:
        parses = parse_text("Hindi si Maria at si Juan kumain.")
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        assert fs.feats.get("NEG_SCOPE") == "WIDE"
        assert fs.feats.get("DISTRIB") is None


# === Top-1 uniqueness =================================================


class TestNoAmbiguityBlowup:
    """The new L81 rule should produce exactly one parse for the
    canonical bawat / kada surfaces; no ambiguity blowup with
    existing rules."""

    @pytest.mark.parametrize("sentence", [
        "Bawat bata, kumain.",
        "Kada bata, kumain.",
    ])
    def test_canonical_unique_parse(self, sentence: str) -> None:
        parses = parse_text(sentence)
        assert len(parses) == 1
