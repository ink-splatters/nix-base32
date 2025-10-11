import pytest

from base32.detail import encoded_length, max_decoded_length


def test_encoded_length_of_zero_input_is_zero():
    assert encoded_length(0) == 0


def test_max_decoded_length_of_zero_input_is_zero():
    assert max_decoded_length(0) == 0


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 8, 16, 31, 32, 33])
def test_encoded_length_matches_ceil_formula(n: int):
    # ceil(n * 8 / 5) == (n*8 + 4) // 5
    assert encoded_length(n) == (n * 8 + 4) // 5


@pytest.mark.parametrize("n", range(1, 25))
def test_max_decoded_length_matches_capacity_upper_bound(n: int):
    # This is a capacity upper bound (as in the reference decoder)
    assert max_decoded_length(n) == (n * 5 + 7) // 8
