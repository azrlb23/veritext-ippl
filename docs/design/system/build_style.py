"""Menulis ../STYLE.md. Tabel warna dan kontras dihitung dari tokens.json, jangan diketik manual."""
import os
from vt_kit import TOK, C, HERE
from check_style import ratio

rows_c = ''.join('| `%s` | `%s` |\n' % (k, v) for k, v in C.items())
rows_k = ''
for fg, bg, need, why in TOK['contrast']:
    r = ratio(C[fg], C[bg])
    rows_k += '| `%s` | `%s` | %s : 1 | %s : 1 | %s | %s |\n' % (fg, bg, ('%.2f' % r).replace('.', ','), ('%.1f' % need).replace('.', ','), 'lulus' if r >= need else 'GAGAL', why)

doc = """# VeriText AI Style Guide: laptop, mode terang

Versi %s. Aturan wajib kecuali ditulis "boleh". Acuan gaya: `anywhere-signup 1.svg` (pill lembut, isian berisi warna, aksen biru, font Outfit). Aturan anti-slop mengikuti FMS (disetujui 2026-11-03).

Tiga hal harus sinkron: nilai di `tokens.json`, komponen di `vt_kit.py` (satu-satunya tempat menggambar), aturan di dokumen ini dan `check_style.py`.

```bash
cd docs/design/system && python3 build_screens.py && python3 build_style.py && python3 check_style.py
```

## 1. Prinsip
1. Hirarki dari ukuran dan warna isi, bukan garis. Tidak ada outline kecuali cincin fokus, cincin error, dropzone, dan titik radio.
2. Satu aksi utama per layar. Maksimal satu tombol biru solid.
3. Warna aksen hanya untuk hal yang perlu perhatian. Kondisi normal = teks netral.
4. Hal terpenting di bagian atas halaman.
5. Satu istilah untuk satu hal (Indonesia; istilah teknis seperti Hybrid, Tier, token tetap).

## 2. Kanvas
Laptop %d px lebar. Sidebar %d px, margin isi %d px. Kartu radius %d, isian radius %d, tombol dan filter pil penuh.

## 3. Aturan anti-slop (dari FMS)
- Tanpa tile atau lingkaran berwarna di belakang ikon. Tanpa ikon hias.
- Tombol tanpa ikon depan kecuali bermakna. Radio tanpa ikon; terpilih = titik terisi + latar tint.
- Tombol netral dan isian hanya isi warna, tanpa garis. Bingkai hanya saat fokus (biru) atau error (merah).
- Badge pil hanya untuk pengecualian (Diproses, Gagal). Baris normal = teks abu-abu.
- Kartu dipisah dari latar oleh bayangan tipis, tanpa bingkai. Tanpa kartu di dalam kartu.
- Ringkasan angka = satu panel berkolom dengan garis rambut, bukan deretan kartu berikon.
- Tanpa sub-header generik, tanpa grafik mini hiasan, tanpa menu titik tiga yang tidak berfungsi.
- Data contoh harus konsisten satu sama lain (angka ringkasan cocok dengan isi daftar).
- Garis rambut hanya sebagai pemisah di dalam daftar dan tabel.

### Dilarang: terlalu banyak warna (tiga pola dari tinjauan 2026-11-03)
1. **Kapsul status di setiap baris tabel** ("Selesai" hijau berulang tiap baris). Status normal ditulis teks abu-abu. Badge hanya untuk pengecualian (Diproses, Gagal), maksimal %d per layar, dan label yang sama tidak boleh berulang.
2. **Kotak atau lingkaran berwarna berisi ikon di setiap baris** (thumbnail dokumen biru per baris tabel). Baris tabel tanpa ikon bertile.
3. **Pil persentase berwarna pada tile statistik** (pil "75%%" hijau, pil "25%%" oranye). Angka ditulis teks ink dan pendampingnya teks abu ("75%% dari 12 audit").

Anggaran warna per layar: biru primer ditambah **maksimal %d warna status** (hijau, oranye, merah).

### Palet Aurora Biru (dipilih 2026-11-03)
- **Latar:** gradasi `bg` ke `bgMid` ke `bgEnd` dengan orb blur (`auroraBlue`, `auroraCyan`, `auroraViolet`), maksimal 3 orb per 1.400 px tinggi. Warna orb hanya dekoratif, tidak boleh berada di bawah teks tanpa kartu.
- **Kaca:** permukaan berbayang (kartu, header, tooltip) berisi putih 78%% di atas latar gradasi. Tanpa garis tepi.
- **Gradasi:** hanya `primary` ke `primaryLight`, dua ujungnya kontras >=4,5:1 dengan teks putih (tombol utama, hero, tombol Filter). Tanpa gradasi lain di tombol sekunder, batang, atau baris tabel.
- **Dilarang:** monogram atau lingkaran inisial di ubin, ikon dekoratif, dan label pil.

### Alert, fokus, dan tombol (koreksi user 2026-11-03)
- **Alert = teks polos tanpa kotak.** Tanpa latar tint dan tanpa bingkai. Hanya dua warna: merah (galat dan peringatan) dan biru-tinta (info dan sukses). Baris pertama tebal.
- **Fokus dan error isian = garis bawah tebal 3 px** (biru atau merah), bukan cincin atau outline.
- **Tombol utama gelap** (`ink` ke `inkSoft`, teks putih, bayangan netral), bukan biru. Tombol Filter bergradasi biru di dashboard tetap.
- **Tipografi heading landing (referensi user, 2026-11-03):** heading rata tengah dua baris, baris pertama `ink` dan baris kedua `primary`, semibold (600), letter-spacing negatif. **Subjudul** kecil (15-16 px), `sub`, rata tengah, maksimal sekitar 58 karakter per baris, 2-3 baris, jarak baris sekitar 1,55.
- **Spasi antar kata harus alami:** dilarang memaksa lebar teks (`textLength`). Lebar teks dihitung dari tabel huruf Outfit asli (`assets/outfit-widths.json`, fungsi `mw()`), bukan perkiraan rata-rata.
- **Merek = teks saja.** "VeriText AI." (titik biru di akhir boleh), tanpa bulatan, kotak, atau ikon logo di header, footer, maupun sidebar.
- **Panel kanan layar autentikasi:** orb biru diburamkan dengan empat pita kaca vertikal, wordmark putih di tengah, tiga label kecil di dalam inti biru (referensi Crunchy). Tanpa foto atau ilustrasi lanskap.

### Diperbolehkan (gaya Boltshift, disetujui 2026-11-03)
Header pil dan menu pil, kartu metrik pertama berlatar biru bergradasi, satu lingkaran ikon per kartu metrik, pil delta kecil di kartu metrik, grafik batang dengan batang sorotan berarsir dan tooltip, gauge bersegmen, serta tombol Filter bergradasi biru. Ini hanya berlaku di bagian ringkasan atas, tidak di baris daftar atau tabel.

## 4. Pemeriksa otomatis
R1 warna hanya dari token. R2 font minimal %d px. R3 bingkai hanya untuk peran sah. R4 warna teks hanya dari daftar teks. R5 maksimal satu tombol primary. R6 tombol minimal 44 px. R7 kontras dihitung dari token. R8 badge maksimal %d per layar dan tanpa label kembar. R9 maksimal %d warna status per layar. R10 tanpa ikon bertile berulang per baris (tiga atau lebih sejajar vertikal).

## 5. Warna
| Token | Hex |
|---|---|
%s
Warna teks yang boleh: %s.

## 6. Kontras
| Teks atau ikon | Latar | Rasio | Syarat | Hasil | Dipakai untuk |
|---|---|---|---|---|---|
%s
## 7. Penyimpangan yang disengaja
- **Isian tanpa bingkai.** Mengikuti referensi: isian berisi warna `field` di atas kartu putih (rasio sekitar 1,07:1) dengan label kecil di dalam. Batas isian itu tidak mencapai 3:1, jadi kontrasnya lemah di bawah sinar terang. Cincin fokus 2 px (4,67:1) selalu muncul saat diisi. Kalau diputuskan perlu bingkai, ubah satu fungsi `field()`.
- **Biru tombol `#1A73D9`.** Biru referensi `#2D98F8` hanya sekitar 3,4:1 dengan teks putih, jadi digelapkan agar lolos 4,5:1.
- **Mode gelap tidak ada.**

## 8. Berkas
```
docs/design/
  STYLE.md            dokumen ini (dibuat build_style.py)
  system/             tokens.json, vt_kit.py, build_screens.py, build_style.py, check_style.py, assets/
  laptop/             layar SVG (dibuat build_screens.py)
```
""" % (TOK['version'], TOK['canvas']['width'], TOK['canvas']['sidebar'], TOK['canvas']['gutter'], TOK['radius']['card'], TOK['radius']['field'], TOK['budget']['badges'], TOK['budget']['accentHues'], TOK['font']['min'], TOK['budget']['badges'], TOK['budget']['accentHues'], rows_c, ', '.join('`%s`' % t for t in TOK['text']), rows_k)

with open(os.path.join(HERE, '..', 'STYLE.md'), 'w') as f:
    f.write(doc)
print('STYLE.md ditulis')
