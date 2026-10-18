---
name: flowchart-maker
description: Desain flowchart profesional, diagram alur data (DFD), sequence diagram, dan arsitektur sistem, dengan kapabilitas otomatis merender dan mengekspor diagram menjadi berkas gambar PNG/SVG resolusi tinggi. Gunakan ketika merancang flowchart, diagram alur, atau saat pengguna meminta luaran gambar PNG diagram.
metadata:
  model: haiku
---

# Flowchart Maker & PNG Renderer Skill

Skill ini membekali agent dengan keahlian ganda:
1. **Perancangan Diagram Profesional**: Mendesain diagram alur (Flowchart), Data Flow Diagram (DFD), Sequence Diagram, dan arsitektur perangkat lunak dengan standar notasi rekayasa perangkat lunak modern.
2. **Kompilasi Gambar PNG Otomatis**: Mengekspor kode diagram (Mermaid / PlantUML / Graphviz) secara otomatis menjadi berkas gambar biner PNG resolusi tinggi menggunakan skrip terintegrasi `render_diagram.py`.

---

## 1. Kapan Menggunakan Skill Ini

Gunakan skill ini ketika:
- Pengguna meminta pembuatan **Flowchart**, diagram proses, DFD, atau Sequence Diagram.
- Pengguna secara eksplisit meminta **luaran berupa gambar PNG/JPEG** dari diagram.
- Diagram yang ada mengalami masalah *rendering* (seperti *bug* kotak hitam pekat pada SVG converter atau *parse error* sintaks).
- Pengguna ingin mengorganisir diagram ke dalam folder visual (misal: `Diagram_PNGs/` atau `diagram/`).

---

## 2. Standar Desain Flowchart & Pencegahan Bug Visual

Saat menyusun diagram Mermaid:
1. **Pencegahan Bug Kotak Hitam (Cluster Black-Box Bug)**:
   - Hindari penggunaan `subgraph` tanpa styling latar belakang yang jelas, karena beberapa converter SVG/Word menerapkan nilai default `fill: black`.
   - **Solusi Rekomendasi**:
     - Gunakan hierarki datar (*Flat Flowchart* tanpa subgraph) untuk kompatibilitas 100% pada semua converter.
     - ATAU beri deklarasi style eksplisit: `style SUBGRAPH_ID fill:#F8FAFC,stroke:#94A3B8,stroke-width:2px,color:#0F172A`.
2. **Karakter Terlarang dalam Teks Label**:
   - Jangan gunakan titik koma (`;`) di dalam label teks Mermaid (titik koma adalah *statement delimiter* yang memotong baris).
   - Jangan gunakan tanda kutip ganda (`"`) di dalam string yang sudah diapit kutip.
   - Hindari entitas HTML seperti `&gt;` atau `&lt;` yang mengandung titik koma; gunakan kata pengganti seperti `lebih dari`, `minimal`, atau `melebihi`.
3. **Bentuk Simbol Baku**:
   - `[Proses / Langkah]` : Kotak persegi panjang.
   - `{"Keputusan / Decision?"}` : Bentuk belah ketupat (*diamond*).
   - `[("Database / Data Store")]` : Bentuk silinder data.
   - `(["Terminal Awal / Akhir"])` : Bentuk kapsul / rounded rectangle.

---

## 3. Prosedur Otomatisasi Pembuatan Gambar PNG

Untuk menghasilkan berkas gambar PNG langsung ke komputer pengguna, jalankan skrip pembantu yang terpasang pada skill ini:

### Sintaks Eksekusi Skrip:
```bash
python3 .agents/skills/flowchart-maker/scripts/render_diagram.py <file_diagram.mmd> -o <target_folder/nama_file.png> -t mermaid -f png
```

### Parameter:
* `<file_diagram.mmd>`: Berkas teks sumber diagram Mermaid (atau gunakan opsi `--code "flowchart TD..."` untuk kode langsung).
* `-o, --output`: Lokasi dan nama berkas gambar PNG tujuan (misal: `Diagram_PNGs/flowchart_utama.png`).
* `-t, --type`: Jenis mesin diagram (`mermaid`, `plantuml`, `graphviz`, `d2`). Default: `mermaid`.
* `-f, --format`: Format keluaran gambar (`png`, `svg`, `jpeg`, `pdf`). Default: `png`.

---

## 4. Struktur Direktori Rekomendasi

Organisasikan berkas diagram di dalam proyek dengan konvensi berikut:
```
IPPL/
├── diagram/                 # Menyimpan source code diagram (.mmd / .puml)
│   ├── alur_data_utama.mmd
│   └── sequence_auth.mmd
└── Diagram_PNGs/            # Menyimpan hasil render gambar (.png)
    ├── alur_data_utama.png
    └── sequence_auth.png
```

---

## 5. Fallback & Penanganan Lingkungan Terisolasi

Jika akses jaringan dibatasi oleh sandbox:
1. Skrip akan secara otomatis mencetak **Tautan Unduh Langsung (Kroki Direct URL)** yang dapat dibuka oleh pengguna di peramban mereka untuk mengunduh PNG dalam 1 klik.
2. Sediakan juga berkas pratinjau HTML interaktif lokal (`diagram_generator.html`) yang menggunakan pustaka *pako deflate* di peramban klien sehingga pengguna tetap dapat mengonversi gambar secara instan tanpa hambatan lingkungan server.
