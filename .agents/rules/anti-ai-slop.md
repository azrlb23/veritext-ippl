# Rules: Anti-AI Slop & Frontend Polish Standard
> Location: `.agents/rules/anti-ai-slop.md`
> Scope: `frontend/` (Vue 3, Tailwind CSS, TypeScript)
> Reference Skill: `skills/anti-ai-slop/SKILL.md`
> Style Reference: `frontend/design-reference/audyr/style-reference.md`

Semua agen pengembang WAJIB mematuhi aturan berikut saat membuat, memodifikasi, atau menata antarmuka komponen Vue:

## 1. Larangan Mutlak (Zero Tolerance for AI Slop):
1. **DILARANG menggunakan `transition: all`**: Selalu spesifikasikan properti yang ditransisikan (`transition-colors`, `transition-transform`, `transition-opacity`).
2. **DILARANG menggunakan gradien neon generic**: Jangan gunakan `from-purple-500 to-indigo-600` atau gradien heboh pada header/kartu. Latar belakang wajib utilitarian dan bersih (`bg-white` / `bg-slate-50`).
3. **DILARANG menggunakan `shadow-2xl` atau `rounded-3xl` berlebihan**: Gunakan border 1px crisp (`border border-slate-200`) dan bayangan lembut (`shadow-sm`).
4. **DILARANG menggunakan durasi animasi lambat**: Durasi interaksi tombol/menu maksimal `150ms - 200ms`. Jangan gunakan `duration-500` ke atas untuk interaksi klik.
5. **DILARANG menghilangkan outline fokus**: Elemen interaktif harus memiliki `focus-visible:ring-2 focus-visible:ring-blue-500`.

## 2. Standar Desain Analitik Akademik (Audyr Editorial Standard):
1. **Kerapatan Data Tinggi (High Density)**: VeriText AI adalah aplikasi audit naskah ilmiah. Pertahankan kerapatan informasi yang efisien (tabel kompak, padding proporsional `p-4` atau `p-5`).
2. **Angka Monospace / Tabular**: Skor plagiarisme, saldo token, dan angka statistik wajib menggunakan `tabular-nums` atau `font-mono`.
3. **Feedback Taktil**: Setiap tombol interaktif wajib memiliki state `:active` (misal: `active:scale-[0.98]`).
4. **Kontras Teks Terjaga**: Teks body minimal `text-slate-700` dan teks sekunder minimal `text-slate-500` di atas latar putih/terang.
5. **Acuan Token Desain**: Gunakan token warna & tipografi Audyr dari `frontend/design-reference/audyr/` (`--color-ink`, `--color-soft-mist`, `--font-inter`, hairline rules 1px #ededed, tracking -0.025em).
