# fmt: off
"""Type definitions and constants for Nix-style Base32 encoding.

Defines the Nix-specific alphabet, type aliases for valid characters and
strings, and validation logic that ensures Base32 strings contain only
permitted symbols.

The alphabet used here omits ambiguous letters ("e", "o", "u", "t") to
reduce transcription errors, following the Nix convention.
"""

from __future__ import annotations

import typing


def get_args(x: typing.TypeAliasType):
    """Return the underlying arguments of a :class:`typing.TypeAliasType`.

    This helper unpacks the literal arguments from a type alias that
    wraps an internal :data:`typing.Literal`.

    :param x: A :class:`typing.TypeAliasType` object.
    :type x: typing.TypeAliasType
    :returns: Extracted literal arguments sequence.
    :rtype: tuple
    """
    return typing.get_args(x.__value__)


INVALID: int = 0xFF
"""Sentinel integer used for invalid Base32 character mappings."""


# Original reference:
# https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/include/nix/util/base-nix-32.hh#L17
# Note: 'e', 'o', 'u', 't' - omitted to avoid ambiguity.

type NixBase32Char = typing.Literal[
    "0","1","2","3","4","5","6","7",
    "8","9","a","b","c","d","f","g",
    "h","i","j","k","l","m","n","p",
    "q","r","s","v","w","x","y","z"
]
"""Literal type enumerating every valid Nix Base32 character."""


type NixBase32Charset = typing.Literal["".join(get_args(NixBase32Char))]
"""Literal of the full concatenated Nix Base32 alphabet."""

charset: NixBase32Charset = get_args(NixBase32Charset)[0]
"""Canonical string representation of the Nix Base32 alphabet, in order."""


class NixBase32Str(str):
    """Validated string subclass restricted to Nix Base32 characters.

    Instances of this class behave like built-in :class:`str` but cannot
    contain invalid symbols. Construction will raise :class:`ValueError`
    if the input includes any character not in the official Nix alphabet.

    :param value: Base32 string value to validate and store.
    :type value: str
    :raises ValueError: If the input contains any disallowed character.

    :example:
        >>> NixBase32Str("abc123")
        'abc123'
        >>> NixBase32Str("abcd$")  # invalid
        Traceback (most recent call last):
            ...
        ValueError: Invalid Nix base32 string: abcd$
    """

    _allowed: typing.ClassVar[set[str]] = set(charset)

    def __new__(cls, value: str) -> NixBase32Str:  # noqa: PYI034
        if not set(value) <= cls._allowed:
            raise ValueError(f"Invalid Nix base32 string: {value}")
        return super().__new__(cls, value)
