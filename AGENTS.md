# AGENTS.md — Pedoman Teknis & Aturan Pengembang SMOKECUT

Selamat datang di proyek **SMOKECUT** (*Smart Drone-Vision untuk Mitigasi Sekat Bakar & Pencegahan Asap PM2.5*). Dokumen ini berfungsi sebagai panduan standar arsitektur, konvensi teknis, dan aturan kerja mutlak bagi seluruh agen pengembang otonom dan tim rekayasa perangkat lunak.

---

## 1. Ringkasan Arsitektur Sistem

SEKAT-AI adalah sistem perangkat lunak murni (*pure software*, *drone-agnostic*) yang mengolah video/foto udara dari drone kamera RGB standar tanpa memerlukan sensor thermal mahal. Sistem bekerja secara lokal/offline di laptop lapangan maupun cloud dengan alur **Record → Upload → Process → Action**.

```
[Drone RGB Standar (60-100m)]
           │ (File Video .mp4 / Foto .jpg)
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SEKAT-AI Core Engine (FastAPI)               │
│                                                                 │
│  1. Layer Deteksi Dini: YOLOv8n / YOLOv11n (Asap & Titik Api)   │
│  2. Layer Indeks Vegetasi: VARI = (G - R) / (G + R - B)         │
│     -> Peta Semak Kering (Zona Merah/Kuning vs Zona Lembap)    │
│  3. Layer Optimizer Jalur Sekat Bakar (Firebreak Planner):      │
│     -> Kombinasi Fuel Map + Vektor Angin (Speed & Direction)    │
│     -> Penghubung Hambatan Alami (Jalan/Parit) + Safety Buffer  │
│  4. Service Dispatcher: Peta Koordinat GPS & Alert WhatsApp     │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [Dashboard Web Interaktif]      [Distribusi Pesan WhatsApp]
       - Preview Citra / Video Udara   - Tim MPA: Peta Jalur & GPS
       - Multi-layer Visualizer        - Warga Downwind: Early Warning
       - Panel Kontrol Angin & Metrik    Kualitas Udara PM2.5
```

### 3 Lapis Analisis Computer Vision Utama:
1. **Deteksi Asap & Titik Api Awal**: Deteksi kepulan asap mikro atau titik api lokal pada frame video/foto udara menggunakan model object detection ringan.
2. **Pemetaan Semak Kering (VARI Formula)**:
   $$\text{VARI} = \frac{G - R}{G + R - B}$$
   - Nilai tinggi (> 0.1): Vegetasi basah / hijau / aman.
   - Nilai rendah / negatif ($\le 0.1$): Semak kering, ilalang mudah terbakar (Zona Bahan Bakar Berisiko).
3. **Kalkulasi Garis Sekat Bakar Optimal**:
   Algoritma penentuan jalur potong terpendek (lebar 3–5 meter) memotong arah rambat api di depan zona bahan bakar kering dengan mempertimbangkan arah & kecepatan angin, menghubungkan batas alami/jalan setapak, dan mengunci *safety buffer* untuk keselamatan tim pembabat MPA.

---

## 2. Tech Stack yang Digunakan

### Backend & AI Core
- **Bahasa**: Python 3.10+
- **Framework API**: FastAPI + Uvicorn (ringan, performa tinggi, dokumentasi OpenAPI otomatis)
- **Computer Vision & Pemrosesan Citra**: OpenCV (`opencv-python`), NumPy, SciPy
- **Model Object Detection**: Ultralytics YOLO (`yolov8n` / model deteksi asap & api ringan)
- **Data Modeling & Validasi**: Pydantic v2
- **Notification & Mock Gateway**: Service modular untuk simulasi dan pengiriman pesan WhatsApp (format teks & peta koordinat gambar)

### Frontend & Visualizer
- **Framework SPA**: React 18+ dengan Vite
- **Styling**: Tailwind CSS
- **Ikonografi & Komponen**: Lucide React
- **Visualisasi Citra & Peta Udara**: HTML5 Canvas / Leaflet (rendering overlay transparansi heatmap VARI, garis jalur sekat bakar, dan vektor arah angin)

### Tooling & Pengujian
- **Pengujian Backend**: Pytest
- **Linter/Formatter**: Black, Flake8, Ruff
- **Manajemen Versi**: Git

---

## 3. Struktur Direktori Modular

```
SMOKECUT/
├── .git/
├── .gitignore
├── AGENTS.md
├── TODO.md
├── Blueprint Eksekusi SEKAT-AI - AIRIMPACT 2026.md.pdf
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # Entrypoint aplikasi FastAPI
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py               # Konfigurasi aplikasi & environment
│   │   │   └── logger.py               # Format logging standar
│   │   ├── cv/
│   │   │   ├── __init__.py
│   │   │   ├── vari_processor.py       # Algoritma indeks VARI & masking vegetasi
│   │   │   ├── smoke_detector.py       # Detektor asap & api awal (YOLO)
│   │   │   └── firebreak_planner.py    # Algoritma rute sekat bakar optimal + safety buffer
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── weather_service.py      # Integrasi/simulasi data arah & kecepatan angin
│   │   │   └── notification_service.py # Gateway notifikasi WhatsApp (MPA & Downwind)
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes.py               # Endpoint upload, analisis citra/video, & dispatch
│   ├── requirements.txt                # Dependensi Python
│   └── tests/
│       ├── __init__.py
│       ├── test_vari.py                # Unit test formula VARI
│       ├── test_firebreak.py           # Unit test kalkulasi jalur sekat
│       └── test_api.py                 # Integrasi test endpoint
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                     # Layout utama dashboard SEKAT-AI
│       ├── components/
│       │   ├── Header.jsx              # Status koneksi & header dasbor
│       │   ├── MediaUploader.jsx       # Drag & drop upload citra/video
│       │   ├── AerialViewer.jsx        # Canvas viewer dengan toggle multi-layer
│       │   ├── ControlPanel.jsx        # Slider angin, buffer jarak, & trigger analisis
│       │   ├── MetricsCard.jsx         # Panjang babatan, luas aman, status risiko
│       │   └── WhatsAppModal.jsx       # Preview dan aksi dispatch notifikasi WA
│       └── services/
│           └── api.js                  # HTTP client ke backend FastAPI
│
└── samples/                            # Sampel data citra drone untuk demonstrasi & tes
    └── sample_aerial.jpg
```

---

## 4. Perintah Terminal untuk Menjalankan & Menguji Aplikasi

### Persiapan Lingkungan (Setup)

#### Backend:
```bash
# Buat virtual environment Python
python3 -m venv venv
source venv/bin/activate

# Instal dependensi backend
pip install -r backend/requirements.txt
```

#### Frontend:
```bash
# Masuk ke direktori frontend dan instal node dependencies
cd frontend
npm install
cd ..
```

### Menjalankan Aplikasi

#### Menjalankan Backend (Development Server):
```bash
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation Swagger UI tersedia di: `http://localhost:8000/docs`

#### Menjalankan Frontend:
```bash
cd frontend
npm run dev
```
Dashboard UI dapat diakses di: `http://localhost:5173`

### Menjalankan Pengujian (Testing)
```bash
source venv/bin/activate
pytest backend/tests/ -v
```

---

## 5. Aturan Wajib Agen Pengembang (Non-Negotiable)

Setiap agen pengembang otonom yang bekerja pada repositori ini **wajib mematuhi 3 aturan mutlak** berikut:

1. **Kode Bersih, Ringkas, dan Minim Dependensi**:
   - Tulis kode modular dengan prinsip *Separation of Concerns* (SoC) dan *Single Responsibility Principle* (SRP).
   - Jangan menambahkan library/dependensi eksternal tanpa justifikasi teknis yang jelas. Utamakan penggunaan built-in standard library dan pustaka inti yang sudah disepakati (FastAPI, OpenCV, NumPy, Pytest).
   - Kode harus terdokumentasi dengan docstring yang jelas dan type annotations.

2. **Cek File Sebelum Membuat yang Baru**:
   - Selalu periksa (*inspect/read*) file yang sudah ada dalam workspace sebelum membuat fungsi, modul, atau file baru guna menghindari redundansi kode atau duplikasi struktur direktori.
   - Perbaiki atau kembangkan modul yang sudah ada alih-alih membuat modul alternatif yang membingungkan.

3. **Disiplin Update `TODO.md` & Git Commit Deskriptif**:
   - Setiap kali menyelesaikan satu unit tugas/subtugas, perbarui status item pekerjaan di `TODO.md` dari `[ ]` menjadi `[x]`.
   - Lakukan `git commit` dengan pesan yang deskriptif mengikuti konvensi *Conventional Commits* (contoh: `feat: implement VARI index calculation in vari_processor.py`, `test: add unit tests for firebreak pathfinder`, `fix: handle zero division in RGB channels`).

---

## 6. Team Roles, Code Ownership & Branching Rules

Proyek SEKAT-AI dikelola oleh tim 3 orang dengan pembagian peran dan kepemilikan kode (*code ownership*) yang tegas:

### A. Pembagian Peran Tim (Team Roles)
| Anggota | Peran / Jabatan | Wilayah Kepemilikan (Code Ownership) | Tanggung Jawab Utama |
|---|---|---|---|
| **@Aam** | **Project Manager, System Architect & AI Integration Lead** | Root config, `AGENTS.md`, `TODO.md`, `docs/`, branch `main` | Mengelola arsitektur keseluruhan, standarisasi kontrak API (`docs/API_CONTRACT.md`), review & merge branch ke `main`, pengujian *end-to-end*, dan persiapan finalisasi proposal AIRIMPACT 2026. |
| **@Apliy** | **Backend & Computer Vision Engineer** | `backend/` (seluruh modul core, cv, services, api) & `backend/tests/` | Mengembangkan formula VARI, deteksi asap & api awal, algoritma rute sekat bakar, layanan cuaca/angin, WhatsApp alert dispatcher, serta memastikan seluruh unit test lulus 100%. |
| **@Indra** | **Frontend & UI/UX Engineer** | `frontend/` (seluruh komponen, services, styles, assets) | Mengembangkan dashboard web interaktif, media uploader (drag & drop), visualizer multi-layer (canvas drone view), panel kontrol parameter angin, kartu metrik, dan modal simulasi WhatsApp. |

### B. Aturan Isolasi Kode (Boundary Rules)
1. **Zona Eksklusif Backend**: @Apliy memiliki kepemilikan penuh atas direktori `backend/`. Anggota atau agen lain DILARANG memodifikasi file backend tanpa koordinasi dengan @Apliy.
2. **Zona Eksklusif Frontend**: @Indra memiliki kepemilikan penuh atas direktori `frontend/`. Anggota atau agen lain DILARANG memodifikasi file frontend tanpa koordinasi dengan @Indra.
3. **Penyambung Antarmuka**: Seluruh interaksi data antara frontend dan backend WAJIB mengacu secara ketat pada dokumen kontrak resmi di `docs/API_CONTRACT.md` yang disetujui oleh @Aam.

### C. Alur Kerja Percabangan Git (Git Branching Model)
- **`main`**: Branch produksi dan rilis stabil. Hanya @Aam yang berwenang melakukan merge ke branch ini setelah seluruh pengujian lulus dan integrasi terverifikasi.
- **`feat/backend-apliy`**: Branch kerja aktif @Apliy untuk fitur-fitur backend, optimasi CV, dan pengujian unit.
- **`feat/frontend-indra`**: Branch kerja aktif @Indra untuk implementasi UI, komponen React, styling Tailwind, dan interaksi dashboard.

