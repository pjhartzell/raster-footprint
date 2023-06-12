# import numpy as np
# import numpy.typing as npt
# import pytest
# from raster_footprint.raster_footprint import RasterFootprint
# from rasterio.crs import CRS
# from rasterio.transform import Affine
# from shapely.geometry import shape

# from .conftest import read_expected


# @pytest.fixture
# def single_concave_shell() -> npt.NDArray[np.uint8]:
#     mask = np.zeros((8, 8), dtype=np.uint8)
#     mask[1:7, 1:7] = 255
#     mask[3:5, 1] = 0
#     mask[6, 3:5] = 0
#     mask[3, 4] = 255
#     return mask


# @pytest.fixture
# def double_concave_shell() -> npt.NDArray[np.uint8]:
#     mask = np.zeros((8, 15), dtype=np.uint8)
#     mask[1:7, 1:7] = 255
#     mask[3:5, 1] = 0
#     mask[6, 3:5] = 0
#     mask[3, 4] = 255
#     mask[1:7, 8:14] = 255
#     mask[3:5, 13] = 0
#     mask[6, 10:12] = 0
#     return mask


# @pytest.fixture
# def double_concave_shell_with_holes() -> npt.NDArray[np.uint8]:
#     mask = np.zeros((8, 15), dtype=np.uint8)
#     mask[1:7, 1:7] = 255
#     mask[3:5, 1] = 0
#     mask[6, 3:5] = 0
#     mask[2:5, 3:6] = 0
#     mask[3, 4] = 255
#     mask[1:7, 8:14] = 255
#     mask[2:5, 9:12] = 0
#     mask[3:5, 13] = 0
#     mask[6, 10:12] = 0
#     return mask


# @pytest.fixture
# def transform() -> Affine:
#     return Affine(1, 0, 0, 0, -1, 0)


# @pytest.fixture
# def crs() -> CRS:
#     return CRS.from_epsg(4326)


# def test_single_concave_shell(
#     single_concave_shell: npt.NDArray[np.uint8], transform: Affine, crs: CRS
# ) -> None:
#     footprint = RasterFootprint(single_concave_shell, crs, transform).footprint()
#     expected = read_expected("single-concave-shell")
#     assert shape(footprint).normalize() == shape(expected).normalize()


# def test_convex_hull_of_single_concave_shell(
#     single_concave_shell: npt.NDArray[np.uint8], transform: Affine, crs: CRS
# ) -> None:
#     footprint = RasterFootprint(
#         single_concave_shell, crs, transform, convex_hull=True
#     ).footprint()
#     expected = read_expected("convex-hull-of-single-concave-shell")
#     assert shape(footprint).normalize() == shape(expected).normalize()


# def test_double_concave_shell(
#     double_concave_shell: npt.NDArray[np.uint8], transform: Affine, crs: CRS
# ) -> None:
#     footprint = RasterFootprint(double_concave_shell, crs, transform).footprint()
#     expected = read_expected("double-concave-shell")
#     assert shape(footprint).normalize() == shape(expected).normalize()


# def test_convex_hull_of_double_concave_shell(
#     double_concave_shell: npt.NDArray[np.uint8], transform: Affine, crs: CRS
# ) -> None:
#     footprint = RasterFootprint(
#         double_concave_shell, crs, transform, convex_hull=True
#     ).footprint()
#     expected = read_expected("convex-hull-of-double-concave-shell")
#     assert shape(footprint).normalize() == shape(expected).normalize()


# def test_double_concave_shell_with_holes(
#     double_concave_shell_with_holes: npt.NDArray[np.uint8],
#     transform: Affine,
#     crs: CRS,
# ) -> None:
#     footprint = RasterFootprint(
#         double_concave_shell_with_holes, crs, transform
#     ).footprint()
#     expected = read_expected("double-concave-shell-with-holes")
#     assert shape(footprint).normalize() == shape(expected).normalize()


# def test_convex_hull_of_double_concave_shell_with_holes(
#     double_concave_shell_with_holes: npt.NDArray[np.uint8],
#     transform: Affine,
#     crs: CRS,
# ) -> None:
#     footprint = RasterFootprint(
#         double_concave_shell_with_holes, crs, transform, convex_hull=True
#     ).footprint()
#     expected = read_expected("convex-hull-of-double-concave-shell")
#     assert shape(footprint).normalize() == shape(expected).normalize()


# def test_double_concave_shell_with_holes_filled(
#     double_concave_shell_with_holes: npt.NDArray[np.uint8],
#     transform: Affine,
#     crs: CRS,
# ) -> None:
#     footprint = RasterFootprint(
#         double_concave_shell_with_holes,
#         crs,
#         transform,
#         holes=False,
#     ).footprint()
#     expected = read_expected("double-concave-shell")
#     assert shape(footprint).normalize() == shape(expected).normalize()
