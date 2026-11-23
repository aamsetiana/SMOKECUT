"""REST API Routes for SEKAT-AI Core Engine."""

import os
import uuid
import shutil
from pathlib import Path
from typing import Union, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from PIL import Image

from backend.app.core.config import UPLOADS_DIR, SAMPLES_DIR, OUTPUT_DIR
from backend.app.services.vari_analyzer import vari_analyzer
from backend.app.services.fire_detector import fire_detector
from backend.app.services.firebreak_optimizer import firebreak_optimizer
from backend.app.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/api", tags=["Analysis & Dispatch"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi"}


class AnalyzeRequest(BaseModel):
    image_id: str = Field(..., description="Unique ID of previously uploaded image or 'sample'")
    wind_direction: Union[str, float] = Field(default=135.0, description="Wind direction in degrees (0-360) or compass string (e.g. 'SE', 'Tenggara')")
    wind_speed: float = Field(default=14.0, description="Wind velocity in km/h")
    safety_buffer: float = Field(default=25.0, description="Base safety buffer in meters for MPA crew")
    firebreak_width: float = Field(default=4.0, description="Recommended firebreak cutting width in meters (3 - 5m)")


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
            import cv2
            cap = cv2.VideoCapture(str(dest_path))
            if cap.isOpened():
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS) or 25
                target_frame = min(int(fps * 1.0), max(0, total_frames - 1))
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                if ret:
                    height, width = frame.shape[:2]
                    frame_filename = f"{image_id}_frame.jpg"
                    cv2.imwrite(str(UPLOADS_DIR / frame_filename), frame)
                    preview_url = f"/static/uploads/{frame_filename}"
            cap.release()
        except Exception:
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
    elif image_id != "sample":
        matching = list(UPLOADS_DIR.glob(f"{image_id}.*"))
        if matching:
            target_path = matching[0]

    # Fallback to sample image if not found or requested
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
        if not extracted.exists():
            try:
                import cv2
                cap = cv2.VideoCapture(str(target_path))
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(str(extracted), frame)
                    cap.release()
            except Exception:
                pass
        if extracted.exists():
            analysis_image_path = extracted

    # 1. VARI Flammability Fuel Mapping
    vari_res = vari_analyzer.analyze_image(analysis_image_path, image_id=image_id)
    dimensions = vari_res["dimensions"]

    # 2. Smoke & Hotspot Detection
    fire_res = fire_detector.detect(analysis_image_path, image_id=image_id)

    # 3. Firebreak Route Optimizer
    firebreak_res = firebreak_optimizer.optimize(
        image_dimensions=dimensions,
        dry_mask=vari_res["dry_mask"],
        hotspots=fire_res["detections"],
        wind_direction=request.wind_direction,
        wind_speed_kmh=request.wind_speed,
        safety_buffer_meters=request.safety_buffer,
        firebreak_width_meters=request.firebreak_width,
        image_id=image_id,
    )

    # Prepare preview URL for base original image/frame
    video_url = None
    if target_path.suffix.lower() in ALLOWED_VIDEO_EXTENSIONS:
        original_url = f"/static/uploads/{image_id}_frame.jpg"
        web_video = UPLOADS_DIR / f"{image_id}_web.mp4"
        if web_video.exists():
            video_url = f"/static/uploads/{image_id}_web.mp4"
        elif target_path == SAMPLES_DIR / "sample_drone_fire.mp4":
            static_sample_vid = UPLOADS_DIR / "sample_drone_fire.mp4"
            if not static_sample_vid.exists():
                shutil.copy(target_path, static_sample_vid)
            video_url = "/static/uploads/sample_drone_fire.mp4"
        else:
            video_url = f"/static/uploads/{target_path.name}"
    elif target_path == SAMPLES_DIR / "sample_aerial.jpg":
        # Copy to output/uploads directory so it's accessible via HTTP static
        static_sample = UPLOADS_DIR / "sample_aerial.jpg"
        if not static_sample.exists():
            shutil.copy(target_path, static_sample)
        original_url = "/static/uploads/sample_aerial.jpg"
    else:
        original_url = f"/static/uploads/{target_path.name}"

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
                "instruksi_babat": f"Babat semak selebar {firebreak_res['metrics']['recommended_width_meters']}m sepanjang {firebreak_res['metrics']['cutting_length_meters']}m untuk memutus rambatan api",
                "jarak_aman": f"Tim relawan wajib berjarak minimal {firebreak_res['metrics']['effective_safety_buffer_meters']}m dari arah api",
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
            "vari_heatmap_url": vari_res["overlay_url"],
            "detection_overlay_url": fire_res["overlay_url"],
            "firebreak_overlay_url": firebreak_res["overlay_url"],
        },
        "vari_analysis": vari_res["statistics"],
        "detections": fire_res["detections"],
        "firebreak_plan": {
            "trajectory": firebreak_res["trajectory"],
            "metrics": firebreak_res["metrics"],
            "gps_coordinates": firebreak_res["gps_coordinates"],
            "wind": firebreak_res["wind_parameters"],
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
