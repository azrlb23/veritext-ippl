# VeriText AI — Dokumen Verifikasi & Laporan Remediasi Fase 2
## Integritas Keuangan, Kriptografi, Transaksi Database & Skema Alembic

> **Tanggal Rilis**: 24 Oktober 2026  
> **Status Verifikasi**: Selesai Diverifikasi 100% (Green Test Suite)  
> **Metode Pelaksanaan**: Test-Driven Development (TDD) — *Red, Green, Refactor*  
> **Cakupan Pengujian**: 163 Backend Unit/Integration Tests & 25 Frontend Security & Navigation Tests  

---

## 1. Ringkasan Eksekutif & Temuan yang Diperbaiki

Pada perbaikan **Fase 2**, tim rekayasa perangkat lunak VeriText AI berfokus pada pengerasan integritas finansial, kriptografi proteksi webhook, penguncian baris database tingkat transaksi (row-level locking), integritas skema relasional Alembic/PostgreSQL, serta eliminasi manipulasi nilai kemiripan artifisial pada engine plagiarisme.

Tabel di bawah merangkum 11 kode temuan keamanan dan integritas yang dituntaskan:

| ID Temuan | Kategori Keparahan | Klasifikasi Celah | Deskripsi Masalah | Status Remediasi |
|---|:---:|---|---|:---:|
| **[D1]** | **Tinggi (High)** | Cryptographic Flaw / Insecure Webhook | Validasi signature Midtrans di-bypass saat development, perbandingan non-constant-time, gross_amount tidak divalidasi | **RESOLVED & VERIFIED** |
| **[D2]** | **Tinggi (High)** | Concurrency Race Condition | Webhook paralel menerima 2x notifikasi settlement yang memicu pemberian token saldo ganda | **RESOLVED & VERIFIED** |
| **[D3]** | **Sedang (Medium)** | Concurrency Lost Update | Pengurangan token pada audit tanpa pessimistic lock memicu *Lost Update Anomaly* (audit gratis) | **RESOLVED & VERIFIED** |
| **[ROUND5-03]** | **Tinggi (High)** | Cryptographic Flaw / Amount Tampering | Timing attack pada SHA-512 signature string, manipulasi nilai gross_amount, dan pengabaian fraud_status | **RESOLVED & VERIFIED** |
| **[ROUND6-03]** | **Tinggi (High)** | Concurrency Race Condition | Penyesuaian saldo token admin vs pemakaian token audit pengguna saling menimpa tanpa lock | **RESOLVED & VERIFIED** |
| **[ROUND6-04]** | **Kritis (Critical)** | Concurrency / Double-Credit | Webhook Midtrans membaca status PENDING secara bersamaan tanpa lock baris invoice | **RESOLVED & VERIFIED** |
| **[FINAL-01]** | **Sedang (Medium)** | Database Schema Integrity | Missing FK indexes pada `corpus_documents.uploaded_by` dan `password_resets.user_id` memicu full table lock | **RESOLVED & VERIFIED** |
| **[FINAL-03]** | **Sedang (Medium)** | Vector Data Integrity | Ketiadaan composite unique constraint pada `document_chunks(corpus_doc_id, chunk_index)` | **RESOLVED & VERIFIED** |
| **[ROUND3-02]** | **Sedang (Medium)** | Plagiarism Metric Inflation | Floor artifisial `max(sim_ratio, 0.70)` pada Tier 1 Winnowing mendongkrak kemiripan rendah menjadi 70% | **RESOLVED & VERIFIED** |
| **[ROUND3-04]** | **Rendah (Low)** | Plagiarism Metric Phantom Factor | Pengali hantu `max(score_composite, 5.0)` pada Tier 4 menghasilkan rujukan 5.0% pada naskah 0.0% | **RESOLVED & VERIFIED** |
| **[NEW-04]** | **Sedang (Medium)** | Predictable Resource Identifier | Entropi order ID invoice hanya 8 karakter heksadesimal (`[:8]`), rentan tebakan enumerasi | **RESOLVED & VERIFIED** |

---

## 2. Rincian Modifikasi Berkas & Komparasi Diff (Before vs After)

### 2.1. `backend/app/services/billing_service.py` & `backend/app/api/v1/billing.py`
**Masalah**: 
1. `BillingService.process_midtrans_webhook` menggunakan `payload.signature_key != expected_signature` (bukan constant-time) dan mengabaikan pengecekan jika `ENVIRONMENT == "development"`.
2. Ketiadaan pencocokan `float(payload.gross_amount) == float(invoice.gross_amount)`.
3. Ketiadaan evaluasi `fraud_status` (kartu kredit dalam status "challenge" tetap dikreditkan).
4. Ketiadaan `.with_for_update()` pada pembacaan `Invoice` dan `TokenWallet`.
5. Order ID invoice menggunakan `uuid.uuid4().hex[:8]`.

**Solusi & Diff**:
```diff
--- a/backend/app/services/billing_service.py
+++ b/backend/app/services/billing_service.py
@@ -1,5 +1,6 @@
 from datetime import datetime, timezone
 import hashlib
+import hmac
 from typing import Optional
 import uuid
 from fastapi import HTTPException, status
@@ -43,7 +43,7 @@
 
         pkg = PACKAGES[package_id]
         date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
-        order_id = f"VT-{date_str}-{uuid.uuid4().hex[:8].upper()}"
+        order_id = f"VT-{date_str}-{uuid.uuid4().hex[:12].upper()}"
 
         # Demo / Sandbox snap token
         snap_token = f"SNAP-{uuid.uuid4().hex}"
@@ -72,8 +72,12 @@
         )
         expected_signature = hashlib.sha512(expected_sig_raw.encode("utf-8")).hexdigest()
 
-        # In dev mode, allow simulated webhooks if key doesn't match perfectly
-        if settings.ENVIRONMENT != "development" and payload.signature_key != expected_signature:
+        # Constant-time comparison using hmac.compare_digest (strictly enforced, no dev bypass)
+        if not hmac.compare_digest(payload.signature_key, expected_signature):
+            raise HTTPException(
+                status_code=status.HTTP_400_BAD_REQUEST,
+                detail="Invalid Midtrans signature key",
+            )
@@ -80,5 +80,6 @@
 
-        stmt = select(Invoice).where(Invoice.order_id == payload.order_id)
+        # Row-level locking on Invoice to prevent race conditions & double-crediting
+        stmt = select(Invoice).where(Invoice.order_id == payload.order_id).with_for_update()
         result = await db.execute(stmt)
         invoice = result.scalar_one_or_none()
 
@@ -87,6 +87,17 @@
                 detail="Invoice order not found",
             )
 
+        # Strict validation: gross_amount in payload must match invoice record
+        try:
+            payload_amount = float(payload.gross_amount)
+            invoice_amount = float(invoice.gross_amount) if invoice.gross_amount is not None else None
+        except (ValueError, TypeError):
+            raise HTTPException(
+                status_code=status.HTTP_400_BAD_REQUEST,
+                detail=f"Invalid gross amount format: {payload.gross_amount}",
+            )
+        if invoice_amount is not None and abs(payload_amount - invoice_amount) > 0.01:
+            raise HTTPException(
+                status_code=status.HTTP_400_BAD_REQUEST,
+                detail=f"Gross amount mismatch: expected {invoice.gross_amount}, got {payload.gross_amount}",
+            )
+
         if invoice.status == "PAID":
             return True
 
@@ -93,26 +93,35 @@
-            invoice.status = "PAID"
-            invoice.paid_at = datetime.now(timezone.utc)
-            invoice.payment_method = payload.payment_type or "bank_transfer"
-
-            # Credit wallet
-            wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == invoice.user_id)
-            wallet_res = await db.execute(wallet_stmt)
-            wallet = wallet_res.scalar_one_or_none()
-            if not wallet:
-                wallet = TokenWallet(user_id=invoice.user_id, balance=0)
-                db.add(wallet)
-                await db.flush()
-
-            wallet.balance += invoice.token_amount
-            tx = TokenTransaction(
-                wallet_id=wallet.id,
-                transaction_type="CREDIT_TOPUP",
-                amount=invoice.token_amount,
-                balance_after=wallet.balance,
-                reference_id=invoice.id,
-                note=f"Top-up {invoice.package_name}",
-            )
-            db.add(tx)
+            # If fraud_status is present, verify that it is 'accept'
+            fraud_stat = getattr(payload, "fraud_status", None)
+            if fraud_stat and fraud_stat != "accept":
+                invoice.status = "CHALLENGE" if fraud_stat == "challenge" else "FAILED"
+            else:
+                invoice.status = "PAID"
+                invoice.paid_at = datetime.now(timezone.utc)
+                invoice.payment_method = payload.payment_type or "bank_transfer"
+
+                # Credit wallet with row-level locking
+                wallet_stmt = (
+                    select(TokenWallet)
+                    .where(TokenWallet.user_id == invoice.user_id)
+                    .with_for_update()
+                )
+                wallet_res = await db.execute(wallet_stmt)
+                wallet = wallet_res.scalar_one_or_none()
+                if not wallet:
+                    wallet = TokenWallet(user_id=invoice.user_id, balance=0)
+                    db.add(wallet)
+                    await db.flush()
+
+                wallet.balance += invoice.token_amount
+                tx = TokenTransaction(
+                    wallet_id=wallet.id,
+                    transaction_type="CREDIT_TOPUP",
+                    amount=invoice.token_amount,
+                    balance_after=wallet.balance,
+                    reference_id=invoice.id,
+                    note=f"Top-up {invoice.package_name}",
+                )
+                db.add(tx)
```

Pada `backend/app/api/v1/billing.py`:
Endpoint `midtrans_webhook` memanggil langsung `await BillingService.process_midtrans_webhook(db, payload)` yang secara konsisten dan murni mengembalikan status HTTP 400 Bad Request jika signature Midtrans tidak valid.

---

### 2.2. Row-Level Locking Saldo Token (`backend/app/services/document_service.py`, `backend/app/services/audit_service.py`, `backend/app/api/v1/admin.py`)
**Masalah**: Pengurangan kuota token pada saat unggah berkas naskah (`document_service.py`), inisiasi audit task (`audit_service.py`), dan mutasi saldo kuota oleh admin (`admin.py`) membaca baris `TokenWallet` tanpa pessimistic locking, memicu *Lost Update Anomaly*.

**Solusi & Diff**:
Pada `backend/app/services/document_service.py`:
```diff
@@ -117,3 +117,7 @@
         token_cost = 1 if audit_depth == "TIER1_ONLY" else 2
-        wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
+        wallet_stmt = (
+            select(TokenWallet)
+            .where(TokenWallet.user_id == user_id)
+            .with_for_update()
+        )
         wallet_res = await db.execute(wallet_stmt)
```

Pada `backend/app/services/audit_service.py`:
```diff
@@ -31,3 +31,7 @@
         # Check and debit user token wallet
-        wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
+        wallet_stmt = (
+            select(TokenWallet)
+            .where(TokenWallet.user_id == user_id)
+            .with_for_update()
+        )
         wallet_res = await db.execute(wallet_stmt)
```

Pada `backend/app/api/v1/admin.py`:
```diff
@@ -235,3 +235,7 @@
 
-    wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user.id)
+    wallet_stmt = (
+        select(TokenWallet)
+        .where(TokenWallet.user_id == user.id)
+        .with_for_update()
+    )
     wallet = (await db.execute(wallet_stmt)).scalar_one_or_none()
```

---

### 2.3. Skema Alembic & Model Relasional (`backend/alembic/versions/0002_phase2_security_hardening.py`, `backend/app/models/corpus.py`, `backend/app/models/password_reset.py`)
**Masalah**:
1. Ketiadaan indeks pada foreign key `corpus_documents.uploaded_by` dan `password_resets.user_id` menyebabkan PostgreSQL melakukan *full table scan* dan mengunci tabel anak dengan `ShareRowExclusiveLock` saat akun pengguna dimutasi/dihapus.
2. Ketiadaan constraint unik komposit pada `document_chunks` membuka celah duplikasi chunk vektor saat indexing ulang naskah korpus.

**Solusi**:
1. Dibuat migrasi baru `backend/alembic/versions/0002_phase2_security_hardening.py`:
   - `op.create_index('idx_corpus_documents_uploaded_by', 'corpus_documents', ['uploaded_by'])`
   - `op.create_index('idx_password_resets_user_id', 'password_resets', ['user_id'])`
   - `op.create_unique_constraint('uq_document_chunks_corpus_chunk', 'document_chunks', ['corpus_doc_id', 'chunk_index'])`
2. Deklarasi model `backend/app/models/corpus.py`:
   - Menambahkan `Index("idx_corpus_documents_uploaded_by", "uploaded_by")` pada `__table_args__` tanpa duplikasi `index=True` pada Column.
   - Menambahkan `UniqueConstraint("corpus_doc_id", "chunk_index", name="uq_document_chunks_corpus_chunk")` pada `DocumentChunk`.
3. Deklarasi model `backend/app/models/password_reset.py`:
   - Menambahkan `Index("idx_password_resets_user_id", "user_id")` pada `__table_args__` tanpa duplikasi `index=True` pada Column.
4. Sinkronisasi skema basis data kontainer `db/init/02_schema_ddl.sql` agar inisialisasi lingkungan baru secara konsisten memiliki indeks foreign key dan constraint unik yang identik.

---

### 2.4. Koreksi Engine Kemiripan (`backend/app/engine/tier1_lexical.py` & `backend/app/engine/tier4_aggregator.py`)
**Masalah**:
1. Pada `tier1_lexical.py`, baris `similarity=round(min(1.0, max(sim_ratio, 0.70)), 2)` menggelembungkan kemiripan kalimat secara artifisial menjadi 70% meskipun kecocokan hanya 40%.
2. Pada `tier4_aggregator.py`, baris `contrib = round(ratio * max(score_composite, 5.0), 1)` memunculkan rujukan sumber hantu sebesar 5.0% pada naskah yang sama sekali orisinal (0.0%).

**Solusi & Diff**:
Pada `backend/app/engine/tier1_lexical.py`:
```diff
@@ -203,3 +203,3 @@
                     sentence_index=s.index,
                     matching_fingerprints=len(s_matched),
                     total_fingerprints=len(s_hashes),
-                    similarity=round(min(1.0, max(sim_ratio, 0.70)), 2),
+                    similarity=round(min(1.0, sim_ratio), 2),
                     matched_corpus_doc_id=best_doc_id,
```

Pada `backend/app/engine/tier4_aggregator.py`:
```diff
@@ -282,7 +282,7 @@
-        if not source_weights:
+        if not source_weights or score_composite <= 0.0:
             return []
 
         total_weight = sum(item["raw_weight"] for item in source_weights.values())
         if total_weight <= 0:
             total_weight = 1.0
 
         matched_list: List[Dict[str, Any]] = []
         for item in source_weights.values():
             ratio = item["raw_weight"] / total_weight
-            contrib = round(ratio * max(score_composite, 5.0), 1)
+            contrib = round(ratio * score_composite, 1)
             matched_list.append(MatchedSourceData(
```

---

## 3. Rincian Test Cases TDD (`backend/tests/test_remediation_phase2.py`)

Suite pengujian baru `test_remediation_phase2.py` memuat 6 skenario pengujian komprehensif:

1. **`test_tc_sec_09_midtrans_constant_time_hmac_and_no_dev_bypass`**:
   - Memverifikasi penolakan signature tidak valid bahkan ketika `settings.ENVIRONMENT == "development"` (tidak ada celah bypass dev mode).
   - Memverifikasi endpoint router `/api/v1/billing/webhook` mengembalikan HTTP 400 Bad Request pada signature tidak valid.
   - Memverifikasi penolakan manipulasi nominal `gross_amount` dengan HTTP 400.
   - Memverifikasi penahanan status `CHALLENGE` pada transaksi berstatus `fraud_status != "accept"` (dompet token tidak dikreditkan).
   - Memverifikasi pengkreditan saldo saat signature valid, amount cocok, dan fraud status accept.

2. **`test_tc_sec_10_row_level_locking_on_wallet_and_invoice`**:
   - Memeriksa inspeksi AST/SQLAlchemy pernyataan query `Invoice` dan `TokenWallet` pada `midtrans_webhook` memiliki argumen `_for_update_arg is not None`.
   - Memeriksa pernyataan query `TokenWallet` pada `DocumentService.save_uploaded_file_and_create_task` memiliki argumen `.with_for_update()`.
   - Memeriksa pernyataan query `TokenWallet` pada `AuditService.create_audit_task` memiliki argumen `.with_for_update()`.
   - Memeriksa pernyataan query `TokenWallet` pada `admin.adjust_user_tokens` memiliki argumen `.with_for_update()`.

3. **`test_tc_sec_11_alembic_fk_indices_and_unique_constraint`**:
   - Memvalidasi `DocumentChunk.__table__.constraints` memuat `UniqueConstraint` pada `('corpus_doc_id', 'chunk_index')`.
   - Memvalidasi `CorpusDocument.__table__.indexes` memuat indeks foreign key pada kolom `uploaded_by`.
   - Memvalidasi `PasswordReset.__table__.indexes` memuat indeks foreign key pada kolom `user_id`.
   - Memvalidasi berkas migrasi `0002_phase2_security_hardening.py` dapat dieksekusi secara dinamis dengan callable `upgrade` dan `downgrade`.

4. **`test_tc_sec_12_tier1_lexical_no_artificial_70_percent_floor`**:
   - Menjalankan analisis Winnowing leksikal pada kalimat dengan rasio fingerprint terukur ~48%.
   - Memverifikasi bahwa nilai kemiripan `SentenceLexicalMatch.similarity` adalah nilai matematis murni (0.48), bukan angka 0.70.

5. **`test_tc_sec_13_tier4_aggregator_no_phantom_5_percent`**:
   - Menjalankan pipeline lengkap `HybridAggregator` pada naskah yang sama sekali tidak mirip korpus pembanding.
   - Memverifikasi bahwa `score_composite == 0.0` dan daftar `matched_sources` adalah `[]` (tanpa rujukan phantom 5.0%).

6. **`test_tc_sec_14_cryptographic_order_id_entropy`**:
   - Menguji pembuatan 100 order ID top-up secara berulang.
   - Memvalidasi format string regex `^VT-\d{8}-[A-F0-9]{12}$` (48-bit heksadesimal acak).
   - Memastikan tidak ada tabrakan order ID (0 collision).

---

## 4. Bukti Eksekusi Pengujian & Hasil Verifikasi

### 4.1. Eksekusi Unit Test Backend (`unittest discover`)
```bash
$ venv/bin/python3 -m unittest discover -s tests -p "test_*.py"
........................................................
........................................................
........................................................
----------------------------------------------------------------------
Ran 163 tests in 4.142s

OK
```
> **Hasil**: Seluruh **163 pengujian backend** (157 pengujian awal + 6 pengujian Fase 2) **LULUS 100% tanpa kegagalan**.

### 4.2. Eksekusi Pengujian Frontend & Build Produksi Vite
```bash
$ npm test && npm run build

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
  [PASS] Seluruh skenario RBAC & redirect guard lolos (14 tes)
--- 3. Pengujian Edge Cases & Kekokohan Guard ---
  [PASS] Trailing slash, case-insensitivity, default guard lolos (4 tes)

[SUCCESS] Seluruh 25 pengujian berhasil diverifikasi tanpa kegagalan!

> veritext-ai-frontend@1.0.0 build
> vue-tsc && vite build
✓ 217 modules transformed.
dist/index.html                   1.07 kB │ gzip:   0.59 kB
dist/assets/index-ZsyS3Zzl.css   68.93 kB │ gzip:  11.25 kB
dist/assets/index-DK7ym4Te.js   456.66 kB │ gzip: 133.49 kB
✓ built in 1.04s
```
> **Hasil**: Seluruh **25 pengujian frontend** dan **typecheck vue-tsc + build produksi Vite** **LULUS 100% tanpa error**.
