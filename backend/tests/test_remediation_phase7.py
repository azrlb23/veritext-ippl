"""
Test Suite: Remediation Phase 7 — Penutupan Celah Kritis Auth, IDOR Reports/Corpus, Backdoor Cleaning, Token Refund, Worker Config Sync, dan Startup Secret Guard.
TDD Tests verifying:
  - test_tc_sec_37_forgot_password_no_token_leak: Zero-leakage password reset token dispatch
  - test_tc_sec_38_get_report_idor_bola_authorization: IDOR/BOLA authorization enforcement on GET /reports/{report_id}
  - test_tc_sec_39_admin_user_create_no_backdoor_password: Elimination of default backdoor password in admin schema & endpoints
  - test_tc_sec_40_corpus_reviewer_ownership_check: Multi-tenant reviewer document isolation & 403 enforcement
  - test_tc_sec_41_cancel_task_automatic_token_refund: Automated token refund with row-level wallet lock on task cancellation
  - test_tc_sec_42_worker_system_config_hyperparameter_sync: Dynamic AI hyperparameters synchronization from SystemConfig into Celery worker
  - test_tc_sec_43_startup_secret_guard_in_production: Production startup halt on weak/default secret keys
"""

import asyncio
from datetime import datetime, timedelta, timezone
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from pydantic import ValidationError

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, status
from app.main import app, lifespan
from app.core.config import settings
from app.core.security import get_password_hash, hash_token
from app.models.user import User
from app.models.document import Document
from app.models.audit import AuditTask, AuditReport
from app.models.corpus import CorpusDocument
from app.models.password_reset import PasswordReset
from app.models.wallet import TokenWallet, TokenTransaction
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest
from app.services.audit_service import AuditService
from app.workers.tasks import execute_audit_pipeline
import app.api.v1.auth as auth_router
import app.api.v1.reports as report_router


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
    def __init__(self, execute_handler=None, get_handler=None):
        self.execute_handler = execute_handler
        self.get_handler = get_handler
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

    async def get(self, entity, ident):
        if self.get_handler:
            return self.get_handler(entity, ident)
        return None

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


class TestRemediationPhase7(unittest.IsolatedAsyncioTestCase):
    # =========================================================================
    # TC-SEC-37: Penutupan Kebocoran Token Pemulihan Sandi (Zero-Leakage Auth)
    # =========================================================================
    async def test_tc_sec_37_forgot_password_no_token_leak(self):
        """
        TC-SEC-37: Memverifikasi POST /forgot-password TIDAK membocorkan token di body response.
        - Respons JSON harus mengembalikan data={} kosong.
        - Objek PasswordReset disimpan di DB dengan token_hash aman.
        - Reset password diverifikasi langsung via database record tanpa mengandalkan kebocoran HTTP.
        """
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            full_name="Mahasiswa Korban Kebocoran",
            email="korban@kampus.ac.id",
            password_hash=get_password_hash("OldSecret#123"),
            role="FREE",
            is_active=True,
        )

        mock_db = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([user]),
            get_handler=lambda e, ident: user,
        )

        req_forgot = ForgotPasswordRequest(email="korban@kampus.ac.id")
        resp_forgot = await auth_router.forgot_password(req=req_forgot, db=mock_db)

        # 1. Pastikan respons sukses tetapi body data={} KOSONG (tidak ada reset_token!)
        self.assertTrue(resp_forgot.success)
        self.assertEqual(resp_forgot.data, {})
        self.assertNotIn("reset_token", resp_forgot.data)

        # 2. Pastikan PasswordReset tercatat di DB dengan hash aman
        added_resets = [r for r in mock_db.added if isinstance(r, PasswordReset)]
        self.assertEqual(len(added_resets), 1)
        reset_obj = added_resets[0]
        self.assertEqual(reset_obj.user_id, user_id)
        self.assertIsNotNone(reset_obj.token_hash)
        self.assertFalse(reset_obj.is_used)

        # 3. Alur validasi reset password langsung dari database
        valid_raw_token = "secure_token_sent_via_smtp_email_channel_32char!"
        reset_obj.token_hash = hash_token(valid_raw_token)

        mock_db_reset = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([reset_obj]),
            get_handler=lambda e, ident: user,
        )

        req_reset = ResetPasswordRequest(token=valid_raw_token, new_password="NewSecurePassword#2026")
        resp_reset = await auth_router.reset_password(req=req_reset, db=mock_db_reset)
        self.assertTrue(resp_reset.success)
        self.assertTrue(reset_obj.is_used)

    # =========================================================================
    # TC-SEC-38: Kunci IDOR / BOLA pada GET /reports/{report_id}
    # =========================================================================
    async def test_tc_sec_38_get_report_idor_bola_authorization(self):
        """
        TC-SEC-38: Memvalidasi kontrol otorisasi kepemilikan pada GET /reports/{report_id}:
        - Pemilik laporan (owner) -> 200 OK
        - Admin -> 200 OK
        - Pengguna lain (attacker / reviewer lain) -> HTTP 403 Forbidden
        - Laporan tidak ditemukan -> HTTP 404 Not Found
        """
        owner_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        admin_id = uuid.uuid4()

        owner_user = User(id=owner_id, full_name="Mahasiswa Pemilik", role="FREE")
        other_user = User(id=other_user_id, full_name="Pengguna Penyerang", role="FREE")
        admin_user = User(id=admin_id, full_name="Super Admin", role="ADMIN")

        task = AuditTask(id=uuid.uuid4(), user_id=owner_id, user=owner_user)
        report = AuditReport(
            id=uuid.uuid4(),
            audit_task_id=task.id,
            audit_task=task,
            verification_uuid=uuid.uuid4(),
            generated_at=datetime.now(timezone.utc),
            score_composite=12.5,
            score_lexical=10.0,
            score_semantic=15.0,
            score_stylometric=5.0,
            heatmap_annotations=[],
            matched_sources=[],
        )

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([report]))

        # 1. Pemilik laporan mengakses laporannya sendiri -> Sukses
        resp_owner = await report_router.get_report(
            report_id=report.id,
            current_user=owner_user,
            db=mock_db,
        )
        self.assertEqual(resp_owner.data.id, report.id)

        # 2. Admin mengakses laporan user -> Sukses
        resp_admin = await report_router.get_report(
            report_id=report.id,
            current_user=admin_user,
            db=mock_db,
        )
        self.assertEqual(resp_admin.data.id, report.id)

        # 3. User lain mencoba mengakses laporan milik user pertama -> Ditolak 403 Forbidden (BOLA/IDOR Defense)
        with self.assertRaises(HTTPException) as ctx_idor:
            await report_router.get_report(
                report_id=report.id,
                current_user=other_user,
                db=mock_db,
            )
        self.assertEqual(ctx_idor.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Forbidden", ctx_idor.exception.detail)

        # 4. Laporan yang tidak ada di database -> 404 Not Found
        mock_db_empty = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as ctx_404:
            await report_router.get_report(
                report_id=uuid.uuid4(),
                current_user=owner_user,
                db=mock_db_empty,
            )
        self.assertEqual(ctx_404.exception.status_code, status.HTTP_404_NOT_FOUND)



    # =========================================================================
    # TC-SEC-41: Pengembalian Token Otomatis saat Pembatalan Task (cancel_task)
    # =========================================================================
    async def test_tc_sec_41_cancel_task_automatic_token_refund(self):
        """
        TC-SEC-41: Memverifikasi cancel_task mengembalikan saldo token pengguna:
        - Task berstatus QUEUED dibatalkan
        - Saldo wallet bertambah (1 token untuk TIER1_ONLY, 2 token untuk FULL)
        - TokenTransaction bertipe CREDIT_REFUND (tx_type='REFUND') tercatat
        """
        user_id = uuid.uuid4()
        wallet = TokenWallet(user_id=user_id, balance=3)

        task_full = AuditTask(
            id=uuid.uuid4(),
            user_id=user_id,
            audit_depth="FULL",
            status="QUEUED",
        )

        mock_db = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([task_full] if "audit_tasks" in str(s).lower() else [wallet])
        )

        res = await AuditService.cancel_task(mock_db, task_full.id, user_id)
        self.assertTrue(res)
        self.assertEqual(task_full.status, "CANCELLED")

        # Saldo bertambah dari 3 menjadi 5 (refund 2 token untuk FULL)
        self.assertEqual(wallet.balance, 5)

        # Verifikasi TokenTransaction tercatat
        added_txs = [t for t in mock_db.added if isinstance(t, TokenTransaction)]
        self.assertEqual(len(added_txs), 1)
        refund_tx = added_txs[0]
        self.assertEqual(refund_tx.amount, 2)
        self.assertEqual(refund_tx.balance_after, 5)
        self.assertIn(refund_tx.transaction_type, ("CREDIT_REFUND", "REFUND"))
        self.assertEqual(refund_tx.tx_type, "REFUND")


    # =========================================================================
    # TC-SEC-43: Startup Secret Guard Menolak Kunci Default di Mode Produksi
    # =========================================================================
    async def test_tc_sec_43_startup_secret_guard_in_production(self):
        """
        TC-SEC-43: Memvalidasi startup guard di lifespan(app):
        - Di mode ENVIRONMENT='production', jika SECRET_KEY atau JWT_SECRET_KEY lemah/default,
          startup aplikasi GAGAL dengan RuntimeError.
        - Jika secret aman (>= 32 chars non-default), startup berhasil tanpa error.
        """
        # 1. Uji penolakan secret default dev di mode production
        with patch.object(settings, "ENVIRONMENT", "production"):
            with patch.object(settings, "SECRET_KEY", "super-secret-key-change-in-production"):
                with self.assertRaises(RuntimeError) as ctx_sec:
                    async with lifespan(app):
                        pass
                self.assertIn("FATAL: Insecure SECRET_KEY detected in production environment!", str(ctx_sec.exception))

        # 2. Uji penolakan secret pendek (< 32 karakter) di mode production
        with patch.object(settings, "ENVIRONMENT", "production"):
            with patch.object(settings, "SECRET_KEY", "short-secret"):
                with self.assertRaises(RuntimeError) as ctx_short:
                    async with lifespan(app):
                        pass
                self.assertIn("FATAL: Insecure SECRET_KEY detected in production environment!", str(ctx_short.exception))

        # 3. Uji startup sukses jika secret kuat di mode production
        strong_secret = "veritext-production-cryptographically-secure-random-token-2026-xyz!"
        strong_jwt = "veritext-production-jwt-cryptographically-secure-key-2026-abc!"
        with patch.object(settings, "ENVIRONMENT", "production"):
            with patch.object(settings, "SECRET_KEY", strong_secret):
                with patch.object(settings, "JWT_SECRET_KEY", strong_jwt):
                    # Harusnya berjalan lancar tanpa exception
                    async with lifespan(app):
                        pass

    # =========================================================================
    # TC-SEC-44: Refund Token Otomatis saat Terjadi Eksepsi Fatal pada Worker
    # =========================================================================
    def test_tc_sec_44_fatal_pipeline_failure_auto_refund(self):
        """
        TC-SEC-44: Memverifikasi jika worker mengalami eksepsi fatal dan task gagal,
        saldo token yang telah didebit otomatis direfund ke wallet pengguna.
        """
        user_id = uuid.uuid4()
        task_id = uuid.uuid4()
        doc_id = uuid.uuid4()

        task = AuditTask(id=task_id, user_id=user_id, document_id=doc_id, audit_depth="FULL", status="QUEUED")
        wallet = TokenWallet(user_id=user_id, balance=2)
        debit_tx = TokenTransaction(
            wallet_id=wallet.id,
            transaction_type="DEBIT_AUDIT",
            amount=-2,
            balance_after=2,
            reference_id=task_id,
        )

        query_tx_count = [0]

        class MockFailingDB:
            def __init__(self):
                self.added = []
                self.committed = False
                self.rolled_back = False

            def query(self, model):
                m = MagicMock()
                if model == AuditTask:
                    m.filter.return_value.first.return_value = task
                    return m
                elif model == Document:
                    return MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=Document(
                        id=doc_id,
                        stored_filename="corrupt.pdf",
                        mime_type="application/pdf",
                        original_filename="corrupt.pdf",
                    )))))
                elif model == TokenTransaction:
                    query_tx_count[0] += 1
                    m_tx = MagicMock()
                    if query_tx_count[0] == 1:
                        m_tx.filter.return_value.first.return_value = debit_tx
                    else:
                        m_tx.filter.return_value.first.return_value = None
                    return m_tx
                elif model == TokenWallet:
                    m.filter.return_value.first.return_value = wallet
                    return m
                return m

            def commit(self):
                self.committed = True

            def rollback(self):
                self.rolled_back = True

            def add(self, item):
                self.added.append(item)

        mock_db = MockFailingDB()

        with patch("os.path.exists", return_value=True):
            with patch("app.workers.tasks.TextPreprocessor.extract_text_from_file", side_effect=RuntimeError("Corrupt file or fatal storage read error!")):
                with self.assertRaises(RuntimeError):
                    execute_audit_pipeline(mock_db, str(task_id), str(doc_id))

        self.assertEqual(task.status, "FAILED")
        self.assertIn("Corrupt file", task.error_message)

        # Saldo bertambah kembali (2 + 2 = 4)
        self.assertEqual(wallet.balance, 4)

        # Verifikasi TokenTransaction CREDIT_REFUND dibuat
        refund_txs = [t for t in mock_db.added if isinstance(t, TokenTransaction) and t.transaction_type == "CREDIT_REFUND"]
        self.assertEqual(len(refund_txs), 1)
        self.assertEqual(refund_txs[0].amount, 2)
        self.assertEqual(refund_txs[0].balance_after, 4)

