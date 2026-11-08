# Katalog Definitif Seluruh Halaman & State Antarmuka VeriText AI
**Standar Desain:** `ui-ux-pro-max` (WCAG 2.1 AA, Touch Target 44px, Strict 6-Quadrant States) & `anti-ai-slop` (Editorial Data-Dense, 1px Crisp Borders, Tanpa Mockup macOS Mengambang).  
**Referensi Taksonomi:** FMS (*Fuel Management System*).

Dokumen ini memetakan **100% seluruh kemungkinan state** pada aplikasi VeriText AI tanpa ada yang terlewat, mencakup:
1. **6 Kuadran Inti State:** `Idle/Default`, `Loading/Skeleton`, `Empty (Zero-data)`, `Active/Processing`, `Error/Failure`, `Dialog Modal/Action Sheet`.
2. **Kondisi Khusus:** OAuth2 Google SSO, Verifikasi Kriptografis, Countdown Lockout Brute-Force, Filter & Paginasi, dan Hak Akses RBAC (Tamu, Mahasiswa TRIAL, Mahasiswa PREMIUM, Dosen/Reviewer, Super Admin).
3. **Perilaku Responsif Adaptif:** Breakpoint Smartphone (`< 640px`), Tablet (`768px - 1023px`), dan Desktop (`>= 1024px`).
4. **Halaman Error Sistem:** 400, 401, 403, 404, 408, 413, 422, 429, 500, 502, 503, dan Offline Connectivity.

---

## 1. Landing Page (Beranda Publik)
**Rute:** `/` | **Akses:** Publik (Semua Pengguna)

1. `landing--default-idle`
   - Header hero editorial tipografi serif, subheader ringkas, badge "Versi 2.4 Hibrida".
   - Tombol CTA primer "Mulai Audit Naskah" dan CTA sekunder "Lihat Dokumentasi Pipeline".
   - Diagram 4-tier pipeline deteksi (Tier 1 Leksikal Rabin-Karp, Tier 2 Semantik pgvector, Tier 3 Stilometri LLM Anomaly, Tier 4 Agregator Komposit).
   - Metrik statistik platform (Total naskah diaudit, akurasi deteksi parafrasa, kecepatan analisis rata-rata).
2. `landing--navbar-transparent`
   - Navbar melayang di bagian paling atas dengan latar transparan saat halaman belum digulir (*scroll position = 0*).
3. `landing--navbar-scrolled-sticky`
   - Navbar bertransformasi menjadi solid putih (`bg-white/95 backdrop-blur-md`) dengan garis pembatas 1px tegas (`border-b border-[#ededed]`) saat halaman digulir ke bawah.
4. `landing--navbar-mobile-drawer-open`
   - Menu drawer navigasi samping terbuka penuh di smartphone dengan tombol close silang (X) dan touch target 44px.
5. `landing--demo-tab-lexical-active`
   - Tab "Leksikal" aktif pada kotak interactive demo: teks memperlihatkan penjiplakan salin-tempel langsung dengan highlight merah tebal (`#EF4444`).
6. `landing--demo-tab-semantic-active`
   - Tab "Semantik" aktif: teks memperlihatkan parafrasa cerdas sinonim/restrukturisasi kalimat dengan highlight oranye (`#F97316`).
7. `landing--demo-tab-stylometric-active`
   - Tab "Stilometri AI" aktif: teks memperlihatkan anomali generator AI (ChatGPT/Claude) dengan highlight kuning keemasan (`#EAB308`).
8. `landing--demo-evaluating-micro`
   - Indikator evaluasi mikro (progres bar tipis 200ms `ease-out`) saat pengguna mengklik contoh teks demo berbeda.
9. `landing--demo-highlight-hover`
   - Popover tooltip mikro muncul di kursor saat pengguna mengarahkan mouse (*hover*) ke kalimat berwarna di demo, menampilkan persentase kemiripan dan tier deteksi.
10. `landing--footer-standard`
    - Footer lengkap: tautan legalitas UU PDP No. 27/2022, standar etika akademik, tautan verifikasi sertifikat QR, hak cipta institusi.

---

## 2. Login (Masuk Portal Akun)
**Rute:** `/login` | **Akses:** Tamu (Guest Only)

1. `login--default-idle`
   - Kartu login minimalis terpusat (`max-w-[420px]`).
   - Input Alamat Email Kampus / Institusi dengan placeholder `nama@kampus.ac.id`.
   - Input Kata Sandi bertipe `password` dengan ikon mata tertutup (*eye-off*).
   - Checkbox "Ingat sesi saya di perangkat ini".
   - Tombol "Masuk Sekarang →" (state siap klik).
   - Tombol sekunder "Masuk dengan Akun Google Kampus (SSO)".
2. `login--show-password-active`
   - Pengguna menekan tombol toggle mata: tipe input berubah dinamis menjadi `type="text"`, password terbaca, ikon beralih ke mata terbuka (*eye*). Tombol memiliki `type="button"` sehingga tidak memicu form submit.
3. `login--input-focus`
   - State saat kursor berada di dalam input: ring fokus tegas 2px (`focus:ring-2 focus:ring-[#17191c] focus:border-transparent`).
4. `login--empty-field-validation`
   - Pengguna menekan submit saat field kosong: pesan error inline muncul di bawah input terkait dengan icon peringatan dan teks merah (`text-red-600 text-xs`).
5. `login--email-format-invalid`
   - Format email tidak menyertakan `@` atau domain valid: inline error "Format email institusi tidak valid".
6. `login--submitting-loading`
   - Tombol "Masuk Sekarang" menampilkan spinner animasi putar, teks berubah menjadi "Memverifikasi...", seluruh input dinonaktifkan (`disabled:opacity-60 cursor-not-allowed`).
7. `login--error-invalid-credentials`
   - Alert merah muncul di atas form: *"Invalid email or password"*. Tombol dismiss silang (X) aktif dan dapat diklik untuk menyembunyikan alert.
8. `login--error-account-inactive`
   - Alert kuning: *"Akun Anda telah dinonaktifkan oleh Administrator. Silakan hubungi helpdesk akademik."*
9. `login--error-lockout-429`
   - Alert merah proteksi brute-force OWASP (setelah 5x percobaan gagal): *"Akun terkunci sementara demi keamanan. Coba kembali dalam [MM:SS]"* dengan visual countdown timer dinamis.
10. `login--oauth-google-redirecting`
    - Layar transisi putih bersih dengan spinner di tengah: *"Mengarahkan ke Google Identity Service..."*
11. `login--oauth-google-callback-processing`
    - Halaman menangani parameter URL callback dari Google OAuth2 (`/login/callback?code=...`): *"Menyinkronkan profil Google Kampus..."*
12. `login--oauth-google-domain-rejected`
    - Alert merah: *"Akses ditolak. Hanya email dengan domain institusi akademik (.ac.id / .edu) yang diizinkan masuk via Google SSO."*
13. `login--success-redirect`
    - Banner sukses hijau mikro: *"Autentikasi berhasil. Mengalihkan ke workspace..."* lalu otomatis me-redirect ke `/dashboard` atau URL tujuan awal (`?redirect=...`).

---

## 3. Register (Pendaftaran Akun Baru)
**Rute:** `/register` | **Akses:** Tamu (Guest Only)

1. `register--default-idle`
   - Formulir terstruktur: Nama Lengkap, Email Kampus, Nama Institusi / Universitas, Kata Sandi, Konfirmasi Sandi.
   - Checkbox persetujuan pemrosesan dokumen sesuai UU Perlindungan Data Pribadi (UU PDP No. 27/2022) tercentang secara default.
   - Tombol "Daftar Akun Baru →".
   - Tombol "Daftar Otomatis dengan Google Kampus".
2. `register--show-password-active`
   - Toggle mata pada input kata sandi aktif (teks terlihat).
3. `register--show-confirm-password-active`
   - Toggle mata pada input konfirmasi kata sandi aktif secara independen.
4. `register--password-strength-meter`
   - Indikator kekuatan kata sandi di bawah input (Lemah / Sedang / Kuat) berdasarkan kombinasi panjang huruf besar, angka, dan simbol.
5. `register--password-mismatch-error`
   - Validasi instan: alert merah *"Konfirmasi kata sandi tidak cocok dengan kata sandi pertama"*.
6. `register--pdp-uncheck-warning`
   - Pengguna menghapus centang persetujuan UU PDP: tombol submit dinonaktifkan dan muncul tooltip informatif *"Persetujuan pemrosesan data wajib disetujui sesuai regulasi privasi naskah akademik."*
7. `register--submitting-loading`
   - Tombol pendaftaran menampilkan spinner, teks "Mendaftarkan Akun...", seluruh field input read-only.
8. `register--error-duplicate-email`
   - Alert merah dari backend: *"Email institusi tersebut sudah terdaftar. Silakan masuk atau gunakan email lain."*
9. `register--error-invalid-institution`
   - Alert peringatan jika nama institusi dikosongkan.
10. `register--success-confirmation`
    - Layar konfirmasi pendaftaran berhasil dengan pesan *"Akun berhasil dibuat dengan 1 Saldo Token Uji Coba Gratis. Silakan masuk."* dengan tombol CTA langsung ke `/login`.
11. `register--responsive-mobile`
    - Di layar smartphone (< 640px), grid input kata sandi dan konfirmasi sandi otomatis bertumpuk 1 kolom vertikal (`grid-cols-1 sm:grid-cols-2`).

---

## 4. Lupa Kata Sandi (Password Reset Request)
**Rute:** `/forgot-password` | **Akses:** Tamu (Guest Only)

1. `forgot-password--default-idle`
   - Formulir sederhana terpusat: Input Alamat Email Institusi Terdaftar dan tombol "Kirim Tautan Pemulihan".
2. `forgot-password--submitting-loading`
   - Spinner loading pada tombol submit: backend memvalidasi email dan membuat token kriptografis berbatas waktu (15 menit).
3. `forgot-password--success-card`
   - Kartu konfirmasi hijau: *"Tautan pemulihan kata sandi telah dikirim ke email institusi Anda. Silakan periksa folder Inbox atau Spam."*
4. `forgot-password--error-email-not-found`
   - Alert informatif standar keamanan: *"Jika email terdaftar di sistem, tautan pemulihan telah dikirim"* (tidak membocorkan keberadaan email kepada penyerang).
5. `forgot-password--rate-limited-429`
   - Alert merah: *"Anda telah meminta tautan pemulihan terlalu sering. Harap tunggu 5 menit sebelum mencoba kembali."*

---

## 5. Setel Ulang Sandi Baru (Password Reset Confirmation)
**Rute:** `/reset-password?token=...` | **Akses:** Tamu dengan Token Valid

1. `reset-password--token-verifying`
   - Layar memverifikasi keabsahan token reset sandi dari parameter URL.
2. `reset-password--token-invalid-expired`
   - Alert merah dengan icon gembok rusak: *"Tautan pemulihan kata sandi tidak valid atau telah kedaluwarsa. Silakan ajukan permohonan baru."* dengan tombol "Kembali ke Lupa Sandi".
3. `reset-password--form-idle`
   - Input Kata Sandi Baru dan Input Konfirmasi Kata Sandi Baru dengan toggle mata show/hide password.
4. `reset-password--submitting-loading`
   - Spinner loading saat menyimpan hash password baru (bcrypt).
5. `reset-password--success-modal`
   - Dialog sukses: *"Kata sandi Anda berhasil diperbarui. Silakan masuk dengan kata sandi baru Anda."* dengan tombol CTA langsung ke `/login`.

---

## 6. Dashboard (Workspace Audit Naskah)
**Rute:** `/dashboard` | **Akses:** Mahasiswa & Pengguna Terdaftar

1. `dashboard--default-idle`
   - Header editorial datar (*flat*): Nama Pengguna, Badge Institusi, Badge Tier Akun (`TRIAL` / `PREMIUM`), Tombol "Sinkronkan Status".
   - Segmented Horizontal Tabs: `[ Semua ]` `[ Unggah Naskah ]` `[ Antrean Deteksi ]` `[ Riwayat Audit ]`.
   - Grid 4 Kartu Metrik Ringkas: Saldo Token Aktif, Total Naskah Diuji, Audit Selesai, dan Status Worker Celery.
   - Area Dropzone Unggah Naskah terintegrasi (.pdf, .docx, .txt maks 50 MB).
   - Tabel Riwayat Pengujian Naskah Terakhir.
2. `dashboard--tab-all-active`
   - Menampilkan seluruh komponen kerja secara terstruktur dari atas ke bawah.
3. `dashboard--tab-upload-active`
   - Fokus hanya menampilkan dropzone unggah dan opsi kedalaman audit.
4. `dashboard--tab-active-tasks-active`
   - Fokus menampilkan daftar kartu naskah yang saat ini sedang diproses di antrean Celery worker.
5. `dashboard--tab-history-active`
   - Fokus menampilkan tabel riwayat naskah lengkap beserta fitur pencarian dan paginasi.
6. `dashboard--dropzone-drag-over`
   - Pengguna menyeret berkas ke atas dropzone: border berubah menjadi biru tegas 2px (`border-blue-600 bg-blue-50/40`), icon panah membesar mikro.
7. `dashboard--dropzone-file-selected`
   - Berkas terpilih: Menampilkan nama file dokumen, ukuran (MB), badge ekstensi (`.PDF` / `.DOCX`), dan tombol hapus silang (X) untuk ganti berkas.
8. `dashboard--depth-selection-hybrid`
   - Toggle kedalaman aktif pada "Hybrid Penuh (Tier 1-4) • 2 Token" (deteksi leksikal + semantik pgvector + stilometri AI).
9. `dashboard--depth-selection-lexical`
   - Toggle kedalaman aktif pada "Leksikal Cepat (Tier 1) • 1 Token" (Rabin-Karp Winnowing saja).
10. `dashboard--token-insufficient-warning`
    - Saldo token tidak mencukupi untuk kedalaman yang dipilih: Tombol "Mulai Proses Audit" dinonaktifkan, muncul alert kuning *"Saldo token tidak cukup. Anda membutuhkan minimal 2 token untuk pengujian Hybrid."* dengan tombol "+ Top Up Kuota".
11. `dashboard--file-uploading-progress`
    - Bar progres persentase (0% s.d. 100%) saat berkas diunggah dari browser ke endpoint backend `/api/v1/documents/upload`.
12. `dashboard--worker-processing-stage-1`
    - Kartu tugas aktif: *"Tahap 1: Ekstraksi teks naskah dan normalisasi struktur kalimat..."*
13. `dashboard--worker-processing-stage-2`
    - Kartu tugas aktif: *"Tahap 2 (35%): Rabin-Karp Winnowing leksikal n-gram pada korpus..."*
14. `dashboard--worker-processing-stage-3`
    - Kartu tugas aktif: *"Tahap 3 (70%): Penelusuran kemiripan semantik pgvector HNSW & analisis stilometri LLM..."*
15. `dashboard--worker-task-completed-toast`
    - Notifikasi toast hijau muncul di sudut kanan atas: *"Audit naskah '[Judul]' selesai! Skor kemiripan: 18.4%."* dengan tombol "Buka Laporan →".
16. `dashboard--worker-task-failed`
    - Kartu antrean menampilkan status gagal: *"Pemrosesan gagal: Berkas PDF terenkripsi sandi atau tidak memiliki lapisan teks."*
17. `dashboard--task-cancel-dialog`
    - Dialog konfirmasi saat pengguna menekan tombol "Batalkan Tugas" pada antrean audit yang sedang berjalan.
18. `dashboard--empty-history`
    - Tampilan saat akun belum memiliki riwayat pengujian: Komponen EmptyState dengan ilustrasi dokumen akademik bersih dan tombol CTA "Unggah Naskah Pertama".
19. `dashboard--history-desktop-table`
    - Tampilan tabel tabular data-dense pada layar desktop: Kolom Judul Naskah, Waktu Audit, Kedalaman, Status Badge, Skor Kemiripan Gauge, dan Aksi "Lihat Detail".
20. `dashboard--history-mobile-card-list`
    - Tampilan adaptif pada smartphone (< 640px): Tabel otomatis beralih menjadi deretan kartu naskah vertikal yang mudah disentuh tanpa scroll horizontal.
21. `dashboard--syncing-status-spin`
    - Ikon putar berotasi saat tombol "Sinkronkan Status" ditekan untuk memeriksa kondisi terkini antrean worker Celery dan saldo token.

---

## 7. Detail Laporan Audit & Heatmap (Inspection Workbench)
**Rute:** `/audits/:id` | **Akses:** Pemilik Naskah, Reviewer, Super Admin

1. `audit-detail--loading-skeleton`
   - Efek shimmer skeleton loader berkedip halus pada panel teks naskah, indikator gauge skor, dan daftar sumber korpus.
2. `audit-detail--desktop-split-pane`
   - Layout workstation 2 kolom berdampingan di desktop: 
     - Kolom Kiri (60% lebar layar, sticky scroll): Penampil teks naskah asli lengkap dengan anotasi warna heatmap per kalimat.
     - Kolom Kanan (40% lebar layar, tabbed inspector): Panel kendali skor dan analisis mendalam.
3. `audit-detail--mobile-view-tab-text`
   - Layar smartphone: Tab aktif "Teks Naskah & Heatmap" (menampilkan dokumen full-screen).
4. `audit-detail--mobile-view-tab-analysis`
   - Layar smartphone: Tab aktif "Analisis & Ringkasan Skor" (menampilkan speedometer skor dan sumber referensi).
5. `audit-detail--tab-summary-active`
   - Panel kanan menampilkan:
     - Speedometer Gauge Komposit Keseluruhan (Aman / Waspada / Tinggi).
     - Breakdown 3 Kartu Skor: Tier 1 Leksikal (Bobot 50%), Tier 2 Semantik (Bobot 35%), Tier 3 Stilometri AI (Bobot 15%).
     - Kotak Editorial AI Synthesis: Catatan diagnostik akademik dan temuan kunci penjiplakan.
6. `audit-detail--tab-sources-active`
   - Panel kanan menampilkan tabel sumber referensi yang cocok dari Bank Korpus (Judul naskah pembanding, penulis, persentase kemiripan, jumlah kalimat yang match).
7. `audit-detail--tab-diff-active`
   - Panel kanan menampilkan visualisasi perbandingan teks berdampingan (*side-by-side diff*) antara kalimat naskah dengan kalimat dokumen korpus asli.
8. `audit-detail--sentence-popover-hover`
   - Tooltip cepat saat kursor diarahkan ke kalimat ber-highlight di heatmap viewer.
9. `audit-detail--sentence-modal-open`
   - Dialog modal pop-up terbuka saat kalimat diklik: menampilkan detail kalimat naskah, teks sumber korpus pembanding, skor tier, dan algoritma pendeteksi.
10. `audit-detail--filter-tier-highlights`
    - Filter toggle di atas naskah untuk menyalakan/mematikan highlight spesifik: `[✓ Leksikal]` `[✓ Semantik]` `[✓ Stilometri AI]`.
11. `audit-detail--exporting-pdf-spinner`
    - Tombol "Unduh Sertifikat PDF Resmi" menampilkan spinner loading saat server me-render dokumen PDF vektor ber-QR Code.
12. `audit-detail--export-pdf-success`
    - Berkas `Sertifikat-VeriText-[UUID].pdf` berhasil terunduh otomatis ke komputer pengguna.
13. `audit-detail--delete-dialog-open`
    - Dialog konfirmasi penghapusan permanen naskah: *"Apakah Anda yakin ingin menghapus naskah ini? Tindakan ini permanen dan sesuai hak penghapusan UU PDP No. 27/2022."*
14. `audit-detail--deleting-in-progress`
    - Spinner loading saat sistem menghapus berkas di storage disk, vektor embeddings di pgvector, dan record audit di PostgreSQL.
15. `audit-detail--error-not-found-404`
    - Layar galat informatif: *"Laporan audit dengan ID tersebut tidak ditemukan atau telah dihapus permanen sesuai masa retensi data."*

---

## 8. Bank Korpus Dokumen (Corpus Repository)
**Rute:** `/corpus` | **Akses:** Dosen / Reviewer & Super Administrator

1. `corpus--loading-skeleton`
   - Skeleton table loader saat mengambil data koleksi dokumen referensi ilmiah.
2. `corpus--empty-repository`
   - Tampilan saat bank korpus belum memiliki naskah: Ilustrasi perpustakaan digital kosong dan tombol CTA "+ Unggah Naskah Korpus".
3. `corpus--populated-desktop-table`
   - Tabel data-dense korpus di desktop: Kolom Judul Naskah, Kategori (Jurnal/Skripsi/Tesis/Buku), Penulis, Tanggal Terbit, Jumlah Vektor pgvector terindeks, dan Aksi.
4. `corpus--populated-mobile-card-list`
   - Tampilan kartu ringkas vertikal adaptif pada smartphone.
5. `corpus--search-filtering-active`
   - Pengguna mengetik kata kunci pencarian naskah korpus dengan debouncing 300ms.
6. `corpus--search-no-results`
   - Tampilan kosong: *"Tidak ditemukan dokumen korpus yang cocok dengan kriteria pencarian Anda."* dengan tombol "Reset Filter".
7. `corpus--upload-single-modal-open`
   - Dialog modal unggah naskah tunggal: Input Judul, Penulis, Lembaga, Tahun Terbit, Kategori, dan File Picker (.pdf/.docx/.txt).
8. `corpus--upload-zip-modal-open`
   - Dialog modal unggah massal (*batch zip upload*): Area dropzone berkas arsip `.zip` dengan batasan keamanan ekstraksi aman (anti-zip bomb).
9. `corpus--uploading-progress`
   - Bar progres pengunggahan dokumen korpus ke server.
10. `corpus--indexing-badge-active`
    - Baris dokumen menampilkan badge berkedip kuning *"Mengindeks Vektor..."* saat worker Celery sedang mengekstrak embeddings HNSW 384-dimensi.
11. `corpus--indexing-success-badge`
    - Badge berubah menjadi hijau *"Terindeks (384-dim)"* setelah vektor tersimpan di tabel `corpus_embeddings`.
12. `corpus--delete-confirm-modal-open`
    - Dialog konfirmasi sebelum menghapus dokumen referensi korpus dan seluruh indeks vektornya.
13. `corpus--reindex-triggering`
    - Tombol re-index ditekan: notifikasi toast *"Menjadwalkan re-indeksasi seluruh dokumen korpus di background worker."*

---

## 9. Dompet Token & Billing (Token Balance & Invoices)
**Rute:** `/billing` | **Akses:** Seluruh Pengguna Login

1. `billing--default-idle`
   - Kartu Status Saldo Kuota Token Aktif dan estimasi jumlah pengujian naskah yang dapat dilakukan.
   - 3 Pilihan Kartu Paket Token:
     - Paket Mahasiswa / Starter (5 Token - Rp25.000)
     - Paket Peneliti / Pro Academic (20 Token - Rp80.000)
     - Paket Institusi / Campus Bulk (100 Token - Rp350.000)
   - Tabel Riwayat Transaksi & Pembayaran Faktur.
2. `billing--topup-modal-open`
   - Dialog modal konfirmasi pembelian terbuka: menampilkan ringkasan paket terpilih, rincian PPN, total bayar, dan pilihan metode pembayaran (QRIS / Virtual Account Mandiri/BCA/BNI).
3. `billing--payment-qris-display`
   - Modal menampilkan kode QRIS dinamis beresolusi tinggi, batas waktu pembayaran (countdown 15 menit), dan tombol simulasi bayar (*sandbox*).
4. `billing--payment-va-display`
   - Modal menampilkan nomor rekening Virtual Account dengan tombol "Salin Nomor VA" dan petunjuk transfer ATM/M-Banking.
5. `billing--payment-polling-checking`
   - Indikator halus: *"Menunggu konfirmasi pembayaran dari gateway..."* (background polling per 3 detik).
6. `billing--payment-success-modal`
   - Banner hijau perayaan: *"Pembayaran Berhasil Dikonfirmasi! Saldo Anda telah bertambah [X] Token."* dengan tombol "Unduh Faktur PDF" dan "Kembali ke Workspace".
7. `billing--payment-expired`
   - Alert peringatan saat sesi pembayaran QRIS/VA melewati batas waktu 15 menit: *"Sesi pembayaran kedaluwarsa. Silakan buat pesanan baru."*
8. `billing--empty-history`
   - Tampilan saat pengguna belum pernah melakukan transaksi pembelian token: EmptyState *"Belum ada riwayat transaksi token."*
9. `billing--history-desktop-table`
   - Tabel riwayat transaksi di desktop: Nomor Faktur (`INV-2026-XXXX`), Tanggal, Paket, Nominal (Rupiah), Metode Bayar, Status Badge (Lunas / Menunggu / Batal), dan Tombol Unduh Faktur PDF Resmi.
10. `billing--history-mobile-card-list`
    - Tampilan kartu ringkas vertikal adaptif pada smartphone.
11. `billing--invoice-downloading-spinner`
    - Spinner loading saat server mengompilasi berkas PDF faktur pembayaran resmi.

---

## 10. Verifikasi Sertifikat QR (Public Certificate Validator)
**Rute:** `/verify/:uuid?` | **Akses:** Publik (Siapapun tanpa Login)

1. `verify--empty-input-idle`
   - Layar verifikasi publik bersih: Kotak input kode UUID Sertifikat (36 karakter) dan tombol "Verifikasi Keaslian Naskah".
   - Tombol alternatif "Pindai Kode QR dengan Kamera Smartphone".
2. `verify--camera-scanner-active`
   - Viewfinder pemindai kamera aktif di browser dengan garis laser pemindai hijau untuk memindai barcode QR fisik dari dokumen sertifikat cetak.
3. `verify--camera-permission-denied`
   - Alert informatif jika pengguna menolak izin kamera: *"Akses kamera tidak diizinkan. Silakan ketik 36 karakter kode sertifikat secara manual pada kolom di atas."*
4. `verify--verifying-loading`
   - Spinner loading dan indikator pengecekan kriptografis hash SHA-256 dokumen pada database VeriText.
5. `verify--valid-certificate`
   - Sertifikat TERVERIFIKASI ASLI:
     - Banner hijau resmi dengan stempel keabsahan digital.
     - Detail Lengkap: Judul Naskah Akademik, Nama Penulis / Mahasiswa, Nama Institusi Kampus, Tanggal & Jam Audit, Tingkat Kedalaman, Skor Kemiripan Komposit, dan Digital Signature Hash.
     - Tombol "Unduh Salinan Sertifikat Resmi (PDF)".
6. `verify--invalid-certificate`
   - Sertifikat TIDAK VALID / PALSU:
     - Banner merah tegas: *"Sertifikat Tidak Ditemukan atau Tidak Valid. Kode sertifikat tersebut tidak terdaftar dalam catatan audit resmi VeriText AI."*
7. `verify--tampered-document-warning`
   - Peringatan integritas: *"Peringatan: Tanda tangan digital sertifikat tidak cocok dengan data asli pada pangkalan data. Naskah kemungkinan telah dimanipulasi."*

---

## 11. Konsol Tata Kelola Admin (Executive Administration Portal)
**Rute:** `/admin` | **Akses:** Khusus Super Administrator

1. `admin--sidebar-expanded-desktop`
   - Persistent left sidebar navigasi Zendenta (Ink Black `#17191c`) terbuka penuh di layar desktop dengan navigasi: Ringkasan Sistem, Manajemen Pengguna, Bank Korpus, Konfigurasi Algoritma, Log Audit Keamanan, Kepatuhan UU PDP.
2. `admin--sidebar-collapsed-mobile`
   - Sidebar menciut menjadi icon bar bawah atau drawer samping geser (*slide-over drawer*) saat diakses melalui smartphone atau tablet.
3. `admin--tab-overview-telemetry`
   - Dashboard analitik server: Utilisasi CPU & RAM, status koneksi Celery Worker, total naskah akademik diproses, total token beredar, grafik pengujian harian.
4. `admin--tab-users-management`
   - Tabel manajemen seluruh pengguna terdaftar: Nama, Email Institusi, Role (TRIAL, PREMIUM, REVIEWER, ADMIN), Saldo Token, Status Akun (Aktif / Ditangguhkan), dan Tombol Tindakan.
5. `admin--user-edit-modal-open`
   - Dialog modal untuk mengubah role pengguna, menambah/mengurangi saldo token secara manual, atau mereset status lockout brute-force.
6. `admin--user-suspend-confirm-dialog`
   - Dialog konfirmasi penangguhan (*suspend*) akun pengguna yang melanggar ketentuan.
7. `admin--tab-config-algorithm`
   - Panel konfigurasi dinamis algoritma:
     - Slider Pembobotan: Tier 1 Leksikal (default 0.50), Tier 2 Semantik (default 0.35), Tier 3 Stilometri (default 0.15) — dengan validasi total tepat 1.00 (100%).
     - Parameter Rabin-Karp: k-gram size (default 5), window size (default 4).
     - Parameter pgvector HNSW: `ef_search` (default 40), `m` (default 16).
     - Masa Retensi Naskah: Slider hari (default 30 hari).
8. `admin--config-saving-indicator`
   - Spinner loading saat konfigurasi baru disimpan ke tabel `system_configs` dan disinkronkan ke seluruh Celery worker.
9. `admin--tab-audit-logs`
   - Tabel catatan forensik keamanan immutable: Waktu (UTC/WIB), Tipe Aksi (LOGIN, UPLOAD, AUDIT, CONFIG_CHANGE, EXPORT_PDF, DELETE), IP Address pengguna, User-Agent, dan Status Hasil.
10. `admin--logs-exporting-csv-spinner`
    - Spinner loading saat mengunduh log ke format CSV dengan sanitasi anti-formula injection OWASP.
11. `admin--tab-pdp-compliance`
    - Panel audit kepatuhan UU PDP No. 27/2022: Menampilkan daftar naskah yang telah melewati masa retensi 30 hari dan tombol eksekusi *"Jalankan Pembersihan Naskah Kadaluwarsa (Zombie Reaper)"*.
12. `admin--pdp-reaper-running`
    - Status background worker sedang memusnahkan berkas dokumen fisik dan embeddings dari server secara permanen.

---

## 12. Halaman Galat Sistem, Keamanan, & Jaringan (System Error Pages)

### A. HTTP 400 Bad Request
**Rute:** `/400`
1. `error-400--bad-request` (Ilustrasi dokumen rusak: *"Permintaan tidak dapat diproses karena data yang dikirimkan tidak valid atau korup."* Tombol kembali).

### B. HTTP 401 Unauthorized (Sesi Habis / Belum Login)
**Rute:** `/401`
1. `error-401--expired-session` (Banner merah notifikasi: *"Sesi Anda telah berakhir demi keamanan. Silakan masuk kembali."* dengan pengalihan otomatis ke `/login?redirect=...`).
2. `error-401--token-revoked` (Pemberitahuan bahwa token akses telah dicabut karena login di perangkat lain).

### C. HTTP 403 Forbidden (Hak Akses Ditolak)
**Rute:** `/403`
1. `error-403--student-access-admin` (Ilustrasi gembok keamanan: *"Halaman ini terbatas untuk Super Administrator. Akun Anda tidak memiliki wewenang untuk membuka konsol ini."* Tombol "Kembali ke Dashboard").
2. `error-403--student-access-corpus` (Pemberitahuan: *"Bank Korpus Dokumen hanya dapat diakses oleh Dosen / Tim Penilai Akademik."*).

### D. HTTP 404 Not Found (Halaman / Sumber Daya Tidak Ditemukan)
**Rute:** `/:pathMatch(.*)*`
1. `error-404--page-not-found` (Ilustrasi editorial minimalis: *"Halaman yang Anda tuju tidak ditemukan atau URL salah ketik."* Tombol "Kembali ke Beranda").
2. `error-404--audit-report-not-found` (Konteks audit: *"Laporan pengujian naskah dengan ID tersebut tidak ditemukan atau telah dihapus permanen sesuai masa retensi data."*).

### E. HTTP 408 Request Timeout
**Rute:** `/408`
1. `error-408--upload-timeout` (Pemberitahuan: *"Koneksi unggah berkas terputus karena batas waktu habis. Periksa kestabilan jaringan internet Anda."* Tombol "Coba Unggah Ulang").

### F. HTTP 413 Payload Too Large (Ukuran Berkas Melebihi Batas)
**Rute:** Modal / Toast State
1. `error-413--file-size-exceeded` (Alert merah: *"Ukuran berkas melebihi batas maksimum 50 MB. Mohon kompres dokumen naskah Anda sebelum mengunggah."*).

### G. HTTP 422 Unprocessable Entity (Validasi Naskah Gagal)
**Rute:** Modal / Toast State
1. `error-422--corrupted-pdf` (Peringatan: *"Berkas naskah tidak dapat diekstraksi teksnya (file kosong, terenkripsi, atau scan gambar murni tanpa OCR)."*).

### H. HTTP 429 Too Many Requests (Rate Limiting)
**Rute:** Modal / Toast State
1. `error-429--api-rate-limit` (Pemberitahuan: *"Terlalu banyak permintaan dalam waktu singkat. Sistem membatasi demi stabilitas layanan. Mohon tunggu 30 detik."*).

### I. HTTP 500 Internal Server Error
**Rute:** `/500`
1. `error-500--internal-server-error` (Ilustrasi server terganggu: *"Terjadi kendala teknis pada server pemrosesan internal. Tim kami telah menerima log peringatan ini."* Tombol "Muat Ulang Halaman").

### J. HTTP 502 / 503 Bad Gateway & Service Unavailable
**Rute:** `/503`
1. `error-503--worker-maintenance` (Pemberitahuan perawatan worker: *"Layanan antrean pengujian sedang dalam pemeliharaan berkala. Dokumen Anda tetap aman dan akan diproses segera."*).

### K. Offline Connectivity State (Jaringan Internet Terputus)
**Rute:** Global Toast / Offline Banner
1. `network--offline-banner` (Banner kuning di bagian atas layar: *"Koneksi internet terputus. Bekerja dalam mode offline."*).
2. `network--reconnected-toast` (Toast hijau mikro saat internet kembali tersambung: *"Koneksi internet kembali normal."*).
