# Database Architecture & Migration Tracking: VeriText AI

Direktori ini (`db/`) adalah pusat pengelolaan skema basis data, inisialisasi awal (DDL & DML), serta pelacakan migrasi (*schema versioning*) untuk sistem **VeriText AI** berbasis **PostgreSQL 16 + pgvector**.

---

## 1. Struktur Direktori `db/`

```text
db/
├── init/
│   ├── 01_extensions.sql       # DDL: Inisialisasi ekstensi pgcrypto dan pgvector (vector 384D)
│   ├── 02_schema_ddl.sql       # DDL: 14 tabel lengkap, constraints, indexes, HNSW, & rules
│   └── 03_seed_dml.sql         # DML: Data awal (Admin, Reviewer, Trial, Wallets, Sample Corpus)
│
├── migrations/
│   ├── README.md               # Panduan migrasi SQL vs Alembic
│   └── 0001_initial_schema.sql # Skrip migrasi terversi SQL mentah
│
└── README.md                   # Dokumentasi arsitektur dan panduan eksekusi
```

---

## 2. Cara Kerja Inisialisasi Otomatis (Docker Compose)

Pada berkas `docker-compose.yml`, direktori `./db/init` dimuat secara otomatis ke dalam `/docker-entrypoint-initdb.d` milik container PostgreSQL:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
  - ./db/init:/docker-entrypoint-initdb.d:ro
```

Saat kontainer PostgreSQL dijalankan untuk pertama kali (`docker compose up -d`), PostgreSQL akan mengeksekusi semua berkas `.sql` di folder `db/init/` secara berurutan sesuai alfabet:
1. `01_extensions.sql` mengaktifkan ekstensi `pgcrypto` dan `vector`.
2. `02_schema_ddl.sql` membuat 14 tabel, foreign keys, indeks B-Tree & HNSW, serta aturan *immutable audit log*.
3. `03_seed_dml.sql` memasukkan data pengguna awal, dompet token sambutan, dan sampel korpus internal.

---

## 3. Akun Default Hasil Seed DML (`03_seed_dml.sql`)

| Peran | Nama Lengkap | Email | Kata Sandi Default | Saldo Token |
| :--- | :--- | :--- | :--- | :--- |
| **ADMIN** | Super Administrator VeriText | `admin@veritext.ai` | `VeriText#2026` | 9.999 Token |
| **REVIEWER** | Dr. Hendra Gunawan, M.Kom. | `dosen@kampus.ac.id` | `VeriText#2026` | 100 Token |
| **TRIAL** | Mochammad Azriel Albian Putra | `azriel@kampus.ac.id` | `VeriText#2026` | 3 Token |
| **PREMIUM** | Siti Rahmawati | `siti@kampus.ac.id` | `VeriText#2026` | 25 Token |

---

## 4. Dua Jalur Migrasi yang Didukung

### Jalur A: Migrasi via Alembic (Rekomendasi untuk Backend Python)
Backend FastAPI memiliki integrasi Alembic yang tersimpan di `backend/alembic/versions/`.
```bash
cd backend
alembic upgrade head    # Menjalankan migrasi ke versi terbaru
alembic current         # Memeriksa revisi saat ini
```

### Jalur B: Migrasi Manual via SQL
Jika ingin mengeksekusi langsung menggunakan `psql` atau database GUI (DBeaver, pgAdmin):
```bash
psql -U veritext -d veritext_ai -f db/migrations/0001_initial_schema.sql
```
