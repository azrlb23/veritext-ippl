# Pemetaan Halaman & Seluruh State Antarmuka VeriText AI
**Acuan Arsitektur**: Mengadopsi standar taksonomi desain sistematis FMS (*Fuel Management System* - `design/STYLE.md` & `tokens`), diselaraskan dengan **`ui-ux-pro-max`** dan **`anti-ai-slop`**.

Dokumen ini memetakan secara komprehensif **seluruh 9 halaman** aplikasi VeriText AI beserta **semua variasi state** (Ideal/Default, Memuat/Loading, Kosong/Empty, Sedang Berjalan/Processing, Galat/Error, Dialog Modal, serta Perilaku Responsif Mobile vs Tablet vs Desktop).

---

## Ringkasan Matriks Halaman & Segmen Akses

| No | Rute Halaman | Nama Layar | Role Pengguna | Kategori Layout |
|:---|:---|:---|:---|:---|
| **01** | `/` | **Landing Page (Publik)** | Tamu, Mahasiswa, Dosen, Admin | Editorial Marketing & Interactive Demo |
| **02** | `/login` | **Masuk Portal Akun** | Tamu (Guest Only) | Centered Minimalist Form Card |
| **03** | `/register` | **Pendaftaran Akun Baru** | Tamu (Guest Only) | 2-Column Responsive Form Card |
| **04** | `/dashboard` | **Workspace Audit Naskah** | Mahasiswa (TRIAL, PREMIUM, USER) | Academic Workstation (High-Density) |
| **05** | `/audits/:id` | **Detail Laporan Audit & Heatmap**| Mahasiswa, Dosen, Admin | Split-Pane Inspection Workstation |
| **06** | `/corpus` | **Bank Korpus Dokumen** | Dosen / Reviewer & Super Admin | Data Table & Repository Explorer |
| **07** | `/billing` | **Dompet Token & Riwayat Faktur** | Seluruh Pengguna Login | Pricing Grid & Financial Ledger |
| **08** | `/verify/:uuid?` | **Verifikasi Sertifikat QR** | Publik / Tamu & Akademisi | Single-Purpose Public Validator |
| **09** | `/admin` | **Konsol Tata Kelola Admin** | Super Administrator Saja | Fixed Sidebar Executive Console |

---

## Rincian Lengkap State Per Halaman

```
Setiap halaman wajib menangani 6 kuadran state dasar:
[ DEFAULT / IDLE ] ─── [ MEMUAT / LOADING ] ─── [ KOSONG / EMPTY ]
        │                       │                       │
[ PROSES / ACTIVE ] ─── [ GALAT / ERROR ] ──── [ DIALOG MODAL / OVERLAY ]
```

---

### Halaman 01: Landing Page (`/` - `LandingView.vue`)
*Gerbang publik perkenalan platform VeriText AI.*

- **State 1: `landing--default` (Default / Hero Active)**
  - Navbar kapsul mengambang (sticky top).
  - Headline editorial serif, CTA "Coba Audit Sekarang", dan live interactive demo snippet.
  - Tampilan diagram 4-tier pipeline (Leksikal, Semantik, Stilometri, Agregator).
- **State 2: `landing--demo-evaluating` (Demo Sedang Menganalisis)**
  - Pengguna menempel teks di snippet demo.
  - Animasi progress bar mikro berjalan (150ms-300ms) tanpa blocking.
- **State 3: `landing--demo-result` (Hasil Demo Muncul)**
  - Teks terdeteksi disorot dengan highlight heatmap (kuning stilometri, oranye semantik, merah leksikal).
- **Perilaku Responsif**:
  - *Mobile (< 640px)*: Navbar menciut ke hamburger drawer; grid 4 tier bertumpuk vertikal 1 kolom; interactive demo teks menjadi full width.
  - *Tablet (768px)*: Grid 2 kolom; demo berdampingan dengan penjelasan fitur.
  - *Desktop (>= 1024px)*: Container `max-w-7xl`, grid 4 kolom sejajar.

---

### Halaman 02: Masuk Portal Akun (`/login` - `LoginView.vue`)
*Otentikasi kredensial pengguna.*

- **State 1: `login--default` (Formulir Siap)**
  - Input Email dan Input Kata Sandi dengan ikon mata tertutup (*eye-off*).
  - Tombol submit "Masuk Sekarang →" dalam keadaan aktif.
- **State 2: `login--show-password` (Sandi Terlihat)**
  - Input kata sandi berubah ke `type="text"`, ikon mata terbuka, tombol bertipe `type="button"`.
- **State 3: `login--loading` (Memverifikasi Kredensial)**
  - Tombol masuk berputar (*spinner*), input dinonaktifkan (`disabled:opacity-60`).
- **State 4: `login--error-invalid` (Galat Kredensial Salah)**
  - Alert merah muncul: *"Invalid email or password"*. Tombol silang (X) menutup alert.
- **State 5: `login--error-lockout` (Akun Terkunci Sementara)**
  - Alert merah peringatan brute-force: *"Akun terkunci karena terlalu banyak percobaan gagal. Silakan coba kembali dalam 15 menit."*
- **Perilaku Responsif**:
  - *Mobile*: Card mengisi 100% lebar layar dengan padding `px-4`.
  - *Desktop*: Card melayang elegan terpusat (`max-w-[420px]`).

---

### Halaman 03: Pendaftaran Akun Baru (`/register` - `RegisterView.vue`)
*Onboarding pengguna baru dengan kepatuhan UU PDP No. 27/2022.*

- **State 1: `register--default` (Formulir Siap)**
  - Nama Lengkap, Email Kampus, Nama Institusi, Kata Sandi, dan Konfirmasi Sandi.
  - Checkbox persetujuan pemrosesan data UU PDP tercentang default.
- **State 2: `register--password-mismatch` (Sandi Tidak Cocok)**
  - Validasi instan: alert merah *"Konfirmasi kata sandi tidak cocok"*.
- **State 3: `register--submitting` (Mendaftarkan Akun)**
  - Loading spinner pada tombol register.
- **State 4: `register--error-duplicate` (Email Sudah Terdaftar)**
  - Alert error dari backend: *"Email address already registered"*.
- **State 5: `register--success-redirect` (Pendaftaran Berhasil)**
  - Notifikasi sukses "Pendaftaran akun berhasil! Mengalihkan ke login...".
- **Perilaku Responsif**:
  - *Mobile*: Form Kata Sandi & Konfirmasi Sandi bertumpuk vertikal 1 kolom (`grid-cols-1`).
  - *Tablet & Desktop*: Form sandi bersebelahan 2 kolom (`grid-cols-2`).

---

### Halaman 04: Workspace Audit Naskah (`/dashboard` - `DashboardView.vue`)
*Pusat kerja mahasiswa untuk mengunggah naskah dan memantau status audit.*

- **State 1: `dashboard--default` (Workspace Siap / Kanvas Utama)**
  - **Header Bar Ringkas**: Nama pengguna, pill instansi, dan kuota token aktif (tanpa mockup bingkai macOS).
  - **Segmented Control Tabs**: `[ Semua ]` `[ Unggah Naskah ]` `[ Antrean Aktif ]` `[ Riwayat Audit ]`.
  - **4 Metrik Card**: Saldo Token, Total Naskah, Audit Selesai, dan Antrean Celery.
  - **Dropzone Area**: Kotak seret naskah responsif (.pdf, .docx, .txt).
- **State 2: `dashboard--dragging-file` (Pengguna Menyeret Berkas)**
  - Dropzone berubah warna (border biru/hitam tegas, ring aksen cerah, background highlight halus).
- **State 3: `dashboard--uploading` (Mengunggah Dokumen ke Backend)**
  - Progress bar upload berkas, tombol audit terkunci.
- **State 4: `dashboard--insufficient-token` (Kuota Token Habis)**
  - Tombol "Mulai Proses Audit" dinonaktifkan, muncul alert instruksi "Saldo token tidak mencukupi untuk kedalaman ini. Silakan Top Up".
- **State 5: `dashboard--active-processing` (Audit Sedang Berjalan di Worker Celery)**
  - Kartu Antrean Deteksi aktif menampilkan progress bar animasi (Tier 1 -> Tier 2 -> Tier 3).
  - Tombol batal (*Cancel Audit*) tersedia.
- **State 6: `dashboard--empty-history` (Belum Ada Riwayat)**
  - Komponen EmptyState rapi dengan ikon dokumen dan tombol panduan unggah pertama.
- **State 7: `dashboard--history-populated` (Daftar Riwayat Terisi)**
  - Tabel riwayat dokumen dengan skor persentase, tanggal, status, dan tombol aksi detail.
- **Perilaku Responsif**:
  - *Mobile (< 640px)*: Segmented tabs bergulir horizontal; Metrik kartu menjadi 2 kolom (`grid-cols-2`); Tabel riwayat berubah menjadi tampilan kartu kompak vertikal (*card list*).
  - *Tablet (768px)*: Metrik 4 kolom kompak; dropzone ergonomis.
  - *Desktop (>= 1024px)*: Full width data-dense view.

---

### Halaman 05: Detail Laporan Audit & Heatmap (`/audits/:id` - `AuditDetailView.vue`)
*Layar workbench perbandingan dokumen mendalam.*

- **State 1: `audit-detail--loading` (Memuat Hasil Pemeriksaan)**
  - Skeleton loading pada panel heatmap teks dan panel skor metrik.
- **State 2: `audit-detail--analyzed` (Hasil Tersaji Penuh)**
  - **Sisi Kiri**: Heatmap Viewer (teks dokumen asli dengan sorotan warna per kalimat).
  - **Sisi Kanan (Tabbed Inspection)**:
    - Tab 1: Ringkasan Skor (Gauge Kemiripan, Skor Leksikal, Semantik, Stilometri).
    - Tab 2: Matched Sources Table (daftar naskah pembanding di korpus).
    - Tab 3: Side-by-Side Diff (perbandingan kalimat naskah vs sumber korpus).
- **State 3: `audit-detail--sentence-selected` (Modal / Popover Kalimat)**
  - Pengguna mengklik kalimat yang tersorot pada heatmap.
  - Dialog modal `SentenceDetailModal` terbuka: menampilkan rincian persentase plagiarisme, sumber dokumen persis, dan tier deteksi.
- **State 4: `audit-detail--exporting-pdf` (Mengunduh Sertifikat / Invoice)**
  - Tombol "Unduh Sertifikat PDF" menampilkan spinner unduhan.
- **State 5: `audit-detail--not-found` (Tugas Tidak Ditemukan)**
  - EmptyState galat 404: "Laporan audit tidak ditemukan atau telah dihapus sesuai masa retensi".
- **Perilaku Responsif**:
  - *Mobile*: Tampilan split-screen kiri-kanan otomatis berubah menjadi **Tab Beralih**: `[ Naskah & Heatmap ]` vs `[ Analisis & Skor ]`.
  - *Desktop*: 2 Kolom proporsional berdampingan (*sticky left text, scrollable right inspection*).

---

### Halaman 06: Bank Korpus Dokumen (`/corpus` - `CorpusView.vue`)
*Repositori dokumen referensi pembanding bagi Dosen/Reviewer & Admin.*

- **State 1: `corpus--loading` (Memuat Data Korpus)**
  - Skeleton table loader.
- **State 2: `corpus--populated` (Data Korpus Tersedia)**
  - Bar statistik (Total Dokumen Korpus, Total Vektor pgvector terindeks, Kapasitas Penyimpanan).
  - Filter pencarian & kategori naskah.
  - Tabel korpus dengan tombol "Hapus dari Korpus" dan "Unduh Berkas".
- **State 3: `corpus--upload-modal` (Modal Unggah Naskah Korpus Terbuka)**
  - Dialog pop-up formulir pengunggahan batch dokumen referensi ilmiah.
- **State 4: `corpus--indexing` (Proses Ekstraksi Vektor HNSW)**
  - Baris dokumen baru menampilkan badge kuning "Mengindeks Vektor...".
- **State 5: `corpus--empty` (Korpus Kosong)**
  - Tampilan zero-data dengan prompt CTA "Unggah Naskah Referensi Pertama".
- **Perilaku Responsif**:
  - *Mobile*: Filter bar menjadi vertikal; aksi hapus/unduh masuk ke dalam overflow menu titik tiga (...).
  - *Desktop*: Tabel tabular data-dense.

---

### Halaman 07: Dompet Token & Riwayat Transaksi (`/billing` - `BillingView.vue`)
*Pengelolaan kuota pay-as-you-go dan riwayat faktur resmi.*

- **State 1: `billing--default` (Pilihan Paket Kuota)**
  - Kartu Saldo Saat Ini (dengan badge tier akun).
  - 3 Pilihan Paket Kuota: Starter (5 Token), Pro Academic (20 Token), Campus Institutional (100 Token).
  - Tabel Riwayat Transaksi & Unduh Faktur PDF.
- **State 2: `billing--topup-modal` (Modal Pembayaran Terbuka)**
  - Pilihan metode transfer / simulasi QRIS & Virtual Account.
- **State 3: `billing--processing-payment` (Memproses Pembayaran)**
  - State polling verifikasi webhook pembayaran.
- **State 4: `billing--empty-history` (Belum Ada Transaksi)**
  - Tabel riwayat menampilkan status "Belum ada transaksi top up".
- **Perilaku Responsif**:
  - *Mobile*: 3 Paket harga tersusun 1 kolom vertikal (`grid-cols-1`).
  - *Tablet & Desktop*: 3 Paket harga tersusun rapi berdampingan (`grid-cols-3`).

---

### Halaman 08: Verifikasi Sertifikat QR (`/verify/:uuid?` - `VerifyView.vue`)
*Pemeriksa keabsahan sertifikat publik anti-pemalsuan.*

- **State 1: `verify--empty-input` (Menunggu Kode / UUID)**
  - Form pencarian kode sertifikat / QR scanner kamera.
- **State 2: `verify--scanning-camera` (Kamera QR Aktif)**
  - Viewfinder kamera aktif memindai QR code.
- **State 3: `verify--verifying` (Mengecek Hash Sertifikat di Database)**
  - Loading spinner validasi kriptografi.
- **State 4: `verify--valid` (Sertifikat Terverifikasi Asli)**
  - Banner hijau: "Sertifikat Resmi & Sah".
  - Detail: Judul Dokumen, Penulis, Lembaga, Skor Kemiripan, Waktu Audit, dan Digital Signature Hash.
- **State 5: `verify--invalid` (Sertifikat Tidak Ditemukan / Palsu)**
  - Banner merah peringatan: "Sertifikat Tidak Valid atau Tidak Terdaftar pada Sistem VeriText AI".
- **Perilaku Responsif**:
  - *Mobile & Desktop*: Tampilan terpusat (*centered container*) dengan padding responsif.

---

### Halaman 09: Konsol Tata Kelola Admin (`/admin` - `AdminView.vue`)
*Panel eksekutif super administrator dengan Persistent Sidebar.*

- **State 1: `admin--overview` (Dashboard Statistik Sistem)**
  - Metrik: Total Pengguna Terdaftar, Naskah Diaudit, Antrean Worker, Token Beredar.
- **State 2: `admin--users` (Manajemen Pengguna & Role)**
  - Tabel pengguna dengan aksi ganti role (TRIAL, PREMIUM, REVIEWER, ADMIN) dan toggle blokir/aktifkan akun.
- **State 3: `admin--settings` (Pengaturan Bobot Algoritma & Retensi)**
  - Form konfigurasi bobot: Leksikal (T1), Semantik (T2), Stilometri (T3), HNSW parameters, dan Masa Retensi Dokumen (hari).
  - Tombol "Simpan Perubahan Sistem".
- **State 4: `admin--audit-logs` (Log Audit Keamanan)**
  - Tabel immutable audit log mencatat setiap login, reset sandi, pergantian konfigurasi, dan penghapusan berkas.
- **Perilaku Responsif**:
  - *Mobile*: Sidebar admin menciut menjadi icon dock bawah atau slide-over drawer; tabel pengguna mendukung scroll horizontal halus.
  - *Desktop*: Fixed left sidebar navigasi gelap/gelas dengan area kerja eksekutif luas.

---

## Aturan Desain State Global (Anti-AI Slop & Emil Kowalski Principles)

1. **Durasi Mikro-Interaksi**:
   - Seluruh transisi state hover, active, dan tab change dibatasi **150ms - 200ms `ease-out`**.
   - Dilarang keras menggunakan `transition: all`. Selalu gunakan `transition-colors`, `transition-transform`, atau `transition-opacity`.
2. **Ketiadaan Bayangan Mengambang Raksasa**:
   - Seluruh card menggunakan border tegas **1px (`border-[#ededed]` atau `border-gray-200`)** dengan bayangan mikro `shadow-xs` atau `shadow-sm`.
3. **Standar Touch Target**:
   - Di tampilan mobile, setiap elemen interaktif (tombol, tab, toggle mata, checkbox) memiliki area sentuh minimum **44 x 44 piksel**.
4. **Indikator Aksesibilitas**:
   - Setiap state fokus wajib memiliki ring yang terlihat jelas (`focus-visible:ring-2 focus-visible:ring-gray-900 focus-visible:outline-none`).
