"""Firebreak Route Optimizer Service for SEKAT-AI.

Calculates the shortest and safest cutting line (sekat bakar) to block fire progression
ahead of dry fuel zones, incorporating wind vector dynamics and safety buffers for MPA teams.
"""

import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import numpy as np
from PIL import Image, ImageDraw

from backend.app.core.config import (
    DEFAULT_FIREBREAK_WIDTH_METERS,
    DEFAULT_SAFETY_BUFFER_METERS,
    OUTPUT_DIR,
)
from backend.app.services.weather_service import parse_wind_direction, degrees_to_compass


class FirebreakOptimizer:
    """Optimizes firebreak trajectory, safety buffers, and clearing logistics."""

    def __init__(self, pixel_to_meter: float = 0.25):
        """Args:

        pixel_to_meter: Ground sampling distance ratio (~0.25m per pixel at 80m altitude).
        """
        self.pixel_to_meter = pixel_to_meter
        # Baseline reference coordinate for GPS simulation (Riau / Sumatra pilot site)
        self.base_lat = -0.22850
        self.base_lon = 101.55420

    def optimize(
        self,
        image_dimensions: Dict[str, int],
        dry_mask: Optional[np.ndarray],
        hotspots: List[Dict[str, Any]],
        wind_direction: Union[str, float] = 135.0,
        wind_speed_kmh: float = 14.0,
        safety_buffer_meters: float = DEFAULT_SAFETY_BUFFER_METERS,
        firebreak_width_meters: float = DEFAULT_FIREBREAK_WIDTH_METERS,
        image_id: str = "default",
    ) -> Dict[str, Any]:
        """Compute the optimal firebreak trajectory, metrics, and visualization overlay."""
        w = image_dimensions["width"]
        h = image_dimensions["height"]

        wind_deg = parse_wind_direction(wind_direction)
        wind_compass = degrees_to_compass(wind_deg)

        # Meteorological convention: Wind FROM direction pushes flames TO (dir + 180)
        spread_deg = (wind_deg + 180.0) % 360.0
        spread_rad = math.radians(spread_deg)

        # Spread unit vector in image coordinates (x: East/right, y: South/down)
        v_spread_x = math.sin(spread_rad)
        v_spread_y = -math.cos(spread_rad)

        # Perpendicular cutting line unit vector
        v_cut_x = -v_spread_y
        v_cut_y = v_spread_x

        # 1. Determine fire threat anchor point (Centroid)
        if hotspots and len(hotspots) > 0:
            # Use centroid of the active hotspot furthest along the spread direction
            scores = [
                h_item["centroid"]["x"] * v_spread_x + h_item["centroid"]["y"] * v_spread_y
                for h_item in hotspots
            ]
            lead_idx = int(np.argmax(scores))
            cx = float(hotspots[lead_idx]["centroid"]["x"])
            cy = float(hotspots[lead_idx]["centroid"]["y"])
            threat_type = "Titik Api Aktif"
        elif dry_mask is not None and np.sum(dry_mask) > 0:
            # Preventive patrol: use center of mass of dry fuel cluster
            ys, xs = np.where(dry_mask)
            cx = float(np.mean(xs))
            cy = float(np.mean(ys))
            threat_type = "Zona Semak Kering (Patroli Preventif)"
        else:
            cx = w * 0.5
            cy = h * 0.5
            threat_type = "Area Default"

        # 2. Dynamic safety buffer scaled with wind velocity
        # Higher wind speed requires larger buffer distance for team safety
        wind_factor = 1.0 + (max(0.0, wind_speed_kmh) / 35.0)
        effective_buffer_m = round(safety_buffer_meters * wind_factor, 1)
        buffer_pixels = effective_buffer_m / self.pixel_to_meter

        # 3. Position the firebreak line ahead of the threat
        anchor_x = cx + v_spread_x * buffer_pixels
        anchor_y = cy + v_spread_y * buffer_pixels

        # Clamp anchor within canvas
        anchor_x = max(60.0, min(w - 60.0, anchor_x))
        anchor_y = max(60.0, min(h - 60.0, anchor_y))

        # 4. Span cutting line across the corridor
        # Nominal cut length around 100 - 140 meters (400 - 560 pixels)
        target_pixel_span = 480.0
        half_span = target_pixel_span / 2.0

        p1_x = anchor_x - v_cut_x * half_span
        p1_y = anchor_y - v_cut_y * half_span
        p2_x = anchor_x + v_cut_x * half_span
        p2_y = anchor_y + v_cut_y * half_span

        # Boundary clamping with proportion preservation
        p1_x = max(20.0, min(w - 20.0, p1_x))
        p1_y = max(20.0, min(h - 20.0, p1_y))
        p2_x = max(20.0, min(w - 20.0, p2_x))
        p2_y = max(20.0, min(h - 20.0, p2_y))

        # 5. Calculate physical metrics
        pixel_length = math.hypot(p2_x - p1_x, p2_y - p1_y)
        cut_length_meters = round(pixel_length * self.pixel_to_meter, 1)

        # Standard manual babat clearing rate: ~25 meters/hour for 5-person MPA crew
        estimated_hours = round(cut_length_meters / 25.0, 1)

        # Protected area estimate (hectares)
        dry_area_pixels = float(np.sum(dry_mask)) if dry_mask is not None else (w * h * 0.4)
        protected_hectares = round((dry_area_pixels * (self.pixel_to_meter ** 2)) / 10000.0, 2)

        # GPS Coordinates calculation (Start and End Points)
        # 1 degree latitude ~= 111,320m; 1 degree longitude ~= 111,320m * cos(lat)
        m_per_lat = 111320.0
        m_per_lon = 111320.0 * math.cos(math.radians(self.base_lat))

        start_gps = {
            "latitude": round(self.base_lat + ((p1_y - h/2) * self.pixel_to_meter) / m_per_lat, 6),
            "longitude": round(self.base_lon + ((p1_x - w/2) * self.pixel_to_meter) / m_per_lon, 6),
        }
        end_gps = {
            "latitude": round(self.base_lat + ((p2_y - h/2) * self.pixel_to_meter) / m_per_lat, 6),
            "longitude": round(self.base_lon + ((p2_x - w/2) * self.pixel_to_meter) / m_per_lon, 6),
        }

        # 6. Generate Firebreak Visual Overlay (RGBA)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Draw Safety Buffer Circle / Perimeter around threat
        buffer_r = int(buffer_pixels)
        draw.ellipse(
            [int(cx - buffer_r), int(cy - buffer_r), int(cx + buffer_r), int(cy + buffer_r)],
            outline=(245, 158, 11, 100),
            width=2,
        )
        draw.text((int(cx - 55), int(cy + buffer_r - 16)), f"Jarak Aman Tim: {int(effective_buffer_m)}m", fill=(245, 158, 11, 210))

        # Draw Dashed / Thick Firebreak Line (Amber / Yellow)
        num_segments = 24
        for i in range(num_segments):
            if i % 2 == 0:
                t0 = i / num_segments
                t1 = (i + 1) / num_segments
                sx = int(p1_x + (p2_x - p1_x) * t0)
                sy = int(p1_y + (p2_y - p1_y) * t0)
                ex = int(p1_x + (p2_x - p1_x) * t1)
                ey = int(p1_y + (p2_y - p1_y) * t1)
                draw.line([(sx, sy), (ex, ey)], fill=(245, 158, 11, 245), width=5)

        # Draw Endpoints Beacon Circles with clear Indonesian text
        draw.ellipse([int(p1_x - 7), int(p1_y - 7), int(p1_x + 7), int(p1_y + 7)], fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((int(p1_x + 9), int(p1_y - 8)), "Mulai (A)", fill=(255, 255, 255, 240))

        draw.ellipse([int(p2_x - 7), int(p2_y - 7), int(p2_x + 7), int(p2_y + 7)], fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((int(p2_x + 9), int(p2_y - 8)), "Selesai (B)", fill=(255, 255, 255, 240))

        # Draw label on firebreak line
        mid_x = int((p1_x + p2_x) / 2)
        mid_y = int((p1_y + p2_y) / 2)
        draw.text((mid_x - 65, mid_y - 18), "JALUR SEKAT PEMUTUS API", fill=(245, 158, 11, 240))

        # Draw Wind Vector Arrow at Top Right
        arrow_cx, arrow_cy = w - 90, 80
        arrow_len = 35
        ax1 = arrow_cx + int(v_spread_x * arrow_len)
        ay1 = arrow_cy + int(v_spread_y * arrow_len)
        draw.line([(arrow_cx, arrow_cy), (ax1, ay1)], fill=(14, 165, 233, 240), width=4)
        draw.ellipse([arrow_cx - 4, arrow_cy - 4, arrow_cx + 4, arrow_cy + 4], fill=(14, 165, 233, 255))
        draw.text((w - 155, 30), f"Angin: {wind_speed_kmh} km/j", fill=(255, 255, 255, 230))
        draw.text((w - 155, 46), f"Arah: {wind_compass}", fill=(14, 165, 233, 255))

        # Save Overlay Image
        overlay_filename = f"firebreak_overlay_{image_id}.png"
        overlay_path = OUTPUT_DIR / overlay_filename
        overlay.save(overlay_path, "PNG")

        return {
            "trajectory": {
                "start_point": {"x": round(p1_x, 1), "y": round(p1_y, 1)},
                "end_point": {"x": round(p2_x, 1), "y": round(p2_y, 1)},
                "anchor_point": {"x": round(anchor_x, 1), "y": round(anchor_y, 1)},
                "threat_origin": {"x": round(cx, 1), "y": round(cy, 1), "type": threat_type},
            },
            "metrics": {
                "cutting_length_meters": cut_length_meters,
                "recommended_width_meters": firebreak_width_meters,
                "effective_safety_buffer_meters": effective_buffer_m,
                "estimated_clearing_hours": estimated_hours,
                "protected_area_hectares": protected_hectares,
                "recommended_team_size": 5,
            },
            "gps_coordinates": {
                "start": start_gps,
                "end": end_gps,
            },
            "wind_parameters": {
                "direction_degrees": wind_deg,
                "direction_compass": wind_compass,
                "speed_kmh": wind_speed_kmh,
            },
            "overlay_filename": overlay_filename,
            "overlay_url": f"/static/output/{overlay_filename}",
        }


# Singleton instance
firebreak_optimizer = FirebreakOptimizer()
