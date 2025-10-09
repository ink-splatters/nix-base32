try:
    from ._version import __version__ as __version__
except ImportError:
    __version__ = "dev"


# This impl roughly follows the canonical implementation found in
# [nix](https://github.com/NixOS/nix) source tree:
# ```
# src/libutil/base-nix-32.cc
# src/libutil/include/nix/util/base-nix-32.hh
# ```
