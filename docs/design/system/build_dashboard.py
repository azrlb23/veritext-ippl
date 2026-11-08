"""Dashboard VeriText (laptop 1440): satu header, empat tab, blok-blok yang dirakit per state.
Jalankan: python3 build_dashboard.py  -> ../laptop/dashboard/*.svg
Blok: KPI, kartu Unggah, kartu Antrean, grafik+gauge, riwayat. Blok lama dipindah dengan <g translate>."""
import os
from vt_kit import (C, HERE, W, mw, text, rect, circle, hair, card, btn, link, ico, chevron, segmented, select, search_pill, filter_pill,
                    kpi_card, topnav, radio, progress, spinner, badge, segarc, dash, page)

OUT = os.path.join(HERE, '..', 'laptop', 'dashboard')

ROWS = [
    ('Dampak Perubahan Iklim terhadap Ketahanan Pangan', '03 Nov 2026', 'Hybrid', ('Selesai', None), 38.6, 'Buka →'),
    ('Analisis Sentimen Ulasan Aplikasi Mobile Banking', '02 Nov 2026', 'Hybrid', ('Selesai', None), 12.3, 'Buka →'),
    ('Rancang Bangun Sistem Informasi Perpustakaan', '01 Nov 2026', 'Leksikal', ('Diproses 35%', 'blue'), None, 'Batalkan'),
    ('Optimasi Rute Distribusi dengan Algoritma Genetika', '27 Okt 2026', 'Leksikal', ('Gagal', 'red'), None, 'Buka →'),
]
NEWDOC = 'Dampak Perubahan Iklim terhadap Ketahanan Pangan'
BASEQ = [dict(title='Rancang Bangun Sistem Informasi Perpustakaan', stage='Tahap 2 · Rabin-Karp Winnowing', pct=35),
         dict(title='Efektivitas Metode Pembelajaran Daring', stage='Tahap 3 · Semantik dan stilometri', pct=70)]
STAGES = {1: ('Tahap 1 · Ekstraksi teks dan normalisasi kalimat', 15), 2: ('Tahap 2 · Rabin-Karp Winnowing', 35), 3: ('Tahap 3 · Semantik dan stilometri', 70)}


def shift(s, dy):
    return '<g transform="translate(0 %s)">%s</g>' % (dy, s)


def trunc(s, size, weight, maxw):
    if mw(s, size, weight) <= maxw:
        return s
    while s and mw(s + '…', size, weight) > maxw:
        s = s[:-1]
    return s.rstrip() + '…'


# ---------------- header ----------------
def header(tab, sync='idle'):
    b = topnav(['Dashboard', 'Audit', 'Korpus', 'Billing', 'Admin'], 'Dashboard', 'Rizky Pratama', 'rizky@nusantara.ac.id', 'RP')
    b += text(48, 170, 'Ringkasan audit', 34, 500, 'ink', ls=-0.6) + text(48, 200, 'Ringkasan aktivitas dan hasil audit naskah Anda bulan ini', 15, 400, 'sub')
    if sync == 'syncing':
        b += spinner(56, 224, 7, 'primary', 2.2) + text(72, 229, 'Menyinkronkan status antrean dan saldo…', 13, 400, 'sub')
    else:
        b += text(48, 229, 'Terakhir disinkronkan 09.12 WIB · ', 13, 400, 'sub') + link(48 + mw('Terakhir disinkronkan 09.12 WIB · ', 13, 400), 229, 'Sinkronkan status', 13)
    b += select(972, 152, 150, 'Bulan ini')
    b += rect(1138, 148, 128, 52, 'card', 26) + circle(1166, 174, 18, 'field') + ico('up', 1166, 174, 'ink', 1.6) + text(1194, 180, 'Ekspor', 15, 500, 'ink')
    b += filter_pill(1282, 148)
    b += segmented(48, 252, ['Semua', 'Unggah naskah', 'Antrean deteksi', 'Riwayat audit'], tab)
    return b


# ---------------- KPI (basis y=232) ----------------
def kpi(tokens='3', zero=False):
    kp = [('Saldo token', tokens, '↓ 40%' if not zero else '—', 'neutral', '5' if not zero else '1', 'coin', 'hero'), ('Naskah diuji', '14' if not zero else '0', '↑ 27,3%' if not zero else '—', 'neutral', '11' if not zero else '0', 'doc', 'dark'),
          ('Audit selesai', '12' if not zero else '0', '↑ 20,0%' if not zero else '—', 'neutral', '10' if not zero else '0', 'check', 'blue'), ('Rata-rata skor', '24,1%' if not zero else '—', '↓ 3,2%' if not zero else '—', 'good' if not zero else 'neutral', '27,3%' if not zero else '—', 'gauge', 'blue')]
    return ''.join(kpi_card(48 + i * 342, 232, 318, lab, val, dl, tone, 'Bulan lalu:', last, ic, kind) for i, (lab, val, dl, tone, last, ic, kind) in enumerate(kp))


# ---------------- kartu unggah ----------------
def upload(x, y, w, h, st):
    drop, depth, warn, pct = st.get('drop', 'idle'), st.get('depth'), st.get('warn', False), st.get('pct', 0)
    dz_w = 400 if w < 1000 else 620
    rx = x + 28 + dz_w + 32
    rw = x + w - 28 - rx
    b = card(x, y, w, h) + text(x + 28, y + 46, 'Unggah naskah', 22, 500, 'ink')
    zx, zy, zh = x + 28, y + 70, h - 100
    cx, cy = zx + dz_w / 2, zy + zh / 2
    if drop == 'idle':
        b += rect(zx, zy, dz_w, zh, 'field', 24, role='dropzone', stroke='placeholder', sw=1.5, dash='6 5')
        b += ico('up', cx, cy - 30, 'sub', 1.8) + text(cx, cy + 8, 'Tarik & lepas naskah di sini', 16, 600, 'ink', 'middle') + text(cx, cy + 32, '.pdf  .docx  .txt  ·  maks 50 MB', 13, 400, 'sub', 'middle') + link(cx, cy + 62, 'atau pilih dari komputer', 13.5, anchor='middle')
    elif drop == 'drag':
        b += rect(zx, zy, dz_w, zh, 'primaryTint', 24, role='dropzone', stroke='primary', sw=2, dash='6 5')
        b += '<g transform="translate(%s %s) scale(1.7) translate(%s %s)">%s</g>' % (cx, cy - 26, -cx, -(cy - 26), ico('up', cx, cy - 26, 'primaryInk', 1.8))
        b += text(cx, cy + 22, 'Lepaskan untuk mengunggah', 17, 600, 'primaryInk', 'middle') + text(cx, cy + 46, 'Berkas diterima: .pdf, .docx, .txt', 13, 400, 'sub', 'middle')
    else:
        b += rect(zx, zy, dz_w, zh, 'field', 24)
        b += text(zx + 28, zy + 50, trunc(NEWDOC, 15.5, 600, dz_w - 90), 15.5, 600, 'ink') + text(zx + 28, zy + 74, '4.218 kata · 1,2 MB · .docx', 13, 400, 'sub')
        b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round"><path d="M-4.5 -4.5L4.5 4.5M4.5 -4.5L-4.5 4.5"/></g>' % (zx + dz_w - 28, zy + 32, C['sub'])
        if drop == 'uploading':
            b += progress(zx + 28, zy + zh - 62, dz_w - 56, pct) + text(zx + 28, zy + zh - 28, 'Mengunggah… %d%%' % pct, 13.5, 600, 'ink') + text(zx + dz_w - 28, zy + zh - 28, 'ke server', 12.5, 400, 'sub', 'end')
        else:
            b += link(zx + 28, zy + zh - 28, 'Ganti berkas', 13.5)
    b += text(rx, y + 84, 'Kedalaman audit', 13, 500, 'sub')
    b += radio(rx, y + 96, rw, 'Hybrid Penuh · Tier 1–4', '2 token', depth == 'hybrid') + radio(rx, y + 148, rw, 'Leksikal Cepat · Tier 1', '1 token', depth == 'lexical')
    ready = drop == 'file' and depth and not warn
    if warn:
        b += text(rx + 4, y + 224, 'Saldo token tidak cukup. Hybrid membutuhkan 2 token,', 13, 500, 'red') + text(rx + 4, y + 244, 'saldo Anda 1 token.', 13, 500, 'red') + link(rx + rw, y + 244, '+ Top up kuota', 13, anchor='end')
    elif depth:
        b += text(rx + 4, y + 224, 'Audit ini memakai %d token. Sisa saldo %d token.' % (2 if depth == 'hybrid' else 1, 1 if depth == 'hybrid' else 2), 13, 400, 'sub')
    else:
        b += text(rx + 4, y + 224, 'Pilih kedalaman audit untuk melanjutkan.', 13, 400, 'sub')
    by = y + h - 70
    if drop == 'uploading':
        b += btn(rx, by, rw, 44, 'Mengunggah…', 'disabled', 14.5) + spinner(rx + rw / 2 - mw('Mengunggah…', 14.5, 600) / 2 - 18, by + 22, 8, 'sub', 2.2)
    else:
        b += btn(rx, by, rw, 44, 'Mulai proses audit', 'primary' if ready else 'disabled', 14.5)
    return b


# ---------------- kartu antrean ----------------
def queue(x, y, w, h, items, full=False):
    b = card(x, y, w, h) + text(x + 28, y + 46, 'Antrean deteksi', 22, 500, 'ink') + link(x + w - 28, y + 44, 'Semua →' if not full else '%d tugas' % len(items), 13.5, anchor='end') if not full else card(x, y, w, h) + text(x + 28, y + 46, 'Antrean deteksi', 22, 500, 'ink') + text(x + w - 28, y + 44, '%d tugas aktif' % len(items), 13.5, 500, 'sub', 'end')
    if not items:
        return b + text(x + 28, y + 100, 'Tidak ada naskah dalam antrean.', 14, 400, 'sub')
    pitch = 88 if not full else 96
    for i, it in enumerate(items):
        yy = y + 84 + i * pitch
        if i:
            b += hair(x + 28, yy - 14, x + w - 28, yy - 14)
        b += text(x + 28, yy + 14, trunc(it['title'], 14, 600, w - 100), 14, 600, 'ink')
        if it.get('fail'):
            b += text(x + 28, yy + 36, it['fail'][0], 12.5, 600, 'red') + text(x + 28, yy + 54, it['fail'][1], 12.5, 400, 'sub')
            b += link(x + w - 28, yy + 54, 'Coba lagi', 13, anchor='end')
        else:
            b += text(x + 28, yy + 34, it['stage'], 12.5, 400, 'sub') + link(x + w - 28, yy + 34, 'Batalkan', 12.5, 'red', 'end')
            b += progress(x + 28, yy + 46, w - 56 - 52, it['pct']) + text(x + w - 28, yy + 54, '%d%%' % it['pct'], 13, 600, 'ink', 'end')
    return b


# ---------------- grafik + gauge (basis y=376) ----------------
def chart_row():
    b = card(48, 376, 900, 372) + text(76, 424, 'Aktivitas audit', 24, 500, 'ink') + select(776, 394, 144, '8 bulan', 'field')
    top, bot, px0, step = 476, 664, 120, 100
    for k in range(6):
        y = bot - k * (bot - top) / 5.0
        b += dash(px0 - 4, y, 924, y) + text(100, y + 5, str(k), 13, 400, 'sub', 'end')
    for i, (m, v) in enumerate(zip(['Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov'], [1, 0, 2, 1, 2, 1, 4, 3])):
        x = px0 + 12 + i * step
        h = v / 5.0 * (bot - top)
        b += rect(x, top - 14, 64, bot - top + 14, 'field', 16)
        if v:
            if i == 6:
                b += rect(x + 2, bot - h - 2, 60, h, 'url(#gHero)', 14) + rect(x + 2, bot - h - 2, 60, h, 'url(#hatch)', 14) + circle(x + 32, bot - h - 2, 8, 'card') + circle(x + 32, bot - h - 2, 4.5, 'primary')
            else:
                b += rect(x + 2, bot - h - 2, 60, h, 'track', 14)
        b += text(x + 32, 690, m, 14, 400, 'sub', 'middle')
    b += rect(540, 486, 212, 100, 'card', 16, filt='sh') + text(562, 516, 'Oktober 2026', 15, 600, 'ink')
    b += circle(566, 540, 4, 'track') + text(580, 545, 'Naskah diuji', 14, 400, 'sub') + text(730, 545, '4', 14, 600, 'ink', 'end')
    b += circle(566, 566, 4, 'primary') + text(580, 571, 'Rata-rata skor', 14, 400, 'sub') + text(730, 571, '21,4%', 14, 600, 'ink', 'end')
    b += card(972, 376, 420, 372) + text(1000, 424, 'Tingkat keaslian', 24, 500, 'ink') + circle(1352, 414, 22, 'field') + circle(1343, 414, 2.2, 'ink') + circle(1352, 414, 2.2, 'ink') + circle(1361, 414, 2.2, 'ink')
    b += segarc(1182, 604, 96, 150, 14, 0.75) + text(1182, 600, '75%', 44, 500, 'ink', 'middle', ls=-1) + text(1182, 624, 'naskah aman', 13, 400, 'sub', 'middle')
    for i, (lab, val, cap) in enumerate([('Aman (<20%)', '9', '75% dari 12 audit'), ('Perlu ditinjau', '3', '25% dari 12 audit')]):
        x = 996 + i * 190
        b += rect(x, 644, 176, 84, 'field', 18) + text(x + 18, 670, lab, 13, 500, 'sub') + text(x + 18, 708, val, 26, 600, 'ink') + text(x + 18 + mw(val, 26, 600) + 10, 708, cap, 12, 400, 'sub')
    return b


# ---------------- riwayat (kartu dengan tinggi h, kiri-atas di y) ----------------
def history(y, h, mode='table'):
    """mode: table (4 baris) | full (filter + paginasi) | empty."""
    b = card(48, y, 1344, h) + text(76, y + 50, 'Riwayat audit', 24, 500, 'ink')
    if mode == 'full':
        b += segmented(270, y + 26, ['Semua', 'Selesai', 'Diproses', 'Gagal'], 0)
    b += search_pill(1010, y + 24, 236, 'Cari naskah…')
    b += rect(1256, y + 24, 120, 48, 'field', 24) + ico('sort', 1280, y + 48, 'ink', 1.6) + text(1300, y + 53, 'Urutkan', 14, 500, 'ink') + chevron(1362, y + 48)
    if mode == 'empty':
        return b + text(720, y + 160, 'Belum ada riwayat audit', 22, 600, 'ink', 'middle') + text(720, y + 192, 'Unggah naskah pertama Anda untuk melihat hasil audit di sini.', 15, 400, 'sub', 'middle') + btn(600, y + 226, 240, 48, 'Unggah naskah pertama', 'secondary', 14.5)
    b += rect(64, y + 94, 1312, 44, 'field', 12) + rect(82, y + 108, 16, 16, 'track', 4)
    for lab, x in [('Judul naskah', 118), ('ID audit', 520), ('Tanggal', 680), ('Kedalaman', 840), ('Status', 1000), ('Skor', 1160)]:
        b += text(x, y + 121, lab, 14, 400, 'sub')
    b += text(1352, y + 121, 'Aksi', 14, 400, 'sub', 'end')
    for i, (t, d, dep, (st, kind), sc, act) in enumerate(ROWS):
        ry = y + 150 + i * 66
        if i:
            b += hair(64, ry - 8, 1376, ry - 8)
        b += rect(82, ry + 20, 16, 16, 'track', 4) + text(118, ry + 34, trunc(t, 14.5, 500, 380), 14.5, 500, 'ink')
        b += text(520, ry + 34, '#8F2A91C%d' % (4 + i), 13.5, 400, 'sub') + text(680, ry + 34, d, 14, 400, 'sub') + text(840, ry + 34, dep, 14, 500, 'ink')
        b += badge(1000, ry + 15, st, kind) if kind else text(1000, ry + 34, st, 14, 400, 'sub')
        b += text(1160, ry + 34, '—' if sc is None else ('%.1f%%' % sc).replace('.', ','), 14.5, 600, 'orange' if (sc or 0) >= 20 else ('ink' if sc else 'sub'))
        b += link(1352, ry + 34, act, 14, 'red' if act == 'Batalkan' else 'primaryInk', 'end')
    if mode == 'full':
        fy = y + 150 + 4 * 66 + 6
        b += hair(64, fy - 8, 1376, fy - 8) + text(76, fy + 40, 'Menampilkan 1–4 dari 14 audit', 13, 400, 'sub')
        for i, p in enumerate(['1', '2', '3']):
            px = 1376 - (3 - i) * 40
            b += rect(px, fy + 16, 34, 34, 'ink' if i == 0 else 'field', 17) + text(px + 17, fy + 38, p, 13, 600, 'onDark' if i == 0 else 'ink', 'middle')
    return b


# ---------------- overlay ----------------
def toast():
    return (rect(1000, 108, 392, 100, 'card', 22, filt='sh', op=1) + text(1026, 140, trunc('Audit "' + NEWDOC + '" selesai', 14.5, 600, 340), 14.5, 600, 'ink')
            + text(1026, 164, 'Skor kemiripan 18,4% · kategori aman', 13, 400, 'sub') + link(1366, 190, 'Buka laporan →', 13.5, anchor='end'))


def cancel_dialog(h):
    s = rect(0, 0, W, h, 'ink', 0, op=0.22) + rect(470, 330, 500, 238, 'card', 28, filt='sh', op=1)
    s += text(504, 386, 'Batalkan tugas ini?', 24, 600, 'ink') + text(504, 420, trunc('Audit "' + BASEQ[0]['title'] + '"', 14.5, 500, 430), 14.5, 500, 'ink')
    s += text(504, 446, 'akan dihentikan dan token yang terpakai dikembalikan', 14.5, 400, 'sub') + text(504, 468, 'ke saldo Anda.', 14.5, 400, 'sub')
    return s + btn(504, 496, 150, 48, 'Kembali', 'secondary', 14.5) + btn(668, 496, 190, 48, 'Batalkan tugas', 'danger', 14.5)


# ---------------- perakit state ----------------
def semua(cfg):
    zero = cfg.get('zero', False)
    q = cfg.get('queue', BASEQ)
    b = header(0, cfg.get('sync', 'idle')) + shift(kpi(cfg.get('tokens', '3'), zero), 92)
    b += upload(48, 472, 880, 330, cfg.get('up', {})) + queue(952, 472, 440, 330, q)
    y = 826
    if zero:
        return b + history(y, 360, 'empty'), 1240
    b += shift(chart_row(), y - 376) + history(y + 396, 424, 'table')
    return b, y + 396 + 424 + 64


def build(name):
    cfg = STATES[name]
    b, h = {'semua': semua, 'upload': tab_upload, 'queue': tab_queue, 'history': tab_history}[cfg.get('kind', 'semua')](cfg)
    if cfg.get('toast'):
        b += toast()
    if cfg.get('dialog'):
        b += cancel_dialog(h)
    return page('VeriText AI – Dashboard (%s)' % name, 'Dashboard laptop: %s.' % name, W, h, b)


def tab_upload(cfg):
    return header(1) + upload(48, 324, 1344, 380, cfg.get('up', {})), 760


def tab_queue(cfg):
    items = [dict(title=NEWDOC, stage=STAGES[2][0], pct=STAGES[2][1])] + BASEQ
    return header(2) + queue(48, 324, 1344, 120 + 3 * 96, items, True), 324 + 120 + 3 * 96 + 64


def tab_history(cfg):
    return header(3) + history(324, 520, 'full'), 324 + 520 + 64


def stage(n):
    s, p = STAGES[n]
    return [dict(title=NEWDOC, stage=s, pct=p)] + BASEQ[:1]


STATES = {
    'default-idle': {},
    'tab-all-active': {},
    'tab-upload-active': dict(kind='upload'),
    'tab-active-tasks-active': dict(kind='queue'),
    'tab-history-active': dict(kind='history'),
    'history-desktop-table': dict(kind='history'),
    'dropzone-drag-over': dict(up=dict(drop='drag')),
    'dropzone-file-selected': dict(up=dict(drop='file')),
    'depth-selection-hybrid': dict(up=dict(drop='file', depth='hybrid')),
    'depth-selection-lexical': dict(up=dict(drop='file', depth='lexical')),
    'token-insufficient-warning': dict(tokens='1', up=dict(drop='file', depth='hybrid', warn=True)),
    'file-uploading-progress': dict(up=dict(drop='uploading', depth='hybrid', pct=62)),
    'worker-processing-stage-1': dict(queue=stage(1)),
    'worker-processing-stage-2': dict(queue=stage(2)),
    'worker-processing-stage-3': dict(queue=stage(3)),
    'worker-task-completed-toast': dict(queue=BASEQ[1:], toast=True),
    'worker-task-failed': dict(queue=[dict(title=NEWDOC, fail=('Pemrosesan gagal: PDF terenkripsi atau tanpa lapisan teks.', 'Token 2 sudah dikembalikan ke saldo Anda.'))] + BASEQ[:1]),
    'task-cancel-dialog': dict(dialog=True),
    'empty-history': dict(zero=True, queue=[], tokens='1'),
    'syncing-status-spin': dict(sync='syncing'),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for n in STATES:
        with open(os.path.join(OUT, 'dashboard--%s.svg' % n), 'w') as f:
            f.write(build(n))
    print('ok', len(STATES), 'layar dashboard')
