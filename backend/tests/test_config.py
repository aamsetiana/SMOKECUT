"""Unit tests for SEKAT-AI configuration module."""

from backend.app.core.config import (
    APP_NAME,
    APP_VERSION,
    VARI_DRY_THRESHOLD,
    DEFAULT_FIREBREAK_WIDTH_METERS,
    DEFAULT_SAFETY_BUFFER_METERS,
    DEFAULT_WIND_SPEED_KMH,
    DEFAULT_WIND_DIRECTION,
    UPLOADS_DIR,
    OUTPUT_DIR,
    SAMPLES_DIR,
)


def test_config_constants():
    assert "SEKAT-AI" in APP_NAME
    assert APP_VERSION == "1.0.0"
    assert VARI_DRY_THRESHOLD == 0.1
    assert 3.0 <= DEFAULT_FIREBREAK_WIDTH_METERS <= 5.0
    assert DEFAULT_SAFETY_BUFFER_METERS >= 20.0
    assert DEFAULT_WIND_SPEED_KMH > 0
    assert DEFAULT_WIND_DIRECTION == "SE"


def test_runtime_directories_exist():
    assert UPLOADS_DIR.exists()
    assert OUTPUT_DIR.exists()
    assert SAMPLES_DIR.exists()
