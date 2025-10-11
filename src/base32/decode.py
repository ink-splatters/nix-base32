from .detail import NixBase32Str, max_decoded_length, reverse_lookup


def decode(s: NixBase32Str) -> bytes:
    if not s:
        return b""

    res: bytes = [0] * max_decoded_length(len(s))

    for n, ch in enumerate(reversed(s)):
        digit = reverse_lookup(ch)
        if digit is None:
            raise ValueError(f"invalid character {ch!r}")

        b = n * 5
        i = b // 8
        j = b % 8

        res[i] = (res[i] | ((digit << j) & 0xFF)) & 0xFF
        if j > 3:
            res[i + 1] = (res[i + 1] | (digit >> (8 - j))) & 0xFF

    # Trim any trailing padding zeros that don't belong to real bits
    # Find index of the last nonzero or stop when whole digest is real length
    while res and res[-1] == 0:
        # Only drop final zero byte if its 5 bit group didn't contribute nonzero bits
        res.pop()
    return res
