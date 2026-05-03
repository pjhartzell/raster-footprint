# raster-footprint

[![CI Status](https://img.shields.io/github/actions/workflow/status/pjhartzell/raster-footprint/ci.yaml?style=for-the-badge&label=CI)](https://github.com/pjhartzell/raster-footprint/actions/workflows/ci.yaml)
[![Read the Docs](https://img.shields.io/readthedocs/antimeridian?style=for-the-badge)](https://raster-footprint.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/raster-footprint?style=for-the-badge)](https://pypi.org/project/raster-footprint/)

[![GitHub](https://img.shields.io/github/license/pjhartzell/raster-footprint?style=for-the-badge)](https://github.com/pjhartzell/raster-footprint/blob/main/LICENSE)

Create GeoJSON geometries that bound valid raster data. Depends on [rasterio](https://rasterio.readthedocs.io/en/stable/) and [shapely](https://shapely.readthedocs.io/en/stable/manual.html).

## Usage

```shell
pip install raster-footprint
```

Create or manipulate GeoJSON with the CLI:

```shell
raster-footprint --help
usage: raster-footprint [-h] {create,densify,reproject,simplify} ...

options:
  -h, --help            show this help message and exit

commands:
  {create,densify,reproject,simplify}
    create              Create a raster footprint
    densify             Densify a Polygon or MultiPolygon
    reproject           Reproject a Polygon or MultiPolygon
    simplify            Simplify a Polygon or MultiPolygon
```

Import `raster_footprint` functions into your Python script:

```Python
from raster_footprint import footprint_from_href

footprint = footprint_from_href(
    "my_raster.tif",
    densify_distance=100,
    simplify_tolerance=0.001,
    holes=False
)
```

See the [API documentation](https://raster-footprint.readthedocs.io/) for available functions and options.

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

## Contributing

Github [issues](https://github.com/pjhartzell/raster-footprint/issues) and [pull requests](https://github.com/pjhartzell/raster-footprint/pulls).

## License

[Apache-2.0](https://github.com/pjhartzell/raster-footprint/blob/main/LICENSE)
