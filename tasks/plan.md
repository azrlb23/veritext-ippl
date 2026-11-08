# Implementation Plan: VeriText AI (Spec-Driven & Atomic Execution)

## 1. Overview & Alignment with SRS & SDD
Rencana implementasi bertahap ini menerjemahkan spesifikasi dari `SRS_Sistem_Deteksi_Plagiarisme_Hybrid.md`, `SDD_Sistem_Deteksi_Plagiarisme_Hybrid.md`, dan `docs/BLUEPRINT.md` ke dalam alur kerja **Spec-Driven Development (SDD)** dengan aturan **Atomic Code Architecture** (maksimal 150 baris per berkas, 1–4 berkas per tugas).

---

## 2. Capability Map (Aligned with `docs/BLUEPRINT.md`)

| Module ID | Responsibility | SRS Mapping | Depends On |
|---|---|---|---|
| `mod-auth` | Autentikasi JWT (15m) + Refresh Cookie (7d) + Google OAuth 2.0, RBAC 3-Role (`FREE`, `PREMIUM`, `ADMIN`), provisi otomatis 5 Token + 3x Trial AI saat registrasi | FR-AUTH-01 s/d 07 | — |
| `mod-preprocessor` | Validasi magic bytes MIME (.pdf, .docx, .txt maks 15 MB), ekstraksi teks bersih, segmentasi kalimat, batas 2.500 kata `FREE`, dan rumus biaya $\min(5, \lceil \text{kata}/2500 \rceil)$ Token | FR-DOC-01 s/d 08 | `mod-auth` |
| `mod-pipeline-lexical` | Step 1 Deteksi Leksikal Winnowing ($k=5, w=4$) + Rabin-Karp Rolling Hash ($b=257, M=10^9+7$), Tag `RED` ($\ge 80\%$) dan akuisisi korpus otomatis Dual-Scope | FR-CORP-01 s/d 04, FR-DET-01 s/d 02 | `mod-preprocessor` |
| `mod-pipeline-semantic` | Step 2 Deteksi Semantik `paraphrase-multilingual-MiniLM-L12-v2` (384-d) + kueri HNSW `pgvector` (`<=>`) + re-ranker `IndoBERT`, Tag `ORANGE` ($\ge 75\%$) | FR-DET-03 s/d 05 | `mod-pipeline-lexical` |
| `mod-pipeline-judge` | Step 3 Stilometri Goh & Barabasi Burstiness $B$ & TTR + **Dual-Engine LLM Gateway** (Gemini 2.5 Flash + DeepSeek v4.1 Flash via 9Router Failover), Tag `YELLOW`, skor komposit $0.50 + 0.35 + 0.15$ | FR-DET-06 s/d 10 | `mod-pipeline-semantic` |
| `mod-assistant` | AI Chatbot ber-Academic Guardrail (`CHAT_001`), Parafrase Instan 3-Mode (`SENTENCE`, `PARAGRAPH`, `FULL_PAGE`) 3 variasi, dan in-place replacement (`RESOLVED_GREEN`) | FR-CHAT-01 s/d 07 | `mod-pipeline-judge`, `mod-billing` |
| `mod-billing` | Dompet Token (`token_wallets`), pembelian `BY_TOKEN` & `BY_PACKAGE` via Midtrans Snap, verifikasi webhook SHA-512 atomik (`FOR UPDATE`), auto-upgrade `PREMIUM` | FR-PAY-01 s/d 09 | `mod-auth` |
| `mod-report-admin` | Unduh PDF resmi WeasyPrint ber-QR Code (`PREMIUM`), verifikasi QR publik (`/verify/{uuid}`), hard-delete cascade UU PDP, dan Dasbor Admin 100% Read-Only (`GET` murni) | FR-REP-01 s/d 08, FR-ADM-01 s/d 04 | `mod-pipeline-judge`, `mod-billing` |

---

## 3. Phased Implementation Roadmap

### Phase 1: Specification, UML Diagrams & AI Knowledge Base Harmonization
- **Goal**: Menyelesaikan 29 diagram Draw.io Light Mode, menyelaraskan SRS & SDD dengan struktur tabel `.docx`, dan membangun direktori `docs/` serta `AGENTS.md`.
- **Status**: [x] Completed

### Phase 2: Database Schema Alignment & Dual-Engine LLM Gateway (`mod-pipeline-judge` & DB)
- **Goal**: Menyelaraskan model SQLAlchemy & migrasi Alembic dengan 13 tabel pada `docs/DATABASE_SCHEMA.md` (`chat_sessions`, `chat_messages`, kolom `ai_trial_remaining`, `ai_chat_allowance_remaining`, `RESOLVED_GREEN`), serta membangun modul atomik `backend/app/llm/` (`gemini_client.py`, `deepseek_client.py`, `gateway.py`) dengan semua berkas $\le 150$ LOC.
- **Status**: [x] Completed

### Phase 3: Backend De-bloating & Atomic Pipeline Refactor (`mod-auth`, `mod-preprocessor`, `mod-pipeline-*`)
- **Goal**: Memecah berkas-berkas monolitik di `backend/app/` (`auth.py` 781 LOC, `admin.py` 570 LOC, `web_scanner.py` 557 LOC, `tasks.py` 481 LOC) menjadi modul-modul atomik $\le 150$ LOC, menghapus endpoint mutasi admin dan unggah ZIP korpus manual, serta mengimplementasikan router & service `mod-assistant` (`/api/v1/chat/*`).
- **Status**: [x] Completed

### Phase 4: Frontend De-bloating & Split-Screen Studio Workspace (`frontend/src/`)
- **Goal**: Memecah berkas-berkas monolitik di `frontend/src/` (`AdminView.vue` 1222 LOC, `AuditDetailView.vue` 1093 LOC), menghapus `UserManagementTable.vue` dan `SystemSettingsCard.vue`, serta membangun antarmuka **Split-Screen Studio Workspace** dengan Tab 1 (Matched Sources & Diff) dan Tab 2 (AI Chatbot & 3-Mode Paraphrase In-Place).
- **Status**: [x] Completed

### Phase 5: End-to-End Verification & Quality Gate
- **Goal**: Memastikan seluruh unit test & integration test (`pytest`), build TypeScript (`npm run build`), aturan Sub-150 LOC, dan Zero-Emoji Policy lolos 100%.
- **Status**: [x] Completed
