"""Published firebreak and crew-safety standards used by SEKAT-AI.

Every number here comes from a cited document. Values without a source must not be
added; callers report ``None`` ("belum ada data") instead.
"""

from typing import Any, Dict, Optional

# Permen LHK 28/2021 Lampiran I (jalur hijau & jalur kuning): lebar "3 x tinggi tanaman
# terluar yang dilindungi atau paling sedikit 20 meter".
MIN_FIREBREAK_WIDTH_M = 20.0
FIREBREAK_HEIGHT_MULTIPLE = 3.0

# USFS Missoula Fire Sciences Lab (preliminary rule): SSD = 8 x slope-wind factor x
# vegetation height. A factor of 1 only covers radiant heat on flat ground without wind.
SSD_HEIGHT_MULTIPLE = 8.0
MIN_SLOPE_WIND_FACTOR = 1.0

SOURCES = {
    "lebar_sekat": {
        "judul": "Permen LHK No. 28 Tahun 2021 tentang Sekat Bakar, Lampiran I",
        "url": "https://peraturan.bpk.go.id/Download/288707/Permen%20LHK%20Nomor%2028%20Tahun%202021.pdf",
    },
    "pembersihan": {
        "judul": "Permen LHK No. 28 Tahun 2021, Pasal 1, 4, 7, 8 dan Lampiran I angka 2",
        "url": "https://peraturan.bpk.go.id/Download/288707/Permen%20LHK%20Nomor%2028%20Tahun%202021.pdf",
    },
    "jarak_aman": {
        "judul": "USFS Missoula Fire Sciences Laboratory, Firefighter Safety (aturan awal/preliminary)",
        "url": "https://www.firelab.org/project/firefighter-safety",
    },
}

CLEARING_RULES = [
    "Jalur kuning: bersihkan semua vegetasi (termasuk pohon) dan bahan bakaran sampai terlihat tanah "
    "permukaan atau material yang tidak mudah terbakar.",
    "Jalur tidak boleh terputus, punya akses pemantauan, dan mengendalikan erosi.",
    "Lebar ditambah bila lereng makin miring, topografi makin kompleks, atau potensi api makin besar.",
    "Sambungkan ke penghalang yang sudah ada (sungai, jalan, parit/kanal) bila memungkinkan.",
    "Pemanfaatan kayu hasil pembersihan mengikuti peraturan perundang-undangan.",
]


def firebreak_width_m(protected_plant_height_m: Optional[float]) -> float:
    """Standard firebreak width; the legal minimum when the height is unknown."""
    return max(MIN_FIREBREAK_WIDTH_M, FIREBREAK_HEIGHT_MULTIPLE * (protected_plant_height_m or 0.0))


def safe_separation_m(fuel_height_m: Optional[float], slope_wind_factor: Optional[float]) -> Optional[float]:
    """Crew safe separation distance, or ``None`` when the fuel height is unknown."""
    if not fuel_height_m:
        return None
    return round(SSD_HEIGHT_MULTIPLE * max(MIN_SLOPE_WIND_FACTOR, slope_wind_factor or 1.0) * fuel_height_m, 1)


def describe() -> Dict[str, Any]:
    """Rules and sources to expose through the API."""
    return {"aturan_pembersihan": CLEARING_RULES, "sumber": SOURCES}
