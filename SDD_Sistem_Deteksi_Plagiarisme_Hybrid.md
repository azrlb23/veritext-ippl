Software Design Document
for
VeriText
Prepared by Mochammad Azriel Albian Putra
11241045
Informatika
Juni 2026

1
Daftar Isi
Daftar Isi................................................................................................................................... 1
Abstrak......................................................................................................................................3
BAB I
PENDAHULUAN.....................................................................................................................4
1.1. Tujuan Software Design Document.............................................................................. 4
1.2. Ruang Lingkup..............................................................................................................5
1.3. Gambaran Dokumen..................................................................................................... 5
1.4. Referensi........................................................................................................................6
BAB II........................................................................................................................................9
TINJAUAN SISTEM............................................................................................................... 9
1. Deskripsi Umum.............................................................................................................. 9
2.2 Fungsi........................................................................................................................... 10
2.3 Konteks dan Latar Belakang........................................................................................ 11
BAB III
RANCANGAN LINGKUNGAN APLIKASI...................................................................... 13
3.1 Lingkungan Perangkat Keras....................................................................................... 13
3.2 Lingkungan Perangkat Lunak...................................................................................... 13
3.2.1 Stack Teknologi Frontend................................................................................................ 13
3.2.2 Stack Teknologi Backend.................................................................................................14
3.2.3 Infrastruktur..................................................................................................................... 15
3.3 Basis Data...................................................................................................................15
3.4 Component Diagram.................................................................................................. 15
3.5 Communication Interface...........................................................................................20
3.6 Desain Antarmuka (UI/UX)........................................................................................ 20
BAB IV
PERANCANGAN UML........................................................................................................ 21
4.1. Class Diagram............................................................................................................. 21
4.1 Class Diagram.....................................................................................................................21
4.2 Data Flow Diagram (DFD)................................................................................................. 22
4.3 Activity Diagram (Breakdown Per Use Case).................................................................... 26
4.4 Sequence Diagram.............................................................................................................. 65
Daftar Pustaka..................................................................................................................................81
Revision History..............................................................................................................................82

2
Abstrak
Dokumen Software Design Document (SDD) ini merupakan representasi rancangan
teknis yang komprehensif, terstruktur, dan menyeluruh dari sistem perangkat lunak
VeriText AI — sebuah platform deteksi plagiarisme cerdas berbasis arsitektur hybrid
multi-tier yang menggabungkan pendekatan lexical fingerprinting dengan kecerdasan
buatan semantik. Dokumen ini ditulis sebagai tindak lanjut formal dan turunan langsung
dari Software Requirements Specification (SRS) VeriText AI versi 1.0 yang telah
disetujui, dengan tujuan utama mentransformasikan seluruh kebutuhan fungsional dan
non-fungsional yang telah didefinisikan di SRS ke dalam rancangan implementasi teknis
yang konkret, dapat dieksekusi, dan siap dijadikan acuan pengembangan oleh tim insinyur
perangkat lunak.
Sistem VeriText AI dirancang berdasarkan filosofi arsitektur Clean Architecture (CA)
berlapis yang memisahkan secara tegas tanggung jawab antara lapisan presentasi (vue.js
14), lapisan logika bisnis (FastAPI + Pydantic v2), lapisan pemrosesan asinkron (Celery
Worker + Redis Broker), dan lapisan persistensi data (PostgreSQL 16 dengan ekstensi
pgvector). Rancangan ini memungkinkan setiap komponen sistem untuk dikembangkan,
diuji, dan diskalakan secara independen tanpa mengorbankan kohesi fungsional sistem
secara keseluruhan. Pemisahan lapisan yang tegas ini merupakan implementasi nyata dari
prinsip Separation of Concerns (SoC) dan Dependency Inversion Principle (DIP) yang
mendukung maintainability jangka panjang sistem.
Inti dari kemampuan deteksi VeriText AI terletak pada desain pipa pemrosesan hybrid
empat tingkat (4-Tier Detection Pipeline) yang diorkestrasikan secara asinkron oleh
worker Celery. Tier 1 mengimplementasikan algoritma Winnowing dengan parameter
k-gram k=5 dan sliding window w=4 menggunakan Rabin-Karp Rolling Hash untuk
mendeteksi penjiplakan leksikal verbatim secara deterministik dengan kompleksitas O(N).
Tier 2 memanfaatkan model Sentence Transformers berbasis arsitektur BERT (model
paraphrase-multilingual-MiniLM-L12-v2) untuk menghasilkan representasi vektor padat
(dense embeddings) 384-dimensi per kalimat, kemudian mengeksekusi pencarian tetangga
terdekat perkiraan (Approximate Nearest Neighbor - ANN) menggunakan struktur indeks
Hierarchical Navigable Small World (HNSW) pada PostgreSQL pgvector guna
mengungkap parafrasa cerdas yang lolos dari deteksi leksikal. Tier 3 menghitung metrik
statistik stilometri berupa Burstiness Score (variasi panjang kalimat) dan Type-Token
Ratio (TTR) untuk mengidentifikasi pola teks yang terindikasi dihasilkan oleh model
bahasa besar (Large Language Model / LLM). Tier 4 mengagregasi skor terbobot dari
ketiga tier dengan bobot 50:35:15 menjadi satu nilai Overall Composite Similarity Index
yang dijadikan landasan anotasi visual Interactive Heatmap tiga warna.
Dari perspektif rancangan antarmuka, SDD ini mendefinisikan sistem desain visual
yang kohesif berbasis komponen shadcn/ui dengan skema warna semantik yang
memvisualisasikan tier pelanggaran: merah (#EF4444) untuk temuan leksikal, oranye
(#F97316) untuk temuan semantik, dan kuning (#EAB308) untuk anomali AI. Model

3
bisnis freemium diimplementasikan melalui integrasi pembayaran Midtrans Snap dalam
mode sandbox, dengan mekanisme penanganan webhook berbasis validasi signature
SHA-512 yang aman. Aspek kepatuhan terhadap Undang-Undang Perlindungan Data
Pribadi (UU PDP) No. 27/2022 diwujudkan melalui fitur penghapusan permanen dokumen
beserta seluruh representasi vektornya (hard delete cascade) dan pencatatan jejak audit
(audit trail) yang append-only dan immutable.
Dokumen ini memuat secara lengkap: desain rancangan lingkungan perangkat keras
dan perangkat lunak; skema basis data relasional dalam format DDL SQL; strategi
pengindeksan termasuk parameter HNSW; rancangan antarmuka pengguna untuk seluruh
12 halaman utama; class diagram UML lengkap; Data Flow Diagram (DFD) Level 0, 1,
dan 2; serta 42 Activity Diagram dan 18 Sequence Diagram yang masing-masing
memodelkan setiap use case yang telah ditetapkan dalam SRS. Keseluruhan dokumen ini
diharapkan menjadi rujukan teknis tunggal (single source of truth) yang komprehensif bagi
seluruh pemangku kepentingan teknis yang terlibat dalam siklus pengembangan sistem
VeriText AI.

4
BAB I
PENDAHULUAN
1.1. Tujuan Software Design Document
Dokumen Software Design Document (SDD) ini disusun dengan tujuan primer untuk
mentransformasikan seluruh spesifikasi kebutuhan yang telah didefinisikan secara formal
di dalam Software Requirements Specification (SRS) VeriText AI v1.0 ke dalam bentuk
cetak biru teknis (technical blueprint) yang dapat langsung dijadikan acuan implementasi
oleh tim pengembang perangkat lunak. Berbeda dengan SRS yang berkonsentrasi pada
pertanyaan "apa yang harus dilakukan oleh sistem" (what), SDD secara eksklusif
menjawab pertanyaan "bagaimana sistem akan diimplementasikan" (how) dengan tingkat
kerincian yang memadai untuk memungkinkan pengembangan kode tanpa ambiguitas
arsitekturalnya. Setiap keputusan desain yang terdokumentasikan dalam SDD ini didorong
oleh kebutuhan fungsional dan non-fungsional yang sudah tervalidasi dalam SRS sebagai
justifikasi teknisnya.
Tujuan sekunder dokumen ini adalah menjadi media komunikasi teknis yang efektif
antar seluruh peran yang terlibat dalam siklus hidup pengembangan VeriText AI. Bagi tim
Backend Engineer dan AI Engineer, SDD menyediakan spesifikasi teknis terperinci
mengenai desain API endpoint, logika orkestrasi Celery worker, parameter algoritma
Winnowing, strategi pengindeksan HNSW, dan skema basis data relasional maupun
vektor. Bagi tim Frontend Engineer, SDD mendefinisikan kontrak antarmuka (API
interface), spesifikasi komponen visual halaman demi halaman, sistem desain warna,
tipografi, serta panduan responsivitas dan aksesibilitas. Bagi QA Engineer, SDD
menyediakan model alur kerja (activity diagram) dan diagram interaksi (sequence
diagram) untuk setiap use case yang menjadi dasar penyusunan skenario pengujian yang
komprehensif, baik pengujian unit, pengujian integrasi, maupun pengujian End-to-End
(E2E).
Tujuan akademis dokumen ini adalah memenuhi persyaratan penilaian mata kuliah
Implementasi Proses Perangkat Lunak (IPPL) dengan mendemonstrasikan penerapan
metodologi rekayasa perangkat lunak terstruktur, khususnya dalam aspek perancangan
teknis sistem. SDD ini dirancang agar sesuai dengan standar dokumentasi desain
perangkat lunak yang diakui secara internasional, merujuk pada panduan IEEE Std
1016-2009 (Software Design Descriptions) serta IEEE Std 42010:2011 (Architecture
Description). Dengan demikian, dokumen ini tidak hanya memiliki nilai praktis sebagai
acuan implementasi, tetapi juga nilai akademis sebagai demonstrasi kompetensi
perancangan sistem yang terstruktur dan metodologis. Seluruh diagram yang disertakan
menggunakan notasi UML 2.5 yang dirender menggunakan sintaks Mermaid untuk
memastikan keterbacaan dan reproduktibilitas diagram secara digital.

5
1.2. Ruang Lingkup
Ruang lingkup desain teknis yang dicakup oleh dokumen SDD ini sepenuhnya selaras
dengan batasan produk yang telah ditetapkan dalam SRS VeriText AI v1.0. Sistem yang
dirancang adalah platform aplikasi web responsif berbasis desktop-first yang dapat diakses
melalui peramban modern tanpa memerlukan instalasi aplikasi native. Secara arsitektural,
sistem ini terdiri atas tiga lapisan utama yang saling berkomunikasi: (1) Lapisan Presentasi
berbasis Next.js 14 App Router yang berjalan di sisi klien dan server, (2) Lapisan API dan
Logika Bisnis berbasis FastAPI Python yang berjalan di server, dan (3) Lapisan
Pemrosesan Asinkron berbasis Celery worker yang terkoneksi ke Redis sebagai message
broker dan PostgreSQL sebagai persistent store.
Komponen-komponen sistem yang dirancang secara eksplisit dalam dokumen ini
mencakup:
(a) Modul Autentikasi dan Manajemen Sesi dengan implementasi JWT + Refresh Token
berbasis HttpOnly Cookie dan mekanisme rate limiting;
(b) Modul Manajemen Dokumen dengan pipeline validasi berkas multi-format (PDF,
DOCX, TXT), ekstraksi teks menggunakan pdfplumber dan python-docx, pembersihan
regex, dan segmentasi kalimat;
(c) Mesin Deteksi Plagiarisme Hybrid 4-Tier sebagai inti sistem, mencakup algoritma
Winnowing (Tier 1), inferensi Sentence Transformers + kueri HNSW pgvector (Tier 2),
analisis stilometri Burstiness (Tier 3), dan agregator skor komposit (Tier 4);
(d) Modul Visualisasi dan Pelaporan dengan Interactive Heatmap, Side-by-Side
Comparison, generasi PDF sertifikat dengan QR code, dan halaman verifikasi publik;
(e) Modul Bank Korpus dengan bulk ingestion ZIP dan pipeline pengindeksan vektor
massal;
(f) Modul Billing dan Pembayaran dengan integrasi Midtrans Snap sandbox, penanganan
webhook SHA-512, dan manajemen dompet token; serta
(g) Modul Administrasi Sistem dengan monitoring Celery worker, manajemen pengguna,
dan operasi pemeliharaan HNSW reindex.
1.3. Gambaran Dokumen
Dokumen SDD ini disusun dalam empat bab utama yang secara progresif membangun
pemahaman dari gambaran tingkat tinggi menuju rincian implementasi yang sangat
spesifik, mengikuti alur pikir top-down yang logis dan terstruktur.
BAB I – Pendahuluan menetapkan konteks, tujuan, ruang lingkup, dan daftar referensi
dari dokumen desain ini. Bab ini berfungsi sebagai orientasi awal bagi pembaca sebelum
memasuki konten teknis yang lebih mendalam di bab-bab selanjutnya. Pemahaman atas

6
bab ini memungkinkan pembaca untuk mengetahui apa yang akan dan tidak akan dibahas
dalam dokumen ini.
BAB II – Tinjauan Sistem menyajikan pandangan makro arsitektur sistem VeriText
AI. Sub-bab 2.1 mendeskripsikan arsitektur keseluruhan sistem dari sudut pandang tingkat
tinggi, termasuk filosofi desain Clean Architecture, pola komunikasi antar komponen, dan
model deployment yang ditargetkan. Sub-bab 2.2 menguraikan tujuh modul fungsi utama
sistem secara terperinci, menjelaskan bagaimana setiap modul berkontribusi terhadap
kapabilitas sistem secara keseluruhan. Sub-bab 2.3 memberikan konteks dan latar
belakang domain masalah yang menjadi dasar keputusan arsitektural yang diambil dalam
perancangan sistem ini.
BAB III – Rancangan Lingkungan Aplikasi merupakan bab teknis yang paling luas
cakupannya, membahas semua aspek lingkungan di mana sistem akan beroperasi. Sub-bab
3.1 menjabarkan spesifikasi perangkat keras server, perangkat klien yang didukung,
opsionalitas GPU, dan kalkulasi kapasitas penyimpanan. Sub-bab 3.2 mendaftar seluruh
library dan framework beserta versi spesifiknya, justifikasi pemilihan, dan dependency
matrix. Sub-bab 3.3 menyajikan skema lengkap basis data dalam format DDL SQL,
strategi normalisasi, strategi pengindeksan termasuk parameter HNSW, dan ERD
Mermaid. Sub-bab 3.4 menampilkan diagram komponen arsitektural sistem. Sub-bab 3.5
mendefinisikan spesifikasi lengkap REST API, protokol webhook, dan katalog kode error.
Sub-bab 3.6 mendeskripsikan rancangan antarmuka pengguna untuk seluruh 12 halaman
utama sistem, mencakup sistem warna, tipografi, dan panduan aksesibilitas.
BAB IV – Perancangan UML merupakan jantung dari dokumen ini, memuat empat
jenis artefak pemodelan UML yang lengkap. Sub-bab 4.1 menyajikan class diagram
komprehensif yang memodelkan semua entitas data dan relasinya. Sub-bab 4.2
menyajikan Data Flow Diagram dari Level 0 hingga Level 2 untuk proses-proses utama
sistem. Sub-bab 4.3 memuat 42 Activity Diagram yang memodelkan alur kerja setiap use
case secara detail, termasuk decision nodes, fork/join paralel, error paths, dan swimlane
untuk membedakan aksi pengguna dan sistem. Sub-bab 4.4 memuat 18 Sequence Diagram
yang memodelkan interaksi antar komponen sistem untuk use case-use case yang paling
kritis, memperlihatkan urutan pesan, kondisi alternatif, dan penanganan error.

7
BAB II
TINJAUAN SISTEM
1. Deskripsi Umum
VeriText AI adalah sistem perangkat lunak inspeksi integritas akademik berbasis web
yang dirancang dengan filosofi arsitektur Clean Architecture berlapis dan paradigma
separation of concerns yang ketat. Sistem ini beroperasi sebagai layanan web terpusat
(centralized web service) yang dapat diakses melalui peramban modern dari berbagai
perangkat, menawarkan kemampuan deteksi plagiarisme komprehensif yang
menggabungkan pendekatan deterministik leksikal dengan kecerdasan buatan semantik
dalam sebuah pipa pemrosesan terintegrasi yang dieksekusi secara asinkron.
Secara arsitektural makro, sistem VeriText AI terbagi ke dalam empat lapisan utama
yang saling berkomunikasi melalui antarmuka yang terdefinisi dengan baik. Lapisan
Presentasi (Presentation Layer) diimplementasikan menggunakan vue.js 14 dengan App
Router yang mendukung Server-Side Rendering (SSR) dan Client-Side Rendering (CSR)
secara hibrida, memastikan performa halaman yang optimal sekaligus kemampuan
interaktivitas real-time melalui nuxt components. Lapisan Aplikasi dan API (Application
& API Layer) diimplementasikan menggunakan framework FastAPI Python yang
menyediakan antarmuka REST API berbasis standar OpenAPI 3.1, dengan validasi data
menggunakan Pydantic v2 dan pengelolaan sesi database menggunakan SQLAlchemy 2.0
dalam mode asinkron (async). Lapisan Pemrosesan Asinkron (Asynchronous Processing
Layer) menggunakan Celery Distributed Task Queue yang terhubung ke Redis sebagai
message broker dan result backend, bertanggung jawab mengeksekusi seluruh komputasi
intensif AI yang tidak dapat diselesaikan dalam batasan waktu sebuah HTTP request.
Lapisan Persistensi Data (Data Persistence Layer) menggunakan PostgreSQL 16 dengan
ekstensi pgvector yang menyimpan data relasional terstruktur sekaligus data vektor
berdimensi tinggi dalam satu database engine terintegrasi, mengeliminasi kebutuhan akan
database vektor terpisah.

8
Filosofi desain yang mendasari arsitektur VeriText AI adalah prinsip Hexagonal
Architecture (Ports and Adapters) yang dipadukan dengan Clean Architecture Robert C.
Martin. Logika bisnis inti (domain layer) dibuat bebas dari ketergantungan terhadap
framework, database, atau infrastruktur eksternal manapun. Ketergantungan selalu
mengalir ke dalam (dari lapisan luar menuju domain), bukan sebaliknya. Ini
memungkinkan penggantian komponen infrastruktur (misalnya mengganti penyimpanan
file lokal dengan S3, atau mengganti Redis dengan RabbitMQ) tanpa mengubah logika
bisnis inti. Model deployment yang ditargetkan adalah single-server monolith dengan
kapabilitas horizontal scaling pada lapisan Celery worker, yang cocok untuk skala
institusional awal sambil mempertahankan opsi migrasi ke arsitektur microservices di
masa depan.
2.2 Fungsi
Sistem VeriText AI menyediakan tujuh modul fungsi utama yang bekerja secara terintegrasi
untuk memberikan layanan deteksi plagiarisme komprehensif. Masing-masing modul
dirancang sebagai unit fungsional yang kohesif dengan tanggung jawab yang terdefinisi
dengan jelas, mengikuti prinsip Single Responsibility Principle (SRP).
Modul 1: Manajemen Akun & Autentikasi
1. Pendaftaran mandiri dengan 3 token gratis untuk pengguna baru.
2. Autentikasi aman menggunakan JWT (Access Token) dan Refresh Token dalam
HttpOnly Cookie.
3. Role-Based Access Control (RBAC) untuk 5 peran pengguna.
4. Proteksi brute-force dan fitur reset kata sandi.
Modul 2: Manajemen Dokumen & Pra-pemrosesan

9
1. Validasi berkas (maks 15 MB) dan ekstraksi teks murni dari format PDF/DOCX.
2. Segmentasi kalimat dan perekaman posisi karakter (offsets).
3. Penghapusan data permanen (hard delete) untuk mematuhi UU PDP.
Modul 3: Mesin Deteksi Plagiarisme (Hybrid 4-Tier)
1. Orkestrasi pemrosesan asinkron secara sekuensial melalui Celery worker.
2. Pelaksanaan 4 Tier: Leksikal (Winnowing), Semantik (pgvector), Stilometri (AI
pattern), dan Agregasi.
3. Skalabilitas horizontal (tambah worker) dan mekanisme fail-safe (token kembali jika
gagal).
Modul 4: Dasbor & Interactive Heatmap
1. Visualisasi teks beranotasi 3 warna: Merah (Leksikal), Oranye (Semantik), Kuning
(AI).
2. Modal perbandingan berdampingan (Side-by-Side Comparison) dengan naskah
sumber.
3. Gauge skor komposit dan filter tampilan per tier.
Modul 5: Ekspor Laporan Resmi (PDF)
1. Pembuatan laporan PDF resolusi cetak dengan rincian skor dan daftar rujukan
menggunakan WeasyPrint.
2. Tersemat QR Code unik untuk halaman verifikasi keaslian dokumen bagi
publik/dosen.
Modul 6: Transaksi & Dompet Token
1. Model bisnis Freemium berbasis token (1 token = 1 audit).
2. Pembayaran real-time via popup Midtrans Snap (QRIS, VA, GoPay).
3. Pembaruan saldo otomatis dan aman lewat tangkapan webhook SHA-512 Midtrans.
Modul 7: Bank Korpus & Admin
1. Dosen: Unggah massal dokumen pembanding via file ZIP (di-indeks ke pgvector).
2. Admin: Dasbor monitoring (CPU, RAM, Redis), operasi re-indeks HNSW database,
dan peninjauan log audit (security trail).
2.3 Konteks dan Latar Belakang
Domain masalah yang menjadi konteks pengembangan VeriText AI adalah meluasnya
praktik ketidakjujuran akademik di lingkungan pendidikan tinggi Indonesia, yang semakin
diperparah oleh kemudahan akses terhadap model bahasa besar (Large Language Models /
LLM) generatif seperti ChatGPT yang mampu menghasilkan teks berkualitas tinggi dalam

10
hitungan detik. Sistem deteksi plagiarisme konvensional yang hanya mengandalkan
pencocokan string leksikal (seperti Turnitin atau iThenticate dalam mode dasar) tidak lagi
memadai karena teks yang diparafrase menggunakan sinonim atau diubah susunan
sintaksisnya dapat dengan mudah mengelabui sistem berbasis fingerprinting saja.
Demikian pula, teks yang sepenuhnya dihasilkan oleh AI memiliki karakteristik statistik
gaya bahasa yang berbeda dari tulisan manusia autentik, tetapi tidak dapat dideteksi oleh
sistem leksikal murni.
Solusi yang dipilih — arsitektur hybrid multi-tier — menjawab tantangan ini dengan
mengombinasikan kekuatan komplementer dari pendekatan deterministik (Winnowing
untuk pencocokan verbatim yang efisien dan akurat) dan pendekatan probabilistik berbasis
AI (Sentence Transformers untuk deteksi parafrasa semantik). Pemilihan model
paraphrase-multilingual-MiniLM-L12-v2 dari Hugging Face dilandasi oleh kebutuhan
dukungan bahasa Indonesia (multilingual), ukuran model yang kompak (117MB) sehingga
dapat dijalankan pada CPU server tanpa memerlukan GPU, dan kualitas representasi
vektor yang terbukti pada benchmark STS (Semantic Textual Similarity) untuk
bahasa-bahasa Asia Tenggara. Keputusan untuk menggunakan PostgreSQL dengan
ekstensi pgvector alih-alih database vektor khusus (seperti Pinecone, Weaviate, atau
Milvus) didasari oleh pertimbangan kesederhanaan operasional (satu database untuk
semua kebutuhan), ketersediaan ACID guarantees pada operasi yang mengombinasikan
data relasional dan vektor, dan biaya infrastruktur yang lebih rendah untuk skala
institusional.
Keputusan arsitektural kunci lainnya adalah pemilihan Celery sebagai message queue
daripada arsitektur event-driven berbasis Apache Kafka atau RabbitMQ. Pilihan ini
didasarkan pada kematangan ekosistem Celery dalam komunitas Python, kemudahan
konfigurasi dengan Redis sebagai broker (mengeliminasi kebutuhan komponen
infrastruktur terpisah), dukungan bawaan untuk task retry, task cancellation, dan task
result tracking yang sangat dibutuhkan oleh skenario use case VeriText AI, serta
kemampuan horizontal scaling yang memadai untuk skala yang ditargetkan. Secara
keseluruhan, setiap keputusan arsitektural dalam sistem ini diorientasikan pada
keseimbangan optimal antara kemampuan fungsional, performa yang terukur, keamanan
yang dapat diaudit, dan biaya operasional yang berkelanjutan untuk lingkungan akademik.

11
BAB III
RANCANGAN LINGKUNGAN APLIKASI
3.1 Lingkungan Perangkat Keras
1. Akses Web (Desktop/Laptop): Prosesor Dual-core, RAM Minimal 4 GB, Resolusi
layar minimum 1366x768 piksel.
2. Server Compute & Backend: Minimal 4 vCPU, 8GB RAM untuk inferensi
embedding.
3. Penyimpanan (Storage): SSD 100GB+ untuk basis data relasional pgvector dan log
audit.
3.2 Lingkungan Perangkat Lunak
3.2.1 Stack Teknologi Frontend
Library / Framework Versi Justifikasi Pemilihan
vue.js 14.x (App Router)
SSR hybrid untuk SEO dan performa FCP;
App Router mendukung nuxt Server
Components untuk rendering efisien
nuxt 18.x Ekosistem komponen terluas; Concurrent
Mode untuk interaktivitas mulus
TypeScript 5.x
Type safety mencegah bug runtime;
IntelliSense meningkatkan produktivitas
developer
Tailwind CSS 3.x Utility-first CSS; eliminasi CSS unused;
konsistensi desain visual
shadcn/ui Latest Komponen aksesibel berbasis Radix UI;
dapat dikustomisasi tanpa vendor lock-in
TanStack Query v5 Smart polling dengan caching otomatis;
invalidation granular; devtools bawaan
nuxt Hook Form 7.x Validasi form performan; minimal re-render
Zod 3.x Schema validation yang type-safe; integrasi
native dengan nuxt Hook Form
Recharts 2.x Visualisasi chart performa dan metrik admin
qrcode.nuxt 3.x Rendering QR code untuk verifikasi laporan
3.2.2 Stack Teknologi Backend
Library / Framework Versi Justifikasi Pemilihan
Python 3.11+
Performa interpreter yang ditingkatkan; native
async/await; ekosistem AI terlengkap

12
Library / Framework Versi Justifikasi Pemilihan
FastAPI 0.110+
ASGI framework tercepat; OpenAPI 3.1 otomatis;
Pydantic v2 native; dependency injection
Pydantic v2.x
Validasi data 5–50x lebih cepat dari v1; model
generation dari JSON Schema
SQLAlchemy 2.0+
ORM mature dengan dukungan async; Core+ORM
unified API
Alembic 1.13+
Database migration versioning yang terintegrasi
dengan SQLAlchemy
asyncpg 0.29+
Driver PostgreSQL async native; performa connection
pool tertinggi
Celery 5.4+ Mature distributed task queue; task retry, ETA, revoke;
Redis support native
Redis-py 5.x Client Redis async; connection pooling
sentence-transformers 3.x
Abstraksi tingkat tinggi untuk Hugging Face; batch
encoding; model caching
torch (PyTorch) 2.x Komputasi tensor; dukungan CUDA opsional
pdfplumber 0.10+
Ekstraksi teks PDF dengan preservasi layout; tabel
ekstraksi
python-docx 1.1+ Parsing DOCX native Python; akses paragraph dan run
WeasyPrint 61+ HTML/CSS ke PDF renderer; output kualitas cetak
python-jose 3.x JWT signing/verification dengan HMAC-SHA256
passlib + bcrypt 1.7+ Password hashing bcrypt work factor 12
httpx 0.27+ Async HTTP client untuk panggilan Midtrans API
qrcode 7.4+ Generasi QR code untuk embedding di PDF
3.2.3 Infrastruktur
Komponen Versi Konfigurasi Kritis
PostgreSQL 16.x
shared_buffers=2GB, work_mem=64MB, ekstensi
pgvector v0.7.0+
Redis 7.x
maxmemory=2gb,
maxmemory-policy=allkeys-lru,
appendonly=yes
Nginx 1.24+
Reverse proxy; TLS 1.3; rate limiting 60 req/min;
client_max_body_size=15M
Gunicorn + Uvicorn 21+ / 0.29+ 4 worker processes; keepalive 5s
3.3 Basis Data
3.4 Component Diagram
3.5.1 Standar REST API

13
Seluruh endpoint API VeriText AI mengikuti konvensi REST yang konsisten dengan standar
HTTP semantik. Semua request dan response menggunakan format JSON dengan
Content-Type application/json. URL endpoint menggunakan base path /api/v1/
dengan segmen sumber daya dalam bentuk kata benda plural.
Format Respons JSON Standar:
{
 "success": true,
 "data": {},
 "message": "Operasi berhasil dilakukan",
 "meta": {
 "timestamp": "2026-09-27T15:30:00Z",
 "version": "1.0",
 "request_id": "uuid-v4"
 }
}
Format Respons Error JSON Standar:
{
 "success": false,
 "error": {
 "code": "AUTH_INVALID_CREDENTIALS",
 "message": "Email atau kata sandi tidak valid.",
 "details": null
 },
 "meta": {
 "timestamp": "2026-09-27T15:30:01Z",
 "version": "1.0",
 "request_id": "uuid-v4"
 }
}
3.5.2 Katalog Endpoint API Lengkap
Modul Autentikasi (/api/v1/auth)
Method Endpoint Auth Request
Body Response Deskripsi
POST /auth/registe
r
Public
{full_name,
email,
institution,
password}
201
{user_id,
message}
Registrasi
akun baru
POST /auth/login Public {email,
password}
200
{access_tok
en, user} +
Set-Cookie
Login dan
terbitkan
JWT
POST /auth/logout JWT —
200
{message}
Cabut
refresh token

14
Method Endpoint Auth Request
Body Response Deskripsi
POST /auth/refresh Cookie —
200
{access_tok
en}
Perbarui
access token
POST /auth/forgot￾password Public {email} 200
{message}
Kirim email
reset
POST /auth/reset-p
assword Public
{token,
new_passwo
rd}
200
{message}
Eksekusi
reset
password
GET /auth/me JWT — 200 {user}
Data profil
pengguna
aktif
PATCH /auth/profile JWT {full_name,
institution} 200 {user} Perbarui
profil
PATCH /auth/change
-password JWT
{old_passwo
rd,
new_passwo
rd}
200
{message}
Ganti
password
Modul Dokumen (/api/v1/documents)
Method Endpoint Auth Request Response Deskripsi
POST /documents/
upload JWT+Token multipart/for
m-data: file
201
{document_i
d, task_id}
Upload
dokumen +
mulai audit
GET /documents JWT ?page=1&li
mit=20
200
{items[],
total, page}
Daftar
dokumen
pengguna
GET /documents/
{doc_id} JWT —
200
{document}
Detail
dokumen
DELETE /documents/
{doc_id} JWT —
200
{message}
Hapus
dokumen
(UU PDP)
Modul Audit (/api/v1/audits)
Method Endpoint Auth Request Response Deskripsi

15
GET /audits/{task
_id}/status JWT —
200 {status,
progress_pct
, stage}
Smart
polling
status
POST /audits/{task
_id}/cancel JWT —
200
{message}
Batalkan
audit antri
GET /audits/histor
y
JWT
?page&limit
&search&da
te_from&dat
e_to
200
{items[],
total}
Riwayat
audit
GET /audits/histor
y/export-csv JWT ?date_from
&date_to
200 CSV
file stream
Ekspor
riwayat CSV
Modul Laporan (/api/v1/reports)
Method Endpoint Auth Request Response Deskripsi
GET /reports/{rep
ort_id} JWT —
200
{report_data
,
heatmap_an
notations}
Data laporan
heatmap
GET
/reports/{rep
ort_id}/expo
rt-pdf
JWT+Premi
um —
200 PDF
binary
stream
Unduh
sertifikat
PDF
GET
/verify/{veri
fication_uui
d}
Public —
200
{is_valid,
report_sum
mary}
Verifikasi
QR publik
Modul Korpus (/api/v1/corpus)
Method Endpoint Auth Request Response Deskripsi
POST /corpus/inge
st
JWT+Revie
wer
multipart/for
m-data:
zip_file,
category,
academic_ye
ar
201
{queued_co
unt}
Bulk ingest
ZIP
GET /corpus JWT+Revie
wer
?page&categ
ory&year
200
{items[],
total}
Daftar
korpus
PATCH /corpus/{doc
_id}
JWT+Revie
wer
{title,
category,
academic_ye
ar}
200
{corpus_doc
}
Edit
metadata

16
DELETE /corpus/{doc
_id}
JWT+Revie
wer —
200
{message}
Hapus dari
korpus
Modul Billing (/api/v1/billing)
Method Endpoint Auth Request Response Deskripsi
GET /billing/wall
et JWT —
200
{balance,
transactions[
]}
Saldo dan
riwayat
token
POST /billing/topu
p
JWT {package_id
}
201
{order_id,
snap_token}
Mulai
transaksi
Midtrans
POST /billing/web
hook Public+Sig Midtrans
payload 200 OK Penerimaan
webhook
GET /billing/invoi
ces
JWT ?page&statu
s
200
{invoices[]}
Daftar
invoice
GET
/billing/invoi
ces/{inv_id}
/pdf
JWT —
200 PDF
stream
Unduh
invoice PDF
Modul Admin (/api/v1/admin)
Method Endpoint Auth Request Response Deskripsi
GET /admin/users JWT+Admi
n
?page&role
&search&is
_active
200
{users[]}
Daftar
pengguna
GET /admin/users
/{user_id}
JWT+Admi
n —
200 {user,
wallet,
recent_audit
s}
Detail
pengguna
PATCH
/admin/users
/{user_id}/st
atus
JWT+Admi
n
{is_active,
reason}
200
{message}
Suspensi/akt
ivasi
POST
/admin/users
/{user_id}/a
djust-tokens
JWT+Admi
n
{amount,
note}
200
{new_balan
ce}
Koreksi
saldo
GET /admin/healt
h-metrics
JWT+Admi
n —
200 {cpu,
memory,
celery,
db_latency}
Metrik
sistem

17
POST /admin/reind
ex-hnsw
JWT+Admi
n —
202
{message}
Trigger
HNSW
reindex
GET /admin/audit
-logs
JWT+Admi
n
?page&actio
n_type&acto
r_id&date_fr
om
200 {logs[]} Log audit
sistem
3.5.3 Spesifikasi Webhook Midtrans
Endpoint webhook /api/v1/billing/webhook mengimplementasikan protokol validasi
keamanan Midtrans sebagai berikut:
1. Terima HTTP POST dengan payload JSON dari server Midtrans.
2. Ekstrak field kritis: order_id, status_code, gross_amount, signature_key,
transaction_status.
3. Hitung ulang signature menggunakan formula: SHA512(order_id + status_code +
gross_amount + server_key).
4. Bandingkan signature yang dihitung dengan signature_key dari payload. Jika tidak
cocok → return HTTP 403 dan catat insiden keamanan.
5. Periksa idempotency: Jika order_id sudah dalam status PAID, return HTTP 200
tanpa memproses ulang (mencegah kredit ganda).
6. Eksekusi transaksi atomik jika transaction_status adalah settlement atau capture.
7. Return HTTP 200 OK dalam semua kondisi berhasil agar Midtrans tidak melakukan
retry.
3.5.4 Smart Polling Protocol
Frontend mengimplementasikan protokol smart polling menggunakan TanStack Query
dengan konfigurasi adaptif:
const { data: statusData } = useQuery({
 queryKey: ['auditStatus', taskId],
 queryFn: () => fetchAuditStatus(taskId),
 enabled: !!taskId,
 refetchInterval: (data) => {
 // Adaptif: polling lebih cepat saat PROCESSING, berhenti saat terminal state
 if (!data) return 2000;
 if (['SUCCESS', 'FAILED', 'CANCELLED'].includes(data.status)) return false;
 if (data.status === 'QUEUED') return 3000;

18
 return 2000; // PROCESSING
 },
 refetchIntervalInBackground: false, // Hemat bandwidth saat tab tidak aktif
});
3.5.5 Katalog Kode Error
Kode Error HTTP Status Deskripsi
AUTH_INVALID_CREDE
NTIALS 401 Email atau kata sandi tidak
valid
AUTH_ACCOUNT_LOCK
ED 423 Akun dikunci sementara
karena 5 kali gagal login
AUTH_TOKEN_EXPIRED 401 Access token JWT sudah
kedaluwarsa
AUTH_INSUFFICIENT_R
OLE 403
Peran pengguna tidak
memiliki izin untuk operasi
ini
AUTH_ACCOUNT_SUSP
ENDED 403 Akun pengguna telah
dinonaktifkan
DOC_FILE_TOO_LARGE 413 Ukuran berkas melebihi
batas 15 MB
DOC_INVALID_MIME 422 MIME type berkas tidak
valid atau tidak didukung
DOC_INSUFFICIENT_TE
XT 422 Dokumen memiliki kurang
dari 50 kata
DOC_SCANNED_PDF 422 PDF adalah gambar tanpa
lapisan teks
DOC_NOT_FOUND 404 Dokumen tidak ditemukan
atau bukan milik pengguna
AUDIT_INSUFFICIENT_T
OKEN 402 Saldo token kuota tidak
mencukupi
AUDIT_TASK_NOT_CAN
CELLABLE 409
Tugas sudah dalam tahap
PROCESSING, tidak dapat
dibatalkan
PAY_WEBHOOK_SIGNAT
URE_INVALID 403 Signature SHA-512
webhook tidak valid
PAY_ORDER_NOT_FOUN
D
404 Order ID tidak ditemukan di
database

19
Kode Error HTTP Status Deskripsi
REPORT_ACCESS_DENIE
D
403
Laporan audit hanya
tersedia untuk akun
Premium
CORP_DUPLICATE_DOC
UMENT 409
Dokumen dengan hash
SHA-256 yang sama sudah
ada di korpus
ADMIN_SELF_SUSPEND 409 Administrator tidak dapat
menonaktifkan akun sendiri
RATE_LIMIT_EXCEEDED 429 Terlalu banyak request dari
alamat IP ini
INTERNAL_SERVER_ER
ROR 500 Kesalahan server internal
yang tidak terduga
3.5 Communication Interface
3.6 Desain Antarmuka (UI/UX)

20
BAB IV
PERANCANGAN UML
4.1. Class Diagram
Class diagram berikut memodelkan seluruh entitas domain sistem VeriText AI beserta
atribut, method, dan relasi antar kelas. Diagram ini merepresentasikan lapisan domain
model (domain layer) yang menjadi inti dari Clean Architecture sistem, independen dari
framework maupun database yang digunakan.
Setiap kelas domain memiliki tanggung jawab yang jelas sesuai prinsip SRP (Single
Responsibility Principle). Relasi antar kelas mencerminkan pemetaan langsung ke skema
database relasional yang telah didefinisikan dalam Bab III. Method yang dicantumkan
adalah method bisnis utama dari lapisan Service, bukan method CRUD dasar yang
ditangani oleh Repository.

21
4.2 Data Flow Diagram (DFD)
4.2.1 DFD Level 0 – Context Diagram
DFD Level 0 (Context Diagram) menggambarkan sistem VeriText AI sebagai satu proses
tunggal (black box) dan memperlihatkan seluruh entitas eksternal yang berinteraksi dengan
sistem beserta aliran data masuk dan keluar. Terdapat lima entitas eksternal yang berinteraksi
dengan sistem: Pengguna Terdaftar (mahasiswa/penulis yang menggunakan layanan),
Pengunjung/Tamu (pengguna tidak terdaftar yang mengakses halaman publik),
Dosen/Reviewer (pengelola bank korpus), Administrator Sistem (pengelola infrastruktur),
dan Midtrans Payment Gateway (layanan pembayaran eksternal).
4.2.2 DFD Level 1 – Proses Utama Sistem
DFD Level 1 memecah sistem menjadi tujuh proses utama yang selaras dengan tujuh modul
fungsi sistem yang didefinisikan dalam SRS. Setiap proses menampilkan aliran data input
dan output serta keterkaitannya dengan data store dan entitas eksternal.
4.2.3 DFD Level 2 – P1: Manajemen Akun dan Autentikasi

22
4.2.4 DFD Level 2 – P2: Pra-pemrosesan Dokumen

23
4.2.5 DFD Level 2 – P3: Mesin Audit Hybrid 4-Tier

24
4.2.6 DFD Level 2 – P5: Ingesti dan Pengindeksan Korpus
4.3 Activity Diagram (Breakdown Per Use Case)
Sub-bab ini memuat Activity Diagram untuk setiap use case yang telah didefinisikan dalam
SRS. Setiap diagram menggunakan konvensi flowchart dengan representasi swimlane untuk
membedakan aksi pengguna (User) dari aksi sistem (System). Decision node
direpresentasikan dengan bentuk diamond, sedangkan fork/join untuk proses paralel
direpresentasikan dengan notasi yang sesuai. State awal dan akhir ditandai dengan jelas.
AD-AUTH-01: Registrasi Akun Mandiri

25

26
AD-AUTH-02: Login Pengguna dan JWT

27
AD-AUTH-03: Logout Sesi

28
AD-AUTH-04: Ubah Kata Sandi

29
AD-AUTH-05: Reset Kata Sandi

30
AD-AUTH-06: Ubah Profil Pengguna

31
AD-DOC-01: Upload Dokumen

32
AD-DOC-02: Validasi dan Ekstraksi Teks

33
AD-DOC-03: Segmentasi Kalimat

34
AD-DOC-04: Hapus Dokumen (UU PDP)

35
AD-DET-01: Orkestrasi Audit Hybrid

36
AD-DET-02: Tier 1 Winnowing

37
AD-DET-03: Tier 2 Semantic AI
AD-DET-04: Tier 3 Stilometri

38
AD-DET-05: Tier 4 Agregasi Skor

39
AD-DET-06: Smart Polling Status

40
AD-DET-07: Batalkan Audit

41
AD-REP-01: Tampilkan Heatmap

42
AD-REP-02: Side-by-Side Comparison

43
AD-REP-03: Filter Heatmap

44
AD-REP-04: Unduh PDF Resmi

45
AD-REP-05: Verifikasi QR Publik

46
AD-REP-06: Riwayat Audit

47
AD-REP-07: Ekspor CSV

48
AD-CORP-01: Bulk Ingest Korpus

49
AD-CORP-02: Indeks Vektor Korpus

50
AD-CORP-03: Lihat Daftar Korpus

51
AD-CORP-04: Edit Metadata Korpus

52
AD-CORP-05: Hapus Dokumen Korpus

53
AD-PAY-01: Lihat Saldo dan Riwayat

54
AD-PAY-02: Beli Token - Midtrans

55
AD-PAY-03: Proses Webhook Midtrans

56
AD-PAY-04: Unduh Invoice

57
AD-ADM-01: Lihat Daftar Pengguna

58
AD-ADM-02: Suspensi Akun

59
AD-ADM-03: Koreksi Saldo Token

60
AD-ADM-04: Monitor Celery dan Latensi

61
AD-ADM-05: Reindex HNSW

62
AD-ADM-06: Lihat Audit Log

63
4.4 Sequence Diagram
Sub-bab ini memuat Sequence Diagram untuk use case-use case yang paling kritis dalam
sistem VeriText AI. Setiap diagram memperlihatkan interaksi antar komponen sistem
(participant) dalam urutan kronologis yang presisi, disertai blok alt, opt, dan loop untuk
memodelkan kondisi alternatif dan pengulangan.
SD-AUTH-01: Registrasi Akun

64
SD-AUTH-02: Login dan JWT

65
SD-AUTH-03: Logout
SD-AUTH-04: Ubah Password
SD-AUTH-05: Reset Password via Email

66
SD-DOC-01: Upload dan Validasi Dokumen

67
SD-DET-01: Orkestrasi Lengkap Hybrid AI

68
SD-DET-02: Detail Tier 1 Winnowing

69
SD-DET-03: Detail Tier 2 Semantic pgvector

70
SD-DET-04: Detail Tier 3 Stilometri

71
SD-DET-05: Agregasi Tier 4

72
SD-DET-06: Smart Polling Status

73
SD-REP-01: Load Heatmap Viewer

74
SD-REP-04: Generate dan Download PDF
SD-REP-05: Verifikasi QR Publik

75
SD-CORP-01: Bulk Ingest ZIP Korpus
SD-CORP-02: Indexing Vektor Korpus

76
SD-PAY-02: Midtrans Snap Top Up

77
SD-PAY-03: Webhook Processing
SD-ADM-04: Monitor Worker dan Health Check

78

79
Daftar Pustaka
[1] IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications.
New York, NY: IEEE Computer Society, 1998.
[2] IEEE Std 1016-2009, IEEE Standard for Information Technology — Systems Design —
Software Design Descriptions. New York, NY: IEEE Computer Society, 2009.
[3] ISO/IEC/IEEE 42010:2011, Systems and software engineering — Architecture description.
Geneva, Switzerland: ISO/IEC/IEEE, 2011.
[4] ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes —
Requirements engineering. Geneva, Switzerland: ISO/IEC/IEEE, 2018.
[5] S. Schleimer, D. S. Wilkerson, and A. Aiken, "Winnowing: local algorithms for document
fingerprinting," in Proceedings of the 2003 ACM SIGMOD International Conference on
Management of Data (SIGMOD '03), San Diego, CA, USA, 2003, pp. 76–85.
[6] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,"
in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing
(EMNLP-IJCNLP), Hong Kong, 2019, pp. 3982–3992.
[7] Y. A. Malkov and D. A. Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search
Using Hierarchical Navigable Small World Graphs," IEEE Transactions on Pattern Analysis
and Machine Intelligence, vol. 42, no. 4, pp. 824–836, Apr. 2020.
[8] R. C. Martin, Clean Architecture: A Craftsman's Guide to Software Structure and Design,
1st ed. Prentice Hall, 2017.
[9] P. Henderson et al., "pgvector: Open-source vector similarity search for Postgres,"
GitHub repository, 2024. [Online]. Tersedia: https://github.com/pgvector/pgvector.
[10] FastAPI Documentation, "FastAPI Framework, High Performance, Easy to Learn, Fast to Code,
Ready for Production," [Online]. Tersedia: https://fastapi.tiangolo.com/.
[11] vue.js Documentation, "vue.js 14 App Router Documentation," Vercel, [Online].
Tersedia: https://vuejs.org/docs.
[12] Celery Project, "Celery: Distributed Task Queue," [Online].
Tersedia: https://docs.celeryq.dev/.
[13] Midtrans API Documentation, "Core API & Snap Payment Gateway Integration Guide," [Online].
Tersedia: https://docs.midtrans.com/.
[14] OWASP Foundation, "OWASP Top Ten Web Application Security Risks," 2021. [Online].
Tersedia: https://owasp.org/Top10/.
[15] Pemerintah Republik Indonesia, Undang-Undang Republik Indonesia Nomor 27 Tahun 2022
tentang Perlindungan Data Pribadi (UU PDP). Lembaran Negara RI Tahun 2022 Nomor 196.
[16] G. Booch, J. Rumbaugh, and I. Jacobson, The Unified Modeling Language User Guide,
2nd ed. Boston, MA: Addison-Wesley, 2005.
[17] M. Fowler, Patterns of Enterprise Application Architecture, 1st ed.
Boston, MA: Addison-Wesley, 2002.
[18] Tailwind CSS Documentation, "Tailwind CSS v3 Utility-First Framework," [Online].
Tersedia: https://tailwindcss.com/docs.
[19] shadcn/ui, "Re-usable components built with Radix UI and Tailwind CSS," [Online].
Tersedia: https://ui.shadcn.com/.

80
[20] TanStack Query Documentation, "Powerful asynchronous state management for TS/JS," [Online].
Tersedia: https://tanstack.com/query/v5.
[21] WeasyPrint Documentation, "WeasyPrint: The Awesome Document Factory," [Online].
Tersedia: https://weasyprint.org/.
[22] Hugging Face Documentation, "Sentence Transformers: Multilingual Sentence Embeddings," [Online].
Tersedia: https://www.sbert.net/.
[23] SQLAlchemy Documentation, "SQLAlchemy 2.0 ORM with Async Support," [Online].
Tersedia: https://docs.sqlalchemy.org/en/20/.
[24] Alembic Documentation, "Alembic - A Database Migration Tool for SQLAlchemy," [Online].
Tersedia: https://alembic.sqlalchemy.org/.
[25] Redis Documentation, "Redis 7.x: In-memory data structure store," [Online].
Tersedia: https://redis.io/docs/.
Revision History
Versi Tanggal Penulis Deskripsi Perubahan
0.1 25 September 2026 Mochammad Azriel
Albian Putra
Penyusunan draf awal
struktur SDD dan outline
bab.
0.5 26 September 2026 Mochammad Azriel
Albian Putra
Penambahan Bab I–III:
Pendahuluan, Tinjauan
Sistem, Rancangan
Lingkungan, DDL Basis
Data.
0.8 27 September 2026 Mochammad Azriel
Albian Putra
Penambahan Bab IV:
Class Diagram, DFD
Level 0-2, 42 Activity
Diagram, dan 18
Sequence Diagram.
1.0 27 September 2026 Mochammad Azriel
Albian Putra
Finalisasi SDD lengkap
standar IEEE 1016
memuat seluruh artefak
UML untuk semua use
case sistem VeriText AI.