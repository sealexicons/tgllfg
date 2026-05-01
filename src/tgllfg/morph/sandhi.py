# tgllfg/morph/sandhi.py

"""Phonological rewrites applied during paradigm generation.

The Phase 2 baseline covered vowel-hiatus repair, first-CV onset
location (with the orthographic ``ng`` digraph), nasal substitution
under ``mang-``/``pang-``, and the rule that vowel-initial bases take
``-um-``/``-in-`` as a prefix rather than an infix. Phase 2C adds the
five rules that were previously documented as deferred:

* **o → u stem-vowel raising** on suffixation. Automatic: when a
  suffix is attached, the last /o/ in the stem (the final-syllable
  vowel) raises to /u/. ``inom + -in → inumin``,
  ``putol + -in → putulin``. Schachter & Otanes 1972 §4.21.
* **/d/ → /r/ intervocalic alternation**. Per-root opt-in via the
  ``d_to_r`` sandhi flag. Applied as a post-processor after all other
  operations: ``dating + cv_redup → dadating → darating``.
* **High-vowel deletion variant** of suffix attachment. Per-root
  opt-in via the ``high_vowel_deletion`` sandhi flag. Stems ending
  in /i/ or /u/ + a vowel-initial suffix delete the stem-final
  vowel and keep the epenthesised /h/: ``bili + -in → bilhin``
  rather than the formal ``bilihin``.
* **Sonorant-initial -in- → ni-** prefix variant. Automatic: when
  the realis ``-in-`` infix targets a base beginning with a
  sonorant (m, n, ng, l, r, w, y, h), it surfaces as the ``ni-``
  prefix. ``linis + -in- → nilinis`` rather than ``linilis``.
* **ma- non-volitional / stative** (``MOOD: NVOL``) is added at the
  paradigm level — see ``data/tgl/paradigms.yaml`` for the new
  ``ma`` affix-class cells.

Citations: Schachter & Otanes 1972 §4.21 (vowel hiatus / deletion;
o→u raising); §3.5 (sandhi); Kroeger 1993 §4.4 (mang- distributive,
nasal substitution); Ramos & Bautista 1986 paradigm tables.
"""

from __future__ import annotations

VOWELS: frozenset[str] = frozenset("aeiouAEIOU")
SONORANTS: frozenset[str] = frozenset("mnlrwyMNLRWY")


def is_vowel(c: str) -> bool:
    return c in VOWELS


def is_sonorant_initial(base: str) -> bool:
    """Return True if ``base`` begins with a sonorant consonant
    (m, n, ng-as-/ŋ/, l, r, w, y).

    /h/ is *not* counted: although phonetically a sonorant in some
    analyses, the realis -in- infix surfaces normally on /h/-initial
    bases (``hampas + -in- → hinampas``, not ``*ninampas``).
    """
    if not base:
        return False
    if base[:2].lower() == "ng":
        return True
    return base[0] in SONORANTS


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
    """Insert ``infix`` after the first consonant of ``base``.

    Three structural exceptions:

    * Vowel-initial bases prepend ``infix`` (the standard Tagalog rule
      for ``-um-`` / ``-in-`` on vowel-initial roots).
    * The orthographic digraph ``ng`` is treated as a single consonant
      /ŋ/, so ``ngiti + -um- → ngumiti`` (not the erroneous
      ``*numgiti``).
    * Sonorant-initial bases take the realis ``-in-`` as a ``ni-``
      *prefix* rather than an infix. This is automatic for the ``in``
      infix value; ``-um-`` is unaffected. ``linis + -in- → nilinis``;
      ``mahal + -in- → nimahal``.
    """
    if not base:
        return infix
    if is_vowel(base[0]):
        return infix + base
    if infix == "in" and is_sonorant_initial(base):
        return "ni" + base
    if base[:2].lower() == "ng":
        return base[:2] + infix + base[2:]
    return base[0] + infix + base[1:]


def _raise_final_o(stem: str) -> str:
    """Raise the final-syllable /o/ of ``stem`` to /u/.

    Walks back from the end of the stem to the last vowel; if it is
    ``o`` (or ``O``), replace it with ``u`` (or ``U``); otherwise
    return the stem unchanged. Phase 2C automatic rule, applied at
    suffix-attachment time only — bare-stem and reduplicated-stem
    surfaces keep their /o/.
    """
    for i in range(len(stem) - 1, -1, -1):
        ch = stem[i]
        if ch in VOWELS:
            if ch == "o":
                return stem[:i] + "u" + stem[i + 1 :]
            if ch == "O":
                return stem[:i] + "U" + stem[i + 1 :]
            return stem
    return stem


def attach_suffix(base: str, suffix: str, *, high_vowel_deletion: bool = False) -> str:
    """Append ``suffix`` to ``base`` with vowel-hiatus repair plus
    Phase 2C extensions.

    Always:

    * If the stem's final-syllable vowel is /o/, raise it to /u/
      (``inom + -in → inumin``, ``putol + -in → putulin``).

    Default vowel-hiatus repair (h-epenthesis): when the stem ends
    in a vowel and the suffix begins with a vowel, an ``h`` is
    epenthesised: ``basa + -in → basahin``, ``bili + -in → bilihin``.

    Per-root opt-in via ``high_vowel_deletion=True``: stems ending
    in a *high* vowel (/i/ or /u/) instead delete the stem-final
    vowel; the ``h`` survives. ``bili + -in → bilhin``,
    ``buksu + -in → bukshin``. Other vowel-final stems still take
    the standard h-epenthesis. C-final stems concatenate directly.

    Schachter & Otanes 1972 §4.21 documents both the formal
    h-epenthesis pattern and the colloquial deletion variant; the
    flag picks the variant per root.
    """
    if not suffix:
        return base
    base = _raise_final_o(base)
    if base and is_vowel(base[-1]) and is_vowel(suffix[0]):
        if high_vowel_deletion and base[-1].lower() in "iu":
            return base[:-1] + "h" + suffix
        return base + "h" + suffix
    return base + suffix


def cv_reduplicate(base: str) -> str:
    """Prepend the first CV of ``base`` to itself. ``kain`` →
    ``kakain``; ``alis`` → ``aalis``."""
    return first_cv(base) + base


def d_to_r_intervocalic(form: str) -> str:
    """Replace each /d/ in ``form`` with /r/ when it is between two
    vowels. Per-root opt-in via the ``d_to_r`` sandhi flag.

    ``dadating → darating``; ``lakadin → lakarin``. Does not apply
    when the /d/ is word-initial, word-final, or adjacent to a
    consonant — those positions retain /d/.
    """
    if not form:
        return form
    out: list[str] = []
    for i, ch in enumerate(form):
        if ch in ("d", "D") and 0 < i < len(form) - 1:
            if is_vowel(form[i - 1]) and is_vowel(form[i + 1]):
                out.append("r" if ch == "d" else "R")
                continue
        out.append(ch)
    return "".join(out)


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


def nasal_assim_prefix(prefix: str, base: str) -> str:
    """Prepend ``prefix`` (which must end in the orthographic ``ng``
    digraph) to ``base``, place-assimilating the prefix's final
    nasal to the base's first consonant **without** dropping that
    consonant.

    Distinguished from :func:`nasal_substitute`, which DROPS the
    base's first consonant (the historical mang-/nang-/pang- AV
    distributive pattern: ``mang-`` + ``bili`` → ``mamili``). The
    instrumental applicative ``ipang-`` and analogous formations
    retain the consonant: ``pang-`` + ``bili`` → ``pambili``
    (later → ``ipinambili``). The two patterns coexist on the
    same root in modern Tagalog with different meanings.

    Examples (with ``prefix="pang"``):

    * ``bili``  → ``pambili``   (ng → m, b retained)
    * ``tahi``  → ``pantahi``   (ng → n, t retained)
    * ``kuha``  → ``pangkuha``  (ng → ng [vacuous], k retained)
    * ``ulan``  → ``pangulan``  (vowel-initial, no assimilation)
    * ``lakad`` → ``panglakad`` (sonorant-initial, no assimilation)

    The prefix MUST end in ``"ng"`` (digraph for /ŋ/); the function
    treats the last two characters as the assimilation site.
    """
    if not prefix.endswith("ng"):
        raise ValueError(
            f"nasal_assim_prefix requires an ng-final prefix; got {prefix!r}"
        )
    if not base:
        return prefix
    initial = base[0].lower()
    head = prefix[:-2]  # drop the final "ng"
    nasal = _NASAL_SUBSTITUTION.get(initial, "ng")
    return head + nasal + base


__all__ = [
    "SONORANTS",
    "VOWELS",
    "attach_suffix",
    "cv_reduplicate",
    "d_to_r_intervocalic",
    "first_cv",
    "infix_after_first_consonant",
    "is_sonorant_initial",
    "is_vowel",
    "nasal_assim_prefix",
    "nasal_substitute",
]
