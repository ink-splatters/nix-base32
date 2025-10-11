from .detail import NixBase32Str, max_decoded_length, reverse_lookup


def decode(s: NixBase32Str) -> bytes:
    if not s:
        return b""

    # Upper bound capacity, same as the C++ reserve: ceil(len(s) * 5 / 8).
    cap = max_decoded_length(len(s))
    out = bytearray(cap)
    used = 0  # highest index written + 1

    # Iterate least-significant digit first (reverse the string), mirroring the reference.
    for n, ch in enumerate(reversed(s)):
        digit = reverse_lookup(ch)
        if digit is None:
            raise ValueError(f"invalid character {ch!r}")

        b = n * 5
        i = b // 8
        j = b % 8

        # Write low part into byte i.
        out[i] = (out[i] | ((digit << j) & 0xFF)) & 0xFF
        if used < i + 1:
            used = i + 1

        # If the 5-bit group crosses the byte boundary, write the spillover.
        if j and (digit >> (8 - j)):
            out[i + 1] = (out[i + 1] | (digit >> (8 - j))) & 0xFF
            if used < i + 2:
                used = i + 2

    # Return only the bytes that actually received bits.
    return bytes(out[:used])
