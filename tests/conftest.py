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


def check_winding(geometry: Union[Polygon, MultiPolygon, Dict[str, Any]]) -> None:
    if isinstance(geometry, dict):
        geometry = shape(geometry)

    if isinstance(geometry, Polygon):
        assert geometry.exterior.is_ccw
        for interior in geometry.interiors:
            assert not interior.is_ccw
    elif isinstance(geometry, MultiPolygon):
        for polygon in geometry.geoms:
            assert polygon.exterior.is_ccw
            for interior in polygon.interiors:
                assert not interior.is_ccw
    else:
        raise TypeError("'geometry' must be a Polygon, MultiPolygon, or GeoJSON dict")
