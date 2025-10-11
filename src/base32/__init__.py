try:
    from ._version import __version__ as __version__
except ImportError:
    __version__ = "dev"


from .decode import decode
from .detail import NixBase32Str
from .encode import encode

__all__ = ["NixBase32Str", "decode", "encode"]
