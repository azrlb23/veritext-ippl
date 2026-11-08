# Database Schema & Storage Architecture: VeriText AI

Dokumen ini mendefinisikan skema fisik basis data relasional PostgreSQL 16 yang diperluas dengan ekstensi `pgvector` v0.7+. Skema ini mencakup 13 tabel utama yang ternormalisasi (3NF), strategi pengindeksan graf HNSW vektor berdimensi 384, dan aturan integritas referensial yang menjamin kepatuhan hak privasi data (UU PDP No. 27/2022).

---

## 1. Konfigurasi Lingkungan Basis Data

* **RDBMS Engine**: PostgreSQL 16.x (Relational ACID Compliant)
* **Ekstensi Wajib**:
  * `uuid-ossp`: Pembangkit UUID versi 4 acak untuk Primary Key.
  * `vector`: Penyimpanan dense embeddings dan pencarian kesamaan kosinus.
* **Parameter Indeks Vektor HNSW**:
  * Metrik Jarak: Cosine Distance Operator (`<=>`)
  * $m = 16$ (Jumlah koneksi maksimum per node graf)
  * $ef\_construction = 64$ (Kedalaman penelusuran saat pembangunan indeks graf)

---

## 2. Skema Data Definition Language (DDL SQL) Lengkap

```sql
-- Inisialisasi Ekstensi Inti
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- -------------------------------------------------------------
-- 1. IDENTITAS PENGGUNA & AUTENTIKASI
-- -------------------------------------------------------------

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'FREE' CHECK (role IN ('FREE', 'PREMIUM', 'ADMIN')),
    password_hash VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_email ON users(email);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);

CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reset_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- 2. DOMPET TOKEN & MONETISASI MIDTRANS
-- -------------------------------------------------------------

CREATE TABLE token_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 5 CHECK (balance >= 0),
    ai_trial_remaining INTEGER NOT NULL DEFAULT 3 CHECK (ai_trial_remaining >= 0),
    ai_chat_allowance_remaining INTEGER NOT NULL DEFAULT 0 CHECK (ai_chat_allowance_remaining >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_wallets_user_id ON token_wallets(user_id);

CREATE TABLE token_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES token_wallets(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('DEBIT_AUDIT', 'DEBIT_CHAT_PARAPHRASE', 'CREDIT_TOPUP', 'CREDIT_REFUND')),
    reference_id VARCHAR(100),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_token_tx_wallet ON token_transactions(wallet_id);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id VARCHAR(100) NOT NULL UNIQUE,
    purchase_scheme VARCHAR(30) NOT NULL CHECK (purchase_scheme IN ('BY_TOKEN', 'BY_PACKAGE')),
    package_type VARCHAR(50),
    token_amount INTEGER NOT NULL CHECK (token_amount > 0),
    gross_amount NUMERIC(12,2) NOT NULL CHECK (gross_amount >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SETTLEMENT', 'EXPIRE', 'CANCEL')),
    snap_token VARCHAR(255),
    snap_redirect_url TEXT,
    settled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_invoices_order_id ON invoices(order_id);
CREATE INDEX idx_invoices_user_id ON invoices(user_id);

-- -------------------------------------------------------------
-- 3. DOKUMEN & TUGAS PEMINDAIAN ASINKRON
-- -------------------------------------------------------------

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path TEXT,
    file_size_bytes INTEGER NOT NULL DEFAULT 0,
    word_count INTEGER NOT NULL DEFAULT 0,
    token_cost INTEGER NOT NULL DEFAULT 1,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_documents_user_id ON documents(user_id);

CREATE TABLE audit_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'QUEUED' CHECK (status IN ('QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    lexical_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    semantic_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    stylometric_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    composite_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    execution_time_sec NUMERIC(8,3),
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_tasks_doc ON audit_tasks(document_id);
CREATE INDEX idx_audit_tasks_user ON audit_tasks(user_id);

-- -------------------------------------------------------------
-- 4. HASIL KALIMAT HEATMAP & LAPORAN SERTIFIKAT
-- -------------------------------------------------------------

CREATE TABLE audit_sentences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES audit_tasks(id) ON DELETE CASCADE,
    sentence_order INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    current_text TEXT NOT NULL,
    match_type VARCHAR(20) NOT NULL DEFAULT 'NONE' CHECK (match_type IN ('NONE', 'RED', 'ORANGE', 'YELLOW', 'RESOLVED_GREEN')),
    similarity_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    matched_source_id UUID,
    is_modified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_sentences_task ON audit_sentences(task_id);

CREATE TABLE audit_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL UNIQUE REFERENCES audit_tasks(id) ON DELETE CASCADE,
    certificate_uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    qr_code_url TEXT NOT NULL,
    pdf_report_path TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_reports_certificate ON audit_reports(certificate_uuid);

-- -------------------------------------------------------------
-- 5. AI CHATBOT & SESI PARAFRASE INTERAKTIF
-- -------------------------------------------------------------

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_chat_sessions_doc ON chat_sessions(document_id);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('USER', 'ASSISTANT', 'SYSTEM')),
    content TEXT NOT NULL,
    mode VARCHAR(30) CHECK (mode IN ('CONSULTATION', 'SENTENCE', 'PARAGRAPH', 'FULL_PAGE')),
    suggested_options JSONB,
    applied_to_document BOOLEAN NOT NULL DEFAULT FALSE,
    target_sentence_id UUID REFERENCES audit_sentences(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);

-- -------------------------------------------------------------
-- 6. BASIS DATA KORPUS AKADEMIK & PGVECTOR HNSW
-- -------------------------------------------------------------

CREATE TABLE corpus_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(100) NOT NULL,
    doi_or_url TEXT,
    title TEXT NOT NULL,
    author VARCHAR(255),
    year INTEGER,
    language VARCHAR(10) DEFAULT 'id',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    corpus_doc_id UUID NOT NULL REFERENCES corpus_documents(id) ON DELETE CASCADE,
    chunk_order INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    kgram_hashes BIGINT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indeks Vektor HNSW Cosine Ops Berkecepatan Tinggi
CREATE INDEX idx_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- -------------------------------------------------------------
-- 7. AUDIT LOG LOGISTIK & KEAMANAN SISTEM
-- -------------------------------------------------------------

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_logs_event ON audit_logs(event_type);
```

---

## 3. Kebijakan Integritas & Kepatuhan Privasi (UU PDP)

1. **Hard-Delete Cascading**:
   Relasi Foreign Key dari tabel `documents` ke `audit_tasks`, `audit_sentences`, `audit_reports`, `chat_sessions`, dan `chat_messages` dikonfigurasi dengan klausul `ON DELETE CASCADE`. Ketika pengguna menghapus dokumen:
   * Seluruh entri hasil analisis, kalimat anotasi, laporan sertifikat, dan pesan chat terhapus permanen dari basis data secara instan dalam 1 operasi atomik.
   * Berkas fisik pada sistem penyimpanan lokal otomatis dihapus oleh worker.
2. **Isolasi Naskah Pengguna (Zero Auto-Ingestion)**:
   Tabel `documents` dan `audit_sentences` dipisahkan secara fisik dan logis dari tabel korpus `corpus_documents` dan `document_chunks`. Naskah yang dipindai tidak pernah dimasukkan ke dalam basis data korpus publik.
3. **Pemberian Kunci Baris Transaksi Moneter**:
   Operasi perubahan saldo dompet token pada tabel `token_wallets` dan pembaruan invoice pada tabel `invoices` wajib menyertakan klausul `SELECT ... FOR UPDATE` untuk mencegah eksploitasi saldo ganda.
