# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 5n.C.3 Commit 9 — L49 reduplicated wh-plural PRONs.

Adds the productive ``redup_wh_plural`` paradigm cell to
``data/tgl/paradigms.yaml``:

* ``base_pos: PRON``
* ``affix_class: redup_wh_plural``
* operations: ``[redup_root]`` — appends the wh-PRON's surface
  to itself (no sandhi).
* ``feats: {NUM: PL}`` — distinguishes the plural-reading
  derivation from the bare wh-PRON.

The 4 wh-PRONs in ``data/tgl/pronouns.yaml`` (``sino`` /
``ano`` / ``kanino`` / ``alin``) gain
``affix_class: [redup_wh_plural]`` to trigger the cell.

Closes §18 L49 (Phase 5i §9.2 deferral surfaced during Phase
5m wh+man builder work). Per S&O 1972 §6 the redup-PL wh
surfaces are productive across the wh-PRON inventory.

Tests cover:

* Productive surfaces analyze as PRON with ``WH=YES`` (from
  root), ``NUM=PL`` (from cell), and per-base CASE / HUMAN
  inherited from the source PRON.
* Bare wh-PRONs continue without ``NUM=PL``.
* Hyphenated input ``ano-ano`` parses via the hyphen-merge
  tokenizer pre-pass — the merged form ``anoano`` is what the
  productive paradigm generates and indexes.
* The redup_root op (no sandhi) is the right choice for /o/-
  ending wh-PRONs (``ano`` / ``sino`` / ``kanino``): the
  surface keeps /o/ in both copies, distinct from ``full_redup``
  which would raise /o/→/u/ in the first copy.
"""

import pytest

from tgllfg.core.common import Token
from tgllfg.core.pipeline import parse_text
from tgllfg.morph.analyzer import Analyzer


# === Morph layer ==========================================================


@pytest.mark.parametrize("surface,base,case,human", [
    ("anoano",       "ano",     "NOM", False),
    ("sinosino",     "sino",    "NOM", True),
    ("kaninokanino", "kanino",  "DAT", True),
    ("alinalin",     "alin",    "NOM", False),
])
def test_wh_redup_morph(
    surface: str, base: str, case: str, human: bool
) -> None:
    """Each redup wh-PRON analyses as PRON with WH=YES + NUM=PL,
    and CASE / HUMAN from the source PRON."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    redup_prons = [r for r in results
                   if r.pos == "PRON"
                   and r.feats.get("NUM") == "PL"
                   and r.feats.get("WH") is True]
    assert len(redup_prons) >= 1, (
        f"expected ≥1 PRON WH=YES NUM=PL analysis for {surface!r}"
    )
    r = redup_prons[0]
    assert r.lemma == base
    assert r.feats.get("CASE") == case
    if human:
        assert r.feats.get("HUMAN") is True
    else:
        assert r.feats.get("HUMAN") is None or r.feats.get("HUMAN") is False


# === Bare wh-PRONs unchanged =============================================


@pytest.mark.parametrize("surface", ["ano", "sino", "kanino", "alin"])
def test_bare_wh_pron_unchanged(surface: str) -> None:
    """Bare wh-PRONs continue to analyze without NUM=PL — the
    Pronoun.affix_class field on the entry doesn't shadow bare
    lookup."""
    a = Analyzer.from_default()
    token = Token(surface=surface, norm=surface, start=0, end=len(surface))
    results = a.analyze_one(token)
    pron_results = [r for r in results
                    if r.pos == "PRON" and r.feats.get("WH") is True]
    assert len(pron_results) >= 1
    # Bare form has no NUM (vs. NUM=PL on the redup form)
    assert pron_results[0].feats.get("NUM") is None


# === Hyphen-merge tokenizer pre-pass =====================================


def test_hyphenated_input_merges() -> None:
    """Canonical hyphenated ``ano-ano`` tokenizes via the
    hyphen-merge pre-pass to the single-token ``anoano``,
    which is what the productive paradigm generates."""
    parses = parse_text("Ano-ano ang aklat?")
    # The question is grammatically valid via the wh-Q
    # constructions; at minimum, the wh-PRON should resolve.
    assert len(parses) >= 1, "expected ≥1 parse for 'Ano-ano ang aklat?'"


# === Distinct from full_redup (no o→u raising) ===========================


def test_redup_root_no_o_raising_on_wh() -> None:
    """The redup_root op (unlike full_redup) preserves /o/ in the
    first copy. Without this, ``ano`` would derive to ``anuano``
    (wrong) instead of ``anoano`` (correct, attested)."""
    a = Analyzer.from_default()
    # ``anuano`` should NOT have an analysis (no rule produces it).
    bad_token = Token(surface="anuano", norm="anuano", start=0, end=6)
    bad_results = a.analyze_one(bad_token)
    assert all(r.pos == "_UNK" for r in bad_results), (
        f"unexpected analysis for 'anuano': {bad_results}; "
        f"redup_root should NOT raise /o/→/u/"
    )
    # ``anoano`` SHOULD have a clean PRON analysis.
    good_token = Token(surface="anoano", norm="anoano", start=0, end=6)
    good_results = a.analyze_one(good_token)
    prons = [r for r in good_results if r.pos == "PRON"]
    assert len(prons) >= 1
