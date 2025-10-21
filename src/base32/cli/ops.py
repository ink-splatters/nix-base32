import re
import sys
import base64
import binascii

import click

import base32

from .io import infile, outfile


def encode(input: str, output: str) -> None:
    """Reads input and writes Nix base32 output

    :param input: input filename or '-' for stdin
    :type input: str
    :param output: output filename or '-' for stdout
    :type output: str
    """

    data: str

    with infile(input) as f:
        data = f.read().strip()

    # if data is SRI hash
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

    with outfile(output) as f:
        f.write(base32.encode(payload))


def decode(input: str, output: str, sri: bool) -> None:
    """Reads Nix base32 input and writes decoded output

    :param input: input filename or '-' for stdin
    :type input: str
    :param output: output filename or '-' for stdout
    :type output: str
    :param sri: if set
    :type sri: bool
    """

    data: str

    with infile(input) as f:
        data = f.read().strip()

    try:
        decoded = base32.decode(data)
    except Exception as exc:
        click.echo(f"decode error: {exc}", err=True)
        sys.exit(1)

    hexed = binascii.hexlify(decoded).decode("utf-8")

    with outfile(output) as f:
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
            f.write(f"{prefix}-{b64}")
        else:
            f.write(hexed)
