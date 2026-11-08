# VeriText AI Style Guide: laptop, mode terang

Versi 0.1.0. Aturan wajib kecuali ditulis "boleh". Acuan gaya: `anywhere-signup 1.svg` (pill lembut, isian berisi warna, aksen biru, font Outfit). Aturan anti-slop mengikuti FMS (disetujui 2026-11-03).

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
Laptop 1440 px lebar. Sidebar 240 px, margin isi 32 px. Kartu radius 20, isian radius 14, tombol dan filter pil penuh.

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
1. **Kapsul status di setiap baris tabel** ("Selesai" hijau berulang tiap baris). Status normal ditulis teks abu-abu. Badge hanya untuk pengecualian (Diproses, Gagal), maksimal 2 per layar, dan label yang sama tidak boleh berulang.
2. **Kotak atau lingkaran berwarna berisi ikon di setiap baris** (thumbnail dokumen biru per baris tabel). Baris tabel tanpa ikon bertile.
3. **Pil persentase berwarna pada tile statistik** (pil "75%" hijau, pil "25%" oranye). Angka ditulis teks ink dan pendampingnya teks abu ("75% dari 12 audit").

Anggaran warna per layar: biru primer ditambah **maksimal 3 warna status** (hijau, oranye, merah).

### Palet Aurora Biru (dipilih 2026-11-03)
- **Latar:** gradasi `bg` ke `bgMid` ke `bgEnd` dengan orb blur (`auroraBlue`, `auroraCyan`, `auroraViolet`), maksimal 3 orb per 1.400 px tinggi. Warna orb hanya dekoratif, tidak boleh berada di bawah teks tanpa kartu.
- **Kaca:** permukaan berbayang (kartu, header, tooltip) berisi putih 78% di atas latar gradasi. Tanpa garis tepi.
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
R1 warna hanya dari token. R2 font minimal 12 px. R3 bingkai hanya untuk peran sah. R4 warna teks hanya dari daftar teks. R5 maksimal satu tombol primary. R6 tombol minimal 44 px. R7 kontras dihitung dari token. R8 badge maksimal 2 per layar dan tanpa label kembar. R9 maksimal 3 warna status per layar. R10 tanpa ikon bertile berulang per baris (tiga atau lebih sejajar vertikal).

## 5. Warna
| Token | Hex |
|---|---|
| `bg` | `#E8F0FF` |
| `bgMid` | `#DDF4FF` |
| `bgEnd` | `#EDE7FF` |
| `auroraBlue` | `#3B82F6` |
| `auroraCyan` | `#22D3EE` |
| `auroraViolet` | `#A78BFA` |
| `card` | `#FFFFFF` |
| `field` | `#F3F6FC` |
| `hair` | `#E4E8F0` |
| `track` | `#DCE3F0` |
| `disabled` | `#EDF0F6` |
| `ink` | `#0B0F19` |
| `sub` | `#5B6475` |
| `placeholder` | `#636B7A` |
| `primary` | `#1A73D9` |
| `primaryInk` | `#1560BD` |
| `primaryTint` | `#EAF3FE` |
| `primaryLight` | `#3B5BDB` |
| `inkSoft` | `#3A3A40` |
| `greenTint` | `#EAF7EE` |
| `onDark` | `#FFFFFF` |
| `green` | `#15803D` |
| `orange` | `#C2410C` |
| `red` | `#B91C1C` |
| `orangeTint` | `#FFF1E6` |
| `yellow` | `#A16207` |
| `yellowTint` | `#FEF7D6` |
| `redTint` | `#FEF3F2` |

Warna teks yang boleh: `ink`, `sub`, `placeholder`, `primaryInk`, `green`, `orange`, `red`, `yellow`, `onDark`.

## 6. Kontras
| Teks atau ikon | Latar | Rasio | Syarat | Hasil | Dipakai untuk |
|---|---|---|---|---|---|
| `ink` | `card` | 19,15 : 1 | 4,5 : 1 | lulus | Teks utama di kartu |
| `ink` | `bg` | 16,72 : 1 | 4,5 : 1 | lulus | Teks utama di latar |
| `ink` | `field` | 17,69 : 1 | 4,5 : 1 | lulus | Nilai di dalam isian |
| `sub` | `card` | 5,96 : 1 | 4,5 : 1 | lulus | Teks sekunder di kartu |
| `sub` | `bg` | 5,20 : 1 | 4,5 : 1 | lulus | Teks sekunder di latar |
| `sub` | `field` | 5,50 : 1 | 4,5 : 1 | lulus | Label di dalam isian |
| `sub` | `disabled` | 5,22 : 1 | 4,5 : 1 | lulus | Tombol nonaktif |
| `placeholder` | `card` | 5,36 : 1 | 4,5 : 1 | lulus | Placeholder di kartu |
| `placeholder` | `field` | 4,96 : 1 | 4,5 : 1 | lulus | Placeholder di isian |
| `primaryInk` | `card` | 6,10 : 1 | 4,5 : 1 | lulus | Tautan di kartu |
| `primaryInk` | `field` | 5,64 : 1 | 4,5 : 1 | lulus | Tautan di isian |
| `primaryInk` | `primaryTint` | 5,45 : 1 | 4,5 : 1 | lulus | Teks pilihan terpilih |
| `onDark` | `primary` | 4,67 : 1 | 4,5 : 1 | lulus | Teks tombol utama |
| `onDark` | `primaryLight` | 5,67 : 1 | 4,5 : 1 | lulus | Ujung gradasi tombol dan hero |
| `onDark` | `ink` | 19,15 : 1 | 4,5 : 1 | lulus | Filter terpilih |
| `green` | `card` | 5,02 : 1 | 4,5 : 1 | lulus | Teks hijau |
| `green` | `greenTint` | 4,55 : 1 | 4,5 : 1 | lulus | Pil delta membaik |
| `onDark` | `inkSoft` | 11,30 : 1 | 4,5 : 1 | lulus | Teks di atas lingkaran gelap |
| `orange` | `card` | 5,18 : 1 | 4,5 : 1 | lulus | Skor waspada di kartu |
| `red` | `card` | 6,47 : 1 | 4,5 : 1 | lulus | Teks merah |
| `red` | `redTint` | 5,95 : 1 | 4,5 : 1 | lulus | Badge gagal |
| `orange` | `orangeTint` | 4,68 : 1 | 4,5 : 1 | lulus | Tag Tier 2 |
| `yellow` | `yellowTint` | 4,57 : 1 | 4,5 : 1 | lulus | Tag Tier 3 |
| `ink` | `redTint` | 17,62 : 1 | 4,5 : 1 | lulus | Teks di highlight leksikal |
| `ink` | `orangeTint` | 17,31 : 1 | 4,5 : 1 | lulus | Teks di highlight semantik |
| `ink` | `yellowTint` | 17,77 : 1 | 4,5 : 1 | lulus | Teks di highlight stilometri |
| `yellow` | `card` | 4,92 : 1 | 3,0 : 1 | lulus | Garis bawah stilometri (non-teks) |
| `primary` | `card` | 4,67 : 1 | 4,5 : 1 | lulus | Titik biru judul dan cincin fokus |
| `primary` | `track` | 3,62 : 1 | 3,0 : 1 | lulus | Isi progres (non-teks) |

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
