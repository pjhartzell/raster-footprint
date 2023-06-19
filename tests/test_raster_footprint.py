import numpy as np
from shapely.geometry import Polygon, shape

from raster_footprint.footprint import footprint_from_data

from .conftest import CRS, TRANSFORM, check_winding


def test_no_footprint() -> None:
    data_array = np.zeros((3, 3), dtype=np.uint8)
    assert footprint_from_data(data_array, CRS, TRANSFORM, no_data=0) is None


def test_entire_footprint() -> None:
    data_array = np.zeros((3, 3), dtype=np.uint8)
    footprint = shape(footprint_from_data(data_array, CRS, TRANSFORM, no_data=None))
    check_winding(footprint)
    assert footprint == Polygon([(0, 0), (0, -3), (3, -3), (3, 0), (0, 0)])


# def test_entire() -> None:
#     href = "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif"
#     footprint = RasterFootprint.from_href(href, entire=True).footprint()

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.8852067, 40.4853073],
#                 [-105.8840275, 40.3953528],
#                 [-105.6366831, 40.3969793],
#                 [-105.6375325, 40.486939],
#                 [-105.8852067, 40.4853073],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     assert shape(geometry) == shape(footprint)


# import shutil
# from pathlib import Path

# import rasterio

# from raster_footprint.raster_footprint import (
#     RasterFootprint,
#     densify_by_distance,
#     densify_by_factor,
# )


# def test_multiband_all_bands() -> None:
#     href = "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif"
#     footprint = RasterFootprint.from_href(
#         href, no_data=0, bands=[], simplify_tolerance=0.005
#     ).footprint()
#     assert footprint

#     # import json

#     # with open("all-bands.json", "w") as f:
#     #     f.write(json.dumps(footprint, indent=4))

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.7853028, 40.4749528],
#                 [-105.808413, 40.3959062],
#                 [-105.6366831, 40.3969793],
#                 [-105.6372387, 40.455872],
#                 [-105.7853028, 40.4749528],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     expected = shape(geometry)
#     assert shape(footprint) == expected


# def test_multiband_single_band() -> None:
#     href = "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif"
#     footprint = RasterFootprint.from_href(
#         href, no_data=0, bands=[2], simplify_tolerance=0.005
#     ).footprint()
#     assert footprint

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.7838846, 40.4746923],
#                 [-105.8066463, 40.3959185],
#                 [-105.6366831, 40.3969793],
#                 [-105.6372362, 40.4556019],
#                 [-105.7838846, 40.4746923],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     expected = shape(geometry)
#     assert shape(footprint) == expected


# def test_multiband_some_bands() -> None:
#     href = "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif"
#     footprint = RasterFootprint.from_href(
#         href, no_data=0, bands=[1, 4, 5, 6], simplify_tolerance=0.005
#     ).footprint()
#     assert footprint

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.7824664, 40.4744317],
#                 [-105.8052329, 40.3959284],
#                 [-105.6366831, 40.3969793],
#                 [-105.6372387, 40.455872],
#                 [-105.7824664, 40.4744317],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     expected = shape(geometry)
#     assert shape(footprint) == expected


# def test_nonmatching_nodata_all_bands(tmp_path: Path) -> None:
#     href = str(tmp_path / "test.tif")
#     shutil.copy(
#         "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif", href
#     )
#     with rasterio.open(href, "r+") as src:
#         src.nodata = 1

#     footprint = RasterFootprint.from_href(
#         href, no_data=0, bands=[], simplify_tolerance=0.005
#     ).footprint()
#     assert footprint

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.7853028, 40.4749528],
#                 [-105.808413, 40.3959062],
#                 [-105.6366831, 40.3969793],
#                 [-105.6372387, 40.455872],
#                 [-105.7853028, 40.4749528],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     expected = shape(geometry)
#     assert shape(footprint) == expected


# def test_nonmatching_nodata_some_bands(tmp_path: Path) -> None:
#     href = str(tmp_path / "test.tif")
#     shutil.copy(
#         "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif", href
#     )
#     with rasterio.open(href, "r+") as src:
#         src.nodata = 1

#     footprint = RasterFootprint.from_href(
#         href, no_data=0, bands=[1, 4, 5, 6], simplify_tolerance=0.005
#     ).footprint()
#     assert footprint

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.7824664, 40.4744317],
#                 [-105.8052329, 40.3959284],
#                 [-105.6366831, 40.3969793],
#                 [-105.6372387, 40.455872],
#                 [-105.7824664, 40.4744317],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     expected = shape(geometry)
#     assert shape(footprint) == expected


# def test_from_numpy_array() -> None:
#     href = "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif"
#     with rasterio.open(href) as src:
#         numpy_array = src.read()
#         crs = src.crs
#         transform = src.transform
#         no_data = src.nodata
#     footprint = RasterFootprint.from_numpy_array(
#         numpy_array, crs, transform, no_data=no_data, simplify_tolerance=0.005
#     ).footprint()

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.7853028, 40.4749528],
#                 [-105.808413, 40.3959062],
#                 [-105.6366831, 40.3969793],
#                 [-105.6372387, 40.455872],
#                 [-105.7853028, 40.4749528],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     expected = shape(geometry)
#     assert shape(footprint) == expected


# def test_from_numpy_array_entire() -> None:
#     href = "tests/data/AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif"
#     with rasterio.open(href) as src:
#         numpy_array = src.read()
#         crs = src.crs
#         transform = src.transform
#     footprint = RasterFootprint.from_numpy_array(
#         numpy_array, crs, transform
#     ).footprint()

#     geometry = {
#         "type": "Polygon",
#         "coordinates": [
#             [
#                 [-105.8852067, 40.4853073],
#                 [-105.8840275, 40.3953528],
#                 [-105.6366831, 40.3969793],
#                 [-105.6375325, 40.486939],
#                 [-105.8852067, 40.4853073],
#             ]
#         ],
#     }
#     assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
#     assert shape(geometry) == shape(footprint)
#     assert shape(geometry) == shape(footprint)
#     assert shape(geometry) == shape(footprint)
