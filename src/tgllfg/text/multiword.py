# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/text/multiword.py

"""Pre-parse multiword recognition.

Tokens that the canonical orthography writes with an internal hyphen
(``tag-init``, ``daan-daan``, ``humigit-kumulang``, ``tig-isa``,
``kani-kaniya``, ...) tokenize via the default ``\\w+|\\S`` regex as
three separate tokens (``X``, ``-``, ``Y``). The seed lex carries
the canonical *single*-token form (``taginit``, ``daandaan``, ...)
so the morph analyzer's hash-keyed lookup can find it. This module's
:func:`merge_hyphen_compounds` runs as a pre-parse pass to bridge
the two: it collapses ``X``, ``-``, ``Y`` into a single ``XY`` token
when ``XY`` is a known surface in the analyzer index, leaving every
other ``X-Y`` triple alone (notably the symbolic-arithmetic ``5 - 3``
where both sides are digits and the joined form would not be a
compound noun in the lex).

The plan §18 entry on hyphenated lex items called this out as a
post-Phase-5f closing deferral covering Phase 5f Commits 14
(seasons), 16 (``humigit-kumulang`` approximator), 18 (collective
numerals), 19 (distributive cardinals), and 21 (distributive-
possessive). All five constructions are unlocked by the same
single-pass merge — no productive paradigm-engine work needed at
this layer (productive ``tag-`` / ``tig-`` / ``card_redup`` /
``kani-`` paradigms are a separate deferral).
"""

from ..core.common import Token


# Phase 10.J.post-12.4 — multi-word fixed expressions (MWEs) recognized
# as a single token after tokenization. Each entry is the lowercased
# bigram of norms; the merged token's surface preserves the original
# whitespace-separated form and its norm becomes the same joined-with-
# space lowercased string (which matches the analyzer's index key for
# multi-word citations in nouns.yaml).
#
# Per user dialog 2026-05-31 (linguistic guidance):
#
# * ``oras Pilipino``  — lexicalized MWE for "Filipino time" (idiomatic
#   for habitual lateness). Non-compositional; ``oras Amerikano`` /
#   ``oras Hapones`` are not parallel cultural concepts. Treated as a
#   NOUN MWE (analogous to English ``red tape``, ``brain drain``).
#
# * ``ibig sabihin`` — productive verbal/light-verb expression "mean,
#   signify". The form admits clitic interpolation in productive use
#   (``ang ibig kong sabihin`` "what I mean"), but every audit-attested
#   surface is contiguous (PANAHON/sent-41 + wave2-rg-int sent-446 +
#   sent-1256). The contiguous form is registered as a NOUN MWE so it
#   composes with the headless-DP construction ``ang + N → NP[NOM]``;
#   the productive non-contiguous form is future work (STATIVE-VERB
#   + OV-INF complement infrastructure not yet implemented).
_MULTIWORD_NORMS: set[str] = {
    "oras pilipino",
    "ibig sabihin",
}


def merge_multiword_compounds(tokens: list[Token]) -> list[Token]:
    """Collapse bigrams of (token[i], token[i+1]) whose lowercased
    space-joined norms match a registered :data:`_MULTIWORD_NORMS`
    entry into a single token.

    The merged token preserves the original whitespace-separated
    surface form (so ``oras Pilipino`` doesn't lose the capitalization
    or word boundary) and uses the joined-with-space lowercased form
    as its norm. The analyzer's noun-citation index is keyed on
    ``citation.lower()`` (see :meth:`tgllfg.morph.analyzer.Analyzer._build_index`),
    so a NOUN lex entry with citation ``oras Pilipino`` is found
    directly by the joined norm.

    Sentence-internal merges only — leading / trailing whitespace
    around the matched pair is implicit (each token's ``start``/``end``
    bounds are preserved, with the merged token spanning ``a.start``
    to ``b.end``).
    """
    out: list[Token] = []
    i = 0
    n = len(tokens)
    while i < n - 1:
        joined_norm = f"{tokens[i].norm} {tokens[i + 1].norm}"
        if joined_norm in _MULTIWORD_NORMS:
            out.append(Token(
                surface=f"{tokens[i].surface} {tokens[i + 1].surface}",
                norm=joined_norm,
                start=tokens[i].start,
                end=tokens[i + 1].end,
            ))
            i += 2
            continue
        out.append(tokens[i])
        i += 1
    if i < n:
        out.append(tokens[i])
    return out


def merge_hyphen_compounds(tokens: list[Token]) -> list[Token]:
    """Collapse ``X``, ``-``, ``Y`` token triples into a single
    ``XY`` token when both flanking tokens are alphabetic and the
    joined form is a known surface in the analyzer index.

    When the right flanker carries the bound ``-ng`` linker
    (``kani-kaniyang``, ``daan-daang``, ``humigit-kumulang`` —
    note the last one's ``-ng`` is part of the lex entry, not the
    bound linker), the merge tries both the literal join and a
    join-with-``ng``-stripped form. If only the stripped form is
    known, the merge emits two tokens: the merged compound and a
    synthetic ``-ng`` linker token (mirroring
    :func:`split_linker_ng`'s emit shape) so the downstream
    grammar sees a uniform ``Compound + PART[LINK=NG]``
    sequence.

    Symbolic-arithmetic ``-`` between digits is preserved because
    both flanking tokens fail the ``isalpha()`` check; non-canonical
    hyphenated compounds (``Mr-Juan``, ``foo-bar``) are preserved
    because neither variant of the joined form is in the lex.
    """
    from ..morph.analyzer import _get_default

    analyzer = _get_default()
    out: list[Token] = []
    i = 0
    n = len(tokens)
    while i < n:
        if (
            i + 2 < n
            and tokens[i + 1].surface == "-"
            and tokens[i].surface.isalpha()
            and tokens[i + 2].surface.isalpha()
        ):
            x = tokens[i]
            y = tokens[i + 2]
            joined = x.surface + y.surface
            if analyzer.is_known_surface(joined.lower()):
                out.append(Token(
                    surface=joined,
                    norm=joined.lower(),
                    start=x.start,
                    end=y.end,
                ))
                i += 3
                continue
            # Bound -ng linker carve-out: ``kani-kaniyang`` →
            # ``kanikaniya`` + synthetic ``-ng`` linker token.
            if y.surface.lower().endswith("ng") and len(y.surface) > 2:
                y_stem = y.surface[:-2]
                joined_stem = x.surface + y_stem
                if analyzer.is_known_surface(joined_stem.lower()):
                    stem_end = x.start + len(x.surface) + 1 + len(y_stem)
                    out.append(Token(
                        surface=joined_stem,
                        norm=joined_stem.lower(),
                        start=x.start,
                        end=stem_end,
                    ))
                    out.append(Token(
                        surface="-ng",
                        norm="-ng",
                        start=stem_end,
                        end=y.end,
                    ))
                    i += 3
                    continue
        out.append(tokens[i])
        i += 1
    return out
