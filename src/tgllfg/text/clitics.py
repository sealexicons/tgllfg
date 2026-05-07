# tgllfg/text/clitics.py

"""Token-stream pre-passes between tokenize and morph analysis:

* :func:`split_enclitics` splits hand-marked ``host=enc`` orthography
  (a development convention) into separate host and enclitic tokens.
* :func:`split_linker_ng` splits the bound linker enclitic ``-ng``
  off of vowel-final hosts (``batang`` → ``bata`` + ``-ng``). The
  split is informed by the morph analyzer: a ``Vng`` surface that is
  itself a known full form (e.g. ``bumibilang``, ``darating``) is
  left untouched; only when the full surface is unknown AND the
  stem is known does the split fire. The synthetic ``-ng`` token
  carries that exact surface so it cannot collide with the
  standalone case marker ``ng``.
* :func:`split_apostrophe_t` (Phase 5k Commit 2) merges the
  post-vowel bound-clitic ``'t`` (= contracted ``at`` "and") into a
  synthetic ``at`` token. The tokenizer's ``\\w+|\\S`` regex splits
  ``Maria't`` into three tokens (``Maria`` / ``'`` / ``t``); this
  pre-pass collapses the apostrophe + ``t`` pair into one ``at``
  token routing to the standalone Phase 5k Commit 1 ``at``
  PART[COORD=AND] lex entry.
"""

from __future__ import annotations

import re

from ..core.common import Token

ENCLITICS = {"na", "pa", "ba", "din", "rin", "yata", "man", "daw", "raw", "lang"}

_VOWEL_NG_END = re.compile(r"^(.+[aeiouAEIOU])ng$")


def split_enclitics(tokens: list[Token]) -> list[Token]:
    """Split annotated enclitic attachments of the form
    ``host=enclitic`` (e.g. ``kumain=na``) into two tokens. The
    split fires only when the host is non-empty AND the suffix is a
    known enclitic from :data:`ENCLITICS`; otherwise the token is
    preserved unchanged. This guards against eating the standalone
    ``=`` symbol (the digit-tokenization closing deferral added it
    as a symbolic equality PART for arithmetic) and against the
    pre-2026-05-04 silent drop of the post-``=`` portion when it
    wasn't a recognised enclitic.
    """
    out: list[Token] = []
    for t in tokens:
        if "=" in t.surface:
            base, after = t.surface.split("=", 1)
            if base and after in ENCLITICS:
                out.append(Token(base, base.lower(), t.start, t.start+len(base)))
                out.append(Token(after, after.lower(), t.start+len(base)+1, t.end))
            else:
                out.append(t)
        else:
            out.append(t)
    return out


_VOWELS = "aeiouAEIOU"


def split_apostrophe_t(tokens: list[Token]) -> list[Token]:
    """Merge the post-vowel bound clitic ``'t`` into a synthetic
    ``at`` token.

    The bound clitic ``'t`` is the post-vowel contraction of the
    additive coordinator ``at`` "and" (Phase 5k Commit 1
    PART[COORD=AND]). It surfaces in:

    * NP-level coordination: ``Maria't Juan`` (= ``Maria at Juan``).
    * Coordinated cardinals: ``isa't kalahati`` "one and a half";
      ``apat na pu't lima`` 45; ``isang daan at dalawampu`` 120
      vs ``isang daa't dalawampu``.
    * Other lexicalised doublets where post-vowel ``'t`` joins two
      NPs / NUMs.

    The tokenizer's ``\\w+|\\S`` regex splits ``Maria't`` (or the
    space-separated ``Maria 't``) into three tokens:
    ``[Maria, ', t]``. This pre-pass collapses any
    ``[X, ', t]`` triple where ``X`` ends in a vowel into
    ``[X, at]`` (a synthetic ``at`` token spanning the original
    ``'`` and ``t`` positions). The synthetic token's surface is
    ``at`` so it routes to the same Phase 5k Commit 1 ``at``
    PART[COORD=AND] lex entry as the standalone form.

    Runs before :func:`split_linker_ng` so the synthesised ``at``
    is in place before bound-``-ng`` detection (no interaction in
    practice — ``at`` doesn't end in ``-ng``).
    """
    out: list[Token] = []
    i = 0
    n = len(tokens)
    while i < n:
        host = tokens[i]
        if (
            i + 2 < n
            and tokens[i + 1].surface == "'"
            and tokens[i + 2].norm == "t"
            and host.surface
            and host.surface[-1] in _VOWELS
        ):
            out.append(host)
            ap_start = tokens[i + 1].start
            t_end = tokens[i + 2].end
            out.append(Token(
                surface="at", norm="at",
                start=ap_start, end=t_end,
            ))
            i += 3
        else:
            out.append(host)
            i += 1
    return out


def split_linker_ng(tokens: list[Token]) -> list[Token]:
    """Split the bound linker ``-ng`` from vowel-final hosts.

    The decision rule:

    * If the surface is itself a known full form (verb / noun /
      particle / pronoun in the analyzer index), keep it intact.
      This protects the 122+ verb forms ending in ``Vng``
      (``bumibilang``, ``darating``, ...).
    * Else, if the stem (surface without trailing ``ng``) is a known
      surface, split into stem + synthetic ``-ng`` token.
    * Else, if the n-restored stem (the stem with trailing ``n``
      appended) is a known surface, split into the n-restored stem
      + synthetic ``-ng`` token. This covers the 1sg / 1pl.excl /
      1pl.incl DAT pronoun preposed forms ``aking`` / ``aming`` /
      ``ating`` (from ``akin`` / ``amin`` / ``atin`` via
      n-deletion sandhi before the bound ``-ng`` linker — Phase 5f
      closing deferral on the generic preposed-possessor
      construction).
    * Else, leave intact (will fall through to ``_UNK``).

    The synthetic linker token uses surface ``-ng`` so its morph
    lookup hits the dedicated ``-ng`` particle entry rather than the
    standalone genitive case marker ``ng``.
    """
    from ..morph.analyzer import _get_default

    analyzer = _get_default()
    out: list[Token] = []
    for t in tokens:
        m = _VOWEL_NG_END.match(t.surface)
        if m is None:
            out.append(t)
            continue
        if analyzer.is_known_surface(t.norm):
            out.append(t)
            continue
        stem = m.group(1)
        if analyzer.is_known_surface(stem.lower()):
            stem_end = t.start + len(stem)
            out.append(Token(
                surface=stem, norm=stem.lower(),
                start=t.start, end=stem_end,
            ))
            out.append(Token(surface="-ng", norm="-ng", start=stem_end, end=t.end))
            continue
        # n-deletion sandhi fallback: ``aking`` → ``akin`` + ``-ng``
        # (only fires for the irregular 1sg / 1pl.excl / 1pl.incl
        # DAT pronouns where the linker form drops the stem-final
        # ``n`` rather than being purely additive).
        n_restored = stem + "n"
        if analyzer.is_known_surface(n_restored.lower()):
            stem_end = t.start + len(stem)
            out.append(Token(
                surface=n_restored, norm=n_restored.lower(),
                start=t.start, end=stem_end,
            ))
            out.append(Token(surface="-ng", norm="-ng", start=stem_end, end=t.end))
            continue
        out.append(t)
    return out
