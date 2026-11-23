# SMOKECUT 🛰️🔥
> **Smart Drone-Vision untuk Mitigasi Sekat Bakar & Pencegahan Asap PM2.5**  
> *Tagline: "Cegah Api Melebar, Jaga Napas Warga"*  
> **Kompetisi**: AIRIMPACT 2026 (MarkPlus, Inc.)

---

## 📌 Ringkasan Solusi

**SMOKECUT** adalah perangkat lunak murni (*pure software*, *drone-agnostic*) berbasis Computer Vision yang mengolah citra dan video udara dari drone kamera RGB standar tanpa memerlukan sensor thermal mahal. Sistem bekerja secara lokal/offline di laptop lapangan maupun cloud dengan alur **Record → Upload → Process → Action**.

```
[Drone RGB Standar (60-100m)]
           │ (File Video .mp4 / Foto .jpg)
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SMOKECUT Core Engine (FastAPI)               │
│                                                                 │
│  1. Layer Deteksi Dini: YOLOv8 / CV Heuristik (Asap & Api)      │
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

---

## 👥 Tim & Pembagian Peran (Team Roles)

| Anggota | Peran | Kepemilikan Kode | Tanggung Jawab |
|---|---|---|---|
| **@Aam** | **Project Manager & System Architect** | `AGENTS.md`, `TODO.md`, `docs/`, `main` | Mengelola arsitektur keseluruhan, review & merge PR, validasi kontrak API, dan materi AIRIMPACT 2026. |
| **@Apliy** | **Backend & Computer Vision Engineer** | `backend/` & `backend/tests/` | Pengembangan formula VARI, deteksi asap/api, algoritma rute sekat bakar, weather service, dan WhatsApp dispatcher. |
| **@Indra** | **Frontend & UI/UX Engineer** | `frontend/` | Pengembangan dashboard web interaktif, visualizer multi-layer canvas, panel simulasi parameter, dan kartu metrik. |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, FastAPI, Uvicorn, NumPy, Pillow, OpenCV (opsional accelerator), Pytest
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons
- **AI & Computer Vision**: Indeks Vegetasi VARI $\frac{G - R}{G + R - B}$, Color Spectrum Contour Detection, Firebreak Route Optimizer
- **Komunikasi**: RESTful API JSON ([docs/API_CONTRACT.md](docs/API_CONTRACT.md)), Deep-Link WhatsApp (`wa.me`)

---

## 🚀 Panduan Memulai Cepat (Quick Start)

### 1. Kloning Repositori
```bash
git clone https://github.com/aamsetiana/SMOKECUT.git
cd SMOKECUT
```

### 2. Setup & Jalankan Backend (FastAPI)
```bash
# Buat dan aktifkan virtual environment Python
python3 -m venv venv
source venv/bin/activate  # Di Windows: venv\Scripts\activate

# Instal dependensi backend
pip install -r backend/requirements.txt

# Jalankan server FastAPI
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health Status: `http://localhost:8000/health`
- Dokumentasi Interaktif Swagger UI: `http://localhost:8000/docs`

### 3. Setup & Jalankan Frontend (React + Vite)
Buka tab terminal baru:
```bash
cd frontend
npm install
npm run dev
```
- Dashboard UI dapat diakses di: `http://localhost:5173`

### 4. Menjalankan Pengujian Otomatis (Testing)
```bash
source venv/bin/activate
pytest -v
```
*(Seluruh 17 unit test wajib berstatus `PASSED`)*.

---

## 📖 Dokumentasi Lengkap
- [Buku Panduan & Aturan Pengembang](AGENTS.md)
- [Kontrak Resmi API Frontend & Backend](docs/API_CONTRACT.md)
- [Papan Roadmap & Checklist Tugas](TODO.md)

---
*SEKAT-AI — Cegah Api Melebar, Jaga Napas Warga.*
