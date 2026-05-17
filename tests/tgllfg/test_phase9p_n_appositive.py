"""Phase 9.P: NP-appositive proper-name attachment.

Closes Phase 8.I's ``test_n_appositive_proper_name`` pin (R&G
Intermediate sent-113 ``Hindi nakita ni Betty ang kaibigan
niyang si Flor.``).

S&O 1972 §3.16(c) "Personal noun as second component;
personal-noun marker" — the construction class shape:

    NP[CASE=X]  →  NP[CASE=X]  PART[LINK=N{A,G}]  NP[CASE=NOM]
        (↑) = ↓1
        ↓3 ∈ (↑ APP)
        (↓3 MARKER) =c 'SI'

where the first NP supplies head + outer case marker (``ang`` /
``ng`` / ``sa``), the linker glues, and the third NP is a
``si``-personal-name-marked nominal that sits in the head NP's
``APP`` set. The outer case marker on the head NP determines the
construction's role in the matrix clause, per S&O.

Audit-corpus closures (R&G Intermediate):

* ``Hindi nakita ni Betty ang kaibigan niyang si Flor.`` (8.I pin)
* ``Rudy, ito ang kapatid kong si Kathy.``  (lex-blocked on
  ``Rudy``/``Kathy`` post-9.P — the construction parses with
  lex'd substitutes; see ``test_kapatid_kong_si_pedro_dem``)

Wider construction class covered:

* Predicate-NP appositive (``Iyon ang kapatid kong si Pedro.``)
* Bare appositive without possessor (``Iyon ang kaibigang si Maria.``)
* OBJ-position appositive
* GEN-position appositive
* DAT-position appositive
* Plural-head appositive (``ang mga kaibigan kong si Maria.``)
"""

from __future__ import annotations

import pytest


# -----------------------------------------------------------
# Class A: the 8.I pin sentence and minor variants
# -----------------------------------------------------------

class TestPhase8iPinClosure:
    """The 8.I R&G Intermediate sent-113 pin and direct minor
    variants — confirm the NP-appositive rule fires in object
    position with a GEN-PRON possessor + linker."""

    @pytest.mark.parametrize("sentence", [
        "Hindi nakita ni Betty ang kaibigan niyang si Flor.",
        "Nakita ni Betty ang kaibigan niyang si Flor.",
        "Nakita ko ang kaibigan kong si Maria.",
        "Nakita ko ang kaibigan kong si Flor.",
        "Nakita ni Pedro ang kapatid kong si Maria.",
    ])
    def test_obj_appositive_parses(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, (
            f"8.I-shape OBJ appositive failed to parse: {sentence!r}"
        )


# -----------------------------------------------------------
# Class B: predicate-NP appositive (Iyon / Ito subject)
# -----------------------------------------------------------

class TestPredicateAppositive:
    """Predicate-position appositive with DEM-PRO subject.
    Matches the second audit-corpus example shape (``Ito ang
    kapatid kong si Kathy.``) using lex'd proper names."""

    @pytest.mark.parametrize("sentence", [
        "Ito ang kapatid kong si Pedro.",
        "Iyon ang kapatid kong si Pedro.",
        "Iyon ang kaibigan kong si Maria.",
        "Ito ang kaibigan kong si Maria.",
    ])
    def test_dem_subj_predicate_appositive(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class C: bare appositive (no possessor)
# -----------------------------------------------------------

class TestBareAppositive:
    """Appositive without an intervening possessor. The linker
    attaches directly to the head N."""

    @pytest.mark.parametrize("sentence", [
        "Iyon ang kaibigang si Maria.",
        "Kumain ang kaibigang si Flor.",
        "Pumunta ako sa kaibigang si Maria.",
    ])
    def test_bare_head_appositive(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class D: case-marker permutations (NOM / GEN / DAT head)
# -----------------------------------------------------------

class TestCaseMarkerPermutations:
    """The rule is case-parallel — fires whether the head NP is
    NOM (``ang``), GEN (``ng``), or DAT (``sa``)."""

    @pytest.mark.parametrize("sentence", [
        # NOM (ang) — already covered by Class A; one more here for
        # completeness:
        "Nakita ko ang kapatid kong si Pedro.",
        # GEN (ng) — appositive on the actor NP
        "Nakita ko ang aklat ng kaibigan kong si Maria.",
        # DAT (sa) — appositive on a directional/recipient
        "Pumunta ako sa kapatid kong si Pedro.",
        "Sumulat ako sa kaibigan kong si Maria.",
    ])
    def test_case_permutations(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class E: plural-head appositive (mga + N + linker + si)
# -----------------------------------------------------------

class TestPluralHeadAppositive:
    """Head NP carries ``mga`` plural marker; appositive attaches
    to the resulting NP. Composes with the Phase 7a.A mga rule."""

    @pytest.mark.parametrize("sentence", [
        "Nakita ko ang mga kaibigan kong si Maria.",
        "Nakita ko ang mga kapatid kong si Pedro.",
    ])
    def test_plural_head(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"no parse: {sentence!r}"


# -----------------------------------------------------------
# Class F: f-structure shape
# -----------------------------------------------------------

class TestAppositiveFstruct:
    """The appositive's f-structure attaches under the head NP's
    ``APP`` set; the head's PRED is the relational N, the appositive
    contributes the personal-name PRED via the ``si``-NP."""

    def test_app_set_populated(self) -> None:
        """The pivot NP (``ang kapatid kong si Maria``) gets parsed
        as SUBJ for this OV verb. Its f-structure carries LEMMA
        ``kapatid`` and an ``APP`` set whose single member is the
        si-marked appositive with LEMMA ``maria``."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Nakita ni Pedro ang kapatid kong si Maria.",
            n_best=3,
        )
        assert len(parses) >= 1
        _cnode, fstruct, *_ = parses[0]
        # The ang-marked NP is the pivot — under the OV mapping of
        # ``nakita`` it surfaces as SUBJ of the top f-structure.
        subj = fstruct.feats["SUBJ"]
        assert subj.feats.get("LEMMA") == "kapatid", (
            f"expected head LEMMA kapatid; got {subj.feats.get('LEMMA')!r} "
            f"with feats {list(subj.feats.keys())}"
        )
        app = subj.feats.get("APP")
        assert app is not None, (
            f"no APP set on SUBJ; subj.feats keys = {list(subj.feats.keys())}"
        )
        members = list(app)
        assert len(members) == 1, (
            f"expected single appositive; got {len(members)}"
        )
        appositive = members[0]
        assert appositive.feats.get("LEMMA") == "maria", (
            f"expected appositive LEMMA maria; "
            f"got {appositive.feats.get('LEMMA')!r}"
        )
        assert appositive.feats.get("MARKER") == "SI", (
            f"expected appositive MARKER=SI; "
            f"got {appositive.feats.get('MARKER')!r}"
        )


# -----------------------------------------------------------
# Class G: scope guards — the rule does not over-generate
# -----------------------------------------------------------

class TestRuleScopeGuards:
    """The appositive rule is gated on ``(↓3 MARKER) =c 'SI'`` so it
    only fires when the 3rd daughter is a personal-name NP. Verify
    other linker contexts still parse correctly (no spurious
    appositive readings absorbing them)."""

    @pytest.mark.parametrize("sentence", [
        # ADJ-modified NP — pre-existing path, unrelated to appositive:
        "Magandang aklat ito.",
        # NP-possessive without appositive — pre-existing path:
        "Iyon ang kapatid ko.",
        # RC on an NP — pre-existing path; the new rule's 3rd
        # daughter is NP, not S_GAP, so no shadowing:
        "Kumain ang batang nakita ko.",
        # Simple OV with si-PROP as SUBJ — no linker, so no
        # appositive rule firing:
        "Nakita ni Pedro si Maria.",
        # Cardinal-modified NP (Phase 5f Commit 1) — head is a
        # cardinal NP; appositive rule's MARKER=SI guard rejects
        # the inner cardinal-NP gating on CARDINAL_VALUE, so no
        # spurious appositive reading:
        "Bumili ng tatlong aklat si Maria.",
    ])
    def test_no_regression(self, sentence: str) -> None:
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(sentence, n_best=3)
        assert len(parses) >= 1, f"regression on baseline: {sentence!r}"


# -----------------------------------------------------------
# Class H: out-of-scope (deferred to later sub-PRs)
# -----------------------------------------------------------

class TestPhase9pOutOfScope:
    """Construction-class variants NOT closed by 9.P. Each is
    blocked by an orthogonal lex/grammar gap; pin and flip when
    the relevant follow-on sub-PR closes it."""

    def test_adj_modified_proper_name(self) -> None:
        """S&O 1972 §3.16(c) top-form ``mabait na si Mr. Cruz``
        ("kind Mr. Cruz") — ADJ as first element with PROP as
        head. Different headedness from the N-head + PROP-mod
        case 9.P closes; needs a separate rule shape. Defer to
        a later sub-PR; pin asserts current zero-parse."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text(
            "Iyon ang mabait na si Pedro.",
            n_best=3,
        )
        assert len(parses) == 0, (
            "ADJ-modified appositive may have closed; review and "
            "flip if a follow-on landed."
        )

    def test_dem_pro_unmarked_proper_name(self) -> None:
        """S&O 1972 §3.16(d) ``Iyong Juan daw ang kapatid niya.``
        — DEM-PRO + unmarked-PROP (no ``si``). Distinct from
        9.P's si-marked appositive. Defer to a follow-on sub-PR."""
        from tgllfg.core.pipeline import parse_text
        parses = parse_text("Iyong Juan ang kapatid ko.", n_best=3)
        assert len(parses) == 0, (
            "DEM+unmarked-PROP may have closed; review and flip."
        )
