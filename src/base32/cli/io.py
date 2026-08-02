import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, TextIO, cast

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def infile(name: str) -> Iterator[TextIO]:
    """Yield a readable text stream for a filename or stdin if '-'."""
    if name == "-":
        yield cast("TextIO", sys.stdin)
    else:
        with open(name, encoding="utf-8") as f:
            yield f


@contextmanager
def outfile(name: str) -> Iterator[TextIO]:
    """Yield a writable text stream for a filename or stdout if '-'."""
    if name == "-":
        yield cast("TextIO", sys.stdout)
    else:
        with open(name, "w", encoding="utf-8") as f:
            yield f
