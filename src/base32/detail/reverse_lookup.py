"""Reverse lookup utilities for the Nix-style base32 alphabet.

Provides a table-based constant-time mapping from base32 characters back
to their numeric digit values.
Invalid characters are consistently mapped to the :data:`INVALID`
sentinel value, enabling efficient checks during decoding.
"""

from .types import INVALID, charset


def build_lookup_table() -> list[int]:
    """Construct the ASCII lookup table for the Nix base32 alphabet.

    Builds a 256-element array mapping every possible 8-bit character
    to its corresponding base32 digit value or :data:`INVALID` if the
    character is not part of the alphabet.

    :returns:
        Table of integer values indexed by character ordinal
        (0..255).
    :rtype: list[int]

    .. important::
       Called automatically at module import to initialize
       :data:`lookup_table`. In normal use this function need not
       be invoked manually.
    """
    result: list[int] = [INVALID] * 256
    for i, ch in enumerate(charset):
        result[ord(ch)] = i
    return result


lookup_table: list[int] = build_lookup_table()
"""Prebuilt lookup table for ASCII → base32 digit mapping.

This table is generated once at import time to provide constant-time
access for all subsequent reverse lookups.

:meta hide-value:
"""


def reverse_lookup(ch: str) -> int | None:
    """Convert a Nix base32 character to its numeric digit index.

    Uses :data:`lookup_table` for a direct translation of the character
    to its digit value. Returns ``None`` for invalid characters.

    :param ch: Single base32 character to convert.
    :type ch: str
    :returns:
        Integer digit index (0..31) or ``None`` if invalid.
    :rtype: int | None

    :example:
        >>> reverse_lookup("a")
        10
        >>> reverse_lookup("?")
        None
    """
    if len(ch) != 1:
        return None

    codepoint = ord(ch)
    if codepoint >= len(lookup_table):
        return None

    digit: int = lookup_table[codepoint]
    return None if digit == INVALID else digit
