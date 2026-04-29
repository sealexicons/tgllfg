# tgllfg/morph/sandhi.py

"""Phonological rewrites applied during paradigm generation.

Two rules are baked into the engine for the seed slice; broader
sandhi (nasal substitution under ``mang-`` / ``pang-``, full-root
reduplication interactions, stress-conditioned alternations) is
deferred to the scale-up branch.

* **Vowel-hiatus repair**: when a vowel-final base meets a
  vowel-initial suffix (``-in``, ``-an``), the root-final vowel is
  dropped and ``/h/`` is epenthesised. Schachter–Otanes 1972 §4.21
  describes both the ``-h-`` (epenthesis) and ``Ø`` (deletion)
  variants; the seed picks the dominant epenthesis variant
  (``bili + -in → bilhin``).
* **First-consonant location**: a small helper used by infixation.
  Vowel-initial bases take ``-um-`` / ``-in-`` as a *prefix* rather
  than an infix.
"""

from __future__ import annotations

VOWELS: frozenset[str] = frozenset("aeiouAEIOU")


def is_vowel(c: str) -> bool:
    return c in VOWELS


def first_cv(s: str) -> str:
    """Return the first CV (or just V) of ``s``: the chunk used as the
    target of CV-reduplication.

    The first consonant alone (skipping any rest of an onset cluster)
    plus the first vowel: ``kain`` → ``ka``, ``bili`` → ``bi``,
    ``alis`` → ``a``, ``trabaho`` → ``ta`` (skipping the ``r`` of the
    onset cluster, per the standard Tagalog redup rule). Vowel-initial
    bases redup just the leading vowel.

    The orthographic digraph ``ng`` is treated as a single consonant
    /ŋ/, so a base like ``nguha`` (the post-nasal-substitution form
    of ``kuha``) reduplicates to ``ngunguha`` rather than the
    erroneous ``nunguha``.
    """
    if not s:
        return ""
    if is_vowel(s[0]):
        return s[0]
    # Digraph ng (one consonant /ŋ/).
    if s[:2].lower() == "ng":
        for i in range(2, len(s)):
            if is_vowel(s[i]):
                return s[:2] + s[i]
        return s[:2]
    # Single-letter consonant onset.
    for i in range(1, len(s)):
        if is_vowel(s[i]):
            return s[0] + s[i]
    return s  # all consonants — degenerate


def infix_after_first_consonant(base: str, infix: str) -> str:
    """Insert ``infix`` after the first consonant of ``base``. If
    ``base`` is vowel-initial, prepend ``infix`` instead (the
    standard Tagalog rule for ``-um-`` / ``-in-`` on vowel-initial
    roots)."""
    if not base:
        return infix
    if is_vowel(base[0]):
        return infix + base
    return base[0] + infix + base[1:]


def attach_suffix(base: str, suffix: str) -> str:
    """Append ``suffix`` to ``base`` with vowel-hiatus repair.

    If ``base`` ends in a vowel and ``suffix`` begins with a vowel,
    ``/h/`` is epenthesised between them: ``basa + -in → basahin``,
    ``bili + -in → bilihin``, ``gawa + -in → gawahin``. Otherwise
    concatenation is direct.

    Schachter & Otanes 1972 §4.21 documents both this h-epenthesis
    pattern and an optional high-vowel deletion (``bili + -in →
    bilhin``) for high-vowel stems; the engine standardises on the
    epenthesis-only pattern (the more conservative form found in
    formal registers and consistently in Ramos & Bautista 1986).
    The colloquial deletion variant can be added per-root via a
    sandhi rule when needed.
    """
    if not suffix:
        return base
    if base and is_vowel(base[-1]) and is_vowel(suffix[0]):
        return base + "h" + suffix
    return base + suffix


def cv_reduplicate(base: str) -> str:
    """Prepend the first CV of ``base`` to itself. ``kain`` →
    ``kakain``; ``alis`` → ``aalis``."""
    return first_cv(base) + base


# Nasal-substitution table for the mang-/pang-/nang- prefixes. The
# prefix's final ``ng`` adapts its place of articulation to the
# base's initial consonant, which then drops. The keys are the
# initial-consonant set; the values are the substituted nasal.
#
# Citations: Schachter & Otanes 1972 §3.5 (sandhi); Kroeger 1993
# §4.4 (mang- distributive).
_NASAL_SUBSTITUTION: dict[str, str] = {
    "p": "m", "b": "m",
    "t": "n", "d": "n", "s": "n",
    "k": "ng", "g": "ng",
}


def nasal_substitute(base: str) -> str:
    """Apply nasal substitution to ``base`` for ng-final prefixes
    (``mang-`` / ``nang-`` / ``pang-``).

    The base's first consonant is replaced by the homorganic nasal
    that would appear at the prefix-base boundary:

    * ``bili`` → ``mili``  (b → m)
    * ``tahi`` → ``nahi``  (t → n)
    * ``kuha`` → ``nguha`` (k → ng)

    Bases beginning with a sonorant (``l``, ``m``, ``n``, ``r``,
    ``h``, ``y``, ``w``) or a vowel are returned unchanged. The
    caller is responsible for prepending the prefix head (e.g.
    ``ma-`` from ``mang-``) afterwards.
    """
    if not base:
        return base
    initial = base[0].lower()
    if initial in _NASAL_SUBSTITUTION:
        return _NASAL_SUBSTITUTION[initial] + base[1:]
    return base


__all__ = [
    "VOWELS",
    "attach_suffix",
    "cv_reduplicate",
    "first_cv",
    "infix_after_first_consonant",
    "is_vowel",
    "nasal_substitute",
]
