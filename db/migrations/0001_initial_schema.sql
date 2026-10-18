-- ============================================================
-- MIGRATION: 0001_initial_schema
-- ============================================================
-- Tanggal: 2026-10-11
-- Target: PostgreSQL 16 + pgvector
-- Keterangan: Pembuatan ekstensi pgcrypto, vector, dan 14 tabel inti VeriText AI

-- UP
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    institution VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'TRIAL' CHECK (role IN ('TRIAL', 'PREMIUM', 'REVIEWER', 'ADMIN')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_count SMALLINT NOT NULL DEFAULT 0,
    lockout_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);

-- 2. sessions
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL UNIQUE,
    user_agent TEXT,
    ip_address VARCHAR(45),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions (expires_at);

-- 3. password_resets
CREATE TABLE IF NOT EXISTS password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. token_wallets
CREATE TABLE IF NOT EXISTS token_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_token_wallets_user_id ON token_wallets (user_id);

-- 5. token_transactions
CREATE TABLE IF NOT EXISTS token_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID NOT NULL REFERENCES token_wallets(id),
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('DEBIT_AUDIT', 'CREDIT_TOPUP', 'CREDIT_REFUND', 'CREDIT_ADMIN', 'DEBIT_ADMIN')),
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    reference_id UUID,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_token_transactions_wallet_id ON token_transactions (wallet_id);
CREATE INDEX IF NOT EXISTS idx_token_transactions_created_at ON token_transactions (created_at DESC);

-- 6. invoices
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    order_id VARCHAR(100) NOT NULL UNIQUE,
    snap_token TEXT,
    package_name VARCHAR(100) NOT NULL,
    token_amount INTEGER NOT NULL,
    gross_amount BIGINT NOT NULL,
    payment_method VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PAID', 'EXPIRED', 'FAILED', 'CANCEL')),
    midtrans_transaction_id VARCHAR(255),
    paid_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices (user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_order_id ON invoices (order_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices (status);

-- 7. documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL UNIQUE,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    word_count INTEGER,
    sha256_hash VARCHAR(64),
    status VARCHAR(50) NOT NULL DEFAULT 'UPLOADED' CHECK (status IN ('UPLOADED', 'PROCESSING', 'READY', 'ERROR', 'DELETED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents (user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents (status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents (created_at DESC);

-- 8. audit_tasks
CREATE TABLE IF NOT EXISTS audit_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    celery_task_id VARCHAR(255) UNIQUE,
    audit_depth VARCHAR(50) NOT NULL DEFAULT 'FULL' CHECK (audit_depth IN ('TIER1_ONLY', 'FULL')),
    status VARCHAR(50) NOT NULL DEFAULT 'QUEUED' CHECK (status IN ('QUEUED', 'PROCESSING', 'SUCCESS', 'FAILED', 'CANCELLED', 'REVOKED')),
    progress_pct SMALLINT NOT NULL DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
    current_stage VARCHAR(100),
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_tasks_user_id ON audit_tasks (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_tasks_document_id ON audit_tasks (document_id);
CREATE INDEX IF NOT EXISTS idx_audit_tasks_status ON audit_tasks (status);
CREATE INDEX IF NOT EXISTS idx_audit_tasks_celery_id ON audit_tasks (celery_task_id);

-- 9. audit_sentences
CREATE TABLE IF NOT EXISTS audit_sentences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_task_id UUID NOT NULL REFERENCES audit_tasks(id) ON DELETE CASCADE,
    sentence_index INTEGER NOT NULL,
    sentence_text TEXT NOT NULL,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    word_count SMALLINT NOT NULL,
    is_citation BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_audit_task_sentence_index UNIQUE (audit_task_id, sentence_index)
);
CREATE INDEX IF NOT EXISTS idx_audit_sentences_task_id ON audit_sentences (audit_task_id);

-- 10. audit_reports
CREATE TABLE IF NOT EXISTS audit_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_task_id UUID NOT NULL REFERENCES audit_tasks(id) ON DELETE CASCADE UNIQUE,
    verification_uuid UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    score_lexical NUMERIC(5,2),
    score_semantic NUMERIC(5,2),
    score_stylometric NUMERIC(5,2),
    score_composite NUMERIC(5,2),
    heatmap_annotations JSONB NOT NULL DEFAULT '[]'::jsonb,
    matched_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    pdf_path VARCHAR(500),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_reports_task_id ON audit_reports (audit_task_id);
CREATE INDEX IF NOT EXISTS idx_audit_reports_verification_uuid ON audit_reports (verification_uuid);

-- 11. corpus_documents
CREATE TABLE IF NOT EXISTS corpus_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_by UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    category VARCHAR(255),
    academic_year VARCHAR(20),
    stored_filename VARCHAR(500) NOT NULL UNIQUE,
    sha256_hash VARCHAR(64) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING_INDEX' CHECK (status IN ('PENDING_INDEX', 'INDEXING', 'INDEXED', 'ERROR', 'DELETED')),
    total_chunks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_corpus_documents_status ON corpus_documents (status);
CREATE INDEX IF NOT EXISTS idx_corpus_documents_category ON corpus_documents (category);
CREATE INDEX IF NOT EXISTS idx_corpus_documents_sha256 ON corpus_documents (sha256_hash);

-- 12. document_chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    corpus_doc_id UUID NOT NULL REFERENCES corpus_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    start_char INTEGER,
    end_char INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_document_chunks_vector
    ON document_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS idx_document_chunks_corpus_doc_id ON document_chunks (corpus_doc_id);

-- 13. lexical_fingerprints
CREATE TABLE IF NOT EXISTS lexical_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    corpus_doc_id UUID NOT NULL REFERENCES corpus_documents(id) ON DELETE CASCADE,
    fingerprint_hash BIGINT NOT NULL,
    position_start INTEGER,
    position_end INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lexical_fingerprints_hash ON lexical_fingerprints (fingerprint_hash);
CREATE INDEX IF NOT EXISTS idx_lexical_fingerprints_corpus_doc_id ON lexical_fingerprints (corpus_doc_id);

-- 14. audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES users(id),
    actor_ip VARCHAR(45),
    actor_user_agent TEXT,
    action_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    action_result VARCHAR(50) NOT NULL DEFAULT 'SUCCESS' CHECK (action_result IN ('SUCCESS', 'FAILURE', 'BLOCKED')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_id ON audit_logs (actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON audit_logs (action_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs (resource_type, resource_id);

DROP RULE IF EXISTS audit_logs_no_update ON audit_logs;
DROP RULE IF EXISTS audit_logs_no_delete ON audit_logs;
CREATE RULE audit_logs_no_update AS ON UPDATE TO audit_logs DO INSTEAD NOTHING;
CREATE RULE audit_logs_no_delete AS ON DELETE TO audit_logs DO INSTEAD NOTHING;
