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
        is_auto_wind: bool = False,
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

        # 1. Determine fire threat anchor point (Centroid & Threat Profile)
        actual_hotspots = [h for h in hotspots if h.get("class_name") == "hotspot"]
        actual_smokes = [h for h in hotspots if h.get("class_name") == "smoke"]

        if actual_hotspots:
            # Score active hotspots along spread direction to identify leading fire edge
            scores = [
                h_item["centroid"]["x"] * v_spread_x + h_item["centroid"]["y"] * v_spread_y
                for h_item in actual_hotspots
            ]
            lead_idx = int(np.argmax(scores))
            cx = float(actual_hotspots[lead_idx]["centroid"]["x"])
            cy = float(actual_hotspots[lead_idx]["centroid"]["y"])
            threat_type = "Titik Api Aktif"
        elif actual_smokes:
            # Sort smoke plumes to identify primary plume source
            lead_smoke = max(
                actual_smokes,
                key=lambda s: s.get("bbox", {}).get("w", 0) * s.get("bbox", {}).get("h", 0),
            )
            cx = float(lead_smoke["centroid"]["x"])
            cy = float(lead_smoke["centroid"]["y"])
            threat_type = "Kepulan Asap Dini (Api Tersembunyi)"
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
        anchor_x = max(50.0, min(w - 50.0, anchor_x))
        anchor_y = max(50.0, min(h - 50.0, anchor_y))

        # 4. Precision Fuel-Aware Firebreak Span
        # Base lateral span calculated from active fire threat flank spread
        if actual_hotspots:
            t_flames = [
                (h_item["centroid"]["x"] - anchor_x) * v_cut_x + (h_item["centroid"]["y"] - anchor_y) * v_cut_y
                for h_item in actual_hotspots
            ]
            # Safety flank: at least 15m (60px) beyond leftmost and rightmost flame points
            flank_margin = 60.0
            min_t = min(t_flames) - flank_margin
            max_t = max(t_flames) + flank_margin
        else:
            # Nominal base span around anchor: 30m each side
            min_t = -120.0
            max_t = 120.0

        # Scan along cutting axis into dry fuel corridor to determine precise cut boundaries
        t_start = min_t
        t_end = max_t

        if dry_mask is not None and np.sum(dry_mask) > 0:
            step = 6.0
            # Scan left flank (-t)
            cur_t = min_t
            for _ in range(40):
                chk_x = int(round(anchor_x + (cur_t - step) * v_cut_x))
                chk_y = int(round(anchor_y + (cur_t - step) * v_cut_y))
                if 25 <= chk_x < w - 25 and 25 <= chk_y < h - 25 and dry_mask[chk_y, chk_x]:
                    cur_t -= step
                else:
                    # Anchor 20px (5m) into green/safe moisture zone
                    cur_t -= 20.0
                    break
            t_start = max(-260.0, cur_t)

            # Scan right flank (+t)
            cur_t = max_t
            for _ in range(40):
                chk_x = int(round(anchor_x + (cur_t + step) * v_cut_x))
                chk_y = int(round(anchor_y + (cur_t + step) * v_cut_y))
                if 25 <= chk_x < w - 25 and 25 <= chk_y < h - 25 and dry_mask[chk_y, chk_x]:
                    cur_t += step
                else:
                    cur_t += 20.0
                    break
            t_end = min(260.0, cur_t)

        # Minimum effective cut length: at least 40m (160px)
        if (t_end - t_start) < 160.0:
            center_t = (t_start + t_end) / 2.0
            t_start = center_t - 80.0
            t_end = center_t + 80.0

        p1_x = max(25.0, min(w - 25.0, anchor_x + t_start * v_cut_x))
        p1_y = max(25.0, min(h - 25.0, anchor_y + t_start * v_cut_y))
        p2_x = max(25.0, min(w - 25.0, anchor_x + t_end * v_cut_x))
        p2_y = max(25.0, min(h - 25.0, anchor_y + t_end * v_cut_y))

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

        # 6. Generate Precision Tactical Firebreak Visual Overlay (RGBA)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # 6a. Draw Safety Buffer Perimeter and Fire Interception Arrow
        buffer_r = int(buffer_pixels)
        draw.ellipse(
            [int(cx - buffer_r), int(cy - buffer_r), int(cx + buffer_r), int(cy + buffer_r)],
            outline=(245, 158, 11, 140),
            width=2,
        )
        draw.text((int(cx - 65), int(cy + buffer_r - 18)), f"Jarak Aman Tim: {int(effective_buffer_m)}m", fill=(245, 158, 11, 230))

        # Arrow indicating intercepted fire spread vector
        if math.hypot(anchor_x - cx, anchor_y - cy) >= 20.0:
            arr_tip_x = cx + v_spread_x * min(buffer_pixels * 0.85, buffer_pixels - 12.0)
            arr_tip_y = cy + v_spread_y * min(buffer_pixels * 0.85, buffer_pixels - 12.0)
            draw.line([(int(cx), int(cy)), (int(arr_tip_x), int(arr_tip_y))], fill=(239, 68, 68, 220), width=3)
            # Arrowhead
            head_len = 10.0
            h1_x = arr_tip_x - v_spread_x * head_len + v_cut_x * (head_len * 0.5)
            h1_y = arr_tip_y - v_spread_y * head_len + v_cut_y * (head_len * 0.5)
            h2_x = arr_tip_x - v_spread_x * head_len - v_cut_x * (head_len * 0.5)
            h2_y = arr_tip_y - v_spread_y * head_len - v_cut_y * (head_len * 0.5)
            draw.polygon([(int(arr_tip_x), int(arr_tip_y)), (int(h1_x), int(h1_y)), (int(h2_x), int(h2_y))], fill=(239, 68, 68, 240))
            draw.text((int((cx + arr_tip_x)/2 - 45), int((cy + arr_tip_y)/2 - 10)), "Rambatan Terblokir", fill=(255, 255, 255, 220))

        # 6b. Draw Shaded Cutting Corridor (Zona Tebas Lebar 3-5 Meter)
        width_px = max(8.0, (firebreak_width_meters / self.pixel_to_meter))
        w_half = width_px / 2.0
        c1 = (int(p1_x - v_spread_x * w_half), int(p1_y - v_spread_y * w_half))
        c2 = (int(p2_x - v_spread_x * w_half), int(p2_y - v_spread_y * w_half))
        c3 = (int(p2_x + v_spread_x * w_half), int(p2_y + v_spread_y * w_half))
        c4 = (int(p1_x + v_spread_x * w_half), int(p1_y + v_spread_y * w_half))
        draw.polygon([c1, c2, c3, c4], fill=(245, 158, 11, 55), outline=(245, 158, 11, 160))

        # 6c. Draw High-Contrast Dashed Centerline
        num_segments = max(12, int(cut_length_meters / 4.0))
        for i in range(num_segments):
            if i % 2 == 0:
                t0 = i / num_segments
                t1 = (i + 1) / num_segments
                sx = int(p1_x + (p2_x - p1_x) * t0)
                sy = int(p1_y + (p2_y - p1_y) * t0)
                ex = int(p1_x + (p2_x - p1_x) * t1)
                ey = int(p1_y + (p2_y - p1_y) * t1)
                draw.line([(sx, sy), (ex, ey)], fill=(251, 191, 36, 255), width=4)

        # 6d. Draw Distance Tick Marks every 25 meters along the line
        num_ticks = int(cut_length_meters / 25.0)
        tick_len = 6.0
        for ti in range(1, num_ticks + 1):
            t_ratio = (ti * 25.0) / cut_length_meters
            if t_ratio < 0.95:
                tx = p1_x + (p2_x - p1_x) * t_ratio
                ty = p1_y + (p2_y - p1_y) * t_ratio
                t_k1 = (int(tx - v_spread_x * tick_len), int(ty - v_spread_y * tick_len))
                t_k2 = (int(tx + v_spread_x * tick_len), int(ty + v_spread_y * tick_len))
                draw.line([t_k1, t_k2], fill=(255, 255, 255, 240), width=2)
                draw.text((int(tx + 4), int(ty + 2)), f"{ti * 25}m", fill=(255, 255, 255, 210))

        # 6e. Draw Endpoints Beacon Circles with clear Indonesian text
        # Point A (Mulai - Emerald Green)
        draw.ellipse([int(p1_x - 8), int(p1_y - 8), int(p1_x + 8), int(p1_y + 8)], fill=(34, 197, 94, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((int(p1_x + 10), int(p1_y - 9)), "Mulai (A) 0m", fill=(34, 197, 94, 255))

        # Point B (Selesai - Crimson Red)
        draw.ellipse([int(p2_x - 8), int(p2_y - 8), int(p2_x + 8), int(p2_y + 8)], fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((int(p2_x + 10), int(p2_y - 9)), f"Selesai (B) {int(cut_length_meters)}m", fill=(239, 68, 68, 255))

        # Midpoint Tactical Marker
        mid_x = int((p1_x + p2_x) / 2)
        mid_y = int((p1_y + p2_y) / 2)
        draw.ellipse([mid_x - 5, mid_y - 5, mid_x + 5, mid_y + 5], fill=(56, 189, 248, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((mid_x - 70, mid_y - 24), "JALUR SEKAT PEMUTUS API", fill=(245, 158, 11, 245))
        draw.text((mid_x - 90, mid_y - 8), f"Babat: {int(cut_length_meters)}m x Lebar: {int(firebreak_width_meters)}m", fill=(255, 255, 255, 250))

        # 6f. Draw Tactical Recommendation HUD Card on Bottom-Left of Overlay
        card_w, card_h = 340, 74
        cx0, cy0 = 20, max(20, h - card_h - 20)
        cx1, cy1 = cx0 + card_w, cy0 + card_h
        draw.rectangle([cx0, cy0, cx1, cy1], fill=(15, 23, 42, 230), outline=(245, 158, 11, 240), width=2)
        draw.text((cx0 + 12, cy0 + 8), "REKOMENDASI SEKAT BAKAR PRESISI (AI-CV)", fill=(245, 158, 11, 255))
        draw.text((cx0 + 12, cy0 + 26), f"Panjang: {cut_length_meters}m  |  Lebar: {firebreak_width_meters}m  |  Buffer: {int(effective_buffer_m)}m", fill=(255, 255, 255, 245))
        draw.text((cx0 + 12, cy0 + 44), f"A: ({start_gps['latitude']}, {start_gps['longitude']})", fill=(34, 197, 94, 235))
        draw.text((cx0 + 12, cy0 + 58), f"B: ({end_gps['latitude']}, {end_gps['longitude']})", fill=(239, 68, 68, 235))

        # Draw Wind Vector Arrow at Top Right
        arrow_cx, arrow_cy = w - 90, 80
        arrow_len = 35
        ax1 = arrow_cx + int(v_spread_x * arrow_len)
        ay1 = arrow_cy + int(v_spread_y * arrow_len)
        draw.line([(arrow_cx, arrow_cy), (ax1, ay1)], fill=(14, 165, 233, 240), width=4)
        draw.ellipse([arrow_cx - 4, arrow_cy - 4, arrow_cx + 4, arrow_cy + 4], fill=(14, 165, 233, 255))
        if is_auto_wind:
            draw.text((w - 175, 14), "Angin: Deteksi AI Vision", fill=(34, 197, 94, 255))
        draw.text((w - 175, 30), f"Kecepatan: {wind_speed_kmh} km/j", fill=(255, 255, 255, 230))
        draw.text((w - 175, 46), f"Arah Datang: {wind_compass}", fill=(14, 165, 233, 255))

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
                "is_auto_detected": is_auto_wind,
            },
            "overlay_filename": overlay_filename,
            "overlay_url": f"/static/output/{overlay_filename}",
        }


# Singleton instance
firebreak_optimizer = FirebreakOptimizer()
