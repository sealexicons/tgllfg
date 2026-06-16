# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 14.final.post-13 — sanitize verb-percolation on non-verb head lifts.

``cfg/_helpers.py``'s ``_eqs`` prepends the five-equation
``_VERB_PERCOLATION`` block (``(↑ PRED) = ↓1 PRED`` / VOICE / ASPECT /
MOOD / LEX-ASTRUCT) and is contracted to V-initial rules where ``↓1`` is
the verb. A family of *head-sharing* non-verb lifts routed through ``_eqs``
anyway — ``AdvP → ADV``, the compound-TIME AdvP, every ``PP → PREP …``,
the post-modifier-demonstrative ``NP → NP PART DET[DEM]`` family, and
``S_GAP → S_GAP PP``. Each already unifies its daughter onto the matrix via
``(↑) = ↓1``, so the percolation was redundant for the feats the daughter
*has* and, for the five verb feats it lacks, auto-vivified an **empty**
``PRED`` / ``VOICE`` / ``ASPECT`` / ``MOOD`` / ``LEX-ASTRUCT`` f-node on the
lifted phrase (a fronted ADV's TOPIC, a PP ADJUNCT, a demonstrative SUBJ).

The pre-V DAT-PRON OV relative-clause rule (``S_GAP → NP[CASE=DAT]
PART[LINK] V[VOICE=OV]``) was worse than redundant: it percolated from
``↓1`` (the DAT pronoun) and omitted the ``(↑) = ↓3`` head equation its own
header comment specifies, so the RC body's verb content was dropped
entirely and its predicate left empty. This phase added ``(↑) = ↓3`` so the
verb heads the clause.

``test_no_verb_percolation_from_non_verb_daughter`` is the standing
guard: no compiled rule may carry the verb-percolation signature unless
its ``↓1`` is a verb category.
"""

from tgllfg.cfg.grammar import Grammar
from tgllfg.core.common import FStructure
from tgllfg.core.pipeline import parse_text

_VERBAL_FEATS = {"PRED", "VOICE", "ASPECT", "MOOD", "LEX-ASTRUCT"}
# The signature equation of cfg/_helpers.py's _VERB_PERCOLATION block.
_PERCOLATION_SIG = "(↑ PRED) = ↓1 PRED"
# Categories whose ↓1 legitimately carries the five verb features.
_VERB_CATEGORIES = {"V", "VP", "AUX", "VBar"}


def _empty_verbal_nodes(fs: FStructure) -> list[str]:
    """Every path at which an empty (feature-less) verbal-feat f-node hangs."""
    hits: list[str] = []
    seen: set[int] = set()

    def walk(node: FStructure, path: str) -> None:
        if id(node) in seen:
            return
        seen.add(id(node))
        for key, val in node.feats.items():
            sub = f"{path}.{key}"
            if isinstance(val, FStructure):
                if key in _VERBAL_FEATS and not val.feats:
                    hits.append(sub)
                walk(val, sub)
            elif isinstance(val, frozenset):
                for member in val:
                    if isinstance(member, FStructure):
                        walk(member, sub + "[]")

    walk(fs, "↑")
    return hits


def _cat_symbol(daughter: str) -> str:
    """Bare category of a daughter spec: ``NP[CASE=NOM]`` -> ``NP``."""
    return daughter.split("[", 1)[0]


class TestNoVerbPercolationFromNonVerbDaughter:
    """The standing class guard — re-deriving the post-13 detector."""

    def test_no_verb_percolation_from_non_verb_daughter(self) -> None:
        offenders: list[tuple[str, list[str]]] = []
        for rule in Grammar.load_default().rules:
            if _PERCOLATION_SIG not in rule.equations or not rule.rhs:
                continue
            if _cat_symbol(rule.rhs[0]) not in _VERB_CATEGORIES:
                offenders.append((rule.lhs, rule.rhs))
        assert offenders == [], (
            "verb-percolation (_eqs) used where ↓1 is not a verb — these "
            f"head lifts must use a plain equation list:\n{offenders}"
        )


class TestAdvPLiftSanitized:
    def test_fronted_advp_topic_has_no_empty_verbal_feats(self) -> None:
        parses = parse_text("Bukas, kumain siya.", n_best=5)
        assert len(parses) == 1
        topic = parses[0][1].feats.get("TOPIC")
        assert isinstance(topic, FStructure)
        # The ADV's real content survives; the spurious empties are gone.
        assert topic.feats.get("LEMMA") == "bukas"
        assert topic.feats.get("ADV_TYPE") == "TIME"
        assert not (_VERBAL_FEATS & topic.feats.keys())

    def test_compound_time_advp_clean(self) -> None:
        parses = parse_text("Bukas ng gabi, kumain siya.", n_best=5)
        assert len(parses) == 1
        assert _empty_verbal_nodes(parses[0][1]) == []


class TestPPAdjunctSanitized:
    def test_clause_final_pp_adjunct_clean(self) -> None:
        parses = parse_text("Kumain siya para sa bata.", n_best=5)
        assert len(parses) == 1
        assert _empty_verbal_nodes(parses[0][1]) == []


class TestNPDemSanitized:
    def test_post_modifier_dem_subject_clean(self) -> None:
        parses = parse_text("Kumain ang batang ito.", n_best=5)
        assert len(parses) == 1
        subj = parses[0][1].feats.get("SUBJ")
        assert isinstance(subj, FStructure)
        assert subj.feats.get("PRED")  # the head noun's PRED still percolates
        assert not (_VERBAL_FEATS & subj.feats.keys() - {"PRED"})

    def test_cross_case_dem_clean(self) -> None:
        # Phase 9.X.c49 NOM-form DEM on a DAT NP (`sa bahay na ito`).
        parses = parse_text("Pumunta siya sa bahay na ito.", n_best=5)
        assert parses
        assert _empty_verbal_nodes(parses[0][1]) == []


class TestOVRelativeClauseVerbRestored:
    """The pre-V DAT-PRON OV-RC rule now heads on the verb (↓3)."""

    def test_rc_body_carries_real_verb_predicate(self) -> None:
        parses = parse_text(
            "Nagsasalita sila sa bayang kanilang binibisita.", n_best=5
        )
        assert parses
        fs = parses[0][1]
        # No verbal feat anywhere is an empty auto-vivified node.
        assert _empty_verbal_nodes(fs) == []
        # Locate the relativized-noun ADJ member and assert its real verb feats.
        rc_bodies = [
            adj
            for adjunct in (fs.feats.get("ADJUNCT") or ())
            if isinstance(adjunct, FStructure)
            for adj in (adjunct.feats.get("ADJ") or ())
            if isinstance(adj, FStructure) and "REL-PRO" in adj.feats
        ]
        assert rc_bodies, "expected a relativized-noun ADJ with a REL-PRO body"
        body = rc_bodies[0]
        assert body.feats.get("VOICE") == "OV"
        assert body.feats.get("ASPECT") == "IPFV"
        assert str(body.feats.get("PRED", "")).startswith("BISITA")
        # SUBJ is the relativized head (REL-PRO); actor is the DAT-PRON OBJ-AGENT.
        assert body.feats.get("SUBJ") is body.feats.get("REL-PRO")
        assert isinstance(body.feats.get("OBJ-AGENT"), FStructure)
