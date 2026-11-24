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


def parse_wind_direction(direction: Union[str, int, float, None]) -> float:
    """Normalize wind direction to degrees (0 - 360)."""
    if direction is None:
        return 135.0

    if isinstance(direction, (int, float)):
        return float(direction) % 360.0

    dir_clean = str(direction).strip().upper()
    if dir_clean in ("AUTO", "UNKNOWN", "NONE", ""):
        return 135.0

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


def estimate_wind_from_vision(
    detections: list,
    dry_mask=None,
    default_dir: float = 135.0,
    default_speed: float = 14.0,
) -> Dict[str, Any]:
    """Infers wind direction and speed automatically from drone vision.

    Uses smoke plume drift relative to flame hotspot or dry bush fuel gradient.
    """
    import math
    import numpy as np

    flames = [d for d in detections if d.get("class_name") == "hotspot"]
    smokes = [d for d in detections if d.get("class_name") == "smoke"]

    if flames:
        flames.sort(
            key=lambda f: f.get("bbox", {}).get("w", 0) * f.get("bbox", {}).get("h", 0),
            reverse=True,
        )
    if smokes:
        smokes.sort(
            key=lambda s: s.get("bbox", {}).get("w", 0) * s.get("bbox", {}).get("h", 0),
            reverse=True,
        )

    # Method 1: Smoke plume drift relative to flame origin (Physically grounded)
    if flames and smokes:
        fx = flames[0]["centroid"]["x"]
        fy = flames[0]["centroid"]["y"]

        # Largest smoke cluster centroid
        sx = smokes[0]["centroid"]["x"]
        sy = smokes[0]["centroid"]["y"]

        dx = sx - fx
        dy = sy - fy
        dist = math.hypot(dx, dy)

        if dist >= 20.0:
            # In image coords (x: East, y: South), angle of smoke motion:
            # atan2(dx, -dy) gives compass heading (0=North, 90=East, 180=South, 270=West)
            smoke_deg = (math.degrees(math.atan2(dx, -dy))) % 360.0
            # Wind comes FROM the opposite direction
            wind_from_deg = (smoke_deg + 180.0) % 360.0
            # Speed cannot be measured from a single frame, so use the default
            est_speed = default_speed
            compass = degrees_to_compass(wind_from_deg)

            return {
                "direction_degrees": round(wind_from_deg, 1),
                "direction_compass": compass,
                "speed_kmh": est_speed,
                "is_auto_detected": True,
                "estimation_method": "Dispersi Kepulan Asap Drone (Smoke Plume Drift)",
                "confidence": "Rendah (arah relatif kamera, kecepatan asumsi)",
                "keterangan": f"Asap membubung ke arah {degrees_to_compass(smoke_deg)}, perkiraan angin dari {compass} (relatif arah kamera; kecepatan asumsi).",
            }

    # Method 2: Fuel Gradient (flame spreads towards dense dry bushes)
    if flames and dry_mask is not None and np.sum(dry_mask) > 0:
        fx = flames[0]["centroid"]["x"]
        fy = flames[0]["centroid"]["y"]
        ys, xs = np.where(dry_mask)
        mx = float(np.mean(xs))
        my = float(np.mean(ys))
        dx = mx - fx
        dy = my - fy
        dist = math.hypot(dx, dy)
        if dist >= 25.0:
            spread_deg = (math.degrees(math.atan2(dx, -dy))) % 360.0
            wind_from_deg = (spread_deg + 180.0) % 360.0
            compass = degrees_to_compass(wind_from_deg)
            return {
                "direction_degrees": round(wind_from_deg, 1),
                "direction_compass": compass,
                "speed_kmh": 12.0,
                "is_auto_detected": True,
                "estimation_method": "Gradien Konsentrasi Semak Kering (Fuel Gradient)",
                "confidence": "Moderat (Berdasarkan Kontur Bahan Bakar)",
                "keterangan": f"Api berpotensi merambat menuju kantong semak kering di arah {degrees_to_compass(spread_deg)}.",
            }

    # Method 3: Radial Barrier Fallback (Calm / Unknown Wind)
    compass = degrees_to_compass(default_dir)
    return {
        "direction_degrees": default_dir,
        "direction_compass": compass,
        "speed_kmh": default_speed,
        "is_auto_detected": True,
        "estimation_method": "Standar Patroli Lapangan Aman (Baseline Buffer)",
        "confidence": "Konservatif",
        "keterangan": "Angin tenang atau tidak terdeteksi kepulan condong. Rekomendasi sekat bakar dipasang mengunci batas semak kering terdekat.",
    }
