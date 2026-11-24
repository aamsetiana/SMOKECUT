"""WhatsApp Notification and Alert Dispatcher Service for SMOKECUT.

Generates structured tactical dispatch messages for:
1. MPA / BPBD Ground Crews: Cutting length, firebreak width, GPS navigation points, and biomass circularity.
2. Downwind Residents: Early air quality advisory and PM2.5 smoke mitigation protocols.
"""

from typing import Any, Dict
import urllib.parse


class WhatsAppNotificationService:
    """Formats and dispatches tactical alert messages and deep-links."""

    @staticmethod
    def _wind_text(wind: Dict[str, Any]) -> str:
        """Wind description without inventing missing values."""
        if not wind.get("direction_compass"):
            return "belum ada data"
        text = f"dari {wind['direction_compass']}"
        if wind.get("speed_kmh"):
            text += f" ({wind['speed_kmh']:g} km/jam)"
        return text + (" - perkiraan dari citra" if wind.get("is_auto_detected") else "")

    def format_mpa_alert(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tactical message for Masyarakat Peduli Api (MPA) field team."""
        summary = analysis_data.get("summary", {})
        firebreak = analysis_data.get("firebreak_plan", {})
        metrics = firebreak.get("metrics", {})
        gps = firebreak.get("gps_coordinates", {})
        wind = firebreak.get("wind", {})

        def meters(key: str) -> str:
            value = metrics.get(key)
            return f"{value:g} meter" if value else "belum ada data"

        width = metrics.get("recommended_width_meters")
        start, end = gps.get("start"), gps.get("end")
        if start and end:
            gps_text = (
                f"• Titik Mulai (A): `{start['latitude']}, {start['longitude']}`\n"
                f"• Titik Selesai (B): `{end['latitude']}, {end['longitude']}`\n"
                f"• Buka Panduan Peta: https://maps.google.com/?q={start['latitude']},{start['longitude']}\n\n"
            )
        else:
            gps_text = "• Belum ada data GPS. Jangan bergerak sebelum lokasi dipastikan.\n\n"
        notes = "".join(f"• {w}\n" for w in firebreak.get("warnings", []))
        message_text = (
            "🚨 *[SEKAT-AI / SMOKECUT ALERT] REKOMENDASI SEKAT BAKAR*\n"
            f"Status Lapangan: *RISIKO {summary.get('risk_level', 'belum ada data')}* "
            f"({summary.get('hotspots_detected', 0)} titik/garis api terdeteksi)\n\n"
            "📋 *Spesifikasi Sekat Bakar:*\n"
            f"• Panjang Jalur: *{'minimal ' if firebreak.get('is_partial') else ''}{meters('cutting_length_meters')}*\n"
            f"• Lebar: *{f'{width:g} meter' if width else 'belum ada data'}* (Permen LHK 28/2021)\n"
            f"• Jarak Aman Tim: *{meters('effective_safety_buffer_meters')}* dari api\n"
            f"• Angin: {self._wind_text(wind)}\n"
            "• Bersihkan vegetasi dan bahan bakaran sampai terlihat tanah permukaan.\n\n"
            "📍 *Koordinat Navigasi GPS:*\n"
            f"{gps_text}"
            + (f"⚠️ *Catatan:*\n{notes}\n" if notes else "")
            + "🌾 *Hasil Pembersihan:*\n"
            "Angkut rumput dan semak hasil babatan dari jalur. Pemanfaatan kayu mengikuti peraturan."
        )

        encoded_text = urllib.parse.quote(message_text)
        deep_link = f"https://wa.me/?text={encoded_text}"

        return {
            "recipient_group": "Tim MPA / BPBD",
            "message_text": message_text,
            "deep_link": deep_link,
            "target_coordinates": {"start": gps.get("start"), "end": gps.get("end")},
        }

    def format_downwind_warning(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate early PM2.5 air quality warning for residents downwind of the fire threat."""
        firebreak = analysis_data.get("firebreak_plan", {})
        wind = firebreak.get("wind", {})
        message_text = (
            "⚠️ *[PERINGATAN DINI KUALITAS UDARA SEKAT-AI]*\n"
            "Waspada Dispersi Asap & Partikulat Halus PM2.5\n\n"
            "💨 *Kondisi Angin & Jalur Asap:*\n"
            f"• Angin: {self._wind_text(wind)}\n"
            "• Potensi Bahaya: Asap mikro dan partikel PM2.5 berpotensi masuk ke area warga.\n\n"
            "🛡️ *Protokol Perlindungan Mandiri Warga:*\n"
            "1. Tutup pintu, jendela, dan ventilasi rumah.\n"
            "2. Gunakan masker saat beraktivitas di luar rumah.\n"
            "3. Pastikan kelompok rentan (anak-anak, lansia, ibu hamil) tetap di dalam ruangan.\n"
            "4. Ikuti arahan petugas setempat."
        )

        encoded_text = urllib.parse.quote(message_text)
        deep_link = f"https://wa.me/?text={encoded_text}"

        return {
            "recipient_group": "Warga Zona Arah Angin (Downwind)",
            "message_text": message_text,
            "deep_link": deep_link,
        }

    def dispatch(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Produce full dispatch packet containing both MPA instructions and resident warnings."""
        mpa_payload = self.format_mpa_alert(analysis_data)
        downwind_payload = self.format_downwind_warning(analysis_data)

        return {
            "status": "success",
            "message": "Notifikasi WhatsApp siap didistribusikan",
            "dispatches": [mpa_payload, downwind_payload],
        }


# Singleton instance
whatsapp_service = WhatsAppNotificationService()
