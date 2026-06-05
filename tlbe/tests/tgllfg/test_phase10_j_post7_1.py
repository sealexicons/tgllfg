# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.J.post-7.1: palibhasa REASON subordinator + paradigm
extensions for the post-7.1 audit residue.

Adds:

1. ``palibhasa`` PART entry in particles.yaml with
   ``COMP_TYPE=REAS``, parallel to the S-taking ``dahil`` entry
   (Phase 5l Commit 9). The chart's existing
   ``SubordClause → PART[COMP_TYPE=REAS] S`` rule
   (subordination.py:471) and ``S → SubordClause PUNCT[COMMA] S``
   rule (line 189) compose the matrix automatically.

2. ``cluster_redup``-both-variants generation in morph/analyzer.py:
   when a root carries ``cluster_redup`` AND a paradigm cell uses
   ``cv_redup``, both the cluster-preserved (``nagtratrabaho``) and
   cluster-stripped (``nagtatrabaho``) variants are indexed.
   "Both forms are attested in modern Tagalog" per the
   ``first_cv`` docstring; this closes the
   ``palibhasa-juan-rich`` exemplar's inner-clause
   ``Hindi siya nagtatrabaho.``.

3. ``sagot`` lex tweak in verbs.yaml: added ``ma`` to
   ``affix_class`` (potentive-AV ``nasagot``) + ``AV_ABSOL: true``
   (licenses the bare ``S → V[AV-TR] NP[CASE=NOM]`` rule for
   ``Sumagot siya.`` / ``Nasagot siya.``).

Closes 2 of 3 ``pending_closure: post-7.1`` constructed exemplars
(``palibhasa-nanay-walang-pera`` and ``palibhasa-juan-rich``). The
remaining ``palibhasa-marunong`` exemplar is blocked by a deeper
**PART[COMP_TYPE=REAS] + S(PRON-clitic-after-ADJ-head)** chart-
coverage gap (parallel constructs with ``kapag`` / ``kung`` /
``bago`` parse fine; only the REAS family fails) — kept as
xfail with its original ``pending_closure: post-7.1`` tag for
auto-XPASS surfacing when a future clitic-placement sub-PR lands.
"""

from tgllfg.core.pipeline import parse_text


class TestPalibhasaSubordClause:
    """post-7.1: palibhasa as PART[COMP_TYPE=REAS] subordinator."""

    def test_palibhasa_nanay_walang_pera_closes(self) -> None:
        """Smallest-inner-clause exemplar — closes cleanly."""
        s = ("Palibhasa walang pera ang nanay, "
             "hindi kami bumili ng pagkain.")
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        # SubordClause joins matrix ADJUNCT
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None and len(adjunct) >= 1
        # Inner adjunct carries SUBORD_TYPE=REAS
        types = {a.feats.get("SUBORD_TYPE") for a in adjunct}
        assert "REAS" in types, (
            f"expected SUBORD_TYPE=REAS, got {types}"
        )

    def test_palibhasa_bare_subord(self) -> None:
        """A bare ``Palibhasa S`` (without a comma+S2 matrix) should
        compose via the SubordClause rule."""
        # SubordClause requires a matrix; we test by feeding it into
        # a comma-S2 structure with a known-parsing post-half.
        s = "Palibhasa mayaman si Juan, mahaba ang buhay niya."
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1, (
            "palibhasa + simple-ADJ-pred post should compose"
        )


class TestParadigmFixes:
    """post-7.1's lex/morph extensions for the palibhasa residue.

    These tests pin the closure of ``palibhasa-juan-rich`` via the
    ``cluster_redup``-both-variants generation, and document the
    remaining ``palibhasa-marunong`` residue.
    """

    def test_palibhasa_juan_rich_closes(self) -> None:
        """``Hindi siya nagtatrabaho.`` post-half now parses via the
        ``cluster_redup``-both-variants paradigm fix: the morph
        analyzer now indexes BOTH ``nagtatrabaho`` (cluster-stripped
        simple redup) and ``nagtratrabaho`` (cluster-preserved) for
        the same ``trabaho`` AV-IPFV cell. Same applies to
        ``magtatrabaho`` (CTPL). The PANAHON sent-17 corpus form
        ``nagtratrabaho`` (which had Phase 9.X.c6-era support) is
        preserved.
        """
        s = ("Palibhasa mayaman si Juan, "
             "hindi siya nagtatrabaho.")
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1
        _ctree, fs, _astr, _diags = parses[0]
        adjunct = fs.feats.get("ADJUNCT")
        assert adjunct is not None and len(adjunct) >= 1

    def test_nagtatrabaho_and_nagtratrabaho_both_resolve(self) -> None:
        """The cluster_redup-both-variants fix indexes both surface
        forms to the same root ``trabaho`` with identical feats."""
        for surface in ("Nagtatrabaho siya.", "Nagtratrabaho siya."):
            parses = parse_text(surface, n_best=2)
            assert len(parses) >= 1, f"{surface!r} should parse"

    def test_nasagot_av_nvol_resolves(self) -> None:
        """``Nasagot niya ang tanong.`` (AV-NVOL potentive) parses
        via the new ``ma`` class on ``sagot``."""
        parses = parse_text("Nasagot niya ang tanong.", n_best=2)
        assert len(parses) >= 1

    def test_sumagot_siya_resolves(self) -> None:
        """``Sumagot siya.`` (bare AV-TR + NOM-PRON) parses via the
        new ``AV_ABSOL: true`` on ``sagot``."""
        parses = parse_text("Sumagot siya.", n_best=2)
        assert len(parses) >= 1


class TestCliticAbsorbedLinker:
    """post-7.1's clitic-placement fix for the absorbed-linker pattern.

    Root cause (identified in post-7.1): ``_is_pre_linker_pron`` in
    ``clitics/placement.py`` was over-matching — it was designed for
    the Phase 5d Commit 6 possessor-of-N RC construction
    (``aklat kong binasa`` = "book that I read", where ``kong`` =
    ko + -ng linker, and ``ko`` is the possessor of ``aklat``). But
    it also fired on the clitic-absorbed-linker pattern
    (``madali niyang nasagot`` = "easily he/she answered", where
    ``niyang`` = niya + -ng absorbed-linker, and ``niya`` is the V's
    GEN-AGENT). In the latter pattern the clitic must move to the
    canonical post-V position so the chart's
    ``ADJ + -ng + V + ...`` rule fires.

    The fix narrows ``_is_pre_linker_pron`` to NOT match when the
    immediately-preceding token is an ADJ — preserving the
    possessor-of-N case (N / Q / PART hosts) while letting the
    ADJ-host case fall through to the standard PRON-post-V
    Wackernagel reordering.
    """

    def test_palibhasa_marunong_closes(self) -> None:
        """The post-half ``madali niyang nasagot ang tanong.`` is the
        clitic-absorbed-linker form — fixed by narrowing
        ``_is_pre_linker_pron`` to exclude ADJ-preceded PRON-clitics.
        """
        s = ("Palibhasa marunong siya, "
             "madali niyang nasagot ang tanong.")
        parses = parse_text(s, n_best=3)
        assert len(parses) >= 1

    def test_madali_niyang_nasagot_standalone(self) -> None:
        """``Madali niyang nasagot ang tanong.`` standalone also
        parses (the canonical equivalent ``Madaling nasagot niya
        ang tanong.`` parses too — both surface forms now succeed)."""
        for s in (
            "Madali niyang nasagot ang tanong.",
            "Madaling nasagot niya ang tanong.",
        ):
            parses = parse_text(s, n_best=3)
            assert len(parses) >= 1, f"failed: {s!r}"

    def test_possessor_rc_preserved(self) -> None:
        """Anti-regression: the Phase 5d Commit 6 possessor-of-N RC
        construction (the original gate's target) still parses. The
        narrowing only excludes ADJ-preceded PRON-clitics; N / Q /
        PART hosts continue to keep the clitic in place.
        """
        for s in (
            "Ang aklat kong binasa ay maganda.",
            "Ang isda kong kinain ay masarap.",
            "Nakita ko ang aklat mong binasa.",
        ):
            parses = parse_text(s, n_best=3)
            assert len(parses) >= 1, f"possessor-RC regressed: {s!r}"
