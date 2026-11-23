"""Unit tests for early flame and smoke detection."""

import numpy as np
from PIL import Image

from backend.app.services.fire_detector import FireSmokeDetector, fire_detector
from backend.app.core.config import SAMPLES_DIR


def test_detect_flame_synthetic():
    """Synthetic image with bright flame spot should be detected as hotspot."""
    # Create black image with flame patch at center
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    arr[40:55, 40:55] = [255, 140, 20]  # Flame colors

    result = fire_detector.detect(arr, image_id="test_flame")
    assert result["total_detected"] >= 1
    assert result["hotspot_count"] >= 1

    det = result["detections"][0]
    assert det["class_name"] == "hotspot"
    assert det["confidence"] >= 0.85
    assert 35 <= det["centroid"]["x"] <= 60
    assert 35 <= det["centroid"]["y"] <= 60


def test_detect_sample_aerial_image():
    """Detect on real/sample aerial drone image."""
    sample_path = SAMPLES_DIR / "sample_aerial.jpg"
    result = fire_detector.detect(sample_path, image_id="test_aerial")

    assert "detections" in result
    assert result["hotspot_count"] >= 1
    assert "overlay_url" in result
