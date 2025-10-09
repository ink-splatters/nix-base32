import pytest

from base32.detail import charset


@pytest.fixture
def charset_as_string():
    # https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/include/nix/util/base-nix-32.hh#L17
    # e o u t - omitted
    return "0123456789abcdfghijklmnpqrsvwxyz"


def test_literal_type(charset_as_string):
    assert "".join(charset) == charset_as_string
