# fmt: off
import typing

INVALID: int = 0xFF

# https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/include/nix/util/base-nix-32.hh#L17
# e o u t - omitted
NixBase32Char = typing.Literal[
    "0","1","2","3","4","5","6","7",
    "8","9","a","b","c","d","f","g",
    "h","i","j","k","l","m","n","p",
    "q","r","s","v","w","x","y","z"
]

type NixBase32Charset = tuple[NixBase32Char, ...]
charset: NixBase32Charset = typing.get_args(NixBase32Char)
