Software Requirements
Specification
for
Veritext
Version 1.0 approved
Prepared by
11241045 -Mochammad Azriel Albian Putra
24 Juni 2026

Table of Contents
1. Pendahuluan 1
1.1 Tujuan Penulisan Dokumen 1
1.2 Audien yang Dituju dan Pembaca yang Disarankan 1
1.3 Batasan Produk 2
1.4 Definisi dan Istilah 2
1.5 Referensi 4
2. Deskripsi Keseluruhan 6
2.1 Deskripsi Produk 6
2.2 Fungsi Produk 6
2.3 Penggolongan Karakterik Pengguna 7
2.4 Lingkungan Operasi 9
2.5 Batasan Desain dan Implementasi 9
2.6 Dokumentasi Pengguna 9
3. Kebutuhan Antarmuka Eksternal 10
3.1 User Interfaces 10
3.2 Hardware Interface 10
3.3 Software Interface 10
3.4 Communication Interface 11
4. Functional Requirement 12
4.1 Use Case Diagram 18
4.2 Use Case Description 19
Revision History
Name Date Reason For Changes Version

1. Pendahuluan
1.1 Tujuan Penulisan Dokumen
Dokumen Spesifikasi Kebutuhan Perangkat Lunak (Software Requirements
Specification - SRS) ini bertujuan untuk mendefinisikan secara menyeluruh, terperinci,
terstruktur, dan terukur seluruh kebutuhan fungsional (functional requirements) dan
kebutuhan non-fungsional (non-functional requirements) dalam pengembangan sistem
VeriText AI (Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical &
Semantic AI Engine).
Dokumen ini menjadi baseline formal bagi seluruh pemangku kepentingan
(stakeholders), mencakup pengembang perangkat lunak, analis sistem, perancang AI,
penguji sistem (QA Engineer), dan dosen penilai mata kuliah Implementasi Proses Perangkat
Lunak (IPPL) selama siklus hidup rekayasa perangkat lunak berlangsung.
1.2 Audien yang Dituju dan Pembaca yang Disarankan
Dokumen ini disusun untuk dipahami oleh peran-peran berikut sesuai dengan konteks
tanggung jawab masing-masing:
1. Pengembang Backend & AI Engineer: Untuk mengimplementasikan pipa
pemrosesan dokumen bertingkat (Algoritma Winnowing, inferensi model Sentence
Transformers, penyimpanan dan pencarian vektor di PostgreSQL dengan ekstensi
pgvector, serta antrean asinkron Celery).
2. Pengembang Frontend: Untuk mengimplementasikan antarmuka pengguna berbasis
VUE.js 14, visualisasi Interactive Heatmap multibaris tiga warna, mekanisme smart
polling status proses analisis menggunakan TanStack Query, serta integrasi modal
pembayaran paywall.
3. Analis Sistem & Desainer UI/UX: Untuk memvalidasi kesesuaian alur kerja
dokumen, pemetaan aktor, diagram use case, serta interaksi pengguna pada setiap
tingkat akses (Freemium vs Premium).
4. Penguji Sistem (QA Engineer): Sebagai acuan utama dalam penyusunan skenario
pengujian unit (unit testing), pengujian integrasi (integration testing), pengujian
End-to-End (E2E), serta pengujian metrik performa AI (Precision, Recall, F1-Score).
5. Dosen Penguji dan Asisten Laboratorium IPPL: Sebagai instrumen evaluasi
akademis terhadap kepatuhan proses rekayasa perangkat lunak, penerapan

metodologi perancangan terstruktur, dan pemenuhan standar dokumentasi IEEE Std
830-1998.
1.3 Batasan Produk
Produk perangkat lunak StockVault memiliki batasan-batasan sebagai berikut pada tahap
awal pengembangan (initial release):
1. Platform Akses: Sistem hanya dapat diakses melalui aplikasi web berbasis peramban
(browser) modern. Belum tersedia aplikasi mobile native pada rilis pertama, namun
antarmuka web dirancang responsif agar dapat diakses melalui perangkat tablet atau
smartphone.
2. Konektivitas: Koneksi internet yang stabil sangat diperlukan untuk mengakses
seluruh fitur. Sistem tidak mendukung mode offline.
3. Cakupan Manajemen: Pada tahap awal, sistem dikonfigurasi untuk mengelola 1
(satu) gudang fisik. Dukungan untuk multi-gudang akan dipertimbangkan pada
pengembangan tahap berikutnya.
4. Integrasi Eksternal: Pada rilis awal, sistem tidak terintegrasi secara langsung dengan
sistem e-commerce, marketplace, atau sistem akuntansi (ERP) eksternal. Seluruh
data master (barang, supplier, customer) dimasukkan dan dikelola secara mandiri di
dalam sistem StockVault.
5. Otomatisasi: Proses verifikasi fisik barang dan pemilihan lokasi bin (pada proses
putaway) masih memerlukan intervensi manual dari karyawan dan tidak sepenuhnya
otomatis berbasis Artificial Intelligence (AI) pada tahap ini, meskipun terdapat fitur
rekomendasi lokasi sederhana.
1.4 Definisi dan Istilah
Berikut adalah definisi istilah-istilah teknis dan bisnis yang digunakan secara konsisten
dalam dokumen ini:
Tabel 1 Definisi dan Istilah
Istilah / Singkatan Definisi Formal
SRS Software Requirements Specification;
dokumen formal spesifikasi kebutuhan
perangkat lunak standar IEEE 830.

Istilah / Singkatan Definisi Formal
VeriText AI Nama resmi produk perangkat lunak sistem
deteksi plagiarisme cerdas arsitektur hybrid
yang dikembangkan.
Winnowing Algoritma fingerprinting berbasis hashing
dokumen menggunakan k-gram dan sliding
window untuk mendeteksi pencocokan leksikal
kata per kata (exact verbatim match).
K-Gram Potongan substring berurutan sepanjang $k$
karakter atau $k$ kata yang diambil dari
sebuah teks masukan.
Rolling Hash Fungsi hash polinomial (misal: Rabin-Karp)
yang menghitung nilai hash jendela teks baru
secara efisien dari nilai hash jendela
sebelumnya.
Sentence Transformers Model deep learning turunan BERT yang
dimodifikasi menggunakan struktur
siamese/triplet network untuk menghasilkan
dense vector embeddings berkualitas tinggi
pada tingkat kalimat.
Cosine Similarity Pengukuran derajat kemiripan arah antara dua
vektor dalam ruang multidimensi, dihitung
melalui hasil kali titik (dot product)
dinormalisasi dengan perkalian magnitudo
kedua vektor.
pgvector Ekstensi sumber terbuka untuk PostgreSQL
yang memungkinkan penyimpanan dan
pengindeksan vektor berdimensi tinggi serta
pencarian Approximate Nearest Neighbor
(ANN).
HNSW Hierarchical Navigable Small World; struktur
graf berlapis untuk pencarian tetangga terdekat
secara cepat dan efisien pada indeks vektor.
Stylometry Cabang linguistik komputasional yang
menganalisis gaya penulisan unik seseorang
atau mesin melalui metrik distribusi statistik
kata dan kalimat.
Burstiness Variasi statistik dari panjang kalimat dan
struktur frasa dalam suatu dokumen. Tulisan
manusia memiliki burstiness tinggi, sedangkan
teks sintetis AI cenderung homogen.

Istilah / Singkatan Definisi Formal
Perplexity Metrik statistik yang mengukur tingkat
ketidakpastian atau kebingungan model bahasa
dalam memprediksi urutan kata berikutnya
dalam sebuah teks masukan.
Celery Sistem antrean tugas terdistribusi (distributed
task queue) berbasis Python yang berfokus
pada operasi asinkron secara real-time.
Redis In-memory data structure store berkecepatan
tinggi yang digunakan sebagai message broker
antrean Celery dan media penyimpanan cache.
Heatmap Annotation Representasi visual dokumen masukan di mana
segmen-segmen teks diwarnai secara interaktif
sesuai dengan tier indikasi plagiarisme (Merah,
Oranye, Kuning).
Snap Token Token sesi transaksi pembayaran terenkripsi
yang diterbitkan oleh Midtrans API untuk
menampilkan antarmuka pembayaran pop-up
(Snap Modal).
Webhook Metode komunikasi HTTP POST balik dari
server gateway pembayaran pihak ketiga ke
server VeriText AI untuk mengabarkan
perubahan status transaksi secara instan.
RBAC Role-Based Access Control; metode
pembatasan otorisasi sistem berdasarkan peran
pengguna yang telah ditentukan.
UU PDP Undang-Undang Perlindungan Data Pribadi
No. 27 Tahun 2022 Republik Indonesia.
1.5 Referensi
Dokumen dan referensi yang menjadi acuan dalam penyusunan SRS ini adalah:
IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements
Specifications, IEEE Computer Society, 1998.
ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes —
Requirements engineering, ISO/IEC/IEEE, 2018.

S. Schleimer, D. S. Wilkerson, and A. Aiken, "Winnowing: local algorithms for document
fingerprinting," in Proceedings of the 2003 ACM SIGMOD International Conference on
Management of Data (SIGMOD '03), San Diego, CA, USA, 2003, pp. 76–85.
N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese
BERT-Networks," in Proceedings of the 2019 Conference on Empirical Methods in Natural
Language Processing (EMNLP-IJCNLP), Hong Kong, 2019, pp. 3982–3992.
P. Henderson et al., "pgvector: Open-source vector similarity search for Postgres," GitHub
repository, 2024. [Online]. Tersedia: https://github.com/pgvector/pgvector.
FastAPI Documentation, "FastAPI Framework, High Performance, Easy to Learn, Fast to
Code, Ready for Production," [Online]. Tersedia: https://fastapi.tiangolo.com/.
VUE.js Documentation, "VUE.js 14 App Router Documentation," Vercel, [Online].
Tersedia: https://VUEjs.org/docs.
Celery Project, "Celery: Distributed Task Queue," [Online]. Tersedia:
https://docs.celeryq.dev/.
Midtrans API Documentation, "Core API & Snap Payment Gateway Integration Guide,"
[Online]. Tersedia: https://docs.midtrans.com/.
OWASP Foundation, "OWASP Top Ten Web Application Security Risks," 2021. [Online].
Tersedia: https://owasp.org/Top10/.
Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data
Pribadi (UU PDP).

2. Deskripsi Keseluruhan
2.1 Deskripsi Produk
VeriText AI adalah platform perangkat lunak inspeksi integritas akademik berbasis web
yang dirancang untuk mendeteksi plagiarisme secara komprehensif melalui pendekatan
arsitektur hybrid multi-tier:
1. Tier 1 (Lexical Match Engine): Menggunakan algoritma Winnowing dan Rabin-Karp
Rolling Hash untuk mencocokkan kemiripan string kata per kata (verbatim
copy-paste) secara deterministik dengan efisiensi komputasi 𝑂(𝑁).
2. Tier 2 (Semantic AI Cross-Check Engine): Menggunakan model representasi vektor
(Sentence Transformers / IndoBERT) untuk memetakan makna semantik kalimat ke
ruang vektor 384-dimensi, kemudian menghitung Cosine Similarity terhadap basis
data vektor guna mengungkap parafrasa kalimat, penataan ulang sintaksis, dan
substitusi sinonim yang lolos dari Tier 1.
3. Tier 3 (Stylometric & AI-Generated Pattern Analyzer): Mengevaluasi metrik statistik
gaya bahasa (Burstiness Score varians panjang kalimat dan Type-Token Ratio) untuk
mengidentifikasi indikasi teks sintetis yang dihasilkan oleh Generative AI / Large
Language Models (seperti ChatGPT).
4. Tier 4 (Scoring Aggregator & Visualization): Menggabungkan skor terbobot dari
ketiga tier menjadi Composite Similarity Index, menghasilkan laporan Interactive
Heatmap dengan kode warna visual, serta menerbitkan berkas sertifikat audit digital
berformat PDF yang dilengkapi tanda tangan kriptografis dan stempel verifikasi.
Sistem juga mengimplementasikan model bisnis Freemium berbasis token kuota dan
integrasi Payment Gateway Sandbox (Midtrans) untuk memfasilitasi transaksi langganan
mandiri bagi mahasiswa dan peneliti independen.
2.2 Fungsi Produk
Sistem VeriText AI menyediakan 7 modul fungsi utama:
1. Manajemen Akun & Autentikasi (Auth & RBAC): Registrasi mandiri, alokasi kuota
token trial awal, otentikasi JWT, rotasi refresh token, pengaturan profil, dan
pembatasan hak akses berbasis peran (Tamu, Pengguna Trial, Pengguna Premium,
Dosen/Reviewer, Administrator).

2. Manajemen Dokumen & Pra-pemrosesan Teks: Pengunggahan berkas (PDF, DOCX,
TXT), ekstraksi teks fisik non-markup, pembersihan noise karakter (regex
sanitation), segmentasi kalimat (sentence boundary disambiguation), dan ekstraksi
metadata berkas.
3. Mesin Audit Deteksi Plagiarisme Hybrid: Orkestrasi pipa deteksi 4-tier secara
asinkron melalui worker Celery yang terhubung ke broker Redis dan PostgreSQL
dengan ekstensi pgvector.
4. Dasbor Hasil Audit & Interactive Heatmap: Antarmuka peninjauan hasil audit
berbasis visualisasi anotasi warna (Merah untuk leksikal, Oranye untuk parafrasa
semantik, Kuning untuk anomali gaya mesin AI), daftar sumber pembanding terduga,
dan persentase kesamaan per segmen.
5. Penerbitan & Ekspor Laporan Resmi (Certified PDF Export): Pembuatan dokumen
laporan PDF resmi beresolusi cetak yang mencantumkan ringkasan persentase
plagiarisme, kutipan teks berdampingan (side-by-side comparison), serta tautan kode
QR verifikasi integritas laporan.
6. Manajemen Kuota, Transaksi, & Billing (Payment Gateway): Pemantauan sisa saldo
kuota audit, integrasi antarmuka pembayaran Midtrans Snap, penanganan webhook
verifikasi transaksi otomatis, dan pencatatan riwayat invoice.
7. Pengelolaan Bank Korpus & Administrasi Sistem: Modul bagi Dosen dan
Administrator untuk menginjeksi kumpulan berkas tugas ke dalam korpus
pembanding internal (bulk ingestion), mengelola status pengguna, memantau utilisasi
antrean worker, serta meninjau log aktivitas sistem.
2.3 Penggolongan Karakterik Pengguna
Sistem VeriText memiliki tiga aktor utama yang memiliki karakteristik dan hak akses
berbeda sesuai dengan perannya masing-masing.
Tabel 2 Karakteristik Pengguna
Kategori
Pengguna
Deskripsi Tugas
Utama
Hak Akses dalam
Sistem
Tingkat Kemampuan
yang Dibutuhkan
Pengunjung
(Guest)
Menjelajahi informasi
publik, landing page,
simulasi demo ringkas
(maks 100 kata), dan
halaman
Hanya akses baca
pada modul publik;
tidak memiliki hak
akses audit dokumen
penuh.
Keterampilan dasar
menggunakan
peramban web
modern.

Kategori
Pengguna
Deskripsi Tugas
Utama
Hak Akses dalam
Sistem
Tingkat Kemampuan
yang Dibutuhkan
perbandingan harga
langganan.
Pengguna
Terdaftar (Trial /
Free User)
Mengunggah
dokumen tugas
pribadi, memeriksa
plagiarisme tingkat
Tier 1 (Leksikal),
melihat ringkasan
skor di layar, dan
membeli kuota token.
Akses audit terbatas
(maks 1.000
kata/dokumen, kuota
3 token awal, Tier 2 &
ekspor PDF terkunci).
Mahasiswa/penulis
umum yang familiar
dengan format
dokumen
PDF/DOCX.
Pengguna
Premium
(Subscribed User)
Memeriksa naskah
ilmiah/skripsi
berskala besar,
mengakses analisis
multi-tier lengkap
(Leksikal, Semantik
AI, Stilometri), dan
mengunduh sertifikat
PDF.
Akses penuh seluruh
tier deteksi dokumen
hingga 25.000 kata,
prioritas antrean
worker tinggi, ekspor
PDF bebas kuota
aktif.
Mahasiswa tingkat
akhir, dosen, peneliti
mandiri, atau staf
editorial jurnal.
Dosen / Asisten
Lab (Reviewer)
Membuat ruang
kelas/folder mata
kuliah, mengunggah
naskah tugas
mahasiswa secara
massal ke dalam
korpus internal, dan
memeriksa kesamaan
lintas mahasiswa.
Akses pengunggahan
korpus (bulk ingest),
audit silang antar
berkas mahasiswa,
analisis analitik
kesamaan kelas.
Tenaga
pengajar/asisten
laboratorium yang
mengelola tugas
akademik berkas
jamak.
Administrator
Sistem
Memelihara
kestabilan sistem,
mengelola basis data
pengguna, memantau
metrik performa
antrean Celery,
mengatur tarif kuota,
dan memeriksa audit
log.
Full Access (CRUD)
terhadap seluruh tabel
data master,
konfigurasi API key,
manajemen korpus,
dan log audit
keamanan.
Profesional TI dengan
pemahaman basis data
relasional/vektor dan
arsitektur server.

2.4 Lingkungan Operasi
1. Peramban Klien (Client Browser): Google Chrome 115+, Mozilla Firefox 115+,
Apple Safari 16+, Microsoft Edge 115+. Resolusi minimal: 1280x720 piksel.
2. Lingkungan Server Web & Backend: Linux (Ubuntu 22.04 LTS), Python 3.11+,
Uvicorn/Gunicorn ASGI Server, Nginx Reverse Proxy.
3. Lingkungan Antrean & Komputasi Latar Belakang: Redis 7.0+, Celery Worker 5.4+.
4. Lingkungan Basis Data: PostgreSQL 16 dengan ekstensi pgvector v0.7.0+.
5. Jaringan: Koneksi internet minimal 2 Mbps dengan protokol wajib HTTPS/TLS 1.3.
2.5 Batasan Desain dan Implementasi
Pengembangan VeriText mengikuti batasan-batasan teknis dan arsitektur yang telah
ditetapkan untuk memastikan kualitas, keamanan, dan kemudahan pemeliharaan.
1. Tech Stack Utama: VUE.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui,
TanStack Query v5, FastAPI, Pydantic v2, SQLAlchemy 2.0 async, PyTorch,
Hugging Face sentence-transformers, Celery, Redis, Midtrans Snap.
2. Arsitektur Kode: Menerapkan Clean Architecture (Controller-Service-Repository).
Lapisan AI terpisah di dalam worker independen.
3. Kualitas & Pengujian: Pengujian unit dan integrasi dengan pytest di backend dan Jest
di frontend.
4. Keamanan: Hashing password bcrypt, autentikasi JWT via HttpOnly Cookies,
mitigasi STRIDE, dan kepatuhan UU PDP No. 27/2022.
2.6 Dokumentasi Pengguna
Sistem menyediakan User Guide Interaktif (In-App Walkthrough), dokumentasi API
otomatis OpenAPI 3.1 (Swagger), serta Manual Operasional Administrasi untuk Dosen dan
Admin.

3. Kebutuhan Antarmuka Eksternal
3.1 User Interfaces
Antarmuka pengguna VeriText AI dirancang dengan prinsip intuitif, responsif, dan kaya
visualisasi data:
1. Workspace Unggah Dokumen: Dropzone drag-and-drop berkas, indikator ukuran dan
tipe berkas, pemilih kedalaman audit, dan ringkasan sisa saldo kuota.
2. Indikator Progres Real-Time: Progress bar interaktif yang menunjukkan tahapan
analisis secara bertingkat dengan estimasi waktu selesai.
3. Interactive Heatmap Dasbor:
a. Panel Kiri: Naskah teks lengkap yang disorot dengan warna Merah
(Leksikal), Oranye (Semantik), dan Kuning (AI Pattern).
b. Panel Kanan: Kartu skor komposit, rincian per tier, dan daftar sumber
pembanding terduga yang dapat diklik untuk membuka modal side-by-side
comparison.
4. Modal Pembayaran (Snap Paywall): Popup pemilihan paket kuota token dan render
iframe Midtrans Snap.
3.2 Hardware Interface
1. Server Compute: Minimal 4 vCPU untuk pemrosesan teks dan inferensi embedding.
Mendukung opsional akselerasi GPU NVIDIA (CUDA).
2. Storage: Penyimpanan persisten lokal / S3-compatible storage untuk menyimpan
berkas masukan dan arsip PDF laporan audit.
3.3 Software Interface
1. PostgreSQL 16 + pgvector: Kueri relasional dan kueri vektor jarak kosinus (<=>).
2. Redis 7 & Celery 5.4: Antrean tugas asinkron dan broker status pekerjaan.
3. Midtrans Core / Snap API: Pemrosesan pembayaran sandbox dan penerimaan
notifikasi webhook.
4. Hugging Face Transformers: Model multilingual MiniLM-L12-v2 untuk
pembentukan dense embedding 384-dimensi.
5. WeasyPrint / ReportLab: Mesin rendering berkas sertifikat audit PDF resmi.

3.4 Communication Interface
1. Klien-Server: Protokol HTTPS/TLS 1.3, pertukaran payload JSON.
2. Smart Polling: Polling berkala adaptif GET /api/v1/audits/{task_id}/status oleh
TanStack Query.
3. Webhook Security: Validasi signature SHA-512 dari Midtrans.

4. Functional Requirement
Kode Deskripsi Kebutuhan Fungsional
Autentikasi, Akun & Keamanan
FR-AUTH-01 Sistem harus menyediakan fitur registrasi akun mandiri dengan atribut:
Nama Lengkap, Email Unik, Institusi, dan Kata Sandi.
FR-AUTH-02 Sistem harus memvalidasi format email dan memastikan kekuatan kata sandi
minimal 8 karakter kombinasi huruf besar, kecil, angka, dan simbol.
FR-AUTH-03 Sistem harus mengalokasikan 3 saldo token audit gratis secara otomatis ke
akun pengguna yang baru terdaftar.
FR-AUTH-04 Sistem harus memverifikasi login dan menerbitkan Access Token JWT (15
menit) dan Refresh Token (7 hari).
FR-AUTH-05 Sistem harus menyimpan Refresh Token dalam HttpOnly, Secure,
SameSite=Strict Cookie.
FR-AUTH-06 Sistem harus mengakhiri sesi pengguna secara aman saat pengguna memilih
aksi logout.
FR-AUTH-07 Sistem harus memungkinkan pengguna mengganti kata sandi dengan
memvalidasi kata sandi lama terlebih dahulu.
FR-AUTH-08 Sistem harus menyediakan alur reset kata sandi melalui tautan token berbatas
waktu yang dikirimkan ke email terdaftar.
FR-AUTH-09 Sistem harus memungkinkan pengguna memperbarui informasi profil akun
(Nama Lengkap dan Institusi).

FR-AUTH-10 Sistem harus mengunci akun sementara selama 15 menit jika terjadi 5 kali
kegagalan login berturut-turut.
FR-AUTH-11 Sistem harus menegakkan pembatasan hak akses berbasis peran (RBAC)
pada setiap endpoint API.
Unggah, Validasi & Ekstraksi
FR-DOC-01 Sistem harus menyediakan formulir pengunggahan naskah masukan
berformat .pdf, .docx, dan .txt maksimal 15 MB.
FR-DOC-02 Sistem harus memvalidasi integritas biner dan memeriksa magic-byte berkas
untuk mencegah executable upload.
FR-DOC-03 Sistem harus mengekstrak teks fisik dari PDF (pdfplumber) dan DOCX
(python-docx).
FR-DOC-04 Sistem harus membersihkan karakter noise, spasi berlebih, dan format
header/footer naskah yang berulang.
FR-DOC-05 Sistem harus memecah teks bersih menjadi larik chunk kalimat dengan
mencatat indeks posisi karakter awal dan akhir (offsets).
FR-DOC-06 Sistem harus menolak pemrosesan naskah dengan jumlah kata kurang dari 50
kata atau PDF tanpa lapisan teks (scanned PDF).
FR-DOC-07 Sistem harus memungkinkan pengguna menghapus naskah dokumen beserta
seluruh representasi vektornya dari repositori sistem (kepatuhan UU PDP).
Deteksi Plagiarisme Hybrid
FR-DET-01 Sistem harus mendelegasikan pemrosesan audit dokumen ke worker Celery
secara asinkron setelah dikonfirmasi pengguna.

FR-DET-02 Sistem harus mengimplementasikan algoritma Winnowing berbasis k-gram
hash (𝑘 = 5, 𝑤 = 4) untuk mengekstrak sidik jari digital naskah.
FR-DET-03 Sistem harus mencocokkan sidik jari naskah terhadap indeks sidik jari
korpus internal secara instan.
FR-DET-04 Sistem harus menghasilkan representasi vektor dense 384-dimensi untuk
setiap kalimat menggunakan model Sentence Transformers.
FR-DET-05 Sistem harus menjalankan kueri ANN jarak kosinus <=> pada PostgreSQL
pgvector berindeks HNSW dengan ambang batas kemiripan ≥ 0. 85.
FR-DET-06 Sistem harus menghitung metrik Burstiness (varians panjang kalimat) dan
Type-Token Ratio untuk mendeteksi anomali gaya mesin AI.
FR-DET-07 Sistem harus mengagregasi skor terbobot ketiga tier menjadi skor kesamaan
komposit (Overall Similarity Index).
FR-DET-08 Sistem harus mengecualikan kalimat kutipan resmi yang diapit tanda petik
ganda dan disertai rujukan sitasi standar.
FR-DET-09 Sistem harus menyediakan endpoint pemantauan status proses audit asinkron
secara real-time.
FR-DET-10 Sistem harus memungkinkan pengguna membatalkan proses audit yang
sedang mengantre di worker.
Visualisasi & Laporan Audit
FR-REP-01 Sistem harus menyajikan antarmuka Interactive Heatmap dengan anotasi
warna: Merah (Leksikal), Oranye (Semantik), Kuning (AI Pattern).
FR-REP-02 Sistem harus menampilkan daftar dokumen pembanding yang cocok di panel
kanan beserta persentase kontribusi kesamaannya.

FR-REP-03 Sistem harus menyediakan jendela perbandingan berdampingan
(side-by-side) saat pengguna mengklik kalimat berwarna di naskah.
FR-REP-04 Sistem harus membatasi tampilan akun Trial hanya pada sorotan Tier 1, dan
memburamkan rincian Tier 2 & Tier 3.
FR-REP-05 Sistem harus memungkinkan pengguna memfilter tampilan anotasi
berdasarkan tier pelanggaran tertentu.
FR-REP-06 Sistem harus memungkinkan Pengguna Premium mengunduh Laporan Audit
Resmi berformat PDF beresolusi tinggi.
FR-REP-07 Berkas PDF laporan resmi harus menyertakan identitas pengunggah, rincian
skor, sebaran per halaman, daftar rujukan, dan kode QR verifikasi.
FR-REP-08 Sistem harus menyediakan halaman publik untuk memverifikasi keaslian
laporan audit saat kode QR dipindai.
FR-REP-09 Sistem harus menampilkan daftar riwayat audit sebelumnya yang dapat
dicari, difilter, dan diurutkan.
FR-REP-10 Sistem harus memungkinkan pengguna mengekspor ringkasan riwayat audit
ke format CSV atau Excel.
Bank Korpus Pembanding
FR-CORP-01 Sistem harus menyediakan fitur bagi Dosen/Admin untuk mengunggah
kumpulan dokumen pembanding secara massal (bulk ingest).
FR-CORP-02 Sistem harus memproses dan mengindeks vektor kalimat dokumen korpus ke
dalam tabel document_chunks di pgvector.
FR-CORP-03 Sistem harus menampilkan daftar seluruh dokumen korpus yang terdaftar
beserta jumlah kalimat dan tanggal ingest.

FR-CORP-04 Sistem harus memungkinkan pengelompokan korpus berdasarkan
Kategori/Mata Kuliah dan Tahun Akademik.
FR-CORP-05 Sistem harus memungkinkan Dosen mengubah metadata korpus atau
menghapus dokumen tertentu dari bank korpus.
Monetisasi & Billing
FR-PAY-01 Sistem harus mengurangi 1 saldo token kuota dari akun pengguna setiap kali
proses audit dokumen dimulai.
FR-PAY-02 Sistem harus mengembalikan saldo token kuota secara otomatis jika proses
worker mengalami kegagalan fatal.
FR-PAY-03 Sistem harus menampilkan informasi sisa saldo token dan riwayat mutasi
debit/kredit kuota.
FR-PAY-04 Sistem harus menyediakan antarmuka pembelian paket token kuota dan
langganan akun premium.
FR-PAY-05 Sistem harus melakukan permintaan pembuatan transaksi ke Midtrans Snap
API dan menerima Snap Token.
FR-PAY-06 Sistem harus menyediakan endpoint webhook publik
/api/v1/payments/webhook untuk menerima notifikasi pembayaran.
FR-PAY-07 Sistem harus memvalidasi signature SHA-512 dari payload webhook
Midtrans sebelum memperbarui status invoice.
FR-PAY-08 Sistem harus menambahkan saldo token kuota atau memperbarui status akun
ke Premium secara instan setelah status settlement.
FR-PAY-09 Sistem harus menerbitkan bukti pembayaran digital (Invoice PDF) yang
dapat diunduh oleh pengguna.

Pemantauan & Administrasi
FR-ADM-01 Sistem harus menampilkan dasbor analitik bagi Admin: total dokumen,
pengguna aktif, utilisasi kuota, dan total omzet transaksi.
FR-ADM-02 Sistem harus menampilkan daftar seluruh pengguna dengan fitur pencarian,
filter status peran, dan aksi ubah status.
FR-ADM-03 Sistem harus memungkinkan Administrator menonaktifkan (suspend) akun
pengguna yang melanggar ketentuan.
FR-ADM-04 Sistem harus memungkinkan Administrator melakukan penyesuaian saldo
token kuota pengguna secara manual untuk koreksi data.
FR-ADM-05 Sistem harus menampilkan status operasional antrean Celery worker, beban
CPU, dan latensi kueri pgvector.
FR-ADM-06 Sistem harus menyediakan fungsi bagi Administrator untuk menjalankan
reindex tabel vektor HNSW pgvector.
FR-ADM-07 Sistem harus mencatat seluruh aktivitas kritis ke dalam tabel audit_logs yang
tidak dapat diubah (immutable).

4.1 Use Case Diagram

4.2 Use Case Description
Field Nilai / Penjelasan
Use Case ID & Name UC-AUTH-01: Registrasi Akun Mandiri
Process Owner Modul Keamanan & Manajemen Akun
Date Created 24 Juni 2026
Purpose Mendaftarkan pengguna baru ke dalam sistem dan
memberikan kuota token sambutan awal.
Overview Pengguna mengisi form pendaftaran. Sistem
memvalidasi data, melakukan hashing kata sandi
dengan bcrypt, membuat akun baru, dan
mengalokasikan 3 saldo token gratis.
Cross Requirement FR-AUTH-01, FR-AUTH-02, FR-AUTH-03
Actor Pengunjung (Guest)
Preconditions Pengunjung berada di halaman registrasi dan belum
memiliki akun dengan email yang sama.
Postconditions Akun pengguna baru berstatus aktif tersimpan di tabel
users; saldo 3 token tercatat di tabel token_wallets.
Typical Course of Events 1. Pengguna membuka form registrasi.2. Pengguna
mengisi Nama, Email, Institusi, dan Kata Sandi.3.
Pengguna menekan tombol "Daftar".4. Sistem
memvalidasi format email dan kompleksitas kata
sandi.5. Sistem memeriksa keunikan email di basis
data.6. Sistem melakukan hash kata sandi dengan
bcrypt (work factor 12).7. Sistem menyimpan data
pengguna baru.8. Sistem mengalokasikan 3 token
kuota gratis.9. Sistem menampilkan pesan sukses dan
mengarahkan ke halaman login.
Alternative Workflow A1: Registrasi OAuth Google: Pengguna memilih
"Masuk dengan Google". Sistem mengotentikasi akun
via Google OAuth dan membuat akun otomatis.
Exceptional Workflow E1: Email Sudah Terdaftar: Sistem menampilkan
pesan galat: "Email sudah terdaftar. Silakan login atau
gunakan reset kata sandi."E2: Kata Sandi Lemah:
Sistem menampilkan peringatan: "Kata sandi minimal
8 karakter dengan kombinasi huruf besar, kecil, angka,
dan simbol."

UC-AUTH-02 – Login Pengguna & Penerbitan JWT
Field Nilai / Penjelasan
Use Case ID & Name UC-AUTH-02: Login Pengguna & Penerbitan
JWT
Process Owner Modul Keamanan & Sesi
Date Created 24 Juni 2026
Purpose Memverifikasi kredensial pengguna dan
menerbitkan pasangan token otentikasi JWT.
Overview Pengguna memasukkan email dan kata sandi.
Sistem memvalidasi kredensial, mereset
counter gagal login, dan menerbitkan Access
Token serta Refresh Token di HttpOnly cookie.
Cross Requirement FR-AUTH-04, FR-AUTH-05, FR-AUTH-10
Actor Pengguna Terdaftar, Dosen, Admin
Preconditions Pengguna telah memiliki akun terdaftar dan
berstatus aktif (tidak di-suspend).
Postconditions Sesi pengguna aktif; Access Token JWT
dikirim ke klien; Refresh Token tersimpan di
secure cookie.
Typical Course of Events 1. Pengguna membuka halaman login.2.
Pengguna memasukkan email dan kata sandi.3.
Pengguna menekan tombol "Masuk".4. Sistem
memeriksa apakah akun sedang dalam status
terkunci sementara.5. Sistem memverifikasi
hash kata sandi.6. Sistem mereset hitungan
kegagalan login akun.7. Sistem
membangkitkan Access Token JWT (15 menit)
dan Refresh Token (7 hari).8. Sistem
menyematkan Refresh Token ke HttpOnly
Cookie.9. Sistem mengembalikan Access
Token dan data peran pengguna ke klien.10.
Klien mengarahkan pengguna ke halaman
Dasbor Workspace.
Alternative Workflow -
Exceptional Workflow E1: Kredensial Salah: Sistem mencatat
kegagalan, menambah counter gagal login, dan
menampilkan pesan: "Email atau kata sandi
tidak valid."E2: Akun Terkunci Sementara:
Jika gagal login mencapai 5 kali berturut-turut,

Field Nilai / Penjelasan
sistem mengunci akun selama 15 menit dan
menampilkan peringatan: "Akun terkunci
sementara karena 5 kali percobaan gagal."
UC-AUTH-03 – Logout Sesi Pengguna
Field Nilai / Penjelasan
Use Case ID & Name UC-AUTH-03: Logout Sesi Pengguna
Process Owner Modul Keamanan & Sesi
Date Created 24 Juni 2026
Purpose Mengakhiri sesi pengguna secara aman dan
menghapus kredensial token dari peramban.
Overview Pengguna memilih opsi keluar. Sistem
mencabut Refresh Token dari basis data sesi,
membersihkan cookie, dan mengarahkan
kembali ke halaman login.
Cross Requirement FR-AUTH-06
Actor Semua Aktor Terotentikasi
Preconditions Pengguna sedang berada dalam sesi login aktif.
Postconditions Token otentikasi di-blacklist / dicabut; cookie
Refresh Token dihapus; sesi berakhir.
Typical Course of Events 1. Pengguna mengklik tombol "Keluar /
Logout" pada menu profil.2. Sistem
memvalidasi token sesi yang aktif.3. Sistem
mencabut (revoke) status token dari basis data
sesi.4. Sistem mengirimkan header instruksi
penghapusan cookie ke peramban.5. Sistem
mencatat log audit aktivitas logout.6. Klien
menghapus token memori lokal dan
mengarahkan pengguna ke halaman awal.
Alternative Workflow -
Exceptional Workflow -

UC-AUTH-04 – Mengubah Kata Sandi Akun
Field Nilai / Penjelasan
Use Case ID & Name UC-AUTH-04: Mengubah Kata Sandi Akun
Process Owner Modul Keamanan Akun
Date Created 24 Juni 2026
Purpose Memfasilitasi pengguna untuk memperbarui
kata sandi secara berkala demi menjaga
keamanan akun.
Overview Pengguna menginputkan kata sandi lama dan
kata sandi baru. Sistem memvalidasi kebenaran
kata sandi lama, mengecek kekuatan kata sandi
baru, dan menyimpan hash barunya.
Cross Requirement FR-AUTH-02, FR-AUTH-07
Actor Semua Aktor Terotentikasi
Preconditions Pengguna telah login ke dalam sistem.
Postconditions Kata sandi pengguna diperbarui di basis data;
seluruh sesi aktif di perangkat lain dicabut
demi keamanan.
Typical Course of Events 1. Pengguna membuka menu "Pengaturan
Akun" $\rightarrow$ "Keamanan".2. Pengguna
memasukkan Kata Sandi Lama, Kata Sandi
Baru, dan Konfirmasi Kata Sandi Baru.3.
Pengguna menekan tombol "Simpan Kata
Sandi".4. Sistem memverifikasi kebenaran kata
sandi lama.5. Sistem memvalidasi kekuatan
kata sandi baru dan kesesuaian konfirmasi.6.
Sistem melakukan hash kata sandi baru
menggunakan bcrypt.7. Sistem memperbarui
hash di tabel users.8. Sistem mencabut token
sesi lama di perangkat lain.9. Sistem
menampilkan notifikasi sukses pembaruan kata
sandi.
Alternative Workflow -
Exceptional Workflow E1: Kata Sandi Lama Salah: Sistem
menampilkan pesan galat: "Kata sandi lama
yang Anda masukkan tidak sesuai."E2:
Konfirmasi Tidak Cocok: Sistem menampilkan
pesan: "Konfirmasi kata sandi baru tidak
cocok."

UC-AUTH-05 – Permintaan Reset Kata Sandi (Lupa Password)
Field Nilai / Penjelasan
Use Case ID & Name UC-AUTH-05: Permintaan Reset Kata Sandi
(Lupa Password)
Process Owner Modul Keamanan & Notifikasi Email
Date Created 24 Juni 2026
Purpose Membantu pengguna memulihkan akses ke
akun yang terlupa kata sandinya secara aman.
Overview Pengguna memasukkan alamat email terdaftar.
Sistem membangkitkan token reset kriptografi
berbatas waktu (1 jam) dan mengirimkan
tautan pemulihan ke email pengguna.
Cross Requirement FR-AUTH-08
Actor Pengunjung (Guest), Pengguna Terdaftar
Preconditions Pengguna tidak dapat masuk ke sistem karena
lupa kata sandi.
Postconditions Token reset terenkripsi tersimpan sementara di
basis data; email berisi tautan reset dikirimkan
ke pengguna.
Typical Course of Events 1. Pengguna mengklik "Lupa Kata Sandi?" di
halaman login.2. Pengguna menginputkan
alamat email terdaftar.3. Pengguna menekan
tombol "Kirim Tautan Pemulihan".4. Sistem
memeriksa keberadaan email di basis data.5.
Sistem membangkitkan token acak kriptografis
(secure random token) dengan masa
kedaluwarsa 60 menit.6. Sistem menyimpan
hash token pemulihan di tabel
password_resets.7. Sistem mengirimkan pesan
email berisi tautan unik
/reset-password?token=....8. Sistem
menampilkan pesan konfirmasi pengiriman
email ke pengguna.
Alternative Workflow -

Field Nilai / Penjelasan
Exceptional Workflow E1: Email Tidak Ditemukan: Demi mencegah
user enumeration attack, sistem tetap
menampilkan pesan netral: "Jika email
terdaftar di sistem, tautan pemulihan telah
dikirimkan."
1. UC-AUTH-06 – Mengubah Data Profil Pengguna
Field Nilai / Penjelasan
Use Case ID & Name UC-AUTH-06: Mengubah Data Profil
Pengguna
Process Owner Modul Manajemen Profil
Date Created 24 Juni 2026
Purpose Mengizinkan pengguna memperbarui
informasi biodata profil seperti nama lengkap
dan asal institusi.
Overview Pengguna mengubah data profil pada formulir
pengaturan. Sistem memvalidasi kelengkapan
teks dan memperbarui catatan basis data
pengguna.
Cross Requirement FR-AUTH-09
Actor Semua Aktor Terotentikasi
Preconditions Pengguna telah login ke dalam sistem.
Postconditions Informasi profil pengguna diperbarui di tabel
users.
Typical Course of Events 1. Pengguna membuka halaman "Profil
Saya".2. Pengguna menyunting field Nama
Lengkap dan Asal Institusi (kolom email
terkunci).3. Pengguna menekan tombol
"Simpan Profil".4. Sistem memvalidasi input
teks bebas dari skrip jahat (sanitasi XSS).5.
Sistem memperbarui data profil di basis data.6.
Sistem menampilkan notifikasi sukses
pembaruan profil.
Alternative Workflow -

Field Nilai / Penjelasan
Exceptional Workflow E1: Nama Lengkap Kosong: Sistem
menampilkan peringatan: "Nama lengkap
wajib diisi."
UC-DOC-01 – Mengunggah Dokumen Naskah Masukan
Field Nilai / Penjelasan
Use Case ID & Name UC-DOC-01: Mengunggah Dokumen Naskah
Masukan
Process Owner Modul Unggah Dokumen
Date Created 24 Juni 2026
Purpose Menerima berkas naskah yang akan dianalisis,
memeriksa saldo kuota, dan menyimpan berkas
fisik ke media penyimpanan server.
Overview Pengguna menyeret berkas ke dropzone.
Sistem memeriksa ukuran berkas, ketersediaan
saldo token, memotong 1 kuota token, dan
menyimpan berkas dengan nama unik UUID.
Cross Requirement FR-DOC-01, FR-DOC-02, FR-PAY-01
Actor Pengguna Terdaftar (Trial / Premium), Dosen
Preconditions Pengguna telah login dan memiliki sisa saldo
minimal 1 token kuota.
Postconditions Berkas naskah fisik tersimpan aman di disk;
entitas dokumen berstatus UPLOADED
tercatat di basis data; kuota token terpotong 1
unit.
Typical Course of Events 1. Pengguna membuka halaman Workspace
Audit.2. Pengguna mengunggah berkas naskah
(.pdf / .docx / .txt).3. Sistem memverifikasi
ukuran berkas tidak melebihi 15 MB.4. Sistem
memeriksa ketersediaan saldo token kuota
pengguna.5. Pengguna menekan tombol
"Konfirmasi Pemeriksaan".6. Sistem
memotong 1 saldo token dari akun pengguna.7.
Sistem menghasilkan nama berkas aman
berbasis UUIDv4.8. Sistem menyimpan berkas

Field Nilai / Penjelasan
ke direktori penyimpanan terisolasi.9. Sistem
memicu alur validasi dan ekstraksi berkas
(UC-DOC-02).
Alternative Workflow -
Exceptional Workflow E1: Kuota Token Habis: Sistem menolak
proses unggah dan memunculkan modal
paywall pembelian paket token.E2: Ukuran
Berkas > 15 MB: Sistem menampilkan pesan
galat: "Ukuran berkas melebihi batas maksimal
15 MB."
UC-DOC-02 – Validasi Berkas & Ekstraksi Teks (PDF/DOCX/TXT)
Field Nilai / Penjelasan
Use Case ID & Name UC-DOC-02: Validasi Berkas & Ekstraksi
Teks (PDF/DOCX/TXT)
Process Owner Mesin Pra-pemrosesan Teks
Date Created 24 Juni 2026
Purpose Memverifikasi tipe biner berkas dan
mengekstrak seluruh teks murni non-markup
dari berkas dokumen.
Overview Sistem memeriksa magic bytes berkas. Jika
valid, sistem memanggil parser PDF
(pdfplumber) atau DOCX (python-docx),
mengekstrak string teks, dan menghitung total
jumlah kata.
Cross Requirement FR-DOC-02, FR-DOC-03, FR-DOC-06
Actor Sistem Internal (Backend Service)
Preconditions Berkas dokumen telah diunggah (UC-DOC-01)
dan berada di disk server.
Postconditions Teks dokumen mentah berhasil diekstraksi dan
disimpan di tabel sementara
extracted_documents.
Typical Course of Events 1. Sistem membaca header byte biner berkas
untuk memvalidasi MIME-type riil.2. Sistem

Field Nilai / Penjelasan
memanggil modul ekstraktor sesuai ekstensi
berkas.3. Ekstraktor membaca halaman demi
halaman dan mengekstrak konten teks murni.4.
Sistem menghitung total kata dalam naskah.5.
Sistem memverifikasi jumlah kata memenuhi
syarat minimal ($\ge 50$ kata).6. Sistem
meneruskan teks hasil ekstraksi ke modul
segmentasi kalimat (UC-DOC-03).
Alternative Workflow -
Exceptional Workflow E1: Berkas Korup / Ekstensi Palsu (MIME
Mismatch): Sistem membatalkan tugas,
menghapus berkas, mengembalikan token
pengguna, dan mencatat galat: "Berkas tidak
valid atau mengalami kerusakan biner."E2:
PDF Pindai Gambar Tanpa Lapisan Teks:
Sistem mendeteksi jumlah kata $< 50$,
mengembalikan token kuota, dan mengirim
notifikasi: "Dokumen tidak memiliki lapisan
teks yang dapat dibaca."
UC-DOC-03 – Segmentasi Kalimat & Perekaman Character Offset
Field Nilai / Penjelasan
Use Case ID & Name UC-DOC-03: Segmentasi Kalimat &
Perekaman Character Offset
Process Owner Mesin Pra-pemrosesan Teks
Date Created 24 Juni 2026
Purpose Memecah teks naskah menjadi kumpulan
kalimat terstruktur serta merekam posisi indeks
karakter untuk visualisasi heatmap.
Overview Sistem membersihkan noise teks,
menggunakan modul pemecah batas kalimat
(sentence boundary disambiguator), dan
mencatat nomor urut, teks kalimat, serta
koordinat karakter awal dan akhir.
Cross Requirement FR-DOC-04, FR-DOC-05
Actor Sistem Internal (Backend Service)

Field Nilai / Penjelasan
Preconditions Teks naskah mentah telah berhasil diekstraksi
dari berkas (UC-DOC-02).
Postconditions Daftar record kalimat terstruktur tersimpan di
basis data dengan indeks start_offset dan
end_offset yang presisi.
Typical Course of Events 1. Sistem menjalankan pembersihan karakter
non-ASCII dan normalisasi spasi ganda.2.
Sistem mendeteksi pemisah batas kalimat
(titik, tanda seru, tanda tanya yang bukan
singkatan gelar).3. Sistem membentuk larik
objek kalimat.4. Untuk setiap kalimat, sistem
merekam indeks start_char dan end_char relatif
terhadap teks lengkap.5. Sistem menyimpan
larik kalimat ke tabel audit_sentences.6. Sistem
memicu pendelegasian tugas audit ke Celery
worker (UC-DET-01).
Alternative Workflow -
Exceptional Workflow -
UC-DOC-04 – Menghapus Dokumen Naskah Pengguna (Hak UU PDP)
Field Nilai / Penjelasan
Use Case ID & Name UC-DOC-04: Menghapus Dokumen Naskah
Pengguna (Hak UU PDP)
Process Owner Modul Manajemen Dokumen & Kepatuhan
Privasi
Date Created 24 Juni 2026
Purpose Memenuhi hak pengguna atas penghapusan
data pribadi naskah karya tulis (Right to
Erasure) sesuai UU PDP No. 27/2022.
Overview Pengguna memilih dokumen dari riwayat dan
menekan tombol hapus permanen. Sistem
menghapus berkas fisik di disk, catatan
kalimat, vektor embedding di basis data, dan
laporan audit terkait.
Cross Requirement FR-DOC-07, NFR-COMP-02

Field Nilai / Penjelasan
Actor Pengguna Pemilik Dokumen, Administrator
Preconditions Pengguna telah login dan dokumen yang dituju
merupakan milik akun pengguna yang
bersangkutan.
Postconditions Seluruh data terkait dokumen terhapus
permanen dari basis data dan penyimpanan
fisik (hard delete); log penghapusan dicatat.
Typical Course of Events 1. Pengguna membuka menu "Riwayat Audit
Dokumen".2. Pengguna mencari dokumen
yang ingin dihapus.3. Pengguna menekan ikon
"Hapus Dokumen".4. Sistem menampilkan
dialog konfirmasi penghapusan permanen.5.
Pengguna mengonfirmasi persetujuan
penghapusan.6. Sistem membuka transaksi
basis data dan menghapus record di
audit_reports, audit_sentences, dan entitas
dokumen.7. Sistem menghapus berkas fisik
PDF/Word dari disk server.8. Sistem mencatat
log kepatuhan privasi di audit_logs.9. Sistem
menampilkan notifikasi: "Dokumen dan
seluruh data vektor terkait telah dihapus
permanen."
Alternative Workflow -
Exceptional Workflow E1: Pengguna Mencoba Menghapus Dokumen
Milik Pengguna Lain: Sistem menolak
permintaan dengan kode HTTP 403 Forbidden
dan mencatat insiden keamanan.
UC-DET-01 – Menjalankan Pemeriksaan Deteksi Plagiarisme Hybrid
Field Nilai / Penjelasan
Use Case ID & Name UC-DET-01: Menjalankan Pemeriksaan
Deteksi Plagiarisme Hybrid
Process Owner Mesin Orkestrasi Deteksi & Task Dispatcher
Date Created 24 Juni 2026

Field Nilai / Penjelasan
Purpose Mengorkestrasikan keseluruhan tahapan
analisis multi-tier secara otomatis melalui
antrean asinkron Celery.
Overview Sistem membentuk ID tugas (Task UUID),
mengirim pesan tugas ke broker Redis, dan
memicu worker Celery untuk mengeksekusi
Tier 1 s/d Tier 4 secara sekuensial.
Cross Requirement FR-DET-01, FR-DET-09
Actor Sistem Internal (FastAPI Task Dispatcher &
Celery Worker)
Preconditions Dokumen telah berhasil melalui
pra-pemrosesan kalimat (UC-DOC-03).
Postconditions Tugas audit dialokasikan ke worker; status
pekerjaan berubah menjadi QUEUED lalu
PROCESSING.
Typical Course of Events 1. API Gateway menerima permintaan inisiasi
audit dari modul pra-pemrosesan.2. API
Gateway membangkitkan Task UUID unik.3.
API Gateway mendaftarkan status awal tugas
di Redis dengan status QUEUED.4. Celery
worker yang tersedia mengambil pekerjaan
dari antrean Redis.5. Worker memperbarui
status pekerjaan menjadi PROCESSING.6.
Worker mengeksekusi komputasi Tier 1 -
Leksikal (UC-DET-02).7. Worker
mengeksekusi komputasi Tier 2 - Semantik
Vektor (UC-DET-03).8. Worker mengeksekusi
komputasi Tier 3 - Stilometri (UC-DET-04).9.
Worker mengeksekusi komputasi Tier 4 -
Agregasi Skor (UC-DET-05).10. Worker
memperbarui status akhir menjadi SUCCESS.
Alternative Workflow A1: Akun Pengguna Trial: Worker hanya
mengeksekusi Tier 1 (Leksikal) dan melewati
Tier 2 & Tier 3 guna menghemat utilisasi
sumber daya komputasi server.
Exceptional Workflow E1: Kegagalan Fatal Worker: Jika worker
mengalami exception tak terduga, sistem
mengubah status tugas menjadi FAILED,
mengembalikan token kuota pengguna, dan
mencatat stack trace ke log error.

UC-DET-02 – Pemrosesan Tier 1 - Lexical Match Engine (Winnowing Hash)
Field Nilai / Penjelasan
Use Case ID & Name UC-DET-02: Pemrosesan Tier 1 - Lexical
Match Engine (Winnowing Hash)
Process Owner Mesin Deteksi Tier 1
Date Created 24 Juni 2026
Purpose Mendeteksi penjiplakan kata per kata persis
(verbatim copy-paste) menggunakan algoritma
fingerprinting Winnowing k-gram.
Overview Worker memproses teks dokumen menjadi
k-gram (k=5), menghitung rolling hash
Rabin-Karp, memilih hash minimum pada
sliding window (w=4), dan mencocokkannya
ke indeks sidik jari korpus.
Cross Requirement FR-DET-02, FR-DET-03
Actor Sistem Internal (Celery Worker)
Preconditions Naskah teks telah terurai menjadi larik kata
bersih.
Postconditions Seluruh segmen teks yang cocok secara
leksikal ditandai dengan label TIER1_MATCH
dan ditautkan ke ID dokumen sumber
pembanding.
Typical Course of Events 1. Worker mengambil teks naskah masukan.2.
Worker membentuk token $k$-gram kata
dengan ukuran $k=5$.3. Worker menghitung
nilai hash untuk setiap $k$-gram menggunakan
formula Rabin-Karp Rolling Hash.4. Worker
menerapkan algoritma sliding window dengan
ukuran jendela $w=4$ untuk menyeleksi sidik
jari dokumen (fingerprints).5. Worker
membandingkan himpunan hash naskah
terhadap tabel indeks lexical_fingerprints di
basis data.6. Untuk setiap hash yang cocok,
worker mencatat rentang karakter teks
masukan dan ID dokumen rujukan.7. Worker
menghitung persentase kemiripan leksikal
naskah ($S_{\text{Lexical}}$).
Alternative Workflow -

Field Nilai / Penjelasan
Exceptional Workflow -
UC-DET-03 – Pemrosesan Tier 2 - Semantic AI Engine (Sentence Transformers & pgvector)
Field Nilai / Penjelasan
Use Case ID & Name UC-DET-03: Pemrosesan Tier 2 - Semantic AI
Engine (Sentence Transformers & pgvector)
Process Owner Mesin Deteksi Tier 2 & Vector Database
Date Created 24 Juni 2026
Purpose Mengungkap parafrasa cerdas dan substitusi
sinonim dengan membandingkan kedekatan
makna vektor kalimat ke basis data pgvector.
Overview Worker memproses kalimat naskah secara
batch ke model Sentence Transformers
multilingual, menghasilkan vektor
384-dimensi, dan mengeksekusi kueri jarak
kosinus ANN di basis data korpus.
Cross Requirement FR-DET-04, FR-DET-05
Actor Sistem Internal (Celery Worker & PostgreSQL
pgvector)
Preconditions Pipa Tier 1 telah selesai dan akun pengguna
memiliki hak akses analisis semantik
(Premium / Dosen).
Postconditions Pasangan kalimat dengan Cosine Similarity
$\ge 0.85$ ditandai dengan label
TIER2_MATCH beserta skor kemiripan dan
naskah sumber pembanding.
Typical Course of Events 1. Worker mengambil larik kalimat naskah
masukan dari basis data.2. Worker
mengecualikan kalimat yang sudah terdeteksi
100% pada Tier 1 untuk mengoptimasi
komputasi.3. Worker membagi kalimat
menjadi beberapa batch (misal: 32 kalimat per
batch).4. Model
paraphrase-multilingual-MiniLM-L12-v2
melakukan inferensi dan menghasilkan vektor

Field Nilai / Penjelasan
embedding 384D untuk tiap kalimat.5. Untuk
setiap vektor kalimat, worker mengeksekusi
kueri SQL jarak kosinus <=> pada tabel
document_chunks berindeks HNSW.6. Sistem
mengambil record korpus dengan jarak kosinus
$\le 0.15$ (setara Cosine Similarity $\ge
0.85$).7. Worker mencatat kecocokan
semantik, skor kemiripan, nomor kalimat, dan
ID rujukan korpus.8. Worker menghitung
persentase kemiripan semantik naskah
($S_{\text{Semantic}}$).
Alternative Workflow -
Exceptional Workflow -
UC-DET-04 – Pemrosesan Tier 3 - Stylometric & Burstiness Score
Field Nilai / Penjelasan
Use Case ID & Name UC-DET-04: Pemrosesan Tier 3 - Stylometric
& Burstiness Score
Process Owner Mesin Analisis Stilometri
Date Created 24 Juni 2026
Purpose Mengevaluasi gaya bahasa statistik untuk
mengidentifikasi teks yang terindikasi hasil
generasi model AI (AI-generated text).
Overview Worker menghitung distribusi panjang kalimat
dan keragaman kosa kata. Kalimat atau
paragraf dengan struktur yang sangat monoton
dan homogen ditandai sebagai anomali gaya
mesin.
Cross Requirement FR-DET-06
Actor Sistem Internal (Celery Worker)
Preconditions Seluruh kalimat naskah masukan telah terdaftar
dengan informasi panjang karakter dan jumlah
kata.

Field Nilai / Penjelasan
Postconditions Nilai metrik Burstiness dan Type-Token Ratio
tersimpan; blok teks yang terindikasi AI
ditandai dengan label TIER3_MATCH.
Typical Course of Events 1. Worker menghitung panjang kata untuk
setiap kalimat dalam naskah.2. Worker
menghitung nilai rata-rata ($\mu$) dan varians
standar deviasi ($\sigma^2$) panjang kalimat
untuk menentukan skor Burstiness.3. Worker
menghitung rasio Type-Token Ratio (TTR)
untuk mengukur kelimpahan kosakata unik.4.
Jika blok teks memiliki varians panjang
kalimat yang mendekati nol disertai
prediktabilitas struktur tinggi, sistem
menandainya sebagai indikasi teks sintesis
bot/AI.5. Worker mencatat rentang karakter
yang terindikasi dan menghasilkan skor
stilometri ($S_{\text{Stylometric}}$).
Alternative Workflow -
Exceptional Workflow -
UC-DET-05 – Pemrosesan Tier 4 - Scoring Aggregator & Heatmap Mapping
Field Nilai / Penjelasan
Use Case ID & Name UC-DET-05: Pemrosesan Tier 4 - Scoring
Aggregator & Heatmap Mapping
Process Owner Mesin Agregasi Skor & Kompilasi Laporan
Date Created 24 Juni 2026
Purpose Menggabungkan seluruh temuan dari ketiga
tier, menghitung persentase kemiripan total,
dan memetakan koordinat warna anotasi
heatmap.
Overview Worker mengumpulkan hasil deteksi Tier 1, 2,
dan 3, mengecualikan sitasi kutipan resmi,
menghitung rumus skor komposit terbobot, dan
menyusun payload laporan siap saji.
Cross Requirement FR-DET-07, FR-DET-08, FR-REP-01

Field Nilai / Penjelasan
Actor Sistem Internal (Celery Worker)
Preconditions Pemrosesan Tier 1, Tier 2, dan Tier 3 telah
selesai dieksekusi.
Postconditions Laporan audit lengkap tersimpan di tabel
audit_reports; payload anotasi JSON tersimpan
untuk konsumsi frontend; status tugas menjadi
SUCCESS.
Typical Course of Events 1. Worker mengumpulkan seluruh koordinat
kecocokan dari Tier 1, Tier 2, dan Tier 3.2.
Worker memeriksa apakah segmen yang cocok
berada di dalam blok tanda kutip sitasi resmi;
jika ya, segmen tersebut dikecualikan dari
pelanggaran.3. Worker menghitung persentase
kemiripan komposit total menggunakan
formula pembobotan: 
$\text{Score}{\text{Total}} = 0.50 \cdot
S{\text{Lexical}} + 0.35 \cdot
S_{\text{Semantic}} + 0.15 \cdot
S_{\text{Stylometric}}$.4. Worker menyusun
daftar koordinat karakter (character spans)
beserta warna anotasi: Merah (Leksikal),
Oranye (Semantik), Kuning (AI).5. Worker
menyusun ringkasan kontribusi masing-masing
dokumen sumber pembanding.6. Worker
menyimpan entitas laporan akhir ke tabel
audit_reports.7. Worker memperbarui status
pekerjaan di Redis menjadi SUCCESS.
Alternative Workflow -
Exceptional Workflow -
UC-DET-06 – Memantau Progres Pengerjaan Audit (Smart Polling)
Field Nilai / Penjelasan
Use Case ID & Name UC-DET-06: Memantau Progres Pengerjaan
Audit (Smart Polling)
Process Owner Antarmuka Klien & API Gateway
Date Created 24 Juni 2026

Field Nilai / Penjelasan
Purpose Menyediakan pembaruan visual progres
pengerjaan audit dokumen kepada pengguna
secara berkala dan real-time.
Overview Frontend mengirimkan permintaan GET
polling setiap 2 detik ke backend. Sistem
mengembalikan status tahapan aktif dan
persentase estimasi hingga pekerjaan berstatus
SUCCESS.
Cross Requirement FR-DET-09, FR-REP-01
Actor Pengguna (Trial / Premium), Dosen
Preconditions Pengguna telah memulai proses audit dan
memegang Task UUID aktif.
Postconditions Pengguna melihat pergerakan bilah kemajuan
(progress bar) dan otomatis dialihkan ke
halaman Heatmap setelah selesai.
Typical Course of Events 1. Klien web menampilkan antarmuka bilah
kemajuan dengan status QUEUED.2. Kueri
TanStack Query melakukan polling berkala ke
endpoint /api/v1/audits/{task_id}/status.3.
Server membaca status job dari cache Redis
dan mengembalikan respons status (misal:
PROCESSING_TIER2, kemajuan: 65%).4.
Klien memperbarui antarmuka pengguna
sesuai data respons.5. Ketika server
mengembalikan status SUCCESS, klien
menghentikan polling.6. Klien secara otomatis
memuat dan merender halaman Dasbor
Interactive Heatmap.
Alternative Workflow -
Exceptional Workflow E1: Status Berubah Menjadi FAILED: Klien
menghentikan polling dan menampilkan pesan
galat: "Pemeriksaan gagal diproses. Saldo
token Anda telah dikembalikan otomatis."
2. UC-DET-07 – Membatalkan Proses Audit yang Sedang
Berjalan

Field Nilai / Penjelasan
Use Case ID & Name UC-DET-07: Membatalkan Proses Audit yang
Sedang Berjalan
Process Owner Modul Task Dispatcher & Antrean Celery
Date Created 24 Juni 2026
Purpose Mengizinkan pengguna membatalkan tugas
audit yang masih mengantre sebelum
dieksekusi oleh worker.
Overview Pengguna menekan tombol batalkan pada
halaman tunggu. Sistem memeriksa status
tugas di Redis. Jika belum dieksekusi, tugas
dicabut dari antrean dan token kuota
dikembalikan ke akun pengguna.
Cross Requirement FR-DET-10, FR-PAY-02
Actor Pengguna (Trial / Premium)
Preconditions Tugas audit masih berada dalam status
QUEUED di antrean broker Redis.
Postconditions Tugas audit dibatalkan; status menjadi
REVOKED; 1 saldo token kuota dikreditkan
kembali ke akun pengguna.
Typical Course of Events 1. Pengguna menekan tombol "Batalkan
Analisis" pada bilah antrean.2. Klien
mengirimkan permintaan POST
/api/v1/audits/{task_id}/cancel.3. Backend
memeriksa status tugas saat ini di Redis.4. Jika
tugas masih berstatus QUEUED, backend
mengirimkan instruksi revoke ke Celery.5.
Backend memperbarui status tugas menjadi
CANCELLED.6. Backend mengembalikan 1
saldo token kuota ke dompet pengguna.7.
Backend mencatat log pembatalan tugas.8.
Klien menampilkan notifikasi: "Pemeriksaan
berhasil dibatalkan. Kuota token Anda telah
dikembalikan."
Alternative Workflow -
Exceptional Workflow E1: Tugas Sudah Terlanjur Masuk Tahap
Eksekusi (PROCESSING): Sistem menolak
pembatalan dan menampilkan peringatan:
"Dokumen sedang dalam tahap analisis
komputasi dan tidak dapat dibatalkan."

UC-REP-01 – Menampilkan Dasbor Interactive Heatmap
Field Nilai / Penjelasan
Use Case ID & Name UC-REP-01: Menampilkan Dasbor Interactive
Heatmap
Process Owner Modul Visualisasi Laporan & Heatmap Viewer
Date Created 24 Juni 2026
Purpose Menyajikan hasil penelaahan plagiarisme
secara visual dengan teks beranotasi tiga warna
dan ringkasan metrik.
Overview Pengguna membuka hasil audit. Sistem
merender teks naskah dengan latar warna
Merah (Leksikal), Oranye (Semantik), dan
Kuning (AI) serta menampilkan kartu skor di
sisi kanan.
Cross Requirement FR-REP-01, FR-REP-02, FR-REP-04
Actor Pengguna (Trial / Premium), Dosen
Preconditions Laporan audit telah berstatus SUCCESS di
basis data.
Postconditions Pengguna dapat membaca seluruh visualisasi
teks beranotasi dan meninjau ringkasan sumber
rujukan yang cocok.
Typical Course of Events 1. Pengguna membuka tautan hasil audit dari
dasbor riwayat.2. Klien meminta data laporan
dari endpoint /api/v1/reports/{report_id}.3.
Server mengembalikan naskah teks, daftar
koordinat anotasi warna, dan metadata
sumber.4. Frontend merender teks naskah pada
panel kiri dengan blok warna yang
bersesuaian.5. Frontend merender kartu skor
kesamaan komposit dan daftar sumber
pembanding di panel kanan.6. Pengguna dapat
membaca dan menelusuri seluruh dokumen
yang diperiksa.
Alternative Workflow A1: Akun Pengguna Trial: Sistem merender
teks leksikal (Merah), namun memberikan efek

Field Nilai / Penjelasan
buram (blur) pada kalimat Tier 2 (Oranye) dan
menyematkan ajakan upgrade ke Premium.
Exceptional Workflow -
UC-REP-02 – Meninjau Perbandingan Teks Berdampingan (Side-by-Side Comparison)
Field Nilai / Penjelasan
Use Case ID & Name UC-REP-02: Meninjau Perbandingan Teks
Berdampingan (Side-by-Side Comparison)
Process Owner Modul Visualisasi Laporan
Date Created 24 Juni 2026
Purpose Memungkinkan pengguna membandingkan
kalimat masukan dengan kalimat dokumen
sumber secara langsung dalam tampilan
berdampingan.
Overview Pengguna mengklik segmen teks berwarna
pada heatmap. Sistem membuka jendela dialog
perbandingan yang menampilkan teks naskah
pengguna di sebelah kiri dan teks dokumen
sumber asli di sebelah kanan.
Cross Requirement FR-REP-03
Actor Pengguna (Trial / Premium), Dosen
Preconditions Pengguna sedang membuka dasbor Interactive
Heatmap (UC-REP-01).
Postconditions Jendela perbandingan berdampingan tampil di
layar dengan teks yang bersesuaian ditandai
jelas.
Typical Course of Events 1. Pengguna mengklik salah satu kalimat yang
disorot warna di naskah.2. Sistem menangkap
event klik dan membaca ID rujukan dokumen
sumber.3. Sistem menampilkan jendela modal
Side-by-Side Comparison.4. Panel kiri modal
menampilkan kalimat naskah masukan beserta
tier pelanggarannya.5. Panel kanan modal
menampilkan kalimat padanan dari dokumen
korpus rujukan beserta judul naskah dan

Field Nilai / Penjelasan
penulis.6. Pengguna meninjau kemiripan
makna atau susunan kata.7. Pengguna menutup
jendela dialog setelah selesai meninjau.
Alternative Workflow -
Exceptional Workflow -
UC-REP-03 – Memfilter Tampilan Heatmap Berdasarkan Tier Plagiarisme
Field Nilai / Penjelasan
Use Case ID & Name UC-REP-03: Memfilter Tampilan Heatmap
Berdasarkan Tier Plagiarisme
Process Owner Modul Visualisasi Laporan
Date Created 24 Juni 2026
Purpose Memfasilitasi pengguna untuk menyaring dan
mengisolasi visualisasi jenis plagiarisme
tertentu pada naskah.
Overview Pengguna mencentang atau menghilangkan
centang filter pada kontrol toolbar (misal:
hanya ingin melihat indikasi Leksikal Merah,
atau hanya Semantik Oranye). Sistem
memperbarui highlight tampilan teks secara
dinamis.
Cross Requirement FR-REP-05
Actor Pengguna Premium, Dosen
Preconditions Pengguna sedang berada di dasbor Interactive
Heatmap laporan lengkap.
Postconditions Sorotan warna pada naskah diperbarui secara
instan sesuai opsi filter yang aktif.
Typical Course of Events 1. Pengguna melihat bilah toolbar filter di atas
naskah heatmap.2. Pengguna menghilangkan
centang pada filter "Tier 3: AI-Generated
(Kuning)".3. Antarmuka secara reaktif
menghapus latar belakang warna kuning pada
teks naskah.4. Pengguna mencentang kembali
opsi filter.5. Antarmuka kembali menampilkan

Field Nilai / Penjelasan
sorotan warna kuning pada koordinat yang
tepat.
Alternative Workflow -
Exceptional Workflow -
UC-REP-04 – Mengunduh Laporan Audit Resmi Format PDF
Field Nilai / Penjelasan
Use Case ID & Name UC-REP-04: Mengunduh Laporan Audit
Resmi Format PDF
Process Owner Modul Pelaporan & PDF Generation Engine
Date Created 24 Juni 2026
Purpose Menerbitkan dan mengunduh berkas laporan
hasil audit resmi berformat PDF beresolusi
tinggi dengan stempel digital.
Overview Pengguna Premium menekan tombol unduh
PDF. Backend merender dokumen PDF yang
memuat ringkasan skor komposit, rincian per
tier, sebaran halaman, daftar sitasi, dan kode
QR verifikasi.
Cross Requirement FR-REP-06, FR-REP-07
Actor Pengguna Premium, Dosen
Preconditions Pengguna memiliki akun dengan hak akses
Premium aktif dan laporan audit berstatus
SUCCESS.
Postconditions Berkas PDF resmi terunduh ke peramban
pengguna; catatan riwayat ekspor terekam di
log audit.
Typical Course of Events 1. Pengguna menekan tombol "Unduh Laporan
PDF Resmi" di dasbor laporan.2. Frontend
mengirimkan permintaan GET
/api/v1/reports/{report_id}/export-pdf.3.
Backend memverifikasi hak akses peran
Premium pengguna.4. Backend
membangkitkan kode QR unik yang mengarah

Field Nilai / Penjelasan
ke endpoint verifikasi publik.5. Mesin
rendering PDF menyusun dokumen PDF
berstandar cetak formal.6. Server mengirimkan
aliran data berkas PDF sebagai respons
unduhan (attachment).7. Peramban pengguna
menerima dan mengunduh berkas PDF ke
perangkat lokal.
Alternative Workflow -
Exceptional Workflow E1: Pengguna Akun Trial Mencoba
Mengunduh: Sistem menahan permintaan dan
menampilkan modal penawaran upgrade akun
Premium: "Fitur ekspor sertifikat PDF resmi
hanya dapat diakses oleh akun Premium."
UC-REP-05 – Memverifikasi Keaslian Laporan via Kode QR
Field Nilai / Penjelasan
Use Case ID & Name UC-REP-05: Memverifikasi Keaslian Laporan
via Kode QR
Process Owner Modul Verifikasi Publik
Date Created 24 Juni 2026
Purpose Memungkinkan pihak ketiga (dosen, penguji,
instansi luar) memvalidasi keaslian dokumen
sertifikat PDF hasil audit sistem.
Overview Penilai memindai kode QR pada lembar PDF
fisik/digital. Peramban membuka halaman
verifikasi publik resmi VeriText AI yang
menampilkan ringkasan data asli hasil audit di
database.
Cross Requirement FR-REP-08
Actor Pengunjung Umum (Guest / Reviewer)
Preconditions Kode QR pada dokumen PDF resmi dipindai
menggunakan kamera perangkat smartphone
atau pemindai QR.
Postconditions Halaman publik menampilkan status validitas
sertifikat audit dan ringkasan skor asli.

Field Nilai / Penjelasan
Typical Course of Events 1. Pengguna memindai kode QR pada berkas
PDF laporan.2. Peramban membuka tautan
verifikasi publik:
https://veritext.ai/verify/{verification_uuid}.3.
Sistem mencari catatan keaslian laporan di
basis data menggunakan UUID tersebut.4.
Sistem menampilkan halaman verifikasi
berstempel hijau: "Laporan Terverifikasi Asli",
memuat Judul Naskah, Nama Pemilik, Tanggal
Pemeriksaan, dan Skor Kesamaan Komposit
resmi.
Alternative Workflow -
Exceptional Workflow E1: Laporan Palsu / UUID Tidak Ditemukan:
Sistem menampilkan halaman peringatan
merah: "Sertifikat Tidak Valid atau Telah
Dihapus dari Sistem."
UC-REP-06 – Melihat Riwayat Hasil Audit Sebelumnya
Field Nilai / Penjelasan
Use Case ID & Name UC-REP-06: Melihat Riwayat Hasil Audit
Sebelumnya
Process Owner Modul Manajemen Riwayat Pemeriksaan
Date Created 24 Juni 2026
Purpose Menampilkan daftar seluruh dokumen yang
pernah diperiksa oleh pengguna beserta skor
ringkas dan statusnya.
Overview Pengguna membuka menu Riwayat. Sistem
menyajikan tabel daftar dokumen dengan
kolom: Tanggal Audit, Nama Berkas, Jumlah
Kata, Persentase Kesamaan, Status, dan tombol
aksi lihat laporan.
Cross Requirement FR-REP-09
Actor Pengguna Terdaftar (Trial / Premium), Dosen
Preconditions Pengguna telah login ke dalam sistem.

Field Nilai / Penjelasan
Postconditions Tabel riwayat audit ditampilkan sesuai filter
tanggal dan pencarian.
Typical Course of Events 1. Pengguna membuka menu "Riwayat Audit"
pada navigasi utama.2. Klien meminta daftar
riwayat dari endpoint /api/v1/audits/history.3.
Server mengembalikan daftar riwayat dokumen
milik pengguna yang bersangkutan.4.
Antarmuka merender tabel riwayat dilengkapi
indikator warna badge skor kesamaan.5.
Pengguna dapat menggunakan kotak pencarian
untuk mencari dokumen berdasarkan nama
berkas.6. Pengguna dapat mengklik tombol
"Buka Laporan" pada baris dokumen yang
diinginkan.
Alternative Workflow -
Exceptional Workflow E1: Belum Ada Riwayat Pemeriksaan: Sistem
menampilkan antarmuka kosong (empty state)
dengan ilustrasi dan tombol aksi: "Belum ada
riwayat. Mulai periksa dokumen pertama
Anda!"
UC-REP-07 – Mengunduh Rekapitulasi Riwayat Audit (Format CSV/Excel)
Field Nilai / Penjelasan
Use Case ID & Name UC-REP-07: Mengunduh Rekapitulasi
Riwayat Audit (Format CSV/Excel)
Process Owner Modul Pelaporan & Ekspor Data
Date Created 24 Juni 2026
Purpose Memungkinkan pengguna mengekspor daftar
riwayat seluruh audit dokumen ke berkas
spreadsheet untuk keperluan arsip data pribadi.
Overview Pengguna menekan tombol ekspor di halaman
riwayat. Sistem menghasilkan berkas CSV
yang merangkum tanggal, nama berkas, skor
leksikal, skor semantik, skor total, dan status
audit.
Cross Requirement FR-REP-10

Field Nilai / Penjelasan
Actor Pengguna Premium, Dosen, Administrator
Preconditions Pengguna telah login dan memiliki setidaknya
satu catatan riwayat audit.
Postconditions Berkas spreadsheet CSV terunduh ke
perangkat pengguna.
Typical Course of Events 1. Pengguna berada di halaman "Riwayat
Audit".2. Pengguna memilih rentang tanggal
pemeriksaan (opsional).3. Pengguna menekan
tombol "Ekspor ke CSV".4. Backend
memformat data catatan riwayat menjadi
struktur baris dan kolom CSV.5. Peramban
menerima aliran data dan mengunduh berkas
dengan nama Rekapitulasi_Audit_VeriText.csv.
Alternative Workflow -
Exceptional Workflow -
UC-CORP-01 – Mengunggah Berkas Korpus Pembanding Secara Massal (Bulk Ingestion)
Field Nilai / Penjelasan
Use Case ID & Name UC-CORP-01: Mengunggah Berkas Korpus
Pembanding Secara Massal (Bulk Ingestion)
Process Owner Modul Manajemen Bank Korpus
Date Created 24 Juni 2026
Purpose Mengunggah sekumpulan berkas naskah
akademik (ZIP atau multi-file PDF) untuk
dijadikan basis data dokumen pembanding
internal.
Overview Dosen atau Admin mengunggah kumpulan
tugas. Sistem mengekstrak berkas,
memvalidasi integritas teks, dan
mendelegasikan proses vektorisasi massal ke
Celery worker.
Cross Requirement FR-CORP-01, FR-CORP-02
Actor Dosen / Asisten Lab (Reviewer), Administrator

Field Nilai / Penjelasan
Preconditions Pengguna telah login dengan kredensial peran
Dosen atau Administrator.
Postconditions Dokumen korpus terdaftar di sistem; tugas
ekstraksi dan vektorisasi massal dikirim ke
antrean Celery.
Typical Course of Events 1. Dosen membuka menu "Bank Korpus
Dokumen".2. Dosen memilih kategori/mata
kuliah (misal: "Proyek IPPL 2026").3. Dosen
mengunggah berkas arsip .zip berisikan naskah
tugas mahasiswa.4. Sistem mengekstrak arsip
zip dan memvalidasi berkas-berkas di
dalamnya.5. Sistem mendaftarkan
dokumen-dokumen korpus ke tabel
corpus_documents.6. Sistem mengirimkan
tugas vektorisasi korpus ke antrean worker
(UC-CORP-02).7. Sistem menampilkan
ringkasan jumlah dokumen yang berhasil
diantrekan untuk pengindeksan.
Alternative Workflow -
Exceptional Workflow E1: Arsip Mengandung Berkas Bukan
Dokumen: Sistem secara otomatis
mengabaikan berkas non-teks (.exe, .jpg) dan
hanya memproses berkas .pdf, .docx, dan .txt.
UC-CORP-02 – Mengindeks Vektor Kalimat Korpus ke PostgreSQL pgvector
Field Nilai / Penjelasan
Use Case ID & Name UC-CORP-02: Mengindeks Vektor Kalimat
Korpus ke PostgreSQL pgvector
Process Owner Worker Pengindeksan Vektor
Date Created 24 Juni 2026
Purpose Mengonversi seluruh kalimat dalam korpus
pembanding menjadi representasi dense vector
dan menyimpannya ke tabel document_chunks.
Overview Worker Celery mengekstrak teks tiap dokumen
korpus, memotong kalimat, menghitung
embedding dengan Sentence Transformers, dan

Field Nilai / Penjelasan
menyimpan vektor ke kolom vector(384)
dengan indeks HNSW.
Cross Requirement FR-CORP-02, FR-CORP-03
Actor Sistem Internal (Celery Worker & PostgreSQL
pgvector)
Preconditions Dokumen korpus baru berstatus
PENDING_INDEX tersedia di basis data.
Postconditions Ribuan vektor kalimat tersimpan di tabel
document_chunks dan siap ditelusuri melalui
kueri jarak kosinus.
Typical Course of Events 1. Worker mengambil berkas korpus dari
antrean penyimpanan.2. Worker mengekstrak
teks naskah dan memotongnya menjadi larik
kalimat.3. Worker menghitung hash
Winnowing dan menyimpannya di tabel
lexical_fingerprints.4. Worker memproses
kalimat ke model Sentence Transformers untuk
menghasilkan vektor embedding 384D.5.
Worker menyisipkan vektor kalimat ke tabel
document_chunks pada PostgreSQL.6. Indeks
graf HNSW secara inkremental memperbarui
struktur pencarian tetangga terdekat.7. Worker
memperbarui status dokumen korpus menjadi
INDEXED.
Alternative Workflow -
Exceptional Workflow E1: Dokumen Terduplikasi Persis: Sistem
mengenali hash SHA-256 dokumen yang
identik dan melewati proses pengindeksan
ulang guna mencegah duplikasi vektor.
UC-CORP-03 – Melihat Daftar Dokumen Bank Korpus
Field Nilai / Penjelasan
Use Case ID & Name UC-CORP-03: Melihat Daftar Dokumen Bank
Korpus

Field Nilai / Penjelasan
Process Owner Modul Manajemen Bank Korpus
Date Created 24 Juni 2026
Purpose Menampilkan daftar seluruh dokumen yang
aktif dijadikan sebagai bahan rujukan
pembanding internal di sistem.
Overview Dosen atau Admin mengakses halaman bank
korpus untuk meninjau judul dokumen,
kategori mata kuliah, tahun, total kalimat
terindeks, dan status ketersediaan.
Cross Requirement FR-CORP-04
Actor Dosen / Asisten Lab, Administrator
Preconditions Pengguna telah login dengan akun Dosen atau
Administrator.
Postconditions Daftar dokumen korpus ditampilkan dalam
bentuk tabel interaktif.
Typical Course of Events 1. Dosen membuka modul "Bank Korpus".2.
Sistem menampilkan tabel daftar naskah
korpus pembanding.3. Dosen dapat menyaring
daftar berdasarkan Kategori Mata Kuliah atau
Tahun Akademik.4. Dosen dapat melihat
statistik total dokumen dan total vektor kalimat
yang terdaftar dalam korpus.
Alternative Workflow -
Exceptional Workflow -
UC-CORP-04 – Mengubah Kategori & Metadata Korpus
Field Nilai / Penjelasan
Use Case ID & Name UC-CORP-04: Mengubah Kategori &
Metadata Korpus
Process Owner Modul Manajemen Bank Korpus
Date Created 24 Juni 2026

Field Nilai / Penjelasan
Purpose Memperbarui label kategori, mata kuliah, atau
tahun akademik pada dokumen korpus
pembanding.
Overview Dosen memilih dokumen korpus dan
memperbarui metadata klasifikasinya agar
pengelompokan naskah tugas tetap rapi dan
terorganisir.
Cross Requirement FR-CORP-04, FR-CORP-05
Actor Dosen / Asisten Lab, Administrator
Preconditions Dokumen korpus yang dituju terdaftar aktif di
sistem.
Postconditions Metadata dokumen korpus diperbarui di tabel
corpus_documents.
Typical Course of Events 1. Dosen mencari dokumen korpus pada tabel
daftar korpus.2. Dosen mengklik tombol "Edit
Metadata".3. Dosen mengubah Nama Label,
Kategori Mata Kuliah, atau Tahun
Akademik.4. Dosen menekan tombol "Simpan
Perubahan".5. Sistem memvalidasi dan
memperbarui data di tabel basis data.6. Sistem
menampilkan notifikasi sukses pembaruan
metadata.
Alternative Workflow -
Exceptional Workflow -
UC-CORP-05 – Menghapus Dokumen dari Bank Korpus
Field Nilai / Penjelasan
Use Case ID & Name UC-CORP-05: Menghapus Dokumen dari
Bank Korpus
Process Owner Modul Manajemen Bank Korpus
Date Created 24 Juni 2026
Purpose Menghapus naskah tertentu dari basis data
pembanding internal jika dokumen tersebut
ditarik atau tidak relevan lagi.

Field Nilai / Penjelasan
Overview Dosen atau Admin memilih dokumen korpus
dan menekan hapus. Sistem menghapus entitas
dokumen beserta seluruh catatan vektor
kalimatnya dari tabel document_chunks.
Cross Requirement FR-CORP-05
Actor Dosen / Asisten Lab, Administrator
Preconditions Pengguna memiliki wewenang untuk
mengelola bank korpus.
Postconditions Dokumen dan seluruh vektor kalimat terkait
dihapus dari indeks pgvector; kapasitas
penyimpanan diperbarui.
Typical Course of Events 1. Pengguna membuka daftar bank korpus.2.
Pengguna mengklik tombol "Hapus" pada baris
dokumen korpus yang dituju.3. Sistem
memunculkan kotak dialog konfirmasi
penghapusan naskah pembanding.4. Pengguna
menyetujui penghapusan.5. Sistem menghapus
seluruh record vektor pada tabel
document_chunks yang berelasi dengan ID
dokumen tersebut.6. Sistem menghapus sidik
jari leksikal dan entitas dokumen korpus.7.
Sistem menampilkan notifikasi: "Dokumen
berhasil dikeluarkan dari bank korpus."
Alternative Workflow -
Exceptional Workflow -
UC-PAY-01 – Melihat Informasi Saldo Kuota Token & Riwayat Pemakaian
Field Nilai / Penjelasan
Use Case ID & Name UC-PAY-01: Melihat Informasi Saldo Kuota
Token & Riwayat Pemakaian
Process Owner Modul Billing & Dompet Pengguna
Date Created 24 Juni 2026
Purpose Memberikan transparansi kepada pengguna
mengenai jumlah sisa kuota audit dan riwayat
pemakaian token.

Field Nilai / Penjelasan
Overview Pengguna membuka menu kuota/billing.
Sistem menampilkan badge sisa token dan
tabel mutasi (tanggal, aksi: debit audit/kredit
top-up, jumlah token, dan sisa saldo).
Cross Requirement FR-PAY-03
Actor Pengguna Terdaftar (Trial / Premium)
Preconditions Pengguna telah login ke dalam sistem.
Postconditions Informasi saldo kuota token dan riwayat mutasi
ditampilkan di layar.
Typical Course of Events 1. Pengguna mengklik widget saldo token pada
navigasi atas atau menu "Dompet Kuota".2.
Klien meminta data saldo dari endpoint
/api/v1/billing/wallet.3. Server mengembalikan
jumlah sisa token aktif dan riwayat mutasi.4.
Antarmuka menampilkan kartu saldo besar dan
tabel riwayat pemotongan/penambahan
token.5. Pengguna dapat meninjau histori
pemakaian token secara rinci.
Alternative Workflow -
Exceptional Workflow -
UC-PAY-02 – Melakukan Pemesanan Paket Token Kuota (Midtrans Snap)
Field Nilai / Penjelasan
Use Case ID & Name UC-PAY-02: Melakukan Pemesanan Paket
Token Kuota (Midtrans Snap)
Process Owner Modul Billing & Gateway Transaksi
Date Created 24 Juni 2026
Purpose Memfasilitasi pembelian paket isi ulang token
kuota atau langganan premium melalui
antarmuka pembayaran Midtrans.
Overview Pengguna memilih paket token pada modal
paywall. Backend meminta Snap Token ke API
Midtrans Sandbox, lalu frontend membuka

Field Nilai / Penjelasan
popup pembayaran Snap untuk transaksi QRIS
/ Virtual Account.
Cross Requirement FR-PAY-04, FR-PAY-05
Actor Pengguna Terdaftar (Trial / Free User)
Preconditions Pengguna telah login ke dalam sistem.
Postconditions Catatan invoice berstatus PENDING tercatat di
basis data; popup pembayaran Midtrans Snap
terbuka di layar pengguna.
Typical Course of Events 1. Pengguna membuka modal "Beli Kuota
Pemeriksaan".2. Pengguna memilih paket
(misal: "Paket Mahasiswa: 10 Token - Rp
25.000").3. Pengguna menekan tombol
"Lanjutkan ke Pembayaran".4. Backend sistem
menerbitkan nomor unik order_id dan
memanggil API Midtrans Snap.5. Midtrans
mengembalikan parameter string snap_token.6.
Frontend memanggil pustaka klien Midtrans
window.snap.pay(snap_token).7. Antarmuka
popup Midtrans Snap tampil di layar pengguna
menyajikan opsi QRIS, GoPay, dan Transfer
Bank.8. Pengguna melakukan simulasi
pembayaran melalui simulator Midtrans.
Alternative Workflow -
Exceptional Workflow E1: Pengguna Menutup Pop-up Pembayaran:
Sistem menangani event onClose, membiarkan
status invoice tetap PENDING selama masa
tenggang 24 jam, dan menampilkan opsi coba
bayar kembali.
UC-PAY-03 – Memproses Webhook Transaksi Pembayaran dari Midtrans
Field Nilai / Penjelasan
Use Case ID & Name UC-PAY-03: Memproses Webhook Transaksi
Pembayaran dari Midtrans
Process Owner Modul Billing & Keamanan Transaksi
Date Created 24 Juni 2026

Field Nilai / Penjelasan
Purpose Menangkap notifikasi status pembayaran resmi
dari server Midtrans, memvalidasi integritas
data, dan memperbarui saldo kuota pengguna
secara instan.
Overview Server Midtrans mengirimkan HTTP POST
webhook. Backend memvalidasi signature
SHA-512. Jika status adalah settlement, status
invoice diubah menjadi PAID dan saldo token
pengguna langsung ditambahkan.
Cross Requirement FR-PAY-06, FR-PAY-07, FR-PAY-08
Actor Server Gateway Pembayaran (Midtrans Server)
Preconditions Pengguna telah menyelesaikan pembayaran di
simulator Midtrans.
Postconditions Invoice berstatus PAID; saldo token bertambah
di tabel token_wallets; respons HTTP 200 OK
dikirim ke Midtrans.
Typical Course of Events 1. Server Midtrans mengirim HTTP POST
payload ke endpoint
/api/v1/payments/webhook.2. Backend
mengekstrak parameter order_id, status_code,
gross_amount, dan signature_key.3. Backend
menghitung signature mandiri menggunakan
rumus hash SHA-512 dengan Server Key
rahasia.4. Backend memastikan signature
mandiri cocok persis dengan signature_key
dari Midtrans.5. Backend memeriksa nilai
parameter transaction_status (bernilai
settlement atau capture).6. Backend membuka
blok transaksi atomik basis data.7. Backend
memperbarui status invoice menjadi PAID dan
mencatat stempel waktu penyelesaian.8.
Backend mengkreditkan jumlah token kuota
yang dibeli ke dompet pengguna.9. Backend
mencatat log transaksi di audit_logs.10.
Backend mengembalikan status HTTP 200 OK
ke server Midtrans.
Alternative Workflow A1: Pembayaran Kedaluwarsa (Expired): Jika
status bernilai expire, backend mengubah
status invoice menjadi EXPIRED tanpa
penambahan token.

Field Nilai / Penjelasan
Exceptional Workflow E1: Signature Tidak Cocok (Tampering
Attack): Backend mendeteksi ketidakcocokan
hash, membatalkan proses, mencatat insiden
keamanan, dan mengembalikan HTTP 403
Forbidden.
UC-PAY-04 – Mengunduh Bukti Pembayaran Digital (Invoice PDF)
Field Nilai / Penjelasan
Use Case ID & Name UC-PAY-04: Mengunduh Bukti Pembayaran
Digital (Invoice PDF)
Process Owner Modul Billing & Dokumentasi Keuangan
Date Created 24 Juni 2026
Purpose Memberikan kuitansi atau faktur pembayaran
resmi berformat PDF bagi pengguna untuk
keperluan klaim atau dokumentasi keuangan.
Overview Pengguna memilih transaksi yang sudah
berhasil (PAID) pada tabel riwayat pembayaran
dan mengunduh berkas tanda terima digital
resmi.
Cross Requirement FR-PAY-09
Actor Pengguna Terdaftar, Pengguna Premium
Preconditions Transaksi pembayaran telah berstatus PAID.
Postconditions Berkas kuitansi invoice PDF terunduh ke
peramban pengguna.
Typical Course of Events 1. Pengguna membuka tab "Riwayat Transaksi
& Invoice".2. Pengguna mencari transaksi
pembayaran yang telah berhasil.3. Pengguna
menekan tombol "Unduh Invoice".4. Backend
menyusun kuitansi invoice berformat PDF
yang mencantumkan Nomor Transaksi,
Tanggal, Item Paket, Metode Pembayaran, dan
Status Lunas.5. Peramban pengguna menerima
aliran data berkas dan menyimpannya secara
lokal.
Alternative Workflow -

Field Nilai / Penjelasan
Exceptional Workflow -
UC-ADM-01 – Melihat Daftar Pengguna Sistem
Field Nilai / Penjelasan
Use Case ID & Name UC-ADM-01: Melihat Daftar Pengguna Sistem
Process Owner Modul Administrasi Pengguna
Date Created 24 Juni 2026
Purpose Menyajikan daftar seluruh akun pengguna
yang terdaftar di dalam sistem untuk keperluan
manajemen dan audit administratif.
Overview Administrator mengakses menu manajemen
pengguna. Sistem menampilkan tabel akun
lengkap dengan informasi nama, email,
institusi, peran (Role), saldo token, status aktif,
dan tanggal daftar.
Cross Requirement FR-ADM-02
Actor Administrator Sistem
Preconditions Administrator telah login dengan hak akses
superuser.
Postconditions Seluruh data akun pengguna ditampilkan pada
tabel admin interaktif.
Typical Course of Events 1. Admin membuka menu "Manajemen
Pengguna".2. Sistem mengambil data seluruh
pengguna dari tabel users.3. Sistem
menampilkan tabel pengguna dilengkapi fitur
filter berdasarkan peran (Trial, Premium,
Dosen, Admin) dan kotak pencarian.4. Admin
dapat mengklik salah satu baris pengguna
untuk melihat rincian aktivitas akun.
Alternative Workflow -
Exceptional Workflow -

UC-ADM-02 – Mengubah Status Pengguna (Suspensi Akun / Aktivasi)
Field Nilai / Penjelasan
Use Case ID & Name UC-ADM-02: Mengubah Status Pengguna
(Suspensi Akun / Aktivasi)
Process Owner Modul Administrasi Pengguna
Date Created 24 Juni 2026
Purpose Menonaktifkan akun pengguna yang
terindikasi melakukan penyalahgunaan sistem
atau mengaktifkan kembali akun yang
dibekukan.
Overview Admin memilih pengguna target dan
mengubah status akun menjadi SUSPENDED
atau ACTIVE. Pengguna berstatus suspend
tidak dapat login atau mengeksekusi audit.
Cross Requirement FR-ADM-03
Actor Administrator Sistem
Preconditions Akun pengguna target terdaftar di sistem dan
bukan merupakan akun diri Admin sendiri.
Postconditions Status pengguna diperbarui di tabel users;
seluruh sesi login aktif milik pengguna target
langsung dicabut.
Typical Course of Events 1. Admin membuka halaman detail pengguna
target.2. Admin mengklik tombol "Bekukan
Akun (Suspend)".3. Admin mengisi alasan
penonaktifan pada formulir modal
konfirmasi.4. Admin menekan tombol
"Konfirmasi Suspensi".5. Sistem memperbarui
atribut is_active menjadi false di basis data.6.
Sistem mencabut seluruh sesi token JWT aktif
milik pengguna tersebut.7. Sistem mencatat log
audit administratif.8. Sistem menampilkan
pesan sukses pembaruan status akun.
Alternative Workflow A1: Mengaktifkan Kembali Akun: Admin
memilih tombol "Aktifkan Akun" pada
pengguna berstatus suspend untuk memulihkan
hak akses pengguna.
Exceptional Workflow E1: Admin Mencoba Menonaktifkan Akun
Sendiri: Sistem memblokir aksi dan
menampilkan peringatan: "Anda tidak dapat

Field Nilai / Penjelasan
menonaktifkan akun Administrator Anda
sendiri."
UC-ADM-03 – Menyesuaikan Saldo Token Pengguna Secara Manual (Koreksi Admin)
Field Nilai / Penjelasan
Use Case ID & Name UC-ADM-03: Menyesuaikan Saldo Token
Pengguna Secara Manual (Koreksi Admin)
Process Owner Modul Administrasi Billing & Kuota
Date Created 24 Juni 2026
Purpose Mengizinkan Administrator menambahkan
atau mengurangi saldo token kuota pengguna
secara manual untuk kompensasi kendala
sistem.
Overview Admin membuka profil pengguna,
memasukkan jumlah nominal perubahan saldo
token (kredit/debit) beserta keterangan alasan,
dan sistem memperbarui saldo di tabel dompet
token.
Cross Requirement FR-ADM-04
Actor Administrator Sistem
Preconditions Administrator telah login dan akun pengguna
target berstatus aktif.
Postconditions Saldo kuota token pengguna diperbarui;
transaksi manual terekam di buku besar mutasi
dompet token.
Typical Course of Events 1. Admin membuka menu profil pengguna
pada panel manajemen pengguna.2. Admin
mengklik tombol "Koreksi Saldo Token".3.
Admin memasukkan jumlah token (misal: +5
untuk kompensasi) dan mengisi catatan
keterangan.4. Admin menekan tombol
"Simpan Koreksi".5. Sistem membuka
transaksi atomik, menambah saldo di tabel
token_wallets, dan mencatat riwayat
penyesuaian manual.6. Sistem menampilkan

Field Nilai / Penjelasan
notifikasi: "Saldo kuota token berhasil
diperbarui."
Alternative Workflow -
Exceptional Workflow -
UC-ADM-04 – Memantau Status Antrean Celery Worker & Latensi Sistem
Field Nilai / Penjelasan
Use Case ID & Name UC-ADM-04: Memantau Status Antrean
Celery Worker & Latensi Sistem
Process Owner Modul Monitoring Infrastruktur
Date Created 24 Juni 2026
Purpose Menyajikan metrik kesehatan sistem dan
pemantauan beban pemrosesan antrean worker
secara langsung (real-time).
Overview Admin membuka dasbor pemantauan sistem.
Sistem menampilkan jumlah tugas aktif di
Celery, kapasitas memori Redis, waktu respons
rata-rata API, dan beban CPU server.
Cross Requirement FR-ADM-05
Actor Administrator Sistem
Preconditions Administrator telah login ke dasbor sistem.
Postconditions Metrik operasional infrastruktur dan status
antrean worker ditampilkan secara visual.
Typical Course of Events 1. Admin membuka menu "Monitoring
Infrastruktur".2. Klien meminta data telemetri
dari endpoint /api/v1/admin/health-metrics.3.
Server memeriksa koneksi PostgreSQL, Redis
ping, dan status worker Celery aktif.4.
Antarmuka menampilkan grafik penggunaan
CPU, utilisasi memori, serta tabel daftar
pekerjaan yang sedang diproses oleh worker.5.
Admin dapat mengidentifikasi jika terjadi
penumpukan antrean audit.
Alternative Workflow -

Field Nilai / Penjelasan
Exceptional Workflow -
UC-ADM-05 – Menjalankan Reindex Tabel Vektor HNSW Manual
Field Nilai / Penjelasan
Use Case ID & Name UC-ADM-05: Menjalankan Reindex Tabel
Vektor HNSW Manual
Process Owner Modul Pemeliharaan Basis Data Vektor
Date Created 24 Juni 2026
Purpose Memperbaiki dan mereorganisasi struktur graf
indeks HNSW pada kolom vektor PostgreSQL
untuk mengembalikan efisiensi pencarian kueri
ANN.
Overview Admin menekan tombol reindex pada panel
pemeliharaan basis data. Sistem menjalankan
perintah SQL REINDEX INDEX secara
terkontrol di latar belakang untuk menata ulang
graf HNSW.
Cross Requirement FR-ADM-06
Actor Administrator Sistem
Preconditions Administrator telah login dan beban
pemrosesan antrean audit sedang dalam status
rendah.
Postconditions Indeks HNSW pada tabel document_chunks
tertata ulang secara optimal; performa kueri
jarak kosinus kembali ke latensi minimal.
Typical Course of Events 1. Admin membuka menu "Pemeliharaan Basis
Data".2. Admin meninjau statistik jumlah
record vektor dan fragmentasi indeks.3. Admin
menekan tombol "Jalankan Reindex Vektor
(HNSW)".4. Sistem menampilkan dialog
konfirmasi peringatan beban komputasi.5.
Admin menyetujui eksekusi reindex.6.
Backend menjalankan perintah pemeliharaan
REINDEX INDEX CONCURRENTLY
idx_document_chunks_vector.7. Setelah

Field Nilai / Penjelasan
selesai, sistem mencatat log pemeliharaan dan
memperbarui stempel waktu reindex terakhir.8.
Sistem menampilkan notifikasi: "Indeks graf
HNSW berhasil diperbarui secara optimal."
Alternative Workflow -
Exceptional Workflow -
UC-ADM-06 – Melihat Log Aktivitas Sistem (Security Audit Trail)
Field Nilai / Penjelasan
Use Case ID & Name UC-ADM-06: Melihat Log Aktivitas Sistem
(Security Audit Trail)
Process Owner Modul Audit Keamanan & Kepatuhan
Date Created 24 Juni 2026
Purpose Memfasilitasi Administrator untuk meninjau
rekaman jejak audit seluruh aktivitas penting di
dalam sistem demi keperluan investigasi
keamanan.
Overview Admin membuka menu log audit. Sistem
menyajikan tabel kronologis yang memuat
stempel waktu (UTC), alamat IP, identitas
pengguna, tipe aksi, dan deskripsi kejadian.
Cross Requirement FR-ADM-07, NFR-SEC-05
Actor Administrator Sistem
Preconditions Administrator telah login ke sistem.
Postconditions Rekaman log audit sistem ditampilkan dengan
fitur pencarian dan filter rentang waktu.
Typical Course of Events 1. Admin membuka menu "Log Aktivitas
Sistem".2. Sistem menampilkan tabel catatan
audit dari tabel audit_logs.3. Admin dapat
memfilter log berdasarkan kategori aksi
(Login, Pembayaran, Hapus Dokumen,
Suspensi Akun).4. Admin dapat melakukan
pencarian log berdasarkan alamat IP atau nama

Field Nilai / Penjelasan
pengguna tertentu.5. Admin dapat mengekspor
catatan log ke berkas teks terarsip.
Alternative Workflow -
Exceptional Workflow -
5. Kebutuhan Non-Fungsional (Non-Functional Requirements)
Kode Deskripsi Kebutuhan Non-Fungsional
Kebutuhan Performa (Performance)
NFR-PERF-01 Sebanyak 95% dari seluruh permintaan endpoint RESTful API
standar (autentikasi, manajemen profil, riwayat audit, modul
billing) harus mengembalikan respons dengan latensi kurang dari
500 milidetik pada beban operasi normal.
NFR-PERF-02 Halaman antarmuka pengguna web (termasuk Dasbor Workspace
dan Riwayat) harus menyelesaikan proses rendering awal (First
Contentful Paint - FCP) dalam waktu kurang dari 1.8 detik pada
koneksi internet dengan kecepatan unduh minimal 5 Mbps.
NFR-PERF-03 Proses ekstraksi k-gram dan komputasi Winnowing Rolling Hash
untuk dokumen dengan volume 3.000 kata tidak boleh melebihi
durasi 300 milidetik.
NFR-PERF-04 Komputasi inferensi vektor kalimat menggunakan model
Sentence Transformers harus mampu memproses minimal 50
kalimat per detik pada konfigurasi standar server CPU
multi-core.
NFR-PERF-05 Kueri penelusuran tetangga terdekat (Approximate Nearest
Neighbor) pada tabel PostgreSQL document_chunks berindeks
HNSW dengan operator jarak kosinus (<=>) harus menghasilkan
luaran dalam waktu kurang dari 150 milidetik untuk basis data
dengan kapasitas hingga 200.000 vektor kalimat.

NFR-PERF-06 Arsitektur antrean tugas terdistribusi Celery harus mampu
mengorkestrasikan minimal 10 tugas audit dokumen secara
simultan (concurrent tasks) tanpa menyebabkan degradasi
memori server (Memory Leak / Out of Memory).
Kebutuhan Keamanan (Security & STRIDE Threat Model)
NFR-SEC-01 Autentikasi sistem wajib menerapkan skema JSON Web Token
(JWT) dengan algoritma HMAC-SHA256 bertanda tangan
kriptografis kuat.
NFR-SEC-02 Endpoint webhook pembayaran wajib memvalidasi tanda tangan
kriptografi SHA-512 dari Midtrans sebelum memproses
transaksi.
NFR-SEC-03 Seluruh mutasi kuota token wajib dikelola eksklusif melalui
transaksi atomik basis data (ACID Transaction Block) di sisi
backend; klien tidak memiliki wewenang memanipulasi nilai
token secara langsung.
NFR-SEC-04 Setiap naskah yang diunggah wajib dihitung hash SHA-256
untuk memverifikasi integritas fisik berkas.
NFR-SEC-05 Sistem wajib mencatat setiap aktivitas kritis (login, unggah
dokumen, debit token, perubahan hak akses, webhook payment)
ke dalam tabel audit_logs append-only yang memuat stempel
waktu presisi (UTC), alamat IP, User-Agent, dan identitas aktor.
NFR-SEC-06 Kata sandi akun wajib disimpan dalam bentuk hash searah
menggunakan algoritma bcrypt dengan salt unik per record
pengguna.
NFR-SEC-07 Seluruh transmisi data antara klien, server API, Redis broker, dan
PostgreSQL wajib diamankan dengan protokol enkripsi TLS 1.3.
NFR-SEC-08 Berkas naskah yang tersimpan di disk server harus diatur dengan
hak akses direktori terbatas (restricted POSIX file permission
chmod 600).
NFR-SEC-09 Sistem wajib membatasi ukuran berkas maksimal 15 MB dan
memvalidasi real MIME-type berkas melalui inspeksi byte biner.

NFR-SEC-10 API Gateway wajib menerapkan pembatasan laju permintaan
(Rate Limiting) maksimal 60 request per menit per alamat IP
untuk endpoint publik.
NFR-SEC-11 Sistem wajib mengevaluasi klaim peran (role claim) pada lapisan
middleware otorisasi backend sebelum kueri bisnis dieksekusi
(Role-Based Access Control).
Kebutuhan Ketersediaan & Keandalan (Availability & Reliability)
NFR-AVAIL-01 Sistem web VeriText AI harus memiliki tingkat ketersediaan
(availability uptime) minimal 99.5% setiap bulan, di luar jadwal
pemeliharaan terencana (scheduled maintenance window).
NFR-AVAIL-02 Target waktu pemulihan sistem dari insiden kegagalan perangkat
lunak atau server crash maksimal adalah 2 jam hingga sistem
kembali melayani permintaan pengguna.
NFR-AVAIL-03 Batas toleransi kehilangan data transaksional maksimal adalah 1
jam. Sistem basis data relasional PostgreSQL wajib dikonfigurasi
dengan pencatatan Write-Ahead Logging (WAL).
NFR-AVAIL-04 Basis data relasional dan tabel indeks vektor harus dibackup
secara otomatis setiap 24 jam sekali pada jam beban terendah
(pukul 02:00 UTC) dan disimpan pada repositori penyimpanan
terisolasi yang terenkripsi.
NFR-AVAIL-05 Apabila worker inferensi Tier 2 mengalami kelebihan beban
sementara, sistem harus tetap mampu menyelesaikan
pemeriksaan Tier 1 (Leksikal) dan memberikan notifikasi
penundaan kepada pengguna tanpa merusak alur sistem (fail-safe
operation).
Kebutuhan Kepatuhan & Privasi Data (Compliance - UU PDP / GDPR)
NFR-COMP-01 Sistem harus meminta persetujuan eksplisit (explicit consent)
dari pengguna pada formulir pendaftaran mengenai pemrosesan
data profil dan penyimpanan naskah dokumen untuk keperluan
komparasi akademik.
NFR-COMP-02 Sistem harus menyediakan mekanisme bagi pengguna untuk
menghapus dokumen naskah yang pernah diunggah beserta
seluruh representasi vektor turunannya dari repositori sistem atas
permintaan pemilik sah dokumen.

NFR-COMP-03 Naskah dokumen yang ditandai oleh Dosen/Institusi sebagai
"Dokumen Rahasia / Hak Cipta Tertutup" tidak boleh dijadikan
bagian dari bank korpus publik yang dapat diakses oleh institusi
luar.
NFR-COMP-04 Data log riwayat pembayaran, transaksi token, dan notifikasi
webhook wajib disimpan dengan integritas data tinggi
(immutable ledger) selama minimal 3 tahun untuk keperluan
rekonsiliasi keuangan dan audit akuntansi.
Kebutuhan Pemeliharaan & Skalabilitas (Maintainability & Scalability)
NFR-SCALE-01 Seluruh kode sumber backend wajib mengadopsi prinsip Clean
Architecture modular (terbagi tegas atas layer routers, services,
repositories, schemas, dan workers) sehingga penambahan modul
algoritma deteksi baru dapat dilakukan tanpa mengubah logika
modul lainnya.
NFR-SCALE-02 Seluruh perubahan skema basis data PostgreSQL (termasuk
penambahan ekstensi tipe vektor atau indeks HNSW baru) wajib
dikelola melalui skrip migrasi terversi menggunakan pustaka
Alembic.
NFR-SCALE-03 Arsitektur pemrosesan Celery harus dirancang stateless sehingga
kapasitas daya tampung inferensi AI dapat ditingkatkan secara
elastis (horizontal scaling) hanya dengan menambah instans
worker baru yang terkoneksi ke Redis broker yang sama.
NFR-SCALE-04 Seluruh berkas modul logika bisnis esensial (terutama algoritma
rolling hash Winnowing, formula Cosine Similarity, dan
kalkulasi varians Burstiness) wajib memuat dokumentasi
komentar docstring standar Sphinx/PEP 257 yang menjelaskan
parameter masukan, tipe data, nilai kembalian, dan kompleksitas
asimtotik waktu/ruang.
Daftar Pustaka
[1] IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements
Specifications.
 New York, NY: IEEE Computer Society, 1998.
[2] ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes —
 Requirements engineering. Geneva, Switzerland: ISO/IEC/IEEE, 2018.
[3] S. Schleimer, D. S. Wilkerson, and A. Aiken, "Winnowing: local algorithms for document

 fingerprinting," in Proceedings of the 2003 ACM SIGMOD International Conference on
 Management of Data (SIGMOD '03), San Diego, CA, USA, 2003, pp. 76–85.
[4] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese
BERT-Networks,"
 in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing
 (EMNLP-IJCNLP), Hong Kong, 2019, pp. 3982–3992.
[5] P. Henderson et al., "pgvector: Open-source vector similarity search for Postgres,"
 GitHub repository, 2024. [Online]. Tersedia: https://github.com/pgvector/pgvector.
[6] FastAPI Documentation, "FastAPI Framework, High Performance, Easy to Learn, Fast to
Code,"
 [Online]. Tersedia: https://fastapi.tiangolo.com/.
[7] VUE.js Documentation, "VUE.js 14 App Router Documentation," Vercel, [Online].
 Tersedia: https://VUEjs.org/docs.
[8] Celery Project, "Celery: Distributed Task Queue," [Online]. Tersedia: https://docs.celeryq.dev/.
[9] Midtrans API Documentation, "Core API & Snap Payment Gateway Integration Guide,"
[Online].
 Tersedia: https://docs.midtrans.com/.
[10] OWASP Foundation, "OWASP Top Ten Web Application Security Risks," 2021. [Online].
 Tersedia: https://owasp.org/Top10/.
[11] Pemerintah Republik Indonesia, Undang-Undang Republik Indonesia Nomor 27 Tahun 2022
 tentang Perlindungan Data Pribadi (UU PDP). Lembaran Negara RI Tahun 2022 Nomor 196.
[12] G. Booch, J. Rumbaugh, and I. Jacobson, The Unified Modeling Language User Guide, 2nd
ed.
 Boston, MA: Addison-Wesley, 2005.