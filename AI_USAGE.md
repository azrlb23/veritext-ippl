# Dokumentasi dan Kebijakan Penggunaan AI & Agent Skills
## Proyek IPPL (Implementasi Perangkat Lunak) — Versi Optimal (70 Skills)

Dokumen ini mencatat secara formal kerangka kerja, kebijakan, dan pemetaan penggunaan Artificial Intelligence (AI) serta **Antigravity Agent Skills** dalam pengembangan perangkat lunak pada proyek IPPL.

---

## 1. Latar Belakang & Optimalisasi Konteks

Untuk memaksimalkan performa agent, mencegah kehabisan budget token (*context window exhaustion*), dan meminimalisir aktivasi skill yang tidak relevan (*mis-triggering*), proyek IPPL membatasi skills aktif menjadi **70 skills target khusus**.

### Struktur Direktori Skills:
```text
IPPL/
├── .agents/
│   ├── skills/                  <-- 70 SKILLS AKTIF UTAMA
│   │   ├── mermaid-expert/
│   │   ├── fastapi-pro/
│   │   ├── python-pro/
│   │   └── ...
│   └── skills_archive/          <-- 237 SKILLS DIARSIPKAN (HEMAT TOKEN)
├── .agent/                      <-- Symlink ke .agents (kompatibilitas)
├── skills/                      <-- Symlink ke .agents/skills (kemudahan akses)
├── AGENTS.md                    <-- Aturan & instruksi otomatis untuk agen Antigravity
└── AI_USAGE.md                  <-- Dokumen kebijakan ini
```

---

## 2. Pemetaan 70 Skills Aktif per Fase Proyek

### 📋 Fase 1 — Kebutuhan & SRS (6 Skills)
Fokus: Analisis kebutuhan fungsional/non-fungsional, pemodelan sistem, threat modeling, dan kepatuhan privasi dokumen.
1. `mermaid-expert` — Visualisasi diagram alur, use-case, sequence, dan ERD.
2. `security-requirement-extraction` — Ekstraksi kebutuhan keamanan dari threat model.
3. `stride-analysis-patterns` — Analisis ancaman keamanan menggunakan metodologi STRIDE.
4. `business-analyst` — Penyusunan use case, user stories, dan kriteria penerimaan.
5. `api-design-principles` — Prinsip desain antarmuka REST API yang konsisten dan modular.
6. `gdpr-data-handling` — Proteksi data privasi dokumen pengguna pada bagian NFR.

### 📐 Fase 2 — Arsitektur & SDD (6 Skills)
Fokus: Desain arsitektur perangkat lunak, perancangan database, ADR, dan kontrak API.
7. `c4-architecture-c4-architecture` — Dokumentasi arsitektur C4 komprehensif.
8. `architecture-patterns` — Pola Clean Architecture, Hexagonal, dan Layered Architecture.
9. `architecture-decision-records` — Format pencatatan Architecture Decision Records (ADR).
10. `postgresql` — Desain skema, tipe data, constraint, dan indexing database PostgreSQL.
11. `openapi-spec-generation` — Generasi spesifikasi OpenAPI 3.1 untuk kontrak API.
12. `api-documenter` — Dokumentasi API interaktif dan developer reference portal.

### 🤖 Fase 3 — AI & Vector Engine (10 Skills)
Fokus: Pipeline deteksi plagiarisme, ekstraksi fitur teks, vector search, embedding, dan algoritma Winnowing.
13. `python-pro` — Standar penulisan Python 3.11+ modern dan efisien.
14. `async-python-patterns` — Pola async/await non-blocking I/O untuk high-throughput engine.
15. `uv-package-manager` — Manajemen dependensi dan virtual environment secepat kilat.
16. `vector-database-engineer` — Integrasi Pgvector / Vector DB untuk pencarian kemiripan teks.
17. `vector-index-tuning` — Tuning parameter HNSW dan IVFFlat untuk latensi vs akurasi.
18. `embedding-strategies` — Strategi chunking dan pemilihan model embedding teks.
19. `similarity-search-patterns` — Implementasi cosine, dot product, dan nearest-neighbor search.
20. `rag-implementation` — Pipeline retrieval-augmented knowledge base untuk deteksi semantik.
21. `ml-engineer` — Pipeline serving dan inferensi model machine learning produksi.
22. `python-performance-optimization` — Profiling CPU/memory dan optimasi algoritma deteksi kemiripan (Winnowing/Vector).

### ⚙️ Fase 4 — Backend & Worker (8 Skills)
Fokus: API core, autentikasi, database migration, background task, kuota Freemium, dan payment gateway.
23. `fastapi-pro` — Framework FastAPI modern berkinerja tinggi.
24. `auth-implementation-patterns` — Autentikasi JWT, OAuth2, session handling, dan RBAC.
25. `backend-security-coder` — Sanitasi input, mitigasi SQL injection, dan secure headers.
26. `database-migrations-sql-migrations` — Migrasi skema database zero-downtime (Alembic/SQL).
27. `payment-integration` — Integrasi gateway pembayaran (Stripe, Midtrans, dll.).
28. `error-handling-patterns` — Penanganan exception tersentralisasi dan respon error seragam.
29. `secrets-management` — Pengelolaan credential, API keys, dan environment variable aman.
30. `billing-automation` — Siklus manajemen kuota Freemium, limitasi pengecekan, dan invoicing.

### 🖥️ Fase 5 — Frontend Dashboard (8 Skills)
Fokus: Dashboard antarmuka pengguna, visualisasi kemiripan dokumen, KPI metrics, dan UI responsif.
31. `javascript-typescript-typescript-scaffold` — Scaffolding struktur modular project TypeScript.
32. `nextjs-app-router-patterns` — Next.js 14+ App Router, Server Components & Streaming.
33. `typescript-pro` — Strict type safety dan reusable utility types.
34. `tailwind-design-system` — Desain token, styling responsif, dan komponen Tailwind.
35. `react-state-management` — Manajemen state aplikasi (Zustand, React Query).
36. `ui-ux-designer` — Desain visual antarmuka pengguna modern dan estetis.
37. `frontend-security-coder` — Keamanan sisi klien (mitigasi XSS, CSP headers).
38. `kpi-dashboard-design` — Desain visualisasi metrik statistik dan dashboard analitik.

### 🧪 Fase 6 — Testing & QA Akademik (10 Skills)
Fokus: Siklus Test-Driven Development (TDD), pengujian otomatis frontend/backend, SAST security scan.
39. `tdd-orchestrator` — Orkestrasi siklus TDD (Red-Green-Refactor).
40. `unit-testing-test-generate` — Pembuatan unit test otomatis berbasis branch coverage.
41. `python-testing-patterns` — Pytest fixtures, parameterized tests, dan mocking.
42. `javascript-testing-patterns` — Pengujian komponen frontend (Jest / Vitest / Testing Library).
43. `e2e-testing-patterns` — End-to-End testing alur pengguna (Playwright).
44. `llm-evaluation` — Evaluasi akurasi, presisi, dan recall mesin deteksi plagiarisme.
45. `test-automator` — Otomasi pipeline testing.
46. `security-scanning-security-sast` — Static Application Security Testing (Bandit, Semgrep).
47. `code-review-excellence` — Pedoman review kode yang objektif dan terstandarisasi.
48. `data-storytelling` — Visualisasi narasi metrik AI dan pelaporan hasil uji akurasi.

### 🚀 Fase 7 — DevOps & Deployment (7 Skills)
Fokus: CI/CD automation, pipeline lint/test, audit dependensi, dan deployment script.
49. `github-actions-templates` — Template workflow GitHub Actions otomatis.
50. `git-pr-workflows-git-workflow` — Manajemen branch, semantic commits, dan pull request.
51. `changelog-automation` — Otomasi changelog mengikuti format Keep a Changelog.
52. `cicd-automation-workflow-automate` — Otomasi pipeline CI/CD menyeluruh.
53. `deployment-pipeline-design` — Desain pipeline deployment multi-stage.
54. `bash-pro` — Skrip shell otomasi portable dan testable.
55. `dependency-management-deps-audit` — Audit berkala kerentanan keamanan library/dependensi.

### 📝 Fase 8 — Dokumentasi Laporan (3 Skills)
Fokus: Dokumentasi kode sumber, buku panduan pengguna, dan laporan proyek IPPL.
56. `code-documentation-code-explain` — Penjelasan teknis kode sumber yang mudah dipahami.
57. `documentation-generation-doc-generate` — Generasi dokumentasi teknis otomatis.
58. `tutorial-engineer` — Panduan langkah demi langkah (User Guide & Onboarding).

### 🛠️ Lintas Fase & Manajemen Proyek (12 Skills)
Fokus: Investigasi error runtime, pelacakan konteks, refactoring, dan manajemen track Conductor.
59. `debugger` — Investigasi error dan perbaikan bug runtime.
60. `error-detective` — Analisis log sistem dan penelusuran pola error.
61. `track-management` — Pengelolaan track fitur, bugfix, dan refactor.
62. `conductor-setup` — Inisialisasi spesifikasi project dan context Conductor.
63. `conductor-new-track` — Pembuatan track tugas baru.
64. `conductor-implement` — Eksekusi task terpandu TDD.
65. `conductor-status` — Monitoring progress track aktif.
66. `conductor-manage` — Manajemen siklus track (archive, cleanup).
67. `context-management-context-save` — Penyimpanan snapshot konteks pengerjaan.
68. `context-management-context-restore` — Pemulihan konteks saat beralih tugas.
69. `code-refactoring-refactor-clean` — Pembersihan code smell dan perbaikan struktur kode.
70. `code-refactoring-tech-debt` — Identifikasi dan kuantifikasi utang teknis.

---

## 3. Arsip Skills (237 Skills)

Sebanyak 237 skills yang tidak esensial berada di:
📁 [`.agents/skills_archive/`](file:///Users/azrlb23/Documents/IPPL/.agents/skills_archive)

Jika ada kebutuhan mendadak untuk memulihkan skill dari arsip ke status aktif:
```bash
mv .agents/skills_archive/<nama-skill> .agents/skills/
```
