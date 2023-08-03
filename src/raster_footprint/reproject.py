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
    """Reprojects a polygon to WGS84 (EPSG:4326).

    Reprojected polygon vertex coordinates are rounded to ``precision``.
    Duplicate points caused by rounding are removed.

    Args:
        polygon (Polygon): The polygon to reproject.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the given ``polygon``.
        precision (Optional[int]): The number of decimal places to include in
            the reprojected polygon vertex coordinates. Defaults to 7.

    Returns:
        Polygon: The reprojected polygon.
    """
    polygon = shape(transform_geom(crs, "EPSG:4326", polygon, precision=precision))
    shell = [k for k, _ in groupby(polygon.exterior.coords)]
    holes = [[k for k, _ in groupby(interior.coords)] for interior in polygon.interiors]
    return Polygon(shell=shell, holes=holes)


def reproject_multipolygon(
    multipolygon: MultiPolygon,
    crs: CRS,
    *,
    precision: Optional[int] = DEFAULT_PRECISION,
) -> MultiPolygon:
    """Reprojects each polygon in a multipolygon to WGS84 (EPSG:4326).

    Reprojected polygon vertex coordinates are rounded to ``precision``.
    Duplicate points caused by rounding are removed.

    Args:
        multipolygon (MultiPolygon): The multipolygon to reproject.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the given ``multipolygon``.
        precision (Optional[int]): The number of decimal places to include in
            the final polygon vertex coordinates. Defaults to 7.

    Returns:
        MultiPolygon: The reprojected multipolygon.
    """
    reprojected_polygons = [
        reproject_polygon(polygon, crs, precision=precision)
        for polygon in multipolygon.geoms
    ]
    return MultiPolygon(reprojected_polygons)


def reproject_extent(
    extent: T,
    crs: CRS,
    *,
    precision: Optional[int] = DEFAULT_PRECISION,
) -> T:
    """Reprojects a polygon or multipolygon to WGS84 (EPSG:4326).

    Reprojected polygon vertex coordinates are rounded to ``precision``.
    Duplicate points caused by rounding are removed.

    Args:
        extent (T): The polygon or multipolygon to reproject.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the given ``extent``.
        precision (Optional[int]): The number of decimal places to include in
            the final polygon vertex coordinates. Defaults to 7.

    Returns:
        T: The reprojected polygon or multipolygon.
    """
    if isinstance(extent, Polygon):
        return reproject_polygon(extent, crs, precision=precision)
    elif isinstance(extent, MultiPolygon):
        return reproject_multipolygon(extent, crs, precision=precision)
    else:
        raise TypeError("extent must be a Polygon or MultiPolygon")
