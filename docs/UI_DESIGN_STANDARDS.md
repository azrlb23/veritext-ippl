# Standar Desain UI Otoritatif — VeriText AI

Dokumen ini menjadi kiblat dan acuan tunggal antarmuka VeriText AI berdasarkan implementasi final **Landing Page, Auth, Navbar, Footer, dan Verifikasi QR**. Seluruh pembaruan halaman dalam (Akun, Ringkasan, Periksa, Riwayat, Token, Asisten, dan Admin) wajib merujuk pada aturan di sini.

---

## 1. Palet Warna Resmi (Tanpa Ungu Generik)

- **Aksen Utama (Deep Teal)**:
  - Utama: `#0F766E` | Tengah/Hover: `#0D9488`, `#14B8A6`
  - Permukaan Tint Lembut: `#EBF8F6`, `#E6F7F5`
  - Border Kartu Aktif / Halus: `#D5ECE8`, `#CBE6E1`
- **Aksen Sekunder Hangat (Amber / Peach)**:
  - `#D97706`, `#F59E0B`, `#FDBA74` (dipakai pada gradasi `.vt-accent` hero, sapuan blob hangat di `LandingBackdrop`, dan aksen grafik).
- **Kanvas, Teks & Netral**:
  - Kanvas: `#FFFFFF` | Teks Utama (Ink): `#14111C` | Sekunder: `#4B4757` | Muted: `#5E5A6B`
  - Border Netral: `#E8ECEB`, `#ECECEF`
- **Warna Semantik Diagnostik (Khusus Highlight Naskah & Bar Metrik)**:
  - Leksikal: `#EF4444` (`#FEE2E2`) | Semantik: `#F97316` / `#FDBA74` | Stilometri AI: `#F59E0B` / `#EAB308` | Diperbaiki: `#10B981`
- **Larangan Keras Warna**:
  - Dilarang memakai palet ungu lama (`#8A3FE0`, `#7A2FD6`, `#6D28D9`, `#F3EEFA`, `#EDE3FA`) di halaman atau komponen mana pun.
  - Dilarang memakai warna krem/beige kusam (`#FAF3E8`) untuk kartu metrik/UI aktif; kombinasikan putih bersih (`#FFFFFF`), Soft Mint (`#EBF8F6`), dan Deep Teal (`#0F766E`).

---

## 2. Tipografi, Heading & Pengurangan Teks Berlebih

- **Font Tunggal**: `'Plus Jakarta Sans'`, `letter-spacing: -0.025em` (heading `-0.03em` s/d `-0.045em`).
- **Pembatasan `.vt-accent` (Gradasi Italic `#0F766E -> #0D9488 -> #D97706`)**:
  - `.vt-accent` **HANYA** digunakan pada `<h1>` Hero Landing Page.
  - Seluruh judul section lain (`<h2>`, `<h3>`), judul halaman dalam, dan nomor langkah wajib memakai teks solid hitam (`#14111C`) atau Deep Teal (`#0F766E`) tanpa italic.
- **Tanpa Eyebrow & Subjudul Redundan**:
  - Jangan pasang eyebrow label di atas judul (`"Ringkasan"`, `"Periksa naskah"`, `"Selamat datang kembali"`, `"Mulai gratis"`, `"CARA KERJA"`).
  - Chip/badge melayang hanya boleh memuat **1 baris teks** (tanpa subteks kedua di bawahnya).

---

## 3. Sistem Tombol Taktil 3D Bevel

- **Kelas Global (`frontend/src/assets/main.css`)**:
  - `.vt-btn-dark`: `rounded-full`, gradient gelap vertikal `#2A2633 -> #110E18`, highlight atas `inset 0 1px 0 rgba(255,255,255,0.22)`, shadow `0 6px 16px -3px rgba(17,14,24,0.42)`, `hover:brightness-110`, `active:scale-[0.98]`. Gunakan untuk seluruh aksi utama (dan `disabled:bg-none` bila ada state nonaktif berwarna solid).
  - `.vt-btn-light`: `rounded-full`, latar `#FFFFFF`, border `1px solid #ECECEF`, highlight dalam & shadow halus. Gunakan untuk seluruh tombol sekunder putih.
- **Tombol Ikon-Saja (`Icon-Only`)**:
  - Tombol navigasi balik (`Kembali ke beranda` di `AuthCard`, kembali di `ScoreHeader`) wajib berupa tombol bulat ikon-saja (`h-9 w-9` atau `h-11 w-11 rounded-full`, tanpa teks, lengkap dengan `aria-label` dan `title`).
  - Tombol aksi form Auth (`GoogleAuthButton`, `AuthSubmitButton`) mendukung mode `icon-only` bulat `52x52px` berdampingan.

---

## 4. Simplifikasi Kartu, Form & Input

- **Anti-Box & Anti-Outline**:
  - Dilarang membungkus `VtIcon` atau label angka/status dengan kotak/pill background maupun outline di dalam kartu (`bg-[#F5F2FA] rounded-lg`, pill di sekitar `"15% skor"`, `"Sorot kalimat"`, `"Klik gaya"`). Render `VtIcon tone="current" text-[#0F766E]` dan teks langsung di atas kartu.
  - Gunakan tag `<button>`/`<label>`/`<a>` bersih tanpa kartu di dalam kartu (contoh: tagline di bawah `VeriText AI` ditulis langsung di latar tanpa card).
- **Kepadatan Form & Grid**:
  - Form dengan >= 3 kolom input (seperti Register atau pengaturan Akun) wajib memanfaatkan grid 2 kolom (`grid-cols-1 sm:grid-cols-2`) untuk field pendek agar form tidak memanjang vertikal.
  - Seksi informasi/penjelasan (seperti `VerifyHowItWorks`) disajikan sebagai kolom bersih dengan garis pembatas tipis (`border-t border-[#E6ECEB]`) dan catatan 1 baris, bukan deretan kartu kotak.
- **Input Field (`AuthField`)**: Garis bawah aktif/fokus `3px` berwarna Deep Teal (`bg-[#0F766E]`) dengan label fokus `text-[#0F766E]`.

---

## 5. Interaksi, Navbar & Standar Performa

- **Hover-First & Transisi Tanpa Reflow**:
  - Kartu ekspansi (Section 3 `PipelineTierCard`) dan accordion (FAQ `FaqSection`) terbuka saat `@mouseenter` selain `@click`.
  - Gunakan `grid-rows-[0fr] -> grid-rows-[1fr]` (accordion) atau kontainer bertinggi tetap dengan `contain: layout style` agar ekspansi tidak menggeser tata letak di bawahnya.
- **Navbar Adaptif**: Transparan saat di posisi paling atas (`bg-transparent`), lalu berubah menjadi kapsul melayang `rounded-full bg-white/70 backdrop-blur-md border-white/60` saat di-scroll; tautan nav berupa teks inline polos tanpa slider pill, dan aksi tamu memakai kapsul `.vt-btn-dark`.
- **Aturan Performa Backdrop**:
  - Jangan pasang `backdrop-filter` pada ratusan elemen dekoratif (`.vt-tile`, `.vt-glass-pill`), jangan gunakan `filter: blur(140px)` pada blob besar, dan jangan gunakan SVG `feTurbulence` full-page. Gunakan `radial-gradient(closest-side, ...)` murni, `contain: layout style paint`, dan radial fade mask `<= 70%` agar ubin kaca tidak terpotong di tepi kontainer.

---

## 6. Rujukan Implementasi Saat Mengubah Halaman Akun & Lainnya

1. **Halaman Akun (`AkunView.vue`, `ProfileCard.vue`, `PasswordCard.vue`, `DeleteAccountCard.vue`)**:
   - Gunakan warna Deep Teal `#0F766E` untuk seluruh aksen/fokus/tautan (hilangkan sisa ungu).
   - Hilangkan eyebrow redundan dan bungkus form panjang ke grid 2 kolom (`sm:grid-cols-2`) bila memungkinkan.
   - Seluruh tombol aksi utama memakai `.vt-btn-dark`, tombol sekunder `.vt-btn-light`, dan ikon tanpa kotak pembungkus.
2. **Halaman Dalam Lainnya (`RingkasanView`, `PeriksaView`, `RiwayatView`, `TokenView`, `AsistenView`, `AdminOverviewView`)**:
   - Terapkan palet Deep Teal + putih bersih + warna semantik diagnostik saja, heading hitam polos non-italic, serta kartu berborder `#E8ECEB` / `#D5ECE8` tanpa outline/pill dekoratif.
