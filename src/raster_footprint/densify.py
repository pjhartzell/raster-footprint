from typing import Any, List, Optional, Tuple, TypeVar

import numpy as np
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

T = TypeVar("T", Polygon, MultiPolygon)


def densify_by_factor(
    point_list: List[Tuple[float, float]], factor: int
) -> List[Tuple[float, float]]:
    """Densifies the number of points in a list of points by a ``factor``. For
    example, a list of 5 points and a factor of 2 will result in 10 points (one
    new point between each original adjacent points).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        factor (int): The factor by which to densify the points. A larger
            densification factor should be used when reprojection results in
            greater curvature from the original geometry.

    Returns:
        List[Tuple[float, float]]: A list of the densified points.
    """  # noqa: E501
    points: Any = np.asarray(point_list)
    densified_number = len(points) * factor
    existing_indices = np.arange(0, densified_number, factor)
    interp_indices = np.arange(existing_indices[-1] + 1)
    interp_x = np.interp(interp_indices, existing_indices, points[:, 0])
    interp_y = np.interp(interp_indices, existing_indices, points[:, 1])
    return [(x, y) for x, y in zip(interp_x, interp_y)]


def densify_by_distance(
    point_list: List[Tuple[float, float]], distance: float
) -> List[Tuple[float, float]]:
    """Densifies the number of points in a list of points by inserting new
    points at intervals between each set of successive points. For example, if
    two successive points in the list are separated by 10 units and a
    ``distance`` of 2 is provided, 4 new points will be added between the two
    original points (one new point every 2 units of ``distance``).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        distance (float): The interval at which to insert additional points. A
            smaller densification distance should be used when reprojection
            results in greater curvature from the original geometry.

    Returns:
        List[Tuple[float, float]]: A list of the densified points.
    """
    points: Any = np.asarray(point_list)
    dxdy = points[1:, :] - points[:-1, :]
    segment_lengths = np.sqrt(np.sum(np.square(dxdy), axis=1))
    steps = segment_lengths / distance
    coordinate_steps = dxdy / steps.reshape(-1, 1)
    densified_points = np.empty((len(point_list) - 1,), dtype="O")
    for index in range(len(point_list) - 1):
        step = np.arange(steps[index])
        densified_points[index] = (
            np.array((step, step)).T * coordinate_steps[index] + points[index]
        )
    final_point = points[-1].reshape(1, -1)
    densified_array = np.concatenate((*densified_points, final_point), axis=0)
    return [(float(row[0]), float(row[1])) for row in densified_array]


def densify_polygon(
    polygon: Polygon,
    *,
    factor: Optional[int] = None,
    distance: Optional[float] = None,
) -> Polygon:
    """Adds vertices to a polygon using one of the mutually exclusive
    ``factor`` or ``distance`` options.

    Args:
        polygon (Polygon): The polygon to densify.
        factor (Optional[int]): The factor by which to densify the points. A
            larger densification factor should be used when reprojection results
            in greater curvature from the original geometry. Defaults to None.
        distance (Optional[float]): The interval at which to insert additional
            points. A smaller densification distance should be used when
            reprojection results in greater curvature from the original
            geometry. Defaults to None.

    Returns:
        Polygon: The densified polygon.
    """
    if factor is not None and distance is not None:
        raise ValueError("Only one of 'factor' or 'distance' can be specified.")
    if factor is not None:
        shell = densify_by_factor(polygon.exterior.coords, factor)
        holes = [
            densify_by_factor(interior.coords, factor) for interior in polygon.interiors
        ]
        return Polygon(shell=shell, holes=holes)
    elif distance is not None:
        shell = densify_by_distance(polygon.exterior.coords, distance)
        holes = [
            densify_by_distance(interior.coords, distance)
            for interior in polygon.interiors
        ]
        return Polygon(shell=shell, holes=holes)
    else:
        return polygon


def densify_multi_polygon(
    multi_polygon: MultiPolygon,
    *,
    factor: Optional[int] = None,
    distance: Optional[float] = None,
) -> MultiPolygon:
    densified_polygons = [
        densify_polygon(polygon, factor=factor, distance=distance)
        for polygon in multi_polygon.geoms
    ]
    return MultiPolygon(densified_polygons)


def densify_extent(
    extent: T,
    *,
    factor: Optional[int] = None,
    distance: Optional[float] = None,
) -> T:
    """Adds vertices to a polygon using one of the mutually exclusive
    ``factor`` or ``distance`` options.

    Args:
        extent (Union[Polygon, MultiPolygon]): The polygon to densify.
        factor (Optional[int]): The factor by which to densify the points. A
            larger densification factor should be used when reprojection results
            in greater curvature from the original geometry. Defaults to None.
        distance (Optional[float]): The interval at which to insert additional
            points. A smaller densification distance should be used when
            reprojection results in greater curvature from the original
            geometry. Defaults to None.

    Returns:
        Union[Polygon, MultiPolygon]: The densified polygon.
    """
    if isinstance(extent, Polygon):
        return densify_polygon(extent, factor=factor, distance=distance)
    elif isinstance(extent, MultiPolygon):
        return densify_multi_polygon(extent, factor=factor, distance=distance)
    else:
        raise TypeError("extent must be a Polygon or MultiPolygon")
