"""Application configuration settings for SEKAT-AI Core Engine."""

import os
from pathlib import Path
from typing import List

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR.parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
SAMPLES_DIR = BASE_DIR.parent / "samples"
MODELS_DIR = BASE_DIR / "models"

# Ensure runtime directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Application Metadata
APP_NAME = "SMOKECUT Core Engine"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "Smart Drone-Vision untuk Mitigasi Sekat Bakar & Pencegahan Asap PM2.5 "
    "- Solusi Pure Software Drone-Agnostic SMOKECUT untuk AIRIMPACT 2026."
)

# Server Settings
HOST = os.getenv("SEKAT_HOST", "0.0.0.0")
PORT = int(os.getenv("SEKAT_PORT", "8000"))
DEBUG = os.getenv("SEKAT_DEBUG", "True").lower() in ("true", "1", "yes")

# CORS Settings
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "*",
]

# Analytical Defaults (VARI & Firebreak)
VARI_DRY_THRESHOLD = 0.1  # Pixel VARI <= 0.1 is dry flammable fuel zone
DEFAULT_FIREBREAK_WIDTH_METERS = 4.0  # Recommended width: 3 - 5 meters
DEFAULT_SAFETY_BUFFER_METERS = 25.0  # Buffer distance from fire head
DEFAULT_WIND_SPEED_KMH = 14.0  # Realistic default wind velocity
DEFAULT_WIND_DIRECTION = "SE"  # Southeast (Tenggara) towards settlement
