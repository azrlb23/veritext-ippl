# Emil Kowalski & Polish Frontend Principles

Prinsip desain micro-interaction dan CSS hygiene yang terinspirasi dari karya Emil Kowalski (pencipta Sonner, Vaul, dan interaksi di Vercel/Linear):

## 1. Dosa Terbesar: `transition: all`
### Mengapa Dilarang?
`transition: all` menginstruksikan browser memantau dan menginterpolasi setiap properti CSS, termasuk properti layout (`width`, `height`, `padding`, `margin`). Hal ini menyebabkan *layout thrashing*, drop framerate pada perangkat berspesifikasi rendah, dan efek "jelly" yang tidak diinginkan saat elemen pertama kali dimuat.

### Aturan:
Selalu gunakan nama properti yang spesifik:
- Ubah warna teks/latar: `transition-colors duration-150`
- Gerakan transformasi (scale, translate): `transition-transform duration-150 ease-out`
- Opasitas: `transition-opacity duration-150`
- Shadow: `transition-shadow duration-150`

## 2. Durasi & Kurva Easing
- **Mikro-interaksi (tombol, switch, checkbox):** `100ms - 150ms`.
- **Panel, drawer, modal dialog:** `200ms - 250ms`.
- **Dilarang keras:** Durasi di atas 300ms untuk aksi pengguna langsung (terasa lamban/lagging).
- **Kurva Easing:** Gunakan `ease-out` untuk elemen masuk dan `ease-in` untuk elemen keluar.

## 3. Tactile Feedback (Umpan Balik Taktil)
Setiap elemen yang dapat diklik WAJIB memiliki 3 status:
1. **Default:** Jelas terlihat dapat diklik (kontras cukup, kursor pointer).
2. **Hover:** Sedikit peningkatan kontras atau elevasi lembut (`hover:bg-blue-700` atau `hover:border-slate-300`).
3. **Active (Saat Ditekan):** Berikan efek tekan fisik menggunakan `active:scale-[0.98]` atau `active:bg-blue-800`.

## 4. Aksesibilitas Fokus (Keyboard Navigation)
Jangan pernah menghapus outline fokus tanpa pengganti:
- Buruk: `focus:outline-none`
- Benar: `focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2`
