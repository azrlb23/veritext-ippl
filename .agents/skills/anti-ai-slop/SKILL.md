---
name: anti-ai-slop
description: Eliminate generic AI-generated aesthetics, floating card clichés, neon gradients, and poor CSS practices. Enforce high data-density, tactile micro-interactions (Emil Kowalski principles), strict typography, and utilitarian academic UI for Vue 3 and Tailwind CSS.
---

# Anti-AI Slop: Design & Frontend Polish Guide

Skill ini dirancang untuk mendeteksi, mencegah, dan merevisi **AI Slop** (estetika generik murahan hasil generate AI) menjadi antarmuka frontend bertaraf profesional, berwibawa, berdensitas tinggi, dan memiliki *tactile feedback* sekelas Linear, Raycast, dan Vercel.

---

## Kapan Menggunakan Skill Ini

Gunakan skill ini **secara proaktif** saat:
1. Merancang atau memodifikasi komponen antarmuka pengguna (Vue 3, Tailwind CSS).
2. Meninjau (*auditing*) tampilan frontend untuk memastikan terbebas dari klise AI.
3. Menulis styling transisi, animasi, tombol, tabel, dialog modal, atau kartu metrik.
4. Membangun halaman analitik/dashboard data-dense (seperti heatmap naskah, tabel skor, diff).

---

## 3 Pilar Utama Anti-AI Slop

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ANTI-AI SLOP FRAMEWORK                          │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ 1. UNSLOP AUDIT    │ 2. TASTE & DENSITY │ 3. EMIL KOWALSKI POLISH      │
│ (Basmi Klise AI)   │ (Struktur & Font)  │ (CSS & Mikro-Interaksi)      │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ • No neon gradients│ • High data density│ • Haram: `transition: all`   │
│ • No blurry shadow │ • Crisp 1px border │ • Durasi cepat: 150-200ms    │
│ • No generic hero  │ • Tabular numerals │ • State aktif & focus ring   │
│ • High contrast    │ • Utilitarian UI   │ • Transform scale-down click │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

---

## 1. Daftar Anti-Pola AI Slop yang Dilarang Keras

| Anti-Pola AI Slop | Kenapa Dilarang | Solusi Pengganti |
| :--- | :--- | :--- |
| **Header Gradient Ungu/Biru Neon** (`bg-gradient-to-r from-purple-500 to-indigo-600`) | Klise khas template AI crypto/marketing; merusak wibawa aplikasi institusi akademik. | Gunakan latar bersih bertaraf *Editorial/Utilitarian* (`bg-white` atau `bg-slate-50`), teks tegas `text-slate-900`, aksen brand biru tegas `text-blue-600`. |
| **Kartu Mengambang dengan Shadow Raksasa** (`shadow-2xl rounded-3xl`) | Mengaburkan batas elemen dan membuang banyak ruang vertikal. | Gunakan batas tajam 1px: `border border-slate-200 shadow-sm rounded-xl`. |
| **Whitespace Berlebihan (Low Density)** | Memaksa pengguna scrolling terus-menerus pada dashboard analitik. | Terapkan **High Density**: padding proporsional (`p-4` atau `p-5`), tabel kompak (`py-2.5 px-3`), gap terukur. |
| **Teks Sekunder Pudar Tak Terbaca** (`text-gray-400` di latar putih) | Gagal standar aksesibilitas WCAG AAA/AA. | Gunakan minimal `text-slate-600` untuk teks deskripsi dan `text-slate-500` untuk metadata sekunder. |
| **Emil's Sin: `transition: all`** | Memaksa browser me-recalculate layout untuk setiap properti; menyebabkan lag dan animasi aneh. | **Spesifikasikan properti**: `transition-colors`, `transition-transform`, atau `transition-opacity`. |
| **Durasi Animasi Lambat** (`duration-500` atau `duration-700`) | Membuat interaksi tombol terasa lambat dan "berminyak". | Gunakan durasi cepat: `duration-150` atau `duration-200` dengan `ease-out`. |

---

## 2. Praktik Terbaik: Taste & Utilitarian Aesthetics

1. **Tipografi & Angka (Tabular Numerals):**
   * Setiap skor persentase, saldo token, dan angka statistik WAJIB menggunakan font monospaced atau font feature tabular: `font-mono tracking-tight` atau `tabular-nums`.
2. **Karakter Visual Akademik:**
   * Desain harus mencerminkan instrumen audit kredibel (seperti GitHub PR diff, Notion, atau Linear), bukan landing page promosi startup fiktif.
3. **Indikator Status & Badge:**
   * Gunakan kombinasi warna latar lembut + border tipis + teks kontras:
     - Sukses/Aman: `bg-emerald-50 text-emerald-700 border border-emerald-200`
     - Peringatan/Tier Kuning: `bg-amber-50 text-amber-800 border border-amber-200`
     - Bahaya/Tier Merah: `bg-rose-50 text-rose-700 border border-rose-200`

---

## 3. Praktik Terbaik: Emil Kowalski Micro-Interactions

1. **Feedback Tombol yang Taktil (Tactile Press):**
   ```html
   <button class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium shadow-sm 
                  hover:bg-blue-700 active:scale-[0.98] 
                  focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1 
                  transition-all-FORBIDDEN transition-colors transition-transform duration-150 ease-out">
     Analisis Naskah
   </button>
   ```
2. **Hover Baris Tabel Interaktif:**
   * Gunakan perubahan warna latar halus: `hover:bg-slate-50/80 transition-colors duration-150`.
3. **Fokus Aksesibilitas (a11y):**
   * Gunakan `focus-visible:ring-2` alih-alih `focus:outline-none` polos tanpa pengganti visual.

---

## Sumber Rujukan Tambahan
- `resources/anti-patterns-checklist.md`: Daftar periksa 20 anti-pola visual untuk audit cepat file Vue.
- `resources/emil-kowalski-principles.md`: Panduan implementasi mikro-interaksi dan kurva easing.
