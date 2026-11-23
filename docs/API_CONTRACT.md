# SMOKECUT API Contract Documentation

**Status**: RESMI & AKTIF (Implementasi Fase 2)  
**Lead Architect**: @Aam  
**Backend Engineer**: @Apliy  
**Frontend Engineer**: @Indra  
**Base URL Development**: `http://localhost:8000`  
**Swagger UI**: `http://localhost:8000/docs`

Dokumen ini adalah kontrak resmi antara Backend FastAPI (@Apliy) dan Frontend React/Vite (@Indra). Setiap perubahan skema pada endpoint di bawah ini wajib disetujui oleh @Aam.

---

## 1. Static Asset Serving

Endpoint untuk mengambil file citra asli dan layer overlay transparan yang dihasilkan oleh AI engine:

- **Uploads (Citra Asli)**: `GET /static/uploads/{filename}`
- **Outputs (Layer Analisis AI)**: `GET /static/output/{filename}`

---

## 2. Ringkasan Endpoint API

| Method | Endpoint | Deskripsi | Penanggung Jawab |
|---|---|---|---|
| `GET` | `/health` | Pemeriksaan kesehatan server backend | @Apliy |
| `POST` | `/api/upload` | Unggah citra/video drone RGB (.jpg, .png, .mp4) | @Apliy / @Indra |
| `POST` | `/api/analyze` | Eksekusi pipeline 3-Layer (VARI, Deteksi Asap/Api, Sekat Bakar) | @Apliy / @Indra |
| `POST` | `/api/dispatch-whatsapp` | Generate payload pesan instruksi MPA & peringatan warga | @Apliy / @Indra |

---

## 3. Spesifikasi Rinci Endpoint

### 3.1. `POST /api/upload`
Menerima file visual drone, memvalidasi format, menyimpannya di server, dan mengembalikan `image_id` unik untuk dianalisis.

#### Request:
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file`: File biner citra (.jpg, .jpeg, .png) atau rekaman video (.mp4).

#### Response (200 OK):
```json
{
  "status": "success",
  "image_id": "4b6807eaec2e",
  "filename": "drone_patrol_01.jpg",
  "saved_as": "4b6807eaec2e.jpg",
  "preview_url": "/static/uploads/4b6807eaec2e.jpg",
  "media_type": "image",
  "dimensions": {
    "width": 800,
    "height": 600
  }
}
```

#### Error Response (400 Bad Request):
```json
{
  "detail": "Format file '.pdf' tidak didukung. Harap unggah foto (.jpg, .png) atau video (.mp4)."
}
```

---

### 3.2. `POST /api/analyze`
Menjalankan algoritma pemrosesan citra 3 lapis secara simultan dan deterministik.

#### Request:
- **Content-Type**: `application/json`
- **Body JSON**:
```json
{
  "image_id": "sample",
  "wind_direction": 135.0,
  "wind_speed": 14.0,
  "safety_buffer": 25.0,
  "firebreak_width": 4.0
}
```

*Catatan Parameter*:
- `image_id` *(string, required)*: ID yang didapat dari `/api/upload`, atau `"sample"` untuk menggunakan citra bawaan demonstrasi.
- `wind_direction` *(number atau string, default: 135.0)*: Sudut arah angin dalam derajat (`0`–`360`) atau string kompas (`"SE"`, `"Tenggara"`, `"NW"`).
- `wind_speed` *(number, default: 14.0)*: Kecepatan angin dalam km/jam.
- `safety_buffer` *(number, default: 25.0)*: Jarak aman dasar tim MPA dalam meter.
- `firebreak_width` *(number, default: 4.0)*: Rekomendasi lebar jalur babatan (standar MPA: 3–5 meter).

#### Response (200 OK):
```json
{
  "status": "success",
  "image_id": "sample_aerial",
  "summary": {
    "risk_level": "TINGGI",
    "risk_description": "Dominasi semak kering mudah terbakar. Risiko rambatan api sangat tinggi.",
    "hotspots_detected": 1,
    "smoke_detected": 2,
    "cutting_length_meters": 77.0,
    "recommended_width_meters": 4.0,
    "clearing_time_hours": 3.1,
    "protected_hectares": 1.99,
    "effective_safety_buffer_meters": 35.0
  },
  "layers": {
    "original_image_url": "/static/uploads/sample_aerial.jpg",
    "vari_heatmap_url": "/static/output/vari_overlay_sample_aerial.png",
    "detection_overlay_url": "/static/output/detections_sample_aerial.png",
    "firebreak_overlay_url": "/static/output/firebreak_overlay_sample_aerial.png"
  },
  "vari_analysis": {
    "total_pixels": 480000,
    "dry_fuel_percentage": 66.21,
    "moderate_percentage": 0.14,
    "safe_vegetation_percentage": 33.66,
    "mean_vari": 0.129,
    "risk_level": "TINGGI",
    "risk_description": "Dominasi semak kering mudah terbakar. Risiko rambatan api sangat tinggi."
  },
  "detections": [
    {
      "id": 1,
      "class_name": "hotspot",
      "label": "Titik Api Awal",
      "confidence": 0.98,
      "bbox": {
        "x": 465,
        "y": 306,
        "w": 32,
        "h": 27
      },
      "centroid": {
        "x": 481,
        "y": 317
      }
    },
    {
      "id": 2,
      "class_name": "smoke",
      "label": "Kepulan Asap Dini",
      "confidence": 0.92,
      "bbox": {
        "x": 310,
        "y": 0,
        "w": 490,
        "h": 599
      },
      "centroid": {
        "x": 555,
        "y": 299
      }
    }
  ],
  "firebreak_plan": {
    "trajectory": {
      "start_point": { "x": 20.0, "y": 245.7 },
      "end_point": { "x": 229.7, "y": 20.0 },
      "anchor_point": { "x": 60.0, "y": 76.0 },
      "threat_origin": { "x": 150.0, "y": 175.0, "type": "Titik Api Aktif" }
    },
    "metrics": {
      "cutting_length_meters": 77.0,
      "recommended_width_meters": 4.0,
      "effective_safety_buffer_meters": 35.0,
      "estimated_clearing_hours": 3.1,
      "protected_area_hectares": 1.99,
      "recommended_team_size": 5
    },
    "gps_coordinates": {
      "start": { "latitude": -0.228622, "longitude": 101.553347 },
      "end": { "latitude": -0.229129, "longitude": 101.553818 }
    },
    "wind": {
      "direction_degrees": 135.0,
      "direction_compass": "Tenggara (SE)",
      "speed_kmh": 14.0
    }
  },
  "dimensions": {
    "width": 800,
    "height": 600
  }
}
```

---

### 3.3. `POST /api/dispatch-whatsapp`
Menghasilkan payload pesan terstruktur siap salin / kirim via WhatsApp Web / API untuk Tim Lapangan MPA dan Warga Pemukiman.

#### Request:
- **Content-Type**: `application/json`
- **Body JSON**:
```json
{
  "image_id": "sample"
}
```
*(Bisa mengirimkan `image_id` atau meneruskan objek `analysis_data` lengkap dari response `/api/analyze`).*

#### Response (200 OK):
```json
{
  "status": "success",
  "message": "Notifikasi WhatsApp siap didistribusikan",
  "dispatches": [
    {
      "recipient_group": "Tim MPA / BPBD",
      "message_text": "🚨 *[SEKAT-AI ALERT] INSTRUKSI TAKTIS SEKAT BAKAR PREVENTIF*\nStatus Lapangan: *RISIKO TINGGI* (1 titik api/asap terdeteksi)\n\n📋 *Spesifikasi Pembabatan Jalur Sekat Bakar:*\n• Estimasi Panjang Jalur: *77.0 Meter*\n• Lebar Pemotongan: *4.0 Meter* (sesuai standar MPA)\n• Safety Buffer (Jarak Aman): *35.0 Meter* dari kepala api\n• Estimasi Waktu Babat: *3.1 Jam* (regu 5 orang)\n• Arah & Kecepatan Angin: Tenggara (SE) (14.0 km/jam)\n\n📍 *Koordinat Navigasi GPS:*\n• Titik Mulai (A): `-0.228622, 101.553347`\n• Titik Selesai (B): `-0.229129, 101.553818`\n• Buka Panduan Peta: https://maps.google.com/?q=-0.228622,101.553347\n\n🌾 *Sirkularitas Biomassa:*\nRumput dan semak hasil babatan *TIDAK BOLEH DITINGGALKAN* di pinggir jalur! Segera angkut untuk pakan ternak warga atau bahan kompos desa.",
      "deep_link": "https://wa.me/?text=...",
      "target_coordinates": {
        "start": { "latitude": -0.228622, "longitude": 101.553347 },
        "end": { "latitude": -0.229129, "longitude": 101.553818 }
      }
    },
    {
      "recipient_group": "Warga Zona Arah Angin (Downwind)",
      "message_text": "⚠️ *[PERINGATAN DINI KUALITAS UDARA SEKAT-AI]*\nWaspada Dispersi Asap & Partikulat Halus PM2.5\n\n💨 *Kondisi Angin & Jalur Asap:*\n• Arah Embusan Angin: Menuju ke permukiman dari arah Tenggara (SE)\n• Kecepatan Angin: 14.0 km/jam\n• Potensi Bahaya: Asap mikro dan partikel PM2.5 berpotensi masuk ke area warga.\n\n🛡️ *Protokol Perlindungan Mandiri Warga:*\n1. Tutup pintu, jendela, dan ventilasi rumah.\n2. Gunakan masker saat beraktivitas di luar rumah.\n3. Pastikan kelompok rentan (anak-anak, lansia, ibu hamil) tetap di dalam ruangan.\n4. Tim relawan MPA sedang membuka sekat bakar pencegah di batas lahan.",
      "deep_link": "https://wa.me/?text=..."
    }
  ]
}
```

---

## 4. Panduan Implementasi Frontend (@Indra)

1. **Layer Rendering di Canvas**:
   - `layers.original_image_url` dirender di layer paling bawah.
   - `layers.vari_heatmap_url`, `layers.detection_overlay_url`, dan `layers.firebreak_overlay_url` adalah file PNG transparan (RGBA) dengan dimensi yang sama persis (`dimensions.width` $\times$ `dimensions.height`). Cukup tumpuk (*composite*) di canvas/DOM dengan kontrol toggle checkbox/switch per layer.
2. **Deep-Link WhatsApp**:
   - Properti `deep_link` dapat langsung dipasang pada elemen `<a href={item.deep_link} target="_blank">` untuk membuka WhatsApp Web atau aplikasi mobile WhatsApp dengan pesan yang sudah terisi otomatis.
