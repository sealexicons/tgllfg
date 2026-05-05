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

from __future__ import annotations

from ..core.common import Token


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
