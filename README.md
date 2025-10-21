# nix‑base32

Pure‑Python implementation of the Nix‑specific base32 variant.

______________________________________________________________________

## Installation

```bash
uv tool install 'nix-base32[cli] @ git+https://github.com/ink-splatters/nix-base32'
```

______________________________________________________________________

## Usage

### Python

```python
from base32 import encode, decode

data = b"hello"
encoded = encode(data)
print(encoded)           # -> NixBase32Str('nbswy3dp')
print(decode(encoded))   # -> b'hello'
```

### CLI

the CLI was inspired by BSD bintrans' `base64` util (now part of standard macOS distribution).

_Examples:_

```bash
❯ echo de2fc4ce5252da49a272fb22e68c73dcfa12ef08077ac26b40ad3a40dd31376e | base32
0vip67fl0fmd81mw4yh713pi5ynwff6fc8pvfai4knjjab7c8byy

❯ echo 0vip67fl0fmd81mw4yh713pi5ynwff6fc8pvfai4knjjab7c8byy | base32 --sri
sha256-3i/EzlJS2kmicvsi5oxz3PoS7wgHesJrQK06QN0xN24=

❯ echo de2fc4ce5252da49a272fb22e68c73dcfa12ef08077ac26b40ad3a40dd31376e | base32 | base32 -d
de2fc4ce5252da49a272fb22e68c73dcfa12ef08077ac26b40ad3a40dd31376e
```

______________________________________________________________________

## License

MIT — see [LICENSE](LICENSE).

## Contributions

Contributions are welcome at the author's discretion; please open an issue first.
See any standard open collaborative code of conduct such as
[Contributor Covenant](https://www.contributor-covenant.org/).
