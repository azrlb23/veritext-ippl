"""Pemeriksa gaya VeriText. Jalankan dari docs/design/system:  python3 check_style.py

R1  fill/stroke/stop-color hanya dari token (di luar ilustrasi)
R2  ukuran font >= 12
R3  rect berbingkai hanya untuk fokus, error, dropzone, radio
R4  warna teks hanya dari daftar "text" di tokens.json
R5  paling banyak satu tombol primary per layar
R6  target sentuh tombol >= 44
R7  kontras (tabel "contrast" di tokens.json), dihitung dari token
R8  badge hanya untuk pengecualian: maks budget.badges per layar, tanpa label kembar
R9  anggaran warna: maks budget.accentHues warna status (hijau/oranye/merah) per layar
R10 tanpa ikon bertile berulang per baris (>=3 sejajar vertikal)
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vt_kit import TOK, C  # noqa: E402

HEX = {v.upper(): k for k, v in C.items()}
TEXT_OK = set(C[k].upper() for k in TOK['text'])
STROKE_ROLES = {'focus-ring', 'error-ring', 'dropzone', 'radio'}
BTN_ROLES = {'primary', 'secondary', 'disabled', 'danger'}


def lum(h):
    h = h.lstrip('#')
    ch = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255.0
        ch.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def tag(e):
    return e.tag.split('}')[-1]


def walk(e, illus=False):
    illus = illus or e.get('data-role') == 'illustration'
    yield e, illus
    for c in e:
        for x in walk(c, illus):
            yield x


def check_file(path):
    errs = []
    root = ET.parse(path).getroot()
    primaries = 0
    for e, illus in walk(root):
        t = tag(e)
        if t in ('style', 'filter', 'feDropShadow', 'title', 'desc') or illus:
            continue
        for attr in ('fill', 'stroke', 'stop-color'):
            v = e.get(attr)
            if v and v != 'none' and not v.startswith('url(') and v.upper() not in HEX:
                errs.append('R1 warna di luar token %s=%s <%s>' % (attr, v, t))
        if t == 'text':
            fs = float(e.get('font-size', '0'))
            if fs < TOK['font']['min']:
                errs.append('R2 font %.1f < %d: %s' % (fs, TOK['font']['min'], (e.text or '')[:30]))
            f = (e.get('fill') or '').upper()
            if f and f not in TEXT_OK:
                errs.append('R4 warna teks %s tidak boleh: %s' % (f, (e.text or '')[:30]))
        if t in ('rect', 'circle') and e.get('stroke') and e.get('data-role') not in STROKE_ROLES:
            errs.append('R3 bingkai tanpa peran sah <%s>' % t)
        role = e.get('data-role')
        if role == 'primary':
            primaries += 1
        if t == 'rect' and role in BTN_ROLES and float(e.get('height', '0')) < 44:
            errs.append('R6 tombol lebih pendek dari 44')
    if primaries > 1:
        errs.append('R5 %d tombol primary (maks 1)' % primaries)
    errs += check_badges(root) + check_hues(root) + check_icon_tiles(root)
    return errs


def check_badges(root):
    labels = [e.get('data-label') for e, il in walk(root) if not il and e.get('data-role') == 'badge']
    errs = []
    if len(labels) > TOK['budget']['badges']:
        errs.append('R8 %d badge (maks %d); baris normal = teks abu' % (len(labels), TOK['budget']['badges']))
    for l in set(labels):
        if labels.count(l) > 1:
            errs.append('R8 badge "%s" berulang %dx' % (l, labels.count(l)))
    return errs


HUE = {'green': 'hijau', 'orange': 'oranye', 'orangeTint': 'oranye', 'red': 'merah', 'redTint': 'merah',
       'yellow': 'kuning', 'yellowTint': 'kuning'}


def check_hues(root):
    used = set()
    for e, il in walk(root):
        if il:
            continue
        for attr in ('fill', 'stroke'):
            v = (e.get(attr) or '').upper()
            if v in HEX and HEX[v] in HUE:
                used.add(HUE[HEX[v]])
    if len(used) > TOK['budget']['accentHues']:
        return ['R9 %d warna status (%s), maks %d' % (len(used), ', '.join(sorted(used)), TOK['budget']['accentHues'])]
    return []


def check_icon_tiles(root):
    """Bentuk kecil berisi warna yang langsung diikuti ikon garis (<g> stroke) = kotak ikon."""
    errs = []
    cols = {}
    for parent, _ in walk(root):
        kids = list(parent)
        for a, b in zip(kids, kids[1:]):
            if tag(a) not in ('circle', 'rect') or tag(b) != 'g' or not b.get('stroke'):
                continue
            if a.get('data-role') or (a.get('fill') or 'none') == 'none':
                continue
            size = 2 * float(a.get('r', 0)) if tag(a) == 'circle' else min(float(a.get('width', 0)), float(a.get('height', 0)))
            if size <= 64:
                x = round(float(a.get('cx', a.get('x', 0))) / 10)
                cols[x] = cols.get(x, 0) + 1
    for x, n in cols.items():
        if n >= 3:
            errs.append('R10 %d ikon bertile sejajar vertikal (x~%d): ikon bertile per baris dilarang' % (n, x * 10))
    return errs


def check_contrast():
    errs = []
    for fg, bg, need, why in TOK['contrast']:
        r = ratio(C[fg], C[bg])
        if r < need:
            errs.append('R7 %s di atas %s = %.2f:1 < %.1f (%s)' % (fg, bg, r, need, why))
    return errs


def main():
    total = 0
    for e in check_contrast():
        print('ERROR', e)
        total += 1
    files = sorted(f for f in glob.glob(os.path.join(HERE, '..', 'laptop', '**', '*.svg'), recursive=True) if '_lama' not in f)
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    for f in files:
        errs = check_file(f)
        print(('OK    ' if not errs else 'GAGAL ') + os.path.basename(f))
        for e in errs:
            print('   ', e)
        total += len(errs)
    print('\n%d layar diperiksa, %d pelanggaran' % (len(files), total))
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
