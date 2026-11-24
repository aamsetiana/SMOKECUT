"""Tactical Land Cover and Firebreak Mapping Engine for SEKAT-AI.

Composes the printable operational map and the transparent cartographic overlay
(compass, scale bar, HUD) shown on top of the dashboard viewer.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.core.config import OUTPUT_DIR
from backend.app.services.map_renderer import BREAK, DARK, WHITE, Box, draw_detections, draw_firebreak, ui_scale


class TacticalMapGenerator:
    """Generates composite geospatial tactical maps for field operations."""

    @staticmethod
    def _fuel_zones(dry_mask: np.ndarray, mpp: Optional[float]) -> List[Dict[str, Any]]:
        """List contiguous dry-fuel zones covering at least 0.2% of the frame."""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        closed = cv2.morphologyEx(dry_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        zones: List[Dict[str, Any]] = []
        for cnt in sorted(contours, key=cv2.contourArea, reverse=True):
            area_px = cv2.contourArea(cnt)
            if area_px < 0.002 * dry_mask.size:
                break
            area_m2 = area_px * mpp ** 2 if mpp else None
            zones.append({
                "zone_id": len(zones) + 1,
                "area_m2": round(area_m2, 1) if mpp else None,
                "area_hectares": round(area_m2 / 10000.0, 3) if mpp else None,
                "point_count": len(cv2.approxPolyDP(cnt, 0.015 * cv2.arcLength(cnt, True), True)),
            })
        return zones

    @staticmethod
    def _draw_cartography(img: Image.Image, plan: Dict[str, Any]) -> List[Box]:
        """Draw HUD, wind compass, and scale bar; return the boxes they occupy."""
        draw = ImageDraw.Draw(img, "RGBA")
        w, h = img.size
        s = ui_scale(img.size)
        font = ImageFont.load_default(size=max(9, int(14 * s)))
        metrics, wind = plan["metrics"], plan["wind_parameters"]
        line_h, pad, edge = int(20 * s), int(10 * s), int(16 * s)
        radius, stroke = int(6 * s), max(1, int(2 * s))
        panel = DARK + (205,)

        # HUD (top-left: usually sky/smoke, away from the fire front and cutting line)
        length, safe = metrics["cutting_length_meters"], metrics["effective_safety_buffer_meters"]
        rows = [
            ("REKOMENDASI SEKAT BAKAR", BREAK),
            (f"Lebar {metrics['recommended_width_meters']:g} m (Permen LHK 28/2021)", WHITE),
            (f"Panjang {'≥ ' if plan['is_partial'] else ''}{length:g} m" if length else "Panjang: perlu skala", WHITE),
            (f"Jarak aman {safe:g} m dari api" if safe else "Jarak aman: perlu tinggi vegetasi", WHITE),
        ]
        if not plan["is_to_scale"]:
            rows.append(("Posisi garis: ilustrasi, bukan skala", (253, 164, 175)))
        hud_w = int(max(draw.textlength(text, font=font) for text, _ in rows)) + 2 * pad
        hud = (edge, edge, edge + hud_w, edge + line_h * len(rows) + 2 * pad)
        draw.rounded_rectangle(hud, radius=radius, fill=panel, outline=BREAK + (255,), width=stroke)
        for i, (text, color) in enumerate(rows):
            draw.text((edge + pad, edge + pad + i * line_h), text, font=font, fill=color + (255,))

        # Wind compass: the arrow shows where the wind blows to (image-up = north)
        box = None
        if wind["direction_degrees"] is not None:
            speed = f" {wind['speed_kmh']:g} km/j" if wind["speed_kmh"] else ""
            text = f"Angin{speed} dari {wind['direction_compass']}" + (" (perkiraan)" if wind["is_auto_detected"] else "")
            tw, r = int(draw.textlength(text, font=font)), int(24 * s)
            box = (w - tw - 2 * pad - edge, edge, w - edge, edge + 2 * r + line_h + 2 * pad)
            draw.rounded_rectangle(box, radius=radius, fill=panel)
            center = np.array([(box[0] + box[2]) / 2, edge + pad + r])
            draw.ellipse([*(center - r), *(center + r)], outline=WHITE + (200,), width=stroke)
            angle = np.radians(wind["direction_degrees"] + 180.0)
            u = np.array([np.sin(angle), -np.cos(angle)])
            n = np.array([-u[1], u[0]])
            arrow = [center + u * r * 0.8, center - u * r * 0.6 + n * r * 0.45, center - u * r * 0.6 - n * r * 0.45]
            draw.polygon([(float(x), float(y)) for x, y in arrow], fill=(56, 189, 248, 255))
            draw.text((box[0] + pad, box[3] - line_h - pad // 2), text, font=font, fill=WHITE + (255,))

        if not plan["is_to_scale"]:
            return [hud] + ([box] if box else [])
        # Scale bar: 25 m (bottom-right)
        bar = 25.0 / plan["meters_per_pixel"]
        sb = (int(w - bar - 2 * pad - edge), int(h - edge - 2 * line_h), w - edge, h - edge)
        draw.rounded_rectangle(sb, radius=radius, fill=panel)
        draw.line([(sb[0] + pad, sb[3] - pad), (sb[2] - pad, sb[3] - pad)], fill=WHITE + (255,), width=stroke + 1)
        draw.text(((sb[0] + sb[2]) / 2, sb[1] + pad), "25 m", font=font, fill=WHITE + (255,), anchor="mm")
        return [b for b in (hud, box, sb) if b]

    def generate_tactical_map(
        self,
        base_image: Union[str, Path, Image.Image, np.ndarray],
        dry_mask: np.ndarray,
        detections: List[Dict[str, Any]],
        firebreak_plan: Dict[str, Any],
        image_id: str,
        vari_overlay: Union[str, Path, Image.Image, None] = None,
    ) -> Dict[str, Any]:
        """Render the printable map and the standalone cartographic overlay."""
        if isinstance(base_image, np.ndarray):
            base = Image.fromarray(base_image).convert("RGBA")
        elif isinstance(base_image, Image.Image):
            base = base_image.convert("RGBA")
        else:
            base = Image.open(base_image).convert("RGBA")
        if vari_overlay is not None:
            vari = vari_overlay if isinstance(vari_overlay, Image.Image) else Image.open(vari_overlay)
            base = Image.alpha_composite(base, vari.convert("RGBA").resize(base.size))

        metrics, traj = firebreak_plan["metrics"], firebreak_plan["trajectory"]
        mpp, origin = firebreak_plan["meters_per_pixel"], traj["threat_origin"]
        zones = self._fuel_zones(dry_mask, mpp)

        composite = base.convert("RGB")
        occupied = self._draw_cartography(composite, firebreak_plan)
        draw_detections(composite, detections, occupied, show_tags=False)
        if traj["polyline"]:
            draw_firebreak(
                composite, [(p["x"], p["y"]) for p in traj["polyline"]], (origin["x"], origin["y"]),
                metrics["cutting_length_meters"], metrics["recommended_width_meters"],
                firebreak_plan["band_px"], occupied,
            )
        draw_detections(composite, [{**d, "contour": []} for d in detections], occupied)
        carto = Image.new("RGBA", base.size, (0, 0, 0, 0))
        self._draw_cartography(carto, firebreak_plan)

        map_name = f"tactical_map_{image_id}.png"
        overlay_name = f"tactical_overlay_{image_id}.png"
        composite.save(OUTPUT_DIR / map_name, "PNG", compress_level=1)
        carto.save(OUTPUT_DIR / overlay_name, "PNG", compress_level=1)
        return {
            "tactical_map_filename": map_name,
            "tactical_map_url": f"/static/output/{map_name}",
            "tactical_overlay_filename": overlay_name,
            "tactical_overlay_url": f"/static/output/{overlay_name}",
            "fuel_zones": zones,
            "total_fuel_zones": len(zones),
        }


# Singleton instance
tactical_map_generator = TacticalMapGenerator()
