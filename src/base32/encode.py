"""base32 encoding following the Nix variant semantics.

This module defines :func:`encode`, which converts arbitrary byte
strings into a :class:`~base32.detail.types.NixBase32Str`.

The algorithm mirrors the Nix implementation.
"""

from .detail import NixBase32Str, charset, encoded_length


def encode(bs: bytes) -> NixBase32Str:
    """Encode a byte sequence into a Nix base32 string.

    Each group of five bits in ``bs`` is mapped to a single
    character from the Nix base32 alphabet. The result omits
    padding characters and is guaranteed to roundtrip through
    :func:`base32.decode`.

    :param bs: Bytes to encode.
    :type bs: bytes
    :returns: base32 string representation.
    :rtype: base32.detail.types.NixBase32Str

    :example:
        >>> from base32 import encode
        >>> encode(b"foo")
        NixBase32Str('mzxw6')
        >>> encode(b"")
        NixBase32Str('')
    .. seealso::
       **Nix reference implementation:**
       https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/base-nix-32.cc#L20
    """
    if not bs:
        return NixBase32Str("")

    length = encoded_length(len(bs))
    out: list[str] = []

    #  Walk 5-bit groups from MSB to LSB.
    for n in reversed(range(length)):
        b = n * 5
        i = b // 8
        j = b % 8

        b1 = bs[i]
        b2 = bs[i + 1] if i + 1 < len(bs) else 0
        c = ((b1 >> j) | ((b2 << (8 - j)) & 0xFF)) & 0xFF
        out.append(charset[c & 0x1F])

    return NixBase32Str("".join(out))
