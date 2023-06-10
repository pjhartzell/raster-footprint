from raster_footprint.raster_footprint import densify_by_distance, densify_by_factor


def test_densify_by_distance() -> None:
    coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]
    assert len(coords) == 5
    densified_coords = densify_by_distance(coords, 3.33)
    for coord in coords:
        assert coord in densified_coords
    assert len(densified_coords) == 17


def test_densify_by_factor() -> None:
    coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]
    assert len(coords) == 5
    densified_coords = densify_by_factor(coords, 2)
    for coord in coords:
        assert coord in densified_coords
    assert len(densified_coords) == 9
