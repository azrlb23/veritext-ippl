# Gaya UI Violet Kaca

Gaya web VeriText AI sejak 2026-11-08. Berlaku untuk seluruh antarmuka web (frontend). Berkas `docs/design/STYLE.md` dan generator SVG di `docs/design/system/` adalah sistem lama (Aurora Biru) untuk mockup SVG dan tidak lagi menjadi acuan antarmuka web.

Titik rollback sebelum gaya ini: cabang `snapshot/2026-11-08-sebelum-violet-kaca`.

## Prinsip

1. **Bersih dan premium, bukan ramai.** Kartu bersudut besar, bayangan lembut, ruang kosong lega.
2. **Seamless.** Tidak ada kotak panggung berbatas keras. Warna latar menyebar di seluruh halaman dan seksi di atasnya tidak punya latar sendiri.
3. **Tipografi sebagai desain.** Angka besar, judul dua baris dengan baris kedua miring bergradasi.
4. **Nol dekorasi tanpa fungsi.** Dilarang: titik-titik (dot grid, bullet, titik di wordmark), efek pulse, garis tepi berwarna pada kartu dan teks, emoji, statistik atau testimoni karangan.
5. **Bahasa untuk pengguna awam.** Tidak ada nama algoritma, Celery/Redis, versi rilis, UU, akademik, kampus, institut.

## Aturan wajib untuk setiap halaman

1. **Latar:** setiap halaman memakai `components/landing/LandingBackdrop.vue` (sapuan warna ditambah `GlassTileField` yang memudar). Varian `home` untuk beranda, varian `page` untuk halaman lain. Cukup tambahkan `backdrop: "home"` atau `backdrop: "page"` pada `meta` rute di `router/index.ts`. Dilarang kembali ke aurora biru atau blur gradasi polos.
2. **Responsif:** halaman wajib nyaman di desktop (1440), tablet (768), dan ponsel (390). Tidak boleh ada scroll horizontal. Target sentuh minimal 44 px. Ilustrasi miring 3D hanya di `lg` ke atas, medan ubin samping disembunyikan di bawah `md`, tombol aksi penuh lebar di ponsel. Cek ketiga lebar di browser sebelum dianggap selesai.
3. **Navbar:** satu komponen untuk semua ukuran. Desktop (`lg` ke atas) memakai bilah dengan indikator geser; tablet dan ponsel memakai tombol menu dengan lembar menu.

4. **Pemisahan dari latar:** setiap komponen harus terpisah jelas dari latar. Permukaan berdiri di atas kartu putih dengan `shadow-float` atau `shadow-lift`, bukan polos di atas latar. Elemen sekunder di dalam kartu putih (tombol Google, info) memakai tint `#F3EEFA`, bukan putih, supaya tidak menyatu.
5. **Isian formulir:** berupa garis, bukan kotak. Komponen `components/auth/AuthField.vue`: label kecil di atas, teks 16 px, garis bawah netral 2 px, dan garis violet 3 px yang menyapu dari kiri saat fokus atau terisi (merah bila tidak valid). Isian ditaruh di dalam kartu putih.

## Aturan warna 45 / 45 / 10

| Porsi | Peran | Warna |
|---|---|---|
| 45% | Putih dan abu netral | kartu `#FFFFFF`, dasar halaman `#F2F2F4` |
| 45% | Gradasi violet | lilac `#EBDDFA`, anggrek `#D9B8F2`, violet `#B478DF`, violet inti `#8A3FE0`; sorot magenta `#D26BE6` dan periwinkle `#8FA8F5` |
| 10% | Tinta untuk semua yang bisa ditekan | `#14111C`, hover `#2B2438` |

Teks: judul `#14111C`, isi `#4B4757`, keterangan `#5E5A6B`, teks violet kecil `#6D28D9`. Semua lolos kontras 4,5:1 di atas putih.

Merah `#EF4444`, oranye `#F97316`, kuning `#EAB308` hanya penanda hasil (kata, makna, pola AI). Latar penanda: `#FEE2E2`, `#FFEDD5`, `#FEF3C7`. Hijau hanya untuk status aman. Warna ini bukan bagian palet merek.

## Token

- Bayangan (`tailwind.config.js`): `shadow-float` (kartu utama), `shadow-lift` (kartu kecil, tombol sekunder), `shadow-btn-dark` (tombol tinta).
- Kelas (`src/assets/main.css`): `.vt-accent` (teks miring bergradasi violet), `.vt-lines` (garis vertikal tipis), `.vt-fade-x`, `.vt-tiles`, `.vt-tile` (ubin kaca).
- Latar halaman beranda: `components/landing/LandingBackdrop.vue` (sapuan violet, magenta, periwinkle yang diburamkan, posisi dalam persen tinggi halaman).
- Font: Plus Jakarta Sans. Judul `font-semibold` dengan `tracking-[-0.045em]`.

## Pola komponen

- **Kartu:** `rounded-[28px]` sampai `rounded-[36px]`, `bg-white`, `shadow-float` atau `shadow-lift`, tanpa border.
- **Tombol utama:** pil, `bg-[#14111C]`, `text-white`, `shadow-btn-dark`, tinggi 44 sampai 54 px, maksimal satu per tampilan. Tombol sekunder: pil putih dengan `shadow-lift`.
- **Judul seksi:** baris kecil abu, lalu judul besar dengan bagian akhirnya memakai `.vt-accent`.
- **Kartu melayang:** miring dengan `perspective(1200px) rotateY(+-24deg) rotateZ(+-5deg)`, hanya di layar `lg` ke atas.
- **Penanda hasil:** sorotan latar pada teks (bukan garis bawah), dengan nomor kecil bulat bertinta.
- **Ubin kaca:** bagian dari latar di seluruh halaman, bukan hanya hero. `GlassTileField.vue` membuat medan ubin yang memudar dengan mask, ditempatkan oleh `LandingBackdrop.vue` di tepi kiri, kanan, dan dasar halaman di atas sapuan warna. Varian `home` lebih rapat, varian `page` (misalnya verifikasi) lebih ringan, varian `auth` memenuhi sisi kanan halaman masuk dan daftar. Medan samping disembunyikan di bawah lebar `md`.
- **Alur bercerita:** halaman penjelasan memakai tiga ilustrasi bersambung (sertifikat, panah gradasi, ponsel). Di layar kecil alurnya turun ke bawah dengan panah vertikal.
- **Stempel hasil:** lencana bulat berwarna penuh (`VerifySeal.vue`) menumpang di pojok kartu hasil, bukan lencana kapsul.
- **Mobile-first untuk halaman yang dibuka dari QR:** tombol penuh lebar di ponsel, `navigator.share` bila tersedia, dan kondisi memeriksa dengan spinner.
- **Toast:** kartu putih `shadow-float` tanpa garis tepi; warna status hanya pada ikon.
- **Navbar:** dipecah menjadi `Navbar.vue` (cangkang, menyusut saat digulir), `navbar/NavLinks.vue` (bilah dengan indikator putih yang meluncur ke tautan aktif atau yang di-hover), `navbar/NavAuthActions.vue`, dan `navbar/NavMobileMenu.vue` (lembar menu untuk tablet dan ponsel, tutup dengan Escape atau ketuk di luar). Desktop mulai dari `lg`. Tombol Daftar tinta gelap, avatar gradasi violet untuk pengguna masuk. **Footer:** tanpa garis, wordmark raksasa memudar di dasar.

## Aksesibilitas

Elemen interaktif memakai `cursor-pointer` dan cincin fokus `focus-visible:ring-[#8A3FE0]`. Kartu ilustrasi diberi `aria-hidden="true"`. Transisi 150 sampai 300 ms. Berkas komponen maksimal 150 baris.

## Status penerapan

| Halaman | Status |
|---|---|
| Beranda, navbar, footer | selesai |
| Verifikasi QR (/verify) | selesai, latar seamless dengan LandingBackdrop versi dim |
| Login, daftar, lupa dan reset sandi, onboarding | selesai: layout form kiri dan panel kanan dipertahankan, latar `backdrop: "auth"` (ubin memenuhi sisi kanan dan memudar ke kiri); inner form Lupa/Reset/Onboarding baru dirapikan warnanya |
| Periksa naskah (`/periksa`) | selesai (tahap 1 pemisahan dashboard) |
| Riwayat (`/riwayat`), Akun (`/akun`), Asisten AI (`/asisten`) | selesai; navbar pengguna: Ringkasan, Periksa naskah, Riwayat, Asisten AI, Token; Akun dan Verifikasi QR ada di menu avatar |
| Token (`/billing`) | selesai: saldo besar, tiga paket, beli satuan, riwayat pembelian |
| Ringkasan (`/dashboard`) | selesai: saldo, tiga angka, pemeriksaan berjalan, tiga hasil terakhir |
| Ruang kerja audit (`/audits/:id`) | selesai: skor besar, naskah bersorot (latar, bukan garis bawah), panel Sumber / Tulis ulang / Tanya |
| Admin (`/admin`) | belum |
