from shapely.geometry import shape

from raster_footprint import simplify_extent

from .conftest import read_geojson


def test_simplify_polygon() -> None:
    polygon = shape(read_geojson("concave-shell.json"))
    assert len(polygon.exterior.coords) == 13
    simplified = simplify_extent(polygon, tolerance=1.1)
    assert simplified.exterior.is_ccw
    expected = shape(read_geojson("convex-hull-of-concave-shell.json"))
    assert simplified.normalize() == expected.normalize()
