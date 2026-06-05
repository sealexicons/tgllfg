# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5l Commit 11: reported question — ASK_CLASS lex tagging.

Roadmap §12.1 / plan-of-record §5.7, §6 Commit 11.

**Scope reduction note** (mirroring Commit 10's indirect-speech
scope reduction). Plan §1 / §5.7 assumed the existing Phase 5i
``S_INTERROG_COMP`` rule would compose with non-``alam``
ASK-class verbs (``Tinanong niya kung sino ang kumain.`` "He
asked who ate"). Recon during this commit revealed:

1. The Phase 5i matrix-wrap rule requires ``CTRL_CLASS=KNOW``
   on the matrix V; ``tanong`` carries ``CTRL_CLASS=NONE``, so
   the canonical Phase 5i path doesn't fire on tinanong.
2. ``Tinanong niya kung sino ang kumain.`` nonetheless **does
   parse** — but via the Phase 5l COND-adjunct path (the
   matrix ``Tinanong niya`` is a complete OV clause, so the
   ``kung`` clause attaches as a Phase 5l ``SubordClause[COND]``).
3. The resulting parse is structurally valid but semantically
   wrong: the kung-clause is the reported-Q complement, not a
   conditional adjunct.

Building the correct reported-Q path requires:

* Tagging ASK verbs with a CTRL_CLASS variant (or a new
  ASK_CLASS that the Phase 5i rule recognizes).
* Broadening the Phase 5i ``S_INTERROG_COMP`` matrix wrap to
  fire on KNOW + ASK verbs (or a unified COMP-INTERROG-class).
* Optionally tightening the Phase 5l COND-adjunct rule so it
  doesn't fire when the matrix is an ASK verb and the kung-
  clause has Q_TYPE=WH (otherwise the COND parse competes with
  the proper reported-Q parse).

That work is deferred to a Phase 5l follow-on (or Phase 6
functional uncertainty), parallel to the Commit 10 indirect-
speech deferral.

This commit therefore delivers:

* **ASK_CLASS=YES** lex tagging on ``tanong`` in
  ``data/tgl/verbs.yaml``. The diagnostic feat propagates onto
  inflected forms via the paradigm engine.
* The pinned misanalysis is recorded as a known limitation;
  flipping the assertion in
  ``TestReportedQMisanalysisDeferred`` is the trigger for the
  follow-on reported-Q work.
* The Phase 5i KNOW-class indirect-Q path
  (``Alam ko kung sino ang kumain.``) is verified to continue
  parsing — that's the only correct reported-Q path today.
"""

from tgllfg.core.common import Token
from tgllfg.morph import Analyzer
from tgllfg.core.pipeline import parse_text


def _tok(s: str) -> Token:
    return Token(surface=s, norm=s.lower(), start=0, end=len(s))


def _adjunct_with_subord_type(fs, subord_type: str):
    adjuncts = fs.feats.get("ADJUNCT")
    if adjuncts is None:
        return None
    for adj in adjuncts:
        if adj.feats.get("SUBORD_TYPE") == subord_type:
            return adj
    return None


# === ASK_CLASS lex tagging ===========================================


class TestAskClassLexTagging:
    """The ``tanong`` lemma carries ``feats: {ASK_CLASS: "YES"}``
    in ``data/tgl/verbs.yaml``. The feat propagates onto
    inflected forms via the paradigm engine for selected cells
    (parallel to SAY_CLASS in Commit 10)."""

    def test_tinanong_carries_ask_class(self) -> None:
        """``tinanong`` (OV PFV) — canonical reported-Q matrix
        verb form."""
        analyzer = Analyzer.from_default()
        out = analyzer.analyze_one(_tok("tinanong"))
        ask = [a for a in out if a.feats.get("ASK_CLASS") is True]
        assert len(ask) == 1
        assert ask[0].lemma == "tanong"
        assert ask[0].feats.get("VOICE") == "OV"

    def test_ask_class_does_not_leak_to_other_verbs(self) -> None:
        analyzer = Analyzer.from_default()
        for surf in ("kumain", "pumunta", "tumakbo", "sinabi"):
            out = analyzer.analyze_one(_tok(surf))
            for a in out:
                assert a.feats.get("ASK_CLASS") is None, (
                    f"ASK_CLASS unexpectedly present on {surf!r} "
                    f"(lemma={a.lemma})"
                )


# === Phase 5i KNOW-class still works =================================


class TestPhase5iKnowStillWorks:
    """The Phase 5i ``Alam ko kung sino ang kumain.`` path —
    KNOW-verb + GEN + S_INTERROG_COMP — must continue to parse.
    This is the only correct reported-Q path today; pin it
    against any regression from the Commit 11 lex tagging."""

    def test_alam_ko_kung_sino_still_parses(self) -> None:
        parses = parse_text("Alam ko kung sino ang kumain.")
        assert len(parses) >= 1
        # The Phase 5i path lands COMP_TYPE=INTERROG somewhere
        # in the f-structure. Walk to find it.
        _ct, fs, _astr, _diags = parses[0]
        assert _has_feat_value_anywhere(fs, "COMP_TYPE", "INTERROG"), (
            "Phase 5i ``Alam ko kung X`` indirect-Q path no "
            "longer carries COMP_TYPE=INTERROG"
        )


def _has_feat_value_anywhere(fs, feat: str, value: str, _seen=None) -> bool:
    if _seen is None:
        _seen = set()
    if id(fs) in _seen:
        return False
    _seen.add(id(fs))
    if fs.feats.get(feat) == value:
        return True
    for v in fs.feats.values():
        if hasattr(v, "feats"):
            if _has_feat_value_anywhere(v, feat, value, _seen):
                return True
        elif isinstance(v, (list, tuple, set, frozenset)):
            for item in v:
                if hasattr(item, "feats") and _has_feat_value_anywhere(
                    item, feat, value, _seen
                ):
                    return True
    return False


# === ASK reported-Q misanalysis pinned (deferred) ====================


# Phase 5n.A Commit 28 misanalysis + 0-parse tripwires lifted by
# Phase 5n.A Commit 29. See test_phase5n_reported_q.py for the
# positive-parse assertions on those 18 sentences.
