"""base32 encoding following the Nix variant semantics.

This module defines :func:`encode`, which converts arbitrary byte
strings into a :class:`~base32.detail.types.NixBase32Str`.

The algorithm mirrors the Nix implementation.
"""

from __future__ import annotations

import typing

from .detail import NixBase32Str, charset, encoded_length

if typing.TYPE_CHECKING:
    from collections.abc import Iterator


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


def encode_iter(bs: bytes, chunk_size: int = 8192) -> Iterator[str]:
    """Encode bytes and yield output in chunks.

    This is useful for memory-efficient writing of large encoded data.
    The encoding itself requires the full input, but output is yielded
    in manageable chunks.

    :param bs: Bytes to encode.
    :param chunk_size: Maximum characters per yielded chunk.
    :yields: String chunks of the encoded output.

    :example:
        >>> for chunk in encode_iter(b"hello" * 1000, chunk_size=100):
        ...     print(len(chunk))  # Each chunk <= 100 chars
    """
    encoded = encode(bs)
    for i in range(0, len(encoded), chunk_size):
        yield str(encoded[i : i + chunk_size])


def encode_to_stream(
    bs: bytes,
    writer: typing.TextIO,
    *,
    chunk_size: int = 8192,
) -> int:
    """Encode bytes and write to a text stream.

    :param bs: Bytes to encode.
    :param writer: Text stream to write encoded output to.
    :param chunk_size: Write buffer size in characters.
    :returns: Number of characters written.

    :example:
        >>> import io
        >>> buf = io.StringIO()
        >>> encode_to_stream(b"hello", buf)
        8
        >>> buf.getvalue()
        'nbswy3dp'
    """
    written = 0
    for chunk in encode_iter(bs, chunk_size):
        writer.write(chunk)
        written += len(chunk)
    return written


def encode_stream(
    reader: typing.BinaryIO,
    writer: typing.TextIO,
    *,
    chunk_size: int = 8192,
) -> int:
    """Read binary data from a stream, encode, and write to text stream.

    .. note::
        Due to the Nix base32 algorithm processing bits in reverse order
        (MSB to LSB), the full input must be buffered before encoding.
        This function provides streaming I/O but not streaming computation.

    :param reader: Binary stream to read input from.
    :param writer: Text stream to write encoded output to.
    :param chunk_size: I/O buffer size.
    :returns: Number of characters written.

    :example:
        >>> import io
        >>> inp = io.BytesIO(b"hello")
        >>> out = io.StringIO()
        >>> encode_stream(inp, out)
        8
        >>> out.getvalue()
        'nbswy3dp'
    """
    data = reader.read()
    return encode_to_stream(data, writer, chunk_size=chunk_size)
