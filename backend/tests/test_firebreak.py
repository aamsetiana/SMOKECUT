"""Unit tests for firebreak standards and the route optimizer."""

import numpy as np
import pytest

from backend.app.core import standards
from backend.app.services.firebreak_optimizer import firebreak_optimizer

DIMENSIONS = {"width": 800, "height": 600}
HOTSPOT = [{"centroid": {"x": 400, "y": 300}, "class_name": "hotspot"}]
GEO = {"ground_width_m": 400.0, "latitude": -0.5, "longitude": 101.5, "heading_deg": 0.0}


def plan(**kwargs):
    args = dict(image_dimensions=DIMENSIONS, dry_mask=np.ones((600, 800), dtype=bool), hotspots=HOTSPOT,
                wind_direction=180.0, image_id="test_opt")
    args.update(kwargs)
    return firebreak_optimizer.optimize(**args)


def test_width_follows_permen_lhk_28_2021():
    assert standards.firebreak_width_m(None) == 20.0
    assert standards.firebreak_width_m(5.0) == 20.0  # 3 x 5 is below the minimum
    assert standards.firebreak_width_m(10.0) == 30.0


def test_safe_separation_matches_usfs_example():
    assert standards.safe_separation_m(1.0, 2.0) == 16.0  # example in the source
    assert standards.safe_separation_m(None, 2.0) is None


def test_operator_cannot_go_below_standard():
    res = plan(firebreak_width_meters=4.0, safety_buffer_meters=1.0, fuel_height_m=2.0, geo=GEO)
    assert res["metrics"]["recommended_width_meters"] == 20.0
    assert res["metrics"]["effective_safety_buffer_meters"] == 16.0
    assert any("di bawah standar" in w for w in res["warnings"])


def test_nothing_is_measured_without_scale():
    res = plan(fuel_height_m=2.0)
    m = res["metrics"]
    assert not res["is_to_scale"] and res["trajectory"]["polyline"]
    assert m["cutting_length_meters"] is None and m["protected_area_hectares"] is None
    assert m["estimated_clearing_hours"] is None and m["recommended_team_size"] is None
    assert res["gps_coordinates"] == {"start": None, "end": None}


def test_belt_near_edge_is_at_safe_distance():
    res = plan(fuel_height_m=2.0, geo=GEO)  # SSD 16 m, half width 10 m, 0.5 m/px
    assert res["is_to_scale"]
    d = [np.hypot(p["x"] - 400, p["y"] - 300) * 0.5 for p in res["trajectory"]["polyline"]]
    assert min(d) >= 24.0 and max(d) <= 29.0
    assert res["trajectory"]["anchor_point"]["y"] < 300  # wind from south pushes fire north


def test_gps_uses_heading():
    north = plan(fuel_height_m=2.0, geo=GEO)["gps_coordinates"]
    assert north["start"]["latitude"] > -0.5  # line lies north of the centre
    east = plan(fuel_height_m=2.0, geo={**GEO, "heading_deg": 90.0})["gps_coordinates"]
    assert east["start"]["longitude"] > 101.5
    missing = plan(fuel_height_m=2.0, geo={**GEO, "heading_deg": None})["gps_coordinates"]
    assert missing["start"] is None


def test_preventive_line_needs_wind():
    assert plan(hotspots=[], wind_direction=None)["trajectory"]["polyline"] == []
    res = plan(hotspots=[], geo=GEO)
    assert res["metrics"]["cutting_length_meters"] == pytest.approx(400, rel=0.05)


def test_fire_outside_frame_is_not_to_scale():
    res = plan(fuel_height_m=30.0, geo=GEO)  # SSD 240 m does not fit in the frame
    assert not res["is_to_scale"]
    assert res["metrics"]["cutting_length_meters"] is None
