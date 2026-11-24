"""Firebreak Route Optimizer Service for SEKAT-AI.

Places the cutting line (sekat bakar) ahead of the fire. Widths and safe distances come
from ``core.standards``; metric results are only reported when the real scale is known.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

from backend.app.core import standards
from backend.app.core.config import OUTPUT_DIR
from backend.app.services.map_renderer import draw_firebreak
from backend.app.services.weather_service import parse_wind_direction, degrees_to_compass

# Drawing offset (fraction of the longest side) when no real distance is available.
# It is an illustration only and is always reported as "not to scale".
ILLUSTRATION_OFFSET = 0.055


class FirebreakOptimizer:
    """Optimizes firebreak trajectory, safety buffers, and clearing logistics."""

    @staticmethod
    def _front_arc(
        fire_mask: np.ndarray,
        fuel_mask: np.ndarray,
        buffer_px: float,
        spread: Optional[Tuple[float, float]],
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
        # (closing via distance transforms: cost does not grow with the radius)
        grown = (cv2.distanceTransform(1 - fire, cv2.DIST_L2, 5) <= d / 2.0).astype(np.uint8)
        front = ((cv2.distanceTransform(grown, cv2.DIST_L2, 5) > d / 2.0) | (fire > 0)).astype(np.uint8)
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
        if spread is not None and in_fuel.mean() > 0.75:
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

    @staticmethod
    def _fire_mask_from(hotspots: List[Dict[str, Any]], shape: Tuple[int, int]) -> np.ndarray:
        """Rasterise detections when no pixel mask is available."""
        mask = np.zeros(shape, dtype=np.uint8)
        for item in hotspots:
            c = item["centroid"]
            cv2.circle(mask, (int(c["x"]), int(c["y"])), 3, 1, -1)
        return mask.astype(bool)

    @staticmethod
    def _preventive_line(dry_mask: np.ndarray, spread: Tuple[float, float]) -> List[List[float]]:
        """Line across the dry-fuel centre, perpendicular to the wind, until fuel or frame ends."""
        h, w = dry_mask.shape
        ys, xs = np.nonzero(dry_mask)
        # Snap to the closest dry pixel: the centre of mass may fall in a gap.
        near = int(np.argmin((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2))
        x0, y0 = float(xs[near]), float(ys[near])
        closed = cv2.morphologyEx(dry_mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        ends = []
        for sign in (-1, 1):
            x, y = x0, y0
            while True:
                nx, ny = x - sign * spread[1] * 2, y + sign * spread[0] * 2
                if not (4 <= nx < w - 4 and 4 <= ny < h - 4) or not closed[int(ny), int(nx)]:
                    break
                x, y = nx, ny
            ends.append([x, y])
        return ends

    def optimize(
        self,
        image_dimensions: Dict[str, int],
        dry_mask: Optional[np.ndarray],
        hotspots: List[Dict[str, Any]],
        wind_direction: Union[str, float, None] = None,
        wind_speed_kmh: Optional[float] = None,
        safety_buffer_meters: Optional[float] = None,
        firebreak_width_meters: Optional[float] = None,
        image_id: str = "default",
        is_auto_wind: bool = False,
        fire_mask: Optional[np.ndarray] = None,
        fuel_mask: Optional[np.ndarray] = None,
        fuel_height_m: Optional[float] = None,
        protected_plant_height_m: Optional[float] = None,
        slope_wind_factor: Optional[float] = None,
        geo: Optional[Dict[str, Optional[float]]] = None,
    ) -> Dict[str, Any]:
        """Compute the firebreak line, its standard dimensions, and the overlay.

        ``safety_buffer_meters`` and ``firebreak_width_meters`` are operator values; they
        can only increase the standard, never go below it.
        """
        w, h = image_dimensions["width"], image_dimensions["height"]
        longest = max(w, h)
        geo = geo or {}
        ground_width = geo.get("ground_width_m")
        mpp = ground_width / longest if ground_width else None
        warnings: List[str] = []

        # 1. Dimensions from published standards
        width_m = standards.firebreak_width_m(protected_plant_height_m)
        if firebreak_width_meters and firebreak_width_meters > width_m:
            width_m = float(firebreak_width_meters)
        elif firebreak_width_meters and firebreak_width_meters < width_m:
            warnings.append(
                f"Lebar {firebreak_width_meters:g} m di bawah standar; dipakai {width_m:g} m (Permen LHK 28/2021)."
            )
        if not protected_plant_height_m:
            warnings.append("Tinggi tanaman yang dilindungi belum diisi; lebar memakai batas minimum 20 m.")

        ssd = standards.safe_separation_m(fuel_height_m, slope_wind_factor)
        safe_m = max(v for v in (ssd, safety_buffer_meters, 0.0) if v is not None) or None
        if ssd is None:
            warnings.append("Tinggi vegetasi yang terbakar belum diisi; jarak aman standar tidak dapat dihitung.")
        elif not slope_wind_factor:
            warnings.append("Faktor angin-lereng belum diisi; jarak aman hanya berlaku di lahan datar tanpa angin.")
        if mpp is None:
            warnings.append("Skala tidak diketahui; panjang, luas, dan GPS tidak dihitung. Posisi garis hanya ilustrasi.")

        # 2. Wind (blows FROM wind_deg, pushes fire TO the opposite side)
        wind_deg = None if wind_direction is None else parse_wind_direction(wind_direction)
        spread = None
        if wind_deg is not None:
            rad = math.radians(wind_deg + 180.0)
            spread = (math.sin(rad), -math.cos(rad))

        # 3. Line ahead of the visible fire front, otherwise a preventive line
        fires = [d for d in hotspots if d.get("class_name") == "hotspot"]
        if fire_mask is None:
            fire_mask = self._fire_mask_from(fires, (h, w))
        if fuel_mask is None:
            fuel_mask = dry_mask if dry_mask is not None else np.ones((h, w), dtype=bool)
        has_fire = bool(fire_mask.any())
        polyline: List[List[float]] = []
        threat: Optional[Dict[str, Any]] = None
        anchor: Optional[Tuple[float, float]] = None
        to_scale = is_partial = False
        if has_fire:
            arc, outside = None, 0.0
            if mpp and safe_m:
                offset = (safe_m + width_m / 2.0) / mpp  # Near edge of the line at the safe distance
                if offset < longest:
                    arc, outside = self._front_arc(fire_mask, fuel_mask, offset, spread)
                to_scale = arc is not None and len(arc) >= 10
                if not to_scale:
                    warnings.append(
                        f"Jarak aman {safe_m:g} m berada di luar frame. Posisi garis hanya ilustrasi; "
                        "ambil gambar lebih tinggi/lebar."
                    )
                elif outside > 0:
                    is_partial = True
                    warnings.append("Sebagian sekat di luar frame: panjang dan luas hanya untuk bagian yang terlihat. "
                        "Ambil gambar lebih tinggi/lebar.")
            if not to_scale:
                offset = ILLUSTRATION_OFFSET * longest
                while True:
                    arc, outside = self._front_arc(fire_mask, fuel_mask, offset, spread)
                    if outside == 0 or offset < 0.02 * longest:
                        break
                    offset *= 0.95
            if arc is not None and len(arc) >= 10:
                polyline = [[float(x), float(y)] for x, y in self._smooth(arc, int(offset * 0.5))]
                anchor = (float(arc[len(arc) // 2][0]), float(arc[len(arc) // 2][1]))
                ys, xs = np.nonzero(fire_mask)
                near = int(np.argmin((xs - anchor[0]) ** 2 + (ys - anchor[1]) ** 2))
                threat = {"x": float(xs[near]), "y": float(ys[near]), "type": "Titik Api Aktif"}
            else:
                warnings.append("Bahan bakar di depan api tidak terlihat; jalur tidak dapat ditentukan.")
        elif dry_mask is not None and dry_mask.any() and spread is not None:
            polyline = self._preventive_line(dry_mask, spread)
            (ax, ay), (bx, by) = polyline
            anchor = ((ax + bx) / 2, (ay + by) / 2)
            threat = {"x": anchor[0], "y": anchor[1], "type": "Zona Semak Kering (Patroli Preventif)"}
            to_scale = mpp is not None
        else:
            warnings.append("Tidak ada api terlihat dan arah angin belum diisi; jalur tidak dapat ditentukan.")

        if len(polyline) < 2:
            polyline = []
        elif polyline[0][0] > polyline[-1][0]:
            polyline.reverse()

        # 4. Metric results, only with a real scale
        length_m = area_ha = None
        gps: Dict[str, Optional[Dict[str, float]]] = {"start": None, "end": None}
        if polyline and to_scale:
            length_m = round(sum(math.dist(a, b) for a, b in zip(polyline, polyline[1:])) * mpp, 1)
            if has_fire:
                dist = cv2.distanceTransform(1 - fire_mask.astype(np.uint8), cv2.DIST_L2, 5)
                protected = fuel_mask & (dist > offset)
            else:
                protected = dry_mask
            area_ha = round(float(protected.sum()) * mpp ** 2 / 10000.0, 2)
            gps = {
                "start": self._to_gps(polyline[0], (w, h), mpp, geo),
                "end": self._to_gps(polyline[-1], (w, h), mpp, geo),
            }

        # 5. Overlay
        band_px = width_m / mpp if to_scale else None
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if polyline:
            draw_firebreak(overlay, polyline, (threat["x"], threat["y"]), length_m, width_m, band_px, [])
        overlay_filename = f"firebreak_overlay_{image_id}.png"
        overlay.save(OUTPUT_DIR / overlay_filename, "PNG", compress_level=1)

        def point(p: Any) -> Optional[Dict[str, float]]:
            return {"x": round(p[0], 1), "y": round(p[1], 1)} if p else None

        return {
            "trajectory": {
                "polyline": [point(p) for p in polyline],
                "start_point": point(polyline[0]) if polyline else None,
                "end_point": point(polyline[-1]) if polyline else None,
                "anchor_point": point(anchor),
                "threat_origin": threat,
            },
            "meters_per_pixel": mpp,
            "is_to_scale": to_scale,
            "is_partial": is_partial,
            "band_px": band_px,
            "warnings": warnings,
            "standards": standards.describe(),
            "metrics": {
                "cutting_length_meters": length_m,
                "recommended_width_meters": width_m,
                "effective_safety_buffer_meters": safe_m,
                # No published clearing rate for MPA crews on a 20 m belt: not estimated
                "estimated_clearing_hours": None,
                "protected_area_hectares": area_ha,
                "recommended_team_size": None,
            },
            "gps_coordinates": gps,
            "wind_parameters": {
                "direction_degrees": wind_deg,
                "direction_compass": None if wind_deg is None else degrees_to_compass(wind_deg),
                "speed_kmh": wind_speed_kmh,
                "is_auto_detected": is_auto_wind,
            },
            "overlay_filename": overlay_filename,
            "overlay_url": f"/static/output/{overlay_filename}",
        }

    @staticmethod
    def _to_gps(
        p: List[float], size: Tuple[int, int], mpp: float, geo: Dict[str, Optional[float]]
    ) -> Optional[Dict[str, float]]:
        """Convert a pixel to GPS using the photo centre and the bearing of image-up."""
        lat, lon, heading = geo.get("latitude"), geo.get("longitude"), geo.get("heading_deg")
        if lat is None or lon is None or heading is None:
            return None
        right, up = (p[0] - size[0] / 2) * mpp, (size[1] / 2 - p[1]) * mpp
        a = math.radians(heading)
        north, east = up * math.cos(a) - right * math.sin(a), up * math.sin(a) + right * math.cos(a)
        return {
            "latitude": round(lat + north / 111320.0, 6),
            "longitude": round(lon + east / (111320.0 * math.cos(math.radians(lat))), 6),
        }


# Singleton instance
firebreak_optimizer = FirebreakOptimizer()
