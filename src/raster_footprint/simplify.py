from typing import Optional, TypeVar

from shapely.geometry import MultiPolygon, Polygon

T = TypeVar("T", Polygon, MultiPolygon)


def simplify_polygon(polygon: Polygon, *, tolerance: Optional[float] = None) -> Polygon:
    """Reduces the number of polygon vertices such that the simplified polygon
    shape is no further away from the original polygon vertices than
    ``tolerance``.

    Args:
        polygon (Polygon): The polygon to be simplify.
        tolerance (Optional[float]): The maximum distance between the original
            polygon vertices and the simplified polygon. Defaults to None.

    Returns:
        Polygon: The simplified polygon.
    """
    if tolerance is not None:
        # return orient(polygon.simplify(tolerance=tolerance, preserve_topology=False))
        return polygon.simplify(tolerance=tolerance, preserve_topology=False)
    return polygon


def simplify_multi_polygon(
    multi_polygon: MultiPolygon, *, tolerance: Optional[float] = None
) -> MultiPolygon:
    simplified_polygons = [
        simplify_polygon(polygon, tolerance=tolerance)
        for polygon in multi_polygon.geoms
    ]
    return MultiPolygon(simplified_polygons)


def simplify_extent(extent: T, *, tolerance: Optional[float] = None) -> T:
    if isinstance(extent, Polygon):
        return simplify_polygon(extent, tolerance=tolerance)
    elif isinstance(extent, MultiPolygon):
        return simplify_multi_polygon(extent, tolerance=tolerance)
    else:
        raise TypeError("extent must be a Polygon or MultiPolygon")
