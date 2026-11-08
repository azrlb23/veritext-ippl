"""Keluarga Layar Verifikasi Sertifikat QR Publik (laptop 1440 px).

Laman verifikasi publik resmi untuk memeriksa keaslian naskah akademik,
validitas tanda tangan digital SHA-256, dan catatan integritas ledger.
Desain mengadopsi struktur datar bertingkat tunggal (tanpa card-dalam-card),
palet 95% monokromatik utilitarian, dan tata letak terinspirasi dari referensi
eksekutif (header grup langsung di kanvas, pil netral, warna fungsional terarah).

Daftar 7 Layar (id: verify--*):
1. verify--empty-input-idle: Form input UUID & grid kartu standar integritas naskah
2. verify--camera-scanner-active: Viewfinder kamera pemindai QR dokumen fisik
3. verify--camera-permission-denied: Alert informatif akses kamera ditolak peramban
4. verify--verifying-loading: Indikator tahapan verifikasi hash kriptografis
5. verify--valid-certificate: Tampilan sertifikat sah resmi ber-QR Code & skor
6. verify--invalid-certificate: Peringatan kode sertifikat tidak ditemukan / palsu
7. verify--tampered-document-warning: Peringatan manipulasi naskah (checksum mismatch)

Keluaran: docs/design/laptop/verify/*.svg
"""
import os
import sys
from vt_kit import (C, HERE, W, mw, tw, text, rect, circle, hair, card, btn, link, ico, chevron,
                    field, progress, spinner, page, topnav_public)

OUT = os.path.join(HERE, '..', 'laptop', 'verify')
os.makedirs(OUT, exist_ok=True)

# Data contoh sertifikat resmi
CERT_UUID = "8f2a91c4-b7e1-4d90-a35c-7e6189df0123"
CERT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
TAMPERED_HASH = "a71b28d5f3094892c902781bcf739481bc920381749204918239017238120391"
DOC_TITLE = "Dampak Perubahan Iklim terhadap Ketahanan Pangan Lokal di Wilayah Pesisir"
DOC_AUTHOR = "Rizky Pratama · NIM 11241045"
DOC_FACULTY = "Fakultas Teknik Lingkungan & Ketahanan Maritim"
AUDIT_DATE = "03 Nov 2026, 09.12 WIB (Kedalaman: Hibrida Leksikal + Semantik)"


def qr_code(x, y, s=110):
    """Render QR Code SVG matriks bersih dengan token warna resmi."""
    b = rect(x, y, s, s, 'card', 10)
    
    def marker(mx, my):
        return (rect(mx, my, 26, 26, 'ink', 4) +
                rect(mx + 4, my + 4, 18, 18, 'card', 2) +
                rect(mx + 7, my + 7, 12, 12, 'ink', 2))
                
    b += marker(x + 10, y + 10)
    b += marker(x + s - 36, y + 10)
    b += marker(x + 10, y + s - 36)
    
    import random
    r = random.Random(42)
    step = 6.2
    for row in range(14):
        for col in range(14):
            dx = x + 12 + col * step
            dy = y + 12 + row * step
            if (col < 5 and row < 5) or (col > 8 and row < 5) or (col < 5 and row > 8):
                continue
            if r.random() > 0.45:
                b += rect(dx, dy, 4.8, 4.8, 'ink', 1)
    return b


def pill_row(x, y, labels, gap=8):
    """Deretan pill netral abu-abu tanpa warna mencolok (seperti [Good Read] di referensi)."""
    b = ''
    cx = x
    for l in labels:
        w = tw(l, 12, 0.58) + 20
        b += rect(cx, y, w, 24, 'field', 12)
        b += text(cx + w / 2, y + 16, l, 12, 500, 'sub', 'middle')
        cx += w + gap
    return b


def card_top_meta(x, y, w, tag, badge_txt, sub_txt, right_val=None, right_color='sub'):
    """Header baris atas dalam kartu (seperti [checkbox] ES 2 Long +$432.50 ...)."""
    b = rect(x, y, 14, 14, 'field', 4)  # checkbox netral
    b += text(x + 24, y + 11.5, tag, 12.5, 600, 'ink')
    tag_w = tw(tag, 12.5, 0.58)
    
    # Small pill badge netral
    bx = x + 24 + tag_w + 10
    bw = tw(badge_txt, 12, 0.58) + 16
    b += rect(bx, y - 2, bw, 20, 'field', 10)
    b += text(bx + bw / 2, y + 12, badge_txt, 12, 500, 'sub', 'middle')
    
    # Sub metadata
    b += text(bx + bw + 10, y + 11.5, sub_txt, 12, 400, 'sub')
    
    # Kanan: Nilai data / Status & Titik Tiga
    rx = x + w
    if right_val:
        rw = tw(right_val, 13, 0.58)
        b += text(rx - 28, y + 11.5, right_val, 13, 600, right_color, 'end')
    b += text(rx, y + 11.5, '···', 14, 500, 'sub', 'end')
    return b


def group_header(x, y, w, title, sub_meta, right_label='Total Naskah', right_val=None, rc='green'):
    """Header grup langsung di kanvas tanpa kotak kartu pembungkus."""
    b = rect(x, y - 10, 14, 14, 'field', 4)  # checkbox
    b += text(x + 24, y + 1.5, title, 13.5, 600, 'ink')
    tw_title = tw(title, 13.5, 0.58)
    b += text(x + 24 + tw_title + 14, y + 1.5, sub_meta, 12.5, 400, 'sub')
    if right_val:
        rx = x + w
        rw = tw(right_val, 13.5, 0.58)
        b += text(rx - rw - 10, y + 1.5, right_label, 12.5, 500, 'sub', 'end')
        b += text(rx, y + 1.5, right_val, 13.5, 600, rc, 'end')
    return b


def verify_header():
    """Header portal publik bersih dan minimalis."""
    b = topnav_public(['Fitur', 'Pipeline', 'Koleksi', 'Verifikasi'], 'Verifikasi')
    
    # Breadcrumb & Hero Title langsung di atas kanvas
    b += text(48, 126, 'Portal Integritas Publik  /  Verifikasi Sertifikat', 12, 600, 'sub')
    b += text(48, 154, 'Verifikasi Keaslian Sertifikat & Naskah Ilmiah', 24, 600, 'ink', ls=-0.4)
    b += text(48, 178, 'Pemeriksaan keaslian sertifikat audit naskah akademik berbasis tanda tangan digital SHA-256.', 13.5, 400, 'sub')
    return b


def search_bar(y=202, active_tab='input', val='', state='idle', err_type=None, has_primary=False):
    """Bilah pencarian input tunggal bersih tanpa card pembungkus raksasa."""
    b = ''
    btn_kind = 'secondary' if (has_primary or err_type or state == 'loading') else 'primary'
    
    if active_tab == 'input':
        f_state = 'error' if err_type in ('invalid', 'tampered') else state
        b += field(48, y, 1020, 'Nomor UUID Sertifikat (36 karakter, contoh: 8f2a91c4-b7e1-4d90-a35c-7e6189df0123)', val, state=f_state)
        b += btn(1084, y, 308, 48, 'Verifikasi Sertifikat →', btn_kind, 14)
        b += text(48, y + 70, 'Format UUID 36-karakter tertera pada footer sertifikat audit naskah VeriText AI.', 12.5, 400, 'sub')
        b += link(W - 48, y + 70, 'Beralih ke Pemindai QR Dokumen Fisik ->', 12.5, anchor='end')
    else:
        # Camera mode toggle
        b += rect(48, y, 1020, 48, 'field', 14)
        b += circle(74, y + 24, 5, 'green')
        b += text(92, y + 29, 'Mode Pemindai Kamera Aktif · Mengarahkan ke Barcode Dokumen Fisik', 13.5, 500, 'ink')
        b += btn(1084, y, 308, 48, 'Beralih ke Input Manual', 'secondary', 14)
        b += text(48, y + 70, 'Arahkan kamera ke kode QR fisik atau klik tombol di samping untuk mengetik kode.', 12.5, 400, 'sub')
        
    return b


# -----------------------------------------------------------------------------
# 1. EMPTY INPUT IDLE STATE (Dua Baris Kartu Tunggal tanpa Nested Card)
# -----------------------------------------------------------------------------
def pane_empty_idle(y=306):
    """Tampilan idle datar: Header grup di kanvas + kartu-kartu bersih satu tingkat."""
    b = ''
    col_w = (W - 96 - 48) // 3  # 432px each
    
    # Header Baris 1 langsung di kanvas
    b += group_header(48, y, W - 96, 'Standar & Jaringan Integritas Naskah', '3 Kluster Aktif', 'Total Terindeks', '1.420.850', 'green')
    
    # Row 1: 3 Kartu Datar Bersih (y=328, h=276)
    y1 = y + 24
    cards_row1 = [
        ('MULTI-TIER', '2 Mesin', 'Leksikal & Semantik',
         'Verifikasi Multi-Dimensi',
         'Pemeriksaan naskah melalui algoritma Winnowing n-gram dan pencarian semantik vektor IndoBERT 768-dimensi.',
         ['Winnowing 50-Dim', 'pgvector HNSW']),
        ('SHA-256', 'Blok #182.904', '4 Node Konsensus',
         'Buku Besar Digital (Ledger)',
         'Pencatatan tanda tangan kriptografis Ed25519 dan checksum dokumen nirkolusi untuk jaminan orisinalitas.',
         ['SHA-256 Digest', 'Ed25519 W3C']),
        ('REGULASI DIKTI', 'Permendikbud', 'Presisi 99,98%',
         'Kepatuhan & Sertifikasi',
         'Sesuai pedoman Permendikbudristek No. 39/2021 dan standar format metadata sertifikat terbuka OpenCerts 2.0.',
         ['Permendikbud 39/2021', 'OpenCerts 2.0']),
    ]
    for i, (tag, b_txt, s_txt, c_title, c_desc, pills) in enumerate(cards_row1):
        cx = 48 + i * (col_w + 24)
        b += card(cx, y1, col_w, 276)
        b += card_top_meta(cx + 20, y1 + 24, col_w - 40, tag, b_txt, s_txt)
        b += text(cx + 20, y1 + 72, c_title, 16, 600, 'ink')
        
        # Multi-line deskripsi rapi
        words = c_desc.split(' ')
        line1 = ' '.join(words[:7])
        line2 = ' '.join(words[7:14])
        line3 = ' '.join(words[14:])
        b += text(cx + 20, y1 + 102, line1, 13, 400, 'sub')
        b += text(cx + 20, y1 + 122, line2, 13, 400, 'sub')
        if line3:
            b += text(cx + 20, y1 + 142, line3, 13, 400, 'sub')
            
        b += hair(cx + 20, y1 + 220, cx + col_w - 20, y1 + 220)
        b += pill_row(cx + 20, y1 + 236, pills)
        b += ico('doc', cx + col_w - 32, y1 + 248, 'sub', 1.1)
        
    # Header Baris 2 langsung di kanvas
    y2_header = y1 + 276 + 32  # 636
    b += group_header(48, y2_header, W - 96, 'Panduan Verifikasi bagi Penguji Sidang & Mahasiswa', '3 Tahap Cepat', 'Layanan Publik', 'Online 24/7', 'sub')
    
    # Row 2: 3 Kartu Panduan (y=660, h=276)
    y2 = y2_header + 24
    cards_row2 = [
        ('LANGKAH 01', 'Tahap Awal', 'Format 8-4-4-4-12',
         '1. Periksa Nomor UUID',
         'Pastikan 36 karakter alfanumerik tercetak jelas di footer sertifikat naskah. Masukkan kode lengkap dengan tanda pemisah strip (-).',
         ['Sensitif Huruf', 'Standar UUID']),
        ('LANGKAH 02', 'Kamera Fisik', 'Pemindai Barcode',
         '2. Pindai Barcode QR',
         'Arahkan kamera smartphone ke QR Code sertifikat fisik untuk membuka tautan verifikasi resmi secara langsung tanpa mengetik.',
         ['Resolusi Otomatis', 'URL Resmi']),
        ('LANGKAH 03', 'Kriptografi', 'Konsensus Ledger',
         '3. Rekonsiliasi Checksum',
         'Dosen penguji membandingkan nilai hash SHA-256 naskah dengan arsip ledger untuk memastikan naskah belum pernah diubah.',
         ['64-Digit Hash', 'Nirkolusi']),
    ]
    for i, (tag, b_txt, s_txt, c_title, c_desc, pills) in enumerate(cards_row2):
        cx = 48 + i * (col_w + 24)
        b += card(cx, y2, col_w, 276)
        b += card_top_meta(cx + 20, y2 + 24, col_w - 40, tag, b_txt, s_txt)
        b += text(cx + 20, y2 + 72, c_title, 16, 600, 'ink')
        
        words = c_desc.split(' ')
        line1 = ' '.join(words[:7])
        line2 = ' '.join(words[7:14])
        line3 = ' '.join(words[14:])
        b += text(cx + 20, y2 + 102, line1, 13, 400, 'sub')
        b += text(cx + 20, y2 + 122, line2, 13, 400, 'sub')
        if line3:
            b += text(cx + 20, y2 + 142, line3, 13, 400, 'sub')
            
        b += hair(cx + 20, y2 + 220, cx + col_w - 20, y2 + 220)
        b += pill_row(cx + 20, y2 + 236, pills)
        b += ico('doc', cx + col_w - 32, y2 + 248, 'sub', 1.1)
        
    return b


# -----------------------------------------------------------------------------
# 2. CAMERA SCANNER ACTIVE STATE
# -----------------------------------------------------------------------------
def pane_camera_scanner(y=306):
    """Viewfinder kamera pemindai barcode fisik dengan layout bersih satu tingkat."""
    b = ''
    vw = 880
    cw = W - 96 - vw - 24  # 440px
    h_panel = 630
    
    # Header grup langsung di kanvas
    b += group_header(48, y, W - 96, 'Mode Pemindai Optik Kamera Aktif', 'Webcam 1080p @ 60 FPS', 'Status Sensor', 'Mengunci Fokus…', 'sub')
    
    y1 = y + 24
    # Card 1: Viewfinder Kamera Bersih
    b += card(48, y1, vw, h_panel)
    
    # Interior viewport kamera gelap
    vx = 68
    vy = y1 + 20
    v_width = vw - 40
    v_height = h_panel - 80
    b += rect(vx, vy, v_width, v_height, 'ink', 14)
    
    # Top HUD
    b += circle(vx + 24, vy + 28, 5, 'red')
    b += text(vx + 38, vy + 32.5, 'WEBCAM LIVE STREAM (1080p @ 60 FPS) · ISO-18004 DECODER', 12, 500, 'placeholder')
    b += hair(vx, vy + 48, vx + v_width, vy + 48)
    
    # Center Reticle Box
    cx = vx + v_width // 2
    cy = vy + v_height // 2
    rw = 260
    rh = 260
    rx = cx - rw // 2
    ry = cy - rh // 2
    
    # Bracket corners
    bl = 28
    b += hair(rx, ry, rx + bl, ry)
    b += hair(rx, ry, rx, ry + bl)
    b += hair(rx + rw, ry, rx + rw - bl, ry)
    b += hair(rx + rw, ry, rx + rw, ry + bl)
    b += hair(rx, ry + rh, rx + bl, ry + rh)
    b += hair(rx, ry + rh, rx, ry + rh - bl)
    b += hair(rx + rw, ry + rh, rx + rw - bl, ry + rh)
    b += hair(rx + rw, ry + rh, rx + rw, ry + rh - bl)
    # Center line & laser
    b += hair(cx - 16, cy, cx + 16, cy)
    b += hair(cx, cy - 16, cx, cy + 16)
    b += hair(rx + 14, cy - 20, rx + rw - 14, cy - 20)
    
    # Bottom viewport text
    b += text(cx, vy + v_height - 30, 'Arahkan QR Code cetak pada dokumen fisik ke dalam area bingkai target', 13, 500, 'placeholder', 'middle')
    
    # Bawah viewport di dalam kartu utama
    b += text(48 + 24, y1 + h_panel - 26, 'Sensor optik otomatis membaca kode begitu posisi barcode stabil.', 12.5, 400, 'sub')
    b += link(48 + vw - 24, y1 + h_panel - 26, 'Beralih ke Input 36-Digit Manual →', 12.5, anchor='end')
    
    # Card 2: Panduan & Telemetri
    rx_col = 48 + vw + 24
    b += card(rx_col, y1, cw, h_panel)
    b += card_top_meta(rx_col + 24, y1 + 24, cw - 48, 'SENSOR OPTIK', 'Real-Time', 'Fokus Otomatis', '···')
    b += text(rx_col + 24, y1 + 72, 'Panduan Pemindaian Cepat', 17, 600, 'ink')
    b += text(rx_col + 24, y1 + 96, 'Pemeriksaan otomatis bekerja dalam hitungan milidetik begitu QR Code terfokus.', 13, 400, 'sub')
    
    b += hair(rx_col + 24, y1 + 128, rx_col + cw - 24, y1 + 128)
    
    # Baris informasi tanpa kartu di dalamnya
    meta_rows = [
        ('Jarak Sensor Ideal', '20 – 30 cm dari dokumen'),
        ('Pencahayaan Ruang', 'Optimal (Hindari pantulan silau)'),
        ('Kecepatan Deteksi', '< 200 ms saat fokus terkunci'),
        ('Format Kode', 'QR-Code ISO/IEC 18004'),
    ]
    for i, (mlbl, mval) in enumerate(meta_rows):
        my = y1 + 148 + i * 44
        b += text(rx_col + 24, my + 14, mlbl, 12.5, 400, 'sub')
        b += text(rx_col + cw - 24, my + 14, mval, 12.5, 600, 'ink', 'end')
        b += hair(rx_col + 24, my + 28, rx_col + cw - 24, my + 28)
        
    b += text(rx_col + 24, y1 + 350, 'STATUS KALIBRASI SENSOR:', 12, 600, 'sub')
    checks = [
        'Kecerahan Ruang: 88% (Sangat Baik)',
        'Kontras Tepi: 94/100 (Optimal)',
        'Orientasi Bidik: Sejajar / Tegak Lurus',
    ]
    for i, chk in enumerate(checks):
        b += text(rx_col + 24, y1 + 376 + i * 24, '•  ' + chk, 12.5, 400, 'sub')
        
    b += hair(rx_col + 24, y1 + 470, rx_col + cw - 24, y1 + 470)
    b += pill_row(rx_col + 24, y1 + 490, ['Auto-Focus', 'High-Contrast', '60 FPS'])
    b += btn(rx_col + 24, y1 + 546, cw - 48, 48, 'Beralih ke Input Kode UUID Manual', 'secondary', 13.5)
    
    return b


# -----------------------------------------------------------------------------
# 3. CAMERA PERMISSION DENIED STATE
# -----------------------------------------------------------------------------
def pane_camera_denied(y=306):
    """Tampilan saat izin kamera ditolak oleh peramban."""
    b = ''
    vw = 880
    cw = W - 96 - vw - 24  # 440px
    h_panel = 630
    
    # Header grup langsung di kanvas
    b += group_header(48, y, W - 96, 'Status Akses Perangkat Keras', 'Pemberitahuan Sistem Peramban', 'Status Izin', 'Akses Ditolak', 'red')
    
    y1 = y + 24
    # Card 1: Panduan Pemulihan Peramban
    b += card(48, y1, vw, h_panel)
    b += card_top_meta(48 + 24, y1 + 24, vw - 48, 'STATUS IZIN', 'Diblokir', 'Kamera Web', '···')
    b += text(48 + 24, y1 + 72, 'Akses Kamera Ditolak oleh Peramban', 18, 600, 'red')
    b += text(48 + 24, y1 + 96, 'Peramban memblokir izin kamera untuk situs ini. Ikuti panduan pemulihan berdasarkan peramban Anda di bawah:', 13.5, 400, 'sub')
    
    b += hair(48 + 24, y1 + 128, 48 + vw - 24, y1 + 128)
    
    # 3 baris bersih tanpa kartu di dalam kartu
    steps = [
        ('1. Google Chrome & Microsoft Edge',
         'Klik ikon gembok pada bilah alamat URL > Kamera > Ubah ke "Izinkan" > Muat ulang halaman ini.'),
        ('2. Apple Safari (macOS & iPadOS)',
         'Buka menu Safari > Pengaturan untuk Situs Web Ini > Kamera > Pilih "Izinkan" pada daftar dropdown.'),
        ('3. Mozilla Firefox',
         'Klik ikon kamera bergaris merah di bilah alamat situs > Hapus centang pada opsi "Diblokir Sementara".'),
    ]
    for i, (st, sd) in enumerate(steps):
        sy = y1 + 154 + i * 90
        b += text(48 + 24, sy, st, 14, 600, 'ink')
        b += text(48 + 24, sy + 24, sd, 13, 400, 'sub')
        b += hair(48 + 24, sy + 56, 48 + vw - 24, sy + 56)
        
    b += btn(48 + 24, y1 + 546, 260, 48, 'Muat Ulang Perizinan Kamera', 'secondary', 14)
    
    # Card 2: Alternatif Input Manual
    rx_col = 48 + vw + 24
    b += card(rx_col, y1, cw, h_panel)
    b += card_top_meta(rx_col + 24, y1 + 24, cw - 48, 'ALTERNATIF', 'Manual', 'Tanpa Kamera', '···')
    b += text(rx_col + 24, y1 + 72, 'Verifikasi Manual Kode UUID', 17, 600, 'ink')
    b += text(rx_col + 24, y1 + 96, 'Anda tetap dapat memverifikasi keabsahan dokumen tanpa menggunakan sensor kamera.', 13, 400, 'sub')
    
    b += hair(rx_col + 24, y1 + 128, rx_col + cw - 24, y1 + 128)
    b += text(rx_col + 24, y1 + 160, 'Ketikkan 36-karakter kode UUID yang tertera di sertifikat:', 12.5, 400, 'sub')
    b += field(rx_col + 24, y1 + 180, cw - 48, 'Nomor UUID Sertifikat', '8f2a91c4-b7e1-4d90-a35c-7e6189df0123')
    
    # Tombol primer tunggal pada layar ini
    b += btn(rx_col + 24, y1 + 260, cw - 48, 48, 'Verifikasi Kode Manual →', 'primary', 14)
    
    b += hair(rx_col + 24, y1 + 340, rx_col + cw - 24, y1 + 340)
    b += text(rx_col + 24, y1 + 372, 'Punya berkas sertifikat digital dalam format PDF?', 12.5, 400, 'sub')
    b += link(rx_col + 24, y1 + 398, 'Unggah Berkas PDF Dokumen →', 13)
    b += pill_row(rx_col + 24, y1 + 490, ['Format 8-4-4-4-12', 'Enkripsi SSL'])
    
    return b


# -----------------------------------------------------------------------------
# 4. VERIFYING LOADING STATE
# -----------------------------------------------------------------------------
def pane_loading(y=306):
    """Indikator tahapan verifikasi hash kriptografis bersih."""
    b = ''
    cw = 900
    cx = (W - cw) // 2
    h_panel = 580
    
    b += group_header(48, y, W - 96, 'Pengecekan Integritas Kriptografis', 'Mencocokkan Rekaman Ledger', 'Status', 'Sedang Memproses…', 'sub')
    
    y1 = y + 24
    b += card(cx, y1, cw, h_panel)
    b += card_top_meta(cx + 24, y1 + 24, cw - 48, 'PIPELINE VALIDASI', '4 Tahap', 'Konsensus PTN', '···')
    
    # Spinner di tengah
    b += spinner(cx + cw // 2, y1 + 86, 20, 'primary', 3.0)
    b += text(cx + cw // 2, y1 + 136, 'Memvalidasi Tanda Tangan Digital Naskah…', 19, 600, 'ink', 'middle')
    b += text(cx + cw // 2, y1 + 160, 'Mencocokkan nilai checksum SHA-256 pada pangkalan data ledger terdistribusi.', 13.5, 400, 'sub', 'middle')
    
    b += hair(cx + 40, y1 + 194, cx + cw - 40, y1 + 194)
    
    # 4 Baris Checklist Bersih
    nodes = [
        ('Tahap 1: Pencarian Nomor UUID pada Indeks Ledger', 'Selesai (142 ms)', 'done'),
        ('Tahap 2: Perhitungan Checksum SHA-256 Dokumen', 'Sedang memproses…', 'active'),
        ('Tahap 3: Verifikasi Tanda Tangan Digital Kunci Ed25519', 'Menunggu giliran', 'idle'),
        ('Tahap 4: Rekonsiliasi Korpus & Rekaman Konsensus', 'Menunggu giliran', 'idle'),
    ]
    for i, (nl, ns, nstate) in enumerate(nodes):
        ny = y1 + 218 + i * 46
        if nstate == 'done':
            b += text(cx + 40, ny + 14, '[V]', 12, 600, 'green')
            b += text(cx + 66, ny + 14, nl, 13.5, 600, 'ink')
            b += text(cx + cw - 40, ny + 14, ns, 12.5, 600, 'green', 'end')
        elif nstate == 'active':
            b += text(cx + 40, ny + 14, '[*]', 12, 600, 'primaryInk')
            b += text(cx + 66, ny + 14, nl, 13.5, 600, 'primaryInk')
            b += text(cx + cw - 40, ny + 14, ns, 12.5, 600, 'primaryInk', 'end')
        else:
            b += text(cx + 40, ny + 14, '[-]', 12, 400, 'placeholder')
            b += text(cx + 66, ny + 14, nl, 13.5, 400, 'sub')
            b += text(cx + cw - 40, ny + 14, ns, 12.5, 400, 'placeholder', 'end')
        b += hair(cx + 40, ny + 28, cx + cw - 40, ny + 28)
        
    # Kemajuan
    py = y1 + 424
    b += text(cx + 40, py, 'Kemajuan Verifikasi Kriptografis:', 12.5, 500, 'sub')
    b += text(cx + cw - 40, py, '48%', 12.5, 600, 'primaryInk', 'end')
    b += progress(cx + 40, py + 12, cw - 80, 48)
    
    b += text(cx + 40, y1 + 510, 'Pemberitahuan Privasi: Seluruh komputasi dilakukan secara terenkripsi tanpa menyimpan isi naskah Anda.', 12.5, 400, 'sub')
    b += pill_row(cx + 40, y1 + 534, ['SHA-256 Kriptografis', 'Ed25519 W3C', 'Zero-Knowledge'])
    
    return b


# -----------------------------------------------------------------------------
# 5. VALID CERTIFICATE STATE (Struktur Kredensial Tunggal tanpa Nested Card)
# -----------------------------------------------------------------------------
def pane_valid_certificate(y=306):
    """Tampilan Sertifikat Resmi Ber-QR Code & Skor (Struktur Datar tanpa Card-dalam-Card)."""
    b = ''
    vw = 880
    cw = W - 96 - vw - 24  # 440px
    h_panel = 630
    
    # Header grup langsung di kanvas dengan nilai hijau fungsional
    b += group_header(48, y, W - 96, 'Sertifikat Audit Integritas Naskah · Lulus Uji', 'ID: 8f2a91c4-b7e1-4d90-a35c-7e6189df0123', 'Status Dokumen', 'Terdaftar Resmi & Sah', 'green')
    
    y1 = y + 24
    # Card 1: Dokumen Kredensial Akademik Resmi
    b += card(48, y1, vw, h_panel)
    b += card_top_meta(48 + 24, y1 + 24, vw - 48, 'INSTITUT TEKNOLOGI NUSANTARA', 'Lembaga Audit Resmi', 'Fakultas Teknik Lingkungan', '···')
    
    b += text(48 + 24, y1 + 72, DOC_TITLE, 18, 600, 'ink')
    b += text(48 + 24, y1 + 96, 'Surat keterangan hasil uji keaslian naskah akademik berstandar Permendikbudristek No. 39/2021.', 13, 400, 'sub')
    
    b += hair(48 + 24, y1 + 124, 48 + vw - 24, y1 + 124)
    
    # Metadata baris demi baris bersih tanpa kartu di dalam kartu
    doc_meta = [
        ('PENULIS / PENELITI', DOC_AUTHOR),
        ('PROGRAM STUDI', DOC_FACULTY),
        ('WAKTU PENGUJIAN', AUDIT_DATE + ' · 14.820 Kata · 48 Halaman'),
        ('NOMOR UUID IDENTIFIKASI', CERT_UUID),
        ('SHA-256 HASH DOKUMEN', CERT_HASH),
        ('TANDA TANGAN DIGITAL', 'ED25519-SIG: 4a9f82c1b9... (Tervalidasi Konsensus Blok #182.904)'),
    ]
    for i, (lbl, val) in enumerate(doc_meta):
        my = y1 + 146 + i * 54
        b += text(48 + 24, my + 14, lbl, 12, 600, 'sub')
        tc = 'green' if i == 5 else ('primaryInk' if i == 3 else 'ink')
        b += text(48 + 24, my + 34, val, 13.5, 500, tc)
        b += hair(48 + 24, my + 44, 48 + vw - 24, my + 44)
        
    b += pill_row(48 + 24, y1 + 580, ['Leksikal 12,4%', 'Semantik 18,6%', 'Stilometri 8,2%', 'OpenCerts 2.0'])
    b += ico('doc', 48 + vw - 36, y1 + 592, 'sub', 1.1)
    
    # Card 2: Skor & QR Code Validasi
    rx_col = 48 + vw + 24
    b += card(rx_col, y1, cw, h_panel)
    b += card_top_meta(rx_col + 24, y1 + 24, cw - 48, 'HASIL EVALUASI', 'Lulus Ambang', 'Ambang Batas: 20%', '···')
    
    b += text(rx_col + 24, y1 + 72, 'SKOR KEMIRIPAN KOMPOSIT', 12, 600, 'sub')
    # Angka hijau besar terfokus (seperti +$432.50 di referensi)
    b += text(rx_col + 24, y1 + 116, '18,4%', 36, 600, 'green', ls=-1)
    b += text(rx_col + 144, y1 + 98, 'Kategori Aman (<20%)', 14, 600, 'green')
    b += text(rx_col + 144, y1 + 118, 'Lulus Uji Integritas Akademik', 12.5, 400, 'sub')
    
    b += hair(rx_col + 24, y1 + 148, rx_col + cw - 24, y1 + 148)
    
    # QR Code Centered
    qx = rx_col + (cw - 110) // 2
    b += qr_code(qx, y1 + 176, 110)
    b += text(rx_col + cw // 2, y1 + 312, 'Pindai barcode untuk verifikasi langsung melalui peramban smartphone.', 12, 400, 'sub', 'middle')
    
    b += hair(rx_col + 24, y1 + 346, rx_col + cw - 24, y1 + 346)
    
    checks = [
        'Tanda Tangan Kriptografis: Sah & Terdaftar',
        'Checksum Naskah: Identik (0 Deviasi)',
        'Konsensus Blok: 4 Validator Terverifikasi',
    ]
    for i, chk in enumerate(checks):
        b += text(rx_col + 24, y1 + 372 + i * 22, '[OK] ' + chk, 12.5, 400, 'sub')
        
    # Tombol primer tunggal pada layar ini
    b += btn(rx_col + 24, y1 + 474, cw - 48, 48, 'Unduh Sertifikat PDF Resmi', 'primary', 14)
    b += link(rx_col + cw // 2, y1 + 546, 'Salin Tautan Validasi Publik [Link]', 13, anchor='middle')
    b += pill_row(rx_col + 24, y1 + 580, ['PDF/A-1a Standar', 'Buku Besar'])
    
    return b


# -----------------------------------------------------------------------------
# 6. INVALID CERTIFICATE STATE
# -----------------------------------------------------------------------------
def pane_invalid_certificate(y=306):
    """Tampilan diagnostik kegagalan pencarian kode sertifikat tidak terdaftar."""
    b = ''
    vw = 880
    cw = W - 96 - vw - 24  # 440px
    h_panel = 630
    
    # Header grup langsung di kanvas dengan nilai merah fungsional
    b += group_header(48, y, W - 96, 'Hasil Penelusuran Identifikasi Sertifikat', 'Query: 99999999-0000-4000-8000-000000000000', 'Status Catatan', 'Tidak Terdaftar (404)', 'red')
    
    y1 = y + 24
    # Card 1: Hasil Penelusuran
    b += card(48, y1, vw, h_panel)
    b += card_top_meta(48 + 24, y1 + 24, vw - 48, 'STATUS PENCARIAN', '404 Not Found', 'Pemeriksaan Ledger', '···')
    b += text(48 + 24, y1 + 72, 'Kode Sertifikat Tidak Ditemukan', 18, 600, 'red')
    b += text(48 + 24, y1 + 96, 'Nomor UUID 99999999-0000-4000-8000-000000000000 tidak tercatat dalam pangkalan data integritas resmi VeriText AI.', 13.5, 400, 'sub')
    
    b += hair(48 + 24, y1 + 128, 48 + vw - 24, y1 + 128)
    
    # Baris checklist investigasi
    investigations = [
        ('Hasil Penelusuran Sistem', '0 kecocokan dari 1.420.850 rekaman ledger konsorsium perguruan tinggi.'),
        ('1. Periksa Kembali Format Kode UUID', 'Pastikan format kode adalah 8-4-4-4-12 karakter alfanumerik lengkap dengan 4 tanda strip (-).'),
        ('2. Periksa Status Penyelesaian Uji', 'Naskah yang masih berada dalam antrean pemrosesan belum memiliki sertifikat resmi hingga audit selesai.'),
        ('3. Verifikasi Institusi Penerbit', 'Pastikan perguruan tinggi atau institusi penguji telah terdaftar dalam kemitraan resmi VeriText AI.'),
    ]
    for i, (ititle, idesc) in enumerate(investigations):
        iy = y1 + 154 + i * 72
        b += text(48 + 24, iy, ititle, 13.5, 600, 'ink')
        b += text(48 + 24, iy + 22, idesc, 12.5, 400, 'sub')
        b += hair(48 + 24, iy + 44, 48 + vw - 24, iy + 44)
        
    b += btn(48 + 24, y1 + 546, 260, 48, 'Coba Periksa Kode Lain', 'secondary', 14)
    b += pill_row(48 + 310, y1 + 558, ['Bantuan Verifikasi', 'Pusat Layanan'])
    
    # Card 2: Panduan Pencegahan Pemalsuan
    rx_col = 48 + vw + 24
    b += card(rx_col, y1, cw, h_panel)
    b += card_top_meta(rx_col + 24, y1 + 24, cw - 48, 'KEAMANAN', 'Cegah Pemalsuan', 'Edukasi', '···')
    b += text(rx_col + 24, y1 + 72, 'Pencegahan Pemalsuan Dokumen', 17, 600, 'ink')
    b += text(rx_col + 24, y1 + 96, 'Sertifikat resmi selalu memiliki tanda tangan digital yang tersinkronisasi dengan ledger institusi.', 13, 400, 'sub')
    
    b += hair(rx_col + 24, y1 + 128, rx_col + cw - 24, y1 + 128)
    
    cues = [
        ('Stempel Verifikasi Dinamis', 'QR Code asli selalu merujuk ke domain resmi institusi terverifikasi.'),
        ('Kunci SHA-256 Otentik', 'Terdapat 64 digit heksadesimal checksum dokumen yang unik.'),
        ('Tanda Tangan Digital Terbuka', 'Diverifikasi langsung oleh konsorsium validator node perguruan tinggi.'),
    ]
    for i, (ct, cd) in enumerate(cues):
        cy_b = y1 + 154 + i * 72
        b += text(rx_col + 24, cy_b, ct, 13.5, 600, 'ink')
        b += text(rx_col + 24, cy_b + 22, cd, 12, 400, 'sub')
        b += hair(rx_col + 24, cy_b + 44, rx_col + cw - 24, cy_b + 44)
        
    b += text(rx_col + 24, y1 + 412, 'Menemukan indikasi manipulasi atau pemalsuan?', 13, 600, 'ink')
    b += text(rx_col + 24, y1 + 434, 'Laporkan ke Satuan Pengawas Internal kampus untuk investigasi etik.', 12.5, 400, 'sub')
    
    # Tombol primer tunggal pada layar ini
    b += btn(rx_col + 24, y1 + 480, cw - 48, 48, 'Laporkan Dugaan Pemalsuan →', 'primary', 14)
    b += pill_row(rx_col + 24, y1 + 558, ['Pelaporan SPI', 'Anti-Plagiasi'])
    
    return b


# -----------------------------------------------------------------------------
# 7. TAMPERED DOCUMENT WARNING STATE
# -----------------------------------------------------------------------------
def pane_tampered_warning(y=306):
    """Peringatan Kritis: Manipulasi Naskah Terdeteksi (Checksum Mismatch)."""
    b = ''
    vw = 880
    cw = W - 96 - vw - 24  # 440px
    h_panel = 630
    
    # Header grup langsung di kanvas dengan status merah
    b += group_header(48, y, W - 96, 'Hasil Verifikasi Kriptografis Naskah', 'ID: 8f2a91c4-b7e1-4d90-a35c-7e6189df0123', 'Status Integritas', 'Checksum Mismatch (Batal)', 'red')
    
    y1 = y + 24
    # Card 1: Komparasi Hash & Ringkasan Perubahan
    b += card(48, y1, vw, h_panel)
    b += card_top_meta(48 + 24, y1 + 24, vw - 48, 'INTEGRITAS DOKUMEN', 'Modifikasi Terdeteksi', 'Ketidaksesuaian Hash', '···')
    b += text(48 + 24, y1 + 72, 'Peringatan: Naskah Telah Dimodifikasi Pasca-Audit', 18, 600, 'red')
    b += text(48 + 24, y1 + 96, 'Nilai hash SHA-256 berkas fisik berbeda dari rekaman asli saat sertifikat diterbitkan. Dokumen tidak sah.', 13.5, 500, 'red')
    
    b += hair(48 + 24, y1 + 128, 48 + vw - 24, y1 + 128)
    
    # Komparasi Hash (Langsung di kartu tanpa kotak nested)
    b += text(48 + 24, y1 + 154, 'HASH RESMI TERDAFTAR (LEDGER 03 NOV 2026):', 12, 600, 'sub')
    b += text(48 + vw - 24, y1 + 154, 'STATUS: ASLI TERCATAT', 12, 600, 'green', 'end')
    b += text(48 + 24, y1 + 176, CERT_HASH, 12.5, 600, 'ink')
    
    b += hair(48 + 24, y1 + 196, 48 + vw - 24, y1 + 196)
    
    b += text(48 + 24, y1 + 224, 'HASH BERKAS YANG DIUJI SAAT INI (MODIFIKASI):', 12, 600, 'sub')
    b += text(48 + vw - 24, y1 + 224, 'STATUS: BERBEDA (BATAL)', 12, 600, 'red', 'end')
    b += text(48 + 24, y1 + 246, TAMPERED_HASH, 12.5, 600, 'red')
    
    b += hair(48 + 24, y1 + 266, 48 + vw - 24, y1 + 266)
    
    b += text(48 + 24, y1 + 296, 'RINGKASAN ANOMALI & PERUBAHAN ISI NASKAH (FORENSIC DIFF):', 12, 600, 'sub')
    diffs = [
        ('Halaman 4, Alinea 2', 'Teks hasil pengujian ditambahkan 3 alinea baru tanpa verifikasi ulang sitasi.'),
        ('Halaman 7, Tabel 3', 'Angka statistik signifikansi diubah secara manual dari 14% menjadi 42%.'),
        ('Halaman 12, Bibliografi', 'Urutan referensi jurnal dan nomor DOI dimodifikasi setelah audit selesai.'),
    ]
    for i, (dl, dd) in enumerate(diffs):
        dy = y1 + 322 + i * 46
        b += text(48 + 24, dy, '•  ' + dl + ':', 12.5, 600, 'red')
        b += text(48 + 220, dy, dd, 12.5, 400, 'ink')
        b += hair(48 + 24, dy + 22, 48 + vw - 24, dy + 22)
        
    b += text(48 + 24, y1 + 480, 'Pemberitahuan Hukum: Perubahan isi naskah membatalkan sertifikat ini secara otomatis.', 12.5, 600, 'red')
    b += text(48 + 24, y1 + 504, 'Segala bentuk penggunaan sertifikat ini untuk keperluan kelulusan / yudisium dianggap tidak sah.', 12.5, 400, 'sub')
    
    b += btn(48 + 24, y1 + 546, 260, 48, 'Bandingkan Versi Naskah', 'secondary', 14)
    b += pill_row(48 + 310, y1 + 558, ['Forensik Checksum', 'Integritas Naskah'])
    
    # Card 2: Metadata Arsip Asli
    rx_col = 48 + vw + 24
    b += card(rx_col, y1, cw, h_panel)
    b += card_top_meta(rx_col + 24, y1 + 24, cw - 48, 'ARSIP ASLI', 'Blok #182.904', 'ITN Jakarta', '···')
    b += text(rx_col + 24, y1 + 72, 'Metadata Arsip Naskah', 17, 600, 'ink')
    b += text(rx_col + 24, y1 + 96, 'Data arsip naskah asli yang tersimpan dalam repositori konsorsium perguruan tinggi.', 13, 400, 'sub')
    
    b += hair(rx_col + 24, y1 + 128, rx_col + cw - 24, y1 + 128)
    
    meta_rows = [
        ('ID Registrasi', 'VT-2026-ITN-SKR-0892'),
        ('Penulis Asli', 'Rizky Pratama (11241045)'),
        ('Waktu Audit Asli', '03 Nov 2026, 09.12 WIB'),
        ('Skor Asli', '18,4% (Lolos Batas Uji)'),
    ]
    for i, (mlbl, mval) in enumerate(meta_rows):
        my = y1 + 154 + i * 44
        b += text(rx_col + 24, my + 14, mlbl, 12.5, 400, 'sub')
        b += text(rx_col + cw - 24, my + 14, mval, 12.5, 600, 'ink', 'end')
        b += hair(rx_col + 24, my + 28, rx_col + cw - 24, my + 28)
        
    b += text(rx_col + 24, y1 + 360, 'TINDAKAN EVALUATOR & DEKANAT:', 12, 600, 'sub')
    b += text(rx_col + 24, y1 + 386, 'Dosen pembimbing dan panitia ujian disarankan mengunduh berkas salinan naskah asli versi arsip ledger.', 12.5, 400, 'sub')
    
    # Tombol primer tunggal pada layar ini
    b += btn(rx_col + 24, y1 + 450, cw - 48, 48, 'Unduh Berkas Asli Terarsip', 'primary', 14)
    b += link(rx_col + cw // 2, y1 + 524, 'Eskalasi ke Komisi Etik Kampus →', 13, anchor='middle')
    b += pill_row(rx_col + 24, y1 + 558, ['Arsip Dokumen', 'Komisi Etik'])
    
    return b


# -----------------------------------------------------------------------------
# BUILD ALL SCREENS
# -----------------------------------------------------------------------------
def build_all():
    """Membangun 7 layar keluarga Verifikasi Sertifikat QR Publik (laptop 1440 px)."""
    print("Membangun keluarga layar Verifikasi Sertifikat QR (laptop 1440 px)...")
    
    # 1. verify--empty-input-idle
    svg1 = page(
        'Verifikasi Sertifikat - VeriText AI',
        'Laman publik validasi keaslian sertifikat audit naskah akademik.',
        W, 1020, verify_header() + search_bar(202, active_tab='input') + pane_empty_idle(306)
    )
    with open(os.path.join(OUT, 'verify--empty-input-idle.svg'), 'w') as f:
        f.write(svg1)
        
    # 2. verify--camera-scanner-active
    svg2 = page(
        'Pindai QR Sertifikat - VeriText AI',
        'Viewfinder kamera aktif pemindai barcode QR sertifikat fisik.',
        W, 1020, verify_header() + search_bar(202, active_tab='camera') + pane_camera_scanner(306)
    )
    with open(os.path.join(OUT, 'verify--camera-scanner-active.svg'), 'w') as f:
        f.write(svg2)
        
    # 3. verify--camera-permission-denied
    svg3 = page(
        'Izin Kamera Ditolak - VeriText AI',
        'Pemberitahuan izin kamera diblokir peramban dengan opsi verifikasi manual.',
        W, 1020, verify_header() + search_bar(202, active_tab='camera', has_primary=True) + pane_camera_denied(306)
    )
    with open(os.path.join(OUT, 'verify--camera-permission-denied.svg'), 'w') as f:
        f.write(svg3)
        
    # 4. verify--verifying-loading
    svg4 = page(
        'Memvalidasi Sertifikat - VeriText AI',
        'Indikator tahapan loading saat server memverifikasi hash SHA-256 dokumen.',
        W, 1020, verify_header() + search_bar(202, active_tab='input', val=CERT_UUID, state='loading') + pane_loading(306)
    )
    with open(os.path.join(OUT, 'verify--verifying-loading.svg'), 'w') as f:
        f.write(svg4)
        
    # 5. verify--valid-certificate
    svg5 = page(
        'Sertifikat Terverifikasi Sah - VeriText AI',
        'Tampilan sertifikat keaslian resmi naskah akademik dengan skor dan QR.',
        W, 1020, verify_header() + search_bar(202, active_tab='input', val=CERT_UUID, has_primary=True) + pane_valid_certificate(306)
    )
    with open(os.path.join(OUT, 'verify--valid-certificate.svg'), 'w') as f:
        f.write(svg5)
        
    # 6. verify--invalid-certificate
    svg6 = page(
        'Sertifikat Tidak Ditemukan - VeriText AI',
        'Peringatan saat kode UUID sertifikat tidak terdaftar atau tidak valid.',
        W, 1020, verify_header() + search_bar(202, active_tab='input', val='99999999-0000-4000-8000-000000000000', err_type='invalid', has_primary=True) + pane_invalid_certificate(306)
    )
    with open(os.path.join(OUT, 'verify--invalid-certificate.svg'), 'w') as f:
        f.write(svg6)
        
    # 7. verify--tampered-document-warning
    svg7 = page(
        'Peringatan Manipulasi Naskah - VeriText AI',
        'Peringatan integritas naskah dimanipulasi setelah proses audit resmi.',
        W, 1020, verify_header() + search_bar(202, active_tab='input', val=CERT_UUID, err_type='tampered', has_primary=True) + pane_tampered_warning(306)
    )
    with open(os.path.join(OUT, 'verify--tampered-document-warning.svg'), 'w') as f:
        f.write(svg7)
        
    print("Berhasil membangun 7 SVG keluarga Verifikasi Sertifikat QR di laptop/verify/.")


if __name__ == '__main__':
    build_all()
