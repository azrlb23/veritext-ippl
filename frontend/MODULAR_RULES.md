# Panduan & Rules Arsitektur Modular Frontend VeriText AI
> **Target Audience**: AI Agents (Antigravity, Cursor, Copilot, Cline, dll.) & Developer
> **Lingkup**: `frontend/` (Vue 3 + TypeScript + Vite + Tailwind CSS)

Dokumen ini adalah aturan wajib (*mandatory rules*) bagi setiap agent/developer yang ingin memodifikasi, menambah fitur, atau me-refactor kode di `frontend/`.

---

## 1. Prinsip Utama: Arsitektur 3-Layer (Orchestrator-Component-Composable)

Setiap fitur di `frontend/` harus mematuhi pemisahan peran (*separation of concerns*) berikut:

```
┌────────────────────────────────────────────────────────┐
│  src/views/  (Orchestrator Layer)                      │
│  - HANYA mengelola koordinasi state, routing, store,   │
│    dan mengomposisikan sub-komponen.                   │
│  - DILARANG memuat template UI / markup yang panjang.  │
└───────────────────────────┬────────────────────────────┘
                            │
       ┌────────────────────┴────────────────────┐
       ▼                                         ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ src/components/<domain>/        │   │ src/composables/                │
│ (Presentation & Component Layer)│   │ (Logic & State Layer)           │
│ - Murni UI, form, tabel, modal  │   │ - Headless reactive logic       │
│ - Strict Props & Emits typed    │   │ - File upload, polling, toast,  │
│ - Berada di subfolder domain    │   │   modal management              │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

---

## 2. Struktur Direktori & Pemetaan Pecahan Komponen

```
frontend/src/
├── components/
│   ├── common/         # UI primitif & komponen serbaguna
│   │   ├── Modal.vue            # Dialog modal (<Teleport>, ESC listener)
│   │   ├── Badge.vue            # Tag status, varian warna, pulsing dot
│   │   ├── Button.vue           # Tombol dengan loading spinner & varian
│   │   ├── StatCard.vue         # Kartu metrik/KPI dengan ikon & tren
│   │   ├── Alert.vue            # Spanduk peringatan/sukses dismissible
│   │   ├── EmptyState.vue       # Placeholder data kosong
│   │   ├── SkeletonLoader.vue   # Animasi skeleton loading
│   │   └── index.ts             # Barrel export
│   │
│   ├── dashboard/      # Domain: Dashboard Pengujian Dokumen
│   │   ├── DashboardStatsGrid.vue     # Grid metrik saldo & status tugas
│   │   ├── UploadDropzone.vue         # Drag-and-drop & seleksi kedalaman
│   │   ├── AuditProgressTracker.vue   # Indikator progres realtime Celery
│   │   ├── AuditHistoryTable.vue      # Tabel riwayat naskah yang diuji
│   │   └── index.ts
│   │
│   ├── audit/          # Domain: Hasil Audit, Heatmap, & Diff
│   │   ├── ScoreSummaryCard.vue       # Skor komposit + 3 tier breakdown
│   │   ├── SideBySideDiff.vue         # Komparasi teks uji vs sumber korpus
│   │   ├── SentenceDetailModal.vue    # Popup modal rincian kalimat terdeteksi
│   │   ├── ExportReportActions.vue    # Unduh PDF, salin URL, preview QR
│   │   ├── MatchedSourcesTable.vue    # Tabel rujukan sumber yang cocok
│   │   └── index.ts                   # Mengekspor juga HeatmapViewer, SimilarityGauge, TierLegend
│   │
│   ├── billing/        # Domain: Saldo Token & Midtrans Billing
│   │   ├── TokenBalanceCard.vue       # Kartu dompet token & info konversi
│   │   ├── PlanCard.vue               # Kartu paket topup (Mahasiswa/Peneliti/Institusi)
│   │   ├── TransactionHistoryTable.vue# Tabel invoice & metode bayar
│   │   ├── TopupModal.vue             # Modal konfirmasi checkout sandbox
│   │   └── index.ts
│   │
│   ├── corpus/         # Domain: Bank Repositori Dokumen Pembanding
│   │   ├── CorpusStatsGrid.vue        # Statistik total dokumen & vektor HNSW
│   │   ├── CorpusFilterBar.vue        # Filter kategori & pencarian judul
│   │   ├── CorpusTable.vue            # Tabel korpus terindeks pgvector
│   │   ├── CorpusUploadModal.vue      # Modal ingest paket ZIP naskah
│   │   └── index.ts
│   │
│   ├── auth/           # Domain: Autentikasi Pengguna
│   │   ├── AuthCard.vue               # Kartu wrapper logo & branding
│   │   ├── LoginForm.vue              # Form login email & password
│   │   ├── RegisterForm.vue           # Form pendaftaran + konsen UU PDP
│   │   └── index.ts
│   │
│   ├── landing/        # Domain: Landing Page & Edukasi Pipeline
│   │   ├── HeroSection.vue            # Hero banner & CTA
│   │   ├── PipelineTiersGrid.vue      # Edukasi deteksi 4-tier
│   │   ├── FeatureHighlights.vue      # Kepatuhan UU PDP & pgvector HNSW
│   │   └── index.ts
│   │
│   ├── verify/         # Domain: Verifikasi Sertifikat QR Publik
│   │   ├── VerificationBadge.vue      # Banner status keaslian sertifikat
│   │   ├── CertificateDetailsCard.vue # Rincian pengujian publik read-only
│   │   └── index.ts
│   │
│   └── admin/          # Domain: Panel Administrator & Hyper-Tuning
│       ├── AdminStatsGrid.vue         # Beban sistem, latensi ms, total audit
│       ├── UserManagementTable.vue    # Manajemen role & suspend akun
│       ├── SystemSettingsCard.vue     # Hyper-tuning threshold deteksi
│       └── index.ts
│
├── composables/        # Reusable Logic (Headless)
│   ├── useNotification.ts  # Global toast notification
│   ├── usePolling.ts       # Polling interval dengan auto-cleanup
│   ├── useFileUpload.ts    # Validasi berkas, drag-over, & dropzone
│   └── useModal.ts         # State reaktif buka/tutup modal
│
├── types/              # Strict TypeScript Interfaces
│   ├── admin.ts            # Tipe data admin (SystemMetric, SystemConfig, ManagedUser)
│   ├── audit.ts            # Tipe data audit (HeatmapAnnotation, MatchedSource, AuditReport)
│   ├── auth.ts             # Tipe data user & peran
│   ├── billing.ts          # Tipe data wallet & invoice
│   ├── corpus.ts           # Tipe data korpus dokumen
│   ├── document.ts         # Tipe data dokumen naskah
│   └── index.ts            # Re-export semua tipe
│
└── views/              # View Orchestrators
    ├── LandingView.vue
    ├── DashboardView.vue
    ├── AuditDetailView.vue
    ├── BillingView.vue
    ├── CorpusView.vue
    ├── VerifyView.vue
    ├── LoginView.vue
    ├── RegisterView.vue
    └── AdminView.vue
```

---

## 3. Aturan Baku Modifikasi (Rules for Agents)

### Rule 1: Dilarang Membuat Template Monolitik di `src/views/`
- Setiap berkas di `src/views/` **HARUS** berperan murni sebagai orchestrator.
- Panjang file di `src/views/` umumnya **tidak boleh melebihi 150-200 baris**.
- Jika Anda ingin menambahkan elemen visual baru (misalnya tabel baru, formulir baru, atau kartu metrik baru), buatlah sebagai komponen di `components/<domain>/` lalu impor ke view terkait.

### Rule 2: Strict Typing pada Props & Emits
- Gunakan `<script setup lang="ts">`.
- Wajib mendeklarasikan Props menggunakan interface eksplisit:
  ```ts
  interface Props {
    title: string;
    items?: ItemType[];
  }
  const props = withDefaults(defineProps<Props>(), {
    items: () => [],
  });
  ```
- Wajib mendeklarasikan Emits menggunakan signature bertipe spesifik:
  ```ts
  const emit = defineEmits<{
    (e: "submit", payload: FormData): void;
    (e: "cancel"): void;
  }>();
  ```
- **Dilarang keras menggunakan tipe `any`**. Jika butuh tipe data baru, tambahkan di `frontend/src/types/`.

### Rule 3: Jaga Barrel Export (`index.ts`)
- Setiap folder komponen domain (`common/`, `dashboard/`, `audit/`, dll.) memiliki berkas `index.ts`.
- Jika membuat komponen baru atau mengubah nama komponen, **selalu perbarui berkas `index.ts`** di folder tersebut.
- Impor pada view dianjurkan menggunakan folder export:
  ```ts
  import { UploadDropzone, AuditHistoryTable } from "../components/dashboard";
  ```

### Rule 4: Elemen Antarmuka Bersama Wajib Masuk `components/common/`
- Jangan membuat tombol, badge, modal, kartu metrik, atau alert khusus berulang kali di berbagai domain.
- Gunakan komponen dari `components/common/` (`Button.vue`, `Badge.vue`, `Modal.vue`, `StatCard.vue`, `Alert.vue`, `EmptyState.vue`, `SkeletonLoader.vue`).

### Rule 5: Logika Reaktif Asinkron Wajib Masuk Composables
- Logika seperti timer polling, upload berkas, manipulasi modal dialog, dan notifikasi toast harus menggunakan composable di `frontend/src/composables/`:
  * Notifikasi: `const { showNotification } = useNotification();`
  * Modal: `const { isOpen, open, close } = useModal();`
  * Upload Berkas: `const { selectedFile, handleFileSelect } = useFileUpload();`
  * Polling: `usePolling(callbackFn, { intervalMs: 2000 });`

### Rule 6: Kepatuhan `noUnusedLocals` & `noUnusedParameters` (Strict TS)
`tsconfig.json` proyek memiliki aturan ketat:
```json
"strict": true,
"noUnusedLocals": true,
"noUnusedParameters": true
```
- **Jangan pernah meninggalkan variabel, import, emit, atau props yang dideklarasikan tetapi tidak dibaca di `<script setup>`**.
- Jika `defineProps` hanya dipakai di template, jangan tampung dalam `const props = defineProps<...>()`. Cukup panggil `defineProps<...>()`.

### Rule 7: Wajib Verifikasi Build Sebelum Menyelesaikan Tugas
Sebelum menyatakan perubahan selesai, agent **WAJIB** mengeksekusi dua perintah ini di direktori `frontend/`:
```bash
npx vue-tsc --noEmit
npm run build
```
Kedua perintah tersebut harus keluar dengan **exit code 0 (tanpa error)**.
