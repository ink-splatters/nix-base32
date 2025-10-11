import random

import pytest

from base32 import decode, encode
from base32.detail import encoded_length
from base32.detail.types import NixBase32Str


def test_encode_empty_returns_empty_nix_str():
    out = encode(b"")
    assert isinstance(out, NixBase32Str)
    assert out == ""


def test_decode_empty_returns_empty_bytes():
    assert decode(NixBase32Str("")) == b""


@pytest.mark.parametrize("length", [0, 1, 2, 3, 4, 5, 8, 15, 16, 31, 32, 33, 64])
def test_roundtrip_and_lengths(length: int, valid_chars: set[str]):
    bs = bytes((i * 37) & 0xFF for i in range(length))  # varied deterministic pattern
    enc = encode(bs)
    assert isinstance(enc, NixBase32Str)
    assert set(enc) <= valid_chars
    assert len(enc) == encoded_length(len(bs))
    dec = decode(enc)
    assert dec == bs


@pytest.mark.parametrize(
    "payload",
    [
        b"\x00",
        b"\x01\x00",
        b"\xff\x00\x00",
        b"\x00\x00\x00",
        b"\x12\x34\x56\x00",
    ],
)
def test_trailing_zero_bytes_are_preserved(payload: bytes):
    assert decode(encode(payload)) == payload


@pytest.mark.parametrize("seed", range(3), ids=lambda s: f"seed={s}")
def test_seeded_random_roundtrip(seed: int, valid_chars: set[str]):
    rnd = random.Random(seed)
    for _ in range(50):  # fast, deterministic
        n = rnd.randint(0, 128)
        bs = (
            rnd.randbytes(n)
            if hasattr(rnd, "randbytes")
            else bytes(rnd.getrandbits(8) for _ in range(n))
        )
        enc = encode(bs)
        assert isinstance(enc, NixBase32Str)
        assert set(enc) <= valid_chars
        assert len(enc) == encoded_length(len(bs))
        assert decode(enc) == bs


@pytest.mark.parametrize("n", range(25))
def test_decoding_all_zero_digits_canonicalizes_on_reencode(n: int):
    s = NixBase32Str("0" * n)
    out = decode(s)
    # Re-encoding must always yield the canonical representation for the decoded bytes.
    assert encode(out) == NixBase32Str("0" * encoded_length(len(out)))


def test_decode_rejects_invalid_chars_anywhere(prioritized_invalid):
    base = str(encode(b"hello world"))  # non-empty valid base
    bad = (
        prioritized_invalid[0] if prioritized_invalid else "e"
    )  # pick a representative invalid char
    cases = [
        bad + base,
        base[: len(base) // 2] + bad + base[len(base) // 2 :],
        base + bad,
    ]
    for s in cases:
        with pytest.raises(ValueError, match=rf"invalid character {bad!r}"):
            decode(s)  # type: ignore[arg-type]
