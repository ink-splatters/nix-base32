"""Length computation helpers for Nix Base32 encoding.

These functions mirror the capacity and sizing formulas used by the
official Nix implementation. They allow callers to estimate the output
length of encoded data or the maximum number of bytes that can be safely
decoded from a given Base32 representation.
"""


def encoded_length(n: int) -> int:
    """Compute the number of Nix Base32 characters required to encode ``n`` bytes.

    The calculation uses the formula::

        ceil((n * 8) / 5)

    expressed in integer arithmetic as ``(n * 8 - 1) // 5 + 1``.
    It ensures sufficient capacity even when input length isn't a multiple
    of 5-bits.

    :param n: Number of bytes in the input data.
    :type n: int
    :returns: Number of Base32 characters required to represent the input.
    :rtype: int

    :example:
        >>> encoded_length(1)
        2
        >>> encoded_length(5)
        8
    """
    return (n * 8 - 1) // 5 + 1


def max_decoded_length(n: int) -> int:
    """Compute the maximum number of bytes that may decode from ``n`` Base32 characters.

    This mirrors the logic used in the Nix reference decoder:
    ``ceil(n * 5 / 8)``.
    It yields the upper bound of decoded bytes to aid buffer preallocation.

    :param n: Number of Base32 characters in the encoded input.
    :type n: int
    :returns: Maximum number of bytes that can be decoded.
    :rtype: int

    :example:
        >>> max_decoded_length(2)
        1
        >>> max_decoded_length(8)
        5

    .. seealso::
       **Nix reference implementation:**
       https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/base-nix-32.cc#L45
    """
    # ceil(n * 5 / 8): capacity upper-bound used by the reference decoder
    return (n * 5 + 7) // 8
