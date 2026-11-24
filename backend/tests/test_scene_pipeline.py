"""Regression tests for fire-front detection and firebreak placement."""

import io
import time

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app
from backend.app.services.fire_detector import fire_detector, segment_scene
from backend.app.services.firebreak_optimizer import firebreak_optimizer

client = TestClient(app)


def make_scene(width: int = 1280, height: int = 720) -> np.ndarray:
    """Burnt grey land above a broken flame front, dry brown fuel below."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[: height // 2] = (120, 118, 116)
    img[height // 2:] = (130, 110, 50)
    y0, step = height // 2, width // 80
    for x in range(width // 4, 3 * width // 4, step):  # gaps between flames
        img[y0 - step // 3: y0 + step // 3, x: x + step // 2] = (255, 160, 30)
    return img


def test_broken_flames_become_one_front():
    fires = [d for d in fire_detector.detect_cv(make_scene()) if d["class_name"] == "hotspot"]
    assert len(fires) == 1
    assert fires[0]["label"] == "Garis Api Aktif"


def test_burnt_land_is_not_fuel():
    fuel = segment_scene(make_scene()).fuel
    assert fuel[:300].mean() < 0.01
    assert fuel[420:].mean() > 0.99


def test_road_is_not_smoke():
    img = np.full((720, 1280, 3), (130, 110, 50), dtype=np.uint8)
    img[300:340] = (160, 158, 156)
    assert fire_detector.detect_cv(img) == []


@pytest.mark.parametrize("wind", [0.0, 180.0])
def test_firebreak_lies_in_fuel_at_safe_distance(wind):
    img = make_scene()
    masks = segment_scene(img)
    plan = firebreak_optimizer.optimize(
        {"width": 1280, "height": 720}, masks.fuel, fire_detector.detect_cv(img, masks), wind_direction=wind,
        safety_buffer_meters=20.0, image_id="test_front", fire_mask=masks.fire, fuel_mask=masks.fuel,
    )
    dist = cv2.distanceTransform(1 - masks.fire.astype(np.uint8), cv2.DIST_L2, 5)
    line = plan["trajectory"]["polyline"]
    buffer_px = plan["metrics"]["effective_safety_buffer_meters"] / plan["meters_per_pixel"]
    for p in line:
        x, y = int(p["x"]), int(p["y"])
        assert dist[y, x] >= 0.85 * buffer_px
    assert all(p["y"] > 340 for p in line)  # never through burnt land
    assert line[-1]["x"] - line[0]["x"] > 600  # spans the whole front


def test_gps_latitude_increases_northwards():
    res = firebreak_optimizer.optimize(
        {"width": 800, "height": 600}, None, [{"class_name": "hotspot", "centroid": {"x": 400, "y": 300}}],
        wind_direction=90.0, image_id="test_gps",
    )
    traj, gps = res["trajectory"], res["gps_coordinates"]
    assert (traj["start_point"]["y"] < traj["end_point"]["y"]) == (
        gps["start"]["latitude"] > gps["end"]["latitude"]
    )


def test_unknown_image_id_returns_404():
    for image_id in ("tidak_ada_123", "*", "../x"):
        assert client.post("/api/analyze", json={"image_id": image_id}).status_code == 404


def test_results_do_not_depend_on_resolution_and_are_fast():
    lengths = []
    for w, h in ((1280, 720), (3840, 2160)):
        buf = io.BytesIO()
        Image.fromarray(make_scene()).resize((w, h)).save(buf, "JPEG", quality=95)
        up = client.post("/api/upload", files={"file": ("a.jpg", buf.getvalue(), "image/jpeg")}).json()
        start = time.perf_counter()
        res = client.post("/api/analyze", json={"image_id": up["image_id"], "wind_direction": 0, "wind_speed": 10})
        assert time.perf_counter() - start < 2.0
        lengths.append(res.json()["summary"]["cutting_length_meters"])
    assert lengths[0] == pytest.approx(lengths[1], rel=0.05)
