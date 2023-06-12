import pytest
from shapely.geometry import shape

from raster_footprint import densify_by_distance, densify_by_factor, densify_extent

from .conftest import read_geojson


def test_densify_by_distance() -> None:
    coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]
    assert len(coords) == 5
    densified_coords = densify_by_distance(coords, 3.33)
    for coord in coords:
        assert coord in densified_coords
    assert len(densified_coords) == 17


def test_densify_by_factor() -> None:
    coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]
    assert len(coords) == 5
    densified_coords = densify_by_factor(coords, 2)
    for coord in coords:
        assert coord in densified_coords
    assert len(densified_coords) == 9


def test_densify_polygon() -> None:
    polygon = shape(read_geojson("concave-shell.json"))
    assert len(polygon.exterior.coords) == 13

    densified_by_factor = densify_extent(polygon, factor=2)
    assert len(densified_by_factor.exterior.coords) == 25
    assert densified_by_factor.exterior.is_ccw

    densified_by_distance = densify_extent(polygon, distance=1)
    assert len(densified_by_distance.exterior.coords) == 29
    assert densified_by_distance.exterior.is_ccw


def test_densify_polygon_with_holes() -> None:
    polygon = shape(read_geojson("concave-shell-with-two-holes.json"))
    assert len(polygon.exterior.coords) == 13
    assert len(polygon.interiors) == 2
    for interior in polygon.interiors:
        assert len(interior.coords) == 5

    densified_by_factor = densify_extent(polygon, factor=2)
    assert len(densified_by_factor.exterior.coords) == 25
    assert densified_by_factor.exterior.is_ccw
    assert len(densified_by_factor.interiors) == 2
    for interior in densified_by_factor.interiors:
        assert len(interior.coords) == 9
        assert not interior.is_ccw

    densified_by_distance = densify_extent(polygon, distance=1)
    assert len(densified_by_distance.exterior.coords) == 29
    assert densified_by_distance.exterior.is_ccw
    assert len(densified_by_distance.interiors) == 2
    for interior in densified_by_distance.interiors:
        assert len(interior.coords) == 7
        assert not interior.is_ccw


def test_densify_multi_polygon_with_holes() -> None:
    multi_polygon = shape(read_geojson("two-concave-shells-each-with-two-holes.json"))
    for polygon in multi_polygon.geoms:
        assert len(polygon.exterior.coords) == 13
        assert len(polygon.interiors) == 2
        for interior in polygon.interiors:
            assert len(interior.coords) == 5

    densified_by_factor = densify_extent(multi_polygon, factor=2)
    for polygon in densified_by_factor.geoms:
        assert len(polygon.exterior.coords) == 25
        assert polygon.exterior.is_ccw
        assert len(polygon.interiors) == 2
        for interior in polygon.interiors:
            assert len(interior.coords) == 9
            assert not interior.is_ccw

    densified_by_distance = densify_extent(multi_polygon, distance=1)
    for polygon in densified_by_distance.geoms:
        assert len(polygon.exterior.coords) == 29
        assert polygon.exterior.is_ccw
        assert len(polygon.interiors) == 2
        for interior in polygon.interiors:
            assert len(interior.coords) == 7
            assert not interior.is_ccw


def test_double_option_fails() -> None:
    with pytest.raises(
        ValueError, match="Only one of 'factor' or 'distance' can be specified."
    ):
        densify_extent(shape(read_geojson("concave-shell.json")), factor=2, distance=1)
