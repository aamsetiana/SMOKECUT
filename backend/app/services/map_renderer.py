"""Shared drawing primitives for SEKAT-AI overlays, maps, and annotated video."""

import math
from typing import Any, Dict, List, Sequence, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

Point = Tuple[float, float]
Box = Tuple[int, int, int, int]

FIRE = (255, 72, 36)
SMOKE = (125, 211, 252)
BREAK = (255, 214, 10)
DARK = (15, 23, 42)
WHITE = (255, 255, 255)


def ui_scale(size: Tuple[int, int]) -> float:
    """Scale factor for strokes and text, relative to a 1280 px frame."""
    return max(0.5, max(size) / 1280.0)


def draw_tag(
    draw: ImageDraw.ImageDraw,
    size: Tuple[int, int],
    anchor: Point,
    text: str,
    color: Tuple[int, int, int],
    occupied: List[Box],
) -> None:
    """Draw a label near ``anchor``, skipping positions that hit other labels."""
    s = ui_scale(size)
    font = ImageFont.load_default(size=max(10, int(15 * s)))
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    pad, gap = int(6 * s), int(16 * s)
    bw, bh = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    ax, ay = anchor
    if not (0 <= ax < size[0] and 0 <= ay < size[1]):
        return
    candidates = [
        (ax - bw / 2, ay + gap),
        (ax - bw / 2, ay - bh - gap),
        (ax + gap, ay - bh / 2),
        (ax - bw - gap, ay - bh / 2),
    ]
    for cx, cy in candidates:
        bx = int(max(4, min(size[0] - bw - 4, cx)))
        by = int(max(4, min(size[1] - bh - 4, cy)))
        box = (bx, by, int(bx + bw), int(by + bh))
        if any(box[0] < o[2] and o[0] < box[2] and box[1] < o[3] and o[1] < box[3] for o in occupied):
            continue
        draw.rounded_rectangle(
            box, radius=int(5 * s), fill=DARK + (225,), outline=color + (255,), width=max(1, int(1.5 * s))
        )
        draw.text((bx + pad - x0, by + pad - y0), text, font=font, fill=WHITE + (255,))
        occupied.append(box)
        return


def draw_detections(
    img: Image.Image,
    detections: Sequence[Dict[str, Any]],
    occupied: List[Box],
    show_tags: bool = True,
) -> None:
    """Outline the real fire perimeter and the main smoke area (no boxes)."""
    draw = ImageDraw.Draw(img, "RGBA")
    s = ui_scale(img.size)
    smokes = [d for d in detections if d["class_name"] == "smoke"]
    fires = [d for d in detections if d["class_name"] == "hotspot"]

    for det in smokes:
        pts = [tuple(p) for p in det["contour"]]
        if len(pts) >= 3:
            draw.line(pts + [pts[0]], fill=SMOKE + (150,), width=max(1, int(1.5 * s)))
    for det in fires:
        pts = [tuple(p) for p in det["contour"]]
        if len(pts) >= 3:
            draw.polygon(pts, fill=FIRE + (60,))
            draw.line(pts + [pts[0]], fill=FIRE + (255,), width=max(2, int(2.5 * s)))

    if not show_tags:
        return
    for i, det in enumerate(fires[:3], start=1):
        b = det["bbox"]
        draw_tag(draw, img.size, (b["x"] + b["w"] / 2, b["y"]), f"API {i}", FIRE, occupied)
    if smokes:
        c = smokes[0]["centroid"]
        draw_tag(draw, img.size, (c["x"], c["y"]), "ASAP", SMOKE, occupied)


def _point_at(poly: Sequence[Point], dist: float) -> Point:
    """Return the position ``dist`` pixels along a polyline."""
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg > 0 and dist <= seg:
            return x0 + (x1 - x0) * dist / seg, y0 + (y1 - y0) * dist / seg
        dist -= seg
    return poly[-1]


def draw_firebreak(
    img: Image.Image,
    polyline: Sequence[Point],
    threat: Point,
    length_m: float,
    width_m: float,
    band_px: float,
    occupied: List[Box],
) -> None:
    """Draw the recommended cutting corridor with A/B markers and one label."""
    poly = [(float(x), float(y)) for x, y in polyline]
    if len(poly) < 2:
        return
    draw = ImageDraw.Draw(img, "RGBA")
    s = ui_scale(img.size)
    band = int(max(10 * s, band_px))
    draw.line(poly, fill=(0, 0, 0, 255), width=band + int(4 * s), joint="curve")
    draw.line(poly, fill=BREAK + (255,), width=band, joint="curve")

    total = sum(math.dist(a, b) for a, b in zip(poly, poly[1:]))
    dash, pos = 16 * s, 0.0
    while pos < total:
        draw.line(
            [_point_at(poly, pos), _point_at(poly, min(total, pos + dash))],
            fill=(40, 30, 0, 255), width=max(2, int(2.5 * s)),
        )
        pos += 2 * dash

    # Spread arrow: from the nearest fire edge towards the line.
    mid = _point_at(poly, total / 2)
    norm = math.dist(mid, threat)
    if norm > 45 * s:
        ux, uy = (mid[0] - threat[0]) / norm, (mid[1] - threat[1]) / norm
        tip = (mid[0] - ux * (band / 2 + 6 * s), mid[1] - uy * (band / 2 + 6 * s))
        base = (tip[0] - ux * 12 * s, tip[1] - uy * 12 * s)
        start = (threat[0] + ux * 10 * s, threat[1] + uy * 10 * s)
        draw.line([start, base], fill=FIRE + (255,), width=max(2, int(3 * s)))
        k = 7 * s
        draw.polygon(
            [tip, (base[0] - uy * k, base[1] + ux * k), (base[0] + uy * k, base[1] - ux * k)], fill=FIRE + (255,)
        )

    r = 13 * s
    font = ImageFont.load_default(size=max(10, int(16 * s)))
    for (x, y), name, color in ((poly[0], "A", (22, 163, 74)), (poly[-1], "B", (220, 38, 38))):
        draw.ellipse(
            [x - r, y - r, x + r, y + r], fill=color + (255,), outline=WHITE + (255,), width=max(2, int(2 * s))
        )
        draw.text((x, y), name, font=font, fill=WHITE + (255,), anchor="mm")
        occupied.append((int(x - r), int(y - r), int(x + r), int(y + r)))
    label = f"SEKAT BAKAR ±{length_m:.0f} m x {width_m:g} m"
    draw_tag(draw, img.size, _point_at(poly, total * 0.3), label, BREAK, occupied)


def transform_points(points: Sequence[Point], matrix: np.ndarray) -> List[Point]:
    """Apply a 3x3 perspective transform to a list of points."""
    arr = np.asarray(points, dtype=np.float64).reshape(-1, 1, 2)
    return [(float(p[0]), float(p[1])) for p in cv2.perspectiveTransform(arr, matrix).reshape(-1, 2)]
