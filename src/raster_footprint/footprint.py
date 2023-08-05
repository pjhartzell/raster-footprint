from typing import Any, Dict, List, Optional, Union

import numpy as np
import rasterio
from numpy import typing as npt
from rasterio import Affine, DatasetReader
from rasterio.crs import CRS
from shapely.geometry import mapping

from .densify import densify_extent
from .mask import create_mask, get_mask_extent
from .reproject import DEFAULT_PRECISION, reproject_extent
from .simplify import simplify_extent

# TODO: change holes default to False


def footprint_from_mask(
    mask: npt.NDArray[np.uint8],
    crs: CRS,
    transform: Affine,
    *,
    precision: int = DEFAULT_PRECISION,
    densify_factor: Optional[int] = None,
    densify_distance: Optional[float] = None,
    simplify_tolerance: Optional[float] = None,
    convex_hull: bool = False,
    holes: bool = True,
) -> Optional[Dict[str, Any]]:
    """Produces a GeoJSON dictionary containing a polygon or multipolygon
    surrounding valid data locations in the given ``mask`` array.

    A polygon or multipolygon surrounding valid data pixels is extracted from
    the given ``mask`` array. The polygon(s) are densified with additional
    vertices, reprojected to the WGS84 (EPSG:4326) coordinate system, and then
    simplified by reducing the number of polygon vertices. Densifying the
    polygon(s) prior to reprojection reduces projection distortion error.
    Simplification removes vertices that are redundant in defining the
    polygon(s) to within the given ``simplify_tolerance``.

    Args:
        mask (numpy.NDArray[numpy.uint8]): A 2D NumPy array containing 0s and
            255s for nodata/data (invalid/valid data) pixels.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the given ``mask``.
        transform (Affine): A rasterio :class:`affine.Affine` object defining
            the affine transformation from the ``mask`` pixel coordinate system
            to the given ``crs`` coordinate system.
        precision (Optional[int]): The number of decimal places to include in
            the final footprint polygon vertex coordinates. Defaults to 7.
        densify_factor (Optional[int]): The factor by which to increase the
            number of polygon vertices, e.g., a ``factor`` of 2 will double the
            number of vertices. Mutually exclusive with ``densify_distance``.
            Defaults to None.
        densify_distance (Optional[float]): The interval at which to insert
            additional polygon vertices, e.g., a ``distance`` of 2 will insert
            a new vertex every 2 units of distance between existing vertices.
            Mutually exclusive with ``densify_factor``. Defaults to None.
        simplify_tolerance (Optional[float]): The maximum distance between
            original polygon vertices and the simplified polygon(s). Unit is
            geographic decimal degrees. Defaults to None.
        convex_hull (bool): Whether to compute the convex hull of any created
            polygons. The convex hull is applied prior to densification and
            simplification. Defaults to False.
        holes (bool): Whether to include holes in the created polygons. Has
            no effect if ``convex_hull`` is True. Defaults to True.

    Returns:
        Optional[Dict[str, Any]]: A GeoJSON dictionary containing the
        footprint polygon or multipolygon.
    """
    extent = get_mask_extent(
        mask, transform=transform, convex_hull=convex_hull, holes=holes
    )
    if extent is None:
        return None
    densified = densify_extent(extent, factor=densify_factor, distance=densify_distance)
    reprojected = reproject_extent(densified, crs, precision=precision)
    simplified = simplify_extent(reprojected, tolerance=simplify_tolerance)
    return mapping(simplified)  # type: ignore


def footprint_from_data(
    data: npt.NDArray[Any],
    crs: CRS,
    transform: Affine,
    *,
    nodata: Optional[Union[int, float]] = None,
    precision: int = DEFAULT_PRECISION,
    densify_factor: Optional[int] = None,
    densify_distance: Optional[float] = None,
    simplify_tolerance: Optional[float] = None,
    convex_hull: bool = False,
    holes: bool = True,
) -> Optional[Dict[str, Any]]:
    """Produces a GeoJSON dictionary containing a polygon or multipolygon
    surrounding valid data locations in the given ``data`` array.

    Args:
        data (npt.NDArray[Any]): A 2D or 3D NumPy array of raster data.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the raster data in the given
            ``numpy_array`.
        transform (Affine): A rasterio :class:`affine.Affine` object defining
            the affine transformation from the ``data`` pixel coordinate system
            to the given ``crs`` coordinate system.
        nodata (Optional[Union[int, float]]): The nodata value to use for
            creating a data/nodata mask array. If not provided, a footprint for
            the entire raster, including nodata pixels, is returned.
        precision (Optional[int]): The number of decimal places to include in
            the final footprint polygon vertex coordinates. Defaults to 7.
        densify_factor (Optional[int]): The factor by which to increase the
            number of polygon vertices, e.g., a ``factor`` of 2 will double the
            number of vertices. Mutually exclusive with ``densify_distance``.
            Defaults to None.
        densify_distance (Optional[float]): The interval at which to insert
            additional polygon vertices, e.g., a ``distance`` of 2 will insert
            a new vertex every 2 units of distance between existing vertices.
            Mutually exclusive with ``densify_factor``. Defaults to None.
        simplify_tolerance (Optional[float]): The maximum distance between
            original polygon vertices and the simplified polygon(s). Unit is
            geographic decimal degrees. Defaults to None.
        convex_hull (bool): Whether to compute the convex hull of any created
            polygons. The convex hull is applied prior to densification and
            simplification. Defaults to False.
        holes (bool): Whether to include holes in the created polygons. Has
            no effect if ``convex_hull`` is True. Defaults to True.

    Returns:
        Optional[Dict[str, Any]]: A GeoJSON dictionary containing the
        footprint polygon or multipolygon.
    """
    mask = create_mask(data, nodata=nodata)
    return footprint_from_mask(
        mask,
        crs,
        transform,
        precision=precision,
        densify_factor=densify_factor,
        densify_distance=densify_distance,
        simplify_tolerance=simplify_tolerance,
        convex_hull=convex_hull,
        holes=holes,
    )


def footprint_from_href(
    href: str,
    *,
    nodata: Optional[Union[int, float]] = None,
    precision: int = DEFAULT_PRECISION,
    densify_factor: Optional[int] = None,
    densify_distance: Optional[float] = None,
    simplify_tolerance: Optional[float] = None,
    convex_hull: bool = False,
    holes: bool = True,
    bands: Optional[List[int]] = None,
    with_nodata: bool = False,
) -> Optional[Dict[str, Any]]:
    """Produces a GeoJSON dictionary containing a polygon or multipolygon
    surrounding valid data locations in a raster file located at the given
    ``href``.

    The file pointed to by ``href`` must be openable by rasterio.

    Args:
        href (str): An href to a raster data file.
        nodata (Optional[Union[int, float]]): Explicitly sets the nodata value
            to use for creating a data/nodata mask array. If not provided, the
            nodata value in the source file metadata is used. If not provided
            and a nodata value does not exist in the source file metadata, a
            footprint for the entire raster, including nodata pixels, is
            returned.
        precision (Optional[int]): The number of decimal places to include in
            the final footprint polygon vertex coordinates. Defaults to 7.
        densify_factor (Optional[int]): The factor by which to increase the
            number of polygon vertices, e.g., a ``factor`` of 2 will double the
            number of vertices. Mutually exclusive with ``densify_distance``.
            Defaults to None.
        densify_distance (Optional[float]): The interval at which to insert
            additional polygon vertices, e.g., a ``distance`` of 2 will insert
            a new vertex every 2 units of distance between existing vertices.
            Mutually exclusive with ``densify_factor``. Defaults to None.
        simplify_tolerance (Optional[float]): The maximum distance between
            original polygon vertices and the simplified polygon(s). Unit is
            geographic decimal degrees. Defaults to None.
        convex_hull (bool): Whether to compute the convex hull of any created
            polygons. The convex hull is applied prior to densification and
            simplification. Defaults to False.
        holes (bool): Whether to include holes in the created polygons. Has
            no effect if ``convex_hull`` is True. Defaults to True.
        with_nodata (bool): If True, a footprint for the entire raster,
            including nodata pixels, is returned. Defaults to False.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be
            ORd together; e.g., for a pixel to be outside of the footprint,
            all bands must have nodata in that pixel.

    Returns:
        Optional[Dict[str, Any]]: A GeoJSON dictionary containing the
        footprint polygon or multipolygon.
    """
    with rasterio.open(href) as source:
        return footprint_from_rasterio_reader(
            source,
            precision=precision,
            densify_factor=densify_factor,
            densify_distance=densify_distance,
            simplify_tolerance=simplify_tolerance,
            nodata=nodata,
            with_nodata=with_nodata,
            bands=bands,
            convex_hull=convex_hull,
            holes=holes,
        )


def footprint_from_rasterio_reader(
    reader: DatasetReader,
    *,
    nodata: Optional[Union[int, float]] = None,
    precision: int = DEFAULT_PRECISION,
    densify_factor: Optional[int] = None,
    densify_distance: Optional[float] = None,
    simplify_tolerance: Optional[float] = None,
    convex_hull: bool = False,
    holes: bool = True,
    bands: Optional[List[int]] = None,
    with_nodata: bool = False,
) -> Optional[Dict[str, Any]]:
    """Produces a GeoJSON dictionary containing a polygon or multipolygon
    surrounding valid data locations from a :class:`rasterio.io.DatasetReader`
    object, i.e., an opened dataset object returned by a :func:`rasterio.open`
    call.

    Args:
        reader (DatasetReader): A rasterio dataset reader object.
        nodata (Optional[Union[int, float]]): Explicitly sets the nodata value
            to use for creating a data/nodata mask array. If not provided, the
            nodata value in the source file metadata is used. If not provided
            and a nodata value does not exist in the source file metadata, a
            footprint for the entire raster, including nodata pixels, is
            returned.
        precision (Optional[int]): The number of decimal places to include in
            the final footprint polygon vertex coordinates. Defaults to 7.
        densify_factor (Optional[int]): The factor by which to increase the
            number of polygon vertices, e.g., a ``factor`` of 2 will double the
            number of vertices. Mutually exclusive with ``densify_distance``.
            Defaults to None.
        densify_distance (Optional[float]): The interval at which to insert
            additional polygon vertices, e.g., a ``distance`` of 2 will insert
            a new vertex every 2 units of distance between existing vertices.
            Mutually exclusive with ``densify_factor``. Defaults to None.
        simplify_tolerance (Optional[float]): The maximum distance between
            original polygon vertices and the simplified polygon(s). Unit is
            geographic decimal degrees. Defaults to None.
        convex_hull (bool): Whether to compute the convex hull of any created
            polygons. The convex hull is applied prior to densification and
            simplification. Defaults to False.
        holes (bool): Whether to include holes in the created polygons. Has
            no effect if ``convex_hull`` is True. Defaults to True.
        with_nodata (bool): If True, a footprint for the entire raster,
            including nodata pixels, is returned. Defaults to False.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be
            ORd together; e.g., for a pixel to be outside of the footprint,
            all bands must have nodata in that pixel.

    Returns:
        Optional[Dict[str, Any]]: A GeoJSON dictionary containing the
        footprint polygon or multipolygon.
    """
    if not reader.indexes:
        raise ValueError(
            "Raster footprint cannot be computed for an asset with no bands."
        )
    if nodata is not None and len(set(reader.nodatavals)) != 1:
        raise ValueError(
            "When specifying a 'nodata' value, all raster bands must have "
            "the same 'nodata' value."
        )

    if with_nodata:
        mask = np.full(reader.shape[-2:], fill_value=255, dtype=np.uint8)
    elif nodata is None or nodata == reader.nodata:
        if not bands:
            mask = reader.dataset_mask()
        elif len(bands) == 1:
            mask = reader.read_masks(bands)
        else:
            mask = reader.read_masks(bands)
            mask = np.sum(mask, axis=0, dtype=np.uint8)
            mask[mask > 0] = 255
    else:
        if not bands:
            bands = reader.indexes
        mask = create_mask(reader.read(bands), nodata=nodata)

    return footprint_from_mask(
        mask,
        reader.crs,
        reader.transform,
        precision=precision,
        densify_factor=densify_factor,
        densify_distance=densify_distance,
        simplify_tolerance=simplify_tolerance,
        convex_hull=convex_hull,
        holes=holes,
    )
