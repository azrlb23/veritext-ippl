# VeriText AI Project Context (Agent Handoff Artifact)

> Tujuan berkas ini: Memungkinkan sesi AI baru melanjutkan pekerjaan rekayasa kode tanpa harus membaca ulang seluruh riwayat percakapan atau menebak-nebak isi repositori.
> Selalu verifikasi terhadap `AGENTS.md`, `docs/BLUEPRINT.md`, `docs/API_CONTRACT.md`, dan `tasks/todo.md`.

---

## 1. Status Artefak Dokumen & Diagram (100% Selesai & Terkunci)

Seluruh dokumen spesifikasi dan diagram arsitektur telah selesai disusun, diverifikasi, dan diselaraskan 100% dengan standar IEEE & format `.docx` akademik:
1. **SRS (Software Requirements Specification)**: `SRS_Sistem_Deteksi_Plagiarisme_Hybrid.md` (559 baris, 11 Use Case `UC-01` s/d `UC-11`, 0 emoji, 0 callout).
2. **SDD (Software Design Document)**: `SDD_Sistem_Deteksi_Plagiarisme_Hybrid.md` (931 baris, DDL 13 tabel PostgreSQL 16 + `pgvector` HNSW, 25 endpoint REST API, 17 kode error, 0 emoji, 0 callout).
3. **29 Diagram UML & Arsitektur Draw.io Light Mode (`#FFFFFF`)**:
   - Berkas sumber XML: `diagrams/drawio/` (29 berkas `.drawio`).
   - Berkas gambar PNG: `diagrams/exported/` (29 berkas `.png`: `Use Case Diagram`, `Architecture Diagram`, `Component Diagram`, `Class Diagram`, `DFD0`, `DFD1`, `DFD2`, `AD1`–`AD11`, `SD1`–`SD11`).
4. **Basis Pengetahuan AI (`docs/`)**:
   - `docs/BLUEPRINT.md`: Arsitektur 4-lapis, Capability Map (`mod-*`), dan 5 Invarian Sistem.
   - `docs/API_CONTRACT.md`: Kontrak JSON 25 endpoint REST API, Webhook SHA-512 Midtrans, dan 17 kode error.
   - `docs/DATABASE_SCHEMA.md`: Skema DDL SQL 13 tabel + `audit_logs` dan indeks HNSW `vector(384)`.
   - `docs/AI_PIPELINE.md`: Spesifikasi 3-Step Hybrid AI Pipeline & Dual-Engine LLM Gateway (Gemini 2.5 Flash + DeepSeek v4.1 Flash via 9Router).
   - `docs/ATOMIC_CODING_STANDARDS.md`: Aturan kode atomik (Sub-150 LOC per berkas, SRP, S/M Task Slices).
   - `docs/SPEC_DRIVEN_DEVELOPMENT.md`: Siklus 5-fase berpagar gerbang (*Gated Lifecycle*).
   - `docs/FRONTEND-HANDOFF.md`: Panduan arsitektur UI Split-Screen Studio Workspace & 3-Layer Frontend.

---

---

## 2. Status Penyelarasan Arsitektur & Pembersihan Kode (100% Selesai)

Pembersihan dan dekomposisi menyeluruh (*Wave 2 Atomic Sweep & Phase 7 Codebase De-bloating*) telah selesai dieksekusi 100%:
1. **Dekomposisi Berkas Monolitik (< 150 LOC)**: Seluruh "God Files" di backend dan frontend telah dipecah menjadi modul-modul atomik yang mematuhi Single Responsibility Principle.
2. **Pembersihan Fitur Warisan Kampus**:
   - Seluruh rute dan layanan unggah ZIP korpus manual oleh dosen (`corpus.py`, `corpus_service.py`, `corpus_indexer_helper.py`, `corpus_ingest_worker.py`) telah dihapus.
   - Fitur mutasi akun dan tuning bobot algoritma via UI admin telah dihapus total. Admin kini berstatus 100% Read-Only Monitoring (`GET /analytics`, `GET /transactions`, `GET /system-health`, `GET /audit-logs`).
   - Seluruh 15 komponen frontend yatim telah dihapus bersih.
3. **Harmonisasi SaaS 3-Role Model (`FREE`, `PREMIUM`, `ADMIN`)**:
   - Peran default pendaftaran akun baru diselaraskan ke `FREE` (dengan bonus sambutan 5 Token + 3x Trial AI).
   - Peran usang `TRIAL` dan `REVIEWER` telah dihapus dari skema dan batasan database.
4. **Eliminasi Tuntas Atribut `institution`**:
   - Atribut `institution` telah dihapus 100% dari model `User` dan `AuditReport`, skema Pydantic, service sertifikat/invoice PDF, endpoint API, dan skrip inisialisasi basis data.
5. **Dual-Engine LLM Gateway & AI Studio Workspace**:
   - Gateway `gemini_client.py` + `deepseek_client.py` aktif dengan failover otomatis.
   - Studio Workspace split-screen di frontend aktif dengan dukungan interaksi parafrase 3-mode dan penggantian teks naskah in-place.
6. **Log Audit Lengkap**:
   - Rincian seluruh berkas yang dihapus dan dimodifikasi terdokumentasi pada `docs/CLEANUP_AUDIT_LOG.md`.
