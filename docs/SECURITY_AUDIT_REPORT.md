# Laporan Audit Keamanan & Pengerasan Operasional — VeriText AI

Tanggal Audit: 2026-11-28  
Cakupan: 12 Putaran Deep Security & Reliability Scan + 2 Checkpoint Scan (A & B)  
Rentang Commit: `05f7236` s.d. `dfbf316` (cabang `main`)

---

## 1. Ringkasan Eksekutif

Audit menyeluruh dilakukan terhadap backend FastAPI, worker Celery, gateway LLM, skema PostgreSQL/pgvector, frontend Vue 3/Vite, konfigurasi reverse proxy Nginx, dan stack Docker produksi. Sebanyak **36 temuan awal** ditambah **2 temuan lanjutan saat Checkpoint Scan A** telah ditutup seluruhnya tanpa mengubah kontrak peran SaaS 3-Role (`FREE`, `PREMIUM`, `ADMIN`), tanpa pelanggaran batas 150 LOC per berkas sumber, dan mematuhi kebijakan Zero-Emoji.

---

## 2. Rincian Perbaikan per Fase

### Fase 1 (`05f7236`) — Keamanan Jaringan, SSRF, Secret & Startup Pembayaran
- **Mitigasi SSRF**: Menambahkan `backend/app/core/url_guard.py` (`is_safe_public_url`, `extract_report_allowed_urls`) dan memperketat `backend/app/services/source_preview_service.py` agar hanya mengambil `source_url` yang terdaftar pada laporan terkait, lolos validasi IP publik (memblokir `localhost`, loopback, link-local/metadata `169.254.169.254`, IP privat/reserved), menonaktifkan redirect (`follow_redirects=False`), dan membatasi baca respons maksimal 512 KB.
- **Anti-Spoofing Rate Limiter & Header Proxy**: Memperbarui `extract_client_ip` di `backend/app/core/rate_limiter.py` (prioritas `X-Real-IP`, fallback hop paling kanan `X-Forwarded-For`), menambahkan rule untuk `/api/v1/billing/topup`, `/api/v1/auth/refresh`, dan `/api/v1/audits`, serta mengubah `nginx/nginx.conf` menggunakan `X-Forwarded-For $remote_addr` bersama header `Permissions-Policy` dan `Content-Security-Policy`.
- **Fail-Closed Midtrans Produksi**: Startup `lifespan` di `backend/app/main.py` dan `verify_midtrans_signature` di `backend/app/services/billing_webhook_helper.py` menolak konfigurasi kosong atau kunci demo (`DemoServerKey`) saat `ENVIRONMENT=production`.
- **Eliminasi Kebocoran `GEMINI_API_KEY`**: Memindahkan kunci API dari query string `?key=` ke HTTP header `x-goog-api-key` dan menyamarkan detail exception URL di `backend/app/llm/gemini_client.py` serta `backend/app/engine/web_search_providers.py`.

### Fase 2 (`76144d9`) — Paywall Parafrase, IDOR, Concurrency AI & Atomisitas Refund
- **Validasi Mode & Paywall Fail-Closed**: Mengunci `ParaphraseMode` (`SENTENCE`, `PARAGRAPH`, `FULL_PAGE`) serta batas `selected_text` (`3..15000` karakter) di `backend/app/schemas/chat.py`, dan menolak semua mode selain `CHAT` untuk akun `FREE` di `backend/app/services/assistant_service.py`.
- **Concurrency Lock & Validasi Kepemilikan**: Menambahkan `ai_user_slot` (maks. 2 permintaan AI paralel per pengguna via Redis/memori) di `backend/app/services/ai_concurrency.py` dan memvalidasi kepemilikan `sentence_id` sebelum memanggil LLM di `backend/app/api/v1/chat.py`.
- **Atomisitas Antrean & Pembatalan Audit**: Memastikan `db.commit()` dieksekusi sebelum `preprocess_and_audit.delay(...)`, menghapus `inspect().ping()` blocking, menambahkan `refund_failed_dispatch` + HTTP 503 saat dispatch gagal (`upload_charging.py`, `document_service.py`, `audit_service.py`), menerapkan rate/active limit di `start_audit` (`audits.py`), serta mengunci `AuditTask` (`with_for_update()`) sebelum `TokenWallet` di `cancel_task` dan `task_helpers.py`.

### Fase 3 (`f20ce77`) + Checkpoint Scan A — Auth, OAuth CSRF, Email, UU PDP & Query
- **Keamanan Email & Reset Sandi**: Menekan pencetakan OTP/URL reset di log produksi dan menambahkan `html.escape` di `backend/app/core/email.py`; memindahkan pengiriman SMTP ke `BackgroundTasks`, menambahkan `.with_for_update()` pada `PasswordReset`, dan memakai `extract_client_ip` di `backend/app/api/v1/auth_password_reset.py`.
- **OAuth CSRF & Sesi Auth**: Mengikat state OAuth ke cookie `HttpOnly` `vt_oauth_state` (`auth_oauth_codes.py`, `auth_google_oauth.py`), menyamakan atribut `clear_refresh_cookie`, menambah `max_length=128` pada skema sandi (`schemas/auth.py`), mengunci `Session` saat `/auth/refresh` (`auth.py`), dan memuat kuota lengkap `get_user_wallet_info` (`auth_helpers.py`, `auth_google_signup.py`).
- **Kepatuhan Penghapusan Akun UU PDP**: Memperbaiki `purge_user_account` di `backend/app/services/auth_session_helper.py` untuk me-revoke task Celery aktif, menghapus eksplisit `ChatSession`, dan menghilangkan `contextlib.suppress(Exception)` di sekitar query SQL transaksi PostgreSQL.
- **Stream Upload, Escaping & Optimasi Query**: Menghapus pemutusan dini `len(chunk) < chunk_size` pada stream nyata di `document_validator.py`, menambahkan `escape_ilike` (`url_guard.py`) + batas query di `audits.py`, `admin_extra.py`, `admin_users_service.py`, `billing.py`, dan `chat_batch.py`, mengoptimalkan `list_sessions` (`chat_sessions.py`) dengan batch query + batas 50 sesi, serta meng-escape `verify_url` pada `pdf_invoice_draw.py`.

### Fase 4 (`8c01323`) — Reliabilitas Worker, Prompt Firewall, Singleton & Migrasi
- **Reliabilitas Worker & Validasi Checkpoint A**: Memperbaiki `handle_web_scan_refund` agar mengunci wallet sebelum cek duplikat refund, mencegah `handle_audit_failure` menimpa status `CANCELLED`/`SUCCESS`, dan memperluas `clean_zombie_tasks` untuk task `QUEUED` (`task_helpers.py`); menolak berkas hilang dengan `FileNotFoundError` pada non-test dan membatasi `word_count <= 32767` serta `current_stage[:100]` (`tasks.py`).
- **Prompt Injection Delimiters**: Membungkus teks naskah di tag `<untrusted_manuscript>` dengan instruksi pengabaian perintah tersembunyi di `gateway.py`, `chat_prompt.py`, dan `web_search_providers.py`.
- **Thread-Safe Singletons**: Menambahkan `threading.Lock()` (double-checked locking) pada pemuatan model di `tier2_semantic.py` dan `tier2_reranker.py`.
- **Migrasi Indeks**: Menambahkan `index=True` pada `TokenWallet`/`TokenTransaction.reference_id` (`models/wallet.py`) dan migrasi Alembic `backend/alembic/versions/0008_add_tx_ref_idx.py` (`alembic upgrade head`).

### Fase 5 (`1ef8db9`) — Docker Produksi, `.dockerignore` & Dependensi
- Menambahkan `.dockerignore` pada root, `backend/`, dan `frontend/` untuk mencegah `.env`, `venv/`, `uploads/`, `logs/`, dan `tests/` masuk ke layer image.
- Memisahkan dependensi dev/test (`pytest`, `pytest-asyncio`, `ruff`, `mypy`) ke `backend/requirements-dev.txt` dan membersihkan `backend/requirements.txt`.
- Memperkeras `docker-compose.prod.yml` dengan mewajibkan `${POSTGRES_PASSWORD:?}` & `${REDIS_PASSWORD:?}`, menggunakan `REDISCLI_AUTH` pada healthcheck Redis, memasang volume `hf_cache`, menjalankan `alembic upgrade head` saat startup backend, menambahkan healthcheck backend, serta menambahkan layanan Celery `beat`.

### Fase 6 (`264c362`) & Checkpoint Scan B (`dfbf316`) — Frontend, CVE & Uji Regresi
- Memperkeras frontend (`api.ts`, `main.ts`, `auth.ts`, `LoginView.vue`, `OAuthCallbackView.vue`, `ResetPasswordView.vue`, `midtransSnap.ts`, `LoginForm.vue`, `audit.ts`, `VerifyView.vue`), menghapus berkas mati (`AdminView.vue`, `InteractiveDemoMatchPanel.vue`), dan memperbarui `test_architecture.py` ke `AdminOverviewView.vue`.
- Menjalankan `npm audit fix` sehingga `npm audit --omit=dev` mencatat **0 vulnerabilities**.
- Menambahkan suite pengujian regresi keamanan `backend/tests/test_security_hardening.py`.

---

## 3. Hasil Verifikasi & Syarat Deployment Produksi

- **Backend**: `ruff check app tests` bersih (`All checks passed!`), seluruh berkas `backend/app/` & `frontend/src/` berada pada batas `<= 150` baris (`OVER_150_LOC: []`), dan pemeriksaan Zero-Emoji bersih (`EMOJI_FILES: []`).
- **Pengujian**: Suite penuh `pytest -q` mencatat 443 lulus & 1 terlewati (`test_corpus_ann.py` saat container Postgres baru startup), lalu eksekusi lanjutan `pytest tests/test_architecture.py tests/test_corpus_ann.py -q` lulus penuh `16 passed`.
- **Frontend & Compose**: `npm run build`, `node src/tests/navigation.test.mjs`, `npm audit --omit=dev`, dan `docker compose -f docker-compose.prod.yml config --quiet` seluruhnya lulus.
- **Prasyarat Deploy VPS**: Operator wajib mengisi `.env` produksi secara penuh (`ENVIRONMENT=production`, `SECRET_KEY`, `JWT_SECRET_KEY`, `MIDTRANS_SERVER_KEY` asli, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `GOOGLE_CLIENT_ID`/`SECRET`, `SMTP_*`) sebelum menjalankan `docker compose -f docker-compose.prod.yml up -d`.
