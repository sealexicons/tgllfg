# Copyright (c) 2025-2026 G & R Associates LLC
# SPDX-License-Identifier: MIT OR Apache-2.0

# tgllfg/morph/prefix_policy.py

"""Phase 10.Y orthography policy for CC-final prefix + vowel-initial base.

Tagalog orthography conventionally hyphenates a consonant-final
prefix against a vowel-initial root:

  ``mag-`` + ``aral``  → ``mag-aral``   (S&O 1972, R&G 1981, K&Z 1989,
                                          Kroeger 1991: all hyphenate)
  ``nag-`` + ``uusap`` → ``nag-uusap``
  ``pag-`` + ``aaral`` → ``pag-aaral``  (deverbal nominalization)

Pre-10.Y, the engine plain-concatenated everything (``magaral``,
``naguusap``, ``pagaaral``); the tokenizer accepted hyphenated input
but stripped the hyphen into the ``norm``, so a hyphenated audit
token and a hyphenless engine output mapped to the same lookup key.
This was fine until 10.E.6 surfaced the homophony problem: ``alit``
"quarrel" inflected as ``mag-alit`` / ``nag-alit`` collides with
``galit`` "anger" (the ``ma_adj`` predicative ``magalit`` / past
``nagalit``) under hyphenless concat. 10.E.6 sidestepped it by
adding ``alit`` only as a non-inflecting NOUN→ADJ redup; the full
verb was a named engine follow-on, which is 10.Y.

10.Y splits the closed CC-final prefix set into two policy buckets:

* :data:`HYPHENATED_ONLY_PREFIXES` — the ``mag`` / ``nag`` / ``pag``
  family (8 strings). Every reference uniformly hyphenates these.
  The engine emits hyphenated surfaces ONLY; the surface-index keys
  on the hyphenated form. Hyphenless input no longer resolves.
  This is the disambiguation lever: ``mag-alit`` finds the new
  ``alit`` VERB, but bare ``nagalit`` continues to find ``galit``
  ADJ predicative without spurious ambiguity.

* :data:`DUAL_KEYED_PREFIXES` — the ``maka`` / ``naka`` / ``paki`` /
  ``paka`` / ``mapa`` / ``napa`` / ``makipag`` / ``nakipag`` /
  ``magka`` / ``nagka`` / ``pagka`` family (11 strings). References
  are mixed: S&O 1972 prints ``nakaupo`` / ``naka-upo`` inconsistently,
  Kroeger 1991 prefers hyphenless ``nakaupo``. The engine emits the
  hyphenated form as canonical (matching modern orthography), but
  the surface-index ALSO dual-keys the hyphen-stripped form so
  legacy hyphenless input continues to resolve. ~428 audit-corpus
  surfaces ride this back-compat path.

CV-final prefixes (``ma`` / ``na`` / ``pa`` / ``ka`` / ``i`` /
``si`` / ``tig`` / ``tag`` / ``pinaka`` / ``kasing``) are **out of
scope** — Tagalog never hyphenates these (``mainit`` / ``paaralan``
are universal across all 8 references), so 10.Y leaves them unchanged.
These prefixes don't appear in either set below; :func:`is_cc_final`
returns ``False`` for them.

Phase 10.Y future-flexibility:
  This module is the single source of truth. Flipping policy
  (per-family → tiny-opt-in → strict-hyphenated-only) is a
  ~10-line edit here plus regenerating the surface-string pins
  in ``tests/tgllfg/test_phase10_y_*``. The :mod:`tgllfg.morph.analyzer`
  and :mod:`tgllfg.text.tokenizer` modules import names from here;
  no inline policy logic lives in either consumer.

Alternative policies considered and rejected (preserved here so
future reviews can revisit cheaply):

* **Tiny opt-in** (single 16-surface allow-list) — +16 index entries
  (0.2% growth) instead of +428 (5.6%); same 3 audit-fix cost as
  per-family. Rejected as the doc narrative becomes "back-compat list
  of attested surfaces" (looks ad-hoc) rather than "the maka-family
  is canonically mixed-orthography" (looks principled). Reactive
  maintenance: ~3-5 entries per new audit wave.
* **Strict hyphenated-only** — 0 index growth; 32 audit-token
  regressions to OCR-fix or accept-as-bucket-shift. Cleanest
  semantics; highest audit pressure.
"""

# === Hyphenated-only family (8 prefix strings) ===========================
#
# These prefixes emit the hyphenated form as the *only* canonical surface;
# no back-compat hyphenless key. Used by paradigm cells whose ``op:
# prefix`` value is one of these and whose root is vowel-initial.
HYPHENATED_ONLY_PREFIXES: frozenset[str] = frozenset({
    "mag", "nag", "pag",
    "magpa", "nagpa",
    "magsi", "nagsi",
    "pakikipag",
})

# === Dual-keyed family (11 prefix strings) ===============================
#
# These prefixes emit the hyphenated form as canonical, but the surface
# index also retains the hyphen-stripped key for back-compat with legacy
# hyphenless input. References are mixed on hyphen usage for this family;
# pre-10.Y the engine produced these surfaces hyphenless, and ~428 audit-
# corpus surfaces have hits today under the hyphenless key.
DUAL_KEYED_PREFIXES: frozenset[str] = frozenset({
    "maka", "naka",
    "paka", "paki",
    "mapa", "napa",
    "makipag", "nakipag",
    "magka", "nagka", "pagka",
})

# Union — the full set of prefix strings that take a hyphen against a
# vowel-initial base. Consumers needing a single "should I hyphenate?"
# test use :func:`is_cc_final`.
CC_FINAL_PREFIXES: frozenset[str] = HYPHENATED_ONLY_PREFIXES | DUAL_KEYED_PREFIXES


def is_cc_final(prefix: str) -> bool:
    """Return ``True`` if ``prefix`` is one of the CC-final prefixes that
    canonically hyphenates against a vowel-initial base. ``False`` for
    CV-final (``ma`` / ``na`` / ``pa`` / ``ka`` / ``i`` / ``si``) and
    for any non-prefix string."""
    return prefix in CC_FINAL_PREFIXES


def is_hyphenated_only(prefix: str) -> bool:
    """Return ``True`` if ``prefix`` is in the hyphenated-only family
    (mag/nag/pag and derivatives). Surfaces emitted from cells with
    this prefix index under the hyphenated form ONLY."""
    return prefix in HYPHENATED_ONLY_PREFIXES


def is_dual_keyed(prefix: str) -> bool:
    """Return ``True`` if ``prefix`` is in the dual-keyed family
    (maka/naka/paki and derivatives). Surfaces emitted from cells
    with this prefix index under BOTH hyphenated and hyphen-stripped
    forms."""
    return prefix in DUAL_KEYED_PREFIXES


def is_vowel_initial(base: str) -> bool:
    """Return ``True`` if ``base`` starts with a Tagalog vowel
    (``a/e/i/o/u``, case-insensitive)."""
    return bool(base) and base[0].lower() in "aeiou"


def should_hyphenate(prefix: str, base: str) -> bool:
    """Return ``True`` if a hyphen should be inserted between
    ``prefix`` and ``base`` at engine-output time. The conjunction
    of :func:`is_cc_final` and :func:`is_vowel_initial`."""
    return is_cc_final(prefix) and is_vowel_initial(base)


__all__ = [
    "HYPHENATED_ONLY_PREFIXES",
    "DUAL_KEYED_PREFIXES",
    "CC_FINAL_PREFIXES",
    "is_cc_final",
    "is_hyphenated_only",
    "is_dual_keyed",
    "is_vowel_initial",
    "should_hyphenate",
]
