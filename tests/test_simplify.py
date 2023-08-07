from raster_footprint import simplify_geometry
from shapely.geometry import shape

from .conftest import check_winding, read_geojson


def test_simplify_polygon() -> None:
    polygon = shape(read_geojson("concave-shell.json"))
    assert len(polygon.exterior.coords) == 13
    simplified = simplify_geometry(polygon, tolerance=1.1)
    expected = shape(read_geojson("convex-hull-of-concave-shell.json"))
    check_winding(simplified)
    assert simplified.normalize() == expected.normalize()


def test_simplify_polygon_with_holes() -> None:
    polygon = shape(read_geojson("concave-shell-with-two-holes.json"))

    # small tolerance retains holes
    simplified = simplify_geometry(polygon, tolerance=0.8)
    expected = shape(read_geojson("concave-shell-with-two-holes-simplified_0.8.json"))
    check_winding(simplified)
    assert simplified.normalize() == expected.normalize()

    # large tolerance removes holes
    simplified = simplify_geometry(polygon, tolerance=1.1)
    expected = shape(read_geojson("convex-hull-of-concave-shell.json"))
    check_winding(simplified)
    assert simplified.normalize() == expected.normalize()

    # very large tolerance eliminates polygon
    simplified = simplify_geometry(polygon, tolerance=10)
    assert simplified.is_empty


def test_simplify_multi_polygon_with_holes() -> None:
    multi_polygon = shape(read_geojson("two-concave-shells-each-with-two-holes.json"))

    # small tolerance simplifies shells, retains holes
    simplified = simplify_geometry(multi_polygon, tolerance=0.8)
    expected = shape(
        read_geojson("two-concave-shells-each-with-two-holes-simplified_0.8.json")
    )
    check_winding(simplified)
    assert simplified.normalize() == expected.normalize()

    # large tolerance simplifes shells, removes holes
    simplified = simplify_geometry(multi_polygon, tolerance=1.1)
    expected = shape(
        read_geojson("two-concave-shells-each-with-two-holes-simplified_1.1.json")
    )
    check_winding(simplified)
    assert simplified.normalize() == expected.normalize()

    # very large tolerance eliminates all polygons
    simplified = simplify_geometry(multi_polygon, tolerance=10)
    assert simplified.is_empty
