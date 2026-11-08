# Catatan perubahan 2026-11-08

Semua perubahan sesi ini, per area. Cabang `feat/violet-kaca`. Rujukan kontrak: `API_CONTRACT.md`, skema: `DATABASE_SCHEMA.md`, status tugas: `tasks/todo.md`.

## 1. Keamanan unggahan (T9.1 sampai T9.3)
- Ekstensi hanya `pdf`, `docx`, `txt`. Ditolak (400): tanpa ekstensi, nama berjalur (`/`, `\`, `..`), karakter kontrol, nama lebih dari 200 karakter, ekstensi ganda (`a.pdf.exe`, `x.php.txt`). File: `services/upload_filename.py`.
- Verifikasi isi (422): PDF harus diawali `%PDF-`; DOCX harus ZIP berisi `word/document.xml` dengan hasil dekompresi maksimal 50 MB, rasio maksimal 100x, dan maksimal 5.000 entri (anti ZIP bomb); TXT tanpa byte NUL dan dapat didekode (UTF-8 atau CP1252). MIME yang diumumkan tidak boleh bertentangan dengan isi. File: `services/upload_content.py`.
- DOC_003: naskah di bawah 50 kata ditolak (422) pada `/documents/upload` dan `/documents/estimate`; berkas dihapus dan saldo tidak dipotong.
- Pembatas beban: PDF maksimal 400 halaman dan ekstraksi PDF/DOCX di subproses dengan batas waktu 30 detik (`services/safe_extract.py`, `engine/extract_cli.py`); maksimal 3 audit `QUEUED`/`PROCESSING` per pengguna; 10 unggahan atau estimasi per menit per pengguna lewat Redis (`services/upload_limits.py`, tanpa dependensi baru; bila Redis mati pembatas laju dilewati dan dicatat).
- Semua nilai dapat diatur lewat `.env` (`MIN_DOCUMENT_WORDS`, `MAX_PDF_PAGES`, `MAX_DOCX_UNCOMPRESSED_MB`, `MAX_DOCX_COMPRESSION_RATIO`, `EXTRACTION_TIMEOUT_SECONDS`, `MAX_ACTIVE_AUDITS_PER_USER`, `UPLOAD_RATE_LIMIT_PER_MINUTE`).

## 2. Asisten AI opsi B (T8.3)
- Migrasi `0006_chat_multi_document`: `chat_sessions.document_id` opsional, tabel `chat_session_documents`. `db/init/02_schema_ddl.sql` ikut diperbarui (database yang dibuat dari init tidak melewati Alembic; sudah ditandai `alembic stamp head`).
- `POST /chat/message` menerima `document_ids` (maks. 3) dan `session_id`. Konteks: enam kalimat paling relevan per naskah dipilih dengan embedding MiniLM (`services/chat_context.py`) lalu masuk prompt bersama enam pesan terakhir (`services/chat_prompt.py`). Endpoint baru: `GET /chat/sessions`, `GET /chat/sessions/{id}/messages`, `DELETE /chat/sessions/{id}`.

## 3. Biaya token, harga, dan Midtrans
- Biaya audit `min(5, ceil(kata/2500))`, batas FREE 2.500 kata (402, DOC_005), `POST /documents/estimate`.
- Harga paket disamakan dengan `AGENTS.md`: Starter 15 token Rp 25.000, Skripsi Pro 50 token Rp 65.000, Riset Intensif 150 token Rp 150.000; satuan Rp 2.000 per token (minimal 5, maksimal 500) lewat `package_id = pkg_tokens` (`services/billing_packages.py`). ID lama `pkg_10token` dan seterusnya dihapus.
- Midtrans Snap: `services/midtrans_snap.py` membuat transaksi Snap bila `MIDTRANS_SERVER_KEY` bukan kunci contoh; respons `/billing/topup` membawa `payment_ready` dan `client_key`; frontend memuat `snap.js` (`utils/midtransSnap.ts`). Dengan kunci contoh, invoice hanya dicatat. Alur pembayaran asli belum diuji karena kunci sandbox belum diisi.

## 4. Perbaikan galat
- Antrean: tugas dikirim ke Celery sebelum commit sehingga worker gagal ("Task not found"). Sekarang commit dulu (`services/document_service.py`).
- Anotasi laporan tidak membawa `sentence_id`, sehingga parafrase memakai UUID nol. `GET /reports/{id}` kini menambahkannya (`attach_sentence_ids`). Variasi parafrase palsu di frontend dihapus.
- Hapus naskah kini hard-delete: berkas, sesi chat terkait, baris dokumen (sisanya via `ON DELETE CASCADE`). Sertifikat/QR naskah itu menjadi tidak valid.
- Sertifikat PDF: persen sumber (`contribution_pct`), status mengikuti skor (Aman, Perlu ditinjau, Perlu direvisi), istilah awam, klaim "terenkripsi" dibuang. Tautan QR memakai `FRONTEND_URL` (ganti ke domain publik di produksi).
- Pesan galat validasi API (daftar JSON) di halaman masuk dan daftar kini diubah menjadi kalimat (`utils/errorMessage.ts`).
- Tes web-scan dibuat deterministik (`WEB_SCAN_ENABLED` dimatikan di tes itu).

## 5. Mesin Tier 2 (hari yang sama, tahap lanjutan)
- Tier 2 memakai indeks HNSW pgvector, bukan memuat korpus ke memori (`engine/corpus_ann.py`). Diuji langsung pada Postgres: hasil terdekat benar dan rencana kueri memakai `idx_document_chunks_vector`.
- Re-ranker IndoBERT `LazarusNLP/all-indobert-base-v4` (768-d) ditambahkan sebagai lapis kedua (`engine/tier2_indobert.py`). Lihat `AI_PIPELINE.md` bagian 2.2 untuk batasannya.

## 6. Lingkungan
- Python 3.12 (memenuhi "3.11+"): venv baru `backend/venv312`. `requirements.txt` kini membatasi `fastapi<0.130` dan `sqlalchemy<2.1` karena SQLAlchemy 2.1 mengubah driver bawaan PostgreSQL ke psycopg v3 dan memecahkan seluruh tes. Docker: Postgres (`veritext_postgres`) dan Redis (`veritext_redis`) berjalan; worker Celery berjalan.
- `/admin` diperiksa dengan peran ADMIN pada akun uji lokal `admin.uji@veritext-lokal.com` (dibuat langsung di basis data lokal, tanpa sandi di repositori; hapus bila tak perlu).

## 7. Antarmuka Violet Kaca
Ringkasan, Periksa naskah, Riwayat, Asisten AI, Akun, Token, ruang kerja `/audits/:id`, dan `/admin` sudah memakai gaya Violet Kaca (lihat `design/VIOLET-KACA.md`, tabel status). Navbar: Ringkasan, Periksa naskah, Riwayat, Asisten AI, Token; Akun dan Verifikasi QR ada di menu avatar. Komponen lama dihapus (dashboard lama, billing lama, HeatmapViewer, TierLegend, Modal, EmptyState, useModal).

## 8. Tahap penutup
- Sertifikat PDF digayakan ulang Violet Kaca (tinta, tint lilac, aksen violet, tanpa garis kotak); diperiksa lewat render poppler.
- Chat dan tulis ulang tidak lagi memberi jawaban tiruan: tanpa mesin AI, API mengembalikan 503 `AI_001` dan kuota tidak terpotong. Penyebab saat ini: kuota Gemini habis dan 9Router mati (lihat `PENUTUP-SESI-2026-11-08.md` bagian 5.1).
- `GEMINI_MODEL` default `gemini-3.8-flash` (2.5 Flash dipensiunkan untuk kunci baru). Label aksi log admin berbahasa Indonesia.
- Dokumen penutup lengkap: `docs/PENUTUP-SESI-2026-11-08.md`.

## 9. Masih terbuka
- Kunci sandbox Midtrans asli (uji pembayaran Snap).
- PDF sertifikat belum bergaya Violet Kaca.
- Label aksi log audit mentah (misalnya `SYSTEM_INIT`) di `/admin`.
