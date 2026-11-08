# AGENTS.md — VeriText AI Agent Briefing

Baca berkas ini terlebih dahulu pada setiap sesi baru. Berkas ini adalah rujukan otoritatif untuk stack teknologi, perintah eksekusi, invarian domain, dan batasan rekayasa pada repositori **VeriText AI**.

---

## 1. Tech Stack & Exact Versions
- **Backend Runtime**: Python 3.11+ (virtualenv di `backend/venv`)
- **Backend Framework**: FastAPI 0.115.x + Pydantic v2 + Uvicorn ASGI
- **Asynchronous Task Queue**: Celery 5.4.x + Redis 7.2.x (Message Broker & Result Backend)
- **Database & Vector Engine**: PostgreSQL 16.x + ekstensi `pgvector` v0.7.0+ (HNSW `vector(384)`, `m = 16`, `ef_construction = 64`)
- **ORM & Migrations**: SQLAlchemy 2.0.x (`AsyncSession` via `asyncpg`) + Alembic
- **AI & NLP Engine**:
  - **Step 1 (Lexical)**: Algoritma Winnowing ($k=5, w=4$) + Rabin-Karp Rolling Hash ($b=257, M=10^9+7$)
  - **Step 2 (Semantic)**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-d) + Re-ranker Indonesia `LazarusNLP/all-indobert-base-v4` (768-d)
  - **Step 3 (Stylometric & Contextual Judge)**: Goh & Barabasi Burstiness $B = (\sigma_L - \mu_L)/(\sigma_L + \mu_L)$ & TTR + **Dual-Engine LLM Gateway** (Primary: Google Gemini 2.5 Flash; Failover: DeepSeek v4.1 Flash via 9Router `http://localhost:20128/v1`)
- **Frontend Framework**: Vue 3.5.x (Composition API `<script setup lang="ts">`) + Vite 6.x + TypeScript 5.7.x
- **Frontend State, Routing & Styling**: Pinia 2.3.x + Vue Router 4.5.x + Axios 1.7.x + Tailwind CSS 3.4.x
- **Payment Gateway**: Midtrans Core & Snap API v2 (Webhook SHA-512 Verification)
- **PDF Engine**: WeasyPrint 61.x + `qrcode` (Dynamic QR Verification `/verify/{certificate_uuid}`)

---

## 2. Executable Commands

### Backend (`cd backend`)
- Run unit & integration tests: `./venv/bin/pytest`
- Run specific atomic test file: `./venv/bin/pytest tests/test_engine.py -q`
- Lint & format check (Ruff): `./venv/bin/ruff check app tests`
- Start FastAPI dev server: `./venv/bin/uvicorn app.main:app --reload --port 8000`
- Start Celery worker: `./venv/bin/celery -A app.workers.celery_app worker --loglevel=info`
- Run Alembic migrations: `./venv/bin/alembic upgrade head`

### Frontend (`cd frontend`)
- Install dependencies: `npm install`
- Type-check & build verification: `npm run build`
- Start Vite dev server: `npm run dev`
- Run frontend navigation/unit tests: `node src/tests/navigation.test.mjs`

---

## 3. Non-Obvious Patterns & Critical Domain Invariants

1. **Self-Service SaaS 3-Role Model (`FREE`, `PREMIUM`, `ADMIN`)**:
   - **TIDAK ADA** peran `Dosen`, `Mahasiswa`, atau `Superadmin`.
   - `FREE`: Otomatis mendapat **5 Token Gratis** + **3x Kuota Trial AI Chatbot/Parafrase** (`ai_trial_remaining = 3`) saat registrasi; batas maksimal **2.500 kata per dokumen** (1 Token); ukuran berkas maksimal **15 MB**; *View-Only* laporan di web (tidak bisa mengunduh PDF resmi).
   - `PREMIUM`: Otomatis di-upgrade oleh sistem saat webhook Midtrans berstatus `settlement` atau `capture`; mendukung naskah panjang hingga 15 MB, akses penuh AI Chatbot & Parafrase 3-Mode, serta unduh PDF resmi ber-QR Code.
   - `ADMIN`: **100% Read-Only Monitoring** (murni metode HTTP `GET`). Admin **dilarang keras** memiliki fitur mutasi status/suspend pengguna, mutasi saldo token manual, unggah ZIP korpus manual, atau pengubahan bobot algoritma di UI.
2. **Rumus Biaya Token & Sub-Kredit AI**:
   - Biaya audit dokumen: $\text{Biaya} = \min(5, \lceil \text{Jumlah Kata} / 2500 \rceil)$ Token (1 Token per 2.500 kata, dengan *Token Cap* maksimal 5 Token untuk skripsi/tesis panjang).
   - Konsumsi AI Chatbot & Parafrase (Premium User setelah 3x Trial habis): **1 Token = 10x interaksi chat / parafrase kalimat / paragraf** (dilacak pada kolom `ai_chat_allowance_remaining`), atau **1 Token per 2 halaman penuh** untuk mode *Full-Page Batch Paraphrase*.
3. **Skema Pembelian Token Midtrans Snap**:
   - **By Token (Satuan)**: Rp 2.000 / token (minimal pembelian 5 Token = Rp 10.000).
   - **By Paket Token (Bundling)**: Paket Starter (15 Token = Rp 25.000), Paket Skripsi Pro (50 Token = Rp 65.000), Paket Riset Intensif (150 Token = Rp 150.000).
4. **Transaksi Saldo & Webhook Wajib Atomik**:
   - Setiap pemotongan token (`DEBIT_AUDIT`, `DEBIT_CHAT_PARAPHRASE`), refund (`CREDIT_REFUND`), dan top-up (`CREDIT_TOPUP`) **wajib** menggunakan row-level locking (`SELECT ... FOR UPDATE`) di dalam transaksi database aktif.
5. **Rumus Skor Komposit & Tag Warna Semantik**:
   - $S_{\text{Composite}} = (0.50 \times S_{\text{Lexical}}) + (0.35 \times S_{\text{Semantic}}) + (0.15 \times S_{\text{Stylometric}})$
   - Tag kalimat (`match_type`): `NONE`, `RED` (Leksikal $\ge 80\%$), `ORANGE` (Semantik $\ge 75\%$), `YELLOW` (Stilometri / Anomali AI), `RESOLVED_GREEN` (Kalimat yang telah diperbaiki melalui fitur *in-place paraphrase*).
6. **Zero Auto-Ingestion & Hard-Delete Cascade (UU PDP No. 27/2022)**:
   - Naskah pengguna tidak pernah dimasukkan otomatis ke tabel `corpus_documents`.
   - Saat pengguna menghapus naskah (`DELETE /api/v1/documents/{id}`), sistem wajib menghapus berkas fisik di disk serta mengeksekusi *hard-delete cascade* pada `documents`, `audit_tasks`, `audit_sentences`, `audit_reports`, `chat_sessions`, dan `chat_messages`.

---

## 4. Engineering Boundaries

### Always (Wajib Dilakukan)
- Baca `docs/BLUEPRINT.md`, `docs/API_CONTRACT.md`, `docs/DATABASE_SCHEMA.md`, dan `docs/ATOMIC_CODING_STANDARDS.md` sebelum menulis atau mengubah kode.
- Gunakan **Pola Orkestrasi Brain (Argon / Sonnet, Fallback: Flash High) + Worker (`Model="flash"`)**:
  - **Brain (Primary: Gemini Argon / Claude Sonnet; Fallback: Gemini Flash High jika Argon/Sonnet tidak tersedia atau limit)**: Bertindak sebagai *Lead Architect, Orchestrator, & Reviewer* yang merancang spesifikasi per irisan tugas atomik (*S/M Task Slice* 1–4 berkas), mendefinisikan subagen pekerja (`define_subagent` dengan `EnableWriteTools=True`), mendelegasikan penulisan kode ke subagen melalui `invoke_subagent(..., Model="flash")`, serta mengaudit hasil kerja.
  - **Worker (`Model="flash"`)**: Mengeksekusi penulisan/refactoring kode atomik sesuai instruksi Brain, menjalankan pengujian (`pytest` / `ruff` / `npm run build`), dan melaporkan metrik jumlah baris (LOC) setiap berkas kembali ke Brain.
- Patuhi **Aturan Kode Atomik (Sub-150 LOC)**: Setiap berkas kode baru atau hasil refactor wajib memiliki panjang maksimal 150 baris kode dan hanya memiliki satu tanggung jawab tunggal (*Single Responsibility Principle*).
- Patuhi **Zero-Emoji Policy**: Dilarang keras menggunakan karakter emoji visual di dalam kode sumber, tampilan UI, pesan respons API, komentar, maupun dokumen teknis.
- Jalankan pengujian (`pytest` di backend, `npm run build` di frontend) setiap selesai mengerjakan satu irisan tugas atomik (*S/M Task Slice* 1–4 berkas).

### Ask First (Tanyakan Terlebih Dahulu)
- Mengubah struktur tabel pada `docs/DATABASE_SCHEMA.md` atau membuat migrasi Alembic baru yang mengubah kontrak kolom.
- Menambahkan pustaka dependensi baru ke `requirements.txt` atau `package.json`.

### Never (Dilarang Keras)
- Membuat "God File" (> 150 baris) yang mencampur routing, logika bisnis, kueri SQL, dan pemanggilan AI dalam satu berkas.
- Menambahkan kembali fitur birokrasi kampus lama (seperti unggah ZIP korpus oleh dosen, tabel manajemen suspend user oleh admin, atau kartu pengaturan bobot AI di halaman admin).
- Menyimpan kredensial rahasia atau API Key asli ke dalam repositori Git (gunakan `.env` dan `.env.example`).
