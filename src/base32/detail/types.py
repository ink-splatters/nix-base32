# fmt: off
from __future__ import annotations

import typing


def get_args(x: typing.TypeAliasType):
    return typing.get_args(x.__value__)

INVALID: int = 0xFF

# https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/include/nix/util/base-nix-32.hh#L17
# e o u t - omitted
type NixBase32Char = typing.Literal[
    "0","1","2","3","4","5","6","7",
    "8","9","a","b","c","d","f","g",
    "h","i","j","k","l","m","n","p",
    "q","r","s","v","w","x","y","z"
]

type NixBase32Charset = typing.Literal["".join(get_args(NixBase32Char))]
charset: NixBase32Charset = get_args(NixBase32Charset)[0]


class NixBase32Str(str):
    _allowed: typing.ClassVar[NixBase32Charset] = set(charset)

    def __new__(cls, value: str) -> NixBase32Str:  # noqa: PYI034
        if not set(value) <= cls._allowed:
            raise ValueError(f"Invalid Nix base32 string: {value}")
        return super().__new__(cls, value)
