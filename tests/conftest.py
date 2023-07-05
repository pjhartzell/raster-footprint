import json
from pathlib import Path
from typing import Any, Dict, Union

from shapely.geometry import MultiPolygon, Polygon, shape

TEST_DATA_DIRECTORY = Path(__file__).parent / "data"


def read_geojson(name: str) -> Dict[str, Any]:
    path = (TEST_DATA_DIRECTORY / "geojson" / name).with_suffix(".json")
    with open(path) as f:
        data: Dict[str, Any] = json.load(f)
    return data


def check_winding(extent: Union[Polygon, MultiPolygon, Dict[str, Any]]) -> None:
    if isinstance(extent, dict):
        extent = shape(extent)

    if isinstance(extent, Polygon):
        assert extent.exterior.is_ccw
        for interior in extent.interiors:
            assert not interior.is_ccw
    elif isinstance(extent, MultiPolygon):
        for polygon in extent.geoms:
            assert polygon.exterior.is_ccw
            for interior in polygon.interiors:
                assert not interior.is_ccw
    else:
        raise TypeError("`extent` must be a Polygon, MultiPolygon, or GeoJSON dict")
