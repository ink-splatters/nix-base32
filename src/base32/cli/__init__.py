"""CLI interface."""

from __future__ import annotations

import click

from .. import __version__
from . import ops


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(__version__, "--version", "-v")
@click.option("-d", "decode", is_flag=True, help="Decode input.")
@click.option(
    "--sri",
    is_flag=True,
    help="Decode input, producing output in SRI format if the digest matches a known hash length.",
)
@click.option(
    "-i", "--input", is_flag=False, default="-", help='input file (default: "-" for stdin)'
)
@click.option(
    "-o", "--output", is_flag=False, default="-", help='output file (default: "-" for stdout)'
)
def base32(input: str, output: str, decode: bool, sri: bool) -> None:
    """
    The base32 utility acts as a Nix base32 variant decoder when passed the --decode (or -d) flag and as
    a Nix base32 encoder otherwise.
    """

    if decode or sri:
        ops.decode(input, output, sri)
    else:
        ops.encode(input, output)
