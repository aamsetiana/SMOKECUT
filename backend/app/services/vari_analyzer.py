"""VARI (Visible Atmospherically Resistant Index) Analysis Service for SEKAT-AI.

Calculates vegetation flammability index:
    VARI = (Green - Red) / (Green + Red - Blue)
High values (> 0.1): Moist / healthy vegetation (Safe Zone).
Low / Negative values (<= 0.1): Dry thatch / bushes (High Flammability Fuel Zone).
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Union
import numpy as np
from PIL import Image

from backend.app.core.config import (
    VARI_DRY_THRESHOLD,
    OUTPUT_DIR,
)


class VARIAnalyzer:
    """Service to process aerial imagery and compute VARI fuel maps."""

    def __init__(self, dry_threshold: float = VARI_DRY_THRESHOLD, moderate_threshold: float = 0.25):
        self.dry_threshold = dry_threshold
        self.moderate_threshold = moderate_threshold

    def calculate_vari(self, rgb_array: np.ndarray) -> np.ndarray:
        """Compute VARI matrix from an RGB image array with zero-division safeguard.

        Args:
            rgb_array: NumPy array of shape (H, W, 3) with R, G, B channels in uint8 or float.

        Returns:
            NumPy 2D float32 array of shape (H, W) with clipped VARI values [-1.0, 1.0].
        """
        arr = rgb_array.astype(np.float32)
        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]

        denominator = g + r - b
        # Epsilon safeguard against zero or near-zero division
        safe_denom = np.where(np.abs(denominator) < 1e-6, np.sign(denominator + 1e-6) * 1e-6, denominator)

        vari = (g - r) / safe_denom
        # Clip to standard theoretical range [-1.0, 1.0]
        return np.clip(vari, -1.0, 1.0)

    def analyze_image(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        image_id: str,
        is_bgr: bool = False,
    ) -> Dict[str, Any]:
        """Perform complete VARI analysis and export visual overlay.

        Args:
            image_input: File path, PIL Image, or NumPy array.
            image_id: Unique identifier for the image session.
            is_bgr: Set True if input is from cv2.imread (BGR format).

        Returns:
            Dictionary containing fuel statistics, risk classification, and overlay path.
        """
        if isinstance(image_input, (str, Path)):
            pil_img = Image.open(image_input).convert("RGB")
            rgb_arr = np.array(pil_img)
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
            rgb_arr = np.array(pil_img)
        elif isinstance(image_input, np.ndarray):
            if is_bgr:
                # BGR to RGB: swap channels 0 and 2
                rgb_arr = image_input[:, :, ::-1]
            else:
                rgb_arr = image_input
            pil_img = Image.fromarray(rgb_arr.astype(np.uint8))
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        h, w = rgb_arr.shape[:2]
        total_pixels = h * w

        # Calculate VARI
        vari_matrix = self.calculate_vari(rgb_arr)

        # Categorize zones
        dry_mask = vari_matrix <= self.dry_threshold
        moderate_mask = (vari_matrix > self.dry_threshold) & (vari_matrix <= self.moderate_threshold)
        safe_mask = vari_matrix > self.moderate_threshold

        dry_count = int(np.sum(dry_mask))
        moderate_count = int(np.sum(moderate_mask))
        safe_count = int(np.sum(safe_mask))

        dry_percentage = round((dry_count / total_pixels) * 100, 2)
        moderate_percentage = round((moderate_count / total_pixels) * 100, 2)
        safe_percentage = round((safe_count / total_pixels) * 100, 2)
        mean_vari = round(float(np.mean(vari_matrix)), 4)

        # Risk classification with clear, accessible Indonesian descriptions
        if dry_percentage >= 40.0:
            risk_level = "TINGGI"
            risk_description = "Lahan didominasi semak kering (bahan bakar api). Api sangat mudah menjalar cepat."
        elif dry_percentage >= 20.0:
            risk_level = "SEDANG"
            risk_description = "Sebagian semak mengering. Perlu sekat bakar di perbatasan semak kering."
        else:
            risk_level = "RENDAH"
            risk_description = "Didominasi tanaman hijau lembap. Lahan aman dan tahan dari sambaran api."

        # Generate RGBA Heatmap Overlay
        overlay_arr = np.zeros((h, w, 4), dtype=np.uint8)

        # Dry Fuel: Red (239, 68, 68) with 40% alpha (102)
        overlay_arr[dry_mask] = [239, 68, 68, 115]

        # Moderate: Amber/Yellow (245, 158, 11) with 30% alpha (76)
        overlay_arr[moderate_mask] = [245, 158, 11, 80]

        # Safe: Emerald Green (16, 185, 129) with 25% alpha (64)
        overlay_arr[safe_mask] = [16, 185, 129, 65]

        overlay_img = Image.fromarray(overlay_arr)
        overlay_filename = f"vari_overlay_{image_id}.png"
        overlay_path = OUTPUT_DIR / overlay_filename
        overlay_img.save(overlay_path, "PNG")

        return {
            "statistics": {
                "total_pixels": total_pixels,
                "dry_fuel_percentage": dry_percentage,
                "moderate_percentage": moderate_percentage,
                "safe_vegetation_percentage": safe_percentage,
                "mean_vari": mean_vari,
                "risk_level": risk_level,
                "risk_description": risk_description,
            },
            "overlay_filename": overlay_filename,
            "overlay_url": f"/static/output/{overlay_filename}",
            "dry_mask": dry_mask,
            "dimensions": {"width": w, "height": h},
        }


# Singleton instance for application services
vari_analyzer = VARIAnalyzer()
