# fmt: off
"""Type definitions and constants for Nix-style base32 encoding.

Defines the Nix-specific alphabet, type aliases for valid characters and
strings, and validation logic that ensures base32 strings contain only
permitted symbols.

The alphabet used here omits ambiguous letters ("e", "o", "u", "t") to
reduce transcription errors, following the Nix convention.
"""


from typing import ClassVar, Literal, get_args

INVALID: int = 0xFF
"""Sentinel integer used for invalid base32 character mappings."""

# Original reference:
# https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/include/nix/util/base-nix-32.hh#L17
# Note: 'e', 'o', 'u', 't' - omitted to avoid ambiguity.

type NixBase32Charset = Literal["0123456789abcdfghijklmnpqrsvwxyz"]
"""Literal of the full concatenated Nix base32 alphabet."""

charset: NixBase32Charset = get_args(NixBase32Charset.__value__)[0]
"""Canonical string representation of the Nix base32 alphabet, in order."""


class NixBase32Str(str):
    """Validated string subclass restricted to Nix base32 characters.

    Instances of this class behave like built-in :class:`str` but cannot
    contain invalid symbols. Construction will raise :class:`ValueError`
    if the input includes any character not in the official Nix alphabet.

    :param value: base32 string value to validate and store.
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

    _allowed: ClassVar[set[str]] = set(charset)

    def __new__(cls, value: str) -> NixBase32Str:  # noqa: PYI034
        if not set(value) <= cls._allowed:
            raise ValueError(f"Invalid Nix base32 string: {value}")
        return super().__new__(cls, value)
