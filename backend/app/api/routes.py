"""REST API Routes for SEKAT-AI Core Engine."""

import hashlib
import json
import re
import uuid
import shutil
from pathlib import Path
from typing import Union, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
import cv2
import numpy as np
from PIL import Image, ImageOps

from backend.app.core.config import UPLOADS_DIR, SAMPLES_DIR, OUTPUT_DIR
from backend.app.services.geo_metadata import read_drone_metadata
from backend.app.services.vari_analyzer import vari_analyzer
from backend.app.services.fire_detector import fire_detector
from backend.app.services.firebreak_optimizer import firebreak_optimizer
from backend.app.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/api", tags=["Analysis & Dispatch"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi"}

MAX_WORK_SIDE = 1280  # Analysis resolution: keeps results and speed resolution-independent


def extract_keyframe(video_path: Path, frame_path: Path) -> Optional[int]:
    """Save the most informative video frame, resized for analysis; return its index."""
    idx = fire_detector.select_keyframe(video_path)
    if idx is None:
        return None
    cap = cv2.VideoCapture(str(video_path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return None
    scale = MAX_WORK_SIDE / max(frame.shape[:2])
    if scale < 1:
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    frame_path.with_suffix(".json").write_text(json.dumps({"keyframe": idx}))
    return idx


def prepare_image(source: Path, image_id: str) -> Path:
    """Return an upright copy limited to MAX_WORK_SIDE, or the source if already fine."""
    with Image.open(source) as img:
        rotated = img.getexif().get(0x0112, 1) != 1
        if max(img.size) <= MAX_WORK_SIDE and not rotated:
            return source
        work = ImageOps.exif_transpose(img).convert("RGB")
    work.thumbnail((MAX_WORK_SIDE, MAX_WORK_SIDE), Image.LANCZOS)
    path = UPLOADS_DIR / f"{image_id}_work.jpg"
    work.save(path, "JPEG", quality=95)
    return path


def fire_region_mask(detections: list, flames: np.ndarray) -> np.ndarray:
    """Accepted fire regions plus small flames close to them, without distant noise."""
    mask = np.zeros(flames.shape, dtype=np.uint8)
    for det in detections:
        if det["class_name"] == "hotspot":
            cv2.fillPoly(mask, [np.array(det["contour"], dtype=np.int32)], 1)
    radius = max(1, int(0.05 * max(flames.shape)))
    near = cv2.distanceTransform(1 - mask, cv2.DIST_L2, 5) <= radius if mask.any() else np.zeros_like(flames)
    return mask.astype(bool) | (flames & near)


class AnalyzeRequest(BaseModel):
    image_id: str = Field(..., description="Unique ID of previously uploaded image or 'sample'")
    wind_direction: Optional[Union[str, float]] = Field(default=None, description="Wind direction in degrees (0-360), compass string, or None/'auto' for automatic visual detection")
    wind_speed: Optional[float] = Field(default=None, description="Wind velocity in km/h or None for automatic visual estimation")
    safety_buffer: Optional[float] = Field(default=None, description="Base safety buffer in meters or None for automatic AI estimation")
    firebreak_width: Optional[float] = Field(default=None, description="Operator width in meters; never below the Permen LHK 28/2021 standard")
    fuel_height_m: Optional[float] = Field(default=None, gt=0, le=80, description="Height of the burning vegetation (m)")
    protected_plant_height_m: Optional[float] = Field(default=None, gt=0, le=80, description="Height of the outermost protected plants (m)")
    slope_wind_factor: Optional[float] = Field(default=None, ge=1, le=10, description="Slope-wind factor of the USFS safe separation rule")
    ground_width_m: Optional[float] = Field(default=None, gt=0, description="Ground length covered by the longest image side (m)")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude of the image centre")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude of the image centre")
    heading_deg: Optional[float] = Field(default=None, description="Compass bearing of image-up (degrees)")


class DispatchRequest(BaseModel):
    analysis_data: Optional[Dict[str, Any]] = None
    image_id: Optional[str] = None


@router.post("/upload", summary="Upload drone image or video file")
async def upload_media(file: UploadFile = File(...)):
    """Receives and validates drone visual capture files (.jpg, .png, .mp4)."""
    filename = file.filename or "upload.jpg"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_IMAGE_EXTENSIONS and ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format file '{ext}' tidak didukung. Harap unggah foto (.jpg, .png) atau video (.mp4).",
        )

    image_id = uuid.uuid4().hex[:12]
    saved_filename = f"{image_id}{ext}"
    dest_path = UPLOADS_DIR / saved_filename

    # Save to disk
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    width, height = 800, 600
    media_type = "image"
    preview_url = f"/static/uploads/{saved_filename}"

    if ext in ALLOWED_IMAGE_EXTENSIONS:
        try:
            with Image.open(dest_path) as img:
                width, height = img.size
        except Exception:
            pass
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        media_type = "video"
        # Transcode or repackage to web-compatible H.264 MP4 for smooth browser playback
        web_mp4 = UPLOADS_DIR / f"{image_id}_web.mp4"
        try:
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(dest_path), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(web_mp4)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=20,
            )
        except Exception:
            pass

        try:
            frame_path = UPLOADS_DIR / f"{image_id}_frame.jpg"
            if extract_keyframe(dest_path, frame_path) is not None:
                with Image.open(frame_path) as img:
                    width, height = img.size
                preview_url = f"/static/uploads/{frame_path.name}"
        except cv2.error:
            pass

    return {
        "status": "success",
        "image_id": image_id,
        "filename": filename,
        "saved_as": saved_filename,
        "preview_url": preview_url,
        "media_type": media_type,
        "dimensions": {"width": width, "height": height},
    }


@router.post("/analyze", summary="Execute 3-Layer AI Drone-Vision analysis")
async def analyze_aerial_image(request: AnalyzeRequest):
    """Executes full analysis pipeline:

    1. VARI Vegetation Index & Flammability Fuel Map.
    2. Early Smoke and Micro-Flame Detection.
    3. Firebreak Route Optimizer & Safety Buffer Calculation.
    """
    image_id = request.image_id
    target_path = None

    # Check for specific uploaded file or sample shortcuts
    if image_id == "sample_video":
        sample_vid = SAMPLES_DIR / "sample_drone_fire.mp4"
        if sample_vid.exists():
            target_path = sample_vid
            image_id = "sample_drone_fire"
    elif image_id not in ("sample", "sample_aerial"):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", image_id):
            raise HTTPException(status_code=404, detail="File citra tidak ditemukan.")
        matching = list(UPLOADS_DIR.glob(f"{image_id}.*"))
        if not matching:
            # Never answer with another site's firebreak plan
            raise HTTPException(status_code=404, detail="File citra tidak ditemukan. Unggah ulang foto/video.")
        target_path = matching[0]

    if target_path is None or not target_path.exists():
        sample_path = SAMPLES_DIR / "sample_aerial.jpg"
        if sample_path.exists():
            target_path = sample_path
            image_id = "sample_aerial"
        else:
            raise HTTPException(status_code=404, detail="File citra tidak ditemukan.")

    # Determine analysis frame source (if video, use extracted keyframe)
    analysis_image_path = target_path
    if target_path.suffix.lower() in ALLOWED_VIDEO_EXTENSIONS:
        extracted = UPLOADS_DIR / f"{image_id}_frame.jpg"
        meta = extracted.with_suffix(".json")
        if not (extracted.exists() and meta.exists()):
            if extract_keyframe(target_path, extracted) is None:
                raise HTTPException(status_code=400, detail="Video tidak dapat dibaca.")
        keyframe = json.loads(meta.read_text())["keyframe"]
        analysis_image_path = extracted
    else:
        analysis_image_path = prepare_image(target_path, image_id)

    # 1. Smoke & Hotspot Detection (also tells which pixels are unburnt land)
    fire_res = fire_detector.detect(analysis_image_path, image_id=image_id)
    masks = fire_res["masks"]

    # 2. VARI Flammability Fuel Mapping on unburnt land only
    vari_res = vari_analyzer.analyze_image(analysis_image_path, image_id=image_id, valid_mask=masks.fuel)
    dimensions = vari_res["dimensions"]
    if fire_res["hotspot_count"] > 0 and vari_res["statistics"]["risk_level"] != "TINGGI":
        vari_res["statistics"]["risk_level"] = "TINGGI"
        vari_res["statistics"]["risk_description"] = "Api aktif terdeteksi. Segera buat sekat bakar di depan garis api."

    # Resolve Wind Parameters (Auto-detection via Vision if unknown or not specified)
    from backend.app.services.weather_service import estimate_wind_from_vision, parse_wind_direction

    wind_dir = request.wind_direction
    wind_spd = request.wind_speed
    wind_estimation = None

    is_dir_auto = parse_wind_direction(wind_dir) is None
    is_spd_auto = wind_spd is None or wind_spd <= 0

    if is_dir_auto or is_spd_auto:
        wind_est = estimate_wind_from_vision(
            detections=fire_res["detections"],
            dry_mask=vari_res["dry_mask"],
        )
        if is_dir_auto:
            wind_dir = wind_est["direction_degrees"]
        if is_spd_auto:
            wind_spd = wind_est["speed_kmh"]
        wind_estimation = wind_est

    # Real scale and position: operator input wins over drone metadata
    geo = read_drone_metadata(target_path)
    for name in geo:
        if getattr(request, name) is not None:
            geo[name] = getattr(request, name)

    # 3. Firebreak Route Optimizer
    firebreak_res = firebreak_optimizer.optimize(
        image_dimensions=dimensions,
        dry_mask=vari_res["dry_mask"],
        hotspots=fire_res["detections"],
        wind_direction=wind_dir,
        wind_speed_kmh=wind_spd,
        safety_buffer_meters=request.safety_buffer,
        firebreak_width_meters=request.firebreak_width,
        fuel_height_m=request.fuel_height_m,
        protected_plant_height_m=request.protected_plant_height_m,
        slope_wind_factor=request.slope_wind_factor,
        geo=geo,
        image_id=image_id,
        is_auto_wind=is_dir_auto,
        fire_mask=fire_region_mask(fire_res["detections"], masks.fire),
        fuel_mask=masks.fuel,
    )

    if request.ground_width_m:
        firebreak_res["warnings"].append("Skala dari isian operator; hanya akurat bila kamera tegak lurus ke bawah.")

    # 4. Integrated Tactical Land Cover & Firebreak Operational Map
    from backend.app.services.tactical_map_generator import tactical_map_generator
    tactical_map_res = tactical_map_generator.generate_tactical_map(
        base_image=analysis_image_path,
        dry_mask=vari_res["dry_mask"],
        detections=fire_res["detections"],
        firebreak_plan=firebreak_res,
        image_id=image_id,
        vari_overlay=OUTPUT_DIR / vari_res["overlay_filename"],
    )

    # Prepare preview URL for base original image/frame and dynamic video
    video_url = None
    detection_overlay_url = fire_res["overlay_url"]
    firebreak_overlay_url = firebreak_res["overlay_url"]
    vari_overlay_url = vari_res["overlay_url"]

    if target_path.suffix.lower() in ALLOWED_VIDEO_EXTENSIONS:
        original_url = f"/static/uploads/{image_id}_frame.jpg"
        # The plan depends on the parameters, so it is part of the cached file name
        key = json.dumps([firebreak_res["trajectory"], firebreak_res["metrics"], keyframe], sort_keys=True)
        digest = hashlib.sha1(key.encode()).hexdigest()[:8]
        annotated_video = UPLOADS_DIR / f"{image_id}_annotated_{digest}.mp4"
        if not annotated_video.exists():
            fire_detector.annotate_video(
                target_path, annotated_video, firebreak_res, keyframe, dimensions["width"]
            )
        video_url = f"/static/uploads/{(annotated_video if annotated_video.exists() else target_path).name}"

        # Ground-anchored layers are burned into the moving video; static copies would drift
        empty_overlay_name = f"empty_overlay_{image_id}.png"
        Image.new("RGBA", (dimensions["width"], dimensions["height"]), (0, 0, 0, 0)).save(
            OUTPUT_DIR / empty_overlay_name, "PNG"
        )
        detection_overlay_url = firebreak_overlay_url = vari_overlay_url = f"/static/output/{empty_overlay_name}"
    elif target_path == SAMPLES_DIR / "sample_aerial.jpg":
        # Copy to output/uploads directory so it's accessible via HTTP static
        static_sample = UPLOADS_DIR / "sample_aerial.jpg"
        if not static_sample.exists():
            shutil.copy(target_path, static_sample)
        original_url = "/static/uploads/sample_aerial.jpg"
    else:
        original_url = f"/static/uploads/{analysis_image_path.name}"

    metrics, wind = firebreak_res["metrics"], firebreak_res["wind_parameters"]
    mpp = firebreak_res["meters_per_pixel"]
    dry_hectares = round(float(vari_res["dry_mask"].sum()) * mpp ** 2 / 10000.0, 2) if mpp else None
    length_text = f" sepanjang {metrics['cutting_length_meters']:g} m" if metrics["cutting_length_meters"] else ""
    wind_speed_text = f" ({wind['speed_kmh']:g} km/jam)" if wind["speed_kmh"] else ""

    # Compile comprehensive analysis response
    response_payload = {
        "status": "success",
        "image_id": image_id,
        "media_type": "video" if video_url else "image",
        "video_url": video_url,
        "summary": {
            "risk_level": vari_res["statistics"]["risk_level"],
            "risk_description": vari_res["statistics"]["risk_description"],
            "penjelasan_lapangan": {
                "kondisi_semak": f"{vari_res['statistics']['dry_fuel_percentage']}% semak kering mudah terbakar",
                "deteksi_bahaya": f"{fire_res['hotspot_count']} titik api dan {fire_res['smoke_count']} kepulan asap",
                "estimasi_angin": (
                    wind_estimation["keterangan"]
                    if is_dir_auto
                    else f"Angin berembus dari arah {wind['direction_compass']}{wind_speed_text}"
                ),
                "instruksi_babat": (
                    f"Bersihkan jalur selebar {metrics['recommended_width_meters']:g} m{length_text} "
                    "sampai terlihat tanah permukaan (Permen LHK 28/2021)"
                ),
                "jarak_aman": (
                    f"Tim wajib berjarak minimal {metrics['effective_safety_buffer_meters']:g} m dari api"
                    if metrics["effective_safety_buffer_meters"]
                    else "Belum dapat dihitung: isi tinggi vegetasi yang terbakar"
                ),
            },
            "hotspots_detected": fire_res["hotspot_count"],
            "smoke_detected": fire_res["smoke_count"],
            "cutting_length_meters": firebreak_res["metrics"]["cutting_length_meters"],
            "recommended_width_meters": firebreak_res["metrics"]["recommended_width_meters"],
            "clearing_time_hours": firebreak_res["metrics"]["estimated_clearing_hours"],
            "protected_hectares": firebreak_res["metrics"]["protected_area_hectares"],
            "effective_safety_buffer_meters": firebreak_res["metrics"]["effective_safety_buffer_meters"],
        },
        "layers": {
            "original_image_url": original_url,
            "video_url": video_url,
            "tactical_map_url": tactical_map_res["tactical_map_url"],
            "tactical_overlay_url": tactical_map_res["tactical_overlay_url"],
            "vari_heatmap_url": vari_overlay_url,
            "detection_overlay_url": detection_overlay_url,
            "firebreak_overlay_url": firebreak_overlay_url,
        },
        "land_mapping": {
            "total_fuel_zones": tactical_map_res["total_fuel_zones"],
            "fuel_zones": tactical_map_res["fuel_zones"],
            "total_dry_hectares": dry_hectares,
        },
        "vari_analysis": vari_res["statistics"],
        "detections": fire_res["detections"],
        "wind_estimation": wind_estimation,
        "firebreak_plan": {
            "trajectory": firebreak_res["trajectory"],
            "warnings": firebreak_res["warnings"],
            "standards": firebreak_res["standards"],
            "is_to_scale": firebreak_res["is_to_scale"],
            "is_partial": firebreak_res["is_partial"],
            "meters_per_pixel": firebreak_res["meters_per_pixel"],
            "metrics": firebreak_res["metrics"],
            "gps_coordinates": firebreak_res["gps_coordinates"],
            "wind": firebreak_res["wind_parameters"],
            "wind_estimation": wind_estimation,
        },
        "dimensions": dimensions,
    }

    return response_payload


@router.post("/dispatch-whatsapp", summary="Generate WhatsApp alerts for MPA and Downwind residents")
async def dispatch_whatsapp_alerts(request: DispatchRequest):
    """Generates tactical WhatsApp payloads and deep-links for field execution."""
    data = request.analysis_data
    if not data and request.image_id:
        # Re-run analysis or use sample to build payload
        analyze_req = AnalyzeRequest(image_id=request.image_id)
        data = await analyze_aerial_image(analyze_req)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Diperlukan data hasil analisis atau image_id untuk membuat pesan WhatsApp.",
        )

    dispatch_result = whatsapp_service.dispatch(data)
    return dispatch_result
