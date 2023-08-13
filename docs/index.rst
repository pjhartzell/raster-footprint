.. raster-footprint documentation master file, created by
   sphinx-quickstart on Sat Aug  5 14:13:46 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

raster-footprint
================

A Python package for creating `GeoJSON <https://datatracker.ietf.org/doc/html/rfc7946>`_
geometries that bound valid data in a geospatial raster.


What is a raster footprint?
---------------------------

One or more polygons that surround valid data in a raster, or a single polygon
surrounding the entire raster grid.

.. figure:: img/esa-worldcover-tile.png
   :alt: ESA WorldCover tile
   :figclass: align-center

   Footprint (red polygon) of an ESA WorldCover raster tile

The polygon data is stored in a `GeoJSON
<https://datatracker.ietf.org/doc/html/rfc7946>`_ geometry object.

.. code-block:: json

   {
      "type": "Polygon",
      "coordinates": [
         [
            [120.0, -30.0],
            [120.0, -33.0],
            [123.0, -33.0],
            [123.0, -30.0],
            [120.0, -30.0]
         ]
      ]
   }


What are the challenges?
-------------------------------------------------------

By definition, `GeoJSON <https://datatracker.ietf.org/doc/html/rfc7946>`_ geometries
contain point sequences with coordinates referenced to the WGS84 (EPSG:4326) datum.
However, most geospatial raster products exist in a projected coordinate system that is
distorted with respect to WGS84. This can lead to gaps between the raster data and 
polygon boundaries unless additional polygon vertices are inserted prior to transforming
the polygons to WGS84.

Many geospatial rasters also contain pixels that do not contain data, commonly termed
"nodata" pixels. Excluding these nodata pixels can lead to many small polygons and
polygons with holes, thereby increasing the complexity of the raster footprint geometry
object.

A raster footprint geometry must therefore strike a balance between maximizing the
fidelity with which the geometry captures the spatial extent of valid data (not "nodata"
pixels) and the pragmatic desire to limit the number polygon vertices to a reasonable
amount.


What does the raster-footprint package provide?
-----------------------------------------------

A convenient mechanism for creating and tuning raster footprints via a relatively thin
wrapper around `rasterio <https://rasterio.readthedocs.io/en/stable/index.html>`_ and
`Shapely <https://shapely.readthedocs.io/en/stable/manual.html>`_. \

*Use a variety of data sources:*

- raster files openable by `rasterio
  <https://rasterio.readthedocs.io/en/stable/index.html>`_
- `rasterio <https://rasterio.readthedocs.io/en/stable/index.html>`_ `DatasetReader
  <https://rasterio.readthedocs.io/en/stable/api/rasterio.io.html#rasterio.io.DatasetReader>`_
  objects
- `NumPy <https://numpy.org/doc/stable/index.html>`_ arrays of raster data
- `NumPy <https://numpy.org/doc/stable/index.html>`_ arrays of mask values (arrays of 0s
  and 255s for nodata/data pixels)

*Be selective:*

- choose one or more bands from a multiband raster for footprint creation

*Specify a CRS:*

- specify a CRS other than WGS84 for the footprint (caution - invalid `GeoJSON
  <https://datatracker.ietf.org/doc/html/rfc7946>`_!)

*Mitigate projection distortion effects:*

- insert additional polygon vertices via a densification factor or densification distance

*Simplify footprint geometry:*

- use the entire raster grid, i.e., include nodata pixels
- apply a convex hull to the footprint
- discard polygon holes
- simplify the polygons with the `Douglas-Peucker
  <https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm>`_
  algorithm



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
