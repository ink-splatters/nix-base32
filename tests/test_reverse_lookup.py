import pytest

from base32.detail import INVALID, charset, reverse_lookup


@pytest.fixture(scope="module")
def lookup_table_valid_entries():
    from base32.detail.reverse_lookup import lookup_table

    return {v for v in lookup_table if v != INVALID}


def test_invalid_chars_map_to_invalid(invalid_chars):
    results = {reverse_lookup(ch) for ch in invalid_chars}
    assert results == {None}


def test_all_valid_chars_resolvable(valid_chars):
    resolved = [r for r in (reverse_lookup(ch) for ch in valid_chars) if r is not None]
    assert len(resolved) == len(valid_chars) == len(charset)


def test_valid_chars_resolve_to_existing_entries(valid_chars, lookup_table_valid_entries):
    resolved = [
        r for r in (reverse_lookup(ch) for ch in valid_chars) if r in lookup_table_valid_entries
    ]
    assert len(resolved) == len(valid_chars) == len(charset)
