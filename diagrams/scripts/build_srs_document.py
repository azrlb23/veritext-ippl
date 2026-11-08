import os

OUTPUT_SRS_PATH = "/Users/azrlb23/Documents/IPPL/SRS_Sistem_Deteksi_Plagiarisme_Hybrid.md"

def build_srs_content():
    return """Software Requirements Specification
for
VeriText AI
Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical & Semantic AI Engine

Version 1.0 approved
Prepared by
11241045 - Mochammad Azriel Albian Putra
Program Studi Informatika
Institut Teknologi Kalimantan
24 Juni 2026

Table of Contents
1. Pendahuluan
   1.1 Tujuan Penulisan Dokumen
   1.2 Audien yang Dituju dan Pembaca yang Disarankan
   1.3 Batasan Produk
   1.4 Definisi dan Istilah
   1.5 Referensi
2. Deskripsi Keseluruhan
   2.1 Deskripsi Produk
   2.2 Fungsi Produk
   2.3 Penggolongan Karakteristik Pengguna
   2.4 Lingkungan Operasi
   2.5 Batasan Desain dan Implementasi
   2.6 Dokumentasi Pengguna
3. Kebutuhan Antarmuka Eksternal
   3.1 User Interfaces
   3.2 Hardware Interface
   3.3 Software Interface
   3.4 Communication Interface
4. Functional Requirement
   4.1 Use Case Diagram
   4.2 Use Case Description
   4.3 Spesifikasi Kebutuhan Fungsional (Tabel FR)
5. Kebutuhan Non-Fungsional (Non-Functional Requirements)
   5.1 Kebutuhan Performa (Performance Requirements)
   5.2 Kebutuhan Keamanan (Security Requirements)
   5.3 Kebutuhan Kepatuhan Data dan Privasi (Compliance Requirements)
   5.4 Kebutuhan Keandalan (Reliability Requirements)
   5.5 Kebutuhan Kegunaan (Usability Requirements)
   5.6 Kebutuhan Pemeliharaan (Maintainability Requirements)
Revision History

Revision History
| Versi | Tanggal | Penulis | Alasan Perubahan |
| :--- | :--- | :--- | :--- |
| 0.1 | 10 Maret 2026 | Mochammad Azriel Albian Putra | Draf inisial spesifikasi kebutuhan sistem deteksi plagiarisme leksikal. |
| 0.5 | 28 April 2026 | Mochammad Azriel Albian Putra | Integrasi deteksi semantik berbasis Sentence Transformers dan pgvector. |
| 0.9 | 15 Mei 2026 | Mochammad Azriel Albian Putra | Penambahan modul monetisasi token Midtrans dan sertifikasi laporan QR. |
| 1.0 | 24 Juni 2026 | Mochammad Azriel Albian Putra | Rilis final disetujui: Transformasi penuh ke arsitektur Self-Service SaaS 3-Role (Free, Premium, Admin Read-Only), 3-Step Hybrid AI Pipeline, modul AI Chatbot Asisten Naskah & Parafrase Instan 3-Mode, akuisisi korpus otomatis Dual-Scope, dan Split-Screen Studio Workspace. |

---

1. Pendahuluan

1.1 Tujuan Penulisan Dokumen
Dokumen Software Requirements Specification (SRS) ini bertujuan untuk mendefinisikan secara komprehensif, terperinci, terstruktur, dan terukur seluruh kebutuhan fungsional (functional requirements) serta kebutuhan non-fungsional (non-functional requirements) dalam perancangan dan pengembangan sistem VeriText AI (Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical & Semantic AI Engine). Dokumen ini menjadi baseline acuan formal bagi seluruh pemangku kepentingan (stakeholders), mencakup pengembang backend, insinyur kecerdasan buatan (AI engineer), pengembang frontend, analis sistem, perancang UI/UX, penguji perangkat lunak (QA engineer), serta dosen evaluator mata kuliah Implementasi Proses Perangkat Lunak (IPPL).

1.2 Audien yang Dituju dan Pembaca yang Disarankan
Dokumen ini disusun untuk dipahami oleh pembaca dengan peran dan tanggung jawab teknis sebagai berikut:
1. Pengembang Backend & AI Engineer: Sebagai panduan implementasi pipa pemrosesan dokumen bertingkat (Algoritma Winnowing Rabin-Karp, inferensi model Sentence Transformers paraphrase-multilingual-MiniLM-L12-v2, re-ranker LazarusNLP/all-indobert-base-v4, kalkulasi stilometri Goh & Barabasi Burstiness, integrasi Google Gemini 2.5 Flash / OpenRouter AI Judge, pengindeksan vektor HNSW di PostgreSQL pgvector, serta antrean tugas asinkron Celery Redis).
2. Pengembang Frontend: Sebagai spesifikasi implementasi antarmuka pengguna berbasis Vue 3.5 (Composition API), Vite 6, TypeScript 5.7, Pinia 2.3, Tailwind CSS 3.4, visualisasi Split-Screen Studio Workspace, Interactive Heatmap multi-tier tiga warna, modul AI Chatbot kontekstual dengan Guardrail Akademik, serta integrasi modal pembayaran Midtrans Snap.
3. Analis Sistem & Desainer UI/UX: Sebagai acuan validasi kesesuaian alur kerja dokumen, interaksi antarmuka tiga peran pengguna (Free User, Premium User, Admin Read-Only), serta pemenuhan prinsip kegunaan Nielsen Norman Group tanpa menggunakan elemen dekoratif non-akademik (Zero-Emoji Policy).
4. Penguji Sistem (QA Engineer): Sebagai acuan utama dalam merancang skenario pengujian unit (unit testing), pengujian integrasi (integration testing), pengujian End-to-End (E2E), serta pengujian akurasi deteksi (Precision, Recall, F1-Score).
5. Dosen Penilai dan Akademisi: Sebagai instrumen evaluasi akademik terhadap kepatuhan proses rekayasa perangkat lunak berstandar IEEE Std 830-1998 dan ISO/IEC 25010.

1.3 Batasan Produk
Sistem perangkat lunak VeriText AI memiliki batasan-batasan operasional dan teknis formal sebagai berikut:
1. Platform Akses: Sistem beroperasi penuh sebagai aplikasi web berbasis peramban (Single Page Application - SPA) yang responsif dan diakses melalui browser modern (Google Chrome, Mozilla Firefox, Apple Safari, Microsoft Edge). Sistem tidak memerlukan instalasi aplikasi native pada perangkat klien.
2. Model Operasional Mandiri (Self-Service SaaS): Sistem tidak bergantung pada intervensi manual dosen atau operator manusia untuk proses pendaftaran, aktivasi akun, verifikasi dokumen, pemotongan kuota, maupun penagihan pembayaran. Seluruh siklus layanan dioperasikan secara terotomatisasi oleh sistem.
3. Batasan Kuota dan Panjang Naskah Pengguna Gratis (Free User): Pengguna berstatus Free User dibatasi melakukan pemindaian naskah maksimal 2.500 kata per pemeriksaan (setara 1 Token / 1 artikel jurnal), dengan kuota awal 5 Token gratis dan 3 kali uji coba (Trial) fitur AI Chatbot dan Parafrase Instan.
4. Dukungan Naskah Panjang untuk Pengguna Pro (Premium User): Pengguna berstatus Premium User dapat memindai dokumen berskala panjang (proposal, skripsi, tesis, disertasi hingga puluhan ribu kata, dengan batas ukuran berkas 15 MB) yang dikenakan tarif berbasis formula proporsional dengan Batas Maksimum (Token Cap) sebesar 5 Token per dokumen.
5. Jaminan Privasi Data Naskah Pengguna (Zero Auto-Ingestion to Public Corpus): Sesuai kepatuhan Undang-Undang Perlindungan Data Pribadi (UU PDP No. 27 Tahun 2022), naskah yang diunggah oleh pengguna tidak pernah dijadikan korpus publik tanpa izin eksplisit, dan pengguna memiliki hak penuh untuk melakukan penghapusan naskah secara permanen (hard-delete cascade) dari sistem.
6. Ketergantungan Infrastruktur Eksternal: Fungsionalitas pembayaran bergantung pada keandalan Midtrans Payment Gateway, pemindaian web publik bergantung pada Google Search Grounding, dan akuisisi korpus otomatis bergantung pada ketersediaan API OpenAlex, DOAJ, Semantic Scholar, serta Crossref.

1.4 Definisi dan Istilah
Berikut adalah definisi istilah teknis dan terminologi domain yang digunakan secara konsisten dalam dokumen ini:

Tabel 1: Definisi dan Istilah Teknis
| Istilah / Singkatan | Definisi Formal |
| :--- | :--- |
| SRS | Software Requirements Specification; dokumen formal spesifikasi kebutuhan perangkat lunak standar IEEE Std 830-1998. |
| VeriText AI | Nama resmi produk perangkat lunak sistem deteksi plagiarisme cerdas berbasis arsitektur hybrid multi-tier. |
| Winnowing | Algoritma reduksi sidik jari dokumen (fingerprinting) berbasis k-gram dan sliding window yang efisien dalam mendeteksi pencocokan leksikal kata demi kata secara eksak. |
| K-Gram | Potongan substring teks berurutan sepanjang k karakter atau k kata yang diekstraksi dari naskah masukan. |
| Rabin-Karp Rolling Hash | Algoritma hashing polinomial yang menghitung nilai hash jendela teks geser secara inkremental dalam waktu konstan O(1) per langkah. |
| Jaccard Containment | Rasio interseksi himpunan sidik jari teks uji terhadap himpunan sidik jari dokumen pembanding untuk mengukur derajat penjiplakan leksikal verbatim. |
| Sentence Transformers | Model deep learning berbasis arsitektur Siamese BERT untuk memetakan kalimat ke dalam ruang vektor padat (dense vector embeddings). |
| paraphrase-multilingual-MiniLM-L12-v2 | Model transformer multilingual yang menghasilkan vektor 384 dimensi, mendukung lebih dari 50 bahasa, dan dioptimalkan untuk pencarian kemiripan semantik dan parafrase lintas bahasa. |
| LazarusNLP/all-indobert-base-v4 | Model representasi bahasa Indonesia mutakhir berdimensi 768 yang digunakan sebagai re-ranker spesialis dan pemetaan konsep sinonim morfologis Indonesia. |
| pgvector | Ekstensi PostgreSQL untuk menyimpan dan mengindeks vektor multidimensi menggunakan struktur graf Hierarchical Navigable Small World (HNSW). |
| Cosine Distance (<=>) | Metrik jarak angular antara dua vektor dalam ruang multidimensi; jarak mendekati 0 mengindikasikan kemiripan semantik yang sangat tinggi. |
| Burstiness (B) | Metrik stilometri Goh & Barabasi yang mengukur variasi distribusi jarak antar-kemunculan kata kunci untuk mengidentifikasi teks yang dihasilkan oleh model bahasa AI (LLM). |
| Type-Token Ratio (TTR) | Rasio jumlah kosakata unik (types) terhadap total kemunculan kata (tokens) untuk mengukur keragaman leksikal suatu dokumen ilmiah. |
| Gemini 2.5 Flash | Model kecerdasan buatan tingkat lanjut dari Google DeepMind yang diintegrasikan untuk analisis konteks, penyaringan sitasi, dan mesin parafrase ilmiah. |
| Token | Satuan kredit komputasi internal VeriText AI yang tersimpan di TokenWallet untuk mengakses layanan deteksi naskah dan fitur AI. |
| Split-Screen Studio Workspace | Tata letak antarmuka dua kolom seimbang (Interactive Heatmap di sebelah kiri dan Panel Tabular Sumber/AI Chatbot di sebelah kanan). |
| Academic Guardrail | Sistem filter dan validasi prompt pada modul chatbot yang secara ketat membatasi interaksi hanya pada lingkup evaluasi naskah, parafrase ilmiah, tata bahasa, dan sitasi akademik. |
| UU PDP | Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi. |

1.5 Referensi
Penyusunan dokumen ini mengacu pada standar, jurnal ilmiah, dan dokumentasi teknis berikut:
1. IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications.
2. ISO/IEC 25010:2011: Systems and software engineering -- Systems and software Quality Requirements and Evaluation (SQuaRE) -- System and software quality models.
3. Schleimer, S., Wilkerson, D. S., & Aiken, A. (2003). Winnowing: Local algorithms for document fingerprinting. In Proceedings of the 2003 ACM SIGMOD International Conference on Management of Data (pp. 76-85).
4. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP).
5. Goh, K. I., & Barabasi, A. L. (2008). Burstiness and memory in complex systems. EPL (Europhysics Letters), 81(4), 48002.
6. Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP).
7. Dokumentasi Resmi Vue 3.5, Vite 6, Pinia 2.3, Tailwind CSS 3.4 (https://vuejs.org/).
8. Dokumentasi Resmi FastAPI 0.115 dan Pydantic v2 (https://fastapi.tiangolo.com/).
9. Dokumentasi Ekstensi PostgreSQL pgvector 0.7+ (https://github.com/pgvector/pgvector).
10. Dokumentasi Integrasi Midtrans Core & Snap API v2 (https://docs.midtrans.com/).
11. Dokumentasi OpenAlex Academic Graph API (https://docs.openalex.org/).

---

2. Deskripsi Keseluruhan

2.1 Deskripsi Produk
VeriText AI adalah platform perangkat lunak berbasis Software-as-a-Service (SaaS) cerdas yang dirancang untuk mengatasi kelemahan mendasar perangkat deteksi plagiarisme konvensional. Sistem konvensional umumnya hanya mampu mendeteksi penjiplakan salin-tempel langsung (exact copy-paste) dan gagal mengenali parafrase tingkat lanjut, penerjemahan lintas bahasa, serta manipulasi susunan kalimat.

VeriText AI mengimplementasikan pipa deteksi cerdas 3-Step Hybrid AI Detection Engine:
1. Step 1 (Deteksi Leksikal Ekstrem): Menerapkan algoritma Winnowing berbasis Rabin-Karp Rolling Hash untuk mendeteksi penjiplakan kata per kata (verbatim match) secara presisi dengan kecepatan O(N).
2. Step 2 (Deteksi Semantik & Parafrase): Menerapkan model transformer paraphrase-multilingual-MiniLM-L12-v2 berdimensi 384 dipadukan dengan indeks graf HNSW pada PostgreSQL pgvector, serta model spesialis LazarusNLP/all-indobert-base-v4 untuk mendeteksi parafrase tingkat tinggi dan penjiplakan ide lintas bahasa.
3. Step 3 (Evaluasi Stilometri & Contextual AI Judge): Menerapkan analisis variasi ritme penulisan (Burstiness B) dan keragaman leksikal (TTR) yang dikombinasikan dengan inferensi Google Gemini 2.5 Flash untuk membedakan kutipan berizin resmi dari penjiplakan terselubung.

Sistem dilengkapi dengan Split-Screen Studio Workspace dan modul AI Chatbot Asisten Naskah yang memungkinkan pengguna mengidentifikasi kalimat bermasalah, berkonsultasi mengenai perbaikan tata bahasa ilmiah, dan mengeksekusi Parafrase Instan dalam 3 Mode Granularitas (Per Kalimat, Per Paragraf, atau Seluruh Halaman) dengan pembaruan teks secara langsung (in-place replacement) dan kalkulasi ulang skor kemiripan secara real-time.

2.2 Fungsi Produk
Fungsi-fungsi utama VeriText AI dipetakan ke dalam kelompok fitur berikut:
1. Autentikasi dan Manajemen Sesi Terdesentralisasi: Pendaftaran mandiri via email dan Google OAuth 2.0, manajemen token JWT (Access Token 15 menit dan HttpOnly Refresh Token), alokasi otomatis 5 Token gratis dan 3x Trial AI Chatbot/Parafrase untuk pengguna baru.
2. Unggah dan Pra-pemrosesan Multi-Format: Input naskah melalui penempelan teks langsung atau unggah berkas .pdf, .docx, .txt (maksimal 15 MB), ekstraksi teks bersih, pembersihan karakter non-ASCII, serta penghitungan kata dan estimasi biaya token secara transparan.
3. Pipa Deteksi Hybrid 3-Tahap Asinkron: Orkestrasi pemindaian dokumen melalui antrean Celery Redis, penarikan korpus pembanding otomatis dari OpenAlex, DOAJ, Semantic Scholar, Crossref, HuggingFace Indonesian STS, dan Google Search Grounding, serta kalkulasi skor komposit berbobot (0.50 Leksikal + 0.35 Semantik + 0.15 Stilometri).
4. Studio Heatmap & Komparasi Berdampingan: Tampilan naskah interaktif dengan penyorotan warna semantik (Merah untuk leksikal, Oranye untuk semantik, Kuning untuk anomali gaya), kartu sumber kecocokan lengkap dengan tautan DOI resmi, dan perbandingan teks berdampingan (side-by-side diff).
5. AI Chatbot Asisten Naskah & Parafrase Instan: Panel konsultasi naskah yang dilindungi Guardrail Asisten Akademik, generator 3 variasi parafrase ilmiah per segmen, dan mekanisme penggantian kalimat in-place dengan re-skor instan.
6. Pelaporan Resmi dan Verifikasi Sertifikat Publik: Pembuatan laporan audit berformat PDF berkualitas tinggi yang dilengkapi segel digital dan kode QR dinamis, serta portal validasi keaslian laporan publik (/verify/{certificate_uuid}).
7. Manajemen Riwayat & Kepatuhan Privasi UU PDP: Hak penghapusan berkas naskah beserta seluruh data audit dan riwayat chat secara permanen (hard-delete cascading).
8. Monetisasi dan Top-Up Token Midtrans Snap: Pembelian token satuan (By Token) atau paket bundling diskon (By Paket Token) dengan aktivasi instan dan kenaikan status akun otomatis menjadi Premium User saat webhook settlement terverifikasi.
9. Dasbor Pemantauan Layanan Admin (100% Read-Only): Pemantauan agregat statistik pemindaian, grafik tren skor kemiripan, log transaksi keuangan Midtrans, telemetri beban antrean worker Celery, dan log audit keamanan sistem tanpa kemampuan memutasi data pengguna.

2.3 Penggolongan Karakteristik Pengguna
Hak akses dan karakteristik operasional pengguna dikelompokkan ke dalam 3 peran konsisten:

Tabel 2: Matriks Perbandingan Tiga Peran Pengguna
| Kriteria Evaluasi | 1. Free User (Pengguna Gratis) | 2. Premium User (Pengguna Pro / Berbayar) | 3. Admin (100% Read-Only) |
| :--- | :--- | :--- | :--- |
| Kode Role Database | FREE | PREMIUM | ADMIN |
| Status Awal & Saldo | Terdaftar otomatis saat registrasi; memperoleh 5 Token Gratis dan 3x Kuota Trial AI Chatbot/Parafrase. | Otomatis aktif saat transaksi pembelian token berstatus settlement via Midtrans; saldo token sesuai pembelian. | Akun internal terverifikasi; tidak memiliki kuota token komputasi pengguna. |
| Batasan Kata Per Dokumen | Maksimal 2.500 kata per pemeriksaan (setara 1 Token / 1 makalah). | Mendukung naskah panjang (skripsi, tesis, disertasi hingga puluhan ribu kata, batas berkas 15 MB). | Read-Only: Hanya melihat ringkasan statistik total kata yang dipindai sistem. |
| Batas Maksimum Biaya Token | 1 Token per dokumen. | Dikenakan formula min(5, ceil(kata / 2500)) dengan Batas Maksimum (Token Cap) 5 Token. | Tidak ada pemotongan token; murni pemantauan. |
| Akses AI Chatbot & Parafrase | Mode Trial (Maksimal 3x Respon). Setelah habis, terkunci oleh modal paywall top-up. | Bebas menggunakan AI Chatbot dan Parafrase Instan 3-Mode selama saldo token mencukupi. | Tidak dapat mengakses fitur chatbot naskah; hanya memantau latensi API AI. |
| Hak Unduh Laporan PDF | Hanya melihat Interactive Heatmap di layar browser (View-Only). | Dapat mengunduh Laporan PDF Resmi lengkap dengan QR Code Keaslian Dokumen. | Tidak dapat mengunduh naskah atau dokumen privat milik pengguna (UU PDP). |
| Hak Verifikasi QR Publik | Dapat memindai dan memverifikasi QR Code laporan publik di halaman /verify. | Dapat memindai dan memverifikasi QR Code laporan publik di halaman /verify. | Dapat memantau log kueri verifikasi QR sertifikat sistem. |
| Pembelian Token Midtrans | Dapat membeli By Token (satuan) atau By Paket Token untuk otomatis naik ke PREMIUM. | Dapat melakukan top-up kapan saja (By Token atau By Paket Token) dan unduh invoice PDF. | Read-Only: Memantau tabel transaksi masuk Midtrans dan total pendapatan sistem. |
| Mutasi Data Pengguna | Mengelola profil sendiri dan menghapus naskah milik sendiri (UU PDP). | Mengelola profil sendiri dan menghapus naskah milik sendiri (UU PDP). | DILARANG memutasi saldo, mengubah peran, atau menghapus naskah pengguna secara manual. |

2.4 Lingkungan Operasi
Sistem VeriText AI dirancang untuk beroperasi pada lingkungan infrastruktur dan perangkat lunak berikut:
1. Lingkungan Klien (Client Environment):
   - Peramban Web: Google Chrome (versi >= 110), Mozilla Firefox (versi >= 110), Apple Safari (versi >= 16), Microsoft Edge (versi >= 110).
   - Resolusi Layar: Minimum 1280 x 720 piksel (disarankan 1920 x 1080 piksel untuk pengalaman optimal Split-Screen Studio Workspace); tampilan adaptif untuk tablet 768 piksel.
   - Konektivitas Jaringan: Akses internet stabil dengan kecepatan unduh/unggah minimal 1 Mbps.
2. Lingkungan Server (Server & Cloud Infrastructure):
   - Sistem Operasi Server: Ubuntu Server 22.04 LTS / macOS Server / Debian 12 (x86_64 / ARM64).
   - Containerization: Docker Engine 24.0+ dan Docker Compose v2.
   - Database Server: PostgreSQL 16 dengan ekstensi pgvector versi >= 0.7.0.
   - Message Broker & Cache: Redis Server versi 7.2+.
   - Runtime Backend: Python 3.12+ (FastAPI 0.115, SQLAlchemy 2.0 async, Celery 5.4).
   - Runtime Frontend: Node.js 20+ LTS / Vite 6 / Vue 3.5.

2.5 Batasan Desain dan Implementasi
Batasan-batasan teknis yang mengikat arsitektur perangkat lunak meliputi:
1. Standar Stack Frontend: Wajib menggunakan Vue 3.5 (Composition API) berbasis script setup, Vite 6, TypeScript 5.7, Pinia 2.3 untuk manajemen state terpusat, Vue Router 4.5, Axios 1.7 untuk komunikasi REST API, dan Tailwind CSS 3.4. Dilarang keras menggunakan pustaka atau framework di luar stack resmi yang telah disepakati.
2. Kebijakan Visual Tanpa Emoji (Zero-Emoji Policy): Seluruh antarmuka web, pesan notifikasi, badge status, tabel, dan dokumen pelaporan akademik dilarang menggunakan emoji visual satupun. Indikator visual wajib memanfaatkan tipografi yang tegas, palet warna semantik bergradasi bersih, dan ikon SVG monokrom.
3. Skema Vektor Tetap 384 Dimensi: Indeks basis data vektor di PostgreSQL pgvector dikunci pada format vector(384) untuk menjamin kompatibilitas langsung dengan model SBERT paraphrase-multilingual-MiniLM-L12-v2 dan kecepatan pencarian HNSW Cosine (<=>) di bawah 100 milidetik.
4. Kepatuhan Transaksi Atomik: Seluruh pemotongan saldo token, pencatatan transaksi kredit/debit, dan pembaruan invoice wajib dieksekusi di dalam blok transaksi basis data terisolasi menggunakan row-level locking (SELECT ... FOR UPDATE).
5. Kepatuhan Standar Dokumen Akademik: Dokumen SRS dan SDD disusun secara murni tanpa menggunakan sintaks blok penanda GitHub Callout agar ketika disalin ke Microsoft Word atau Google Docs tidak memunculkan teks mentah yang mengganggu format penulisan akademik resmi.

2.6 Dokumentasi Pengguna
Sistem menyediakan dokumentasi operasional terintegrasi:
1. Panduan Interaktif Daring (Onboarding Tour): Panduan langkah demi langkah saat pengguna pertama kali memasuki Split-Screen Studio Workspace.
2. Panduan Interpretasi Skor Plagiarisme: Penjelasan akademik mengenai arti persentase skor komposit, perbedaan penjiplakan leksikal (Merah), parafrase semantik (Oranye), dan anomali stilometri (Kuning).
3. Pusat Bantuan & FAQ Pembayaran Token: Petunjuk tata cara pembelian kuota token via Midtrans Snap (QRIS, GoPay, ShopeePay, Virtual Account Bank Mandiri/BCA/BNI/BRI, dan Kartu Kredit).

---

3. Kebutuhan Antarmuka Eksternal

3.1 User Interfaces
Antarmuka pengguna VeriText AI dirancang dengan tata letak profesional, data-density tinggi, dan tipografi akademik bersih:
1. Halaman Masuk dan Registrasi (Auth Views): Formulir masuk/daftar minimalis dengan validasi input instan, indikator kekuatan kata sandi, opsi masuk cepat Google OAuth 2.0, serta tautan lupa kata sandi.
2. Halaman Dasbor Workspace (Upload & Status): Menampilkan kartu saldo token, riwayat naskah terkini, dan Dropzone unggah berkas yang responsif mendukung seret-dan-lepas (.pdf, .docx, .txt) serta input teks langsung.
3. Halaman Split-Screen Studio Workspace (Layar Analisis & AI Chatbot):
   - Top Summary Bar (Tinggi 64px): Menampilkan judul dokumen, jumlah kata, skor kemiripan komposit total dalam badge tegas, rincian persentase 3-tier, sisa saldo token pengguna, serta tombol aksi cepat (Unduh PDF Resmi, Parafrase Semua Kalimat Terindikasi).
   - Kolom Kiri (Lebar 60%): Interactive Heatmap Document Viewer yang menampilkan naskah asli dengan sorotan warna semantik multi-tier (Merah untuk leksikal >= 80%, Oranye untuk semantik >= 75%, Kuning untuk anomali stilometri), tombol filter sorotan warna ([Semua], [Merah], [Oranye], [Kuning]), serta popover interaktif saat kalimat disorot diklik ([Parafrase Kalimat Ini], [Parafrase Paragraf], [Lihat Sumber]).
   - Kolom Kanan (Lebar 40%): Panel Tabular 2-in-1 dengan tab switcher:
     * Tab 1 (Daftar Sumber Kecocokan): Daftar kartu sumber publikasi ilmiah (OpenAlex, DOAJ, repositori kampus) dilengkapi persentase kontribusi, nama jurnal, tautan DOI resmi, dan jendela komparasi berdampingan (Side-by-Side Diff) antara teks naskah dan teks sumber asli.
     * Tab 2 (AI Chatbot Asisten Naskah & Parafrase): Area percakapan interaktif ber-Guardrail Akademik, badge kuota trial/token di bagian header, kartu 3 opsi variasi parafrase ilmiah lengkap dengan prediksi penurunan persentase kemiripan, tombol aksi [Terapkan ke Naskah & Cek Ulang In-Place], serta tombol saran cepat ([Ubah ke Kalimat Pasif], [Perhalus Kosakata Akademik], [Jelaskan Alasan Plagiat]).
4. Halaman Riwayat & Kepatuhan Privasi (History View): Tabel daftar seluruh riwayat pemeriksaan naskah dengan fitur pencarian, filter tanggal, dan tombol Hapus Permanen (UU PDP) yang memicu modal konfirmasi penghapusan hard-delete.
5. Halaman Top-Up Kuota & Pembayaran (Billing View): Kartu saldo token saat ini, pemilih skema pembelian (By Token custom Rp 2.000/token minimal 5 token, atau By Paket Token bundling hemat: Starter 15 token Rp 25.000, Skripsi Pro 50 token Rp 65.000, Riset Intensif 150 token Rp 150.000), modal sematan Midtrans Snap, serta tabel riwayat transaksi dan tombol unduh invoice PDF.
6. Halaman Verifikasi Sertifikat Publik (/verify/{certificate_uuid}): Halaman publik ringan tanpa kewajiban login untuk memvalidasi keaslian laporan audit, menampilkan stempel digital hijau, nama naskah, waktu audit, dan skor resmi.
7. Halaman Dasbor Pemantauan Admin (/admin - 100% Read-Only): Dasbor analitik metrik global (total naskah dipindai, rata-rata skor plagiarisme, total pendapatan sistem, grafik tren bulanan), tabel riwayat transaksi Midtrans real-time, telemetri kesehatan antrean worker Celery dan Redis, serta tabel log audit keamanan sistem tanpa tombol aksi manipulasi data pengguna.

3.2 Hardware Interface
Sistem tidak berinteraksi langsung dengan perangkat keras fisik khusus selain server komputasi standar:
1. Server Basis Data & Komputasi AI: Minimum 4 vCPU (disarankan 8 vCPU), 8 GB RAM (disarankan 16 GB RAM untuk efisiensi indeks HNSW pgvector dan inferensi Sentence Transformers), serta penyimpanan Solid State Drive (SSD) NVMe minimal 50 GB.
2. Perangkat Klien: Komputer pribadi, laptop, atau tablet dengan prosesor dual-core, RAM minimal 4 GB, dan layar beresolusi minimal 1280 x 720 piksel.

3.3 Software Interface
Sistem berinteraksi dengan antarmuka perangkat lunak eksternal berikut:
1. PostgreSQL 16 dengan pgvector: Antarmuka basis data relasional dan vektor melalui koneksi pool asyncpg dan SQLAlchemy 2.0 pada port 5432.
2. Redis 7.2: Broker pesan dan penyimpanan hasil tugas Celery pada port 6379.
3. Midtrans Snap & Notification Webhook API: Antarmuka gerbang pembayaran untuk inisiasi transaksi Snap token dan penerimaan webhook notifikasi status pembayaran berbasis verifikasi SHA-512.
4. OpenAlex Academic Graph API: Antarmuka REST API publik (https://api.openalex.org/) untuk penarikan metadata dan abstrak karya ilmiah Indonesia dan internasional.
5. Directory of Open Access Journals (DOAJ) API: Antarmuka penelusuran artikel jurnal akses terbuka resmi (https://doaj.org/api/v2/).
6. Semantic Scholar Academic Graph API: Antarmuka penelusuran publikasi ilmiah global (https://api.semanticscholar.org/graph/v1/).
7. Crossref REST API: Antarmuka verifikasi nomor Digital Object Identifier (DOI) resmi (https://api.crossref.org/).
8. Google Generative AI (Gemini 2.5 Flash API): Antarmuka model kecerdasan buatan untuk evaluasi sitasi konteks, penyaringan anomali stilometri, dan mesin parafrase ilmiah.
9. Google OAuth 2.0 API: Antarmuka autentikasi pihak ketiga untuk registrasi dan login cepat berbasis OpenID Connect.

3.4 Communication Interface
Standar komunikasi perangkat lunak meliputi:
1. Protokol Komunikasi Klien-Server: Seluruh komunikasi antara peramban web dan gateway API wajib menggunakan protokol HTTPS terenkripsi TLS versi 1.3 melalui port 443.
2. Format Pertukaran Data: Menggunakan JavaScript Object Notation (JSON) terstruktur mengacu pada spesifikasi OpenAPI versi 3.1.
3. Autentikasi Permintaan API: Permintaan terautentikasi wajib menyertakan header Authorization: Bearer <JWT_ACCESS_TOKEN> dengan masa berlaku 15 menit.
4. Smart Polling Asinkron: Pengembang frontend Vue 3.5 mengimplementasikan mekanisme smart polling menggunakan Axios dengan interval adaptif (2 detik pada fase aktif, eksponensial backoff hingga maksimal 10 detik) untuk memantau status penyelesaian audit naskah asinkron pada endpoint GET /api/v1/audits/status/{task_id}.
5. Webhook Security Interface: Endpoint penerimaan webhook pembayaran (POST /api/v1/billing/webhook) memvalidasi keaslian notifikasi menggunakan algoritma SHA-512 dengan rumus:
   SHA512(order_id + status_code + gross_amount + ServerKey).

---

4. Functional Requirement

4.1 Use Case Diagram
Arsitektur fungsional VeriText AI mencakup 3 Aktor (Free User, Premium User, Admin Read-Only) dan 11 Use Case Inti (UC-01 s/d UC-11).

![Use Case Diagram](diagrams/exported/Use%20Case%20Diagram.png)

Deskripsi relasi aktor dan use case pada diagram:
1. Free User: Berinteraksi dengan UC-01 (Masuk & Registrasi), UC-02 (Kelola Profil), UC-03 (Unggah Naskah batas 2.500 kata), UC-04 (Eksekusi Deteksi 3-Tahap), UC-05 (Tinjau Heatmap Web View), UC-06 (AI Chatbot Trial maks 3x), UC-07 (Parafrase Instan Trial maks 3x), UC-08 (Verifikasi QR Publik), UC-09 (Hapus Riwayat Naskah PDP), dan UC-10 (Beli Token & Upgrade Premium).
2. Premium User: Memiliki seluruh hak akses Free User, ditambah keleluasaan memindai naskah panjang tanpa batas kata (Token Cap 5 Token) pada UC-03 & UC-04, akses penuh tanpa batas trial pada AI Chatbot (UC-06) dan Parafrase Instan 3-Mode (UC-07) berbasis saldo token, hak mengunduh Laporan PDF Resmi ber-QR Code pada UC-08, serta top-up token dan unduh invoice pada UC-10.
3. Admin (100% Read-Only): Berinteraksi dengan UC-01 untuk login ke sistem, dan UC-11 untuk memantau dasbor analitik, log transaksi keuangan, serta telemetri server secara pasif tanpa melakukan mutasi data pengguna.
4. Relasi <<includes>>: UC-03 secara otomatis menyertakan (includes) eksekusi pipa deteksi UC-04. UC-10 menyertakan verifikasi webhook notifikasi Midtrans.
5. Relasi <<extend>>: Fitur AI Chatbot (UC-06) dan Parafrase Instan (UC-07) merupakan perluasan opsional (extend) yang dapat dipicu langsung dari peninjauan Heatmap naskah (UC-05).

4.2 Use Case Description
Berikut adalah 11 tabel spesifikasi Use Case terperinci:

Tabel 3: UC-01 Masuk dan Registrasi Akun
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-01 |
| Nama Use Case | Masuk dan Registrasi Akun |
| Aktor | Free User, Premium User, Admin |
| Deskripsi Singkat | Pengguna mendaftarkan akun baru atau masuk ke sistem menggunakan email/password atau Google OAuth 2.0. Sistem mengalokasikan otomatis 5 Token gratis dan 3x Trial Chatbot untuk akun baru. |
| Prekondisi | Pengguna memiliki peramban web dan koneksi internet; belum terautentikasi di sesi aktif. |
| Postkondisi | Pengguna memperoleh sesi aktif (JWT Access Token & HttpOnly Refresh Cookie) dan diarahkan ke Workspace. |
| Alur Utama | 1. Pengguna membuka halaman /login atau /register.<br>2. Pengguna memilih metode autentikasi (Email atau Google OAuth).<br>3. Jika Email: Pengguna memasukkan nama, email, dan kata sandi, lalu klik "Daftar" atau "Masuk".<br>4. Sistem memvalidasi kelayakan data dan memverifikasi hash kata sandi dengan bcrypt.<br>5. Jika akun baru: Sistem membuat record pengguna (role='FREE') dan mengalokasikan saldo 5 Token serta 3x Kuota Trial AI pada TokenWallet.<br>6. Sistem menerbitkan JWT Access Token dan Refresh Token pada HttpOnly Cookie.<br>7. Sistem mengarahkan pengguna ke Dasbor Workspace. |
| Alur Alternatif | 3a. Masuk dengan Google OAuth:<br>  3a.1 Pengguna klik tombol "Masuk dengan Google".<br>  3a.2 Sistem mengarahkan peramban ke Google Consent Screen.<br>  3a.3 Pengguna mengonfirmasi akun Google.<br>  3a.4 Google mengembalikan authorization code ke backend callback.<br>  3a.5 Sistem menukar kode dengan Google ID Token, memverifikasi profil, dan melakukan upsert akun (role='FREE' jika baru).<br>  3a.6 Sistem menerbitkan sesi JWT dan mengarahkan ke Dasbor.<br>4a. Kredensial tidak valid:<br>  4a.1 Sistem mencatat percobaan gagal dan mengembalikan kode status 401 Unauthorized.<br>  4a.2 Antarmuka menampilkan pesan galat "Email atau kata sandi tidak valid". |

Tabel 4: UC-02 Kelola Profil dan Kata Sandi
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-02 |
| Nama Use Case | Kelola Profil dan Kata Sandi |
| Aktor | Free User, Premium User |
| Deskripsi Singkat | Pengguna memperbarui informasi identitas profil atau memperbarui kata sandi keamanan akun. |
| Prekondisi | Pengguna telah masuk ke sistem dengan sesi JWT valid. |
| Postkondisi | Informasi profil atau hash kata sandi pengguna di database berhasil diperbarui. |
| Alur Utama | 1. Pengguna membuka halaman /settings.<br>2. Pengguna memperbarui nama lengkap atau institusi afiliasi.<br>3. Pengguna menekan tombol "Simpan Profil".<br>4. Sistem melakukan sanitasi string (anti-XSS) dan memperbarui record di tabel users.<br>5. Sistem menampilkan notifikasi sukses "Profil berhasil diperbarui". |
| Alur Alternatif | 2a. Pengguna ingin mengubah kata sandi:<br>  2a.1 Pengguna membuka tab "Keamanan", memasukkan kata sandi lama dan kata sandi baru (minimal 8 karakter).<br>  2a.2 Pengguna menekan tombol "Perbarui Kata Sandi".<br>  2a.3 Sistem memverifikasi hash kata sandi lama. Jika cocok, sistem melakukan hashing bcrypt pada kata sandi baru dan memperbarui database.<br>  2a.4 Sistem mencabut seluruh sesi aktif lain demi keamanan.<br>  2a.5 Sistem menampilkan notifikasi sukses "Kata sandi berhasil diperbarui".<br>2b. Kata sandi lama tidak cocok: Sistem menolak dan menampilkan pesan galat "Kata sandi lama salah". |

Tabel 5: UC-03 Unggah dan Validasi Naskah
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-03 |
| Nama Use Case | Unggah dan Validasi Naskah |
| Aktor | Free User, Premium User |
| Deskripsi Singkat | Pengguna mengunggah berkas naskah (.pdf, .docx, .txt) atau menempelkan teks langsung. Sistem memvalidasi kelayakan berkas, menghitung jumlah kata, dan menampilkan kalkulator estimasi biaya token. |
| Prekondisi | Pengguna telah masuk ke sistem dan berada di Dasbor Workspace. |
| Postkondisi | Naskah berhasil disimpan sementara dan siap diproses oleh pipa deteksi plagiarisme. |
| Alur Utama | 1. Pengguna memilih metode input naskah (unggah berkas atau tempel teks langsung).<br>2. Pengguna mengunggah berkas naskah (ukuran maksimal 15 MB) atau menempelkan teks.<br>3. Sistem memeriksa magic bytes MIME type berkas dan memvalidasi integritas struktur.<br>4. Sistem mengekstraksi teks bersih dan menghitung jumlah kata naskah.<br>5. Sistem mengevaluasi batasan akun: Jika pengguna berstatus FREE, jumlah kata tidak boleh melebihi 2.500 kata.<br>6. Sistem menghitung estimasi biaya token menggunakan formula: Biaya = min(5, ceil(kata / 2500)) Token.<br>7. Sistem menampilkan ringkasan dokumen, jumlah kata, dan konfirmasi biaya token sebelum pengguna memulai pemeriksaan. |
| Alur Alternatif | 3a. Berkas tidak valid atau ukuran > 15 MB: Sistem menolak berkas dan menampilkan pesan galat "Format berkas tidak didukung atau ukuran melebihi batas 15 MB".<br>5a. Akun FREE mengunggah naskah > 2.500 kata: Sistem menampilkan modal paywall "Batas akun gratis adalah 2.500 kata. Silakan upgrade ke Premium untuk memindai naskah panjang (skripsi/tesis)". |

Tabel 6: UC-04 Deteksi Plagiarisme Hybrid 3-Tahap
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-04 |
| Nama Use Case | Deteksi Plagiarisme Hybrid 3-Tahap |
| Aktor | Free User, Premium User |
| Deskripsi Singkat | Sistem mengeksekusi pipa deteksi hybrid tiga tahap secara asinkron melalui antrean Celery Redis setelah saldo token dipotong secara atomik. |
| Prekondisi | Naskah telah divalidasi (UC-03) dan saldo token pengguna mencukupi biaya audit. |
| Postkondisi | Status audit COMPLETED, skor komposit terhitung, dan kalimat naskah ditandai warna indikator. |
| Alur Utama | 1. Pengguna menekan tombol "Mulai Periksa Naskah".<br>2. Sistem memotong saldo TokenWallet secara atomik di dalam database transaction.<br>3. Sistem membuat task audit baru dan mengirimkannya ke antrean Celery Redis.<br>4. Worker Celery mengeksekusi Step 1 (Deteksi Leksikal Winnowing) mencocokkan k-gram Rabin-Karp terhadap fingerprint korpus.<br>5. Worker Celery mengeksekusi Step 2 (Deteksi Semantik SBERT & IndoBERT) menghasilkan vektor 384-d dan kueri KNN Cosine pada indeks HNSW pgvector.<br>6. Worker Celery mengeksekusi Step 3 (Evaluasi Stilometri & Contextual AI Judge) menghitung Burstiness, TTR, dan validasi sitasi via Gemini 2.5 Flash.<br>7. Worker menghitung skor komposit berbobot: Skor = 0.50 Leksikal + 0.35 Semantik + 0.15 Stilometri.<br>8. Worker memperbarui status audit menjadi COMPLETED pada database.<br>9. Antarmuka web pengguna mendeteksi penyelesaian via smart polling dan memuat hasil. |
| Alur Alternatif | 2a. Saldo token pengguna tidak mencukupi: Sistem membatalkan inisiasi audit dan menampilkan pesan galat "Saldo token Anda tidak mencukupi, silakan top-up terlebih dahulu".<br>4a. Kegagalan worker komputasi: Celery otomatis melakukan retry hingga 3 kali; jika tetap gagal, sistem mengembalikan (refund) saldo token pengguna secara atomik. |

Tabel 7: UC-05 Tinjau Laporan dan Heatmap Kemiripan
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-05 |
| Nama Use Case | Tinjau Laporan dan Heatmap Kemiripan |
| Aktor | Free User, Premium User |
| Deskripsi Singkat | Pengguna meninjau naskah interaktif pada Split-Screen Studio Workspace, melihat sorotan warna semantik, dan membandingkan kalimat dengan sumber asli. |
| Prekondisi | Pemeriksaan naskah telah selesai berstatus COMPLETED (UC-04). |
| Postkondisi | Pengguna memahami distribusi persentase plagiarisme dan rincian sumber kecocokan. |
| Alur Utama | 1. Pengguna membuka tampilan hasil analisis naskah.<br>2. Sistem menyajikan antarmuka Split-Screen Studio Workspace:<br>   - Kolom Kiri: Naskah asli dengan Interactive Heatmap multi-warna (Merah = Leksikal, Oranye = Semantik, Kuning = Gaya/AI).<br>   - Kolom Kanan: Panel Daftar Sumber Kecocokan lengkap dengan persentase kontribusi dan tautan DOI resmi.<br>3. Pengguna dapat mengklik tombol filter sorotan ([Semua], [Merah], [Oranye], [Kuning]).<br>4. Pengguna mengklik salah satu kalimat bermasalah pada naskah.<br>5. Sistem menampilkan popover aksi dan menampilkan teks perbandingan berdampingan (Side-by-Side Diff) dengan dokumen pembanding asli. |
| Alur Alternatif | 4a. Pengguna ingin memperbaiki kalimat yang diklik: Pengguna memilih opsi "Parafrase Kalimat Ini", yang otomatis mengarahkan fokus ke tab AI Asisten (UC-07). |

Tabel 8: UC-06 Konsultasi Naskah via AI Chatbot
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-06 |
| Nama Use Case | Konsultasi Naskah via AI Chatbot |
| Aktor | Free User (Trial 3x), Premium User (Token) |
| Deskripsi Singkat | Pengguna berdiskusi dengan AI Asisten Akademik di panel kanan Workspace mengenai pembedahan naskah, kaidah penulisan ilmiah, dan sitasi. |
| Prekondisi | Pengguna berada di Split-Screen Studio Workspace (UC-05) dan memiliki kuota chat (Trial untuk Free, Saldo Token untuk Premium). |
| Postkondisi | Pesan dan jawaban tersimpan di riwayat percakapan chat_messages dan kuota/token terpotong. |
| Alur Utama | 1. Pengguna membuka Tab 2 "AI Asisten" pada panel kanan Workspace.<br>2. Pengguna mengetikkan pertanyaan atau memilih tombol cepat ([Perhalus Paragraf], [Ubah ke Kalimat Pasif], [Jelaskan Kenapa Ini Plagiat]).<br>3. Sistem memeriksa hak akses: Jika Free User, pastikan ai_trial_remaining > 0; jika Premium User, pastikan saldo token mencukupi.<br>4. Modul AcademicGuardrail memvalidasi prompt masukan untuk memastikan konteks berada dalam lingkup akademik.<br>5. Sistem mengirimkan prompt beserta konteks naskah ke Gemini 2.5 Flash API.<br>6. Gemini API mengembalikan respon terstruktur penjelasan ilmiah.<br>7. Sistem memotong kuota trial (Free) atau sub-kredit token (Premium: 1 Token / 10 respon).<br>8. Sistem menampilkan respon di gelembung obrolan dan menyimpan rekaman ke chat_messages. |
| Alur Alternatif | 3a. Kuota Trial Free User telah habis (= 0): Sistem mengunci area input chat dan memunculkan modal paywall top-up token untuk upgrade ke Premium User.<br>4a. Prompt melanggar Guardrail Akademik (misal: meminta lelucon, kode berbahaya, atau topik di luar naskah): Sistem menolak permintaan dengan pesan santun "AI Asisten VeriText hanya dapat melayani konsultasi naskah ilmiah, tata bahasa, dan perbaikan sitasi akademik". |

Tabel 9: UC-07 Parafrase Instan dan Cek Ulang Kalimat
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-07 |
| Nama Use Case | Parafrase Instan dan Cek Ulang Kalimat |
| Aktor | Free User (Trial 3x), Premium User (Token) |
| Deskripsi Singkat | Pengguna memilih kalimat/paragraf bermasalah pada heatmap untuk diparafrase otomatis oleh AI ke dalam 3 variasi ilmiah, lalu menerapkannya langsung ke naskah dengan hitung ulang skor real-time. |
| Prekondisi | Kalimat berstatus plagiat (Merah/Oranye/Kuning) dipilih pada heatmap dan kuota mencukupi. |
| Postkondisi | Teks naskah diperbarui secara in-place, skor kemiripan segmen dan komposit turun, indikator sorotan berubah menjadi Hijau (Telah Diperbaiki). |
| Alur Utama | 1. Pengguna memilih mode parafrase (Per Kalimat, Per Paragraf, atau Seluruh Halaman Sekaligus).<br>2. Pengguna mengklik tombol "Parafrase Sekarang".<br>3. Sistem memanggil modul AI Paraphrase Engine dengan parameter tone akademik.<br>4. Sistem menghasilkan 3 kartu opsi variasi kalimat/paragraf ilmiah.<br>5. Sistem menghitung estimasi prediksi penurunan skor kemiripan pada masing-masing opsi (misal: turun dari 88% menjadi 8%).<br>6. Pengguna memilih salah satu opsi terbaik dan mengklik tombol "Terapkan ke Naskah & Cek Ulang".<br>7. Sistem mengganti teks kalimat di naskah secara in-place pada tabel audit_sentences.<br>8. Sistem menghitung ulang skor kemiripan segmen dan memperbarui skor komposit total secara real-time.<br>9. Heatmap pada layar web langsung diperbarui: warna sorotan kalimat berubah menjadi Hijau (Telah Diperbaiki). |
| Alur Alternatif | 2a. Kuota habis: Sistem menampilkan penawaran paket token Midtrans.<br>6a. Pengguna tidak ingin menerapkan ke naskah: Pengguna dapat mengklik tombol "Salin Teks" untuk menyalin kalimat ke clipboard manual. |

Tabel 10: UC-08 Unduh Laporan PDF dan Verifikasi QR
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-08 |
| Nama Use Case | Unduh Laporan PDF dan Verifikasi QR |
| Aktor | Premium User (Unduh PDF), Free User / Publik (Verifikasi QR) |
| Deskripsi Singkat | Pengguna Premium mengunduh dokumen laporan audit resmi berformat PDF ber-QR Code. Publik atau dosen dapat memverifikasi keaslian sertifikat melalui pemindaian kode QR di URL publik. |
| Prekondisi | Pemeriksaan naskah telah selesai (UC-04). |
| Postkondisi | Berkas PDF resmi terunduh atau data keaslian sertifikat tervalidasi pada halaman verifikasi. |
| Alur Utama | 1. Pengguna Premium menekan tombol "Unduh Laporan PDF Resmi".<br>2. Sistem memverifikasi peran pengguna (role == 'PREMIUM').<br>3. Sistem mengompilasi data ringkasan naskah, grafik skor, daftar sumber, dan visualisasi heatmap ke dalam format PDF standar akademik.<br>4. Sistem menghasilkan kode QR dinamis yang mengarah ke tautan permanen: https://veritext.ai/verify/{certificate_uuid}.<br>5. Sistem menyematkan stempel digital dan menyajikan unduhan berkas PDF ke browser pengguna.<br>6. Pihak ketiga/publik memindai kode QR dari berkas cetak atau membuka tautan verifikasi.<br>7. Sistem memvalidasi UUID sertifikat pada basis data dan menampilkan halaman verifikasi resmi berstempel hijau. |
| Alur Alternatif | 2a. Free User mencoba menekan tombol unduh PDF: Sistem memunculkan modal paywall "Pengunduhan Laporan PDF dan Sertifikat Keaslian Ber-QR merupakan fitur eksklusif Premium User. Silakan beli paket token untuk upgrade akun Anda". |

Tabel 11: UC-09 Kelola dan Hapus Riwayat Naskah (UU PDP)
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-09 |
| Nama Use Case | Kelola dan Hapus Riwayat Naskah (Kepatuhan UU PDP) |
| Aktor | Free User, Premium User |
| Deskripsi Singkat | Pengguna melihat daftar riwayat naskah yang pernah diperiksa dan dapat menghapus naskah secara permanen (hard-delete cascading) sesuai hak privasi pemilik data. |
| Prekondisi | Pengguna telah masuk ke sistem dan memiliki riwayat pemeriksaan naskah. |
| Postkondisi | Dokumen fisik, sidik jari leksikal, rekaman audit, dan seluruh pesan percakapan chat dihapus permanen dari basis data dan media penyimpanan. |
| Alur Utama | 1. Pengguna membuka menu "Riwayat Naskah" (/history).<br>2. Sistem menyajikan tabel riwayat pemeriksaan (judul naskah, waktu audit, persentase kemiripan, status).<br>3. Pengguna memilih dokumen dan menekan ikon/tombol "Hapus Permanen".<br>4. Sistem memunculkan dialog konfirmasi bahaya penghapusan data permanen sesuai UU PDP.<br>5. Pengguna menyetujui konfirmasi penghapusan.<br>6. Sistem memvalidasi bahwa user_id pemohon cocok dengan pemilik dokumen.<br>7. Sistem mengeksekusi hard-delete cascade: menghapus berkas fisik dari storage, menghapus data naskah dari tabel documents, audit_tasks, audit_sentences, audit_reports, chat_sessions, dan chat_messages.<br>8. Sistem mencatat log peristiwa penghapusan pada audit_logs.<br>9. Sistem menghapus baris naskah dari antarmuka dan menampilkan toast sukses "Dokumen telah dihapus permanen dari sistem". |
| Alur Alternatif | 6a. Pemohon bukan pemilik naskah: Sistem menolak dengan kode 403 Forbidden. |

Tabel 12: UC-10 Beli Kuota Token dan Upgrade Premium
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-10 |
| Nama Use Case | Beli Kuota Token dan Upgrade Premium |
| Aktor | Free User, Premium User |
| Deskripsi Singkat | Pengguna membeli saldo token menggunakan metode pembayaran Midtrans Snap (By Token atau By Paket Token). Verifikasi webhook Midtrans secara instan menambah saldo dan menaikkan status akun menjadi Premium User. |
| Prekondisi | Pengguna telah masuk ke sistem dan berada di halaman /billing. |
| Postkondisi | Saldo TokenWallet bertambah, peran akun naik menjadi PREMIUM, dan invoice PDF tersedia. |
| Alur Utama | 1. Pengguna membuka halaman "Top-Up Kuota Token" (/billing).<br>2. Pengguna memilih salah satu dari 2 skema pembelian:<br>   - Skema A (By Token): Memasukkan jumlah token custom (Rp 2.000/token, minimal 5 token).<br>   - Skema B (By Paket Token): Memilih paket bundling diskon (Starter 15 Token Rp 25.000, Skripsi Pro 50 Token Rp 65.000, Riset Intensif 150 Token Rp 150.000).<br>3. Pengguna mengklik tombol "Beli Sekarang".<br>4. Backend memvalidasi parameter dan menerbitkan transaksi ke Midtrans Snap API.<br>5. Sistem mencatat record invoice berstatus PENDING di database.<br>6. Antarmuka web membuka modal pembayaran sematan Midtrans Snap.<br>7. Pengguna memilih saluran pembayaran (QRIS, GoPay, ShopeePay, Virtual Account Bank Mandiri/BCA/BNI/BRI, atau Kartu Kredit) dan menyelesaikan transaksi.<br>8. Server Midtrans mengirimkan HTTP POST notifikasi webhook ke server VeriText AI.<br>9. Sistem memverifikasi integritas signature_key SHA-512.<br>10. Di dalam transaksi atomik dengan row-level lock: sistem memperbarui status invoice menjadi SETTLEMENT, menambah saldo TokenWallet, dan mengubah peran akun pengguna menjadi PREMIUM.<br>11. Antarmuka web pengguna mendeteksi status sukses, menampilkan saldo token baru, badge akun "PREMIUM USER", dan tautan unduh invoice PDF. |
| Alur Alternatif | 9a. Signature key webhook tidak cocok: Sistem menolak notifikasi dengan kode 400 Bad Request demi keamanan.<br>10a. Pembayaran kedaluwarsa atau dibatalkan pengguna: Status invoice diperbarui menjadi EXPIRED / CANCELLED tanpa mutasi saldo. |

Tabel 13: UC-11 Pantau Dasbor Analitik dan Log Transaksi (100% Read-Only)
| Atribut | Keterangan |
| :--- | :--- |
| Kode Use Case | UC-11 |
| Nama Use Case | Pantau Dasbor Analitik dan Log Transaksi (Admin 100% Read-Only) |
| Aktor | Admin (Read-Only) |
| Deskripsi Singkat | Administrator memantau indikator kinerja layanan, analitik audit naskah, log transaksi keuangan Midtrans, dan kesehatan infrastruktur server tanpa intervensi data pengguna. |
| Prekondisi | Administrator masuk ke sistem menggunakan akun berstatus role == 'ADMIN'. |
| Postkondisi | Administrator memperoleh wawasan operasional sistem secara real-time. |
| Alur Utama | 1. Administrator membuka halaman /admin.<br>2. Sistem memvalidasi token JWT dan memastikan hak akses murni role == 'ADMIN'.<br>3. Sistem mengeksekusi kueri agregasi SELECT pada basis data (menghitung total naskah diperiksa, rata-rata skor kemiripan, total revenue keuangan, jumlah pengguna aktif).<br>4. Sistem menyajikan grafik tren pemindaian dan distribusi pelanggaran plagiarisme multi-tier.<br>5. Administrator membuka tab "Log Transaksi Midtrans" untuk mengamati daftar 50 transaksi pembayaran terakhir beserta status pelunasannya.<br>6. Administrator membuka tab "Telemetri Sistem" untuk memantau status kesehatan antrean Celery Worker, latensi kueri pgvector, dan pemakaian memori Redis.<br>7. Seluruh interaksi bersifat 100% Read-Only (hanya pembacaan data tanpa tombol/fungsi pengubahan). |
| Alur Alternatif | 2a. Pengguna non-admin mencoba membuka URL /admin: Sistem menolak akses dengan kode 403 Forbidden dan mencatat insiden keamanan pada audit_logs. |

4.3 Spesifikasi Kebutuhan Fungsional (Tabel FR)
Kebutuhan fungsional sistem diklasifikasikan ke dalam modul-modul berikut:

Tabel 14: Kebutuhan Fungsional Modul Autentikasi dan Profil (FR-AUTH)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-AUTH-01 | Registrasi Akun Mandiri | Sistem wajib menyediakan formulir pendaftaran akun mandiri menggunakan alamat email unik, nama lengkap, dan kata sandi minimal 8 karakter. | Wajib (Mandatory) |
| FR-AUTH-02 | Otentikasi Masuk Email | Sistem wajib memvalidasi kredensial pengguna menggunakan verifikasi hash kata sandi berbasis algoritma Bcrypt (work factor 12). | Wajib (Mandatory) |
| FR-AUTH-03 | Alokasi Kuota Pengguna Baru | Sistem wajib secara otomatis mengalokasikan saldo awal 5 Token Gratis dan 3 kali Kuota Trial AI Chatbot/Parafrase pada TokenWallet saat akun FREE pertama kali terdaftar. | Wajib (Mandatory) |
| FR-AUTH-04 | Masuk Cepat Google OAuth 2.0 | Sistem wajib mendukung autentikasi Single Sign-On (SSO) menggunakan Google OAuth 2.0 dengan verifikasi integritas Google ID Token di sisi server. | Wajib (Mandatory) |
| FR-AUTH-05 | Manajemen Sesi JWT Ganda | Sistem wajib menerbitkan Access Token JWT berbatas waktu 15 menit dan Refresh Token acak tersimpan pada HttpOnly Secure Cookie dengan masa berlaku 7 hari. | Wajib (Mandatory) |
| FR-AUTH-06 | Rotasi Refresh Token Otomatis | Sistem wajib menerapkan mekanisme Refresh Token Rotation; setiap penggunaan token pembaruan wajib menerbitkan token baru dan menganulir token sebelumnya. | Wajib (Mandatory) |
| FR-AUTH-07 | Pencabutan Sesi dan Keluar | Sistem wajib menyediakan fitur Logout yang menghapus cookie sesi di peramban dan membatalkan hash refresh token pada tabel sessions di basis data. | Wajib (Mandatory) |
| FR-AUTH-08 | Perbarui Profil Mandiri | Sistem wajib mengizinkan pengguna memperbarui nama lengkap dan institusi afiliasi dengan validasi sanitasi teks anti-XSS. | Wajib (Mandatory) |
| FR-AUTH-09 | Perbarui Kata Sandi Akun | Sistem wajib memvalidasi kecocokan kata sandi lama sebelum mengizinkan pembaruan hash kata sandi baru dan mencabut seluruh sesi aktif lain. | Wajib (Mandatory) |
| FR-AUTH-10 | Pemulihan Lupa Kata Sandi | Sistem wajib menyediakan fitur pemulihan kata sandi melalui pengiriman token pemulihan acak berbatas waktu 60 menit ke email pengguna terdaftar. | Wajib (Mandatory) |
| FR-AUTH-11 | Penerapan Role-Based Access Control (RBAC) | Sistem wajib menerapkan kontrol akses berbasis 3 peran (FREE, PREMIUM, ADMIN Read-Only) secara ketat pada setiap rute antarmuka dan endpoint API backend. | Wajib (Mandatory) |

Tabel 15: Kebutuhan Fungsional Modul Unggah dan Pra-pemrosesan Naskah (FR-DOC)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-DOC-01 | Dukungan Format Berkas | Sistem wajib mendukung pengunggahan berkas digital dengan ekstensi .pdf, .docx, .txt, serta input penempelan teks langsung pada area kerja editor. | Wajib (Mandatory) |
| FR-DOC-02 | Batasan Ukuran Berkas Fisik | Sistem wajib membatasi ukuran fisik berkas yang diunggah maksimal 15 Megabytes (MB) dan menolak berkas yang melebihi batas tersebut. | Wajib (Mandatory) |
| FR-DOC-03 | Validasi Magic MIME-Type | Sistem wajib memvalidasi berkas berdasarkan magic bytes MIME-type untuk mencegah manipulasi ekstensi palsu atau serangan berkas berbahaya. | Wajib (Mandatory) |
| FR-DOC-04 | Ekstraksi Teks Bersih | Sistem wajib mengekstraksi teks dokumen, menghapus tag biner, dan menormalisasi whitespace tanpa menghilangkan struktur paragraf asli. | Wajib (Mandatory) |
| FR-DOC-05 | Segmentasi Kalimat Cerdas | Sistem wajib memecah teks dokumen menjadi array kalimat diskret menggunakan pustaka pemroses bahasa alami berbasis tanda baca akhir kalimat (. ! ?). | Wajib (Mandatory) |
| FR-DOC-06 | Batasan Panjang Naskah Free User | Sistem wajib membatasi panjang naskah per pemeriksaan untuk Free User maksimal 2.500 kata (setara 1 Token) dan menampilkan modal peningkatan akun jika melampaui batas. | Wajib (Mandatory) |
| FR-DOC-07 | Dukungan Naskah Panjang Premium User | Sistem wajib mendukung pemrosesan naskah panjang (skripsi/tesis puluhan ribu kata) untuk akun Premium User dengan batas berkas 15 MB. | Wajib (Mandatory) |
| FR-DOC-08 | Kalkulator Token Real-Time | Sistem wajib menghitung jumlah kata secara real-time sebelum pemindaian dan menampilkan biaya token berdasarkan formula: min(5, ceil(kata / 2500)) Token. | Wajib (Mandatory) |

Tabel 16: Kebutuhan Fungsional Modul Akuisisi Korpus Otomatis (FR-CORP)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-CORP-01 | Pemanenan Otomatis OpenAlex Graph API | Sistem wajib memiliki layanan AutomatedCorpusHarvester yang menarik metadata, DOI, dan abstrak karya ilmiah Indonesia & global dari OpenAlex API secara berkala. | Wajib (Mandatory) |
| FR-CORP-02 | Pemanenan Jurnal DOAJ & Semantic Scholar | Sistem wajib mengintegrasikan penarikan artikel akses terbuka dari DOAJ REST API dan Semantic Scholar Academic Graph untuk memperkaya perbendaharaan ilmiah. | Wajib (Mandatory) |
| FR-CORP-03 | Pengindeksan Vektor HNSW Dual-Scope | Sistem wajib memecah dokumen korpus menjadi potongan teks (chunks) 300 kata, menghasilkan dense embeddings 384-d, dan menyimpannya di indeks graf HNSW pgvector. | Wajib (Mandatory) |
| FR-CORP-04 | Grounding Pencarian Web Publik | Sistem wajib mendukung modul WebScanner yang memanfaatkan Google Search Grounding untuk menelusuri artikel web publik dan repositori kampus (e-Prints). | Wajib (Mandatory) |

Tabel 17: Kebutuhan Fungsional Modul Mesin Deteksi Plagiarisme 3-Tahap (FR-DET)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-DET-01 | Step 1: Deteksi Leksikal Winnowing | Sistem wajib mengimplementasikan algoritma Winnowing dengan Rabin-Karp rolling hash (basis b=257, modulus prima M=1.000.000.007, k-gram=5, sliding window w=4) untuk mendeteksi penjiplakan leksikal verbatim. | Wajib (Mandatory) |
| FR-DET-02 | Ambang Batas Leksikal (Merah) | Sistem wajib menandai kalimat dengan nilai koefisien Jaccard Containment >= 80% sebagai pelanggaran leksikal berindikator MERAH (Tier 1). | Wajib (Mandatory) |
| FR-DET-03 | Step 2: Deteksi Semantik SBERT | Sistem wajib menghasilkan embedding vektor 384 dimensi pada tiap kalimat menggunakan paraphrase-multilingual-MiniLM-L12-v2 dan mencari tetangga terdekat pada pgvector HNSW menggunakan operator jarak Cosine (<=>). | Wajib (Mandatory) |
| FR-DET-04 | Re-Ranker Spesialis Bahasa Indonesia | Sistem wajib menyaring pasangan kalimat kandidat berbahasa Indonesia menggunakan model LazarusNLP/all-indobert-base-v4 untuk mengevaluasi sinonim morfologis ilmiah. | Wajib (Mandatory) |
| FR-DET-05 | Ambang Batas Semantik (Oranye) | Sistem wajib menandai kalimat dengan nilai Cosine Similarity >= 75% (jarak <= 0.25) yang tidak terdeteksi pada Step 1 sebagai parafrase berindikator ORANYE (Tier 2). | Wajib (Mandatory) |
| FR-DET-06 | Step 3: Evaluasi Stilometri | Sistem wajib mengevaluasi ritme variasi penulisan menggunakan rumus Goh & Barabasi Burstiness B dan Type-Token Ratio (TTR) untuk mendeteksi kalimat hasil sintesis LLM. | Wajib (Mandatory) |
| FR-DET-07 | Contextual AI Judge & Filter Sitasi | Sistem wajib mengintegrasikan Gemini 2.5 Flash / OpenRouter untuk menyaring false positive (kutipan berizin dengan penanda sitasi resmi) dan menandai kalimat anomali berindikator KUNING (Tier 3). | Wajib (Mandatory) |
| FR-DET-08 | Formula Agregasi Skor Komposit | Sistem wajib menghitung skor kemiripan akhir dokumen berdasarkan formula agregasi berbobot: Skor_Komposit = (0.50 * Skor_Leksikal) + (0.35 * Skor_Semantik) + (0.15 * Skor_Stilometri). | Wajib (Mandatory) |
| FR-DET-09 | Penjadwalan Tugas Asinkron Celery | Sistem wajib mendelegasikan eksekusi pemindaian ke antrean tugas Celery Redis dengan dukungan antrean prioritas (Priority Queue) untuk pengguna berbayar. | Wajib (Mandatory) |

Tabel 18: Kebutuhan Fungsional Modul AI Chatbot & Parafrase Instan (FR-CHAT)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-CHAT-01 | Panel AI Chatbot Kontekstual | Sistem wajib menyediakan panel AI Chatbot interaktif yang disematkan berdampingan dengan lembar Interactive Heatmap pada Split-Screen Studio Workspace. | Wajib (Mandatory) |
| FR-CHAT-02 | Guardrail Asisten Akademik | Sistem wajib menerapkan modul AcademicGuardrail yang menolak permintaan percakapan di luar konteks evaluasi naskah ilmiah, perbaikan tata bahasa, parafrase, dan sitasi. | Wajib (Mandatory) |
| FR-CHAT-03 | Parafrase Instan 3-Mode Granularitas | Sistem wajib menyediakan fitur parafrase cerdas dalam 3 mode pilihan: Mode Per Kalimat (Single Sentence), Mode Per Paragraf (Paragraph Block), dan Mode Seluruh Halaman (Full Page Batch). | Wajib (Mandatory) |
| FR-CHAT-04 | Generator 3 Variasi Opsi Ilmiah | Sistem wajib menghasilkan 3 pilihan variasi kalimat/paragraf dengan kosakata akademik terstandar lengkap dengan estimasi prediksi penurunan persentase kemiripan. | Wajib (Mandatory) |
| FR-CHAT-05 | Terapkan ke Naskah In-Place & Re-Score | Sistem wajib menyediakan tombol "Terapkan ke Naskah & Cek Ulang" yang mengganti teks kalimat di naskah secara in-place, menghitung ulang skor secara real-time, dan mengubah warna sorotan menjadi HIJAU (Telah Diperbaiki). | Wajib (Mandatory) |
| FR-CHAT-06 | Batasan Kuota Trial Pengguna Gratis | Sistem wajib membatasi penggunaan AI Chatbot dan Parafrase Instan pada akun FREE maksimal 3 kali respon uji coba sebelum menampilkan modal paywall peningkatan akun. | Wajib (Mandatory) |
| FR-CHAT-07 | Tarif Token Pengguna Premium | Sistem wajib memotong kuota akun PREMIUM dengan tarif transparan: 1 Token untuk 10 kali respon chat/parafrase per kalimat, atau 1 Token per 2 halaman penuh untuk batch paraphrase. | Wajib (Mandatory) |

Tabel 19: Kebutuhan Fungsional Modul Pelaporan dan Sertifikasi PDF (FR-REP)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-REP-01 | Tampilan Interactive Heatmap Web | Sistem wajib menyajikan hasil audit dalam format Interactive Heatmap pada antarmuka web yang dapat ditinjau oleh seluruh pengguna (Free maupun Premium). | Wajib (Mandatory) |
| FR-REP-02 | Komparasi Teks Berdampingan | Sistem wajib menyajikan tampilan pembanding berdampingan (Side-by-Side Diff) antara kalimat naskah pengguna dengan teks sumber asli pembanding. | Wajib (Mandatory) |
| FR-REP-03 | Filter Sorotan Berdasarkan Tier | Sistem wajib menyediakan tombol filter tampilan sorotan heatmap ([Semua], [Merah - Leksikal], [Oranye - Semantik], [Kuning - Gaya]) untuk memudahkan navigasi. | Wajib (Mandatory) |
| FR-REP-04 | Pembuatan Laporan PDF Resmi | Sistem wajib menyediakan fitur generate dokumen Laporan Audit Resmi berformat PDF berkualitas cetak yang dilengkapi diagram skor, daftar sumber, dan stempel digital bagi Premium User. | Wajib (Mandatory) |
| FR-REP-05 | Penyematan Kode QR Dinamis | Sistem wajib menyematkan kode QR dinamis pada setiap berkas laporan PDF resmi yang mengarah ke URL verifikasi publik (/verify/{certificate_uuid}). | Wajib (Mandatory) |
| FR-REP-06 | Verifikasi Sertifikat Publik | Sistem wajib menyediakan halaman validasi publik tanpa kewajiban autentikasi untuk memverifikasi keaslian sertifikat dan menampilkan badge hijau keabsahan naskah. | Wajib (Mandatory) |
| FR-REP-07 | Riwayat Pemeriksaan Naskah | Sistem wajib menyimpan riwayat seluruh naskah yang pernah dipindai oleh pengguna pada tabel documents dan audit_tasks. | Wajib (Mandatory) |
| FR-REP-08 | Penghapusan Permanen (UU PDP) | Sistem wajib menyediakan fitur penghapusan naskah secara permanen (hard-delete cascading) yang menghapus berkas fisik, rekaman audit, dan riwayat chat dari sistem. | Wajib (Mandatory) |

Tabel 20: Kebutuhan Fungsional Modul Monetisasi, Token & Midtrans (FR-PAY)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-PAY-01 | Manajemen Saldo TokenWallet | Sistem wajib mencatat saldo token komputasi pengguna pada tabel token_wallets dan mendukung pencatatan riwayat transaksi kredit/debit secara atomik. | Wajib (Mandatory) |
| FR-PAY-02 | Pemotongan Token Proporsional | Sistem wajib memotong saldo token saat pemeriksaan naskah berdasarkan rumus: min(5, ceil(kata / 2500)) Token. | Wajib (Mandatory) |
| FR-PAY-03 | Skema Pembelian By Token (Satuan) | Sistem wajib mendukung pembelian token satuan kustom dengan harga dasar Rp 2.000 per token (minimal pembelian 5 Token = Rp 10.000). | Wajib (Mandatory) |
| FR-PAY-04 | Skema Pembelian By Paket Token | Sistem wajib menyediakan 3 pilihan paket bundling diskon: Paket Starter (15 Token = Rp 25.000), Paket Skripsi Pro (50 Token = Rp 65.000), dan Paket Riset Intensif (150 Token = Rp 150.000). | Wajib (Mandatory) |
| FR-PAY-05 | Integrasi Modal Midtrans Snap | Sistem wajib mengintegrasikan antarmuka gerbang pembayaran Midtrans Snap API untuk memproses berbagai saluran bayar (QRIS, e-Wallet, VA Bank, Kartu Kredit). | Wajib (Mandatory) |
| FR-PAY-06 | Penerimaan Webhook Terverifikasi | Sistem wajib menerima HTTP POST notifikasi webhook Midtrans dan memvalidasi keaslian signature_key berbasis algoritma SHA-512. | Wajib (Mandatory) |
| FR-PAY-07 | Peningkatan Akun Otomatis (Auto-Upgrade) | Sistem wajib secara otomatis mengubah status peran pengguna dari FREE menjadi PREMIUM seketika saat notifikasi pelunasan (settlement/capture) terverifikasi. | Wajib (Mandatory) |
| FR-PAY-08 | Isolasi Transaksi Atomik Database | Seluruh mutasi saldo dan pembaruan invoice wajib menggunakan transaksi terisolasi dengan penguncian baris (row-level locking SELECT ... FOR UPDATE). | Wajib (Mandatory) |
| FR-PAY-09 | Pembuatan Unduhan Invoice PDF | Sistem wajib menyediakan dokumen tanda terima pembayaran digital (invoice PDF) resmi yang dapat diunduh pengguna dari halaman penagihan. | Wajib (Mandatory) |

Tabel 21: Kebutuhan Fungsional Modul Pemantauan Layanan Admin (FR-ADM)
| Kode FR | Nama Kebutuhan Fungsional | Deskripsi Spesifikasi Teknis | Tingkat Kepentingan |
| :--- | :--- | :--- | :--- |
| FR-ADM-01 | Dasbor Analitik Global Read-Only | Sistem wajib menyediakan tampilan dasbor analitik bagi Admin untuk memantau agregat total naskah diperiksa, rata-rata skor kemiripan, total revenue, dan jumlah pengguna aktif. | Wajib (Mandatory) |
| FR-ADM-02 | Log Transaksi Keuangan Read-Only | Sistem wajib menyajikan tabel riwayat transaksi pembayaran Midtrans secara real-time yang mencakup order_id, metode bayar, nominal bruto, dan status transaksi. | Wajib (Mandatory) |
| FR-ADM-03 | Telemetri Kesehatan Antrean Worker | Sistem wajib menampilkan status kesehatan antrean tugas Celery, jumlah worker aktif, pemakaian memori Redis, dan latensi kueri pgvector secara pasif. | Wajib (Mandatory) |
| FR-ADM-04 | Log Audit Keamanan Sistem | Sistem wajib mencatat dan menyajikan rekaman log aktivitas keamanan penting (percobaan login gagal, insiden brute-force, dan penghapusan naskah) pada tabel audit_logs. | Wajib (Mandatory) |

---

5. Kebutuhan Non-Fungsional (Non-Functional Requirements)

5.1 Kebutuhan Performa (Performance Requirements)
Tabel 22: Kebutuhan Non-Fungsional Performa (NFR-PERF)
| Kode NFR | Parameter Kualitas | Spesifikasi Target Terukur |
| :--- | :--- | :--- |
| NFR-PERF-01 | Waktu Respon API Gateway | 95% permintaan REST API non-audit (autentikasi, profil, riwayat, billing) wajib direspons dengan latensi <= 200 milidetik pada beban normal. |
| NFR-PERF-02 | Kecepatan Deteksi Leksikal | Tahap 1 Winnowing leksikal wajib menyelesaikan pemindaian naskah 2.500 kata dalam waktu <= 1,5 detik. |
| NFR-PERF-03 | Kecepatan Kueri Vektor HNSW | Kueri pencarian tetangga terdekat Cosine (<=>) pada indeks HNSW pgvector wajib diselesaikan dalam waktu <= 100 milidetik per batch kalimat. |
| NFR-PERF-04 | Latensi Respon AI Chatbot | Respon konsultasi AI Chatbot dan pembuatan 3 variasi parafrase via Gemini 2.5 Flash API wajib disajikan dalam waktu <= 5,0 detik. |
| NFR-PERF-05 | Kapasitas Konkurensi Worker | Klaster Celery Worker pada infrastruktur minimum wajib mampu memproses minimal 10 tugas pemindaian naskah secara paralel tanpa kegagalan antrean. |

5.2 Kebutuhan Keamanan (Security Requirements)
Tabel 23: Kebutuhan Non-Fungsional Keamanan (NFR-SEC)
| Kode NFR | Parameter Kualitas | Spesifikasi Target Terukur |
| :--- | :--- | :--- |
| NFR-SEC-01 | Enkripsi Kanal Komunikasi | Seluruh komunikasi klien-server wajib menggunakan enkripsi TLS versi 1.3 dengan cipher suite modern dan konfigurasi HSTS (Strict-Transport-Security). |
| NFR-SEC-02 | Hashing Kata Sandi | Kata sandi pengguna wajib disimpan dalam bentuk hash kriptografis menggunakan algoritma Bcrypt dengan cost factor minimal 12. |
| NFR-SEC-03 | Integritas Webhook Pembayaran | Endpoint webhook Midtrans wajib memvalidasi kecocokan SHA-512 signature key sebelum melakukan mutasi saldo token atau kenaikan peran akun. |
| NFR-SEC-04 | Keamanan Cookie Sesi | Refresh token wajib dikirimkan dalam cookie dengan atribut HttpOnly, Secure, dan SameSite=Lax untuk mencegah serangan pencurian sesi via Cross-Site Scripting (XSS). |
| NFR-SEC-05 | Masa Berlaku Token Akses | Access Token JWT wajib dikonfigurasi dengan masa kedaluwarsa maksimal 15 menit untuk meminimalisasi risiko penyalahgunaan token yang terkompromi. |
| NFR-SEC-06 | Proteksi SQL Injection | Seluruh interaksi basis data wajib menggunakan ORM SQLAlchemy 2.0 dengan kueri terparameterisasi penuh (parameterized queries); dilarang merangkai string SQL mentah. |
| NFR-SEC-07 | Sanitasi Masukan Teks (XSS) | Seluruh input string dari formulir dan unggahan teks wajib melalui proses sanitasi karakter berbahaya sebelum disimpan ke database atau dirender ke DOM. |
| NFR-SEC-08 | Pembatasan Laju Permintaan (Rate Limiting) | Endpoint autentikasi dan API publik wajib dibatasi maksimal 60 permintaan per menit per alamat IP menggunakan mekanisme sliding window rate limiter. |
| NFR-SEC-09 | Isolasi Transaksi Atomik (Concurrency) | Setiap mutasi saldo token dan perubahan status invoice wajib menggunakan penguncian baris eksplisit (SELECT ... FOR UPDATE) untuk mencegah race condition. |
| NFR-SEC-10 | Sanitasi Nama dan Tipe Berkas | Berkas naskah yang diunggah wajib diubah namanya menjadi acak UUIDv4 dan divalidasi berdasarkan magic bytes MIME-type untuk mencegah eksekusi skrip berbahaya. |
| NFR-SEC-11 | Pencatatan Log Audit Keamanan | Seluruh peristiwa login gagal, perubahan hak akses, transaksi pembayaran, dan penghapusan naskah wajib dicatat secara persisten pada tabel audit_logs. |
| NFR-SEC-12 | Proteksi Prompt Injection & Scope Guardrail | Modul AI Chatbot wajib dilengkapi Academic Guardrail untuk mendeteksi upaya manipulasi prompt (jailbreak/prompt injection) dan menolak instruksi di luar koridor akademik. |

5.3 Kebutuhan Kepatuhan Data dan Privasi (Compliance Requirements)
Tabel 24: Kebutuhan Non-Fungsional Kepatuhan Privasi (NFR-COMP)
| Kode NFR | Parameter Kualitas | Spesifikasi Target Terukur |
| :--- | :--- | :--- |
| NFR-COMP-01 | Kepatuhan UU Perlindungan Data Pribadi | Sistem wajib mematuhi seluruh ketentuan UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi dalam hal pengumpulan, pemrosesan, dan penyimpanan data pengguna. |
| NFR-COMP-02 | Hak Penghapusan Data Permanen (Right to Erasure) | Sistem wajib menyediakan mekanisme penghapusan naskah secara tuntas (hard-delete cascading) yang menghapus seluruh jejak berkas fisik, hasil audit, dan rekaman percakapan chat. |
| NFR-COMP-03 | Jaminan Privasi Naskah (Zero Auto-Ingestion) | Naskah yang diunggah oleh pengguna tidak pernah dijadikan korpus publik tanpa izin eksplisit; naskah pengguna tetap menjadi hak milik intelektual pengguna seutuhnya. |

5.4 Kebutuhan Keandalan (Reliability Requirements)
Tabel 25: Kebutuhan Non-Fungsional Keandalan (NFR-REL)
| Kode NFR | Parameter Kualitas | Spesifikasi Target Terukur |
| :--- | :--- | :--- |
| NFR-REL-01 | Ketersediaan Layanan (Availability) | Sistem wajib memiliki tingkat ketersediaan (uptime) minimal 99,5% dalam periode evaluasi bulanan, di luar jadwal pemeliharaan terencana. |
| NFR-REL-02 | Mekanisme Retry Tugas Asinkron | Worker Celery wajib memiliki kebijakan otomatis mencoba ulang (retry policy) hingga 3 kali dengan penundaan eksponensial jika terjadi kegagalan jaringan API eksternal. |
| NFR-REL-03 | Pengembalian Saldo Otomatis (Token Refund) | Jika tugas pemindaian naskah gagal total setelah 3 kali percobaan, sistem wajib mengembalikan saldo token yang sempat dipotong secara otomatis ke TokenWallet pengguna. |
| NFR-REL-04 | Penurunan Layanan Anggun (Graceful Degradation) | Jika API Google Gemini mengalami gangguan, modul AI Judge wajib melakukan fallback ke penyedia OpenRouter secara transparan tanpa menghentikan proses audit. |

5.5 Kebutuhan Kegunaan (Usability Requirements)
Tabel 26: Kebutuhan Non-Fungsional Kegunaan (NFR-USAB)
| Kode NFR | Parameter Kualitas | Spesifikasi Target Terukur |
| :--- | :--- | :--- |
| NFR-USAB-01 | Kebijakan Visual Bebas Emoji (Zero-Emoji Policy) | Seluruh komponen antarmuka web, teks, notifikasi, dan diagram sistem dilarang menggunakan emoji visual apapun; antarmuka wajib bergaya akademik utilitarian. |
| NFR-USAB-02 | Keterbacaan dan Kontras Aksesibilitas | Desain antarmuka wajib memenuhi rasio kontras teks minimal 4,5:1 sesuai pedoman Web Content Accessibility Guidelines (WCAG 2.1 Level AA). |
| NFR-USAB-03 | Waktu Adaptasi Pengguna Baru | Pengguna baru dengan kemampuan operasional komputer standar wajib mampu memahami alur unggah dan peninjauan heatmap dalam waktu <= 10 menit tanpa pelatihan formal. |
| NFR-USAB-04 | Responsivitas Tata Letak Layar | Antarmuka Split-Screen Studio Workspace wajib menyesuaikan tata letak secara mulus pada resolusi layar 1280 piksel ke atas dan bertransformasi menjadi susunan bertumpuk pada layar tablet 768 piksel. |

5.6 Kebutuhan Pemeliharaan (Maintainability Requirements)
Tabel 27: Kebutuhan Non-Fungsional Pemeliharaan (NFR-MAINT)
| Kode NFR | Parameter Kualitas | Spesifikasi Target Terukur |
| :--- | :--- | :--- |
| NFR-MAINT-01 | Pola Arsitektur Berlapis (Clean Architecture) | Struktur kode backend wajib memisahkan secara tegas antara lapisan controller (API), lapisan service (logika bisnis), lapisan repository (akses data), dan lapisan worker. |
| NFR-MAINT-02 | Cakupan Pengujian Otomatis (Test Coverage) | Basis kode backend wajib memiliki cakupan pengujian unit dan integrasi otomatis (pytest) minimal 80% pada modul logika bisnis utama. |
| NFR-MAINT-03 | Dokumentasi Kontrak API Interaktif | Seluruh endpoint REST API wajib terdokumentasi secara otomatis menggunakan OpenAPI 3.1 dan dapat diakses melalui antarmuka interaktif Swagger UI (/docs). |
| NFR-MAINT-04 | Konfigurasi Terpusat Berbasis Lingkungan | Seluruh kredensial rahasia, URL database, dan API key wajib dikelola melalui berkas konfigurasi .env menggunakan validasi pustaka pydantic-settings. |
"""

def main():
    content = build_srs_content()
    with open(OUTPUT_SRS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully generated complete SRS at {OUTPUT_SRS_PATH}")
    print(f"File size: {os.path.getsize(OUTPUT_SRS_PATH)} bytes, lines: {len(content.splitlines())}")

if __name__ == "__main__":
    main()
