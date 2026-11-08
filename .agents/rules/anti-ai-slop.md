# Rules: Anti-AI Slop & Frontend Polish Standard
> Location: `.agents/rules/anti-ai-slop.md`
> Scope: `frontend/` (Vue 3, Tailwind CSS, TypeScript)
> Reference Skill: `skills/anti-ai-slop/SKILL.md`
> Style Reference: `frontend/design-reference/audyr/style-reference.md`

Semua agen pengembang WAJIB mematuhi aturan berikut saat membuat, memodifikasi, atau menata antarmuka komponen Vue:

## 1. Larangan Mutlak (Zero Tolerance for AI Slop):
1. **DILARANG menggunakan `transition: all`**: Selalu spesifikasikan properti yang ditransisikan (`transition-colors`, `transition-transform`, `transition-opacity`).
2. **DILARANG menggunakan gradien neon generic**: Jangan gunakan `from-purple-500 to-indigo-600` atau gradien heboh pada header/kartu. Latar belakang wajib utilitarian dan bersih (`bg-white` / `bg-slate-50`).
3. **DILARANG menggunakan `shadow-2xl` atau `rounded-3xl` berlebihan**: Kartu dipisah dari latar oleh bayangan lembut (`shadow-sm`) tanpa bingkai (keputusan 2026-11-03: aturan FMS menggantikan "border 1px crisp"). Garis 1px hanya sebagai pemisah di dalam daftar/tabel dan sebagai cincin fokus atau error pada isian.
4. **DILARANG menggunakan durasi animasi lambat**: Durasi interaksi tombol/menu maksimal `150ms - 200ms`. Jangan gunakan `duration-500` ke atas untuk interaksi klik.
5. **DILARANG menghilangkan outline fokus**: Elemen interaktif harus memiliki `focus-visible:ring-2 focus-visible:ring-blue-500`.

6. **DILARANG kapsul/badge status di setiap baris**: Status normal (mis. "Selesai") = teks abu-abu. Badge pil hanya untuk pengecualian (Diproses, Gagal), maksimal 2 per layar, dan label yang sama tidak boleh berulang.
7. **DILARANG kotak/lingkaran berwarna berisi ikon di setiap baris** tabel atau daftar (mis. thumbnail dokumen biru per baris). Baris tanpa ikon bertile.
8. **DILARANG pil persentase berwarna pada tile statistik** (mis. pil "75%" hijau, "25%" oranye): angka ditulis teks `ink`, pendampingnya teks abu ("75% dari 12 audit").
9. **DILARANG terlalu banyak warna**: Satu warna primer + maksimal 3 warna status (hijau/oranye/merah) per layar.
   - **Diperbolehkan (gaya Boltshift, disetujui 2026-11-03):** header/menu pil, kartu metrik pertama bergradasi biru, satu lingkaran ikon dan pil delta kecil per kartu metrik, grafik batang dengan sorotan berarsir, gauge bersegmen, tombol Filter bergradasi. Hanya di ringkasan atas, bukan di baris tabel.
   - Gradien neon generik (butir 1.2) tetap dilarang. Palet resmi: Aurora Biru (2026-11-03): latar gradasi lembut + orb blur (maks 3 per 1.400 px), kartu kaca (putih 78% tanpa garis tepi), gradasi hanya primary ke primaryLight dengan kontras teks putih >=4,5:1.
   - Dilarang monogram/lingkaran inisial pada ubin atau daftar (mis. lingkaran "UU", "SK").
   - Alert/banner = teks polos tanpa kotak berwarna (hanya merah untuk galat, biru-tinta untuk info/sukses). Indikator fokus/error isian = garis bawah tebal, bukan outline. Tombol utama gelap (ink), bukan biru generik.
   - Heading landing dua baris (baris 1 ink, baris 2 primary, semibold), subjudul kecil dan sempit (maks ~58 karakter/baris); dilarang memaksa lebar teks (textLength) karena membuat spasi antar kata melebar.
   - Merek hanya teks "VeriText AI.": dilarang bulatan biru, kotak, atau ikon logo di header/footer/sidebar mana pun.
10. **Rujukan lengkap dan pemeriksa otomatis**: `docs/design/STYLE.md` dan `docs/design/system/check_style.py` (R8–R10 mendeteksi pola di atas).

## 2. Standar Desain Analitik Akademik (Audyr Editorial Standard):
1. **Kerapatan Data Tinggi (High Density)**: VeriText AI adalah aplikasi audit naskah ilmiah. Pertahankan kerapatan informasi yang efisien (tabel kompak, padding proporsional `p-4` atau `p-5`).
2. **Angka Monospace / Tabular**: Skor plagiarisme, saldo token, dan angka statistik wajib menggunakan `tabular-nums` atau `font-mono`.
3. **Feedback Taktil**: Setiap tombol interaktif wajib memiliki state `:active` (misal: `active:scale-[0.98]`).
4. **Kontras Teks Terjaga**: Teks body minimal `text-slate-700` dan teks sekunder minimal `text-slate-500` di atas latar putih/terang.
5. **Acuan Token Desain**: Gunakan token warna & tipografi Audyr dari `frontend/design-reference/audyr/` (`--color-ink`, `--color-soft-mist`, `--font-inter`, hairline rules 1px #ededed, tracking -0.025em).
