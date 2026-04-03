"""Tests for streaming encode/decode functionality."""

import io
import random

import pytest

from base32 import (
    NixBase32Str,
    decode,
    decode_iter,
    decode_stream,
    decode_to_stream,
    encode,
    encode_iter,
    encode_stream,
    encode_to_stream,
)


class TestEncodeIter:
    """Tests for encode_iter generator."""

    def test_empty_input_yields_nothing(self):
        chunks = list(encode_iter(b""))
        assert chunks == []

    def test_small_input_single_chunk(self):
        chunks = list(encode_iter(b"hello", chunk_size=100))
        assert len(chunks) == 1
        assert "".join(chunks) == encode(b"hello")

    def test_chunked_output_reassembles_correctly(self):
        data = b"hello world this is a longer test string"
        chunks = list(encode_iter(data, chunk_size=5))
        reassembled = "".join(chunks)
        assert reassembled == encode(data)

    def test_chunk_sizes_respected(self):
        data = b"x" * 100  # Will produce ~160 chars
        chunk_size = 10
        chunks = list(encode_iter(data, chunk_size=chunk_size))
        for chunk in chunks[:-1]:  # All but last
            assert len(chunk) == chunk_size
        assert len(chunks[-1]) <= chunk_size

    @pytest.mark.parametrize("size", [1, 5, 32, 64, 128, 1000])
    def test_various_input_sizes(self, size: int):
        data = bytes(range(256)) * (size // 256 + 1)
        data = data[:size]
        chunks = list(encode_iter(data, chunk_size=17))  # Odd chunk size
        assert "".join(chunks) == encode(data)


class TestDecodeIter:
    """Tests for decode_iter generator."""

    def test_empty_input_yields_nothing(self):
        chunks = list(decode_iter(""))
        assert chunks == []

    def test_small_input_single_chunk(self):
        encoded = str(encode(b"hello"))
        chunks = list(decode_iter(encoded, chunk_size=100))
        assert len(chunks) == 1
        assert b"".join(chunks) == b"hello"

    def test_chunked_output_reassembles_correctly(self):
        original = b"hello world this is a longer test string"
        encoded = str(encode(original))
        chunks = list(decode_iter(encoded, chunk_size=5))
        reassembled = b"".join(chunks)
        assert reassembled == original

    def test_chunk_sizes_respected(self):
        original = b"x" * 100
        encoded = str(encode(original))
        chunk_size = 10
        chunks = list(decode_iter(encoded, chunk_size=chunk_size))
        for chunk in chunks[:-1]:  # All but last
            assert len(chunk) == chunk_size
        assert len(chunks[-1]) <= chunk_size


class TestEncodeToStream:
    """Tests for encode_to_stream function."""

    def test_writes_to_stringio(self):
        buf = io.StringIO()
        written = encode_to_stream(b"hello", buf)
        assert written == 8
        assert buf.getvalue() == "dxn6qrb8"  # Nix base32, not RFC 4648

    def test_empty_input(self):
        buf = io.StringIO()
        written = encode_to_stream(b"", buf)
        assert written == 0
        assert buf.getvalue() == ""

    def test_returns_correct_count(self):
        data = b"test data for counting"
        buf = io.StringIO()
        written = encode_to_stream(data, buf)
        assert written == len(buf.getvalue())
        assert written == len(encode(data))


class TestDecodeToStream:
    """Tests for decode_to_stream function."""

    def test_writes_to_bytesio(self):
        buf = io.BytesIO()
        written = decode_to_stream("dxn6qrb8", buf)  # Nix base32
        assert written == 5
        assert buf.getvalue() == b"hello"

    def test_empty_input(self):
        buf = io.BytesIO()
        written = decode_to_stream("", buf)
        assert written == 0
        assert buf.getvalue() == b""

    def test_returns_correct_count(self):
        original = b"test data for counting"
        encoded = str(encode(original))
        buf = io.BytesIO()
        written = decode_to_stream(encoded, buf)
        assert written == len(original)


class TestEncodeStream:
    """Tests for encode_stream function (reader -> writer)."""

    def test_basic_roundtrip(self):
        inp = io.BytesIO(b"hello")
        out = io.StringIO()
        written = encode_stream(inp, out)
        assert written == 8
        assert out.getvalue() == "dxn6qrb8"  # Nix base32

    def test_empty_input(self):
        inp = io.BytesIO(b"")
        out = io.StringIO()
        written = encode_stream(inp, out)
        assert written == 0
        assert out.getvalue() == ""

    def test_large_input(self):
        data = bytes(range(256)) * 100  # 25.6KB
        inp = io.BytesIO(data)
        out = io.StringIO()
        written = encode_stream(inp, out)
        assert written == len(encode(data))
        assert decode(NixBase32Str(out.getvalue())) == data


class TestDecodeStream:
    """Tests for decode_stream function (reader -> writer)."""

    def test_basic_roundtrip(self):
        inp = io.StringIO("dxn6qrb8")  # Nix base32
        out = io.BytesIO()
        written = decode_stream(inp, out)
        assert written == 5
        assert out.getvalue() == b"hello"

    def test_empty_input(self):
        inp = io.StringIO("")
        out = io.BytesIO()
        written = decode_stream(inp, out)
        assert written == 0
        assert out.getvalue() == b""

    def test_strips_whitespace_by_default(self):
        inp = io.StringIO("  dxn6qrb8  \n")  # Nix base32
        out = io.BytesIO()
        written = decode_stream(inp, out)
        assert written == 5
        assert out.getvalue() == b"hello"

    def test_strip_disabled(self):
        # With strip=False, whitespace would cause an error
        inp = io.StringIO("dxn6qrb8")  # Nix base32, no whitespace
        out = io.BytesIO()
        written = decode_stream(inp, out, strip=False)
        assert written == 5

    def test_large_input(self):
        data = bytes(range(256)) * 100  # 25.6KB
        encoded = str(encode(data))
        inp = io.StringIO(encoded)
        out = io.BytesIO()
        written = decode_stream(inp, out)
        assert written == len(data)
        assert out.getvalue() == data


class TestStreamingRoundtrip:
    """Integration tests for streaming encode/decode."""

    @pytest.mark.parametrize("seed", range(3))
    def test_random_data_roundtrip(self, seed: int):
        rnd = random.Random(seed)
        for _ in range(10):
            size = rnd.randint(0, 1000)
            data = bytes(rnd.getrandbits(8) for _ in range(size))

            # Encode via stream
            enc_out = io.StringIO()
            encode_stream(io.BytesIO(data), enc_out)

            # Decode via stream
            dec_out = io.BytesIO()
            decode_stream(io.StringIO(enc_out.getvalue()), dec_out)

            assert dec_out.getvalue() == data

    def test_all_byte_values(self):
        """Ensure all byte values roundtrip correctly through streams."""
        data = bytes(range(256))
        enc_out = io.StringIO()
        encode_stream(io.BytesIO(data), enc_out)

        dec_out = io.BytesIO()
        decode_stream(io.StringIO(enc_out.getvalue()), dec_out)

        assert dec_out.getvalue() == data
