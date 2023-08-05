from typing import Optional, TypeVar

from shapely.geometry import MultiPolygon, Polygon

T = TypeVar("T", Polygon, MultiPolygon)


def simplify_polygon(polygon: Polygon, *, tolerance: Optional[float] = None) -> Polygon:
    """Reduces the number of vertices in the given ``polygon`` such that the
    outline of the simplified polygon is no further away from any of the
    original polygon vertices than ``tolerance``.

    Note that ``tolerance`` must be given in units of geographic decimal degrees.

    Args:
        polygon (Polygon): The polygon to simplify.
        tolerance (Optional[float]): The maximum distance between the original
            polygon vertices and the simplified polygon. Unit is geographic
            decimal degrees. Defaults to ``None``.

    Returns:
        Polygon: The simplified polygon.
    """
    if tolerance is not None:
        return polygon.simplify(tolerance=tolerance, preserve_topology=False)
    return polygon


def simplify_multipolygon(
    multipolygon: MultiPolygon, *, tolerance: Optional[float] = None
) -> MultiPolygon:
    """Reduces the number of vertices in each polygon of the given
    ``multipolygon`` such that the outline of each simplified polygon is no
    further away from any of its original vertices than ``tolerance``.

    Note that ``tolerance`` must be given in units of geographic decimal degrees.

    Args:
        multipolygon (MultiPolygon): The multipolygon to simplify.
        tolerance (Optional[float]): The maximum distance between original
            polygon vertices and the simplified polygon. Unit is geographic
            decimal degrees. Defaults to ``None``.

    Returns:
        MultiPolygon: The simplified multipolygon.
    """
    simplified_polygons = [
        simplify_polygon(polygon, tolerance=tolerance) for polygon in multipolygon.geoms
    ]
    return MultiPolygon(simplified_polygons)


def simplify_extent(extent: T, *, tolerance: Optional[float] = None) -> T:
    """Reduces the number of vertices in a polygon or each polygon of a
    multipolygon such that the outline of each simplified polygon is no
    further away from any of its original vertices than ``tolerance``.

    Args:
        extent (T): The polygon or multipolygon to simplify.
        tolerance (Optional[float]): The maximum distance between original
            polygon vertices and the simplified polygon. Unit is geographic
            decimal degrees. Defaults to ``None``.

    Returns:
        T: The simplified polygon or multipolygon.
    """
    if isinstance(extent, Polygon):
        return simplify_polygon(extent, tolerance=tolerance)
    elif isinstance(extent, MultiPolygon):
        return simplify_multipolygon(extent, tolerance=tolerance)
    else:
        raise TypeError("extent must be a Polygon or MultiPolygon")
