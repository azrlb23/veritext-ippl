# VeriText AI — Konteks Proyek Lengkap

> Disusun: 2026-10-23, dari pembacaan langsung kode, git history, dokumen, dan hasil menjalankan tes.
> Cakupan: repo `/Users/azrlb23/Documents/IPPL` (branch `main`, remote `github.com/azrlb23/veritext-ippl`, 35 commit, working tree bersih saat disusun).
> Pemilik: Mochammad Azriel Albian Putra (NIM 11241045), mata kuliah IPPL, Institut Teknologi Nasional.
> Sifat dokumen: potret keadaan nyata kode, bukan klaim dokumentasi. Bagian 11 memuat temuan yang bertentangan dengan klaim README/SRS/SDD.

---

## 1. Ringkasan Satu Paragraf

VeriText AI adalah prototipe sistem deteksi plagiarisme akademik berbahasa Indonesia dengan pipa hybrid 4-tier (leksikal Winnowing, semantik embedding 384-D, stilometri deteksi pola AI, agregasi skor + heatmap). Monorepo: backend FastAPI + SQLAlchemy 2 async + Celery + PostgreSQL/pgvector + Redis, frontend Vue 3 + Vite + Pinia + Tailwind 3. Ada 4 peran (TRIAL, PREMIUM, REVIEWER, ADMIN), dompet token berbayar (Midtrans sandbox simulasi), verifikasi sertifikat PDF + QR publik, bank korpus pembanding, dan konsol admin. Target tugas: minimal 30% fitur untuk UTS; README mengklaim 3 dari 7 fitur inti selesai (42,86%) dan sisanya "tersedia/terintegrasi".

## 2. Peta Repo

```
IPPL/
├── backend/                FastAPI app (app/), Alembic, tests/
│   └── app/{core,models,schemas,api/v1,services,engine,workers}
├── frontend/               Vue 3 SPA (src/{views,components/<domain>,composables,stores,services,types,router,utils})
├── db/                     init/ (01 ext, 02 DDL 14 tabel, 03 seed), migrations/0001 SQL mentah
├── docs/skills_mapping_ippl.md
├── .agents/{rules,skills(70),skills_archive(237)}   .agent -> .agents, skills -> .agents/skills (symlink)
├── .cursorrules            aturan agen untuk frontend
├── docker-compose.yml      postgres pgvector:pg16 + redis:7-alpine
├── .env / .env.example     (.env di-gitignore; daftar key identik dengan example)
├── README.md, AI_USAGE.md, PANDUAN_PRESENTASI_UTS.md
├── SRS_*.md (94 KB), SDD_*.md (44 KB), TESTING_WHITEBOX_VERITEXT_AI.md (47 KB)
└── contoh_naskah_uji.txt   naskah contoh untuk demo
```

Ukuran kode (baris): backend app ≈ 4.600, backend tests ≈ 3.000 (whitebox 1.558), frontend src ≈ 9.800 (AdminView 1.172, UserManagementTable 885, DashboardView 574).

## 3. Stack & Versi Terpasang

| Lapisan | Teknologi | Catatan |
|---|---|---|
| API | FastAPI 0.128, Pydantic 2.13, pydantic-settings | Respons dibungkus `APIResponse[T]` (`success,message,data,meta`) |
| ORM/DB | SQLAlchemy 2.0.54 (async asyncpg + sync psycopg2), Alembic, PostgreSQL 16 + pgvector | Dua engine: async untuk API, sync untuk Celery/Alembic |
| Antrean | Celery 5.6 + Redis 7 | Ada fallback mock Celery dan fallback thread lokal |
| Auth | PyJWT HS256 + bcrypt langsung | Refresh token acak di cookie HttpOnly, hash SHA-256 di tabel `sessions` |
| PDF | reportlab + qrcode | Sertifikat audit (`pdf_certificate_service.py`, 460 baris) |
| Ekstraksi teks | pdfplumber, python-docx | `.txt` coba utf-8/latin-1/cp1252 |
| Frontend | Vue 3.5, Vue Router 4.5, Pinia 2.3, axios, Tailwind 3.4, Vite 6, vue-tsc 2.2, TS 5.7 | Tanpa Vitest; tes pakai skrip `node --experimental-strip-types` |
| Font/desain | Plus Jakarta Sans + Source Serif 4; token "Steep" (`design-reference/steep`), alias "Audyr" | Palet monokrom ink `#17191c`, kartu 24 px, tombol pill |

Mesin lokal (diverifikasi): macOS Darwin 25.5, Node v24.21, `.venv` Python **3.9.6**, tidak ada Python 3.11+, uv/pyenv tidak ada, Docker daemon **tidak berjalan**, folder `uploads/` kosong.

## 4. Arsitektur Backend

### 4.1 Alur modul
`main.py` → CORS (origin localhost:5173/3000) → router `/api/v1` yang memuat `auth, documents, audits, reports, corpus, billing, admin`. Handler exception global mengembalikan 500 JSON (detail asli hanya saat `DEBUG`). `/health` dan `/` tersedia, Swagger di `/docs`.

### 4.2 Endpoint (semua di bawah `/api/v1`)

| Router | Endpoint | Akses | Catatan perilaku |
|---|---|---|---|
| auth | `POST /register` | publik | Role `TRIAL`, dompet 5 token, set cookie refresh. Respons `token_balance=5` ditulis keras |
| | `POST /login` | publik | Lihat temuan F1 |
| | `POST /logout`, `/refresh` | bearer / cookie | Refresh tidak merotasi token; logout hapus baris sesi |
| | `POST /forgot-password`, `/reset-password` | publik | **Stub**: hanya mengembalikan pesan sukses |
| | `GET /me`, `PATCH /profile`, `PATCH /change-password` | bearer | |
| documents | `POST /upload` | bearer | Validasi ekstensi (pdf/docx/txt), 0 byte, maks 50 MB; debit token; buat `Document`+`AuditTask`; jalankan audit |
| | `GET ""`, `GET/DELETE /{id}` | bearer, milik sendiri | DELETE = soft delete (`deleted_at`) |
| audits | `POST ""`, `GET /{id}/status`, `POST /{id}/cancel` | bearer, milik sendiri | Biaya: 1 token (TIER1_ONLY) atau 2 (FULL) |
| | `GET /tasks`, `/history`, `/history/export-csv` | bearer | Pencarian `ilike` nama file |
| reports | `GET /reports/{id}` | bearer | Terima `report.id` atau `audit_task_id`; **tanpa cek kepemilikan** |
| | `GET /reports/{id}/export-pdf` | **tanpa auth** | Parameter `token` ada tapi tidak dipakai |
| | `GET /verify/{uuid}` | publik | Valid / tidak ditemukan / dokumen sudah dihapus (UU PDP) |
| corpus | `POST /ingest`, `GET`, `PATCH/DELETE /{id}` | REVIEWER, ADMIN | Ingest hanya `.zip` (header `PK`, maks 100 MB, dedupe SHA-256); DELETE = status `DELETED` |
| billing | `GET /wallet`, `POST /topup`, `GET /invoices`, `GET /invoices/{id}/pdf` | bearer | Paket: 10/50/200 token = Rp25.000/100.000/350.000. PDF invoice hanya stub PDF minimal |
| | `POST /webhook` | publik | Verifikasi signature SHA-512 dilewati bila `ENVIRONMENT == "development"` |
| admin | `/users` CRUD, `/users/{id}/reset-password`, `/status`, `/adjust-tokens` | ADMIN | `{user_id}` boleh UUID atau email; `PUT` bersifat upsert |
| | `GET /health-metrics`, `POST /reindex-hnsw`, `GET /audit-logs`, `POST /purge-retention` | ADMIN | CPU/memori/redis/celery di health-metrics **angka tetap**; reindex-hnsw **stub** |

Otorisasi: `get_current_user` (Bearer JWT → muat user + wallet; 401/403) dan `require_role(*roles)` (ADMIN selalu lolos).

### 4.3 Model data (14 tabel, `backend/app/models`)
`users` (role CHECK TRIAL/PREMIUM/REVIEWER/ADMIN di SQL, tidak di model), `sessions`, `password_resets`, `token_wallets` (CHECK balance ≥ 0), `token_transactions` (DEBIT_AUDIT, CREDIT_TOPUP, CREDIT_REFUND, CREDIT_ADMIN, DEBIT_ADMIN), `invoices`, `documents`, `audit_tasks` (status QUEUED/PROCESSING/SUCCESS/FAILED/CANCELLED/REVOKED, depth TIER1_ONLY/FULL), `audit_sentences`, `audit_reports` (skor Numeric(5,2), `heatmap_annotations` + `matched_sources` JSONB, `verification_uuid` unik), `corpus_documents`, `document_chunks` (`Vector(384)`, indeks HNSW cosine di DDL), `lexical_fingerprints` (BigInteger hash), `audit_logs`. Tipe kustom `GUID` (UUID PG / CHAR(36)) dan fallback `Vector` bila pgvector tidak terpasang.

### 4.4 Pipa deteksi (`backend/app/engine`)
1. **Preprocessor**: segmentasi kalimat dengan offset karakter eksak (`text[start:end] == kalimat`), daftar singkatan Indonesia/akademik, penanganan angka desimal dan inisial, deteksi kalimat sitasi (`[1]`, `(Santoso dkk., 2023)`, "Daftar Pustaka").
2. **Tier 1 Winnowing**: k=5, w=4, basis 257, mod 1.000.000.007, Rabin-Karp rolling hash, tie-break paling kanan; skor = containment (|FP∩korpus| / |FP dokumen|)×100. Kalimat dianggap cocok bila ≥40% fingerprint cocok atau ≥3 fingerprint; similarity kalimat dikunci minimal 0,70.
3. **Tier 2 Semantik**: ambang parafrasa 0,75. Memakai `sentence_transformers` bila terpasang, **jika tidak** memakai embedding deterministik 384-D buatan sendiri (stemmer awalan/akhiran Indonesia, peta sinonim → konsep, n-gram karakter, proyeksi hash SHA-256, normalisasi L2). Kalimat yang sudah cocok di Tier 1 dikecualikan. Skor = jumlah similarity kalimat cocok / jumlah kalimat non-sitasi ×100.
4. **Tier 3 Stilometri**: burstiness = (σ−μ)/(σ+μ), ambang AI 0,20; TTR; 11 pola frasa transisi AI (ID/EN). Skor = 60% faktor burstiness + 25% keseragaman panjang kalimat + 15% penanda transisi; `is_ai` bila burstiness < 0,20 dan skor ≥ 35.
5. **Tier 4 Agregator**: komposit = 0,50·T1 + 0,35·T2 + 0,15·T3 (bobot dari config). Heatmap per kalimat dengan prioritas T1 (RED `#EF4444`) > T2 (ORANGE `#F97316`) > T3 (YELLOW `#EAB308`, hanya mode FULL dan skor T3 ≥ 30). `matched_sources` dihitung dari bobot (T1: jumlah match×1,5; T2: total similarity×2) dikali `max(komposit, 5)`. Mode `TIER1_ONLY` melewati T2/T3 dan komposit = T1.
6. **Korpus bawaan**: `ReferenceCorpusBank` (singleton) berisi 5 makalah sintetis dalam kode (`c1111111…` s.d. `c5555555…`) yang diindeks di memori; di worker digabung dengan korpus DB berstatus `INDEXED`.

### 4.5 Eksekusi audit
`execute_audit_pipeline(db, task_id, doc_id)` (sinkron): PROCESSING (10%) → ekstraksi teks (25%) → muat indeks korpus (40%) → jalankan agregator → simpan `AuditSentence` dan `AuditReport` → SUCCESS (100%). Pada error: rollback, status FAILED + `error_message`, lalu raise. Pengiriman: `DocumentService` mengecek worker Celery hidup via `inspect().ping()` (timeout 0,3 s); jika tidak ada, menjalankan pipa di **thread daemon** lokal. `AuditService.create_audit_task` mencoba `.delay()` lalu thread bila gagal. Progres antar-tahap di DB hanyalah penanda yang di-commit berurutan setelah pipa selesai, bukan progres nyata per tier.

### 4.6 Konfigurasi (`core/config.py`)
Semua dari env (`.env`, `../.env`, case-sensitive, `extra=ignore`). Default berupa nilai pengembangan (secret, DB, Midtrans demo). Nilai penting: `ACCESS_TOKEN_EXPIRE_MINUTES` default **1440** di kode vs **15** di `.env.example`; `MAX_FILE_SIZE_MB=50`; `ALLOWED_EXTENSIONS=pdf,docx,txt`; bobot dan parameter Winnowing; `CELERY_*` ke Redis; timezone Celery `Asia/Jakarta`, batas waktu tugas 25/30 menit.

## 5. Arsitektur Frontend

- **Aturan wajib** (`frontend/MODULAR_RULES.md`, `.cursorrules`, `.agents/rules/*`): view hanya orkestrator (±150–200 baris); komponen di `components/<domain>/` dengan barrel `index.ts`; komponen umum dari `components/common`; logika async di `composables/`; props/emits bertipe, tanpa `any`; `noUnusedLocals/Parameters` aktif; sebelum selesai jalankan `npx vue-tsc --noEmit` dan `npm run build`. Aturan anti-AI-slop: tanpa `transition: all`, gradien neon, `shadow-2xl`, animasi >200 ms; fokus ring wajib; angka tabular/mono. Sebagian aturan ini sudah dilanggar oleh `AdminView.vue` (1.172 baris) dan `UserManagementTable.vue` (885 baris).
- **Rute** (`router/index.ts`): `/` landing, `/dashboard`, `/audits/:id`, `/login`, `/register` (guestOnly), `/corpus` (REVIEWER, ADMIN), `/billing`, `/verify/:uuid?` (publik), `/admin` (ADMIN), catch-all → `/`. Guard di `utils/navigation.ts::evaluateNavigationGuard` (fungsi murni, diuji). Navbar bersegmen per peran; ADMIN tidak melihat Beranda/Saldo/Upload, dan di `/admin` serta `/corpus` (sebagai ADMIN) navbar publik + footer disembunyikan karena konsol admin punya sidebar sendiri.
- **State**: Pinia `auth` (token + user di `localStorage`, `tokenBalance` fallback 5, `fetchProfile` saat mount, logout pada 401 profil) dan `audit` (`pollTaskStatus` dengan `setInterval` 2 s; parameter `onComplete` tidak dipakai). Composable: `useNotification`, `usePolling`, `useFileUpload`, `useModal`.
- **HTTP**: axios `baseURL = VITE_API_BASE_URL || /api/v1`, `withCredentials`, header Bearer dari `localStorage`; interceptor 401 hanya menghapus token lokal (tidak ada alur refresh). Vite dev server port 5173 dengan proxy `/api` → `localhost:8000`.
- **Domain komponen**: common (Alert, Badge, Button, EmptyState, Modal, ModernCard, SkeletonLoader, StatCard, ToastContainer), dashboard, audit (ScoreSummaryCard, SideBySideDiff, SentenceDetailModal, ExportReportActions, MatchedSourcesTable) + HeatmapViewer/SimilarityGauge/TierLegend di root, billing, corpus, auth, landing (Hero, PipelineTiersGrid, FeatureHighlights, DashboardShowcaseWindow, InteractiveDemoSnippet, InvertedDarkSection), verify, admin.
- **Evolusi desain** (dari git log): Audyr/Plus Jakarta → emoji dan titik dekoratif dihapus (gaya utilitarian akademik) → sistem desain "Steep" (serif editorial, kartu 24 px, pill) → navbar kapsul mengambang yang menyusut saat scroll → konsol admin dengan sidebar tetap dan palet ink-black.

## 6. Model Peran & Kuota

| Peran | Saldo awal | Akses |
|---|---|---|
| TRIAL | 5 (register) | Dashboard, upload/audit, billing, verifikasi |
| PREMIUM | — (tampil badge PREMIUM) | Sama seperti TRIAL; tidak ada logika backend yang membedakan |
| REVIEWER | 100 (seed) | + Bank Korpus |
| ADMIN | 9.999 (seed) | Semua, konsol `/admin` |

Biaya audit 1 (TIER1_ONLY) / 2 (FULL) token. Top-up lewat Midtrans Snap **simulasi** (token Snap dibuat lokal `SNAP-<uuid>`; kredit terjadi saat webhook `settlement/capture`).

## 7. Basis Data & Infrastruktur

- `docker compose up -d` menjalankan `veritext_postgres` (pgvector:pg16, port 5432, healthcheck) dan `veritext_redis`. `db/init/*.sql` dieksekusi otomatis saat volume pertama kali dibuat: ekstensi (pgcrypto, vector), 14 tabel + indeks (termasuk HNSW cosine pada `document_chunks.embedding`, aturan immutable untuk audit log), seed 4 pengguna (admin, dosen, azriel, siti) + dompet + 1 dokumen korpus dengan 2 chunk (vektor konstan) + 2 fingerprint dummy.
- Dua jalur skema yang harus disinkronkan manual: Alembic `0001_initial_schema.py` dan SQL `0001_initial_schema.sql`. Belum ada migrasi 0002.
- Ketidakkonsistenan seed: SQL memberi akun azriel 3 token dan README db menyebut 3, sedangkan kode login (`auth_service`) membuat akun serupa dengan 5 token.

## 8. Pengujian

| Suite | Jumlah | Status yang diverifikasi hari ini |
|---|---|---|
| Backend pytest/unittest: `test_architecture`, `test_backend`, `test_engine` | 54 | **54 lulus** (`pytest --ignore` dua modul di bawah) |
| `test_pdf_certificate.py` | ±2 | **Tidak bisa dikoleksi**: `ModuleNotFoundError: qrcode` |
| `test_whitebox_suites.py` (73 kasus: 39 happy, 22 bad, 12 blocker, 7 fitur) | 73 | **Tidak bisa dikoleksi**: impor `app.api` → `reports` → `pdf_certificate_service` → `qrcode`. Percobaan memasang `reportlab` terbaru ditolak karena Python 3.9 |
| Frontend `npm test` (guard navigasi) | 25 | **25 lulus** |

`TESTING_WHITEBOX_VERITEXT_AI.md` mengklaim 129/129 lulus (56 + 73) di mesin yang berbeda; klaim itu tidak bisa direproduksi di environment ini tanpa Python ≥ 3.11 dan dependensi lengkap. Whitebox suite memakai `MockAsyncSession` (tanpa DB nyata), jadi tidak menguji SQL, Celery, atau Postgres. Belum ada tes integrasi/E2E, tes komponen Vue, ataupun pengukuran akurasi (precision/recall) mesin deteksi, padahal SRS menyebutnya.

Perintah verifikasi yang dipakai proyek:
```bash
cd backend && python3 -m unittest discover -s tests -p "test_*.py" -v
cd frontend && npm test && npx vue-tsc --noEmit && npm run build
```

## 9. Dokumen & Proses Akademik

- **SRS** (IEEE 830, 24 Juni 2026) dan **SDD** (Juni 2026), keduanya ditulis Azriel. Isi SRS: pendahuluan, deskripsi umum, antarmuka eksternal, requirement fungsional, use case. Sisa salin-tempel dari proyek lain: teks "Produk perangkat lunak **StockVault**" (SRS 1.3); SRS juga menyebut "VUE.js 14" dan TanStack Query, padahal implementasi memakai Vue 3.5 + Pinia + axios.
- **PANDUAN_PRESENTASI_UTS.md**: skrip demo 15 menit (landing → upload/audit mahasiswa → verifikasi QR → korpus dosen → konsol admin → capaian + tanya jawab) dan daftar antisipasi pertanyaan dosen.
- **AI_USAGE.md** dan **docs/skills_mapping_ippl.md**: kebijakan penggunaan AI; 70 skill aktif dipetakan ke 8 fase proyek, 237 diarsipkan. Dokumen merujuk `AGENTS.md` yang **tidak ada** di repo.
- Seed kredensial demo tercantum di README (kata sandi seragam untuk akun seed).

## 10. Riwayat Pengerjaan (35 commit, 2026-10-18 s.d. 2026-10-21)

- 10-18: prototipe inti, konsol admin + role guard, tipografi Plus Jakarta Sans, mesin 4-tier end-to-end.
- 10-19: README/UTS, CRUD admin (user, reset password), segmentasi tab admin, mode "Real" (hapus default mock), perbaikan numpy truthiness tier-2, PDF sertifikat valid (ReportLab), jalankan audit tanpa Celery, dokumen presentasi, hapus emoji.
- 10-20: sistem desain Steep, landing editorial, navbar kapsul/kolaps saat scroll, konsol admin terpadu + integrasi korpus, skill `refero-design`.
- 10-21: 73 kasus whitebox, commit "mau di ripiu ibnu nopal." (pesan commit tidak deskriptif).

## 11. Temuan Terverifikasi dari Kode (urut keparahan)

Seluruhnya dibaca langsung dari sumber; tidak ada yang dieksploitasi atau dijalankan terhadap server.

**Keamanan / kebenaran**
- **F1. Bypass login seed (kritis).** `services/auth_service.py:authenticate_user` menerima kata sandi literal `VeriText#2026` untuk `admin@veritext.ai`, `dosen@kampus.ac.id`, `azriel@kampus.ac.id` **tanpa memeriksa hash**, dan membuat akun itu otomatis bila belum ada (termasuk ADMIN dengan 9.999 token). Hash seed di `03_seed_dml.sql` memang **tidak cocok** dengan kata sandi itu (diverifikasi dengan bcrypt), jadi bypass ini yang membuat login seed berfungsi. Efek: kata sandi admin yang diganti lewat UI tetap bisa dilewati. Wajib dihapus sebelum deploy apa pun; perbaikan benar = seed dengan hash valid.
- **F2. Laporan dan PDF terbuka.** `GET /reports/{id}` hanya mewajibkan login, tidak memeriksa pemilik; `GET /reports/{id}/export-pdf` tidak mewajibkan autentikasi sama sekali (parameter `token` diabaikan) dan memuat nama pengguna + institusi. UUID tidak mudah ditebak, tetapi `verification_uuid`/`report_id` bocor lewat tautan verifikasi dan respons lain.
- **F3. Webhook pembayaran tanpa signature di mode default.** `ENVIRONMENT` default `development`, sehingga `POST /billing/webhook` dengan `order_id` yang valid dan `transaction_status=settlement` mengkredit token tanpa signature.
- **F4. Secret dan masa berlaku token.** Default `SECRET_KEY`/`JWT_SECRET_KEY` ada di kode; akses token default 24 jam; cookie refresh `secure=False`; refresh token tidak dirotasi; tidak ada rate limit meski kolom `failed_login_count`/`lockout_until` ada (tidak dipakai).
- **F5. Debit token rawan balapan.** Saldo dibaca tanpa `FOR UPDATE`; dua audit paralel bisa sama-sama lolos cek. CHECK `balance >= 0` di DB hanya menggagalkan salah satunya dengan error 500, bukan 402.
- **F6. Admin.** Aksi admin (CRUD user, adjust token, status) tidak menulis `audit_logs` (hanya purge yang menulis), padahal UI menampilkan "Log Audit"; admin dapat menghapus dirinya sendiri atau admin terakhir; `PUT /admin/users/{id}` membuat pengguna baru bila tidak ditemukan; role tidak divalidasi di skema (hanya CHECK DB).
- **F7. Klaim UU PDP.** `DELETE /documents/{id}` hanya soft delete dan berkas fisik tetap ada sampai admin memanggil `purge-retention`, tetapi pesan respons menyatakan "deleted permanently".

**Fungsionalitas yang berbeda dari klaim**
- **F8. Tier 2 bukan MiniLM/HNSW di praktik.** `sentence-transformers` tidak ada di `requirements.txt`/`pyproject.toml`; jalur nyata = embedding hash deterministik buatan sendiri. Pencarian kemiripan dilakukan di Python (kalimat × chunk, O(n·m)); tidak ada satu pun query pgvector (`<=>`) di kode aplikasi, jadi indeks HNSW di DDL tidak dipakai pipa. README/SDD yang menyebut MiniLM + ANN HNSW menggambarkan target, bukan perilaku saat ini.
- **F9. Ingest korpus ZIP tidak mengekstrak ZIP.** `index_corpus_document` memanggil `extract_text_from_file` pada berkas `.zip`; ekstensi itu jatuh ke fallback "baca biner dan decode utf-8 dengan replace", sehingga yang diindeks adalah sampah biner. Kegagalan `.delay()` ditelan diam-diam (status tetap `PENDING_INDEX` selamanya). `reindex-hnsw` hanya mengembalikan pesan sukses.
- **F10. Stub:** forgot/reset password, PDF invoice, health-metrics (CPU 18,5 / memori 42,1 / redis HEALTHY / celery 0 tetap), progres audit (hanya penanda berurutan).
- **F11. Korpus tiruan.** Pembanding efektif hanyalah 5 paragraf sintetis di kode + apa pun yang diindeks admin; skor "plagiarisme" terhadap dunia nyata praktis nol.
- **F12. Frontend:** `audit.ts::pollTaskStatus` memiliki parameter `onComplete` yang tidak dipanggil; tidak ada refresh token di klien; `tokenBalance` fallback 5 menyembunyikan state kosong.

**Lingkungan & proses**
- **F13.** Python proyek ≥ 3.11 tetapi `.venv` 3.9.6 dan tidak ada Python lain di mesin; `qrcode`/`reportlab` tidak terpasang di venv; 2 modul tes tidak jalan. `requirements.txt` tidak memuat `sentence-transformers`.
- **F14.** Docker tidak aktif; kondisi DB/Redis tidak diketahui; `uploads/` kosong sehingga belum pernah ada audit nyata di mesin ini (atau sudah dibersihkan).
- **F15.** README menyebut folder `backend/scripts/` dan `AGENTS.md` (AI_USAGE) yang tidak ada; SRS memuat sisa teks "StockVault".

## 12. Cara Menjalankan (menurut README, dengan koreksi lingkungan)

```bash
cp .env.example .env
docker compose up -d                     # postgres + redis (Docker harus aktif)
cd backend && python3.11 -m venv .venv   # butuh Python >= 3.11 (belum ada di mesin ini)
source .venv/bin/activate && pip install -r requirements.txt
alembic upgrade head                     # atau biarkan db/init yang membuat skema saat volume baru
uvicorn app.main:app --reload --port 8000
celery -A app.workers.celery_app worker --loglevel=info   # opsional; tanpa ini audit jalan di thread lokal
cd ../frontend && npm install && npm run dev               # http://localhost:5173
```

Catatan: skema bisa dibuat dua kali (init SQL Docker + Alembic); jalankan salah satu pada DB kosong, bukan keduanya.

## 13. Pertanyaan/Keputusan Terbuka untuk Pemilik

1. Apakah demo UTS tetap memakai login seed bypass (F1)? Bila ya, tandai jelas sebagai "mode demo" dan nonaktifkan lewat flag env; bila tidak, ganti hash seed.
2. Apakah Tier 2 akan memakai `sentence-transformers` sungguhan + query pgvector, atau presentasi diubah agar jujur menyebut embedding deterministik?
3. Perbaiki ingest ZIP (ekstrak lalu indeks per berkas) atau ubah UI menjadi unggah berkas tunggal?
4. Siapkan Python 3.11+ agar 73 tes whitebox bisa dijalankan ulang dan klaim 129/129 terbukti.
5. Mau dilanjutkan fitur 4–7 ke status "selesai" (README baru menandai 1–3), mana yang diprioritaskan sebelum UTS?
