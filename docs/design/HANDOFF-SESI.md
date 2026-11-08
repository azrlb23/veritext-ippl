# Serah-terima sesi: desain UI VeriText AI (SVG laptop 1440 px)

Dibuat 2026-11-03 supaya agen lain (Antigravity, Codex, dll.) bisa melanjutkan tanpa riwayat percakapan. Sumber kebenaran adalah berkas di repo dan `git status`, bukan catatan ini. Baca urutan ini sebelum bertindak: `docs/design/STYLE.md`, `.agents/rules/anti-ai-slop.md`, `docs/design/DAFTAR-LAYAR.md`, lalu dokumen ini.

Pemilik desain: Azriel (NIM 11241045), proyek IPPL (VeriText AI). Bahasa UI dan percakapan: Indonesia.

## 1. Lokasi

```
docs/design/
  STYLE.md              aturan gaya (DIBUAT OTOMATIS oleh system/build_style.py, jangan edit manual)
  DAFTAR-LAYAR.md       151 SVG yang harus dibuat + status
  HANDOFF-SESI.md       dokumen ini
  system/               generator + pemeriksa (Python 3.9, tanpa dependensi)
    tokens.json         SATU-SATUNYA sumber warna, radius, ukuran, anggaran
    vt_kit.py           pustaka komponen (satu-satunya tempat menggambar)
    build_auth.py       33 layar autentikasi
    build_dashboard.py  20 layar dashboard
    build_landing.py    beranda (ringkas = resmi, panjang = arsip)
    build_style.py      menulis STYLE.md
    check_style.py      pemeriksa otomatis R1-R10
    build_screens.py    SISA LAMA, tidak dipakai (boleh dihapus setelah user setuju)
    assets/outfit-widths.json   lebar huruf Outfit asli (dipakai mw())
  laptop/               hasil SVG
    landing--default-idle.svg
    auth/  dashboard/   (satu berkas per state)
    _lama/              arsip versi lama (tidak diperiksa pemeriksa)
  eksplorasi/           percobaan gaya (Boltshift v1/v2, palet-modern); bukan sistem
```

Berkas liar di akar repo dan `docs/svg/` (pagedone-login.svg, anywhere-signup.svg, 19 halaman versi pertama) adalah percobaan awal yang **melanggar aturan sekarang**. Jangan dipakai; tanyakan user sebelum menghapus.

## 2. Menjalankan dan memeriksa

```bash
cd docs/design/system
python3 build_auth.py && python3 build_dashboard.py && python3 build_landing.py
python3 build_style.py       # perbarui STYLE.md setelah mengubah token/aturan
python3 check_style.py       # harus 0 pelanggaran; argumen: path SVG tertentu
```

Python di mesin ini hanya 3.9. Jangan memakai sintaks 3.10+. Tidak ada dependensi pihak ketiga.

Cara melihat hasil: buka SVG di browser. Font Outfit dimuat dari Google Fonts lewat `@import` di dalam SVG, jadi perlu internet. SVG tinggi (beranda ±5.000 px) sebaiknya dilihat per potongan (ubah `viewBox` di salinan sementara).

## 3. Cara sistem bekerja (jangan dilanggar)

- Warna HANYA lewat nama token (`C['ink']`, `'primary'`, ...). Nama yang tidak ada akan `KeyError`. Jangan menulis hex di layar.
- Semua komponen digambar di `vt_kit.py`. Layar baru = rakit dari komponen; kalau perlu komponen baru, tambahkan ke kit.
- Permukaan `card` dengan filter `sh` otomatis menjadi kaca (putih 78%) lewat `rect()`.
- `page()` menggambar latar gradasi Aurora + orb blur. Gradien tersedia: `gHero` (biru), `gDark` (tombol utama), `gFilter`, `gBg`, `hatch`, `gSheen` (hanya di landing).
- Blok lama dipindah dengan `<g transform="translate(0 dy)">` (lihat `shift()` di `build_dashboard.py`).
- Satu layar = satu fungsi yang dikendalikan konfigurasi per state (lihat `STATES` di `build_dashboard.py`, daftar `LOGIN/REGISTER/...` di `build_auth.py`).
- Lebar teks dihitung dengan `mw(teks, ukuran, bobot)` dari tabel huruf asli. **Dilarang `textLength`** (membuat spasi antar kata melebar).
- Grup `data-role="illustration"` dikecualikan dari pemeriksa (dipakai panel kanan auth). Jangan menyalahgunakannya untuk menyelundupkan warna.
- Setelah mengubah kit/token, bangun ulang SEMUA layar dan jalankan pemeriksa.

## 4. Keputusan desain final (sudah disetujui user)

1. **Palet Aurora Biru:** latar gradasi lembut (`bg` -> `bgMid` -> `bgEnd`) + maksimal 3 orb blur per 1.400 px; kartu kaca putih 78% tanpa garis tepi; gradasi hanya `primary` -> `primaryLight` (kedua ujung kontras >=4,5:1 dengan teks putih).
2. **Gaya Boltshift** (header pil, menu pil, kartu metrik dengan satu lingkaran ikon + pil delta kecil, grafik batang dengan sorotan berarsir, gauge bersegmen) hanya di bagian ringkasan atas. Baris tabel/daftar tidak boleh memakai pil status, ikon bertile, atau pil persentase.
3. **Merek = teks "VeriText AI." saja.** Dilarang bulatan biru, kotak, ikon logo, monogram/lingkaran inisial (mis. "UU", "SK").
4. **Tombol utama gelap** (`ink` -> `inkSoft`), maksimal satu per layar. Tombol sekunder = isi netral tanpa garis. Tombol Filter bergradasi biru di dashboard adalah pengecualian.
5. **Alert = teks polos tanpa kotak** (merah untuk galat/peringatan, biru-tinta untuk info/sukses). **Fokus/error isian = garis bawah tebal 3 px**, bukan outline.
6. **Tipografi landing:** heading dua baris rata tengah (baris 1 `ink`, baris 2 `primary`, semibold), subjudul kecil dan sempit (maks ~58 karakter/baris, 2-3 baris). Font Outfit.
7. **Panel kanan layar auth:** orb biru diburamkan, empat pita kaca vertikal, wordmark putih "VeriText AI" di tengah, tiga label kecil di dalam inti biru (referensi Crunchy). Tanpa foto/lanskap.
8. **Beranda:** versi ringkas (5 seksi, ±4.987 px) adalah resmi. Seksi "Cara kerja" = carousel kartu ber-tab (kartu tengah bergradasi, kartu samping di belakang). Seksi kepercayaan = kutipan bertipografi besar + kolom angka + bar akreditasi.
9. **Bahasa untuk audiens:** jangan menampilkan konten developer (arsitektur, Celery/Redis, nama algoritma, "Live Production API", versi rilis) di halaman publik.

## 5. Aturan anti-slop (ringkas; sumber: `.agents/rules/anti-ai-slop.md` dan `STYLE.md`)

- Kapsul/badge status di setiap baris dilarang (status normal = teks abu; badge hanya untuk pengecualian, maks 2 per layar, tanpa label kembar).
- Kotak/lingkaran berwarna berisi ikon di setiap baris dilarang.
- Pil persentase berwarna pada tile statistik dilarang ("75% dari 12 audit" sebagai teks abu).
- Anggaran warna: biru primer + maks 3 warna status (hijau/oranye/merah/kuning dihitung per layar).
- Tanpa kartu di dalam kartu (blok `field` di dalam kaca boleh), tanpa sub-header generik, tanpa grafik pajangan.
- Jangan memperluas larangan sendiri. User pernah menegur saat larangan diperluas melebihi yang ia sebut (ia menyukai bagian atas gaya Boltshift).
- Jangan mengarang bukti (testimoni, angka, logo institusi). Tandai teks buatan sendiri dan akui.

`check_style.py` memeriksa: R1 warna hanya token, R2 font >=12, R3 bingkai hanya peran sah, R4 warna teks dari daftar, R5 maks satu tombol primary, R6 tombol >=44 px, R7 kontras dari token, R8 badge maks 2 tanpa kembar, R9 maks 3 warna status, R10 tanpa >=3 ikon bertile sejajar vertikal. Pemeriksa tidak menilai selera: selalu lihat hasil render.

## 6. Status

Selesai (54 SVG, semuanya lolos pemeriksa): beranda ringkas, 33 layar auth (login 13, register 10, lupa sandi 5, reset sandi 5), 20 layar dashboard.

Belum (urutan yang disarankan, detail ID di `DAFTAR-LAYAR.md`):
1. **Detail laporan audit (±13):** split pane desktop (naskah + highlight 60%, inspector 40%), tab Ringkasan/Sumber/Diff, popover dan modal kalimat, filter tier, ekspor PDF, dialog hapus, 404. Tier: merah (leksikal), oranye (semantik), kuning (stilometri).
2. **Chat AI (13):** panel chat di laporan, pil hero hidup, consent, streaming, kutipan, penolakan, galat, rate limit, kuota. **Tunda sampai keputusan privasi (bagian 8).**
3. Bank korpus (13), billing (11), verifikasi sertifikat (7), konsol admin (12).
4. Halaman galat sistem (15) lalu varian mobile (8, ditunda).

Jangan commit tanpa diminta user. Belum ada yang di-commit.

## 7. Cara kerja yang disukai user

1. Tunggu referensi UI/UX sebelum membangun halaman baru; jangan langsung membangun banyak layar.
2. Satu keluarga layar per kelompok: 1-2 contoh dulu, lalu batch; laporkan apa yang dibuat, asumsi, dan kekurangan.
3. Setelah render, periksa tumpang-tindih (teks/tombol/modal) dan perbaiki sendiri sebelum melapor.
4. Saat meringkas/mengubah besar: diagnosis jujur -> usulan konkret -> minta persetujuan -> file terpisah -> buktikan refaktor tidak mengubah hasil lama (`cmp`).
5. Kreatif lewat struktur, kedalaman, dan tipografi, bukan dekorasi atau warna tambahan.
6. Jawab dan tulis dalam bahasa Indonesia, ringkas, tanpa memuji diri.

## 8. Pertanyaan terbuka

- **Chat AI (Gemini):** landing berjanji "tanpa pelatihan model pihak ketiga" dan kepatuhan UU PDP; mengirim potongan hasil audit ke Gemini bertentangan kecuali memakai tier API yang tidak melatih dari data, ada persetujuan eksplisit, dan data minimal. Backend saat ini tidak memakai LLM eksternal (Tier 3 = statistik lokal). Chatbot tidak boleh menjadi alat "tulis ulang supaya lolos deteksi". Keputusan ada di user.
- Dialog batalkan tugas menyatakan token dikembalikan (berdasar commit backend "refund on cancel"); belum diverifikasi ke kode.
- Teks keterangan akreditasi, deskripsi tier di landing, dan data contoh (85%, 1,2 dtk, 30 hari, 12.480 naskah) adalah contoh, bukan data nyata.
- Aturan fokus `focus-visible:ring-2` di rule IPPL bertentangan dengan garis bawah fokus; user memilih garis bawah.
- Fakta proyek lain ada di `docs/PROJECT_CONTEXT.md` (login seed melewati cek hash, Tier 2 memakai embedding buatan sendiri, hapus naskah baru soft delete).

## 9. Jebakan teknis

- `data-role="state-bar"` dipakai untuk garis bawah fokus/error; jangan memakai `stroke` pada `rect` kecuali peran sah (`dropzone`, `radio`).
- Dropzone memakai `stroke` putus-putus (peran `dropzone`) dan titik radio memakai `data-role="radio"`.
- Posisi seksi beranda ringkas ditentukan di `build_short()` (offset eksplisit). Menambah baris di satu seksi menggeser seksi sesudahnya: sesuaikan offset.
- `build_landing.py` memakai pergeseran global `OFF` untuk blok yang dipakai ulang; jangan lupa meresetnya ke 0.
- Peramban pratinjau yang dipakai sesi ini hanya merender SVG di dalam folder proyek dan menyusutkan gambar tinggi; potong `viewBox` untuk memeriksa detail.
