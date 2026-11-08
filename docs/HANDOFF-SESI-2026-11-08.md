# Serah-terima sesi 2026-11-08 (untuk sesi baru)

Baca urutan ini dahulu: `AGENTS.md`, berkas ini, `docs/design/VIOLET-KACA.md`, `tasks/todo.md` (Phase 8 dan 9), lalu `docs/API_CONTRACT.md`, `docs/DATABASE_SCHEMA.md`, `docs/ATOMIC_CODING_STANDARDS.md`. Bahasa pengguna dan UI: Indonesia. Pengguna: Azriel (proyek IPPL, VeriText AI).

## 1. Aturan kerja dari pengguna
- **Jangan commit otomatis.** Di akhir setiap penerapan, tanyakan apakah pengguna mau commit, lalu tunggu jawabannya. Push ke remote hanya bila diminta.
- Kerjakan bertahap, tiap irisan 1 sampai 4 berkas (AGENTS.md), jalankan tes, lalu laporkan.
- Selalu lihat hasil UI di browser pane pada tiga lebar: 1440, 768, 390. Tidak boleh ada scroll horizontal, target sentuh minimal 44 px.
- Mengubah skema DB atau menambah dependensi butuh persetujuan. Yang sudah disetujui: opsi B untuk chat (lihat bagian 4). Belum disetujui: dependensi baru (misalnya `slowapi`).
- Nol emoji, berkas maksimal 150 baris, tanpa kata UU, akademik, kampus, institut di UI.

## 2. Keadaan repositori
- Cabang kerja: `feat/violet-kaca`. Commit: `022ac66` (beranda, navbar, footer), `3f7592b` (navbar baru, verifikasi, latar ubin), `f1c64e5` (halaman auth). Hanya cabang `snapshot/2026-11-08-sebelum-violet-kaca` (`cdb6646`) yang sudah di-push ke GitHub.
- **Belum di-commit (sekitar 30 berkas):** tahap 1 (halaman `/periksa`, navbar pengguna masuk, komponen `DropArea`, `DepthChoice`, `AuditSummary`) dan tahap 2 (biaya token per kata). Pengguna belum menjawab pertanyaan commit. Tanyakan di awal sesi.
- Server dev: frontend `localhost:5173` (milik pengguna, HMR), backend `localhost:8000`. `.env` lokal diubah `MAX_FILE_SIZE_MB=15`; backend harus dimuat ulang agar terbaca.
- Akun seed lokal (`db/init/03_seed_dml.sql`): ADMIN azrielalbian23@gmail.com, PREMIUM azrielalbian8@gmail.com (100 token), FREE albianazriel3@gmail.com. Sandi seragam diberikan pengguna di chat serah-terima; minta pengguna bila perlu login di browser pane. Jangan menuliskan sandi di balasan.
- Python venv 3.9 (target dokumen 3.11, mesin tidak punya). `sentence-transformers` 5.1.2 dan `torch` 2.8.0 terpasang. Model di `~/.cache/huggingface`: MiniLM multibahasa, mMARCO, dan bge-reranker-v2-m3 (yang terakhir terhubung ke Tier 2 lewat `engine/tier2_reranker.py`).
- Tes: backend `cd backend && ./venv/bin/pytest -q` (253 lulus), `./venv/bin/ruff check app tests` (bersih). Frontend `cd frontend && npm run build && node src/tests/navigation.test.mjs`.

## 3. Sistem gaya Violet Kaca (sudah berlaku)
Panduan: `docs/design/VIOLET-KACA.md`. Inti: dasar `#F2F2F4`, kartu putih `shadow-float`/`shadow-lift`, gradasi violet, tinta `#14111C` untuk semua tombol, isian berupa garis (`components/auth/AuthField.vue`), judul dengan baris miring `.vt-accent`, latar lewat `meta.backdrop` pada rute (`home`, `page`, `auth`) yang memakai `components/landing/LandingBackdrop.vue` dan `GlassTileField.vue`. Komponen harus terpisah dari latar (kartu putih berbayangan; elemen sekunder dalam kartu memakai tint `#F3EEFA`). Dilarang titik, pulse, outline berwarna, kotak panggung berbatas keras.

Halaman selesai: beranda `/`, `/verify`, `/login`, `/register`, `/forgot-password`, `/reset-password`, `/onboarding`, `/periksa`, navbar, footer, toast, modal sambutan.
Halaman yang MASIH BERLAYOUT LAMA (harus dirombak total): `/dashboard`, `/billing`, `/audits/:id` (ruang kerja), `/admin`. Navbar pengguna masuk sekarang: Ringkasan, Periksa naskah, Token, Verifikasi QR. Rencana: Akun dan Verifikasi masuk menu avatar; pertimbangkan bilah tab bawah di ponsel.

## 4. Pekerjaan yang belum dikerjakan (urutan disarankan)
1. **T9.1 sampai T9.3 (keamanan unggahan, prioritas):** ekstensi hanya `pdf/docx/txt`, verifikasi isi (magic bytes: `%PDF-`, ZIP dengan `word/document.xml`, TXT tanpa NUL), tolak ekstensi ganda dan nama berjalur, minimal 50 kata (DOC_003, 422, juga di `/documents/estimate`), dan pembatas beban (halaman PDF, ukuran dekompresi DOCX, waktu ekstraksi, antrean aktif per pengguna, laju unggah). Rincian di `tasks/todo.md` Phase 9. Titik masuk kode: `backend/app/services/document_validator.py`, `upload_charging.py`, `word_counter.py`, `api/v1/documents.py`.
2. **T8.3 Asisten AI, opsi B (skema disetujui):** `chat_sessions.document_id` jadi opsional dan tabel relasi `chat_session_documents` lewat migrasi Alembic (head sekarang `0005_chat_and_subcredits`); endpoint daftar sesi, riwayat pesan, dan kirim pesan dengan `document_ids`; konteks dari kalimat paling relevan (MiniLM) masuk ke prompt. **Temuan penting:** `POST /chat/message` sekarang TIDAK membaca dokumen (prompt hanya `"Bantu penulisan:" + pertanyaan`). Perbarui `DATABASE_SCHEMA.md` dan `API_CONTRACT.md`.
3. **T8.4 dan T9.4 halaman:** `/asisten`, `/riwayat`, `/akun` (profil, ganti kata sandi, hapus akun; kontrak `DELETE /auth/me` dan `change-password` sudah ada), perampingan `/dashboard` menjadi Ringkasan, `/billing` menjadi Token (saldo, paket, invoice), lalu ruang kerja `/audits/:id` dan `/admin`.
4. Setelah unggah berhasil, `PeriksaView` mengarah ke `/dashboard`; pindahkan ke `/riwayat` bila halaman itu sudah ada.

## 5. Keputusan bisnis yang sudah final
- Biaya audit `min(5, ceil(kata / 2500))`, minimal 1, tidak bergantung kedalaman (sudah diterapkan: `token_pricing.py`, `upload_charging.py`). Akun FREE maksimal 2.500 kata (402, `DOC_005`). Berkas maksimal 15 MB. `POST /documents/estimate` menghitung biaya tanpa menyimpan.
- Pilihan "Pindai cepat" tidak lebih murah dari "Audit penuh"; tanyakan pengguna bila ingin diskon.
- ADMIN 100% read-only. Naskah pengguna tidak pernah masuk `corpus_documents`. Hapus naskah = hard-delete cascade.

## 6. Celah dan catatan
- `DOC_003` tercantum di kontrak tetapi belum ada di kode (T9.2).
- Harga paket di `backend/app/services/billing_service.py` (50 token = Rp 100.000, dan seterusnya) berbeda dari AGENTS.md dan halaman billing (50 token = Rp 65.000; Rp 25.000 / 15 token; Rp 150.000 / 150 token). Minta keputusan pengguna lalu samakan.
- Tier 2 tidak mengquery pgvector (membandingkan di memori). Dokumen menyebut HNSW.
- IndoBERT re-ranker disebut di dokumen tetapi tidak ada di kode (yang dipakai bge-reranker-v2-m3).
- Memori proyek: `/Users/azrlb23/.claude/projects/-Users-azrlb23-Documents-IPPL/memory/` (gaya, alur kerja, keputusan).
