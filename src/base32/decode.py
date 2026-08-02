"""base32 decoding utility following the Nix variant.

Implements :func:`decode`, the inverse of
:func:`base32.encode`.
"""

from typing import TYPE_CHECKING, BinaryIO, TextIO

from .detail import NixBase32Str, max_decoded_length, reverse_lookup

if TYPE_CHECKING:
    from collections.abc import Iterator


def decode(s: str | NixBase32Str) -> bytes:
    """Decode a Nix base32 string back into the original bytes.

    The algorithm reverses :func:`base32.encode`, consuming bits
    five at a time from LSB to MSB (right to left).

    :param s: Nix base32 string to decode.
    :type s: str | base32.detail.types.NixBase32Str
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


def decode_iter(s: str | NixBase32Str, chunk_size: int = 8192) -> Iterator[bytes]:
    """Decode a Nix base32 string and yield output in chunks.

    This is useful for memory-efficient writing of large decoded data.
    The decoding itself requires the full input, but output is yielded
    in manageable chunks.

    :param s: Nix base32 string to decode.
    :param chunk_size: Maximum bytes per yielded chunk.
    :yields: Bytes chunks of the decoded output.
    :raises ValueError: If the string contains invalid base32 symbol(s).

    :example:
        >>> for chunk in decode_iter("0" * 1000, chunk_size=100):
        ...     print(len(chunk))  # Each chunk <= 100 bytes
    """
    decoded = decode(s)
    for i in range(0, len(decoded), chunk_size):
        yield decoded[i : i + chunk_size]


def decode_to_stream(
    s: str | NixBase32Str,
    writer: BinaryIO,
    *,
    chunk_size: int = 8192,
) -> int:
    """Decode a Nix base32 string and write to a binary stream.

    :param s: Nix base32 string to decode.
    :param writer: Binary stream to write decoded output to.
    :param chunk_size: Write buffer size in bytes.
    :returns: Number of bytes written.
    :raises ValueError: If the string contains invalid base32 symbol(s).

    :example:
        >>> import io
        >>> buf = io.BytesIO()
        >>> decode_to_stream("nbswy3dp", buf)
        5
        >>> buf.getvalue()
        b'hello'
    """
    written = 0
    for chunk in decode_iter(s, chunk_size):
        writer.write(chunk)
        written += len(chunk)
    return written


def decode_stream(
    reader: TextIO,
    writer: BinaryIO,
    *,
    chunk_size: int = 8192,
    strip: bool = True,
) -> int:
    """Read base32 text from a stream, decode, and write to binary stream.

    .. note::
        Due to the Nix base32 algorithm processing characters in reverse
        order, the full input must be buffered before decoding.
        This function provides streaming I/O but not streaming computation.

    :param reader: Text stream to read base32 input from.
    :param writer: Binary stream to write decoded output to.
    :param chunk_size: I/O buffer size.
    :param strip: Whether to strip whitespace from input (default True).
    :returns: Number of bytes written.
    :raises ValueError: If the input contains invalid base32 symbol(s).

    :example:
        >>> import io
        >>> inp = io.StringIO("nbswy3dp")
        >>> out = io.BytesIO()
        >>> decode_stream(inp, out)
        5
        >>> out.getvalue()
        b'hello'
    """
    data = reader.read()
    if strip:
        data = data.strip()
    return decode_to_stream(data, writer, chunk_size=chunk_size)
