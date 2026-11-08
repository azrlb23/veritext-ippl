# Frontend Handoff: Split-Screen Studio Workspace & 3-Layer Architecture

Dokumen ini mendefinisikan aturan pengembangan antarmuka pengguna (UI/UX) pada direktori `frontend/` agar tampilan Vue 3.5 selalu sinkron 100% dengan kontrak backend (`docs/API_CONTRACT.md`) dan patuh pada batas kode atomik (`docs/ATOMIC_CODING_STANDARDS.md`).

---

## 1. Lima Aturan Anti-Drifting Frontend

1. **Tipe Data Berasal dari `src/types/`**: Jangan pernah menulis ulang tipe respons secara inline di dalam komponen `.vue`. Impor antarmuka TypeScript dari `src/types/auth.ts`, `src/types/audit.ts`, `src/types/billing.ts`, atau `src/types/chat.ts`.
2. **Komponen Tidak Pernah Memanggil `axios` atau `fetch` Secara Langsung**: Seluruh panggilan HTTP wajib melewati layanan di `src/services/` (`authService.ts`, `documentService.ts`, `auditService.ts`, `chatService.ts`, `billingService.ts`) yang menggunakan instance terpusat `src/services/api.ts`.
3. **Arsitektur 3-Layer (Orchestrator - Component - Composable)**:
   - `src/views/*.vue` adalah **Orchestrator tipis (< 100 baris)** yang hanya mengatur koordinasi state Pinia, routing, dan menyusun sub-komponen.
   - `src/components/<domain>/*.vue` adalah **Komponen Presentasi murni (< 150 baris)** dengan `defineProps` dan `defineEmits` bertipe ketat.
   - `src/composables/use*.ts` adalah **Logika Reaktif Headless (< 100 baris)** seperti polling status Celery (`usePolling.ts`), filter warna heatmap (`useHeatmapFilter.ts`), dan manajemen parafrase in-place (`useParaphrase.ts`).
4. **Zero-Emoji & Utilitarian Academic UI**: Dilarang menggunakan emoji visual di seluruh template HTML, tombol, badge, maupun toast. Gunakan ikon vektor SVG bersih (Lucide Icons) dan tipografi akademik (`Plus Jakarta Sans` untuk header/UI, `Inter` untuk teks naskah, `JetBrains Mono` untuk angka skor/token/hash).
5. **Penegakan Hak Akses 3-Role di UI**:
   - `FREE`: Tampilkan lencana sisa kuota Trial AI (`3x Trial`) dan batas 2.500 kata. Saat tombol "Unduh Laporan PDF Resmi" diklik oleh `FREE`, tampilkan modal penawaran upgrade ke Premium (jangan panggil unduhan biner langsung).
   - `PREMIUM`: Buka akses penuh naskah panjang (hingga 15 MB), tombol unduh PDF ber-QR Code, serta kuota AI berbasis token.
   - `ADMIN`: Rute `/admin` hanya menampilkan 4 panel observasi Read-Only (Statistik Global, Transaksi Midtrans, Kesehatan Worker Celery/pgvector, dan Log Audit Keamanan). **Tidak boleh ada tombol suspend user, ubah role, tambah token manual, atau form pengubahan bobot algoritma.**

---

## 2. Spesifikasi Tata Letak Split-Screen Studio Workspace (`/workspace/report/:id`)

Halaman hasil analisis plagiarisme menggunakan tata letak **Split-Screen Studio Workspace** berdensitas data tinggi yang terbagi atas 3 area utama:

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ TOP SUMMARY BAR (Tinggi 64px)                                                        │
│ [Judul Naskah & Jumlah Kata] | [Skor Komposit: 18.4%] [Merah] [Oranye] [Kuning]      │
│                                | [Parafrase Semua (1 Hal)] [Unduh Laporan PDF & QR]  │
├──────────────────────────────────────────────────┬───────────────────────────────────┤
│ KOLOM KIRI (60% Lebar Layar)                     │ KOLOM KANAN (40% Lebar Layar)     │
│ Interactive Heatmap Document Viewer              │ Panel Tabular 2-in-1              │
│                                                  │ [Tab 1: Sumber] [Tab 2: AI Chat]  │
│ Filter: [Semua] [Merah] [Oranye] [Kuning] [Hijau]├───────────────────────────────────┤
│ ┌──────────────────────────────────────────────┐ │ Jika Tab 1 (Sumber Kecocokan):    │
│ │ Lembar Naskah Asli Pengguna                  │ │ - Kartu sumber terurut %          │
│ │                                              │ │ - Judul, Penulis, Tahun, Link DOI │
│ │ Kalimat normal tanpa indikasi plagiat.       │ │ - Komparasi Teks Side-by-Side     │
│ │ [Kalimat Merah: Leksikal >= 80%]             │ │                                   │
│ │ [Kalimat Oranye: Semantik >= 75%]            │ │ Jika Tab 2 (AI Chatbot & Parafrase│
│ │ [Kalimat Kuning: Stilometri / AI]            │ │ - Mode: Kalimat / Paragraf / Hal  │
│ │ [Kalimat Hijau: RESOLVED_GREEN]              │ │ - 3 Kartu Opsi Variasi + Skor Baru│
│ └──────────────────────────────────────────────┘ │ - Tombol [Terapkan ke Naskah]     │
└──────────────────────────────────────────────────┴───────────────────────────────────┘
```

### Skema Warna Semantik Heatmap (WCAG 2.1 AA Compliant)
| Kategori (`match_type`) | Warna Teks & Border | Warna Latar Sorotan | Makna Deteksi |
|---|---|---|---|
| `RED` | `#991B1B` (Border `#DC2626`) | `#FEE2E2` | Step 1 Leksikal Winnowing ($\ge 80\%$ verbatim copy-paste). |
| `ORANGE` | `#9A3412` (Border `#EA580C`) | `#FFEDD5` | Step 2 Semantik SBERT & IndoBERT ($\ge 75\%$ parafrase konsep). |
| `YELLOW` | `#854D0E` (Border `#CA8A04`) | `#FEF9C3` | Step 3 Stilometri Burstiness & Contextual AI Judge (Anomali AI). |
| `RESOLVED_GREEN` | `#166534` (Border `#16A34A`) | `#DCFCE7` | Kalimat telah berhasil diperbaiki secara in-place melalui parafrase. |

---

## 3. Alur Interaksi In-Place Paraphrase & Real-Time Re-Scoring

1. Pengguna mengklik kalimat bertanda `RED`, `ORANGE`, atau `YELLOW` pada `HeatmapViewer.vue`.
2. Muncul `SentencePopover.vue` dengan 3 tombol aksi kontekstual:
   - `[Parafrase Kalimat Ini]` (`mode = 'SENTENCE'`)
   - `[Parafrase Paragraf Ini]` (`mode = 'PARAGRAPH'`)
   - `[Bandingkan dengan Sumber Asli]` (Membuka Tab 1 `SideBySideDiff.vue`).
3. Jika pengguna memilih opsi parafrase, panel kanan otomatis berpindah ke **Tab 2 (`AiAssistantTab.vue`)** dan memanggil `POST /api/v1/chat/paraphrase`.
4. Panel kanan merender 3 kartu variasi kalimat ilmiah (`ParaphraseOptionCard.vue`), masing-masing menampilkan gaya bahasa dan prediksi penurunan skor kemiripan (misal: `Turun dari 86.4% ke 12.0%`).
5. Saat pengguna menekan tombol **`[Terapkan ke Naskah]`** pada salah satu variasi:
   - Frontend memanggil `POST /api/v1/chat/apply-paraphrase`.
   - Backend memperbarui `current_text` pada `audit_sentences`, mengubah `match_type` menjadi `'RESOLVED_GREEN'`, dan mengembalikan `new_similarity_score` serta `new_composite_score`.
   - Store Pinia memperbarui kalimat di `HeatmapViewer.vue` secara reaktif tanpa me-reload halaman: warna sorotan berubah menjadi Hijau dan angka skor komposit pada `TopSummaryBar.vue` langsung turun seketika.
