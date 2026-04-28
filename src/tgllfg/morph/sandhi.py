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
    target of CV-reduplication. ``kain`` → ``ka``; ``alis`` → ``a``;
    ``bili`` → ``bi``."""
    if not s:
        return ""
    if is_vowel(s[0]):
        return s[0]
    for i in range(1, len(s)):
        if is_vowel(s[i]):
            return s[: i + 1]
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
    the root-final vowel is dropped and ``/h/`` is epenthesised:
    ``bili + -in → bilhin``. Otherwise concatenation is direct.
    """
    if not suffix:
        return base
    if base and is_vowel(base[-1]) and is_vowel(suffix[0]):
        return base[:-1] + "h" + suffix
    return base + suffix


def cv_reduplicate(base: str) -> str:
    """Prepend the first CV of ``base`` to itself. ``kain`` →
    ``kakain``; ``alis`` → ``aalis``."""
    return first_cv(base) + base


__all__ = [
    "VOWELS",
    "attach_suffix",
    "cv_reduplicate",
    "first_cv",
    "infix_after_first_consonant",
    "is_vowel",
]
