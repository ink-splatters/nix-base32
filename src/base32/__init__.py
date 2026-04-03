"""Pure-Python implementation of the Nix-style base32 codec.

The interface is two functions—:func:`encode` and :func:`decode`.
The codec generally follows upstream implementation (in Nix source tree)

The Nix base32 variant differs from RFC 4648 base32:
letters *e*, *o*, *u*, and *t* are omitted.

Example
-------

>>> from base32 import encode, decode
>>> s = encode(b"hello")
>>> s
NixBase32Str('nbswy3dp')
>>> decode(s)
b'hello'

The :class:`~base32.detail.types.NixBase32Str` type is returned to
ensure all encoded representations are valid according to Nix alphabet.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("nix-base32")
except PackageNotFoundError:
    from typing import Final

    __version__: Final[str] = "dev"


from .decode import decode, decode_iter, decode_stream, decode_to_stream
from .detail import NixBase32Str
from .encode import encode, encode_iter, encode_stream, encode_to_stream

__all__ = [
    "NixBase32Str",
    "decode",
    "decode_iter",
    "decode_stream",
    "decode_to_stream",
    "encode",
    "encode_iter",
    "encode_stream",
    "encode_to_stream",
]
