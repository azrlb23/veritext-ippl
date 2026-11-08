"""Beranda VeriText mengikuti layout 'Landing Page.pdf' (11 hlm landscape) dengan gaya Boltshift.

Koordinat elemen diambil dari PDF (piksel 2x per halaman) lalu dipetakan ke kanvas 1440:
x -> x * S, y -> ((offset halaman + y) - 359) * S + 150. Jadi urutan dan jarak relatif antar elemen sama dengan PDF.
Jalankan: python3 build_landing.py  -> ../laptop/landing--default-idle.svg
"""
import math
import os
from vt_kit import C, HERE, W, text, rect, circle, hair, card, btn, ico, chevron, rich, brand, page, esc, tw, segarc, HL, mw

S = 0.855
OFF = [0]  # pergeseran vertikal blok (dipakai versi ringkas)
OUT = os.path.join(HERE, '..', 'laptop')


def X(x):
    return round(x * S, 1)


def Y(p, y):
    a = (p - 1) * 974 + (y - 86)
    return round((a - 359) * S + 150 + OFF[0], 1)


def L(v):
    return round(v * S, 1)


def T(p, x, y, s, size=15, weight=400, fill='ink', anchor='start', ls=None):
    return text(X(x), round(Y(p, y) + size * 0.35, 1), s, size, weight, fill, anchor, ls)


def BOX(p, x, y, w, h, fill='field', r=24, filt=None):
    return rect(X(x), Y(p, y), L(w), L(h), fill, r, filt=filt)


def CARD(p, x, y, w, h, r=32):
    return rect(X(x), Y(p, y), L(w), L(h), 'card', r, filt='sh')


def CARDY(p1, y1, p2, y2, x, w, r=40):
    return rect(X(x), Y(p1, y1), L(w), round(Y(p2, y2) - Y(p1, y1), 1), 'card', r, filt='sh')


def H(p, x, y, parts, size, anchor='start', weight=500, ls=None):
    inner = ''.join(('<tspan fill="%s">%s</tspan>' % (C['primary'], esc(s))) if acc else esc(s) for s, acc in parts)
    return '<text x="%s" y="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (
        X(x), round(Y(p, y) + size * 0.35, 1), size, weight, C['ink'], anchor, (' letter-spacing="%s"' % ls) if ls else '', inner)


def para(p, x, y, segs, size=14.5, anchor='start'):
    inner = ''
    for s in segs:
        t, k = (s, None) if isinstance(s, str) else s
        col = {'b': C['ink'], 'a': C['primaryInk'], None: C['sub']}[k]
        inner += '<tspan font-weight="%s" fill="%s">%s</tspan>' % (600 if k else 400, col, esc(t))
    return '<text x="%s" y="%s" font-size="%s" fill="%s" text-anchor="%s">%s</text>' % (X(x), round(Y(p, y) + size * 0.35, 1), size, C['ink'], anchor, inner)


def eyebrow(p, x, y, label, anchor='start'):
    """Label seksi: teks polos huruf kapital kecil, tanpa pil."""
    return T(p, x, y, label, 13, 600, 'sub', anchor, ls=1.2)


def ring(cx, cy, r, pct, sw=9):
    track = '<path d="M%s %sA%s %s 0 1 1 %s %sA%s %s 0 1 1 %s %s" fill="none" stroke="%s" stroke-width="%s"/>' % (
        cx - r, cy, r, r, cx + r, cy, r, r, cx - r, cy, C['track'], sw)
    if pct >= 0.999:
        val = track.replace(C['track'], C['primary'])
    else:
        a = 2 * math.pi * pct
        val = '<path d="M%s %sA%s %s 0 %d 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (
            cx, cy - r, r, r, 1 if pct > 0.5 else 0, cx + r * math.sin(a), cy - r * math.cos(a), C['primary'], sw)
    return track + val


def spark(pts, dot=True):
    """Garis halus (Catmull-Rom -> Bezier) + titik akhir."""
    d = 'M%s %s' % pts[0]
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += 'C%.1f %.1f %.1f %.1f %s %s' % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    s = '<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linecap="round"/>' % (d, C['ink'])
    if dot:
        s += circle(pts[-1][0], pts[-1][1], 3.5, 'ink')
    return s


def sp(p, pts):
    return [(X(x), Y(p, y)) for x, y in pts]


def seg_nav_hero():
    b = ''
    # ---------- navigasi (pil melayang di tengah, seperti di PDF) ----------
    nx, nw = 190, 1060
    b += rect(nx, 24, nw, 68, 'card', 34, filt='sh')
    b += '<text x="%s" y="65" font-size="20" font-weight="600" fill="%s">VeriText <tspan fill="%s">AI</tspan></text>' % (nx + 36, C['ink'], C['primary'])
    b += rect(nx + 206, 32, 118, 52, 'field', 26) + text(nx + 265, 63, 'Beranda', 15, 500, 'ink', 'middle')
    for lab, x in [('Dashboard', 346), ('Saldo Token', 466), ('Verifikasi QR', 596)]:
        b += text(nx + x, 63, lab, 15, 500, 'sub')
    b += rect(nx + 760, 32, 218, 52, 'field', 26) + circle(nx + 788, 58, 14, 'card') + text(nx + 788, 63, 'M', 13, 600, 'ink', 'middle')
    b += text(nx + 814, 63, 'Mochammad…', 15, 500, 'ink') + text(nx + 960, 63, '1T', 14, 600, 'primaryInk', 'end')
    b += text(nx + 1018, 63, 'Keluar', 15, 500, 'sub', 'middle')

    # ---------- 1. hero ----------
    b += CARD(1, 75, 445, 463, 240, 30)
    b += T(1, 102, 496, '3.503', 30, 600) + T(1, 102, 527, '2% vs minggu lalu', 13, 400, 'sub')
    b += hair(X(232), Y(1, 472), X(232), Y(1, 658)) + T(1, 258, 485, 'Kategori', 15, 600)
    for i, (k, v) in enumerate([('Skripsi', '1.373'), ('Jurnal', '930'), ('Tesis', '745'), ('Buku', '432'), ('Lainnya', '23')]):
        b += T(1, 258, 517 + i * 32, k, 14, 400, 'sub') + T(1, 511, 517 + i * 32, v, 14, 500, 'ink', 'end')
    for x, ch, on in [(102, 'J', 0), (119, 'S', 0), (133, 'M', 0), (149, 'S', 1)]:
        b += T(1, x, 648, ch, 12, 600 if on else 400, 'ink' if on else 'sub')
    b += CARD(1, 1178, 612, 430, 180, 30)
    b += T(1, 1211, 657, 'Audit selesai', 15, 500, 'primaryInk') + T(1, 1211, 705, '2,4rb', 38, 600) + T(1, 1211, 746, '↑ 5,5% vs minggu lalu', 13, 400, 'sub')
    b += ring(X(1525), Y(1, 702), L(48), 0.75, 9) + T(1, 1525, 692, '75%', 16, 600, 'ink', 'middle') + T(1, 1525, 712, 'aman', 12, 400, 'sub', 'middle')
    b += H(1, 842, 800, [('Audit naskah lebih cepat', 0)], 74, 'middle', 600, -2) + H(1, 842, 915, [('dan nol plagiarisme', 1)], 74, 'middle', 600, -2)
    for i, ln in enumerate(['VeriText AI adalah platform audit orisinalitas berbasis', 'metrik terukur yang mendukung pemeriksaan, pelaporan, dan', 'integritas akademik di seluruh kampus.']):
        b += text(720, round(Y(1, 1018) + 5.6 + i * 25, 1), ln, 16, 400, 'sub', 'middle')
    b += btn(X(636), round(Y(2, 173) - 26, 1), 168, 52, 'Mulai audit', 'primary', 15.5) + T(2, 948, 173, 'Lihat demo', 16, 500, 'ink', 'middle')
    b += CARD(2, 235, 217, 351, 220, 30)
    b += T(2, 261, 256, 'Skor orisinalitas', 14, 400, 'sub') + T(2, 261, 291, '84,8%', 30, 600) + T(2, 378, 296, 'naik dari bulan lalu', 12.5, 400, 'sub')
    b += hair(X(261), Y(2, 323), X(560), Y(2, 323))
    b += spark(sp(2, [(330, 372), (352, 368), (385, 356), (415, 349), (440, 348), (462, 357), (476, 350), (488, 341)]))
    for x, m, on in [(274, 'Agu', 0), (361, 'Sep', 0), (447, 'Okt', 0), (540, 'Nov', 1)]:
        b += T(2, x, 400, m, 12, 600 if on else 400, 'ink' if on else 'sub', 'middle')
    b += circle(X(164), Y(2, 326), L(24), 'card') + T(2, 164, 326, 'RP', 13, 600, 'ink', 'middle')
    b += '<path d="M%s %sH%s M%s %sL%s %sM%s %sL%s %s" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round"/>' % (
        X(193), Y(2, 326), X(226), X(218), Y(2, 316), X(226), Y(2, 326), X(218), Y(2, 336), X(226), Y(2, 326), C['sub'])
    b += rect(X(1056), Y(2, 376), L(464), L(60), 'card', 26, filt='sh') + T(2, 1082, 406, 'Tanyakan hasil audit…', 14, 400, 'placeholder')
    b += T(2, 1352, 406, '@', 16, 400, 'sub', 'middle')
    b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="1.7" stroke-linecap="round"><circle r="8"/><path d="M0 -4V0L3 2"/></g>' % (X(1382), Y(2, 406), C['sub'])
    b += T(2, 1432, 406, 'RP', 13, 600, 'primaryInk', 'middle')
    return b


def seg_canvas():
    b = ''
    # ---------- 2. kanvas produk ----------
    b += eyebrow(2, 842, 906, 'LIVE PRODUCT CANVAS', 'middle')
    b += H(2, 842, 980, [('Satu Kanvas Terpadu untuk ', 0), ('Seluruh Analisis', 1)], 46, 'middle', 500, -0.8)
    b += T(3, 842, 105, 'Semua artefak yang Anda lihat di beranda bermuara dalam ruang kerja interaktif — memadukan deteksi', 17, 400, 'sub', 'middle')
    b += T(3, 842, 141, 'leksikal, vektor semantik, dan narasi diagnosis AI.', 17, 400, 'sub', 'middle')
    b += CARDY(3, 220, 4, 585, 88, 1508, 44)
    for x in (137, 169, 201):
        b += circle(X(x), Y(3, 260), L(10), 'track')
    b += T(3, 419, 260, 'VeriText Academic', 15, 500) + T(3, 596, 260, '/', 15, 400, 'sub') + T(3, 612, 260, 'Workspace Audit', 15, 400, 'sub') + T(3, 776, 260, '/', 15, 400, 'sub') + T(3, 795, 260, 'Naskah-Skripsi-2026.pdf', 15, 500)
    b += T(3, 1290, 260, 'Audit Selesai', 13.5, 600, 'primaryInk', 'middle') + btn(X(1365), round(Y(3, 260) - 22, 1), 163, 44, 'Buka Workspace →', 'secondary', 14)
    b += hair(X(88), Y(3, 298), X(1596), Y(3, 298)) + hair(X(498), Y(3, 298), X(498), Y(4, 585))
    # sidebar
    b += BOX(3, 115, 325, 355, 72, 'field', 28) + circle(X(148), Y(3, 361), L(17), 'card') + T(3, 148, 361, 'V', 13, 600, 'ink', 'middle')
    b += T(3, 183, 352, 'Laboratorium AI', 16, 600) + T(3, 183, 375, 'Fakultas Teknik', 13, 400, 'sub') + chevron(X(446), Y(3, 361))
    b += T(3, 127, 450, 'MENU UTAMA', 12, 600, 'sub', ls=1.2)
    b += BOX(3, 115, 474, 355, 46, 'primaryTint', 20) + T(3, 169, 497, 'Ringkasan Audit', 15, 600, 'primaryInk')
    for y, lab, ic in [(549, 'Heatmap Interaktif', 'doc'), (600, 'Repositori Korpus', 'stack'), (651, 'Metrik pgvector HNSW', 'bars')]:
        b += T(3, 169, y, lab, 15, 400, 'sub') + ico(ic, X(142), Y(3, y), 'sub', 1.6)
    b += T(3, 127, 726, 'PROGRAM STUDI', 12, 600, 'sub', ls=1.2)
    for y, lab in [(769, 'Teknik Informatika'), (814, 'Sains Data'), (859, 'Sistem Informasi')]:
        b += circle(X(137), Y(3, y), L(6), 'track') + T(3, 156, y, lab, 15, 400, 'sub')
    b += BOX(4, 115, 448, 355, 110, 'field', 26) + T(4, 135, 482, 'UU PDP No. 27/2022', 14, 600) + T(4, 451, 482, 'Tersertifikasi', 13, 600, 'primaryInk', 'end')
    b += T(4, 135, 511, 'Enkripsi SHA-256 melindungi hak cipta', 13, 400, 'sub') + T(4, 135, 530, 'naskah mahasiswa secara penuh.', 13, 400, 'sub')
    # panel utama
    b += H(3, 544, 370, [('Laporan Diagnostik Naskah', 0)], 34, 'start', 500, -0.4)
    b += T(3, 544, 411, 'Pengujian naskah ilmiah berbasis korpus nasional • Waktu proses: 1.120 ms', 14, 400, 'sub')
    b += T(3, 1263, 384, 'UUID:', 14, 400, 'sub') + T(3, 1315, 384, 'f47ac10b', 14, 600) + T(3, 1436, 384, 'Unduh PDF', 14, 500, 'sub')
    b += hair(X(544), Y(3, 450), X(1550), Y(3, 450))
    b += BOX(3, 545, 490, 1004, 187, 'field', 30) + T(3, 593, 546, 'PERTANYAAN ANALISIS AI', 12.5, 600, 'primaryInk', ls=1)
    b += T(3, 578, 587, '"Bagaimana tingkat orisinalitas naskah dan distribusi parafrasa semantik', 20, 400) + T(3, 578, 627, 'pada bab metodologi riset?"', 20, 400)
    for x in (545, 889, 1233):
        b += BOX(3, x, 718, 316, 257, 'field', 28)
    b += T(3, 571, 767, '3.503', 28, 600) + T(3, 834, 778, 'k=5, w=4', 13, 500, 'sub', 'end') + T(3, 571, 801, 'Token Sidik Jari Leksikal', 13, 400, 'sub')
    b += hair(X(571), Y(3, 903), X(834), Y(3, 903)) + T(3, 571, 929, 'Rujukan Terdekat', 13, 400, 'sub') + T(3, 835, 929, 'Skripsi IF-2023', 13, 500, 'ink', 'end')
    b += T(3, 915, 778, 'SKOR', 12.5, 600, 'primaryInk', ls=1) + T(3, 915, 802, 'ORISINALITAS', 12.5, 600, 'primaryInk', ls=1) + T(3, 915, 849, '84,8%', 36, 600)
    b += T(3, 915, 891, 'Batas Aman (<20%', 13, 400, 'sub') + T(3, 915, 915, 'Kesamaan)', 13, 400, 'sub')
    b += ring(X(1127), Y(3, 846), L(45), 0.85, 9) + T(3, 1127, 840, '85%', 15, 600, 'ink', 'middle') + T(3, 1127, 858, 'Murni', 12, 400, 'sub', 'middle')
    b += T(3, 1259, 767, '46,2%', 28, 600) + T(3, 1487, 790, 'HNSW', 13, 600, 'primaryInk', 'end') + T(3, 1259, 801, 'Penelusuran Parafrasa', 13, 400, 'sub') + T(3, 1259, 825, 'Semantik', 13, 400, 'sub')
    b += spark(sp(3, [(1308, 890), (1340, 881), (1380, 867), (1410, 861), (1438, 863), (1456, 875), (1478, 860)]))
    b += hair(X(1259), Y(3, 914), X(1523), Y(3, 914))
    for x, lab, on in [(1259, 'Bab I', 0), (1319, 'Bab II', 0), (1389, 'Bab III', 0), (1467, 'Bab IV', 1)]:
        b += T(3, x, 937, lab, 12, 600 if on else 400, 'ink' if on else 'sub')
    b += BOX(4, 545, 87, 1004, 453, 'field', 30) + T(4, 577, 132, 'KESIMPULAN INTEGRITAS TINGKAT TINGGI (HIGH-LEVEL IMPACT)', 13, 600, 'ink', ls=0.6)
    b += para(4, 577, 167, ['Skor orisinalitas naskah mencapai ', ('84,8%', 'b'), '. Tingkat kesamaan komposit terdeteksi sebesar ', ('15,2%', 'b'), ' (10,5% leksikal'], 14.5)
    b += para(4, 577, 197, ['Tier 1, 3,8% parafrasa Tier 2, dan 0,9% anomali gaya tulisan). Naskah dinyatakan ', ('Layak Maju ke Sidang Ujian', 'a')], 14.5)
    b += para(4, 577, 227, ['karena masih di bawah batas toleransi maksimal 20%.'], 14.5)
    b += hair(X(577), Y(4, 269), X(1517), Y(4, 269)) + T(4, 577, 302, 'TEMUAN KUNCI HASIL KOMPARASI (KEY FINDINGS)', 13, 600, 'ink', ls=0.6)
    for y, lead, r1, r2 in [(340, 'Kecocokan Leksikal Langsung: ', 'Ditemukan 12 penggalan kalimat verbatim yang identik dengan repositori', 'skripsi internal 2023 pada paragraf definisi landasan teori.'),
                            (404, 'Parafrasa Semantik Cerdas: ', 'Algoritma pgvector mendeteksi 4 kalimat dengan susunan kalimat diubah dan', 'sinonim digunakan, namun jarak kosinus semantik tetap sangat dekat (≥ 0.82).'),
                            (468, 'Pola Gaya Bahasa Manusia: ', 'Analisis varians panjang kalimat (Burstiness = 0.42) dan kekayaan kosakata (TTR =', '0.68) memastikan draf ditulis oleh manusia secara autentik.')]:
        b += para(4, 599, y, [(lead, 'b'), r1], 14.5) + para(4, 599, y + 26, [r2], 14.5)
    return b


def seg_inspect():
    b = ''
    # ---------- 3. inspeksi dokumen ----------
    b += eyebrow(5, 88, 146, 'INSPEKSI DOKUMEN REAL-TIME')
    b += H(5, 88, 215, [('Cara Kerja Engine ', 0), ('Mendiagnosis', 1)], 46, 'start', 500, -0.8) + H(5, 88, 277, [('Naskah', 1)], 46, 'start', 500, -0.8)
    b += T(5, 88, 339, 'Pilih salah satu tingkat pengujian untuk melihat bagaimana sistem menandai kalimat', 17, 400, 'sub') + T(5, 88, 371, 'secara transparan bersama bukti pembandingnya.', 17, 400, 'sub')
    b += BOX(5, 945, 293, 651, 92, 'field', 40) + BOX(5, 953, 300, 215, 78, 'card', 34, 'sh-sm')
    for cx_, l1, l2, on in [(1060, 'Tier 1: Hashing', 'Leksikal', 1), (1285, 'Tier 2: Semantik', 'Dense', 0), (1495, 'Tier 3:', 'Stilometri AI', 0)]:
        b += T(5, cx_, 326, l1, 14.5, 600 if on else 500, 'ink' if on else 'sub', 'middle') + T(5, cx_, 352, l2, 14.5, 600 if on else 500, 'ink' if on else 'sub', 'middle')
    b += hair(X(88), Y(5, 425), X(1596), Y(5, 425))
    b += rect(0, Y(5, 477), W, round(Y(6, 311) - Y(5, 477), 1), 'card', 0)
    b += T(5, 127, 513, 'Naskah Uji vs Repositori Korpus', 15, 500) + circle(X(415), Y(5, 513), L(4), 'track') + T(5, 462, 513, 'Salin-Tempel Langsung', 15, 500)
    b += para(5, 1557, 513, ['Algoritma: ', ('Rabin-Karp Rolling Hash', 'b')], 13.5, 'end')
    b += hair(0, Y(5, 548), W, Y(5, 548)) + hair(X(968), Y(5, 548), X(968), Y(6, 311))
    b += T(5, 141, 613, 'FRAGMEN NASKAH DOKUMEN MAHASISWA', 12.5, 600, 'sub', ls=1) + T(5, 916, 613, 'Bab II • Tinjauan Pustaka', 13, 400, 'sub', 'end')
    b += BOX(5, 141, 658, 775, 271, 'field', 34)
    ty = lambda y: round(Y(5, y) + 7, 1)
    b += rich(X(180), ty(718), ['Dalam pengujian ini terbukti bahwa ', ('"algoritma Winnowing', 'lex')], 19, 0.5, 'sub')
    b += rich(X(180), ty(756), [('mereduksi jumlah fingerprint teks dengan memilih nilai hash', 'lex')], 19, 0.5, 'sub')
    b += rich(X(180), ty(794), [('minimum dalam jendela berukuran konstan."', 'lex'), ' Metode ini'], 19, 0.5, 'sub')
    b += rich(X(180), ty(832), ['secara konsisten mempertahankan ketahanan terhadap'], 19, 0.5, 'sub')
    b += rich(X(180), ty(871), ['transposisi kata.'], 19, 0.5, 'sub')
    b += BOX(5, 141, 962, 775, 142, 'field', 34) + circle(X(186), Y(5, 1003), L(11), 'primaryTint') + T(5, 186, 1003, '!', 13, 700, 'primaryInk', 'middle')
    b += T(5, 225, 1002, 'Catatan Hasil Diagnosis:', 16, 600) + T(5, 225, 1033, '100% kecocokan n-gram leksikal terdeteksi tanpa perubahan token atau', 13.5, 400, 'sub') + T(5, 225, 1064, 'urutan kata.', 13.5, 400, 'sub')
    b += T(5, 1020, 617, 'RUJUKAN PEMBANDING KORPUS', 12.5, 600, 'sub', ls=1) + T(5, 1544, 617, '100% Kecocokan', 13.5, 600, 'red', 'end')
    b += BOX(5, 1021, 668, 523, 246, 'field', 34) + T(5, 1054, 713, 'Skripsi Mahasiswa IF-2023 #DOC-0941', 14.5, 600) + T(5, 1054, 751, 'Repositori Tugas Akhir Informatika', 13, 400, 'sub')
    b += hair(X(1054), Y(5, 777), X(1510), Y(5, 777))
    for i, l in enumerate(['"algoritma Winnowing mereduksi jumlah fingerprint', 'teks dengan memilih nilai hash minimum dalam jendela', 'berukuran konstan."']):
        b += T(5, 1054, 806 + i * 30.5, l, 14, 400, 'ink')
    b += T(5, 1020, 970, 'Metrik Nilai', 14, 400, 'sub') + T(5, 1543, 970, 'k=5, w=4 (Hash Identik)', 14, 600, 'ink', 'end') + hair(X(1020), Y(5, 993), X(1543), Y(5, 993))
    b += T(5, 1020, 1029, 'Algoritma Inti', 14, 400, 'sub') + T(5, 1543, 1029, 'Rabin-Karp Rolling Hash', 14, 600, 'ink', 'end')
    b += T(6, 1020, 113, 'Bobot Komposit', 14, 400, 'sub') + T(6, 1543, 113, '50%', 15, 600, 'ink', 'end') + hair(X(1020), Y(6, 175), X(1543), Y(6, 175))
    b += T(6, 1282, 230, 'Coba Uji Naskah Lengkap di Workspace →', 15, 500, 'sub', 'middle')
    return b


def seg_arch():
    b = ''
    # ---------- 4. arsitektur 4-tier ----------
    b += eyebrow(6, 842, 590, 'ARSITEKTUR DETEKSI 4-TIER', 'middle')
    b += H(6, 842, 665, [('Tiga lapis kecerdasan untuk satu ', 0), ('kepastian', 1)], 46, 'middle', 500, -0.8) + H(6, 842, 728, [('integritas', 1)], 46, 'middle', 500, -0.8)
    b += T(6, 842, 797, 'Dirancang khusus untuk membedakan antara salin-tempel langsung, parafrasa cerdas berbasis sinonim, dan', 17, 400, 'sub', 'middle')
    b += T(6, 842, 832, 'sintesis otomatis model bahasa AI.', 17, 400, 'sub', 'middle')
    b += CARDY(6, 912, 7, 592, 88, 867, 40) + CARDY(6, 912, 7, 592, 987, 609, 40)
    b += T(6, 156, 980, 'SINERGI DUA MESIN', 12.5, 600, 'primaryInk', ls=1) + T(6, 355, 980, '• Tier 1 + Tier 2', 13, 400, 'sub')
    b += H(7, 141, 113, [('Mengapa satu algoritma saja tidak pernah', 0)], 31, 'start', 500, -0.4) + H(7, 141, 166, [('cukup?', 0)], 31, 'start', 500, -0.4)
    b += para(7, 141, 227, ['Pemeriksa plagiarisme konvensional hanya mengandalkan pencocokan teks'], 15.5) + para(7, 141, 259, ['langsung (*string matching*), sehingga mudah dikelabui oleh sinonim dan'], 15.5)
    b += para(7, 141, 291, ['parafrasa. VeriText AI menggabungkan ', ('Winnowing hash', 'b'), ' berkecepatan tinggi'], 15.5) + para(7, 141, 323, ['dengan ', ('penalaran semantik dense 384D', 'b'), ' melalui pgvector.'], 15.5)
    b += hair(X(141), Y(7, 392), X(902), Y(7, 392)) + hair(X(521), Y(7, 418), X(521), Y(7, 540))
    for x, t1, t2, tone, d1, d2 in [(141, 'Winnowing Hashing', '100% Identik', 'red', 'Mendeteksi salin-tempel langsung', 'kalimat demi kalimat tanpa distorsi.'),
                                    (551, 'pgvector HNSW', 'Semantik ≥ 0.75', 'orange', 'Menangkap parafrasa pintar dan sinonim', 'dalam ruang vektor dense.')]:
        b += T(7, x, 440, t1, 15, 600) + T(7, x + 351, 442, t2, 12.5, 600, tone, 'end') + T(7, x, 484, d1, 13.5, 400, 'sub') + T(7, x, 506, d2, 13.5, 400, 'sub')
    b += T(6, 1040, 982, 'FORMULA AGREGASI', 12.5, 600, 'sub', ls=1) + T(6, 1544, 982, '< 1.500 ms Latensi', 14, 600, 'primaryInk', 'end')
    b += T(7, 1040, 99, 'Formula Pembobotan Komposit', 14, 400, 'sub') + H(7, 1040, 150, [('0,50 T1 + 0,35 T2 + 0,15 T3', 0)], 30, 'start', 500, -0.4)
    b += hair(X(1040), Y(7, 423), X(1544), Y(7, 423))
    for y, lab, v in [(449, 'Tier 1: Hashing Leksikal', '50%'), (488, 'Tier 2: Parafrasa Semantik', '35%'), (526, 'Tier 3: Stilometri AI', '15%')]:
        b += T(7, 1065, y, lab, 14, 400, 'sub') + T(7, 1544, y, v, 14, 600, 'ink', 'end')
    tiers = [(88, 'TIER 1 • LEKSIKAL', 'red', 'k=5, w=4', 'Winnowing Fingerprinting',
              ['Algoritma Rabin-Karp 64-bit membentuk', 'jendela geser (sliding window) untuk', 'mendeteksi penjiplakan salin-tempel langsung', 'dengan efisiensi memori optimal.'], 'Kompleksitas: ', 'O(n)', 'Latensi <10 ms'),
             (601, 'TIER 2 • SEMANTIK', 'orange', '384 Dimensi', 'pgvector HNSW Cosine',
              ['Memproyeksikan makna naskah ke ruang', 'vektor dense (MiniLM-L12-v2) untuk', 'mengungkap parafrasa cerdas dan', 'restrukturisasi kalimat pasif-aktif.'], 'Indeks Vektor: ', 'HNSW (m=16)', 'Sim ≥ 0.75'),
             (1115, 'TIER 3 • STILOMETRI', 'yellow', 'Burstiness', 'Pola Sintaksis Model LLM',
              ['Mengevaluasi varians panjang kalimat dan', 'kekayaan leksikal (Type-Token Ratio) untuk', 'membedakan ritme tulisan manusia asli dengan', 'teks robotik AI.'], 'Metrik: ', 'TTR & Varians', 'Anomali < 0.20')]
    for x, tag, tone, side, title, desc, f1, f2, f3 in tiers:
        b += CARD(7, x, 625, 481, 386, 40) + T(7, x + 40, 681, tag, 12.5, 600, tone, ls=1) + T(7, x + 441, 681, side, 13, 400, 'sub', 'end')
        b += H(7, x + 40, 746, [(title, 0)], 27, 'start', 500, -0.3)
        for i, d in enumerate(desc):
            b += T(7, x + 40, 793 + i * 30.7, d, 14.5, 400, 'sub')
        b += hair(X(x + 40), Y(7, 925), X(x + 441), Y(7, 925)) + para(7, x + 40, 958, [f1, (f2, 'b')], 14) + T(7, x + 441, 958, f3, 14, 600, 'ink', 'end')
    return b


def seg_trust(link=True):
    b = ''
    # ---------- 5. kepercayaan ----------
    b += hair(0, Y(8, 87), W, Y(8, 87))
    b += T(8, 88, 186, 'MENGAPA INSTITUSI MEMILIH VERITEXT', 13, 600, 'sub', ls=1)
    b += H(8, 88, 244, [('Integritas karya ilmiah tanpa kompromi', 0)], 40, 'start', 600, -0.6) + H(8, 88, 302, [('privasi data.', 1)], 40, 'start', 600, -0.6)
    b += T(8, 119, 403, 'Verifikasi Sertifikat QR →', 16, 600) + T(8, 395, 403, 'Bank Korpus Riset →', 16, 500, 'sub') + hair(X(88), Y(8, 472), X(946), Y(8, 472))
    b += T(8, 88, 524, 'KEPATUHAN & AKREDITASI NASIONAL', 12.5, 600, 'sub', ls=1)
    gx, gy, gw = X(88), Y(8, 556), L(858)
    tw_ = round((gw - 16) / 2, 1)
    for i, (nm, cap) in enumerate([('UU PDP 27/2022', 'Perlindungan Data Pribadi'), ('SINTA Kemdikbud', 'Indeks ilmiah nasional'),
                                   ('Perpustakaan Nasional', 'Repositori karya ilmiah'), ('Telkom University', 'Universitas')]):
        tx, ty = gx + (i % 2) * (tw_ + 16), gy + (i // 2) * 80
        b += rect(tx, ty, tw_, 66, 'card', 22, filt='sh')
        b += text(tx + 26, ty + 29, nm, 15, 600, 'ink') + text(tx + 26, ty + 49, cap, 12.5, 400, 'sub')
    b += CARD(8, 999, 253, 597, 341, 40) + T(8, 1054, 307, 'Studi Kasus 2026', 13, 600, 'primaryInk') + T(8, 1557, 308, 'Institut Riset', 13, 400, 'sub', 'end')
    for i, l in enumerate(['"VeriText AI menghemat 85% waktu penelaahan dokumen', 'skripsi kami. Pemeriksaan leksikal dan semantik dilakukan', 'dalam 1,2 detik dengan jaminan hak privasi mahasiswa sesuai', 'UU PDP."']):
        b += T(8, 1038, 363 + i * 31, l, 15, 400, 'ink')
    b += hair(X(1038), Y(8, 497), X(1557), Y(8, 497)) + circle(X(1060), Y(8, 532), L(18), 'field') + T(8, 1060, 532, 'Dr', 13, 600, 'ink', 'middle')
    b += T(8, 1102, 523, 'Dr. Budi Santoso, M.Kom.', 15, 600) + T(8, 1102, 544, 'Ketua Komite Integritas Akademik', 13, 400, 'sub')
    if link:
        b += T(8, 744, 987, 'Engine Hybrid 4-Tier >', 16, 500, 'sub')
    return b


def seg_cta(columns=True):
    b = ''
    # ---------- 6. CTA ----------
    b += H(9, 842, 160, [('Deteksi esensi, bukan ', 0), ('sekadar kata', 1)], 72, 'middle', 500, -2)
    b += T(9, 842, 291, 'Model pembanding semantik dense 384-dimensi dan winnowing hash', 19, 400, 'sub', 'middle') + T(9, 842, 334, 'kriptografis untuk integritas karya ilmiah tanpa kompromi.', 19, 400, 'sub', 'middle')
    b += btn(X(664), Y(9, 424), L(356), L(69), 'Buka Workspace Audit →', 'surface', 16)
    if columns:
        b += T(9, 842, 688, 'STANDAR KEPATUHAN AKADEMIK & KRIPTOGRAFI INSTITUSIONAL', 12.5, 600, 'sub', 'middle', ls=1.2)
        for x, t, d1, d2 in [(114, 'UU PDP No. 27/2022', 'Perlindungan privasi naskah tanpa', 'pelatihan model pihak ketiga'), (498, 'SHA-256 Hash', 'Stempel kriptografis bukti keaslian', 'sertifikat publik QR'),
                             (882, 'pgvector HNSW', 'Indeks dense 384-dimensi untuk', 'penalaran semantik kosinus'), (1265, 'Celery & Redis', 'Antrean asynchronous terdistribusi', 'dengan throughput tinggi')]:
            b += T(9, x, 779, t, 15, 600) + T(9, x, 809, d1, 13, 400, 'sub') + T(9, x, 830, d2, 13, 400, 'sub')
    return b


def seg_compl():
    b = ''
    # ---------- 7. kepatuhan ----------
    b += rect(0, Y(10, 277), W, round(Y(11, 278) - Y(10, 277), 1), 'card', 0)
    b += eyebrow(10, 153, 364, 'STANDAR KEPATUHAN')
    b += H(10, 153, 434, [('Kepatuhan Privasi Dokumen & ', 0), ('Standar Akademik Nasional', 1)], 40, 'start', 500, -0.6)
    for i, l in enumerate(['VeriText AI mengimplementasikan Clean Architecture dengan pemisahan domain logic yang ketat, kepatuhan penuh', 'terhadap Undang-Undang Perlindungan Data Pribadi (UU PDP No. 27/2022), enkripsi SHA-256 untuk sidik jari naskah, dan', 'sertifikat QR kriptografis yang dapat diverifikasi publik tanpa kebocoran data sensitif.']):
        b += T(10, 153, 500 + i * 35.5, l, 16.5, 400, 'sub')
    for x, big, t, ds in [(153, '< 1.500 ms', 'Latensi Query pgvector', ['Pencarian kemiripan vektor HNSW', 'berkecepatan tinggi dengan metrik jarak', 'kosinus.']),
                          (623, '100%', 'Kepatuhan UU PDP No. 27/2022', ['Jaminan hak penghapusan permanen', 'dokumen naskah (Right to Erasure) dari', 'korpus.']),
                          (1093, 'UUID v4', 'Sertifikat Kriptografis', ['Verifikasi publik instan via scan QR code', 'tanpa mewajibkan autentikasi akun.'])]:
        b += BOX(10, x, 651, 438, 279, 'field', 34) + T(10, x + 40, 720, big, 36, 600, 'primaryInk' if big == '100%' else 'ink') + T(10, x + 40, 774, t, 15, 600)
        for i, d in enumerate(ds):
            b += T(10, x + 40, 816 + i * 30.5, d, 14, 400, 'sub')
    b += hair(X(153), Y(10, 983), X(1531), Y(10, 983))
    for x, t, ds in [(153, 'CLEAN ARCHITECTURE', ['Pemisahan lapis Domain,', 'Application, dan Infrastructure yang', 'modular & testable.']), (504, 'ENKRIPSI SHA-256', ['Sidik jari dokumen dianonimisasi', 'dengan hash satu arah tanpa', 'kompromi integritas data.']),
                     (854, 'ASYNC WORKERS', ['Celery queue didukung Redis', 'broker untuk pemrosesan naskah', 'paralel non-blocking.']), (1204, 'STANDAR DIKTI', ['Selaras dengan pedoman', 'integritas akademik dan etika', 'publikasi ilmiah nasional.'])]:
        b += BOX(10, x, 1022, 327, 165, 'field', 30) + T(10, x + 27, 1060, t, 13, 600, 'ink', ls=0.8)
        for i, d in enumerate(ds):
            b += T(10, x + 27, 1097 + i * 25.5, d, 13.5, 400, 'sub')
    return b


def seg_footer():
    b = ''
    # ---------- 8. footer ----------
    b += hair(0, Y(11, 537), W, Y(11, 537))
    b += brand(X(88), round(Y(11, 637) + 8, 1), 22)
    for i, l in enumerate(['Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur Hybrid Lexical &', 'Semantic AI Engine dengan Pipa Pemrosesan 4-Tier untuk Mata Kuliah', 'Implementasi Perangkat Lunak (IPPL).']):
        b += T(11, 88, 693 + i * 31, l, 14.5, 400, 'sub')
    b += para(11, 88, 800, ['Kepatuhan Privasi Dokumen: ', ('UU Perlindungan Data Pribadi (UU PDP) No. 27/2022', 'b')], 14.5)
    for x, head, items in [(1258, 'TAUTAN SINGKAT', ['Dashboard Pengujian', 'Repositori Korpus', 'Paket Kuota Token', 'Verifikasi Sertifikat'])]:
        b += T(11, x, 626, head, 14, 600, 'ink', ls=0.8)
        for i, it in enumerate(items):
            b += T(11, x, 672 + i * 38.3, it, 15, 400, 'sub')
    b += hair(X(88), Y(11, 903), X(1596), Y(11, 903))
    b += T(11, 88, 955, '© 2026 Tim Pengembang VeriText AI. Hak Cipta Dilindungi Undang-Undang.', 13, 400, 'sub')
    return b


def build():
    b = seg_nav_hero() + seg_canvas() + seg_inspect() + seg_arch() + seg_trust() + seg_cta() + seg_compl() + seg_footer()
    height = int(Y(11, 955) + 110)
    return page('VeriText AI – Beranda (layout PDF)', 'Beranda publik mengikuti layout Landing Page.pdf: hero, kanvas produk, inspeksi dokumen, arsitektur 4-tier, kepercayaan, CTA, kepatuhan, dan footer.', W, height, b)


# ---------------- versi ringkas (disetujui 2026-11-03) ----------------
def Ha(x, y, parts, size, anchor='start', weight=500, ls=None):
    inner = ''.join(('<tspan fill="%s">%s</tspan>' % (C['primary'], esc(t))) if acc else esc(t) for t, acc in parts)
    return '<text x="%s" y="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (
        x, round(y + size * 0.35, 1), size, weight, C['ink'], anchor, (' letter-spacing="%s"' % ls) if ls else '', inner)


def abs_eyebrow(x, y, label, anchor='start'):
    return text(x, y, label, 13, 600, 'sub', anchor, ls=1.2)


def place(p, ytop, target):
    OFF[0] = 0
    OFF[0] = round(target - Y(p, ytop), 1)


def seg_report(y0):
    """Satu laporan: gabungan 'Live Product Canvas' dan inspeksi dokumen, dengan highlight ketiga tier."""
    b = abs_eyebrow(720, y0 - 238, 'LAPORAN DIAGNOSTIK', 'middle')
    b += Ha(720, y0 - 190, [('Satu laporan untuk', 0)], 46, 'middle', 600, -0.8) + Ha(720, y0 - 136, [('seluruh analisis', 1)], 46, 'middle', 600, -0.8)
    b += text(720, y0 - 82, 'Deteksi leksikal, semantik, dan gaya penulisan dirangkum dalam', 16, 400, 'sub', 'middle')
    b += text(720, y0 - 56, 'satu laporan yang bisa ditelusuri sampai ke kalimat dan sumbernya.', 16, 400, 'sub', 'middle')
    wx, ww, wh = 75, 1290, 780
    b += rect(wx, y0, ww, wh, 'card', 40, filt='sh')
    for x in (112, 138, 164):
        b += circle(x, y0 + 33, 8, 'track')
    b += text(455, y0 + 38, 'VeriText Academic', 15, 500) + text(603, y0 + 38, '/', 15, 400, 'sub') + text(618, y0 + 38, 'Workspace Audit', 15, 400, 'sub')
    b += text(748, y0 + 38, '/', 15, 400, 'sub') + text(763, y0 + 38, 'Naskah-Skripsi-2026.pdf', 15, 500)
    b += text(1110, y0 + 38, 'Audit Selesai', 13.5, 600, 'primaryInk', 'middle') + btn(1180, y0 + 11, 163, 44, 'Buka Workspace →', 'secondary', 14)
    b += hair(wx, y0 + 66, wx + ww, y0 + 66)
    # kolom kiri: naskah dengan highlight tiga tier
    b += Ha(115, y0 + 118, [('Laporan Diagnostik Naskah', 0)], 30, 'start', 500, -0.4)
    b += text(115, y0 + 150, 'Pengujian naskah ilmiah berbasis korpus nasional • Waktu proses: 1.120 ms', 14, 400, 'sub')
    b += rect(115, y0 + 178, 640, 262, 'field', 30) + text(143, y0 + 212, 'FRAGMEN NASKAH • BAB II TINJAUAN PUSTAKA', 12.5, 600, 'sub', ls=1)
    lines = [['Perubahan iklim global merupakan ', ('tantangan terbesar yang dihadapi', 'lex')],
             [('umat manusia', 'lex'), ' pada abad ke-21 karena berdampak'],
             ['langsung pada ketahanan pangan, ', ('kestabilan ekonomi negara', 'sem')],
             [('berkembang', 'sem'), '. Dalam konteks ini, ', ('penting dicatat bahwa', 'sty')],
             ['mitigasi harus dilakukan secara terkoordinasi.']]
    for i, l in enumerate(lines):
        b += rich(143, y0 + 258 + i * 36, l, 17, 0.5, 'sub')
    for i, (hl, lab) in enumerate([('lex', 'Salin-tempel'), ('sem', 'Parafrasa'), ('sty', 'Anomali AI')]):
        tint, line = HL[hl]
        lx = 143 + i * 150
        b += rect(lx, y0 + 470, 14, 14, tint, 3) + rect(lx, y0 + 482, 14, 2, line) + text(lx + 22, y0 + 483, lab, 13, 400, 'sub')
    # kolom kanan: skor + rincian tier
    b += text(800, y0 + 120, 'SKOR ORISINALITAS', 12.5, 600, 'primaryInk', ls=1) + text(800, y0 + 184, '84,8%', 56, 600, 'ink', ls=-1.5)
    b += text(800, y0 + 214, 'Batas aman (<20% kesamaan)', 13.5, 400, 'sub') + segarc(1230, y0 + 222, 62, 108, 12, 0.848)
    for i, (nm, tone, bobot, v) in enumerate([('Tier 1 · Leksikal', 'red', 'bobot 50%', '10,5%'), ('Tier 2 · Semantik', 'orange', 'bobot 35%', '3,8%'), ('Tier 3 · Stilometri', 'yellow', 'bobot 15%', '0,9%')]):
        y = y0 + 300 + i * 52
        b += hair(800, y - 26, 1325, y - 26) + text(800, y + 5, nm, 14.5, 600, tone) + text(1010, y + 5, bobot, 13.5, 400, 'sub') + text(1325, y + 5, v, 15, 600, 'ink', 'end')
    b += hair(800, y0 + 430, 1325, y0 + 430) + text(800, y0 + 462, 'Kesamaan komposit', 14.5, 500, 'sub') + text(1325, y0 + 462, '15,2%', 16, 700, 'ink', 'end')
    # kesimpulan + temuan kunci
    b += rect(115, y0 + 508, 1210, 228, 'field', 30) + text(147, y0 + 548, 'KESIMPULAN INTEGRITAS', 12.5, 600, 'ink', ls=1)
    for i, segs in enumerate([['Skor orisinalitas naskah mencapai ', ('84,8%', 'b'), '. Tingkat kesamaan komposit'], ['terdeteksi sebesar ', ('15,2%', 'b'), ' (10,5% leksikal, 3,8% parafrasa,'],
                              ['0,9% anomali gaya tulisan). Naskah dinyatakan'], [('Layak Maju ke Sidang Ujian', 'a'), ' karena masih di bawah'], ['batas toleransi maksimal 20%.']]):
        inner = ''.join('<tspan font-weight="%s" fill="%s">%s</tspan>' % (600 if isinstance(t, tuple) else 400, C[{'b': 'ink', 'a': 'primaryInk'}[t[1]]] if isinstance(t, tuple) else C['sub'], esc(t[0] if isinstance(t, tuple) else t)) for t in segs)
        b += '<text x="147" y="%s" font-size="15" fill="%s">%s</text>' % (y0 + 584 + i * 25, C['ink'], inner)
    b += hair(740, y0 + 540, 740, y0 + 706) + text(776, y0 + 548, 'TEMUAN KUNCI', 12.5, 600, 'ink', ls=1)
    for i, (lead, d1, d2) in enumerate([('Kecocokan leksikal langsung', '12 penggalan kalimat identik dengan', 'repositori skripsi internal 2023.'),
                                        ('Parafrasa semantik', '4 kalimat diubah susunannya namun maknanya', 'tetap sangat dekat (kosinus ≥ 0.82).'),
                                        ('Pola gaya bahasa manusia', 'Varians panjang kalimat dan kekayaan', 'kosakata menunjukkan tulisan manusia.')]):
        y = y0 + 584 + i * 52
        b += text(776, y, lead, 14.5, 600, 'ink') + text(776, y + 22, d1 + ' ' + d2, 13.5, 400, 'sub')
    return b


HOW = [('doc', 'Menemukan salin-tempel', ['Mencocokkan naskah kalimat demi kalimat', 'dengan dokumen di bank korpus, bahkan', 'untuk potongan yang sangat pendek.'], '50%'),
       ('stack', 'Menangkap parafrasa', ['Mengenali kalimat yang susunan atau', 'sinonimnya diubah namun maknanya', 'tetap sama dengan sumber.'], '35%'),
       ('gauge', 'Menandai gaya yang janggal', ['Melihat perubahan ritme dan kekayaan kata', 'yang khas dari teks hasil generator AI,', 'bukan tulisan manusia.'], '15%')]


def how_card(x, y, w, h, d, center, side=None):
    """Kartu carousel: ikon, judul, deskripsi, dan bar kaca di tepi bawah (bobot + tautan)."""
    ic, title, ds, bobot = d
    b = ''
    if center:
        b += rect(x, y, w, h, 'url(#gHero)', 34, filt='sh-hero') + rect(x, y, w, h, 'url(#gSheen)', 34)
        c_ink, c_sub, circ, icc, tsize, dsize = 'onDark', 'onDark', 'card', 'primary', 32, 15
    else:
        b += rect(x, y, w, h, 'card', 34, filt='sh')
        c_ink, c_sub, circ, icc, tsize, dsize = 'ink', 'sub', 'url(#gHero)', 'onDark', 26, 14.5
    ox = 120 if side == 'R' else 40  # kartu kanan: konten dimulai setelah bagian yang tertutup kartu tengah
    b += circle(x + ox + 28, y + 66, 28, circ) + ico(ic, x + ox + 28, y + 66, icc, 2)
    b += text(x + ox, y + 150, title, tsize, 500, c_ink)
    for i, ln in enumerate(ds):
        b += text(x + ox, y + 190 + i * 24, ln, dsize, 400, c_sub)
    bx, by, bw = x + 16, y + h - 30, w - 32
    b += rect(bx, by, bw, 58, 'card', 22, filt='sh')
    if side != 'R':
        b += text(bx + 26, by + 37, bobot, 20, 600, 'ink') + text(bx + 26 + mw(bobot, 20, 600) + 10, by + 36, 'bobot dari skor akhir', 12.5, 400, 'sub')
    if side != 'L':
        b += text(bx + bw - 26, by + 36, 'Lihat contoh →', 14, 600, 'primaryInk', 'end')
    return b


def seg_how(y0):
    b = abs_eyebrow(720, y0, 'CARA KERJA', 'middle')
    b += Ha(720, y0 + 52, [('Tiga lapis pemeriksaan,', 0)], 46, 'middle', 600, -0.8) + Ha(720, y0 + 106, [('satu skor', 1)], 46, 'middle', 600, -0.8)
    b += text(720, y0 + 160, 'Setiap tier menangkap jenis kemiripan yang berbeda,', 16, 400, 'sub', 'middle')
    b += text(720, y0 + 186, 'lalu digabung menjadi satu skor yang bisa diaudit.', 16, 400, 'sub', 'middle')
    # tab pil (tier tengah aktif)
    tabs = ['Tier 1 · Leksikal', 'Tier 2 · Semantik', 'Tier 3 · Stilometri']
    ws = [mw(t, 14.5, 500) + 48 for t in tabs]
    total = sum(ws) + 12
    tx, ty = 720 - total / 2, y0 + 232
    b += rect(tx, ty, total, 52, 'card', 26, filt='sh')
    cx = tx + 6
    for i, (t, w) in enumerate(zip(tabs, ws)):
        if i == 1:
            b += rect(cx, ty + 6, w, 40, 'ink', 20)
        b += text(cx + w / 2, ty + 31, t, 14.5, 500, 'onDark' if i == 1 else 'sub', 'middle')
        cx += w
    # kartu: samping di belakang, tengah di depan
    cy = y0 + 330
    b += how_card(75, cy + 36, 470, 270, HOW[0], False, 'L') + how_card(895, cy + 36, 470, 270, HOW[2], False, 'R')
    b += how_card(470, cy, 500, 334, HOW[1], True)
    b += text(720, cy + 420, 'Skor akhir = 50% leksikal + 35% semantik + 15% stilometri', 16, 500, 'sub', 'middle')
    return b


def seg_trust_short(y0):
    """Kepercayaan: kutipan bertipografi besar, kolom angka dari isi kutipan, bar akreditasi selebar konten."""
    b = abs_eyebrow(75, y0, 'MENGAPA INSTITUSI MEMILIH VERITEXT')
    b += Ha(75, y0 + 56, [('Integritas karya ilmiah tanpa kompromi', 0)], 44, 'start', 600, -0.8) + Ha(75, y0 + 110, [('privasi data.', 1)], 44, 'start', 600, -0.8)
    b += text(1365, y0 + 62, 'Verifikasi Sertifikat QR →', 15, 600, 'ink', 'end') + text(1365, y0 + 92, 'Bank Korpus Riset →', 15, 500, 'sub', 'end')
    gy = y0 + 176
    # kartu kutipan
    b += rect(75, gy, 780, 372, 'card', 40, filt='sh')
    b += '<text x="108" y="%s" font-size="190" font-weight="700" fill="%s" fill-opacity="0.22">“</text>' % (gy + 150, C['primaryInk'])
    b += '<text x="118" y="%s" font-size="30" font-weight="500" letter-spacing="-0.4" fill="%s">VeriText AI menghemat</text>' % (gy + 118, C['ink'])
    b += '<text x="118" y="%s" font-size="30" font-weight="500" letter-spacing="-0.4" fill="%s"><tspan fill="%s" font-weight="600">85%%</tspan> waktu penelaahan dokumen</text>' % (gy + 160, C['ink'], C['primaryInk'])
    b += '<text x="118" y="%s" font-size="30" font-weight="500" letter-spacing="-0.4" fill="%s">skripsi kami.</text>' % (gy + 202, C['ink'])
    b += text(118, gy + 252, 'Pemeriksaan leksikal dan semantik dilakukan dalam 1,2 detik', 15.5, 400, 'sub') + text(118, gy + 278, 'dengan jaminan hak privasi mahasiswa sesuai UU PDP.', 15.5, 400, 'sub')
    b += hair(118, gy + 308, 815, gy + 308) + text(118, gy + 340, 'Dr. Budi Santoso, M.Kom.', 15.5, 600, 'ink') + text(118 + mw('Dr. Budi Santoso, M.Kom.', 15.5, 600) + 14, gy + 340, 'Ketua Komite Integritas Akademik', 13.5, 400, 'sub')
    b += text(815, gy + 340, 'Studi Kasus 2026 · Institut Riset', 12.5, 500, 'sub', 'end')
    # kolom angka (tanpa kartu), mulai sedikit lebih tinggi dari kartu
    sx = 905
    for i, (num, cap) in enumerate([('85%', 'waktu penelaahan dokumen lebih hemat'), ('1,2 dtk', 'pemeriksaan leksikal dan semantik per naskah'), ('30 hari', 'masa retensi naskah, lalu dihapus otomatis')]):
        y = gy - 14 + i * 128
        if i:
            b += hair(sx, y - 18, 1365, y - 18)
        b += text(sx, y + 52, num, 60, 600, 'ink', ls=-1.5) + text(sx, y + 82, cap, 15, 400, 'sub')
    # bar akreditasi
    ay = gy + 372 + 34
    b += rect(75, ay, 1290, 120, 'card', 32, filt='sh') + text(111, ay + 36, 'KEPATUHAN & AKREDITASI NASIONAL', 12.5, 600, 'sub', ls=1.2)
    for i, (nm, cap) in enumerate([('UU PDP 27/2022', 'Perlindungan Data Pribadi'), ('SINTA Kemdikbud', 'Indeks ilmiah nasional'), ('Perpustakaan Nasional', 'Repositori karya ilmiah'), ('Telkom University', 'Universitas')]):
        x = 111 + i * 312
        if i:
            b += hair(x - 24, ay + 54, x - 24, ay + 98)
        b += text(x, ay + 76, nm, 16, 600, 'ink') + text(x, ay + 97, cap, 13, 400, 'sub')
    return b


def seg_cta_short(y0):
    b = Ha(720, y0 + 30, [('Deteksi esensi,', 0)], 64, 'middle', 600, -1.5) + Ha(720, y0 + 100, [('bukan sekadar kata', 1)], 64, 'middle', 600, -1.5)
    b += text(720, y0 + 162, 'Periksa orisinalitas naskah Anda dengan tiga lapis pemeriksaan', 16, 400, 'sub', 'middle')
    b += text(720, y0 + 188, 'dan terima laporan yang bisa dipertanggungjawabkan.', 16, 400, 'sub', 'middle')
    b += btn(568, y0 + 226, 304, 59, 'Buka Workspace Audit →', 'surface', 16)
    return b


def build_short():
    OFF[0] = 0
    b = seg_nav_hero()
    b += seg_report(1330)
    b += seg_how(2340)
    b += seg_trust_short(3290)
    b += seg_cta_short(4120)
    place(11, 537, 4560)
    b += seg_footer()
    height = int(Y(11, 955) + 70)
    OFF[0] = 0
    defs = '<linearGradient id="gSheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s" stop-opacity="0.30"/><stop offset="0.55" stop-color="%s" stop-opacity="0"/></linearGradient>' % (C['onDark'], C['onDark'])
    return page('VeriText AI – Beranda (ringkas)', 'Beranda publik ringkas: hero, satu laporan diagnostik, cara kerja tiga tier (carousel), kepercayaan, CTA, dan footer.', W, height, b, defs)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, '_lama'), exist_ok=True)
    with open(os.path.join(OUT, '_lama', 'landing--panjang-11-halaman.svg'), 'w') as f:
        f.write(build())
    with open(os.path.join(OUT, 'landing--default-idle.svg'), 'w') as f:
        f.write(build_short())
    print('ok landing--default-idle (ringkas) + arsip panjang')
