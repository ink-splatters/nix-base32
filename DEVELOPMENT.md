# Development

______________________________________________________________________

## Prerequisites

\[uv\](https://docs.astral.sh/uv/

______________________________________________________________________

## Linting and tests

```bash
uv sync
uv pip install .[cli]
poe fix        # format and lint
poe test       # run tests with coverage
```

______________________________________________________________________

## Publishing

1. Tag a release:

   ```bash
   git tag v0.1.0
   git push --tags
   ```

2. GitHub Actions will build using *uv‑dynamic‑versioning* and publish to PyPI if
   `PYPI_API_TOKEN` is defined in repository secrets.

______________________________________________________________________

## TODO
