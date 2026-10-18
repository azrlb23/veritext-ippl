# VeriText AI

> **Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical & Semantic AI Engine**  
> Proyek Pengembangan Perangkat Lunak untuk Mata Kuliah Rekayasa Perangkat Lunak / IPPL.

---

## 📌 Ringkasan Proyek

VeriText AI mengimplementasikan pipa pemrosesan hybrid 4 tingkat (*4-Tier Detection Pipeline*) untuk mendeteksi berbagai bentuk kecurangan akademik:
- **Tier 1 (Leksikal)**: Algoritma *Winnowing* (k-gram $k=5$, sliding window $w=4$, Rabin-Karp Hash) untuk mendeteksi plagiarisme *verbatim* / *copy-paste* langsung.
- **Tier 2 (Semantik)**: Representasi vektor padat (*dense embeddings*) 384-dimensi menggunakan `paraphrase-multilingual-MiniLM-L12-v2` dan pencarian ANN (*Approximate Nearest Neighbor*) berbasis indeks HNSW pada PostgreSQL `pgvector`.
- **Tier 3 (Stilometri & AI)**: Analisis variasi panjang kalimat (*Burstiness*) dan keragaman kosa kata (*Type-Token Ratio* - TTR) untuk mendeteksi anomali teks hasil generasi AI / LLM.
- **Tier 4 (Agregasi & Visualisasi)**: Penggabungan skor terbobot (50% Leksikal : 35% Semantik : 15% Stilometri) menjadi *Overall Composite Similarity Index* dengan *Interactive Heatmap* 3 warna:
  - 🔴 **Merah (`#EF4444`)**: Plagiarisme Leksikal / Verbatim
  - 🟠 **Oranye (`#F97316`)**: Plagiarisme Semantik / Parafrasa
  - 🟡 **Kuning (`#EAB308`)**: Anomali Pola AI / Pola Stilometri

---

## 🏗️ Struktur Monorepo

```
IPPL/
├── frontend/                   # Lapisan Presentasi (Vue 3, Vite, Tailwind CSS, Pinia)
│   ├── src/
│   │   ├── assets/             # CSS & Static styles (Tailwind base, tier theme colors)
│   │   ├── components/         # Reusable UI components (Navbar, Footer, TierLegend, HeatmapViewer, etc.)
│   │   ├── views/              # Pages (Landing, Dashboard, AuditDetail, Login, Register, Corpus, Billing, Verify)
│   │   ├── stores/             # State Management (Pinia: auth, audit)
│   │   ├── services/           # HTTP API client & service layers
│   │   ├── types/              # TypeScript Interfaces & Model DTOs
│   │   ├── router/             # Vue Router route declarations
│   │   ├── App.vue             # Root Vue Component
│   │   └── main.ts             # Vue Application bootstrap
│   ├── tailwind.config.js      # Konfigurasi skema warna tier & tema
│   ├── vite.config.ts          # Konfigurasi Vite & dev proxy
│   └── package.json
│
├── backend/                    # Lapisan API, Logika Bisnis & Worker (FastAPI, Celery, SQLAlchemy)
│   ├── app/
│   │   ├── core/               # Konfigurasi, Database session async/sync, JWT Security
│   │   ├── models/             # 14 Tabel SQLAlchemy 2.0 (users, sessions, documents, audit_*, corpus_*, etc.)
│   │   ├── schemas/            # Pydantic v2 validation & response schemas
│   │   ├── api/v1/             # REST Routers (auth, documents, audits, reports, corpus, billing, admin)
│   │   ├── services/           # Domain business logic & operations
│   │   ├── workers/            # Celery app & distributed processing tasks
│   │   └── main.py             # FastAPI App instance, CORS, middleware, routers mounting
│   ├── alembic/                # Database Migrations (Relasional + pgvector HNSW)
│   ├── scripts/                # Database bootstrap SQL & scripts
│   ├── requirements.txt        # Python dependency manifest
│   └── pyproject.toml          # Project configuration & metadata
│
├── docker-compose.yml          # Postgres 16 (pgvector) & Redis 7 Infrastructure
├── .env.example                # Template konfigurasi variabel lingkungan
├── .gitignore
├── SRS_Sistem_Deteksi_Plagiarisme_Hybrid.md
├── SDD_Sistem_Deteksi_Plagiarisme_Hybrid.md
└── README.md
```

---

## 🚀 Panduan Memulai Cepat (Quickstart)

### 1. Prasyarat Sistem
- Docker & Docker Compose
- Node.js 18+ & npm
- Python 3.11+

### 2. Konfigurasi Lingkungan
Salin file konfigurasi contoh:
```bash
cp .env.example .env
```

### 3. Menjalankan Infrastruktur Basis Data & Antrean (Docker)
Jalankan PostgreSQL 16 (dengan ekstensi `pgvector` & `pgcrypto`) serta Redis 7:
```bash
docker compose up -d
```
Pastikan kontainer berjalan:
```bash
docker compose ps
```

### 4. Menjalankan Backend (FastAPI + Celery)
```bash
cd backend

# Buat virtual environment & aktifkan
python3 -m venv .venv
source .venv/bin/activate

# Install dependensi
pip install -r requirements.txt

# Jalankan migrasi basis data
alembic upgrade head

# Jalankan server API
uvicorn app.main:app --reload --port 8000

# Di terminal terpisah, jalankan Celery Worker
celery -A app.workers.celery_app worker --loglevel=info
```
API Documentation (Swagger UI): `http://localhost:8000/docs`

### 5. Menjalankan Frontend (Vue 3 + Tailwind CSS)
```bash
cd frontend

# Install dependensi Node.js
npm install

# Jalankan server development Vite
npm run dev
```
Akses antarmuka web di: `http://localhost:5173`

---

## 🎨 Skema Warna Semantik Tier Plagiarisme

| Tier | Kategori | Warna | Hex Code | Deskripsi |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | Leksikal (*Verbatim*) | Merah | `#EF4444` | Penjiplakan kata per kata persis (Winnowing $k=5$) |
| **Tier 2** | Semantik (*Paraphrase*) | Oranye | `#F97316` | Penjiplakan parafrasa (Embedding 384-dim HNSW Cosine $\ge 0.78$) |
| **Tier 3** | Pola AI (*Stylometric*) | Kuning | `#EAB308` | Anomali stilometri (Burstiness Rendah $\le 4.5$, TTR Rendah $\le 0.42$) |
| **Status Aman** | Orisinal | Hijau | `#22C55E` | Konten orisinal, skor kesamaan $\le 25\%$ |

---

## 🔒 Lisensi & Integritas Akademik
Dikembangkan untuk implementasi proyek Rekayasa Perangkat Lunak (IPPL). Mengikuti standar kepatuhan privasi data dan perlindungan kekayaan intelektual naskah akademik.
