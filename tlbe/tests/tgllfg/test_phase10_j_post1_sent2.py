# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-1 PANAHON sent-2 close-out: three constructions
plus the colon-split + comma-at pipeline-level synthesis.

PANAHON sent-2 (R&G 1981): ``Dadalawa lamang ang masasabing tunay
na panahon dito: ang panahon ng tag-init mula Abril hanggang
Hunyo, at ang panahon ng tag-ulan mula Hulyo hanggang Oktubre.``

Three c-structure gaps were closed:

* (a) AV-NVOL-TR pre-N participial modifier (``masasabing N``).
* (b) PP[PREP_TYPE=RANGE] (``mula X hanggang Y``) + NP-NOM-attach.
* (c) Binary NP coord with leading comma (``X, at Y``) —
  synthesized at pipeline level to avoid chart-state count cost.

And one pipeline-level mechanism:

* (d) Colon-split fast path — splits the input on ``:`` and
  parses each half independently before the chart-level rule,
  bypassing the cross-colon span fan-out.
"""

import pytest

from tgllfg.cfg import Grammar
from tgllfg.core.pipeline import parse_text


class TestAvNvolParticipial:
    def test_masasabing_panahon_in_ang_np(self) -> None:
        """``Dadalawa lamang ang masasabing panahon.`` — the AV-NVOL
        potentive verb modifies the head N inside an ang-marked
        NP. Before the post-1 rule, the V's OBJ slot remained
        unfilled and completeness blocked the parse."""
        parses = parse_text("Dadalawa lamang ang masasabing panahon.")
        assert len(parses) >= 1
        # The matrix predicate is the cardinal "Dadalawa" (BE-CARDINAL).
        # The pivot SUBJ NP is "ang masasabing panahon".
        _ct, fs, _astr, _diags = parses[0]
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        # The head N is panahon (the modifier rule's `(↑) = ↓3`).
        # masasabi rides as a member of SUBJ's ADJ set.
        adj_set = subj.feats.get("ADJ")
        assert adj_set is not None, "AV-NVOL participial absent from ADJ set"
        # One of the ADJ members is a V f-structure with VOICE=AV
        # and SUBJ=PRO (agent absorbed by the rule).
        found = False
        for member in adj_set:
            if (member.feats.get("VOICE") == "AV"
                    and member.feats.get("MOOD") == "NVOL"):
                inner_subj = member.feats.get("SUBJ")
                if inner_subj is not None and inner_subj.feats.get("PRED") == "PRO":
                    found = True
                    break
        assert found, (
            "Did not find AV-NVOL participial with PRO-SUBJ in ADJ set"
        )

    def test_av_nvol_rule_exists_with_narrow_gate(self) -> None:
        """The new rule must gate on ``V[VOICE=AV, MOOD=NVOL, TR=TR]``
        and ``PART`` with a ``LINK`` constraint."""
        g = Grammar.load_default()
        # Look for the N-LHS rule with bracketed V[AV, NVOL, TR] first daughter.
        matches = [
            r for r in g.rules
            if r.lhs == "N"
            and len(r.rhs) == 3
            and r.rhs[0] == "V[VOICE=AV, MOOD=NVOL, TR=TR]"
            and r.rhs[1] == "PART"
            and r.rhs[2] == "N"
        ]
        assert len(matches) == 1, (
            f"Expected exactly one AV-NVOL pre-N participial rule, "
            f"found {len(matches)}"
        )


class TestRangePP:
    def test_mula_hanggang_in_clause(self) -> None:
        """``Maganda ang panahon mula Abril hanggang Hunyo.`` — the
        range PP attaches inside the NOM NP."""
        parses = parse_text(
            "Maganda ang panahon mula Abril hanggang Hunyo."
        )
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        # Walk down to find a PP with PREP_TYPE='RANGE' and both
        # endpoints carrying MONTH_VALUE.
        subj = fs.feats.get("SUBJ")
        assert subj is not None
        adj_set = subj.feats.get("ADJ")
        assert adj_set is not None
        range_pp = None
        for member in adj_set:
            if member.feats.get("PREP_TYPE") == "RANGE":
                range_pp = member
                break
        assert range_pp is not None, "No PP[PREP_TYPE=RANGE] in SUBJ's ADJ set"
        lo = range_pp.feats.get("RANGE_LO")
        hi = range_pp.feats.get("RANGE_HI")
        assert lo is not None and hi is not None
        # April = 4, June = 6 (from morph SEM_CLASS=MONTH entries —
        # the YAML loader stores MONTH_VALUE as a string, parallel to
        # CARDINAL_VALUE).
        assert lo.feats.get("MONTH_VALUE") == "4"
        assert hi.feats.get("MONTH_VALUE") == "6"

    def test_range_pp_requires_mula_hanggang_bracket(self) -> None:
        """The range PP rule should only fire when both ``mula`` and
        ``hanggang`` are present. A bare ``mula sa Abril`` PP should
        carry PREP_TYPE=SOURCE (inherited from the PREP entry), not
        RANGE."""
        # Use a sentence where mula but no hanggang appears as a
        # clause-final adjunct via ay-fronting.
        parses = parse_text("Mula sa Abril ay maganda ang panahon.")
        if not parses:
            pytest.skip("Test fixture sentence didn't parse; not the focus.")
        _ct, fs, _astr, _diags = parses[0]
        # The TOPIC (or some ADJUNCT) should be a PP with
        # PREP_TYPE=SOURCE, never RANGE.
        for key in ("TOPIC", "ADJUNCT"):
            v = fs.feats.get(key)
            if v is None:
                continue
            if hasattr(v, "feats"):
                assert v.feats.get("PREP_TYPE") != "RANGE", (
                    f"{key}'s PREP_TYPE leaked to RANGE without hanggang"
                )

    def test_range_pp_rules_registered(self) -> None:
        """Four PP[PREP_TYPE=RANGE] rules (one per SEM_CLASS in
        MONTH / TIME / DAY / YEAR) plus the NOM-only NP-attach rule
        gated on the same chart-side feat. Phase 10.J.post-1
        narrowed both ends — LHS advertises ``PREP_TYPE=RANGE`` so
        the attach rule's PP daughter bracket can match only the
        range-PP rule (not the generic ``PREP NP[DAT]`` or
        time-frame PPs), keeping chart-state count down.
        """
        g = Grammar.load_default()
        range_pp_rules = [
            r for r in g.rules
            if r.lhs == "PP[PREP_TYPE=RANGE]"
            and len(r.rhs) == 4
            and r.rhs[0] == "PREP"
            and r.rhs[2] == "PART"
        ]
        assert len(range_pp_rules) == 4

        nom_attach = [
            r for r in g.rules
            if r.lhs == "NP[CASE=NOM]"
            and r.rhs == ["NP[CASE=NOM]", "PP[PREP_TYPE=RANGE]"]
        ]
        assert len(nom_attach) == 1


class TestColonSplitFastPath:
    def test_panahon_sent2_closes(self) -> None:
        """PANAHON sent-2 — closes via the colon-split fast path
        because the chart-level colon-appositive rule's
        cross-colon span fan-out exceeds the default cap on this
        multi-PP-modified-NP-list sentence."""
        text = (
            "Dadalawa lamang ang masasabing tunay na panahon dito: "
            "ang panahon ng tag-init mula Abril hanggang Hunyo, "
            "at ang panahon ng tag-ulan mula Hulyo hanggang Oktubre."
        )
        parses = parse_text(text)
        assert len(parses) >= 1
        # The matrix carries the appositive in its APP set.
        _ct, fs, _astr, _diags = parses[0]
        app = fs.feats.get("APP")
        assert app is not None, "Colon appositive not glued to matrix"
        assert len(app) >= 1

    def test_panahon_sent9_closes(self) -> None:
        """PANAHON sent-9 — the long-tail comma-enumeration after a
        colon. Same fast-path mechanism as sent-2.

        **Phase 10.J.post-4 tightening (analysis A pin).** The
        colon-split fires first (pipeline.py:243) and early-returns,
        collapsing the ``(X ay Y) : Z`` vs ``X ay (Y : Z)``
        ambiguity in favor of analysis A (matrix-level colon-
        appositive). Analysis B handling is deferred to post-5
        (the spike-then-decide sub-PR).

        Structure of analysis A on sent-9:

        * Matrix is an S-coord (``COORD=AND``) with 2 conjuncts
          for the top-level ``at`` (``Tigang rin ... bukirin`` +
          ``karaniwang ang inaani ay mga prutas at gulay``).
        * The post-colon enumeration (``ang mangga, bayabas,
          santol, abokado, melon at pakwan``) sits in the matrix's
          ``APP`` set as a single ``COORD=AND`` NP with 6
          conjuncts.
        * The second S-coord conjunct carries the inner ay-clause
          (``ang inaani ay mga prutas at gulay``). Its ``TOPIC ==
          SUBJ`` identity comes from the chart-level Phase 4 §7.4
          rule. ``REL-PRO`` is not surfaced at the matrix (the
          chart's ``=c`` constraining equation enforces the
          binding but doesn't write the feature). The post-4
          chained-pipeline-split infra does NOT change this — the
          ``ay`` is inside an S-coord conjunct of the colon-
          split's pre-half, not at its matrix level, so the
          chained ay-split doesn't fire here. (Top-level ay-
          fronting + chained-ay-from-colon-pre both DO surface
          REL-PRO; tests for those identities live in
          ``test_phase10_j_post4.py``.)
        * The first S-coord conjunct (``Tigang rin ang mga
          bukirin``) has no TOPIC (no ay-fronting on that side).
        """
        text = (
            "Tigang rin ang mga bukirin at karaniwang ang inaani ay "
            "mga prutas at gulay: ang mangga, bayabas, santol, "
            "abokado, melon at pakwan."
        )
        parses = parse_text(text)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]

        # Matrix S is the top-level `at`-coord: COORD=AND, 2
        # conjuncts, 1 APP from the colon-appositive enumeration.
        assert fs.feats.get("COORD") == "AND", (
            "Top-level should be S-coord (`Tigang rin ... at "
            "karaniwang ...`)."
        )
        conjuncts = fs.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2, (
            f"Expected 2 S-coord conjuncts; got {len(conjuncts)}"
        )
        conj_list = list(conjuncts)

        # APP is the post-colon enumeration NP: COORD=AND with 6
        # conjuncts (mangga, bayabas, santol, abokado, melon,
        # pakwan).
        app = fs.feats.get("APP")
        assert app is not None, "Colon appositive missing from APP"
        assert len(app) == 1
        appositive = next(iter(app))
        assert appositive.feats.get("COORD") == "AND", (
            "Post-colon enumeration should be a COORD=AND NP"
        )
        enum_conjuncts = appositive.feats.get("CONJUNCTS")
        assert enum_conjuncts is not None
        assert len(enum_conjuncts) == 6, (
            f"Expected 6 fruits/vegs in enumeration; got "
            f"{len(enum_conjuncts)}"
        )

        # Inner ay-clause (the second S-coord conjunct) has
        # TOPIC == SUBJ from chart-level Phase 4 §7.4. REL-PRO
        # is not surfaced at the matrix (see docstring).
        inner_ay = conj_list[1]
        assert inner_ay.feats.get("PRED") == "BE-N <SUBJ>", (
            "Inner ay-clause should be predicative-N"
        )
        topic = inner_ay.feats.get("TOPIC")
        subj = inner_ay.feats.get("SUBJ")
        assert topic is not None, (
            "Inner ay-clause should have TOPIC (the fronted NP)"
        )
        assert subj is not None, "Inner ay-clause should have SUBJ"
        assert topic is subj, (
            "Inner ay-clause TOPIC must equal SUBJ (Phase 4 §7.4)"
        )

        # First S-coord conjunct (Tigang rin ang mga bukirin) has
        # no TOPIC — no ay-fronting on that side.
        first_conj = conj_list[0]
        assert first_conj.feats.get("TOPIC") is None, (
            "First S-coord conjunct should have no TOPIC "
            "(no ay-fronting on that side)"
        )

    def test_short_colon_sentence_still_works(self) -> None:
        """A short colon-appositive sentence should parse via the
        chart-level rule (Phase 9.X.c26) when the fast path either
        succeeds or falls through. Either route is acceptable —
        what matters is that the closure doesn't regress."""
        parses = parse_text(
            "Maganda ang ulan: malakas ito."
        )
        assert len(parses) >= 1


class TestCommaAtNpSynthesis:
    def test_post_colon_binary_comma_at_coord(self) -> None:
        """Inside a colon-split's post-half, a ``X, at Y`` shape
        triggers the pipeline-level synthesis of a
        ``NP[CASE=NOM, COORD=AND]`` matrix. The chart has no binary
        comma+at coord rule (it was removed to avoid chart-state
        count regression on non-comma sentences), so this path is
        the only route.
        """
        text = (
            "Maganda ang panahon dito: ang panahon ng tag-init mula "
            "Abril hanggang Hunyo, at ang panahon ng tag-ulan mula "
            "Hulyo hanggang Oktubre."
        )
        parses = parse_text(text)
        assert len(parses) >= 1
        _ct, fs, _astr, _diags = parses[0]
        app = fs.feats.get("APP")
        assert app is not None
        # The appositive is itself a COORD=AND NP with two conjuncts.
        appositive = next(iter(app))
        assert appositive.feats.get("COORD") == "AND"
        conjuncts = appositive.feats.get("CONJUNCTS")
        assert conjuncts is not None
        assert len(conjuncts) == 2

    def test_chart_has_no_comma_at_binary_coord(self) -> None:
        """Guard: the chart rule for binary comma+at NP coord must
        stay unregistered. If a regression accidentally re-adds it,
        the ``test_phase5k_coord_interactions
        .test_cardinal_plus_adj_plus_coord`` test would also fail
        (verified during post-1 implementation)."""
        g = Grammar.load_default()
        comma_at_rules = [
            r for r in g.rules
            if r.lhs.startswith("NP[CASE=")
            and len(r.rhs) == 4
            and r.rhs[1] == "PUNCT[PUNCT_CLASS=COMMA]"
            and r.rhs[2] == "PART[COORD=AND]"
            and r.rhs[0].startswith("NP[CASE=")
            and r.rhs[3].startswith("NP[CASE=")
        ]
        assert len(comma_at_rules) == 0, (
            "Binary comma+at NP coord chart rule should not exist; "
            "synthesis lives at pipeline level (see "
            "_try_comma_at_np_split in core/pipeline.py)."
        )


class TestNoRegressionOnCanonicalParses:
    def test_cardinal_plus_adj_plus_coord_canonical_first(self) -> None:
        """The OBJ-bearing ``BUY <SUBJ, OBJ>`` parse must rank as
        ``parses[0]`` for the long GEN-coord test sentence — the
        original chart attempts at Phase 10.J.post-1 demoted this
        canonical parse past the default 5000-tree iteration cap
        before the rules were re-narrowed (NOM-only NP-PP attach
        + pipeline-level comma-at synthesis). Regression guard."""
        parses = parse_text(
            "Bumili ng dalawang malalaking aklat "
            "at ng tatlong maliliit na lapis si Maria."
        )
        assert parses, "Three-way composition test fixture failed to parse"
        _ct, fs, _astr, _diags = parses[0]
        obj = fs.feats.get("OBJ")
        assert obj is not None, "Canonical BUY parse is not parses[0]"
        assert obj.feats.get("COORD") == "AND"
