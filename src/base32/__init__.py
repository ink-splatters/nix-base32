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

try:
    from ._version import __version__ as __version__
except ImportError:
    __version__ = "dev"

from .decode import decode
from .detail import NixBase32Str
from .encode import encode

__all__ = ["NixBase32Str", "decode", "encode"]
