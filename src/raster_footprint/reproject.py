from typing import Optional, TypeVar

from rasterio.crs import CRS
from rasterio.warp import transform_geom
from shapely.constructive import remove_repeated_points
from shapely.geometry import MultiPolygon, Polygon, shape

DEFAULT_PRECISION = 7

T = TypeVar("T", Polygon, MultiPolygon)


def reproject_geometry(
    source_crs: CRS,
    destination_crs: CRS,
    geometry: T,
    *,
    precision: Optional[int] = DEFAULT_PRECISION,
) -> T:
    """Reprojects a polygon or multipolygon from a source CRS to a destination CRS.

    Reprojected polygon vertex coordinates are rounded to ``precision``.
    Duplicate points caused by rounding are removed.

    Args:
        source_crs (CRS): A :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the input ``geometry``.
        destination_crs (CRS): A :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the output geometry.
        geometry (T): The polygon or multipolygon to reproject.
        precision (Optional[int]): The number of decimal places to include in
            the final polygon vertex coordinates. Defaults to 7.

    Returns:
        T: The reprojected polygon or multipolygon.
    """
    return remove_repeated_points(
        shape(
            transform_geom(source_crs, destination_crs, geometry, precision=precision)
        )
    )
