"""Unit test for sample aerial data availability and integrity."""

from PIL import Image
from backend.app.core.config import SAMPLES_DIR


def test_sample_aerial_image_exists_and_valid():
    sample_path = SAMPLES_DIR / "sample_aerial.jpg"
    assert sample_path.exists(), f"Sample aerial image not found at {sample_path}"

    with Image.open(sample_path) as img:
        assert img.format in ("JPEG", "JPG")
        width, height = img.size
        assert width >= 600 and height >= 400
        assert img.mode in ("RGB", "RGBA")
