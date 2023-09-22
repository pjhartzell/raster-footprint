"""This is a "private" module that is not part of our public API. The interfaces in this
module can change at any time without warning."""

import argparse
import json
import os
import sys
from typing import Optional

from shapely.geometry import mapping, shape

from raster_footprint import (
    densify_geometry,
    footprint_from_href,
    reproject_geometry,
    simplify_geometry,
)


def output(footprint, outfile: Optional[str] = None):
    if outfile is not None:
        dirname = os.path.dirname(outfile)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(outfile, "w") as f:
            json.dump(footprint, f, indent=4)
    else:
        print(json.dumps(footprint, indent=4))


def create(args) -> None:
    href = args.pop("infile")
    outfile = args.pop("outfile", None)

    footprint = footprint_from_href(href, **args)
    output(footprint, outfile)


def densify(args) -> None:
    infile = args.pop("infile")
    outfile = args.pop("outfile", None)

    with open(infile, "r") as f:
        geometry = shape(json.load(f))

    densified = mapping(densify_geometry(geometry, **args))
    output(densified, outfile)


def reproject(args) -> None:
    infile = args.pop("infile")
    outfile = args.pop("outfile", None)

    with open(infile, "r") as f:
        geometry = shape(json.load(f))

    reprojected = mapping(reproject_geometry(geometry, **args))
    output(reprojected, outfile)


def simplify(args) -> None:
    infile = args.pop("infile")
    outfile = args.pop("outfile", None)

    with open(infile, "r") as f:
        geometry = shape(json.load(f))

    simplified = mapping(simplify_geometry(geometry, **args))
    output(simplified, outfile)


def cli() -> None:
    # fmt: off
    parser = argparse.ArgumentParser(prog="raster-footprint")
    subparsers = parser.add_subparsers(title="commands", required=True)

    # create footprint
    parser_create = subparsers.add_parser("create", help="Create a raster footprint")
    parser_create.set_defaults(func=create)
    parser_create.add_argument("infile", help="Input raster filename")
    parser_create.add_argument("--outfile", help="Output footprint filename")
    parser_create.add_argument("--destination-crs", help="Footprint coordinate CRS")
    parser_create.add_argument("--nodata", type=float, help="Input raster nodata value")
    parser_create.add_argument("--precision", type=int, help="Footprint coordinate precision")

    densify_group_create = parser_create.add_mutually_exclusive_group()
    densify_group_create.add_argument("--densify-factor", type=int, help="Densification factor")
    densify_group_create.add_argument("--densify-distance", type=float, help="Densification distance")

    parser_create.add_argument("--simplify-tolerance", type=float, help="Simplification tolerance")
    parser_create.add_argument("--convex-hull", action="store_true", help="Apply convex hull to footprint")
    parser_create.add_argument("--holes", action="store_true", help="Include polygon holes in footprint")
    parser_create.add_argument("--bands", nargs="+", type=int, help="Raster band indices to include in footprint")
    parser_create.add_argument("--with-nodata", action="store_true", help="Include nodata pixels in the footprint")

    # densify footprint
    parser_densify = subparsers.add_parser("densify", help="Densify a Polygon or MultiPolygon")
    parser_densify.set_defaults(func=densify)
    parser_densify.add_argument("infile", help="Input footprint filename")
    parser_densify.add_argument("--outfile", help="Output footprint filename")

    densify_group_densify = parser_densify.add_mutually_exclusive_group(required=True)
    densify_group_densify.add_argument("--factor", type=int, help="Densification factor")
    densify_group_densify.add_argument("--distance", type=float, help="Densification distance")

    parser_densify.add_argument("--precision", type=int, help="Footprint coordinate precision")

    # reproject footprint
    parser_simplify = subparsers.add_parser("reproject", help="Reproject a Polygon or MultiPolygon")
    parser_simplify.set_defaults(func=reproject)
    parser_simplify.add_argument("infile", help="Input footprint filename")
    parser_simplify.add_argument("source_crs", type=int, help="Input footprint CRS EPSG code", metavar="source-epsg")
    parser_simplify.add_argument("destination_crs", type=int, help="Output footprint CRS EPSG code", metavar="destination-epsg")
    parser_simplify.add_argument("--outfile", help="Output footprint filename")
    parser_simplify.add_argument("--precision", type=int, help="Footprint coordinate precision")

    # simplify footprint
    parser_simplify = subparsers.add_parser("simplify", help="Simplify a Polygon or MultiPolygon")
    parser_simplify.set_defaults(func=simplify)
    parser_simplify.add_argument("infile", help="Input footprint filename")
    parser_simplify.add_argument("--outfile", help="Output footprint filename")
    parser_simplify.add_argument("--tolerance", type=float, help="Simplification tolerance")

    parser.parse_args(sys.argv[1:] or ["--help"])
    args = vars(parser.parse_args(sys.argv[1:] or ["--help"]))
    func = args.pop("func")
    args = {k: v for k, v in args.items() if v is not None}
    func(args)
    # fmt: on


if __name__ == "__main__":
    cli()
