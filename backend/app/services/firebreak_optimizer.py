"""Firebreak Route Optimizer Service for SEKAT-AI.

Calculates the shortest and safest cutting line (sekat bakar) to block fire progression
ahead of dry fuel zones, incorporating wind vector dynamics and safety buffers for MPA teams.
"""

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

from backend.app.core.config import (
    DEFAULT_FIREBREAK_WIDTH_METERS,
    DEFAULT_SAFETY_BUFFER_METERS,
    OUTPUT_DIR,
)
from backend.app.services.map_renderer import draw_firebreak
from backend.app.services.weather_service import parse_wind_direction, degrees_to_compass


MIN_BUFFER_METERS = 15.0


class FirebreakOptimizer:
    """Optimizes firebreak trajectory, safety buffers, and clearing logistics."""

    def __init__(self, footprint_meters: float = 320.0):
        """Args:

        footprint_meters: Assumed ground length covered by the longest image side
            (0.25 m/px at 1280 px). Keeps results independent of image resolution.
        """
        self.footprint_meters = footprint_meters
        # Baseline reference coordinate for GPS simulation (Riau / Sumatra pilot site)
        self.base_lat = -0.22850
        self.base_lon = 101.55420

    def meters_per_pixel(self, width: int, height: int) -> float:
        """Approximate ground sampling distance for an image size."""
        return self.footprint_meters / max(width, height)

    @staticmethod
    def _front_arc(
        fire_mask: np.ndarray,
        fuel_mask: np.ndarray,
        buffer_px: float,
        spread: Tuple[float, float],
    ) -> Tuple[Optional[np.ndarray], float]:
        """Trace the line ``buffer_px`` ahead of the fire that lies in unburnt fuel.

        Returns the arc points (N, 2), or None, and the fraction of the arc that
        falls outside the frame.
        """
        h, w = fire_mask.shape
        d = int(math.ceil(buffer_px))
        pad = 2 * d + 4
        fire = cv2.copyMakeBorder(fire_mask.astype(np.uint8), pad, pad, pad, pad, cv2.BORDER_CONSTANT)
        # Bridge notches in the front so the cutting line stays short and walkable.
        size = max(3, d | 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        front = cv2.morphologyEx(fire, cv2.MORPH_CLOSE, kernel)
        dist = cv2.distanceTransform(1 - front, cv2.DIST_L2, 5)
        _, labels = cv2.connectedComponents((dist <= buffer_px).astype(np.uint8))
        main = int(np.argmax(np.bincount(labels[fire > 0])))
        contours, _ = cv2.findContours((labels == main).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        loop = max(contours, key=len).reshape(-1, 2) - pad
        n = len(loop)

        margin = max(4, int(0.012 * max(h, w)))
        x, y = loop[:, 0], loop[:, 1]
        inside = (x >= margin) & (x < w - margin) & (y >= margin) & (y < h - margin)
        in_fuel = fuel_mask[np.clip(y, 0, h - 1), np.clip(x, 0, w - 1)]
        if in_fuel.mean() > 0.75:
            # Fuel on every side: only the side the wind pushes the fire to matters.
            ys, xs = np.nonzero((labels[pad:-pad, pad:-pad] == main) & fire_mask)
            rel = loop - np.array([xs.mean(), ys.mean()])
            cosine = (rel @ np.array(spread)) / np.maximum(1e-6, np.linalg.norm(rel, axis=1))
            in_fuel = in_fuel & (cosine > math.cos(math.radians(75)))
        if not in_fuel.any():
            return None, 0.0
        outside = float((in_fuel & ~inside).sum()) / float(in_fuel.sum())

        # Close small gaps, then take the longest run on the circular loop.
        gap = max(3, int(buffer_px * 0.8)) | 1
        runs = np.tile(in_fuel & inside, 3).astype(np.uint8).reshape(1, -1)
        runs = cv2.morphologyEx(runs, cv2.MORPH_CLOSE, np.ones((1, gap), np.uint8)).ravel()
        closed = runs[n:2 * n].astype(bool) & inside
        if closed.all():
            return loop, outside
        first_gap = int(np.argmin(closed))
        rolled = np.roll(closed, -first_gap).astype(np.int8)
        edges = np.diff(np.concatenate([[0], rolled, [0]]))
        starts, ends = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]
        if len(starts) == 0:
            return None, outside
        k = int(np.argmax(ends - starts))
        return np.roll(loop, -first_gap, axis=0)[starts[k]:ends[k]], outside

    @staticmethod
    def _smooth(arc: np.ndarray, window: int) -> np.ndarray:
        """Moving-average smoothing, reduced to few vertices."""
        half = min(window, len(arc) - 1) // 2
        pts = np.pad(arc.astype(np.float64), ((half, half), (0, 0)), mode="edge")
        kernel = np.ones(2 * half + 1) / (2 * half + 1)
        pts = np.stack([np.convolve(pts[:, i], kernel, mode="valid") for i in (0, 1)], axis=1)
        return cv2.approxPolyDP(pts.astype(np.float32).reshape(-1, 1, 2), 2.5, False).reshape(-1, 2)

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
        fire_mask: Optional[np.ndarray] = None,
        fuel_mask: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """Compute the optimal firebreak trajectory, metrics, and visualization overlay."""
        w = image_dimensions["width"]
        h = image_dimensions["height"]
        mpp = self.meters_per_pixel(w, h)
        warnings: List[str] = []

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
        buffer_pixels = effective_buffer_m / mpp

        # 3. Follow the actual fire front when one is visible
        polyline: List[List[float]] = []
        has_fire = fire_mask is not None and fuel_mask is not None and bool(fire_mask.any())
        if has_fire:
            target_m = effective_buffer_m
            while True:
                arc, outside = self._front_arc(
                    fire_mask, fuel_mask, effective_buffer_m / mpp, (v_spread_x, v_spread_y)
                )
                if outside == 0 or effective_buffer_m <= MIN_BUFFER_METERS:
                    break
                effective_buffer_m = round(max(MIN_BUFFER_METERS, effective_buffer_m - 2.5), 1)
            if effective_buffer_m < target_m:
                warnings.append(
                    f"Jarak aman ideal {target_m:g} m tidak muat di frame, sekat digambar pada "
                    f"{effective_buffer_m:g} m. Ambil gambar lebih tinggi/lebar."
                )
            if outside > 0:
                warnings.append("Sebagian sekat berada di luar frame. Ambil gambar lebih tinggi/lebar.")
            buffer_pixels = effective_buffer_m / mpp
            if arc is not None and len(arc) >= 10:
                polyline = [[float(x), float(y)] for x, y in self._smooth(arc, int(buffer_pixels * 0.5))]

        if len(polyline) >= 2:
            if polyline[0][0] > polyline[-1][0]:
                polyline.reverse()
            anchor_x, anchor_y = (float(v) for v in arc[len(arc) // 2])
            ys, xs = np.nonzero(fire_mask)
            near = int(np.argmin((xs - anchor_x) ** 2 + (ys - anchor_y) ** 2))
            cx, cy = float(xs[near]), float(ys[near])
        else:
            if has_fire:
                warnings.append("Bahan bakar di depan api tidak terlihat jelas; jalur memakai arah angin saja.")
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
            polyline = [[p1_x, p1_y], [p2_x, p2_y]]

        (p1_x, p1_y), (p2_x, p2_y) = polyline[0], polyline[-1]

        # 5. Calculate physical metrics
        pixel_length = sum(math.dist(a, b) for a, b in zip(polyline, polyline[1:]))
        cut_length_meters = round(pixel_length * mpp, 1)

        # Standard manual babat clearing rate: ~25 meters/hour for 5-person MPA crew
        estimated_hours = round(cut_length_meters / 25.0, 1)

        # Protected area estimate (hectares)
        if has_fire:
            # Unburnt fuel beyond the buffer, i.e. what the line keeps from burning
            dist = cv2.distanceTransform(1 - fire_mask.astype(np.uint8), cv2.DIST_L2, 5)
            dry_area_pixels = float(np.sum(fuel_mask & (dist > buffer_pixels)))
        else:
            dry_area_pixels = float(np.sum(dry_mask)) if dry_mask is not None else (w * h * 0.4)
        protected_hectares = round((dry_area_pixels * (mpp ** 2)) / 10000.0, 2)

        # GPS Coordinates calculation (Start and End Points)
        # 1 degree latitude ~= 111,320m; 1 degree longitude ~= 111,320m * cos(lat)
        m_per_lat = 111320.0
        m_per_lon = 111320.0 * math.cos(math.radians(self.base_lat))

        start_gps = {
            "latitude": round(self.base_lat + ((h/2 - p1_y) * mpp) / m_per_lat, 6),
            "longitude": round(self.base_lon + ((p1_x - w/2) * mpp) / m_per_lon, 6),
        }
        end_gps = {
            "latitude": round(self.base_lat + ((h/2 - p2_y) * mpp) / m_per_lat, 6),
            "longitude": round(self.base_lon + ((p2_x - w/2) * mpp) / m_per_lon, 6),
        }

        # 6. Generate Firebreak Visual Overlay (RGBA)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw_firebreak(
            overlay, polyline, (cx, cy), cut_length_meters, firebreak_width_meters, firebreak_width_meters / mpp, []
        )

        # Save Overlay Image
        overlay_filename = f"firebreak_overlay_{image_id}.png"
        overlay_path = OUTPUT_DIR / overlay_filename
        overlay.save(overlay_path, "PNG", compress_level=1)

        return {
            "trajectory": {
                "polyline": [{"x": round(x, 1), "y": round(y, 1)} for x, y in polyline],
                "start_point": {"x": round(p1_x, 1), "y": round(p1_y, 1)},
                "end_point": {"x": round(p2_x, 1), "y": round(p2_y, 1)},
                "anchor_point": {"x": round(anchor_x, 1), "y": round(anchor_y, 1)},
                "threat_origin": {"x": round(cx, 1), "y": round(cy, 1), "type": threat_type},
            },
            "meters_per_pixel": mpp,
            "warnings": warnings,
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
