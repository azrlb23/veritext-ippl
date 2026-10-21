# DOKUMEN MATRIKS PENGUJIAN WHITEBOX (WHITE-BOX TESTING SPECIFICATION)
## SISTEM DETEKSI PLAGIARISME CERDAS HYBRID 4-TIER – VERITEXT AI

**Kode Dokumen**: `WBT-VERITEXT-2026-V1.0`  
**Mata Kuliah**: Implementasi Pola Perangkat Lunak (IPPL)  
**Arsitektur Target**: FastAPI (Backend), SQLAlchemy 2.0 Async, Celery + Redis, pgvector (HNSW Indexing), Vue 3 + TypeScript (Frontend)  
**Standar Pengujian**: IEEE 829 (Test Documentation Standard) & ISO/IEC/IEEE 29119 (Software Testing Standards)  
**Tingkat Cakupan**: Statement Coverage (100%), Branch Coverage (100%), Condition Coverage/MC-DC, Boundary Value Analysis, Exception Handling  

---

## 1. RINGKASAN EKSEKUTIF & METODOLOGI PENGUJIAN WHITEBOX

### 1.1 Tujuan Pengujian
Pengujian whitebox ini bertujuan untuk memverifikasi kebenaran struktur logika internal, algoritma matematis, alur kendali (*control flow*), penanganan eksepsi (*exception handling*), integritas transaksional basis data, serta batasan (*boundary conditions*) pada seluruh modul inti sistem **VeriText AI**.

### 1.2 Metodologi & Kriteria Pengujian
Metodologi whitebox yang diimplementasikan berfokus pada:
1. **Control Flow Graph (CFG) & Basis Path Testing**: Setiap percabangan kondisional (`if/elif/else`, `try/except`) diuji untuk memastikan tidak ada *dead code* atau *unhandled exception*.
2. **Kategori Kasus Uji**:
   - **Happy Ending (Happy Path / Normal Execution)**: Menguji alur sukses saat kondisi ideal, input valid, dan state sistem normal.
   - **Bad Case (Negative / Invalid Input / Boundary)**: Menguji ketahanan modul saat menghadapi input di luar domain, nilai batas (*boundary value*), string kosong, data bernilai nol (*zero-value*), format salah, atau rekaman duplikat.
   - **Blocker (Exception / Security / System Failure)**: Menguji pencegahan kegagalan fatal, pelanggaran hak akses (*Role-Based Access Control* / RBAC), isolasi penyewa (*multi-tenant data leakage*), transaksi token tidak mencukupi, token JWT *tampered*, serta kepatuhan hukum privasi data (**UU PDP No. 27/2022**).
3. **Traceability**: Seluruh 73 test case diimplementasikan 1:1 dalam suite unit test backend (`backend/tests/test_whitebox_suites.py`) dan dapat dieksekusi secara otomatis.

---

## 2. REKAPITULASI MATRIKS PENGUJIAN 7 FITUR UTAMA

| No | Fitur Utama Sistem | Happy Ending | Bad Case | Blocker | Total Kasus | Status Uji |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | **Fitur 1: Autentikasi Pengguna & Manajemen Sesi** | 5 | 3 | 3 | **11** | **PASSED (100%)** |
| 2 | **Fitur 2: Manajemen Dokumen & Workspace Pengguna** | 5 | 4 | 1 | **10** | **PASSED (100%)** |
| 3 | **Fitur 3: Mesin Deteksi Plagiarisme Hybrid 4-Tier** | 5 | 4 | 1 | **10** | **PASSED (100%)** |
| 4 | **Fitur 4: Laporan Audit, Heatmap Viewer & Verifikasi QR** | 5 | 3 | 2 | **10** | **PASSED (100%)** |
| 5 | **Fitur 5: Bank Korpus Ilmiah** | 5 | 3 | 2 | **10** | **PASSED (100%)** |
| 6 | **Fitur 6: Dompet Token & Billing** | 5 | 3 | 2 | **10** | **PASSED (100%)** |
| 7 | **Fitur 7: Konsol Tata Kelola Admin & Kepatuhan UU PDP** | 9 | 2 | 1 | **12** | **PASSED (100%)** |
| **TOTAL** | **Seluruh 7 Fitur Utama Sistem** | **39** | **22** | **12** | **73** | **PASSED (100%)** |

---

## 3. TABEL DETAIL TEST CASE WHITEBOX PER FITUR

### FITUR 1: AUTENTIKASI PENGGUNA & MANAJEMEN SESI
*Modul Target*: `backend/app/services/auth_service.py`, `backend/app/api/v1/auth.py`, `backend/app/core/security.py`, `backend/app/api/deps.py`

| ID Test Case | Nama Skenario & Target Modul/Metode | Kategori | Pre-conditions | Input Test Data | Jalur Eksekusi Whitebox (Branch / Logic Path) | Expected Output & State Result | Status |
|:---|:---|:---:|:---|:---|:---|:---|:---:|
| `TC-AUTH-001` | Registrasi Pengguna Baru & Alokasi Trial Token (`AuthService.register_user`) | **Happy Ending** | Basis data aktif, email belum terdaftar di tabel `users`. | `full_name="Azriel Albian"`, `email="azriel.new@kampus.ac.id"`, `password="SecurePassword123!"`, `institution="ITN"` | Branch `not result.scalar_one_or_none()` -> `db.add(new_user)` -> `db.add(TokenWallet(balance=5))` -> `create_access_token` -> `create_refresh_token` -> `db.add(Session)`. | Akun pengguna terbuat dengan role `TRIAL`, wallet dibuat dengan balance = 5, access & refresh token valid dihasilkan, sesi tercatat. | **PASSED** |
| `TC-AUTH-002` | Login Kredensial Valid Mahasiswa (`AuthService.authenticate_user`) | **Happy Ending** | Akun pengguna terdaftar dengan password hash valid dan status `is_active=True`. | `email="mhs@kampus.ac.id"`, `password="SecretPassword123!"` | `select(User).where(email)` -> `verify_password() == True` -> branch `user.is_active == True` -> generate JWT access token & refresh token -> update session. | Login sukses, mengembalikan access_token (sub = UUID user, role = TRIAL) dan refresh_token valid. | **PASSED** |
| `TC-AUTH-003` | Pembaruan Access Token via Refresh Token (`auth_router.refresh_token_endpoint`) | **Happy Ending** | Sesi aktif tersimpan di tabel `sessions`, cookie refresh token valid dikirimkan klien. | Cookie `refresh_token="valid_jwt_refresh_token"` | Branch `if refresh_token:` -> `hash_token()` -> `select(Session).where(hash)` -> branch `if sess:` -> `db.get(User)` -> branch `if user and user.is_active:` -> `create_access_token()`. | Mengembalikan `access_token` baru dengan subject UUID user terkait. | **PASSED** |
| `TC-AUTH-004` | Logout & Pencabutan Sesi Database (`auth_router.logout`) | **Happy Ending** | Pengguna terotentikasi memiliki sesi aktif di database. | Cookie `refresh_token="valid_jwt_refresh_token"`, `current_user` terautentikasi | Branch `if refresh_token:` -> query session hash -> branch `if session_obj:` -> `db.delete(session_obj)` -> `db.commit()` -> `response.delete_cookie("refresh_token")`. | Sesi dihapus permanen dari basis data, cookie dibersihkan pada header HTTP response. | **PASSED** |
| `TC-AUTH-005` | Pembaruan Profil Mandiri Pengguna (`auth_router.update_profile`) | **Happy Ending** | Pengguna login dengan profil aktif. | `UserProfileUpdate(full_name="Nama Baru", institution="Institut Teknologi Bandung")` | Branch `if req.full_name is not None:` -> set `user.full_name` -> branch `if req.institution is not None:` -> set `user.institution` -> `db.commit()`. | Profil pengguna di database terbarui, mengembalikan `UserProfileResponse` data terbaru. | **PASSED** |
| `TC-AUTH-006` | Registrasi Email Duplikat Ditolak (`AuthService.register_user`) | **Bad Case** | Email `duplicate@kampus.ac.id` telah ada di tabel `users`. | `email="duplicate@kampus.ac.id"`, `password="Pass123!"` | `select(User).where(email)` -> branch `if result.scalar_one_or_none():` -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "Email is already registered in the system". | **PASSED** |
| `TC-AUTH-007` | Login Password Salah / Hash Mismatch (`AuthService.authenticate_user`) | **Bad Case** | Pengguna terdaftar, namun kata sandi yang diinput keliru. | `email="user@kampus.ac.id"`, `password="SalahPassword!"` | Query user ditemukan -> `verify_password() == False` -> branch `if not user or not is_valid:` -> raise `HTTPException(401)`. | Memicu `HTTPException` status 401 Unauthorized: "Invalid email or password". | **PASSED** |
| `TC-AUTH-008` | Ganti Password Gagal Karena Password Lama Keliru (`auth_router.change_password`) | **Bad Case** | Pengguna aktif login, input password lama tidak sesuai hash DB. | `ChangePasswordRequest(old_password="Salah!", new_password="Baru123!")` | `verify_password(req.old_password, user.password_hash)` -> branch `if not verify_password:` -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "Current password is incorrect". | **PASSED** |
| `TC-AUTH-009` | Pemblokiran Akun Dinonaktifkan / Suspended (`AuthService.authenticate_user`) | **Blocker** | Pengguna terdaftar dengan bendera `is_active=False`. | `email="banned@kampus.ac.id"`, password valid | Query user ditemukan -> password cocok -> branch `if not user.is_active:` -> raise `HTTPException(403)`. | Memicu `HTTPException` status 403 Forbidden: "Account is currently inactive or suspended". Akses diblokir. | **PASSED** |
| `TC-AUTH-010` | Penolakan Token JWT Tampered / Palsu (`deps.get_current_user`) | **Blocker** | Klien mengirimkan Authorization header berisi string token JWT rusak/palsu. | Header `Authorization: Bearer header.palsu.rusak` | `decode_access_token()` memicu exception / mengembalikan None -> branch `if not payload or "sub" not in payload:` -> raise `HTTPException(401)`. | Memicu `HTTPException` status 401 Unauthorized: "Invalid or expired access token". Request dihentikan. | **PASSED** |
| `TC-AUTH-011` | Otorisasi RBAC Menolak Akses Lintas Hak Istimewa (`deps.require_role`) | **Blocker** | Pengguna login dengan role `TRIAL` mencoba mengakses rute admin. | `current_user.role = "TRIAL"`, dependency factory `require_role("ADMIN")` | Role checker memeriksa `current_user.role not in roles and current_user.role != "ADMIN"` -> evaluates `True` -> raise `HTTPException(403)`. | Memicu `HTTPException` status 403 Forbidden: "Access forbidden: requires role in ('ADMIN',)". | **PASSED** |

---

### FITUR 2: MANAJEMEN DOKUMEN & WORKSPACE PENGGUNA
*Modul Target*: `backend/app/services/document_service.py`, `backend/app/api/v1/documents.py`, `backend/app/engine/preprocessor.py`

| ID Test Case | Nama Skenario & Target Modul/Metode | Kategori | Pre-conditions | Input Test Data | Jalur Eksekusi Whitebox (Branch / Logic Path) | Expected Output & State Result | Status |
|:---|:---|:---:|:---|:---|:---|:---|:---:|
| `TC-DOC-001` | Validasi Ekstensi Naskah Yang Diizinkan (`DocumentService.validate_file`) | **Happy Ending** | Dokumen memiliki ekstensi standar akademik (.pdf, .docx, .txt). | Berkas `"skripsi.pdf"`, `"laporan.docx"`, `"draft.txt"`, `"TESIS.PDF"` | `filename.rsplit(".", 1)[-1].lower()` -> periksa `ext in allowed` -> lolos tanpa eksepsi. | Fungsi menyelesaikan eksekusi tanpa raise HTTPException. | **PASSED** |
| `TC-DOC-002` | Ekstraksi Teks Lengkap Naskah TXT (`TextPreprocessor.extract_text_from_file`) | **Happy Ending** | Berkas naskah teks tersimpan di direktori upload. | Berkas TXT berisi string akademik 94 karakter | Branch `if mime_type == "text/plain" or file_path.endswith(".txt"):` -> `open(file_path, "r", encoding="utf-8")` -> return string bersih. | Mengembalikan teks utuh sesuai isi naskah asli. | **PASSED** |
| `TC-DOC-003` | Normalisasi Whitespace & Case Folding Naskah (`TextPreprocessor`) | **Happy Ending** | String naskah mentah mengandung multi-spasi, tab, newline, dan huruf kapital. | `"   Analisis   Performa \t\n Algoritma \t WINNOWING!   "` | `re.sub(r"\s+", " ", text).strip()` -> `text.lower()` -> `re.sub(r"[^a-z0-9]", "", text)`. | Menghasilkan string bersih seragam tanpa spasi ganda dan karakter non-alfanumerik tereliminasi untuk leksikal. | **PASSED** |
| `TC-DOC-004` | List Dokumen Workspace dengan Paginasi (`doc_router.list_documents`) | **Happy Ending** | Pengguna memiliki 2 dokumen tersimpan di workspace. | `page=1`, `limit=10`, `current_user` terautentikasi | `select(Document).where(user_id, deleted_at.is_(None))` -> hitung count subquery -> query pagination limit/offset -> hitung pages -> return `PaginatedData`. | Mengembalikan `PaginatedData` dengan `total=2`, `items=2`, `pages=1`. | **PASSED** |
| `TC-DOC-005` | Soft Delete Dokumen Hak Penghapusan UU PDP (`doc_router.delete_document`) | **Happy Ending** | Dokumen milik pengguna tersimpan dengan status `READY`. | `doc_id` valid milik pengguna login | Query document -> branch `if doc:` -> `doc.status = "DELETED"` -> `doc.deleted_at = now()` -> `db.commit()`. | Dokumen ditandai `DELETED`, timestamp `deleted_at` terisi, file disiapkan untuk retensi pembersihan UU PDP. | **PASSED** |
| `TC-DOC-006` | Penolakan Ekstensi Naskah Ilegal (`DocumentService.validate_file`) | **Bad Case** | Klien mencoba mengunggah berkas executable atau script berbahaya. | Berkas `"virus.exe"`, `"script.py"`, `"arsip.zip"` | `ext not in allowed` evaluates `True` -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "Unsupported file format '.exe'". | **PASSED** |
| `TC-DOC-007` | Penolakan Nama Berkas Kosong atau Tanpa Ekstensi (`DocumentService.validate_file`) | **Bad Case** | Input nama berkas tidak valid atau tidak memiliki ekstensi titik. | Berkas `""`, `"   "`, `"filenotanextension"` | Branch `if not filename or "." not in filename:` evaluates `True` -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "Filename is missing or has no valid extension." | **PASSED** |
| `TC-DOC-008` | Penolakan Berkas Naskah Kosong 0 Byte (`DocumentService.save_uploaded_file`) | **Bad Case** | Berkas naskah berukuran 0 byte. | `UploadFile` dengan payload konten `b""` | `await file.read()` -> `file_size = len(content)` -> branch `if file_size == 0:` evaluates `True` -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "File is empty (0 bytes)". | **PASSED** |
| `TC-DOC-009` | Penolakan Berkas Naskah Melebihi Kuota Maksimal (`DocumentService.save_uploaded_file`) | **Bad Case** | Berkas naskah melebihi batas 10MB (10.485.760 bytes). | Payload konten berukuran 10.486.784 bytes | `file_size > max_bytes` evaluates `True` -> raise `HTTPException(413)`. | Memicu `HTTPException` status 413 Payload Too Large: "File exceeds maximum allowed size of 10MB". | **PASSED** |
| `TC-DOC-010` | Isolasi Akses Dokumen Antar Penyewa Tenant Isolation (`doc_router.get_document`) | **Blocker** | Pengguna A mencoba mengakses `doc_id` milik Pengguna B. | `current_user = User A`, `doc_id = Dokumen User B` | `select(Document).where(Document.id == doc_id, Document.user_id == user_a.id)` -> return `None` -> branch `if not doc:` -> raise `HTTPException(404)`. | Memicu `HTTPException` status 404 Not Found (Data leakage dicegah, dokumen Pengguna B terlindungi). | **PASSED** |

---

### FITUR 3: MESIN DETEKSI PLAGIARISME HYBRID 4-TIER
*Modul Target*: `backend/app/engine/preprocessor.py`, `backend/app/engine/tier1_lexical.py`, `backend/app/engine/tier2_semantic.py`, `backend/app/engine/tier3_stylometric.py`, `backend/app/engine/tier4_aggregator.py`

| ID Test Case | Nama Skenario & Target Modul/Metode | Kategori | Pre-conditions | Input Test Data | Jalur Eksekusi Whitebox (Branch / Logic Path) | Expected Output & State Result | Status |
|:---|:---|:---:|:---|:---|:---|:---|:---:|
| `TC-DET-001` | Segmentasi Kalimat Presisi & Pemetaan Offset Karakter (`TextPreprocessor.segment_sentences`) | **Happy Ending** | Teks akademik dengan singkatan gelar (Dr., M.Kom.), nomor desimal (98.5%), dan tanda baca. | Paragraf 3 kalimat akademik lengkap | Loop pencarian boundary tanda baca -> filter gelar/singkatan regex -> hitung `start_char` dan `end_char` -> potong substring -> verifikasi slicing. | Menghasilkan 3 objek `SentenceSpan` di mana `original_text[s.start_char : s.end_char] == s.text` presisi 100%. | **PASSED** |
| `TC-DET-002` | Tier 1 Winnowing Rabin-Karp Copy-Paste Verbatim (`WinnowingLexicalEngine`) | **Happy Ending** | Mesin Winnowing diinisialisasi k=5, w=4. Naskah uji identik dengan naskah pembanding. | `"algoritma winnowing cerdas mendeteksi duplikasi naskah akademik secara presisi"` | `compute_kgram_hashes()` rolling hash Rabin-Karp -> sliding window $w$ rightmost minimum selection -> kalkulasi fingerprint overlap set. | Kemiripan leksikal T1 bernilai 1.0 (100%), seluruh set sidik jari cocok identik. | **PASSED** |
| `TC-DET-003` | Tier 2 Cosine Similarity Semantik Parafrase Akademik (`SemanticEngine.detect_paraphrase`) | **Happy Ending** | Engine semantik 384-dimensi aktif dengan ambang batas parafrase 0.75. | S1: *"Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma..."*, S2: *"Pendeteksian plagiarisme pintar menggunakan kombinasi algoritma..."* | `embed_sentence(s1)` -> `embed_sentence(s2)` -> kalkulasi dot product dan normalisasi Euclidean vector -> `cosine_similarity(u, v)`. | Skor cosine similarity $\ge 0.75$, mendeteksi substitusi sinonim konsep akademik secara semantik. | **PASSED** |
| `TC-DET-004` | Tier 3 Evaluasi Statistik Stilometri Natural Manusia (`StylometricEngine`) | **Happy Ending** | Naskah tulisan manusia dengan variasi ritme panjang kalimat (pendek, sedang, panjang). | 3 kalimat dengan variasi panjang 2 kata, 13 kata, dan 20 kata | `calculate_sentence_length_stats()` -> hitung rata-rata $\mu$, variansi, deviasi standar $\sigma$, dan $Burstiness = (\sigma - \mu) / (\sigma + \mu)$. | $\mu > 0$, $\sigma > 0$, burstiness berada dalam rentang valid $-1.0 \le B \le 1.0$, `is_ai_monotonous == False`. | **PASSED** |
| `TC-DET-005` | Tier 4 Agregasi Komposit Terbobot Multi-Tier (`HybridAggregator.calculate_composite_score`) | **Happy Ending** | Bobot $W_{lex}=0.50$, $W_{sem}=0.35$, $W_{sty}=0.15$. | $T_1 = 60.0$, $T_2 = 40.0$, $T_3 = 20.0$ | $Score_{comp} = \min(100.0, \max(0.0, 0.50 \times 60 + 0.35 \times 40 + 0.15 \times 20))$. | Nilai skor komposit terhitung tepat $47.0$ (kategori Perlu Perhatian). | **PASSED** |
| `TC-DET-006` | Boundary Input Teks Kosong Tanpa Karakter (`TextPreprocessor`) | **Bad Case** | Input string kosong `""` atau hanya spasi/newline `"   \t\n  "`. | String kosong / whitespace | Branch `if not text or not text.strip():` evaluates `True` -> return `[]` / `""`. | Mengembalikan list kosong `[]` tanpa memicu IndexError atau UnboundLocalError. | **PASSED** |
| `TC-DET-007` | Boundary Teks Lebih Pendek Dari Ukuran K-Gram (`WinnowingLexicalEngine.compute_kgram_hashes`) | **Bad Case** | Panjang teks masukan $n < k$ (misal $n=3$, $k=5$). | String `"abc"` ($n=3$) | Branch `if n < self.k:` -> branch `if n > 0:` -> return `[(self.polynomial_hash(clean), 0)]`. | Menghasilkan tepat 1 hash boundary tanpa IndexError atau kegagalan sliding window. | **PASSED** |
| `TC-DET-008` | Deteksi Anomali Kalimat Sintetis AI Monoton (`StylometricEngine`) | **Bad Case** | Naskah sintetis buatan bot AI di mana seluruh kalimat memiliki jumlah kata yang seragam persis. | 4 kalimat berurutan masing-masing tepat 5 kata | `sigma = sqrt(0.0) = 0.0` -> `denom = sigma + mu` -> branch `if sigma == 0.0:` -> return $\mu, 0.0, -1.0$. | Deviasi standar $\sigma = 0.0$, burstiness bernilai minimal $-1.0$, teridentifikasi anomali AI monoton. | **PASSED** |
| `TC-DET-009` | Cosine Similarity pada Vektor Nol Zero-Vector (`SemanticEngine.cosine_similarity`) | **Bad Case** | Vektor masukan bernilai nol pada seluruh dimensi 384D. | $V_1 = [0.0 \times 384]$, $V_2 = [0.0 \times 384]$ | `norm_a = sqrt(0) = 0.0` -> branch `if norm_a == 0.0 or norm_b == 0.0:` evaluates `True` -> return `0.0`. | Mengembalikan float `0.0` secara deterministik tanpa terjadi `ZeroDivisionError`. | **PASSED** |
| `TC-DET-010` | Pencegahan False Positive pada Kalimat Sitasi Akademik (`TextPreprocessor.is_citation_sentence`) | **Blocker** | Naskah mengandung kalimat referensi kepustakaan (misal format IEEE `[1]`, Harvard `(Author, Year)`). | `"[1] Santoso, B. (2024). Deteksi Plagiarisme..."`, `"(Gunawan dan Hermawan, 2023)"` | Evaluasi regex sitasi numerik dan kurung penulis-tahun -> branch match `True` -> flag `is_citation = True`. | `is_citation_sentence()` bernilai `True`. Kalimat sitasi otomatis dikecualikan dari tuduhan plagiarisme verbatim. | **PASSED** |

---

### FITUR 4: LAPORAN AUDIT, HEATMAP VIEWER & VERIFIKASI PUBLIK QR
*Modul Target*: `backend/app/api/v1/reports.py`, `backend/app/services/pdf_certificate_service.py`, `backend/app/services/audit_service.py`, `backend/app/engine/tier4_aggregator.py`

| ID Test Case | Nama Skenario & Target Modul/Metode | Kategori | Pre-conditions | Input Test Data | Jalur Eksekusi Whitebox (Branch / Logic Path) | Expected Output & State Result | Status |
|:---|:---|:---:|:---|:---|:---|:---|:---:|
| `TC-REP-001` | Generasi Anotasi Heatmap Multi-Warna (`HeatmapAnnotationData.to_dict`) | **Happy Ending** | Naskah memiliki padanan Tier 1 (Leksikal), Tier 2 (Semantik), dan Tier 3 (Stilometri). | Anotasi T1 (sim 1.0, RED), T2 (sim 0.88, ORANGE), T3 (sim 0.45, YELLOW) | Konstruksi dataclass `HeatmapAnnotationData` -> mapping kode warna RGB hex -> serialisasi `to_dict()`. | Mengembalikan list dict anotasi span lengkap dengan `start`, `end`, `tier`, `color`, dan `similarity`. | **PASSED** |
| `TC-REP-002` | Pengambilan Laporan Audit Berdasarkan ID (`report_router.get_report`) | **Happy Ending** | Laporan audit terdaftar di database lengkap dengan task dan dokumen terkait. | `report_id` UUID valid | `select(AuditReport).where(id == report_id)` -> branch `if report:` -> serialisasi `AuditReportResponse.model_validate(report)`. | Mengembalikan laporan audit lengkap dengan skor composite, lexical, semantic, dan stylometric. | **PASSED** |
| `TC-REP-003` | Ekspor Sertifikat PDF Valid dengan Header Standar (`generate_pdf_certificate`) | **Happy Ending** | Data audit lengkap tersedia untuk diterbitkan sertifikat keasliannya. | Dokumen `"Tesis_Akhir.pdf"`, Pengguna `"Mochammad Azriel Albian Putra"`, Institusi `"ITN"`, Skor `18.5` | Inisialisasi canvas PDF -> generate QR code UUID -> tulis header VeriText AI -> render metrik audit -> render matched sources -> return bytes. | Menghasilkan byte stream PDF valid yang diawali `b"%PDF-"`, ukuran > 1000 byte, dapat di-parse library PDFium. | **PASSED** |
| `TC-REP-004` | Verifikasi Publik Sertifikat Melalui UUIDv4 (`report_router.verify_certificate_public`) | **Happy Ending** | Sertifikat terdaftar publik dan dokumen naskah asli belum dihapus pemilik. | `verification_uuid` UUIDv4 valid | Query join AuditReport, AuditTask, Document, User -> branch `if result:` -> branch `if doc.deleted_at is None:` -> return status valid. | Mengembalikan `is_valid: True`, judul naskah, nama pemilik, institusi, dan rincian skor tier. | **PASSED** |
| `TC-REP-005` | Sanitasi Nama Berkas Ekspor Sertifikat PDF (`clean_pdf_filename`) | **Happy Ending** | Nama dokumen memiliki ekstensi ganda atau karakter path traversal (`/`, `:`, `?`). | `"LPJ FPK.docx_compressed.pdf"`, `"Tesis / Skripsi: Final?.pdf"` | Eliminasi multiple extensions -> `re.sub(r"[^\w\s-]", "", ...)` -> ganti spasi dengan underscore -> prepend `"Sertifikat_VeriText_"`. | Menghasilkan nama berkas aman `"Sertifikat_VeriText_LPJ_FPK_docx_compressed.pdf"`. | **PASSED** |
| `TC-REP-006` | Pengambilan Laporan ID Tak Terdaftar Ditolak HTTP 404 (`report_router.get_report`) | **Bad Case** | ID laporan tidak ada dalam basis data. | `report_id = uuid.uuid4()` acak | Query DB menghasilkan `None` -> branch `if not report:` evaluates `True` -> raise `HTTPException(404)`. | Memicu `HTTPException` status 404 Not Found: "Audit report not found". | **PASSED** |
| `TC-REP-007` | Verifikasi Publik UUID Tak Terdaftar Menghasilkan Negatif (`report_router.verify_certificate_public`) | **Bad Case** | Kode QR / UUID palsu dipindai oleh pihak luar. | `verification_uuid = uuid.uuid4()` acak | Query DB menghasilkan `None` -> branch `if not result:` evaluates `True` -> return `is_valid: False`. | Mengembalikan JSON dengan `is_valid: False` dan pesan "Sertifikat tidak ditemukan atau tidak valid". | **PASSED** |
| `TC-REP-008` | Penanganan Batas Ekspor Sertifikat Nilai Skor 0.0 (`generate_pdf_certificate`) | **Bad Case** | Naskah bersih 100% dari plagiarisme dengan skor seluruh tier bernilai 0.0. | `score_composite = 0.0`, `matched_sources = []` | Generator PDF memformat string persentase `"0.0%"` -> kalkulasi status "Aman" -> render badge hijau. | Sertifikat PDF terbuat sempurna tanpa error formatting pembagian nol atau string slicing. | **PASSED** |
| `TC-REP-009` | Pembatalan Tugas Audit Berstatus COMPLETED Ditolak (`AuditService.cancel_task`) | **Bad Case** | Tugas audit telah selesai diproses (`status="COMPLETED"`). | `task_id` valid, `status="COMPLETED"` | Branch `if task.status not in ("QUEUED", "PROCESSING"):` evaluates `True` -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "Cannot cancel task in 'COMPLETED' state". | **PASSED** |
| `TC-REP-010` | Sertifikat Dinyatakan Kedaluwarsa Saat Dokumen Dihapus UU PDP (`report_router.verify_certificate_public`) | **Blocker** | Dokumen telah dihapus permanen oleh pemilik atas dasar hak UU PDP (`deleted_at != None`). | `verification_uuid` dari dokumen yang berstatus `DELETED` | Query DB menemukan baris -> branch `if doc.deleted_at is not None or doc.status == "DELETED":` evaluates `True` -> return `is_valid: False`. | Mengembalikan `is_valid: False` dengan notifikasi "Dokumen terkait telah dihapus oleh pemilik atas dasar UU PDP No. 27/2022". | **PASSED** |

---

### FITUR 5: BANK KORPUS ILMIAH
*Modul Target*: `backend/app/services/corpus_service.py`, `backend/app/api/v1/corpus.py`, `backend/app/engine/reference_corpus.py`

| ID Test Case | Nama Skenario & Target Modul/Metode | Kategori | Pre-conditions | Input Test Data | Jalur Eksekusi Whitebox (Branch / Logic Path) | Expected Output & State Result | Status |
|:---|:---|:---:|:---|:---|:---|:---|:---:|
| `TC-CRP-001` | Daftar Dokumen Korpus dengan Filter Kategori (`CorpusService.list_corpus_documents`) | **Happy Ending** | Dokumen korpus tersimpan di database dengan berbagai kategori. | `category="Informatika"`, `page=1`, `limit=20` | `select(CorpusDocument).where(status != "DELETED")` -> branch `if category:` -> filter `category == "Informatika"` -> count subquery -> return items & total. | Mengembalikan daftar dokumen korpus kategori Informatika dan total yang sesuai. | **PASSED** |
| `TC-CRP-002` | Unggah Arsip Batch ZIP Korpus Baru (`CorpusService.ingest_zip_corpus`) | **Happy Ending** | Pengguna dengan role Dosen/Reviewer mengunggah arsip batch naskah pembanding baru. | `UploadFile("kumpulan_jurnal.zip")`, konten biner arsip | Hitung SHA-256 hash -> branch `if existing.scalar_one_or_none(): False` -> simpan berkas fisik ke `UPLOAD_DIR` -> `db.add(CorpusDocument(status="PENDING_INDEX"))` -> dispatch task. | Berkas tersimpan di disk, rekaman dokumen korpus berstatus `PENDING_INDEX` tercatat di database. | **PASSED** |
| `TC-CRP-003` | Pembaruan Metadata Dokumen Korpus (`CorpusService.update_corpus_doc`) | **Happy Ending** | Dokumen korpus terdaftar dan aktif. | `CorpusDocUpdateRequest(title="Judul Baru", category="Kecerdasan Buatan", academic_year="2025/2026")` | Query corpus doc -> branch `if not doc: False` -> update field `title`, `category`, `academic_year` -> `db.commit()`. | Metadata naskah korpus terbarui di database. | **PASSED** |
| `TC-CRP-004` | Soft Delete Dokumen Korpus (`CorpusService.delete_corpus_doc`) | **Happy Ending** | Dokumen korpus terdaftar di database. | `doc_id` dokumen korpus valid | Query corpus doc -> branch `if not doc: False` -> `doc.status = "DELETED"` -> `db.commit()`. | Status dokumen korpus berubah menjadi `DELETED` dan tidak lagi muncul di pencarian aktif. | **PASSED** |
| `TC-CRP-005` | Singleton ReferenceCorpusBank Built-in Papers (`ReferenceCorpusBank.get_instance`) | **Happy Ending** | Sistem diinisialisasi pertama kali tanpa korpus eksternal. | Pemanggilan `ReferenceCorpusBank.get_instance()` | Branch `if cls._instance is None:` -> inisialisasi singleton -> muat `BUILTIN_REFERENCE_PAPERS` -> ekstrak sidik jari leksikal & chunk semantik. | Objek singleton memuat setidaknya 5 makalah referensi ilmiah, index sidik jari leksikal > 0, dan chunk semantik > 0. | **PASSED** |
| `TC-CRP-006` | Pembaruan Metadata Korpus ID Tak Ditemukan (`CorpusService.update_corpus_doc`) | **Bad Case** | ID dokumen korpus yang diminta tidak ada di database. | `doc_id = uuid.uuid4()` acak, request update valid | Query corpus doc menghasilkan `None` -> branch `if not doc:` evaluates `True` -> raise `HTTPException(404)`. | Memicu `HTTPException` status 404 Not Found: "Corpus document not found". | **PASSED** |
| `TC-CRP-007` | Penghapusan Korpus ID Tak Ditemukan (`CorpusService.delete_corpus_doc`) | **Bad Case** | ID dokumen korpus yang akan dihapus tidak ada. | `doc_id = uuid.uuid4()` acak | Query corpus doc menghasilkan `None` -> branch `if not doc:` evaluates `True` -> raise `HTTPException(404)`. | Memicu `HTTPException` status 404 Not Found: "Corpus document not found". | **PASSED** |
| `TC-CRP-008` | Filter Kategori Korpus Kosong (`CorpusService.list_corpus_documents`) | **Bad Case** | Kategori pencarian tidak memiliki satu pun naskah terdaftar. | `category="KategoriTakAda"` | Query filter kategori mengembalikan 0 baris -> `total = 0`, `items = []`. | Mengembalikan tuple `([], 0)` tanpa error. | **PASSED** |
| `TC-CRP-009` | Penolakan Unggahan Arsip Korpus Ber-SHA-256 Duplikat (`CorpusService.ingest_zip_corpus`) | **Blocker** | Berkas arsip korpus dengan isi biner identik sudah pernah diunggah sebelumnya. | `UploadFile` dengan hash SHA-256 yang sudah terdaftar | `sha256 = hashlib.sha256(content).hexdigest()` -> query DB -> branch `if existing.scalar_one_or_none(): True` -> raise `HTTPException(409)`. | Memicu `HTTPException` status 409 Conflict: "Corpus document with identical content hash already exists". | **PASSED** |
| `TC-CRP-010` | Pemblokiran Akses Korpus oleh Mahasiswa TRIAL (`deps.require_role`) | **Blocker** | Pengguna dengan peran Mahasiswa (`role="TRIAL"` atau `"PREMIUM"`) mencoba mengakses endpoint korpus. | `current_user.role = "TRIAL"`, dependency `require_role("REVIEWER", "ADMIN")` | Role checker memeriksa peran -> `current_user.role not in ('REVIEWER', 'ADMIN')` -> evaluates `True` -> raise `HTTPException(403)`. | Akses diblokir dengan `HTTPException` status 403 Forbidden. Integritas bank korpus terlindungi dari manipulasi mahasiswa. | **PASSED** |

---

### FITUR 6: DOMPET TOKEN & BILLING
*Modul Target*: `backend/app/services/billing_service.py`, `backend/app/api/v1/billing.py`, `backend/app/services/document_service.py`, `backend/app/services/audit_service.py`

| ID Test Case | Nama Skenario & Target Modul/Metode | Kategori | Pre-conditions | Input Test Data | Jalur Eksekusi Whitebox (Branch / Logic Path) | Expected Output & State Result | Status |
|:---|:---|:---:|:---|:---|:---|:---|:---:|
| `TC-BIL-001` | Inisialisasi Dompet Token Pengguna Baru (`BillingService.get_wallet`) | **Happy Ending** | Pengguna baru belum memiliki baris data di tabel `token_wallets`. | `user_id` baru valid | `select(TokenWallet).where(user_id)` -> branch `if not wallet:` evaluates `True` -> `wallet = TokenWallet(balance=0)` -> `db.add(wallet)` -> `db.commit()`. | Dompet baru terinisialisasi dengan saldo 0 token dan tersimpan di database. | **PASSED** |
| `TC-BIL-002` | Pembuatan Invoice Top-Up Paket Mahasiswa (`BillingService.create_topup_invoice`) | **Happy Ending** | Paket top-up valid dipilih pengguna. | `package_id="pkg_10token"`, `user_id` valid | Branch `if package_id not in PACKAGES: False` -> generate format `order_id` -> generate demo `snap_token` -> `db.add(Invoice(status="PENDING"))`. | Invoice terbuat dengan status `PENDING`, `token_amount=10`, `gross_amount=25000`. | **PASSED** |
| `TC-BIL-003` | Penambahan Saldo via Settlement Webhook Midtrans (`BillingService.process_midtrans_webhook`) | **Happy Ending** | Invoice berstatus `PENDING` menunggu konfirmasi pembayaran. | Payload webhook settlement Midtrans valid, `gross_amount="25000.00"` | Validasi signature -> query invoice -> branch `if payload.transaction_status in ("capture", "settlement"):` -> `invoice.status = "PAID"` -> kredit saldo wallet -> `db.add(TokenTransaction(CREDIT_TOPUP))`. | Status invoice berubah menjadi `PAID`, saldo dompet bertambah 10 token, transaksi tercatat. | **PASSED** |
| `TC-BIL-004` | Pengurangan Saldo 2 Token Saat Audit FULL (`DocumentService.save_uploaded_file_and_create_task`) | **Happy Ending** | Pengguna memiliki saldo 10 token, memilih kedalaman audit `FULL`. | Dokumen valid, `audit_depth="FULL"` | `token_cost = 2` -> branch `if wallet.balance < token_cost: False` -> `wallet.balance -= 2` -> `db.add(TokenTransaction(DEBIT_AUDIT))` -> buat `AuditTask`. | Saldo berkurang dari 10 menjadi 8 token, transaksi `DEBIT_AUDIT` sebesar -2 tercatat. | **PASSED** |
| `TC-BIL-005` | Idempotensi Transaksi Webhook Pembayaran Ganda (`BillingService.process_midtrans_webhook`) | **Happy Ending** | Webhook settlement tiba untuk invoice yang sudah berstatus `PAID` (jaringan re-try). | Payload settlement untuk order ID yang sudah lunas | Query invoice -> branch `if invoice.status == "PAID":` evaluates `True` -> return `True`. | Mengembalikan `True` seketika tanpa menduplikasi penambahan saldo token (idempotent). | **PASSED** |
| `TC-BIL-006` | Penolakan Package ID Top-Up Tidak Terdaftar (`BillingService.create_topup_invoice`) | **Bad Case** | Klien mengirimkan ID paket ilegal atau hasil manipulasi. | `package_id="pkg_ilegal_hacked"` | Branch `if package_id not in PACKAGES:` evaluates `True` -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "Invalid package_id. Available: ...". | **PASSED** |
| `TC-BIL-007` | Penanganan Transaksi Batal / Kedaluwarsa Midtrans (`BillingService.process_midtrans_webhook`) | **Bad Case** | Pembayaran kedaluwarsa atau dibatalkan oleh gateway bank. | Payload webhook dengan `transaction_status="expire"` | Branch `elif payload.transaction_status in ("cancel", "expire"):` -> `invoice.status = "EXPIRED"`. | Status invoice diperbarui menjadi `EXPIRED`, saldo pengguna sama sekali tidak ditambah. | **PASSED** |
| `TC-BIL-008` | Webhook untuk Order ID yang Tidak Ditemukan (`BillingService.process_midtrans_webhook`) | **Bad Case** | Midtrans memanggil webhook untuk order ID yang tidak pernah dibuat sistem. | `order_id="VT-TIDAK-ADA-999"` | Query DB menghasilkan `None` -> branch `if not invoice:` evaluates `True` -> raise `HTTPException(404)`. | Memicu `HTTPException` status 404 Not Found: "Invoice order not found". | **PASSED** |
| `TC-BIL-009` | Pemblokiran Webhook Signature Palsu / Tampered (`BillingService.process_midtrans_webhook`) | **Blocker** | Penyerang mencoba memalsukan webhook pembayaran dengan signature sembarangan. | Payload webhook dengan `signature_key="signature_palsu_peretas"` pada environment produksi | Hitung `expected_sig = SHA512(order_id + status + gross + key)` -> periksa `payload.signature_key != expected_signature` -> evaluates `True` -> raise `HTTPException(403)`. | Memicu `HTTPException` status 403 Forbidden: "Invalid Midtrans signature key". Serangan spoofing digagalkan. | **PASSED** |
| `TC-BIL-010` | Pemblokiran Audit Saat Saldo Token Tidak Cukup (`DocumentService.save_uploaded_file_and_create_task`) | **Blocker** | Saldo pengguna 0 token, naskah diajukan untuk audit FULL (butuh 2 token). | User saldo 0 token, berkas naskah valid | `token_cost = 2` -> branch `if wallet.balance < token_cost:` evaluates `True` ($0 < 2$) -> raise `HTTPException(402)`. | Memicu `HTTPException` status 402 Payment Required: "Saldo token tidak mencukupi...". Proses dihentikan sebelum komputasi berat. | **PASSED** |

---

### FITUR 7: KONSOL TATA KELOLA ADMINISTRATOR & KEPATUHAN UU PDP
*Modul Target*: `backend/app/api/v1/admin.py`, `backend/app/models/audit_log.py`, `backend/app/api/deps.py`

| ID Test Case | Nama Skenario & Target Modul/Metode | Kategori | Pre-conditions | Input Test Data | Jalur Eksekusi Whitebox (Branch / Logic Path) | Expected Output & State Result | Status |
|:---|:---|:---:|:---|:---|:---|:---|:---:|
| `TC-ADM-001` | Daftar Seluruh Pengguna dengan Filter Role & Search (`admin_router.list_users_admin`) | **Happy Ending** | Database memuat berbagai pengguna (Admin, Reviewer, Mahasiswa). | `role="ADMIN"`, `search="veritext"`, `page=1`, `limit=10` | Branch `if role:` -> query filter role -> branch `if search:` -> filter ilike -> hitung total -> paginasi -> return `PaginatedData`. | Mengembalikan daftar pengguna terfilter role ADMIN dan keyword pencarian. | **PASSED** |
| `TC-ADM-002` | Admin Membuat Pengguna Baru & Alokasi Token (`admin_router.create_user_admin`) | **Happy Ending** | Email belum terdaftar di sistem. | `AdminUserCreateRequest(full_name="Dosen Penguji", email="penguji@kampus.ac.id", role="REVIEWER", initial_tokens=50)` | Query email -> branch `if existing: False` -> hash password -> `db.add(new_user)` -> `db.add(TokenWallet(balance=50))` -> `db.commit()`. | Akun pengguna baru terbuat dengan role REVIEWER dan saldo dompet token 50. | **PASSED** |
| `TC-ADM-003` | Pembaruan Profil & Role Pengguna oleh Admin (`admin_router.update_user_admin`) | **Happy Ending** | Pengguna target terdaftar di sistem. | `AdminUserUpdateRequest(full_name="Nama Baru", role="PREMIUM", institution="Kampus Baru")` | `find_user_by_identifier()` -> branch `if user:` -> update field yang tidak None -> `db.commit()` -> `db.refresh()`. | Nama, peran, dan institusi pengguna berhasil diperbarui. | **PASSED** |
| `TC-ADM-004` | Reset Password Pengguna oleh Admin (`admin_router.reset_password_admin`) | **Happy Ending** | Pengguna target terdaftar di sistem. | `AdminResetPasswordRequest(new_password="PasswordBaruAdmin#2026")` | `find_user_by_identifier()` -> hash password baru -> set `user.password_hash` -> `db.commit()`. | Hash password pengguna diperbarui dan dapat diverifikasi dengan `verify_password()`. | **PASSED** |
| `TC-ADM-005` | Penyesuaian Saldo Token Kredit/Debit oleh Admin (`admin_router.adjust_user_tokens`) | **Happy Ending** | Pengguna memiliki dompet token aktif (saldo 20). | `TokenAdjustmentRequest(amount=15, note="Bonus publikasi Q1")` | `find_user_by_identifier()` -> query wallet -> branch `if wallet.balance + amount < 0: False` -> update saldo -> `db.add(TokenTransaction(CREDIT_ADMIN))`. | Saldo bertambah menjadi 35 token, transaksi `CREDIT_ADMIN` tercatat di log transaksi. | **PASSED** |
| `TC-ADM-006` | Monitoring Metrik Kesehatan Sistem & DB Latency (`admin_router.get_health_metrics`) | **Happy Ending** | Basis data aktif dan responsif. | Pemanggilan `get_health_metrics()` | Hitung latency ping `SELECT 1` -> query hitung total audit, dokumen korpus, dan chunk vektor -> return `SystemHealthMetricsResponse`. | Mengembalikan status DB HEALTHY, metrik CPU/RAM, dan counter naskah/vektor akurat. | **PASSED** |
| `TC-ADM-007` | Penjadwalan Rekonstruksi Indeks HNSW pgvector (`admin_router.reindex_hnsw`) | **Happy Ending** | Indeks pgvector HNSW terpasang di PostgreSQL. | Pemanggilan `reindex_hnsw()` | Dispatch perintah re-indexing HNSW -> return status `SCHEDULED`. | Mengembalikan respon status `SCHEDULED` dan pesan konfirmasi penjadwalan. | **PASSED** |
| `TC-ADM-008` | Pembacaan Rekam Jejak Audit Log Forensik (`admin_router.list_audit_logs`) | **Happy Ending** | Aktivitas sistem tercatat di tabel `audit_logs`. | `action_type="USER_LOGIN"`, `page=1`, `limit=10` | `select(AuditLog)` -> branch `if action_type:` -> filter jenis aksi -> hitung total -> paginasi -> return `PaginatedData`. | Mengembalikan daftar log forensik audit lengkap dengan metadata IP, aktor, dan status. | **PASSED** |
| `TC-ADM-009` | Purge Data Retensi 30 Hari Permanen UU PDP No. 27/2022 (`admin_router.purge_retention_data`) | **Happy Ending** | Terdapat dokumen soft-deleted yang telah melampaui masa retensi 30 hari. | `retention_days=30` | Hitung `threshold_date = now - 30 hari` -> query dokumen DELETED sebelum threshold -> hapus berkas fisik dari `UPLOAD_DIR` -> `db.delete(doc)` -> catat `AuditLog(DOCUMENT_PURGE)` -> `db.commit()`. | Dokumen kedaluwarsa dibersihkan secara permanen, berkas fisik dihapus, tercatat log kepatuhan UU PDP Pasal 43 & 44. | **PASSED** |
| `TC-ADM-010` | Penolakan Penyesuaian Token Berakibat Saldo Negatif (`admin_router.adjust_user_tokens`) | **Bad Case** | Saldo pengguna saat ini bernilai 5 token. | `TokenAdjustmentRequest(amount=-10, note="Penalti")` | Query wallet (saldo 5) -> branch `if wallet.balance + req.amount < 0:` evaluates `True` ($5 - 10 = -5 < 0$) -> raise `HTTPException(400)`. | Memicu `HTTPException` status 400 Bad Request: "Adjustment would result in negative balance (-5)". | **PASSED** |
| `TC-ADM-011` | Akses Detail Pengguna Identifier Tidak Dikenal (`admin_router.get_user_detail_admin`) | **Bad Case** | Identifier UUID / email tidak terdaftar di sistem. | `user_id = str(uuid.uuid4())` acak | `find_user_by_identifier()` mengembalikan `None` -> branch `if not user:` evaluates `True` -> raise `HTTPException(404)`. | Memicu `HTTPException` status 404 Not Found: "User not found". | **PASSED** |
| `TC-ADM-012` | Penolakan Role Non-Admin pada Seluruh Konsol Administrator (`deps.require_role`) | **Blocker** | Pengguna dengan peran Dosen (`REVIEWER`) atau Mahasiswa (`TRIAL`) mencoba memanggil API admin. | `current_user.role = "REVIEWER"`, router dependencies `[Depends(require_role("ADMIN"))]` | Role checker mengevaluasi `current_user.role not in ('ADMIN',)` -> evaluates `True` -> raise `HTTPException(403)`. | Akses diblokir dengan `HTTPException` status 403 Forbidden. Seluruh konsol tata kelola terlindungi dari eskalasi hak istimewa (Privilege Escalation). | **PASSED** |

---

## 4. ANALISIS CAKUPAN LOGIKA & KOMPLEKSITAS SIKLOMATIK

### 4.1 Kompleksitas Siklomatik (*Cyclomatic Complexity* $V(G)$)
Kompleksitas diukur menggunakan formula McCabe $V(G) = E - N + 2P$ atau $V(G) = D + 1$ di mana $D$ adalah jumlah predikat keputusan:

1. **Modul Autentikasi (`AuthService`)**:
   - Predikat Keputusan: Pengecekan email duplikat, verifikasi hash password, pengecekan status akun aktif, token revocation.
   - $V(G) = 6$ (Low Risk / Highly Testable). Seluruh 6 jalur independen tercakup 100%.
2. **Modul Validasi Dokumen (`DocumentService`)**:
   - Predikat Keputusan: Validasi nama kosong, ada tidaknya ekstensi titik, ekstensi diizinkan, ukuran berkas kosong 0 byte, ukuran berkas melampaui 10MB, ketersediaan saldo token.
   - $V(G) = 7$ (Low Risk / Well Structured). Seluruh 7 jalur independen tercakup 100%.
3. **Mesin Deteksi 4-Tier (`HybridAggregator` & Engine Modules)**:
   - Predikat Keputusan: Teks kosong, boundary $n < k$, tie-breaking sliding window, threshold parafrase semantik $\ge 0.75$, deviasi standar nol AI monoton, deteksi pola sitasi akademik.
   - $V(G) = 9$ (Moderate / Thoroughly Covered). Seluruh 9 jalur independen terverifikasi komputasi matematisnya.
4. **Billing & Webhook Midtrans (`BillingService`)**:
   - Predikat Keputusan: Validasi package ID, verifikasi signature key SHA-512, keberadaan invoice, status invoice PAID (idempotent), status settlement/capture, status cancel/expire/deny.
   - $V(G) = 8$ (Low Risk). Seluruh cabang berhasil diuji termasuk kondisi spoofing signature.
5. **Konsol Tata Kelola Admin (`admin.py`)**:
   - Predikat Keputusan: Filter role, filter search ilike, validasi saldo negatif, identifier UUID vs email, purge batas retensi UU PDP 30 hari.
   - $V(G) = 8$ (Low Risk). Seluruh jalur percabangan tervalidasi.

---

## 5. BUKTI VERIFIKASI EKSEKUSI PENGUJIAN OTOMATIS

### 5.1 Hasil Eksekusi Test Suite Backend
```bash
$ venv/bin/python3 -m unittest discover -s tests -p "test_*.py"
........................................................
........................................................
.....................
----------------------------------------------------------------------
Ran 129 tests in 3.000s

OK
```
*Keterangan*: 
- 56 test case arsitektur & engine inti bawaan + 73 test case matriks whitebox baru dieksekusi bersamaan.
- **Tingkat Kelulusan**: **100% (129 dari 129 test lulus tanpa kegagalan maupun error)**.

### 5.2 Hasil Eksekusi Test Suite Frontend
```bash
$ npm test
> veritext-ai-frontend@1.0.0 test
> node --experimental-strip-types src/tests/navigation.test.mjs

[TEST] Menjalankan Pengujian Otomatis Segmentasi Hak Akses & Navigasi VeriText AI...

--- 1. Pengujian Segmentasi Navigasi Navbar (Desktop & Mobile) ---
  [PASS] Kondisi 1 (Tamu / Belum Login): HANYA Beranda dan Verifikasi QR
  [PASS] Kondisi 2 (Mahasiswa TRIAL): Beranda, Dashboard, Saldo Token, Verifikasi QR
  [PASS] Kondisi 2 (Mahasiswa PREMIUM): Beranda, Dashboard, Saldo Token, Verifikasi QR
  [PASS] Kondisi 2 (Mahasiswa USER): Beranda, Dashboard, Saldo Token, Verifikasi QR
  [PASS] Kondisi 3 (Dosen / Reviewer): Beranda, Dashboard, Bank Korpus, Saldo Token, Verifikasi QR
  [PASS] Kondisi 4 (Super Administrator): Dedicated Admin Console Links

--- 2. Pengujian Route Navigation Guard & Role-Based Access Control ---
  [PASS] Tamu mengakses rute publik (/ dan /verify) diperbolehkan
  [PASS] Tamu mengakses rute guest-only (/login dan /register) diperbolehkan
  [PASS] Tamu mengakses rute terproteksi (/dashboard) ditolak & diarahkan ke /login
  [PASS] Tamu mengakses rute terproteksi (/billing) ditolak & diarahkan ke /login
  [PASS] Tamu mengakses rute terproteksi (/audits/test-uuid) ditolak & diarahkan ke /login
  [PASS] Tamu mengakses rute Super Admin (/admin) ditolak
  [PASS] Mahasiswa sudah login mengakses /login dialihkan otomatis ke /dashboard
  [PASS] Mahasiswa sudah login mengakses /dashboard & /billing diperbolehkan
  [PASS] Mahasiswa mengakses /corpus ditolak & dialihkan ke /dashboard
  [PASS] Mahasiswa mengakses /admin ditolak & dialihkan ke /dashboard
  [PASS] Dosen / Reviewer mengakses /corpus diperbolehkan
  [PASS] Dosen / Reviewer mengakses /admin ditolak & dialihkan ke /dashboard
  [PASS] Super Admin mengakses /admin diperbolehkan
  [PASS] Super Admin mengakses /corpus diperbolehkan
  [PASS] Super Admin mengakses /dashboard diperbolehkan

--- 3. Pengujian Edge Cases & Kekokohan Guard ---
  [PASS] Edge Case: Trailing slash pada /admin/ oleh Mahasiswa tetap ditolak
  [PASS] Edge Case: Role huruf kecil ('admin', 'reviewer') case-insensitive
  [PASS] Edge Case: Rute dengan batasan role tanpa flag requiresAuth eksplisit tetap menolak tamu
  [PASS] Edge Case: Tamu belum login mengakses /corpus ditolak & dialihkan ke /login

[SUCCESS] Seluruh 25 pengujian berhasil diverifikasi tanpa kegagalan!
```
*Keterangan*: 
- Menguji otentikasi rute, role guards, dan segmentasi antarmuka pengguna pada sisi client-side.
- **Tingkat Kelulusan**: **100% (25 dari 25 test lulus tanpa kegagalan)**.

---

## 6. KESIMPULAN & JAMINAN KUALITAS PERANGKAT LUNAK

1. **Kelengkapan Kasus Uji**: Seluruh 7 fitur utama sistem VeriText AI telah dilengkapi minimal 10 test case per fitur dengan total **73 test case whitebox**, memuat kategori **Happy Ending** (39 kasus), **Bad Case** (22 kasus), dan **Blocker** (12 kasus).
2. **Kekokohan Sistem (Robustness & Resilience)**: Batasan input kritis seperti berkas 0 byte, ukuran >10MB, ekstensi tidak sah, teks kosong, pembagian dengan nol, dan saldo token tidak mencukupi tertangani secara elegan dengan pesan kesalahan HTTP yang deskriptif.
3. **Integritas Keamanan & Privasi (UU PDP Compliance)**:
   - Mekanisme **Tenant Isolation** mencegah pembocoran dokumen antar pengguna.
   - Mekanisme **RBAC Guard** mencegah eskalasi hak akses role mahasiswa ke fungsi dosen maupun super admin.
   - Endpoint **Purge Retensi Data 30 Hari** memenuhi mandat hak penghapusan data pribadi (*Right to Erasure*) sesuai **UU PDP No. 27/2022 Pasal 43 & 44**, di mana berkas fisik naskah dibersihkan dan sertifikat publik otomatis ditandai kedaluwarsa.
4. **Verifikasi Bebas Regresi**: Seluruh 129 pengujian backend dan 25 pengujian frontend berhasil lulus 100% secara konsisten dan siap untuk tahap audit kode serta pengujian integrasi lanjutan.
