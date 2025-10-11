from base32.detail import encoded_length, max_decoded_length


def test_encoded_length_of_zero_input_is_zero():
    assert encoded_length(0) == 0


def test_max_decoded_length_of_zero_input_is_zero():
    assert max_decoded_length(0) == 0
