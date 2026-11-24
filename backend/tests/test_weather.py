"""Unit tests for weather service, wind direction parsing, and AI visual wind estimation."""

import numpy as np
import pytest

from backend.app.services.weather_service import (
    parse_wind_direction,
    degrees_to_compass,
    estimate_wind_from_vision,
)


def test_parse_wind_direction():
    """Ensure various compass representations and edge cases parse correctly."""
    assert parse_wind_direction(None) is None
    assert parse_wind_direction("auto") is None
    assert parse_wind_direction("UNKNOWN") is None
    assert parse_wind_direction("") is None
    assert parse_wind_direction("bukan arah") is None
    assert parse_wind_direction("N") == 0.0
    assert parse_wind_direction("UTARA") == 0.0
    assert parse_wind_direction("SE") == 135.0
    assert parse_wind_direction("TENGGARA") == 135.0
    assert parse_wind_direction("W") == 270.0
    assert parse_wind_direction(90) == 90.0
    assert parse_wind_direction(450.0) == 90.0  # modulo 360


def test_degrees_to_compass():
    """Verify conversion of angle degrees to 8-point Indonesian compass."""
    assert "Utara" in degrees_to_compass(0.0)
    assert "Timur Laut" in degrees_to_compass(45.0)
    assert "Timur" in degrees_to_compass(90.0)
    assert "Tenggara" in degrees_to_compass(135.0)
    assert "Selatan" in degrees_to_compass(180.0)
    assert "Barat Daya" in degrees_to_compass(225.0)
    assert "Barat" in degrees_to_compass(270.0)
    assert "Barat Laut" in degrees_to_compass(315.0)


def test_estimate_wind_smoke_plume_drift():
    """Flame at (100, 100), smoke at (100, 50). Smoke moves North -> wind comes FROM South (180°)."""
    detections = [
        {
            "class_name": "hotspot",
            "centroid": {"x": 100, "y": 100},
            "bbox": {"w": 20, "h": 20},
        },
        {
            "class_name": "smoke",
            "centroid": {"x": 100, "y": 50},
            "bbox": {"w": 60, "h": 60},
        },
    ]

    res = estimate_wind_from_vision(detections)
    assert res["is_auto_detected"] is True
    assert "Smoke Plume Drift" in res["estimation_method"]
    assert abs(res["direction_degrees"] - 180.0) < 1.0
    assert "Selatan" in res["direction_compass"]
    assert res["speed_kmh"] is None  # not measurable from one frame


def test_wind_is_unknown_without_smoke():
    """Neither flames nor fuel reveal the wind, so nothing may be invented."""
    fire = [{"class_name": "hotspot", "centroid": {"x": 100, "y": 100}, "bbox": {"w": 20, "h": 20}}]
    for detections in ([], fire):
        res = estimate_wind_from_vision(detections, dry_mask=np.ones((300, 300), dtype=bool))
        assert res["direction_degrees"] is None
        assert res["speed_kmh"] is None
