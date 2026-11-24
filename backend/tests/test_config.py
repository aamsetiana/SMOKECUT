"""Unit tests for SEKAT-AI configuration module."""

from backend.app.core.config import (
    APP_NAME,
    APP_VERSION,
    VARI_DRY_THRESHOLD,
    UPLOADS_DIR,
    OUTPUT_DIR,
    SAMPLES_DIR,
)


def test_config_constants():
    assert "SMOKECUT" in APP_NAME
    assert APP_VERSION == "1.0.0"
    assert VARI_DRY_THRESHOLD == 0.1


def test_runtime_directories_exist():
    assert UPLOADS_DIR.exists()
    assert OUTPUT_DIR.exists()
    assert SAMPLES_DIR.exists()
