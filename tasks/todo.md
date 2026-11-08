# Atomic Task Checklist (`tasks/todo.md`)

Setiap tugas dirancang berukuran S/M (menyentuh 1–4 berkas, masing-masing $\le 150$ baris kode) dengan kriteria keberterimaan dan perintah verifikasi eksplisit.
**Protokol Eksekusi**: Agen utama (**Brain** — Primary: Gemini Argon / Claude Sonnet; Fallback: Gemini Flash High jika Argon/Sonnet tidak tersedia) bertugas sebagai *Lead Architect, Orchestrator, & Code Reviewer* yang mendelegasikan eksekusi penulisan kode ke subagen pekerja (**Worker**: `invoke_subagent` dengan `Model="flash"` dan `EnableWriteTools=True`).

---

## Phase 1: Specification, UML Diagrams & AI Knowledge Base
- [x] **T1.1**: Generasi 29 Diagram UML & Arsitektur Draw.io Light Mode (`diagrams/drawio/*.drawio` & `diagrams/exported/*.png`).
  - *Verification*: `ls diagrams/exported/*.png | wc -l` menghasilkan `29`.
- [x] **T1.2**: Penyelarasan penuh `SRS_Sistem_Deteksi_Plagiarisme_Hybrid.md` dan `SDD_Sistem_Deteksi_Plagiarisme_Hybrid.md` dengan struktur tabel `.docx` asli (0 emoji, 0 callout).
  - *Verification*: Pemeriksaan skrip Python memastikan `callouts=0, emojis=0, missing_imgs=[]`.
- [x] **T1.3**: Penyusunan Knowledge Base AI (`AGENTS.md`, `docs/BLUEPRINT.md`, `docs/API_CONTRACT.md`, `docs/DATABASE_SCHEMA.md`, `docs/AI_PIPELINE.md`, `docs/ATOMIC_CODING_STANDARDS.md`, `docs/SPEC_DRIVEN_DEVELOPMENT.md`, `docs/PROJECT-CONTEXT.md`, `docs/FRONTEND-HANDOFF.md`).

---

## Phase 2: Database Schema & Dual-Engine LLM Gateway
- [x] **T2.1**: Tambahkan model SQLAlchemy `chat.py` (`ChatSession`, `ChatMessage`, $\le 100$ LOC) serta perbarui `wallet.py` (`ai_trial_remaining`, `ai_chat_allowance_remaining`) dan `audit.py` (`current_text`, `RESOLVED_GREEN`, $\le 150$ LOC).
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_architecture.py tests/test_backend.py -q` (`30 passed`)
- [x] **T2.2**: Buat paket atomik `backend/app/llm/` (`gemini_client.py`, `deepseek_client.py`, `gateway.py`, masing-masing $\le 110$ LOC) dengan dukungan batch prompt (maks 15 kalimat) dan automatic failover, serta refactor `backend/app/engine/ai_detector.py` (336 LOC $\rightarrow$ 139 LOC).
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_jalur1_gemini.py tests/test_llm_gateway.py -q` (`20 passed`)

---

## Phase 3: Backend De-bloating & Atomic Services
- [x] **T3.1**: Implementasikan `backend/app/services/assistant_service.py` (Academic Guardrail `CHAT_001`, 3-Mode Paraphrase, in-place replacement) dan `backend/app/api/v1/chat.py` ($\le 130$ LOC).
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_chat_assistant.py tests/test_architecture.py -q` (`17 passed`)
- [x] **T3.2**: Pangkas `backend/app/api/v1/admin.py` (570 LOC $\rightarrow$ 99 LOC) menjadi 100% Read-Only (`GET` murni: `analytics`, `transactions`, `system-health`, `audit-logs`) dan hapus endpoint mutasi user/korpus manual dari router.
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_admin_readonly.py tests/test_backend.py -q` (`34 passed`)
- [x] **T3.3**: Dekomposisi `backend/app/api/v1/auth.py` (781 LOC $\rightarrow$ 139 LOC) dan `backend/app/engine/web_scanner.py` (557 LOC $\rightarrow$ 143 LOC) menjadi sub-modul atomik $\le 150$ LOC.
  - *Verification*: `cd backend && ./venv/bin/ruff check app/api/v1/auth*.py app/engine/web_*.py && ./venv/bin/pytest tests/test_google_oauth_and_reset.py tests/test_jalur1_gemini.py tests/test_engine.py -q` (`56 passed`)

---

## Phase 4: Frontend De-bloating & Split-Screen Studio Workspace
- [x] **T4.1**: Pangkas `frontend/src/views/AdminView.vue` (1222 LOC $\rightarrow$ 124 LOC) dan `CorpusView.vue` (701 LOC $\rightarrow$ 110 LOC) menjadi dasbor Read-Only murni serta hapus `UserManagementTable.vue` dan `SystemSettingsCard.vue`.
  - *Verification*: `cd frontend && npm run build && node src/tests/navigation.test.mjs` (`25 passed`)
- [x] **T4.2**: Pecah `frontend/src/views/AuditDetailView.vue` (1093 LOC $\rightarrow$ 107 LOC) menjadi **Split-Screen Studio Workspace** dengan `TopSummaryBar.vue` (102 LOC), `HeatmapViewer.vue` (116 LOC), `MatchedSourcesTab.vue` (104 LOC), `AiAssistantTab.vue` (137 LOC), dan `ParaphraseOptionCard.vue` (45 LOC).
  - *Verification*: `cd frontend && npm run build && node src/tests/navigation.test.mjs` (`25 passed`)

---

## Phase 6: Wave 2 Full-Repo Atomic Sweep ($\le 150$ LOC), Live Server & Alembic 0005
- [x] **T6.1**: Dekomposisi `backend/app/workers/tasks.py` dan seluruh berkas `backend/app/engine/*.py` menjadi modul-modul atomik $\le 150$ LOC.
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_engine.py tests/test_jalur1_gemini.py tests/test_remediation_phase7.py -q` (`53 passed`, `0 files > 150 LOC`)
- [x] **T6.2**: Dekomposisi seluruh berkas `backend/app/services/*.py`, `backend/app/api/v1/reports.py`, `billing.py`, dan `models/audit.py` menjadi $\le 150$ LOC.
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_backend.py tests/test_pdf_certificate.py tests/test_remediation_phase6.py tests/test_remediation_phase7.py -q` (`32 passed`, `0 files > 150 LOC`)
- [x] **T6.3**: Dekomposisi `VerifyView.vue`, `DashboardView.vue`, `OnboardingView.vue`, `BillingView.vue`, `ResetPasswordView.vue`, `ForgotPasswordView.vue`, serta komponen `dashboard/*` dan `verify/*` menjadi $\le 150$ LOC, dan hapus `CorpusUploadModal.vue`.
  - *Verification*: `cd frontend && npm run build` (`0 files > 150 LOC`)
- [x] **T6.4**: Dekomposisi komponen `auth/*`, `landing/*`, `audit/*`, `Navbar.vue`, dan `utils/navigation.ts` menjadi $\le 150$ LOC.
  - *Verification*: `cd frontend && npm run build && node src/tests/navigation.test.mjs` (`25 passed`, `0 files > 150 LOC`)
- [x] **T6.5**: Jalankan uji coba live server lokal (FastAPI `uvicorn` + Vite `dev` + Dual-Engine LLM Gateway health/endpoint test).
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_live_smoke.py -q` (`4 passed`, full suite `244 passed`)
- [x] **T6.6**: Buat migrasi Alembic `0005_chat_and_subcredits.py` (74 LOC) dan sinkronkan `db/init/02_schema_ddl.sql`.
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_architecture.py -q` (`10 passed`)

---

## Phase 7: Full Codebase De-bloating, SaaS 3-Role Harmonization & Institution Removal
- [x] **T7.1**: Pembersihan 15 berkas dead code/komponen yatim frontend di `frontend/src/components/{audit,verify,common}/`, `SimilarityGauge.vue`, `types/corpus.ts`, dan sinkronisasi barrel exports.
  - *Verification*: `cd frontend && npm run build && node src/tests/navigation.test.mjs` (Lulus, 0 errors).
- [x] **T7.2**: Penghapusan endpoint korpus manual & router token duplikat (`backend/app/api/v1/corpus.py`, `tokens.py`, `services/corpus_service.py`, `services/corpus_indexer_helper.py`, `workers/corpus_ingest_worker.py`, `schemas/corpus.py`).
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_architecture.py tests/test_remediation_phase3.py tests/test_remediation_phase5.py tests/test_remediation_phase7.py tests/test_whitebox_suites.py -q` (110 passed).
- [x] **T7.3**: Pemangkasan modul admin mutasi & `system_config.py` (`services/admin_legacy_ops.py`, `services/admin_config_ops.py`, `models/system_config.py`) dan penegakan admin 100% Read-Only (4 route GET murni).
  - *Verification*: `cd backend && ./venv/bin/pytest tests/test_admin_readonly.py tests/test_backend.py -q` (34 passed).
- [x] **T7.4**: Harmonisasi peran SaaS (`FREE`, `PREMIUM`, `ADMIN`) dan eliminasi total atribut `institution` dari model, skema, service PDF, helper autentikasi, serta skrip DDL/DML basis data.
  - *Verification*: `cd backend && ./venv/bin/pytest -q` (211 passed, 0 failures), `cd backend && ./venv/bin/ruff check app tests` (All checks passed).
- [x] **T7.5**: Pembersihan artefak root/docs usang (`anywhere-signup.svg`, `pagedone-login.svg`, `build_screens.py`, `docs/activity_diagrams/`) dan dokumentasi audit pembersihan lengkap di `docs/CLEANUP_AUDIT_LOG.md`.
  - *Verification*: Seluruh berkas diperiksa dan diverifikasi secara menyeluruh.

---

## Backlog (ditunda)
- [ ] **B1**: UI dua bahasa (Indonesia dan Inggris) dengan i18n frontend. Ditunda sampai mesin multibahasa selesai.

---

## Phase 8: Pemisahan dashboard dan Asisten AI (disetujui 2026-11-08)
- [x] **T8.1**: Halaman `/periksa` (unggah, pilihan kedalaman, ringkasan biaya) dan navbar pengguna masuk (Ringkasan, Periksa naskah, Token, Verifikasi QR).
- [x] **T8.2**: Biaya token = `min(5, ceil(kata / 2500))` (`token_pricing.py`, `upload_charging.py`, `word_counter.py`), batas FREE 2.500 kata (402), `POST /documents/estimate`, batas berkas 15 MB, modal sambutan Violet Kaca.
  - *Verification*: `cd backend && ./venv/bin/pytest -q` (253 passed); `cd frontend && npm run build && node src/tests/navigation.test.mjs`
- [x] **T8.3 (Opsi B, skema disetujui)**: Asisten AI dengan konteks dokumen. Migrasi Alembic: `chat_sessions.document_id` menjadi opsional dan tabel relasi `chat_session_documents`; endpoint daftar sesi, riwayat pesan, dan kirim pesan dengan `document_ids`; konteks diambil dari kalimat paling relevan (MiniLM) lalu masuk ke prompt. Perbarui `DATABASE_SCHEMA.md` dan `API_CONTRACT.md`.
- [x] **T8.4**: Halaman `/asisten`, `/riwayat`, `/akun` selesai (2026-11-08, diverifikasi di 1440/768/390). `/billing` menjadi Token selesai (harga mengikuti AGENTS.md, beli satuan didukung backend lewat `pkg_tokens`). `/dashboard` menjadi Ringkasan selesai (komponen dashboard lama dihapus).
- [ ] **T8.5**: `audits/:id` (ruang kerja) selesai; sisa `/admin` dan komponen lama bergaya aurora biru. Perbaikan: anotasi laporan kini membawa `sentence_id` (sebelumnya parafrase memakai UUID nol).
- [x] **T8.6 (celah kontrak)**: `DOC_003` (naskah di bawah 50 kata ditolak, 422) tercantum di kontrak tetapi belum diimplementasikan.

## Phase 9: Pengamanan unggahan dan perombakan sisa halaman (diminta 2026-11-08)
- [x] **T9.1 (prioritas, keamanan)**: Pengetatan unggahan. Hanya ekstensi `pdf`, `docx`, `txt`; tolak tanpa ekstensi, ekstensi ganda (misalnya `a.pdf.exe`), nama berkas dengan jalur (`../`), dan ekstensi aneh. Verifikasi isi, bukan hanya nama: PDF harus diawali `%PDF-`, DOCX harus berkas ZIP yang berisi `word/document.xml`, TXT tidak boleh mengandung byte NUL dan harus bisa didekode. Tolak bila tipe MIME bertentangan dengan isi.
- [x] **T9.2 (DOC_003)**: Naskah di bawah 50 kata ditolak dengan 422, baik di `POST /documents/upload` maupun `POST /documents/estimate` (estimasi mengembalikan alasan). Perbarui tes lama yang memakai naskah pendek.
- [x] **T9.3 (cegah kelebihan beban)**: Batasi agar dokumen tidak membebani sistem: batas halaman PDF, batas ukuran hasil dekompresi DOCX (cegah ZIP bomb), batas waktu ekstraksi, batas jumlah antrean aktif per pengguna, dan batas laju unggah. Usulan nilai ditentukan bersama pengguna; rate limit butuh dependensi baru (misalnya `slowapi`), jadi minta persetujuan dulu.
- [ ] **T9.4 (perombakan layout)**: Seluruh halaman yang masih bergaya lama diganti ke Violet Kaca: Ringkasan (`/dashboard`), Token (`/billing`), ruang kerja (`/audits/:id`), `/admin`, serta halaman baru Riwayat, Akun, dan Asisten (lihat T8.4 dan T8.5). Mengikuti aturan wajib di `docs/design/VIOLET-KACA.md` (latar `meta.backdrop`, kartu berbayangan, isian berupa garis, responsif 1440/768/390).
