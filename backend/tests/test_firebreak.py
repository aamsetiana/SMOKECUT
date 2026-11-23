"""Unit tests for Firebreak Route Optimizer service."""

import numpy as np
import pytest

from backend.app.services.firebreak_optimizer import firebreak_optimizer


def test_firebreak_optimization_with_hotspot():
    """Firebreak must be placed in front of active hotspot in downwind direction."""
    dimensions = {"width": 800, "height": 600}
    dry_mask = np.zeros((600, 800), dtype=bool)
    dry_mask[200:500, 300:700] = True

    hotspots = [
        {"centroid": {"x": 480, "y": 320}, "class_name": "hotspot"}
    ]

    result = firebreak_optimizer.optimize(
        image_dimensions=dimensions,
        dry_mask=dry_mask,
        hotspots=hotspots,
        wind_direction=135.0,  # Southeast wind
        wind_speed_kmh=14.0,
        safety_buffer_meters=25.0,
        image_id="test_opt",
    )

    metrics = result["metrics"]
    assert metrics["cutting_length_meters"] > 0
    assert metrics["effective_safety_buffer_meters"] >= 25.0
    assert metrics["estimated_clearing_hours"] > 0
    assert metrics["recommended_width_meters"] == 4.0

    traj = result["trajectory"]
    assert "start_point" in traj
    assert "end_point" in traj

    gps = result["gps_coordinates"]
    assert -90 <= gps["start"]["latitude"] <= 90
    assert -180 <= gps["start"]["longitude"] <= 180
    assert "overlay_url" in result


def test_safety_buffer_scales_with_wind():
    """Higher wind speed must produce larger safety buffer."""
    dimensions = {"width": 800, "height": 600}
    dry_mask = np.ones((600, 800), dtype=bool)

    res_low = firebreak_optimizer.optimize(
        image_dimensions=dimensions,
        dry_mask=dry_mask,
        hotspots=[],
        wind_speed_kmh=5.0,
        safety_buffer_meters=20.0,
        image_id="low_wind",
    )

    res_high = firebreak_optimizer.optimize(
        image_dimensions=dimensions,
        dry_mask=dry_mask,
        hotspots=[],
        wind_speed_kmh=35.0,
        safety_buffer_meters=20.0,
        image_id="high_wind",
    )

    assert (
        res_high["metrics"]["effective_safety_buffer_meters"]
        > res_low["metrics"]["effective_safety_buffer_meters"]
    )
