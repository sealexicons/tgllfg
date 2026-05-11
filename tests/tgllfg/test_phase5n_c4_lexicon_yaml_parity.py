"""Phase 5n.C.4 Commit 12 — BASE ↔ YAML parity test.

For every lemma the YAML loader produces, the resulting
``LexicalEntry`` list must equal the corresponding ``BASE`` list
row-by-row. The test starts trivial (the YAML tree is empty in C12,
so the loop is a no-op) and grows naturally as C13–C16 migrate
entries out of ``BASE`` into the YAML files. Once C16 reduces
``BASE`` to a compatibility shim and points the consumer at the
loader, this test ratchets to checking the loader-only path.

The directional check is **loader → BASE**, not the reverse:

* YAML entries that don't appear in BASE → test FAILS (probably a
  migration bug; the YAML record should match BASE exactly).
* BASE entries that don't yet appear in YAML → test PASSES (these
  are still authoritative on the Python side until the migration
  reaches them).
"""

from __future__ import annotations

import pytest

from tgllfg.core.lexicon import BASE
from tgllfg.core.lexicon_loader import load_lex_entries


def test_every_loaded_yaml_entry_appears_in_base() -> None:
    """During C13–C15 the migration COPIES entries from BASE into
    the YAML tree without removing them from BASE — BASE remains
    authoritative until C16 cuts over to the loader. So the
    parity check is *entry-level membership* (every YAML record
    matches a BASE record for the same lemma) rather than
    *list equality*. C16 tightens this to full list equality once
    BASE becomes empty."""
    loaded = load_lex_entries()
    for lemma, yaml_entries in loaded.items():
        base_entries = BASE.get(lemma, [])
        for entry in yaml_entries:
            assert entry in base_entries, (
                f"YAML entry for lemma {lemma!r} does not match any "
                f"BASE entry: {entry!r}"
            )


def test_yaml_entries_appear_in_base_subsequence_order() -> None:
    """Stronger: YAML entries for a lemma appear in the same
    relative order as in BASE. Catches accidental reorderings
    during migration that would change the analyzer's
    first-match-wins selection at C16 cutover."""
    loaded = load_lex_entries()
    for lemma, yaml_entries in loaded.items():
        base_entries = BASE.get(lemma, [])
        base_idx = 0
        for entry in yaml_entries:
            try:
                base_idx = base_entries.index(entry, base_idx) + 1
            except ValueError:
                # Out of order, or not in BASE.
                raise AssertionError(
                    f"YAML entry order for lemma {lemma!r} does not "
                    f"match BASE's subsequence order at: {entry!r}"
                ) from None


def test_loader_is_callable_in_repo_default() -> None:
    """Smoke: ``load_lex_entries()`` with no arguments resolves the
    default data dir under the repo and returns a dict (possibly
    empty). Catches path-construction regressions."""
    out = load_lex_entries()
    assert isinstance(out, dict)


@pytest.mark.parametrize("lemma_in_base", sorted(BASE.keys()))
def test_yaml_entries_for_base_lemma_match_base(lemma_in_base: str) -> None:
    """Per-lemma migration scoreboard. Each ``BASE`` lemma is either
    still Python-only (loader output empty for this lemma — test
    short-circuits as a pass) or partially / fully migrated, in
    which case every YAML record must match a BASE record. The
    parametrize gives pytest a per-lemma signal so the migration
    progress is visible at a glance.
    """
    loaded = load_lex_entries()
    yaml_entries = loaded.get(lemma_in_base, [])
    base_entries = BASE[lemma_in_base]
    if not yaml_entries:
        # Not yet migrated; still Python-authoritative — fine.
        return
    for entry in yaml_entries:
        assert entry in base_entries, (
            f"YAML entry for lemma {lemma_in_base!r} does not match "
            f"any BASE entry: {entry!r}"
        )
