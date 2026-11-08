# Gaya UI Violet Kaca

Gaya web VeriText AI sejak 2026-11-08. Berlaku untuk seluruh antarmuka web (frontend). Berkas `docs/design/STYLE.md` dan generator SVG di `docs/design/system/` adalah sistem lama (Aurora Biru) untuk mockup SVG dan tidak lagi menjadi acuan antarmuka web.

Titik rollback sebelum gaya ini: cabang `snapshot/2026-11-08-sebelum-violet-kaca`.

## Prinsip

1. **Bersih dan premium, bukan ramai.** Kartu bersudut besar, bayangan lembut, ruang kosong lega.
2. **Seamless.** Tidak ada kotak panggung berbatas keras. Warna latar menyebar di seluruh halaman dan seksi di atasnya tidak punya latar sendiri.
3. **Tipografi sebagai desain.** Angka besar, judul dua baris dengan baris kedua miring bergradasi.
4. **Nol dekorasi tanpa fungsi.** Dilarang: titik-titik (dot grid, bullet, titik di wordmark), efek pulse, garis tepi berwarna pada kartu dan teks, emoji, statistik atau testimoni karangan.
5. **Bahasa untuk pengguna awam.** Tidak ada nama algoritma, Celery/Redis, versi rilis, UU, akademik, kampus, institut.

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
- **Ubin kaca:** hanya di hero, memudar ke tepi kiri, kanan, dan bawah.
- **Navbar:** kapsul `bg-white/80 backdrop-blur-xl shadow-lift`, tombol Daftar tinta gelap. **Footer:** tanpa garis, wordmark raksasa memudar di dasar.

## Aksesibilitas

Elemen interaktif memakai `cursor-pointer` dan cincin fokus `focus-visible:ring-[#8A3FE0]`. Kartu ilustrasi diberi `aria-hidden="true"`. Transisi 150 sampai 300 ms. Berkas komponen maksimal 150 baris.

## Status penerapan

| Halaman | Status |
|---|---|
| Beranda, navbar, footer | selesai |
| Verifikasi QR | lihat riwayat commit |
| Dashboard, billing, admin, login, daftar, onboarding | belum (masih aurora biru lama) |
