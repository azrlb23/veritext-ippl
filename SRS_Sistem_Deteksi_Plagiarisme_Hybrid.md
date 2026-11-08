Software Requirements Specification
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
Revision History
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
5. Kebutuhan Non-Fungsional (Non-Functional Requirements)
Daftar Pustaka

Revision History
| Name | Date | Reason For Changes | Version |
| :--- | :--- | :--- | :--- |
| Mochammad Azriel Albian Putra | 10 Maret 2026 | Draf inisial spesifikasi kebutuhan sistem deteksi plagiarisme leksikal. | 0.1 |
| Mochammad Azriel Albian Putra | 28 April 2026 | Integrasi deteksi semantik berbasis Sentence Transformers dan pgvector. | 0.5 |
| Mochammad Azriel Albian Putra | 15 Mei 2026 | Penambahan modul monetisasi token Midtrans dan sertifikasi laporan QR. | 0.9 |
| Mochammad Azriel Albian Putra | 24 Juni 2026 | Rilis final disetujui: Transformasi penuh ke arsitektur Self-Service SaaS 3-Role (Free, Premium, Admin Read-Only), 3-Step Hybrid AI Pipeline, modul AI Chatbot Asisten Naskah & Parafrase Instan 3-Mode, akuisisi korpus otomatis Dual-Scope, dan Split-Screen Studio Workspace. | 1.0 |

---

1. Pendahuluan

1.1 Tujuan Penulisan Dokumen
Dokumen Software Requirements Specification (SRS) ini bertujuan untuk mendefinisikan secara komprehensif, terperinci, terstruktur, dan terukur seluruh kebutuhan fungsional (functional requirements) serta kebutuhan non-fungsional (non-functional requirements) dalam perancangan dan pengembangan sistem VeriText AI (Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical & Semantic AI Engine). Dokumen ini menjadi baseline acuan formal bagi seluruh pemangku kepentingan (stakeholders), mencakup pengembang backend, insinyur kecerdasan buatan (AI engineer), pengembang frontend, analis sistem, perancang UI/UX, penguji perangkat lunak (QA engineer), serta dosen evaluator mata kuliah Implementasi Proses Perangkat Lunak (IPPL).

1.2 Audien yang Dituju dan Pembaca yang Disarankan
Dokumen ini disusun untuk dipahami oleh pembaca dengan peran dan tanggung jawab teknis sebagai berikut:
1. Pengembang Backend & AI Engineer: Sebagai panduan implementasi pipa pemrosesan dokumen bertingkat (Algoritma Winnowing Rabin-Karp, inferensi model Sentence Transformers paraphrase-multilingual-MiniLM-L12-v2, re-ranker LazarusNLP/all-indobert-base-v4, kalkulasi stilometri Goh & Barabasi Burstiness, integrasi Dual-Engine LLM Gateway Google Gemini 2.5 Flash & DeepSeek v4.1 Flash via 9Router, pengindeksan vektor HNSW di PostgreSQL pgvector, serta antrean tugas asinkron Celery Redis).
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
| Burstiness (B) | Metrik stilometri Goh & Barabasi B = (sigma_L - mu_L) / (sigma_L + mu_L) yang mengukur koefisien keanekaragaman panjang kalimat untuk mengidentifikasi teks yang dihasilkan oleh model bahasa AI (LLM). |
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
Sistem VeriText AI memiliki tiga aktor utama yang memiliki karakteristik, wewenang, dan hak akses berbeda sesuai dengan perannya masing-masing dalam model layanan mandiri (Self-Service SaaS):

Tabel 2 Karakteristik Pengguna
| Kategori Pengguna | Deskripsi Tugas Utama | Hak Akses dalam Sistem | Tingkat Kemampuan yang Dibutuhkan |
| :--- | :--- | :--- | :--- |
| Free User (Pengguna Gratis) | Mengunggah dan memeriksa keaslian naskah mandiri hingga batas 2.500 kata per pemeriksaan (setara 1 Token / 1 makalah), meninjau laporan hasil pemindaian melalui Interactive Heatmap di peramban web, berkonsultasi perbaikan kalimat via AI Chatbot (kuota trial maksimal 3 kali respon), serta melakukan top-up kuota token untuk meningkatkan status akun. | Akses fitur dasar (UC-01 Masuk/Daftar, UC-02 Profil, UC-03 Unggah Naskah batas 2.500 kata, UC-04 Eksekusi Deteksi, UC-05 Tinjau Heatmap Web View, UC-06 AI Chatbot Trial 3x, UC-07 Parafrase Instan Trial 3x, UC-08 Verifikasi QR Publik, UC-09 Hapus Riwayat Naskah Mandiri sesuai UU PDP, UC-10 Pembelian Token & Upgrade Premium). Terkunci dari pengunduhan berkas Laporan PDF Resmi dan dibatasi pada pemindaian naskah pendek. | Pengguna awam/pemula dengan kemampuan dasar operasional peramban web (browser), formulir digital, serta navigasi teks naskah akademik standar. |
| Premium User (Pengguna Pro / Berbayar) | Memindai naskah akademik berskala panjang (proposal, skripsi, tesis, disertasi hingga puluhan ribu kata, batas berkas 15 MB), memanfaatkan fitur AI Chatbot dan Parafrase Instan 3-Mode (Per Kalimat, Per Paragraf, Seluruh Halaman) secara bebas selama saldo token mencukupi, mengunduh Laporan Audit Resmi berformat PDF beresolusi tinggi lengkap dengan segel digital dan Dynamic QR Code, serta mengelola pembelian token dan unduhan invoice resmi. | Akses penuh fitur pengguna (seluruh hak Free User ditambah pemrosesan naskah panjang tanpa batas kata dengan formula token cap maksimal 5 token pada UC-03 & UC-04, akses AI Chatbot & Parafrase tanpa batas trial pada UC-06 & UC-07 berbasis pemotongan saldo token komputasi, unduh dokumen PDF resmi ber-QR pada UC-08, serta top-up token dan unduh invoice pada UC-10). | Mahasiswa tingkat akhir, dosen, peneliti, atau akademisi profesional dengan kemampuan interpretasi skor kemiripan multi-tier (leksikal, semantik, stilometri) dan penyuntingan naskah ilmiah. |
| Admin (Pengelola Layanan Read-Only) | Memantau stabilitas operasional layanan secara pasif, mengamati analitik global (agregat total naskah diperiksa, rata-rata skor plagiarisme, total omzet transaksi keuangan Midtrans, jumlah pengguna aktif), mengawasi telemetri kesehatan antrean tugas worker Celery dan utilisasi memori Redis/pgvector, serta meninjau log audit keamanan sistem (Security Audit Logs) tanpa intervensi data privat pengguna. | Akses khusus 100% Read-Only ke Dasbor Pemantauan Layanan (/admin pada UC-11) dan autentikasi login (UC-01). Dilarang keras memutasi saldo token, memodifikasi identitas pengguna, mengubah status peran secara manual, atau melihat dan mengunduh berkas naskah privat milik pengguna demi mematuhi UU PDP No. 27/2022. | Administrator sistem atau personel teknis IT dengan kemampuan pemahaman telemetri server, pembacaan log transaksi keuangan, serta analisis kesehatan infrastruktur aplikasi web. |

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
   - Runtime Backend: Python 3.11+ (FastAPI 0.115, SQLAlchemy 2.0 async, Celery 5.4).
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
4. Smart Polling Asinkron: Pengembang frontend Vue 3.5 mengimplementasikan mekanisme smart polling menggunakan Axios dengan interval adaptif (3 detik saat QUEUED, 1,5 detik saat PROCESSING, dan 5 detik saat terjadi kendala jaringan) untuk memantau status penyelesaian audit naskah asinkron pada endpoint GET /api/v1/audits/{task_id}/status.
5. Webhook Security Interface: Endpoint penerimaan webhook pembayaran (POST /api/v1/billing/webhook) memvalidasi keaslian notifikasi menggunakan algoritma SHA-512 dengan rumus:
   SHA512(order_id + status_code + gross_amount + ServerKey).

---


---

4. Functional Requirement
Sistem VeriText AI mendefinisikan serangkaian kebutuhan fungsional komprehensif yang memfasilitasi seluruh siklus operasional deteksi plagiarisme cerdas, bimbingan parafrase interaktif, pelaporan tersertifikasi, dan tata kelola akun mandiri. Kebutuhan fungsional dipetakan secara terstruktur ke dalam 7 klaster arsitektural utama pada tabel berikut:

Tabel 3: Spesifikasi Kebutuhan Fungsional (Functional Requirements)
| Kode | Deskripsi Kebutuhan Fungsional |
| :--- | :--- |
| **Autentikasi, Akun & Keamanan** | |
| FR-AUTH-01 | Sistem wajib menyediakan formulir pendaftaran akun mandiri menggunakan alamat email unik, nama lengkap, dan kata sandi minimal 8 karakter. |
| FR-AUTH-02 | Sistem wajib memvalidasi kredensial pengguna menggunakan verifikasi hash kata sandi berbasis algoritma Bcrypt (work factor 12). |
| FR-AUTH-03 | Sistem wajib secara otomatis mengalokasikan saldo awal 5 Token Gratis dan 3 kali Kuota Trial AI Chatbot/Parafrase pada TokenWallet saat akun FREE pertama kali terdaftar. |
| FR-AUTH-04 | Sistem wajib mendukung autentikasi Single Sign-On (SSO) menggunakan Google OAuth 2.0 dengan verifikasi integritas Google ID Token di sisi backend server. |
| FR-AUTH-05 | Sistem wajib menerbitkan Access Token JWT berbatas waktu 15 menit dan Refresh Token acak tersimpan pada HttpOnly Secure Cookie dengan masa berlaku 7 hari. |
| FR-AUTH-06 | Sistem wajib menerapkan mekanisme Refresh Token Rotation; setiap penggunaan token pembaruan wajib menerbitkan token baru dan menganulir token sebelumnya. |
| FR-AUTH-07 | Sistem wajib menyediakan fitur Logout yang menghapus cookie sesi di peramban dan membatalkan hash refresh token pada tabel sessions di basis data. |
| FR-AUTH-08 | Sistem wajib mengizinkan pengguna memperbarui informasi nama lengkap profil dengan validasi sanitasi teks anti-XSS. |
| FR-AUTH-09 | Sistem wajib memvalidasi kecocokan kata sandi lama sebelum mengizinkan pembaruan hash kata sandi baru dan mencabut seluruh sesi aktif lain demi keamanan akun. |
| FR-AUTH-10 | Sistem wajib menyediakan alur pemulihan kata sandi melalui pengiriman token pemulihan acak berbatas waktu 60 menit ke email pengguna terdaftar. |
| FR-AUTH-11 | Sistem wajib menegakkan pembatasan hak akses berbasis 3 peran (Role-Based Access Control: FREE, PREMIUM, ADMIN Read-Only) secara ketat pada setiap rute antarmuka dan endpoint API. |
| **Unggah, Validasi & Ekstraksi Naskah** | |
| FR-DOC-01 | Sistem wajib mendukung pengunggahan berkas digital dengan ekstensi .pdf, .docx, .txt, serta input penempelan teks langsung pada area kerja editor. |
| FR-DOC-02 | Sistem wajib membatasi ukuran fisik berkas yang diunggah maksimal 15 Megabytes (MB) dan menolak berkas yang melebihi batas tersebut. |
| FR-DOC-03 | Sistem wajib memvalidasi berkas berdasarkan magic bytes MIME-type untuk mencegah manipulasi ekstensi palsu atau serangan berkas berbahaya (executable upload). |
| FR-DOC-04 | Sistem wajib mengekstrak teks bersih dari PDF (pdfplumber) dan DOCX (python-docx), menghapus tag biner, dan menormalisasi whitespace tanpa merusak struktur paragraf asli. |
| FR-DOC-05 | Sistem wajib memecah teks dokumen menjadi array kalimat diskret dengan mencatat offset posisi karakter awal dan akhir serta menolak pemrosesan naskah dengan jumlah kata kurang dari 50 kata. |
| FR-DOC-06 | Sistem wajib membatasi panjang naskah per pemeriksaan untuk Free User maksimal 2.500 kata (setara 1 Token) dan menampilkan modal peningkatan akun jika melampaui batas. |
| FR-DOC-07 | Sistem wajib mendukung pemrosesan naskah panjang (skripsi, tesis, disertasi puluhan ribu kata) untuk akun Premium User dengan batas berkas 15 MB. |
| FR-DOC-08 | Sistem wajib menghitung jumlah kata secara real-time sebelum pemindaian dan menampilkan biaya token berdasarkan formula: min(5, ceil(kata / 2500)) Token dengan Batas Maksimum (Token Cap) 5 Token. |
| **Akuisisi Korpus Otomatis & Deteksi Plagiarisme Hybrid 3-Tahap** | |
| FR-CORP-01 | Sistem wajib memiliki layanan AutomatedCorpusHarvester yang menarik metadata, DOI, dan abstrak karya ilmiah Indonesia & global dari OpenAlex Graph API secara berkala. |
| FR-CORP-02 | Sistem wajib mengintegrasikan penarikan artikel akses terbuka dari DOAJ REST API, Semantic Scholar Academic Graph, dan Crossref API untuk memperkaya perbendaharaan korpus ilmiah. |
| FR-CORP-03 | Sistem wajib memecah dokumen korpus menjadi potongan teks (chunks) 300 kata, menghasilkan dense embeddings 384-d, dan menyimpannya di indeks graf HNSW PostgreSQL pgvector. |
| FR-CORP-04 | Sistem wajib mendukung modul WebScanner yang memanfaatkan Google Search Grounding untuk menelusuri artikel web publik dan repositori kampus (e-Prints). |
| FR-DET-01 | Sistem wajib mendelegasikan pemrosesan audit dokumen ke antrean worker Celery Redis secara asinkron setelah saldo token dipotong secara atomik. |
| FR-DET-02 | Sistem wajib mengimplementasikan Step 1 (Deteksi Leksikal Winnowing) dengan Rabin-Karp rolling hash (basis b=257, modulus prima M=1.000.000.007, k-gram=5, sliding window w=4) untuk mengekstrak sidik jari digital naskah dan mencocokkannya ke indeks korpus internal. |
| FR-DET-03 | Sistem wajib menandai kalimat dengan nilai koefisien Jaccard Containment >= 80% sebagai pelanggaran leksikal berindikator MERAH (Tier 1). |
| FR-DET-04 | Sistem wajib mengimplementasikan Step 2 (Deteksi Semantik SBERT) menghasilkan dense embedding 384 dimensi pada tiap kalimat menggunakan paraphrase-multilingual-MiniLM-L12-v2 dan menjalankan kueri KNN jarak Cosine (<=>) pada pgvector berindeks HNSW. |
| FR-DET-05 | Sistem wajib menyaring pasangan kalimat kandidat berbahasa Indonesia menggunakan re-ranker spesialis model LazarusNLP/all-indobert-base-v4 untuk mengevaluasi sinonim morfologis ilmiah. |
| FR-DET-06 | Sistem wajib menandai kalimat dengan nilai Cosine Similarity >= 75% (jarak <= 0.25) yang tidak terdeteksi pada Step 1 sebagai parafrase semantik berindikator ORANYE (Tier 2). |
| FR-DET-07 | Sistem wajib mengimplementasikan Step 3 (Evaluasi Stilometri) menghitung ritme variasi penulisan menggunakan rumus Goh & Barabasi Burstiness B dan Type-Token Ratio (TTR) untuk mendeteksi anomali sintesis model bahasa AI (LLM). |
| FR-DET-08 | Sistem wajib mengintegrasikan Contextual AI Judge (Dual-Engine LLM Gateway: Google Gemini 2.5 Flash dengan failover otomatis ke DeepSeek v4.1 Flash via 9Router) untuk menyaring false positive (kutipan resmi berizin) dan menandai kalimat anomali gaya berindikator KUNING (Tier 3). |
| FR-DET-09 | Sistem wajib menghitung skor kemiripan akhir dokumen (Overall Similarity Index) berdasarkan formula agregasi berbobot: Skor_Komposit = (0.50 * Skor_Leksikal) + (0.35 * Skor_Semantik) + (0.15 * Skor_Stilometri). |
| FR-DET-10 | Sistem wajib menyediakan endpoint pemantauan status proses audit asinkron secara real-time via mekanisme smart polling. |
| **AI Chatbot Asisten Naskah & Parafrase Instan** | |
| FR-CHAT-01 | Sistem wajib menyediakan panel AI Chatbot interaktif yang disematkan berdampingan dengan lembar Interactive Heatmap pada Split-Screen Studio Workspace. |
| FR-CHAT-02 | Sistem wajib menerapkan modul AcademicGuardrail yang secara ketat membatasi interaksi percakapan hanya pada lingkup evaluasi naskah ilmiah, perbaikan tata bahasa, parafrase akademik, dan sitasi. |
| FR-CHAT-03 | Sistem wajib menyediakan fitur parafrase cerdas dalam 3 mode pilihan: Mode Per Kalimat (Single Sentence), Mode Per Paragraf (Paragraph Block), dan Mode Seluruh Halaman (Full Page Batch). |
| FR-CHAT-04 | Sistem wajib menghasilkan 3 pilihan variasi kalimat/paragraf dengan kosakata akademik terstandar lengkap dengan estimasi prediksi penurunan persentase kemiripan. |
| FR-CHAT-05 | Sistem wajib menyediakan tombol 'Terapkan ke Naskah & Cek Ulang' yang mengganti teks kalimat di naskah secara in-place, menghitung ulang skor secara real-time, dan mengubah warna sorotan menjadi HIJAU (Telah Diperbaiki). |
| FR-CHAT-06 | Sistem wajib membatasi penggunaan AI Chatbot dan Parafrase Instan pada akun FREE maksimal 3 kali respon uji coba sebelum menampilkan modal paywall peningkatan akun. |
| FR-CHAT-07 | Sistem wajib memotong kuota akun PREMIUM dengan tarif transparan: 1 Token untuk 10 kali respon chat/parafrase per kalimat, atau 1 Token per 2 halaman penuh untuk batch paraphrase. |
| **Visualisasi, Sertifikasi PDF & Riwayat (UU PDP)** | |
| FR-REP-01 | Sistem wajib menyajikan hasil audit dalam format Interactive Heatmap pada antarmuka web yang dapat ditinjau oleh seluruh pengguna (Free maupun Premium). |
| FR-REP-02 | Sistem wajib menyajikan tampilan pembanding berdampingan (Side-by-Side Diff) antara kalimat naskah pengguna dengan teks sumber asli pembanding. |
| FR-REP-03 | Sistem wajib menyediakan tombol filter tampilan sorotan heatmap ([Semua], [Merah - Leksikal], [Oranye - Semantik], [Kuning - Gaya]) untuk mempermudah navigasi peninjauan. |
| FR-REP-04 | Sistem wajib menyediakan fitur generate dokumen Laporan Audit Resmi berformat PDF berkualitas cetak yang dilengkapi diagram skor, daftar sumber, dan stempel digital bagi Premium User. |
| FR-REP-05 | Sistem wajib menyematkan kode QR dinamis pada setiap berkas laporan PDF resmi yang mengarah ke tautan permanen verifikasi publik (/verify/{certificate_uuid}). |
| FR-REP-06 | Sistem wajib menyediakan halaman validasi publik tanpa kewajiban login untuk memverifikasi keaslian sertifikat dan menampilkan stempel digital hijau keabsahan naskah. |
| FR-REP-07 | Sistem wajib menyimpan riwayat seluruh naskah yang pernah dipindai oleh pengguna pada tabel documents dan audit_tasks dengan fitur pencarian dan filter tanggal. |
| FR-REP-08 | Sistem wajib menyediakan fitur penghapusan naskah secara permanen (hard-delete cascading) yang menghapus berkas fisik, rekaman audit, dan riwayat chat dari sistem sesuai UU PDP. |
| **Monetisasi, Token & Billing Midtrans** | |
| FR-PAY-01 | Sistem wajib mencatat saldo token komputasi pengguna pada tabel token_wallets dan mendukung pencatatan riwayat transaksi kredit/debit secara atomik. |
| FR-PAY-02 | Sistem wajib memotong saldo token saat pemeriksaan naskah berdasarkan formula: min(5, ceil(kata / 2500)) Token dengan Batas Maksimum (Token Cap) 5 Token. |
| FR-PAY-03 | Sistem wajib mendukung pembelian token satuan kustom (By Token) dengan harga dasar Rp 2.000 per token (minimal pembelian 5 Token = Rp 10.000). |
| FR-PAY-04 | Sistem wajib menyediakan 3 pilihan paket bundling diskon (By Paket Token): Paket Starter (15 Token = Rp 25.000), Paket Skripsi Pro (50 Token = Rp 65.000), dan Paket Riset Intensif (150 Token = Rp 150.000). |
| FR-PAY-05 | Sistem wajib mengintegrasikan antarmuka gerbang pembayaran Midtrans Snap API untuk memproses berbagai saluran bayar (QRIS, GoPay, ShopeePay, VA Bank Mandiri/BCA/BNI/BRI, Kartu Kredit). |
| FR-PAY-06 | Sistem wajib menerima HTTP POST notifikasi webhook Midtrans dan memvalidasi keaslian signature_key berbasis algoritma SHA-512. |
| FR-PAY-07 | Sistem wajib secara otomatis mengubah status peran pengguna dari FREE menjadi PREMIUM seketika saat notifikasi pelunasan (settlement/capture) terverifikasi. |
| FR-PAY-08 | Seluruh mutasi saldo dan pembaruan invoice wajib menggunakan transaksi terisolasi dengan penguncian baris (row-level locking SELECT ... FOR UPDATE) untuk mencegah race condition. |
| FR-PAY-09 | Sistem wajib menyediakan dokumen tanda terima pembayaran digital (invoice PDF) resmi yang dapat diunduh pengguna dari halaman penagihan. |
| **Pemantauan Layanan Admin (100% Read-Only)** | |
| FR-ADM-01 | Sistem wajib menyediakan tampilan dasbor analitik bagi Admin untuk memantau agregat total naskah diperiksa, rata-rata skor kemiripan, total revenue, dan jumlah pengguna aktif secara read-only. |
| FR-ADM-02 | Sistem wajib menyajikan tabel riwayat transaksi pembayaran Midtrans secara real-time yang mencakup order_id, metode bayar, nominal bruto, dan status transaksi secara read-only. |
| FR-ADM-03 | Sistem wajib menampilkan status kesehatan antrean tugas Celery, jumlah worker aktif, pemakaian memori Redis, dan latensi kueri pgvector secara pasif. |
| FR-ADM-04 | Sistem wajib mencatat dan menyajikan rekaman log aktivitas keamanan penting (percobaan login gagal, insiden brute-force, dan penghapusan naskah) pada tabel audit_logs.

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
Berikut adalah 11 tabel spesifikasi Use Case terperinci yang mencakup seluruh alur kerja operasional platform VeriText AI:

Tabel 4: UC-01 Masuk dan Registrasi Akun
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-01: Masuk dan Registrasi Akun |
| **Process Owner** | Modul Keamanan, Autentikasi & Sesi Pengguna (AuthService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Memfasilitasi pendaftaran akun baru secara mandiri, autentikasi masuk pengguna via email/kata sandi atau Google OAuth 2.0, alokasi kuota awal token dan trial, serta pengakhiran sesi (logout) secara aman. |
| **Overview** | Pengguna mendaftar akun baru atau masuk ke sistem menggunakan kredensial email/kata sandi maupun akun Google. Sistem menerbitkan pasangan token otentikasi JWT (Access Token 15 menit dan Refresh Token HttpOnly 7 hari), mengalokasikan otomatis 5 Token gratis dan 3x Kuota Trial AI Chatbot/Parafrase bagi akun FREE baru, serta mengamankan pengakhiran sesi saat logout. |
| **Cross Requirement** | FR-AUTH-01, FR-AUTH-02, FR-AUTH-03, FR-AUTH-04, FR-AUTH-05, FR-AUTH-06, FR-AUTH-07, FR-AUTH-11 |
| **Actor** | Free User, Premium User, Admin |
| **Preconditions** | Pengguna memiliki peramban web yang terhubung ke jaringan internet dan mengakses halaman autentikasi VeriText AI (/login atau /register); belum memiliki sesi aktif. |
| **Postconditions** | Pengguna terdaftar di tabel users (role='FREE' untuk pendaftaran baru), sesi JWT aktif diterbitkan, dompet token (token_wallets) teralokasi, atau cookie sesi dicabut saat pengguna keluar. |
| **Typical Course of Events** | 1. Pengguna membuka halaman /login atau /register.<br>2. Pengguna memilih metode autentikasi (Email & Kata Sandi atau Google OAuth 2.0).<br>3. Pengguna memasukkan nama lengkap, alamat email, dan kata sandi minimal 8 karakter.<br>4. Pengguna menekan tombol "Daftar" atau "Masuk".<br>5. Sistem memvalidasi kelayakan format input dan memeriksa status percobaan login (lockout check).<br>6. Jika registrasi baru: Sistem membuat record pengguna di tabel users dengan peran role='FREE' dan mengalokasikan saldo 5 Token gratis serta 3x Kuota Trial AI pada tabel token_wallets.<br>7. Jika login: Sistem memverifikasi hash kata sandi menggunakan algoritma Bcrypt (work factor 12).<br>8. Sistem menerbitkan Access Token JWT (masa aktif 15 menit) dan Refresh Token acak tersimpan pada HttpOnly Secure Cookie (masa aktif 7 hari).<br>9. Sistem mencatat log aktivitas pada tabel audit_logs dan mengarahkan pengguna ke Dasbor Workspace. |
| **Alternative Workflow** | A1: Masuk Cepat dengan Google OAuth 2.0:<br>1. Pengguna memilih tombol "Masuk dengan Google".<br>2. Sistem mengalihkan peramban ke Google Consent Screen.<br>3. Pengguna memilih dan menyetujui akun Google.<br>4. Google mengembalikan authorization code ke backend callback (/api/v1/auth/google).<br>5. Sistem menukar kode dengan Google ID Token, memvalidasi profil, dan melakukan upsert akun (role='FREE' jika pengguna baru).<br>6. Sistem menerbitkan sesi JWT ganda dan mengarahkan pengguna ke Dasbor Workspace. |
| **Exceptional Workflow** | E1: Kredensial Salah: Sistem mencatat percobaan gagal, mengembalikan kode HTTP 401 Unauthorized, dan menampilkan pesan: "Email atau kata sandi tidak valid."<br>E2: Akun Terkunci Sementara (Brute-Force): Jika terjadi kegagalan login 5 kali berturut-turut, sistem mengunci akun selama 15 menit dan menampilkan pesan: "Akun terkunci sementara karena 5 kali percobaan gagal berturut-turut."<br>E3: Email Sudah Digunakan: Pada alur registrasi, jika email duplikat, sistem menampilkan pesan galat: "Alamat email sudah terdaftar. Silakan login atau gunakan menu pemulihan kata sandi." |

Tabel 5: UC-02 Kelola Profil dan Kata Sandi
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-02: Kelola Profil dan Kata Sandi |
| **Process Owner** | Modul Manajemen Pengguna & Keamanan Kredensial (AuthService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Mengizinkan pengguna memperbarui biodata profil akun (nama lengkap) serta mengubah kata sandi keamanan akun. |
| **Overview** | Pengguna yang telah terautentikasi dapat memperbarui data identitas profil atau memperbarui kata sandi akun melalui validasi kata sandi lama dan penerapan enkripsi hash Bcrypt baru. |
| **Cross Requirement** | FR-AUTH-08, FR-AUTH-09, FR-AUTH-10, NFR-SEC-02 |
| **Actor** | Free User, Premium User |
| **Preconditions** | Pengguna berada dalam sesi login aktif dengan Access Token JWT yang valid. |
| **Postconditions** | Informasi biodata profil pada tabel users diperbarui, atau hash kata sandi baru diperbarui dan seluruh sesi aktif lainnya dicabut. |
| **Typical Course of Events** | 1. Pengguna membuka halaman Pengaturan Akun (/settings).<br>2. Pengguna menyunting informasi nama lengkap profil.<br>3. Pengguna menekan tombol "Simpan Perubahan Profil".<br>4. Sistem melakukan validasi sanitasi teks (anti-XSS) dan memperbarui record di basis data.<br>5. Sistem menampilkan notifikasi sukses "Profil berhasil diperbarui". |
| **Alternative Workflow** | A1: Penggantian Kata Sandi Akun:<br>1. Pengguna membuka tab "Keamanan", memasukkan kata sandi lama, kata sandi baru (minimal 8 karakter), dan konfirmasi kata sandi baru.<br>2. Pengguna menekan tombol "Perbarui Kata Sandi".<br>3. Sistem memverifikasi kecocokan hash kata sandi lama dengan Bcrypt.<br>4. Sistem melakukan hashing Bcrypt pada kata sandi baru dan menyimpan pembaruan ke tabel users.<br>5. Sistem mencabut seluruh refresh token aktif lainnya di tabel sessions demi keamanan.<br>6. Sistem menampilkan notifikasi sukses "Kata sandi berhasil diperbarui".<br>A2: Alur Pemulihan Lupa Kata Sandi:<br>1. Pengguna membuka menu "Lupa Kata Sandi", memasukkan email terdaftar, dan menekan "Kirim Tautan Reset".<br>2. Sistem membangkitkan token pemulihan acak berbatas waktu 60 menit dan mengirimkan tautan reset ke email pengguna.<br>3. Pengguna membuka tautan email, memasukkan kata sandi baru, dan sistem memperbarui kredensial akun. |
| **Exceptional Workflow** | E1: Kata Sandi Lama Salah: Sistem menolak pembaruan kata sandi dan menampilkan pesan galat: "Kata sandi lama tidak cocok."<br>E2: Kata Sandi Baru Lemah: Jika kata sandi baru kurang dari 8 karakter, sistem menampilkan: "Kata sandi minimal 8 karakter dengan kombinasi huruf dan angka." |

Tabel 6: UC-03 Unggah dan Validasi Naskah
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-03: Unggah dan Validasi Naskah |
| **Process Owner** | Modul Unggah Dokumen & Mesin Pra-pemrosesan Teks (PreprocessorEngine) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Menerima berkas naskah (.pdf, .docx, .txt) atau input teks langsung, memvalidasi integritas berkas, mengekstrak teks bersih, menghitung jumlah kata, dan menampilkan kalkulator biaya token. |
| **Overview** | Pengguna mengunggah naskah melalui dropzone atau menempelkan teks. Sistem memeriksa format biner (magic bytes), batasan ukuran (maksimal 15 MB), batasan kata akun Free (maksimal 2.500 kata), serta menghitung estimasi biaya token berdasarkan formula proporsional dengan batasan maksimum (Token Cap) 5 Token. |
| **Cross Requirement** | FR-DOC-01, FR-DOC-02, FR-DOC-03, FR-DOC-04, FR-DOC-05, FR-DOC-06, FR-DOC-07, FR-DOC-08, FR-PAY-02 |
| **Actor** | Free User, Premium User |
| **Preconditions** | Pengguna telah masuk ke sistem dan berada di Dasbor Workspace (/workspace). |
| **Postconditions** | Berkas tersimpan di storage terisolasi dengan nama acak UUIDv4, record metadata dokumen tersimpan di tabel documents, dan rincian estimasi biaya token ditampilkan. |
| **Typical Course of Events** | 1. Pengguna membuka halaman Dasbor Workspace.<br>2. Pengguna memilih metode input naskah (unggah berkas atau penempelan teks langsung).<br>3. Pengguna menyeret/memilih berkas (.pdf, .docx, .txt) maksimal 15 MB atau menempelkan teks.<br>4. Sistem memeriksa magic bytes MIME type untuk mencegah pengunggahan skrip berbahaya.<br>5. Sistem mengekstrak teks murni menggunakan pdfplumber atau python-docx dan membersihkan noise karakter.<br>6. Sistem memecah teks menjadi array kalimat diskret dengan mencatat offset posisi karakter awal dan akhir.<br>7. Sistem menghitung total kata naskah (word_count).<br>8. Sistem mengevaluasi batasan akun: Jika pengguna berstatus Free User, total kata diverifikasi <= 2.500 kata.<br>9. Sistem menghitung estimasi biaya token menggunakan formula: Biaya = min(5, ceil(kata / 2500)) Token.<br>10. Sistem menampilkan ringkasan naskah, jumlah kata, dan konfirmasi biaya token pada antarmuka sebelum pemindaian dimulai. |
| **Alternative Workflow** | A1: Penempelan Teks Langsung (Direct Paste): Pengguna menempelkan teks langsung ke area editor teks. Sistem langsung mengeksekusi penghitungan kata real-time dan kalkulasi biaya token tanpa ekstraksi biner. |
| **Exceptional Workflow** | E1: Ukuran Berkas Melebihi Batas: Jika berkas > 15 MB, sistem menolak berkas dengan pesan: "Ukuran berkas melebihi batas maksimum 15 MB."<br>E2: Ekstensi Tidak Didukung / Magic Byte Rusak: Sistem menampilkan galat: "Format berkas tidak didukung atau berkas rusak. Hanya menerima berkas .pdf, .docx, dan .txt."<br>E3: Jumlah Kata Kurang dari 50 Kata: Sistem menolak pemrosesan naskah dengan pesan: "Naskah terlalu pendek (minimal 50 kata untuk analisis ilmiah)."<br>E4: Pelanggaran Batas Kata Free User (> 2.500 Kata): Sistem menampilkan modal paywall: "Naskah Anda terdiri dari X kata. Batas akun Free User adalah 2.500 kata per dokumen. Silakan upgrade ke Premium User untuk memindai naskah panjang (skripsi/tesis)." |

Tabel 7: UC-04 Deteksi Plagiarisme Hybrid 3-Tahap
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-04: Deteksi Plagiarisme Hybrid 3-Tahap |
| **Process Owner** | Mesin Audit Deteksi Plagiarisme Hybrid (HybridAuditOrchestrator) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Mengeksekusi pipa deteksi plagiarisme 3-tahap (Leksikal Winnowing, Semantik SBERT & IndoBERT, Stilometri & AI Judge) secara asinkron melalui antrean Celery Redis setelah saldo token dipotong secara atomik. |
| **Overview** | Pengguna mengonfirmasi pemeriksaan naskah. Sistem memotong saldo token pengguna secara atomik di dalam transaksi basis data, lalu mendaftarkan tugas ke antrean Celery Redis. Tiga tahap audit dijalankan secara bertingkat untuk mendeteksi penjiplakan leksikal, semantik/parafrase, dan anomali gaya tulisan AI, hingga skor komposit akhir terhitung. |
| **Cross Requirement** | FR-CORP-01, FR-CORP-02, FR-CORP-03, FR-CORP-04, FR-DET-01, FR-DET-02, FR-DET-03, FR-DET-04, FR-DET-05, FR-DET-06, FR-DET-07, FR-DET-08, FR-DET-09, FR-DET-10, FR-PAY-01, FR-PAY-02 |
| **Actor** | Free User, Premium User |
| **Preconditions** | Naskah telah divalidasi (UC-03) dan saldo token pengguna di tabel token_wallets mencukupi estimasi biaya pemeriksaan. |
| **Postconditions** | Status audit COMPLETED di tabel audit_tasks, seluruh kalimat naskah tersimpan dengan label indikator warna pada tabel audit_sentences, dan skor komposit tersimpan di tabel audit_reports. |
| **Typical Course of Events** | 1. Pengguna menekan tombol "Mulai Periksa Naskah".<br>2. Sistem membuka transaksi atomik dengan row-level lock (SELECT ... FOR UPDATE) pada tabel token_wallets untuk memotong saldo token sesuai biaya audit.<br>3. Sistem mendaftarkan tugas audit ke antrean Celery Redis dengan status QUEUED.<br>4. Worker Celery mengambil tugas dan mengubah status menjadi PROCESSING.<br>5. Worker mengeksekusi Step 1 (Deteksi Leksikal Winnowing): Menghitung Rabin-Karp rolling hash (k-gram=5, window=4), mencocokkan sidik jari terhadap indeks korpus, dan menandai kalimat dengan Jaccard Containment >= 80% sebagai pelanggaran leksikal (MERAH).<br>6. Worker mengeksekusi Step 2 (Deteksi Semantik SBERT & IndoBERT): Meng-generate dense embeddings 384-d menggunakan paraphrase-multilingual-MiniLM-L12-v2, menjalankan kueri KNN jarak Cosine (<=>) pada pgvector berindeks HNSW, menyaring kandidat Indonesia dengan LazarusNLP/all-indobert-base-v4, dan menandai kalimat dengan Cosine Similarity >= 75% sebagai parafrase (ORANYE).<br>7. Worker mengeksekusi Step 3 (Stilometri & Contextual AI Judge): Menghitung Goh & Barabasi Burstiness B dan TTR, mengevaluasi kutipan resmi berizin melalui Google Gemini 2.5 Flash, dan menandai anomali gaya tulisan buatan AI (KUNING).<br>8. Worker mengagregasi skor komposit berbobot: Skor_Komposit = 0.50 Leksikal + 0.35 Semantik + 0.15 Stilometri.<br>9. Worker memperbarui status audit menjadi COMPLETED pada tabel audit_tasks dan audit_reports.<br>10. Frontend Vue 3 mendeteksi status COMPLETED melalui mekanisme smart polling dan otomatis memuat hasil analisis ke Split-Screen Studio Workspace. |
| **Alternative Workflow** | A1: Penghentian Dini pada Pelanggaran Berat: Jika hasil pemindaian Step 1 menemukan kemiripan leksikal verbatim > 95% pada seluruh dokumen, sistem menandai dokumen sebagai copy-paste masif dan mempercepat komputasi tahap berikutnya. |
| **Exceptional Workflow** | E1: Saldo Token Tidak Mencukupi: Sistem membatalkan inisiasi audit, mengembalikan kode HTTP 402 Payment Required, dan menampilkan modal penawaran top-up token.<br>E2: Kegagalan Worker Komputasi (Task Failure): Celery mencoba ulang tugas hingga 3 kali; jika tetap gagal total, sistem membatalkan tugas, mencatat log galat, dan mengeksekusi refund saldo token secara atomik ke akun pengguna. |

Tabel 8: UC-05 Tinjau Laporan dan Heatmap Kemiripan
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-05: Tinjau Laporan dan Heatmap Kemiripan |
| **Process Owner** | Modul Visualisasi Laporan & Heatmap Viewer (ReportGeneratorService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Menyajikan naskah interaktif ber-Interactive Heatmap pada Split-Screen Studio Workspace, menampilkan kartu rincian sumber kecocokan, dan perbandingan teks berdampingan (side-by-side diff). |
| **Overview** | Pengguna menelaah hasil pemeriksaan naskah pada tata letak Split-Screen Studio Workspace. Kolom kiri menyajikan lembar naskah dengan penyorotan warna semantik 3-tier, sedangkan kolom kanan menyajikan panel daftar sumber kecocokan beranotasi DOI ilmiah dan komparasi berdampingan. |
| **Cross Requirement** | FR-REP-01, FR-REP-02, FR-REP-03 |
| **Actor** | Free User, Premium User |
| **Preconditions** | Pemeriksaan naskah telah selesai berstatus COMPLETED (UC-04). |
| **Postconditions** | Pengguna memperoleh wawasan visual terperinci mengenai sebaran plagiarisme, tingkat keparahan indikasi, dan rujukan dokumen sumber asli. |
| **Typical Course of Events** | 1. Pengguna membuka tampilan hasil analisis naskah (/workspace/report/{id}).<br>2. Sistem menyajikan antarmuka Split-Screen Studio Workspace:<br>   - Top Summary Bar: Judul dokumen, jumlah kata, skor komposit total dalam badge tegas, dan persentase rincian 3-tier.<br>   - Kolom Kiri (60%): Interactive Heatmap Viewer menampilkan naskah dengan sorotan warna semantik (Merah = Leksikal >= 80%, Oranye = Semantik >= 75%, Kuning = Stilometri/AI).<br>   - Kolom Kanan (40%): Panel Tab 1 "Sumber Kecocokan" menampilkan kartu sumber terurut berdasarkan persentase kontribusi kemiripan lengkap dengan tautan DOI resmi.<br>3. Pengguna dapat mengklik tombol filter sorotan ([Semua], [Merah], [Oranye], [Kuning]).<br>4. Pengguna mengklik salah satu kalimat bermasalah pada lembar naskah.<br>5. Sistem menampilkan popover aksi cepat dan menampilkan jendela perbandingan teks berdampingan (Side-by-Side Diff) antara teks naskah dan teks dokumen sumber asli. |
| **Alternative Workflow** | A1: Pengguna Mengklik Opsi Parafrase dari Popover: Pengguna memilih tombol [Parafrase Kalimat Ini] pada popover; sistem otomatis mengalihkan fokus ke Tab 2 (AI Chatbot & Parafrase) dengan konteks kalimat terpilih (UC-07). |
| **Exceptional Workflow** | E1: Laporan Tidak Ditemukan: Jika ID laporan tidak valid atau naskah telah dihapus, sistem mengembalikan kode HTTP 404 Not Found dan menampilkan pesan: "Laporan pemeriksaan tidak ditemukan atau telah dihapus." |

Tabel 9: UC-06 Konsultasi Naskah via AI Chatbot
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-06: Konsultasi Naskah via AI Chatbot |
| **Process Owner** | Modul AI Chatbot Asisten Naskah (AcademicAssistantService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Memfasilitasi diskusi interaktif antara pengguna dan AI Asisten Akademik di panel Split-Screen Studio Workspace mengenai evaluasi naskah, kaidah penulisan ilmiah, perbaikan tata bahasa, dan sitasi. |
| **Overview** | Pengguna berkonsultasi mengenai kalimat bermasalah dengan AI Asisten. Sistem menerapkan Academic Guardrail secara ketat untuk membatasi ruang lingkup tanya-jawab hanya pada ranah akademik, memotong kuota trial (Free User) atau sub-kredit token (Premium User), dan menyajikan respons bimbingan terstruktur. |
| **Cross Requirement** | FR-CHAT-01, FR-CHAT-02, FR-CHAT-06, FR-CHAT-07, NFR-SEC-12 |
| **Actor** | Free User (Trial 3x), Premium User (Token) |
| **Preconditions** | Pengguna berada di Split-Screen Studio Workspace dan memiliki kuota chat aktif (ai_trial_remaining > 0 untuk Free User, atau saldo token mencukupi untuk Premium User). |
| **Postconditions** | Pertanyaan dan respon AI tersimpan di tabel chat_messages, serta kuota trial atau sub-kredit token terpotong secara transparan. |
| **Typical Course of Events** | 1. Pengguna membuka Tab 2 "AI Asisten" pada panel kanan Split-Screen Studio Workspace.<br>2. Pengguna mengetikkan pertanyaan konsultasi atau memilih tombol prompt cepat ([Perhalus Paragraf], [Ubah ke Kalimat Pasif], [Jelaskan Alasan Plagiat]).<br>3. Sistem memeriksa hak akses kuota: Free User diverifikasi ai_trial_remaining > 0; Premium User diverifikasi memiliki saldo token.<br>4. Modul AcademicGuardrail menganalisis teks prompt masukan untuk mendeteksi upaya manipulasi (jailbreak/prompt injection) dan memastikan pertanyaan relevan dengan etika ilmiah.<br>5. Sistem menyusun konteks naskah beserta riwayat obrolan dan mengirimkan payload ke Google Gemini 2.5 Flash API.<br>6. Gemini API mengembalikan jawaban bimbingan penulisan ilmiah terstruktur.<br>7. Sistem memotong 1 kuota trial (Free User) atau sub-kredit token (Premium User: 1 Token / 10 respons).<br>8. Sistem menyajikan respons di gelembung obrolan dan menyimpan rekaman ke tabel chat_messages. |
| **Alternative Workflow** | A1: Pengalihan ke Penyedia Fallback: Jika API Gemini mengalami gangguan sementara atau batas laju (HTTP 429), Dual-Engine LLM Gateway secara otomatis beralih ke DeepSeek v4.1 Flash (via 9Router) untuk menyajikan respon tanpa interupsi bagi pengguna. |
| **Exceptional Workflow** | E1: Kuota Trial Free User Telah Habis: Jika sisa kuota trial = 0, sistem mengunci area input obrolan dan menampilkan modal paywall: "Batas 3 kali uji coba AI Asisten telah habis. Silakan beli paket token untuk menikmati akses tanpa batas sebagai Premium User."<br>E2: Pelanggaran Academic Guardrail: Jika pengguna mengajukan pertanyaan non-akademik (misal: meminta lelucon, skrip kode jahat, atau topik di luar naskah), sistem menolak permintaan dan mengembalikan respon: "AI Asisten VeriText hanya melayani konsultasi naskah ilmiah, tata bahasa, dan perbaikan sitasi akademik." |

Tabel 10: UC-07 Parafrase Instan dan Cek Ulang Kalimat
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-07: Parafrase Instan dan Cek Ulang Kalimat |
| **Process Owner** | Modul Parafrase Instan & Re-Scoring Engine (AcademicAssistantService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Menghasilkan 3 opsi variasi parafrase ilmiah berstandar akademik dalam 3 mode pilihan (Per Kalimat, Per Paragraf, Seluruh Halaman) dan menerapkan variasi terpilih langsung ke naskah dengan penghitungan ulang skor secara real-time. |
| **Overview** | Pengguna memilih segmen teks naskah yang berindikasi plagiat pada heatmap. Sistem mengaktifkan AI Paraphrase Engine untuk menghasilkan 3 opsi kalimat akademik alternatif lengkap dengan prediksi penurunan skor kemiripan. Pengguna memilih opsi terbaik dan menerapkannya ke naskah (in-place replacement), memicu kalkulasi ulang skor secara instan dan memperbarui warna sorotan menjadi Hijau (Telah Diperbaiki). |
| **Cross Requirement** | FR-CHAT-03, FR-CHAT-04, FR-CHAT-05, FR-CHAT-06, FR-CHAT-07 |
| **Actor** | Free User (Trial 3x), Premium User (Token) |
| **Preconditions** | Kalimat/segmen bermasalah dipilih pada heatmap naskah dan kuota parafrase mencukupi. |
| **Postconditions** | Teks kalimat pada tabel audit_sentences diperbarui secara in-place, skor kemiripan segmen dan komposit naskah turun, dan warna sorotan kalimat pada heatmap berubah menjadi Hijau. |
| **Typical Course of Events** | 1. Pengguna memilih segmen teks pada Interactive Heatmap dan memilih mode parafrase (Mode Per Kalimat, Per Paragraf, atau Seluruh Halaman Sekaligus).<br>2. Pengguna mengklik tombol "Parafrase Sekarang".<br>3. Sistem memeriksa ketersediaan kuota (Trial untuk Free User, Saldo Token untuk Premium User).<br>4. Sistem mengirimkan teks ke mesin parafrase Gemini 2.5 Flash dengan instruksi restrukturisasi kalimat pasif-aktif dan substitusi sinonim ilmiah.<br>5. Sistem menyajikan 3 kartu opsi variasi parafrase lengkap dengan perkiraan penurunan skor (misal: "Turun dari 88% menjadi 12%").<br>6. Pengguna memilih salah satu variasi terbaik dan mengklik tombol "Terapkan ke Naskah & Cek Ulang In-Place".<br>7. Sistem mengganti teks kalimat di naskah secara in-place pada tabel audit_sentences.<br>8. Sistem mengeksekusi penghitungan ulang skor kemiripan segmen dan memperbarui skor komposit total naskah secara real-time.<br>9. Antarmuka heatmap pada layar peramban langsung diperbarui: warna sorotan kalimat berubah menjadi HIJAU (Telah Diperbaiki) dan badge skor total di Top Summary Bar berkurang seketika. |
| **Alternative Workflow** | A1: Pengguna Menyalin Variasi ke Clipboard: Pengguna memilih tombol "Salin Teks" pada salah satu opsi variasi untuk menyalin kalimat ke clipboard tanpa langsung mengubah teks di naskah. |
| **Exceptional Workflow** | E1: Kuota Habis: Sistem mengunci tombol parafrase dan memunculkan modal penawaran paket token Midtrans.<br>E2: Segmen Teks Kosong: Jika pengguna memicu aksi tanpa memilih teks valid, sistem menampilkan peringatan: "Silakan pilih kalimat atau paragraf yang hendak diparafrase." |

Tabel 11: UC-08 Unduh Laporan PDF dan Verifikasi QR
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-08: Unduh Laporan PDF dan Verifikasi QR |
| **Process Owner** | Modul Pelaporan, Sertifikasi & Verifikasi Integritas Publik (ReportGeneratorService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Menerbitkan dan mengunduh berkas Laporan Audit Resmi berformat PDF beresolusi tinggi lengkap dengan segel digital dan kode QR dinamis bagi Premium User, serta memfasilitasi verifikasi keaslian laporan secara publik tanpa kewajiban login. |
| **Overview** | Pengguna Premium dapat mengunduh dokumen PDF laporan resmi yang mencakup ringkasan eksekutif, grafik skor komposit 3-tier, daftar sumber referensi dengan DOI, dan stempel digital ber-QR Code. Pihak ketiga (dosen, penguji, mitra) dapat memindai QR Code untuk memvalidasi keaslian dokumen secara instan di portal verifikasi publik. |
| **Cross Requirement** | FR-REP-04, FR-REP-05, FR-REP-06 |
| **Actor** | Premium User (Unduh PDF), Free User / Publik (Verifikasi QR) |
| **Preconditions** | Pemeriksaan naskah telah selesai berstatus COMPLETED (UC-04). |
| **Postconditions** | Berkas PDF resmi terunduh ke perangkat lokal, atau status keabsahan sertifikat disajikan pada halaman verifikasi publik. |
| **Typical Course of Events** | Skenario Unduh Laporan PDF Resmi (Premium User):<br>1. Pengguna Premium menekan tombol "Unduh Laporan PDF Resmi" pada Top Summary Bar.<br>2. Sistem memverifikasi peran pengguna (role == 'PREMIUM').<br>3. Sistem mengompilasi metadata dokumen, skor komposit, rincian per tier, daftar sumber, dan visualisasi anotasi naskah.<br>4. Sistem membangkitkan Dynamic QR Code yang mengarah ke URL publik permanen: https://veritext.ai/verify/{certificate_uuid}.<br>5. Engine WeasyPrint merender HTML/CSS akademik menjadi berkas PDF berkualitas cetak dengan stempel digital resmi.<br>6. Sistem menyajikan berkas PDF ke peramban pengguna untuk diunduh.<br><br>Skenario Verifikasi Integritas Publik (Dosen / Penguji / Pihak Ketiga):<br>1. Pihak ketiga memindai kode QR dari berkas cetak atau membuka tautan https://veritext.ai/verify/{certificate_uuid}.<br>2. Sistem memvalidasi UUID sertifikat pada basis data tabel audit_reports tanpa kewajiban autentikasi login.<br>3. Sistem menyajikan halaman validasi resmi dengan stempel hijau keabsahan naskah, nama dokumen, tanggal audit, dan persentase skor resmi. |
| **Alternative Workflow** | A1: Pengunduhan Ulang Riwayat: Pengguna Premium dapat mengunduh kembali berkas PDF laporan kapan saja dari halaman Riwayat Dokumen (/history). |
| **Exceptional Workflow** | E1: Free User Mencoba Mengunduh PDF: Jika akun Free User menekan tombol unduh PDF, sistem mengembalikan kode HTTP 403 Forbidden dan memunculkan modal paywall: "Pengunduhan Laporan PDF Resmi berstempel digital dan sertifikat QR merupakan fitur eksklusif Premium User. Silakan beli paket token untuk upgrade akun Anda."<br>E2: QR Code Palsu / Sertifikat Telah Dihapus: Jika certificate_uuid tidak ditemukan di database, portal menampilkan stempel merah: "Sertifikat Tidak Ditemukan atau Naskah Telah Dihapus Permanen oleh Pemilik Data (Kepatuhan UU PDP)." |

Tabel 12: UC-09 Kelola dan Hapus Riwayat Naskah (UU PDP)
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-09: Kelola dan Hapus Riwayat Naskah (Kepatuhan UU PDP) |
| **Process Owner** | Modul Manajemen Riwayat Dokumen & Kepatuhan Privasi (ReportGeneratorService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Memfasilitasi peninjauan riwayat seluruh naskah yang pernah diperiksa dan memberikan hak penghapusan naskah secara permanen (hard-delete cascading) bagi pengguna sesuai amanat UU Perlindungan Data Pribadi. |
| **Overview** | Pengguna dapat melihat daftar seluruh pemeriksaan naskah terdahulu, mencari berdasarkan judul, dan memfilter berdasarkan tanggal. Pengguna memiliki kendali mutlak untuk menghapus naskah secara permanen dari server; sistem mengeksekusi penghapusan berantai (cascade) atas berkas fisik, rekaman naskah, larik kalimat, laporan audit, dan riwayat chat. |
| **Cross Requirement** | FR-REP-07, FR-REP-08, NFR-COMP-01, NFR-COMP-02, NFR-COMP-03 |
| **Actor** | Free User, Premium User |
| **Preconditions** | Pengguna telah masuk ke sistem dan memiliki riwayat pemeriksaan naskah. |
| **Postconditions** | Berkas fisik naskah, rekaman tabel documents, audit_tasks, audit_sentences, audit_reports, chat_sessions, dan chat_messages terhapus permanen dari sistem. |
| **Typical Course of Events** | 1. Pengguna membuka halaman "Riwayat Naskah" (/history).<br>2. Sistem menyajikan tabel riwayat pemeriksaan (judul naskah, waktu audit, persentase skor kemiripan, jumlah kata, status).<br>3. Pengguna memilih salah satu dokumen dan menekan tombol "Hapus Permanen".<br>4. Sistem menampilkan dialog modal konfirmasi bahaya penghapusan data permanen sesuai UU PDP No. 27/2022.<br>5. Pengguna mengetikkan konfirmasi persetujuan penghapusan.<br>6. Sistem memverifikasi bahwa user_id pemohon cocok dengan pemilik sah dokumen.<br>7. Sistem mengeksekusi hard-delete cascade di dalam transaksi basis data: menghapus berkas naskah dari storage fisik, menghapus record dari tabel documents, audit_tasks, audit_sentences, audit_reports, chat_sessions, dan chat_messages.<br>8. Sistem mencatat log insiden penghapusan pada tabel audit_logs untuk kebutuhan kepatuhan hukum.<br>9. Sistem memperbarui tabel riwayat di layar pengguna dan menampilkan notifikasi sukses: "Dokumen dan seluruh data terkait telah dihapus permanen dari sistem." |
| **Alternative Workflow** | A1: Pembatalan Penghapusan: Pengguna menekan tombol "Batal" pada dialog modal; sistem menutup dialog tanpa memutasi data apapun. |
| **Exceptional Workflow** | E1: Percobaan Akses Tidak Sah: Jika pemohon bukan pemilik sah dokumen, sistem menolak eksekusi dengan kode HTTP 403 Forbidden dan mencatat peringatan keamanan pada audit_logs. |

Tabel 13: UC-10 Beli Kuota Token dan Upgrade Premium
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-10: Beli Kuota Token dan Upgrade Premium |
| **Process Owner** | Modul Billing, Dompet Kuota & Integrasi Midtrans (BillingService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Memfasilitasi pembelian saldo token komputasi melalui Midtrans Snap API (skema By Token satuan atau By Paket Token diskon) dengan verifikasi notifikasi webhook SHA-512 yang secara instan menambah saldo dompet dan menaikkan status peran akun menjadi Premium User. |
| **Overview** | Pengguna memilih jumlah token custom atau paket bundling diskon pada halaman billing. Backend membuat transaksi ke Midtrans Snap API dan menyajikan modal pembayaran (QRIS, GoPay, ShopeePay, VA Bank, Kartu Kredit). Saat pembayaran lunas, webhook Midtrans mengirimkan notifikasi settlement; sistem memverifikasi signature SHA-512, menambah saldo token di dalam transaksi atomik, mengubah peran akun menjadi PREMIUM, dan menerbitkan invoice resmi. |
| **Cross Requirement** | FR-PAY-01, FR-PAY-03, FR-PAY-04, FR-PAY-05, FR-PAY-06, FR-PAY-07, FR-PAY-08, FR-PAY-09, NFR-SEC-03 |
| **Actor** | Free User, Premium User |
| **Preconditions** | Pengguna telah masuk ke sistem dan berada di halaman Pembelian Kuota (/billing). |
| **Postconditions** | Saldo tabel token_wallets bertambah, peran pengguna pada tabel users berubah menjadi 'PREMIUM', status invoice menjadi 'SETTLEMENT', dan dokumen invoice PDF tersedia. |
| **Typical Course of Events** | 1. Pengguna membuka halaman Pembelian Kuota (/billing).<br>2. Pengguna memilih salah satu dari 2 skema pembelian:<br>   - Skema A (By Token): Memasukkan jumlah token custom (harga dasar Rp 2.000/token, minimal 5 token = Rp 10.000).<br>   - Skema B (By Paket Token): Memilih paket bundling hemat: Starter (15 Token = Rp 25.000), Skripsi Pro (50 Token = Rp 65.000), atau Riset Intensif (150 Token = Rp 150.000).<br>3. Pengguna menekan tombol "Beli Sekarang".<br>4. Backend memvalidasi parameter masukan, membuat record invoice berstatus PENDING di tabel invoices, dan meminta Snap Token ke Midtrans API.<br>5. Sistem menyajikan modal sematan Midtrans Snap di layar peramban pengguna.<br>6. Pengguna memilih metode pembayaran (QRIS, e-Wallet GoPay/ShopeePay, Virtual Account Bank Mandiri/BCA/BNI/BRI, atau Kartu Kredit) dan menyelesaikan pelunasan.<br>7. Server Midtrans mengirimkan HTTP POST notifikasi webhook ke endpoint /api/v1/billing/webhook.<br>8. Backend mengekstrak order_id, status_code, gross_amount, dan signature_key, lalu memvalidasi signature menggunakan formula SHA-512.<br>9. Di dalam transaksi basis data atomik dengan row-level lock (SELECT ... FOR UPDATE): sistem memastikan status invoice belum SETTLEMENT, memperbarui status menjadi SETTLEMENT, menambah saldo token di tabel token_wallets, dan mengubah status peran pengguna menjadi 'PREMIUM' (user.role = 'PREMIUM').<br>10. Frontend mendeteksi status sukses via smart polling / pop-up callback, menampilkan badge status "PREMIUM USER", memperbarui widget saldo token, dan menyajikan tautan unduh Invoice PDF. |
| **Alternative Workflow** | A1: Pengunduhan Tanda Terima (Invoice PDF): Pengguna menekan tombol "Unduh Invoice" pada riwayat transaksi; sistem menerbitkan berkas PDF bukti pembayaran resmi. |
| **Exceptional Workflow** | E1: Signature Webhook Tidak Cocok (Untrusted Payload): Sistem menolak notifikasi dengan kode HTTP 403 Forbidden, membatalkan mutasi saldo, dan mencatat peringatan keamanan pada audit_logs.<br>E2: Pembayaran Kedaluwarsa / Dibatalkan: Jika pengguna membatalkan transaksi atau batas waktu bayar habis, status invoice diperbarui menjadi EXPIRE / CANCEL tanpa perubahan saldo. |

Tabel 14: UC-11 Pantau Dasbor Analitik dan Log Transaksi (Admin 100% Read-Only)
| Field | Nilai / Penjelasan |
| :--- | :--- |
| **Use Case ID & Name** | UC-11: Pantau Dasbor Analitik dan Log Transaksi (Admin 100% Read-Only) |
| **Process Owner** | Modul Monitoring Layanan & Audit Keamanan (AdminMonitoringService) |
| **Date Created** | 24 Juni 2026 |
| **Purpose** | Menyajikan dasbor analitik metrik global, grafik tren skor plagiarisme, log transaksi keuangan Midtrans, telemetri beban infrastruktur antrean Celery worker, dan log audit keamanan bagi Administrator secara 100% Read-Only tanpa intervensi data pengguna. |
| **Overview** | Administrator yang memiliki hak akses role == 'ADMIN' memantau indikator kesehatan dan pertumbuhan operasional platform secara terpusat. Seluruh antarmuka admin bersifat pasif (murni GET / pembacaan data agregat) tanpa tombol atau fungsi untuk mengubah data pengguna, memutasi saldo, atau mengintip berkas naskah privat demi menjaga kepatuhan privasi UU PDP. |
| **Cross Requirement** | FR-ADM-01, FR-ADM-02, FR-ADM-03, FR-ADM-04, NFR-COMP-03 |
| **Actor** | Admin (Read-Only) |
| **Preconditions** | Administrator telah masuk ke sistem menggunakan akun berstatus peran role == 'ADMIN'. |
| **Postconditions** | Administrator memperoleh wawasan komprehensif mengenai stabilitas operasional, utilisasi komputasi, dan kesehatan finansial sistem secara real-time. |
| **Typical Course of Events** | 1. Administrator membuka halaman Dasbor Admin (/admin).<br>2. Sistem memvalidasi token JWT dan memastikan peran pengguna adalah role == 'ADMIN'.<br>3. Sistem mengeksekusi kueri agregasi pembacaan (SELECT) pada basis data:<br>   - Menghitung total naskah yang dipindai, rata-rata skor kemiripan komposit, total pendapatan sistem (revenue), dan jumlah pengguna aktif.<br>   - Menghasilkan data grafik tren pemindaian dokumen harian dan sebaran distribusi skor kemiripan multi-tier.<br>4. Administrator membuka tab "Transaksi Keuangan" untuk memantau daftar 50 transaksi pembayaran Midtrans terakhir beserta nomor order, nominal, dan status settlement secara read-only.<br>5. Administrator membuka tab "Telemetri Server" untuk mengamati status kesehatan antrean worker Celery, pemakaian memori Redis, dan latensi kueri pgvector.<br>6. Administrator membuka tab "Audit Log Keamanan" untuk meninjau rekaman aktivitas login gagal, percobaan brute-force, dan peristiwa penghapusan naskah.<br>7. Seluruh interaksi berlangsung 100% Read-Only tanpa adanya formulir atau tombol mutasi data pengguna. |
| **Alternative Workflow** | A1: Ekspor Ringkasan Metrik Agregat: Administrator dapat mengunduh laporan ringkasan analitik statistik sistem bulanan dalam format CSV/PDF agregat tanpa data pribadi pengguna. |
| **Exceptional Workflow** | E1: Percobaan Akses oleh Non-Admin (Free / Premium): Jika pengguna berstatus role != 'ADMIN' mencoba mengakses rute /admin atau endpoint /api/v1/admin/*, sistem menolak permintaan dengan kode HTTP 403 Forbidden dan mencatat insiden keamanan pada audit_logs. |

---

5. Kebutuhan Non-Fungsional (Non-Functional Requirements)
Kebutuhan non-fungsional mendefinisikan batasan kualitas, kriteria performa teknis, standar keamanan tingkat tinggi, serta kepatuhan hukum privasi yang wajib dipenuhi oleh sistem VeriText AI. Kebutuhan ini dirinci ke dalam format 2 kolom terstruktur berdasarkan 6 dimensi kualitas ISO/IEC 25010 pada tabel berikut:

Tabel 15: Spesifikasi Kebutuhan Non-Fungsional (Non-Functional Requirements)
| Kode | Deskripsi Kebutuhan Non-Fungsional |
| :--- | :--- |
| **Kebutuhan Performa & Latensi (Performance)** | |
| NFR-PERF-01 | Sebanyak 95% dari seluruh permintaan endpoint RESTful API standar (autentikasi, manajemen profil, riwayat naskah, dan transaksi billing) wajib mengembalikan respons dengan latensi kurang dari 200 milidetik pada beban operasi normal. |
| NFR-PERF-02 | Tahap 1 deteksi leksikal berbasis algoritma Winnowing dan Rabin-Karp rolling hash wajib menyelesaikan pemindaian naskah 2.500 kata dalam waktu kurang dari atau sama dengan 1,5 detik. |
| NFR-PERF-03 | Kueri penelusuran tetangga terdekat (Approximate Nearest Neighbor) pada indeks graf HNSW PostgreSQL pgvector dengan operator jarak kosinus (<=>) wajib menghasilkan luaran dalam waktu kurang dari 100 milidetik per batch kalimat. |
| NFR-PERF-04 | Respon konsultasi AI Chatbot Asisten Naskah dan pembuatan 3 variasi parafrase instan via Google Gemini 2.5 Flash API wajib disajikan dalam waktu kurang dari atau sama dengan 5,0 detik. |
| NFR-PERF-05 | Arsitektur antrean tugas terdistribusi Celery pada infrastruktur server minimum wajib mampu mengorkestrasikan minimal 10 tugas audit dokumen secara simultan (concurrent tasks) tanpa degradasi antrean atau kebocoran memori (Memory Leak). |
| **Kebutuhan Keamanan & Integritas (Security)** | |
| NFR-SEC-01 | Seluruh komunikasi transmisi data klien-server wajib menggunakan protokol enkripsi TLS 1.3 dengan cipher suite modern dan konfigurasi HSTS (HTTP Strict Transport Security). |
| NFR-SEC-02 | Kata sandi akun pengguna wajib disimpan dalam bentuk hash searah menggunakan algoritma Bcrypt dengan cost factor minimal 12 dan salt unik per record. |
| NFR-SEC-03 | Endpoint webhook pembayaran Midtrans wajib memvalidasi kecocokan tanda tangan kriptografi SHA-512 (signature_key) sebelum mengeksekusi penambahan saldo token atau kenaikan peran akun. |
| NFR-SEC-04 | Refresh token wajib dikirimkan dalam cookie dengan atribut HttpOnly, Secure, dan SameSite=Lax untuk mencegah serangan pencurian sesi melalui Cross-Site Scripting (XSS). |
| NFR-SEC-05 | Access Token JWT wajib dikonfigurasi dengan masa kedaluwarsa maksimal 15 menit untuk meminimalisasi risiko penyalahgunaan kredensial sesi yang terkompromi. |
| NFR-SEC-06 | Seluruh interaksi basis data wajib menggunakan Object-Relational Mapping (ORM) SQLAlchemy 2.0 dengan kueri terparameterisasi penuh (parameterized queries) guna mencegah kerentanan SQL Injection. |
| NFR-SEC-07 | Seluruh masukan teks dari formulir pengguna dan berkas naskah wajib melalui proses sanitasi karakter berbahaya sebelum disimpan ke basis data atau dirender ke DOM. |
| NFR-SEC-08 | API Gateway wajib menerapkan pembatasan laju permintaan (Rate Limiting) maksimal 60 request per menit per alamat IP menggunakan mekanisme sliding window rate limiter. |
| NFR-SEC-09 | Seluruh mutasi kuota token dan perubahan status invoice wajib menggunakan transaksi atomik basis data dengan penguncian baris eksplisit (SELECT ... FOR UPDATE) untuk mencegah kondisi perlombaan (race condition). |
| NFR-SEC-10 | Berkas naskah yang diunggah wajib diubah namanya menjadi acak UUIDv4 dan divalidasi berdasarkan magic bytes MIME-type untuk mencegah eksekusi skrip berkas berbahaya. |
| NFR-SEC-11 | Sistem wajib mencatat setiap aktivitas keamanan penting (percobaan login gagal, insiden brute-force, transaksi moneter, dan penghapusan naskah) ke dalam tabel audit_logs append-only secara persisten. |
| NFR-SEC-12 | Modul AI Chatbot wajib dilengkapi Academic Guardrail untuk mendeteksi upaya manipulasi prompt (jailbreak/prompt injection) dan secara tegas menolak instruksi di luar koridor akademik. |
| **Kebutuhan Ketersediaan & Keandalan (Availability & Reliability)** | |
| NFR-AVAIL-01 | Sistem web VeriText AI wajib memiliki tingkat ketersediaan (availability uptime) minimal 99,5% dalam periode evaluasi bulanan, di luar jadwal pemeliharaan terencana. |
| NFR-AVAIL-02 | Worker Celery wajib memiliki kebijakan otomatis mencoba ulang tugas (retry policy) hingga 3 kali dengan penundaan eksponensial (exponential backoff) jika terjadi kegagalan jaringan API eksternal. |
| NFR-AVAIL-03 | Jika tugas pemindaian naskah mengalami kegagalan fatal setelah 3 kali percobaan, sistem wajib mengembalikan saldo token kuota yang sempat dipotong secara otomatis ke akun pengguna (token refund). |
| NFR-AVAIL-04 | Jika API Google Gemini mengalami gangguan sementara atau batas laju kuota, modul AI Judge wajib melakukan penurunan layanan anggun (graceful degradation) dengan beralih ke mesin cadangan DeepSeek v4.1 Flash (via 9Router) secara transparan tanpa menghentikan proses audit. |
| NFR-AVAIL-05 | Target waktu pemulihan sistem (Recovery Time Objective - RTO) dari insiden kegagalan perangkat lunak atau server crash maksimal adalah 2 jam, dan batas toleransi kehilangan data transaksional (Recovery Point Objective - RPO) maksimal 1 jam dengan pencatatan Write-Ahead Logging (WAL) PostgreSQL. |
| **Kebutuhan Kepatuhan & Privasi Data (Compliance - UU PDP / GDPR)** | |
| NFR-COMP-01 | Sistem wajib mematuhi seluruh ketentuan Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP) dalam hal persetujuan eksplisit, pengumpulan, dan pemrosesan data pengguna. |
| NFR-COMP-02 | Sistem wajib menyediakan hak penghapusan data secara tuntas (Right to Erasure / Hard-Delete Cascading) yang menghapus berkas fisik, rekaman naskah, larik kalimat, laporan audit, dan riwayat chat atas permintaan pemilik sah dokumen. |
| NFR-COMP-03 | Naskah dokumen yang diunggah oleh pengguna tidak pernah dijadikan korpus publik tanpa izin eksplisit; naskah pengguna tetap menjadi hak milik intelektual pengguna seutuhnya (Zero Auto-Ingestion to Public Corpus). |
| NFR-COMP-04 | Rekaman log transaksi pembayaran, mutasi saldo token, dan notifikasi webhook wajib disimpan dengan integritas data tinggi (immutable ledger) selama minimal 3 tahun untuk keperluan rekonsiliasi keuangan dan audit akuntansi. |
| **Kebutuhan Kegunaan (Usability)** | |
| NFR-USAB-01 | Seluruh komponen antarmuka web, teks, notifikasi, dan diagram sistem dilarang menggunakan emoji visual apapun; antarmuka wajib bergaya akademik utilitarian yang bersih dan profesional (Zero-Emoji Policy). |
| NFR-USAB-02 | Desain antarmuka wajib memenuhi rasio kontras teks minimal 4,5:1 terhadap latar belakang sesuai pedoman Web Content Accessibility Guidelines (WCAG 2.1 Level AA). |
| NFR-USAB-03 | Pengguna baru dengan kemampuan operasional komputer standar wajib mampu memahami alur unggah dan peninjauan heatmap dalam waktu kurang dari atau sama dengan 10 menit tanpa pelatihan formal. |
| NFR-USAB-04 | Antarmuka Split-Screen Studio Workspace wajib menyesuaikan tata letak secara responsif pada resolusi layar 1280 piksel ke atas dan bertransformasi menjadi susunan bertumpuk pada layar tablet 768 piksel. |
| **Kebutuhan Pemeliharaan & Skalabilitas (Maintainability & Scalability)** | |
| NFR-SCALE-01 | Seluruh kode sumber backend wajib mengadopsi prinsip Clean Architecture modular (terbagi tegas atas layer routers/controllers, services, repositories, schemas, dan Celery workers) sehingga pemeliharaan komponen dapat dilakukan secara independen. |
| NFR-SCALE-02 | Basis kode backend wajib memiliki cakupan pengujian unit dan integrasi otomatis (pytest) minimal 80% pada modul logika bisnis utama. |
| NFR-SCALE-03 | Seluruh endpoint REST API wajib terdokumentasi secara otomatis menggunakan spesifikasi OpenAPI 3.1 dan dapat diakses melalui antarmuka Swagger UI interaktif (/docs). |
| NFR-SCALE-04 | Seluruh kredensial rahasia, URL koneksi basis data, dan API key wajib dikelola melalui variabel lingkungan terpusat (.env) menggunakan validasi pustaka pydantic-settings. |
| NFR-SCALE-05 | Arsitektur pemrosesan worker Celery dirancang stateless sehingga kapasitas pemindaian dokumen dapat ditingkatkan secara horizontal (horizontal scaling) dengan menambah instans worker baru yang terkoneksi ke Redis broker yang sama. |

---

Daftar Pustaka
[1] IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications. New York, NY: IEEE Computer Society, 1998.
[2] ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes — Requirements engineering. Geneva, Switzerland: ISO/IEC/IEEE, 2018.
[3] ISO/IEC 25010:2011, Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models. Geneva, Switzerland: ISO/IEC, 2011.
[4] S. Schleimer, D. S. Wilkerson, and A. Aiken, "Winnowing: local algorithms for document fingerprinting," in Proceedings of the 2003 ACM SIGMOD International Conference on Management of Data (SIGMOD '03), San Diego, CA, USA, 2003, pp. 76–85.
[5] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP), Hong Kong, 2019, pp. 3982–3992.
[6] Y. A. Malkov and D. A. Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs," IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 42, no. 4, pp. 824–836, Apr. 2020.
[7] K.-I. Goh and A.-L. Barabasi, "Burstiness and memory in complex systems," Europhysics Letters (EPL), vol. 81, no. 4, p. 48002, 2008.
[8] P. Henderson et al., "pgvector: Open-source vector similarity search for Postgres," GitHub repository, 2024. [Online]. Tersedia: https://github.com/pgvector/pgvector.
[9] FastAPI Documentation, "FastAPI Framework, High Performance, Easy to Learn, Fast to Code, Ready for Production," [Online]. Tersedia: https://fastapi.tiangolo.com/.
[10] Vue.js Core Team, "Vue.js 3.5 Documentation: The Progressive JavaScript Framework," [Online]. Tersedia: https://vuejs.org/guide/introduction.html.
[11] Celery Project, "Celery: Distributed Task Queue," [Online]. Tersedia: https://docs.celeryq.dev/.
[12] Midtrans API Documentation, "Core API & Snap Payment Gateway Integration Guide," [Online]. Tersedia: https://docs.midtrans.com/.
[13] OWASP Foundation, "OWASP Top Ten Web Application Security Risks," 2021. [Online]. Tersedia: https://owasp.org/Top10/.
[14] Pemerintah Republik Indonesia, Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP). Lembaran Negara RI Tahun 2022 Nomor 196.
[15] G. Booch, J. Rumbaugh, and I. Jacobson, The Unified Modeling Language User Guide, 2nd ed. Boston, MA: Addison-Wesley, 2005.
