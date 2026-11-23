"""Unit tests for VARI (Visible Atmospherically Resistant Index) calculation and zoning."""

import numpy as np
import pytest
from PIL import Image

from backend.app.services.vari_analyzer import VARIAnalyzer, vari_analyzer


def test_vari_pure_green():
    """Pure green foliage should yield maximum positive VARI value (1.0)."""
    # G=255, R=0, B=0 -> (255 - 0) / (255 + 0 - 0) = 1.0
    pure_green = np.zeros((10, 10, 3), dtype=np.uint8)
    pure_green[:, :, 1] = 255

    vari = vari_analyzer.calculate_vari(pure_green)
    assert np.allclose(vari, 1.0)


def test_vari_dry_grass_red_dominant():
    """Dry, withered vegetation (higher Red than Green) yields low or negative VARI."""
    # R=200, G=150, B=60 -> (150 - 200) / (150 + 200 - 60) = -50 / 290 = -0.1724
    dry_pixel = np.zeros((5, 5, 3), dtype=np.uint8)
    dry_pixel[:, :, 0] = 200  # Red
    dry_pixel[:, :, 1] = 150  # Green
    dry_pixel[:, :, 2] = 60   # Blue

    vari = vari_analyzer.calculate_vari(dry_pixel)
    expected = (150 - 200) / (150 + 200 - 60)
    assert np.allclose(vari, expected, atol=1e-3)
    assert np.all(vari <= 0.1)  # Accurately identified as dry fuel


def test_vari_zero_division_safety():
    """Denominator (G + R - B) near or equal to zero must not cause NaN or Inf."""
    # G=50, R=50, B=100 -> G + R - B = 0
    zero_denom = np.zeros((5, 5, 3), dtype=np.uint8)
    zero_denom[:, :, 0] = 50
    zero_denom[:, :, 1] = 50
    zero_denom[:, :, 2] = 100

    vari = vari_analyzer.calculate_vari(zero_denom)
    assert not np.any(np.isnan(vari))
    assert not np.any(np.isinf(vari))
    assert np.all(vari >= -1.0) and np.all(vari <= 1.0)


def test_analyze_image_produces_overlay_and_stats(tmp_path):
    """Testing complete image analysis pipeline on sample image."""
    img = Image.new("RGB", (100, 100), color=(180, 150, 70))
    result = vari_analyzer.analyze_image(img, image_id="test_unit")

    stats = result["statistics"]
    assert stats["total_pixels"] == 10000
    assert stats["dry_fuel_percentage"] > 0
    assert stats["risk_level"] in ("TINGGI", "SEDANG", "RENDAH")
    assert "overlay_url" in result
    assert result["dry_mask"].shape == (100, 100)
