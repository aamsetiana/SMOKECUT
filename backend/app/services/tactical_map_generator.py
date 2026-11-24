"""Tactical Land Cover and Firebreak Mapping Engine for SMOKECUT.

Renders full geospatial operational maps integrating:
1. Fuel Bed Polygon Zoning (Dry flammable shrub contours and area in Ha/m2).
2. Organic Fire Perimeter & Smoke Hazard Dispersion Plumes (replaces crude bounding boxes).
3. Strategic Choke-Point Firebreak Cutting Corridor (3-5m swath, centerline, distance ticks).
4. Professional Cartographic Elements (Scale bar, Compass rose, GPS grid, and Tactical HUD).
"""

import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

from backend.app.core.config import OUTPUT_DIR


class TacticalMapGenerator:
    """Generates composite geospatial tactical maps for field operations."""

    def __init__(self, pixel_to_meter: float = 0.25):
        self.pixel_to_meter = pixel_to_meter
        self.base_lat = -0.22850
        self.base_lon = 101.55420

    def generate_tactical_map(
        self,
        base_image: Union[str, Path, Image.Image, np.ndarray],
        dry_mask: np.ndarray,
        detections: List[Dict[str, Any]],
        firebreak_plan: Dict[str, Any],
        image_id: str,
        vari_overlay: Union[str, Path, Image.Image, np.ndarray, None] = None,
    ) -> Dict[str, Any]:
        """Renders an all-in-one tactical land and firebreak operational map."""
        if isinstance(base_image, (str, Path)):
            pil_base = Image.open(base_image).convert("RGBA")
        elif isinstance(base_image, Image.Image):
            pil_base = base_image.convert("RGBA")
        elif isinstance(base_image, np.ndarray):
            pil_base = Image.fromarray(base_image).convert("RGBA")
        else:
            raise ValueError(f"Unsupported image type: {type(base_image)}")

        w, h = pil_base.size

        # Blend VARI heatmap onto base image so the tactical map shows the dry fuel land mapping
        vari_target = vari_overlay or (OUTPUT_DIR / f"vari_overlay_{image_id}.png")
        if vari_target is not None:
            try:
                pil_vari = None
                if isinstance(vari_target, (str, Path)) and Path(vari_target).exists():
                    pil_vari = Image.open(vari_target).convert("RGBA")
                elif isinstance(vari_target, Image.Image):
                    pil_vari = vari_target.convert("RGBA")
                elif isinstance(vari_target, np.ndarray):
                    pil_vari = Image.fromarray(vari_target).convert("RGBA")
                if pil_vari is not None:
                    if pil_vari.size != (w, h):
                        pil_vari = pil_vari.resize((w, h))
                    pil_base = Image.alpha_composite(pil_base, pil_vari)
            except Exception:
                pass

        # Create overlays:
        # 1. Full map overlay (contains all unified elements for standalone cartographic print map)
        map_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(map_overlay)

        # 2. Dedicated cartographic overlay for multi-layer dashboard view (scale, compass, HUD, fuel zone outlines)
        carto_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw_carto = ImageDraw.Draw(carto_overlay)

        # -------------------------------------------------------------
        # 1. Fuel Bed Polygon Contours (Zonasi Bahan Bakar Kering)
        # -------------------------------------------------------------
        fuel_zones_metadata = []
        if dry_mask is not None and np.sum(dry_mask) > 0:
            dry_u8 = (dry_mask.astype(np.uint8) * 255)
            # Smooth mask slightly to produce organic contours
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dry_closed = cv2.morphologyEx(dry_u8, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(dry_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            zone_idx = 1
            for cnt in contours:
                area_px = cv2.contourArea(cnt)
                if area_px < 600:  # Skip tiny speckles
                    continue

                area_m2 = area_px * (self.pixel_to_meter ** 2)
                area_ha = area_m2 / 10000.0

                # Approximate contour with smooth polygon
                epsilon = 0.015 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                poly_pts = [(int(pt[0][0]), int(pt[0][1])) for pt in approx]

                if len(poly_pts) >= 3:
                    # Draw clean vector fuel polygon with light fill
                    draw.polygon(poly_pts, fill=(239, 68, 68, 24), outline=(239, 68, 68, 180))
                    draw_carto.polygon(poly_pts, fill=(239, 68, 68, 16), outline=(239, 68, 68, 160))

                    # Compute polygon center for labeling
                    m = cv2.moments(cnt)
                    if m["m00"] > 0:
                        lbl_x = int(m["m10"] / m["m00"])
                        lbl_y = int(m["m01"] / m["m00"])
                        if 40 <= lbl_x <= w - 120 and 40 <= lbl_y <= h - 40:
                            label_str = f"ZONA BAHAN BAKAR #{zone_idx} ({area_ha:.2f} Ha)"
                            lbl_w = max(110, len(label_str) * 6 + 12)
                            draw.rectangle([lbl_x - lbl_w//2, lbl_y - 9, lbl_x + lbl_w//2, lbl_y + 9], fill=(15, 23, 42, 215), outline=(239, 68, 68, 180))
                            draw.text((lbl_x - lbl_w//2 + 6, lbl_y - 7), label_str, fill=(252, 165, 165, 240))

                            draw_carto.rectangle([lbl_x - lbl_w//2, lbl_y - 9, lbl_x + lbl_w//2, lbl_y + 9], fill=(15, 23, 42, 215), outline=(239, 68, 68, 180))
                            draw_carto.text((lbl_x - lbl_w//2 + 6, lbl_y - 7), label_str, fill=(252, 165, 165, 240))

                    fuel_zones_metadata.append({
                        "zone_id": zone_idx,
                        "area_m2": round(area_m2, 1),
                        "area_hectares": round(area_ha, 3),
                        "point_count": len(poly_pts),
                    })
                    zone_idx += 1

        # -------------------------------------------------------------
        # 2. Fire Contours & Smoke Hazard Dispersion Plumes (for Full Map)
        # -------------------------------------------------------------
        actual_hotspots = [d for d in detections if d.get("class_name") == "hotspot"]
        actual_smokes = [d for d in detections if d.get("class_name") == "smoke"]

        # 2a. Smoke dispersion hazard plumes
        labeled_smoke = False
        for s_item in actual_smokes:
            bbox = s_item["bbox"]
            sx0, sy0 = bbox["x"], bbox["y"]
            sx1, sy1 = sx0 + bbox["w"], sy0 + bbox["h"]
            draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=12, fill=(56, 189, 248, 25), outline=(56, 189, 248, 140), width=2)
            if not labeled_smoke:
                draw.text((sx0 + 6, max(6, sy0 - 14)), "💨 ZONA DISPERSI ASAP PM2.5", fill=(186, 230, 253, 240))
                labeled_smoke = True

        # 2b. Organic Fire Perimeters
        for h_item in actual_hotspots:
            bbox = h_item["bbox"]
            hx, hy = bbox["x"], bbox["y"]
            hw, hh = bbox["w"], bbox["h"]
            draw.ellipse([hx - 6, hy - 6, hx + hw + 6, hy + hh + 6], fill=(239, 68, 68, 45), outline=(239, 68, 68, 160), width=2)
            draw.ellipse([hx, hy, hx + hw, hy + hh], fill=(249, 115, 22, 180), outline=(255, 255, 255, 230), width=2)

        # Draw a single clean fire label at the center of fire front
        if actual_hotspots:
            avg_hx = int(sum(h["bbox"]["x"] + h["bbox"]["w"]//2 for h in actual_hotspots) / len(actual_hotspots))
            avg_hy = int(sum(h["bbox"]["y"] for h in actual_hotspots) / len(actual_hotspots))
            draw.text((avg_hx + 10, max(10, avg_hy - 14)), "🔥 INTI API AKTIF", fill=(254, 202, 202, 255))

        # -------------------------------------------------------------
        # 3. Firebreak Cutting Swath, Interception Vector, & Buffer
        # -------------------------------------------------------------
        traj = firebreak_plan.get("trajectory", {})
        metrics = firebreak_plan.get("metrics", {})
        wind_p = firebreak_plan.get("wind", {})

        p1 = traj.get("start_point", {"x": 50.0, "y": 50.0})
        p2 = traj.get("end_point", {"x": 200.0, "y": 200.0})
        anchor = traj.get("anchor_point", {"x": 125.0, "y": 125.0})
        threat = traj.get("threat_origin", {"x": 100.0, "y": 100.0})

        p1_x, p1_y = p1["x"], p1["y"]
        p2_x, p2_y = p2["x"], p2["y"]
        cx, cy = threat["x"], threat["y"]
        anchor_x, anchor_y = anchor["x"], anchor["y"]

        cut_len = metrics.get("cutting_length_meters", 100.0)
        rec_width = metrics.get("recommended_width_meters", 4.0)
        eff_buffer = metrics.get("effective_safety_buffer_meters", 35.0)

        # Spread and cut vectors
        wind_deg = wind_p.get("direction_degrees", 135.0)
        spread_deg = (wind_deg + 180.0) % 360.0
        spread_rad = math.radians(spread_deg)
        v_spread_x = math.sin(spread_rad)
        v_spread_y = -math.cos(spread_rad)

        # 3a. Safety Buffer Ring around fire
        buf_r_px = int(eff_buffer / self.pixel_to_meter)
        draw.ellipse(
            [int(cx - buf_r_px), int(cy - buf_r_px), int(cx + buf_r_px), int(cy + buf_r_px)],
            outline=(245, 158, 11, 130),
            width=2,
        )
        draw.text((int(cx - 65), int(cy + buf_r_px - 18)), f"Jarak Aman Tim: {int(eff_buffer)}m", fill=(245, 158, 11, 230))

        # 3b. Intercepted Spread Vector Arrow
        if math.hypot(anchor_x - cx, anchor_y - cy) >= 20.0:
            arr_tip_x = cx + v_spread_x * min(buf_r_px * 0.85, buf_r_px - 12.0)
            arr_tip_y = cy + v_spread_y * min(buf_r_px * 0.85, buf_r_px - 12.0)
            draw.line([(int(cx), int(cy)), (int(arr_tip_x), int(arr_tip_y))], fill=(239, 68, 68, 220), width=3)
            # Arrowhead
            head_len = 10.0
            v_cut_x, v_cut_y = -v_spread_y, v_spread_x
            h1_x = arr_tip_x - v_spread_x * head_len + v_cut_x * (head_len * 0.5)
            h1_y = arr_tip_y - v_spread_y * head_len + v_cut_y * (head_len * 0.5)
            h2_x = arr_tip_x - v_spread_x * head_len - v_cut_x * (head_len * 0.5)
            h2_y = arr_tip_y - v_spread_y * head_len - v_cut_y * (head_len * 0.5)
            draw.polygon([(int(arr_tip_x), int(arr_tip_y)), (int(h1_x), int(h1_y)), (int(h2_x), int(h2_y))], fill=(239, 68, 68, 240))
            draw.text((int((cx + arr_tip_x)/2 - 45), int((cy + arr_tip_y)/2 - 10)), "Rambatan Terblokir", fill=(255, 255, 255, 220))

        # 3c. Shaded Physical Cutting Swath (Zona Tebas Lebar 3-5m)
        width_px = max(8.0, rec_width / self.pixel_to_meter)
        w_half = width_px / 2.0
        c1 = (int(p1_x - v_spread_x * w_half), int(p1_y - v_spread_y * w_half))
        c2 = (int(p2_x - v_spread_x * w_half), int(p2_y - v_spread_y * w_half))
        c3 = (int(p2_x + v_spread_x * w_half), int(p2_y + v_spread_y * w_half))
        c4 = (int(p1_x + v_spread_x * w_half), int(p1_y + v_spread_y * w_half))
        draw.polygon([c1, c2, c3, c4], fill=(245, 158, 11, 70), outline=(245, 158, 11, 200))

        # 3d. Dashed Precision Centerline
        num_segments = max(12, int(cut_len / 4.0))
        for i in range(num_segments):
            if i % 2 == 0:
                t0 = i / num_segments
                t1 = (i + 1) / num_segments
                sx = int(p1_x + (p2_x - p1_x) * t0)
                sy = int(p1_y + (p2_y - p1_y) * t0)
                ex = int(p1_x + (p2_x - p1_x) * t1)
                ey = int(p1_y + (p2_y - p1_y) * t1)
                draw.line([(sx, sy), (ex, ey)], fill=(251, 191, 36, 255), width=4)

        # 3e. 25m Interval Distance Tick Marks
        num_ticks = int(cut_len / 25.0)
        tick_len = 7.0
        for ti in range(1, num_ticks + 1):
            t_ratio = (ti * 25.0) / cut_len
            if t_ratio < 0.95:
                tx = p1_x + (p2_x - p1_x) * t_ratio
                ty = p1_y + (p2_y - p1_y) * t_ratio
                t_k1 = (int(tx - v_spread_x * tick_len), int(ty - v_spread_y * tick_len))
                t_k2 = (int(tx + v_spread_x * tick_len), int(ty + v_spread_y * tick_len))
                draw.line([t_k1, t_k2], fill=(255, 255, 255, 240), width=2)
                draw.text((int(tx + 4), int(ty + 2)), f"{ti * 25}m", fill=(255, 255, 255, 220))

        # 3f. Waypoint Beacons (Point A: Mulai, Point B: Selesai)
        # Point A (Mulai - Green)
        draw.ellipse([int(p1_x - 9), int(p1_y - 9), int(p1_x + 9), int(p1_y + 9)], fill=(34, 197, 94, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((int(p1_x + 12), int(p1_y - 9)), "MULAI (A) 0m", fill=(34, 197, 94, 255))

        # Point B (Selesai - Red)
        draw.ellipse([int(p2_x - 9), int(p2_y - 9), int(p2_x + 9), int(p2_y + 9)], fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((int(p2_x + 12), int(p2_y - 9)), f"SELESAI (B) {int(cut_len)}m", fill=(239, 68, 68, 255))

        # Midpoint Marker
        mid_x = int((p1_x + p2_x) / 2)
        mid_y = int((p1_y + p2_y) / 2)
        draw.ellipse([mid_x - 5, mid_y - 5, mid_x + 5, mid_y + 5], fill=(56, 189, 248, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((mid_x - 85, mid_y - 26), "JALUR SEKAT PEMUTUS API (AI)", fill=(245, 158, 11, 245))
        draw.text((mid_x - 95, mid_y - 10), f"Babat: {int(cut_len)}m x Lebar: {int(rec_width)}m", fill=(255, 255, 255, 250))

        # -------------------------------------------------------------
        # 4. Cartography: Compass Rose, Scale Bar, Grid, & Legend
        # -------------------------------------------------------------
        # 4a. Geospatial Corner Crosshairs (draw on both print map and carto overlay)
        for crx, cry in [(30, 30), (w - 30, 30), (30, h - 30), (w - 30, h - 30)]:
            draw.line([(crx - 10, cry), (crx + 10, cry)], fill=(148, 163, 184, 180), width=1)
            draw.line([(crx, cry - 10), (crx, cry + 10)], fill=(148, 163, 184, 180), width=1)
            draw_carto.line([(crx - 10, cry), (crx + 10, cry)], fill=(148, 163, 184, 180), width=1)
            draw_carto.line([(crx, cry - 10), (crx, cry + 10)], fill=(148, 163, 184, 180), width=1)

        # 4b. Compass Rose at Top-Right
        rose_cx, rose_cy = w - 65, 65
        for d_ctx in [draw, draw_carto]:
            d_ctx.ellipse([rose_cx - 26, rose_cy - 26, rose_cx + 26, rose_cy + 26], fill=(15, 23, 42, 210), outline=(56, 189, 248, 220), width=2)
            d_ctx.polygon([(rose_cx, rose_cy - 22), (rose_cx - 5, rose_cy), (rose_cx, rose_cy - 4)], fill=(239, 68, 68, 255))
            d_ctx.polygon([(rose_cx, rose_cy - 22), (rose_cx + 5, rose_cy), (rose_cx, rose_cy - 4)], fill=(255, 255, 255, 255))
            d_ctx.polygon([(rose_cx, rose_cy + 22), (rose_cx - 5, rose_cy), (rose_cx, rose_cy + 4)], fill=(148, 163, 184, 255))
            d_ctx.polygon([(rose_cx, rose_cy + 22), (rose_cx + 5, rose_cy), (rose_cx, rose_cy + 4)], fill=(203, 213, 225, 255))
            d_ctx.text((rose_cx - 4, rose_cy - 36), "U", fill=(239, 68, 68, 255))
            d_ctx.text((rose_cx - 40, rose_cy + 30), f"Angin: {wind_p.get('speed_kmh', 14)} km/j", fill=(255, 255, 255, 220))
            d_ctx.text((rose_cx - 40, rose_cy + 44), f"Arah: {wind_p.get('direction_compass', 'Tenggara')}", fill=(56, 189, 248, 230))

        # 4c. Operational Scale Bar at Bottom-Right
        # 50 meters = 200 pixels at 0.25 m/pixel
        bar_w = 200
        bx0, by0 = w - bar_w - 30, h - 45
        for d_ctx in [draw, draw_carto]:
            d_ctx.rectangle([bx0 - 10, by0 - 18, bx0 + bar_w + 10, by0 + 20], fill=(15, 23, 42, 220), outline=(100, 116, 139, 180), width=1)
            d_ctx.line([(bx0, by0), (bx0 + bar_w, by0)], fill=(255, 255, 255, 255), width=3)
            d_ctx.line([(bx0, by0 - 5), (bx0, by0 + 5)], fill=(255, 255, 255, 255), width=2)
            d_ctx.line([(bx0 + bar_w//2, by0 - 5), (bx0 + bar_w//2, by0 + 5)], fill=(255, 255, 255, 255), width=2)
            d_ctx.line([(bx0 + bar_w, by0 - 5), (bx0 + bar_w, by0 + 5)], fill=(255, 255, 255, 255), width=2)
            d_ctx.text((bx0 - 3, by0 - 16), "0m", fill=(255, 255, 255, 230))
            d_ctx.text((bx0 + bar_w//2 - 10, by0 - 16), "25m", fill=(255, 255, 255, 230))
            d_ctx.text((bx0 + bar_w - 12, by0 - 16), "50m", fill=(255, 255, 255, 230))
            d_ctx.text((bx0 + bar_w//2 - 28, by0 + 5), "Skala Drone", fill=(148, 163, 184, 220))

        # 4d. Tactical HUD Card at Bottom-Left
        card_w, card_h = 360, 96
        hx0, hy0 = 25, max(20, h - card_h - 25)
        hx1, hy1 = hx0 + card_w, hy0 + card_h
        gps_s = firebreak_plan.get("gps_coordinates", {}).get("start", {})
        gps_e = firebreak_plan.get("gps_coordinates", {}).get("end", {})

        for d_ctx in [draw, draw_carto]:
            d_ctx.rectangle([hx0, hy0, hx1, hy1], fill=(15, 23, 42, 235), outline=(245, 158, 11, 240), width=2)
            d_ctx.text((hx0 + 12, hy0 + 8), "PETA TAKTIS PEMOTONGAN SEKAT LAHAN (SEKAT-AI)", fill=(245, 158, 11, 255))
            d_ctx.text((hx0 + 12, hy0 + 26), f"Target: Panjang {cut_len}m  |  Lebar {rec_width}m  |  Buffer {int(eff_buffer)}m", fill=(255, 255, 255, 250))
            d_ctx.text((hx0 + 12, hy0 + 44), f"Titik Awal  [A]: Lat {gps_s.get('latitude', -0.2285)}, Lon {gps_s.get('longitude', 101.5542)}", fill=(34, 197, 94, 240))
            d_ctx.text((hx0 + 12, hy0 + 60), f"Titik Akhir [B]: Lat {gps_e.get('latitude', -0.2295)}, Lon {gps_e.get('longitude', 101.5562)}", fill=(239, 68, 68, 240))
            d_ctx.text((hx0 + 12, hy0 + 76), f"Estimasi: ~{metrics.get('estimated_clearing_hours', 4.1)} Jam (Regu 5 Orang)  |  Lindungi: {metrics.get('protected_area_hectares', 1.95)} Ha", fill=(148, 163, 184, 230))

        # Composite base image with tactical overlay
        composite_map = Image.alpha_composite(pil_base, map_overlay)

        # Save both full tactical map and standalone transparent overlay
        tactical_map_filename = f"tactical_map_{image_id}.png"
        tactical_map_path = OUTPUT_DIR / tactical_map_filename
        composite_map.convert("RGB").save(tactical_map_path, "PNG")

        tactical_overlay_filename = f"tactical_overlay_{image_id}.png"
        tactical_overlay_path = OUTPUT_DIR / tactical_overlay_filename
        carto_overlay.save(tactical_overlay_path, "PNG")

        return {
            "tactical_map_filename": tactical_map_filename,
            "tactical_map_url": f"/static/output/{tactical_map_filename}",
            "tactical_overlay_filename": tactical_overlay_filename,
            "tactical_overlay_url": f"/static/output/{tactical_overlay_filename}",
            "fuel_zones": fuel_zones_metadata,
            "total_fuel_zones": len(fuel_zones_metadata),
        }


# Singleton instance
tactical_map_generator = TacticalMapGenerator()
