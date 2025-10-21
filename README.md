# nix‑base32

Pure‑Python implementation of the Nix‑specific Base32 variant.

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

```bash
echo "68656c6c6f..." | base32 encode -           # hex -> Nix Base32
echo "nbswy3dp..." | base32 decode -             # Nix Base32 -> hex
```

______________________________________________________________________

## License

MIT — see [LICENSE](LICENSE).

## Contributions

Contributions are welcome at the author's discretion; please open an issue first.
See any standard open collaborative code of conduct such as
[Contributor Covenant](https://www.contributor-covenant.org/).
