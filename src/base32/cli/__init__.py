"""CLI interface."""

from __future__ import annotations

import re
import sys
import base64
import binascii
from typing import TextIO

import click

from .. import __version__, decode, encode


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "--version", "-v")
def base32() -> None:
    """Pure Python Nix Base32 encoder/decoder."""


def _read_input(source: str, stream: TextIO) -> str:
    """Return the input text either from the argument or stdin."""
    data = stream.read().strip() if source == "-" else source.strip()
    return data


@base32.command()
@click.argument("input", metavar="INPUT")
def encode_cmd(input: str) -> None:
    """Encode INPUT (hex string or SRI) to Nix Base32.

    INPUT may be '-' to read from stdin.
    """
    data = _read_input(input, sys.stdin)

    if m := re.match(
        r"^sha\d{3}-((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)$",
        data,
    ):
        payload = base64.b64decode(m.group(1))
    else:
        if not re.fullmatch(r"[0-9a-fA-F]+", data):
            click.echo("error: only hex or SRI input supported", err=True)
            sys.exit(1)
        payload = binascii.unhexlify(data)

    click.echo(encode(payload))


@base32.command()
@click.argument("input", metavar="INPUT")
@click.option(
    "--sri",
    is_flag=True,
    help="Produce output in SRI format if the digest matches a known hash length.",
)
def decode_cmd(input: str, sri: bool) -> None:
    """Decode INPUT (Nix Base32 string) back to bytes, printing hex or SRI form."""
    data = _read_input(input, sys.stdin)
    try:
        decoded = decode(data)
    except Exception as exc:
        click.echo(f"decode error: {exc}", err=True)
        sys.exit(1)

    hexed = binascii.hexlify(decoded).decode("utf-8")

    if sri:
        length = len(hexed)
        prefix = {
            64: "sha256",
            96: "sha384",
            128: "sha512",
        }.get(length)

        if prefix is None:
            click.echo("SRI mode supported only for SHA256/384/512 digests", err=True)
            sys.exit(1)

        b64 = base64.b64encode(decoded).decode("utf-8")
        click.echo(f"{prefix}-{b64}")
    else:
        click.echo(hexed)
