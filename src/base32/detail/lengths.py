def encoded_length(n: int) -> int:
    return (n * 8 - 1) // 5 + 1


def max_decoded_length(n: int) -> int:
    # ceil(n * 5 / 8): capacity upper-bound used by the reference decoder:
    # https://github.com/NixOS/nix/blob/fb117e0cacc9b0bb29288ee9d3cb6dc0b5ff34a5/src/libutil/base-nix-32.cc#L45

    return (n * 5 + 7) // 8
