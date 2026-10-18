-- ============================================================
-- VERITEXT AI: DATABASE EXTENSIONS INITIALIZATION
-- ============================================================
-- File: db/init/01_extensions.sql
-- Keterangan: Mengaktifkan ekstensi kriptografi dan pencarian vektor

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Verifikasi keberhasilan instalasi ekstensi
SELECT extname, extversion FROM pg_extension WHERE extname IN ('pgcrypto', 'vector');
