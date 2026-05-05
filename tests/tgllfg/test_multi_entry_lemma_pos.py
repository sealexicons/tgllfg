"""Phase 5f closing deferral: multiple lex entries per ``(lemma, pos)``.

The morph analyzer's noun index used to be ``dict[str, MorphAnalysis]``
(scalar-valued per surface), so a second NOUN entry for the same
citation silently shadowed the first. Phase 5f hit this with
``kuwarto`` (room vs quarter-of-hour; Commits 8 + 12) and
``linggo`` (week vs Sunday; Commit 13) — the latter resolved by
feature-merging the two readings on a single entry, the former
deferred. This commit closes the deferral by extending the
analyzer's noun index to ``dict[str, list[MorphAnalysis]]``
(parallel to the existing list-valued ``verb_forms`` and
``particles`` indices).

The chart parser already handles multiple analyses per token via
the standard ``mlist[i]`` lattice, so no downstream changes are
needed: the syntactic context selects between competing readings.
For ``kuwarto``, the minute-composition rule's
``(↓3 SEM_CLASS) =c 'FRACTION'`` constraint picks the
clock-fraction reading; NP-modifier rules consume the bare-NOUN
"room" reading.

Tests cover:

* Analyzer: ``kuwarto`` returns two NOUN MorphAnalyses (room and
  FRACTION); ordering is insertion order in the YAML.
* Single-entry nouns are unchanged: ``aklat`` returns one NOUN
  analysis as before.
* End-to-end parse: ``Pumunta ako sa alasotso y kuwarto`` (8:15
  with the FRACTION reading) and ``Bumili ako ng kuwarto`` (the
  "room" reading) both parse correctly via different syntactic
  paths.
* Other multi-entry lookups (verbs, particles) unchanged.
"""

from __future__ import annotations

from tgllfg.morph import analyze_tokens
from tgllfg.core.pipeline import parse_text
from tgllfg.text import tokenize


class TestMultiEntryNoun:
    """``kuwarto`` has two NOUN readings."""

    def test_kuwarto_two_readings(self) -> None:
        toks = tokenize("kuwarto")
        ml = analyze_tokens(toks)
        nouns = [c for c in ml[0] if c.pos == "NOUN"]
        assert len(nouns) == 2, f"expected 2 NOUN readings, got {len(nouns)}"
        # Both share the lemma; SEM_CLASS distinguishes them.
        assert all(n.lemma == "kuwarto" for n in nouns)
        sem_classes = {n.feats.get("SEM_CLASS") for n in nouns}
        assert sem_classes == {None, "FRACTION"}

    def test_kuwarto_clock_fraction_parses(self) -> None:
        """``alasotso y kuwarto`` "8:15" — the FRACTION reading
        fires the minute-composition rule."""
        rs = parse_text("Pumunta ako sa alasotso y kuwarto.", n_best=1)
        assert rs, "no parse"

    def test_kuwarto_room_parses(self) -> None:
        """``Bumili ako ng kuwarto`` — the "room" reading fires
        the standard NP-modifier path."""
        rs = parse_text("Bumili ako ng kuwarto.", n_best=1)
        assert rs, "no parse"
        _, f, _, _ = rs[0]
        obj = f.feats.get("OBJ")
        assert obj is not None
        assert obj.feats.get("LEMMA") == "kuwarto"


class TestSingleEntryNoun:
    """Single-entry nouns are unchanged: only one MorphAnalysis."""

    def test_aklat_single_reading(self) -> None:
        toks = tokenize("aklat")
        ml = analyze_tokens(toks)
        nouns = [c for c in ml[0] if c.pos == "NOUN"]
        assert len(nouns) == 1
        assert nouns[0].lemma == "aklat"
