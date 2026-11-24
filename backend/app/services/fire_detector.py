"""Early Smoke and Flame / Hotspot Detection Service for SEKAT-AI.

Lightweight, deterministic computer-vision detection based on colour and texture.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
from PIL import Image

from backend.app.core.config import OUTPUT_DIR
from backend.app.services.map_renderer import draw_detections, draw_firebreak, transform_points

MAX_ANNOTATED_SECONDS = 60


@dataclass
class SceneMasks:
    """Boolean per-pixel scene classes of one frame."""

    fire: np.ndarray
    smoke: np.ndarray
    fuel: np.ndarray  # Unburnt, unobscured vegetation/soil that fire can reach


def flame_mask(rgb: np.ndarray) -> np.ndarray:
    """Pixels with flame colour (bright, saturated red-orange to yellow)."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, (3, 105, 222), (32, 255, 255)) > 0
    ys, xs = np.nonzero(mask)
    r, g, b = rgb[ys, xs].astype(np.int16).T
    mask[ys, xs] = (g >= 85) & (r - b >= 90) & (r >= g)
    return mask


def ground_mask(rgb: np.ndarray) -> np.ndarray:
    """Coloured (unburnt, smoke-free) land, as an 8-bit mask for feature tracking."""
    return cv2.inRange(cv2.cvtColor(cv2.blur(rgb, (9, 9)), cv2.COLOR_RGB2HSV), (0, 55, 20), (179, 255, 255))


def segment_scene(rgb: np.ndarray) -> SceneMasks:
    """Split a frame into flame, smoke/haze, and unburnt fuel.

    Smoke, sky, ash and asphalt are nearly colourless, while vegetation and dry
    shrubs keep colour saturation. Smoke is additionally bright and untextured.
    """
    h, w = rgb.shape[:2]
    sigma = max(0.8, 5.0 * max(h, w) / 1280.0)
    fire = flame_mask(rgb)
    blurred = cv2.cvtColor(cv2.GaussianBlur(rgb, (0, 0), sigma), cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    mean = cv2.GaussianBlur(gray, (0, 0), sigma)
    std = np.sqrt(np.maximum(cv2.GaussianBlur(gray * gray, (0, 0), sigma) - mean * mean, 0))
    colourless = blurred[..., 1] < 55
    smoke = colourless & (blurred[..., 2] > 125) & (std < 13)
    fuel = ~colourless & (blurred[..., 2] > 20) & ~fire
    return SceneMasks(fire=fire, smoke=smoke, fuel=fuel)


class FireSmokeDetector:
    """Detects fire fronts and smoke areas from drone RGB imagery."""

    @staticmethod
    def _regions(mask: np.ndarray, link_px: int, min_area: int, open_px: int = 0) -> List[Dict[str, Any]]:
        """Group nearby mask pixels into regions, sorted by area (largest first)."""
        # Work on the occupied part only; flames usually cover a small area.
        ox, oy, cw, ch = cv2.boundingRect(mask.astype(np.uint8))
        if cw == 0:
            return []
        work = mask[oy:oy + ch, ox:ox + cw].astype(np.uint8)
        if open_px > 1:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_px, open_px))
            work = cv2.morphologyEx(work, cv2.MORPH_OPEN, kernel)
        size = max(3, link_px | 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        # Pad so closing is not cut off at the image border.
        padded = cv2.copyMakeBorder(work, size, size, size, size, cv2.BORDER_CONSTANT)
        closed = cv2.morphologyEx(padded, cv2.MORPH_CLOSE, kernel)[size:-size, size:-size].copy()
        _, labels, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
        areas = np.bincount(labels.ravel(), weights=work.ravel())
        regions = []
        for i in np.argsort(-areas):
            if i == 0 or areas[i] < min_area:
                continue
            x, y, bw, bh = (int(v) for v in stats[i][:4])
            local = (labels[y:y + bh, x:x + bw] == i).astype(np.uint8)
            radius = float(cv2.distanceTransform(np.pad(local, 1), cv2.DIST_L2, 5).max())
            ys, xs = np.nonzero(local & work[y:y + bh, x:x + bw])
            contours, _ = cv2.findContours(local, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE, offset=(x + ox, y + oy))
            contour = max(contours, key=cv2.contourArea)
            contour = cv2.approxPolyDP(contour, 0.0015 * max(mask.shape), True)
            regions.append({
                "area": int(areas[i]),
                "compactness": radius / float(np.sqrt(areas[i])),
                "bbox": {"x": x + ox, "y": y + oy, "w": bw, "h": bh},
                "centroid": {"x": int(xs.mean()) + x + ox, "y": int(ys.mean()) + y + oy},
                "contour": contour.reshape(-1, 2).tolist(),
            })
        return regions

    def detect_cv(self, rgb_array: np.ndarray, masks: Optional[SceneMasks] = None) -> List[Dict[str, Any]]:
        """Deterministic detector returning one entry per fire front / smoke area."""
        masks = masks or segment_scene(rgb_array)
        h, w = rgb_array.shape[:2]
        s = max(h, w) / 1280.0
        detections: List[Dict[str, Any]] = []

        def add(region: Dict[str, Any], class_name: str, label: str, confidence: float) -> None:
            detections.append({
                "id": len(detections) + 1,
                "class_name": class_name,
                "label": label,
                "confidence": round(confidence, 3),
                "bbox": region["bbox"],
                "centroid": region["centroid"],
                "area_px": region["area"],
                "contour": region["contour"],
            })

        for reg in self._regions(masks.fire, int(22 * s), max(8, int(40 * s * s))):
            is_front = max(reg["bbox"]["w"], reg["bbox"]["h"]) > 0.08 * max(h, w)
            label = "Garis Api Aktif" if is_front else "Titik Api Awal"
            add(reg, "hotspot", label, min(0.98, 0.85 + reg["area"] / (4000.0 * s * s) * 0.12))
        smokes = self._regions(masks.smoke, int(25 * s), max(60, int(0.01 * h * w)), open_px=int(15 * s))
        # Roads and canals are grey too, but long and thin
        for reg in [r for r in smokes if r["compactness"] >= 0.12][:3]:
            add(reg, "smoke", "Area Asap", min(0.92, 0.74 + reg["area"] / (h * w) * 0.5))
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

        masks = segment_scene(rgb_arr)
        detections = self.detect_cv(rgb_arr, masks)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw_detections(overlay, detections, [])

        overlay_filename = f"detections_{image_id}.png"
        overlay_path = OUTPUT_DIR / overlay_filename
        overlay.save(overlay_path, "PNG", compress_level=1)

        return {
            "detections": detections,
            "masks": masks,
            "total_detected": len(detections),
            "hotspot_count": sum(1 for d in detections if d["class_name"] == "hotspot"),
            "smoke_count": sum(1 for d in detections if d["class_name"] == "smoke"),
            "overlay_filename": overlay_filename,
            "overlay_url": f"/static/output/{overlay_filename}",
        }

    @staticmethod
    def select_keyframe(video_path: Path, samples: int = 12) -> Optional[int]:
        """Return the index of a sharp frame showing much fire, away from the edge."""
        cap = cv2.VideoCapture(str(video_path))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        best, best_score = None, -1.0
        for idx in sorted({int(i) for i in np.linspace(0, max(0, total - 1) * 0.95, samples)}):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok:
                continue
            k = 640.0 / max(frame.shape[:2])
            small = cv2.resize(frame, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            sharp = cv2.Laplacian(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), cv2.CV_32F).var()
            fire = flame_mask(small[:, :, ::-1].copy())
            rows = np.nonzero(fire.any(axis=1))[0]
            # Fire at the bottom edge leaves no room to draw the firebreak.
            room = 1.0 if rows.size == 0 else min(1.0, 0.2 + 4.0 * (1 - rows[-1] / fire.shape[0]))
            score = (1.0 + float(fire.sum())) * room * float(np.sqrt(sharp))
            if score > best_score:
                best, best_score = idx, score
        cap.release()
        return best

    @staticmethod
    def _frame_motions(video_path: Path, max_frames: int) -> List[np.ndarray]:
        """Cumulative transforms mapping frame 0 to each frame (camera motion)."""
        cap = cv2.VideoCapture(str(video_path))
        motions: List[np.ndarray] = []
        prev = None
        while len(motions) < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            k = 640.0 / max(frame.shape[:2])
            small = cv2.resize(frame, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            step = np.eye(3)
            if prev is not None:
                # Only track ground features: smoke and flames move on their own.
                pts = cv2.goodFeaturesToTrack(prev[0], 500, 0.01, 6, mask=prev[1])
                if pts is not None and len(pts) >= 12:
                    nxt, status, _ = cv2.calcOpticalFlowPyrLK(prev[0], gray, pts, None, winSize=(25, 25), maxLevel=4)
                    good = status.ravel() == 1
                    if good.sum() >= 12:
                        found, _ = cv2.findHomography(pts[good], nxt[good], cv2.RANSAC, 2.0)
                        step = found if found is not None else step
            # Express the step in full-resolution pixels.
            scale = np.diag([k, k, 1.0])
            step = np.linalg.inv(scale) @ step @ scale
            motions.append(step @ motions[-1] if motions else step)
            prev = (gray, ground_mask(small[:, :, ::-1].copy()))
        cap.release()
        return motions

    def annotate_video(
        self,
        input_video_path: Path,
        output_video_path: Path,
        firebreak: Optional[Dict[str, Any]] = None,
        keyframe: int = 0,
        keyframe_width: Optional[int] = None,
    ) -> Path:
        """Burn fire outlines and a ground-locked firebreak into the video.

        The firebreak is planned once on ``keyframe`` and then follows the ground
        using the estimated camera motion, so it does not drift while panning.
        """
        cap = cv2.VideoCapture(str(input_video_path))
        if not cap.isOpened():
            return input_video_path
        fps = cap.get(cv2.CAP_PROP_FPS) or 10.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        max_frames = int(fps * MAX_ANNOTATED_SECONDS)

        motions: List[np.ndarray] = []
        line: List[Any] = []
        to_start = np.eye(3)
        if firebreak:
            motions = self._frame_motions(input_video_path, max_frames)
            ratio = w / float(keyframe_width or w)
            traj = firebreak["trajectory"]
            points = traj["polyline"] + [traj["threat_origin"]]
            line = [(p["x"] * ratio, p["y"] * ratio) for p in points]
            metrics = firebreak["metrics"]
            band = metrics["recommended_width_meters"] / firebreak["meters_per_pixel"] * ratio
            if motions:
                to_start = np.linalg.inv(motions[min(keyframe, len(motions) - 1)])

        temp_raw = output_video_path.parent / f"temp_{output_video_path.name}"
        out = cv2.VideoWriter(str(temp_raw), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        for idx in range(max_frames):
            ok, frame = cap.read()
            if not ok:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            empty = np.zeros((h, w), dtype=bool)  # Only fire is outlined per frame
            fires = self.detect_cv(rgb, SceneMasks(fire=flame_mask(rgb), smoke=empty, fuel=empty))
            occupied: List[Any] = []
            draw_detections(img, fires, occupied, show_tags=False)
            if line and idx < len(motions):
                moved = transform_points(line, motions[idx] @ to_start)
                if all(abs(x) < 4 * w and abs(y) < 4 * h for x, y in moved):
                    draw_firebreak(
                        img, moved[:-1], moved[-1], metrics["cutting_length_meters"],
                        metrics["recommended_width_meters"], band, occupied,
                    )
            draw_detections(img, [{**d, "contour": []} for d in fires[:1]], occupied)
            out.write(cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR))
        cap.release()
        out.release()

        # Transcode to web-compatible H.264; keep the raw file if ffmpeg is missing.
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(temp_raw), "-c:v", "libx264", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output_video_path),
                ],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120, check=True,
            )
            temp_raw.unlink(missing_ok=True)
        except (OSError, subprocess.SubprocessError):
            temp_raw.replace(output_video_path)
        return output_video_path


# Singleton instance
fire_detector = FireSmokeDetector()
