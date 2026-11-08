// Generator SVG halaman VeriText AI (frame laptop 1440px).
// Jalankan: node docs/svg/build-laptop.mjs  -> menulis ke docs/svg/laptop/
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const OUT = path.join(path.dirname(fileURLToPath(import.meta.url)), 'laptop');
fs.mkdirSync(OUT, { recursive: true });

const C = {
  ink: '#17191c', border: '#ededed', line: '#d4d4d4', muted: '#6b7280', soft: '#f5f5f4', bg: '#fafaf9', white: '#ffffff',
  blue: '#2563eb', red: '#ef4444', orange: '#f97316', yellow: '#eab308', green: '#16a34a',
};
const W = 1440;
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const tw = (s, size, k = 0.54) => String(s).length * size * k;

// ---------- primitives ----------
function T(x, y, s, o = {}) {
  const { size = 14, weight = 400, fill = C.ink, anchor = 'start', serif = false, mono = false, ls, tl } = o;
  return `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}"${serif ? ' class="s"' : ''}${mono ? ' class="m"' : ''}${ls ? ` letter-spacing="${ls}"` : ''}${tl ? ` textLength="${tl}" lengthAdjust="spacingAndGlyphs"` : ''}>${esc(s)}</text>`;
}
function R(x, y, w, h, o = {}) {
  const { r = 0, fill = 'none', stroke, sw = 1, dash, op } = o;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}"${r ? ` rx="${r}"` : ''} fill="${fill}"${stroke ? ` stroke="${stroke}" stroke-width="${sw}"` : ''}${dash ? ` stroke-dasharray="${dash}"` : ''}${op ? ` fill-opacity="${op}"` : ''}/>`;
}
const L = (x1, y1, x2, y2, stroke = C.border, sw = 1) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="${sw}"/>`;
const card = (x, y, w, h, o = {}) => R(x + 0.5, y + 0.5, w - 1, h - 1, { r: 8, fill: C.white, stroke: C.border, ...o });

function badge(x, y, text, color = C.muted, size = 11) {
  const w = tw(text, size, 0.6) + 16;
  return { w, svg: R(x, y, w, 22, { r: 11, fill: color, op: 0.12 }) + T(x + w / 2, y + 15, text, { size, weight: 600, fill: color, anchor: 'middle' }) };
}
function btn(x, y, w, h, label, v = 'primary', size = 14) {
  const st = {
    primary: { fill: C.ink, stroke: C.ink, tc: '#fff' },
    secondary: { fill: '#fff', stroke: C.line, tc: C.ink },
    danger: { fill: '#fff', stroke: '#fca5a5', tc: '#b91c1c' },
    disabled: { fill: '#f0f0ef', stroke: '#f0f0ef', tc: '#a3a3a3' },
    blue: { fill: C.blue, stroke: C.blue, tc: '#fff' },
  }[v];
  return R(x + 0.5, y + 0.5, w - 1, h - 1, { r: 8, fill: st.fill, stroke: st.stroke }) + T(x + w / 2, y + h / 2 + size * 0.36, label, { size, weight: 600, fill: st.tc, anchor: 'middle' });
}
function field(x, y, w, label, val, o = {}) {
  const { ph = false, focus = false, icon, hint } = o;
  let s = T(x, y, label, { size: 13, weight: 500 });
  s += R(x + 0.5, y + 8.5, w - 1, 44, { r: 8, fill: '#fff', stroke: focus ? C.ink : C.line, sw: focus ? 2 : 1 });
  s += T(x + 14, y + 36, val, { size: 14, fill: ph ? '#9ca3af' : C.ink });
  if (icon === 'eye-off') s += eyeOff(x + w - 26, y + 30);
  if (hint) s += T(x, y + 70, hint, { size: 12, fill: C.muted });
  return s;
}
function eyeOff(cx, cy, c = C.muted) {
  return `<g transform="translate(${cx} ${cy})" fill="none" stroke="${c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M-9 0Q0 -8 9 0Q0 8 -9 0Z"/><circle r="2.5"/><path d="M-8 -8L8 8"/></g>`;
}
function google(x, y, sc = 0.4) {
  return `<g transform="translate(${x} ${y}) scale(${sc})"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></g>`;
}
const check = (cx, cy, c = '#fff', s = 1) => `<path d="M${cx - 4 * s} ${cy}l${3 * s} ${3 * s} ${5 * s}-${6 * s}" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
function checkbox(x, y, label, on = true) {
  return R(x + 0.5, y + 0.5, 17, 17, { r: 4, fill: on ? C.ink : '#fff', stroke: on ? C.ink : C.line }) + (on ? check(x + 9, y + 9) : '') + T(x + 28, y + 14, label, { size: 13 });
}
function logo(x, y, light = false) {
  const fg = light ? '#fff' : C.ink, bg = light ? '#fff' : C.ink, tick = light ? C.ink : '#fff';
  return R(x, y, 24, 24, { r: 6, fill: bg }) + `<path d="M${x + 7} ${y + 12.5}l3.5 3.5 6.5-8" fill="none" stroke="${tick}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>` + T(x + 34, y + 18, 'VeriText AI', { size: 16, weight: 700, fill: fg });
}
function tabs(x, y, labels, active, w = 140, color = C.ink) {
  let s = L(x, y + 40, x + labels.length * w, y + 40);
  labels.forEach((l, i) => {
    const on = i === active;
    s += T(x + i * w + w / 2, y + 25, l, { size: 14, weight: on ? 600 : 500, fill: on ? C.ink : C.muted, anchor: 'middle' });
    if (on) s += R(x + i * w, y + 38, w, 2.5, { fill: color });
  });
  return s;
}
// teks dengan highlight; segmen: string | [teks, warna]
function rich(x, y, segs, size = 14, k = 0.54) {
  let cx = x, out = '';
  for (const s of segs) {
    const [txt, hl] = typeof s === 'string' ? [s, null] : s;
    const w = +(txt.length * size * k).toFixed(1);
    if (hl) out += R(cx, y - size, w, size + 6, { r: 2, fill: hl, op: 0.22 }) + R(cx, y + 4, w, 2, { fill: hl });
    out += T(cx, y, txt, { size, tl: w });
    cx += w;
  }
  return out;
}
function gauge(cx, cy, r, p, color, sw = 16) {
  const th = Math.PI * (1 - p);
  const ex = cx + r * Math.cos(th), ey = cy - r * Math.sin(th);
  return `<path d="M${cx - r} ${cy}A${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none" stroke="${C.border}" stroke-width="${sw}" stroke-linecap="butt"/>` +
    `<path d="M${cx - r} ${cy}A${r} ${r} 0 0 1 ${ex.toFixed(1)} ${ey.toFixed(1)}" fill="none" stroke="${color}" stroke-width="${sw}"/>`;
}
const levelColor = (p) => (p < 20 ? C.green : p < 40 ? C.orange : C.red);

// tabel: cols [{label,w,align}], rows: sel / {badge:[text,color]} / {score:n} / {link:text}
function table(x, y, cols, rows, rowH = 52) {
  const tot = cols.reduce((a, c) => a + c.w, 0);
  let s = card(x, y, tot, 40 + rows.length * rowH, { r: 8 }) + R(x + 1, y + 1, tot - 2, 39, { fill: C.soft });
  let cx = x;
  cols.forEach((c) => {
    const ax = c.align === 'right' ? cx + c.w - 16 : cx + 16;
    s += T(ax, y + 25, c.label.toUpperCase(), { size: 11, weight: 600, fill: C.muted, ls: 0.8, anchor: c.align === 'right' ? 'end' : 'start' });
    cx += c.w;
  });
  rows.forEach((row, ri) => {
    const ry = y + 40 + ri * rowH;
    s += L(x + 1, ry, x + tot - 1, ry);
    let px = x;
    row.forEach((cell, ci) => {
      const c = cols[ci], my = ry + rowH / 2;
      const ax = c.align === 'right' ? px + c.w - 16 : px + 16;
      if (typeof cell === 'string') s += T(ax, my + 5, cell, { size: 13.5, anchor: c.align === 'right' ? 'end' : 'start', weight: ci === 0 ? 500 : 400, fill: ci === 0 ? C.ink : '#404040' });
      else if (cell.mono) s += T(ax, my + 5, cell.mono, { size: 12.5, mono: true, fill: '#404040', anchor: c.align === 'right' ? 'end' : 'start' });
      else if (cell.badge) s += badge(ax, my - 11, cell.badge[0], cell.badge[1]).svg;
      else if (cell.score != null) {
        const col = levelColor(cell.score);
        s += R(ax, my - 3, 90, 6, { r: 3, fill: C.border }) + R(ax, my - 3, Math.max(4, 0.9 * cell.score), 6, { r: 3, fill: col }) + T(ax + 102, my + 5, cell.score.toFixed(1).replace('.', ',') + '%', { size: 13.5, weight: 600 });
      } else if (cell.link) s += T(ax, my + 5, cell.link, { size: 13.5, weight: 600, anchor: c.align === 'right' ? 'end' : 'start' });
      px += c.w;
    });
  });
  return s;
}

// ---------- page chrome ----------
function page(name, h, body, title) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${h}" viewBox="0 0 ${W} ${h}" role="img" aria-labelledby="t">
<title id="t">${esc(title)}</title>
<defs><style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Source+Serif+4:wght@500;600;700&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap');
text{font-family:'Inter','Helvetica Neue',Arial,sans-serif}
.s{font-family:'Source Serif 4',Georgia,'Times New Roman',serif}
.m{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
</style></defs>
${R(0, 0, W, h, { fill: C.bg })}
${body}
</svg>
`;
  fs.writeFileSync(path.join(OUT, name + '.svg'), svg);
  console.log('ok', name);
}

function publicNav(active = '') {
  const links = ['Fitur', 'Pipeline', 'Demo', 'Verifikasi'];
  let s = R(0, 0, W, 64, { fill: C.white }) + L(0, 64, W, 64) + logo(64, 20);
  let x = 540;
  links.forEach((l) => { s += T(x, 37, l, { size: 14, weight: 500, fill: l === active ? C.ink : C.muted }); x += tw(l, 14) + 40; });
  s += T(1180, 37, 'Masuk', { size: 14, weight: 600 }) + btn(1250, 12, 126, 40, 'Daftar');
  return s;
}
function appNav(active) {
  const links = ['Dashboard', 'Bank Korpus', 'Billing', 'Admin'];
  let s = R(0, 0, W, 64, { fill: C.white }) + L(0, 64, W, 64) + logo(64, 20);
  let x = 300;
  links.forEach((l) => {
    const w = tw(l, 14);
    const on = l === active;
    s += T(x, 37, l, { size: 14, weight: on ? 600 : 500, fill: on ? C.ink : C.muted });
    if (on) s += R(x, 61.5, w, 2.5, { fill: C.ink });
    x += w + 36;
  });
  const b = badge(1090, 21, '3 TOKEN', C.blue, 11);
  s += b.svg + T(1086, 36, 'Saldo', { size: 12, fill: C.muted, anchor: 'end' });
  s += `<circle cx="1352" cy="32" r="16" fill="${C.ink}"/>` + T(1352, 37, 'RP', { size: 12, weight: 600, fill: '#fff', anchor: 'middle' });
  s += T(1326, 37, 'Rizky Pratama', { size: 13, weight: 500, anchor: 'end' });
  return s;
}
function authCard(x, y, w, h) { return card(x, y, w, h, { r: 12 }); }
function authShell(content) {
  return R(0, 0, W, 64, { fill: C.white }) + L(0, 64, W, 64) + logo(64, 20) + T(1376, 37, '← Kembali ke beranda', { size: 13, fill: C.muted, anchor: 'end' }) + content;
}

// ---------- 01 landing ----------
{
  let b = publicNav('Pipeline');
  b += badge(64, 112, '● Versi 2.4 Hibrida', C.ink).svg.replace(/fill-opacity="0.12"/, 'fill-opacity="0.07"');
  ['Audit orisinalitas', 'naskah akademik,', 'sampai ke makna.'].forEach((l, i) => { b += T(64, 210 + i * 70, l, { size: 62, weight: 600, serif: true, ls: -1.2 }); });
  ['VeriText AI memeriksa kemiripan leksikal, semantik, dan gaya', 'penulisan dalam satu laporan, dengan bukti per kalimat yang', 'bisa dipertanggungjawabkan di hadapan dosen penguji.'].forEach((l, i) => { b += T(64, 424 + i * 28, l, { size: 17, fill: C.muted }); });
  b += btn(64, 520, 214, 50, 'Mulai Audit Naskah →', 'primary', 15) + btn(294, 520, 260, 50, 'Lihat Dokumentasi Pipeline', 'secondary', 15);
  b += T(64, 612, 'Sesuai UU PDP No. 27/2022 · Naskah dihapus otomatis setelah masa retensi 30 hari', { size: 13, fill: C.muted });
  // demo
  b += card(760, 104, 616, 456, { r: 10 });
  b += T(784, 140, 'DEMO INTERAKTIF', { size: 11, weight: 600, fill: C.muted, ls: 1 });
  b += tabs(776, 150, ['Leksikal', 'Semantik', 'Stilometri AI'], 0, 140, C.red);
  const ty = 232;
  const lines = [
    ['Perubahan iklim global merupakan ', ['tantangan terbesar yang dihadapi', C.red]],
    [['umat manusia', C.red], ' pada abad ke-21 karena berdampak langsung'],
    ['pada ketahanan pangan, ketersediaan air, serta ', ['kestabilan ekonomi', C.orange]],
    [['negara berkembang', C.orange], '. Dalam konteks ini, ', ['penting dicatat bahwa', C.yellow]],
    ['mitigasi harus dilakukan secara terkoordinasi lintas sektor.'],
  ];
  lines.forEach((l, i) => { b += rich(784, ty + i * 34, l, 14.5); });
  b += L(760, 420, 1376, 420);
  b += T(784, 454, 'Skor kemiripan', { size: 12, fill: C.muted }) + T(784, 488, '62,0%', { size: 34, weight: 600, serif: true });
  b += gauge(1280, 500, 56, 0.62, C.red, 12);
  [[C.red, 'Salin-tempel'], [C.orange, 'Parafrasa'], [C.yellow, 'Anomali AI']].forEach(([c, t], i) => { b += R(784 + i * 128, 516, 10, 10, { r: 2, fill: c }) + T(800 + i * 128, 526, t, { size: 12, fill: C.muted }); });
  b += T(1376 - 24, 546, 'Arahkan kursor ke kalimat berwarna untuk detail tier', { size: 11, fill: '#9ca3af', anchor: 'end' });
  // metrics
  b += L(64, 660, 1376, 660) + L(64, 764, 1376, 764);
  [['12.480', 'naskah telah diaudit'], ['94,2%', 'akurasi deteksi parafrasa'], ['38 dtk', 'rata-rata waktu analisis']].forEach(([n, l], i) => {
    const x = 64 + i * 437.33;
    if (i) b += L(x, 680, x, 744);
    b += T(x + (i ? 32 : 0), 722, n, { size: 40, weight: 600, serif: true }) + T(x + (i ? 32 : 0) + tw(n, 40, 0.5) + 14, 722, l, { size: 14, fill: C.muted });
  });
  // pipeline
  b += T(64, 836, 'PIPELINE DETEKSI 4 TIER', { size: 12, weight: 600, fill: C.muted, ls: 1.5 });
  b += T(64, 884, 'Empat lapisan, satu skor yang bisa diaudit.', { size: 38, weight: 600, serif: true, ls: -0.5 });
  const tiers = [
    [C.red, 'TIER 1', 'Leksikal', 'Rabin-Karp Winnowing', 'Mendeteksi salin-tempel lewat n-gram', 'dan fingerprint pada seluruh korpus.', 'Bobot 50%'],
    [C.orange, 'TIER 2', 'Semantik', 'pgvector HNSW', 'Menangkap parafrasa dan restrukturisasi', 'kalimat dengan embedding 384 dimensi.', 'Bobot 35%'],
    [C.yellow, 'TIER 3', 'Stilometri', 'LLM Anomaly', 'Menandai perubahan gaya penulisan', 'yang khas dari teks hasil generator AI.', 'Bobot 15%'],
    [C.ink, 'TIER 4', 'Agregator', 'Skor Komposit', 'Menggabungkan ketiga tier menjadi satu', 'skor dan sintesis editorial yang transparan.', '100%'],
  ];
  tiers.forEach(([c, t, n, a, d1, d2, w], i) => {
    const x = 64 + i * 332;
    b += card(x, 924, 312, 232) + R(x + 1, 925, 310, 4, { fill: c });
    b += T(x + 24, 968, t, { size: 11, weight: 600, fill: c === C.yellow ? '#a16207' : c, ls: 1.2 }) + T(x + 24, 1002, n, { size: 26, weight: 600, serif: true });
    b += T(x + 24, 1030, a, { size: 13, weight: 500, mono: true, fill: C.muted });
    b += T(x + 24, 1072, d1, { size: 13.5, fill: '#404040' }) + T(x + 24, 1092, d2, { size: 13.5, fill: '#404040' });
    b += L(x + 24, 1118, x + 288, 1118) + T(x + 24, 1142, w, { size: 13, weight: 600 });
  });
  // footer
  b += R(0, 1220, W, 220, { fill: C.white }) + L(0, 1220, W, 1220) + logo(64, 1256);
  b += T(64, 1312, 'Platform audit orisinalitas naskah akademik.', { size: 13, fill: C.muted }) + T(64, 1332, '© 2026 VeriText AI · Proyek IPPL', { size: 13, fill: C.muted });
  [['Produk', ['Audit Naskah', 'Pipeline Deteksi', 'Bank Korpus']], ['Legalitas', ['UU PDP No. 27/2022', 'Etika Akademik', 'Kebijakan Retensi']], ['Verifikasi', ['Cek Sertifikat QR', 'Pindai Kamera', 'Bantuan']]].forEach(([h, ls], i) => {
    const x = 760 + i * 210;
    b += T(x, 1264, h, { size: 12, weight: 600, fill: C.muted, ls: 1 });
    ls.forEach((l, j) => { b += T(x, 1296 + j * 26, l, { size: 14 }); });
  });
  page('01-landing', 1440, b, 'VeriText AI – Landing Page');
}

// ---------- 02 login ----------
{
  let c = authCard(510, 130, 420, 600);
  c += T(540, 190, 'Masuk ke VeriText AI', { size: 28, weight: 600, serif: true }) + T(540, 218, 'Gunakan akun institusi untuk membuka workspace audit.', { size: 13.5, fill: C.muted });
  c += field(540, 262, 360, 'Alamat Email Institusi', 'nama@kampus.ac.id', { ph: true });
  c += field(540, 352, 360, 'Kata Sandi', '••••••••••', { icon: 'eye-off', ph: true });
  c += checkbox(540, 450, 'Ingat sesi saya di perangkat ini', false) + T(900, 464, 'Lupa sandi?', { size: 13, weight: 500, anchor: 'end' });
  c += btn(540, 492, 360, 48, 'Masuk Sekarang →', 'primary', 15);
  c += L(540, 572, 700, 572) + T(720, 577, 'atau', { size: 12, fill: C.muted, anchor: 'middle' }) + L(740, 572, 900, 572);
  c += R(540.5, 592.5, 359, 46, { r: 8, fill: '#fff', stroke: C.line }) + google(640, 604, 0.45) + T(676, 621, 'Masuk dengan Akun Google Kampus (SSO)', { size: 13, weight: 600, anchor: 'start' }).replace('x="676"', 'x="668"');
  c += T(720, 690, 'Belum punya akun? ', { size: 13, fill: C.muted, anchor: 'end' }) + T(720, 690, 'Daftar sekarang', { size: 13, weight: 600 });
  page('02-login', 860, authShell(c), 'VeriText AI – Login');
}

// ---------- 03 register ----------
{
  let c = authCard(440, 100, 560, 760);
  c += T(476, 160, 'Buat akun baru', { size: 28, weight: 600, serif: true }) + T(476, 188, 'Dapatkan 1 saldo token uji coba gratis setelah mendaftar.', { size: 13.5, fill: C.muted });
  c += field(476, 224, 488, 'Nama Lengkap', 'Nama sesuai identitas akademik', { ph: true });
  c += field(476, 296, 488, 'Email Kampus', 'nama@kampus.ac.id', { ph: true });
  c += field(476, 368, 488, 'Nama Institusi / Universitas', 'Universitas Nusantara', { ph: true });
  c += field(476, 440, 236, 'Kata Sandi', '••••••••', { icon: 'eye-off', ph: true });
  c += field(728, 440, 236, 'Konfirmasi Sandi', '••••••••', { icon: 'eye-off', ph: true });
  [C.green, C.green, C.border].forEach((col, i) => { c += R(476 + i * 84, 516, 76, 4, { r: 2, fill: col }); });
  c += T(740, 521, 'Sedang', { size: 12, weight: 500, fill: C.orange, anchor: 'start' }).replace('x="740"', 'x="736"');
  c += checkbox(476, 546, 'Saya menyetujui pemrosesan naskah sesuai UU PDP No. 27/2022', true);
  c += btn(476, 586, 488, 48, 'Daftar Akun Baru →', 'primary', 15);
  c += L(476, 666, 676, 666) + T(720, 671, 'atau', { size: 12, fill: C.muted, anchor: 'middle' }) + L(764, 666, 964, 666);
  c += R(476.5, 686.5, 487, 46, { r: 8, fill: '#fff', stroke: C.line }) + google(640, 698, 0.45) + T(668, 715, 'Daftar Otomatis dengan Google Kampus', { size: 13, weight: 600 });
  c += T(720, 780, 'Sudah punya akun? ', { size: 13, fill: C.muted, anchor: 'end' }) + T(720, 780, 'Masuk', { size: 13, weight: 600 });
  page('03-register', 920, authShell(c), 'VeriText AI – Register');
}

// ---------- 04 lupa sandi ----------
{
  let c = authCard(510, 150, 420, 400);
  c += T(540, 212, 'Lupa kata sandi?', { size: 28, weight: 600, serif: true });
  c += T(540, 240, 'Masukkan email institusi terdaftar. Kami akan mengirim', { size: 13.5, fill: C.muted }) + T(540, 260, 'tautan pemulihan yang berlaku 15 menit.', { size: 13.5, fill: C.muted });
  c += field(540, 292, 360, 'Alamat Email Institusi', 'nama@kampus.ac.id', { ph: true, focus: true });
  c += btn(540, 380, 360, 48, 'Kirim Tautan Pemulihan', 'primary', 15);
  c += T(720, 470, '← Kembali ke halaman masuk', { size: 13, weight: 600, anchor: 'middle' });
  page('04-forgot-password', 700, authShell(c), 'VeriText AI – Lupa Kata Sandi');
}

// ---------- 05 reset sandi ----------
{
  let c = authCard(510, 130, 420, 470);
  c += T(540, 192, 'Setel kata sandi baru', { size: 28, weight: 600, serif: true }) + T(540, 220, 'Gunakan minimal 8 karakter dengan angka dan simbol.', { size: 13.5, fill: C.muted });
  c += field(540, 256, 360, 'Kata Sandi Baru', '••••••••••', { icon: 'eye-off', ph: true });
  c += field(540, 346, 360, 'Konfirmasi Kata Sandi Baru', '••••••••••', { icon: 'eye-off', ph: true });
  [C.green, C.green, C.green].forEach((col, i) => { c += R(540 + i * 124, 440, 112, 4, { r: 2, fill: col }); });
  c += T(540, 466, 'Kekuatan: Kuat', { size: 12, weight: 500, fill: C.green });
  c += btn(540, 496, 360, 48, 'Simpan Kata Sandi Baru', 'primary', 15);
  page('05-reset-password', 700, authShell(c), 'VeriText AI – Setel Ulang Kata Sandi');
}

// ---------- 06 dashboard ----------
{
  let b = appNav('Dashboard');
  b += T(64, 130, 'Halo, Rizky Pratama', { size: 34, weight: 600, serif: true, ls: -0.4 });
  const b1 = badge(64, 148, 'Universitas Nusantara', C.muted), b2 = badge(64 + b1.w + 8, 148, 'TRIAL', C.blue);
  b += b1.svg + b2.svg + btn(1200, 98, 176, 42, '↻  Sinkronkan Status', 'secondary', 13);
  const tl = ['Semua', 'Unggah Naskah', 'Antrean Deteksi', 'Riwayat Audit'];
  b += R(64.5, 196.5, 4 * 148 + 8 - 1, 44, { r: 8, fill: '#fff', stroke: C.border });
  tl.forEach((l, i) => {
    const x = 68 + i * 148;
    if (i === 0) b += R(x, 200, 144, 36, { r: 6, fill: C.ink });
    b += T(x + 72, 223, l, { size: 13.5, weight: 600, fill: i === 0 ? '#fff' : C.muted, anchor: 'middle' });
  });
  [['Saldo Token Aktif', '3', 'cukup untuk 1 audit Hybrid'], ['Total Naskah Diuji', '14', '+2 minggu ini'], ['Audit Selesai', '12', '2 dalam antrean'], ['Status Worker Celery', 'Aktif', '4 dari 4 worker siaga']].forEach(([l, v, h], i) => {
    const x = 64 + i * 333;
    b += card(x, 268, 313, 108) + T(x + 20, 296, l, { size: 12, weight: 500, fill: C.muted }) + T(x + 20, 340, v, { size: 36, weight: 600, serif: true, fill: i === 3 ? C.green : C.ink }) + T(x + 20, 362, h, { size: 12, fill: C.muted });
  });
  // upload
  b += R(64.5, 404.5, 819, 263, { r: 10, fill: '#fff', stroke: C.line, sw: 1.5, dash: '6 5' });
  b += `<g transform="translate(474 470)" fill="none" stroke="${C.ink}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M0 18V-14M-10 -4L0 -14L10 -4M-18 12V22H18V12"/></g>`;
  b += T(474, 528, 'Tarik & lepas naskah di sini', { size: 20, weight: 600, serif: true, anchor: 'middle' }) + T(474, 554, '.pdf  .docx  .txt  ·  maksimal 50 MB', { size: 13, fill: C.muted, anchor: 'middle' });
  b += btn(394, 576, 160, 42, 'Pilih Berkas', 'secondary', 14);
  b += card(908, 404, 468, 264);
  b += T(932, 436, 'Kedalaman audit', { size: 14, weight: 600 });
  b += R(932.5, 450.5, 419, 62, { r: 8, fill: '#fafafa', stroke: C.ink, sw: 2 }) + `<circle cx="958" cy="481" r="8" fill="#fff" stroke="${C.ink}" stroke-width="2"/><circle cx="958" cy="481" r="4" fill="${C.ink}"/>` + T(982, 477, 'Hybrid Penuh (Tier 1–4)', { size: 14, weight: 600 }) + T(982, 497, 'Leksikal + semantik + stilometri AI', { size: 12, fill: C.muted }) + T(1336, 486, '2 Token', { size: 13, weight: 600, anchor: 'end' });
  b += R(932.5, 522.5, 419, 62, { r: 8, fill: '#fff', stroke: C.border }) + `<circle cx="958" cy="553" r="8" fill="#fff" stroke="${C.line}" stroke-width="2"/>` + T(982, 549, 'Leksikal Cepat (Tier 1)', { size: 14, weight: 600 }) + T(982, 569, 'Rabin-Karp Winnowing saja', { size: 12, fill: C.muted }) + T(1336, 558, '1 Token', { size: 13, weight: 600, anchor: 'end' });
  b += btn(932, 604, 420, 46, 'Mulai Proses Audit', 'disabled', 14);
  // history
  b += T(64, 726, 'Riwayat Pengujian Terakhir', { size: 24, weight: 600, serif: true }) + T(1376, 726, 'Lihat semua →', { size: 13, weight: 600, anchor: 'end' });
  const cols = [{ label: 'Judul Naskah', w: 400 }, { label: 'Waktu Audit', w: 170 }, { label: 'Kedalaman', w: 150 }, { label: 'Status', w: 150 }, { label: 'Skor Kemiripan', w: 230 }, { label: 'Aksi', w: 212, align: 'right' }];
  const rows = [
    ['Dampak Perubahan Iklim terhadap Ketahanan Pangan', '03 Nov 2026, 09:12', 'Hybrid', { badge: ['Selesai', C.green] }, { score: 38.6 }, { link: 'Lihat Detail →' }],
    ['Analisis Sentimen Ulasan Aplikasi Mobile Banking', '02 Nov 2026, 14:40', 'Hybrid', { badge: ['Selesai', C.green] }, { score: 12.3 }, { link: 'Lihat Detail →' }],
    ['Rancang Bangun Sistem Informasi Perpustakaan', '01 Nov 2026, 20:05', 'Leksikal', { badge: ['Diproses 35%', C.blue] }, '—', { link: 'Batalkan' }],
    ['Efektivitas Metode Pembelajaran Daring Pasca Pandemi', '29 Okt 2026, 11:27', 'Hybrid', { badge: ['Selesai', C.green] }, { score: 61.8 }, { link: 'Lihat Detail →' }],
    ['Optimasi Rute Distribusi dengan Algoritma Genetika', '27 Okt 2026, 08:50', 'Leksikal', { badge: ['Gagal', C.red] }, '—', { link: 'Lihat Detail →' }],
  ];
  b += table(64, 748, cols, rows, 56);
  page('06-dashboard', 1140, b, 'VeriText AI – Dashboard');
}

// ---------- 07 audit detail ----------
{
  let b = appNav('Dashboard');
  b += T(64, 98, 'Dashboard  /  Riwayat Audit  /  8f2a91c4', { size: 12.5, fill: C.muted });
  b += T(64, 136, 'Dampak Perubahan Iklim terhadap Ketahanan Pangan', { size: 28, weight: 600, serif: true, ls: -0.3 });
  const x1 = badge(64, 152, 'Hybrid Penuh', C.ink), x2 = badge(64 + x1.w + 8, 152, 'Selesai', C.green);
  b += x1.svg + x2.svg + T(64 + x1.w + x2.w + 24, 168, 'Diaudit 03 Nov 2026, 09:12 WIB · 4.218 kata', { size: 12.5, fill: C.muted });
  b += btn(1120, 100, 256, 44, '⤓  Unduh Sertifikat PDF Resmi', 'primary', 13.5) + btn(1120, 154, 256, 34, 'Hapus naskah', 'danger', 13);
  // left
  b += card(64, 208, 744, 744);
  b += T(88, 240, 'Tampilkan:', { size: 12.5, fill: C.muted });
  [['Leksikal', C.red], ['Semantik', C.orange], ['Stilometri AI', C.yellow]].forEach(([l, c], i) => {
    const x = 160 + i * 138;
    b += R(x + 0.5, 224.5, 126, 32, { r: 16, fill: '#fff', stroke: C.line }) + R(x + 12, 235, 12, 12, { r: 3, fill: c }) + check(x + 18, 241, '#fff', 0.8) + T(x + 32, 245, l, { size: 12.5, weight: 500 });
  });
  b += L(64, 272, 808, 272);
  const R_ = C.red, O = C.orange, Y = C.yellow;
  const txt = [
    [['BAB II', null]],
    [],
    ['Perubahan iklim global merupakan ', [ 'tantangan terbesar yang dihadapi umat manusia', R_ ], ' pada'],
    [['abad ke-21 karena berdampak langsung', R_], ' pada ketahanan pangan, ketersediaan air,'],
    ['serta ', ['kestabilan ekonomi negara berkembang', O], '. Berbagai studi menunjukkan bahwa'],
    ['kenaikan suhu rata-rata ', ['berkorelasi dengan penurunan produktivitas', O], ' lahan pertanian'],
    ['di wilayah tropis.'],
    [],
    [['Dalam konteks ini, penting untuk dicatat bahwa', Y], ' mitigasi harus dilakukan secara'],
    ['terkoordinasi lintas sektor. ', ['Selain itu, perlu dipahami bahwa adaptasi petani', Y], ' lokal menjadi'],
    ['kunci keberhasilan program ketahanan pangan nasional dalam jangka panjang.'],
    [],
    ['Penelitian ini menggunakan pendekatan kuantitatif dengan data panel dari 34 provinsi'],
    ['selama periode 2010–2023. ', ['Data dianalisis menggunakan regresi efek tetap untuk', R_], ' menguji'],
    [['hubungan antara anomali curah hujan dan hasil panen padi', R_], ', jagung, serta kedelai.'],
    [],
    ['Hasil awal mengindikasikan adanya efek ambang pada suhu di atas 32°C yang secara'],
    ['signifikan menurunkan hasil panen, terutama pada musim kemarau berkepanjangan.'],
    [],
    ['Temuan ini sejalan dengan kerangka adaptasi yang diusulkan pada bagian berikutnya.'],
  ];
  txt.forEach((l, i) => { if (l.length) b += rich(88, 306 + i * 30, l.map((s) => (Array.isArray(s) && s[1] === null ? s[0] : s)), 14, 0.53); });
  b += T(88, 306, 'BAB II', { size: 12, weight: 700, fill: C.muted, ls: 1.2 });
  b += R(790, 290, 6, 120, { r: 3, fill: C.border }) ;
  // right
  b += tabs(832, 208, ['Ringkasan', 'Sumber', 'Diff'], 0, 120);
  b += card(832, 262, 544, 690);
  b += gauge(1104, 392, 100, 0.386, C.orange, 18) + T(1104, 384, '38,6%', { size: 40, weight: 600, serif: true, anchor: 'middle' }) + T(1104, 416, 'Waspada', { size: 14, weight: 600, fill: C.orange, anchor: 'middle' });
  b += T(992, 424, '0', { size: 11, fill: C.muted, anchor: 'middle' }) + T(1216, 424, '100', { size: 11, fill: C.muted, anchor: 'middle' });
  [[C.red, 'Tier 1 · Leksikal', 'Bobot 50%', 44.2], [C.orange, 'Tier 2 · Semantik', 'Bobot 35%', 36.0], ['#ca8a04', 'Tier 3 · Stilometri AI', 'Bobot 15%', 18.5]].forEach(([c, n, w, v], i) => {
    const y = 456 + i * 72;
    b += R(856, y, 496, 60, { r: 8, fill: C.soft }) + R(856, y, 4, 60, { fill: c });
    b += T(876, y + 26, n, { size: 13.5, weight: 600 }) + T(876, y + 46, w, { size: 12, fill: C.muted });
    b += R(1060, y + 27, 190, 6, { r: 3, fill: C.border }) + R(1060, y + 27, 1.9 * v, 6, { r: 3, fill: c }) + T(1336, y + 36, v.toFixed(1).replace('.', ',') + '%', { size: 15, weight: 600, anchor: 'end' });
  });
  b += T(856, 700, 'SINTESIS EDITORIAL AI', { size: 11, weight: 600, fill: C.muted, ls: 1.2 });
  b += R(856, 714, 496, 212, { r: 8, fill: '#fff', stroke: C.border });
  ['Skor komposit berada pada rentang waspada. Kemiripan', 'tertinggi muncul pada paragraf pembuka Bab II yang', 'menyalin hampir utuh definisi dari 2 sumber korpus.', '', 'Parafrasa semantik ditemukan pada pembahasan efek', 'suhu terhadap produktivitas lahan. Disarankan menambah', 'sitasi langsung dan menulis ulang kalimat bertanda merah.'].forEach((l, i) => { if (l) b += T(876, 746 + i * 24, l, { size: 13.5, fill: '#404040' }); });
  page('07-audit-detail', 1000, b, 'VeriText AI – Detail Laporan Audit');
}

// ---------- 08 corpus ----------
{
  let b = appNav('Bank Korpus');
  b += T(64, 130, 'Bank Korpus Dokumen', { size: 34, weight: 600, serif: true, ls: -0.4 }) + T(64, 158, '248 dokumen · 246 terindeks · 2 sedang diindeks', { size: 13.5, fill: C.muted });
  b += btn(1004, 100, 120, 42, 'Re-index', 'secondary', 13.5) + btn(1136, 100, 120, 42, 'Unggah ZIP', 'secondary', 13.5) + btn(1268, 100, 108, 42, '+ Naskah', 'primary', 13.5);
  b += R(64.5, 188.5, 420, 44, { r: 8, fill: '#fff', stroke: C.line }) + `<g fill="none" stroke="${C.muted}" stroke-width="1.8" stroke-linecap="round"><circle cx="88" cy="209" r="6"/><path d="M93 214l5 5"/></g>` + T(108, 216, 'Cari judul, penulis, atau lembaga…', { size: 14, fill: '#9ca3af' });
  b += R(496.5, 188.5, 170, 44, { r: 8, fill: '#fff', stroke: C.line }) + T(512, 216, 'Semua kategori', { size: 14 }) + T(650, 216, '⌄', { size: 14, fill: C.muted, anchor: 'end' });
  const cols = [{ label: 'Judul Naskah', w: 380 }, { label: 'Kategori', w: 120 }, { label: 'Penulis', w: 200 }, { label: 'Terbit', w: 110 }, { label: 'Indeks Vektor', w: 200 }, { label: 'Aksi', w: 302, align: 'right' }];
  const ok = { badge: ['Terindeks (384-dim)', C.green] }, ix = { badge: ['Mengindeks Vektor…', '#ca8a04'] };
  const act = { link: 'Re-index    Hapus' };
  const rows = [
    ['Ketahanan Pangan di Era Perubahan Iklim', 'Jurnal', 'Dewi Lestari, M.Si.', '2022', ok, act],
    ['Sistem Informasi Akademik Berbasis Web', 'Skripsi', 'Ahmad Fauzi', '2021', ok, act],
    ['Pengaruh Media Sosial terhadap Perilaku Belajar', 'Tesis', 'Nadia Putri', '2023', ok, act],
    ['Dasar-Dasar Pemrosesan Bahasa Alami', 'Buku', 'Prof. Budi Santoso', '2020', ok, act],
    ['Optimasi Logistik dengan Algoritma Genetika', 'Jurnal', 'Rina Marlina', '2024', ix, act],
    ['Analisis Kebijakan Energi Terbarukan Nasional', 'Tesis', 'Yoga Pratama', '2023', ok, act],
    ['Machine Learning untuk Deteksi Plagiarisme', 'Jurnal', 'Dr. Hendra Wijaya', '2025', ix, act],
    ['Studi Kelayakan Pembangunan PLTS Atap', 'Skripsi', 'Salsabila Rahma', '2022', ok, act],
  ];
  b += table(64, 256, cols, rows, 52);
  b += T(64, 764, 'Menampilkan 1–8 dari 248 dokumen', { size: 13, fill: C.muted });
  ['‹', '1', '2', '3', '…', '31', '›'].forEach((p, i) => { const x = 1376 - (7 - i) * 40; const on = p === '1'; b += R(x + 0.5, 744.5, 34, 34, { r: 6, fill: on ? C.ink : '#fff', stroke: on ? C.ink : C.border }) + T(x + 17.5, 766, p, { size: 13, weight: 600, fill: on ? '#fff' : C.ink, anchor: 'middle' }); });
  page('08-corpus', 840, b, 'VeriText AI – Bank Korpus');
}

// ---------- 09 billing ----------
{
  let b = appNav('Billing');
  b += T(64, 130, 'Dompet Token & Billing', { size: 34, weight: 600, serif: true, ls: -0.4 });
  b += card(64, 164, 1312, 124) + T(92, 198, 'SALDO TOKEN AKTIF', { size: 11, weight: 600, fill: C.muted, ls: 1.2 }) + T(92, 262, '3', { size: 64, weight: 600, serif: true }) + T(140, 262, 'token', { size: 16, fill: C.muted });
  b += T(1344, 214, 'Cukup untuk 1 audit Hybrid atau 3 audit Leksikal.', { size: 14, fill: C.muted, anchor: 'end' }) + T(1344, 240, 'Token tidak memiliki masa kedaluwarsa.', { size: 13, fill: C.muted, anchor: 'end' });
  const plans = [['Starter · Mahasiswa', '5 Token', 'Rp25.000', 'Rp5.000 / token', false], ['Pro Academic · Peneliti', '20 Token', 'Rp80.000', 'Rp4.000 / token', true], ['Campus Bulk · Institusi', '100 Token', 'Rp350.000', 'Rp3.500 / token', false]];
  plans.forEach(([n, t, p, u, hot], i) => {
    const x = 64 + i * 444;
    b += hot ? R(x + 1, 321, 422, 252, { r: 8, fill: '#fff', stroke: C.ink, sw: 2 }) : card(x, 320, 424, 254);
    if (hot) b += badge(x + 20, 306, 'PALING POPULER', C.ink, 10).svg.replace('fill-opacity="0.12"', 'fill-opacity="1"').replace(/fill="#17191c" fill-opacity="1"/, `fill="${C.ink}"`).replace(/(<text[^>]*?)fill="#17191c"/, '$1fill="#fff"');
    b += T(x + 24, 356, n, { size: 13.5, weight: 600, fill: C.muted }) + T(x + 24, 404, t, { size: 34, weight: 600, serif: true }) + T(x + 24, 440, p, { size: 22, weight: 600 }) + T(x + 24 + tw(p, 22, 0.58) + 12, 440, u, { size: 12.5, fill: C.muted });
    b += T(x + 24, 474, 'Termasuk faktur PDF resmi dan dukungan', { size: 12.5, fill: C.muted }) + T(x + 24, 492, 'verifikasi sertifikat QR.', { size: 12.5, fill: C.muted });
    b += btn(x + 24, 514, 376, 44, 'Beli Paket', hot ? 'primary' : 'secondary', 14);
  });
  b += T(64, 636, 'Riwayat Transaksi', { size: 24, weight: 600, serif: true });
  const cols = [{ label: 'No. Faktur', w: 190 }, { label: 'Tanggal', w: 170 }, { label: 'Paket', w: 230 }, { label: 'Nominal', w: 160 }, { label: 'Metode', w: 190 }, { label: 'Status', w: 150 }, { label: 'Faktur', w: 222, align: 'right' }];
  const rows = [
    [{ mono: 'INV-2026-0042' }, '28 Okt 2026', 'Pro Academic · 20 Token', 'Rp80.000', 'QRIS', { badge: ['Lunas', C.green] }, { link: 'Unduh PDF' }],
    [{ mono: 'INV-2026-0031' }, '12 Okt 2026', 'Starter · 5 Token', 'Rp25.000', 'VA Mandiri', { badge: ['Lunas', C.green] }, { link: 'Unduh PDF' }],
    [{ mono: 'INV-2026-0027' }, '05 Okt 2026', 'Starter · 5 Token', 'Rp25.000', 'VA BCA', { badge: ['Batal', C.red] }, '—'],
    [{ mono: 'INV-2026-0019' }, '21 Sep 2026', 'Starter · 5 Token', 'Rp25.000', 'QRIS', { badge: ['Menunggu', '#ca8a04'] }, '—'],
  ];
  b += table(64, 660, cols, rows, 52);
  page('09-billing', 960, b, 'VeriText AI – Billing');
}

// ---------- 10 verify ----------
{
  let b = publicNav('Verifikasi');
  b += T(720, 190, 'VERIFIKASI PUBLIK', { size: 12, weight: 600, fill: C.muted, ls: 1.5, anchor: 'middle' });
  b += T(720, 252, 'Periksa keaslian sertifikat audit.', { size: 46, weight: 600, serif: true, anchor: 'middle', ls: -0.8 });
  b += T(720, 292, 'Masukkan 36 karakter kode UUID pada sertifikat, atau pindai QR Code-nya.', { size: 16, fill: C.muted, anchor: 'middle' });
  b += card(420, 336, 600, 330, { r: 12 });
  b += field(460, 374, 520, 'Kode UUID Sertifikat', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', { ph: true, focus: true });
  b += btn(460, 466, 520, 50, 'Verifikasi Keaslian Naskah', 'primary', 15);
  b += L(460, 548, 690, 548) + T(720, 553, 'atau', { size: 12, fill: C.muted, anchor: 'middle' }) + L(750, 548, 980, 548);
  b += btn(460, 574, 520, 50, '▣  Pindai Kode QR dengan Kamera Smartphone', 'secondary', 14);
  b += T(720, 720, 'Verifikasi mencocokkan hash SHA-256 dan tanda tangan digital pada pangkalan data VeriText AI.', { size: 13, fill: C.muted, anchor: 'middle' });
  page('10-verify-idle', 860, b, 'VeriText AI – Verifikasi Sertifikat (idle)');

  // valid
  let v = publicNav('Verifikasi');
  v += card(420, 110, 600, 680, { r: 12 });
  v += R(421, 111, 598, 92, { r: 11, fill: '#f0fdf4' }) + L(421, 203, 1019, 203, '#bbf7d0');
  v += `<circle cx="470" cy="157" r="22" fill="${C.green}"/>` + check(470, 157, '#fff', 1.6) + T(508, 150, 'SERTIFIKAT TERVERIFIKASI ASLI', { size: 16, weight: 700, fill: '#166534' }) + T(508, 172, 'Tanda tangan digital cocok dengan catatan audit resmi.', { size: 13, fill: '#166534' });
  const rows = [['Judul Naskah', 'Dampak Perubahan Iklim terhadap Ketahanan Pangan'], ['Penulis', 'Rizky Pratama'], ['Institusi', 'Universitas Nusantara'], ['Waktu Audit', '03 Nov 2026, 09:12 WIB'], ['Kedalaman', 'Hybrid Penuh (Tier 1–4)'], ['Skor Kemiripan', '38,6% — Waspada']];
  rows.forEach(([k, val], i) => { const y = 240 + i * 52; v += T(452, y, k, { size: 12.5, fill: C.muted }) + T(452, y + 22, val, { size: 15, weight: 500 }) + L(452, y + 34, 988, y + 34); });
  v += T(452, 570, 'Digital Signature Hash', { size: 12.5, fill: C.muted }) + R(452, 582, 536, 56, { r: 6, fill: C.soft }) + T(466, 606, '9f2c4e1a7b83d05c6e12a94f0b7d3c58', { size: 12.5, mono: true }) + T(466, 624, 'e1a7f4b20c9d6385a1b7e04d92c3f6a8', { size: 12.5, mono: true });
  v += btn(452, 670, 536, 50, '⤓  Unduh Salinan Sertifikat Resmi (PDF)', 'primary', 14) + T(720, 760, 'UUID: 8f2a91c4-3b7e-4d15-a6c2-0e9f5b1d7a38', { size: 12, mono: true, fill: C.muted, anchor: 'middle' });
  page('10b-verify-valid', 860, v, 'VeriText AI – Verifikasi Sertifikat (valid)');
}

// ---------- 11 admin ----------
{
  let b = R(0, 0, 240, 900, { fill: C.ink }) + logo(28, 24, true);
  [['Ringkasan Sistem', true], ['Manajemen Pengguna'], ['Bank Korpus'], ['Konfigurasi Algoritma'], ['Log Audit Keamanan'], ['Kepatuhan UU PDP']].forEach(([l, on], i) => {
    const y = 96 + i * 46;
    if (on) b += R(12, y, 216, 38, { r: 6, fill: '#fff', op: 0.1 }) + R(12, y + 8, 3, 22, { fill: '#fff' });
    b += T(32, y + 24, l, { size: 14, weight: on ? 600 : 500, fill: on ? '#fff' : '#a3a3a3' });
  });
  b += L(24, 836, 216, 836, '#2e3136') + `<circle cx="44" cy="866" r="14" fill="#fff" fill-opacity="0.12"/>` + T(44, 870, 'SA', { size: 11, weight: 600, fill: '#fff', anchor: 'middle' }) + T(68, 862, 'Super Admin', { size: 13, weight: 600, fill: '#fff' }) + T(68, 878, 'admin@veritext.ac.id', { size: 11, fill: '#a3a3a3' });
  b += T(280, 76, 'Ringkasan Sistem', { size: 34, weight: 600, serif: true, ls: -0.4 }) + T(280, 104, 'Telemetri server dan aktivitas audit 14 hari terakhir.', { size: 13.5, fill: C.muted });
  b += badge(1224, 56, '● Semua layanan normal', C.green).svg.replace('x="1224"', 'x="1190"');
  [['Utilisasi CPU', '42%', C.ink], ['Utilisasi RAM', '61%', C.ink], ['Celery Worker', '4 / 4', C.green], ['Token Beredar', '1.842', C.ink]].forEach(([l, v, col], i) => {
    const x = 280 + i * 281;
    b += card(x, 136, 265, 104) + T(x + 20, 164, l, { size: 12, weight: 500, fill: C.muted }) + T(x + 20, 214, v, { size: 38, weight: 600, serif: true, fill: col });
  });
  b += card(280, 264, 780, 330) + T(304, 298, 'Pengujian Harian', { size: 16, weight: 600 }) + T(1036, 298, '14 hari', { size: 12.5, fill: C.muted, anchor: 'end' });
  const data = [32, 48, 41, 60, 72, 55, 64, 80, 68, 90, 76, 85, 95, 88];
  [0, 1, 2, 3].forEach((i) => { const y = 340 + i * 56; b += L(304, y, 1036, y); });
  data.forEach((d, i) => { const h = d * 1.7, x = 316 + i * 52; b += R(x, 508 - h, 30, h, { r: 2, fill: i === 12 ? C.ink : '#c7c7c3' }); b += T(x + 15, 530, String(i + 20 > 31 ? i - 11 : i + 20), { size: 10.5, fill: C.muted, anchor: 'middle' }); });
  b += T(1036, 568, 'Okt – Nov 2026', { size: 11, fill: C.muted, anchor: 'end' });
  b += card(1084, 264, 292, 330) + T(1108, 298, 'Status Worker', { size: 16, weight: 600 });
  [['worker-01', 'Siaga'], ['worker-02', 'Memproses'], ['worker-03', 'Siaga'], ['worker-04', 'Memproses']].forEach(([n, s], i) => {
    const y = 330 + i * 56;
    b += L(1108, y - 12, 1352, y - 12) + `<circle cx="1116" cy="${y + 10}" r="5" fill="${s === 'Siaga' ? C.green : C.blue}"/>` + T(1134, y + 15, n, { size: 13, mono: true }) + T(1352, y + 15, s, { size: 12.5, weight: 500, fill: C.muted, anchor: 'end' });
  });
  b += T(280, 636, 'Aktivitas Keamanan Terbaru', { size: 20, weight: 600, serif: true }) + T(1376, 636, 'Lihat log lengkap →', { size: 13, weight: 600, anchor: 'end' });
  const cols = [{ label: 'Waktu (WIB)', w: 200 }, { label: 'Aksi', w: 200 }, { label: 'Pengguna', w: 260 }, { label: 'IP Address', w: 200 }, { label: 'Status', w: 236, align: 'right' }];
  const rows = [
    ['03 Nov, 09:12:08', { mono: 'AUDIT' }, 'rizky@nusantara.ac.id', { mono: '114.125.20.7' }, { badge: ['Berhasil', C.green] }],
    ['03 Nov, 08:57:41', { mono: 'LOGIN' }, 'dewi@nusantara.ac.id', { mono: '103.28.12.44' }, { badge: ['Berhasil', C.green] }],
    ['03 Nov, 08:31:19', { mono: 'LOGIN' }, 'unknown@mail.com', { mono: '45.13.77.2' }, { badge: ['Terkunci 429', C.red] }],
  ];
  b += table(280, 660, cols, rows, 46);
  page('11-admin-overview', 900, b, 'VeriText AI – Konsol Admin');
}

// ---------- 12 error pages ----------
const errs = [
  ['400', 'Permintaan tidak valid', 'Permintaan tidak dapat diproses karena data yang dikirimkan tidak valid atau korup.', 'Kembali', 'Ke beranda'],
  ['401', 'Sesi Anda telah berakhir', 'Demi keamanan, silakan masuk kembali. Anda akan dialihkan otomatis ke halaman masuk.', 'Masuk Kembali', 'Ke beranda'],
  ['403', 'Akses ditolak', 'Halaman ini terbatas untuk Super Administrator. Akun Anda tidak memiliki wewenang untuk membuka konsol ini.', 'Kembali ke Dashboard', 'Hubungi helpdesk'],
  ['404', 'Halaman tidak ditemukan', 'Halaman yang Anda tuju tidak ditemukan atau URL salah ketik.', 'Kembali ke Beranda', 'Laporkan masalah'],
  ['408', 'Koneksi unggah terputus', 'Koneksi unggah berkas terputus karena batas waktu habis. Periksa kestabilan jaringan internet Anda.', 'Coba Unggah Ulang', 'Ke dashboard'],
  ['500', 'Gangguan pada server', 'Terjadi kendala teknis pada server pemrosesan internal. Tim kami telah menerima log peringatan ini.', 'Muat Ulang Halaman', 'Ke beranda'],
  ['503', 'Layanan sedang dipelihara', 'Layanan antrean pengujian sedang dalam pemeliharaan berkala. Dokumen Anda tetap aman dan akan diproses segera.', 'Muat Ulang Halaman', 'Cek status'],
];
for (const [code, title, desc, p1, p2] of errs) {
  let b = R(0, 0, W, 64, { fill: C.white }) + L(0, 64, W, 64) + logo(64, 20);
  b += R(180, 200, 1080, 1, { fill: C.border }) + R(180, 640, 1080, 1, { fill: C.border });
  b += T(180, 420, code, { size: 220, weight: 700, serif: true, fill: C.ink, ls: -6 });
  b += T(180 + 20, 250, 'KODE GALAT ' + code, { size: 12, weight: 600, fill: C.muted, ls: 1.5 }).replace(`x="${200}"`, 'x="184"');
  b += T(720, 330, title, { size: 38, weight: 600, serif: true, ls: -0.4 });
  const words = desc.split(' '); let line = '', ly = 372; const out = [];
  for (const w of words) { if ((line + ' ' + w).length > 52) { out.push(line); line = w; } else line = line ? line + ' ' + w : w; } out.push(line);
  out.forEach((l, i) => { b += T(720, ly + i * 26, l, { size: 16, fill: C.muted }); });
  const by = ly + out.length * 26 + 24;
  b += btn(720, by, tw(p1, 15, 0.58) + 56, 48, p1, 'primary', 15) + btn(720 + tw(p1, 15, 0.58) + 72, by, tw(p2, 15, 0.58) + 56, 48, p2, 'secondary', 15);
  b += T(180, 676, 'Jika masalah berlanjut, sertakan kode galat ' + code + ' saat menghubungi helpdesk akademik.', { size: 13, fill: C.muted });
  page('12-error-' + code, 760, b, 'VeriText AI – Galat ' + code);
}
