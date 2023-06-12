from itertools import groupby
from typing import Optional, TypeVar

from rasterio.crs import CRS
from rasterio.warp import transform_geom
from shapely.geometry import MultiPolygon, Polygon, shape

DEFAULT_PRECISION = 7

T = TypeVar("T", Polygon, MultiPolygon)


def reproject_polygon(
    polygon: Polygon, crs: CRS, *, precision: Optional[int] = DEFAULT_PRECISION
) -> Polygon:
    """Projects a polygon to EPSG 4326 and rounds the projected vertex
    coordinates to ``precision``.

    Duplicate points caused by rounding are removed.

    Args:
        polygon (Polygon): The polygon to reproject.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the input polygon.
        precision (Optional[int]): The number of decimal places to include in
            the final polygon vertex coordinates. Defaults to 7.

    Returns:
        Polygon: The reprojected polygon.
    """
    polygon = shape(transform_geom(crs, "EPSG:4326", polygon, precision=precision))
    # Rounding to precision can produce duplicate coordinates, so we remove
    # them. Once shapely>=2.0.0 is required, this can be replaced with
    # shapely.constructive.remove_repeated_points
    shell = [k for k, _ in groupby(polygon.exterior.coords)]
    holes = [[k for k, _ in groupby(interior.coords)] for interior in polygon.interiors]
    return Polygon(shell=shell, holes=holes)


def reproject_multi_polygon(
    multi_polygon: MultiPolygon,
    crs: CRS,
    *,
    precision: Optional[int] = DEFAULT_PRECISION,
) -> MultiPolygon:
    reprojected_polygons = [
        reproject_polygon(polygon, crs, precision=precision)
        for polygon in multi_polygon.geoms
    ]
    return MultiPolygon(reprojected_polygons)


def reproject_extent(
    extent: T,
    crs: CRS,
    *,
    precision: Optional[int] = DEFAULT_PRECISION,
) -> T:
    if isinstance(extent, Polygon):
        return reproject_polygon(extent, crs, precision=precision)
    elif isinstance(extent, MultiPolygon):
        return reproject_multi_polygon(extent, crs, precision=precision)
    else:
        raise TypeError("extent must be a Polygon or MultiPolygon")
