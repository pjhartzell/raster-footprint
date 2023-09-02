import pytest
from raster_footprint import densify_by_distance, densify_by_factor, densify_geometry
from shapely.geometry import Point, shape

from .conftest import check_winding, read_geojson

SQUARE = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]


def test_densify_by_distance() -> None:
    densified_coords = densify_by_distance(SQUARE, 3.33)
    for coord in SQUARE:
        assert coord in densified_coords
    assert len(densified_coords) == 17


def test_densify_by_factor() -> None:
    densified_coords = densify_by_factor(SQUARE, 2)
    for coord in SQUARE:
        assert coord in densified_coords
    assert len(densified_coords) == 9


def test_densify_polygon() -> None:
    polygon = shape(read_geojson("concave-shell.json"))
    assert len(polygon.exterior.coords) == 13

    densified_by_factor = densify_geometry(polygon, factor=2)
    assert len(densified_by_factor.exterior.coords) == 25
    check_winding(densified_by_factor)

    densified_by_distance = densify_geometry(polygon, distance=1)
    assert len(densified_by_distance.exterior.coords) == 29
    check_winding(densified_by_distance)


def test_densify_polygon_with_holes() -> None:
    polygon = shape(read_geojson("concave-shell-with-two-holes.json"))
    assert len(polygon.exterior.coords) == 13
    assert len(polygon.interiors) == 2
    for interior in polygon.interiors:
        assert len(interior.coords) == 5

    densified_by_factor = densify_geometry(polygon, factor=2)
    assert len(densified_by_factor.exterior.coords) == 25
    assert len(densified_by_factor.interiors) == 2
    for interior in densified_by_factor.interiors:
        assert len(interior.coords) == 9
    check_winding(densified_by_factor)

    densified_by_distance = densify_geometry(polygon, distance=1)
    assert len(densified_by_distance.exterior.coords) == 29
    assert len(densified_by_distance.interiors) == 2
    for interior in densified_by_distance.interiors:
        assert len(interior.coords) == 7
    check_winding(densified_by_distance)


def test_densify_multi_polygon_with_holes() -> None:
    multi_polygon = shape(read_geojson("two-concave-shells-each-with-two-holes.json"))
    for polygon in multi_polygon.geoms:
        assert len(polygon.exterior.coords) == 13
        assert len(polygon.interiors) == 2
        for interior in polygon.interiors:
            assert len(interior.coords) == 5

    densified_by_factor = densify_geometry(multi_polygon, factor=2)
    for polygon in densified_by_factor.geoms:
        assert len(polygon.exterior.coords) == 25
        assert len(polygon.interiors) == 2
        for interior in polygon.interiors:
            assert len(interior.coords) == 9
    check_winding(densified_by_factor)

    densified_by_distance = densify_geometry(multi_polygon, distance=1)
    for polygon in densified_by_distance.geoms:
        assert len(polygon.exterior.coords) == 29
        assert len(polygon.interiors) == 2
        for interior in polygon.interiors:
            assert len(interior.coords) == 7
    check_winding(densified_by_distance)


def test_densify_precision() -> None:
    def check_precision(geometry, precision):
        for polygon in geometry.geoms:
            for coord in polygon.exterior.coords:
                for value in coord:
                    assert len(str(value).split(".")[1]) <= precision
            for interior in polygon.interiors:
                for coord in interior.coords:
                    for value in coord:
                        assert len(str(value).split(".")[1]) <= precision

    precision = 6
    multipolygon = shape(
        read_geojson("two-concave-shells-each-with-two-holes-wkt-sinusoidal")
    )

    densified_by_factor = densify_geometry(multipolygon, factor=2, precision=precision)
    check_precision(densified_by_factor, precision)

    densified_by_distance = densify_geometry(
        multipolygon, distance=10000, precision=precision
    )
    check_precision(densified_by_distance, precision)


def test_double_option_fails() -> None:
    with pytest.raises(
        ValueError, match="Only one of 'factor' or 'distance' can be specified."
    ):
        densify_geometry(
            shape(read_geojson("concave-shell.json")), factor=2, distance=1
        )


def test_not_polygon_or_multi_polygon_fails() -> None:
    with pytest.raises(TypeError):
        densify_geometry(Point(0, 0))
