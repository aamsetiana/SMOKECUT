"""Real scale and position of a photo, read from drone metadata (EXIF/XMP)."""

import math
import re
from pathlib import Path
from typing import Dict, Optional

from PIL import Image

FULL_FRAME_DIAGONAL_MM = 43.27
MAX_NADIR_PITCH = -80.0  # Scale is only uniform when the camera looks straight down


def read_drone_metadata(path: Path) -> Dict[str, Optional[float]]:
    """Return ground_width_m, latitude, longitude, heading_deg (None when unavailable).

    ``ground_width_m`` is the ground length covered by the longest image side.
    Altitude in drone metadata is relative to the take-off point.
    """
    result: Dict[str, Optional[float]] = dict.fromkeys(("ground_width_m", "latitude", "longitude", "heading_deg"))
    if path.suffix.lower() not in (".jpg", ".jpeg"):
        return result
    xmp = path.read_bytes()[:300_000].decode("latin-1")

    def tag(*names: str) -> Optional[float]:
        for name in names:
            match = re.search(rf'drone-dji:{name}(?:="|>)\s*([+-]?\d+(?:\.\d+)?)', xmp)
            if match:
                return float(match.group(1))
        return None

    pitch = tag("GimbalPitchDegree")
    if pitch is None or pitch > MAX_NADIR_PITCH:
        return result
    with Image.open(path) as img:
        width, height = img.size
        exif = img.getexif()
    if exif.get(0x0112, 1) != 1:
        return result
    focal = exif.get_ifd(0x8769).get(41989)  # FocalLengthIn35mmFilm
    altitude = tag("RelativeAltitude")
    if focal and altitude and altitude > 0:
        diagonal = altitude * FULL_FRAME_DIAGONAL_MM / float(focal)
        result["ground_width_m"] = diagonal * max(width, height) / math.hypot(width, height)
    result["latitude"] = tag("GpsLatitude")
    result["longitude"] = tag("GpsLongitude", "GpsLongtitude")
    result["heading_deg"] = tag("GimbalYawDegree")
    return result
