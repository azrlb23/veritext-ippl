# System Blueprint: VeriText AI

## 1. Executive Summary & Visi Sistem

**VeriText AI** adalah platform inspeksi integritas naskah akademik dan asisten perbaikan penulisan ilmiah berbasis web (*Self-Service SaaS*). Sistem ini mengintegrasikan mesin deteksi plagiarisme cerdas 3-tahap (*3-Step Hybrid AI Detection Pipeline*) dengan pendampingan revisi interaktif (*Split-Screen Studio Workspace*).

Sistem dirancang dengan dua pilar utama:
1. **Keandalan & Akurasi Komputasi Ilmiah**: Mengombinasikan kecepatan deterministik algoritma leksikal lokal (*Winnowing Rabin-Karp*), kepekaan semantik vektor padat (*Sentence Transformers + IndoBERT* pada basis data *PostgreSQL pgvector HNSW*), dan ketajaman filter kontekstual AI (*Dual-Engine: Google Gemini Flash & DeepSeek via 9Router*).
2. **Kemandirian Operasional & Perlindungan Data**: Beroperasi penuh secara otomatis tanpa ketergantungan pada staf institusi/admin manual, didukung sistem ekonomi token transparan melalui *Midtrans Snap*, serta pemenuhan hak privasi data pengguna sesuai amanat Undang-Undang Perlindungan Data Pribadi (UU PDP No. 27 Tahun 2022).

---

## 2. Tech Stack & Environment Architecture

| Lapisan | Teknologi | Peran & Justifikasi |
|---|---|---|
| **Frontend Web Client** | Vue 3.5 (Composition API) + Vite 6 + TypeScript 5.7 | Arsitektur SPA desktop-first berkecepatan tinggi, type-safe, efisien memori, dan ideal untuk perenderan *in-place* teks naskah. |
| **State & Navigation** | Pinia 2.3 + Vue Router 4.5 | Manajemen state modular terpusat (sesi, wallet token, state workspace) dengan proteksi rute RBAC. |
| **Styling & Icons** | Tailwind CSS 3.4 + Lucide Icons | Desain antarmuka utilitarian akademik berdensitas data tinggi, rasio kontras WCAG 2.1 AA, dan kepatuhan Zero-Emoji Policy. |
| **Backend Framework** | FastAPI 0.115 (Python 3.11+) | Framework ASGI asinkron berkinerja tinggi, validasi I/O ketat berbasis Pydantic v2, dan dokumentasi otomatis OpenAPI 3.1. |
| **Asynchronous Task Queue** | Celery 5.4 + Redis 7.2 | Message broker dan task runner terdistribusi untuk memproses pemindaian naskah dan pra-pemrosesan teks berat tanpa memblokir server API. |
| **Vector Database & Storage** | PostgreSQL 16 + ekstensi `pgvector` v0.7+ | Basis data relasional ACID untuk 13 entitas utama serta pencarian semantik berkecepatan tinggi menggunakan indeks graf HNSW (`vector(384)`). |
| **Payment Gateway** | Midtrans Core & Snap API v2 | Transaksi moneter token komputasi otomatis dengan verifikasi tanda tangan kriptografis SHA-512 pada webhook. |
| **Dual-Engine LLM Gateway** | Google Gemini 2.5 Flash + DeepSeek v4.1 Flash (9Router) | Mesin pertimbangan kontekstual (*Contextual AI Judge*), parafrase instan 3-mode, dan asisten konsultasi akademik dengan toleransi kegagalan otomatis (*automatic failover*). |
| **PDF Generation Engine** | WeasyPrint 61.x | Perender HTML/CSS akademik beresolusi cetak untuk penerbitan dokumen sertifikat laporan audit ber-QR Code. |

---

## 3. Arsitektur 4-Lapis Bersih (Clean 4-Layer Architecture)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAPISAN 1: PRESENTASI (FRONTEND)                      │
│      Vue 3.5 SPA • Split-Screen Studio Workspace • Interactive Heatmap      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / JSON REST API
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                  LAPISAN 2: LOGIKA BISNIS & GATEWAY (BACKEND)               │
│        FastAPI ASGI • Pydantic v2 • JWT / RBAC • Dual-Engine LLM Gateway    │
└──────────────────┬───────────────────────────────────┬──────────────────────┘
                   │ Antrean Celery Task               │ Kueri SQL / Transaksi
┌──────────────────▼───────────────────┐  ┌────────────▼─────────────────────┐
│  LAPISAN 3: KOMPUTASI ASINKRON (AI)  │  │   LAPISAN 4: BASIS DATA & VDB    │
│  • Celery 5.4 + Redis 7.2 Broker     │  │  • PostgreSQL 16 (13 Tabel Relasional)│
│  • Step 1: Winnowing Rabin-Karp      │  │  • pgvector v0.7+ (Indeks HNSW 384-d)│
│  • Step 2: SBERT + IndoBERT Re-rank  │  │  • Midtrans Snap API Webhook     │
│  • Step 3: Stilometri & LLM Judge    │  │  • Dual-Scope Academic Corpus    │
└──────────────────────────────────────┘  └──────────────────────────────────┘
```

---

## 4. Capability Map & Modul Sistem Atomik

Sistem dibagi ke dalam 8 modul atomik dengan batas tanggung jawab tunggal (*Single Responsibility Principle*):

| Modul ID | Nama Modul | Tanggung Jawab Utama | Batas Kewenangan & Dependensi |
|---|---|---|---|
| `mod-auth` | Autentikasi & RBAC | Registrasi akun mandiri, login email & Google OAuth, rotasi JWT, dan pembatasan hak akses 3-role (`FREE`, `PREMIUM`, `ADMIN`). | Terisolasi pada identitas pengguna. Menghubungi `mod-billing` hanya untuk inisialisasi dompet kuota awal. |
| `mod-preprocessor` | Pra-pemrosesan Teks | Validasi magic bytes MIME (.pdf, .docx, .txt maks 15 MB), ekstraksi teks murni, segmentasi kalimat ber-offset karakter, dan kalkulator biaya token. | Menghasilkan struktur teks bersih berlarik kalimat. Tidak menjalankan komputasi audit. |
| `mod-pipeline-lexical` | Audit Leksikal (Step 1) | Algoritma Winnowing Rabin-Karp ($k=5, w=4, b=257, M=10^9+7$), pencocokan sidik jari cepat, penandaan pelanggaran leksikal verbatim (Tag Merah $\ge 80\%$). | Komputasi CPU murni di worker Celery. Independen dari API eksternal. |
| `mod-pipeline-semantic` | Audit Semantik (Step 2) | Ekstraksi dense embedding 384-d (`paraphrase-multilingual-MiniLM-L12-v2`), kueri graf HNSW pgvector (`<=>`), dan re-ranking `IndoBERT` (Tag Oranye $\ge 75\%$). | Berinteraksi dengan tabel korpus `document_chunks` di PostgreSQL. |
| `mod-pipeline-judge` | Stilometri & LLM Judge (Step 3) | Analisis Goh & Barabasi Burstiness $B$ dan TTR, verifikasi kutipan sah via Dual-Engine LLM, dan agregasi skor komposit $0.50 + 0.35 + 0.15$. | Mengonsumsi hasil Step 1 & 2. Memanggil LLM Gateway. |
| `mod-assistant` | AI Chatbot & Parafrase | Konsultasi penulisan ber-Academic Guardrail, generator 3 variasi parafrase (Per Kalimat, Per Paragraf, Seluruh Halaman), dan pembaruan naskah in-place. | Memeriksa saldo kuota ke `mod-billing`. Mengirim hasil perbaikan ke naskah aktif. |
| `mod-billing` | Monetisasi & Transaksi | Pembuatan invoice transaksi Midtrans Snap, verifikasi webhook SHA-512 atomik, auto-upgrade status ke `PREMIUM`, dan mutasi buku besar token. | Pemegang kendali mutasi tabel `token_wallets` dan `invoices`. |
| `mod-report-admin` | Pelaporan PDF, QR & Monitoring Admin | Render laporan resmi PDF WeasyPrint ber-QR Code (`PREMIUM`), verifikasi QR publik (`/verify/{uuid}`), hard-delete cascade UU PDP, serta dasbor Admin 100% Read-Only (`GET` murni). | Membaca hasil audit dan metrik agregat tanpa mutasi data pengguna. |

---

## 5. Invarian & Batasan Kritis Sistem (System Invariants)

1. **Invarian Hak Akses & Admin Read-Only**: Peran Administrator (`role = 'ADMIN'`) secara ketat berstatus 100% Read-Only. Seluruh endpoint admin hanya mengizinkan metode HTTP `GET`. Tidak ada antarmuka atau endpoint backend yang mengizinkan manipulasi saldo pengguna, pemblokiran manual, atau perubahan skor audit.
2. **Invarian Kepatuhan UU PDP (Zero Auto-Ingestion & Hard-Delete Cascade)**: Naskah pengguna tidak pernah dimasukkan ke dalam basis korpus publik pembanding tanpa izin tertulis. Penghapusan naskah oleh pemilik sah dokumen mengeksekusi *hard-delete cascading* yang menghapus berkas fisik, rekaman naskah, larik kalimat, laporan audit, dan riwayat chat secara permanen.
3. **Invarian Transaksi Token Atomik**: Setiap pemotongan token pemindaian naskah dan penambahan token dari pembayaran Midtrans wajib dieksekusi di dalam transaksi basis data dengan *row-level locking* (`SELECT ... FOR UPDATE`) guna mencegah kondisi perlombaan (*race condition*).
4. **Invarian Dual-Engine Failover**: Lapisan LLM tidak boleh memiliki titik kegagalan tunggal (*single point of failure*). Jika Google Gemini Flash mengalami gangguan atau batas laju (*rate-limit 429*), sistem wajib secara transparan mengalihkan beban kerja ke DeepSeek v4.1 Flash tanpa menghasilkan galat pada sisi pengguna.
5. **Invarian Estetika & Aksesibilitas**: Sistem mematuhi *Zero-Emoji Policy* (0 emoji visual di seluruh UI, diagram, dokumen, dan pesan respons) serta memenuhi rasio kontras teks minimal 4,5:1 (WCAG 2.1 Level AA).
