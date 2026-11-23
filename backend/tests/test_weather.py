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
    assert parse_wind_direction(None) == 135.0
    assert parse_wind_direction("auto") == 135.0
    assert parse_wind_direction("UNKNOWN") == 135.0
    assert parse_wind_direction("") == 135.0
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
    assert res["speed_kmh"] >= 8.0


def test_estimate_wind_fuel_gradient():
    """Flame at (100, 100), no smoke, but dry fuel cluster centered at (200, 100)."""
    detections = [
        {
            "class_name": "hotspot",
            "centroid": {"x": 100, "y": 100},
            "bbox": {"w": 20, "h": 20},
        }
    ]
    dry_mask = np.zeros((300, 300), dtype=bool)
    dry_mask[90:110, 190:210] = True  # Center around (200, 100)

    res = estimate_wind_from_vision(detections, dry_mask=dry_mask)
    assert res["is_auto_detected"] is True
    assert "Fuel Gradient" in res["estimation_method"]
    # Spread is to the East (90°), so wind comes FROM West (270°)
    assert abs(res["direction_degrees"] - 270.0) < 5.0
    assert "Barat" in res["direction_compass"]


def test_estimate_wind_baseline_fallback():
    """No flames or detections falls back to baseline buffer."""
    res = estimate_wind_from_vision([])
    assert res["is_auto_detected"] is True
    assert "Baseline Buffer" in res["estimation_method"]
    assert res["direction_degrees"] == 135.0
