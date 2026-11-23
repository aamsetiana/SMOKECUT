# TODO.md — Roadmap Eksekusi & Papan Tugas Proyek SEKAT-AI

Proyek: **SEKAT-AI (Smart Drone-Vision untuk Mitigasi Sekat Bakar & Pencegahan Asap PM2.5)**  
Kompetisi: **AIRIMPACT 2026 (MarkPlus, Inc.)**  
Metodologi: **Iteratif Bertahap & Berbasis Pengujian (TDD & Verifikasi Bertingkat)**

---

## Ringkasan Progres Proyek

| Fase | Deskripsi | Status | Total Tugas | Selesai |
|---|---|---|---|---|
| **Fase 1** | Inisialisasi & Struktur Dasar | `done` | 6 | 6 |
| **Fase 2** | Core Backend & Logika Computer Vision | `pending` | 8 | 0 |
| **Fase 3** | Antarmuka / Frontend Dashboard | `pending` | 7 | 0 |
| **Fase 4** | Integrasi Sistem & Pengujian MVP | `pending` | 6 | 0 |
| **Fase 5** | Aset Presentasi & Finalisasi AIRIMPACT 2026 | `pending` | 5 | 0 |

---

## Rincian Item Pekerjaan

### Fase 1: Inisialisasi & Struktur Dasar Proyek
- [x] 1.1 Siapkan struktur direktori modular (`backend/app/{api,core,cv,services}`, `backend/tests`, `frontend/src/{components,services}`, `samples`).
- [x] 1.2 Buat `backend/requirements.txt` dengan dependensi esensial (FastAPI, Uvicorn, OpenCV-Python, NumPy, SciPy, Ultralytics, Pydantic, Pytest).
- [x] 1.3 Inisialisasi boiler-plate backend FastAPI (`backend/app/main.py`) lengkap dengan CORS, routing dasar, dan health-check endpoint (`GET /health`).
- [x] 1.4 Inisialisasi scaffolding frontend berbasis React + Vite + Tailwind CSS dengan tema visual profesional (drone/geospatial look).
- [x] 1.5 Siapkan modul konfigurasi (`backend/app/core/config.py`) untuk path upload, model weight, dan parameter default analitik.
- [x] 1.6 Sediakan setidaknya 1 sampel citra drone lahan rawan bakar (`samples/sample_aerial.jpg`) sebagai data uji coba awal.

---

### Fase 2: Core Backend / Logika Utama Computer Vision & AI
- [x] 2.1 Implementasi modul kalkulasi indeks vegetasi **VARI** (`backend/app/cv/vari_processor.py`):
  - Formula: $\text{VARI} = \frac{G - R}{G + R - B}$
  - Penanganan kasus pembagian dengan nol (*zero division safe guard*).
  - Klasifikasi zonasi: Zona Merah/Kuning (semak kering mudah terbakar, nilai $\le 0.1$) vs Zona Hijau (vegetasi lembap, nilai $> 0.1$).
  - Pembuatan heatmap visualisasi (overlay RGBA transparan 30%).
- [x] 2.2 Tulis unit test untuk modul VARI (`backend/tests/test_vari.py`) untuk memverifikasi akurasi matematis formula dan ketahanan input citra.
- [x] 2.3 Implementasi modul deteksi dini asap & api (`backend/app/cv/smoke_detector.py`):
  - Integrasi inferensi model deteksi ringan (YOLOv8n / YOLOv11n) untuk frame video/foto.
  - Ekstraksi koordinat bounding box, confidence score, dan titik pusat (*centroid*).
  - Fallback deteksi berbasis *color/motion heuristic* jika bobot model belum terunduh saat offline.
- [x] 2.4 Implementasi algoritma penentu jalur sekat bakar optimal (`backend/app/cv/firebreak_planner.py`):
  - Menghitung arah perambatan berdasarkan kontur zona semak kering dan vektor angin (arah & kecepatan).
  - Kalkulasi jalur pembabatan terpendek di depan arah api dengan spesifikasi lebar sekat 3–5 meter.
  - Perhitungan *safety buffer* (jarak aman minimal tim MPA dari potensi titik api).
  - Estimasi panjang jalur babatan (dalam meter) dan konversi ke koordinat poliline.
- [x] 2.5 Tulis unit test untuk optimizer sekat bakar (`backend/tests/test_firebreak.py`).
- [x] 2.6 Implementasi service simulasi data angin & cuaca (`backend/app/services/weather_service.py`):
  - Dukungan parameter manual (kecepatan & arah mata angin) untuk mode patroli lapangan offline.
  - Mock generator data arah angin realistis.
- [ ] 2.7 Implementasi WhatsApp Alert Dispatcher (`backend/app/services/notification_service.py`):
  - Generator pesan untuk Tim MPA: ringkasan status risiko, panjang jalur babat (meter), koordinat GPS, dan tautan peta visual.
  - Generator pesan peringatan dini untuk Warga Downwind (zona arah angin): rekomendasi tutup jendela, pemakaian masker, perlindungan kelompok rentan.
- [ ] 2.8 Bangun REST API endpoints (`backend/app/api/routes.py`):
  - `POST /api/upload`: Unggah file citra (.jpg) atau video (.mp4).
  - `POST /api/analyze`: Memicu analisis 3-layer (VARI, Asap/Api, Rekomendasi Jalur Sekat Bakar).
  - `POST /api/dispatch-whatsapp`: Memicu pengiriman notifikasi peringatan ke MPA dan warga.

---

### Fase 3: Antarmuka / Frontend Dashboard (SEKAT-AI Visualizer)
- [ ] 3.1 Bangun layout utama dashboard (`frontend/src/App.jsx`) dengan tema dark/geospatial modern, navbar status, dan indikator mode (Patroli Preventif vs Respons Cepat).
- [ ] 3.2 Kembangkan komponen upload interaktif (`frontend/src/components/MediaUploader.jsx`) dengan drag-and-drop, validasi format (.mp4/.jpg), dan preview citra.
- [ ] 3.3 Kembangkan kanvas penampil citra udara multi-layer (`frontend/src/components/AerialViewer.jsx`):
  - Layer 1: Citra asli (drone RGB view).
  - Layer 2 (Toggle): Heatmap VARI transparan (Zona Bahan Bakar Kering Merah/Kuning).
  - Layer 3 (Toggle): Bounding box deteksi asap mikro / api awal.
  - Layer 4 (Toggle): Garis putus-putus tebal rekomendasi sekat bakar optimal + label jarak.
  - Layer 5: Ikon dan vektor arah angin aktif.
- [ ] 3.4 Kembangkan panel kontrol simulasi (`frontend/src/components/ControlPanel.jsx`):
  - Kontrol arah angin (kompas / sudut derajat) dan kecepatan angin (km/jam).
  - Pilihan lebar sekat bakar (3m, 4m, 5m) dan safety buffer slider.
  - Tombol aksi utama "Jalankan Analisis AI".
- [ ] 3.5 Kembangkan kartu metrik analitik (`frontend/src/components/MetricsCard.jsx`):
  - Estimasi panjang babatan (meter).
  - Estimasi luas lahan aman terlindungi (hektare).
  - Tingkat ancaman asap PM2.5 ke permukiman (Aman / Waspada / Bahaya).
  - Estimasi biomassa semak yang dapat diolah menjadi pakan/kompos.
- [ ] 3.6 Kembangkan modul preview & dispatch WhatsApp (`frontend/src/components/WhatsAppModal.jsx`):
  - Tampilan card notifikasi real-time untuk Tim MPA (Peta + Koordinat GPS).
  - Tampilan card peringatan dini untuk Warga Downwind.
  - Tombol kirim dengan konfirmasi simulasi pengiriman sukses.
- [ ] 3.7 Integrasikan API client (`frontend/src/services/api.js`) untuk komunikasi asinkron yang mulus antara frontend dan backend FastAPI.

---

### Fase 4: Integrasi Sistem & Pengujian MVP
- [ ] 4.1 Uji alur kerja *end-to-end* (Upload Foto/Video → Proses VARI & Jalur Sekat → Render Hasil di Dashboard → Kirim Notifikasi WhatsApp).
- [ ] 4.2 Lakukan verifikasi mode offline (memastikan seluruh inferensi dan visualisasi dapat berjalan tanpa akses internet di laptop lapangan).
- [ ] 4.3 Jalankan suite pengujian otomatis (`pytest backend/tests/ -v`) dan pastikan 100% lulus (*all tests passing*).
- [ ] 4.4 Optimasi performa: pastikan kalkulasi VARI dan rendering canvas responsif (< 2 detik untuk citra resolusi drone standar).
- [ ] 4.5 Siapkan panduan eksekusi cepat (*Quick Start Guide*) dan dokumentasi skenario pengujian di `README.md`.
- [ ] 4.6 Buat checkpoint git commit untuk MVP yang stabil dan berfungsi penuh.

---

### Fase 5: Aset Presentasi & Finalisasi AIRIMPACT 2026
- [ ] 5.1 Buat aset visual resolusi tinggi (Dashboard Mockup) untuk **Slide 5** sesuai panduan Bagian 4 Blueprint (Header dasbor, foto udara, overlay merah semak kering, garis putus-putus sekat bakar, panah arah angin, tombol kirim WA).
- [ ] 5.2 Siapkan rangkuman copywriting siap salin untuk 10 slide presentasi PPTX (Rasio 16:9, Font $\ge 18\text{ pt}$ isi, $\ge 12\text{ pt}$ referensi) sesuai Bagian 3 Blueprint.
- [ ] 5.3 Validasi 6 kriteria penilaian juri: *Problem Relevance, Solution Innovation, Feasibility, Impact & Measurability, Behavior Change, Collaboration & Sustainability*.
- [ ] 5.4 Lakukan audit kepatuhan terhadap **Checklist Final Anti-Diskualifikasi** (Bagian 6 Blueprint).
- [ ] 5.5 Final save point dan laporan komprehensif kepada Project Manager.
