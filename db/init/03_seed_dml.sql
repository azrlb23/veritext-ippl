-- ============================================================
-- VERITEXT AI: DATABASE SEED DATA (DML)
-- ============================================================
-- File: db/init/03_seed_dml.sql
-- Keterangan: Data awal (Seed) untuk Pengguna Default, Paket Token, dan Sampel Korpus

-- 1. SEED PENGGUNA DEFAULT
-- Password Default: 'VeriText#2026' (bcrypt hash)
INSERT INTO users (id, full_name, email, institution, password_hash, role, is_active)
VALUES 
    -- Super Administrator
    ('11111111-1111-1111-1111-111111111111', 'Super Administrator VeriText', 'admin@veritext.ai', 'VeriText AI System', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L5.X4S/W6', 'ADMIN', TRUE),
    
    -- Dosen / Reviewer Kampus
    ('22222222-2222-2222-2222-222222222222', 'Dr. Hendra Gunawan, M.Kom.', 'dosen@kampus.ac.id', 'Institut Teknologi Nasional', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L5.X4S/W6', 'REVIEWER', TRUE),
    
    -- Mahasiswa / Trial User
    ('33333333-3333-3333-3333-333333333333', 'Mochammad Azriel Albian Putra', 'azriel@kampus.ac.id', 'Institut Teknologi Nasional', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L5.X4S/W6', 'TRIAL', TRUE),

    -- Mahasiswa / Premium User
    ('44444444-4444-4444-4444-444444444444', 'Siti Rahmawati', 'siti@kampus.ac.id', 'Universitas Indonesia', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L5.X4S/W6', 'PREMIUM', TRUE)
ON CONFLICT (email) DO NOTHING;

-- 2. SEED DOMPET TOKEN (Wallets)
INSERT INTO token_wallets (id, user_id, balance)
VALUES 
    ('a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 9999), -- Admin Unlimited
    ('a2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 100),  -- Dosen Kuota Kelas
    ('a3333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', 3),    -- Trial User Sambutan (3 token)
    ('a4444444-4444-4444-4444-444444444444', '44444444-4444-4444-4444-444444444444', 25)   -- Premium User
ON CONFLICT (user_id) DO NOTHING;

-- 3. SEED MUTASI TOKEN AWAL (Ledger Transactions)
INSERT INTO token_transactions (wallet_id, transaction_type, amount, balance_after, note)
VALUES 
    ('a1111111-1111-1111-1111-111111111111', 'CREDIT_ADMIN', 9999, 9999, 'Alokasi token inisial Administrator'),
    ('a2222222-2222-2222-2222-222222222222', 'CREDIT_ADMIN', 100, 100, 'Alokasi token verifikasi tugas kuliah'),
    ('a3333333-3333-3333-3333-333333333333', 'CREDIT_ADMIN', 3, 3, 'Bonus sambutan pendaftaran akun baru (3 token gratis)'),
    ('a4444444-4444-4444-4444-444444444444', 'CREDIT_TOPUP', 25, 25, 'Top-up paket sidang kilat via Midtrans');

-- 4. SEED SAMPEL KORPUS PEMBANDING INTERNAL (Corpus Documents)
INSERT INTO corpus_documents (id, uploaded_by, title, category, academic_year, stored_filename, sha256_hash, status, total_chunks)
VALUES 
    ('c1111111-1111-1111-1111-111111111111', 
     '22222222-2222-2222-2222-222222222222', 
     'Analisis Performa Model Transformer pada Pemrosesan Teks Bahasa Indonesia', 
     'Informatika / AI', 
     '2025/2026', 
     'corpus_nlp_transformer_2025.pdf', 
     'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 
     'INDEXED', 
     2)
ON CONFLICT (stored_filename) DO NOTHING;

-- 5. SEED VEKTOR CHUNKS SAMPEL (384-Dimensi Vektor pgvector)
-- Catatan: Vektor diisi representasi 384 elemen float32
INSERT INTO document_chunks (id, corpus_doc_id, chunk_index, chunk_text, embedding, start_char, end_char)
VALUES 
    ('d1111111-1111-1111-1111-111111111111', 
     'c1111111-1111-1111-1111-111111111111', 
     0, 
     'Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi semantik berbasis deep learning.', 
     array_fill(0.051::real, ARRAY[384])::vector, 
     0, 
     115),
    ('d2222222-2222-2222-2222-222222222222', 
     'c1111111-1111-1111-1111-111111111111', 
     1, 
     'Penerapan struktur indeks Hierarchical Navigable Small World memungkinkan penelusuran tetangga terdekat secara efisien pada basis data PostgreSQL.', 
     array_fill(0.042::real, ARRAY[384])::vector, 
     116, 
     263)
ON CONFLICT (id) DO NOTHING;

-- 6. SEED SIDIK JARI LEKSIKAL WINNOWING (Lexical Fingerprints)
INSERT INTO lexical_fingerprints (corpus_doc_id, fingerprint_hash, position_start, position_end)
VALUES 
    ('c1111111-1111-1111-1111-111111111111', 9876543210123456, 0, 45),
    ('c1111111-1111-1111-1111-111111111111', 1234567890987654, 46, 115)
ON CONFLICT DO NOTHING;

-- 7. SEED AUDIT LOGS AWAL (Jejak Keamanan Sistem)
INSERT INTO audit_logs (actor_id, actor_ip, actor_user_agent, action_type, resource_type, resource_id, action_result, metadata)
VALUES 
    ('11111111-1111-1111-1111-111111111111', '127.0.0.1', 'System Provisioner', 'SYSTEM_INIT', 'DATABASE', '11111111-1111-1111-1111-111111111111', 'SUCCESS', '{"description": "Inisialisasi basis data dan data seed awal selesai"}');
