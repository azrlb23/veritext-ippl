"""Keluarga Layar Dompet Token & Billing (laptop 1440 px).

Pola mengikuti build_dashboard.py:
- Topnav: menu 'Billing' aktif.
- Header: judul 'Dompet Token & Riwayat Faktur', subjudul, saldo aktif.
- Area konten:
  1. Kartu Saldo Kuota Aktif & ringkasan pemakaian.
  2. 3 Pilihan Paket Kuota Token: Starter (5 Token), Pro Academic (20 Token), Campus Institutional (100 Token).
  3. Tabel Riwayat Pembayaran & Faktur Resmi PDF.
- Modal & State:
  - billing--default-idle
  - billing--topup-modal-open (pilih metode QRIS / VA)
  - billing--payment-qris-display (QRIS dinamis)
  - billing--payment-va-display (nomor Virtual Account)
  - billing--payment-polling-checking (status polling konfirmasi bayar)
  - billing--payment-success-modal (notifikasi bayar sukses)
  - billing--payment-expired (notifikasi sesi bayar kedaluwarsa)
  - billing--empty-history (tabel invoice kosong)
  - billing--history-desktop-table (tabel invoice terisi)
  - billing--invoice-downloading-spinner (indikator mengunduh faktur PDF)
- Keluaran: docs/design/laptop/billing/*.svg
"""
import os
import sys
from vt_kit import (C, HERE, W, mw, text, rect, circle, hair, card, btn, link, ico, chevron,
                    segmented, select, progress, spinner, badge, segarc, dash, page, table_head)

OUT = os.path.join(HERE, '..', 'laptop', 'billing')
os.makedirs(OUT, exist_ok=True)

# Data contoh transaksi invoice (ditandai contoh buatan):
INVOICES = [
    ("INV-2026-8812", "02 Nov 2026, 14.15 WIB", "Paket Pro Academic (20 Token)", "Rp80.000", "QRIS Mandiri", "Lunas"),
    ("INV-2026-8104", "18 Okt 2026, 09.30 WIB", "Paket Starter (5 Token)", "Rp25.000", "BCA Virtual Account", "Lunas"),
    ("INV-2026-7491", "28 Sep 2026, 11.20 WIB", "Paket Starter (5 Token)", "Rp25.000", "QRIS Gopay", "Lunas"),
    ("INV-2026-6920", "12 Sep 2026, 16.45 WIB", "Paket Pro Academic (20 Token)", "Rp80.000", "BNI Virtual Account", "Lunas"),
]

PLANS = [
    ("Starter Mahasiswa", "5 Token", "Rp25.000", "Rp5.000 / audit", "Cukup untuk 2x audit Hybrid penuh atau 5x audit Leksikal cepat.", "doc", False),
    ("Pro Academic", "20 Token", "Rp80.000", "Rp4.000 / audit", "Hemat 20%. Direkomendasikan untuk penyusunan skripsi, tesis, dan publikasi jurnal.", "coin", True),
    ("Campus Bulk", "100 Token", "Rp350.000", "Rp3.500 / audit", "Hemat 30%. Kuota fleksibel tanpa batas kedaluwarsa untuk laboratorium riset.", "stack", False),
]


def billing_header(tokens=3, has_modal=False):
    """Header topnav + breadcrumb + judul & kuota."""
    b = ''
    from vt_kit import topnav
    b += topnav(['Dashboard', 'Audit', 'Korpus', 'Billing', 'Admin'], 'Billing', 'Rizky Pratama', 'rizky@nusantara.ac.id', 'RP')
    
    b += text(48, 142, 'Manajemen Akun  /  Langganan & Kuota Pengujian Naskah', 13, 500, 'sub')
    b += text(48, 174, 'Dompet Token & Riwayat Faktur', 24, 600, 'ink', ls=-0.4)
    b += text(48, 200, 'Beli kuota pengujian sesuai kebutuhan (pay-as-you-go) tanpa biaya langganan bulanan', 13.5, 400, 'sub')
    
    # Saldo token baris ringkas kanan atas
    b += rect(1140, 146, 252, 52, 'field', 26)
    b += circle(1168, 172, 16, 'card')
    b += ico('coin', 1168, 172, 'primaryInk', 1.6)
    b += text(1194, 166, 'Saldo Aktif Anda', 12, 500, 'sub')
    b += text(1194, 186, '%d Token Uji' % tokens, 16, 600, 'ink')
    
    b += hair(48, 222, W - 48, 222)
    return b


def pane_plans(y=242, has_modal=False):
    """3 Kartu Paket Token Pilihan."""
    b = ''
    w_card = (W - 96 - 2 * 24) // 3
    
    for i, (name, tokens, price, per_unit, desc, ic, popular) in enumerate(PLANS):
        x = 48 + i * (w_card + 24)
        h_card = 230
        
        # Kartu kaca (highlight khusus untuk paket terpopuler Pro Academic)
        if popular:
            b += rect(x, y, w_card, h_card, 'card', 20, filt='sh')
            # Garis aksen biru atas
            b += rect(x + 24, y + 2, w_card - 48, 3, 'primary', 1.5)
            # Badge terpopuler
            b += rect(x + w_card - 110, y + 18, 86, 22, 'primaryTint', 11)
            b += text(x + w_card - 67, y + 33, 'TERPOPULER', 12, 600, 'primaryInk', 'middle')
        else:
            b += card(x, y, w_card, h_card)
            
        b += circle(x + 40, y + 42, 16, 'primaryTint' if popular else 'field')
        b += ico(ic, x + 40, y + 42, 'primaryInk' if popular else 'sub', 1.6)
        b += text(x + 66, y + 46, name, 16, 600, 'ink')
        
        # Angka Token & Harga
        b += text(x + 40, y + 92, tokens, 30, 600, 'ink', ls=-0.6)
        b += text(x + 40, y + 118, price, 18, 600, 'primaryInk')
        b += text(x + 40 + mw(price, 18, 600) + 8, y + 118, '· ' + per_unit, 12.5, 400, 'sub')
        
        # Keterangan
        b += text(x + 40, y + 148, desc[:48], 12.5, 400, 'sub')
        b += text(x + 40, y + 168, desc[48:], 12.5, 400, 'sub')
        
        # Tombol Beli: Paket terpopuler memakai 'primary' (jika modal tidak terbuka)
        btn_kind = 'secondary'
        if popular and not has_modal:
            btn_kind = 'primary'
        b += btn(x + 40, y + 176, w_card - 80, 44, 'Pilih Paket Ini →', btn_kind, 13.5)
        
    return b


def pane_invoices(y=496, empty=False, downloading=False):
    """Tabel Riwayat Transaksi & Pembayaran Faktur (menempel ke kanan, kiri, dan bawah layar)."""
    h_panel = 1020 - y  # 524 px membentang penuh hingga batas bawah kanvas (y=1020)
    b = ''
    # Panel penuh menempel ke kanan, kiri, dan bawah layar tanpa sisa celah latar
    b += rect(0, y, W, h_panel, 'card', filt='sh')
    b += hair(0, y, W, y)
    
    # Header Tabel
    b += text(48, y + 42, 'Riwayat Transaksi & Faktur Resmi', 18, 600, 'ink')
    b += text(48, y + 64, 'Unduh bukti pembayaran resmi bertanda tangan digital untuk pelaporan biaya riset', 13, 400, 'sub')
    
    cols = [
        ('NOMOR FAKTUR', 48, 'start'),
        ('TANGGAL TRANSAKSI', 220, 'start'),
        ('PAKET KUOTA', 460, 'start'),
        ('NOMINAL', 760, 'start'),
        ('METODE PEMBAYARAN', 940, 'start'),
        ('STATUS & FAKTUR', 1392, 'end'),
    ]
    for lab, x_pos, anc in cols:
        b += text(x_pos, y + 104, lab.upper(), 12, 600, 'sub', anc, ls=0.8)
    b += hair(0, y + 116, W, y + 116)
    
    if empty:
        cx, cy = W // 2, y + 270
        b += circle(cx, cy - 40, 30, 'field')
        b += ico('coin', cx, cy - 40, 'sub', 2.0)
        b += text(cx, cy + 20, 'Belum Ada Riwayat Transaksi', 18, 600, 'ink', 'middle')
        b += text(cx, cy + 44, 'Seluruh riwayat pembelian token dan bukti faktur resmi PDF akan tercatat di sini.', 13.5, 400, 'sub', 'middle')
        return b
        
    for i, (inv_no, date_lbl, plan_name, amount, method, status) in enumerate(INVOICES):
        ry = y + 130 + i * 68
        if i > 0:
            b += hair(0, ry - 14, W, ry - 14)
            
        b += text(48, ry + 16, inv_no, 14, 600, 'ink')
        b += text(220, ry + 16, date_lbl, 13, 400, 'sub')
        b += text(460, ry + 16, plan_name, 13.5, 500, 'ink')
        b += text(760, ry + 16, amount, 14, 600, 'ink')
        b += text(940, ry + 16, method, 13, 400, 'sub')
        
        # Kolom Status & Aksi (tanpa dot hijau, rata kanan rapi tanpa tabrakan)
        is_first_row_downloading = (i == 0 and downloading)
        if is_first_row_downloading:
            b += spinner(1260, ry + 12, 6.5, 'primary', 2.0)
            b += text(1392, ry + 16, 'Mengunduh PDF…', 13, 500, 'primaryInk', 'end')
        else:
            b += link(1392, ry + 16, 'Faktur PDF', 13, anchor='end')
            b += text(1313, ry + 16, '·', 13, 400, 'sub', 'middle')
            b += text(1300, ry + 16, status, 13, 500, 'green', 'end')
            
    # Paginasi di Bawah (menempel rapi dengan garis pemisah penuh ke batas bawah layar)
    py = 1020 - 46
    b += hair(0, py - 16, W, py - 16)
    b += text(48, py + 10, 'Menampilkan 1–4 dari 4 faktur pembelian', 13, 400, 'sub')
    b += text(1392, py + 10, 'Faktur tersimpan aman sesuai ketentuan perpajakan', 12.5, 400, 'sub', 'end')
    
    return b


def modal_topup_select():
    """Modal pilihan metode pembayaran (QRIS / VA)."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 270, 200, 540, 540
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += text(mx + 36, my + 44, 'Konfirmasi Pembelian Kuota', 20, 600, 'ink')
    b += text(mx + 36, my + 68, 'Paket Pro Academic (20 Token Uji Hibrida)', 13.5, 400, 'sub')
    b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round"><path d="M-6 -6L6 6M6 -6L-6 6"/></g>' % (mx + mw_box - 36, my + 44, C['sub'])
    b += hair(mx + 24, my + 88, mx + mw_box - 24, my + 88)
    
    # Ringkasan Biaya
    b += rect(mx + 36, my + 108, mw_box - 72, 94, 'field', 14)
    b += text(mx + 54, my + 134, 'Harga Paket 20 Token', 13, 400, 'sub')
    b += text(mx + mw_box - 54, my + 134, 'Rp80.000', 13.5, 500, 'ink', 'end')
    b += text(mx + 54, my + 158, 'PPN 11% (Faktur Resmi)', 13, 400, 'sub')
    b += text(mx + mw_box - 54, my + 158, 'Termasuk', 13, 500, 'sub', 'end')
    b += hair(mx + 54, my + 172, mx + mw_box - 54, my + 172)
    b += text(mx + 54, my + 192, 'Total Pembayaran', 14, 600, 'ink')
    b += text(mx + mw_box - 54, my + 192, 'Rp80.000', 18, 600, 'primaryInk', 'end')
    
    # Pilihan Metode Pembayaran
    b += text(mx + 36, my + 234, 'PILIH METODE PEMBAYARAN', 12, 600, 'sub', ls=0.8)
    
    # Opsi 1: QRIS
    b += rect(mx + 36, my + 248, mw_box - 72, 60, 'primaryTint', 14)
    b += circle(mx + 60, my + 278, 6, 'primary')
    b += text(mx + 76, my + 275, 'QRIS (BCA, Mandiri, GoPay, OVO, Dana)', 13.5, 600, 'primaryInk')
    b += text(mx + 76, my + 294, 'Verifikasi instan otomatis · Tanpa biaya transaksi', 12, 400, 'sub')
    
    # Opsi 2: Virtual Account
    b += rect(mx + 36, my + 318, mw_box - 72, 60, 'field', 14)
    b += circle(mx + 60, my + 348, 6, 'card')
    b += text(mx + 76, my + 345, 'Virtual Account Bank Mandiri / BCA / BNI', 13.5, 500, 'ink')
    b += text(mx + 76, my + 364, 'Transfer melalui ATM atau Mobile Banking', 12, 400, 'sub')
    
    # Tombol Lanjut Bayar (Satu tombol gelap primary)
    b += btn(mx + 36, my + 440, mw_box - 72, 48, 'Lanjut ke Pembayaran QRIS →', 'primary', 14)
    b += text(mx + mw_box // 2, my + 512, 'Pembayaran aman diverifikasi oleh payment gateway resmi berizin BI', 12, 400, 'sub', 'middle')
    
    return b


def modal_payment_qris(polling=False, expired=False):
    """Modal tampilan kode QRIS dinamis & countdown."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 250, 180, 500, 580
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += text(mx + mw_box // 2, my + 42, 'Pembayaran QRIS Nasional', 19, 600, 'ink', 'middle')
    b += text(mx + mw_box // 2, my + 64, 'Pindai menggunakan aplikasi mobile banking atau e-wallet', 13, 400, 'sub', 'middle')
    b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round"><path d="M-6 -6L6 6M6 -6L-6 6"/></g>' % (mx + mw_box - 36, my + 42, C['sub'])
    b += hair(mx + 24, my + 82, mx + mw_box - 24, my + 82)
    
    # Kotak QR Code
    q_size = 180
    qx, qy = mx + (mw_box - q_size) // 2, my + 104
    b += rect(qx, qy, q_size, q_size, 'field', 14)
    
    if expired:
        # State: expired
        b += circle(qx + q_size // 2, qy + q_size // 2, 28, 'redTint')
        b += ico('doc', qx + q_size // 2, qy + q_size // 2, 'red', 2.0)
        b += text(mx + mw_box // 2, my + 316, 'Sesi Pembayaran Kedaluwarsa', 16, 600, 'red', 'middle')
        b += text(mx + mw_box // 2, my + 338, 'Batas waktu 15 menit telah habis. Kode QR tidak lagi berlaku.', 12.5, 400, 'sub', 'middle')
        b += btn(mx + 48, my + 380, mw_box - 96, 48, 'Buat Pesanan Baru →', 'primary', 14)
    else:
        # Pola QR imitasi bersih dengan kotak-kotak sudut
        b += rect(qx + 16, qy + 16, 42, 42, 'ink', 6)
        b += rect(qx + 24, qy + 24, 26, 26, 'card', 3)
        b += rect(qx + 30, qy + 30, 14, 14, 'ink', 2)
        
        b += rect(qx + q_size - 58, qy + 16, 42, 42, 'ink', 6)
        b += rect(qx + q_size - 50, qy + 24, 26, 26, 'card', 3)
        b += rect(qx + q_size - 44, qy + 30, 14, 14, 'ink', 2)
        
        b += rect(qx + 16, qy + q_size - 58, 42, 42, 'ink', 6)
        b += rect(qx + 24, qy + q_size - 50, 26, 26, 'card', 3)
        b += rect(qx + 30, qy + q_size - 44, 14, 14, 'ink', 2)
        
        # Titik tengah QR
        b += rect(qx + 76, qy + 76, 28, 28, 'primary', 6)
        b += text(qx + 90, qy + 95, 'VT', 12, 700, 'onDark', 'middle')
        
        # Countdown & Nominal
        b += text(mx + mw_box // 2, my + 312, 'TOTAL PEMBAYARAN: Rp80.000', 16, 600, 'ink', 'middle')
        b += text(mx + mw_box // 2, my + 334, 'Berlaku dalam: 14 menit 42 detik', 12.5, 500, 'orange', 'middle')
        
        # Status Polling
        if polling:
            b += rect(mx + 48, my + 360, mw_box - 96, 46, 'field', 23)
            b += spinner(mx + 76, my + 383, 7, 'primary', 2.0)
            b += text(mx + 94, my + 388, 'Mengecek konfirmasi pembayaran gateway…', 12.5, 500, 'primaryInk')
        else:
            b += rect(mx + 48, my + 360, mw_box - 96, 46, 'field', 23)
            b += circle(mx + 76, my + 383, 4, 'orange')
            b += text(mx + 92, my + 388, 'Menunggu pembayaran dari bank / dompet digital…', 12.5, 400, 'sub')
            
        b += btn(mx + 48, my + 424, mw_box - 96, 48, 'Simulasi Pembayaran Berhasil (Sandbox)', 'secondary', 13.5)
        b += link(mx + mw_box // 2, my + 502, 'Ganti Metode Pembayaran Lain →', 13, anchor='middle')
        
    return b


def modal_payment_va():
    """Modal tampilan nomor Virtual Account."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 260, 200, 520, 520
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += text(mx + 36, my + 44, 'Pembayaran Virtual Account', 20, 600, 'ink')
    b += text(mx + 36, my + 68, 'Transfer tepat hingga digit terakhir agar otomatis terverifikasi', 13, 400, 'sub')
    b += '<g transform="translate(%s %s)" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round"><path d="M-6 -6L6 6M6 -6L-6 6"/></g>' % (mx + mw_box - 36, my + 44, C['sub'])
    b += hair(mx + 24, my + 88, mx + mw_box - 24, my + 88)
    
    # Kotak VA
    b += rect(mx + 36, my + 110, mw_box - 72, 100, 'field', 14)
    b += text(mx + 54, my + 138, 'NOMOR VIRTUAL ACCOUNT MANDIRI', 12, 600, 'sub', ls=0.8)
    b += text(mx + 54, my + 172, '8890 1124 1045 8812', 22, 600, 'ink', ls=1.0)
    b += rect(mx + mw_box - 120, my + 146, 66, 34, 'card', 17)
    b += text(mx + mw_box - 87, my + 168, 'Salin', 12.5, 600, 'primaryInk', 'middle')
    
    # Petunjuk Transfer
    b += text(mx + 36, my + 236, 'PETUNJUK TRANSFER ATM & M-BANKING', 12, 600, 'sub', ls=0.8)
    steps = [
        "1. Masuk ke aplikasi Livin' Mandiri atau ATM Mandiri terdekat.",
        "2. Pilih menu Bayar > Multi Payment > Masukkan kode 8890 (VeriText).",
        "3. Masukkan nomor VA di atas dan pastikan nominal tepat Rp80.000.",
        "4. Konfirmasi transaksi. Kuota token akan otomatis masuk dalam 5 detik."
    ]
    for i, s_txt in enumerate(steps):
        b += text(mx + 36, my + 262 + i * 24, s_txt, 12.5, 400, 'sub')
        
    b += btn(mx + 36, my + 386, mw_box - 72, 48, 'Saya Sudah Mentransfer', 'secondary', 14)
    b += text(mx + mw_box // 2, my + 466, 'Batas waktu pembayaran: 23 jam 59 menit', 12, 400, 'sub', 'middle')
    
    return b


def modal_payment_success():
    """Modal konfirmasi pembayaran berhasil & token bertambah."""
    b = rect(0, 0, W, 1020, 'ink', op=0.45)
    
    mx, my, mw_box, mh_box = W // 2 - 250, 220, 500, 420
    b += rect(mx, my, mw_box, mh_box, 'card', 24, filt='sh')
    
    b += circle(mx + mw_box // 2, my + 68, 28, 'greenTint')
    b += ico('check', mx + mw_box // 2, my + 68, 'green', 2.2)
    
    b += text(mx + mw_box // 2, my + 130, 'Pembayaran Berhasil!', 22, 600, 'ink', 'middle')
    b += text(mx + mw_box // 2, my + 156, 'Saldo Anda telah bertambah +20 Token Uji Hibrida.', 14, 500, 'ink', 'middle')
    b += text(mx + mw_box // 2, my + 178, 'Nomor Faktur: INV-2026-8812 · Total Bayar: Rp80.000', 13, 400, 'sub', 'middle')
    
    b += rect(mx + 48, my + 210, mw_box - 96, 68, 'field', 14)
    b += text(mx + 68, my + 238, 'Saldo Token Baru Anda:', 13, 400, 'sub')
    b += text(mx + mw_box - 68, my + 250, '23 Token', 22, 600, 'green', 'end')
    
    b += btn(mx + 48, my + 304, mw_box - 96, 48, 'Unduh Bukti Faktur PDF Resmi', 'primary', 14)
    b += link(mx + mw_box // 2, my + 382, 'Kembali ke Workspace Naskah →', 13.5, anchor='middle')
    
    return b


def build_all():
    """Membangun 10 layar keluarga Dompet Token & Billing (laptop 1440 px)."""
    print("Membangun keluarga layar Dompet Token & Billing (laptop 1440 px)...")
    
    # 1. Default Idle / Populated Table
    svg1 = page(
        'Dompet Token & Riwayat Faktur - VeriText AI',
        'Laman pembelian kuota token dan daftar faktur pembayaran resmi.',
        W, 1020, billing_header(tokens=3) + pane_plans(242) + pane_invoices(496)
    )
    with open(os.path.join(OUT, 'billing--default-idle.svg'), 'w') as f:
        f.write(svg1)
    with open(os.path.join(OUT, 'billing--history-desktop-table.svg'), 'w') as f:
        f.write(svg1)
        
    # 2. Topup Modal Open
    svg2 = page(
        'Konfirmasi Pembelian Kuota - VeriText AI',
        'Dialog modal konfirmasi pembelian token dan pemilihan metode bayar.',
        W, 1020, billing_header(tokens=3, has_modal=True) + pane_plans(242, has_modal=True) + pane_invoices(496) + modal_topup_select()
    )
    with open(os.path.join(OUT, 'billing--topup-modal-open.svg'), 'w') as f:
        f.write(svg2)
        
    # 3. Payment QRIS Display
    svg3 = page(
        'Pembayaran QRIS Nasional - VeriText AI',
        'Tampilan kode QRIS dinamis untuk pembayaran paket kuota.',
        W, 1020, billing_header(tokens=3, has_modal=True) + pane_plans(242, has_modal=True) + pane_invoices(496) + modal_payment_qris()
    )
    with open(os.path.join(OUT, 'billing--payment-qris-display.svg'), 'w') as f:
        f.write(svg3)
        
    # 4. Payment VA Display
    svg4 = page(
        'Pembayaran Virtual Account - VeriText AI',
        'Tampilan nomor Virtual Account Mandiri beserta petunjuk transfer.',
        W, 1020, billing_header(tokens=3, has_modal=True) + pane_plans(242, has_modal=True) + pane_invoices(496) + modal_payment_va()
    )
    with open(os.path.join(OUT, 'billing--payment-va-display.svg'), 'w') as f:
        f.write(svg4)
        
    # 5. Payment Polling Checking
    svg5 = page(
        'Verifikasi Pembayaran - VeriText AI',
        'State background polling mengecek konfirmasi webhook pembayaran dari gateway.',
        W, 1020, billing_header(tokens=3, has_modal=True) + pane_plans(242, has_modal=True) + pane_invoices(496) + modal_payment_qris(polling=True)
    )
    with open(os.path.join(OUT, 'billing--payment-polling-checking.svg'), 'w') as f:
        f.write(svg5)
        
    # 6. Payment Success Modal
    svg6 = page(
        'Pembayaran Berhasil - VeriText AI',
        'Notifikasi sukses saldo token bertambah dengan tombol unduh faktur PDF.',
        W, 1020, billing_header(tokens=23, has_modal=True) + pane_plans(242, has_modal=True) + pane_invoices(496) + modal_payment_success()
    )
    with open(os.path.join(OUT, 'billing--payment-success-modal.svg'), 'w') as f:
        f.write(svg6)
        
    # 7. Payment Expired
    svg7 = page(
        'Sesi Pembayaran Kedaluwarsa - VeriText AI',
        'Peringatan saat batas waktu 15 menit QRIS telah habis.',
        W, 1020, billing_header(tokens=3, has_modal=True) + pane_plans(242, has_modal=True) + pane_invoices(496) + modal_payment_qris(expired=True)
    )
    with open(os.path.join(OUT, 'billing--payment-expired.svg'), 'w') as f:
        f.write(svg7)
        
    # 8. Empty History
    svg8 = page(
        'Belum Ada Riwayat Transaksi - VeriText AI',
        'Tampilan empty state saat akun baru belum pernah melakukan pembelian token.',
        W, 1020, billing_header(tokens=1) + pane_plans(242) + pane_invoices(496, empty=True)
    )
    with open(os.path.join(OUT, 'billing--empty-history.svg'), 'w') as f:
        f.write(svg8)
        
    # 9. Invoice Downloading Spinner
    svg9 = page(
        'Mengunduh Faktur Resmi - VeriText AI',
        'Indikator spinner loading saat mengompilasi berkas PDF faktur pembayaran.',
        W, 1020, billing_header(tokens=3) + pane_plans(242) + pane_invoices(496, downloading=True)
    )
    with open(os.path.join(OUT, 'billing--invoice-downloading-spinner.svg'), 'w') as f:
        f.write(svg9)
        
    print("Berhasil membangun 10 SVG keluarga Dompet Token & Billing di laptop/billing/.")


if __name__ == '__main__':
    build_all()
