"""Keluarga Layar Bank Korpus Dokumen (laptop 1440 px).

Pembaruan Refined UI/UX Pro Max (Audyr / Boltshift standard):
1. Header lebih ringkas & bersih tanpa konten teknis/developer berlebihan:
   - Judul: "Bank Korpus"
   - Subjudul: "Basis data referensi naskah akademik pembanding"
2. Tombol Aksi di Header:
   - Satu tombol utama gelap: [ + Unggah ]
   - Satu tombol ikon sekunder kompak: [ (Ikon Panah Atas) ZIP ]
3. Variasi Visual Atas (Bukan cuma deretan kartu metrik generik):
   - Kolom Kiri: Gauge kapasitas penyimpanan terpakai & sebaran kategori naskah
   - Kolom Kanan: 2 Metrik ringkas terintegrasi + status sinkronisasi
4. Padding & Spacing proporsional, tactile buttons, tanpa AI slop.
"""
import os
import sys
from vt_kit import (C, HERE, W, mw, text, rect, circle, hair, card, btn, link, ico, chevron,
                    segmented, select, progress, spinner, badge, segarc, dash, page, table_head, search_pill)

OUT = os.path.join(HERE, '..', 'laptop', 'corpus')
os.makedirs(OUT, exist_ok=True)

# Data contoh dokumen korpus (ditandai contoh buatan):
CORPUS_ROWS = [
    ("Jurnal Agronomi Pesisir Vol. 14", "Dr. Ir. Suhendra, M.Si.", "Jurnal Ilmiah", "28 Okt 2026", "1.420 vektor", "Terindeks"),
    ("Prosiding Simposium Ketahanan Iklim 2024", "Budi Santoso dkk.", "Prosiding", "24 Okt 2026", "3.110 vektor", "Terindeks"),
    ("Model Hidrometeorologi Estuari Jawa", "Puslitbang SDA", "Laporan Riset", "19 Okt 2026", "890 vektor", "Terindeks"),
    ("Analisis Spasial Salinitas Lahan Basah", "Prof. Hartono, M.Sc.", "Tesis / Disertasi", "15 Okt 2026", "2.450 vektor", "Terindeks"),
    ("Sintesis Varietas Padi Toleran Salin", "Kelompok Peneliti Bioteknologi", "Buku / Bab", "10 Okt 2026", "1.180 vektor", "Terindeks"),
]


def corpus_header(has_modal=False):
    """Header ringkas & bersih: Judul singkat, subjudul fungsional, tombol aksi efisien."""
    b = ''
    from vt_kit import topnav
    b += topnav(['Dashboard', 'Audit', 'Korpus', 'Billing', 'Admin'], 'Korpus', 'Dr. Hendra Gunawan', 'hendra@nusantara.ac.id', 'HG')
    
    # Subheader ringkas tanpa jargon teknis berlebihan
    b += text(48, 142, 'Workspace Dosen  /  Repositori Referensi', 13, 500, 'sub')
    b += text(48, 174, 'Bank Korpus', 24, 600, 'ink', ls=-0.4)
    b += text(48, 200, 'Basis data referensi naskah akademik pembanding untuk pengujian kemiripan', 13.5, 400, 'sub')
    
    # Tombol aksi kanan atas:
    # 1. Tombol primer gelap: + Unggah (ringkas)
    # 2. Tombol ikon sekunder: Upload ZIP
    btn_kind = 'secondary' if has_modal else 'primary'
    b += btn(1150, 150, 142, 48, '+ Unggah', btn_kind, 14)
    
    # Tombol ZIP: Ikon + 1 kata
    b += rect(1302, 150, 90, 48, 'field', 24)
    b += ico('up', 1324, 174, 'ink', 1.6)
    b += text(1342, 179, 'ZIP', 13.5, 600, 'ink')
    
    b += hair(48, 222, W - 48, 222)
    return b


def pane_corpus_analytics(y=242):
    """Variasi Visual: Kiri = Visualisasi Kapasitas Storage & Bar Kategori; Kanan = 2 Kartu Metrik Ringkas."""
    b = ''
    
    # 1. Panel Kiri (Visualisasi Kapasitas & Distribusi): w=840 (total w=1344)
    w_left = 840
    b += card(48, y, w_left, 134)
    
    b += text(76, y + 36, 'Kapasitas Penyimpanan Referensi', 15, 600, 'ink')
    b += text(76, y + 58, '4,82 GB terpakai dari total kuota alokasi 20 GB (24,1%)', 13, 400, 'sub')
    
    # Segmented Storage Bar multi-kategori
    bx, by, bw = 76, y + 74, w_left - 56
    b += rect(bx, by, bw, 12, 'field', 6)
    # Jurnal (Biru) 45%
    b += rect(bx, by, bw * 0.45, 12, 'primary', 6)
    # Tesis/Disertasi (Cyan) 30%
    b += rect(bx + bw * 0.45, by, bw * 0.30, 12, 'auroraCyan', 0)
    # Prosiding & Buku (Soft) 15%
    b += rect(bx + bw * 0.75, by, bw * 0.15, 12, 'track', 0)
    
    # Legenda Kategori di bawah bar
    b += circle(bx + 6, y + 108, 4, 'primary')
    b += text(bx + 16, y + 112, 'Jurnal (558)', 12, 500, 'sub')
    
    b += circle(bx + 140, y + 108, 4, 'auroraCyan')
    b += text(bx + 150, y + 112, 'Tesis & Disertasi (372)', 12, 500, 'sub')
    
    b += circle(bx + 330, y + 108, 4, 'track')
    b += text(bx + 340, y + 112, 'Prosiding & Buku (310)', 12, 500, 'sub')
    
    b += text(bx + bw, y + 112, 'Status: Sinkronisasi Normal', 12, 600, 'green', 'end')

    # 2. Dua Kartu Metrik di Kanan: w=228 per card (48 + 840 + 24 + 228 + 24 + 228 = 1392)
    w_card = 228
    # Kartu 1: Total Dokumen
    x1 = 48 + w_left + 24
    b += card(x1, y, w_card, 134)
    b += circle(x1 + 32, y + 36, 16, 'field')
    b += ico('doc', x1 + 32, y + 36, 'primaryInk', 1.6)
    b += text(x1 + 58, y + 40, 'Total Dokumen', 13, 500, 'sub')
    b += text(x1 + 32, y + 84, '1.240', 28, 600, 'ink', ls=-0.6)
    b += text(x1 + 32, y + 108, '↑ 42 naskah bulan ini', 12, 500, 'green')

    # Kartu 2: Vektor Terindeks
    x2 = x1 + w_card + 24
    b += card(x2, y, w_card, 134)
    b += circle(x2 + 32, y + 36, 16, 'field')
    b += ico('stack', x2 + 32, y + 36, 'primaryInk', 1.6)
    b += text(x2 + 58, y + 40, 'Vektor Terindeks', 13, 500, 'sub')
    b += text(x2 + 32, y + 84, '384.920', 28, 600, 'ink', ls=-0.6)
    b += text(x2 + 32, y + 108, 'Model 384-dimensi aktif', 12, 400, 'sub')

    return b


def pane_corpus_table(y=400, empty=False, indexing=False, search_query='', filter_no_match=False):
    """Area Konten: Search bar, filter kategori, tabel naskah korpus (menempel ke kanan, kiri, dan bawah layar)."""
    h_panel = 1020 - y  # 620 px
    b = ''
    # Panel penuh menempel ke kanan, kiri, dan bawah layar
    b += rect(0, y, W, h_panel, 'card', filt='sh')
    b += hair(0, y, W, y)
    
    # Bar Pencarian & Filter di atas tabel (dimulai dari x=48)
    b += search_pill(48, y + 24, 400, search_query if search_query else 'Cari judul naskah atau penulis…')
    
    # Filter Segmented Kategori
    categories = ['Semua Kategori', 'Jurnal Ilmiah', 'Prosiding', 'Tesis / Disertasi', 'Buku']
    b += segmented(468, y + 26, categories, 0)
    
    # Tombol pemicu Re-Index di kanan atas tabel (berakhir di x=1392)
    b += rect(1392 - 168, y + 26, 168, 44, 'field', 22)
    b += ico('gear', 1392 - 146, y + 48, 'ink', 1.6)
    b += text(1392 - 126, y + 53, 'Jadwalkan Re-Index', 13, 500, 'ink')
    
    # Kepala Tabel
    cols = [
        ('JUDUL NASKAH REFERENSI', 48, 'start'),
        ('PENULIS & LEMBAGA', 480, 'start'),
        ('KATEGORI', 780, 'start'),
        ('TANGGAL TERBIT', 960, 'start'),
        ('STATUS VEKTOR', 1140, 'start'),
        ('AKSI', 1392, 'end'),
    ]
    for lab, x_pos, anc in cols:
        b += text(x_pos, y + 104, lab.upper(), 12, 600, 'sub', anc, ls=0.8)
    b += hair(0, y + 116, W, y + 116)
    
    if empty or filter_no_match:
        cx, cy = W // 2, y + 300
        b += circle(cx, cy - 40, 32, 'field')
        b += ico('doc', cx, cy - 40, 'sub', 2.0)
        if filter_no_match:
            b += text(cx, cy + 20, 'Tidak Ditemukan Dokumen yang Cocok', 18, 600, 'ink', 'middle')
            b += text(cx, cy + 44, 'Tidak ada dokumen referensi dengan kata kunci pencarian tersebut.', 13.5, 400, 'sub', 'middle')
            b += link(cx, cy + 76, 'Reset Kata Kunci Pencarian →', 13.5, anchor='middle')
        else:
            b += text(cx, cy + 20, 'Belum ada dokumen referensi', 20, 600, 'ink', 'middle')
            b += text(cx, cy + 46, 'Unggah berkas naskah ilmiah untuk memulai basis data pembanding.', 14, 400, 'sub', 'middle')
            b += btn(cx - 90, cy + 74, 180, 48, '+ Unggah naskah', 'primary', 14)
        return b
        
    rows_data = list(CORPUS_ROWS)
    if indexing:
        rows_data = [
            ("Kajian Dinamika Pantai dan Erosi Pesisir", "Rahmat Hidayat (UNDIP)", "Jurnal Ilmiah", "Hari ini", "Ekstraksi...", "Mengindeks...")
        ] + rows_data[:4]
        
    for i, (title, author, cat_lbl, date_lbl, vec_lbl, status_lbl) in enumerate(rows_data):
        ry = y + 144 + i * 66
        if i > 0:
            b += hair(0, ry - 14, W, ry - 14)
            
        is_indexing_row = status_lbl == "Mengindeks..."
        
        b += text(48, ry + 16, title, 14.5, 600, 'ink')
        b += text(480, ry + 16, author, 13.5, 400, 'sub')
        b += text(780, ry + 16, cat_lbl, 13, 500, 'ink')
        b += text(960, ry + 16, date_lbl, 13, 400, 'sub')
        
        if is_indexing_row:
            b += spinner(1140, ry + 12, 6.5, 'yellow', 2.0)
            b += text(1154, ry + 16, 'Mengindeks…', 12.5, 600, 'yellow')
        else:
            b += text(1140, ry + 16, vec_lbl, 13, 400, 'sub')
            
        b += text(1392, ry + 16, 'Hapus', 12.5, 500, 'red', 'end')
        b += text(1348, ry + 16, '·', 12.5, 400, 'sub', 'middle')
        b += link(1340, ry + 16, 'Unduh', 12.5, anchor='end')
        
    py = 1020 - 46
    b += hair(0, py - 16, W, py - 16)
    b += text(48, py + 10, 'Menampilkan 1–5 dari 1.240 dokumen naskah', 13, 400, 'sub')
    
    px = 1392 - 164
    b += rect(px, py - 8, 40, 36, 'field', 18)
    b += ico('search', px + 20, py + 10, 'sub', 1.6)
    b += rect(px + 42, py - 8, 38, 36, 'ink', 18)
    b += text(px + 61, py + 15, '1', 13.5, 600, 'onDark', 'middle')
    b += rect(px + 84, py - 8, 38, 36, 'field', 18)
    b += text(px + 103, py + 15, '2', 13.5, 500, 'ink', 'middle')
    b += rect(px + 126, py - 8, 38, 36, 'field', 18)
    b += text(px + 145, py + 15, '3', 13.5, 500, 'ink', 'middle')
    
    return b


def modal_upload_single():
    """Modal unggah dokumen naskah korpus tunggal."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 280, 200, 560, 540
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += text(mx + 36, my + 44, 'Unggah Naskah Referensi', 20, 600, 'ink')
    b += text(mx + 36, my + 68, 'Naskah akan diindeks ke dalam korpus pembanding', 13.5, 400, 'sub')
    b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round"><path d="M-6 -6L6 6M6 -6L-6 6"/></g>' % (mx + mw_box - 36, my + 44, C['sub'])
    b += hair(mx + 24, my + 88, mx + mw_box - 24, my + 88)
    
    from vt_kit import field
    b += field(mx + 36, my + 110, mw_box - 72, 'Judul Dokumen Ilmiah', 'Kajian Dinamika Pantai dan Erosi Pesisir', state='focus')
    b += field(mx + 36, my + 180, mw_box - 72, 'Penulis / Pengarang Utama', 'Rahmat Hidayat (UNDIP)', state='idle')
    
    b += text(mx + 36, my + 266, 'Kategori Dokumen', 12.5, 500, 'sub')
    b += select(mx + 36, my + 276, mw_box - 72, 'Jurnal Ilmiah Terakreditasi', surface='field')
    
    b += rect(mx + 36, my + 340, mw_box - 72, 100, 'field', 14, role='dropzone', stroke='placeholder', sw=1.5, dash='6 5')
    b += ico('up', mx + mw_box // 2, my + 372, 'primaryInk', 1.8)
    b += text(mx + mw_box // 2, my + 400, 'kajian-pantai-2026.pdf (2,4 MB)', 13.5, 600, 'ink', 'middle')
    b += text(mx + mw_box // 2, my + 420, 'Format didukung: .pdf, .docx, .txt (maks 50 MB)', 12, 400, 'sub', 'middle')
    
    b += btn(mx + 36, my + 466, mw_box - 72, 48, 'Mulai Ekstraksi & Indeks', 'primary', 14)
    return b


def modal_upload_zip(progress_pct=None):
    """Modal unggah batch arsip ZIP dokumen referensi."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 280, 220, 560, 490
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += text(mx + 36, my + 44, 'Unggah Arsip ZIP Korpus', 20, 600, 'ink')
    b += text(mx + 36, my + 68, 'Ekstraksi kumpulan naskah ilmiah secara otomatis', 13.5, 400, 'sub')
    b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round"><path d="M-6 -6L6 6M6 -6L-6 6"/></g>' % (mx + mw_box - 36, my + 44, C['sub'])
    b += hair(mx + 24, my + 88, mx + mw_box - 24, my + 88)
    
    if progress_pct is not None:
        b += circle(mx + mw_box // 2, my + 155, 26, 'primaryTint')
        b += ico('stack', mx + mw_box // 2, my + 155, 'primaryInk', 2.0)
        b += text(mx + mw_box // 2, my + 208, 'Mengekstrak Arsip ZIP… (%d%%)' % progress_pct, 18, 600, 'ink', 'middle')
        b += text(mx + mw_box // 2, my + 230, 'Mendekompresi 24 dokumen PDF & verifikasi berkas…', 13.5, 400, 'sub', 'middle')
        
        b += progress(mx + 48, my + 260, mw_box - 96, progress_pct)
        b += text(mx + 48, my + 290, 'Memproses: jurnal-agronomi-batch-04.pdf', 12.5, 400, 'sub')
        b += text(mx + mw_box - 48, my + 290, '14 / 24 selesai', 12.5, 600, 'ink', 'end')
        
        b += rect(mx + 48, my + 348, mw_box - 96, 48, 'disabled', 24)
        b += text(mx + mw_box // 2, my + 377, 'Memproses di Background…', 13.5, 500, 'sub', 'middle')
    else:
        b += rect(mx + 36, my + 120, mw_box - 72, 160, 'field', 16, role='dropzone', stroke='placeholder', sw=1.5, dash='6 5')
        b += ico('stack', mx + mw_box // 2, my + 170, 'primaryInk', 2.2)
        b += text(mx + mw_box // 2, my + 208, 'Tarik & lepas berkas .ZIP di sini', 16, 600, 'ink', 'middle')
        b += text(mx + mw_box // 2, my + 230, 'Maksimal 100 naskah per arsip ZIP (Maks 100 MB)', 13, 400, 'sub', 'middle')
        b += link(mx + mw_box // 2, my + 256, 'atau pilih dari komputer →', 13, anchor='middle')
        
        b += text(mx + 36, my + 316, 'Format file di dalam ZIP harus berupa .pdf, .docx, atau .txt.', 12.5, 400, 'sub')
        b += text(mx + 36, my + 338, 'Sistem memindai otomatis struktur berkas untuk keamanan.', 12.5, 400, 'sub')
        
        b += btn(mx + 36, my + 404, mw_box - 72, 48, 'Mulai Ekstraksi Batch', 'primary', 14)
        
    return b


def modal_delete_corpus():
    """Dialog konfirmasi penghapusan naskah dari Bank Korpus."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 270, 260, 540, 290
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += circle(mx + mw_box // 2, my + 54, 24, 'redTint')
    b += ico('doc', mx + mw_box // 2, my + 54, 'red', 2.0)
    
    b += text(mx + mw_box // 2, my + 112, 'Hapus Dokumen dari Korpus?', 19, 600, 'ink', 'middle')
    b += text(mx + mw_box // 2, my + 138, 'Naskah "Jurnal Agronomi Pesisir Vol. 14" dan 1.420 vektor', 13.5, 500, 'ink', 'middle')
    b += text(mx + mw_box // 2, my + 158, 'akan dihapus secara permanen dari basis data referensi.', 13.5, 400, 'sub', 'middle')
    
    b += rect(mx + 48, my + 204, 210, 48, 'redTint', 24)
    b += text(mx + 153, my + 233, 'Ya, Hapus Dokumen', 14, 600, 'red', 'middle')
    b += btn(mx + 282, my + 204, 210, 48, 'Batal', 'secondary', 14)
    
    return b


def toast_reindex():
    """Toast notifikasi saat re-indeks dijadwalkan."""
    tx, ty, tw_toast = W // 2 - 200, 100, 400
    b = rect(tx, ty, tw_toast, 48, 'ink', 24, filt='sh-hero')
    b += circle(tx + 24, ty + 24, 6, 'green')
    b += text(tx + 40, ty + 29, 'Re-indeksasi dokumen korpus dijadwalkan!', 13, 500, 'onDark')
    return b


def build_skeleton():
    """State: corpus--loading-skeleton."""
    b = corpus_header()
    
    # Area Analitik Skeleton (48 + 840 + 24 + 228 + 24 + 228 = 1392)
    w_left = 840
    b += card(48, 242, w_left, 134)
    b += rect(76, 270, 220, 16, 'track', 8)
    b += rect(76, 296, 320, 12, 'track', 6)
    b += rect(76, 318, w_left - 56, 12, 'field', 6)
    
    w_card = 228
    for i in range(2):
        x = 48 + w_left + 24 + i * (w_card + 24)
        b += card(x, 242, w_card, 134)
        b += circle(x + 32, 278, 16, 'track')
        b += rect(x + 58, 270, 100, 14, 'track', 7)
        b += rect(x + 32, 312, 90, 22, 'track', 11)
        
    # Tabel Skeleton (menempel ke kanan, kiri, dan bawah layar y=1020)
    b += rect(0, 400, W, 1020 - 400, 'card', filt='sh')
    b += hair(0, 400, W, 400)
    b += rect(48, 424, 380, 44, 'track', 22)
    b += rect(450, 424, 360, 44, 'track', 22)
    b += hair(0, 484, W, 484)
    
    for r in range(6):
        ry = 512 + r * 64
        b += rect(48, ry, 280, 16, 'track', 8)
        b += rect(480, ry, 180, 14, 'track', 7)
        b += rect(780, ry, 100, 14, 'track', 7)
        b += rect(960, ry, 120, 14, 'track', 7)
        b += rect(1140, ry, 110, 14, 'track', 7)
        
    return page('Memuat Bank Korpus - VeriText AI', 'Skeleton loading state saat repositori naskah korpus dimuat.', W, 1020, b)


def build_all():
    """Membangun 12 layar keluarga Bank Korpus Dokumen (laptop 1440 px)."""
    print("Membangun ulang keluarga layar Bank Korpus Dokumen (Refined UI/UX)...")
    
    base_page = corpus_header() + pane_corpus_analytics(242)
    
    # 1. Populated Desktop Table (Default)
    svg1 = page(
        'Bank Korpus - VeriText AI',
        'Repositori naskah ilmiah pembanding untuk pengujian kemiripan.',
        W, 1020, base_page + pane_corpus_table(400)
    )
    with open(os.path.join(OUT, 'corpus--populated-desktop-table.svg'), 'w') as f:
        f.write(svg1)
        
    # 2. Loading Skeleton
    with open(os.path.join(OUT, 'corpus--loading-skeleton.svg'), 'w') as f:
        f.write(build_skeleton())
        
    # 3. Empty Repository (Zero-data)
    svg3 = page(
        'Bank Korpus Kosong - VeriText AI',
        'Tampilan saat belum ada naskah referensi di dalam repositori korpus.',
        W, 1020, corpus_header(has_modal=True) + pane_corpus_analytics(242) + pane_corpus_table(400, empty=True)
    )
    with open(os.path.join(OUT, 'corpus--empty-repository.svg'), 'w') as f:
        f.write(svg3)
        
    # 4. Search Filtering Active
    svg4 = page(
        'Pencarian Korpus - VeriText AI',
        'Penyaringan dokumen referensi berdasarkan kata kunci naskah.',
        W, 1020, base_page + pane_corpus_table(400, search_query='Agronomi Pesisir')
    )
    with open(os.path.join(OUT, 'corpus--search-filtering-active.svg'), 'w') as f:
        f.write(svg4)
        
    # 5. Search No Results
    svg5 = page(
        'Pencarian Tidak Ditemukan - VeriText AI',
        'Tampilan saat kata kunci pencarian naskah korpus tidak menghasilkan kecocokan.',
        W, 1020, base_page + pane_corpus_table(400, filter_no_match=True, search_query='Kriptografi Kuantum')
    )
    with open(os.path.join(OUT, 'corpus--search-no-results.svg'), 'w') as f:
        f.write(svg5)
        
    # 6. Upload Single Modal Open
    svg6 = page(
        'Unggah Naskah Korpus - VeriText AI',
        'Dialog modal pengunggahan naskah ilmiah referensi tunggal.',
        W, 1020, corpus_header(has_modal=True) + pane_corpus_analytics(242) + pane_corpus_table(400) + modal_upload_single()
    )
    with open(os.path.join(OUT, 'corpus--upload-single-modal-open.svg'), 'w') as f:
        f.write(svg6)
        
    # 7. Upload ZIP Modal Open
    svg7 = page(
        'Unggah Arsip ZIP Korpus - VeriText AI',
        'Dialog modal pengunggahan massal arsip ZIP dokumen korpus.',
        W, 1020, corpus_header(has_modal=True) + pane_corpus_analytics(242) + pane_corpus_table(400) + modal_upload_zip()
    )
    with open(os.path.join(OUT, 'corpus--upload-zip-modal-open.svg'), 'w') as f:
        f.write(svg7)
        
    # 8. Uploading Progress
    svg8 = page(
        'Proses Dekompresi Batch - VeriText AI',
        'Bar progres proses dekompresi dan ekstraksi naskah arsip ZIP.',
        W, 1020, corpus_header(has_modal=True) + pane_corpus_analytics(242) + pane_corpus_table(400) + modal_upload_zip(progress_pct=58)
    )
    with open(os.path.join(OUT, 'corpus--uploading-progress.svg'), 'w') as f:
        f.write(svg8)
        
    # 9. Indexing Badge Active
    svg9 = page(
        'Mengindeks Vektor pgvector - VeriText AI',
        'Baris dokumen baru menampilkan indikator spinner kuning proses ekstraksi embeddings.',
        W, 1020, base_page + pane_corpus_table(400, indexing=True)
    )
    with open(os.path.join(OUT, 'corpus--indexing-badge-active.svg'), 'w') as f:
        f.write(svg9)
        
    # 10. Indexing Success Badge
    svg10 = page(
        'Vektor Terindeks Berhasil - VeriText AI',
        'Seluruh dokumen korpus berstatus terindeks hijau di pgvector HNSW.',
        W, 1020, base_page + pane_corpus_table(400)
    )
    with open(os.path.join(OUT, 'corpus--indexing-success-badge.svg'), 'w') as f:
        f.write(svg10)
        
    # 11. Delete Confirm Modal Open
    svg11 = page(
        'Konfirmasi Hapus Korpus - VeriText AI',
        'Dialog modal konfirmasi penghapusan dokumen dan vektor dari bank korpus.',
        W, 1020, base_page + pane_corpus_table(400) + modal_delete_corpus()
    )
    with open(os.path.join(OUT, 'corpus--delete-confirm-modal-open.svg'), 'w') as f:
        f.write(svg11)
        
    # 12. Reindex Triggering Toast
    svg12 = page(
        'Jadwalkan Re-Index Korpus - VeriText AI',
        'Toast notifikasi saat perintah re-indeksasi seluruh naskah dikirim ke Celery worker.',
        W, 1020, base_page + pane_corpus_table(400) + toast_reindex()
    )
    with open(os.path.join(OUT, 'corpus--reindex-triggering.svg'), 'w') as f:
        f.write(svg12)
        
    print("Selesai merevisi 12 SVG keluarga Bank Korpus Dokumen.")


if __name__ == '__main__':
    build_all()
