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


def test_loaded_yaml_matches_base_row_by_row() -> None:
    """For every lemma in the YAML tree, the loader's output must
    equal what ``BASE`` has — record-for-record, in declaration
    order."""
    loaded = load_lex_entries()
    for lemma, yaml_entries in loaded.items():
        base_entries = BASE.get(lemma, [])
        assert yaml_entries == base_entries, (
            f"lemma {lemma!r}: YAML {len(yaml_entries)} entries "
            f"vs BASE {len(base_entries)} entries differ — see "
            f"per-entry diff in pytest output"
        )


def test_loader_is_callable_in_repo_default() -> None:
    """Smoke: ``load_lex_entries()`` with no arguments resolves the
    default data dir under the repo and returns a dict (possibly
    empty). Catches path-construction regressions."""
    out = load_lex_entries()
    assert isinstance(out, dict)


@pytest.mark.parametrize("lemma_in_base", sorted(BASE.keys()))
def test_every_base_lemma_is_either_in_yaml_or_python_only(
    lemma_in_base: str,
) -> None:
    """Surface check on the migration scoreboard: each ``BASE``
    lemma is either still Python-only (loader output empty) or
    YAML-migrated (loader output equals BASE). The actual equality
    check happens in :func:`test_loaded_yaml_matches_base_row_by_row`;
    this test is a per-lemma signal so pytest's parametrize report
    shows the migration scoreboard at a glance.
    """
    loaded = load_lex_entries()
    yaml_entries = loaded.get(lemma_in_base, [])
    base_entries = BASE[lemma_in_base]
    if not yaml_entries:
        # Python-only — fine, this lemma hasn't been migrated yet.
        return
    assert yaml_entries == base_entries
