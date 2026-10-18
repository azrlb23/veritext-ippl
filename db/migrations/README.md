# Database Migration Tracking: VeriText AI

Folder ini digunakan untuk melacak riwayat perubahan skema database (*database migration tracking*) dalam format SQL terversi.

## Daftar Versi Migrasi

| Versi | Nama Berkas | Tanggal | Deskripsi |
| :--- | :--- | :--- | :--- |
| `0001` | `0001_initial_schema.sql` | 11 Okt 2026 | Inisialisasi awal 14 tabel, pgvector extension, indeks HNSW, dan immutability rules. |

## Konvensi Penamaan Migrasi Baru
Setiap kali ada penambahan atau pengubahan skema database di masa mendatang:
1. Buat berkas baru dengan format nomor urut 4 digit: `0002_<deskripsi_perubahan>.sql`.
2. Sertakan blok `UP` (perubahan skema) dan `DOWN` (rollback).
3. Sinkronisasikan dengan skrip revisi Alembic di `backend/alembic/versions/`.
