# raster-footprint

[![CI Status](https://img.shields.io/github/actions/workflow/status/pjhartzell/raster-footprint/ci.yaml?style=for-the-badge&label=CI)](https://github.com/pjhartzell/raster-footprint/actions/workflows/ci.yaml)
[![Read the Docs](https://img.shields.io/readthedocs/antimeridian?style=for-the-badge)](https://raster-footprint.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/raster-footprint?style=for-the-badge)](https://pypi.org/project/raster-footprint/)

[![GitHub](https://img.shields.io/github/license/pjhartzell/raster-footprint?style=for-the-badge)](https://github.com/pjhartzell/raster-footprint/blob/main/LICENSE)

Create GeoJSON geometries that bound valid (not "nodata" pixels) raster data. Depends on [rasterio](https://rasterio.readthedocs.io/en/stable/) and [shapely](https://shapely.readthedocs.io/en/stable/manual.html).

## Usage

```shell
pip install raster-footprint
```

Import and call one of the footprint functions with some options:

```python
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

Clone and install in editable mode with the development optional dependencies:

```shell
git https://github.com/pjhartzell/raster-footprint
cd raster-footprint
pip install -e ".[dev,docs]"
```

We use [pytest](https://docs.pytest.org/) for tests:

```shell
pytest
```

We use [Sphinx](https://www.sphinx-doc.org/) for docs:

```shell
make -C docs html
```

## Contributing

Github [issues](https://github.com/pjhartzell/raster-footprint/issues) and [pull requests](https://github.com/pjhartzell/raster-footprint/pulls).

## License

[Apache-2.0](https://github.com/pjhartzell/raster-footprint/blob/main/LICENSE)
