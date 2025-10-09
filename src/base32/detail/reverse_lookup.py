from . import INVALID, NixBase32Char, charset


def build_lookup_table() -> list[int]:
    result: list[int] = [INVALID] * 256

    for i, ch in enumerate(charset):
        result[ord(ch)] = i

    return result


lookup_table: list[int] = build_lookup_table()


def reverse_lookup(ch: NixBase32Char) -> int | None:
    digit: int = lookup_table[ord(ch)]
    return None if digit == INVALID else digit
