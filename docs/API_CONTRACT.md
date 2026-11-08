# API Contract Specification: VeriText AI

Dokumen ini mendefinisikan kontrak pertukaran data RESTful API resmi antara Frontend Vue 3.5 SPA, Backend FastAPI 0.115, dan integrasi pihak ketiga (Midtrans Snap, Dual-Scope Academic APIs). Seluruh 25 endpoint dan 17 kode galat pada dokumen ini berkorespondensi 100% dengan `SDD_Sistem_Deteksi_Plagiarisme_Hybrid.md` Sub-bab 3.5 dan `docs/DATABASE_SCHEMA.md`.

---

## 1. Standar Format Respons (Envelope Pattern)

Seluruh endpoint API VeriText AI wajib mengembalikan respons dalam format pembungkus (*envelope*) standar berformat JSON (`Content-Type: application/json`).

### 1.1. Respons Sukses Standar
```json
{
  "success": true,
  "data": {},
  "message": "Deskripsi status operasi yang berhasil dilakukan.",
  "meta": {
    "timestamp": "2026-06-24T10:00:00.000Z",
    "version": "1.0",
    "request_id": "c1f7b8a2-3e4d-4a1b-9f2c-5d8e7a6b5c4d"
  }
}
```

### 1.2. Respons Galat Standar
```json
{
  "success": false,
  "error": {
    "code": "CHAT_001",
    "message": "Permintaan ditolak: Melanggar batas etika akademik (Academic Assistant Guardrail).",
    "details": null
  },
  "meta": {
    "timestamp": "2026-06-24T10:00:01.000Z",
    "version": "1.0",
    "request_id": "c1f7b8a2-3e4d-4a1b-9f2c-5d8e7a6b5c4d"
  }
}
```

---

## 2. Katalog Lengkap 25 Endpoint API per Modul

### 2.1. Modul Autentikasi dan Profil Akun (`mod-auth` — Endpoint Otentikasi & Google SSO)

| Method | Endpoint | Auth | Request Body | Response `data` | Deskripsi |
|---|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Publik | `{"email": "str", "password": "str", "full_name": "str"}` | `{"access_token": "jwt", "token_type": "bearer", "user": {"id": "uuid", "email": "str", "full_name": "str", "role": "FREE", "token_balance": 5}}` | Registrasi akun baru mandiri; alokasi 5 Token & 3x Kuota Trial AI. |
| `POST` | `/api/v1/auth/login` | Publik | `{"email": "str", "password": "str"}` | `{"access_token": "jwt", "token_type": "bearer", "user": {"id": "uuid", "email": "str", "full_name": "str", "role": "FREE", "token_balance": 5}}` | Autentikasi email penuh & kata sandi; terbitkan JWT dan HttpOnly Refresh Cookie (7d). Alias dinonaktifkan. |
| `GET` | `/api/v1/auth/google/login` | Publik | `None` | `HTTP 307 Redirect` | Inisiasi Google OAuth 2.0; set HttpOnly cookie `g_oauth_state` (CSRF), redirect ke Google Auth. Return 503 jika `GOOGLE_CLIENT_ID` kosong. |
| `GET` | `/api/v1/auth/google/callback` | Publik | Query: `code`, `state` | `HTTP 307 Redirect` | Callback Google OAuth. Validasi CSRF state cookie; jika user ada: terbitkan sesi dan redirect `/auth/callback?token=...`; jika user baru: terbitkan signup ticket JWT (10m) dan redirect `/onboarding?ticket=...`. |
| `POST` | `/api/v1/auth/google/verify` | Publik | `{"credential": "str"}` | `TokenResponse` / `HTTP 409` | Verifikasi Google ID Token (One Tap/GIS). Validasi audience & verified_email. Jika user ada: kembalikan TokenResponse; jika user baru: HTTP 409 `{"code": "SIGNUP_REQUIRED", "signup_ticket": "jwt"}`. |
| `POST` | `/api/v1/auth/google/complete` | Publik | `{"ticket": "str", "full_name": "str", "password": "str"}` | `{"access_token": "jwt", "token_type": "bearer", "user": {...}}` | Menyelesaikan pendaftaran akun Google dengan signup ticket; validasi password kuat; alokasi User FREE + TokenWallet 5 token & 3 trial AI secara atomik; set HttpOnly refresh cookie. |
| `POST` | `/api/v1/auth/refresh` | Refresh Cookie | `None` | `{"access_token": "jwt", "refresh_token": "str"}` | Rotasi refresh token di tabel `sessions` dan penerbitan Access Token JWT baru. |
| `POST` | `/api/v1/auth/logout` | Bearer JWT | `None` | `{}` | Pencabutan refresh token dari tabel `sessions` dan pembersihan cookie sesi peramban. |
| `GET` | `/api/v1/auth/me` | Bearer JWT | `None` | `{"id": "uuid", "email": "str", "full_name": "str", "role": "FREE/PREMIUM/ADMIN", "token_balance": 5}` | Mengambil profil pengguna aktif dan sisa saldo token komputasi. |
| `PATCH` | `/api/v1/auth/profile` | Bearer JWT | `{"full_name": "str"}` | `{"id": "uuid", "full_name": "str", ...}` | Memperbarui nama lengkap pengguna aktif. |
| `PATCH` / `POST` | `/api/v1/auth/change-password` | Bearer JWT | `{"old_password": "str", "new_password": "str"}` | `{}` | Memvalidasi kata sandi lama, menyimpan hash Bcrypt baru, dan mencabut seluruh sesi aktif. |
| `DELETE` | `/api/v1/auth/me` | Bearer JWT | `None` | `{}` | Hard-delete cascading data pribadi & naskah pengguna sesuai UU PDP No. 27/2022. |
| `POST` | `/api/v1/auth/forgot-password` | Publik | `{"email": "str"}` | `{}` | Mengirim email reset kata sandi dengan token acak 64 karakter (OWASP Zero-Leak). |
| `POST` | `/api/v1/auth/reset-password` | Publik | `{"token": "str", "new_password": "str"}` | `{}` | Reset kata sandi dengan token sekali pakai (anti-replay) dan revokasi sesi lama. |

---

### 2.2. Modul Dokumen dan Pra-pemrosesan (`mod-preprocessor` — 4 Endpoint)

| Method | Endpoint | Auth | Request Body | Response `data` | Deskripsi |
|---|---|---|---|---|---|
| `POST` | `/api/v1/documents/upload` | Bearer JWT | `multipart/form-data`: `file` (.pdf/.docx/.txt <= 15 MB) atau `text: str`, `title: str` | `{"document_id": "uuid", "title": "str", "file_size_bytes": 1450200, "word_count": 2150, "token_cost": 1, "sentences_count": 84, "is_valid": true}` | Validasi magic bytes MIME, ekstraksi teks, segmentasi kalimat, cek batas 2.500 kata `FREE`, dan hitung biaya token $\min(5, \lceil \text{kata}/2500 \rceil)$. |
| `POST` | `/api/v1/documents/estimate` | Bearer JWT | `multipart/form-data`: `file` (.pdf/.docx/.txt <= 15 MB) | `{"word_count": 5100, "token_cost": 3, "within_plan": true, "max_free_words": 2500}` | Menghitung jumlah kata dan biaya audit tanpa menyimpan berkas dan tanpa memotong saldo. Biaya = `min(5, ceil(kata / 2500))` token. `within_plan` bernilai `false` bila akun FREE melebihi 2.500 kata. |
| `GET` | `/api/v1/documents` | Bearer JWT | Query: `page=1&limit=20` | `{"total": 12, "items": [{"id": "uuid", "title": "str", "word_count": 2150, "token_cost": 1, "created_at": "datetime"}]}` | Mengambil daftar riwayat naskah milik pengguna aktif. |
| `GET` | `/api/v1/documents/{id}` | Bearer JWT | `None` | `{"id": "uuid", "title": "str", "original_filename": "str", "word_count": 2150, "token_cost": 1, "created_at": "datetime"}` | Mengambil detail metadata naskah spesifik milik pengguna aktif. |
| `DELETE` | `/api/v1/documents/{id}` | Bearer JWT | `None` | `{"document_id": "uuid", "status": "PERMANENTLY_DELETED"}` | Mengeksekusi hard-delete cascading berkas fisik, rekaman `documents`, `audit_tasks`, `audit_sentences`, `audit_reports`, `chat_sessions`, dan `chat_messages` (UU PDP). |

---

### 2.3. Modul Pipeline Audit Deteksi Plagiarisme (`mod-pipeline-*` — 3 Endpoint)

| Method | Endpoint | Auth | Request Body | Response `data` | Deskripsi |
|---|---|---|---|---|---|
| `POST` | `/api/v1/audits/execute` | Bearer JWT | `{"document_id": "uuid"}` | `{"task_id": "uuid", "status": "QUEUED", "tokens_deducted": 1, "new_balance": 4}` | Memotong saldo `token_wallets` secara atomik (`SELECT ... FOR UPDATE`), mencatat `DEBIT_AUDIT` di `token_transactions`, dan mengirim task ke Celery Redis. |
| `GET` | `/api/v1/audits/{task_id}/status` | Bearer JWT | `None` | `{"task_id": "uuid", "status": "PROCESSING", "progress_pct": 65, "current_step": "Step 2: Semantic SBERT", "report_id": "uuid\|null"}` | Endpoint smart polling adaptif (3s saat `QUEUED`, 1.5s saat `PROCESSING`) untuk memantau penyelesaian audit. |
| `GET` | `/api/v1/audits/{id}/report` | Bearer JWT | `None` | `{"report_id": "uuid", "task_id": "uuid", "composite_score": 18.5, "tiers": {"lexical": 22.0, "semantic": 15.0, "stylometric": 8.0}, "sentences": [...], "sources": [...]}` | Mengambil data lengkap laporan naskah beranotasi Interactive Heatmap (`NONE`, `RED`, `ORANGE`, `YELLOW`, `RESOLVED_GREEN`) dan daftar sumber. |

---

### 2.4. Modul AI Chatbot Asisten dan Parafrase Instan (`mod-assistant` — 3 Endpoint)

| Method | Endpoint | Auth | Request Body | Response `data` | Deskripsi |
|---|---|---|---|---|---|
| `POST` | `/api/v1/chat/message` | Bearer JWT | `{"document_ids": ["uuid"] (maks. 3, opsional), "document_id": "uuid\|null" (lama, setara satu elemen document_ids), "session_id": "uuid\|null", "sentence_id": "uuid\|null", "prompt": "str (1-4000)"}` | `{"message_id": "uuid", "session_id": "uuid", "role": "ASSISTANT", "content": "str", "active_engine": "GEMINI_FLASH\|DEEPSEEK_9ROUTER", "ai_trial_remaining": 2, "balance": 4, "ai_chat_allowance_remaining": 9}` | Tanpa `session_id` membuat sesi baru yang terhubung ke `document_ids`; dengan `session_id` melanjutkan sesi (naskah konteks diambil dari sesi). Naskah harus milik pengguna (`DOC_004`, 404). Enam kalimat paling relevan per naskah dipilih dengan embedding MiniLM lalu masuk ke prompt bersama enam pesan terakhir. Memeriksa Academic Guardrail (`CHAT_001`), memotong 1 kuota trial (`FREE`) atau 1 sub-kredit chat (`PREMIUM`: 1 Token = 10 interaksi), dan memanggil Dual-Engine LLM Gateway. |
| `GET` | `/api/v1/chat/sessions` | Bearer JWT | `None` | `[{"id": "uuid", "title": "str", "document_ids": ["uuid"], "last_message": "str\|null", "message_count": 4, "updated_at": "iso8601"}]` | Daftar sesi asisten milik pengguna, terbaru lebih dulu. |
| `GET` | `/api/v1/chat/sessions/{id}/messages` | Bearer JWT | `None` | `[{"id": "uuid", "role": "USER\|ASSISTANT", "content": "str", "mode": "CONSULTATION", "created_at": "iso8601"}]` | Riwayat pesan sesi, urut waktu naik. Sesi milik orang lain mengembalikan 404. |
| `DELETE` | `/api/v1/chat/sessions/{id}` | Bearer JWT | `None` | `{}` | Menghapus sesi beserta seluruh pesannya secara permanen. |
| `POST` | `/api/v1/chat/paraphrase` | Bearer JWT | `{"sentence_id": "uuid", "mode": "SENTENCE\|PARAGRAPH\|FULL_PAGE"}` | `{"sentence_id": "uuid", "mode": "SENTENCE", "variations": [{"option_id": 1, "style": "Formal Akademik", "text": "str", "predicted_score": 8.5}, ...]}` | Menghasilkan 3 variasi parafrase ilmiah dalam `suggested_options` JSONB lengkap dengan prediksi penurunan skor kemiripan. |
| `POST` | `/api/v1/chat/apply-paraphrase` | Bearer JWT | `{"sentence_id": "uuid", "selected_text": "str"}` | `{"sentence_id": "uuid", "current_text": "str", "match_type": "RESOLVED_GREEN", "new_similarity": 6.2, "new_composite_score": 14.1, "is_modified": true}` | Mengganti `current_text` pada `audit_sentences` secara in-place, menghitung ulang skor komposit di `audit_tasks`, dan mengubah `match_type` menjadi `RESOLVED_GREEN`. |

---

### 2.5. Modul Pelaporan, Sertifikasi dan Verifikasi Publik (`mod-report` — 2 Endpoint)

| Method | Endpoint | Auth | Request Body | Response `data` | Deskripsi |
|---|---|---|---|---|---|
| `GET` | `/api/v1/reports/{id}/download` | Bearer JWT (`PREMIUM`) | `None` | Binary stream: `application/pdf` | Mengunduh Laporan Audit Resmi PDF beresolusi cetak berstempel digital dan Dynamic QR Code (`REP_001` jika diakses oleh `FREE`). |
| `GET` | `/api/v1/reports/verify/{uuid}` | Publik | `None` | `{"valid": true, "certificate_uuid": "uuid", "document_title": "str", "author": "str", "audit_date": "datetime", "composite_score": 14.1}` | Portal validasi publik tanpa login untuk memverifikasi keaslian sertifikat via `certificate_uuid` (`REP_002` jika tidak ditemukan/dihapus). |

---

### 2.6. Modul Monetisasi Billing dan Pemantauan Admin (`mod-billing` & `mod-admin` — 7 Endpoint)

| Method | Endpoint | Auth | Request Body | Response `data` | Deskripsi |
|---|---|---|---|---|---|
| `POST` | `/api/v1/billing/checkout` | Bearer JWT | `{"purchase_scheme": "BY_TOKEN\|BY_PACKAGE", "token_amount": 15, "package_type": "STARTER\|SKRIPSI_PRO\|RISET_INTENSIF\|null"}` | `{"order_id": "str", "gross_amount": 25000, "snap_token": "str", "snap_redirect_url": "str"}` | Membuat record `invoices` berstatus `PENDING` dan meminta Snap Token ke Midtrans API. |
| `POST` | `/api/v1/billing/webhook` | Midtrans SHA-512 | `{"order_id": "str", "status_code": "200", "gross_amount": "25000.00", "signature_key": "str", "transaction_status": "settlement"}` | `{"status": "ok"}` | Memvalidasi signature SHA-512, mengunci baris `invoices` & `token_wallets` (`FOR UPDATE`), memperbarui status ke `SETTLEMENT`, menambah saldo token, dan mengubah `users.role = 'PREMIUM'`. |
| `GET` | `/api/v1/billing/invoices` | Bearer JWT | `None` | `{"items": [{"order_id": "str", "purchase_scheme": "BY_PACKAGE", "token_amount": 15, "gross_amount": 25000, "status": "SETTLEMENT", "settled_at": "datetime"}]}` | Menampilkan riwayat transaksi pembayaran pengguna aktif beserta tautan unduh Invoice PDF. |
| `GET` | `/api/v1/admin/analytics` | Bearer JWT (`ADMIN`) | `None` | `{"total_documents": 1420, "avg_similarity": 16.4, "total_revenue": 8450000, "active_users": 640}` | Dasbor statistik analitik global penggunaan sistem (murni HTTP `GET` / 100% Read-Only). |
| `GET` | `/api/v1/admin/transactions` | Bearer JWT (`ADMIN`) | Query: `limit=50` | `{"total_revenue": 8450000, "items": [{"order_id": "str", "gross_amount": 25000, "status": "SETTLEMENT", "settled_at": "datetime"}]}` | Log riwayat transaksi pembayaran Midtrans secara real-time (murni HTTP `GET` / 100% Read-Only). |
| `GET` | `/api/v1/admin/system-health` | Bearer JWT (`ADMIN`) | `None` | `{"celery_workers": 4, "queue_depth": 2, "redis_mem_mb": 145, "pgvector_latency_ms": 18}` | Telemetri kesehatan infrastruktur Celery worker, Redis, dan pgvector (murni HTTP `GET` / 100% Read-Only). |
| `GET` | `/api/v1/admin/audit-logs` | Bearer JWT (`ADMIN`) | Query: `limit=100` | `{"items": [{"timestamp": "datetime", "actor_id": "uuid", "event_type": "LOGIN_FAILURE", "ip_address": "str", "description": "str"}]}` | Meninjau rekaman log audit keamanan sistem pada tabel `audit_logs` (murni HTTP `GET` / 100% Read-Only). |

---

## 3. Katalog Lengkap 17 Kode Galat Terpusat (Selaras SDD Tabel 3.11)

| Kode Error | HTTP Status | Deskripsi Standar | Endpoint Terkait |
|---|---|---|---|
| `AUTH_001` | `401 Unauthorized` | Email atau kata sandi tidak valid. | `POST /api/v1/auth/login` |
| `AUTH_002` | `401 Unauthorized` | Access token JWT telah kedaluwarsa atau signature tidak valid. | Seluruh endpoint terproteksi |
| `AUTH_003` | `403 Forbidden` | Peran pengguna tidak memiliki hak akses (RBAC violation). | `/api/v1/admin/*`, `/reports/download` |
| `DOC_001` | `413 Payload Too Large` | Ukuran berkas naskah yang diunggah melebihi batas maksimum 15 MB. | `POST /api/v1/documents/upload` |
| `DOC_002` | `400` / `422` | Berkas ditolak: nama tanpa ekstensi, berjalur, berekstensi ganda, atau ekstensi selain `.pdf`/`.docx`/`.txt` (400); isi tidak sesuai ekstensi atau MIME (PDF harus diawali `%PDF-`, DOCX harus ZIP berisi `word/document.xml`, TXT tanpa byte NUL dan dapat didekode), DOCX berpotensi ZIP bomb (hasil dekompresi > 50 MB atau rasio > 100x), atau PDF > 400 halaman (422). | `POST /api/v1/documents/upload`, `POST /api/v1/documents/estimate` |
| `DOC_003` | `422 Unprocessable Entity` | Naskah memiliki kurang dari 50 kata (tidak memenuhi syarat analisis). Berkas tidak disimpan dan saldo tidak dipotong. Juga berlaku pada estimasi. | `POST /api/v1/documents/upload`, `POST /api/v1/documents/estimate` |
| `DOC_006` | `422` / `429` | Pembatas beban: ekstraksi teks melebihi 30 detik (422); pengguna sudah memiliki 3 audit berstatus `QUEUED`/`PROCESSING` (429); lebih dari 10 unggahan atau estimasi per menit per pengguna (429, header `Retry-After: 60`; pembatas dilewati bila Redis tidak tersedia). | `POST /api/v1/documents/upload`, `POST /api/v1/documents/estimate` |
| `DOC_004` | `404 Not Found` | Dokumen yang diminta tidak ditemukan atau bukan milik pengguna aktif. | `GET/DELETE /api/v1/documents/{id}` |
| `DOC_005` | `402 Payment Required` | Naskah akun FREE melebihi batas 2.500 kata per dokumen. Berkas tidak disimpan dan saldo tidak dipotong. | `POST /api/v1/documents/upload`, `POST /api/v1/audits/start` |
| `AUDIT_001` | `402 Payment Required` | Saldo token tidak mencukupi untuk melakukan pemeriksaan naskah. | `POST /api/v1/audits/execute` |
| `AUDIT_002` | `400 Bad Request` | Batas kata Free User terlampaui (maksimal 2.500 kata per dokumen). | `POST /api/v1/audits/execute` |
| `CHAT_001` | `400 Bad Request` | Pelanggaran Guardrail: Permintaan di luar etika akademik ditolak. | `POST /api/v1/chat/message` |
| `CHAT_002` | `402 Payment Required` | Batas kuota Trial AI Chatbot/Parafrase (3x) untuk Free User telah habis. | `POST /api/v1/chat/*` |
| `BILL_001` | `403 Forbidden` | Verifikasi signature SHA-512 webhook Midtrans gagal (untrusted source). | `POST /api/v1/billing/webhook` |
| `BILL_002` | `404 Not Found` | Nomor order transaksi pembayaran tidak ditemukan di basis data. | `POST /api/v1/billing/webhook` |
| `BILL_003` | `400 Bad Request` | Transaksi pembayaran telah kedaluwarsa atau dibatalkan oleh pengguna. | `POST /api/v1/billing/checkout` |
| `BILL_004` | `400 Bad Request` | Jumlah token yang dibeli kurang dari batas minimum pembelian (min. 5 token). | `POST /api/v1/billing/checkout` |
| `REP_001` | `403 Forbidden` | Unduh laporan PDF resmi hanya dapat diakses oleh akun Premium User. | `GET /api/v1/reports/{id}/download` |
| `REP_002` | `404 Not Found` | Kode QR atau sertifikat verifikasi keaslian naskah tidak valid/dihapus. | `GET /api/v1/reports/verify/{uuid}` |
