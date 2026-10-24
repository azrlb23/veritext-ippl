# VeriText AI — Laporan Audit Keamanan (Pemindaian Kebocoran)

> Tanggal: 2026-10-23. Metode: pembacaan kode (read-only) oleh dua subagen (`code-reviewer` untuk backend, `frontend-developer` untuk frontend/infra) + verifikasi ulang klaim kunci oleh penyusun. Tidak ada eksploit yang dijalankan dan tidak ada kode proyek yang diubah.
> Cakupan: seluruh repo `/Users/azrlb23/Documents/IPPL`. Konteks arsitektur: lihat `docs/PROJECT_CONTEXT.md`.
> Catatan: temuan F1–F15 di PROJECT_CONTEXT.md bagian 11 dilengkapi di sini; bila ada selisih, dokumen ini lebih baru.

## Ringkasan

~30 temuan: 1 Kritis, ~8 Tinggi, ~10 Sedang, sisanya Rendah. Tidak ada temuan XSS/SQL injection/path traversal. `.env` tidak pernah masuk riwayat git. Untuk demo di laptop sendiri, prioritas tertinggi adalah bagian A dan B (bisa dimanfaatkan tanpa login atau dari jaringan yang sama).

Label verifikasi: **[V]** dikonfirmasi langsung oleh penyusun dari kode; **[A]** dilaporkan subagen dari pembacaan kode, belum diulang penyusun.

## A. Bocor tanpa/hampir tanpa autentikasi

| ID | Sev | Lokasi | Temuan |
|---|---|---|---|
| A1 | Tinggi | `api/v1/reports.py` `export-pdf` | Tidak butuh autentikasi (parameter `token` diabaikan). PDF memuat nama penulis, institusi, judul naskah. **[V]** |
| A2 | Tinggi | `api/v1/reports.py` `get_report` | Hanya cek login, tanpa cek pemilik (IDOR). Respons memuat `heatmap_annotations[].text_snippet` (potongan isi naskah orang lain) dan `pdf_path` (path server). **[V]/[A]** |
| A3 | Tinggi | `api/v1/reports.py` `/verify/{uuid}` | Publik, tanpa rate limit; mengembalikan nama asli, institusi, nama berkas, skor. Pesan "tidak ditemukan" vs "dihapus" berbeda. **[V]** |
| A4 | Tinggi | `docker-compose.yml:10-11,27-28` | Postgres 5432 dan Redis 6379 di-publish ke semua interface; Redis tanpa `requirepass` dan menjadi broker Celery; password Postgres punya default. **[V]** |
| A5 | Sedang | `frontend/vite.config.ts` | Dev server `host: 0.0.0.0` + proxy `/api` ke backend lokal; orang di LAN bisa memakai backend. **[V]** |

## B. Kredensial & secret

| ID | Sev | Lokasi | Temuan |
|---|---|---|---|
| B1 | **Kritis** | `core/config.py:16-17`, `.env.example` | `SECRET_KEY`, `JWT_SECRET_KEY`, password DB, kunci Midtrans punya default publik di git; `DEBUG=True` default; tanpa guard saat startup. Bila `.env` tidak menimpa, JWT ADMIN bisa dipalsukan. (Nilai `.env` lokal tidak dibaca.) **[V]** |
| B2 | Tinggi | `services/auth_service.py:74,100` | Bypass login: kata sandi seed diterima untuk 3 email seed tanpa cek hash, akun dibuat otomatis bila belum ada. Sebelumnya dibutuhkan karena hash seed salah. **[V]** |
| B3 | Tinggi | `db/init/03_seed_dml.sql`, `schemas/admin.py`, `api/v1/admin.py` | Seed berisi ADMIN dengan kata sandi yang terdokumentasi di README; default `VeriText#2026` juga dipakai saat admin membuat user dan pada upsert `PUT /admin/users`. Berlaku walau B2 dihapus. **[A]** |
| B4 | Info | `db/init/03_seed_dml.sql` (uncommitted) | Saat audit, berkas ini berstatus modified: keempat hash diganti dengan hash bcrypt yang **cocok** dengan kata sandi seed (diverifikasi). Perubahan dilakukan di luar sesi audit; B2 tidak lagi dibutuhkan untuk database baru. Volume Postgres yang sudah ada tidak menjalankan ulang init. **[V]** |

## C. Sesi & autentikasi

| ID | Sev | Lokasi | Temuan |
|---|---|---|---|
| C1 | Tinggi | `api/v1/auth.py`, `services/auth_service.py` | Tanpa rate limit/lockout (kolom `failed_login_count`/`lockout_until` tidak pernah dipakai). Register memberi 5 token gratis tanpa batas (alias `+tag` diterima). **[V]** |
| C2 | Tinggi | `api/v1/auth.py` `/refresh`, `/logout` | `Session.expires_at` tidak dicek; refresh token tidak dirotasi; ganti/reset password tidak mencabut sesi; logout butuh access token valid. **[V]** |
| C3 | Sedang | `api/v1/auth.py` | Cookie refresh `secure=False`, tanpa `path`; `delete_cookie` tidak cocok atributnya. **[V]** |
| C4 | Sedang | `core/config.py`, `core/security.py` | Token akses 24 jam default (contoh env: 15 menit); tanpa `jti/iss/aud`. **[V]** |
| C5 | Sedang | `frontend/src/stores/auth.ts` | Token akses di `localStorage`; `veritext_user` (role, saldo) dipercaya klien tanpa validasi — hanya mengubah tampilan UI, data tetap dijaga server. **[A]** |
| C6 | Sedang | `services/auth_service.py` | Enumerasi user: pesan "email sudah terdaftar"; login tidak melakukan kerja bcrypt untuk email tak dikenal (selisih waktu). **[A]** |
| C7 | Rendah | `api/v1/auth.py` | `forgot-password`/`reset-password` stub (membalas sukses tanpa memeriksa apa pun). **[V]** |
| C8 | Rendah | `frontend/src/services/api.ts` | `withCredentials: true` global; interceptor 401 hanya menghapus localStorage tanpa reset store Pinia. **[A]** |

## D. Uang & token

| ID | Sev | Lokasi | Temuan |
|---|---|---|---|
| D1 | Tinggi | `services/billing_service.py` | Signature webhook dilewati bila `ENVIRONMENT == "development"` (default). Nominal payload tidak dibandingkan dengan invoice; `fraud_status` diabaikan; perbandingan signature tidak konstan-waktu. **[V]** |
| D2 | Tinggi | `services/billing_service.py` | Dua webhook `settlement` paralel membaca `PENDING` dan sama-sama mengkredit (tanpa `FOR UPDATE`/update atomik). **[V]** |
| D3 | Sedang | `document_service.py`, `audit_service.py`, `admin.py` | Debit/penyesuaian saldo tanpa row lock; audit paralel bisa melewati cek saldo (CHECK DB menggagalkan satu dengan 500). **[V]** |
| D4 | Rendah | `billing_service.py` | 404 "Invoice order not found" membocorkan keberadaan order id. **[A]** |

## E. Data pengguna & UU PDP

| ID | Sev | Lokasi | Temuan |
|---|---|---|---|
| E1 | Tinggi | `api/v1/documents.py`, `audit_service.py`, `reports.py` | `DELETE /documents/{id}` hanya soft delete, pesan menyatakan "permanen". Berkas fisik, `audit_sentences`, dan snippet laporan tetap ada dan masih terakses lewat `/reports`; dokumen terhapus masih bisa diaudit ulang; daftar task masih menampilkan judulnya. Purge hanya manual oleh admin. **[V]/[A]** |
| E2 | Sedang | — | Tidak ada endpoint hapus akun mandiri; `delete_user_admin` tidak menghapus berkas unggahan dan gagal 500 bila user punya dokumen/task/invoice. **[A]** |
| E3 | Sedang | `workers/tasks.py`, `schemas/audit.py` | `str(exc)` disimpan di `error_message` dan dikembalikan lewat status audit (bisa berisi path/SQL). `main.py` mengembalikan detail error bila `DEBUG`. **[V]/[A]** |
| E4 | Info | `backend/uploads/` | Berisi 4 PDF (±8,6 MB, 19 Okt). Isi tidak dibuka. Di-gitignore, tetapi jangan ikut deploy/backup publik bila naskah asli. **[V]** |

## F. Validasi input & ketahanan

| ID | Sev | Lokasi | Temuan |
|---|---|---|---|
| F1 | Sedang | `services/pdf_certificate_service.py:217,223,229,337` | `document_title`, `user_name`, `institution`, judul sumber masuk ke `Paragraph(...)` tanpa escape. Markup ReportLab (mis. `<img src=...>`) dapat memicu fetch dari server atau 500. Mudah dipicu karena endpoint PDF tanpa auth (A1). **[V]** |
| F2 | Sedang | `services/document_service.py`, `corpus_service.py` | Hanya cek ekstensi nama berkas (tanpa magic byte); seluruh berkas dibaca ke memori sebelum cek ukuran; parsing PDF/DOCX tanpa batas halaman/ukuran (DOCX = ZIP, rawan zip bomb); `inspect().ping()` memblokir handler async; fallback thread daemon tanpa batas. **[A]** |
| F3 | Sedang | `api/v1/corpus.py`, `corpus_service.py`, `schemas/corpus.py` | Reviewer mana pun dapat mengubah/menghapus korpus milik orang lain tanpa audit log; respons membuka `stored_filename`, `uploaded_by`, `sha256_hash`; 409 hash identik membocorkan keberadaan berkas. Ingest ZIP tidak mengekstrak ZIP (jadi zip-slip belum relevan; indeks berisi sampah biner). **[A]/[V]** |
| F4 | Sedang | `api/v1/admin.py`, `schemas/admin.py` | `role` string bebas (hanya CHECK DB); tanpa guard diri sendiri/admin terakhir; upsert diam-diam di `PUT /users/{id}`; email duplikat → 500; token awal/penyesuaian tak dibatasi; reset password admin min 6 karakter tanpa pencabutan sesi. **[A]** |
| F5 | Rendah | `api/v1/audits.py`, `admin.py` | Wildcard `%`/`_` pada `ilike` tidak di-escape (dampak kecil, query tetap parameterized). **[A]** |
| F6 | Rendah | `api/v1/reports.py` | Parameter `?token=` dideklarasikan pada `export-pdf` (mengundang JWT di URL: log, Referer). **[V]** |

## G. Hardening, observabilitas, frontend

| ID | Sev | Lokasi | Temuan |
|---|---|---|---|
| G1 | Sedang | `main.py` | `/docs`, `/redoc`, `/openapi.json` selalu aktif; tanpa HSTS, `X-Content-Type-Options`, CSP, `Cache-Control: no-store`. CORS aman (hanya origin localhost), tetapi `allow_credentials=True` berarti tidak boleh pernah diganti `*`. **[V]/[A]** |
| G2 | Rendah | Log audit | Login, gagal login, perubahan role, kredit webhook, aksi korpus, dan hampir semua aksi admin tidak tercatat; `actor_ip` tidak pernah diisi. Hanya purge yang menulis `audit_logs`. **[V]** |
| G3 | Rendah | `frontend/src/utils/navigation.ts` | `to.fullPath` (termasuk query) masuk ke `?redirect=` di URL login. Sisi baca (`LoginView.vue`) aman dari open redirect. **[A]** |
| G4 | Rendah | `ExportReportActions.vue` | Tautan bagikan memakai `window.location.origin` (origin dev/LAN bisa tersalin). **[A]** |
| G5 | Rendah | `.gitignore` | Tidak ada kebocoran saat ini; pola `.env.production` dll. belum tercakup (hanya `.env.local`/`.env.*.local`). **[A]** |
| G6 | Info | `.agents/skills/flowchart-maker` | Skill mengirim isi diagram ke `kroki.io` (perilaku terdokumentasi); jangan beri arsitektur rahasia. Tidak ditemukan pola prompt injection atau blob base64 panjang di `.agents`. **[V]/[A]** |

## H. Yang diperiksa dan bersih

- Tidak ada `v-html`, `innerHTML`, `eval`; semua data tampil via `{{ }}` (ter-escape).
- `npm audit --omit=dev`: 0 kerentanan.
- Semua query SQL parameterized (tidak ada injection); path upload aman (`uuid4.ext` dengan ekstensi allow-list).
- Rute `/documents`, `/audits`, `/billing/wallet|topup|invoices` memfilter `current_user.id`; `/admin/*` dijaga `require_role("ADMIN")` di level router; `/corpus/*` REVIEWER/ADMIN. Klaim `role` di JWT diabaikan (dibaca dari DB), dan `is_active` dicek tiap request.
- `/audits/history/export-csv` tidak rawan CSV injection (hanya UUID/enum/angka).
- `.env`, `uploads/`, `.venv`, `node_modules` tidak ter-track dan tidak pernah ada di riwayat git; tidak ada kunci asli (hanya placeholder Midtrans `SB-Mid-*Demo*`).
- Tidak ada source map; tidak ada secret `VITE_*` di bundle.

## I. Urutan perbaikan yang disarankan (belum dikerjakan)

1. A1/A2/F1/E1: owner check + auth di `/reports/*` dan `export-pdf`, escape ReportLab, filter `deleted_at` pada audit & laporan, hapus `pdf_path` dan `?token=` dari respons/parameter.
2. A4/A5: Docker bind `127.0.0.1`, `requirepass` Redis, Vite `host: localhost`.
3. B2: hapus bypass login (hash seed sudah valid; reset volume Postgres atau update hash di DB lama).
4. D1/D2/D3: webhook atomik + cek nominal + `hmac.compare_digest`; `FOR UPDATE` pada wallet.
5. B1/C1/C4: secret wajib dari env + guard startup di luar development; rate limit & lockout; token akses 15 menit.
6. C2/C3: validasi `expires_at`, rotasi refresh, cabut sesi saat ganti/reset password, cookie `secure`/`path` mengikuti environment.
7. E1/E2: penghapusan nyata (berkas + data turunan) dan endpoint hapus akun.
8. F2–F4, G1–G2: batas upload & parsing, otorisasi korpus, validasi role & guard admin, matikan docs di produksi, security header, audit log aksi sensitif.

## J. Batasan audit

- Pembacaan statis; tidak ada pengujian dinamis terhadap server berjalan (Docker tidak aktif saat audit).
- Item berlabel [A] belum diverifikasi ulang secara independen oleh penyusun.
- Nilai `.env` lokal dan isi `backend/uploads/*.pdf` sengaja tidak dibaca.
- Dependensi Python tidak diaudit (`pip-audit` tidak dijalankan); hanya `npm audit` untuk frontend.
