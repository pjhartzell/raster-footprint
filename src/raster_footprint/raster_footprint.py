"""Generate convex hulls of valid raster data for use in STAC Item geometries."""

import logging
from itertools import groupby
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

import numpy as np
import numpy.typing as npt
import rasterio
import rasterio.features
from rasterio import Affine, DatasetReader
from rasterio.crs import CRS
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon, orient

logger = logging.getLogger(__name__)

# Roughly 1 centimeter in geodetic coordinates
DEFAULT_PRECISION = 7

T = TypeVar("T", bound="RasterFootprint")


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


def reproject_polygon(
    polygon: Polygon, crs: CRS, precision: Optional[int] = DEFAULT_PRECISION
) -> Polygon:
    """Projects a polygon to EPSG 4326 and rounds the projected vertex
    coordinates to ``precision``.

    Duplicate points caused by rounding are removed.

    Args:
        polygon (Polygon): The polygon to reproject.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the input polygon.
        precision (int): The number of decimal places to include in the final
            polygon vertex coordinates.

    Returns:
        Polygon: Polygon in EPSG 4326.
    """
    polygon = shape(transform_geom(crs, "EPSG:4326", polygon, precision=precision))
    # Rounding to precision can produce duplicate coordinates, so we remove
    # them. Once once shapely>=2.0.0 is required, this can be replaced with
    # shapely.constructive.remove_repeated_points
    polygon = Polygon([k for k, _ in groupby(polygon.exterior.coords)])
    return polygon


def create_data_mask(
    data_array: npt.NDArray[Any], no_data: Optional[Union[int, float]] = None
) -> npt.NDArray[np.uint8]:
    """Produces a mask of valid data in the given ``data_array``.

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


class RasterFootprint:
    """An object for creating a convex hull polygon around all areas within an
    raster that have data values (i.e., they do not have the nodata value).
    This convex hull is termed the "footprint" of the raster data and is
    returned by the :meth:`footprint` method as a polygon in a GeoJSON
    dictionary for use as the geometry attribute of a STAC Item.

    Two important operations during this calculation are the densification of
    the footprint in the native CRS and simplification of the footprint after
    reprojection to EPSG 4326. If the initial low-vertex polygon in the native
    CRS is not densified, this can result in a reprojected polygon that does not
    accurately represent the data footprint. For example, a MODIS asset
    represented by a rectangular 5 point Polygon in a sinusoidal projection will
    reproject to a parallelogram in EPSG 4326, when it would be more accurately
    represented by a polygon with two parallel sides and two curved sides. The
    difference between these representations is greater the further away from
    the meridian and equator the asset is located.

    After reprojection to EPSG 4326, the footprint may have more points than
    desired. This can be simplified to a polygon with fewer points that maintain
    a maximum distance to the original geometry.

    Args:
        mask_array (numpy.NDArray[Any]): A mask of valid data pixels. More
            specifically, a numpy array containing 0s at nodata pixel locations
            and 255s at data pixel locations.
        crs (CRS): A rasterio :class:`rasterio.crs.CRS` object defining the
            coordinate reference system of the raster data.
        transform (Affine): Affine class defining the transformation from pixel
            to CRS coordinates.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        densification_factor (Optional[int]): The factor by which to increase
            point density within the footprint polygon before projection to
            EPSG 4326. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of 3
            would place two points between each point, etc. Higher densities
            produce higher fidelity footprints in areas of high projection
            distortion. Mutually exclusive with ``densification_distance``.
        densification_distance (Optional[float]): The distance by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. If the distance is set to 2 and the segment
            length between two polygon vertices is 10, 4 new vertices would be
            created along the segment. Higher densities produce higher fidelity
            footprints in areas of high projection distortion. Mutually
            exclusive with ``densification_factor``.
        simplify_tolerance (Optional[float]): Distance, in degrees, within
            which all locations on the simplified polygon will be to the original
            polygon.
    """

    mask_array: npt.NDArray[Any]
    """2D or 3D array of raster data."""

    crs: CRS
    """Coordinate reference system of the raster data."""

    transform: Affine
    """Transformation matrix from pixel to CRS coordinates."""

    precision: int
    """Number of decimal places in the final footprint coordinates."""

    densification_factor: Optional[int]
    """Optional factor for densifying polygon vertices before reprojection to
    EPSG 4326."""

    densification_distance: Optional[float]
    """Optional distance for densifying polygon vertices before reprojection to
    EPSG 4326."""

    simplify_tolerance: Optional[float]
    """Optional maximum allowable error when simplifying the reprojected
    polygon."""

    def __init__(
        self,
        mask_array: npt.NDArray[np.uint8],
        crs: CRS,
        transform: Affine,
        *,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
    ) -> None:
        self.mask_array = mask_array
        self.crs = crs
        self.transform = transform
        self.precision = precision
        if densification_factor is not None and densification_distance is not None:
            raise ValueError(
                "Only one of 'densification_factor' or 'densification_distance' "
                "can be specified."
            )
        self.densification_factor = densification_factor
        self.densification_distance = densification_distance
        self.simplify_tolerance = simplify_tolerance

    def footprint(self) -> Optional[Dict[str, Any]]:
        """Produces the footprint surrounding data (not nodata) pixels in the
        source image. If the footprint is unable to be computed, None is
        returned.

        Returns:
            Optional[Dict[str, Any]]: A GeoJSON dictionary containing the
            footprint polygon.
        """
        polygon = self.data_extent()
        if polygon is None:
            return None
        polygon = self.densify_polygon(polygon)
        polygon = self.reproject_polygon(polygon)
        polygon = self.simplify_polygon(polygon)
        return mapping(polygon)  # type: ignore

    def data_extent(self) -> Optional[Polygon]:
        """Produces the data footprint in the native CRS.

        Args:
            mask (numpy.NDArray[numpy.uint8]): A 2D array containing 0s and 255s
                for nodata/data pixels.

        Returns:
            Optional[Polygon]: A native CRS polygon of the convex hull of data
            pixels.
        """
        data_polygons = [
            shape(polygon_dict)
            for polygon_dict, region_value in rasterio.features.shapes(
                self.mask_array, transform=self.transform
            )
            if region_value == 255
        ]

        if not data_polygons:
            return None
        elif len(data_polygons) == 1:
            polygon = data_polygons[0]
        else:
            polygon = MultiPolygon(data_polygons).convex_hull

        return orient(polygon)

    def densify_polygon(self, polygon: Polygon) -> Polygon:
        """Adds vertices to the footprint polygon in the native CRS using
        either ``self.densification_factor`` or
        ``self.densification_distance``.

        Args:
            polygon (Polygon): Footprint polygon in the native CRS.

        Returns:
            Polygon: Densified footprint polygon in the native CRS.
        """
        assert not (self.densification_factor and self.densification_distance)
        if self.densification_factor is not None:
            return Polygon(
                densify_by_factor(polygon.exterior.coords, self.densification_factor)
            )
        elif self.densification_distance is not None:
            return Polygon(
                densify_by_distance(
                    polygon.exterior.coords, self.densification_distance
                )
            )
        else:
            return polygon

    def reproject_polygon(self, polygon: Polygon) -> Polygon:
        """Projects a polygon to EPSG 4326 and rounds the projected vertex
        coordinates to ``self.precision``.

        Duplicate points caused by rounding are removed.

        Args:
            polygon (Polygon): Footprint polygon in the native CRS.

        Returns:
            Polygon: Footprint polygon in EPSG 4326.
        """
        return reproject_polygon(polygon, self.crs, self.precision)

    def simplify_polygon(self, polygon: Polygon) -> Polygon:
        """Reduces the number of polygon vertices such that the simplified
        polygon shape is no further away than the original polygon vertices
        than ``self.simplify_tolerance``.

        Args:
            polygon (Polygon): Polygon to be simplified.

        Returns:
            Polygon: Reduced vertex polygon.
        """
        if self.simplify_tolerance is not None:
            return orient(
                polygon.simplify(
                    tolerance=self.simplify_tolerance, preserve_topology=False
                )
            )
        return polygon

    @classmethod
    def from_href(
        cls: Type[T],
        href: str,
        *,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[Union[int, float]] = None,
        entire: bool = False,
        bands: List[int] = [1],
    ) -> T:
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
            return cls.from_rasterio_dataset_reader(
                reader=source,
                precision=precision,
                densification_factor=densification_factor,
                densification_distance=densification_distance,
                simplify_tolerance=simplify_tolerance,
                no_data=no_data,
                entire=entire,
                bands=bands,
            )

    @classmethod
    def from_rasterio_dataset_reader(
        cls: Type[T],
        reader: DatasetReader,
        *,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[Union[int, float]] = None,
        entire: bool = False,
        bands: List[int] = [1],
    ) -> T:
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
            mask = create_data_mask(reader.read(bands), no_data=no_data)

        return cls(
            mask_array=mask,
            crs=reader.crs,
            transform=reader.transform,
            precision=precision,
            densification_factor=densification_factor,
            densification_distance=densification_distance,
            simplify_tolerance=simplify_tolerance,
        )

    @classmethod
    def from_numpy_array(
        cls: Type[T],
        numpy_array: npt.NDArray[Any],
        crs: CRS,
        transform: Affine,
        *,
        no_data: Optional[Union[int, float]] = None,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
    ) -> T:
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
        mask = create_data_mask(numpy_array, no_data=no_data)
        return cls(
            mask_array=mask,
            crs=crs,
            transform=transform,
            precision=precision,
            densification_factor=densification_factor,
            densification_distance=densification_distance,
            simplify_tolerance=simplify_tolerance,
        )
