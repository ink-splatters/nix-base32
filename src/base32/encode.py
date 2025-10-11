from .detail import NixBase32Str, charset, encoded_length


def encode(bs: bytes) -> NixBase32Str:
    if not bs:
        return NixBase32Str("")

    length = encoded_length(len(bs))
    out: list[str] = []

    # Mirrors the reference algorithm: walk 5 bit groups from MSB to LSB,
    # pulling from adjacent bytes as needed:
    # https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/base-nix-32.cc#L20
    for n in reversed(range(length)):
        b = n * 5
        i = b // 8
        j = b % 8

        b1 = bs[i]
        b2 = bs[i + 1] if i + 1 < len(bs) else 0
        c = ((b1 >> j) | ((b2 << (8 - j)) & 0xFF)) & 0xFF
        out.append(charset[c & 0x1F])

    return NixBase32Str("".join(out))
