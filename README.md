# raster-footprint

[![CI Status](https://img.shields.io/github/actions/workflow/status/pjhartzell/raster-footprint/ci.yaml?style=for-the-badge&label=CI)](https://github.com/pjhartzell/raster-footprint/actions/workflows/ci.yaml)
[![Read the Docs](https://img.shields.io/readthedocs/raster-footprint?style=for-the-badge)](https://raster-footprint.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/raster-footprint?style=for-the-badge)](https://pypi.org/project/raster-footprint/)

[![GitHub](https://img.shields.io/github/license/pjhartzell/raster-footprint?style=for-the-badge)](https://github.com/pjhartzell/raster-footprint/blob/main/LICENSE)

Create GeoJSON geometries that bound valid raster data. Depends on [rasterio](https://rasterio.readthedocs.io/en/stable/) and [shapely](https://shapely.readthedocs.io/en/stable/manual.html).

## Installation

```shell
pip install raster-footprint
```

## CLI

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

## Python API

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

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup and the release process.

## License

[Apache-2.0](https://github.com/pjhartzell/raster-footprint/blob/main/LICENSE)
