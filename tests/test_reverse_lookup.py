# fmt: off
import itertools

import pytest

from base32.detail import INVALID, reverse_lookup


@pytest.fixture
def charset():
    from base32.detail import charset as chs

    return set(chs)


@pytest.fixture
def valid_chars(charset):
    return list(charset)


@pytest.fixture
def invalid_chars(charset):
    return {chr(n) for n in range(256)} - charset


@pytest.fixture
def lookup_table_valid_entries():
    from base32.detail.reverse_lookup import lookup_table

    return set(filter(lambda x: x != INVALID, lookup_table))


def test_looking_up_invalid_chars_results_in_invalid(invalid_chars):
    invalid_chars_lookup_results = list({reverse_lookup(ch) for ch in invalid_chars})

    assert len(invalid_chars_lookup_results) == 1
    assert invalid_chars_lookup_results[0] is None


def test_looking_up_valid_chars_succeeds(valid_chars, charset):
    assert len(
        [
            *itertools.takewhile(
                lambda x: x is not None,
                (reverse_lookup(ch) for ch in valid_chars)
            )
        ]
    ) == len(charset)


def test_looking_up_valid_chars_resolves_from_correct_mapping(
    charset, lookup_table_valid_entries, valid_chars
):
    assert len(
        [
            *itertools.takewhile(
                lambda x: x in lookup_table_valid_entries,
                (reverse_lookup(ch) for ch in valid_chars),
            )
        ]
    ) == len(charset)
