"""Tests the footprint module.

Primarily tests `footprint_from_href` and `footprint_from_data` since
`footprint_from_rasterio_reader` and `footprint_from_mask` are called
internally by those functions.
"""

import shutil
from pathlib import Path
from typing import Tuple

import numpy as np
import pytest
import rasterio
from numpy import typing as npt
from raster_footprint.footprint import footprint_from_data, footprint_from_href
from rasterio import Affine
from rasterio.crs import CRS
from shapely.geometry import shape

from .conftest import TEST_DATA_DIRECTORY, check_winding, read_geojson

HrefDataCrsTransform = Tuple[str, npt.NDArray[np.uint8], CRS, Affine]

ASTER_HREF = str(
    Path(
        TEST_DATA_DIRECTORY,
        "geotiff",
        "AST_L1T_00310012006175412_20150516104359-SWIR.clipped.tif",
    )
)


@pytest.fixture
def modis_href_data_crs_transform() -> HrefDataCrsTransform:
    href = str(
        Path(
            TEST_DATA_DIRECTORY,
            "geotiff",
            "MCD43A4.A2001055.h25v06.006.2016113010159_B01.reduced.TIF",
        )
    )
    with rasterio.open(href) as src:
        data_array = src.read()
        crs = src.crs
        transform = src.transform
    return (href, data_array, crs, transform)


def test_no_footprint() -> None:
    data_array = np.zeros((3, 3), dtype=np.uint8)
    crs = "EPSG:4326"
    transform = Affine(1, 0, 0, 0, -1, 0)
    assert footprint_from_data(data_array, transform, crs, nodata=0) is None


def test_modis(modis_href_data_crs_transform: HrefDataCrsTransform) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis.json")

    href_footprint = footprint_from_href(href, holes=True)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(
        data_array, transform, crs, nodata=32767, holes=True
    )
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_with_nodata(modis_href_data_crs_transform: HrefDataCrsTransform) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis-with_nodata.json")

    href_footprint = footprint_from_href(href, with_nodata=True)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(data_array, transform, crs)
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_precision(modis_href_data_crs_transform: HrefDataCrsTransform) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis-precision-1.json")

    href_footprint = footprint_from_href(href, precision=1, holes=True)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(
        data_array, transform, crs, nodata=32767, precision=1, holes=True
    )
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_densify_factor(
    modis_href_data_crs_transform: HrefDataCrsTransform,
) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis-densify_factor-2.json")

    href_footprint = footprint_from_href(href, densify_factor=2, holes=True)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(
        data_array, transform, crs, nodata=32767, densify_factor=2, holes=True
    )
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_densify_distance(
    modis_href_data_crs_transform: HrefDataCrsTransform,
) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis-densify_distance-100000.json")

    href_footprint = footprint_from_href(href, densify_distance=100000, holes=True)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(
        data_array, transform, crs, nodata=32767, densify_distance=100000, holes=True
    )
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_simplify_tolerance(
    modis_href_data_crs_transform: HrefDataCrsTransform,
) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis-simplify_tolerance-0.05.json")

    href_footprint = footprint_from_href(href, simplify_tolerance=0.05, holes=True)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(
        data_array, transform, crs, nodata=32767, simplify_tolerance=0.05, holes=True
    )
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_densify_distance_and_simplify_tolerance(
    modis_href_data_crs_transform: HrefDataCrsTransform,
) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson(
        "modis-densify_distance-100000-simplify_tolerance-0.01.json"
    )

    href_footprint = footprint_from_href(
        href, densify_distance=100000, simplify_tolerance=0.01, holes=True
    )
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(
        data_array,
        transform,
        crs,
        nodata=32767,
        densify_distance=100000,
        simplify_tolerance=0.01,
        holes=True,
    )
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_convex_hull(modis_href_data_crs_transform: HrefDataCrsTransform) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis-convex_hull.json")

    href_footprint = footprint_from_href(href, convex_hull=True)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(
        data_array, transform, crs, nodata=32767, convex_hull=True
    )
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_modis_no_holes(modis_href_data_crs_transform: HrefDataCrsTransform) -> None:
    href, data_array, crs, transform = modis_href_data_crs_transform
    expected = read_geojson("modis-no_holes.json")

    href_footprint = footprint_from_href(href)
    check_winding(href_footprint)
    assert shape(href_footprint).normalize() == shape(expected).normalize()

    data_footprint = footprint_from_data(data_array, transform, crs, nodata=32767)
    check_winding(data_footprint)
    assert shape(data_footprint).normalize() == shape(expected).normalize()


def test_multiband_all_bands() -> None:
    footprint = footprint_from_href(ASTER_HREF, simplify_tolerance=0.005)
    check_winding(footprint)
    expected = read_geojson("aster-all-bands.json")
    assert shape(footprint).normalize() == shape(expected).normalize()


def test_multiband_single_band() -> None:
    footprint = footprint_from_href(ASTER_HREF, bands=[2], simplify_tolerance=0.005)
    check_winding(footprint)
    expected = read_geojson("aster-band-2.json")
    assert shape(footprint).normalize() == shape(expected).normalize()


def test_multiband_some_bands() -> None:
    footprint = footprint_from_href(
        ASTER_HREF, bands=[1, 4, 5, 6], simplify_tolerance=0.005
    )
    check_winding(footprint)
    expected = read_geojson("aster-bands-1-4-5-6.json")
    assert shape(footprint).normalize() == shape(expected).normalize()


def test_nonmatching_nodata_all_bands(tmp_path: Path) -> None:
    tmp_href = str(tmp_path / "test.tif")
    shutil.copy(ASTER_HREF, tmp_href)
    with rasterio.open(tmp_href, "r+") as src:
        src.nodata = 1

    footprint = footprint_from_href(tmp_href, nodata=0, simplify_tolerance=0.005)
    check_winding(footprint)
    expected = read_geojson("aster-all-bands.json")
    assert shape(footprint).normalize() == shape(expected).normalize()


def test_nonmatching_nodata_some_bands(tmp_path: Path) -> None:
    tmp_href = str(tmp_path / "test.tif")
    shutil.copy(ASTER_HREF, tmp_href)
    with rasterio.open(tmp_href, "r+") as src:
        src.nodata = 1

    footprint = footprint_from_href(
        tmp_href, nodata=0, bands=[1, 4, 5, 6], simplify_tolerance=0.005
    )
    check_winding(footprint)
    expected = read_geojson("aster-bands-1-4-5-6.json")
    assert shape(footprint).normalize() == shape(expected).normalize()
