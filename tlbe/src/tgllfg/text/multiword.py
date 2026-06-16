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
from ..morph.prefix_policy import is_vowel_initial


def merge_multiword_compounds(tokens: list[Token]) -> list[Token]:
    """Collapse a run of tokens whose lowercased space-joined norms match a
    registered multi-word expression into a single token, longest-match-first.

    The MWE inventory is data-driven (``data/tgl/mwe.yaml``, surfaced as
    :meth:`tgllfg.morph.analyzer.Analyzer.multiword_norms`) and **n-gram**:
    ``oras Pilipino`` / ``ibig sabihin`` are bigrams, ``parang kailan lang`` is
    a trigram. (Phase 14.final.post-12 replaced the hardcoded bigram-only
    ``_MULTIWORD_NORMS`` set + split ``nouns.yaml`` companions with this.)

    The merged token preserves the original whitespace-separated surface form
    (so ``oras Pilipino`` keeps its capitalization + word boundary) and uses
    the joined-with-space lowercased form as its norm — the same key the
    analyzer indexes the MWE's ``MorphAnalysis`` under, so ``analyze_one``
    finds it directly. Sentence-internal merges only; the merged token spans
    the first token's ``start`` to the last token's ``end``.
    """
    from ..morph.analyzer import _get_default

    norms = _get_default().multiword_norms()
    if not norms:
        return tokens
    max_n = max(len(s.split()) for s in norms)
    out: list[Token] = []
    i = 0
    n = len(tokens)
    while i < n:
        merged = False
        # Longest window first so a trigram MWE wins over a bigram prefix it
        # contains (and so two adjacent MWEs don't mis-merge across the seam).
        for k in range(min(max_n, n - i), 1, -1):
            window = tokens[i:i + k]
            joined_norm = " ".join(t.norm for t in window)
            if joined_norm in norms:
                out.append(Token(
                    surface=" ".join(t.surface for t in window),
                    norm=joined_norm,
                    start=window[0].start,
                    end=window[-1].end,
                ))
                i += k
                merged = True
                break
        if not merged:
            out.append(tokens[i])
            i += 1
    return out


def _split_cc_prefix(text: str) -> tuple[str, str] | None:
    """Phase 10.Y helper. If ``text`` is a hyphenless CC-final-prefix +
    vowel-initial-stem form (``nagarte`` = ``nag`` + ``arte``;
    ``nakaupo`` = ``naka`` + ``upo``), return the ``(prefix, base)``
    split. Otherwise return ``None``. Used by
    :func:`merge_hyphen_compounds` to try a hyphen-inserted variant
    of an unrecognized hyphenless join when the analyzer's surface
    index keys the form hyphenated. The closed
    :data:`tgllfg.morph.prefix_policy.CC_FINAL_PREFIXES` set is
    iterated longest-first to avoid ambiguous splits (``nakipag``
    before ``nak`` etc.).
    """
    from ..morph.prefix_policy import CC_FINAL_PREFIXES
    for prefix in sorted(CC_FINAL_PREFIXES, key=len, reverse=True):
        if (
            text.startswith(prefix)
            and len(text) > len(prefix)
            and is_vowel_initial(text[len(prefix):])
        ):
            return prefix, text[len(prefix):]
    return None


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
            # Phase 10.Y: when ``x`` is itself a CC-final-prefix + vowel-
            # initial-stem form (``Nagarte`` = ``nag`` + ``arte``), the
            # analyzer index now keys the inflected-moderative output
            # under the hyphenated canonical form (``nag-artearte``,
            # not ``nagartearte``). The hyphenless ``joined`` above
            # doesn't hit; try the hyphen-inserted variant too. The
            # hyphen-insertion split is unambiguous because
            # :data:`CC_FINAL_PREFIXES` is a closed set and the regex
            # matches longest-first.
            prefix_split = _split_cc_prefix(x.surface.lower())
            if prefix_split is not None:
                prefix, base = prefix_split
                joined_with_hyphen = f"{prefix}-{base}{y.surface.lower()}"
                if analyzer.is_known_surface(joined_with_hyphen):
                    # Preserve x.surface's original casing on the
                    # emitted surface (mirrors the bare-join path's
                    # ``surface=joined`` convention).
                    cased_x_prefix = x.surface[: len(prefix)]
                    cased_x_base = x.surface[len(prefix):]
                    emitted_surface = (
                        f"{cased_x_prefix}-{cased_x_base}{y.surface}"
                    )
                    out.append(Token(
                        surface=emitted_surface,
                        norm=joined_with_hyphen,
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
