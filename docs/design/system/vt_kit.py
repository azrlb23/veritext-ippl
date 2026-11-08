"""Pustaka komponen VeriText (laptop 1440, mode terang).

Semua layar digambar dari sini. Warna hanya lewat nama token (tokens.json):
memakai nama yang tidak ada akan KeyError, jadi warna liar tidak bisa lolos.
Elemen yang punya peran khusus diberi data-role supaya check_style.py bisa memeriksanya.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(os.path.join(HERE, 'tokens.json')))
C = TOK['color']
W = TOK['canvas']['width']
R_CARD = TOK['radius']['card']
R_FIELD = TOK['radius']['field']
GLASS = 0.78  # permukaan kaca: putih 78% di atas latar gradasi


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def tw(s, size, k=0.55):
    return len(str(s)) * size * k


def text(x, y, s, size=14, weight=400, fill='ink', anchor='start', ls=None):
    return '<text x="%s" y="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (
        x, y, size, weight, C[fill], anchor, (' letter-spacing="%s"' % ls) if ls else '', esc(s))


def paint(name):
    """Nama token, atau url(#gradien) yang didefinisikan page()."""
    return name if name.startswith('url(') else C[name]


def circle(cx, cy, r, fill):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (cx, cy, r, paint(fill))


def rect(x, y, w, h, fill=None, r=0, role=None, stroke=None, sw=1, dash=None, filt=None, op=None):
    if op is None and fill == 'card' and filt == 'sh':
        op = GLASS
    a = ' fill="%s"' % (paint(fill) if fill else 'none')
    if op is not None:
        a += ' fill-opacity="%s"' % op
    if stroke:
        a += ' stroke="%s" stroke-width="%s"' % (C[stroke], sw)
    if dash:
        a += ' stroke-dasharray="%s"' % dash
    if filt:
        a += ' filter="url(#%s)"' % filt
    if role:
        a += ' data-role="%s"' % role
    return '<rect x="%s" y="%s" width="%s" height="%s"%s%s/>' % (x, y, w, h, (' rx="%s"' % r) if r else '', a)


def hair(x1, y1, x2, y2):
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>' % (x1, y1, x2, y2, C['hair'])


def card(x, y, w, h):
    return rect(x, y, w, h, 'card', R_CARD, filt='sh')


# ---------- kontrol ----------
def field(x, y, w, label, value, state='idle', icon=None, msg=None):
    """Isian: isi warna + label kecil di dalam. Tanpa bingkai; bingkai hanya saat fokus atau error."""
    h = 56
    s = rect(x, y, w, h, 'disabled' if state == 'dim' else 'field', R_FIELD)
    if state in ('focus', 'error'):
        s += rect(x + 16, y + h - 5, w - 32, 3, 'primary' if state == 'focus' else 'red', 1.5, role='state-bar')
    s += text(x + 16, y + 21, label, 12, 500, 'primaryInk' if state == 'focus' else ('red' if state == 'error' else 'sub'))
    s += text(x + 16, y + 42, value, 15, 500, 'placeholder' if state == 'ph' else ('sub' if state == 'dim' else 'ink'))
    if icon in ('eye-off', 'eye'):
        cx, cy = x + w - 28, y + 28
        s += ('<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
              '<path d="M-9 0Q0 -8 9 0Q0 8 -9 0Z"/><circle r="2.5"/>%s</g>') % (cx, cy, C['sub'], '<path d="M-8 -8L8 8"/>' if icon == 'eye-off' else '')
    if msg:
        s += text(x + 4, y + h + 18, msg, 12, 500, 'red')
    return s


def banner(x, y, w, msg, kind='red', dismiss=True):
    """Pesan satu baris di atas form. Hanya untuk pengecualian (galat, peringatan, sukses)."""
    fg = {'red': 'red', 'yellow': 'red', 'green': 'primaryInk', 'blue': 'primaryInk'}[kind]
    lines = msg.split('\n')
    h = 44 if len(lines) == 1 else 66
    s = ''
    for i, ln in enumerate(lines):
        s += text(x + 2, y + (26 if h == 44 else 18 + i * 22), ln, 14, 600 if i == 0 else 500, fg)
    if dismiss:
        s += ('<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round"><path d="M-4.5 -4.5L4.5 4.5M4.5 -4.5L-4.5 4.5"/></g>') % (x + w - 8, y + 14, C['sub'])
    return s


def banner_h(msg):
    return 44 if '\n' not in msg else 66


def spinner(cx, cy, r=9, color='primary', sw=2.6):
    """Penanda memuat (busur 270 derajat, statis di SVG)."""
    return '<path d="M%s %sA%s %s 0 1 1 %s %s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (cx, cy - r, r, r, cx - r, cy, C[color], sw)


def strength(x, y, level, w=370):
    """Meter kekuatan sandi: 3 batang + label. level 1..3."""
    col = {1: 'red', 2: 'orange', 3: 'primary'}[level]
    lab = {1: 'Lemah', 2: 'Sedang', 3: 'Kuat'}[level]
    bw = (w - 120 - 12) / 3.0
    s = ''
    for i in range(3):
        s += rect(x + i * (bw + 6), y, bw, 5, col if i < level else 'track', 2.5)
    return s + text(x + w, y + 6, lab, 12.5, 600, {'red': 'red', 'orange': 'orange', 'primary': 'primaryInk'}[col], 'end')


def btn(x, y, w, h, label, kind='secondary', size=15):
    """primary: satu per layar. secondary: isi netral tanpa garis. disabled: terkunci."""
    assert h >= 44, 'target sentuh minimal 44'
    fill, tc, role, filt = {
        'primary': ('url(#gDark)', 'onDark', 'primary', 'sh-btn'),
        'secondary': ('field', 'ink', 'secondary', None),
        'surface': ('card', 'ink', 'secondary', None),
        'disabled': ('disabled', 'sub', 'disabled', None),
        'danger': ('redTint', 'red', 'danger', None),
    }[kind]
    return rect(x, y, w, h, fill, h // 2, role=role, filt=filt) + text(x + w / 2, y + h / 2 + size * 0.36, label, size, 600, tc, 'middle')


def link(x, y, s, size=14, fill='primaryInk', anchor='start'):
    return text(x, y, s, size, 600, fill, anchor)


def checkbox(x, y, label, on=False):
    s = rect(x, y, 20, 20, 'ink' if on else 'field', 6)
    if on:
        s += '<path d="M%s %sl3.5 3.5 6-7" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' % (x + 5, y + 10.5, C['onDark'])
    return s + text(x + 30, y + 15, label, 14, 400, 'ink')


def radio(x, y, w, label, meta, on):
    """Terpilih = titik terisi + latar tint (satu sinyal)."""
    s = rect(x, y, w, 44, 'primaryTint' if on else 'field', 22)
    cx, cy = x + 24, y + 22
    s += '<circle cx="%s" cy="%s" r="8" fill="%s" data-role="radio"/>' % (cx, cy, C['card'])
    if on:
        s += '<circle cx="%s" cy="%s" r="4.5" fill="%s"/>' % (cx, cy, C['primary'])
    s += text(x + 46, y + 27, label, 14, 600 if on else 500, 'primaryInk' if on else 'ink')
    s += text(x + w - 18, y + 27, meta, 13, 600, 'primaryInk' if on else 'sub', 'end')
    return s


def segmented(x, y, items, active):
    """Filter: wadah isian, pil terpilih putih (kartu)."""
    widths = [tw(i, 14, 0.56) + 36 for i in items]
    s = rect(x, y, sum(widths) + 8, 44, 'field', 22)
    cx = x + 4
    for i, (lab, w) in enumerate(zip(items, widths)):
        if i == active:
            s += rect(cx, y + 4, w, 36, 'card', 18, filt='sh-sm')
        s += text(cx + w / 2, y + 27, lab, 14, 600 if i == active else 500, 'ink' if i == active else 'sub', 'middle')
        cx += w
    return s


def badge(x, y, label, kind):
    """Hanya untuk pengecualian (diproses, gagal). Baris normal = teks abu."""
    tint, tc = {'blue': ('primaryTint', 'primaryInk'), 'red': ('redTint', 'red')}[kind]
    w = tw(label, 12.5, 0.58) + 22
    return ('<g data-role="badge" data-label="%s">' % esc(label)) + rect(x, y, w, 26, tint, 13) + text(x + w / 2, y + 17.5, label, 12.5, 600, tc, 'middle') + '</g>'


def progress(x, y, w, pct):
    return rect(x, y, w, 6, 'track', 3) + rect(x, y, max(6, w * pct / 100.0), 6, 'primary', 3)


# ---------- kerangka ----------
NAV = [('Dashboard', ''), ('Unggah Naskah', ''), ('Antrean Deteksi', '2'), ('Riwayat Audit', ''), ('Bank Korpus', ''), ('Billing & Token', '')]


def brand(x, y, size=18):
    return ('<text x="%s" y="%s" font-size="%s" font-weight="700" fill="%s">VeriText AI<tspan fill="%s">.</tspan></text>'
            % (x, y, size, C['ink'], C['primary']))


def sidebar(active='Dashboard', tokens=3, h=1020):
    s = rect(0, 0, TOK['canvas']['sidebar'], h, 'card')
    s += brand(28, 52)
    s += text(28, 106, 'MENU', 12, 600, 'sub', ls=1.2)
    for i, (lab, cnt) in enumerate(NAV):
        y = 120 + i * 50
        on = lab == active
        if on:
            s += rect(16, y, 208, 44, 'primaryTint', 22)
        s += text(40, y + 27, lab, 14.5, 600 if on else 500, 'primaryInk' if on else 'ink')
        if cnt:
            s += text(206, y + 27, cnt, 13, 600, 'sub', 'end')
    s += text(28, h - 128, 'Saldo token', 12, 500, 'sub') + text(28, h - 86, str(tokens), 44, 600, 'ink')
    s += text(28, h - 56, 'Cukup untuk 1 audit Hybrid', 12, 400, 'sub') + link(28, h - 30, 'Top up kuota →', 13.5)
    return s


def topbar(x, w, initials=None):
    s = rect(x, 16, 480, 44, 'card', 22) + text(x + 24, 43, 'Cari naskah atau ID audit…', 14, 400, 'placeholder')
    s += circle(x + w - 32, 38, 20, 'field') + ico('user', x + w - 32, 38, 'ink', 1.7)
    return s


ICONS = {
    'coin': '<circle r="8"/><path d="M-3.5 0H3.5M0 -3.5V3.5"/>',
    'doc': '<path d="M-5.5 -8H2L6 -4V8H-5.5Z"/><path d="M-2 0H2.5M-2 3.5H2.5"/>',
    'check': '<circle r="8"/><path d="M-3.5 0L-1 2.5L4 -3"/>',
    'gauge': '<path d="M-8 4A8 8 0 0 1 8 4"/><path d="M0 4L4 -2"/>',
    'bell': '<path d="M-6 3V-1A6 6 0 0 1 6 -1V3L7.5 5H-7.5ZM-2 8H2"/>',
    'gear': '<circle r="3"/><path d="M0 -8V-5.5M0 5.5V8M-8 0H-5.5M5.5 0H8M-5.7 -5.7L-4 -4M4 4L5.7 5.7M-5.7 5.7L-4 4M4 -4L5.7 -5.7"/>',
    'up': '<path d="M0 6V-8M-5 -3L0 -8L5 -3M-8 4V8H8V4"/>',
    'search': '<circle cx="-1.5" cy="-1.5" r="6"/><path d="M3 3L8 8"/>',
    'filter': '<path d="M-7 -3H7M-7 3H7"/><circle cx="-2" cy="-3" r="2.2"/><circle cx="2" cy="3" r="2.2"/>',
    'sort': '<path d="M-7 -5H7M-7 0H3M-7 5H0"/>',
    'stack': '<path d="M-8 -5L0 -9L8 -5L0 -1ZM-8 0L0 4L8 0M-8 4.5L0 8.5L8 4.5"/>',
    'bars': '<path d="M-6 8V0M0 8V-8M6 8V-4"/>',
    'user': '<circle cx="0" cy="-3.2" r="3.4"/><path d="M-6.5 7c0-3.3 2.9-5.5 6.5-5.5s6.5 2.2 6.5 5.5"/>',
}


def ico(name, cx, cy, color='ink', w=1.8):
    return '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">%s</g>' % (
        cx, cy, C[color], w, ICONS[name])


def chevron(cx, cy, fill='ink'):
    return ('<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M-5 -2L0 3L5 -2"/></g>') % (cx, cy, C[fill])


def select(x, y, w, label, surface='card'):
    """Pil pilihan (dropdown). Label dulu, panah sesudahnya."""
    return rect(x, y, w, 44, surface, 22) + text(x + 20, y + 28, label, 14.5, 500, 'ink') + chevron(x + w - 24, y + 22)


def arc(cx, cy, r, pct, sw=22):
    """Gauge setengah lingkaran polos: jalur + isi satu warna."""
    import math
    th = math.pi * (1 - pct)
    ex, ey = cx + r * math.cos(th), cy - r * math.sin(th)
    return ('<path d="M%s %sA%s %s 0 0 1 %s %s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>'
            '<path d="M%s %sA%s %s 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>') % (
        cx - r, cy, r, r, cx + r, cy, C['track'], sw, cx - r, cy, r, r, ex, ey, C['primary'], sw)


def topnav(items, active, name, email, initials=None):
    """Header pil: merek, menu pil (aktif = gelap), pengguna dengan icon kontak."""
    s = rect(48, 24, W - 96, 68, 'card', 34, filt='sh')
    s += brand(80, 65, 21)
    widths = [tw(i, 15, 0.55) + 36 for i in items]
    tot = sum(widths) + 16
    x0 = W / 2 - tot / 2
    s += rect(x0, 32, tot, 52, 'field', 26)
    cx = x0 + 8
    for i, (lab, w) in enumerate(zip(items, widths)):
        if lab == active:
            s += rect(cx, 38, w, 40, 'ink', 20)
        s += text(cx + w / 2, 63, lab, 15, 500, 'onDark' if lab == active else 'ink', 'middle')
        cx += w
    s += rect(1064, 34, 80, 48, 'field', 24) + ico('bell', 1092, 58) + circle(1102, 48, 6.5, 'field') + circle(1102, 48, 4.5, 'red') + ico('gear', 1120, 58)
    s += circle(1178, 58, 18, 'field') + ico('user', 1178, 58, 'ink', 1.7)
    s += text(1208, 54, name, 13.5, 600, 'ink') + text(1208, 72, email, 12, 400, 'sub')
    return s


def kpi_card(x, y, w, label, value, delta, tone, last_label, last_value, icon, kind):
    """Kartu metrik: label, angka, pil delta kecil, 'bulan lalu', satu lingkaran ikon.
    kind: hero (biru bergradasi) | dark | blue | plain. tone: good | neutral."""
    hero = kind == 'hero'
    s = rect(x, y, w, 124, 'url(#gHero)', 22, filt='sh-hero') if hero else card(x, y, w, 124)
    s += text(x + 24, y + 36, label, 15, 500, 'onDark' if hero else 'sub')
    s += text(x + 24, y + 84, value, 42, 600, 'onDark' if hero else 'ink', ls=-0.8)
    px, dw = x + 24 + tw(value, 42, 0.56) + 14, tw(delta, 12.5, 0.6) + 20
    if hero:
        s += rect(px, y + 60, dw, 24, 'ink', 12, op=0.28) + text(px + dw / 2, y + 76.5, delta, 12.5, 600, 'onDark', 'middle')
    else:
        good = tone == 'good'
        s += rect(px, y + 60, dw, 24, 'greenTint' if good else 'field', 12) + text(px + dw / 2, y + 76.5, delta, 12.5, 600, 'green' if good else 'sub', 'middle')
    s += text(x + 24, y + 110, last_label, 13, 400, 'onDark' if hero else 'sub') + text(x + 24 + tw(last_label, 13, 0.52) + 6, y + 110, last_value, 13, 600, 'onDark' if hero else 'ink')
    cx, cy = x + w - 52, y + 40
    s += circle(cx, cy, 22, 'card' if hero else ('url(#gDark)' if kind == 'dark' else 'url(#gHero)'))
    s += ico(icon, cx, cy, 'primary' if hero else 'onDark')
    return s


def filter_pill(x, y, w=110):
    return rect(x, y, w, 52, 'url(#gFilter)', 26) + rect(x + 4, y + 4, 44, 44, 'card', 22) + ico('filter', x + 26, y + 26, 'ink', 1.6) + text(x + 62, y + 32, 'Filter', 15, 500, 'onDark')


def search_pill(x, y, w, placeholder):
    return rect(x, y, w, 48, 'field', 24) + circle(x + 28, y + 24, 16, 'card') + ico('search', x + 28, y + 24, 'ink', 1.6) + text(x + 54, y + 29, placeholder, 14, 400, 'placeholder')


def segarc(cx, cy, r1, r2, n, pct, sw=22):
    """Gauge bersegmen: segmen radial satu warna; empat segmen terakhir memudar lewat opasitas."""
    import math
    out = ''
    filled = int(math.ceil(n * pct))
    for i in range(n):
        a = math.pi - (i + 0.5) * (math.pi / n)
        x1, y1 = cx + r1 * math.cos(a), cy - r1 * math.sin(a)
        x2, y2 = cx + r2 * math.cos(a), cy - r2 * math.sin(a)
        on = i < filled
        fade = i - (filled - 4)
        op = 1.0 if (not on or fade <= 0) else [1.0, 0.7, 0.5, 0.35][min(fade, 3)]
        out += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-opacity="%s" stroke-width="%s" stroke-linecap="round"/>' % (
            x1, y1, x2, y2, C['primary'] if on else C['track'], op, sw)
    return out


def dash(x1, y1, x2, y2):
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1" stroke-dasharray="4 5"/>' % (x1, y1, x2, y2, C['hair'])


def table_head(x, y, w, cols):
    """cols: [(label, dx, anchor)]. Kepala tabel = teks kecil + satu garis rambut."""
    s = ''.join(text(x + dx, y + 20, lab.upper(), 12, 600, 'sub', anc, ls=0.8) for lab, dx, anc in cols)
    return s + hair(x, y + 32, x + w, y + 32)


HL = {'lex': ('redTint', 'red'), 'sem': ('orangeTint', 'orange'), 'sty': ('yellowTint', 'yellow')}


_WIDTHS = json.load(open(os.path.join(HERE, 'assets', 'outfit-widths.json')))['w']


def mw(s, size, weight=400):
    """Lebar teks Outfit yang sebenarnya (tabel hasil ukur di browser), tanpa kerning."""
    t = _WIDTHS[str(min((400, 500, 600, 700), key=lambda w: abs(w - weight)))]
    return round(sum(t.get(ch, 55) for ch in s) * size / 100.0, 1)


def rich(x, y, segs, size=15, k=0.5, base='ink'):
    """Teks dengan highlight per tier. segs: str | (str, 'lex'|'sem'|'sty'). Lebar dari tabel huruf asli, spasi alami (tanpa textLength)."""
    out, cx = '', x
    gap = mw(' ', size)
    for s in segs:
        txt, hl = (s, None) if isinstance(s, str) else s
        lead = len(txt) - len(txt.lstrip())
        txt = txt.strip()
        if lead and cx > x:
            cx += gap
        w = mw(txt, size, 500 if hl else 400)
        if hl:
            tint, line = HL[hl]
            out += rect(cx, y - size, w, size + 8, tint, 3) + rect(cx, y + 5, w, 2, line)
        out += '<text x="%s" y="%s" font-size="%s" font-weight="%s" fill="%s">%s</text>' % (
            round(cx, 1), y, size, 500 if hl else 400, C['ink'] if hl else C[base], esc(txt))
        cx += w
        if len(s if isinstance(s, str) else s[0]) > len((s if isinstance(s, str) else s[0]).rstrip()):
            cx += gap
    return out


def topnav_public(items, active):
    s = rect(48, 24, W - 96, 68, 'card', 34, filt='sh')
    s += brand(80, 65, 21)
    widths = [tw(i, 15, 0.55) + 36 for i in items]
    tot = sum(widths) + 16
    x0 = W / 2 - tot / 2
    s += rect(x0, 32, tot, 52, 'field', 26)
    cx = x0 + 8
    for lab, w in zip(items, widths):
        if lab == active:
            s += rect(cx, 38, w, 40, 'ink', 20)
        s += text(cx + w / 2, 63, lab, 15, 500, 'onDark' if lab == active else 'ink', 'middle')
        cx += w
    s += text(W - 264, 63, 'Masuk', 15, 500, 'ink') + btn(W - 200, 36, 120, 44, 'Daftar', 'secondary', 14.5)
    return s


def _bg(w, h):
    s = rect(0, 0, w, h, 'url(#gBg)')
    g = ''
    y = 0
    while y < h:
        for cx, cy, r, col, op in ((w - 200, y + 220, 250, 'auroraBlue', 0.32), (180, y + 760, 270, 'auroraCyan', 0.30), (w - 260, y + 1180, 250, 'auroraViolet', 0.30)):
            g += '<circle cx="%s" cy="%s" r="%s" fill="%s" fill-opacity="%s"/>' % (cx, cy, r, C[col], op)
        y += 1400
    return s + '<g filter="url(#orb)">' + g + '</g>'


def _grad():
    g = lambda i, a, b, x2, y2: ('<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="%s"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>\n' % (i, x2, y2, C[a], C[b]))
    shbtn = '<filter id="sh-btn" x="-20%%" y="-40%%" width="140%%" height="220%%"><feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#0B0F19" flood-opacity="0.26"/></filter>\n'
    glow = ('<linearGradient id="gGlow" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0.28"/></linearGradient>\n' % (C['primaryTint'], C['primaryLight']))
    bgg = ('<linearGradient id="gBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="0.55" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>\n' % (C['bg'], C['bgMid'], C['bgEnd']))
    return (shbtn + glow + bgg + '<filter id="orb" x="-60%%" y="-60%%" width="220%%" height="220%%"><feGaussianBlur stdDeviation="70"/></filter>\n' + g('gHero', 'primary', 'primaryLight', 1, 1) + g('gFilter', 'primary', 'primaryLight', 1, 0) + g('gDark', 'ink', 'inkSoft', 1, 1) +
            '<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="%s" stroke-opacity="0.35" stroke-width="2"/></pattern>\n' % C['onDark'] +
            '<filter id="sh-hero" x="-10%%" y="-10%%" width="120%%" height="140%%"><feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#1A73D9" flood-opacity="0.28"/></filter>\n')


def page(title, desc, w, h, body, defs=''):
    defs = _grad().replace('%%', '%') + defs
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-labelledby="t d">\n'
            '<title id="t">%s</title>\n<desc id="d">%s</desc>\n<defs>\n'
            '<style>@import url(\'https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&amp;display=swap\');'
            'text{font-family:\'Outfit\',\'Gilroy\',\'Poppins\',\'Helvetica Neue\',Arial,sans-serif}</style>\n'
            '<filter id="sh" x="-5%%" y="-5%%" width="110%%" height="120%%"><feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#8A98B8" flood-opacity="0.14"/></filter>\n'
            '<filter id="sh-sm" x="-10%%" y="-20%%" width="120%%" height="160%%"><feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#8A98B8" flood-opacity="0.25"/></filter>\n'
            '<filter id="glow" x="-20%%" y="-30%%" width="140%%" height="210%%"><feDropShadow dx="0" dy="8" stdDeviation="7" flood-color="#1A73D9" flood-opacity="0.35"/></filter>\n'
            '%s</defs>\n%s\n%s\n</svg>\n') % (w, h, w, h, esc(title), esc(desc), defs, _bg(w, h), body)
