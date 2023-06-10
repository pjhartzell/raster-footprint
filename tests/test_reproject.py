# - test noop (4326)
# - test epsg
# - test wkt
from shapely.geometry import shape

from raster_footprint.raster_footprint import reproject_polygon

from .conftest import read_expected


def test_epsg_noop() -> None:
    polygon = shape(read_expected("single-concave-shell.json"))
    reprojected_polygon = reproject_polygon(polygon, 4326)
    assert polygon.normalize() == reprojected_polygon.normalize()


# def test_epsg_utm() -> None:
#     polygon = shape(
#         read_expected("double-concave-shell-with-holes-epsg-32631-input.json")
#     )
#     reprojected_polygon = reproject_polygon(polygon, 32631)
#     expected = shape(
#         read_expected("double-concave-shell-with-holes-epsg-32631-reprojected.json")
#     )
#     assert reprojected_polygon.normalize() == expected.normalize()


def test_wkt_sinusoidal() -> None:
    ...
