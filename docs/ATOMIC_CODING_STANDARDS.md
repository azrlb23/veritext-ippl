# Atomic Coding Standards & Architecture: VeriText AI

Dokumen ini merupakan pedoman baku implementasi kode sumber (*Coding Playbook*) untuk seluruh rekayasa perangkat lunak pada proyek VeriText AI. Dokumen ini wajib dipatuhi oleh seluruh pengembang perangkat lunak dan asisten AI agar basis kode tetap ringkas, bersih, modular, mudah diuji, dan bebas dari berkas raksasa (*God Files*) yang berbelit-belit.

---

## 1. Prinsip Utama Atomic Code Architecture

**Atomic Code Architecture** adalah pendekatan rekayasa perangkat lunak di mana setiap unit kode (fungsi, kelas, komponen UI, atau modul) dipecah hingga tingkat atomik—menjadi bagian terkecil yang independen, memiliki tanggung jawab tunggal, dan dapat diuji secara mandiri (*self-contained & isolated*).

---

## 2. Lima Aturan Emas (The 5 Golden Rules)

### Aturan 1: Batas Panjang Berkas Maksimal (Sub-150 Lines Rule)
* **Aturan Mutlak**: Tidak boleh ada berkas kode (`.py`, `.vue`, `.ts`) yang melebihi **150 baris kode** (LOC).
* **Pengecualian**: Berkas skema DDL SQL atau berkas *fixture* pengujian statis maksimal 200 baris.
* **Jika berkas mendekati 150 baris**: Berkas tersebut **wajib** didekomposisi menjadi sub-modul yang lebih kecil (misalnya memisahkan fungsi utilitas, validator skema, template HTML, atau pemecahan komponen UI).

### Aturan 2: Prinsip Tanggung Jawab Tunggal (Single Responsibility Principle)
* Setiap berkas hanya boleh memiliki **satu alasan untuk berubah**.
* Dilarang menggabungkan logika rute (*routing*), validasi data, kueri basis data, dan logika komputasi AI dalam satu berkas pengendali (*controller*).
* Pisahkan secara tegas:
  - Backend: `api/v1/*.py` (Router) $\rightarrow$ `services/*.py` (Business Logic) $\rightarrow$ `engine/*.py` / `llm/*.py` (Pure Computation & AI) $\rightarrow$ `models/*.py` (ORM).
  - Frontend: `views/*.vue` (Orchestrator $< 100$ LOC) $\rightarrow$ `components/<domain>/*.vue` (Pure UI $< 150$ LOC) $\rightarrow$ `composables/use*.ts` (Headless Reactive State $< 100$ LOC) $\rightarrow$ `services/*Service.ts` (API Client).

### Aturan 3: Irisan Tugas Kecil / Sedang (S/M Task Slices)
* Setiap tahapan implementasi hanya boleh menyentuh **1 hingga 4 berkas** dalam satu waktu.
* Hindari perubahan massal (*sprawling PRs*) yang memodifikasi puluhan berkas sekaligus, karena menyulitkan pelacakan *bug* dan regresi.

### Aturan 4: Verifikasi Uji Otomatis Mandiri (Explicit Verification Commands)
* Setiap modul atau fungsi atomik wajib memiliki berkas pengujian unit pendamping.
* Setiap berkas harus dapat diverifikasi dengan perintah terminal langsung:
  * Backend: `cd backend && ./venv/bin/pytest tests/test_engine.py -q`
  * Frontend: `cd frontend && npm run build`

### Aturan 5: Zero-Emoji & Utilitarian Code Quality
* Dilarang menyematkan karakter emoji visual di dalam kode sumber, pesan log, komentar kode, dokumen *markdown*, maupun elemen antarmuka pengguna.
* Gunakan penamaan variabel dan fungsi yang deskriptif dalam Bahasa Inggris teknis baku (*camelCase* untuk TypeScript/Vue, *snake_case* untuk Python).

---

## 3. Struktur Direktori Target Atomik (Backend & Frontend)

### 3.1. Struktur Backend Atomik (`backend/app/`)
```
backend/app/
├── api/
│   ├── deps.py                         # Dependency injection JWT & DB (< 100 LOC)
│   └── v1/
│       ├── router.py                   # Agregator router v1 (< 50 LOC)
│       ├── auth.py                     # Endpoint login, register, OAuth, refresh (< 120 LOC)
│       ├── users.py                    # Endpoint profil & ganti password (< 90 LOC)
│       ├── documents.py                # Endpoint unggah, list, hard-delete (< 110 LOC)
│       ├── audits.py                   # Endpoint eksekusi, status polling, report (< 110 LOC)
│       ├── chat.py                     # Endpoint konsultasi & parafrase 3-mode (< 120 LOC)
│       ├── reports.py                  # Endpoint unduh PDF & verifikasi QR (< 100 LOC)
│       ├── billing.py                  # Endpoint checkout, webhook SHA-512, invoice (< 120 LOC)
│       └── admin.py                    # 4 endpoint GET Read-Only murni (< 110 LOC)
├── core/
│   ├── config.py                       # Pydantic settings terpusat (< 100 LOC)
│   ├── database.py                     # Engine SQLAlchemy AsyncSession (< 70 LOC)
│   └── security.py                     # Bcrypt cost=12 & JWT HS256 (< 100 LOC)
├── models/                             # 13 Tabel Entitas SQLAlchemy (masing-masing < 120 LOC)
│   ├── user.py                         # Tabel users
│   ├── session.py                      # Tabel sessions
│   ├── password_reset.py               # Tabel password_resets
│   ├── wallet.py                       # Tabel token_wallets & token_transactions
│   ├── invoice.py                      # Tabel invoices
│   ├── document.py                     # Tabel documents
│   ├── audit.py                        # Tabel audit_tasks, audit_sentences, audit_reports
│   ├── chat.py                         # Tabel chat_sessions & chat_messages
│   ├── corpus.py                       # Tabel corpus_documents & document_chunks
│   └── audit_log.py                    # Tabel audit_logs
├── schemas/                            # Kontrak Pydantic v2 (masing-masing < 120 LOC)
│   ├── common.py                       # ApiResponse envelope & meta
│   ├── auth.py
│   ├── document.py
│   ├── audit.py
│   ├── chat.py
│   ├── billing.py
│   └── admin.py
├── engine/                             # Komponen Pipa AI 3-Tahap Atomik
│   ├── preprocessor.py                 # Ekstraksi PDF/DOCX & segmentasi kalimat (< 140 LOC)
│   ├── tier1_lexical.py                # Winnowing Rabin-Karp k=5, w=4 (< 130 LOC)
│   ├── tier2_semantic.py               # SBERT 384-d + pgvector HNSW + IndoBERT (< 140 LOC)
│   ├── tier3_stylometric.py            # Goh & Barabasi Burstiness B & TTR (< 110 LOC)
│   ├── composite_scorer.py             # Rumus 0.50 Leksikal + 0.35 Semantik + 0.15 Stilometri (< 70 LOC)
│   └── harvesters/                     # Akuisisi Korpus Dual-Scope Otomatis
│       ├── openalex_client.py          # OpenAlex & DOAJ API (< 120 LOC)
│       ├── scholar_client.py           # Semantic Scholar & Crossref API (< 120 LOC)
│       └── web_grounding.py            # Gemini Search Grounding (< 110 LOC)
├── llm/                                # Dual-Engine LLM Gateway (Anti-429 & Failover)
│   ├── gemini_client.py                # Google Gemini 2.5 Flash SDK client (< 110 LOC)
│   ├── deepseek_client.py              # DeepSeek v4.1 Flash via 9Router client (< 110 LOC)
│   └── gateway.py                      # Circuit breaker & automatic failover (< 90 LOC)
├── services/                           # Layanan Logika Bisnis Atomik
│   ├── auth_service.py                 # Logika autentikasi & provisi 5 token/3 trial (< 140 LOC)
│   ├── document_service.py             # Validasi magic bytes, rumus token, hard-delete (< 130 LOC)
│   ├── audit_service.py                # Orkestrasi task & smart polling status (< 130 LOC)
│   ├── assistant_service.py            # Academic Guardrail & 3-Mode Paraphrase (< 140 LOC)
│   ├── billing_service.py              # Checkout Midtrans & webhook FOR UPDATE (< 140 LOC)
│   ├── pdf_certificate_service.py      # Render laporan PDF & QR Code (< 120 LOC)
│   └── pdf_invoice_service.py          # Render invoice PDF (< 110 LOC)
└── workers/
    ├── celery_app.py                   # Konfigurasi Celery & Redis (< 60 LOC)
    └── tasks.py                        # Task asinkron & auto-refund gagal (< 140 LOC)
```

### 3.2. Struktur Frontend Atomik (`frontend/src/`)
```
frontend/src/
├── services/                           # Klien HTTP Axios per domain (< 100 LOC)
│   ├── api.ts
│   ├── authService.ts
│   ├── documentService.ts
│   ├── auditService.ts
│   ├── chatService.ts
│   └── billingService.ts
├── composables/                        # Logika Reaktif Headless (< 100 LOC)
│   ├── usePolling.ts
│   ├── useFileUpload.ts
│   ├── useHeatmapFilter.ts
│   ├── useParaphrase.ts
│   └── useNotification.ts
├── stores/                             # Pinia State Stores (< 120 LOC)
│   ├── auth.ts
│   └── audit.ts
├── components/
│   ├── common/                         # Komponen Primitif (< 100 LOC)
│   ├── dashboard/                      # Dropzone, Kalkulator Token, Tabel Riwayat (< 140 LOC)
│   ├── audit/                          # Split-Screen Studio Workspace (< 140 LOC)
│   │   ├── TopSummaryBar.vue
│   │   ├── HeatmapViewer.vue
│   │   ├── SentencePopover.vue
│   │   ├── MatchedSourcesTable.vue
│   │   ├── SideBySideDiff.vue
│   │   ├── AiAssistantTab.vue
│   │   └── ParaphraseOptionCard.vue
│   ├── billing/                        # By Token & By Paket Token Midtrans (< 130 LOC)
│   ├── verify/                         # Portal Verifikasi QR Publik (< 120 LOC)
│   └── admin/                          # 4 Komponen Observasi Read-Only (< 130 LOC)
└── views/                              # View Orchestrators (< 100 LOC)
```

---

## 4. Contoh Komparasi: Monolitik vs Atomik

### Pendekatan Buruk (Monolitik / "God Class" > 400 Baris — Dilarang)
```python
# DILARANG: Mencampur semua tanggung jawab dalam satu berkas raksasa
class PlagiarismDetector:
    def extract_text(self, file): ...
    def compute_winnowing(self, text): ...
    def query_pgvector(self, embedding): ...
    def calculate_burstiness(self, text): ...
    def call_gemini_api(self, prompt): ...
    def deduct_tokens(self, user_id): ...
    def generate_pdf_report(self, task_id): ...
```

### Pendekatan VeriText AI (Atomic Architecture <= 150 Baris — Wajib)
Setiap operasi diisolasi pada berkas mandirinya sendiri:
1. `engine/preprocessor.py` $\rightarrow$ Hanya mengekstrak teks bersih dan memecah kalimat.
2. `engine/tier1_lexical.py` $\rightarrow$ Hanya fungsi matematika hash Rabin-Karp & Winnowing.
3. `engine/tier2_semantic.py` $\rightarrow$ Hanya inferensi SBERT, kueri HNSW pgvector, dan re-ranking IndoBERT.
4. `llm/gateway.py` $\rightarrow$ Hanya mengatur pertukaran otomatis antara Gemini 2.5 Flash dan DeepSeek v4.1 Flash.
5. `services/billing_service.py` $\rightarrow$ Hanya memotong/menambah saldo token dengan `SELECT ... FOR UPDATE`.

---

## 5. Daftar Periksa (Checklist) Sebelum Menyelesaikan Tugas
- [ ] Panjang setiap berkas yang dibuat/diubah tidak melebihi 150 baris kode.
- [ ] Berkas hanya memiliki 1 tanggung jawab spesifik (*Single Responsibility*).
- [ ] Tidak ada penggunaan karakter emoji visual (*Zero-Emoji Policy*).
- [ ] Seluruh fungsi publik memiliki *type hint* lengkap (Python typing / TypeScript interfaces).
- [ ] Telah diuji dengan perintah verifikasi mandiri dan dinyatakan lolos (*100% green check*).
