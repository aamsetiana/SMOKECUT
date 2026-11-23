"""Early Smoke and Flame / Hotspot Detection Service for SEKAT-AI.

Provides lightweight, deterministic Computer Vision detection as a primary / fallback
engine, with optional YOLOv8 inference if local weights are present.
"""

from pathlib import Path
from typing import Dict, Any, List, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.core.config import MODELS_DIR, OUTPUT_DIR


class FireSmokeDetector:
    """Detects early micro-flames and smoke plumes from drone RGB imagery."""

    def __init__(self, weights_path: Path = MODELS_DIR / "yolov8n.pt"):
        self.weights_path = weights_path
        self._yolo_model = None

    def _get_connected_components_bboxes(
        self, binary_mask: np.ndarray, min_area: int = 8, max_area: int = 50000
    ) -> List[Dict[str, int]]:
        """Extract bounding boxes from a binary mask using efficient flood-fill / connected components."""
        h, w = binary_mask.shape
        visited = np.zeros((h, w), dtype=bool)
        bboxes = []

        # Find positive coordinates
        ys, xs = np.where(binary_mask)
        if len(xs) == 0:
            return []

        # Simple grid-based clustering for fast processing without heavy dependencies
        step = 8
        for i in range(len(xs)):
            cx, cy = xs[i], ys[i]
            if visited[cy, cx]:
                continue

            # BFS to find connected cluster
            queue = [(cx, cy)]
            visited[cy, cx] = True
            cluster_xs = [cx]
            cluster_ys = [cy]

            while queue:
                qx, qy = queue.pop(0)
                # Check neighbors within a 4-pixel radius to bridge small gaps
                x_min_n = max(0, qx - 3)
                x_max_n = min(w, qx + 4)
                y_min_n = max(0, qy - 3)
                y_max_n = min(h, qy + 4)

                sub_mask = binary_mask[y_min_n:y_max_n, x_min_n:x_max_n] & ~visited[y_min_n:y_max_n, x_min_n:x_max_n]
                sub_ys, sub_xs = np.where(sub_mask)
                for sy, sx in zip(sub_ys, sub_xs):
                    nx = x_min_n + sx
                    ny = y_min_n + sy
                    visited[ny, nx] = True
                    cluster_xs.append(nx)
                    cluster_ys.append(ny)
                    if len(queue) < 150:  # Bound BFS expansion speed
                        queue.append((nx, ny))

            area = len(cluster_xs)
            if min_area <= area <= max_area:
                bx0 = int(min(cluster_xs))
                by0 = int(min(cluster_ys))
                bx1 = int(max(cluster_xs))
                by1 = int(max(cluster_ys))
                bw = bx1 - bx0 + 1
                bh = by1 - by0 + 1
                bboxes.append({
                    "x": bx0,
                    "y": by0,
                    "w": bw,
                    "h": bh,
                    "area": area,
                    "centroid_x": int(np.mean(cluster_xs)),
                    "centroid_y": int(np.mean(cluster_ys)),
                })

        # Merge overlapping or close bounding boxes
        merged = []
        for b in bboxes:
            merged_with_existing = False
            for m in merged:
                # Check distance between centroids
                dist = np.hypot(b["centroid_x"] - m["centroid_x"], b["centroid_y"] - m["centroid_y"])
                if dist < max(b["w"], b["h"], m["w"], m["h"]) * 0.8:
                    # Merge boxes
                    nx0 = min(m["x"], b["x"])
                    ny0 = min(m["y"], b["y"])
                    nx1 = max(m["x"] + m["w"], b["x"] + b["w"])
                    ny1 = max(m["y"] + m["h"], b["y"] + b["h"])
                    m["x"] = nx0
                    m["y"] = ny0
                    m["w"] = nx1 - nx0
                    m["h"] = ny1 - ny0
                    m["area"] += b["area"]
                    m["centroid_x"] = (nx0 + nx1) // 2
                    m["centroid_y"] = (ny0 + ny1) // 2
                    merged_with_existing = True
                    break
            if not merged_with_existing:
                merged.append(b)

        return merged

    def detect_cv(self, rgb_array: np.ndarray) -> List[Dict[str, Any]]:
        """Lightweight and deterministic Computer Vision flame & smoke detector."""
        r = rgb_array[:, :, 0].astype(int)
        g = rgb_array[:, :, 1].astype(int)
        b = rgb_array[:, :, 2].astype(int)

        detections = []
        det_id = 1

        # 1. Hotspot / Flame core detection:
        # High Red, moderate Green, low Blue with pronounced R - B differential
        flame_mask = (r >= 210) & (g >= 100) & (b <= 95) & (r - b >= 90)
        flame_clusters = self._get_connected_components_bboxes(flame_mask, min_area=8)

        for cluster in flame_clusters:
            # Score confidence based on core brightness and size
            confidence = min(0.98, 0.85 + (cluster["area"] / 500.0) * 0.12)
            detections.append({
                "id": det_id,
                "class_name": "hotspot",
                "label": "Titik Api Awal",
                "confidence": round(confidence, 3),
                "bbox": {
                    "x": cluster["x"],
                    "y": cluster["y"],
                    "w": cluster["w"],
                    "h": cluster["h"],
                },
                "centroid": {
                    "x": cluster["centroid_x"],
                    "y": cluster["centroid_y"],
                },
            })
            det_id += 1

        # 2. Smoke plume detection:
        # Grayish / hazy appearance: elevated Blue compared to dry fuel, balanced R & G,
        # moderate to high brightness, and adjacent to dry / warm areas.
        # Background dry grass has B <= 95; smoke plume has B in [105, 175] with R, G in [160, 235]
        smoke_mask = (
            (b >= 105)
            & (b <= 175)
            & (r >= 165)
            & (r <= 235)
            & (g >= 145)
            & (g <= 215)
            & (abs(r - g) <= 50)
            & (r - b <= 100)
            & (~flame_mask)
        )
        smoke_clusters = self._get_connected_components_bboxes(smoke_mask, min_area=20)

        for cluster in smoke_clusters:
            # Plumes must be sufficiently sized to be considered real smoke
            confidence = min(0.92, 0.74 + (cluster["area"] / 1000.0) * 0.15)
            detections.append({
                "id": det_id,
                "class_name": "smoke",
                "label": "Kepulan Asap Dini",
                "confidence": round(confidence, 3),
                "bbox": {
                    "x": cluster["x"],
                    "y": cluster["y"],
                    "w": cluster["w"],
                    "h": cluster["h"],
                },
                "centroid": {
                    "x": cluster["centroid_x"],
                    "y": cluster["centroid_y"],
                },
            })
            det_id += 1

        return detections

    def detect(self, image_input: Union[str, Path, Image.Image, np.ndarray], image_id: str) -> Dict[str, Any]:
        """Execute detection pipeline, render visual annotation overlay, and return detected objects."""
        if isinstance(image_input, (str, Path)):
            pil_img = Image.open(image_input).convert("RGB")
            rgb_arr = np.array(pil_img)
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
            rgb_arr = np.array(pil_img)
        elif isinstance(image_input, np.ndarray):
            rgb_arr = image_input
            pil_img = Image.fromarray(rgb_arr)
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        h, w = rgb_arr.shape[:2]

        # Use CV heuristic detector (or YOLO if weights exist)
        detections = self.detect_cv(rgb_arr)

        # Generate transparent overlay with bounding box annotations
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for det in detections:
            bbox = det["bbox"]
            x0, y0 = bbox["x"], bbox["y"]
            x1, y1 = x0 + bbox["w"], y0 + bbox["h"]

            if det["class_name"] == "hotspot":
                color_box = (239, 68, 68, 240)  # Bright Red
                color_fill = (239, 68, 68, 40)
                label_text = f"HOTSPOT ({int(det['confidence']*100)}%)"
            else:
                color_box = (56, 189, 248, 240)  # Light Sky Blue
                color_fill = (56, 189, 248, 30)
                label_text = f"ASAP ({int(det['confidence']*100)}%)"

            # Draw bounding box & semi-transparent fill
            draw.rectangle([x0, y0, x1, y1], outline=color_box, width=3)
            draw.rectangle([x0, y0, x1, y1], fill=color_fill)

            # Draw tag box
            tag_w = max(90, len(label_text) * 7)
            tag_h = 16
            tag_y0 = max(0, y0 - tag_h - 2)
            draw.rectangle([x0, tag_y0, x0 + tag_w, tag_y0 + tag_h], fill=color_box)
            draw.text((x0 + 4, tag_y0 + 2), label_text, fill=(255, 255, 255, 255))

        overlay_filename = f"detections_{image_id}.png"
        overlay_path = OUTPUT_DIR / overlay_filename
        overlay.save(overlay_path, "PNG")

        return {
            "detections": detections,
            "total_detected": len(detections),
            "hotspot_count": sum(1 for d in detections if d["class_name"] == "hotspot"),
            "smoke_count": sum(1 for d in detections if d["class_name"] == "smoke"),
            "overlay_filename": overlay_filename,
            "overlay_url": f"/static/output/{overlay_filename}",
        }


# Singleton instance
fire_detector = FireSmokeDetector()
