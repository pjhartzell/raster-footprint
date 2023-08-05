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
    shape = data_array.shape
    if nodata is not None:
        mask: npt.NDArray[np.uint8] = np.full(shape, fill_value=0, dtype=np.uint8)
        if np.isnan(nodata):
            mask[~np.isnan(data_array)] = 1
        else:
            mask[data_array != nodata] = 1
        mask = np.sum(mask, axis=0, dtype=np.uint8)
        mask[mask > 0] = 255
    else:
        mask = np.full(shape[-2:], fill_value=255, dtype=np.uint8)
    return mask


def get_mask_extent(
    mask: npt.NDArray[np.uint8],
    *,
    transform: Affine = Affine(1, 0, 0, 0, 1, 0),
    convex_hull: bool = False,
    holes: bool = True,
) -> Optional[Union[Polygon, MultiPolygon]]:
    """Creates a polygon or multipolygon surrounding valid data locations.

    Polygons are created around each contiguous region of valid data locations
    in the given ``mask``. Valid data locations are defined as locations in the
    mask with a value of 255.

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
            no effect if ``convex_hull`` is True. Defaults to True.

    Returns:
        Optional[Union[Polygon, MultiPolygon]: A polygon or multipolygon
        enclosing data pixels in the given ``mask``. The polygon vertex
        coordinates are transformed according to the given ``transform``.
    """
    data_polygons = [
        shape(polygon_dict)
        for polygon_dict, region_value in rasterio.features.shapes(
            mask, transform=transform
        )
        if region_value == 255
    ]

    if not data_polygons:
        return None

    if not holes and not convex_hull:
        data_polygons = [Polygon(poly.exterior.coords) for poly in data_polygons]
        unioned_polygons = unary_union(data_polygons)
        if isinstance(unioned_polygons, Polygon):
            data_polygons = [unioned_polygons]
        else:
            data_polygons = list(unioned_polygons.geoms)

    data_polygons = [orient(poly) for poly in data_polygons]

    if len(data_polygons) == 1:
        data_extent = data_polygons[0]
    else:
        data_extent = MultiPolygon(data_polygons)

    if convex_hull:
        data_extent = orient(data_extent.convex_hull)

    return data_extent
