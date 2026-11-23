"""Weather and Wind Direction Processing Service for SEKAT-AI."""

from typing import Dict, Any, Union


COMPASS_TO_DEGREES = {
    "N": 0.0,
    "UTARA": 0.0,
    "NNE": 22.5,
    "NE": 45.0,
    "TIMUR LAUT": 45.0,
    "ENE": 67.5,
    "E": 90.0,
    "TIMUR": 90.0,
    "ESE": 112.5,
    "SE": 135.0,
    "TENGGARA": 135.0,
    "SSE": 157.5,
    "S": 180.0,
    "SELATAN": 180.0,
    "SSW": 202.5,
    "SW": 225.0,
    "BARAT DAYA": 225.0,
    "WSW": 247.5,
    "W": 270.0,
    "BARAT": 270.0,
    "WNW": 292.5,
    "NW": 315.0,
    "BARAT LAUT": 315.0,
    "NNW": 337.5,
}


def parse_wind_direction(direction: Union[str, int, float]) -> float:
    """Normalize wind direction to degrees (0 - 360)."""
    if isinstance(direction, (int, float)):
        return float(direction) % 360.0

    dir_clean = str(direction).strip().upper()
    if dir_clean in COMPASS_TO_DEGREES:
        return COMPASS_TO_DEGREES[dir_clean]

    # Try numeric string
    try:
        return float(dir_clean) % 360.0
    except ValueError:
        # Default to Southeast (135°)
        return 135.0


def degrees_to_compass(degrees: float) -> str:
    """Convert degrees (0 - 360) to 8-point Indonesian compass direction."""
    deg = degrees % 360.0
    if 337.5 <= deg or deg < 22.5:
        return "Utara (N)"
    elif 22.5 <= deg < 67.5:
        return "Timur Laut (NE)"
    elif 67.5 <= deg < 112.5:
        return "Timur (E)"
    elif 112.5 <= deg < 157.5:
        return "Tenggara (SE)"
    elif 157.5 <= deg < 202.5:
        return "Selatan (S)"
    elif 202.5 <= deg < 247.5:
        return "Barat Daya (SW)"
    elif 247.5 <= deg < 292.5:
        return "Barat (W)"
    else:
        return "Barat Laut (NW)"
