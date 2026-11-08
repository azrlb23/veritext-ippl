-- ============================================================
-- VERITEXT AI: DATABASE SEED DATA (DML)
-- ============================================================
-- File: db/init/03_seed_dml.sql
-- Keterangan: Data awal (Seed) untuk Pengguna Default, Paket Token, dan Sampel Korpus

-- 1. SEED PENGGUNA DEFAULT
-- Password Default: 'Azrlb123*' (bcrypt hash)
INSERT INTO users (id, full_name, email, password_hash, role, is_active)
VALUES 
    -- Super Administrator (ADMIN)
    ('11111111-1111-1111-1111-111111111111', 'Azriel Albian', 'azrielalbian23@gmail.com', '$2b$12$8/4q7HKkppgIsw.gbmuklOE7jG.bL3Jtuft7aSmBS7m.deujuh38a', 'ADMIN', TRUE),
    
    -- Akun Berbayar (PREMIUM)
    ('22222222-2222-2222-2222-222222222222', 'Azriel Albian', 'azrielalbian8@gmail.com', '$2b$12$8/4q7HKkppgIsw.gbmuklOE7jG.bL3Jtuft7aSmBS7m.deujuh38a', 'PREMIUM', TRUE),
    
    -- Akun Pengguna Gratis (FREE)
    ('33333333-3333-3333-3333-333333333333', 'Azriel Albian', 'albianazriel3@gmail.com', '$2b$12$8/4q7HKkppgIsw.gbmuklOE7jG.bL3Jtuft7aSmBS7m.deujuh38a', 'FREE', TRUE)
ON CONFLICT (email) DO NOTHING;

-- 2. SEED DOMPET TOKEN (Wallets)
INSERT INTO token_wallets (id, user_id, balance, ai_trial_remaining, ai_chat_allowance_remaining)
VALUES 
    ('a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 9999, 3, 0), -- Admin Unlimited Monitoring
    ('a2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 100, 3, 10), -- Premium Saldo Awal
    ('a3333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', 5, 3, 0)     -- Free User Sambutan (5 token)
ON CONFLICT (user_id) DO NOTHING;

-- 3. SEED MUTASI TOKEN AWAL (Ledger Transactions)
INSERT INTO token_transactions (wallet_id, transaction_type, amount, balance_after, note)
VALUES 
    ('a1111111-1111-1111-1111-111111111111', 'CREDIT_TOPUP', 9999, 9999, 'Alokasi token inisial Administrator'),
    ('a2222222-2222-2222-2222-222222222222', 'CREDIT_TOPUP', 100, 100, 'Alokasi token inisial Premium'),
    ('a3333333-3333-3333-3333-333333333333', 'CREDIT_TOPUP', 5, 5, 'Bonus sambutan pendaftaran akun baru (5 token gratis)');

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
