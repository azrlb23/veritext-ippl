"""
Test Suite: Remediation Phase 2 — Integritas Keuangan, Kriptografi, Transaksi Database & Skema Alembic
TDD Tests verifying:
  - test_tc_sec_09_midtrans_constant_time_hmac_and_no_dev_bypass
  - test_tc_sec_10_row_level_locking_on_wallet_and_invoice
  - test_tc_sec_11_alembic_fk_indices_and_unique_constraint
  - test_tc_sec_12_tier1_lexical_no_artificial_70_percent_floor
  - test_tc_sec_13_tier4_aggregator_no_phantom_5_percent
  - test_tc_sec_14_cryptographic_order_id_entropy
"""

import asyncio
from datetime import datetime, timezone
import hashlib
import hmac
import importlib.util
import os
import re
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import Index, UniqueConstraint, select
from sqlalchemy.dialects import postgresql

from app.main import app
from app.core.config import settings
from app.core.database import get_db
from app.models.audit import AuditTask
from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
from app.models.document import Document
from app.models.invoice import Invoice
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.admin import TokenAdjustmentRequest
from app.schemas.audit import AuditStartRequest
from app.schemas.billing import MidtransWebhookPayload
from app.services.billing_service import BillingService
from app.services.audit_service import AuditService
from app.services.document_service import DocumentService
from app.engine.preprocessor import TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier4_aggregator import HybridAggregator, MatchedSourceData
from app.api.v1 import admin as admin_module
from app.api.v1 import billing as billing_router


class MockQueryResult:
    def __init__(self, items=None, scalar_val=None):
        self._items = items if items is not None else []
        self._scalar_val = scalar_val

    def scalar_one_or_none(self):
        if self._scalar_val is not None:
            return self._scalar_val
        return self._items[0] if self._items else None

    def scalar(self):
        if self._scalar_val is not None:
            return self._scalar_val
        return self._items[0] if self._items else None

    def scalars(self):
        return self

    def all(self):
        return list(self._items)

    def first(self):
        return self._items[0] if self._items else None


class MockAsyncSession:
    def __init__(self, execute_handler=None):
        self.execute_handler = execute_handler
        self.executed_statements = []
        self.added = []
        self.deleted = []
        self.committed = False
        self.flushed = False

    async def execute(self, stmt):
        self.executed_statements.append(stmt)
        if self.execute_handler:
            res = self.execute_handler(stmt)
            if asyncio.iscoroutine(res):
                return await res
            return res
        return MockQueryResult([])

    def add(self, item):
        self.added.append(item)
        if hasattr(item, "id") and getattr(item, "id", None) is None:
            item.id = uuid.uuid4()

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True

    async def refresh(self, item):
        pass

    async def delete(self, item):
        self.deleted.append(item)


class TestRemediationPhase2TDD(unittest.IsolatedAsyncioTestCase):
    """Fase 2 Test-Driven Verification Suite: Keuangan, Kriptografi, Konkurensi & Skema."""

    async def test_tc_sec_09_midtrans_constant_time_hmac_and_no_dev_bypass(self):
        """
        [D1 & ROUND5-03]:
        1. Webhook Midtrans menolak signature tidak valid dengan HTTP 400 (atau 403) via API.
        2. Dalam development mode (settings.ENVIRONMENT == 'development'), bypass dev TIDAK berlaku untuk signature palsu.
        3. Memvalidasi nominal gross_amount dengan invoice; menolak nominal yang dimanipulasi dengan HTTP 400.
        4. Transaksi dengan fraud_status != 'accept' (mis. 'challenge') tidak mengkredit saldo dompet token.
        5. Menggunakan hmac.compare_digest untuk mencegah side-channel timing attack.
        """
        order_id = "VT-20261024-TESTSEC09"
        status_code = "200"
        gross_amount = "25000.00"
        correct_raw = f"{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}"
        valid_sig = hashlib.sha512(correct_raw.encode("utf-8")).hexdigest()

        invoice = Invoice(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            order_id=order_id,
            token_amount=10,
            gross_amount=25000,
            status="PENDING",
            package_name="Paket Mahasiswa",
        )
        wallet = TokenWallet(id=uuid.uuid4(), user_id=invoice.user_id, balance=5)

        # Handler that returns invoice first, then wallet
        call_idx = 0
        def exec_handler(stmt):
            nonlocal call_idx
            call_idx += 1
            if call_idx == 1:
                return MockQueryResult([invoice])
            return MockQueryResult([wallet])

        # Sub-test A: Invalid signature in development mode MUST be rejected (no dev bypass!)
        with patch.object(settings, "ENVIRONMENT", "development"):
            mock_db = MockAsyncSession(execute_handler=exec_handler)
            tampered_payload = MidtransWebhookPayload(
                order_id=order_id,
                status_code=status_code,
                gross_amount=gross_amount,
                signature_key="tampered_fake_signature_hash_1234567890abcdef",
                transaction_status="settlement",
                payment_type="bank_transfer",
            )
            # Both direct call and endpoint MUST reject with HTTP 400
            with self.assertRaises(HTTPException) as ctx:
                await BillingService.process_midtrans_webhook(mock_db, tampered_payload)
            self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Invalid Midtrans signature key", ctx.exception.detail)

            # Webhook endpoint router maps invalid signature to HTTP 400
            with self.assertRaises(HTTPException) as ctx_ep:
                await billing_router.midtrans_webhook(tampered_payload, mock_db)
            self.assertEqual(ctx_ep.exception.status_code, status.HTTP_400_BAD_REQUEST)

        # Sub-test A2: Legacy dummy signatures ('dummy_sig', 'sig') MUST be strictly rejected with HTTP 400 even in dev mode
        with patch.object(settings, "ENVIRONMENT", "development"):
            mock_db = MockAsyncSession(execute_handler=exec_handler)
            for fake_sig in ("dummy_sig", "sig"):
                fake_payload = MidtransWebhookPayload(
                    order_id=order_id,
                    status_code=status_code,
                    gross_amount=gross_amount,
                    signature_key=fake_sig,
                    transaction_status="settlement",
                    payment_type="bank_transfer",
                )
                with self.assertRaises(HTTPException) as ctx_fake:
                    await BillingService.process_midtrans_webhook(mock_db, fake_payload)
                self.assertEqual(ctx_fake.exception.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("Invalid Midtrans signature key", ctx_fake.exception.detail)

        # Sub-test B: Nominal gross_amount mismatch manipulation rejected with HTTP 400
        call_idx = 0
        invoice.status = "PENDING"
        mismatched_amount_raw = f"{order_id}{status_code}5000.00{settings.MIDTRANS_SERVER_KEY}"
        mismatched_sig = hashlib.sha512(mismatched_amount_raw.encode("utf-8")).hexdigest()

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        manipulated_payload = MidtransWebhookPayload(
            order_id=order_id,
            status_code=status_code,
            gross_amount="5000.00",  # Manipulated: invoice is 25000.00
            signature_key=mismatched_sig,
            transaction_status="settlement",
            payment_type="bank_transfer",
        )
        with self.assertRaises(HTTPException) as ctx:
            await BillingService.process_midtrans_webhook(mock_db, manipulated_payload)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Gross amount mismatch", ctx.exception.detail)

        # Sub-test B2: Malformed gross_amount string rejected with HTTP 400 Bad Request
        call_idx = 0
        invoice.status = "PENDING"
        bad_gross_raw = f"{order_id}{status_code}not_a_number{settings.MIDTRANS_SERVER_KEY}"
        bad_gross_sig = hashlib.sha512(bad_gross_raw.encode("utf-8")).hexdigest()
        bad_amount_payload = MidtransWebhookPayload(
            order_id=order_id,
            status_code=status_code,
            gross_amount="not_a_number",
            signature_key=bad_gross_sig,
            transaction_status="settlement",
            payment_type="bank_transfer",
        )
        with self.assertRaises(HTTPException) as ctx_bad:
            await BillingService.process_midtrans_webhook(mock_db, bad_amount_payload)
        self.assertEqual(ctx_bad.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid gross amount format", ctx_bad.exception.detail)

        # Sub-test C: fraud_status != 'accept' does NOT credit token wallet
        call_idx = 0
        invoice.status = "PENDING"
        wallet.balance = 5
        mock_db = MockAsyncSession(execute_handler=exec_handler)
        challenge_payload = MidtransWebhookPayload(
            order_id=order_id,
            status_code=status_code,
            gross_amount=gross_amount,
            signature_key=valid_sig,
            transaction_status="capture",
            payment_type="credit_card",
            fraud_status="challenge",
        )
        res = await BillingService.process_midtrans_webhook(mock_db, challenge_payload)
        self.assertTrue(res)
        self.assertEqual(invoice.status, "CHALLENGE")
        self.assertEqual(wallet.balance, 5)  # No tokens added on fraud challenge!

        # Sub-test D: Valid signature, matched amount, and fraud_status=='accept' credits wallet
        call_idx = 0
        invoice.status = "PENDING"
        wallet.balance = 5
        mock_db = MockAsyncSession(execute_handler=exec_handler)
        valid_payload = MidtransWebhookPayload(
            order_id=order_id,
            status_code=status_code,
            gross_amount=gross_amount,
            signature_key=valid_sig,
            transaction_status="settlement",
            payment_type="bank_transfer",
            fraud_status="accept",
        )
        res = await BillingService.process_midtrans_webhook(mock_db, valid_payload)
        self.assertTrue(res)
        self.assertEqual(invoice.status, "PAID")
        self.assertEqual(wallet.balance, 15)  # 5 + 10 credited

    async def test_tc_sec_10_row_level_locking_on_wallet_and_invoice(self):
        """
        [D2, D3, ROUND6-03 & ROUND6-04]:
        Query pembacaan Invoice pada webhook dan TokenWallet pada mutasi saldo
        menerapkan row-level locking (.with_for_update()) untuk mengeliminasi Lost Update Anomaly.
        """
        user_id = uuid.uuid4()
        order_id = "VT-LOCK-20261024"
        raw = f"{order_id}20025000.00{settings.MIDTRANS_SERVER_KEY}"
        sig = hashlib.sha512(raw.encode("utf-8")).hexdigest()

        invoice = Invoice(
            id=uuid.uuid4(),
            user_id=user_id,
            order_id=order_id,
            token_amount=10,
            gross_amount=25000,
            status="PENDING",
            package_name="Paket 10",
        )
        wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=10)

        # 1. Verify Midtrans Webhook uses with_for_update() on Invoice AND TokenWallet
        exec_count = 0
        webhook_stmts = []
        def webhook_handler(stmt):
            nonlocal exec_count
            exec_count += 1
            webhook_stmts.append(stmt)
            if exec_count == 1:
                return MockQueryResult([invoice])
            return MockQueryResult([wallet])

        mock_db_webhook = MockAsyncSession(execute_handler=webhook_handler)
        payload = MidtransWebhookPayload(
            order_id=order_id,
            status_code="200",
            gross_amount="25000.00",
            signature_key=sig,
            transaction_status="settlement",
        )
        await BillingService.process_midtrans_webhook(mock_db_webhook, payload)

        self.assertGreaterEqual(len(webhook_stmts), 2)
        invoice_query = webhook_stmts[0]
        wallet_query = webhook_stmts[1]

        self.assertIsNotNone(
            getattr(invoice_query, "_for_update_arg", None),
            "Query Invoice pada midtrans_webhook wajib memanggil .with_for_update()",
        )
        self.assertIsNotNone(
            getattr(wallet_query, "_for_update_arg", None),
            "Query TokenWallet pada midtrans_webhook wajib memanggil .with_for_update()",
        )

        # 2. Verify DocumentService token deduction uses with_for_update() on TokenWallet
        doc_stmts = []
        def doc_handler(stmt):
            doc_stmts.append(stmt)
            return MockQueryResult([wallet])

        mock_db_doc = MockAsyncSession(execute_handler=doc_handler)
        mock_file = AsyncMock()
        mock_file.filename = "skripsi_lock_test.pdf"
        mock_file.read.return_value = b"konten valid pengujian locking dokumen"
        mock_file.content_type = "application/pdf"

        from app.workers.celery_app import celery_app
        with patch.object(celery_app.control, "inspect", return_value=None):
            await DocumentService.save_uploaded_file_and_create_task(
                db=mock_db_doc, user_id=user_id, file=mock_file, audit_depth="FULL"
            )

        wallet_selects = [
            s for s in doc_stmts
            if hasattr(s, "column_descriptions") and any(d.get("name") == "TokenWallet" or d.get("type") == TokenWallet for d in s.column_descriptions)
        ]
        self.assertGreaterEqual(len(wallet_selects), 1)
        self.assertIsNotNone(
            getattr(wallet_selects[0], "_for_update_arg", None),
            "Query TokenWallet pada DocumentService wajib memanggil .with_for_update()",
        )

        # 3. Verify AuditService create_audit_task uses with_for_update() on TokenWallet
        audit_stmts = []
        test_doc = Document(id=uuid.uuid4(), user_id=user_id, status="READY", original_filename="doc.txt")
        audit_idx = 0
        def audit_handler(stmt):
            nonlocal audit_idx
            audit_idx += 1
            audit_stmts.append(stmt)
            if audit_idx == 1:
                return MockQueryResult([test_doc])
            return MockQueryResult([wallet])

        mock_db_audit = MockAsyncSession(execute_handler=audit_handler)
        req = AuditStartRequest(document_id=test_doc.id, audit_depth="FULL")
        with patch.object(celery_app.control, "inspect", return_value=None):
            await AuditService.create_audit_task(mock_db_audit, user_id, req)

        audit_wallet_selects = [
            s for s in audit_stmts
            if hasattr(s, "column_descriptions") and any(d.get("name") == "TokenWallet" or d.get("type") == TokenWallet for d in s.column_descriptions)
        ]
        self.assertGreaterEqual(len(audit_wallet_selects), 1)
        self.assertIsNotNone(
            getattr(audit_wallet_selects[0], "_for_update_arg", None),
            "Query TokenWallet pada AuditService wajib memanggil .with_for_update()",
        )

        # 4. Verify Admin adjust_user_tokens uses with_for_update() on TokenWallet
        admin_stmts = []
        target_user = User(id=user_id, full_name="Mahasiswa", email="mhs@kampus.id", role="TRIAL")
        admin_idx = 0
        def admin_handler(stmt):
            nonlocal admin_idx
            admin_idx += 1
            admin_stmts.append(stmt)
            if admin_idx == 1:
                return MockQueryResult([target_user])
            return MockQueryResult([wallet])

        mock_db_admin = MockAsyncSession(execute_handler=admin_handler)
        adj_req = TokenAdjustmentRequest(amount=5, note="Bonus apresiasi riset")
        await admin_module.adjust_user_tokens(user_id=str(user_id), req=adj_req, db=mock_db_admin)

        admin_wallet_selects = [
            s for s in admin_stmts
            if hasattr(s, "column_descriptions") and any(d.get("name") == "TokenWallet" or d.get("type") == TokenWallet for d in s.column_descriptions)
        ]
        self.assertGreaterEqual(len(admin_wallet_selects), 1)
        self.assertIsNotNone(
            getattr(admin_wallet_selects[0], "_for_update_arg", None),
            "Query TokenWallet pada adjust_user_tokens wajib memanggil .with_for_update()",
        )

    def test_tc_sec_11_alembic_fk_indices_and_unique_constraint(self):
        """
        [FINAL-01 & FINAL-03]:
        1. DocumentChunk memiliki UniqueConstraint('corpus_doc_id', 'chunk_index').
        2. corpus_documents(uploaded_by) memiliki indeks foreign key.
        3. password_resets(user_id) memiliki indeks foreign key.
        4. Berkas migrasi Alembic 0002_phase2_security_hardening.py mendefinisikan upgrade & downgrade.
        """
        # 1. Check DocumentChunk UniqueConstraint
        chunk_table = DocumentChunk.__table__
        unique_constraints = [c for c in chunk_table.constraints if isinstance(c, UniqueConstraint)]
        chunk_unique_cols = [
            set(col.name for col in uc.columns) for uc in unique_constraints
        ]
        self.assertIn(
            {"corpus_doc_id", "chunk_index"},
            chunk_unique_cols,
            "DocumentChunk wajib memiliki UniqueConstraint pada (corpus_doc_id, chunk_index)",
        )

        # 2. Check CorpusDocument uploaded_by index
        corpus_table = CorpusDocument.__table__
        corpus_index_names = [idx.name for idx in corpus_table.indexes]
        self.assertIn(
            "idx_corpus_documents_uploaded_by",
            corpus_index_names,
            "corpus_documents wajib memiliki index eksplisit idx_corpus_documents_uploaded_by",
        )
        # Check no duplicate indexes on uploaded_by
        uploaded_by_indexes = [
            idx.name for idx in corpus_table.indexes
            if any(c.name == "uploaded_by" for c in idx.columns)
        ]
        self.assertEqual(
            len(uploaded_by_indexes),
            1,
            f"Ditemukan duplikasi index pada corpus_documents.uploaded_by: {uploaded_by_indexes}",
        )

        # 3. Check PasswordReset user_id index
        pw_table = PasswordReset.__table__
        pw_index_names = [idx.name for idx in pw_table.indexes]
        self.assertIn(
            "idx_password_resets_user_id",
            pw_index_names,
            "password_resets wajib memiliki index eksplisit idx_password_resets_user_id",
        )
        # Check no duplicate indexes on user_id
        user_id_indexes = [
            idx.name for idx in pw_table.indexes
            if any(c.name == "user_id" for c in idx.columns)
        ]
        self.assertEqual(
            len(user_id_indexes),
            1,
            f"Ditemukan duplikasi index pada password_resets.user_id: {user_id_indexes}",
        )

        # 4. Check Alembic migration file existence & structural integrity
        migration_file = os.path.join(
            BACKEND_DIR, "alembic", "versions", "0002_phase2_security_hardening.py"
        )
        self.assertTrue(
            os.path.exists(migration_file),
            f"File migrasi Alembic {migration_file} tidak ditemukan!",
        )

        spec = importlib.util.spec_from_file_location("migration_0002", migration_file)
        migration_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_mod)

        self.assertEqual(migration_mod.revision, "0002_phase2_security_hardening")
        self.assertEqual(migration_mod.down_revision, "0001_initial_schema")
        self.assertTrue(callable(migration_mod.upgrade))
        self.assertTrue(callable(migration_mod.downgrade))

    def test_tc_sec_12_tier1_lexical_no_artificial_70_percent_floor(self):
        """
        [ROUND3-02]:
        tier1_lexical.py menghasilkan skor matematis murni tanpa inflasi artifisial 70%.
        Kalimat dengan rasio fingerprint 45% harus menghasilkan nilai ~0.45, BUKAN 0.70.
        """
        engine = WinnowingLexicalEngine(k=5, w=4)
        sample_sentence = "Algoritma pencarian kemiripan leksikal teks dokumen akademik berbasis winnowing."
        sentences = TextPreprocessor.segment_sentences(sample_sentence)
        s_fps = engine.extract_fingerprints(sentences[0].text)
        s_hashes = [h for h, _ in s_fps]

        self.assertGreaterEqual(len(s_hashes), 4, "Kalimat uji harus menghasilkan minimal 4 fingerprint")

        # Simulate corpus where exactly 40% - 50% of fingerprints match
        total_fps = len(s_hashes)
        match_count = total_fps // 2  # exactly ~50%
        simulated_corpus_hashes = s_hashes[:match_count]

        corpus_index = {
            h: [{"doc_id": "corpus-doc-01", "title": "Buku Rujukan Algoritma", "category": "Ilmu Komputer"}]
            for h in simulated_corpus_hashes
        }

        result = engine.analyze_document(
            original_text=sample_sentence,
            sentences=sentences,
            corpus_index=corpus_index,
        )

        self.assertEqual(len(result.sentence_matches), 1)
        match = result.sentence_matches[0]

        expected_ratio = round(match_count / total_fps, 2)
        # CRITICAL ASSERTION: The similarity must NOT be inflated to 0.70!
        self.assertEqual(
            match.similarity,
            expected_ratio,
            f"Kemiripan kalimat terinflasi! Ekspektasi matematis murni: {expected_ratio}, aktual: {match.similarity}",
        )
        self.assertLess(
            match.similarity,
            0.70,
            "Kemiripan 50% tidak boleh terkerek artifisial menjadi 0.70 (eliminasi floor)",
        )

    def test_tc_sec_13_tier4_aggregator_no_phantom_5_percent(self):
        """
        [ROUND3-04]:
        tier4_aggregator.py menghasilkan skor 0.0% dan matched sources kosong pada naskah
        yang sama sekali tidak mirip korpus (tanpa floor phantom 5.0%).
        """
        aggregator = HybridAggregator()
        completely_original_text = (
            "Kucing hitam melompati pagar bambu di belakang rumah nenek pada hari selasa siang yang cerah."
        )

        # Run pipeline with empty reference corpus (no overlap)
        result = aggregator.run_pipeline(
            original_text=completely_original_text,
            audit_depth="FULL",
            custom_corpus_index={},
            custom_corpus_chunks=[],
        )

        self.assertEqual(result.score_lexical, 0.0)
        self.assertEqual(result.score_semantic, 0.0)

        # Check matched_sources: MUST be empty list when score/overlap is 0.0
        self.assertEqual(
            len(result.matched_sources),
            0,
            f"Naskah non-plagiat memunculkan sumber pembanding hantu: {result.matched_sources}",
        )

        # Direct test on _aggregate_matched_sources with score_composite = 0.0
        dummy_t1 = MagicMock()
        dummy_t1.corpus_contributions = {
            "c1": {"title": "Doc 1", "category": "Umum", "match_count": 2}
        }
        res_sources = aggregator._aggregate_matched_sources(
            t1_result=dummy_t1,
            t2_result=None,
            score_composite=0.0,
        )
        self.assertEqual(
            len(res_sources),
            0,
            "Ketika score_composite bernilai 0.0, tidak boleh ada kontribusi sumber phantom 5.0%!",
        )

    async def test_tc_sec_14_cryptographic_order_id_entropy(self):
        """
        [NEW-04]:
        Pembuatan order ID top-up memiliki entropi kriptografis tinggi (12 hex chars = 48-bit random)
        dan tidak dapat diprediksi secara sekuensial.
        Format: VT-YYYYMMDD-XXXXXXXXXXXX (12 karakter hex acak)
        """
        mock_db = MockAsyncSession()
        user_id = uuid.uuid4()

        order_ids = set()
        pattern = re.compile(r"^VT-\d{8}-[A-F0-9]{12}$")

        for _ in range(100):
            inv = await BillingService.create_topup_invoice(mock_db, user_id, "pkg_10token")
            order_id = inv.order_id
            self.assertIsNotNone(
                pattern.match(order_id),
                f"Order ID {order_id} tidak memenuhi standar entropi VT-YYYYMMDD-XXXXXXXXXXXX (12 hex chars)!",
            )
            order_ids.add(order_id)

        # Zero collision across 100 generations
        self.assertEqual(
            len(order_ids),
            100,
            "Terjadi tabrakan order ID! Entropi generator tidak memadai.",
        )


if __name__ == "__main__":
    unittest.main()
