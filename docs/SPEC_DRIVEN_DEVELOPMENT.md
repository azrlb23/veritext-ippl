# Spec-Driven Development (SDD) Guide & Playbook: VeriText AI

Dokumen ini mendefinisikan metodologi rekayasa perangkat lunak **Spec-Driven Development (SDD)** yang diwajibkan dalam pengembangan platform VeriText AI. Metodologi ini memastikan bahwa setiap baris kode yang ditulis telah melalui perancangan spesifikasi, kontrak API, dan dekomposisi tugas atomik terlebih dahulu.

---

## 1. Prinsip Utama Spec-Driven Development

Dalam VeriText AI, prinsip dasar SDD adalah:
* **Tidak Ada Kode Tanpa Spesifikasi Terkunci**: Dilarang menulis kode logika bisnis sebelum kontrak API (`docs/API_CONTRACT.md`) dan skema data (`docs/DATABASE_SCHEMA.md`) disepakati dan dikunci.
* **Pengembangan Bersamaan (Concurrent Engineering)**: Frontend dan Backend dapat bekerja secara simultan tanpa saling memblokir (*unblocked*) karena bentuk data respons (*payload*) telah didefinisikan secara presisi.
* **Verifikasi Mandiri Sebelum Integrasi**: Setiap irisan tugas kecil wajib diverifikasi dengan perintah pengujian otomatis sebelum digabungkan ke cabang utama (*main branch*).

---

## 2. Siklus 5-Fase Berpagar Gerbang (The 5-Phase Gated Lifecycle)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   FASE 0    │ ──> │    FASE 1    │ ──> │    FASE 2    │ ──> │    FASE 3    │ ──> │    FASE 4    │
│ Scope Check │     │ Contract &   │     │ Review Gate  │     │ Atomic Task  │     │ Implement &  │
│ & Map       │     │ Spec First   │     │ & Sign-Off   │     │ Breakdown    │     │ Verify (TDD) │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

### Fase 0: Scope Check & Pemetaan Kemampuan
1. Setiap fitur atau kebutuhan baru dianalisis dan dipetakan ke dalam salah satu dari 8 modul atomik:
   * `mod-auth`, `mod-preprocessor`, `mod-pipeline-lexical`, `mod-pipeline-semantic`, `mod-pipeline-judge`, `mod-assistant`, `mod-billing`, `mod-report-admin`.
2. Menetapkan dependensi satu arah (*one-way dependency*) antar modul untuk mencegah keterikatan melingkar (*circular dependency*).

---

### Fase 1: Desain Kontrak & Spesifikasi Terlebih Dahulu (Contract-First)
Sebelum membuat berkas `.py` atau `.vue`:
1. Definisikan jalur endpoint, metode HTTP, skema masukan (*request*), dan skema keluaran (*response*) pada **`docs/API_CONTRACT.md`**.
2. Definisikan skema tabel basis data dan tipe data kolom pada **`docs/DATABASE_SCHEMA.md`**.
3. Pastikan penanganan kode galat (*error code*) telah terdaftar di katalog galat resmi sistem.

---

### Fase 2: Gerbang Evaluasi dan Persetujuan (Review Gate)
* Tim Frontend mengevaluasi: *"Apakah seluruh field yang dibutuhkan untuk merender UI Workspace (seperti persentase tier, highlight warna, dan rujukan DOI) sudah ada dalam respons API?"*
* Tim Backend/AI mengevaluasi: *"Apakah formula komputasi dan penanganan failover LLM dapat dieksekusi secara aman dan hemat biaya?"*
* **Aturan Keras**: Koding tidak boleh dimulai sebelum Fase 1 dan Fase 2 disetujui.

---

### Fase 3: Pemecahan Tugas Atomik (Atomic Task Breakdown)
1. Pecah pekerjaan menjadi irisan tugas berukuran kecil/sedang (*S/M Task Slices*):
   * Satu tugas hanya menyentuh **1 hingga 4 berkas**.
   * Ukuran setiap berkas kode dibatasi **maksimal 150 baris kode**.
2. Setiap tugas dalam daftar kerja (*task list*) wajib memiliki:
   * **Deskripsi Jelas**: Apa fungsi atomik yang dibuat.
   * **Kriteria Keberterimaan (Acceptance Criteria)**: Syarat fungsional yang harus terpenuhi.
   * **Perintah Verifikasi Eksplisit**: Perintah terminal langsung untuk menguji kode (misal: `cd backend && ./venv/bin/pytest tests/test_engine.py -q`).

---

### Fase 4: Implementasi Paralel & Verifikasi Otomatis (TDD Workflow)
Dengan kontrak yang terkunci rapat:
1. **Frontend**:
   * Dapat mengimplementasikan komponen antarmuka Vue 3 dan *composables* menggunakan data tiruan (*mock data*) yang formatnya persis dengan `API_CONTRACT.md`.
2. **Backend**:
   * Mengimplementasikan endpoint FastAPI, skema Pydantic, dan worker Celery yang mencocokkan kontrak API secara presisi.
   * Mengembangkan tes unit dan integrasi otomatis dengan *pytest*.
3. **Verifikasi Bersama**:
   * Jalankan pengujian menyeluruh: seluruh pengujian unit harus berstatus hijau (*100% passed*).

---

## 3. Matriks Peran dan Tanggung Jawab

| Peran | Tanggung Jawab Utama dalam SDD |
|---|---|
| **Brain / Lead Architect (Primary: Gemini Argon / Claude Sonnet; Fallback: Flash High)** | Mengawasi kepatuhan 4-lapis, menyusun prompt spesifikasi atomik, menugaskan subagen Worker, dan mengaudit batas sub-150 LOC serta Zero-Emoji. |
| **Worker Subagent (`Model="flash"`, `EnableWriteTools=True`)** | Mengeksekusi implementasi kode atomik (1–4 berkas per tugas), menjalankan unit test (`pytest` / `npm run build`), dan melaporkan status ke Brain. |

---

## 4. Protokol Orkestrasi Multi-Agen: Brain (Argon / Sonnet -> Fallback Flash) + Worker (Flash)

Untuk menjaga efisiensi token, kecepatan eksekusi tinggi, dan ketelitian arsitektural, pengerjaan setiap fase pada `tasks/todo.md` wajib mengikuti alur **Brain-Worker Delegation** dengan skema fallback model:

* **Hierarki Pemilihan Model Brain**:
  1. **Primary Brain**: **Gemini Argon** atau **Claude Sonnet**.
  2. **Fallback Brain**: Apabila Gemini Argon dan Claude Sonnet tidak tersedia atau mencapai batas kuota (*rate limit*), sesi utama (**Brain**) otomatis beralih menggunakan **Gemini Flash (High)** tanpa mengubah disiplin verifikasi SDD.
* **Alur Kerja Eksekusi**:
  1. **Perencanaan Irisan oleh Brain**:
     - Brain membaca tugas aktif di `tasks/todo.md` serta kontrak terkait di `docs/`.
     - Brain menyiapkan instruksi kerja yang eksplisit (daftar berkas target, tanda tangan fungsi/kelas, batasan $\le 150$ LOC per berkas, dan perintah uji).
  2. **Delegasi Eksekusi ke Worker (`Model="flash"`)**:
     - Brain mendaftarkan tipe subagen `atomic-flash-worker` menggunakan `define_subagent` (`EnableWriteTools=True`).
     - Brain memanggil `invoke_subagent(TypeName="atomic-flash-worker", Model="flash", ...)` untuk mengeksekusi 1 irisan tugas (*S/M Task Slice*).
     - Worker menulis berkas kode, memeriksa jumlah baris (`wc -l`), menjalankan linter dan unit test, lalu mengirimkan laporan ringkas kembali ke Brain.
  3. **Audit & Sign-Off oleh Brain**:
     - Brain memverifikasi laporan Worker, memastikan tidak ada regresi, tidak ada berkas $> 150$ LOC, dan tidak ada karakter emoji, sebelum menandai tugas `[x]` selesai di `tasks/todo.md`.
