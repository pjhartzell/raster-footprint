import json
import os
import subprocess
from tempfile import TemporaryDirectory

from shapely.geometry import shape

from tests.conftest import TEST_DATA_DIRECTORY, check_winding, read_geojson


def test_cli_create() -> None:
    infile = os.path.join(
        TEST_DATA_DIRECTORY,
        "geotiff",
        "MCD43A4.A2001055.h25v06.006.2016113010159_B01.reduced.TIF",
    )
    densify_distance = 100000
    simplify_tolerance = 0.01

    with TemporaryDirectory() as tmp_dir:
        outfile = os.path.join(tmp_dir, "from_href.json")
        subprocess.run(
            [
                "raster-footprint",
                "create",
                infile,
                "--outfile",
                outfile,
                "--densify-distance",
                str(densify_distance),
                "--simplify-tolerance",
                str(simplify_tolerance),
                "--holes",
            ],
            check=True,
        )

        with open(outfile) as f:
            from_href = shape(json.load(f))
        expected = shape(
            read_geojson("modis-densify_distance-100000-simplify_tolerance-0.01.json")
        )

        check_winding(from_href)
        assert from_href.normalize() == expected.normalize()


def test_cli_densify() -> None:
    infile = os.path.join(
        TEST_DATA_DIRECTORY,
        "geojson",
        "concave-shell.json",
    )
    factor = 2
    distance = 1

    with TemporaryDirectory() as tmp_dir:
        outfile_factor = os.path.join(tmp_dir, "densified_by_factor.json")
        subprocess.run(
            [
                "raster-footprint",
                "densify",
                infile,
                "--outfile",
                outfile_factor,
                "--factor",
                str(factor),
            ],
            check=True,
        )
        with open(outfile_factor) as f:
            densified_by_factor = shape(json.load(f))

        check_winding(densified_by_factor)
        assert len(densified_by_factor.exterior.coords) == 25

        outfile_distance = os.path.join(tmp_dir, "densified_by_distance.json")
        subprocess.run(
            [
                "raster-footprint",
                "densify",
                infile,
                "--outfile",
                outfile_distance,
                "--distance",
                str(distance),
            ],
            check=True,
        )
        with open(outfile_distance) as f:
            densified_by_distance = shape(json.load(f))

        check_winding(densified_by_distance)
        assert len(densified_by_distance.exterior.coords) == 29


def test_cli_reproject() -> None:
    infile = os.path.join(
        TEST_DATA_DIRECTORY,
        "geojson",
        "two-concave-shells-each-with-two-holes-epsg-32631.json",
    )
    source_epsg = 32631
    destination_epsg = 4326
    precision = 5

    with TemporaryDirectory() as tmp_dir:
        outfile = os.path.join(tmp_dir, "reprojected.json")
        subprocess.run(
            [
                "raster-footprint",
                "reproject",
                infile,
                str(source_epsg),
                str(destination_epsg),
                "--outfile",
                outfile,
                "--precision",
                str(precision),
            ],
            check=True,
        )

        with open(outfile) as f:
            reprojected = shape(json.load(f))
        expected = shape(read_geojson("two-concave-shells-each-with-two-holes.json"))

        check_winding(reprojected)
        assert reprojected.normalize() == expected.normalize()


def test_cli_simplify() -> None:
    infile = os.path.join(
        TEST_DATA_DIRECTORY,
        "geojson",
        "concave-shell.json",
    )
    tolerance = 1.1

    with TemporaryDirectory() as tmp_dir:
        outfile = os.path.join(tmp_dir, "simplified.json")
        subprocess.run(
            [
                "raster-footprint",
                "simplify",
                infile,
                "--outfile",
                outfile,
                "--tolerance",
                str(tolerance),
            ],
            check=True,
        )

        with open(outfile) as f:
            simplified = shape(json.load(f))
        expected = shape(read_geojson("convex-hull-of-concave-shell.json"))

        check_winding(simplified)
        assert simplified.normalize() == expected.normalize()
