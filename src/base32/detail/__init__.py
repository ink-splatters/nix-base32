from .charset import INVALID, NixBase32Char, NixBase32Charset, charset
from .reverse_lookup import reverse_lookup


def encoded_length(n: int) -> int:
    return (n * 8 - 1) // 5 + 1


__all__ = [
    "INVALID",
    "NixBase32Char",
    "NixBase32Charset",
    "charset",
    "encoded_length",
    "reverse_lookup",
]
