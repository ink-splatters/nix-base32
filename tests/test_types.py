import random

import pytest

from base32.detail.types import NixBase32Str


def test_charset_drops_eout_and_is_ascii_subset(valid_chars, charset):
    assert set("eout").isdisjoint(valid_chars)
    # sanity: charset string enumerates the same valid chars
    assert set(charset) == valid_chars


def test_empty_string_is_valid():
    s = NixBase32Str("")
    assert isinstance(s, NixBase32Str)
    assert s == ""


def test_all_valid_single_chars_are_accepted(valid_chars):
    for ch in valid_chars:
        s = NixBase32Str(ch)
        assert isinstance(s, NixBase32Str)
        assert s == ch


def test_long_valid_string_is_accepted(charset):
    s = charset * 2  # deterministic
    out = NixBase32Str(s)
    assert isinstance(out, NixBase32Str)
    assert out == s


def test_each_invalid_single_char_is_rejected(invalid_chars_ordered):
    for ch in invalid_chars_ordered:
        with pytest.raises(ValueError, match="Invalid Nix base32 string:"):
            NixBase32Str(ch)


def test_mixed_strings_reject_if_any_invalid_present(prioritized_invalid, invalid_chars, charset):
    # Prioritize e/o/u/t but also include a couple non-priority samples
    others = sorted(invalid_chars - set(prioritized_invalid))
    sample_others = [others[0], others[-1]] if len(others) >= 2 else others

    for bad in prioritized_invalid + sample_others:
        base = charset
        cases = [
            bad + base,  # invalid at start
            base[:5] + bad + base[5:],  # invalid in middle
            base + bad,  # invalid at end
        ]
        for s in cases:
            with pytest.raises(ValueError, match="Invalid Nix base32 string:"):
                NixBase32Str(s)


def test_combinations_of_prioritized_invalids_are_rejected(prioritized_invalid, charset):
    # Focus on prioritized invalids; try singles, representative pairs, some triples, and the set combined.
    singles = prioritized_invalid
    pairs = list({a + b for a in prioritized_invalid for b in prioritized_invalid})
    triples = []
    if len(prioritized_invalid) >= 3:
        triples = [
            prioritized_invalid[0] + prioritized_invalid[1] + prioritized_invalid[2],
            prioritized_invalid[-1] + prioritized_invalid[0] + prioritized_invalid[1],
        ]
    combined = ["".join(prioritized_invalid)] if prioritized_invalid else []
    samples = singles + pairs + triples + combined

    for bad in samples:
        with pytest.raises(ValueError, match="Invalid Nix base32 string:"):
            NixBase32Str(bad)
        with pytest.raises(ValueError, match="Invalid Nix base32 string:"):
            NixBase32Str(charset[:3] + bad + charset[-3:])


@pytest.mark.parametrize("seed", range(3), ids=lambda s: f"seed={s}")
def test_seeded_random_property(seed, charset, invalid_chars, prioritized_invalid):
    rnd = random.Random(seed)
    valid_pool = list(charset)
    invalid_priority_pool = prioritized_invalid
    invalid_other_pool = sorted(invalid_chars - set(prioritized_invalid)) or ["!"]

    for _ in range(50):  # keep fast and deterministic
        length = rnd.randint(0, 24)
        s_chars = []
        for _ in range(length):
            if rnd.random() < 0.7:
                s_chars.append(rnd.choice(valid_pool))
            else:
                # Bias invalids toward e/o/u/t (~70% of invalid picks)
                if invalid_priority_pool and rnd.random() < 0.7:
                    s_chars.append(rnd.choice(invalid_priority_pool))
                else:
                    s_chars.append(rnd.choice(invalid_other_pool))
        s = "".join(s_chars)
        if set(s) <= set(valid_pool):
            out = NixBase32Str(s)
            assert isinstance(out, NixBase32Str)
            assert out == s
        else:
            with pytest.raises(ValueError, match="Invalid Nix base32 string:"):
                NixBase32Str(s)
