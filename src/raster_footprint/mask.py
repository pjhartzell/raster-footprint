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
    data_array: npt.NDArray[Any], *, no_data: Optional[Union[int, float]] = None
) -> npt.NDArray[np.uint8]:
    """Produces a mask of valid data in the given numpy ``data_array``.

    Locations in the data array matching the given ``no_data`` value are set to
    0, all other array locations are set to 255. If ``no_data`` is not provided,
    all array locations are set to 255.

    Args:
        data_array (numpy.NDArray[Any]): A 2D or 3D array of raster data.
        no_data (Optional[Union[int, float]]): The nodata value. If not
            provided, all array locations are set to 255.

    Returns:
        numpy.NDArray[numpy.uint8]: A 2D array containing 0s and 255s for
        nodata/data pixels.
    """
    if data_array.ndim == 2:
        data_array = data_array[np.newaxis, :]
    shape = data_array.shape
    if no_data is not None:
        mask: npt.NDArray[np.uint8] = np.full(shape, fill_value=0, dtype=np.uint8)
        if np.isnan(no_data):
            mask[~np.isnan(data_array)] = 1
        else:
            mask[np.where(data_array != no_data)] = 1
        mask = np.sum(mask, axis=0, dtype=np.uint8)
        mask[mask > 0] = 255
    else:
        mask = np.full(shape, fill_value=255, dtype=np.uint8)
    return mask


def get_mask_extent(
    mask: npt.NDArray[np.uint8],
    transform: Affine,
    *,
    convex_hull: bool = False,
    holes: bool = True,
) -> Optional[Union[Polygon, MultiPolygon]]:
    """Produces the convex hull of the data footprint in coordinates defined by
    the given ``transform``.

    Args:
        mask (numpy.NDArray[numpy.uint8]): A 2D array containing 0s and 255s
            for nodata/data pixels.
        transform (Affine): A rasterio :class:`affine.Affine` object defining
            the affine transformation from pixel coordinates to the data native
            CRS coordinates.
        convex_hull (bool): Whether to return the convex hull of the extracted
            footprint. Defaults to False.
        holes (bool): Whether to include holes in the extracted footprint. Has
            no effect if ``convex_hull`` is True. Defaults to True.

    Returns:
        Optional[Union[Polygon, MultiPolygon]: A polygon or multi-polygon
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
