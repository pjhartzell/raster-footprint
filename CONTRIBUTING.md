# Contributing

[Issues](https://github.com/pjhartzell/raster-footprint/issues) and [pull requests](https://github.com/pjhartzell/raster-footprint/pulls) are welcome.

## Developing

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Install uv, clone the repo, then sync the dev environment:

```shell
git clone https://github.com/pjhartzell/raster-footprint
cd raster-footprint
uv sync
```

`uv sync` installs the project in editable mode along with the `dev` dependency group. To also install the `docs` group, use `uv sync --group docs`.

Install the [pre-commit](https://pre-commit.com/) hooks (they run against the dev environment, so `uv sync` must come first):

```shell
uv run pre-commit install
```

Run tests with [pytest](https://docs.pytest.org/):

```shell
uv run pytest
```

Build docs with [Sphinx](https://www.sphinx-doc.org/):

```shell
uv run --group docs make -C docs html
```

## Releasing

Versioning follows [semantic versioning](https://semver.org/).

1. On a `release/vX.Y.Z` branch, bump the version in [pyproject.toml](./pyproject.toml) and update the [CHANGELOG](./CHANGELOG.md).
2. Open a PR and merge it to `main`.
3. Tag `main` with `vX.Y.Z` and push the tag — the [release workflow](./.github/workflows/release.yaml) builds the package and publishes to PyPI.
4. Create a GitHub [release](https://github.com/pjhartzell/raster-footprint/releases) for the tag.
