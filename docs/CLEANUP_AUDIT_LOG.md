# VeriText AI Codebase Cleanup Audit Log

Dokumentasi resmi eksekusi pembersihan menyeluruh (*codebase de-bloating & harmonization*) pada repositori VeriText AI. Dokumen ini mencatat seluruh artefak yang dihapus, direfaktor, dan diverifikasi sesuai prinsip arsitektur atomik, kebijakan nihil emoji (*Zero-Emoji Policy*), serta model SaaS mandiri 3-Role (`FREE`, `PREMIUM`, `ADMIN`).

---

## 1. Ringkasan Eksekutif Pembersihan

Pembersihan ini mengeksekusi 5 irisan tugas (*5 Slices*) untuk mengeliminasi kode usang warisan birokrasi kampus, menghapus endpoint mutasi administratif yang tidak diizinkan, menstandardisasi peran pengguna menjadi 3-Role SaaS (`FREE`, `PREMIUM`, `ADMIN`), serta menghapus tuntas atribut `institution` dari seluruh lapisan aplikasi (model database, skema Pydantic, service PDF, endpoint API, dan skrip DDL/DML basis data).

Hasil akhir:
- **Total Berkas Dihapus**: 26 berkas kode sumber dan berkas aset (termasuk folder `docs/activity_diagrams/`).
- **Atribut `institution`**: Dieliminasi 100% dari basis data, backend, service PDF, dan kontrak API.
- **Peran Sistem**: Default pengguna diselaraskan dari `TRIAL` menjadi `FREE`.
- **Status Admin**: Ditegakkan 100% Read-Only Monitoring murni (4 route HTTP GET).
- **Hasil Pengujian Backend**: 211 test suite `pytest` lulus (0 gagal).
- **Hasil Linting Backend**: `ruff check app tests` 100% lolos tanpa error.
- **Hasil Build Frontend**: `npm run build` dan `navigation.test.mjs` sukses tanpa regresi.

---

## 2. Rincian Eksekusi per Irisan Tugas (Slices)

### Slice 1: Pembersihan Dead Code & Komponen Yatim Frontend
1. **Berkas Dihapus (15 berkas)**:
   - Seluruh direktori `frontend/src/components/audit/` (8 berkas):
     - `DiffMatchedSourceBox.vue`
     - `DiffOriginalSentenceBox.vue`
     - `ExportReportActions.vue`
     - `MatchedSourcesTable.vue`
     - `ScoreSummaryCard.vue`
     - `SentenceDetailModal.vue`
     - `SideBySideDiff.vue`
     - `index.ts`
   - Komponen yatim `frontend/src/components/verify/`:
     - `CertificateLookup.vue`
     - `VerificationBadge.vue`
   - Komponen yatim `frontend/src/components/common/`:
     - `Alert.vue`
     - `Badge.vue`
     - `ModernCard.vue`
     - `SkeletonLoader.vue`
     - `StatCard.vue`
   - Komponen yatim root:
     - `frontend/src/components/SimilarityGauge.vue`
   - Tipe data usang:
     - `frontend/src/types/corpus.ts`
2. **Pembersihan Barrel Exports**:
   - `frontend/src/components/verify/index.ts`: Hanya mengekspor komponen aktif (`CertificateDetailsCard`, `VerifySearchBox`, `CertificateDetails`).
   - `frontend/src/components/common/index.ts`: Hanya mengekspor komponen aktif (`Modal`, `Button`, `EmptyState`, `ToastContainer`).
   - `frontend/src/types/index.ts`: Menghapus referensi `./corpus`.
3. **Penyelarasan Pengujian Arsitektur**:
   - Memperbarui `backend/tests/test_architecture.py` (baris 87) untuk memeriksa komponen aktif `TierLegend.vue`.
4. **Verifikasi**:
   - `npm run build`: Berhasil tanpa error.
   - `node src/tests/navigation.test.mjs`: Lulus.
   - `pytest tests/test_architecture.py`: 12/12 passed.

### Slice 2: Penghapusan Unggah Korpus Manual & Router Token Duplikat
1. **Berkas Dihapus (6 berkas)**:
   - `backend/app/api/v1/corpus.py` (Router unggah ZIP korpus manual oleh dosen).
   - `backend/app/api/v1/tokens.py` (Router token duplikat yang tumpang tindih dengan `billing.py`).
   - `backend/app/services/corpus_service.py` (Service ekstraksi ZIP dan parsing korpus manual).
   - `backend/app/services/corpus_indexer_helper.py` (Helper dekomposisi ZIP korpus manual).
   - `backend/app/workers/corpus_ingest_worker.py` (Celery worker untuk korpus manual).
   - `backend/app/schemas/corpus.py` (Skema permintaan dan respons korpus manual).
2. **Pembersihan Router & Celery Tasks**:
   - Menghapus registrasi `corpus_router` dan `tokens_router` dari `backend/app/api/v1/router.py`.
   - Menghapus Celery task `index_corpus_document` dari `backend/app/workers/__init__.py` dan `backend/app/workers/tasks.py`.
   - Membersihkan import barrel di `backend/app/services/__init__.py` dan `backend/app/schemas/__init__.py`.
3. **Penyelarasan Pengujian**:
   - Memperbarui `tests/test_architecture.py`, `tests/test_remediation_phase3.py`, `tests/test_remediation_phase5.py`, `tests/test_remediation_phase7.py`, dan `tests/test_whitebox_suites.py`.
4. **Verifikasi**:
   - 110 test lulus pada test suite terkait.

### Slice 3: Penghapusan Layanan Mutasi Admin & SystemConfig
1. **Berkas Dihapus (3 berkas)**:
   - `backend/app/services/admin_legacy_ops.py` (Operasi mutasi akun dan suspend).
   - `backend/app/services/admin_config_ops.py` (Operasi tuning bobot algoritma via UI).
   - `backend/app/models/system_config.py` (Tabel model `system_configs`).
2. **Restrukturisasi Router & Skema Admin**:
   - Memangkas `backend/app/api/v1/admin.py` menjadi 66 LOC murni Read-Only Monitoring dengan 4 endpoint HTTP GET:
     - `GET /api/v1/admin/analytics`
     - `GET /api/v1/admin/transactions`
     - `GET /api/v1/admin/system-health` (dengan alias kompatibilitas `/health-metrics`)
     - `GET /api/v1/admin/audit-logs`
   - Memangkas `backend/app/schemas/admin.py` menjadi 52 LOC (`SystemHealthMetricsResponse`, `AuditLogResponse`).
   - Menghapus task sinkronisasi konfigurasi `sync_system_config` dari `backend/app/workers/tasks.py` dan `task_helpers.py`.
3. **Penyelarasan Pengujian**:
   - Menyesuaikan pengujian pada `test_remediation_phase1.py`, `test_remediation_phase2.py`, `test_remediation_phase3.py`, `test_remediation_phase6.py`, `test_remediation_phase7.py`, dan `test_whitebox_suites.py`.
4. **Verifikasi**:
   - 102 test lulus pada suite terkait; `ruff check app` 100% lulus.

### Slice 4: Harmonisasi Peran SaaS (FREE) & Eliminasi Tuntas Atribut Institution
1. **Model Database**:
   - `backend/app/models/user.py`: Menghapus kolom `institution` dan mengubah nilai bawaan `role` menjadi `"FREE"`.
   - `backend/app/models/audit.py`: Menghapus properti `@property def institution(self)`.
2. **Skema Pydantic**:
   - `backend/app/schemas/auth.py`: Menghapus atribut `institution` dari `UserRegisterRequest`, `UserProfileResponse`, `UserProfileUpdate`, dan `OnboardingRequest`.
   - `backend/app/schemas/audit.py`: Menghapus atribut `institution` dari `AuditReportResponse` dan `AuditVerificationResponse`.
3. **Autentikasi & Keamanan**:
   - `backend/app/core/security.py`: Mengubah parameter bawaan `create_access_token(role="FREE")`.
   - `backend/app/services/auth_service.py`: Menghapus alokasi `institution` dan menetapkan `role="FREE"`.
   - `backend/app/api/v1/auth_helpers.py`: Menghapus penanganan `institution` pada `format_user_profile`, `update_profile`, dan `complete_onboarding`.
   - `backend/app/api/v1/auth_google_oauth.py`: Menghapus logika domain email institusi dan menetapkan pengguna Google baru ke `role="FREE"`.
4. **Layanan Pembuatan Dokumen Resmi (PDF)**:
   - `backend/app/services/report_view_helper.py`: Menghapus argumen dan pemetaan `institution`.
   - `backend/app/services/pdf_certificate_service.py`: Menghapus parameter `institution` pada `generate_pdf_certificate`.
   - `backend/app/services/pdf_certificate_draw.py`: Menghapus baris institusi dari tabel metadata sertifikat audit.
   - `backend/app/services/pdf_invoice_service.py`: Menghapus parameter `institution` pada `generate_invoice_pdf`.
   - `backend/app/services/pdf_invoice_draw.py`: Menghapus baris institusi dari tabel informasi pembeli invoice.
   - `backend/app/api/v1/billing.py`: Menghapus pembacaan dan pengiriman `institution` pada invoice.
5. **Frontend DTO & Type Alignment**:
   - `frontend/src/services/authService.ts`: Menghapus atribut `institution` dari `RegisterDTO` dan `OnboardingDTO`.
   - `frontend/src/views/OnboardingView.vue`: Menghapus argumen `institution` pada `authStore.completeOnboarding`.
   - `frontend/src/types/audit.ts`: Menghapus `institution?: string | null;` dari definisi tipe `AuditReport`.
   - `frontend/src/types/auth.ts`: Menyelaraskan `UserRole` strictly ke `"FREE" | "PREMIUM" | "ADMIN"`.
   - `frontend/src/types/admin.ts`: Menyelaraskan role pada `ManagedUser` strictly ke `"FREE" | "PREMIUM" | "ADMIN"`.
   - `frontend/src/components/billing/TokenBalanceCard.vue`: Mengubah default prop `role` dari `"TRIAL"` ke `"FREE"`.
   - `frontend/src/components/workspace/TopSummaryBar.vue`: Menyelaraskan guard `isFreeUser` strictly ke `role === "FREE"`.
6. **Skrip Inisialisasi Basis Data & Migrasi**:
   - `db/init/02_schema_ddl.sql`: Menghapus kolom `institution` pada tabel `users`, menegakkan `CHECK (role IN ('FREE', 'PREMIUM', 'ADMIN'))`, dan menghapus definisi tabel `system_configs`.
   - `db/init/03_seed_dml.sql`: Menghapus kolom dan nilai institusi dari data seed awal pengguna, serta memperbarui peran awal ke `ADMIN`, `PREMIUM`, dan `FREE`.
   - `db/migrations/0001_initial_schema.sql`: Menghapus kolom `institution` dan menyelaraskan batasan peran `CHECK (role IN ('FREE', 'PREMIUM', 'ADMIN'))`.
   - `backend/alembic/versions/0001_initial_schema.py`: Menghapus kolom `institution` dan menyelaraskan batasan peran.
   - `db/README.md`: Menyelaraskan tabel akun default ke peran `ADMIN`, `PREMIUM`, dan `FREE`.
7. **Penyelarasan Pengujian**:
   - Memperbarui `test_pdf_certificate.py`, `test_backend.py`, `test_google_oauth_and_reset.py`, `test_whitebox_suites.py`, `test_remediation_phase1.py`, `test_remediation_phase4.py`, `test_remediation_phase5.py`, `test_remediation_phase6.py`, dan `test_remediation_phase7.py`.
8. **Verifikasi**:
   - Seluruh test suite lulus 100%.

### Slice 5: Pembersihan Berkas Root & Dokumentasi
1. **Berkas Dihapus**:
   - `anywhere-signup.svg` (Aset visual SVG usang di root proyek).
   - `pagedone-login.svg` (Aset visual SVG usang di root proyek).
   - `docs/design/laptop/auth/register--error-invalid-institution.svg` (Aset visual SVG usang untuk validasi institusi).
   - `docs/design/system/build_screens.py` (Skrip usang pendahulu).
   - `docs/activity_diagrams/` (Direktori diagram aktivitas lama yang telah digantikan oleh `diagrams/`).
2. **Pembersihan Skrip Desain**:
   - `docs/design/system/build_auth.py`: Menghapus state dan penanganan error `error-invalid-institution`.
   - `docs/design/DAFTAR-LAYAR.md`: Menghapus baris registrasi dengan invalid institution.
   - `docs/design/system/build_verify.py`: Menghapus karakter simbol non-ascii menjadi penanda ASCII bersih.
3. **Penyusunan Dokumentasi**:
   - Menghasilkan berkas audit log ini (`docs/CLEANUP_AUDIT_LOG.md`).
   - Memperbarui `tasks/todo.md` dan `docs/PROJECT-CONTEXT.md`.

---

## 3. Matriks Kepatuhan Batasan Rekayasa

| Batasan / Aturan | Target | Hasil Akhir | Keterangan |
|---|---|---|---|
| **Sub-150 LOC Rule** | Setiap berkas `.py`, `.vue`, `.ts` $\le 150$ LOC | Terpenuhi 100% | Seluruh berkas baru dan hasil refactor berada di bawah batas 150 baris. |
| **Zero-Emoji Policy** | 0 emoji di kode, komentar, UI, dan dokumen | Terpenuhi 100% | Tidak ada karakter emoji visual yang digunakan. |
| **Self-Service SaaS 3-Role** | Hanya peran `FREE`, `PREMIUM`, `ADMIN` | Terpenuhi 100% | Peran `TRIAL` dan `REVIEWER` telah dibersihkan secara konsisten. |
| **Admin Read-Only Monitoring** | 100% HTTP GET murni | Terpenuhi 100% | Seluruh endpoint mutasi admin dihapus; tersisa 4 rute GET. |
| **Zero Auto-Ingestion & UU PDP** | Naskah pengguna tidak masuk korpus referensi | Terpenuhi 100% | Hak hapus permanen terlindungi secara atomik cascade. |
| **Atribut Institution** | Dihapus tuntas dari seluruh arsitektur | Terpenuhi 100% | 0 kemunculan di `backend/app/`, skema, dan database DDL/DML. |

---

## 4. Rekapitulasi Verifikasi Otomatis

- **Pytest Full Suite**:
  - Perintah: `cd backend && ./venv/bin/pytest -q`
  - Hasil: `211 passed, 3 warnings in 158.14s`
- **Ruff Code Linter**:
  - Perintah: `cd backend && ./venv/bin/ruff check app tests`
  - Hasil: `All checks passed!`
- **Frontend Type-Check & Build**:
  - Perintah: `cd frontend && npm run build`
  - Hasil: `vite v6.4.4 building for production... [OK] built in 997ms`
- **Frontend Navigation & RBAC Test**:
  - Perintah: `cd frontend && node src/tests/navigation.test.mjs`
  - Hasil: `[SUCCESS] Seluruh verifikasi navigasi 3-Role SaaS berhasil!`

## Perombakan Modul Autentikasi (2026-11-08)

Alasan: alur Google mengarahkan ADMIN ke halaman pengguna, akun Google baru langsung dibuat tanpa kredensial, jalur kode simulasi masih ada, dan halaman admin berbeda gaya dari halaman lain.

Backend:
- Jalur `simulated_google_dev_code` dihapus total; tanpa `GOOGLE_CLIENT_ID` endpoint login Google mengembalikan 503.
- Validasi `state` (CSRF) via cookie `g_oauth_state`; validasi `aud` dan `email_verified` pada `/google/verify`.
- Akun Google baru tidak lagi dibuat otomatis. Email yang belum terdaftar menerima signup ticket (JWT 10 menit) dan akun baru dibuat hanya setelah `POST /auth/google/complete` (nama + kata sandi kuat, role FREE, 5 token, 3 trial AI).
- `POST /auth/onboarding` dihapus. Login kembali memakai email penuh (alias username dihapus).

Frontend:
- `getHomeRouteForRole`: ADMIN selalu ke `/admin`; FREE/PREMIUM ke `/dashboard`. Guard menolak lintas role pada `/dashboard`, `/billing`, `/audits/:id`, `/admin`.
- Callback Google menunggu profil terisi sebelum redirect berdasarkan role.
- Modal "Selamat Datang, [Nama]" untuk semua role pada setiap login, login Google, dan pendaftaran.
- Halaman ADMIN memakai Navbar, Footer, dan latar yang sama dengan halaman pengguna; hanya isinya yang monitoring (tetap read-only).
- Halaman Verifikasi QR: kamera palsu dan klaim yang tidak diimplementasikan (Ed25519, OpenCerts, Permendikbudristek) dihapus.
- Dekorasi titik (titik jendela macOS, titik biru pada judul/brand, karakter bullet) dihapus.

Verifikasi: pytest 221 lulus, ruff bersih, npm run build hijau, navigation test lulus, 0 berkas di atas 150 baris.
