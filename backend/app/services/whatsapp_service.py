"""WhatsApp Notification and Alert Dispatcher Service for SMOKECUT.

Generates structured tactical dispatch messages for:
1. MPA / BPBD Ground Crews: Cutting length, firebreak width, GPS navigation points, and biomass circularity.
2. Downwind Residents: Early air quality advisory and PM2.5 smoke mitigation protocols.
"""

from typing import Dict, Any, List
import urllib.parse


class WhatsAppNotificationService:
    """Formats and dispatches tactical alert messages and deep-links."""

    def format_mpa_alert(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tactical message for Masyarakat Peduli Api (MPA) field team."""
        summary = analysis_data.get("summary", {})
        firebreak = analysis_data.get("firebreak_plan", {})
        metrics = firebreak.get("metrics", {})
        gps = firebreak.get("gps_coordinates", {})
        wind = firebreak.get("wind", {})

        length_m = metrics.get("cutting_length_meters", 120.0)
        width_m = metrics.get("recommended_width_meters", 4.0)
        buffer_m = metrics.get("effective_safety_buffer_meters", 25.0)
        hours = metrics.get("estimated_clearing_hours", 4.8)
        team_size = metrics.get("recommended_team_size", 5)

        start_lat = gps.get("start", {}).get("latitude", -0.2285)
        start_lon = gps.get("start", {}).get("longitude", 101.5542)
        end_lat = gps.get("end", {}).get("latitude", -0.2295)
        end_lon = gps.get("end", {}).get("longitude", 101.5562)

        risk_level = summary.get("risk_level", "TINGGI")
        hotspot_count = summary.get("hotspots_detected", 0)

        message_text = (
            "🚨 *[SEKAT-AI / SMOKECUT ALERT] INSTRUKSI TAKTIS SEKAT BAKAR PREVENTIF*\n"
            f"Status Lapangan: *RISIKO {risk_level}* ({hotspot_count} titik api/asap terdeteksi)\n\n"
            "📋 *Spesifikasi Pembabatan Jalur Sekat Bakar:*\n"
            f"• Estimasi Panjang Jalur: *{length_m} Meter*\n"
            f"• Lebar Pemotongan: *{width_m} Meter* (sesuai standar MPA)\n"
            f"• Safety Buffer (Jarak Aman): *{buffer_m} Meter* dari kepala api\n"
            f"• Estimasi Waktu Babat: *{hours} Jam* (regu {team_size} orang)\n"
            f"• Arah & Kecepatan Angin: {wind.get('direction_compass', 'Tenggara')} ({wind.get('speed_kmh', 14)} km/jam)\n\n"
            "📍 *Koordinat Navigasi GPS:*\n"
            f"• Titik Mulai (A): `{start_lat}, {start_lon}`\n"
            f"• Titik Selesai (B): `{end_lat}, {end_lon}`\n"
            f"• Buka Panduan Peta: https://maps.google.com/?q={start_lat},{start_lon}\n\n"
            "🌾 *Sirkularitas Biomassa:*\n"
            "Rumput dan semak hasil babatan *TIDAK BOLEH DITINGGALKAN* di pinggir jalur! "
            "Segera angkut untuk pakan ternak warga atau bahan kompos desa."
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
        wind_compass = wind.get("direction_compass", "Tenggara (SE)")
        wind_speed = wind.get("speed_kmh", 14.0)

        message_text = (
            "⚠️ *[PERINGATAN DINI KUALITAS UDARA SEKAT-AI]*\n"
            "Waspada Dispersi Asap & Partikulat Halus PM2.5\n\n"
            "💨 *Kondisi Angin & Jalur Asap:*\n"
            f"• Arah Embusan Angin: Menuju ke permukiman dari arah {wind_compass}\n"
            f"• Kecepatan Angin: {wind_speed} km/jam\n"
            "• Potensi Bahaya: Asap mikro dan partikel PM2.5 berpotensi masuk ke area warga.\n\n"
            "🛡️ *Protokol Perlindungan Mandiri Warga:*\n"
            "1. Tutup pintu, jendela, dan ventilasi rumah.\n"
            "2. Gunakan masker saat beraktivitas di luar rumah.\n"
            "3. Pastikan kelompok rentan (anak-anak, lansia, ibu hamil) tetap di dalam ruangan.\n"
            "4. Tim relawan MPA sedang membuka sekat bakar pencegah di batas lahan."
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
