def encoded_length(n: int) -> int:
    return (n * 8 - 1) // 5 + 1


def max_decoded_length(n: int) -> int:
    return (n * 5 + 7) // 8
