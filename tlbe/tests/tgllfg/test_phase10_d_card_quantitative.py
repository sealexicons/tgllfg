# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Phase 10.D — CARD quantitative X-X (card_redup unification + milyon).

Fourth R-bucket sibling. Reconciles the pre-10.A ``card_redup``
cell (Phase 5n.C.3 Commit 2) with the newer productive redup
approach:

1. **Op unification** — ``card_redup`` migrates from the bespoke
   ``full_redup`` op (always raised the first-copy /o/) to the
   shared ``redup_root`` op. First-copy /o/→/u/ raising is now the
   per-root ``redup_o_raise`` sandhi flag (same machinery as 10.A
   ``taon`` → ``taun-taon``). The ``full_redup`` op +
   ``sandhi.full_reduplicate`` were removed (card_redup was their
   sole user). Surfaces for ``daan`` / ``libo`` are byte-identical
   to the pre-10.D output.
2. **milyon coverage** — new ``milyon`` "million" NOUN root
   (COLL_VALUE=MILLIONS) joins ``daan`` / ``libo`` in the
   card_redup series. As a Spanish loan with a closed final
   syllable /-on/, it does NOT take first-copy raising
   (``milyon`` → ``milyonmilyon``, not ``*milyunmilyon``) — it
   simply opts out of ``redup_o_raise``, which the unified op
   makes a no-op-by-default.
3. **Cross-cutting feats** — ``REDUP=FULL`` + ``REDUP_SEM=QUANT``
   (quantitative large-number redup, distinct from the
   DISTR/FREQ siblings) added to the cell. No
   ``lemma_redup_hyphen``: card_redup is NOUN→NOUN (no POS-flip),
   so the LEMMA stays the bare root (``libo`` / ``daan`` /
   ``milyon``), per the convention that only POS-flip redup cells
   hyphenate (cf. ``redup_intens_adj``).

Phase 10.D.post-1 adds the native ``angaw`` "million"
(``angaw-angaw``), which S&O 1972 p.224 lists as the *primary*
"millions" form — noting ``milyon-milyon`` "also occurs, but is less
common than the forms listed above." Same COLL_VALUE=MILLIONS, no
``loan`` field; ends in the glide ``-aw`` (no stem /o/), so like
``daan`` it has nothing to raise → ``angawangaw``.

References: Schachter & Otanes 1972 §6 / p.224 (attests ``daan-daan`` /
``libu-libo`` / ``angaw-angaw`` + ``libu-libong tao``); Phase 10
external-reviewer typology.
"""

import pytest

from tgllfg.morph.analyzer import _apply, _get_default
from tgllfg.morph.paradigms import Operation


# === Op-level surfaces (redup_root replaces full_redup) ================


@pytest.mark.parametrize("base,flags,expected", [
    # libo opts into redup_o_raise → first-copy /o/→/u/.
    ("libo",   {"redup_o_raise"}, "libulibo"),
    # daan has no stem /o/ — raising is a no-op even with the flag.
    ("daan",   {"redup_o_raise"}, "daandaan"),
    ("daan",   set(),             "daandaan"),
    # angaw ends in the glide -aw (no stem /o/) — raise is a no-op.
    ("angaw",  {"redup_o_raise"}, "angawangaw"),
    ("angaw",  set(),             "angawangaw"),
    # milyon opts OUT — the Spanish-loan closed syllable keeps /o/.
    ("milyon", set(),             "milyonmilyon"),
])
def test_redup_root_card_surfaces(
    base: str, flags: set, expected: str,
) -> None:
    """The unified ``redup_root`` op reproduces the card_redup
    surfaces (byte-identical to the removed ``full_redup`` for
    daan/libo) and yields the no-raise ``milyonmilyon`` for the
    Spanish loan."""
    assert _apply(Operation(op="redup_root"), base, flags, base) == expected


def test_full_redup_op_removed() -> None:
    """The bespoke ``full_redup`` op is gone — _apply raises on it
    (card_redup was its sole user; Phase 10.D unified onto
    redup_root)."""
    with pytest.raises(ValueError, match="unknown operation"):
        _apply(Operation(op="full_redup"), "libo", set(), "libo")


def test_full_reduplicate_function_removed() -> None:
    """``sandhi.full_reduplicate`` is removed."""
    import tgllfg.morph.sandhi as sandhi
    assert not hasattr(sandhi, "full_reduplicate")


# === Productive analyses (incl. new milyon) ============================


@pytest.mark.parametrize("surface,lemma,coll", [
    ("daandaan",     "daan",   "HUNDREDS"),
    ("libulibo",     "libo",   "THOUSANDS"),
    ("angawangaw",   "angaw",  "MILLIONS"),
    ("milyonmilyon", "milyon", "MILLIONS"),
])
def test_card_redup_measure_nouns(
    surface: str, lemma: str, coll: str,
) -> None:
    """Each quantitative-redup surface analyses as a MEASURE NOUN
    carrying REDUP=FULL + REDUP_SEM=QUANT + the root COLL_VALUE,
    with the lemma kept as the bare root (no hyphenation —
    card_redup is same-POS NOUN→NOUN)."""
    analyses = _get_default()._index.nouns.get(surface, [])
    measure = [
        a for a in analyses
        if a.pos == "NOUN" and a.feats.get("MEASURE") is True
    ]
    assert len(measure) >= 1, (
        f"expected a MEASURE NOUN analysis for {surface!r}; got {analyses!r}"
    )
    a = measure[0]
    assert a.lemma == lemma
    assert a.feats.get("COLL_VALUE") == coll
    assert a.feats.get("REDUP") == "FULL"
    assert a.feats.get("REDUP_SEM") == "QUANT"


def test_milyon_no_first_copy_raise() -> None:
    """``milyon`` produces ``milyonmilyon`` (no raise); the raised
    candidate ``milyunmilyon`` is NOT indexed. Confirms the
    Spanish-loan closed-syllable opt-out."""
    idx = _get_default()._index
    assert "milyonmilyon" in idx.nouns
    assert "milyunmilyon" not in idx.nouns


def test_libo_raises_milyon_does_not() -> None:
    """Contrast within the same cell: native vowel-final ``libo``
    raises (``libulibo``), Spanish-loan ``milyon`` does not
    (``milyonmilyon``). The raising is the per-root
    ``redup_o_raise`` flag, not a property of the cell/op."""
    idx = _get_default()._index
    assert "libulibo" in idx.nouns
    assert "libolibo" not in idx.nouns      # libo DID raise
    assert "milyonmilyon" in idx.nouns
    assert "milyunmilyon" not in idx.nouns  # milyon did NOT raise


def test_angaw_native_millions() -> None:
    """``angaw`` is the native primary "millions" form (S&O 1972 p.224 —
    ``angaw-angaw``; the loan ``milyon-milyon`` "less common"). It shares
    COLL_VALUE=MILLIONS with ``milyon`` but carries no ``loan`` field,
    and ends in the glide -aw (no stem /o/), so ``angawangaw`` is the
    only indexed redup surface (no raised ``*angawangaw`` variant to
    consider)."""
    idx = _get_default()._index
    assert "angawangaw" in idx.nouns
    bare = [
        a for a in idx.nouns.get("angaw", [])
        if a.pos == "NOUN" and a.feats.get("REDUP") is None
    ]
    assert len(bare) >= 1, "expected a bare native angaw NOUN"
    assert bare[0].feats.get("COLL_VALUE") == "MILLIONS"


def test_bare_milyon_noun() -> None:
    """The bare ``milyon`` citation analyses as a plain NOUN
    (COLL_VALUE=MILLIONS), unaffected by the card_redup opt-in."""
    analyses = _get_default()._index.nouns.get("milyon", [])
    bare = [
        a for a in analyses
        if a.pos == "NOUN"
        and a.feats.get("MEASURE") is None
        and a.feats.get("REDUP") is None
    ]
    assert len(bare) >= 1, f"expected bare milyon NOUN; got {analyses!r}"
    assert bare[0].lemma == "milyon"
    assert bare[0].feats.get("COLL_VALUE") == "MILLIONS"


# === Hyphenated input flows through merge_hyphen_compounds ============


@pytest.mark.parametrize("hyphenated,merged", [
    ("daan-daan",     "daandaan"),
    ("libu-libo",     "libulibo"),
    ("angaw-angaw",   "angawangaw"),
    ("milyon-milyon", "milyonmilyon"),
])
def test_hyphenated_input_known_surface(
    hyphenated: str, merged: str,
) -> None:
    """Canonical hyphenated input (``libu-libo`` etc.) folds via the
    merge_hyphen_compounds pre-pass to the joined surface the cell
    generates, so the analyzer recognizes it. ``milyon-milyon`` is
    the Phase 10.D addition, paralleling the existing daan-daan /
    libu-libo coverage."""
    from tgllfg.text import merge_hyphen_compounds, split_linker_ng, tokenize
    toks = merge_hyphen_compounds(split_linker_ng(tokenize(hyphenated)))
    assert [t.surface for t in toks] == [merged], (
        f"expected hyphen-merge {hyphenated!r} → [{merged!r}], "
        f"got {[t.surface for t in toks]}"
    )
    assert _get_default().is_known_surface(merged), (
        f"merged surface {merged!r} is not a known surface"
    )
