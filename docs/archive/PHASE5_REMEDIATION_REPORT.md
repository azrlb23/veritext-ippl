# VeriText AI — Dokumen Verifikasi & Laporan Remediasi Fase 5
## Ketahanan Engine AI, Visualisasi Heatmap & Frontend Error Boundaries

> **Tanggal Rilis**: 24 Oktober 2026  
> **Status Verifikasi**: Selesai Diverifikasi 100% (Green Test Suite)  
> **Metode Pelaksanaan**: Test-Driven Development (TDD) — *Red, Green, Refactor*  
> **Cakupan Pengujian**: 182 Backend Unit & Integration Tests (178 Existing + 4 New Phase 5 Suites dengan Edge Cases Komprehensif) & 25 Frontend Navigation & Security Tests  

---

## 1. Ringkasan Eksekutif & Temuan yang Diperbaiki

Pada perbaikan **Fase 5**, rekayasa perangkat lunak VeriText AI berfokus pada **ketahanan komputasi mesin deteksi plagiarisme (AI Engine Stability)**, **eliminasi memory leak pada inferensi PyTorch / Sentence Transformers**, **proteksi keamanan dekompresi arsip korpus (Anti Zip-Slip & Anti Zip-Bomb)**, serta **eliminasi data mock/dummy pada visualisasi Heatmap naskah dan Side-by-Side Diff**.

Tabel berikut merangkum 4 temuan teknis utama yang berhasil dituntaskan dan diverifikasi:

| ID Temuan | Kategori Keparahan | Klasifikasi Celah | Deskripsi Masalah | Status Remediasi |
|---|:---:|---|---|:---:|
| **[C4 & DTO]** | **Tinggi (High)** | Data Flow & Frontend Contract Defect | DTO `AuditReportResponse` tidak memuat `document_text`, memaksa UI menggunakan paragraf statis/dummy | **RESOLVED & VERIFIED** |
| **[ROBUSTNESS]** | **Sedang (Medium)** | Numerical Instability / Crash Risk | Input `NaN` atau `Inf` pada agregator komposit dapat merusak kalkulasi skor dan menghasilkan respons JSON invalid | **RESOLVED & VERIFIED** |
| **[RAM LEAK]** | **Tinggi (High)** | Resource Exhaustion / RAM Leak | Model transformer diinisialisasi ulang tanpa batas dan inferensi autograd graph tidak dinonaktifkan (`torch.inference_mode`) | **RESOLVED & VERIFIED** |
| **[SECURITY]** | **Tinggi (High)** | Path Traversal & Denial of Service | Dekompresi arsip ZIP korpus rentan terhadap Directory Traversal (Zip-Slip) dan uncompressed DoS (Zip-Bomb) | **RESOLVED & VERIFIED** |

---

## 2. Rincian Modifikasi Teknis & Verifikasi Kode

### 2.1. Dynamic Manuscript Delivery & DTO Hardening (`backend/app/schemas/audit.py`, `models/audit.py`, `api/v1/reports.py`)
- **Implementasi**: Penambahan field `document_text: Optional[str] = None` pada skema `AuditReportResponse` dan `AuditReport` interface frontend.
- **Resolusi Otomatis & Preservasi Offset**: Property `document_text` pada model `AuditReport` mengutamakan pembacaan naskah fisik asli dari disk via `TextPreprocessor.extract_text_from_file`. Jika jatuh pada fallback rekonstruksi kalimat database, celah antar kalimat dipadukan dengan gap padding berbasis `start_char` agar koordinat karakter heatmap `document_text[start:end]` selalu presisi.
- **Query Optimization**: Endpoint `GET /api/v1/reports/{report_id}` mengaktifkan eager loading `selectinload(AuditTask.sentences)` untuk efisiensi kueri database tanpa N+1 overhead.

### 2.2. Robustness & Sanitasi Nilai NaN/Inf Mesin Tier 4 (`backend/app/engine/tier4_aggregator.py`)
- **Implementasi**: Penambahan metode utilitas statis `HybridAggregator.sanitize_score(val)` yang diterapkan pada `calculate_composite_score`, `run_pipeline`, dan seluruh field nilai skor di `HybridAuditResult`.
- **Mekanisme**: Setiap skor masukan (T1 Leksikal, T2 Semantik, T3 Stilometri, dan skor komposit) divalidasi terhadap `math.isnan()` dan `math.isinf()`. Jika ditemukan nilai tidak wajar, dinormalisasi ke `0.0`. Seluruh skor dibatasi secara ketat dalam interval `[0.0, 100.0]` dan dibulatkan ke 2 desimal.

### 2.3. Singleton Transformer, PyTorch Inference Mode & Batching (`backend/app/engine/tier2_semantic.py`)
- **Implementasi**: Pola Singleton model via `SemanticEngine.get_shared_model()`. Instance `SentenceTransformer` hanya dimuat sekali dan digunakan bersama di seluruh instansiasi mesin analisis.
- **Batch Processing**: Penambahan metode `embed_sentences(texts)` untuk komputasi embedding dalam batch (`batch_size=32`) secara efisien.
- **Memory Leak Elimination**: Ekstraksi inferensi vektor semantik dibungkus dalam `torch.inference_mode()` (atau fallback `torch.no_grad()`). Penghentian pelacakan komputasi gradien secara drastis mengurangi jejak alokasi RAM server dan mencegah kebocoran memori pada beban pemrosesan naskah ribuan halaman.

### 2.4. Dekompresi Aman Berkas Korpus ZIP (`backend/app/services/corpus_service.py` & `workers/tasks.py`)
- **Implementasi**: Metode `CorpusService.extract_zip_safely(zip_file, target_dir, max_uncompressed_bytes)`.
- **Proteksi Zip-Slip**: Setiap entri path berkas di dalam arsip divalidasi menggunakan `os.path.abspath(target_path).startswith(target_dir_abs + os.sep)`. Entri yang memuat manipulasi `../` atau path absolut langsung ditolak dengan HTTP 400 Bad Request.
- **Proteksi Zip-Bomb**: Sistem menghitung total ukuran uncompressed bytes kumulatif dari header ZIP dan secara aktif memantau ukuran aliran stream saat proses ekstraksi berlangsung. Jika melampaui batas keamanan (maks 200MB), dekompresi dihentikan dan melempar HTTP 400 Bad Request.
- **Proteksi Symlink & File Korup**: Memeriksa atribut `stat.S_ISLNK(mode)` pada header arsip untuk menolak symlink traversal, serta menangkap `zipfile.BadZipFile` untuk mengembalikan HTTP 400.
- **Integrasi Celery Worker**: Fungsi worker `index_corpus_document` mengintegrasikan `extract_zip_safely` untuk mengekstrak dan membaca seluruh dokumen teks di dalam arsip ZIP korpus sebelum segmentasi dan pembuatan embedding pgvector.

### 2.5. Rekayasa Visualisasi Interaktif Heatmap & Side-by-Side Diff (`frontend/src/...`)
- **`HeatmapViewer.vue`**:
  - Seluruh data dummy/mock paragraf statis dihapus 100%.
  - Teks naskah asli dirender secara dinamis melalui komputasi slice karakter (`renderedSlices`) yang memadukan rentang offset `start_char` dan `end_char` dari hasil deteksi 3 tier (T1 Merah, T2 Oranye, T3 Kuning).
  - Algoritma pemotongan teks mendukung penanganan span tumpang tindih (*overlapping annotations*) secara mulus tanpa menghilangkan teks naskah.
  - Dilengkapi kontrol filter lapisan sorotan per-tier yang reaktif.
- **`SideBySideDiff.vue`**:
  - Kolom kiri: Menampilkan kalimat naskah asli pengguna yang diekstrak langsung dari offset dokumen.
  - Kolom kanan: Menampilkan kutipan segmen korpus pembanding rujukan hasil temu balik semantik/leksikal.
  - Indeks seleksi diproteksi dengan komputasi aman (`safeIndex`) dan `currentAnnotation` untuk mencegah akses `undefined` saat daftar anotasi berubah.
- **`audit.ts` Pinia Store**:
  - Penambahan metode `stopPolling()` dan jaminan pemanggilan `clearInterval` pada unmount, pergantian rute, maupun reset state untuk mengeliminasi background timer leak.

---

## 3. Hasil Pengujian Verifikasi TDD

```
test_tc_sec_30_dto_includes_document_text: OK
test_tc_sec_31_engine_nan_inf_score_sanitization: OK
test_tc_sec_32_pytorch_inference_mode_singleton: OK
test_tc_sec_33_safe_zip_decompression_anti_bomb_slip: OK

Ran 4 tests in 0.101s
OK
Ran 182 total backend tests in 6.629s
OK (100% Pass)
```
