# tests/conftest.py
import pytest

from base32.detail import charset as nix_charset


@pytest.fixture(scope="session")
def charset() -> str:
    # Expose charset as a fixture so tests can request it explicitly
    return nix_charset


@pytest.fixture(scope="session")
def valid_chars(charset: str) -> set[str]:
    # All allowed chars as a set
    return set(charset)


@pytest.fixture(scope="session")
def invalid_chars(valid_chars: set[str]) -> set[str]:
    # Printable ASCII (0x20..0x7E) minus valid chars
    return {chr(x) for x in range(0x20, 0x7F)} - valid_chars


@pytest.fixture(scope="session")
def prioritized_invalid(invalid_chars: set[str]) -> list[str]:
    # e, o, u, t should be tested first (only keep those actually invalid)
    return [c for c in "eout" if c in invalid_chars]


@pytest.fixture(scope="session")
def invalid_chars_ordered(invalid_chars: set[str], prioritized_invalid: list[str]) -> list[str]:
    # Prioritized invalids first, then the rest (sorted for determinism)
    rest = sorted(invalid_chars - set(prioritized_invalid))
    return prioritized_invalid + rest
