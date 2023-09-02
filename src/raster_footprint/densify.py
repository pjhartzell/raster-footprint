from typing import Any, List, Optional, Tuple

import numpy as np
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

from .constants import DEFAULT_PRECISION, T


def densify_by_factor(
    point_list: List[Tuple[float, float]],
    factor: int,
    *,
    precision: int = DEFAULT_PRECISION,
) -> List[Tuple[float, float]]:
    """Increases the number of points in a list by a factor.

    Equidistant points are added between each pair of adjacent existing points.
    The number of points added is controlled by the ``factor`` argument. For
    example, a list of 5 points and a factor of 2 will result in a list of 9
    points (one new point added between each original set of adjacent points).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        factor (int): The factor by which to densify the points.
        precision (Optional[int]): The number of decimal places to include in
            the point coordinates. Defaults to 7.

    Returns:
        List[Tuple[float, float]]: The densified point list.
    """
    points: Any = np.asarray(point_list)
    densified_number = len(points) * factor
    existing_indices = np.arange(0, densified_number, factor)
    interp_indices = np.arange(existing_indices[-1] + 1)
    interp_x = np.round(
        np.interp(interp_indices, existing_indices, points[:, 0]), decimals=precision
    )
    interp_y = np.round(
        np.interp(interp_indices, existing_indices, points[:, 1]), decimals=precision
    )
    return [(x, y) for x, y in zip(interp_x, interp_y)]


def densify_by_distance(
    point_list: List[Tuple[float, float]],
    distance: float,
    *,
    precision: int = DEFAULT_PRECISION,
) -> List[Tuple[float, float]]:
    """Increases the number of points in a list according to a distance interval.

    New points are inserted between each pair of adjacent existing points with the
    spacing controlled by the ``distance`` argument. For example, if two
    adjacent points in the list are separated by 10 units and a ``distance`` of
    2 is provided, 4 new points will be inserted between the two original points
    (one new point every 2 units of ``distance``).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        distance (float): The interval at which to insert additional points.
        precision (Optional[int]): The number of decimal places to include in
            the point coordinates. Defaults to 7.

    Returns:
        List[Tuple[float, float]]: The densified point list.
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
    densified_array = np.round(
        np.concatenate((*densified_points, final_point), axis=0), decimals=precision
    )
    return [(float(row[0]), float(row[1])) for row in densified_array]


def densify_polygon(
    polygon: Polygon,
    *,
    factor: Optional[int] = None,
    distance: Optional[float] = None,
    precision: int = DEFAULT_PRECISION,
) -> Polygon:
    """Adds vertices to a polygon.

    Vertices are added according to one of the mutually exclusive ``factor`` or
    ``distance`` arguments.

    Args:
        polygon (Polygon): The polygon to densify.
        factor (Optional[int]): The factor by which to increase the number of
            polygon vertices, e.g., a ``factor`` of 2 will double the number of
            vertices. Mutually exclusive with ``distance``. Defaults to ``None``.
        distance (Optional[float]): The interval at which to insert additional
            polygon vertices, e.g., a ``distance`` of 2 will insert a new vertex
            every 2 units of distance between existing vertices. Mutually
            exclusive with ``factor``. Defaults to ``None``.
        precision (Optional[int]): The number of decimal places to include in
            the densified polygon vertex coordinates. Defaults to 7.

    Returns:
        Polygon: The densified polygon.
    """
    if factor is not None and distance is not None:
        raise ValueError("Only one of 'factor' or 'distance' can be specified.")
    if factor is not None:
        shell = densify_by_factor(polygon.exterior.coords, factor, precision=precision)
        holes = [
            densify_by_factor(interior.coords, factor, precision=precision)
            for interior in polygon.interiors
        ]
        return Polygon(shell=shell, holes=holes)
    elif distance is not None:
        shell = densify_by_distance(
            polygon.exterior.coords, distance, precision=precision
        )
        holes = [
            densify_by_distance(interior.coords, distance, precision=precision)
            for interior in polygon.interiors
        ]
        return Polygon(shell=shell, holes=holes)
    else:
        return polygon


def densify_multipolygon(
    multipolygon: MultiPolygon,
    *,
    factor: Optional[int] = None,
    distance: Optional[float] = None,
    precision: int = DEFAULT_PRECISION,
) -> MultiPolygon:
    """Adds vertices to each polygon in a multipolygon.

    Vertices are added according to one of the mutually exclusive ``factor`` or
    ``distance`` arguments.

    Args:
        multipolygon (MultiPolygon): The multipolygon to densify.
        factor (Optional[int]): The factor by which to increase the number of
            polygon vertices, e.g., a ``factor`` of 2 will double the number of
            vertices. mutually exclusive with ``distance``.  Defaults to ``None``.
        distance (Optional[float]): The interval at which to insert additional
            polygon vertices, e.g., a ``distance`` of 2 will insert a new vertex
            every 2 units of distance between existing vertices.  Mutually
            exclusive with ``factor``. Defaults to ``None``.
        precision (Optional[int]): The number of decimal places to include in
            the densified multipolygon vertex coordinates. Defaults to 7.

    Returns:
        MultiPolygon: The densified multipolygon.
    """
    densified_polygons = [
        densify_polygon(polygon, factor=factor, distance=distance, precision=precision)
        for polygon in multipolygon.geoms
    ]
    return MultiPolygon(densified_polygons)


def densify_geometry(
    geometry: T,
    *,
    factor: Optional[int] = None,
    distance: Optional[float] = None,
    precision: int = DEFAULT_PRECISION,
) -> T:
    """Adds vertices to a polygon or each polygon in a multipolygon.

    Args:
        geometry (T): The polygon or multipolygon to densify.
        factor (Optional[int]): The factor by which to increase the number of
            polygon vertices, e.g., a ``factor`` of 2 will double the number of
            vertices. Mutually exclusive with ``distance``. Defaults to ``None``.
        distance (Optional[float]): The interval at which to insert additional
            polygon vertices, e.g., a ``distance`` of 2 will insert a new vertex
            every 2 units of distance between existing vertices. Mutually
            exclusive with ``factor``. Defaults to ``None``.
        precision (Optional[int]): The number of decimal places to include in
            the densified geometry coordinates. Defaults to 7.

    Returns:
        T: The densified polygon or multipolygon.
    """
    if isinstance(geometry, Polygon):
        return densify_polygon(
            geometry, factor=factor, distance=distance, precision=precision
        )
    elif isinstance(geometry, MultiPolygon):
        return densify_multipolygon(
            geometry, factor=factor, distance=distance, precision=precision
        )
    else:
        raise TypeError("geometry must be a Polygon or MultiPolygon")
