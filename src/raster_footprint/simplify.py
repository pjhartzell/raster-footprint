from typing import Optional

from .constants import T


def simplify_geometry(geometry: T, *, tolerance: Optional[float] = None) -> T:
    """Reduces the number of vertices in a polygon or each polygon of a
    multipolygon such that the outline of each simplified polygon is no
    further away from any of its original vertices than ``tolerance``.

    Args:
        geometry (T): The polygon or multipolygon to simplify.
        tolerance (Optional[float]): The maximum distance between original
            polygon vertices and the simplified polygon. Unit is geographic
            decimal degrees. Defaults to ``None``.

    Returns:
        T: The simplified polygon or multipolygon.
    """
    if tolerance is not None:
        return geometry.simplify(tolerance=tolerance, preserve_topology=False)
    return geometry
