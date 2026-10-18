# Rules: Frontend Modularization & Component Architecture
> Location: `.agent/rules/frontend-modularization.md`
> Scope: `frontend/` (Vue 3 + TypeScript + Vite + Tailwind CSS)

Lihat dokumentasi lengkap di: `frontend/MODULAR_RULES.md`

## Ringkasan Aturan untuk Agent:

1. **Views Are Orchestrators Only**:
   - `src/views/*` TIDAK BOLEH memuat markup template monolitik.
   - Views hanya mengoordinasikan sub-komponen, stores, composables, dan routing.
   - Komponen visual baru harus ditempatkan di `src/components/<domain>/`.

2. **Daftar Domain Komponen**:
   - `components/common/`: UI atomik serbaguna (`Button`, `Badge`, `Modal`, `StatCard`, `Alert`, `EmptyState`, `SkeletonLoader`).
   - `components/dashboard/`: Pengujian naskah (`UploadDropzone`, `AuditProgressTracker`, `AuditHistoryTable`, `DashboardStatsGrid`).
   - `components/audit/`: Laporan audit (`ScoreSummaryCard`, `SideBySideDiff`, `SentenceDetailModal`, `ExportReportActions`, `MatchedSourcesTable`, `HeatmapViewer`, `SimilarityGauge`, `TierLegend`).
   - `components/billing/`: Kuota & Midtrans (`TokenBalanceCard`, `PlanCard`, `TransactionHistoryTable`, `TopupModal`).
   - `components/corpus/`: Repositori naskah (`CorpusStatsGrid`, `CorpusFilterBar`, `CorpusTable`, `CorpusUploadModal`).
   - `components/auth/`: Akun (`AuthCard`, `LoginForm`, `RegisterForm`).
   - `components/landing/`: Edukasi naskah (`HeroSection`, `PipelineTiersGrid`, `FeatureHighlights`).
   - `components/verify/`: Sertifikat QR (`VerificationBadge`, `CertificateDetailsCard`).
   - `components/admin/`: Panel pengawasan & tuning (`AdminStatsGrid`, `UserManagementTable`, `SystemSettingsCard`).

3. **Composables Reusable (`src/composables/`)**:
   - `useNotification.ts`: Toast global.
   - `usePolling.ts`: Polling otomatis dengan `onUnmounted` cleanup.
   - `useFileUpload.ts`: Drag-and-drop & file validation.
   - `useModal.ts`: State buka/tutup modal.

4. **Strict TypeScript Compliance**:
   - `defineProps<Props>()` dan `defineEmits<Emits>()` wajib bertipe eksplisit.
   - Tidak boleh ada unused variable (`noUnusedLocals` dan `noUnusedParameters` aktif).
   - Selalu eksekusi `npx vue-tsc --noEmit` dan `npm run build` sebelum menyelesaikan tugas.
