"""Integration and unit tests for SEKAT-AI REST API endpoints."""

import io
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_upload_image_endpoint():
    """Test POST /api/upload with valid JPEG image."""
    img_byte_arr = io.BytesIO()
    img = Image.new("RGB", (200, 200), color=(100, 150, 80))
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    response = client.post(
        "/api/upload",
        files={"file": ("test_drone.jpg", img_bytes, "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "image_id" in data
    assert data["dimensions"]["width"] == 200
    assert data["dimensions"]["height"] == 200


def test_upload_invalid_extension():
    """Test POST /api/upload with disallowed extension."""
    response = client.post(
        "/api/upload",
        files={"file": ("malicious.exe", b"not an image", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "tidak didukung" in response.json()["detail"]


def test_analyze_sample_image():
    """Test POST /api/analyze on standard sample aerial image."""
    payload = {
        "image_id": "sample",
        "wind_direction": "SE",
        "wind_speed": 14.0,
        "safety_buffer": 25.0,
        "firebreak_width": 4.0,
    }

    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "summary" in data
    assert data["summary"]["risk_level"] in ("TINGGI", "SEDANG", "RENDAH")
    assert data["summary"]["cutting_length_meters"] > 0

    assert "layers" in data
    assert "vari_heatmap_url" in data["layers"]
    assert "detection_overlay_url" in data["layers"]
    assert "firebreak_overlay_url" in data["layers"]

    assert "vari_analysis" in data
    assert "detections" in data
    assert "firebreak_plan" in data
    assert "gps_coordinates" in data["firebreak_plan"]


def test_dispatch_whatsapp_endpoint():
    """Test POST /api/dispatch-whatsapp generating MPA and resident alerts."""
    payload = {"image_id": "sample"}

    response = client.post("/api/dispatch-whatsapp", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    dispatches = data["dispatches"]
    assert len(dispatches) == 2

    # Verify MPA team message
    mpa_msg = dispatches[0]
    assert mpa_msg["recipient_group"] == "Tim MPA / BPBD"
    assert "wa.me" in mpa_msg["deep_link"]
    assert "SMOKECUT ALERT" in mpa_msg["message_text"]

    # Verify Downwind residents message
    downwind_msg = dispatches[1]
    assert "Downwind" in downwind_msg["recipient_group"]
    assert "wa.me" in downwind_msg["deep_link"]
    assert "PM2.5" in downwind_msg["message_text"]


def test_upload_and_analyze_video_endpoint():
    """Test uploading an MP4 drone video and running full 3-layer analysis on its keyframe."""
    video_path = "samples/sample_drone_fire.mp4"
    with open(video_path, "rb") as f:
        res_upload = client.post(
            "/api/upload",
            files={"file": ("sample_drone_fire.mp4", f, "video/mp4")},
        )

    assert res_upload.status_code == 200
    upload_data = res_upload.json()
    assert upload_data["status"] == "success"
    assert upload_data["media_type"] == "video"
    image_id = upload_data["image_id"]

    # Trigger analysis on the uploaded video
    payload = {
        "image_id": image_id,
        "wind_direction": 135.0,
        "wind_speed": 14.0,
        "safety_buffer": 25.0,
        "firebreak_width": 4.0,
    }
    res_analyze = client.post("/api/analyze", json=payload)
    assert res_analyze.status_code == 200
    analyze_data = res_analyze.json()

    assert analyze_data["status"] == "success"
    assert "vari_analysis" in analyze_data
    assert "detections" in analyze_data
    assert "firebreak_plan" in analyze_data
    assert analyze_data["summary"]["cutting_length_meters"] > 0
    assert "frame.jpg" in analyze_data["layers"]["original_image_url"]

