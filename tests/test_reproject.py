import pytest
from shapely.geometry import Point, shape

from raster_footprint import reproject_extent

from .conftest import check_winding, read_geojson


def test_epsg_4326_is_noop() -> None:
    polygon = shape(read_geojson("concave-shell.json"))
    reprojected = reproject_extent(polygon, 4326)
    check_winding(reprojected)
    assert reprojected.normalize() == polygon.normalize()


def test_epsg_utm_32361() -> None:
    multi_polygon = shape(
        read_geojson("two-concave-shells-each-with-two-holes-epsg-32631.json")
    )
    reprojected = reproject_extent(multi_polygon, 32631, precision=5)
    expected = shape(read_geojson("two-concave-shells-each-with-two-holes.json"))
    check_winding(reprojected)
    assert reprojected.normalize() == expected.normalize()


def test_wkt_sinusoidal() -> None:
    wkt = 'PROJCS["AEA        WGS84",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'  # noqa
    multi_polygon = shape(
        read_geojson("two-concave-shells-each-with-two-holes-wkt-sinusoidal.json")
    )
    reprojected = reproject_extent(multi_polygon, wkt, precision=5)
    expected = shape(read_geojson("two-concave-shells-each-with-two-holes.json"))
    check_winding(reprojected)
    assert reprojected.normalize() == expected.normalize()


def test_remove_duplicate_points() -> None:
    duplicates = shape(read_geojson("concave-shell-with-duplicate-points.json"))
    deduplicated = shape(read_geojson("concave-shell.json"))
    reprojected = reproject_extent(duplicates, 4326)
    check_winding(reprojected)
    assert reprojected.normalize() == deduplicated.normalize()


def test_precision() -> None:
    polygon = shape(read_geojson("concave-shell-dithered.json"))

    reprojected = reproject_extent(polygon, 4326, precision=3)
    check_winding(reprojected)
    for coord in reprojected.exterior.coords:
        for value in coord:
            assert len(str(value).split(".")[1]) == 3
            assert str(value).endswith("3")

    reprojected = reproject_extent(polygon, 4326, precision=5)
    check_winding(reprojected)
    for coord in reprojected.exterior.coords:
        for value in coord:
            assert len(str(value).split(".")[1]) == 5
            assert str(value).endswith("6")


def test_not_polygon_or_multi_polygon_fails() -> None:
    with pytest.raises(TypeError):
        reproject_extent(Point(0, 0), 4326)
