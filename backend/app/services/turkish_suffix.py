"""Vowel-harmonized Turkish dative and genitive suffixes for proper nouns.

Character and location names are fixed proper nouns, so suffixes are joined
with an apostrophe (``Fındık'a``, ``Zeytin'in``). Compound place names such as
``Paylaşım Bahçesi`` already end in the third-person possessive suffix
(-ı/-i/-u/-ü directly after a consonant); Turkish grammar buffers those with
``n`` instead of the usual ``y`` (``bahçesine``, not ``bahçesiye``), so that
pattern is detected before falling back to the plain-root buffer rule.
"""

from __future__ import annotations

_TURKISH_LOWER_MAP = str.maketrans(
    {"İ": "i", "I": "ı", "Ç": "ç", "Ğ": "ğ", "Ö": "ö", "Ş": "ş", "Ü": "ü"}
)

_FRONT_UNROUNDED = "ei"
_FRONT_ROUNDED = "öü"
_BACK_UNROUNDED = "aı"
_BACK_ROUNDED = "ou"
_VOWELS = _FRONT_UNROUNDED + _FRONT_ROUNDED + _BACK_UNROUNDED + _BACK_ROUNDED
_POSSESSIVE_TRIGGER_VOWELS = "ıiuü"


def _turkish_lower(word: str) -> str:
    return word.translate(_TURKISH_LOWER_MAP).lower()


def _last_vowel(word: str) -> str:
    lowered = _turkish_lower(word)
    for char in reversed(lowered):
        if char in _VOWELS:
            return char
    raise ValueError(f"'{word}' has no vowel to derive a Turkish suffix from.")


def _ends_with_third_person_possessive(word: str) -> bool:
    """Detect the -ı/-i/-u/-ü possessive suffix, e.g. in ``Ağacı`` or ``Bahçesi``."""
    lowered = _turkish_lower(word)
    if len(lowered) < 2 or lowered[-1] not in _POSSESSIVE_TRIGGER_VOWELS:
        return False
    return lowered[-2] not in _VOWELS


def dative_suffix(name: str) -> str:
    """Return the dative suffix (-a/-e) with its buffer consonant, if any."""
    vowel = _last_vowel(name)
    suffix_vowel = "e" if vowel in _FRONT_UNROUNDED + _FRONT_ROUNDED else "a"
    lowered = _turkish_lower(name)
    if lowered[-1] not in _VOWELS:
        buffer = ""
    elif _ends_with_third_person_possessive(name):
        buffer = "n"
    else:
        buffer = "y"
    return f"{buffer}{suffix_vowel}"


def genitive_suffix(name: str) -> str:
    """Return the genitive suffix (-in/-ın/-un/-ün) with its buffer consonant, if any."""
    vowel = _last_vowel(name)
    if vowel in _FRONT_UNROUNDED:
        suffix = "in"
    elif vowel in _FRONT_ROUNDED:
        suffix = "ün"
    elif vowel in _BACK_UNROUNDED:
        suffix = "ın"
    else:
        suffix = "un"
    buffer = "n" if _turkish_lower(name)[-1] in _VOWELS else ""
    return f"{buffer}{suffix}"


def to_dative(name: str) -> str:
    """Format a proper noun with an apostrophe and its dative suffix, e.g. ``Fındık'a``."""
    return f"{name}'{dative_suffix(name)}"


def to_genitive(name: str) -> str:
    """Format a proper noun with an apostrophe and its genitive suffix, e.g. ``Zeytin'in``."""
    return f"{name}'{genitive_suffix(name)}"
