"""Keluarga Layar Detail Laporan Audit & Heatmap (laptop 1440 px).

Pola mengikuti build_dashboard.py:
- Layout split-pane desktop: kiri (~60% / 780px naskah ber-highlight kalimat), kanan (~40% / 544px inspector tabbed).
- Header topnav + subheader naskah & tombol ekspor PDF.
- Blok-blok yang dirakit per state:
  1. audit-detail--desktop-split-pane (default split pane)
  2. audit-detail--tab-summary-active (tab ringkasan aktif)
  3. audit-detail--tab-sources-active (tab sumber korpus aktif)
  4. audit-detail--tab-diff-active (tab perbandingan diff kalimat)
  5. audit-detail--filter-tier-highlights (filter tier dimatikan/dinyalakan)
  6. audit-detail--sentence-popover-hover (tooltip hover pada kalimat tersorot)
  7. audit-detail--sentence-modal-open (dialog modal detail kalimat dibuka)
  8. audit-detail--exporting-pdf-spinner (state loading unduh PDF)
  9. audit-detail--export-pdf-success (state sukses unduh PDF)
  10. audit-detail--delete-dialog-open (dialog konfirmasi hapus permanen UU PDP)
  11. audit-detail--deleting-in-progress (state proses penghapusan naskah)
  12. audit-detail--loading-skeleton (state shimmer memuat naskah)
  13. audit-detail--error-not-found-404 (state galat dokumen 404)
"""
import os
import sys
from vt_kit import (C, HERE, W, mw, text, rect, circle, hair, card, btn, link, ico, chevron,
                    segmented, select, progress, spinner, badge, segarc, dash, page, rich, HL, table_head)

OUT = os.path.join(HERE, '..', 'laptop', 'audit')
os.makedirs(OUT, exist_ok=True)

# Data contoh naskah akademik (ditandai contoh buatan):
DOC_TITLE = "Dampak Perubahan Iklim terhadap Ketahanan Pangan Lokal di Wilayah Pesisir"
DOC_META = "Penulis: Rizky Pratama (NIM 11241045) · Institut Teknologi Nusantara · Diperiksa: 03 Nov 2026, 09.12 WIB"

PARAGRAFS = [
    [
        ("Perubahan iklim global merupakan salah satu tantangan lingkungan paling mendesak di abad ke-21 yang memberikan dampak langsung pada stabilitas ekosistem pertanian.", None),
        (" Peningkatan suhu permukaan laut serta pergeseran pola curah hujan musiman telah memicu penurunan produktivitas lahan basah secara signifikan di berbagai sentra pangan pesisir.", ("sem", "sem")),
        (" Fenomena kenaikan muka air laut yang terus berlangsung mempercepat laju intrusi air asin ke dalam akuifer air tawar.", None),
    ],
    [
        ("Intrusi air laut mengakibatkan salinisasi tanah pertanian produktif yang menurunkan daya dukung lahan terhadap tanaman padi sawah.", ("lex", "lex")),
        (" Berdasarkan data empiris stasiun klimatologi lokal, frekuensi anomali cuaca ekstrem seperti banjir rob dan kekeringan berkepanjangan mengalami eskalasi frekuensi sebesar 34% dalam satu dekade terakhir.", None),
        (" Kondisi hidrometeorologis ini secara sistematis merusak infrastruktur irigasi primer dan sekunder yang menjadi urat nadi ketahanan pangan masyarakat pesisir.", ("sty", "sty")),
    ],
    [
        ("Oleh karena itu, diperlukan perumusan strategi adaptasi berbasis kearifan lokal yang dipadukan dengan pemanfaatan varietas tanaman toleran salinitas tinggi.", None),
        (" Pendekatan multisektoral yang melibatkan pemangku kebijakan, akademisi, dan kelompok tani lokal menjadi prasyarat mutlak demi menjamin keberlanjutan kedaulatan pangan.", ("sem", "sem")),
        (" Penguatan kapasitas kelembagaan desa dalam pengelolaan risiko bencana iklim harus diprioritaskan sebagai pilar ketahanan komunitas.", None),
    ],
    [
        ("Penelitian ini bertujuan untuk memetakan kerentanan spasial lahan sawah terdampak intrusi serta merumuskan model mitigasi adaptif terpadu.", None),
        (" Analisis risiko iklim dilakukan dengan menggabungkan proyeksi pemodelan sirkulasi atmosfer regional dengan data sosio-ekonomi rumah tangga petani.", None),
    ]
]

# Daftar sumber korpus rujukan (contoh buatan):
SOURCES_DATA = [
    ("Jurnal Agronomi Pesisir Vol. 14", "Dr. Ir. Suhendra, M.Si. (IPB)", "Tier 2 · Semantik", "24,8%", "4 kalimat", "orange"),
    ("Prosiding Simposium Ketahanan Iklim 2024", "Budi Santoso dkk. (UGM)", "Tier 1 · Leksikal", "18,2%", "3 kalimat", "red"),
    ("Model Hidrometeorologi Estuari Jawa", "Puslitbang Sumber Daya Air", "Tier 2 · Semantik", "11,5%", "2 kalimat", "orange"),
    ("Sintesis Literatur Perubahan Iklim AI", "Model Generator GPT-4", "Tier 3 · Stilometri", "8,4%", "1 kalimat", "yellow"),
]


def audit_header(export_state='idle'):
    """Header topnav + breadcrumb + judul naskah + aksi."""
    b = ''
    from vt_kit import topnav
    b += topnav(['Dashboard', 'Audit', 'Korpus', 'Billing', 'Admin'], 'Audit', 'Rizky Pratama', 'rizky@nusantara.ac.id', 'RP')
    
    b += text(48, 142, 'Workspace Audit  /  Laporan Naskah  /  #AUD-2026-8812', 13, 500, 'sub')
    b += text(48, 174, DOC_TITLE, 24, 600, 'ink', ls=-0.4)
    b += text(48, 200, DOC_META, 13.5, 400, 'sub')
    
    if export_state == 'loading':
        b += rect(1100, 150, 164, 48, 'field', 24)
        b += spinner(1126, 174, 8, 'primary', 2.2)
        b += text(1144, 179, 'Membuat PDF…', 14, 500, 'primaryInk')
    elif export_state == 'success':
        b += rect(1100, 150, 164, 48, 'field', 24)
        b += ico('check', 1124, 174, 'primaryInk', 1.8)
        b += text(1142, 179, 'PDF Terunduh', 14, 600, 'primaryInk')
    else:
        b += btn(1100, 150, 164, 48, 'Unduh PDF Resmi', 'primary', 14)

    b += rect(1276, 150, 116, 48, 'field', 24)
    b += text(1334, 179, 'Hapus', 14, 500, 'red', 'middle')
    
    b += hair(48, 222, W - 48, 222)
    return b


def pane_document(x, y, w, h, hl_filter=('lex', 'sem', 'sty'), show_hover_popover=False):
    """Panel Kiri (~60%): Naskah dengan anotasi highlight per kalimat."""
    b = card(x, y, w, h)
    
    b += text(x + 28, y + 42, 'Naskah Asli & Heatmap Deteksi', 18, 600, 'ink')
    b += text(x + 28, y + 64, 'Sorotan kalimat menunjukkan kecocokan dengan basis data referensi', 13, 400, 'sub')
    
    fx = x + w - 380
    b += text(fx - 44, y + 48, 'Filter:', 12.5, 600, 'sub')
    
    lex_on = 'lex' in hl_filter
    b += rect(fx, y + 28, 92, 34, 'redTint' if lex_on else 'field', 17)
    b += circle(fx + 14, y + 45, 4.5, 'red' if lex_on else 'placeholder')
    b += text(fx + 26, y + 50, 'Leksikal', 12.5, 600 if lex_on else 400, 'red' if lex_on else 'sub')
    
    sem_on = 'sem' in hl_filter
    b += rect(fx + 100, y + 28, 102, 34, 'orangeTint' if sem_on else 'field', 17)
    b += circle(fx + 114, y + 45, 4.5, 'orange' if sem_on else 'placeholder')
    b += text(fx + 126, y + 50, 'Semantik', 12.5, 600 if sem_on else 400, 'orange' if sem_on else 'sub')
    
    sty_on = 'sty' in hl_filter
    b += rect(fx + 210, y + 28, 106, 34, 'yellowTint' if sty_on else 'field', 17)
    b += circle(fx + 224, y + 45, 4.5, 'yellow' if sty_on else 'placeholder')
    b += text(fx + 236, y + 50, 'Stilometri', 12.5, 600 if sty_on else 400, 'yellow' if sty_on else 'sub')

    b += hair(x + 24, y + 80, x + w - 24, y + 80)
    
    ty = y + 120
    popover_anchor = None
    
    for p_idx, p in enumerate(PARAGRAFS):
        b += text(x + 28, ty, 'P%02d' % (p_idx + 1), 12, 600, 'placeholder')
        
        segs_to_draw = []
        for s_idx, (stext, tier) in enumerate(p):
            active_tier = tier if (tier and tier in hl_filter) else None
            segs_to_draw.append((stext, active_tier))
            
        b += rich(x + 64, ty, segs_to_draw[:2], size=14.5)
        
        # Simpan anchor untuk popover hover pada kalimat leksikal di Paragraf 2
        if p_idx == 1 and show_hover_popover:
            popover_anchor = (x + 64, ty)
            
        ty += 28
        if len(segs_to_draw) > 2:
            b += rich(x + 64, ty, segs_to_draw[2:], size=14.5)
            ty += 28
        ty += 16
        
    # Render Popover Hover mikro jika aktif
    if show_hover_popover and popover_anchor:
        px, py = popover_anchor[0] + 120, popover_anchor[1] - 46
        pw, ph = 320, 42
        b += rect(px, py, pw, ph, 'ink', 12, filt='sh-hero')
        b += circle(px + 18, py + 21, 4.5, 'red')
        b += text(px + 30, py + 25, 'Tier 1 Leksikal (91,4% match)', 12.5, 600, 'onDark')
        b += text(px + pw - 14, py + 25, 'Klik untuk rincian →', 12, 400, 'sub', 'end')
        
    return b


def pane_inspector_summary(x, y, w, h):
    """Panel Kanan (~40%): Tab Ringkasan (Gauge Komposit + 3 Skor Tier + Sintesis AI)."""
    b = card(x, y, w, h)
    
    tabs = ['Ringkasan', 'Sumber (4)', 'Perbandingan Diff']
    b += segmented(x + 24, y + 24, tabs, 0)
    b += hair(x + 24, y + 80, x + w - 24, y + 80)
    
    # 1. Gauge Komposit
    cx, cy = x + w // 2, y + 175
    b += segarc(cx, cy, 68, 88, 28, 0.386, sw=14)
    b += text(cx, cy - 10, '38,6%', 38, 600, 'ink', 'middle', ls=-0.8)
    b += text(cx, cy + 16, 'SKOR KEMIRIPAN KOMPOSIT', 12, 600, 'sub', 'middle', ls=0.8)
    
    b += rect(cx - 90, cy + 32, 180, 26, 'orangeTint', 13)
    b += text(cx, cy + 49, 'Kategori: Perlu Tinjauan', 12.5, 600, 'orange', 'middle')
    
    # 2. 3 Tier Pembobotan
    b += text(x + 28, y + 280, 'RINCIAN PEMBOBOTAN DETEKSI', 12, 600, 'sub', ls=1.0)
    
    tiers = [
        ('Tier 1 · Leksikal Verbatim', 'Rabin-Karp Winnowing (k=5, w=4)', '42,0%', '50%', 'red', 'redTint', 0.42),
        ('Tier 2 · Semantik Parafrasa', 'pgvector HNSW Cosine Similarity', '38,5%', '35%', 'orange', 'orangeTint', 0.385),
        ('Tier 3 · Stilometri AI', 'Analisis Burstiness & Perpleksitas', '15,2%', '15%', 'yellow', 'yellowTint', 0.152),
    ]
    
    for i, (t_name, t_sub, t_val, t_weight, t_col, t_tint, t_pct) in enumerate(tiers):
        ty = y + 306 + i * 78
        b += rect(x + 24, ty, w - 48, 68, 'field', 14)
        b += circle(x + 42, ty + 24, 5, t_col)
        b += text(x + 56, ty + 28, t_name, 14, 600, 'ink')
        b += text(x + 56, ty + 48, t_sub, 12, 400, 'sub')
        b += text(x + w - 44, ty + 28, t_val, 16, 600, t_col, 'end')
        b += text(x + w - 44, ty + 48, 'Bobot: ' + t_weight, 12, 500, 'sub', 'end')
        b += rect(x + 56, ty + 56, w - 120, 4, 'track', 2)
        b += rect(x + 56, ty + 56, max(6, (w - 120) * t_pct), 4, t_col, 2)
        
    # 3. AI Editorial Synthesis
    sy = y + 558
    b += rect(x + 24, sy, w - 48, 134, 'field', 16)
    b += circle(x + 46, sy + 30, 12, 'card')
    b += ico('doc', x + 46, sy + 30, 'primaryInk', 1.6)
    b += text(x + 68, sy + 35, 'Catatan Diagnostik Akademik', 14, 600, 'ink')
    
    b += text(x + 40, sy + 66, 'Naskah memiliki kemiripan semantik dominan pada bagian metodologi', 13, 400, 'ink')
    b += text(x + 40, sy + 88, 'dan deskripsi dampak intrusi pesisir. Ditemukan 4 naskah rujukan di korpus', 13, 400, 'ink')
    b += text(x + 40, sy + 110, 'yang memiliki kesesuaian struktur argumen di atas ambang batas 35%.', 13, 400, 'sub')
    
    return b


def pane_inspector_sources(x, y, w, h):
    """Panel Kanan (~40%): Tab Sumber Korpus."""
    b = card(x, y, w, h)
    
    tabs = ['Ringkasan', 'Sumber (4)', 'Perbandingan Diff']
    b += segmented(x + 24, y + 24, tabs, 1)
    b += hair(x + 24, y + 80, x + w - 24, y + 80)
    
    b += text(x + 28, y + 112, 'DAFTAR SUMBER RUJUKAN TERDETEKSI', 12, 600, 'sub', ls=1.0)
    b += text(x + w - 28, y + 112, 'Total 4 dokumen', 12.5, 400, 'sub', 'end')
    
    for i, (title, author, tier_lbl, score, count, tone) in enumerate(SOURCES_DATA):
        sy = y + 132 + i * 116
        b += rect(x + 24, sy, w - 48, 104, 'field', 14)
        
        # Penanda nomor urut
        b += circle(x + 46, sy + 28, 12, 'card')
        b += text(x + 46, sy + 33, str(i + 1), 12, 600, 'ink', 'middle')
        
        # Judul & Penulis
        b += text(x + 68, sy + 30, title, 14.5, 600, 'ink')
        b += text(x + 68, sy + 50, author, 12.5, 400, 'sub')
        
        # Baris bawah kartu sumber: Tier, Jumlah kalimat, Skor, Tombol Buka Diff
        b += circle(x + 72, sy + 76, 4, tone)
        b += text(x + 82, sy + 80, tier_lbl, 12, 500, 'sub')
        b += text(x + 230, sy + 80, count, 12, 400, 'sub')
        
        b += text(x + w - 130, sy + 80, score, 15, 600, tone, 'end')
        b += link(x + w - 44, sy + 80, 'Bandingkan →', 12.5, anchor='end')
        
    return b


def pane_inspector_diff(x, y, w, h):
    """Panel Kanan (~40%): Tab Perbandingan Diff Kalimat."""
    b = card(x, y, w, h)
    
    tabs = ['Ringkasan', 'Sumber (4)', 'Perbandingan Diff']
    b += segmented(x + 24, y + 24, tabs, 2)
    b += hair(x + 24, y + 80, x + w - 24, y + 80)
    
    b += text(x + 28, y + 112, 'PERBANDINGAN KALIMAT BERDAMPINGAN', 12, 600, 'sub', ls=1.0)
    b += text(x + w - 28, y + 112, 'Kalimat #04 · Tier 1', 12.5, 600, 'red', 'end')
    
    # Blok Kalimat Naskah Uji
    b += rect(x + 24, y + 132, w - 48, 180, 'field', 14)
    b += text(x + 40, y + 158, 'TEKS NASKAH MAHASISWA (PARAGRAF 2)', 12, 600, 'sub', ls=0.8)
    b += rect(x + 40, y + 172, w - 80, 84, 'redTint', 8)
    b += text(x + 52, y + 196, 'Intrusi air laut mengakibatkan salinisasi tanah pertanian produktif', 13.5, 500, 'ink')
    b += text(x + 52, y + 218, 'yang menurunkan daya dukung lahan terhadap tanaman padi sawah.', 13.5, 500, 'ink')
    b += text(x + 52, y + 242, 'Kecocokan leksikal verbatim: 91,4% (Winnowing k=5)', 12, 600, 'red')
    b += text(x + 40, y + 286, 'Metode: Rabin-Karp Hash Match pada substring 42 karakter', 12, 400, 'sub')
    
    # Ikon panah perbandingan di tengah
    cy_mid = y + 338
    b += hair(x + 48, cy_mid, x + w - 48, cy_mid)
    b += circle(x + w // 2, cy_mid, 16, 'card')
    b += ico('up', x + w // 2, cy_mid, 'sub', 1.6)
    
    # Blok Kalimat Sumber Asli Korpus
    b += rect(x + 24, y + 364, w - 48, 210, 'field', 14)
    b += text(x + 40, y + 390, 'SUMBER RUJUKAN ASLI (KORPUS #KRP-041)', 12, 600, 'sub', ls=0.8)
    b += text(x + 40, y + 412, 'Prosiding Simposium Ketahanan Iklim 2024 · UGM', 13.5, 600, 'ink')
    b += rect(x + 40, y + 426, w - 80, 84, 'card', 8)
    b += text(x + 52, y + 450, 'Intrusi air laut telah mengakibatkan salinisasi lahan pertanian produktif', 13.5, 500, 'ink')
    b += text(x + 52, y + 472, 'sehingga menurunkan daya dukung tanah terhadap budidaya padi sawah.', 13.5, 500, 'ink')
    b += text(x + 52, y + 496, 'Halaman 48 · Paragraf 3 · Penulis: Budi Santoso dkk.', 12, 400, 'sub')
    b += link(x + 40, y + 546, 'Lihat Dokumen Korpus Lengkap →', 13)
    
    # Tombol navigasi kalimat berikutnya di bawah
    b += btn(x + 24, y + 642, w - 48, 48, 'Lanjut ke Kalimat Cocok Berikutnya (2/4) →', 'secondary', 13.5)
    
    return b


def modal_sentence(x, y, w, h):
    """Modal klik kalimat: rincian kalimat naskah vs korpus."""
    # Overlay gelap transparan
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    # Kotak Dialog Modal
    mx, my, mw_box, mh_box = W // 2 - 320, 180, 640, 560
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    # Header Modal
    b += circle(mx + 42, my + 44, 14, 'redTint')
    b += circle(mx + 42, my + 44, 5, 'red')
    b += text(mx + 68, my + 42, 'Rincian Temuan Deteksi Kalimat #04', 18, 600, 'ink')
    b += text(mx + 68, my + 62, 'Terdeteksi pada Tier 1 (Leksikal Verbatim) dengan skor 91,4%', 13, 400, 'sub')
    
    # Tombol Tutup X
    b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round"><path d="M-6 -6L6 6M6 -6L-6 6"/></g>' % (mx + mw_box - 36, my + 44, C['sub'])
    b += hair(mx + 24, my + 82, mx + mw_box - 24, my + 82)
    
    # Isi Kalimat Naskah
    b += text(mx + 36, my + 116, 'TEKS PADA NASKAH MAHASISWA', 12, 600, 'sub', ls=0.8)
    b += rect(mx + 36, my + 128, mw_box - 72, 76, 'redTint', 10)
    b += text(mx + 50, my + 154, 'Intrusi air laut mengakibatkan salinisasi tanah pertanian produktif', 13.5, 500, 'ink')
    b += text(mx + 50, my + 176, 'yang menurunkan daya dukung lahan terhadap tanaman padi sawah.', 13.5, 500, 'ink')
    
    # Isi Kalimat Sumber Asli
    b += text(mx + 36, my + 236, 'SUMBER RUJUKAN ASLI TERDAFTAR DI KORPUS', 12, 600, 'sub', ls=0.8)
    b += rect(mx + 36, my + 248, mw_box - 72, 100, 'field', 10)
    b += text(mx + 50, my + 274, 'Prosiding Simposium Ketahanan Iklim 2024 · Universitas Gadjah Mada', 13, 600, 'ink')
    b += text(mx + 50, my + 296, '"Intrusi air laut telah mengakibatkan salinisasi lahan pertanian produktif', 13, 400, 'sub')
    b += text(mx + 50, my + 316, 'sehingga menurunkan daya dukung tanah terhadap budidaya padi sawah."', 13, 400, 'sub')
    
    # Parameter Algoritma
    b += rect(mx + 36, my + 368, mw_box - 72, 86, 'field', 10)
    b += text(mx + 50, my + 394, 'METRIK ALGORITMA PENILAIAN', 12, 600, 'sub', ls=0.8)
    b += text(mx + 50, my + 418, 'Algoritma: Rabin-Karp Winnowing (k=5, w=4) · Hash match 14 token', 12.5, 400, 'ink')
    b += text(mx + 50, my + 438, 'Ambang batas deteksi: 35% · Kontribusi bobot ke skor akhir: +12,4%', 12.5, 400, 'sub')
    
    # Tombol Aksi Bawah Modal
    b += btn(mx + mw_box - 164, my + mh_box - 64, 128, 44, 'Tutup Dialog', 'secondary', 13.5)
    b += link(mx + 36, my + mh_box - 36, 'Buka di Tab Perbandingan Diff →', 13.5)
    
    return b


def modal_delete(in_progress=False):
    """Dialog konfirmasi penghapusan permanen naskah (UU PDP)."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 270, 240, 540, 340
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += circle(mx + mw_box // 2, my + 60, 26, 'redTint')
    b += ico('doc', mx + mw_box // 2, my + 60, 'red', 2.0)
    
    if in_progress:
        b += text(mx + mw_box // 2, my + 124, 'Menghapus Naskah Permanen…', 19, 600, 'ink', 'middle')
        b += text(mx + mw_box // 2, my + 152, 'Memusnahkan berkas fisik storage, vektor embeddings, dan metadata.', 13.5, 400, 'sub', 'middle')
        b += spinner(mx + mw_box // 2, my + 210, 16, 'red', 3.0)
        b += text(mx + mw_box // 2, my + 256, 'Mohon tunggu beberapa detik sesuai hak UU PDP…', 12.5, 400, 'sub', 'middle')
    else:
        b += text(mx + mw_box // 2, my + 120, 'Hapus Naskah Secara Permanen?', 19, 600, 'ink', 'middle')
        b += text(mx + mw_box // 2, my + 150, 'Tindakan ini tidak dapat dibatalkan. Berkas dokumen naskah,', 13.5, 400, 'sub', 'middle')
        b += text(mx + mw_box // 2, my + 172, 'vektor pgvector, serta catatan audit akan dihapus seketika', 13.5, 400, 'sub', 'middle')
        b += text(mx + mw_box // 2, my + 194, 'sesuai ketentuan UU Perlindungan Data Pribadi (UU PDP No. 27/2022).', 13.5, 500, 'ink', 'middle')
        
        # Tombol konfirmasi merah & batal
        b += rect(mx + 48, my + 248, 210, 48, 'redTint', 24)
        b += text(mx + 153, my + 277, 'Ya, Hapus Permanen', 14, 600, 'red', 'middle')
        b += btn(mx + 282, my + 248, 210, 48, 'Batal Simpan Naskah', 'secondary', 14)
        
    return b


def build_skeleton():
    """State: audit-detail--loading-skeleton."""
    b = ''
    from vt_kit import topnav
    b += topnav(['Dashboard', 'Audit', 'Korpus', 'Billing', 'Admin'], 'Audit', 'Rizky Pratama', 'rizky@nusantara.ac.id', 'RP')
    
    # Shimmer breadcrumb
    b += rect(48, 134, 280, 14, 'track', 7)
    b += rect(48, 160, 520, 26, 'track', 13)
    b += rect(48, 194, 380, 14, 'track', 7)
    b += hair(48, 222, W - 48, 222)
    
    # Panel Kiri Skeleton
    b += card(48, 240, 780, 720)
    b += rect(76, 268, 240, 20, 'track', 10)
    b += rect(76, 296, 360, 14, 'track', 7)
    b += hair(72, 320, 804, 320)
    
    for row in range(12):
        y_sk = 350 + row * 28
        b += rect(76, y_sk, 40, 14, 'track', 4)
        b += rect(126, y_sk, 670, 14, 'field', 4)
        
    # Panel Kanan Skeleton
    b += card(848, 240, 544, 720)
    b += rect(872, 264, 320, 36, 'track', 18)
    b += circle(1120, 410, 80, 'track')
    b += rect(960, 530, 320, 20, 'track', 10)
    b += rect(872, 580, 496, 68, 'field', 14)
    b += rect(872, 660, 496, 68, 'field', 14)
    b += rect(872, 740, 496, 68, 'field', 14)
    
    return page('Memuat Laporan Audit - VeriText AI', 'Shimmer skeleton loader saat naskah sedang disiapkan.', W, 1020, b)


def build_404():
    """State: audit-detail--error-not-found-404."""
    b = ''
    from vt_kit import topnav
    b += topnav(['Dashboard', 'Audit', 'Korpus', 'Billing', 'Admin'], 'Audit', 'Rizky Pratama', 'rizky@nusantara.ac.id', 'RP')
    
    # Kotak Empty / 404 terpusat
    cx, cy = W // 2, 460
    b += card(cx - 320, cy - 180, 640, 380)
    
    b += circle(cx, cy - 80, 34, 'field')
    b += ico('doc', cx, cy - 80, 'sub', 2.2)
    
    b += text(cx, cy - 10, 'Laporan Audit Tidak Ditemukan', 22, 600, 'ink', 'middle')
    b += text(cx, cy + 20, 'Naskah dengan ID #AUD-2026-8812 tidak terdaftar pada sistem atau', 14, 400, 'sub', 'middle')
    b += text(cx, cy + 42, 'telah dihapus secara permanen sesuai batas retensi 30 hari UU PDP.', 14, 400, 'sub', 'middle')
    
    b += btn(cx - 150, cy + 90, 300, 48, 'Kembali ke Dashboard Utama', 'primary', 14)
    b += link(cx, cy + 164, 'Pusat Bantuan & Kebijakan Retensi →', 13, anchor='middle')
    
    return page('Laporan Tidak Ditemukan - VeriText AI', 'Halaman galat saat dokumen audit naskah tidak ditemukan.', W, 1020, b)


def build_all():
    """Membangun 13 layar keluarga detail laporan audit."""
    print("Membangun keluarga layar Detail Laporan Audit (laptop 1440 px)...")
    
    # 1. Desktop Split Pane Default
    svg1 = page(
        'Laporan Audit Naskah - VeriText AI',
        'Laporan inspeksi kemiripan naskah akademik split-pane 60/40.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720) + pane_inspector_summary(848, 240, 544, 720)
    )
    with open(os.path.join(OUT, 'audit-detail--desktop-split-pane.svg'), 'w') as f:
        f.write(svg1)

    # 2. Tab Ringkasan Aktif
    with open(os.path.join(OUT, 'audit-detail--tab-summary-active.svg'), 'w') as f:
        f.write(svg1)

    # 3. Tab Sumber Korpus Aktif
    svg3 = page(
        'Sumber Referensi Terdeteksi - VeriText AI',
        'Tab sumber referensi korpus yang cocok dengan kalimat naskah.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720) + pane_inspector_sources(848, 240, 544, 720)
    )
    with open(os.path.join(OUT, 'audit-detail--tab-sources-active.svg'), 'w') as f:
        f.write(svg3)

    # 4. Tab Perbandingan Diff Aktif
    svg4 = page(
        'Perbandingan Kalimat Diff - VeriText AI',
        'Tab perbandingan kalimat naskah dengan teks dokumen korpus asli berdampingan.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720) + pane_inspector_diff(848, 240, 544, 720)
    )
    with open(os.path.join(OUT, 'audit-detail--tab-diff-active.svg'), 'w') as f:
        f.write(svg4)

    # 5. Filter Tier Highlights (Hanya Semantik yang Aktif)
    svg5 = page(
        'Filter Sorotan Tier - VeriText AI',
        'Filter highlight dimatikan sebagian untuk meneliti kategori spesifik.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720, hl_filter=('sem',)) + pane_inspector_summary(848, 240, 544, 720)
    )
    with open(os.path.join(OUT, 'audit-detail--filter-tier-highlights.svg'), 'w') as f:
        f.write(svg5)

    # 6. Popover Hover Kalimat
    svg6 = page(
        'Tooltip Sorotan Kalimat - VeriText AI',
        'Popover mikro saat kursor diarahkan ke kalimat ber-highlight.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720, show_hover_popover=True) + pane_inspector_summary(848, 240, 544, 720)
    )
    with open(os.path.join(OUT, 'audit-detail--sentence-popover-hover.svg'), 'w') as f:
        f.write(svg6)

    # 7. Modal Klik Kalimat
    svg7 = page(
        'Detail Kalimat Terdeteksi - VeriText AI',
        'Dialog modal pop-up menampilkan rincian temuan deteksi kalimat naskah.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720) + pane_inspector_summary(848, 240, 544, 720) + modal_sentence(0, 0, W, 1020)
    )
    with open(os.path.join(OUT, 'audit-detail--sentence-modal-open.svg'), 'w') as f:
        f.write(svg7)

    # 8. Ekspor PDF Loading Spinner
    svg8 = page(
        'Membuat PDF Sertifikat - VeriText AI',
        'Indikator spinner loading saat mengompilasi berkas PDF sertifikat resmi.',
        W, 1020, audit_header('loading') + pane_document(48, 240, 780, 720) + pane_inspector_summary(848, 240, 544, 720)
    )
    with open(os.path.join(OUT, 'audit-detail--exporting-pdf-spinner.svg'), 'w') as f:
        f.write(svg8)

    # 9. Ekspor PDF Sukses
    svg9 = page(
        'Sertifikat PDF Berhasil Diunduh - VeriText AI',
        'Status berhasil saat sertifikat PDF telah diunduh.',
        W, 1020, audit_header('success') + pane_document(48, 240, 780, 720) + pane_inspector_summary(848, 240, 544, 720)
    )
    with open(os.path.join(OUT, 'audit-detail--export-pdf-success.svg'), 'w') as f:
        f.write(svg9)

    # 10. Dialog Hapus Naskah (UU PDP)
    svg10 = page(
        'Konfirmasi Hapus Naskah - VeriText AI',
        'Dialog modal konfirmasi penghapusan permanen sesuai hak UU PDP No. 27/2022.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720) + pane_inspector_summary(848, 240, 544, 720) + modal_delete(in_progress=False)
    )
    with open(os.path.join(OUT, 'audit-detail--delete-dialog-open.svg'), 'w') as f:
        f.write(svg10)

    # 11. Deleting In Progress
    svg11 = page(
        'Proses Penghapusan Naskah - VeriText AI',
        'State proses pemusnahan berkas fisik dan embeddings dari server.',
        W, 1020, audit_header('idle') + pane_document(48, 240, 780, 720) + pane_inspector_summary(848, 240, 544, 720) + modal_delete(in_progress=True)
    )
    with open(os.path.join(OUT, 'audit-detail--deleting-in-progress.svg'), 'w') as f:
        f.write(svg11)

    # 12. Loading Skeleton
    svg12 = build_skeleton()
    with open(os.path.join(OUT, 'audit-detail--loading-skeleton.svg'), 'w') as f:
        f.write(svg12)

    # 13. Error Not Found 404
    svg13 = build_404()
    with open(os.path.join(OUT, 'audit-detail--error-not-found-404.svg'), 'w') as f:
        f.write(svg13)

    print("Berhasil membangun 13 SVG keluarga Detail Laporan Audit di laptop/audit/.")


if __name__ == '__main__':
    build_all()
