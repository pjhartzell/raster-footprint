from typing import Any, Optional, Union

import numpy as np
import rasterio.features
from affine import Affine
from numpy import typing as npt
from shapely import unary_union
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon, orient


def create_mask(
    data_array: npt.NDArray[Any], *, nodata: Optional[Union[int, float]] = None
) -> npt.NDArray[np.uint8]:
    """Produces a mask of valid data locations in a NumPy array.

    Locations in ``data_array`` matching the given ``nodata`` value are set to
    0; all other array locations are set to 255. If ``nodata`` is not provided,
    all array locations are set to 255.

    Args:
        data_array (numpy.NDArray[Any]): A NumPy 2D or 3D array of raster data.
        nodata (Optional[Union[int, float]]): The nodata value. If not
            provided, all array locations are set to 255. Defaults to ``None``.

    Returns:
        numpy.NDArray[numpy.uint8]: A 2D NumPy array containing 0s and 255s for
        nodata/data pixels.
    """
    if data_array.ndim == 2:
        data_array = data_array[np.newaxis, :]
    array_shape = data_array.shape
    if nodata is not None:
        mask: npt.NDArray[np.uint8] = np.full(array_shape, fill_value=0, dtype=np.uint8)
        if np.isnan(nodata):
            mask[~np.isnan(data_array)] = 1
        else:
            mask[data_array != nodata] = 1
        mask = np.sum(mask, axis=0, dtype=np.uint8)
        mask[mask > 0] = 255
    else:
        mask = np.full(array_shape[-2:], fill_value=255, dtype=np.uint8)
    return mask


def get_mask_geometry(
    mask: npt.NDArray[np.uint8],
    *,
    transform: Affine = Affine(1, 0, 0, 0, 1, 0),
    convex_hull: bool = False,
    holes: bool = False,
) -> Optional[Union[Polygon, MultiPolygon]]:
    """Creates a polygon or multipolygon surrounding valid data pixels.

    Polygons are created around each contiguous region of valid data pixels
    in the given ``mask``, where a valid data pixel has a value of 255.

    Args:
        mask (numpy.NDArray[numpy.uint8]): A 2D NumPy array containing 0s and 255s
            for nodata/data (invalid/valid) pixels.
        transform (Affine): An :class:`affine.Affine` object defining
            the affine transformation from pixel coordinates to a desired
            coordinate system. Defaults to an identity transform, which returns
            polygons based on pixel coordinates.
        convex_hull (bool): Whether to return the convex hull of the created
            polygons. Defaults to False.
        holes (bool): Whether to include holes in the created polygons. Has
            no effect if ``convex_hull`` is True. Defaults to False.

    Returns:
        Optional[Union[Polygon, MultiPolygon]: A polygon or multipolygon
        enclosing valid data pixels in the given ``mask``. The polygon vertex
        coordinates are transformed according to the given ``transform``.
    """
    polygons = [
        shape(polygon_dict)
        for polygon_dict, region_value in rasterio.features.shapes(
            mask, transform=transform
        )
        if region_value == 255
    ]

    if not polygons:
        return None

    if not holes and not convex_hull:
        polygons = [Polygon(poly.exterior.coords) for poly in polygons]
        unioned_polygons = unary_union(polygons)
        if isinstance(unioned_polygons, Polygon):
            polygons = [unioned_polygons]
        else:
            polygons = list(unioned_polygons.geoms)

    polygons = [orient(poly) for poly in polygons]

    if len(polygons) == 1:
        geometry = polygons[0]
    else:
        geometry = MultiPolygon(polygons)

    if convex_hull:
        geometry = orient(geometry.convex_hull)

    return geometry
