"""Low-level internal utilities for Nix-style base32 encoding and decoding.

This subpackage provides fine-grained tools used by higher-level base32
logic.  It encapsulates Nix-specific alphabet definitions, validation
types, length computations, and fast reverse-lookup functionality.

The exposed API is intentionally narrow—only stable primitives required
by the public encoder/decoder surface are exported.

Example usage::

    from base32.detail import encoded_length, reverse_lookup

    n = 16
    print(f"{n} bytes -> roughly {encoded_length(n)} base32 chars")

    digit = reverse_lookup("f")
    print(f"Digit for 'f': {digit}")
"""

from .lengths import encoded_length, max_decoded_length
from .reverse_lookup import reverse_lookup
from .types import INVALID, NixBase32Char, NixBase32Str, charset

__all__ = [
    "INVALID",
    "NixBase32Char",
    "NixBase32Str",
    "charset",
    "encoded_length",
    "max_decoded_length",
    "reverse_lookup",
]
