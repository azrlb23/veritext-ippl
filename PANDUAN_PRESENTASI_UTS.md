# PANDUAN RUNUT PRESENTASI EVALUASI UTS IPPL
**Proyek:** VeriText AI — *Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical & Semantic AI Engine*  
**Mata Kuliah:** Rekayasa Perangkat Lunak / IPPL (Implementasi & Pengujian Perangkat Lunak)  
**Pengembang:** Mochammad Azriel Albian Putra (11241045)  
**Target Durasi:** 12 – 15 Menit

---

## 1. PETA ALUR RUNUT DEMO (ROADMAP)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ALUR RUNUT DEMO EVALUASI UTS                         │
└────────────────────────────────────────────────────────────────────────┘
                                   │
  [SEGMEN 1: TAMU / PUBLIK]        ▼  (00:00 - 02:00)
  • Problem Statement: Kelemahan Turnitin leksikal vs Parafrasa AI
  • Prinsip Least Privilege: Navbar tamu hanya Beranda & Verifikasi QR
  • Demo Interaktif 3 Tab Diagnostik di Landing Page
                                   │
  [SEGMEN 2: MAHASISWA (CORE)]     ▼  (02:00 - 07:00)
  • Login Mahasiswa (azriel@kampus.ac.id) & Dompet Token
  • Upload Live contoh_naskah_uji.txt (SHA-256 Hashing)
  • Reactive Polling: 10% -> 25% -> 40% -> 65% -> 85% -> 100%
  • Bedah Interactive Heatmap 3-Warna:
    - Merah (Bab I): Winnowing Leksikal (Copy-Paste murni)
    - Oranye (Bab II): Semantik Cosine Similarity >= 0.75 (Parafrasa ide)
    - Kuning (Bab III): Anomali Stilometri / AI Monoton (ChatGPT)
    - Bersih / Putih (Bab IV): Teks Orisinal Mahasiswa
  • Side-by-Side Diff & Rincian Offset Kalimat
  • Unduh Sertifikat PDF Resmi ber-QR Code Kriptografis
                                   │
  [SEGMEN 3: PUBLIK / VERIFIKASI QR] ▼ (07:00 - 08:30)
  • Buka /verify/:uuid di tab incognito (Simulasi scan QR oleh Dosen)
  • Kepatuhan UU PDP No. 27/2022 (Right to be Forgotten)
                                   │
  [SEGMEN 4: DOSEN / REVIEWER]     ▼  (08:30 - 10:00)
  • Login Dosen (dosen@kampus.ac.id)
  • Menu khusus Bank Korpus (/corpus): Filter kategori & ingest naskah
                                   │
  [SEGMEN 5: SUPER ADMINISTRATOR]  ▼  (10:00 - 12:00)
  • Login Admin (admin@veritext.ai) & Dedicated Console (/admin)
  • 5 Tab: Overview Metrik, Kelola User & Token, Tuning AI, Log Forensik CSV
                                   │
  [SEGMEN 6: CAPAIAN & QA]         ▼  (12:00 - 15:00)
  • Capaian UTS: 42,86% (Target minimal 30%)
  • Bukti 81 Automated Tests (100% Pass Rate) di Terminal
  • Sesi Tanya Jawab
```

---

## 2. DETAIL AKSI LAYAR & PANDUAN BICARA PER SEGMEN

### Segmen 1: Pembukaan, Problem Statement & Tamu (00:00 – 02:00)
- **Aksi Layar:** Buka browser di `http://localhost:5173/` (Landing Page).
- **Sorotan Antarmuka:** 
  1. Navbar Tamu hanya berisi `Beranda` dan `Verifikasi QR` (Prinsip *Least Privilege*).
  2. Tab demo interaktif Tier 1, Tier 2, dan Tier 3 pada komponen demo landing page.
- **Naskah Bicara:**
  > *"Selamat pagi/siang Bapak/Ibu Dosen Penguji. Hari ini kami mempresentasikan **VeriText AI**, Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical & Semantic AI Engine.*
  > 
  > *Masalah nyata di dunia akademik: alat deteksi konvensional seperti Turnitin hanya mencocokkan string leksikal kata-per-kata. Begitu mahasiswa memparafrasa naskah dengan sinonim atau AI-spinner, kesamaan string turun ke 0%. Sebaliknya, detektor AI komersial saat ini bekerja layaknya black-box yang menuduh tanpa transparansi bukti kalimat mana yang bermasalah.*
  > 
  > *VeriText AI memadukan 3 mesin analitik dalam satu pipa komputasi: algoritma Winnowing Fingerprinting deterministik, representasi semantik vektor 384 dimensi berbasis pgvector HNSW, dan analisis ritme stilometri AI."*

---

### Segmen 2: Mahasiswa — Live Upload, Heatmap & PDF (02:00 – 07:00)
- **Aksi Layar 1:** Login akun Mahasiswa (`azriel@kampus.ac.id` / `VeriText#2026`).
- **Aksi Layar 2:** Drag-and-drop file `contoh_naskah_uji.txt`, pilih mode **Pemeriksaan Penuh (FULL - 2 Token)**, klik **Mulai Audit**.
- **Aksi Layar 3:** Tunjukkan progress bar reaktif (10% &rarr; 25% &rarr; 40% &rarr; 65% &rarr; 85% &rarr; 100%).
- **Aksi Layar 4:** Buka laporan audit:
  - Tunjukkan **Skor Komposit** terbobot: $50\% \text{ Leksikal} + 35\% \text{ Semantik} + 15\% \text{ Stilometri}$.
  - Tunjukkan **Heatmap 3-Warna**:
    - 🔴 **Merah (Bab I):** Jiplakan kata-per-kata langsung tertangkap Winnowing.
    - 🟠 **Oranye (Bab II):** Parafrasa sinonim yang lolos dari leksikal, tertangkap oleh embedding semantik.
    - 🟡 **Kuning (Bab III):** Teks seragam ChatGPT yang terdeteksi karena varians panjang kalimat monoton (*Burstiness* rendah).
    - ⚪ **Putih/Bersih (Bab IV):** Naskah orisinal tanpa stabilo.
  - Klik salah satu kalimat merah/oranye untuk membuka **Side-by-Side Diff** (membandingkan teks mahasiswa dengan naskah asli jurnal).
  - Klik **"Unduh Sertifikat PDF"** & perlihatkan PDF hasil unduhan dengan nama rapi (`Sertifikat_VeriText_...pdf`) dan kode QR yang valid.
- **Naskah Bicara:**
  > *"Pada skenario mahasiswa, pemrosesan naskah didelegasikan ke antrean latar belakang Celery & Redis dengan polling reaktif. Jika Redis tidak aktif, backend memiliki mekanisme fallback in-process daemon otomatis sehingga proses tidak pernah freeze.*
  > 
  > *Laporan hasil audit memetakan masalah secara transparan: Bab I tertangkap merah karena plagiat leksikal, Bab II tertangkap oranye karena plagiat semantik ide, dan Bab III tertangkap kuning karena teks buatan AI. Sertifikat resmi ber-QR Code juga dapat langsung diunduh secara resmi."*

---

### Segmen 3: Publik — Verifikasi QR & Kepatuhan UU PDP (07:00 – 08:30)
- **Aksi Layar:** Buka jendela Incognito (tanpa login), akses URL `/verify/:uuid` (simulasi scan QR oleh penguji).
- **Sorotan Antarmuka:** Validasi integritas digital berbasis UUID kriptografis.
- **Naskah Bicara:**
  > *"Pihak penguji atau kampus tidak perlu meminta file mentah mahasiswa. Cukup scan QR code pada sertifikat PDF untuk memvalidasi keaslian naskah di portal publik.*
  > 
  > *Sistem kami juga patuh pada **UU PDP No. 27/2022 (Right to be Forgotten)**: jika mahasiswa menghapus naskahnya, portal verifikasi otomatis menampilkan status kedaluwarsa tanpa membocorkan identitas pemilik."*

---

### Segmen 4: Dosen / Reviewer — Bank Korpus Internal (08:30 – 10:00)
- **Aksi Layar:** Logout, login akun Dosen (`dosen@kampus.ac.id` / `VeriText#2026`).
- **Sorotan Antarmuka:** Menu **Bank Korpus** (`/corpus`) muncul khusus untuk Dosen/Reviewer untuk mengunggah repositori naskah lokal kampus yang diindeks ke pgvector.
- **Naskah Bicara:**
  > *"Dosen memiliki wewenang mengelola Bank Korpus kampus. Dokumen dipecah menjadi chunk kalimat, diekstrak sidik jari leksikalnya, dan diindeks ke PostgreSQL pgvector. Ini menjamin kedaulatan data kampus tanpa harus mengirim naskah ke server pihak ketiga di luar negeri."*

---

### Segmen 5: Super Administrator — Enterprise Console (10:00 – 12:00)
- **Aksi Layar:** Logout, login akun Super Admin (`admin@veritext.ai` / `VeriText#2026`).
- **Sorotan 5 Tab Admin:**
  1. **Overview & Metrik:** Telemetri latensi basis data, Celery worker, dan total vektor chunk.
  2. **Kelola Pengguna:** CRUD user, reset password, dan koreksi saldo token.
  3. **Tuning Engine AI:** Pengaturan ambang batas semantik (0.75) dan trigger re-index HNSW.
  4. **Log Audit Forensik:** Jejak aktivitas aktor + tombol **Ekspor CSV**.
- **Naskah Bicara:**
  > *"Konsol Super Administrator terisolasi penuh sesuai prinsip Separation of Concerns. Admin dapat memantau telemetri sistem secara real-time, mengoreksi saldo token secara transaksional, mengkalibrasi hyperparameter engine, dan mengunduh jejak audit forensik dalam format CSV."*

---

### Segmen 6: Capaian UTS & Penutup (12:00 – 15:00)
- **Aksi Layar:** Tampilkan slide rangkuman / terminal hasil pengujian otomatis.
- **Sorotan:**
  - Capaian Fungsional: **42,86% (3 dari 7 modul inti selesai 100%, melebihi target UTS 30%)**.
  - Kualitas Kode: **81 Automated Tests (100% Pass Rate)**: 56 Backend tests + 25 Frontend navigation tests.
- **Naskah Bicara:**
  > *"Sebagai penutup, VeriText AI telah melampaui target implementasi UTS dengan progres fungsional 42,86% dan dilindungi oleh 81 automated tests tanpa kegagalan. Kami siap membuka sesi tanya jawab untuk Bapak/Ibu Dosen Penguji."*

---

## 3. ANTISIPASI PERTANYAAN KRITIS DOSEN PENGUJI

| Pertanyaan Dosen Penguji | Poin Jawaban Teknis Rekayasa |
| :--- | :--- |
| **Kenapa pakai Winnowing, bukan Levenshtein / Jaccard biasa?** | Levenshtein memiliki kompleksitas $O(N \times M)$ yang sangat lambat untuk dokumen panjang. Winnowing menggunakan **Rabin-Karp Rolling Hash** berkecepatan $O(1)$ per jendela dengan jaminan matematis bahwa kesamaan substring minimal 8 karakter pasti terdeteksi. |
| **Kenapa pgvector HNSW, bukan IVFFlat atau DB terpisah?** | IVFFlat butuh training centroid dan kualitas pencariannya turun jika data bertambah. **HNSW** berbasis graf multi-layer dengan kompleksitas pencarian $O(\log N)$. Menggunakan pgvector di PostgreSQL menjamin konsistensi **transaksi ACID** tanpa repot sinkronisasi ke DB terpisah. |
| **Bagaimana membuktikan teks buatan AI? Bukankah rawan false positive?** | Tier 3 kami tidak berdiri sendiri, melainkan menggabungkan **Burstiness (varians panjang kalimat)**, **Sentence Uniformity**, dan **Marker Patterns**. Sitasi formal diabaikan secara cerdas, dan bobot Tier 3 pada skor akhir hanya dibatasi $15\%$ untuk mencegah tuduhan keliru. |
| **Kenapa harus Celery & Redis? Kalau servernya mati gimana?** | Ekstraksi teks dan inferensi vektor adalah operasi *CPU-bound*. Jika dijalankan langsung di FastAPI, server web akan mengalami *thread starvation* (timeout). Jika Celery/Redis mati, sistem kami memiliki **fallback in-process daemon threading otomatis** sehingga tidak pernah macet. |
| **Bagaimana keamanan hak aksesnya?** | *Defense-in-depth*: Rute frontend dijaga oleh navigation guards (25 pengujian lulus), backend dijaga oleh middleware JWT `require_role("ADMIN")`, dan query database dibatasi ketat per `user_id` untuk mencegah celah IDOR. |

---

## 4. PRE-FLIGHT CHECKLIST DEMO

1. **File Naskah Uji Siap Saji:** [`contoh_naskah_uji.txt`](file:///Users/azrlb23/Documents/IPPL/contoh_naskah_uji.txt) (waktu proses cuma ~3 detik dan langsung memicu 4 warna heatmap secara sempurna).
2. **Kredensial Akun Sandbox Demo:**
   - **Mahasiswa:** `azriel@kampus.ac.id` / `VeriText#2026`
   - **Dosen:** `dosen@kampus.ac.id` / `VeriText#2026`
   - **Super Admin:** `admin@veritext.ai` / `VeriText#2026`
3. **Perintah Menjalankan Servis:**
   - Database & Redis: `docker compose up -d`
   - Backend: `cd backend && venv/bin/uvicorn app.main:app --reload --port 8000`
   - Frontend: `cd frontend && npm run dev`
