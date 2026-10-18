# Anti-Patterns Checklist (Unslop & Taste Audit)

Gunakan checklist ini saat mereview komponen `.vue` untuk mendeteksi tanda-tanda AI Slop:

## 1. Warna & Latar Belakang
- [ ] **Tidak ada gradien ungu-neon (`from-purple-600 to-pink-500`)** di header, kartu, atau teks hero.
- [ ] **Tidak ada "glassmorphism" berlebihan** (`backdrop-blur-xl bg-white/10`) yang membuat teks sulit terbaca.
- [ ] Latar belakang konsisten menggunakan palet netral yang tenang (`bg-white`, `bg-slate-50`, `bg-slate-100`).
- [ ] Rasio kontras teks terhadap latar belakang minimal 4.5:1 (WCAG AA). Hindari `text-slate-400` untuk teks body.

## 2. Struktur Kartu & Elevasi
- [ ] Kartu menggunakan pembatas tegas `border border-slate-200` alih-alih hanya mengandalkan bayangan.
- [ ] Tidak menggunakan `shadow-2xl` atau `shadow-xl` pada kartu statis biasa. Gunakan `shadow-sm` atau border tanpa bayangan.
- [ ] Radius sudut proporsional: maksimal `rounded-xl` untuk kartu, `rounded-lg` untuk tombol, bukan `rounded-3xl` seperti gelembung mainan.

## 3. Kerapatan Data (Data Density)
- [ ] Padding dan margin proporsional (dashboard analitik bukan poster promosi).
- [ ] Tabel memiliki baris yang rapat dan terbaca (`py-2.5` atau `py-3`).
- [ ] Angka statistik, metrik skor, dan timestamp menggunakan `tabular-nums` atau `font-mono`.

## 4. Hirarki Tipografi
- [ ] Maksimal 3 ukuran font dalam satu modul/kartu untuk menjaga ketenangan visual.
- [ ] Judul seksi tegas (`text-slate-900 font-semibold tracking-tight`), bukan teks abu-abu pudar.
- [ ] Label kecil menggunakan `text-xs font-medium text-slate-500 uppercase tracking-wider`.
