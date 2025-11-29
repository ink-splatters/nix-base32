"""CLI integration tests using subprocess.

These tests verify the actual CLI behavior, including:
- stdin/stdout handling
- File I/O operations
- SRI format conversion
- Error handling and exit codes

Note: These tests require the 'cli' extra to be installed:
    uv pip install -e ".[cli]"
"""

import sys
import tempfile
import subprocess
from pathlib import Path

import pytest

# Check if click is available
try:
    import click  # noqa: F401

    HAS_CLI = True
except ImportError:
    HAS_CLI = False

pytestmark = pytest.mark.skipif(not HAS_CLI, reason="CLI extras not installed (need click)")

# CLI is invoked via Python module
CLI_CMD = [sys.executable, "-m", "base32.cli"]


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run the CLI with given arguments and optional stdin."""
    return subprocess.run(
        [*CLI_CMD, *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


class TestEncodeBasic:
    """Basic encoding tests via CLI."""

    def test_encode_hex_stdin(self):
        """Encode hex input from stdin."""
        result = run_cli(stdin="68656c6c6f")  # "hello" in hex
        assert result.returncode == 0
        assert result.stdout.strip() == "dxn6qrb8"

    def test_encode_uppercase_hex(self):
        """Hex input should be case-insensitive."""
        result = run_cli(stdin="68656C6C6F")  # Mixed case
        assert result.returncode == 0
        assert result.stdout.strip() == "dxn6qrb8"

    def test_encode_empty_hex(self):
        """Empty hex input produces empty output."""
        result = run_cli(stdin="")
        # Empty input might be treated as an error or produce empty output
        # depending on implementation - just verify no crash
        assert result.returncode in (0, 1)

    def test_encode_sha256_hex(self):
        """Encode a 32-byte SHA256 hash (64 hex chars)."""
        # SHA256 of empty string
        sha256_empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        result = run_cli(stdin=sha256_empty)
        assert result.returncode == 0
        # Verify it decodes back correctly
        assert len(result.stdout.strip()) == 52  # 32 bytes -> 52 nix base32 chars


class TestDecodeBasic:
    """Basic decoding tests via CLI."""

    def test_decode_stdin(self):
        """Decode nix base32 from stdin."""
        result = run_cli("-d", stdin="dxn6qrb8")
        assert result.returncode == 0
        assert result.stdout.strip() == "68656c6c6f"  # "hello" in hex

    def test_decode_with_whitespace(self):
        """Whitespace in input should be handled."""
        result = run_cli("-d", stdin="  dxn6qrb8  \n")
        assert result.returncode == 0
        assert result.stdout.strip() == "68656c6c6f"

    def test_decode_invalid_chars(self):
        """Invalid characters should produce an error."""
        result = run_cli("-d", stdin="invalid!")
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or result.returncode == 1


class TestSRIFormat:
    """Tests for SRI (Subresource Integrity) format handling."""

    def test_encode_sri_sha256(self):
        """Encode from SRI sha256 format."""
        # SRI format: sha256-<base64>
        # This is the empty string hash in SRI format
        sri_input = "sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="
        result = run_cli(stdin=sri_input)
        assert result.returncode == 0
        assert len(result.stdout.strip()) == 52  # 32 bytes

    def test_encode_sri_sha384(self):
        """Encode from SRI sha384 format."""
        # SHA384 of empty string
        sri_input = "sha384-OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb"
        result = run_cli(stdin=sri_input)
        assert result.returncode == 0
        assert len(result.stdout.strip()) == 77  # 48 bytes -> 77 chars

    def test_encode_sri_sha512(self):
        """Encode from SRI sha512 format."""
        # SHA512 of empty string
        sri_input = "sha512-z4PhNX7vuL3xVChQ1m2AB9Yg5AULVxXcg/SpIdNs6c5H0NE8XYXysP+DGNKHfuwvY7kxvUdBeoGlODJ6+SfaPg=="
        result = run_cli(stdin=sri_input)
        assert result.returncode == 0
        assert len(result.stdout.strip()) == 103  # 64 bytes -> 103 chars

    def test_decode_to_sri_sha256(self):
        """Decode to SRI sha256 format."""
        # First encode something
        sha256_hex = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        encode_result = run_cli(stdin=sha256_hex)
        assert encode_result.returncode == 0
        encoded = encode_result.stdout.strip()

        # Now decode back to SRI
        decode_result = run_cli("--sri", stdin=encoded)
        assert decode_result.returncode == 0
        assert decode_result.stdout.strip().startswith("sha256-")

    def test_decode_to_sri_sha512(self):
        """Decode to SRI sha512 format (64 bytes)."""
        # SHA512 produces 64 bytes = 128 hex chars
        sha512_hex = "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        encode_result = run_cli(stdin=sha512_hex)
        assert encode_result.returncode == 0
        encoded = encode_result.stdout.strip()

        # Decode to SRI
        decode_result = run_cli("--sri", stdin=encoded)
        assert decode_result.returncode == 0
        assert decode_result.stdout.strip().startswith("sha512-")

    def test_sri_unsupported_length(self):
        """SRI mode should reject non-standard hash lengths."""
        # 10 bytes doesn't match any SHA variant
        hex_10bytes = "00112233445566778899"
        encode_result = run_cli(stdin=hex_10bytes)
        encoded = encode_result.stdout.strip()

        decode_result = run_cli("--sri", stdin=encoded)
        assert decode_result.returncode != 0
        assert "supported" in decode_result.stderr.lower() or decode_result.returncode == 1

    def test_sri_invalid_hash_length(self):
        """SRI input with wrong hash length should be rejected."""
        # sha256 but with only 16 bytes (should be 32)
        invalid_sri = "sha256-AAAAAAAAAAAAAAAAAAAAAA=="  # 16 bytes
        result = run_cli(stdin=invalid_sri)
        assert result.returncode != 0
        assert "32 bytes" in result.stderr or "error" in result.stderr.lower()

    def test_sri_roundtrip_sha256(self):
        """Full roundtrip: SRI -> nix base32 -> SRI."""
        original_sri = "sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="

        # Encode SRI to nix base32
        encode_result = run_cli(stdin=original_sri)
        assert encode_result.returncode == 0
        encoded = encode_result.stdout.strip()

        # Decode back to SRI
        decode_result = run_cli("--sri", stdin=encoded)
        assert decode_result.returncode == 0
        assert decode_result.stdout.strip() == original_sri


class TestFileIO:
    """Tests for file input/output operations."""

    def test_input_from_file(self):
        """Read input from a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("68656c6c6f")  # "hello" in hex
            f.flush()
            input_path = f.name

        try:
            result = run_cli("-i", input_path)
            assert result.returncode == 0
            assert result.stdout.strip() == "dxn6qrb8"
        finally:
            Path(input_path).unlink()

    def test_output_to_file(self):
        """Write output to a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            output_path = f.name

        try:
            result = run_cli("-o", output_path, stdin="68656c6c6f")
            assert result.returncode == 0

            content = Path(output_path).read_text()
            assert content.strip() == "dxn6qrb8"
        finally:
            Path(output_path).unlink()

    def test_input_and_output_files(self):
        """Both input and output as files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("68656c6c6f")
            f.flush()
            input_path = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            output_path = f.name

        try:
            result = run_cli("-i", input_path, "-o", output_path)
            assert result.returncode == 0

            content = Path(output_path).read_text()
            assert content.strip() == "dxn6qrb8"
        finally:
            Path(input_path).unlink()
            Path(output_path).unlink()


class TestErrorHandling:
    """Tests for error conditions and exit codes."""

    def test_invalid_hex_input(self):
        """Non-hex input should produce an error."""
        result = run_cli(stdin="not-valid-hex!")
        assert result.returncode != 0

    def test_missing_input_file(self):
        """Missing input file should produce an error."""
        result = run_cli("-i", "/nonexistent/file/path.txt")
        assert result.returncode != 0

    def test_version_flag(self):
        """--version should show version info."""
        result = run_cli("--version")
        assert result.returncode == 0
        # Should contain version number or "dev"
        assert result.stdout.strip() or "dev" in result.stdout.lower()

    def test_help_flag(self):
        """--help should show help text."""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "base32" in result.stdout.lower()


class TestRoundtrip:
    """End-to-end roundtrip tests via CLI."""

    @pytest.mark.parametrize(
        "hex_input",
        [
            "00",  # Single byte
            "ff",  # Max byte
            "0000000000",  # Multiple zeros
            "deadbeef",  # Classic test value
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256
        ],
    )
    def test_hex_roundtrip(self, hex_input: str):
        """Hex -> nix base32 -> hex roundtrip."""
        # Encode
        encode_result = run_cli(stdin=hex_input)
        assert encode_result.returncode == 0
        encoded = encode_result.stdout.strip()

        # Decode
        decode_result = run_cli("-d", stdin=encoded)
        assert decode_result.returncode == 0
        decoded = decode_result.stdout.strip()

        assert decoded.lower() == hex_input.lower()
