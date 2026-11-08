"""Keluarga layar autentikasi (login, register, lupa sandi, reset sandi), laptop 1440.
Jalankan: python3 build_auth.py  -> ../laptop/auth/*.svg
Satu kerangka (kartu kaca + ilustrasi danau), satu fungsi render yang dikendalikan konfigurasi per state."""
import os
from vt_kit import C, HERE, W, text, rect, circle, card, field, btn, link, checkbox, banner, banner_h, spinner, strength, brand, page, tw

OUT = os.path.join(HERE, '..', 'laptop', 'auth')
FX, FW = 158, 370  # kolom form (koordinat kartu)

NAMA, EMAIL, INST = 'Rizky Pratama', 'rizky@nusantara.ac.id', 'Universitas Nusantara'
DOTS = '••••••••••'


def art_defs():
    d = '<radialGradient id="gOrb" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="%s"/><stop offset="0.72" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (C['primaryLight'], C['primary'], C['auroraBlue'])
    d += '<filter id="orbBlur" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="13"/></filter>'
    d += '<linearGradient id="gBand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="%s" stop-opacity="0.22"/><stop offset="0.5" stop-color="%s" stop-opacity="0.03"/><stop offset="1" stop-color="%s" stop-opacity="0.10"/></linearGradient>' % ((C['onDark'],) * 3)
    d += '<clipPath id="cardClip"><rect x="80" y="78" width="1040" height="740" rx="28"/></clipPath>'
    for i, (x0, x1) in enumerate(BANDS):
        d += '<clipPath id="band%d"><rect x="%d" y="78" width="%d" height="740"/></clipPath>' % (i, x0, x1 - x0)
    return d


BANDS = [(690, 800), (800, 910), (910, 1020), (1020, 1120)]
OFFS = [(-34, 8, 0.94), (-12, 3, 0.99), (12, -3, 1.04), (36, -8, 1.10)]  # dx, dy, skala orb per pita (efek bias kaca)


def art():
    cx, cy = 880, 448
    g = '<g clip-path="url(#cardClip)">'
    for i, (x0, x1) in enumerate(BANDS):
        dx, dy, sc = OFFS[i]
        g += '<g clip-path="url(#band%d)"><g transform="translate(%s %s) scale(%s) translate(%s %s)">' % (i, cx + dx, cy + dy, sc, -cx, -cy)
        g += '<circle cx="%s" cy="%s" r="238" fill="url(#gOrb)" filter="url(#orbBlur)"/>' % (cx, cy)
        g += '<circle cx="770" cy="330" r="70" fill="%s" fill-opacity="0.55" filter="url(#orbBlur)"/>' % C['auroraCyan']
        g += '<circle cx="990" cy="640" r="95" fill="%s" fill-opacity="0.5" filter="url(#orbBlur)"/>' % C['auroraViolet']
        g += '</g></g>'
        g += '<rect x="%d" y="78" width="%d" height="740" fill="url(#gBand)"/>' % (x0, x1 - x0)
        g += '<rect x="%d" y="78" width="2" height="740" fill="%s" fill-opacity="0.55"/>' % (x0, C['onDark'])
    g += '</g>'
    # wordmark dan tiga label kecil
    g += '<text x="%s" y="%s" font-size="46" font-weight="600" letter-spacing="1" fill="%s" text-anchor="middle">VeriText AI</text>' % (cx + 6, cy + 16, C['onDark'])
    for x, y, l1, l2 in [(900, 318, 'Tiga tier', 'pemeriksaan'), (752, 566, 'Laporan per', 'kalimat'), (968, 548, 'Sertifikat', 'terverifikasi QR')]:
        g += '<text x="%s" y="%s" font-size="12.5" fill="%s">%s</text><text x="%s" y="%s" font-size="12.5" fill="%s">%s</text>' % (x, y, C['onDark'], l1, x, y + 16, C['onDark'], l2)
    return g


def frame(inner, title, scrim=''):
    defs = '<g data-role="illustration">' + art_defs() + '</g>'
    b = '<g transform="translate(120 2)">' + card(80, 78, 1040, 740) + '<g data-role="illustration">' + art() + '</g>'
    b += brand(162, 137, 15.5) + text(371, 136, 'Verifikasi', 14, 600, 'sub') + text(498, 136, 'Bantuan', 14, 600, 'sub')
    b += inner + scrim + '</g>'
    return page('VeriText AI – ' + title, 'Layar autentikasi: ' + title + '.', W, 900, b, defs)


def head(eyebrow, title, sub_lines, link_txt=None, ey=291, ty=348, ts=44, sy=389):
    s = text(165, ey, eyebrow, 14, 600, 'sub', ls=0.4)
    s += '<text x="162" y="%s" font-size="%s" font-weight="600" letter-spacing="-0.8" fill="%s">%s<tspan fill="%s">.</tspan></text>' % (ty, ts, C['ink'], title, C['primary'])
    for i, ln in enumerate(sub_lines):
        s += text(165, sy + i * 22, ln, 15, 400, 'sub')
    if link_txt:
        s += link(165 + tw(sub_lines[-1], 15, 0.5) + 6, sy + (len(sub_lines) - 1) * 22, link_txt, 15)
    return s


def center(msg, sub=None):
    s = spinner(343, 430, 28, 'primary', 3.2) + text(343, 506, msg, 20, 600, 'ink', 'middle')
    if sub:
        s += text(343, 534, sub, 14, 400, 'sub', 'middle')
    return s


def form(y0, rows, banner_cfg=None, meter=None, check=None, buttons=None, tooltip=None, check_link=None):
    """rows: [[(label, value, state, icon, msg), ...], ...] (1 atau 2 isian per baris)."""
    s, y = '', y0
    if banner_cfg:
        msg, kind, dis = banner_cfg
        s += banner(FX, y, FW, msg, kind, dis)
        y += banner_h(msg) + 18
    row_y, last_msg = y, False
    for row in rows:
        row_y = y
        n = len(row)
        w = FW if n == 1 else (FW - 14) / 2.0
        has_msg = False
        for i, (lab, val, st, ic, msg) in enumerate(row):
            s += field(round(FX + i * (w + 14), 1), y, round(w, 1), lab, val, st, ic, msg)
            has_msg = has_msg or bool(msg)
        last_msg = has_msg
        y += 88 if has_msg else 68
    if meter:
        my = row_y + (88 if last_msg else 68)
        s += strength(FX, my, meter, FW)
        y = my + 26
    if check:
        s += checkbox(FX + 2, y - 4, check[0], check[1])
        if check_link:
            s += link(FX + FW, y + 11, check_link, 14, anchor='end')
        y += 38
    if buttons:
        sec, prim, kind = buttons
        if sec:
            s += btn(FX, y, 190, 48, sec[0], 'disabled' if sec[1] == 'dim' else 'secondary')
            s += btn(FX + 206, y, 164, 48, prim, kind)
        else:
            s += btn(FX, y, FW, 48, prim, kind)
        if tooltip:
            s += rect(FX, y + 58, 330, 54, 'card', 16, filt='sh') + text(FX + 16, y + 81, tooltip[0], 12.5, 500, 'ink') + text(FX + 16, y + 100, tooltip[1], 12.5, 500, 'ink')
        if kind == 'disabled' and prim.endswith('…'):
            s += spinner(FX + (206 + 82 if sec else 185) - tw(prim, 15, 0.52) / 2 - 20, y + 24, 8, 'sub', 2.2)
    return s


def save(name, svg):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + '.svg'), 'w') as f:
        f.write(svg)


# ---------------- login ----------------
def login(state):
    h = head('SELAMAT DATANG KEMBALI', 'Masuk ke VeriText AI', ['Belum punya akun? '], 'Daftar')
    em = ('Email institusi', 'nama@kampus.ac.id', 'ph', None, None)
    pw = ('Kata sandi', DOTS, 'focus', 'eye-off', None)
    ban = None
    prim, kind, sec = 'Masuk', 'primary', ('Google Kampus', 'ok')
    chk = ('Ingat sesi saya', False)
    filled_em = ('Email institusi', EMAIL, 'idle', None, None)
    filled_pw = ('Kata sandi', DOTS, 'idle', 'eye-off', None)
    inner = None
    if state == 'show-password-active':
        em, pw = filled_em, ('Kata sandi', 'Rahasia#2026', 'focus', 'eye', None)
    elif state == 'input-focus':
        em, pw = ('Email institusi', 'rizky@nusantara', 'focus', None, None), ('Kata sandi', 'Masukkan kata sandi', 'ph', 'eye-off', None)
    elif state == 'empty-field-validation':
        em, pw = ('Email institusi', '', 'error', None, 'Email wajib diisi'), ('Kata sandi', '', 'error', 'eye-off', 'Kata sandi wajib diisi')
    elif state == 'email-format-invalid':
        em, pw = ('Email institusi', 'rizky@nusantara', 'error', None, 'Format email institusi tidak valid'), filled_pw
    elif state == 'submitting-loading':
        em, pw = ('Email institusi', EMAIL, 'dim', None, None), ('Kata sandi', DOTS, 'dim', None, None)
        prim, kind, sec, chk = 'Memverifikasi…', 'disabled', ('Google Kampus', 'dim'), ('Ingat sesi saya', False)
    elif state == 'error-invalid-credentials':
        em, pw, ban = filled_em, filled_pw, ('Invalid email or password', 'red', True)
    elif state == 'error-account-inactive':
        em, pw, ban = filled_em, filled_pw, ('Akun Anda dinonaktifkan oleh Administrator.\nSilakan hubungi helpdesk akademik.', 'yellow', True)
    elif state == 'error-lockout-429':
        em, pw, ban = filled_em, filled_pw, ('Akun terkunci sementara demi keamanan.\nCoba kembali dalam 04:32', 'red', False)
    elif state == 'oauth-google-domain-rejected':
        ban = ('Akses ditolak. Hanya email institusi (.ac.id / .edu)\nyang diizinkan masuk lewat Google SSO.', 'red', True)
    elif state == 'success-redirect':
        em, pw, ban = ('Email institusi', EMAIL, 'dim', None, None), ('Kata sandi', DOTS, 'dim', None, None), ('Autentikasi berhasil. Mengalihkan ke workspace…', 'green', False)
        prim, kind, sec = 'Masuk', 'disabled', ('Google Kampus', 'dim')
    elif state == 'oauth-google-redirecting':
        inner = center('Mengarahkan ke Google Identity Service…', 'Anda akan kembali ke VeriText AI setelah masuk.')
    elif state == 'oauth-google-callback-processing':
        inner = center('Menyinkronkan profil Google Kampus…', 'Mohon tunggu sebentar.')
    if inner is None:
        inner = form(408, [[em], [pw]], ban, None, chk, (sec, prim, kind), None, 'Lupa sandi?')
    return frame(h + inner, 'Masuk (%s)' % state)


# ---------------- register ----------------
def register(state):
    h = head('MULAI GRATIS', 'Buat akun baru', ['Sudah punya akun? '], 'Masuk', ey=214, ty=262, ts=40, sy=292)
    f_nama, f_em, f_inst = ('Nama lengkap', 'Nama sesuai identitas akademik', 'ph', None, None), ('Email kampus', 'nama@kampus.ac.id', 'ph', None, None), ('Institusi / universitas', 'Nama universitas', 'ph', None, None)
    f_pw, f_cf = ('Kata sandi', '••••••••', 'ph', 'eye-off', None), ('Konfirmasi sandi', '••••••••', 'ph', 'eye-off', None)
    filled = [('Nama lengkap', NAMA, 'idle', None, None), ('Email kampus', EMAIL, 'idle', None, None), ('Institusi / universitas', INST, 'idle', None, None)]
    pw_f, cf_f = ('Kata sandi', DOTS[:8], 'idle', 'eye-off', None), ('Konfirmasi sandi', DOTS[:8], 'idle', 'eye-off', None)
    rows = [[f_nama], [f_em], [f_inst], [f_pw, f_cf]]
    ban, meter, chk, tip = None, None, ('Saya menyetujui pemrosesan naskah sesuai UU PDP No. 27/2022', True), None
    prim, kind, sec = 'Daftar', 'primary', ('Google Kampus', 'ok')
    if state == 'show-password-active':
        rows = [[filled[0]], [filled[1]], [filled[2]], [('Kata sandi', 'Rahasia#2026', 'focus', 'eye', None), cf_f]]
    elif state == 'show-confirm-password-active':
        rows = [[filled[0]], [filled[1]], [filled[2]], [pw_f, ('Konfirmasi sandi', 'Rahasia#2026', 'focus', 'eye', None)]]
    elif state == 'password-strength-meter':
        rows, meter = [[filled[0]], [filled[1]], [filled[2]], [('Kata sandi', 'Rahasia26', 'focus', 'eye-off', None), f_cf]], 2
    elif state == 'password-mismatch-error':
        rows, meter = [[filled[0]], [filled[1]], [filled[2]], [pw_f, ('Konfirmasi sandi', DOTS[:6], 'error', 'eye-off', 'Tidak cocok')]], 3
    elif state == 'pdp-uncheck-warning':
        rows = [[filled[0]], [filled[1]], [filled[2]], [pw_f, cf_f]]
        chk, tip, prim, kind = ('Saya menyetujui pemrosesan naskah sesuai UU PDP No. 27/2022', False), ('Persetujuan pemrosesan data wajib disetujui', 'sesuai regulasi privasi naskah akademik.'), 'Daftar', 'disabled'
    elif state == 'submitting-loading':
        d = lambda r: (r[0], r[1], 'dim', None, None)
        rows = [[d(filled[0])], [d(filled[1])], [d(filled[2])], [d(pw_f), d(cf_f)]]
        prim, kind, sec = 'Mendaftarkan…', 'disabled', ('Google Kampus', 'dim')
    elif state == 'error-duplicate-email':
        rows, ban = [[filled[0]], [('Email kampus', EMAIL, 'error', None, None)], [filled[2]], [pw_f, cf_f]], ('Email institusi sudah terdaftar.\nSilakan masuk atau gunakan email lain.', 'red', True)
    elif state == 'success-confirmation':
        h = head('PENDAFTARAN BERHASIL', 'Akun berhasil dibuat', ['Anda mendapat 1 saldo token uji coba gratis.', 'Silakan masuk untuk mulai mengaudit naskah.'], ey=291, ty=348, ts=44, sy=389)
        return frame(h + btn(FX, 470, 220, 48, 'Masuk sekarang', 'primary'), 'Daftar (%s)' % state)
    y0 = 316
    return frame(h + form(y0, rows, ban, meter, chk, (sec, prim, kind), tip), 'Daftar (%s)' % state)


# ---------------- lupa sandi ----------------
def forgot(state):
    sub = ['Masukkan email institusi terdaftar. Kami kirim tautan', 'pemulihan yang berlaku 15 menit.']
    h = head('PEMULIHAN AKUN', 'Lupa kata sandi', sub)
    em = ('Email institusi', 'nama@kampus.ac.id', 'focus', None, None)
    ban, prim, kind, sec = None, 'Kirim tautan', 'primary', ('Kembali masuk', 'ok')
    if state == 'submitting-loading':
        em, prim, kind, sec = ('Email institusi', EMAIL, 'dim', None, None), 'Mengirim…', 'disabled', ('Kembali masuk', 'dim')
    elif state == 'error-email-not-found':
        em, ban = ('Email institusi', 'tidak.dikenal@kampus.ac.id', 'idle', None, None), ('Jika email terdaftar di sistem, tautan pemulihan\ntelah dikirim ke kotak masuk Anda.', 'blue', False)
    elif state == 'rate-limited-429':
        em, ban, prim, kind = ('Email institusi', EMAIL, 'idle', None, None), ('Terlalu sering meminta tautan pemulihan.\nTunggu 5 menit sebelum mencoba kembali.', 'red', False), 'Kirim tautan', 'disabled'
    elif state == 'success-card':
        h = head('PEMULIHAN AKUN', 'Periksa email Anda', ['Tautan pemulihan telah dikirim ke email institusi.', 'Periksa folder Inbox atau Spam.'])
        return frame(h + banner(FX, 428, FW, 'Tautan berlaku 15 menit sejak dikirim.', 'green', False) + btn(FX, 504, 250, 48, 'Kembali ke halaman masuk', 'primary'), 'Lupa sandi (%s)' % state)
    return frame(h + form(432, [[em]], ban, None, None, (sec, prim, kind)), 'Lupa sandi (%s)' % state)


# ---------------- reset sandi ----------------
def reset(state):
    if state == 'token-verifying':
        return frame(head('KATA SANDI BARU', 'Setel ulang sandi', []) + center('Memverifikasi tautan pemulihan…', 'Token berlaku 15 menit.'), 'Reset sandi (%s)' % state)
    if state == 'token-invalid-expired':
        h = head('KATA SANDI BARU', 'Tautan tidak berlaku', ['Minta tautan pemulihan yang baru untuk melanjutkan.'])
        return frame(h + banner(FX, 420, FW, 'Tautan pemulihan tidak valid atau kedaluwarsa.\nAjukan permohonan baru.', 'red', False) + btn(FX, 516, 250, 48, 'Kembali ke Lupa Sandi', 'primary'), 'Reset sandi (%s)' % state)
    h = head('KATA SANDI BARU', 'Setel ulang sandi', ['Gunakan minimal 8 karakter dengan angka dan simbol.'])
    rows = [[('Kata sandi baru', 'Minimal 8 karakter', 'focus', 'eye-off', None)], [('Konfirmasi kata sandi baru', DOTS, 'ph', 'eye-off', None)]]
    prim, kind = 'Simpan kata sandi baru', 'primary'
    if state == 'submitting-loading':
        rows = [[('Kata sandi baru', DOTS, 'dim', None, None)], [('Konfirmasi kata sandi baru', DOTS, 'dim', None, None)]]
        prim, kind = 'Menyimpan…', 'disabled'
    body = h + form(420, rows, None, None, None, (None, prim, kind))
    scrim = ''
    if state == 'success-modal':
        scrim = rect(80, 78, 1040, 740, 'ink', 28, op=0.16) + rect(370, 333, 460, 230, 'card', 28, filt='sh')
        scrim += text(402, 395, 'Kata sandi diperbarui', 26, 600, 'ink') + text(402, 427, 'Silakan masuk dengan kata sandi baru Anda.', 15, 400, 'sub') + btn(402, 481, 160, 48, 'Masuk', 'primary')
        body = h + form(420, [[('Kata sandi baru', DOTS, 'dim', None, None)], [('Konfirmasi kata sandi baru', DOTS, 'dim', None, None)]], None, None, None, (None, 'Simpan kata sandi baru', 'disabled'))
    return frame(body, 'Reset sandi (%s)' % state, scrim)


LOGIN = ['default-idle', 'show-password-active', 'input-focus', 'empty-field-validation', 'email-format-invalid', 'submitting-loading', 'error-invalid-credentials', 'error-account-inactive',
         'error-lockout-429', 'oauth-google-redirecting', 'oauth-google-callback-processing', 'oauth-google-domain-rejected', 'success-redirect']
REGISTER = ['default-idle', 'show-password-active', 'show-confirm-password-active', 'password-strength-meter', 'password-mismatch-error', 'pdp-uncheck-warning', 'submitting-loading',
            'error-duplicate-email', 'success-confirmation']
FORGOT = ['default-idle', 'submitting-loading', 'success-card', 'error-email-not-found', 'rate-limited-429']
RESET = ['token-verifying', 'token-invalid-expired', 'form-idle', 'submitting-loading', 'success-modal']

if __name__ == '__main__':
    n = 0
    for pre, fn, states in [('login', login, LOGIN), ('register', register, REGISTER), ('forgot-password', forgot, FORGOT), ('reset-password', reset, RESET)]:
        for st in states:
            save('%s--%s' % (pre, st), fn(st))
            n += 1
    print('ok', n, 'layar auth')
