import io
import sys
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def infile(name: str) -> Iterator[io.TextIOBase]:
    """Yield a readable text stream for a filename or stdin if '-'."""
    if name == "-":
        yield sys.stdin
    else:
        with open(name, encoding="utf-8") as f:
            yield f


@contextmanager
def outfile(name: str) -> Iterator[io.TextIOBase]:
    """Yield a writable text stream for a filename or stdout if '-'."""
    if name == "-":
        yield sys.stdout
    else:
        with open(name, "w", encoding="utf-8") as f:
            yield f
