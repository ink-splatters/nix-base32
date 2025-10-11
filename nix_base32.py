#!/usr/bin/env python

import re
import base64
import argparse
import binascii
import fileinput

_chars = "0123456789abcdfghijklmnpqrsvwxyz"
_invalid = 0xFF


def _build_reverse_map() -> list[int]:
    m = [_invalid] * 256
    for i, ch in enumerate(_chars):
        m[ord(ch)] = i
    return m


_reverse_map: list[int] = _build_reverse_map()


def _encoded_length(n: int) -> int:
    return (n * 8 - 1) // 5 + 1


def _reverse_lookup(ch: str) -> int | None:
    digit = _reverse_map[ord(ch)]
    return None if digit == _invalid else digit


def encode(bs: bytes) -> str:
    if not bs:
        return ""

    length = _encoded_length(len(bs))
    out: list[str] = []

    for n in reversed(range(length)):
        b = n * 5
        i = b // 8
        j = b % 8
        b1 = bs[i]
        b2 = bs[i + 1] if i + 1 < len(bs) else 0
        c = ((b1 >> j) | ((b2 << (8 - j)) & 0xFF)) & 0xFF
        out.append(_chars[c & 0x1F])

    # Strip redundant leading zero groups for symmetry
    return "".join(out)  # .lstrip(_chars[0])


def decode(s: str) -> bytes:
    if not s:
        return b""

    # Provisional maximum length
    res = [0] * ((len(s) * 5 + 7) // 8)

    for n, ch in enumerate(reversed(s)):
        digit = _reverse_lookup(ch)
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
    return bytes(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="nix_base32", description="Pure Python nix base32 codec")

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    enc = subparsers.add_parser("encode")
    enc.add_argument("input", metavar="INPUT")

    dec = subparsers.add_parser("decode")
    dec.add_argument("input", metavar="INPUT")
    dec.add_argument("--sri", action="store_true", help="Produce output in SRI format")

    args = parser.parse_args()
    #
    inp: str = (
        next(iter(fileinput.input(files=[args.input], encoding="utf-8"))).split()[0]  # noqa: SIM115
        if args.input == "-"
        else args.input
    )

    match args.cmd:
        case "encode":
            if m := re.match(
                r"^sha[\d]{3}-((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)", inp
            ):
                sri_payload = m.group(1)
                inp = base64.b64decode(sri_payload)
            else:
                inp = inp.lower()
                if re.match(r"^[0-9a-f]+$", inp) is None:
                    raise ValueError("only SRI or hexlified inputs are currently supported")
                inp = binascii.unhexlify(inp)

            print(encode(inp))

        case "decode":
            output = decode(inp)
            hexlified = binascii.hexlify(output).decode("utf-8")

            if args.sri:
                pfx: str
                match len(hexlified):
                    case 64:
                        pfx = "sha256"
                    case 96:
                        pfx = "sha384"
                    case 128:
                        pfx = "sha512"
                    case _:
                        raise ValueError(
                            "SRI mode only supported when decoded value is SHA-256, SHA-384 or SHA-512 hash"
                        )

                print(f"{pfx}-{base64.b64encode(output).decode('utf-8')}")
            else:
                print(hexlified)
