import numpy as np
import numpy.typing as npt
import pytest
from raster_footprint import create_mask
from raster_footprint.mask import get_mask_geometry
from rasterio import Affine
from shapely.geometry import shape

from .conftest import read_geojson

TRANSFORM = Affine(1, 0, 0, 0, -1, 0)


@pytest.fixture
def concave_shell() -> npt.NDArray[np.uint8]:
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[1:7, 1:7] = 255
    mask[3:5, 1] = 0
    mask[6, 3:5] = 0
    return mask


@pytest.fixture
def two_concave_shells() -> npt.NDArray[np.uint8]:
    mask = np.zeros((8, 15), dtype=np.uint8)
    mask[1:7, 1:7] = 255
    mask[3:5, 1] = 0
    mask[6, 3:5] = 0
    mask[1:7, 8:14] = 255
    mask[3:5, 13] = 0
    mask[6, 10:12] = 0
    return mask


@pytest.fixture
def two_concave_shells_with_holes() -> npt.NDArray[np.uint8]:
    mask = np.zeros((8, 15), dtype=np.uint8)
    mask[1:7, 1:7] = 255
    mask[3:5, 1] = 0
    mask[6, 3:5] = 0
    mask[2:5, 3:6] = 0
    mask[3, 4] = 255
    mask[1:7, 8:14] = 255
    mask[3:5, 13] = 0
    mask[6, 10:12] = 0
    mask[2:5, 9] = 0
    mask[2:5, 11] = 0
    return mask


def test_create_mask_nodata_none() -> None:
    expected = np.ones((5, 5), dtype=np.uint8) * 255

    array_2d = np.random.rand(5, 5)
    mask = create_mask(array_2d, nodata=None)
    assert np.array_equal(mask, expected)

    array_3d = np.random.rand(2, 5, 5)
    mask = create_mask(array_3d, nodata=None)
    assert np.array_equal(mask, expected)


def test_create_mask_nan_nodata() -> None:
    array = np.random.rand(5, 5)
    array[2, 2] = np.nan
    mask = create_mask(array, nodata=np.nan)
    expected = np.ones((5, 5), dtype=np.uint8) * 255
    expected[2, 2] = 0
    assert np.array_equal(mask, expected)


def test_create_mask_2d_array() -> None:
    array = np.random.rand(5, 5)
    array[2, 2] = 0
    mask = create_mask(array, nodata=0)
    expected = np.ones((5, 5), dtype=np.uint8) * 255
    expected[2, 2] = 0
    assert np.array_equal(mask, expected)


def test_create_mask_3d_array() -> None:
    array = np.random.rand(2, 5, 5)
    array[0, 2, 2] = 0
    array[1, 1:4, 1:4] = 0
    mask = create_mask(array, nodata=0)
    expected = np.ones((5, 5), dtype=np.uint8) * 255
    expected[2, 2] = 0
    assert np.array_equal(mask, expected)


def test_geometry_concave_shell(concave_shell: npt.NDArray[np.uint8]) -> None:
    geometry = get_mask_geometry(concave_shell, transform=TRANSFORM)
    expected = read_geojson("concave-shell")
    assert shape(geometry).normalize() == shape(expected).normalize()


def test_geometry_convex_hull_of_concave_shell(
    concave_shell: npt.NDArray[np.uint8],
) -> None:
    geometry = get_mask_geometry(concave_shell, transform=TRANSFORM, convex_hull=True)
    expected = read_geojson("convex-hull-of-concave-shell")
    assert shape(geometry).normalize() == shape(expected).normalize()


def test_geometry_two_concave_shells(
    two_concave_shells: npt.NDArray[np.uint8],
) -> None:
    geometry = get_mask_geometry(two_concave_shells, transform=TRANSFORM)
    expected = read_geojson("two-concave-shells")
    assert shape(geometry).normalize() == shape(expected).normalize()


def test_geometry_convex_hull_of_two_concave_shells(
    two_concave_shells: npt.NDArray[np.uint8],
) -> None:
    geometry = get_mask_geometry(
        two_concave_shells, transform=TRANSFORM, convex_hull=True
    )
    expected = read_geojson("convex-hull-of-two-concave-shells")
    assert shape(geometry).normalize() == shape(expected).normalize()


def test_geometry_two_concave_shells_with_holes(
    two_concave_shells_with_holes: npt.NDArray[np.uint8],
) -> None:
    geometry = get_mask_geometry(
        two_concave_shells_with_holes, transform=TRANSFORM, holes=True
    )
    expected = read_geojson("two-concave-shells-with-holes")
    assert shape(geometry).normalize() == shape(expected).normalize()


def test_geometry_convex_hull_of_two_concave_shells_with_holes(
    two_concave_shells_with_holes: npt.NDArray[np.uint8],
) -> None:
    geometry = get_mask_geometry(
        two_concave_shells_with_holes, transform=TRANSFORM, convex_hull=True
    )
    expected = read_geojson("convex-hull-of-two-concave-shells")
    assert shape(geometry).normalize() == shape(expected).normalize()


def test_geometry_two_concave_shells_with_holes_filled(
    two_concave_shells_with_holes: npt.NDArray[np.uint8],
) -> None:
    geometry = get_mask_geometry(two_concave_shells_with_holes, transform=TRANSFORM)
    expected = read_geojson("two-concave-shells")
    assert shape(geometry).normalize() == shape(expected).normalize()
