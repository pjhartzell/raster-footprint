from typing import TypeVar

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

T = TypeVar("T", Polygon, MultiPolygon)

DEFAULT_PRECISION = 7
