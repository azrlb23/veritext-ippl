# Daftar Lengkap Halaman & Seluruh State Antarmuka VeriText AI

Format penamaan dan hierarki state di bawah ini mengadopsi taksonomi sistematis FMS (*Fuel Management System* - `design/`), diselaraskan dengan standar **`ui-ux-pro-max`** dan **`anti-ai-slop`**, mencakup seluruh kemungkinan status UI, interaksi mikro, error code (404, 403, 401, 500, 429), OAuth Google, modal dialog, hingga variasi responsif di smartphone.

---

### 1. Landing Page (Beranda Publik)
**Rute:** `/`
1. `landing--default` (Tampilan utama: Hero banner editorial, statistik platform, penjelasan 4-tier pipeline deteksi, CTA "Mulai Pengujian")
2. `landing--navbar-scrolled` (Navbar transparan beralih menjadi solid sticky dengan border 1px dan backdrop blur halus)
3. `landing--navbar-mobile-drawer` (Menu drawer navigasi samping terbuka pada layar smartphone)
4. `landing--demo-tab-lexical` (Interactive demo beralih ke naskah contoh plagiarisme leksikal verbatim / copy-paste)
5. `landing--demo-tab-semantic` (Interactive demo beralih ke naskah contoh parafrasa cerdas semantik pgvector)
6. `landing--demo-tab-stylometric` (Interactive demo beralih ke naskah contoh manipulasi generator AI / ChatGPT)
7. `landing--demo-evaluating` (Indikator loading mikro 200ms saat berpindah tab naskah demo)
8. `landing--demo-highlight-hover` (Tooltip penjelasan muncul saat pengguna mengarahkan kursor ke kalimat naskah ber-highlight)

---

### 2. Login (Masuk Portal Akun)
**Rute:** `/login`
1. `login--default` (Formulir bersih: Input Email Institusi dan Input Kata Sandi dengan ikon mata tertutup)
2. `login--show-password` (Pengguna menekan tombol mata: teks kata sandi terlihat, ikon mata terbuka)
3. `login--oauth-google-click` (Pengguna menekan tombol "Masuk dengan Akun Google Kampus")
4. `login--oauth-google-redirecting` (Layar transisi/spinner mengarahkan browser ke consent screen Google OAuth2)
5. `login--oauth-google-callback` (Layar memproses otorisasi token Google dari callback URL)
6. `login--oauth-google-failed` (Alert merah: "Gagal masuk dengan Google. Akun tidak terdaftar atau domain email tidak diizinkan")
7. `login--submitting` (Tombol masuk menampilkan spinner loading, seluruh input di-disable sementara)
8. `login--error-invalid` (Alert merah: "Invalid email or password" disertai tombol dismiss silang X)
9. `login--error-empty-field` (Validasi inline: border merah pada input email atau kata sandi yang dikosongkan)
10. `login--error-lockout` (Alert merah HTTP 429: "Akun terkunci sementara karena 5x kegagalan berturut-turut. Tunggu 15 menit")
11. `login--success-redirect` (Status otentikasi valid, token JWT tersimpan, browser dialihkan otomatis ke `/dashboard`)

---

### 3. Register (Pendaftaran Akun Baru)
**Rute:** `/register`
1. `register--default` (Formulir bersih: Nama Lengkap, Email Kampus, Nama Institusi, Kata Sandi, Konfirmasi Sandi, Checkbox Persetujuan UU PDP)
2. `register--show-password` (Toggle mata aktif pada input kata sandi)
3. `register--show-confirm-password` (Toggle mata aktif pada input konfirmasi kata sandi)
4. `register--oauth-google` (Pendaftaran instan satu klik menggunakan identitas Google OAuth Kampus)
5. `register--password-mismatch` (Validasi instan: alert merah "Konfirmasi kata sandi tidak cocok")
6. `register--password-weak` (Peringatan inline jika sandi kurang dari 8 karakter)
7. `register--pdp-uncheck-warning` (Alert peringatan jika checkbox persetujuan UU PDP No. 27/2022 sengaja dimatikan pengguna)
8. `register--submitting` (Spinner loading aktif pada tombol pendaftaran)
9. `register--error-duplicate` (Alert merah HTTP 400: "Alamat email kampus sudah terdaftar pada sistem")
10. `register--success` (Banner hijau berhasil mendaftar, otomatis berpindah ke halaman login)

---

### 4. Lupa Kata Sandi (Password Reset Request)
**Rute:** `/forgot-password` *(Spesifikasi Baru)*
1. `forgot-password--default` (Input tunggal: Alamat Email Terdaftar dan tombol "Kirim Tautan Pemulihan")
2. `forgot-password--submitting` (Spinner loading saat sistem memverifikasi email dan membuat token kriptografis)
3. `forgot-password--success-sent` (Kartu konfirmasi hijau: "Tautan pemulihan kata sandi telah dikirim ke email institusi Anda")
4. `forgot-password--error-not-found` (Alert merah jika alamat email tidak dikenali)
5. `forgot-password--rate-limited` (Alert HTTP 429: "Anda telah meminta reset sandi terlalu sering. Harap tunggu beberapa menit")

---

### 5. Atur Ulang Sandi Baru (Password Reset Confirmation)
**Rute:** `/reset-password?token=...` *(Spesifikasi Baru)*
1. `reset-password--default` (Input Kata Sandi Baru dan Konfirmasi Kata Sandi Baru)
2. `reset-password--invalid-token` (Alert merah: "Tautan pemulihan tidak valid atau telah kedaluwarsa")
3. `reset-password--submitting` (Spinner loading saat hash sandi baru disimpan ke database)
4. `reset-password--success` (Notifikasi sukses sandi berhasil diperbarui, tombol direct ke Login)

---

### 6. Dashboard (Workspace Audit Naskah)
**Rute:** `/dashboard`
1. `dashboard--default` (Kanvas utama editorial bersih: Ringkasan Saldo Token, Metrik Pengujian, Segmented Tabs, Dropzone Unggah, Tabel Riwayat)
2. `dashboard--tab-all` (Tab aktif: Menampilkan seluruh kanvas lengkap secara berurutan)
3. `dashboard--tab-upload` (Tab aktif: Fokus pada area dropzone unggah berkas dan pemilihan kedalaman audit)
4. `dashboard--tab-active` (Tab aktif: Fokus pada daftar antrean audit yang sedang diproses worker Celery)
5. `dashboard--tab-history` (Tab aktif: Fokus pada tabel riwayat seluruh naskah yang pernah diuji)
6. `dashboard--file-dragging` (Efek hover visual saat pengguna menyeret berkas ke atas kotak dropzone)
7. `dashboard--file-selected` (Berkas terpilih: Nama file, ukuran dalam MB, dan icon format muncul di dropzone)
8. `dashboard--depth-hybrid` (Mode audit dipilih: Hybrid Penuh Tier 1-4, memotong 2 token)
9. `dashboard--depth-lexical` (Mode audit dipilih: Leksikal Cepat Tier 1, memotong 1 token)
10. `dashboard--insufficient-token` (Alert kuning & tombol audit terkunci: "Saldo token Anda 0. Cukupi kuota terlebih dahulu")
11. `dashboard--uploading` (Progress bar persentase pengunggahan dokumen dari browser ke server backend)
12. `dashboard--processing-worker` (Animasi kartu pemrosesan bertahap: Parser Naskah -> Tier 1 -> Tier 2 -> Tier 3 Stilometri)
13. `dashboard--cancelling-task` (Dialog konfirmasi & proses pembatalan audit yang sedang berjalan)
14. `dashboard--task-failed` (Badge merah dan pesan galat pada kartu antrean jika naskah korup atau format tidak terbaca)
15. `dashboard--empty-history` (Tampilan ramah saat akun mahasiswa baru belum pernah melakukan audit naskah sama sekali)
16. `dashboard--history-populated-desktop` (Tabel tabular data-dense di layar laptop/desktop)
17. `dashboard--history-populated-mobile` (Tampilan kartu ringkas vertikal adaptif di layar smartphone < 640px)
18. `dashboard--syncing-status` (Ikon rotasi berputar saat tombol "Sinkronkan Status" ditekan manual)

---

### 7. Detail Laporan Audit & Heatmap (Audit Inspection Workbench)
**Rute:** `/audits/:id`
1. `audit-detail--loading` (Skeleton loader berkedip halus pada seluruh panel teks dan grafik metrik)
2. `audit-detail--analyzed-desktop` (Layout Split-Pane 2 kolom: Teks naskah ber-heatmap di kiri, panel inspeksi di kanan)
3. `audit-detail--analyzed-mobile-text` (Layar smartphone: Tab aktif "Naskah & Heatmap")
4. `audit-detail--analyzed-mobile-scores` (Layar smartphone: Tab aktif "Ringkasan Skor & Sumber")
5. `audit-detail--tab-summary` (Panel kanan menampilkan Speedometer Similarity Composite, skor T1, T2, T3, dan Catatan Diagnostik AI)
6. `audit-detail--tab-sources` (Panel kanan menampilkan tabel sumber referensi yang cocok dari Bank Korpus)
7. `audit-detail--tab-diff` (Panel kanan menampilkan perbandingan kalimat berdampingan: teks naskah vs teks asli korpus)
8. `audit-detail--sentence-modal` (Modal pop-up terbuka saat kalimat di-klik: menampilkan tier deteksi, persentase kemiripan, dan sumber spesifik)
9. `audit-detail--exporting-pdf` (Spinner loading saat sistem men-generate sertifikat PDF resmi ber-QR Code)
10. `audit-detail--export-success` (File sertifikat PDF otomatis terunduh ke perangkat pengguna)
11. `audit-detail--delete-dialog` (Dialog konfirmasi penghapusan naskah permanen sesuai kepatuhan hak UU PDP)
12. `audit-detail--deleting` (Proses penghapusan naskah, vektor embeddings, dan log dari server)

---

### 8. Bank Korpus Dokumen (Corpus Repository)
**Rute:** `/corpus` *(Khusus Dosen / Reviewer & Admin)*
1. `corpus--loading` (Skeleton table loader saat mengambil data koleksi dokumen korpus)
2. `corpus--empty` (Empty state: "Belum ada dokumen referensi di Bank Korpus. Unggah dokumen pertama Anda")
3. `corpus--populated-desktop` (Tabel lengkap naskah referensi: Judul, Penulis, Kategori, Jumlah Paragraf, Status Vektor pgvector)
4. `corpus--populated-mobile` (Daftar kartu vertikal korpus adaptif untuk layar smartphone)
5. `corpus--filter-active` (Pengguna menyaring korpus berdasarkan kata kunci atau kategori jurnal/skripsi/tesis)
6. `corpus--filter-no-results` (Tampilan kosong: "Tidak ditemukan dokumen korpus dengan kata kunci tersebut")
7. `corpus--upload-modal-single` (Dialog pop-up unggah naskah korpus tunggal: Judul, Penulis, Kategori, Berkas)
8. `corpus--upload-modal-zip` (Dialog pop-up unggah arsip naskah massal / batch upload format ZIP)
9. `corpus--uploading` (Progress bar proses unggah dan dekompresi aman arsip ZIP)
10. `corpus--indexing-badge` (Badge status kuning "Mengindeks Vektor..." saat Celery memproses HNSW pgvector)
11. `corpus--delete-confirm-modal` (Dialog konfirmasi sebelum menghapus dokumen referensi korpus)

---

### 9. Dompet Token & Billing (Token Balance & Invoices)
**Rute:** `/billing`
1. `billing--default` (Kartu Saldo Aktif, 3 Pilihan Paket Kuota: Starter, Pro, Institutional, dan Riwayat Pembayaran)
2. `billing--topup-modal` (Dialog pop-up konfirmasi pembelian: ringkasan paket, rincian biaya, dan pilihan metode bayar)
3. `billing--payment-qris` (Tampilan kode QRIS dinamis untuk dipindai melalui mobile banking / e-wallet)
4. `billing--payment-va` (Tampilan nomor Virtual Account beserta petunjuk transfer)
5. `billing--payment-checking` (Status background polling: "Mengecek status pembayaran Anda...")
6. `billing--payment-success` (Banner hijau berhasil: Saldo token bertambah, invoice otomatis terbit)
7. `billing--payment-expired` (Pemberitahuan bahwa sesi pembayaran telah habis waktu)
8. `billing--empty-history` (Tampilan kosong pada tabel riwayat transaksi pembayaran)
9. `billing--history-populated-desktop` (Tabel transaksi: Kode Invoice, Tanggal, Nominal, Metode, Status, Aksi Unduh PDF)
10. `billing--history-populated-mobile` (Daftar kartu riwayat invoice vertikal pada smartphone)
11. `billing--downloading-invoice` (Spinner loading saat mengunduh berkas faktur resmi PDF)

---

### 10. Verifikasi Sertifikat QR (Public Certificate Validator)
**Rute:** `/verify/:uuid?`
1. `verify--empty-input` (Layar formulir pencarian: Kotak input kode UUID sertifikat dan tombol "Verifikasi Keaslian")
2. `verify--camera-scanner-active` (Viewfinder kamera aktif pada smartphone untuk memindai barcode QR fisik dari dokumen cetak)
3. `verify--camera-permission-denied` (Pesan peringatan jika izin kamera ditolak oleh browser pengguna)
4. `verify--verifying` (Spinner loading: Sistem memeriksa keabsahan tanda tangan kriptografis di database)
5. `verify--valid` (Sertifikat SAH: Banner hijau resmi, Judul Naskah, Penulis, Lembaga, Skor Komposit, Waktu Penerbitan, Digital Signature)
6. `verify--invalid` (Sertifikat TIDAK VALID: Banner merah "Dokumen tidak ditemukan atau sertifikat telah dipalsukan")
7. `verify--tampered-warning` (Peringatan integritas: "Hash berkas tidak cocok dengan catatan hash saat pengujian pertama")

---

### 11. Konsol Tata Kelola Admin (Executive Administration Portal)
**Rute:** `/admin` *(Khusus Super Administrator)*
1. `admin--sidebar-expanded` (Persistent left sidebar navigasi Zendenta Ink Black terbuka penuh di desktop)
2. `admin--sidebar-mobile-drawer` (Sidebar menciut menjadi slide-over mobile drawer saat dibuka di smartphone)
3. `admin--tab-overview` (Dashboard telemetri: Grafik utilisasi server, total pengujian naskah, load worker Celery)
4. `admin--tab-users` (Tabel manajemen pengguna: Ubah role TRIAL/PREMIUM/REVIEWER/ADMIN, toggle akun aktif/suspend)
5. `admin--user-edit-modal` (Modal pop-up untuk menyetel kuota token khusus atau mereset kredensial pengguna)
6. `admin--tab-config` (Panel formulir pengaturan bobot T1 Leksikal, T2 Semantik, T3 Stilometri, k-gram, dan HNSW)
7. `admin--config-saving` (Indikator saat konfigurasi algoritma baru disimpan ke database `system_configs`)
8. `admin--tab-logs` (Tabel immutable security audit logs: pencatatan login, ekspor PDF, modifikasi sistem)
9. `admin--logs-exporting-csv` (Proses ekspor data log ke format CSV dengan sanitasi anti-CSV injection OWASP)
10. `admin--tab-pdp` (Panel retensi data UU PDP No. 27/2022: tombol pemicu pembersihan naskah kedaluwarsa 30 hari)
11. `admin--pdp-reaper-running` (Status worker zombie reaper sedang menghapus berkas naskah kedaluwarsa dari disk)

---

### 12. Halaman Galat Sistem & Keamanan (Error & Edge Case Pages)

#### A. 401 Unauthorized (Belum Login / Sesi Kedaluwarsa)
**Rute:** `/401` *(atau redirect otomatis ke `/login`)*
1. `error-401--expired-session` (Banner merah notifikasi: "Sesi Anda telah berakhir demi keamanan. Silakan masuk kembali")
2. `error-401--token-revoked` (Pemberitahuan bahwa token akses tidak valid karena login di perangkat lain)

#### B. 403 Forbidden (Akses Ditolak / Tidak Berhak)
**Rute:** `/403`
1. `error-403--student-to-admin` (Ilustrasi gembok & pesan: "Halaman ini khusus untuk Super Administrator. Akun Anda tidak memiliki hak akses")
2. `error-403--student-to-corpus` (Pesan: "Bank Korpus hanya dapat diakses oleh Dosen / Tim Penilai Akademik")
3. `error-403--action-back-dashboard` (Tombol navigasi jelas "Kembali ke Dashboard Mahasiswa")

#### C. 404 Not Found (Halaman / Dokumen Tidak Ditemukan)
**Rute:** `/:pathMatch(.*)*`
1. `error-404--page-not-found` (Ilustrasi minimalis editorial: "Halaman yang Anda cari tidak tersedia atau tautan salah")
2. `error-404--audit-expired` (Konteks naskah: "Laporan audit dengan ID tersebut tidak ditemukan atau telah dihapus permanen sesuai masa retensi")
3. `error-404--action-home` (Tombol utama "Kembali ke Beranda" dan "Pusat Bantuan")

#### D. 429 Too Many Requests (Rate Limiting / Anti-Spam)
**Rute:** Pop-up Modal / Dedicated State
1. `error-429--login-brute-force` (Hitung mundur 15 menit pencegahan serangan kata sandi)
2. `error-429--api-rate-limit` (Pemberitahuan "Permintaan audit terlalu cepat. Mohon beri jeda 30 detik antar pengujian")

#### E. 500 & 503 Internal Server Error / Service Unavailable
**Rute:** `/500`
1. `error-500--database-disconnected` (Peringatan sistem: "Gagal menghubungkan ke pangkalan data PostgreSQL")
2. `error-503--worker-unavailable` (Peringatan antrean: "Antrean Celery worker sedang dalam perawatan. Berkas Anda tetap aman dalam antrean")
3. `error-500--action-retry` (Tombol interaktif "Coba Muat Ulang Sekarang")
