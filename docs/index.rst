.. raster-footprint documentation master file, created by
   sphinx-quickstart on Sat Aug  5 14:13:46 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

raster-footprint
================

A Python package for creating `GeoJSON <https://datatracker.ietf.org/doc/html/rfc7946>`_
geometries that bound valid data in a geospatial rasters.


What is a raster footprint?
---------------------------

One or more polygons that surround valid data in a raster, or a single polygon
surrounding the entire raster grid. For example, a single polygon that bounds the entire
raster grid an ESA WorldCover tile:

.. image:: img/esa-worldcover-tile.png
   :alt: ESA WorldCover tile

|

The polygon is stored in a `GeoJSON
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
distorted with respect to WGS84. This leads to gaps between the raster data and the
`GeoJSON <https://datatracker.ietf.org/doc/html/rfc7946>`_ polygons unless additional
polygon vertices are inserted prior to transformation to WGS84.

Many geospatial rasters also contain pixels that do not contain data, commonly termed
"nodata" pixels. We can create raster footprints that only bound areas of valid data by
excluding these nodata pixels. However, this often increases the number and complexity
of the polygons, easily producing `GeoJSON
<https://datatracker.ietf.org/doc/html/rfc7946>`_ geometry objects with tens of
thousands of coordinates that require multiple megabytes when stored to disk.

The goal is to balance the competing interests of maximizing the fidelity with which a
footprint captures the spatial extent of valid raster data in the WGS84 datum and the
desire to limit the footprint geometry to a reasonable number of coordinates.


How does the raster-footprint package help?
-----------------------------------------------

The raster-footprint package provides an API for creating footprints with options to
tune acceptable projection error and reduce footprint complexity. 

*Use a variety of data sources:*

- raster files openable by `rasterio
  <https://rasterio.readthedocs.io/en/stable/index.html>`_
- `rasterio <https://rasterio.readthedocs.io/en/stable/index.html>`_ `DatasetReader
  <https://rasterio.readthedocs.io/en/stable/api/rasterio.io.html#rasterio.io.DatasetReader>`_
  objects
- `NumPy <https://numpy.org/doc/stable/index.html>`_ arrays of raster data
- `NumPy <https://numpy.org/doc/stable/index.html>`_ arrays of mask values (arrays of 0s
  and 255s for nodata/data pixels)

*Mitigate projection distortion effects:*

- insert additional polygon vertices via a densification factor or densification distance

*Reduce footprint complexity:*

- use the entire raster grid, i.e., include nodata pixels
- apply a convex hull to the footprint
- discard polygon holes
- simplify the polygons with the `Douglas-Peucker
  <https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm>`_
  algorithm

*Be selective:*

- choose one or more bands from a multiband raster for footprint creation

*Specify a CRS:*

- specify a CRS other than WGS84 for the footprint (caution - invalid `GeoJSON
  <https://datatracker.ietf.org/doc/html/rfc7946>`_!)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
