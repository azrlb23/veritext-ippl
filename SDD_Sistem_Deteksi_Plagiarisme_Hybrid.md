Software Design Document
for
VeriText AI
Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical & Semantic AI Engine

Version 1.0 approved
Prepared by
11241045 - Mochammad Azriel Albian Putra
Program Studi Informatika
Institut Teknologi Kalimantan
Juni 2026

Table of Contents
Daftar Isi
Abstrak
BAB I PENDAHULUAN
1.1. Tujuan Software Design Document
1.2. Ruang Lingkup
1.3. Gambaran Dokumen
1.4. Referensi
BAB II TINJAUAN SISTEM
2.1. Deskripsi Umum
2.2. Fungsi Produk
2.3. Konteks dan Latar Belakang
BAB III RANCANGAN LINGKUNGAN APLIKASI
3.1. Lingkungan Perangkat Keras
3.2. Lingkungan Perangkat Lunak
  3.2.1. Stack Teknologi Frontend
  3.2.2. Stack Teknologi Backend
  3.2.3. Infrastruktur
3.3. Basis Data
3.4. Component Diagram
  3.4.1. Modul Autentikasi dan Manajemen Sesi (AuthService)
  3.4.2. Modul Pra-pemrosesan Dokumen (PreprocessorEngine)
  3.4.3. Modul Pipeline Deteksi Tiga Tahap & Akuisisi Korpus (HybridAuditOrchestrator)
  3.4.4. Modul Manajemen Token dan Pembayaran (BillingService)
  3.4.5. Modul Pembuatan Laporan dan Sertifikasi (ReportGeneratorService)
  3.4.6. Modul AI Chatbot Asisten Naskah dan Parafrase Instan (AcademicAssistantService)
  3.4.7. Modul Monitoring Layanan Read-Only Admin (AdminMonitoringService)
3.5. Communication Interface
  3.5.1. Standar REST API
  3.5.2. Katalog Endpoint API
    3.5.2.1. Modul Autentikasi dan Profil Akun
    3.5.2.2. Modul Dokumen dan Pra-pemrosesan
    3.5.2.3. Modul Pipeline Audit Deteksi Plagiarisme
    3.5.2.4. Modul AI Chatbot Asisten dan Parafrase Instan
    3.5.2.5. Modul Pelaporan, Sertifikasi dan Verifikasi Publik
    3.5.2.6. Modul Monetisasi Billing dan Pemantauan Admin
  3.5.3. Protokol Keamanan Webhook Midtrans
  3.5.4. Mekanisme Smart Polling
  3.5.5. Katalog Kode Error Terpusat
3.6. Desain Antarmuka (UI/UX)
BAB IV PERANCANGAN UML
4.1. Class Diagram
4.2. Data Flow Diagram (DFD)
  4.2.1. DFD Level 0 – Context Diagram
  4.2.2. DFD Level 1 – System Overview
  4.2.3. DFD Level 2 – Deteksi Plagiarisme Hybrid dan AI Chatbot
4.3. Activity Diagram (Breakdown Per Use Case AD1 s/d AD11)
4.4. Sequence Diagram (Breakdown Per Use Case SD1 s/d SD11)
Daftar Pustaka
Revision History

---

Abstrak
Dokumen Software Design Document (SDD) ini merupakan representasi rancangan teknis yang komprehensif, terstruktur, dan menyeluruh dari sistem perangkat lunak VeriText AI — platform deteksi plagiarisme cerdas berbasis arsitektur hybrid multi-tier yang menggabungkan pendekatan deterministik lexical fingerprinting dengan kecerdasan buatan semantik. Dokumen ini disusun sebagai turunan langsung dari Software Requirements Specification (SRS) VeriText AI versi 1.0, dengan tujuan mentransformasikan seluruh kebutuhan fungsional dan non-fungsional ke dalam rancangan implementasi teknis konkret yang siap dieksekusi oleh tim pengembang perangkat lunak.

Sistem VeriText AI dibangun di atas Clean Architecture berlapis yang memisahkan secara tegas tanggung jawab antara lapisan presentasi (Vue 3.5 Composition API + Vite 6 + TypeScript 5.7 + Pinia 2.3 + Tailwind CSS 3.4), lapisan logika bisnis dan gateway API (FastAPI 0.115 + Pydantic v2 + SQLAlchemy 2.0 Async), lapisan pemrosesan asinkron (Celery 5.4 + Redis 7.2 Broker), dan lapisan persistensi data terpadu (PostgreSQL 16 dengan ekstensi pgvector berindeks HNSW). Pemisahan lapisan ini menjamin prinsip Separation of Concerns (SoC) dan Dependency Inversion Principle (DIP).

Inti komputasi VeriText AI bertumpu pada pipa pemrosesan 3-Step Hybrid AI Detection Pipeline: Step 1 Leksikal menggunakan algoritma Winnowing Rabin-Karp Rolling Hash (k-gram=5, window=4) untuk mendeteksi penjiplakan verbatim (Tag MERAH); Step 2 Semantik memanfaatkan Sentence Transformers paraphrase-multilingual-MiniLM-L12-v2 (vektor 384-dimensi) yang diindeks dengan HNSW Cosine Distance (<=>) dipadukan dengan re-ranker spesialis bahasa Indonesia LazarusNLP/all-indobert-base-v4 untuk mendeteksi parafrase cerdas (Tag ORANYE); Step 3 Stilometri dan AI Judge menganalisis rasio Burstiness Goh & Barabasi dan Type-Token Ratio (TTR) yang disaring oleh Dual-Engine LLM Gateway (Google Gemini 2.5 Flash dengan failover otomatis ke DeepSeek v4.1 Flash via 9Router) guna mendeteksi anomali teks mesin (Tag KUNING). Agregasi skor komposit akhir dihitung dengan formula terbobot 0.50 Leksikal + 0.35 Semantik + 0.15 Stilometri.

Selain mesin deteksi, sistem dilengkapi modul interaktif Split-Screen Studio Workspace yang menyatukan Interactive Heatmap di kolom kiri dengan AI Chatbot Asisten Naskah & Parafrase Instan 3-Mode (Per Kalimat, Per Paragraf, Seluruh Halaman) di panel kanan yang dikunci oleh Academic Assistant Guardrail. Model operasional bersifat Self-Service SaaS dengan 3 Peran Pengguna: Free User (kuota 5 token dan 3x trial AI), Premium User (akses naskah panjang dengan token cap 5 token per dokumen, unduh PDF resmi ber-QR Code, dan akses penuh AI), serta Admin yang 100% Read-Only (monitoring telemetri dan log transaksi tanpa mutasi data). Monetisasi token dikelola via Midtrans Snap dengan auto-upgrade instan status pengguna saat webhook settlement terverifikasi. Kepatuhan privasi UU Perlindungan Data Pribadi (UU PDP No. 27/2022) dijamin melalui mekanisme hard-delete cascade dan zero auto-ingestion ke korpus publik.

Dokumen ini memuat secara lengkap: spesifikasi perangkat keras dan lunak; skema 13 tabel basis data relasional DDL SQL beserta parameter HNSW; diagram komponen dan antarmuka; spesifikasi REST API dan webhook; desain UI/UX; Class Diagram domain; Data Flow Diagram (DFD Level 0, 1, dan 2); serta 11 Activity Diagram (AD1–AD11) dan 11 Sequence Diagram (SD1–SD11) yang berkorespondensi satu-ke-satu dengan 11 Use Case pada dokumen SRS VeriText AI. Dokumen ini menjadi rujukan teknis tunggal (single source of truth) yang bebas dari elemen dekoratif non-akademik sesuai standar akademik tinggi.


BAB I
PENDAHULUAN

1.1. Tujuan Software Design Document
Dokumen Software Design Document (SDD) ini disusun dengan tujuan primer untuk mentransformasikan seluruh spesifikasi kebutuhan perangkat lunak yang telah didefinisikan secara formal di dalam Software Requirements Specification (SRS) VeriText AI versi 1.0 ke dalam bentuk cetak biru teknis (technical blueprint) yang terperinci, terukur, dan siap diimplementasikan. Jika dokumen SRS berfokus pada apa yang harus dipenuhi oleh sistem (what), maka dokumen SDD ini secara eksklusif dan mendalam menjawab bagaimana sistem diimplementasikan (how), mencakup struktur kelas, alur data antarmuka, algoritma komputasi, skema basis data, dan protokol integrasi jaringan.

Tujuan sekunder dokumen ini adalah menyediakan instrumen komunikasi dan kolaborasi formal antar anggota tim rekayasa perangkat lunak:
1. Bagi Backend Engineer & AI Engineer: Sebagai panduan pasti dalam mengimplementasikan endpoint REST API FastAPI, arsitektur task Celery, algoritma Winnowing Rabin-Karp, kueri graf HNSW pgvector, inferensi model Sentence Transformers dan IndoBERT, serta integrasi LLM Gemini 2.5 Flash.
2. Bagi Frontend Engineer: Sebagai acuan implementasi antarmuka pengguna berbasis Vue 3.5 (Composition API), Vite 6, TypeScript 5.7, Pinia 2.3, Axios 1.7, dan Tailwind CSS 3.4 pada Split-Screen Studio Workspace dan sistem desain semantik.
3. Bagi QA & Test Engineer: Sebagai dasar penyusunan skenario pengujian unit (unit test), pengujian integrasi (integration test), dan pengujian End-to-End (E2E) berdasarkan pemodelan alur kerja Activity Diagram dan Sequence Diagram.
4. Bagi Tim Akademik & Dosen Penilai: Sebagai bukti pemenuhan metodologi rekayasa perangkat lunak terstruktur berstandar IEEE Std 1016-2009 (Software Design Descriptions) dan ISO/IEC/IEEE 42010:2011 (Systems and Software Engineering - Architecture Description) pada mata kuliah Implementasi Proses Perangkat Lunak (IPPL).

1.2. Ruang Lingkup
Ruang lingkup desain teknis yang dicakup dalam SDD ini mencakup seluruh arsitektur platform VeriText AI versi 1.0 yang beroperasi sebagai aplikasi web desktop-first modern. Ruang lingkup perancangan teknis meliputi:
1. Arsitektur 4-Lapis Bersih (Clean 4-Layer Architecture): Pemisahan terstruktur antara Lapisan Presentasi (Vue 3.5 SPA), Lapisan Logika Bisnis & Gateway API (FastAPI), Lapisan Komputasi Asinkron & AI Engine (Celery + Redis), serta Lapisan Persistensi & Layanan Eksternal (PostgreSQL 16 pgvector, Midtrans Snap, Academic Graph APIs, Gemini AI).
2. Sistem Autentikasi Mandiri & RBAC 3-Role: Manajemen sesi stateless berbasis JWT (Access Token 15 menit) dan Refresh Token (HttpOnly Cookie 7 hari) serta Google OAuth 2.0 untuk 3 peran: Free User, Premium User, dan Admin (100% Read-Only).
3. Modul Pemrosesan Dokumen & Kalkulasi Biaya Token: Validasi ekstensi (.pdf, .docx, .txt), pengecekan ukuran berkas (maksimal 15 MB), ekstraksi teks bersih, segmentasi kalimat berbasis regex batas kalimat, dan kalkulasi otomatis kebutuhan token: Biaya = min(5, ceil(kata / 2.500)).
4. Pipa Deteksi 3-Tahap Hybrid: Integrasi algoritma Winnowing leksikal (k=5, w=4), pencarian semantik vektor padat 384 dimensi HNSW Cosine Distance (<=>) berpadu re-ranker IndoBERT, serta analisis stilometri Burstiness Goh & Barabasi dan TTR yang disaring oleh Gemini Contextual AI Judge.
5. Antarmuka Split-Screen Studio Workspace: Tata letak dua kolom terintegrasi yang menyajikan Interactive Heatmap 3-tier di sebelah kiri dan Panel Tabular 2-in-1 (Matched Sources & AI Chatbot Asisten Naskah) di sebelah kanan.
6. Fitur Parafrase Instan 3-Mode & Guardrail Akademik: Kemampuan parafrase Per Kalimat, Per Paragraf, dan Seluruh Halaman yang menghasilkan 3 opsi variasi ilmiah serta pembaruan teks naskah in-place dengan kalkulasi ulang skor seketika.
7. Modul Billing Midtrans Snap & Dompet Token: Pembelian token satuan (By Token) dan paket bundling (By Paket Token) dengan verifikasi webhook SHA-512 yang otomatis menaikkan status pengguna Free menjadi Premium secara instan.
8. Kepatuhan Privasi Dokumen (UU PDP No. 27/2022): Jaminan naskah pengguna tidak pernah diunggah ke korpus publik tanpa izin (Zero Auto-Ingestion) serta fitur hard-delete cascade naskah dan sesi percakapan chat.

1.3. Gambaran Dokumen
Dokumen SDD ini diorganisasikan ke dalam empat bab utama yang menyajikan rancangan sistem secara top-down:
- BAB I - Pendahuluan: Menguraikan tujuan penyusunan dokumen, ruang lingkup teknis sistem, gambaran struktur dokumen, dan tabel referensi standar formal yang diacu.
- BAB II - Tinjauan Sistem: Menyajikan deskripsi umum arsitektur makro perangkat lunak disertai Architecture Diagram 4-Lapis, dekomposisi tujuh fungsi modul utama, serta analisis konteks dan latar belakang teknis pemilihan arsitektur hybrid.
- BAB III - Rancangan Lingkungan Aplikasi: Mendefinisikan spesifikasi tujuh layanan modul backend, lingkungan perangkat keras dan perangkat lunak (frontend Vue 3.5, backend FastAPI, infrastruktur pendukung), skema basis data 13 tabel DDL SQL beserta indeks HNSW pgvector, diagram komponen arsitektur, spesifikasi protokol komunikasi REST API dan webhook Midtrans, serta panduan antarmuka UI/UX Split-Screen Workspace.
- BAB IV - Perancangan UML: Memuat seluruh artefak visual pemodelan perangkat lunak mencakup Class Diagram 13 entitas, Data Flow Diagram (DFD Level 0, Level 1, Level 2), 11 Activity Diagram (AD1 s/d AD11), dan 11 Sequence Diagram (SD1 s/d SD11) yang berkorespondensi satu-ke-satu dengan 11 Use Case pada dokumen SRS VeriText AI.

1.4. Referensi
Penyusunan dokumen SDD ini merujuk pada standar industri, publikasi ilmiah, dan dokumentasi resmi teknologi berikut:

Tabel 1.1: Daftar Referensi Standar dan Pustaka Teknis
| No | Dokumen Acuan / Standar | Penerbit / Sumber | Deskripsi Relevansi |
| :--- | :--- | :--- | :--- |
| 1 | IEEE Std 1016-2009 | IEEE Computer Society | Standar internasional format dan struktur Software Design Descriptions (SDD). |
| 2 | ISO/IEC/IEEE 42010:2011 | ISO / IEC / IEEE | Kerangka kerja konseptual deskripsi arsitektur sistem dan perangkat lunak. |
| 3 | IEEE Std 830-1998 | IEEE Computer Society | Standar spesifikasi kebutuhan perangkat lunak (acuan dokumen SRS VeriText AI). |
| 4 | ISO/IEC 25010:2011 | ISO / IEC | Model kualitas perangkat lunak (karakteristik fungsional, performa, dan keandalan). |
| 5 | UU RI No. 27 Tahun 2022 | Lembaran Negara Republik Indonesia | Undang-Undang Perlindungan Data Pribadi (UU PDP) mengenai hak penghapusan data. |
| 6 | Schleimer et al. (2003) | ACM SIGMOD Conference | Makalah Winnowing: Local Algorithms for Document Fingerprinting (Step 1 Leksikal). |
| 7 | Reimers & Gurevych (2019) | EMNLP-IJCNLP | Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks (Step 2 Semantik). |
| 8 | Malkov & Yashunin (2020) | IEEE TPAMI | Hierarchical Navigable Small World Graphs untuk pencarian ANN berkecepatan tinggi. |
| 9 | Goh & Barabasi (2008) | Europhysics Letters (EPL) | Teori Burstiness and Memory in Complex Systems (analisis stilometri Step 3). |
| 10 | Martin, Robert C. (2017) | Prentice Hall | Buku Clean Architecture: A Craftsman's Guide to Software Structure and Design. |
| 11 | Vue.js Official Documentation | Vue.js Core Team | Panduan resmi Vue 3.5 Composition API, Reactivity Core, dan SFC. |
| 12 | Vite Official Documentation | Vite Core Team | Panduan bundler Vite 6, Hot Module Replacement (HMR), dan konfigurasi build. |
| 13 | Pinia Official Documentation | Eduardo San Martin Morote | Dokumentasi modular state management resmi untuk Vue 3. |
| 14 | FastAPI Official Documentation | Tiangolo (Sebastián Ramírez) | Dokumentasi resmi framework ASGI FastAPI 0.115 dan Pydantic v2. |
| 15 | pgvector Documentation | PostgreSQL Community | Dokumentasi ekstensi pgvector v0.7+ dan operator jarak Cosine (<=>). |
| 16 | Celery Official Documentation | Celery Project | Panduan distributed task queue Celery 5.4 dan Redis result backend. |
| 17 | Midtrans API Documentation | PT Midtrans Indonesia | Panduan integrasi Snap payment gateway, parameter order, dan webhook SHA-512. |
| 18 | OpenAlex API Documentation | OurResearch | Spesifikasi API REST OpenAlex Academic Graph untuk akuisisi korpus otomatis. |
| 19 | Google Gemini API Docs | Google DeepMind | Dokumentasi Generative Language API Gemini 2.5 Flash dan Google Search Grounding. |


BAB II
TINJAUAN SISTEM

2.1. Deskripsi Umum
VeriText AI adalah platform perangkat lunak inspeksi integritas naskah akademik cerdas berbasis web yang dirancang dengan memadukan prinsip Clean Architecture (CA) Robert C. Martin dan arsitektur Ports and Adapters (Hexagonal Architecture). Sistem ini dirancang untuk beroperasi secara mandiri (Self-Service SaaS) di mana seluruh proses pengguna—mulai dari pendaftaran akun, validasi naskah, perhitungan token, komputasi deteksi multi-tahap, konsultasi AI Chatbot, hingga pembelian token dan pembayaran—berjalan 100% otomatis tanpa memerlukan intervensi manual administrator.

Arsitektur makro VeriText AI dibagi menjadi empat lapisan logis yang terisolasi secara ketat:
1. Lapisan 1 - Presentasi (Frontend Web Client): Diimplementasikan menggunakan Vue 3.5 Single Page Application (SPA) berbasis Composition API, didukung bundler Vite 6, bahasa TypeScript 5.7, pengelola state modular Pinia 2.3, perute Vue Router 4.5, klien HTTP Axios 1.7, dan kerangka utilitas Tailwind CSS 3.4. Lapisan ini bertanggung jawab merender Split-Screen Studio Workspace dan menangani interaktivitas pengguna secara reaktif.
2. Lapisan 2 - Logika Bisnis & Gateway API (Backend Core): Diimplementasikan menggunakan framework FastAPI 0.115 (Python 3.11+). Lapisan ini mengeksekusi routing REST API v1, validasi skema request/response menggunakan Pydantic v2, pengamanan rute via JWT dan Google OAuth 2.0, kalkulasi biaya token atomik, evaluasi Academic Assistant Guardrail, dan penanganan webhook Midtrans yang aman.
3. Lapisan 3 - Komputasi Asinkron & Pipa AI (Celery Worker & ML Engine): Menggunakan Celery 5.4 Task Queue dengan Redis 7.2 sebagai Message Broker. Lapisan ini memproses tugas komputasi berat secara non-blocking di latar belakang, menjalankan Step 1 Winnowing leksikal, Step 2 inferensi Sentence Transformers dan pencarian graf HNSW pgvector, Step 3 analisis stilometri Goh & Barabasi, serta evaluasi filter kontekstual Google Gemini 2.5 Flash.
4. Lapisan 4 - Persistensi Data, Korpus Otomatis & Layanan Eksternal: Berpusat pada database relasional PostgreSQL 16 dengan ekstensi pgvector yang menyimpan 13 tabel data dan indeks vektor 384 dimensi HNSW. Lapisan ini juga mengintegrasikan layanan eksternal: Midtrans Snap API, OpenAlex API, DOAJ API, Semantic Scholar API, Crossref API, dan Google Generative AI API.

Berikut adalah representasi visual diagram arsitektur sistem VeriText AI:

![Architecture Diagram](diagrams/exported/Architecture%20Diagram.png)

2.2. Fungsi Produk
Sistem VeriText AI mengintegrasikan tujuh modul fungsional utama yang saling terhubung melalui antarmuka layanan:
1. Modul Autentikasi dan Manajemen Akun (AuthService): Mengatur alur login dan registrasi akun mandiri menggunakan Email/Password dan Google OAuth 2.0. Saat akun Free baru terdaftar, modul ini secara otomatis mengalokasikan 5 Token Saldo Gratis dan 3 kali kuota Trial AI Chatbot/Parafrase.
2. Modul Manajemen Dokumen dan Pra-pemrosesan (PreprocessorEngine): Menangani unggah berkas naskah multi-format (.pdf, .docx, .txt) dengan batas ukuran 15 MB atau penempelan teks langsung di workspace. Modul ini melakukan ekstraksi teks bersih, penghitungan kata real-time, dan kalkulasi estimasi pemotongan token sesuai rumus: Biaya = min(5, ceil(kata / 2.500)).
3. Modul Mesin Deteksi Plagiarisme 3-Tahap (HybridAuditOrchestrator): Mengatur alur deteksi plagiarisme secara berjenjang dari Step 1 Winnowing leksikal (Tag MERAH), Step 2 Semantic SBERT + IndoBERT Re-ranker pada pgvector HNSW (Tag ORANYE), hingga Step 3 Stilometri dan Contextual AI Judge Gemini (Tag KUNING), serta menghitung nilai Overall Composite Similarity Score dengan bobot 0.50 : 0.35 : 0.15.
4. Modul Visualisasi Laporan dan Heatmap (ReportViewerService): Menyajikan naskah beranotasi warna pada Interactive Heatmap di kolom kiri Split-Screen Workspace, visualisasi Side-by-Side Comparison dengan naskah pembanding, penyaringan sorotan per kategori plagiat, serta penyediaan tautan DOI/URL sumber asli.
5. Modul AI Chatbot Asisten Naskah dan Parafrase Instan (AcademicAssistantService): Menyediakan asisten ilmiah interaktif di panel kanan workspace yang dikunci dengan Academic Assistant Guardrail. Modul ini mendukung parafrase instan dalam 3 mode fleksibel (Per Kalimat, Per Paragraf, Seluruh Halaman) yang menghasilkan 3 opsi kalimat akademik dan menerapkan perbaikan ke naskah secara in-place disertai perhitungan ulang skor seketika.
6. Modul Manajemen Token dan Pembayaran Midtrans (BillingService): Mengelola dompet token komputasi (TokenWallet), pembelian token secara eceran (By Token) maupun paket diskon (By Paket Token) melalui Midtrans Snap, serta pembaruan otomatis saldo dan peningkatan status akun menjadi Premium saat webhook settlement terverifikasi.
7. Modul Sertifikasi PDF dan Monitoring Layanan (Report & AdminMonitoringService): Menghasilkan dokumen laporan resmi berformat PDF dengan QR Code verifikasi keaslian dokumen publik (/verify/{uuid}) untuk pengguna Premium, serta menyediakan dasbor telemetri dan log transaksi bagi Admin yang bersifat 100% Read-Only (tanpa mutasi data pengguna).

2.3. Konteks dan Latar Belakang
Latar belakang teknis perancangan arsitektur hybrid pada VeriText AI berakar pada kelemahan fundamental sistem deteksi plagiarisme konvensional. Sistem generasi awal yang hanya mengandalkan pencocokan string leksikal (seperti n-gram atau Winnowing murni) sangat rentan terhadap manipulasi parafrase cerdas, penggantian sinonim kata demi kata, pengubahan struktur kalimat aktif-pasif, dan penerjemahan lintas bahasa (cross-lingual). Sebaliknya, sistem modern yang mengandalkan model bahasa AI secara penuh sering kali mengalami kendala latensi komputasi yang tinggi, biaya komputasi API yang mahal untuk dokumen berukuran puluhan ribu kata (seperti skripsi dan disertasi), serta risiko halusinasi positif palsu pada sitasi dan kutipan langsung yang sah.

VeriText AI memecahkan dikotomi tersebut melalui pendekatan 3-Step Hybrid Detection Pipeline:
- Step 1 mengeksekusi Winnowing Rabin-Karp secara deterministik dengan kompleksitas O(N) untuk menangkap penjiplakan leksikal copy-paste secara instan.
- Step 2 mengeksekusi inferensi vektor padat 384-dimensi menggunakan Sentence Transformers paraphrase-multilingual-MiniLM-L12-v2 dipadukan dengan indeks graf HNSW pada PostgreSQL pgvector dan re-ranker LazarusNLP/all-indobert-base-v4 untuk menangkap parafrase konsep semantik berbahasa Indonesia dan internasional.
- Step 3 mengeksekusi analisis statistik stilometri Goh & Barabasi Burstiness dan TTR yang dikombinasikan dengan Dual-Engine LLM Gateway (Google Gemini 2.5 Flash & DeepSeek v4.1 Flash via 9Router) sebagai Contextual AI Judge untuk membedakan tulisan manusia, parafrase akademik, dan teks yang dihasilkan mesin (LLM).

Dengan arsitektur ini, VeriText AI menghadirkan efisiensi komputasi yang tinggi, akurasi deteksi multi-bahasa yang tajam, dan transparansi laporan yang dapat diandalkan oleh sivitas akademika.



BAB III
RANCANGAN LINGKUNGAN APLIKASI

3.1. Lingkungan Perangkat Keras
1. Perangkat Klien (Web Browser):
   - Prosesor: Minimum Dual-Core 1.5 GHz atau lebih tinggi.
   - Memori RAM: Minimum 4 GB RAM.
   - Resolusi Layar: Minimum 1280 x 720 piksel (resolusi yang direkomendasikan adalah 1920 x 1080 piksel untuk pengalaman optimal Split-Screen Studio Workspace).
   - Koneksi Internet: Minimum 1 Mbps stabil dengan latensi wajar.
2. Perangkat Server (Cloud Host / VPS Compute Node):
   - Prosesor: Minimum 4 vCPU (disarankan 8 vCPU arsitektur x86_64 atau ARM64).
   - Memori RAM: Minimum 8 GB RAM (disarankan 16 GB untuk mendukung efisiensi indeks HNSW pgvector dan inferensi Sentence Transformers).
   - Penyimpanan: Minimum 50 GB NVMe SSD (disarankan 100 GB SSD dengan IOPS tinggi untuk efisiensi kueri vektor dan penyimpanan korpus).

3.2. Lingkungan Perangkat Lunak

3.2.1. Stack Teknologi Frontend
Tabel 3.1: Stack Teknologi Frontend VeriText AI
| Library / Framework | Versi | Justifikasi Pemilihan |
| :--- | :--- | :--- |
| Vue 3 | 3.5.x | Framework SPA modern dengan Composition API dan Reactivity Engine yang sangat cepat, efisien memori, dan ideal untuk pembaruan in-place teks naskah. |
| Vite | 6.x | Build tool dan development server generasi baru berbasis Rollup dan esbuild dengan Hot Module Replacement (HMR) berkecepatan sub-milidetik. |
| TypeScript | 5.7.x | Static typing yang ketat untuk mendefinisikan antarmuka kontrak API, mencegah error runtime, dan meningkatkan keandalan kode frontend. |
| Pinia | 2.3.x | Pengelola state global modular yang ringan, type-safe, dan terintegrasi mulus dengan Vue 3 Composition API (mengelola sesi user, saldo wallet, dan state workspace). |
| Vue Router | 4.5.x | Routing resmi Vue 3 yang mendukung navigation guards untuk proteksi rute berbasis RBAC (hanya pengguna login yang dapat mengakses /workspace). |
| Axios | 1.7.x | HTTP client berbasis promise yang mendukung request/response interceptors untuk otomatisasi penambahan JWT Bearer Token dan penanganan error terpusat. |
| Tailwind CSS | 3.4.x | Utility-first CSS framework untuk membangun tata letak Split-Screen Studio Workspace yang presisi, responsif, berdensitas data tinggi, dan bebas dari CSS tidak terpakai. |

3.2.2. Stack Teknologi Backend
Tabel 3.2: Stack Teknologi Backend VeriText AI
| Library / Framework | Versi | Justifikasi Pemilihan |
| :--- | :--- | :--- |
| Python | 3.11+ | Lingkungan eksekusi backend berkinerja tinggi dengan optimasi runtime CPython dan ekosistem AI terlengkap di dunia. |
| FastAPI | 0.115.x | Framework ASGI modern berkinerja tinggi, menghasilkan dokumentasi OpenAPI 3.1 otomatis, mendukung async/await native, dan dependency injection. |
| Pydantic | 2.x | Validasi data dan serialisasi skema request/response berbasis engine Rust (pydantic-core) yang 5-50x lebih cepat daripada Pydantic v1. |
| SQLAlchemy | 2.0.x | ORM dan SQL Core modern dengan dukungan async penuh (AsyncSession) untuk interaksi database PostgreSQL yang aman dan terstruktur. |
| asyncpg | 0.29.x | Driver koneksi database PostgreSQL asinkron berkecepatan tinggi berbasis protokol biner PostgreSQL. |
| Celery | 5.4.x | Distributed task queue untuk mengeksekusi pipeline deteksi plagiarisme 3-tahap secara asinkron di latar belakang. |
| Redis | 7.2.x | In-memory message broker dan result backend berlatensi ultra-rendah untuk antrean tugas Celery dan mekanisme rate limiting. |
| sentence-transformers | 3.x | Framework inferensi model transformer Siamese BERT untuk enkoding vektor semantik teks multilingual (paraphrase-multilingual-MiniLM-L12-v2). |
| PyTorch | 2.x | Pustaka komputasi tensor untuk mengeksekusi model embedding pada CPU/GPU server. |
| pdfplumber & python-docx | 0.10+ / 1.1+ | Pustaka ekstraksi teks murni dari berkas dokumen PDF dan DOCX dengan presisi karakter dan metadata yang tinggi. |
| WeasyPrint | 61.x | Engine render HTML/CSS ke berkas PDF beresolusi cetak untuk penerbitan laporan sertifikat resmi. |
| passlib + bcrypt | 1.7.x | Pustaka enkripsi hashing kata sandi dengan salt dinamis standar industri (Bcrypt cost factor 12). |
| google-genai | 0.1+ | SDK resmi Google Gemini untuk integrasi Gemini 2.5 Flash sebagai Contextual AI Judge dan Asisten Parafrase Ilmiah. |

3.2.3. Infrastruktur
Tabel 3.3: Komponen Infrastruktur dan Konfigurasi Kritis
| Komponen | Versi | Konfigurasi Kritis |
| :--- | :--- | :--- |
| PostgreSQL | 16.x | shared_buffers=2GB, work_mem=64MB, maintenance_work_mem=512MB, ekstensi pgvector v0.7.0+ |
| Redis | 7.x | maxmemory=2gb, maxmemory-policy=allkeys-lru, appendonly=yes |
| Nginx | 1.24+ | Reverse proxy; TLS 1.3; rate limiting 60 req/min; client_max_body_size=15M |
| Gunicorn + Uvicorn | 21+ / 0.29+ | 4 worker processes; keepalive 5s; uvicorn.workers.UvicornWorker |
| Midtrans Payment Gateway | Core & Snap v2 | Sandbox & Production environment; verifikasi webhook signature SHA-512 |

3.3. Basis Data
Struktur basis data VeriText AI dirancang menggunakan sistem manajemen basis data relasional PostgreSQL 16 yang diperluas dengan ekstensi pgvector. Skema ini memodelkan 13 entitas domain utama (direalisasikan ke dalam 15 tabel fisik DDL SQL termasuk tabel pendukung keamanan password_resets dan audit_logs) yang dinormalisasi hingga bentuk normal ketiga (3NF) untuk menjamin integritas relasional dan konsistensi data.

Berikut adalah skema Data Definition Language (DDL SQL) lengkap yang digunakan dalam sistem:

```sql
-- Inisialisasi Ekstensi Vektor
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Tabel users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'FREE' CHECK (role IN ('FREE', 'PREMIUM', 'ADMIN')),
    password_hash VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_email ON users(email);

-- 2. Tabel sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);

-- 3. Tabel password_resets
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reset_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabel token_wallets
CREATE TABLE token_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 5 CHECK (balance >= 0),
    ai_trial_remaining INTEGER NOT NULL DEFAULT 3 CHECK (ai_trial_remaining >= 0),
    ai_chat_allowance_remaining INTEGER NOT NULL DEFAULT 0 CHECK (ai_chat_allowance_remaining >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_wallets_user_id ON token_wallets(user_id);

-- 5. Tabel token_transactions
CREATE TABLE token_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES token_wallets(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('DEBIT_AUDIT', 'DEBIT_CHAT_PARAPHRASE', 'CREDIT_TOPUP', 'CREDIT_REFUND')),
    reference_id VARCHAR(100),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_token_tx_wallet ON token_transactions(wallet_id);

-- 6. Tabel invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id VARCHAR(100) NOT NULL UNIQUE,
    purchase_scheme VARCHAR(30) NOT NULL CHECK (purchase_scheme IN ('BY_TOKEN', 'BY_PACKAGE')),
    package_type VARCHAR(50),
    token_amount INTEGER NOT NULL CHECK (token_amount > 0),
    gross_amount NUMERIC(12,2) NOT NULL CHECK (gross_amount >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SETTLEMENT', 'EXPIRE', 'CANCEL')),
    snap_token VARCHAR(255),
    snap_redirect_url TEXT,
    settled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_invoices_order_id ON invoices(order_id);
CREATE INDEX idx_invoices_user_id ON invoices(user_id);

-- 7. Tabel documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path TEXT,
    file_size_bytes INTEGER NOT NULL DEFAULT 0,
    word_count INTEGER NOT NULL DEFAULT 0,
    token_cost INTEGER NOT NULL DEFAULT 1,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_documents_user_id ON documents(user_id);

-- 8. Tabel audit_tasks
CREATE TABLE audit_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'QUEUED' CHECK (status IN ('QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    lexical_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    semantic_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    stylometric_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    composite_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    execution_time_sec NUMERIC(8,3),
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_tasks_doc ON audit_tasks(document_id);
CREATE INDEX idx_audit_tasks_user ON audit_tasks(user_id);

-- 9. Tabel audit_sentences
CREATE TABLE audit_sentences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES audit_tasks(id) ON DELETE CASCADE,
    sentence_order INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    current_text TEXT NOT NULL,
    match_type VARCHAR(20) NOT NULL DEFAULT 'NONE' CHECK (match_type IN ('NONE', 'RED', 'ORANGE', 'YELLOW', 'RESOLVED_GREEN')),
    similarity_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    matched_source_id UUID,
    is_modified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_sentences_task ON audit_sentences(task_id);

-- 10. Tabel audit_reports
CREATE TABLE audit_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL UNIQUE REFERENCES audit_tasks(id) ON DELETE CASCADE,
    certificate_uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    qr_code_url TEXT NOT NULL,
    pdf_report_path TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_reports_certificate ON audit_reports(certificate_uuid);

-- 11. Tabel chat_sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_chat_sessions_doc ON chat_sessions(document_id);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);

-- 12. Tabel chat_messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('USER', 'ASSISTANT', 'SYSTEM')),
    content TEXT NOT NULL,
    mode VARCHAR(30) CHECK (mode IN ('CONSULTATION', 'SENTENCE', 'PARAGRAPH', 'FULL_PAGE')),
    suggested_options JSONB,
    applied_to_document BOOLEAN NOT NULL DEFAULT FALSE,
    target_sentence_id UUID REFERENCES audit_sentences(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);

-- 13. Tabel corpus_documents & document_chunks (pgvector HNSW)
CREATE TABLE corpus_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(100) NOT NULL,
    doi_or_url TEXT,
    title TEXT NOT NULL,
    author VARCHAR(255),
    year INTEGER,
    language VARCHAR(10) DEFAULT 'id',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    corpus_doc_id UUID NOT NULL REFERENCES corpus_documents(id) ON DELETE CASCADE,
    chunk_order INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    kgram_hashes BIGINT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indeks Vektor HNSW Berkinerja Tinggi
CREATE INDEX idx_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- Tabel Tambahan Keamanan: audit_logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_logs_event ON audit_logs(event_type);
```


3.4. Component Diagram
Component Diagram memodelkan dekomposisi sistem ke dalam komponen-komponen arsitektural yang dapat digunakan kembali, batas-batas layanannya, antarmuka yang disediakan (Provided Interfaces), serta antarmuka yang dibutuhkan (Required Interfaces). Arsitektur VeriText AI terdiri atas 7 modul layanan inti yang bekerja secara terintegrasi:

3.4.1. Modul Autentikasi dan Manajemen Sesi (AuthService)
Layanan AuthService bertanggung jawab atas seluruh siklus hidup identitas pengguna dalam sistem VeriText AI. Layanan ini menerapkan standar autentikasi OAuth 2.0 Password Flow dengan JWT (JSON Web Tokens) dan integrasi Google OAuth 2.0.
Spesifikasi Teknis AuthService:
1. Token Payload: JWT Access Token ditandatangani menggunakan algoritma HMAC-SHA256 (HS256) dengan masa berlaku (TTL) 15 menit. Payload JWT memuat klaim standar: sub (UUID user_id), email, role ('FREE' | 'PREMIUM' | 'ADMIN'), iat, dan exp.
2. Refresh Token: Refresh Token berukuran 64-byte kriptografis disimpan dalam cookie peramban dengan atribut HttpOnly, Secure, SameSite=Lax, dan TTL 7 hari. Nilai hash SHA-256 dari refresh token disimpan di tabel sessions pada database untuk memungkinkan pencabutan sesi (session revocation) secara instan.
3. Password Hashing: Kata sandi pengguna dienkripsi menggunakan Bcrypt dengan work factor cost = 12.
4. Auto-Provisioning Kuota Awal: Saat pengguna baru menyelesaikan registrasi (baik via email maupun Google OAuth), AuthService secara atomik memicu pembuatan record pada tabel token_wallets dengan saldo awal balance = 5 token gratis dan kuota coba asisten AI ai_trial_remaining = 3.

3.4.2. Modul Pra-pemrosesan Dokumen (PreprocessorEngine)
Layanan PreprocessorEngine bertugas mengonversi naskah mentah dari berbagai format berkas ke dalam representasi teks terstruktur yang siap diproses oleh AI pipeline.
Spesifikasi Teknis PreprocessorEngine:
1. Validasi Berkas: Memeriksa ukuran berkas (maksimal 15 MB) dan memverifikasi magic bytes MIME type untuk mencegah serangan file upload (hanya mengizinkan application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, dan text/plain).
2. Ekstraksi Teks Bersih: Mengekstrak teks dari PDF menggunakan pdfplumber dan DOCX menggunakan python-docx, melakukan normalisasi Unicode (NFC), menghapus whitespace berlebih, dan mempertahankan tanda baca esensial.
3. Penghitungan Kata dan Estimasi Biaya: Menghitung total kata naskah (word_count) dan menghitung biaya konsumsi token sesuai formula: Biaya = min(5, ceil(kata / 2.500)).
4. Segmentasi Kalimat: Memecah teks naskah menjadi larik kalimat individual menggunakan regular expression berbasis batas kalimat ilmiah (sentence boundary markers: titik, tanda tanya, tanda seru yang diikuti spasi dan huruf kapital, dengan penanganan khusus singkatan gelar dan sitasi seperti 'dkk.', 'et al.', 'Prof.', 'Dr.'). Setiap kalimat diberi nomor urut sentence_order dan dicatat pada tabel audit_sentences.

3.4.3. Modul Pipeline Deteksi Tiga Tahap & Akuisisi Korpus (HybridAuditOrchestrator & CorpusHarvesterService)
Layanan ini merupakan inti komputasi cerdas yang mengeksekusi pipeline 3-Step Hybrid AI dan mengelola pembaruan korpus pembanding otomatis tanpa ketergantungan pada input manual institusi.
Spesifikasi Teknis Pipeline 3-Tahap:
1. Step 1 - Winnowing Lexical Match: Menghasilkan k-gram karakter (k=5) dan sliding window (w=4). Menggunakan Rabin-Karp Rolling Hash (basis b=257, prima M=1.000.000.007) untuk menghasilkan sidik jari leksikal (fingerprints). Fingerprints naskah dicocokkan dengan fingerprints korpus pada kolom kgram_hashes di tabel document_chunks. Kalimat dengan persentase kecocokan leksikal >= 80% ditandai sebagai match_type = 'RED'.
2. Step 2 - Semantic AI & HNSW Search: Setiap kalimat naskah dienkode menjadi dense vector 384-dimensi menggunakan Sentence Transformers paraphrase-multilingual-MiniLM-L12-v2. Vektor kalimat dikueri ke tabel document_chunks pada PostgreSQL pgvector menggunakan operator Cosine Distance (<=>) berindeks HNSW (m=16, ef_construction=64). Kandidat kalimat yang memiliki Cosine Similarity >= 0.75 kemudian dinilai ulang oleh re-ranker spesialis Indonesia LazarusNLP/all-indobert-base-v4 dan ditandai sebagai match_type = 'ORANGE'.
3. Step 3 - Stilometri & Contextual AI Judge: Menghitung koefisien Burstiness Goh & Barabasi B = (sigma_L - mu_L) / (sigma_L + mu_L) dan Type-Token Ratio (TTR) naskah. Kalimat anomali yang memiliki pola sintaksis buatan dievaluasi oleh Google Gemini 2.5 Flash (dengan failover otomatis ke DeepSeek v4.1 Flash via 9Router) untuk menyaring sitasi yang sah. Kalimat plagiat hasil AI ditandai sebagai match_type = 'YELLOW'.
4. Agregator Skor Komposit: Menghitung Overall Composite Similarity Score: S_Composite = (0.50 * S_Lexical) + (0.35 * S_Semantic) + (0.15 * S_Stylometric).
5. Akuisisi Korpus Otomatis (Dual-Scope): Modul CorpusHarvesterService secara berkala menarik karya ilmiah dari 6 sumber resmi: OpenAlex Academic Graph API, DOAJ API, Semantic Scholar Academic Graph API, Crossref REST API, HuggingFace Indonesian STS & Paraphrase Datasets, serta Google Search Grounding. Dokumen yang diakuisisi dipecah menjadi chunks, dihitung embedding vektornya, dan disimpan ke tabel corpus_documents dan document_chunks.

3.4.4. Modul Manajemen Token dan Pembayaran (BillingService)
Layanan BillingService mengelola ekonomi token komputasi dalam sistem VeriText AI dan menjamin integritas transaksi moneter.
Spesifikasi Teknis BillingService:
1. Model Konsumsi Token: 1 Token mencakup audit plagiarisme hingga 2.500 kata (dengan batas maksimum 5 Token per dokumen), atau 10x respon AI Chatbot / parafrase per kalimat dan paragraf, atau 2 halaman penuh untuk batch paraphrase.
2. Skema Pembelian:
   - By Token (Eceran): Pengguna bebas memasukkan jumlah token (minimal 5 token = Rp 10.000, dengan tarif dasar Rp 2.000 / token).
   - By Paket Token (Bundling Diskon): Paket Starter (15 Token = Rp 25.000), Paket Skripsi Pro (50 Token = Rp 65.000), dan Paket Riset Intensif (150 Token = Rp 150.000).
3. Integrasi Midtrans Snap: Mengirim parameter transaksi ke Midtrans Snap API dan menerima Snap Token untuk memunculkan modal pembayaran di peramban klien.
4. Pemrosesan Webhook Atomik: Menangkap notifikasi HTTP POST dari Midtrans, memverifikasi tanda tangan kriptografis SHA-512, dan mengeksekusi transaksi database menggunakan baris terkunci (SELECT ... FOR UPDATE) untuk menambah saldo token_wallets dan otomatis menaikkan status role akun dari 'FREE' menjadi 'PREMIUM'.

3.4.5. Modul Pembuatan Laporan dan Sertifikasi (ReportGeneratorService)
Layanan ini bertanggung jawab memformat dan mengekspor hasil audit plagiarisme ke dalam dokumen resmi berstandar publikasi.
Spesifikasi Teknis ReportGeneratorService:
1. Generasi PDF: Mengompilasi naskah beranotasi heatmap, ringkasan skor komposit, rincian perbandingan sumber pembanding, dan metadata dokumen ke dalam dokumen PDF resolusi cetak menggunakan pustaka WeasyPrint.
2. Sertifikasi QR Code: Menghasilkan UUID sertifikat unik yang disematkan ke dalam gambar QR Code menggunakan pustaka qrcode. QR Code mengarah ke URL publik https://veritext.ai/verify/{certificate_uuid}.
3. Otorisasi Akses Unduh: Mengunduh berkas laporan PDF resmi merupakan hak khusus pengguna berstatus Premium User. Pengguna Free User dapat melihat laporan interaktif di web dan memverifikasi QR Code publik.

3.4.6. Modul AI Chatbot Asisten Naskah dan Parafrase Instan (AcademicAssistantService)
Layanan ini menggantikan paradigma konvensional dengan menghadirkan pendampingan revisi naskah cerdas yang terintegrasi langsung di layar workspace.
Spesifikasi Teknis AcademicAssistantService:
1. Academic Assistant Guardrail: Memeriksa setiap pesan pengguna menggunakan lapisan validasi sistemik. Jika permintaan terdeteksi di luar konteks perbaikan naskah akademik (misalnya permintaan pembuatan tugas dari nol, konten berbahaya, atau pertanyaan non-ilmiah), sistem menolak permintaan dengan kode error CHAT_001 (GUARDRAIL_VIOLATION).
2. Tiga Mode Granularitas Parafrase:
   - Mode Per Kalimat: Memparafrase satu kalimat spesifik yang diklik pengguna pada heatmap.
   - Mode Per Paragraf: Memparafrase seluruh paragraf sekaligus dengan menjaga koherensi dan transisi antar-kalimat.
   - Mode Seluruh Halaman: Memparafrase seluruh kalimat berstatus merah/oranye/kuning pada satu halaman secara batch.
3. Generator 3 Opsi Variasi: Menghasilkan 3 variasi kalimat parafrase berkaidah akademik baku disertai estimasi skor kemiripan baru.
4. Pembaruan Naskah In-Place: Saat pengguna memilih salah satu variasi dan mengklik 'Terapkan ke Naskah', teks pada dokumen diperbarui secara in-place, skor kemiripan segmen dan komposit dihitung ulang secara real-time, dan warna highlight di heatmap berubah menjadi Hijau (Telah Diperbaiki).

3.4.7. Modul Monitoring Layanan Read-Only Admin (AdminMonitoringService)
Layanan ini dirancang khusus untuk administrator sistem dengan prinsip 100% Read-Only (hanya membaca data agregat, tanpa fitur penulisan atau mutasi data pengguna).
Spesifikasi Teknis AdminMonitoringService:
1. Pembatasan Hak Akses Ketat: Seluruh endpoint di bawah /api/v1/admin/* hanya mengizinkan metode HTTP GET. Sistem sama sekali tidak menyediakan endpoint POST/PUT/PATCH/DELETE untuk mengubah saldo pengguna, memblokir akun secara manual, atau mengubah skor audit.
2. Metrik Telemetri: Menyajikan statistik agregat total dokumen yang dipindai, distribusi rata-rata skor plagiarisme, status antrean Celery worker, dan penggunaan kapasitas database pgvector.
3. Log Transaksi Moneter: Menampilkan riwayat transaksi masuk Midtrans, rincian nomor order, nominal pendapatan (revenue), dan status settlement.


Berikut adalah representasi visual diagram komponen sistem VeriText AI:

![Component Diagram](diagrams/exported/Component%20Diagram.png)

Tabel 3.4: Katalog Antarmuka Komponen (Provided & Required Interfaces)
| Komponen | Provided Interface | Required Interface | Deskripsi Peran Komponen |
| :--- | :--- | :--- | :--- |
| Frontend Web Client | IWebUI (HTTP/HTML5) | IAuthAPI, IBillingAPI, IReportAPI | Antarmuka pengguna interaktif Vue 3.5 yang menyajikan halaman dasbor dan Split-Screen Studio Workspace. |
| Auth & RBAC Service | IAuthAPI | IDatabaseSession | Menangani alokasi token JWT, refresh token, otentikasi Google OAuth, dan verifikasi hak akses peran. |
| Document Preprocessor | IDocValidation | IStorageEngine | Memvalidasi integritas berkas masukan, mengekstrak teks murni, dan melakukan segmentasi kalimat. |
| Hybrid Audit Orchestrator | IPipelineDispatch | ISemanticSearch, IAssistantContext | Mengorkestrasikan eksekusi bertingkat Step 1 Winnowing, Step 2 SBERT/IndoBERT, dan Step 3 Stilometri/Gemini. |
| Semantic Vector Engine | ISemanticSearch | IpgvectorSQL | Menghitung vektor dense embedding 384-d dan mengeksekusi kueri tetangga terdekat pada indeks HNSW pgvector. |
| Academic Assistant | IAssistantContext | IGeminiAPI, IDatabaseSession | Menerapkan guardrail etika ilmiah, menghasilkan 3 opsi variasi parafrase, dan memperbarui teks in-place. |
| Billing & Wallet Service | IBillingAPI | IMidtransSnap, ITransactionDDL | Mengelola saldo token komputasi, pembuatan invoice, dan pemrosesan webhook pembayaran Midtrans yang atomik. |
| Report & Certificate | IReportAPI | IWeasyPrintPDF, IQRVerifier | Menghasilkan laporan resmi PDF bertanda tangan QR Code dan menyediakan portal verifikasi sertifikat publik. |
| Admin Telemetry Service | IAdminMonitoring | IReadOnlySELECT | Menyediakan dasbor statistik layanan, telemetri antrean worker, dan log transaksi moneter (100% GET). |

3.5. Communication Interface

3.5.1. Standar REST API
Seluruh antarmuka eksternal VeriText AI menggunakan protokol komunikasi REST API berbasis HTTPS dengan format pertukaran data JSON (Content-Type: application/json).
1. Format Respons Sukses Standar:
```json
{
  "success": true,
  "data": {},
  "message": "Deskripsi status operasi yang berhasil",
  "meta": {
    "timestamp": "2026-06-24T10:00:00Z",
    "version": "1.0",
    "request_id": "c1f7b8a2-3e4d-4a1b-9f2c-5d8e7a6b5c4d"
  }
}
```
2. Format Respons Error Standar:
```json
{
  "success": false,
  "error": {
    "code": "CHAT_001",
    "message": "Permintaan ditolak: Melanggar batas etika akademik (Academic Assistant Guardrail).",
    "details": null
  },
  "meta": {
    "timestamp": "2026-06-24T10:00:01Z",
    "version": "1.0",
    "request_id": "c1f7b8a2-3e4d-4a1b-9f2c-5d8e7a6b5c4d"
  }
}
```

3.5.2. Katalog Endpoint API
Katalog endpoint API disusun ke dalam tabel 6 kolom terperinci yang mencakup metode HTTP, jalur endpoint, kebutuhan autentikasi, representasi skema request body, skema response, dan deskripsi fungsi bisnis yang dikelompokkan per sub-modul layanan:

3.5.2.1. Modul Autentikasi dan Profil Akun
Tabel 3.5: Endpoint API Modul Autentikasi dan Profil Akun
| Method | Endpoint | Auth | Request Body | Response | Deskripsi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| POST | /api/v1/auth/register | Publik | `{"email": "str", "password": "str", "full_name": "str"}` | `{"user_id": "uuid", "role": "FREE", "wallet": {"balance": 5, "ai_trial_remaining": 3}}` | Registrasi akun baru secara mandiri, otomatis alokasi 5 Token & 3x Kuota Trial. |
| POST | /api/v1/auth/login | Publik | `{"email": "str", "password": "str"}` | `{"access_token": "jwt", "token_type": "bearer", "user": {...}}` | Autentikasi kredensial email & kata sandi, terbitkan Access Token JWT dan HttpOnly Refresh Cookie. |
| POST | /api/v1/auth/google | Publik | `{"id_token": "str"}` | `{"access_token": "jwt", "user": {...}}` | Autentikasi Single Sign-On (SSO) Google OAuth 2.0 dan sinkronisasi akun. |
| POST | /api/v1/auth/refresh | Refresh Cookie | None | `{"access_token": "jwt", "token_type": "bearer"}` | Rotasi refresh token dan penerbitan Access Token JWT baru yang valid. |
| POST | /api/v1/auth/logout | Bearer JWT | None | `{"message": "Logout berhasil"}` | Pencabutan refresh token dari database dan pembersihan cookie sesi peramban. |
| GET | /api/v1/users/me | Bearer JWT | None | `{"id": "uuid", "email": "str", "role": "FREE/PREMIUM", "wallet": {"balance": 15, "ai_trial_remaining": 3}}` | Mengambil profil pengguna aktif, sisa saldo token komputasi, dan kuota trial AI. |
| PUT | /api/v1/users/profile | Bearer JWT | `{"full_name": "str"}` | `{"id": "uuid", "full_name": "str", "updated_at": "datetime"}` | Memperbarui informasi nama lengkap profil pengguna dengan sanitasi anti-XSS. |
| POST | /api/v1/users/change-password | Bearer JWT | `{"old_password": "str", "new_password": "str"}` | `{"message": "Kata sandi berhasil diperbarui"}` | Memvalidasi kata sandi lama, menyimpan hash Bcrypt baru, dan mencabut sesi aktif lainnya. |

3.5.2.2. Modul Dokumen dan Pra-pemrosesan
Tabel 3.6: Endpoint API Modul Dokumen dan Pra-pemrosesan
| Method | Endpoint | Auth | Request Body | Response | Deskripsi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| POST | /api/v1/documents/upload | Bearer JWT | Multipart/form-data: `file: UploadFile` atau `text: str` | `{"document_id": "uuid", "word_count": 2150, "token_cost": 1, "is_valid": true}` | Mengunggah berkas naskah (.pdf, .docx, .txt maks 15 MB) atau input teks, validasi MIME, ekstraksi teks, dan hitung estimasi biaya token. |
| GET | /api/v1/documents | Bearer JWT | None (Query: `page=1&limit=20`) | `{"total": 12, "items": [{"id": "uuid", "title": "str", "word_count": 2150, "token_cost": 1}]}` | Mengambil daftar seluruh riwayat naskah yang pernah diperiksa oleh pengguna aktif. |
| GET | /api/v1/documents/{id} | Bearer JWT | None | `{"id": "uuid", "title": "str", "word_count": 2150, "token_cost": 1, "created_at": "datetime"}` | Mengambil detail metadata naskah spesifik yang dimiliki pengguna aktif. |
| DELETE | /api/v1/documents/{id} | Bearer JWT | None | `{"document_id": "uuid", "status": "PERMANENTLY_DELETED"}` | Mengeksekusi hard-delete cascading berkas fisik, rekaman naskah, audit, dan riwayat chat (kepatuhan UU PDP). |

3.5.2.3. Modul Pipeline Audit Deteksi Plagiarisme
Tabel 3.7: Endpoint API Modul Pipeline Audit Deteksi Plagiarisme
| Method | Endpoint | Auth | Request Body | Response | Deskripsi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| POST | /api/v1/audits/execute | Bearer JWT | `{"document_id": "uuid"}` | `{"task_id": "uuid", "status": "QUEUED", "tokens_deducted": 1, "new_balance": 4}` | Memotong saldo token secara atomik dan mendaftarkan tugas pemindaian 3-tahap ke antrean Celery Redis. |
| GET | /api/v1/audits/{task_id}/status | Bearer JWT | None | `{"task_id": "uuid", "status": "PROCESSING", "progress_pct": 65, "current_step": "Step 2: Semantic SBERT"}` | Endpoint smart polling untuk memantau status penyelesaian komputasi audit naskah secara asinkron. |
| GET | /api/v1/audits/{id}/report | Bearer JWT | None | `{"report_id": "uuid", "composite_score": 18.5, "tiers": {"lexical": 22.0, "semantic": 15.0, "stylometric": 8.0}, "sentences": [...], "sources": [...]}` | Mengambil data lengkap laporan naskah beranotasi Interactive Heatmap 3-tier untuk Split-Screen Studio Workspace. |

3.5.2.4. Modul AI Chatbot Asisten dan Parafrase Instan
Tabel 3.8: Endpoint API Modul AI Chatbot Asisten dan Parafrase Instan
| Method | Endpoint | Auth | Request Body | Response | Deskripsi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| POST | /api/v1/chat/message | Bearer JWT | `{"document_id": "uuid", "sentence_id": "uuid", "prompt": "str"}` | `{"message_id": "uuid", "session_id": "uuid", "role": "ASSISTANT", "content": "str", "ai_trial_remaining": 2, "balance": 4}` | Mengirim pertanyaan konsultasi naskah ber-Academic Guardrail ke Dual-Engine LLM Gateway. |
| POST | /api/v1/chat/paraphrase | Bearer JWT | `{"sentence_id": "uuid", "mode": "SENTENCE/PARAGRAPH/FULL_PAGE"}` | `{"sentence_id": "uuid", "mode": "SENTENCE", "variations": [{"option_id": 1, "style": "Formal Akademik", "text": "str", "predicted_score": 8.5}, ...]}` | Menghasilkan 3 variasi parafrase ilmiah lengkap dengan prediksi penurunan persentase kemiripan. |
| POST | /api/v1/chat/apply-paraphrase | Bearer JWT | `{"sentence_id": "uuid", "selected_text": "str"}` | `{"sentence_id": "uuid", "current_text": "str", "match_type": "RESOLVED_GREEN", "new_similarity": 6.2, "new_composite_score": 14.1, "is_modified": true}` | Mengganti kalimat di naskah secara in-place, menghitung ulang skor secara real-time, dan mengubah warna sorotan menjadi Hijau. |

3.5.2.5. Modul Pelaporan, Sertifikasi dan Verifikasi Publik
Tabel 3.9: Endpoint API Modul Pelaporan, Sertifikasi dan Verifikasi Publik
| Method | Endpoint | Auth | Request Body | Response | Deskripsi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| GET | /api/v1/reports/{id}/download | Premium User | None | Binary stream: `application/pdf` | Mengunduh Laporan Audit Resmi berformat PDF beresolusi cetak lengkap dengan stempel digital dan Dynamic QR Code. |
| GET | /api/v1/reports/verify/{uuid} | Publik | None | `{"valid": true, "certificate_uuid": "uuid", "document_title": "str", "author": "str", "audit_date": "datetime", "composite_score": 14.1}` | Portal validasi publik tanpa login untuk memverifikasi keaslian laporan dan integritas sertifikat via URL QR. |

3.5.2.6. Modul Monetisasi Billing dan Pemantauan Admin
Tabel 3.10: Endpoint API Modul Monetisasi Billing dan Pemantauan Admin
| Method | Endpoint | Auth | Request Body | Response | Deskripsi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| POST | /api/v1/billing/checkout | Bearer JWT | `{"purchase_scheme": "BY_TOKEN/BY_PACKAGE", "token_amount": 15, "package_type": "STARTER"}` | `{"order_id": "str", "gross_amount": 25000, "snap_token": "str", "snap_redirect_url": "str"}` | Membuat transaksi pembelian token (By Token / By Paket Token) dan meminta Snap Token ke Midtrans. |
| POST | /api/v1/billing/webhook | Midtrans SHA-512 | `{"order_id": "str", "status_code": "200", "gross_amount": "25000.00", "signature_key": "str", "transaction_status": "settlement"}` | `{"status": "ok"}` | Menangkap webhook Midtrans, validasi signature SHA-512, tambah saldo token atomik, auto-upgrade ke PREMIUM. |
| GET | /api/v1/billing/invoices | Bearer JWT | None | `{"items": [{"order_id": "str", "amount": 25000, "status": "SETTLEMENT", "pdf_url": "str"}]}` | Menampilkan riwayat transaksi pembayaran dan tautan unduh berkas Invoice PDF resmi. |
| GET | /api/v1/admin/analytics | Admin Read-Only | None | `{"total_documents": 1420, "avg_similarity": 16.4, "total_revenue": 8450000, "active_users": 640}` | Dasbor statistik analitik global penggunaan sistem (murni GET / 100% read-only). |
| GET | /api/v1/admin/transactions | Admin Read-Only | None (Query: `limit=50`) | `{"total_revenue": 8450000, "items": [{"order_id": "str", "gross_amount": 25000, "status": "SETTLEMENT"}]}` | Log riwayat transaksi pembayaran Midtrans secara real-time (murni GET / 100% read-only). |
| GET | /api/v1/admin/system-health | Admin Read-Only | None | `{"celery_workers": 4, "queue_depth": 2, "redis_mem_mb": 145, "pgvector_latency_ms": 18}` | Telemetri kesehatan infrastruktur Celery worker, Redis, dan pgvector (murni GET / 100% read-only). |
| GET | /api/v1/admin/audit-logs | Admin Read-Only | None (Query: `limit=100`) | `{"items": [{"timestamp": "datetime", "actor": "str", "action": "LOGIN_FAILURE", "ip": "str"}]}` | Meninjau rekaman log audit keamanan sistem untuk kepatuhan privasi (murni GET / 100% read-only). |

3.5.3. Protokol Keamanan Webhook Midtrans
Untuk menjamin keamanan pembaruan status transaksi moneter dan menghindari serangan replay attack atau pemalsuan data:
1. Midtrans mengirimkan HTTP POST notifikasi ke /api/v1/billing/webhook saat status pembayaran berubah (settlement, capture, expire, cancel).
2. Sistem mengekstrak parameter kritis: order_id, status_code, gross_amount, dan signature_key.
3. Sistem menghitung ulang signature pembanding menggunakan formula SHA-512:
   Signature = SHA512(order_id + status_code + gross_amount + MIDTRANS_SERVER_KEY)
4. Jika signature yang dihitung tidak cocok secara eksak dengan signature_key yang dikirimkan Midtrans, sistem langsung menolak request dengan kode HTTP 403 Forbidden dan mencatat insiden keamanan pada audit_logs.
5. Jika signature valid dan status adalah settlement atau capture:
   - Sistem membuka transaksi database atomik dengan baris terkunci (SELECT * FROM invoices WHERE order_id = :order_id FOR UPDATE).
   - Memastikan status invoice belum SETTLEMENT (idempotensi transaksi).
   - Menambahkan jumlah saldo token ke tabel token_wallets.
   - Mengubah status peran akun pengguna pada tabel users menjadi 'PREMIUM' (user.role = 'PREMIUM').
   - Memperbarui status invoice menjadi 'SETTLEMENT'.
   - Mengembalikan respons HTTP 200 OK ke Midtrans.

3.5.4. Mekanisme Smart Polling
Untuk memantau perkembangan status pemrosesan naskah yang dieksekusi secara asinkron oleh Celery tanpa membebani server dan jaringan, frontend Vue 3 mengimplementasikan mekanisme Smart Polling adaptif:
```typescript
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

export function useAuditPolling(taskId: string, onCompleted: (reportId: string) => void) {
  const status = ref<'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED'>('QUEUED');
  const progressPct = ref(0);
  let timer: ReturnType<typeof setTimeout> | null = null;

  const pollStatus = async () => {
    try {
      const response = await axios.get(`/api/v1/audits/${taskId}/status`);
      const data = response.data.data;
      status.value = data.status;
      progressPct.value = data.progress_pct;

      if (data.status === 'COMPLETED') {
        onCompleted(data.report_id);
        return;
      }
      if (data.status === 'FAILED' || data.status === 'CANCELLED') {
        return;
      }

      // Interval adaptif: 3 detik jika QUEUED, 1.5 detik jika PROCESSING
      const interval = data.status === 'QUEUED' ? 3000 : 1500;
      timer = setTimeout(pollStatus, interval);
    } catch (error) {
      console.error('Polling error:', error);
      timer = setTimeout(pollStatus, 5000);
    }
  };

  onMounted(() => pollStatus());
  onUnmounted(() => { if (timer) clearTimeout(timer); });

  return { status, progressPct };
}
```

3.5.5. Katalog Kode Error Terpusat
Tabel 3.11: Katalog Kode Error Sistem VeriText AI
| Kode Error | HTTP Status | Deskripsi | Endpoint Terkait |
| :--- | :--- | :--- | :--- |
| AUTH_001 | 401 Unauthorized | Email atau kata sandi tidak valid. | POST /api/v1/auth/login |
| AUTH_002 | 401 Unauthorized | Access token JWT telah kedaluwarsa atau signature tidak valid. | Seluruh endpoint terproteksi |
| AUTH_003 | 403 Forbidden | Peran pengguna tidak memiliki hak akses (RBAC violation). | /api/v1/admin/*, /reports/download |
| DOC_001 | 413 Payload Too Large | Ukuran berkas naskah yang diunggah melebihi batas maksimum 15 MB. | POST /api/v1/documents/upload |
| DOC_002 | 422 Unprocessable Entity | Format berkas tidak didukung (hanya menerima .pdf, .docx, .txt). | POST /api/v1/documents/upload |
| DOC_003 | 422 Unprocessable Entity | Naskah memiliki kurang dari 50 kata (tidak memenuhi syarat analisis). | POST /api/v1/documents/upload |
| DOC_004 | 404 Not Found | Dokumen yang diminta tidak ditemukan atau bukan milik pengguna aktif. | GET/DELETE /api/v1/documents/{id} |
| AUDIT_001 | 402 Payment Required | Saldo token tidak mencukupi untuk melakukan pemeriksaan naskah. | POST /api/v1/audits/execute |
| AUDIT_002 | 400 Bad Request | Batas kata Free User terlampaui (maksimal 2.500 kata per dokumen). | POST /api/v1/audits/execute |
| CHAT_001 | 400 Bad Request | Pelanggaran Guardrail: Permintaan di luar etika akademik ditolak. | POST /api/v1/chat/message |
| CHAT_002 | 402 Payment Required | Batas kuota Trial AI Chatbot/Parafrase (3x) untuk Free User telah habis. | POST /api/v1/chat/* |
| BILL_001 | 403 Forbidden | Verifikasi signature SHA-512 webhook Midtrans gagal (untrusted source). | POST /api/v1/billing/webhook |
| BILL_002 | 404 Not Found | Nomor order transaksi pembayaran tidak ditemukan di basis data. | POST /api/v1/billing/webhook |
| BILL_003 | 400 Bad Request | Transaksi pembayaran telah kedaluwarsa atau dibatalkan oleh pengguna. | POST /api/v1/billing/checkout |
| BILL_004 | 400 Bad Request | Jumlah token yang dibeli kurang dari batas minimum pembelian (min. 5 token). | POST /api/v1/billing/checkout |
| REP_001 | 403 Forbidden | Unduh laporan PDF resmi hanya dapat diakses oleh akun Premium User. | GET /api/v1/reports/{id}/download |
| REP_002 | 404 Not Found | Kode QR atau sertifikat verifikasi keaslian naskah tidak valid/dihapus. | GET /api/v1/reports/verify/{uuid} |

3.6. Desain Antarmuka (UI/UX)
Antarmuka pengguna VeriText AI dirancang dengan filosofi Split-Screen Studio Workspace yang mengutamakan kepadatan data ilmiah, kejelasan navigasi, dan kenyamanan peninjauan dokumen dalam waktu lama tanpa distraksi visual non-akademik:
1. Top Summary Bar (Tinggi 64px): Menampilkan judul naskah, jumlah kata, indikator persentase skor komposit total, rincian skor per tier (Leksikal, Semantik, AI), sisa saldo token pengguna, serta tombol aksi cepat (Unduh PDF Resmi, Parafrase Halaman).
2. Kolom Kiri - Interactive Heatmap Viewer (60% Lebar Layar): Menampilkan naskah asli pengguna di atas lembar putih bersih. Teks yang terdeteksi plagiat disorot menggunakan skema warna semantik:
   - MERAH (#DC2626 - Tier 1 Leksikal): Indikasi copy-paste verbatim tingkat tinggi.
   - ORANYE (#EA580C - Tier 2 Semantik): Indikasi parafrase konsep kalimat.
   - KUNING (#CA8A04 - Tier 3 Stilometri / AI): Indikasi struktur sintaksis anomali buatan AI.
   - HIJAU (#16A34A - Resolved): Indikasi kalimat yang telah berhasil diperbaiki melalui parafrase instan.
   Saat kalimat yang disorot diklik, muncul popover aksi kontekstual: [Parafrase Kalimat] [Parafrase Paragraf] [Bandingkan dengan Sumber Asli].
3. Kolom Kanan - Panel Tabular 2-in-1 (40% Lebar Layar):
   - Tab 1: Matched Sources: Menampilkan daftar karya ilmiah dan sumber web yang cocok lengkap dengan persentase kontribusi kemiripan, judul jurnal, nama penulis, tautan DOI/URL resmi, serta kartu perbandingan teks berdampingan (Side-by-Side Comparison).
   - Tab 2: AI Asisten Naskah & Parafrase: Menampilkan panel percakapan interaktif ber-guardrail untuk konsultasi perbaikan naskah, tombol aksi cepat parafrase, serta tampilan 3 opsi variasi kalimat ilmiah dengan tombol aksi 'Terapkan ke Naskah'.
4. Standar Tipografi: Menggunakan jenis huruf Plus Jakarta Sans untuk elemen antarmuka dan tombol, Inter untuk keterbacaan teks paragraf naskah ilmiah, serta JetBrains Mono untuk tampilan kode hash, angka token, dan formula komputasi.


BAB IV
PERANCANGAN UML

4.1. Class Diagram
Class Diagram VeriText AI memodelkan arsitektur lapisan domain model (domain layer) dan persistensi basis data yang terdiri atas 13 entitas inti sistem. Setiap kelas memiliki atribut data dengan tipe data yang terdefinisi ketat, relasi asosiasi dan multiplisitas yang tepat, serta method bisnis utama. Tidak terdapat method mutasi bagi peran Administrator atau Dosen karena seluruh operasi pengguna berjalan secara otomatis mandiri (Self-Service SaaS) dan peran Admin bersifat 100% Read-Only.

Berikut adalah representasi visual diagram kelas sistem VeriText AI:

![Class Diagram](diagrams/exported/Class%20Diagram.png)

Tabel 4.1: Penjelasan 13 Entitas Domain pada Class Diagram
| Nama Entitas | Multiplisitas & Relasi | Peran dan Tanggung Jawab Domain |
| :--- | :--- | :--- |
| User | 1 -- 1 TokenWallet, 1 -- * Document, 1 -- * Invoice, 1 -- * ChatSession | Entitas pengguna utama sistem; menyimpan identitas akun, peran ('FREE'/'PREMIUM'/'ADMIN'), dan status keaktifan. |
| Session | * -- 1 User | Menyimpan sesi autentikasi pengguna aktif beserta hash refresh token dan waktu kedaluwarsa. |
| TokenWallet | 1 -- 1 User, 1 -- * TokenTransaction | Menyimpan saldo kredit token komputasi, sisa kuota coba AI (ai_trial_remaining = 3), dan sub-kredit chat. |
| Invoice | * -- 1 User | Mencatat tagihan pembayaran Midtrans Snap, skema pembelian (By Token / By Paket), dan status settlement. |
| TokenTransaction | * -- 1 TokenWallet | Buku besar (ledger) mutasi kredit dan debet saldo token yang bersifat append-only dan immutable. |
| Document | * -- 1 User, 1 -- * AuditTask, 1 -- * ChatSession | Menyimpan metadata berkas naskah yang diunggah, jumlah kata (word_count), dan estimasi biaya token. |
| AuditTask | * -- 1 Document, 1 -- * AuditSentence, 1 -- 1 AuditReport | Mengelola status pengerjaan pemeriksaan plagiarisme asinkron dan mencatat skor komposit serta waktu eksekusi. |
| AuditSentence | * -- 1 AuditTask | Menyimpan potongan kalimat individual naskah, tipe sorotan warna ('NONE'/'RED'/'ORANGE'/'YELLOW'/'RESOLVED_GREEN'), dan teks terkini. |
| AuditReport | 1 -- 1 AuditTask | Menyimpan rekaman sertifikat laporan resmi, UUID sertifikat unik, URL kode QR publik, dan lokasi berkas PDF. |
| ChatSession | * -- 1 User, * -- 1 Document, 1 -- * ChatMessage | Mengelola sesi percakapan asisten ilmiah yang terikat pada naskah dokumen tertentu. |
| ChatMessage | * -- 1 ChatSession, * -- 0..1 AuditSentence | Menyimpan riwayat pesan, mode parafrase (SENTENCE/PARAGRAPH/FULL_PAGE), 3 opsi variasi JSONB, dan status terapan. |
| CorpusDocument | 1 -- * DocumentChunk | Menyimpan metadata karya ilmiah pembanding yang diakuisisi otomatis dari OpenAlex, DOAJ, dan Semantic Scholar. |
| DocumentChunk | * -- 1 CorpusDocument | Menyimpan potongan teks korpus beserta dense vector embedding 384 dimensi berindeks HNSW pgvector. |

4.2. Data Flow Diagram (DFD)
Data Flow Diagram memodelkan perpindahan dan transformasi aliran data dalam sistem secara berjenjang dari gambaran konteks tingkat tinggi hingga rincian proses komputasi internal.

4.2.1. DFD Level 0 – Context Diagram
Context Diagram menggambarkan sistem VeriText AI sebagai satu lingkaran proses tunggal yang berinteraksi dengan enam entitas eksternal: Free User, Premium User, Admin (100% Read-Only), Midtrans Payment Gateway, Dual-Scope Academic APIs (OpenAlex, DOAJ, Crossref), dan Google Gemini AI API.

![DFD Level 0](diagrams/exported/DFD0-Context%20Diagram.png)

4.2.2. DFD Level 1 – System Overview
DFD Level 1 mendekomposisi sistem menjadi tujuh proses utama yang berinteraksi dengan enam data store (D1 Users & Wallets, D2 Documents & Tasks, D3 Corpus & Embeddings, D4 Reports & Certificates, D5 ChatSessions & Messages, D6 Invoices & Transactions):
- Proses 1.0: Autentikasi & Akun
- Proses 2.0: Unggah & Validasi Naskah
- Proses 3.0: Deteksi Hybrid 3-Tahap
- Proses 4.0: AI Chatbot & Parafrase Instan
- Proses 5.0: Pelaporan & QR PDF
- Proses 6.0: Token & Midtrans Billing
- Proses 7.0: Monitoring Layanan (Admin Read-Only)

![DFD Level 1](diagrams/exported/DFD1-System%20Overview.png)

4.2.3. DFD Level 2 – Deteksi Plagiarisme Hybrid dan AI Chatbot
DFD Level 2 merinci proses 3.0 (Deteksi Plagiarisme) dan proses 4.0 (AI Chatbot) menjadi sub-proses komputasi detail:
- Sub-proses 3.1: Segmentasi Kalimat & Normalisasi Teks
- Sub-proses 3.2: Step 1 Winnowing Lexical Fingerprinting
- Sub-proses 3.3: Step 2 SBERT Multilingual & pgvector HNSW
- Sub-proses 3.4: Step 3 Stilometri & Gemini Contextual AI Judge
- Sub-proses 3.5: Agregasi Skor Komposit & Heatmap Multi-Warna
- Sub-proses 4.1: Academic Guardrail & Prompt Validator
- Sub-proses 4.2: Generator 3 Opsi Parafrase Kalimat/Paragraf
- Sub-proses 4.3: Terapkan ke Naskah & Hitung Ulang Skor In-Place

![DFD Level 2](diagrams/exported/DFD2-Deteksi%20Plagiarisme%20Hybrid%20dan%20AI%20Chatbot.png)

4.3. Activity Diagram (Breakdown Per Use Case AD1 s/d AD11)
Sub-bab ini menyajikan 11 Activity Diagram bergaya swimlane yang berkorespondensi satu-ke-satu dengan 11 Use Case pada dokumen SRS VeriText AI. Seluruh diagram dirancang dengan tata letak swimlane bersih, bebas dari tumpang tindih elemen (zero collision), dan menggunakan notasi UML standar hitam-putih.

### AD1: Aktivitas Masuk dan Registrasi Akun (UC-01)
Diagram ini memodelkan alur autentikasi pengguna menggunakan metode Email/Password maupun Google OAuth 2.0. Diagram memperlihatkan percabangan verifikasi format, pencocokan hash Bcrypt, penolakan kredensial salah, penukaran auth code Google, hingga penerbitan token JWT dan alokasi otomatis 5 Token & 3x kuota trial asisten AI.

![AD1: Masuk dan Registrasi Akun](diagrams/exported/AD1-Masuk%20dan%20Registrasi%20Akun.png)

### AD2: Aktivitas Kelola Profil dan Kata Sandi (UC-02)
Diagram ini memodelkan alur pengaturan akun oleh pengguna yang terbagi ke dalam dua sub-alur terpisah: (1) Pembaruan Nama Lengkap Profil melalui sanitasi anti-XSS, dan (2) Pembaruan Kata Sandi Akun melalui verifikasi hash Bcrypt kata sandi lama, penolakan kata sandi lama yang salah, dan enkripsi kata sandi baru yang otomatis mencabut seluruh sesi aktif lainnya.

![AD2: Kelola Profil dan Kata Sandi](diagrams/exported/AD2-Kelola%20Profil%20dan%20Kata%20Sandi.png)

### AD3: Aktivitas Unggah dan Validasi Naskah (UC-03)
Diagram ini memodelkan alur penerimaan dokumen (.pdf, .docx, .txt) atau teks langsung. Sistem memvalidasi ukuran berkas (<= 15 MB) dan magic MIME type, mengekstrak teks bersih, menghitung jumlah kata, membatasi naskah Free User maksimal 2.500 kata (atau memunculkan paywall), serta menghitung biaya token konsumsi sesuai formula min(5, ceil(kata/2500)).

![AD3: Unggah dan Validasi Naskah](diagrams/exported/AD3-Unggah%20dan%20Validasi%20Naskah.png)

### AD4: Aktivitas Deteksi Plagiarisme Hybrid 3-Tahap (UC-04)
Diagram ini memodelkan alur eksekusi deteksi plagiarisme cerdas secara asinkron di latar belakang oleh worker Celery: pemotongan token atomik, eksekusi Step 1 Winnowing leksikal (Tag Merah), Step 2 Semantic SBERT + IndoBERT pada pgvector HNSW (Tag Oranye), Step 3 Stilometri dan Gemini AI Judge (Tag Kuning), agregasi skor komposit (0.50 : 0.35 : 0.15), hingga penampilan hasil akhir pada Interactive Heatmap.

![AD4: Deteksi Plagiarisme Hybrid 3-Tahap](diagrams/exported/AD4-Deteksi%20Plagiarisme%20Hybrid%203-Tahap.png)

### AD5: Aktivitas Tinjau Laporan dan Heatmap Kemiripan (UC-05)
Diagram ini memodelkan alur peninjauan laporan di Split-Screen Studio Workspace: perenderan heatmap dokumen naskah di sebelah kiri, daftar sumber kecocokan di sebelah kanan, penyaringan highlight warna (Merah, Oranye, Kuning), dan pembukaan popover Side-by-Side Comparison saat kalimat bermasalah diklik.

![AD5: Tinjau Laporan dan Heatmap Kemiripan](diagrams/exported/AD5-Tinjau%20Laporan%20dan%20Heatmap%20Kemiripan.png)

### AD6: Aktivitas Konsultasi Naskah via AI Chatbot (UC-06)
Diagram ini memodelkan alur tanya-jawab bimbingan ilmiah di panel kanan workspace: pemeriksaan kuota (evaluasi status trial 3x untuk Free User / saldo token untuk Premium User), evaluasi Academic Assistant Guardrail (menolak instruksi off-topic atau non-akademik), pengiriman konteks ke Dual-Engine LLM Gateway (Gemini 2.5 Flash / DeepSeek v4.1 Flash via 9Router), pemotongan kuota, dan penampilan respon konsultasi di chat panel.

![AD6: Konsultasi Naskah via AI Chatbot](diagrams/exported/AD6-Konsultasi%20Naskah%20via%20AI%20Chatbot.png)

### AD7: Aktivitas Parafrase Instan dan Cek Ulang Kalimat (UC-07)
Diagram ini memodelkan alur perbaikan naskah interaktif: pemilihan mode parafrase (Per Kalimat, Per Paragraf, Seluruh Halaman), penghasilan 3 opsi variasi ilmiah oleh AI, pemilihan variasi terbaik oleh pengguna, penerapan teks baru secara in-place, perhitungan ulang skor kemiripan secara real-time, dan perubahan sorotan menjadi Hijau.

![AD7: Parafrase Instan dan Cek Ulang Kalimat](diagrams/exported/AD7-Parafrase%20Instan%20dan%20Cek%20Ulang%20Kalimat.png)

### AD8: Aktivitas Unduh Laporan PDF dan Verifikasi QR (UC-08)
Diagram ini memodelkan dua sub-alur sertifikasi: (1) Pengunduhan Laporan PDF resmi yang memeriksa status Premium User (menolak Free User dengan paywall) dan mengompilasi laporan ber-QR Code dengan WeasyPrint, dan (2) Verifikasi keaslian dokumen publik melalui pemindaian QR Code yang memeriksa keabsahan UUID sertifikat di database.

![AD8: Unduh Laporan PDF dan Verifikasi QR](diagrams/exported/AD8-Unduh%20Laporan%20PDF%20dan%20Verifikasi%20QR.png)

### AD9: Aktivitas Kelola dan Hapus Riwayat Naskah (UC-09)
Diagram ini memodelkan hak kendali privasi data pengguna sesuai Undang-Undang Perlindungan Data Pribadi (UU PDP No. 27/2022): peninjauan daftar naskah, konfirmasi penghapusan permanen, eksekusi hard-delete cascade (menghapus berkas fisik, task, highlight, dan sesi percakapan chat), serta pencatatan peristiwa penghapusan pada log audit keamanan.

![AD9: Kelola dan Hapus Riwayat Naskah](diagrams/exported/AD9-Kelola%20dan%20Hapus%20Riwayat%20Naskah.png)

### AD10: Aktivitas Beli Kuota Token dan Upgrade Premium (UC-10)
Diagram ini memodelkan alur monetisasi dan top-up token: pemilihan skema pembelian (By Token eceran atau By Paket Token), pembuatan invoice PENDING, pembukaan popup pembayaran Midtrans Snap, pembayaran pengguna (QRIS, VA, Kartu), pengiriman webhook notifikasi Midtrans, verifikasi signature SHA-512, penambahan saldo token atomik, dan peningkatan otomatis status akun menjadi Premium User.

![AD10: Beli Kuota Token dan Upgrade Premium](diagrams/exported/AD10-Beli%20Kuota%20Token%20dan%20Upgrade%20Premium.png)

### AD11: Aktivitas Pantau Dasbor Analitik dan Log Transaksi (UC-11)
Diagram ini memodelkan aktivitas observasi administrator yang murni bersifat Read-Only: login akun admin, validasi hak akses role == 'ADMIN', eksekusi kueri agregasi SELECT pada basis data, penyajian telemetri kesehatan worker Celery, serta peninjauan tabel log transaksi moneter Midtrans tanpa hak melakukan manipulasi data pengguna.

![AD11: Pantau Dasbor Analitik dan Log Transaksi](diagrams/exported/AD11-Pantau%20Dasbor%20Analitik%20dan%20Log%20Transaksi.png)

4.4. Sequence Diagram (Breakdown Per Use Case SD1 s/d SD11)
Sub-bab ini menyajikan 11 Sequence Diagram UML 2.0 yang memperlihatkan urutan kronologis pertukaran pesan (pesan sinkron, pesan asinkron, pesan balik/return, dan self-call) antar komponen arsitektur sistem untuk setiap use case.

### SD1: Sequence Diagram Masuk dan Registrasi Akun (UC-01)
Diagram ini memodelkan interaksi antara User, AuthView (Vue 3), AuthAPI (FastAPI), AuthService, PostgreSQL, dan Google OAuth API dalam alur autentikasi email dan Google OAuth.

![SD1: Masuk dan Registrasi Akun](diagrams/exported/SD1-Masuk%20dan%20Registrasi%20Akun.png)

### SD2: Sequence Diagram Kelola Profil dan Kata Sandi (UC-02)
Diagram ini memodelkan interaksi pembaruan profil pengguna serta penggantian kata sandi yang melibatkan UserService, hashing Bcrypt, dan pencabutan sesi aktif pada basis data PostgreSQL.

![SD2: Kelola Profil dan Kata Sandi](diagrams/exported/SD2-Kelola%20Profil%20dan%20Kata%20Sandi.png)

### SD3: Sequence Diagram Unggah dan Validasi Naskah (UC-03)
Diagram ini memodelkan interaksi pengunggahan berkas dokumen ke WorkspaceView, validasi MIME magic oleh DocumentAPI, ekstraksi teks dan penghitungan kata oleh PreprocessorEngine, serta kalkulasi biaya token konsumsi oleh TokenWalletService.

![SD3: Unggah dan Validasi Naskah](diagrams/exported/SD3-Unggah%20dan%20Validasi%20Naskah.png)

### SD4: Sequence Diagram Deteksi Plagiarisme Hybrid 3-Tahap (UC-04)
Diagram ini memodelkan orkestrasi asinkron penuh antara WorkspaceView, AuditOrchestrator, WinnowingEngine (Tier 1), SemanticVectorEngine (Tier 2 pgvector HNSW), StylometricAIEngine (Tier 3 Gemini AI), dan basis data penyimpanan skor laporan.

![SD4: Deteksi Plagiarisme Hybrid 3-Tahap](diagrams/exported/SD4-Deteksi%20Plagiarisme%20Hybrid%203-Tahap.png)

### SD5: Sequence Diagram Tinjau Laporan dan Heatmap Kemiripan (UC-05)
Diagram ini memodelkan pemanggilan data laporan audit dari ReportAPI, perenderan Interactive Heatmap pada WorkspaceView, filter kategori highlight, dan penampilan popover perbandingan sumber berdampingan.

![SD5: Tinjau Laporan dan Heatmap Kemiripan](diagrams/exported/SD5-Tinjau%20Laporan%20dan%20Heatmap%20Kemiripan.png)

### SD6: Sequence Diagram Konsultasi Naskah via AI Chatbot (UC-06)
Diagram ini memodelkan alur interaksi chat ilmiah: pengecekan kuota token/trial, validasi etika akademik oleh AcademicGuardrail, pemanggilan Gemini 2.5 Flash API, pemotongan kuota kredit, dan penampilan pesan di ChatPanel.

![SD6: Konsultasi Naskah via AI Chatbot](diagrams/exported/SD6-Konsultasi%20Naskah%20via%20AI%20Chatbot.png)

### SD7: Sequence Diagram Parafrase Instan dan Cek Ulang Kalimat (UC-07)
Diagram ini memodelkan alur permintaan 3 variasi parafrase ke GeminiAIService, pemilihan variasi oleh pengguna, pembaruan teks in-place oleh AuditOrchestrator, perhitungan ulang skor kalimat, dan pembaruan visual highlight menjadi hijau.

![SD7: Parafrase Instan dan Cek Ulang Kalimat](diagrams/exported/SD7-Parafrase%20Instan%20dan%20Cek%20Ulang%20Kalimat.png)

### SD8: Sequence Diagram Unduh Laporan PDF dan Verifikasi QR (UC-08)
Diagram ini memodelkan dua alur: (1) Otorisasi role Premium User, kompilasi dokumen PDF ber-QR Code dengan ReportGeneratorService, dan pengunduhan file, serta (2) Pemindaian URL QR publik dan verifikasi keabsahan sertifikat pada database.

![SD8: Unduh Laporan PDF dan Verifikasi QR](diagrams/exported/SD8-Unduh%20Laporan%20PDF%20dan%20Verifikasi%20QR.png)

### SD9: Sequence Diagram Kelola dan Hapus Riwayat Naskah (UC-09)
Diagram ini memodelkan alur pemenuhan hak privasi UU PDP: konfirmasi modal pengguna, panggilan DELETE ke DocumentAPI, penghapusan berkas fisik dari storage, penghapusan berantai (cascade delete) task dan chat di PostgreSQL, serta pencatatan audit log.

![SD9: Kelola dan Hapus Riwayat Naskah](diagrams/exported/SD9-Kelola%20dan%20Hapus%20Riwayat%20Naskah.png)

### SD10: Sequence Diagram Beli Kuota Token dan Upgrade Premium (UC-10)
Diagram ini memodelkan transaksi pembayaran digital: pembuatan invoice PENDING, request Snap Token ke Midtrans, pembayaran pengguna via QRIS/VA, penangkapan webhook notifikasi, verifikasi signature SHA-512, penambahan saldo token atomik, peningkatan peran menjadi Premium User, dan smart polling frontend yang mendeteksi status settlement.

![SD10: Beli Kuota Token dan Upgrade Premium](diagrams/exported/SD10-Beli%20Kuota%20Token%20dan%20Upgrade%20Premium.png)

### SD11: Sequence Diagram Pantau Dasbor Analitik dan Log Transaksi (UC-11)
Diagram ini memodelkan pengawasan pasif oleh Admin: otorisasi role == 'ADMIN', kueri agregasi SELECT data statistik audit, kueri data pendapatan transaksi Midtrans, dan inspeksi telemetri antrean worker Celery secara aman tanpa kemampuan mutasi data.

![SD11: Pantau Dasbor Analitik dan Log Transaksi](diagrams/exported/SD11-Pantau%20Dasbor%20Analitik%20dan%20Log%20Transaksi.png)

---

Daftar Pustaka
[1] IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications. New York, NY: IEEE Computer Society, 1998.
[2] IEEE Std 1016-2009, IEEE Standard for Information Technology — Systems Design — Software Design Descriptions. New York, NY: IEEE Computer Society, 2009.
[3] ISO/IEC/IEEE 42010:2011, Systems and software engineering — Architecture description. Geneva, Switzerland: ISO/IEC/IEEE, 2011.
[4] ISO/IEC 25010:2011, Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models. Geneva, Switzerland: ISO/IEC, 2011.
[5] Pemerintah Republik Indonesia, Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP). Lembaran Negara RI Tahun 2022 Nomor 196.
[6] S. Schleimer, D. S. Wilkerson, and A. Aiken, "Winnowing: local algorithms for document fingerprinting," in Proceedings of the 2003 ACM SIGMOD International Conference on Management of Data (SIGMOD '03), San Diego, CA, USA, 2003, pp. 76–85.
[7] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP), Hong Kong, 2019, pp. 3982–3992.
[8] Y. A. Malkov and D. A. Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs," IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 42, no. 4, pp. 824–836, Apr. 2020.
[9] K.-I. Goh and A.-L. Barabasi, "Burstiness and memory in complex systems," Europhysics Letters (EPL), vol. 81, no. 4, p. 48002, 2008.
[10] R. C. Martin, Clean Architecture: A Craftsman's Guide to Software Structure and Design, 1st ed. Prentice Hall, 2017.
[11] Vue.js Core Team, "Vue.js 3.5 Documentation: The Progressive JavaScript Framework," [Online]. Tersedia: https://vuejs.org/guide/introduction.html.
[12] Vite Core Team, "Vite: Next Generation Frontend Tooling," [Online]. Tersedia: https://vite.dev/guide/.
[13] E. San Martin Morote, "Pinia: The intuitive, type safe, and flexible Store for Vue," [Online]. Tersedia: https://pinia.vuejs.org/.
[14] FastAPI Documentation, "FastAPI Framework, High Performance, Easy to Learn, Fast to Code, Ready for Production," [Online]. Tersedia: https://fastapi.tiangolo.com/.
[15] P. Henderson et al., "pgvector: Open-source vector similarity search for Postgres," GitHub repository, 2024. [Online]. Tersedia: https://github.com/pgvector/pgvector.
[16] Celery Project, "Celery: Distributed Task Queue," [Online]. Tersedia: https://docs.celeryq.dev/.
[17] Midtrans API Documentation, "Core API & Snap Payment Gateway Integration Guide," [Online]. Tersedia: https://docs.midtrans.com/.
[18] OWASP Foundation, "OWASP Top Ten Web Application Security Risks," 2021. [Online]. Tersedia: https://owasp.org/Top10/.
[19] Tailwind CSS Documentation, "Tailwind CSS v3 Utility-First Framework," [Online]. Tersedia: https://tailwindcss.com/docs.
[20] Google DeepMind, "Gemini API Documentation: Gemini 2.5 Flash and Search Grounding," [Online]. Tersedia: https://ai.google.dev/docs.
[21] OurResearch, "OpenAlex API: An open and comprehensive catalog of scholarly papers, authors, institutions, and more," [Online]. Tersedia: https://docs.openalex.org/.
[22] WeasyPrint Documentation, "WeasyPrint: The Awesome Document Factory," [Online]. Tersedia: https://weasyprint.org/.
[23] Hugging Face Documentation, "Sentence Transformers: Multilingual Sentence Embeddings," [Online]. Tersedia: https://www.sbert.net/.
[24] SQLAlchemy Documentation, "SQLAlchemy 2.0 ORM with Async Support," [Online]. Tersedia: https://docs.sqlalchemy.org/en/20/.
[25] Redis Documentation, "Redis 7.x: In-memory data structure store," [Online]. Tersedia: https://redis.io/docs/.

---


---

Revision History
| Versi | Tanggal | Penulis | Deskripsi Perubahan |
| :--- | :--- | :--- | :--- |
| 0.1 | 25 September 2026 | Mochammad Azriel Albian Putra | Penyusunan draf awal struktur SDD dan outline bab sesuai acuan IEEE Std 1016-2009. |
| 0.5 | 26 September 2026 | Mochammad Azriel Albian Putra | Penambahan Bab I-III: Pendahuluan, Tinjauan Sistem, Rancangan Lingkungan Aplikasi, dan DDL Basis Data. |
| 0.9 | 27 September 2026 | Mochammad Azriel Albian Putra | Penambahan Bab IV: Class Diagram, DFD Level 0-2, Activity Diagram, dan Sequence Diagram. |
| 1.0 | 28 September 2026 | Mochammad Azriel Albian Putra | Rilis final disetujui: Transformasi penuh ke arsitektur Self-Service SaaS 3-Role (Free, Premium, Admin Read-Only), 3-Step Hybrid AI Pipeline, modul AI Chatbot Asisten Naskah & Parafrase Instan 3-Mode, skema 13 tabel DDL SQL (chat_sessions, chat_messages, token_wallets, invoices), serta penyelarasan penuh tepat 11 Activity Diagram (AD1-AD11) dan 11 Sequence Diagram (SD1-SD11) berkorespondensi satu-ke-satu dengan 11 Use Case dokumen SRS VeriText AI. |
