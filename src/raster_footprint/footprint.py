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
    """Produces the footprint surrounding data (not nodata) pixels in the
    source image. If the footprint is unable to be computed, None is
    returned.

    Returns:
        Optional[Dict[str, Any]]: A GeoJSON dictionary containing the
        footprint polygon.
    """
    extent = get_mask_extent(mask, transform, convex_hull=convex_hull, holes=holes)
    if extent is None:
        return None
    densified = densify_extent(extent, factor=densify_factor, distance=densify_distance)
    reprojected = reproject_extent(densified, crs, precision=precision)
    simplified = simplify_extent(reprojected, tolerance=simplify_tolerance)
    return mapping(simplified)  # type: ignore


def footprint_from_data(
    numpy_array: npt.NDArray[Any],
    crs: CRS,
    transform: Affine,
    *,
    no_data: Optional[Union[int, float]] = None,
    precision: int = DEFAULT_PRECISION,
    densify_factor: Optional[int] = None,
    densify_distance: Optional[float] = None,
    simplify_tolerance: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Produces a :class:`RasterFootprint` instance from a numpy array of
    image data.

    Args:
        numpy_array (npt.NDArray[Any]): A numpy array of image data.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the data contained in the given
            ``numpy_array`.
        transform (Affine): Affine class defining the transformation from
            pixel to CRS coordinates.
        no_data (Optional[Union[int, float]]): The nodata value to use for
            creating the nodata/data mask. If not provided, a footprint for
            the entire raster is returned.
        precision (int): The number of decimal places to include in the
            final footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. A factor of 2 would double the density
            of points (placing one new point between each existing pair of
            points), a factor of 3 would place two points between each point,
            etc. Higher densities produce higher fidelity footprints in
            areas of high projection distortion. Mutually exclusive with
            ``densification_distance``.
        densification_distance (Optional[float]): The distance by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. If the distance is set to 2 and the
            segment length between two polygon vertices is 10, 4 new
            vertices would be created along the segment. Higher densities
            produce higher fidelity footprints in areas of high projection
            distortion.  Mutually exclusive with ``densification_factor``.
        simplify_tolerance (Optional[float]): Distance, in degrees, within
            which all locations on the simplified polygon will be to the
            original polygon.
    """
    mask = create_mask(numpy_array, no_data=no_data)
    return footprint_from_mask(
        mask,
        crs,
        transform,
        precision=precision,
        densify_factor=densify_factor,
        densify_distance=densify_distance,
        simplify_tolerance=simplify_tolerance,
    )


def footprint_from_href(
    href: str,
    *,
    precision: int = DEFAULT_PRECISION,
    densify_factor: Optional[int] = None,
    densify_distance: Optional[float] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[Union[int, float]] = None,
    entire: bool = False,
    bands: List[int] = [1],
) -> Optional[Dict[str, Any]]:
    """Produces a :class:`RasterFootprint` instance from an image href.

    The href can point to any file that is openable by rasterio.

    Args:
        href (str): The href of the image to process.
        precision (int): The number of decimal places to include in the
            final footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. A factor of 2 would double the density
            of points (placing one new point between each existing pair of
            points), a factor of 3 would place two points between each point,
            etc. Higher densities produce higher fidelity footprints in
            areas of high projection distortion. Mutually exclusive with
            ``densification_distance``.
        densification_distance (Optional[float]): The distance by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. If the distance is set to 2 and the
            segment length between two polygon vertices is 10, 4 new
            vertices would be created along the segment. Higher densities
            produce higher fidelity footprints in areas of high projection
            distortion.  Mutually exclusive with ``densification_factor``.
        simplify_tolerance (Optional[float]): Distance, in degrees, within
            which all locations on the simplified polygon will be to the
            original polygon.
        no_data (Optional[Union[int, float]]): Explicitly sets the nodata
            value. If not provided, the nodata value in the source image
            metadata is used. If not provided and a nodata value does not
            exist in the source image metadata, a footprint for the entire
            raster is returned.
        entire (bool): If True, the ``no_data`` option is ignored and a
            footprint for the entire raster, including nodata pixels, is
            returned.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be
            ORd together; e.g., for a pixel to be outside of the footprint,
            all bands must have nodata in that pixel.

    Returns:
        RasterFootprint: A :class:`RasterFootprint` instance.
    """
    with rasterio.open(href) as source:
        return footprint_from_rasterio_reader(
            source,
            precision=precision,
            densify_factor=densify_factor,
            densify_distance=densify_distance,
            simplify_tolerance=simplify_tolerance,
            no_data=no_data,
            entire=entire,
            bands=bands,
        )


def footprint_from_rasterio_reader(
    reader: DatasetReader,
    *,
    precision: int = DEFAULT_PRECISION,
    densify_factor: Optional[int] = None,
    densify_distance: Optional[float] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[Union[int, float]] = None,
    entire: bool = False,
    bands: List[int] = [1],
) -> Optional[Dict[str, Any]]:
    """Produces a :class:`RasterFootprint` instance from a
    :class:`rasterio.io.DatasetReader` object, i.e., an opened dataset
    object returned by a :func:`rasterio.open` call.

    Args:
        reader (DatasetReader): A rasterio dataset reader object for the
            image to process.
        precision (int): The number of decimal places to include in the
            final footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. A factor of 2 would double the density
            of points (placing one new point between each existing pair of
            points), a factor of 3 would place two points between each point,
            etc. Higher densities produce higher fidelity footprints in
            areas of high projection distortion. Mutually exclusive with
            ``densification_distance``.
        densification_distance (Optional[float]): The distance by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. If the distance is set to 2 and the
            segment length between two polygon vertices is 10, 4 new
            vertices would be created along the segment. Higher densities
            produce higher fidelity footprints in areas of high projection
            distortion.  Mutually exclusive with ``densification_factor``.
        simplify_tolerance (Optional[float]): Distance, in degrees, within
            which all locations on the simplified polygon will be to the
            original polygon.
        no_data (Optional[Union[int, float]]): Explicitly sets the nodata
            value. If not provided, the nodata value in the source image
            metadata is used. If not provided and a nodata value does not
            exist in the source image metadata, a footprint for the entire
            raster is returned.
        entire (bool): If True, the ``no_data`` option is ignored and a
            footprint for the entire raster, including nodata pixels, is
            returned.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be
            ORd together; e.g., for a pixel to be outside of the footprint,
            all bands must have nodata in that pixel.

    Returns:
        RasterFootprint: A :class:`RasterFootprint` instance.
    """
    if not reader.indexes:
        raise ValueError(
            "Raster footprint cannot be computed for an asset with no bands."
        )
    if no_data is not None and len(set(reader.nodatavals)) != 1:
        raise ValueError(
            "When specifying a 'no_data' value, all raster bands must have "
            "the same 'nodata' value."
        )

    if entire:
        mask = np.full(reader.shape, fill_value=255, dtype=np.uint8)
        # does reader.shape return a three dimensional array for a multiband image?
    elif no_data is None or no_data == reader.nodata:
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
        mask = create_mask(reader.read(bands), no_data=no_data)

    return footprint_from_mask(
        mask,
        reader.crs,
        reader.transform,
        precision=precision,
        densify_factor=densify_factor,
        densify_distance=densify_distance,
        simplify_tolerance=simplify_tolerance,
    )
