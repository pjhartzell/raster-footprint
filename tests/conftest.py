import json
from pathlib import Path
from typing import Any, Dict

TEST_DATA_DIRECTORY = Path(__file__).parent / "data" / "geojson"


def read_geojson(name: str) -> Dict[str, Any]:
    path = (TEST_DATA_DIRECTORY / name).with_suffix(".json")
    with open(path) as f:
        data: Dict[str, Any] = json.load(f)
    return data
