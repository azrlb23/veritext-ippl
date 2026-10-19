# PANDUAN PRESENTASI UTS IPPL — VeriText AI

**Proyek:** VeriText AI — Sistem Deteksi Plagiarisme Hybrid Lexical & Semantic  
**Pengembang:** Mochammad Azriel Albian Putra (11241045)  
**Durasi Target:** 12–15 menit

---

## URUTAN DEMO (dari mana ke mana)

| # | Segmen | Akun yang Dipakai | Durasi |
|---|--------|-------------------|--------|
| 1 | Landing Page (Tamu) | Tanpa login | 00:00 – 02:00 |
| 2 | Upload & Audit Naskah (Mahasiswa) | `azriel@kampus.ac.id` | 02:00 – 07:00 |
| 3 | Verifikasi Sertifikat (Publik) | Tab Incognito | 07:00 – 08:30 |
| 4 | Bank Korpus (Dosen) | `dosen@kampus.ac.id` | 08:30 – 10:00 |
| 5 | Konsol Admin | `admin@veritext.ai` | 10:00 – 12:00 |
| 6 | Capaian & Tanya Jawab | — | 12:00 – 15:00 |

Password semua akun: `VeriText#2026`

---

## SEGMEN 1: Landing Page — Tamu (00:00–02:00)

**Buka:** `http://localhost:5173`

**Yang ditunjukkan:**
- Navbar tamu hanya menampilkan **Beranda** dan **Verifikasi QR** — tidak ada menu Dashboard, Korpus, atau Admin (prinsip *least privilege*)
- Klik tab **Tier 1**, **Tier 2**, **Tier 3** di komponen demo interaktif untuk memperlihatkan cara kerja masing-masing mesin deteksi

**Poin bicara:**
> Turnitin hanya mencocokkan kata per kata. Begitu mahasiswa memparafrasa menggunakan sinonim, kemiripan leksikal bisa turun ke 0%. VeriText AI memadukan tiga mesin: Winnowing leksikal, embedding semantik 384 dimensi, dan analisis stilometri — semuanya berjalan dalam satu pipeline.

---

## SEGMEN 2: Upload & Audit Naskah — Mahasiswa (02:00–07:00)

**Login:** `azriel@kampus.ac.id`

**Urutan aksi:**
1. Drag-and-drop file `contoh_naskah_uji.txt` ke dropzone, pilih **FULL (2 Token)**, klik **Mulai Audit**
2. Tunjukkan progress bar bergerak: 10% → 25% → 40% → 65% → 85% → 100%
3. Klik **Lihat Laporan** saat selesai

**Di halaman laporan, tunjukkan satu per satu:**

| Komponen | Yang Ditunjukkan |
|----------|-----------------|
| Skor Komposit | Hasil akhir: 50% Leksikal + 35% Semantik + 15% Stilometri |
| Heatmap — Merah (Bab I) | Copy-paste langsung, tertangkap Winnowing rolling hash |
| Heatmap — Oranye (Bab II) | Parafrasa sinonim, tertangkap cosine similarity >= 0.75 |
| Heatmap — Kuning (Bab III) | Kalimat panjangnya seragam = pola ChatGPT (burstiness rendah) |
| Heatmap — Bersih (Bab IV) | Naskah orisinal, tidak ditandai |
| Side-by-Side Diff | Klik kalimat merah/oranye → muncul perbandingan dengan naskah sumber |
| Tabel Sumber Cocok | Dokumen rujukan mana yang paling banyak dicontek + persentasenya |
| Unduh Sertifikat PDF | Klik "Unduh Sertifikat PDF" → file keluar dengan nama rapi + QR Code aktif |

**Poin bicara:**
> Kalau Celery/Redis tidak aktif, backend punya fallback thread daemon otomatis — proses tetap jalan, tidak freeze.

---

## SEGMEN 3: Verifikasi Sertifikat — Publik (07:00–08:30)

**Buka:** Tab incognito, akses `/verify/:uuid` (salin dari halaman laporan)

**Yang ditunjukkan:**
- Siapapun bisa memvalidasi keaslian sertifikat tanpa perlu login
- UUID sertifikat dicocokkan ke database secara langsung
- Jika mahasiswa sudah menghapus naskahnya (UU PDP No. 27/2022), portal menampilkan status kedaluwarsa — tidak ada data pribadi yang bocor

---

## SEGMEN 4: Bank Korpus — Dosen (08:30–10:00)

**Login:** `dosen@kampus.ac.id`

**Yang ditunjukkan:**
- Menu **Bank Korpus** hanya muncul di navbar Dosen/Reviewer — tidak terlihat oleh mahasiswa
- Filter kategori dokumen (skripsi, jurnal, prosiding)
- Upload arsip ZIP berisi banyak PDF sekaligus — sistem otomatis memecah teks, menghitung fingerprint, dan mengindeks vektor ke pgvector

**Poin bicara:**
> Data naskah tidak dikirim ke server luar negeri. Kampus punya kendali penuh atas repositori pembandingnya sendiri.

---

## SEGMEN 5: Konsol Admin (10:00–12:00)

**Login:** `admin@veritext.ai`

**Tab yang ditunjukkan:**

| Tab | Fungsi |
|-----|--------|
| Overview & Metrik | Status sistem real-time: latensi DB, status Redis, Celery worker, jumlah vektor chunk |
| Kelola Pengguna | CRUD user, reset password, suspend akun, koreksi saldo token |
| Tuning Engine AI | Ubah threshold cosine semantik (default 0.75), trigger re-index HNSW |
| Log Audit Forensik | Riwayat seluruh aksi sistem dengan timestamp + tombol Ekspor CSV |

**Poin bicara:**
> Navbar admin terisolasi penuh — tidak ada link ke Dashboard mahasiswa atau Beranda publik. Ini implementasi *separation of concerns* di level antarmuka.

---

## SEGMEN 6: Capaian & Tanya Jawab (12:00–15:00)

**Angka yang perlu disebutkan:**
- Capaian implementasi: **42,86%** (3 dari 7 modul inti selesai, target UTS minimal 30%)
- Pengujian otomatis: **81 tests, 0 gagal** (56 backend + 25 frontend navigation guard)

---

## ANTISIPASI PERTANYAAN DOSEN

**"Kenapa Winnowing, bukan Levenshtein atau Jaccard?"**
> Levenshtein kompleksitasnya O(N×M) — lambat untuk dokumen panjang. Rabin-Karp Rolling Hash yang dipakai Winnowing berjalan O(1) per jendela. Jaminan matematisnya: kesamaan substring minimal 8 karakter pasti tertangkap oleh minimal satu fingerprint.

**"Kenapa pgvector HNSW, bukan IVFFlat atau database vektor terpisah?"**
> IVFFlat butuh training centroid dan akurasi pencariannya turun kalau data bertambah dinamis. HNSW berbasis graf multi-layer dengan pencarian O(log N). Karena pakai pgvector di dalam PostgreSQL, semua operasi (billing, user, vektor) terjadi dalam satu transaksi ACID — tidak perlu sinkronisasi dua database.

**"Stilometri rawan false positive untuk naskah manusia yang kebetulan seragam?"**
> Tier 3 tidak berdiri sendiri. Skor akhirnya hanya berbobot 15% dari komposit total. Selain itu threshold anomali AI baru aktif kalau burstiness < 0.20 DAN skor stilometri >= 35% secara bersamaan. Sitasi formal seperti (Santoso et al., 2024) juga diabaikan dari hitungan panjang kalimat.

**"Kalau Redis/Celery mati, bagaimana?"**
> Ada fallback otomatis: sistem mendeteksi tidak ada worker aktif lewat `celery inspect ping()`, lalu mengalihkan eksekusi ke daemon thread in-process. Proses audit tetap jalan tanpa perlu intervensi manual.

**"Bagaimana mahasiswa tidak bisa akses data mahasiswa lain?"**
> Tiga lapis: (1) Navigation guard frontend menolak rute yang tidak sesuai role. (2) Middleware backend `require_role()` memvalidasi JWT di setiap request. (3) Setiap query dokumen dan laporan dibatasi `WHERE user_id = current_user.id` — menutup celah IDOR.

---

## CHECKLIST SEBELUM DEMO

```bash
# 1. Pastikan Docker aktif (PostgreSQL + Redis)
docker compose up -d

# 2. Jalankan backend (Terminal 1)
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 3. Jalankan frontend (Terminal 2)
cd frontend && npm run dev

# 4. Verifikasi semua test lulus (opsional, untuk ditunjukkan ke dosen)
cd backend && venv/bin/python -m unittest discover -s tests -p "test_*.py"
cd frontend && npm test
```

**File naskah uji:** `contoh_naskah_uji.txt` (ada di root folder proyek)  
Waktu proses: sekitar 3–4 detik. Langsung menghasilkan 4 warna heatmap.
