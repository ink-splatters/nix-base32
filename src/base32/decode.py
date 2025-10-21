"""base32 decoding utility following the Nix variant.

Implements :func:`decode`, the inverse of
:func:`base32.encode`.
"""

from .detail import NixBase32Str, max_decoded_length, reverse_lookup


def decode(s: NixBase32Str) -> bytes:
    """Decode a Nix base32 string back into the original bytes.

    The algorithm reverses :func:`base32.encode`, consuming bits
    five at a time from LSB to MSB (right to left).

    :param s: Nix base32 string to decode.
    :type s: base32.detail.types.NixBase32Str
    :returns: Original binary data represented by ``s``.
    :rtype: bytes
    :raises ValueError: If the string contains invalid base32 symbol(s).

    :example:
        >>> from base32 import encode, decode
        >>> s = encode(b"hi")
        >>> s
        NixBase32Str('nbqwcid')
        >>> decode(s)
        b'hi'
    """
    if not s:
        return b""

    # Upper-bound capacity = ceil(len(s) * 5 / 8)
    cap = max_decoded_length(len(s))
    out = bytearray(cap)
    used = 0

    for n, ch in enumerate(reversed(s)):
        digit = reverse_lookup(ch)
        if digit is None:
            raise ValueError(f"invalid character {ch!r}")

        b = n * 5
        i = b // 8
        j = b % 8

        out[i] = (out[i] | ((digit << j) & 0xFF)) & 0xFF
        if used < i + 1:
            used = i + 1

        # If 5-bit group crosses byte boundary, spill over.
        if j and (digit >> (8 - j)):
            out[i + 1] = (out[i + 1] | (digit >> (8 - j))) & 0xFF
            if used < i + 2:
                used = i + 2

    return bytes(out[:used])
