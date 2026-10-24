"""
Test Suite: Remediation Phase 3 — Kepatuhan Hukum UU PDP No. 27/2022 & Pembersihan Berkas Nyata
TDD Tests verifying:
  - test_tc_sec_15_physical_file_deletion_on_document_delete
  - test_tc_sec_16_corpus_cascade_cleanup_on_delete
  - test_tc_sec_17_self_account_deletion_endpoint
  - test_tc_sec_18_block_audit_on_deleted_document
  - test_tc_sec_19_audit_log_non_repudiation_actor_recording
  - test_tc_sec_20_admin_self_lockout_protection
  - test_tc_sec_21_admin_user_deletion_no_foreign_key_violation_500
  - test_tc_sec_22_csv_formula_injection_sanitization
"""

import asyncio
from datetime import datetime, timezone
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import delete, func, select, update

from app.core.config import settings
from app.core.database import get_db
from app.core.security import sanitize_csv_formula
from app.models.audit import AuditReport, AuditSentence, AuditTask
from app.models.audit_log import AuditLog
from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
from app.models.document import Document
from app.models.invoice import Invoice
from app.models.session import Session
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.admin import AdminUserUpdateRequest, UserStatusUpdateRequest
from app.schemas.audit import AuditStartRequest
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.corpus_service import CorpusService
from app.services.document_service import DocumentService
from app.api.v1 import admin as admin_router
from app.api.v1 import audits as audits_router
from app.api.v1 import auth as auth_router
from app.api.v1 import corpus as corpus_router
from app.api.v1 import documents as doc_router


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

    async def get(self, entity, ident):
        if self.execute_handler:
            res = self.execute_handler(f"GET_{entity.__name__}_{ident}")
            if res is not None:
                if isinstance(res, MockQueryResult):
                    return res.scalar_one_or_none()
                return res
        return None


class TestRemediationPhase3TDD(unittest.IsolatedAsyncioTestCase):
    """Fase 3 Test-Driven Verification Suite: UU PDP No. 27/2022 & Pembersihan Berkas Nyata."""

    def setUp(self):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        self.temp_files = []

    def tearDown(self):
        for fpath in self.temp_files:
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass

    def _create_temp_upload_file(self, prefix: str = "test_doc") -> tuple[str, str]:
        filename = f"{prefix}_{uuid.uuid4().hex}.pdf"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(b"%PDF-1.4 Mock sensitive academic manuscript content")
        self.temp_files.append(file_path)
        return filename, file_path

    async def test_tc_sec_15_physical_file_deletion_on_document_delete(self):
        """
        [E1 & ROUND3-08]:
        1. DELETE /api/v1/documents/{id} menghapus fisik berkas riil di disk (os.remove()).
        2. Status dokumen di database diperbarui menjadi 'DELETED' dan deleted_at diisi timestamp UTC.
        3. Berkas fisik benar-benar terhapus dari filesystem server (kepatuhan UU PDP No. 27/2022 Pasal 40 & 43).
        4. Request dokumen tidak ditemukan menghasilkan HTTP 404.
        """
        stored_filename, file_path = self._create_temp_upload_file("user_paper")
        self.assertTrue(os.path.exists(file_path), "File fisik harus ada sebelum penghapusan")

        user = User(id=uuid.uuid4(), email="student@univ.ac.id", role="USER")
        doc = Document(
            id=uuid.uuid4(),
            user_id=user.id,
            original_filename="skripsi_rahasia.pdf",
            stored_filename=stored_filename,
            file_size_bytes=1024,
            mime_type="application/pdf",
            status="READY",
            deleted_at=None,
        )

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([doc]))

        # Panggil endpoint DELETE /api/v1/documents/{id}
        resp = await doc_router.delete_document(doc_id=doc.id, current_user=user, db=mock_db)

        # Verifikasi fisik berkas telah dihapus dari disk
        self.assertFalse(
            os.path.exists(file_path),
            "Pelanggaran UU PDP E1/ROUND3-08: Berkas naskah fisik masih tertinggal di filesystem server!",
        )

        # Verifikasi status logis database
        self.assertEqual(doc.status, "DELETED")
        self.assertIsNotNone(doc.deleted_at)
        self.assertTrue(mock_db.committed)
        self.assertIn("UU PDP", resp.message)

        # Sub-test: Non-existent document raises 404
        empty_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as ctx:
            await doc_router.delete_document(doc_id=uuid.uuid4(), current_user=user, db=empty_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_tc_sec_16_corpus_cascade_cleanup_on_delete(self):
        """
        [ROUND3-08]:
        1. Menghapus korpus via CorpusService.delete_corpus_doc menghapus rekaman anak
           DocumentChunk dan LexicalFingerprint di database.
        2. Berkas arsip fisik korpus di disk server juga dihapus.
        3. Status korpus diset menjadi 'DELETED'.
        """
        stored_filename, file_path = self._create_temp_upload_file("corpus_archive")
        self.assertTrue(os.path.exists(file_path))

        corpus_id = uuid.uuid4()
        corpus_doc = CorpusDocument(
            id=corpus_id,
            title="Arsip Skripsi 2024",
            stored_filename=stored_filename,
            status="INDEXED",
        )

        executed_stmts = []

        def exec_handler(stmt):
            executed_stmts.append(stmt)
            # When selecting the corpus doc
            stmt_str = str(stmt).lower()
            if "select" in stmt_str and "corpus_documents" in stmt_str:
                return MockQueryResult([corpus_doc])
            return MockQueryResult([])

        mock_db = MockAsyncSession(execute_handler=exec_handler)

        res = await CorpusService.delete_corpus_doc(mock_db, corpus_id)
        self.assertTrue(res)

        # 1. Berkas fisik korpus di disk harus terhapus
        self.assertFalse(
            os.path.exists(file_path),
            "Residu fisik berkas arsip korpus masih tertinggal di disk setelah delete!",
        )

        # 2. Status diubah menjadi DELETED
        self.assertEqual(corpus_doc.status, "DELETED")
        self.assertTrue(mock_db.committed)

        # 3. Harus ada delete statement untuk DocumentChunk dan LexicalFingerprint
        chunk_deleted = False
        fingerprint_deleted = False
        for s in executed_stmts:
            s_str = str(s).lower()
            if "delete" in s_str and "document_chunks" in s_str:
                chunk_deleted = True
            if "delete" in s_str and "lexical_fingerprints" in s_str:
                fingerprint_deleted = True

        self.assertTrue(
            chunk_deleted,
            "DocumentChunk anak tidak dihapus saat korpus dihapus (vektor orphan di DB)",
        )
        self.assertTrue(
            fingerprint_deleted,
            "LexicalFingerprint anak tidak dihapus saat korpus dihapus (residu sidik jari di DB)",
        )

        # Sub-test: Non-existent corpus document raises HTTP 404
        empty_corpus_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as ctx_missing:
            await CorpusService.delete_corpus_doc(empty_corpus_db, uuid.uuid4())
        self.assertEqual(ctx_missing.exception.status_code, status.HTTP_404_NOT_FOUND)

        # Sub-test: Already deleted corpus document cannot be re-deleted and raises HTTP 404
        already_deleted_corpus = CorpusDocument(
            id=uuid.uuid4(),
            title="Arsip Terhapus",
            stored_filename="deleted_corpus.pdf",
            status="DELETED",
        )
        def exec_deleted_handler(stmt):
            s_str = str(stmt).lower()
            if "status != 'deleted'" in s_str or "status !=" in s_str:
                return MockQueryResult([])
            return MockQueryResult([already_deleted_corpus])

        deleted_corpus_db = MockAsyncSession(execute_handler=exec_deleted_handler)
        with self.assertRaises(HTTPException) as ctx_already_del:
            await CorpusService.delete_corpus_doc(deleted_corpus_db, already_deleted_corpus.id)
        self.assertEqual(ctx_already_del.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_tc_sec_17_self_account_deletion_endpoint(self):
        """
        [E2 & FINAL-08]:
        1. Endpoint DELETE /api/v1/auth/me tersedia bagi subjek data untuk menghapus akun mandiri (UU PDP Pasal 8).
        2. Membersihkan berkas fisik naskah di disk milik user tersebut.
        3. Menghapus rekaman Session, TokenWallet, dan TokenTransaction.
        4. Meng-anonymize jejak audit_logs (set actor_id = NULL) tanpa menghapus histori forensik.
        5. Menghapus entitas User.
        """
        stored1, path1 = self._create_temp_upload_file("user_paper_1")
        stored2, path2 = self._create_temp_upload_file("user_paper_2")

        user_id = uuid.uuid4()
        user = User(id=user_id, email="self_delete@univ.ac.id", role="USER", is_active=True)

        doc1 = Document(id=uuid.uuid4(), user_id=user_id, stored_filename=stored1)
        doc2 = Document(id=uuid.uuid4(), user_id=user_id, stored_filename=stored2)
        wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=5)

        executed_stmts = []

        def exec_handler(stmt):
            executed_stmts.append(stmt)
            s_str = str(stmt).lower()
            if "select" in s_str and "documents" in s_str:
                return MockQueryResult([doc1, doc2])
            if "select" in s_str and "token_wallets" in s_str:
                return MockQueryResult([wallet])
            if "select" in s_str and "audit_tasks" in s_str:
                return MockQueryResult([])
            return MockQueryResult([])

        mock_db = MockAsyncSession(execute_handler=exec_handler)

        mock_response = Response()
        api_resp = await auth_router.delete_own_account(
            response=mock_response, current_user=user, db=mock_db
        )

        # 1. Seluruh berkas fisik naskah milik user terhapus dari disk
        self.assertFalse(os.path.exists(path1), "Berkas naskah 1 fisik tidak terhapus pada hapus akun mandiri")
        self.assertFalse(os.path.exists(path2), "Berkas naskah 2 fisik tidak terhapus pada hapus akun mandiri")

        # 2. Entitas user dihapus
        self.assertIn(user, mock_db.deleted)
        self.assertTrue(mock_db.committed)

        # 3. Cookie refresh_token dihapus
        self.assertIn('refresh_token=""', mock_response.headers.get("set-cookie", ""))

        # 4. Verifikasi anonymization pada audit_logs (actor_id = NULL)
        audit_log_anonymized = False
        for s in executed_stmts:
            s_str = str(s).lower()
            if "update" in s_str and "audit_logs" in s_str:
                audit_log_anonymized = True
        self.assertTrue(audit_log_anonymized, "Jejak audit_logs tidak di-anonymize saat user dihapus")

    async def test_tc_sec_18_block_audit_on_deleted_document(self):
        """
        [NEW-REV-02]:
        1. Memastikan pembuatan AuditTask baru pada dokumen yang berstatus 'DELETED' ditolak dengan HTTP 400.
        2. Memastikan pembuatan AuditTask baru pada dokumen yang memiliki deleted_at ditolak dengan HTTP 400.
        """
        user_id = uuid.uuid4()
        deleted_doc = Document(
            id=uuid.uuid4(),
            user_id=user_id,
            stored_filename="old_deleted.pdf",
            status="DELETED",
            deleted_at=datetime.now(timezone.utc),
        )

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([deleted_doc]))

        req = AuditStartRequest(document_id=deleted_doc.id, audit_depth="FULL")

        with self.assertRaises(HTTPException) as ctx:
            await AuditService.create_audit_task(mock_db, user_id, req)

        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx.exception.detail, "Cannot audit a deleted document")

        # Sub-test: Dokumen status != 'DELETED' tetapi deleted_at is not None juga ditolak
        soft_deleted_doc = Document(
            id=uuid.uuid4(),
            user_id=user_id,
            stored_filename="old_ready_but_deleted.pdf",
            status="READY",
            deleted_at=datetime.now(timezone.utc),
        )
        mock_db2 = MockAsyncSession(execute_handler=lambda s: MockQueryResult([soft_deleted_doc]))
        with self.assertRaises(HTTPException) as ctx2:
            await AuditService.create_audit_task(mock_db2, user_id, req)
        self.assertEqual(ctx2.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx2.exception.detail, "Cannot audit a deleted document")

    async def test_tc_sec_19_audit_log_non_repudiation_actor_recording(self):
        """
        [NEW-REV-03 & FINAL-REV-05]:
        Pembersihan data retensi (/purge-retention) merekam identitas aktor riil
        (actor_id, actor_ip, actor_user_agent) pada tabel audit_logs dan bukan NULL.
        """
        admin = User(id=uuid.uuid4(), email="superadmin@univ.ac.id", role="ADMIN", is_active=True)

        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "203.0.113.42"
        mock_request.headers.get.side_effect = lambda h: "VeriText-Security-Inspector/3.0" if h.lower() == "user-agent" else None

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))

        resp = await admin_router.purge_retention_data(
            request=mock_request,
            retention_days=30,
            current_user=admin,
            db=mock_db,
        )

        # Periksa entri AuditLog yang ditambahkan ke database
        audit_log_entries = [item for item in mock_db.added if isinstance(item, AuditLog)]
        self.assertTrue(len(audit_log_entries) > 0, "AuditLog tidak dibuat pada operasi purge-retention")

        log = audit_log_entries[0]
        self.assertEqual(log.actor_id, admin.id, "Non-repudiation violation: actor_id masih bernilai NULL!")
        self.assertEqual(log.actor_ip, "203.0.113.42", "Non-repudiation violation: actor_ip masih bernilai NULL!")
        self.assertEqual(
            log.actor_user_agent,
            "VeriText-Security-Inspector/3.0",
            "Non-repudiation violation: actor_user_agent masih bernilai NULL!",
        )
        self.assertEqual(log.action_type, "DOCUMENT_PURGE")
        self.assertEqual(log.action_result, "SUCCESS")

    async def test_tc_sec_20_admin_self_lockout_protection(self):
        """
        [NEW-REV-04]:
        Penonaktifan atau penghapusan akun ditolak jika user tersebut adalah satu-satunya
        Super Admin aktif (mencegah permanent system lockout).
        """
        solo_admin = User(
            id=uuid.uuid4(),
            email="solo_admin@univ.ac.id",
            full_name="Solo Admin",
            role="ADMIN",
            is_active=True,
        )

        # 1 admin aktif di sistem
        def exec_handler_solo(stmt):
            s_str = str(stmt).lower()
            if "get_user" in s_str:
                return solo_admin
            if "count(" in s_str:
                return MockQueryResult(scalar_val=1)
            if "users" in s_str:
                return MockQueryResult([solo_admin])
            return MockQueryResult([])

        # Sub-test A: Penonaktifan admin terakhir ditolak dengan HTTP 400
        mock_db_deactivate = MockAsyncSession(execute_handler=exec_handler_solo)
        with self.assertRaises(HTTPException) as ctx_deact:
            await admin_router.update_user_status(
                user_id=str(solo_admin.id),
                req=UserStatusUpdateRequest(is_active=False),
                db=mock_db_deactivate,
            )
        self.assertEqual(ctx_deact.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx_deact.exception.detail, "Cannot deactivate or delete the last active administrator")

        # Sub-test B: Penghapusan admin terakhir via admin route ditolak dengan HTTP 400
        mock_db_del_admin = MockAsyncSession(execute_handler=exec_handler_solo)
        with self.assertRaises(HTTPException) as ctx_del_admin:
            await admin_router.delete_user_admin(
                user_id=str(solo_admin.id),
                db=mock_db_del_admin,
            )
        self.assertEqual(ctx_del_admin.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx_del_admin.exception.detail, "Cannot deactivate or delete the last active administrator")

        # Sub-test C: Penghapusan admin terakhir via self-delete /auth/me ditolak dengan HTTP 400
        mock_db_self_del = MockAsyncSession(execute_handler=exec_handler_solo)
        with self.assertRaises(HTTPException) as ctx_self:
            await auth_router.delete_own_account(
                response=Response(),
                current_user=solo_admin,
                db=mock_db_self_del,
            )
        self.assertEqual(ctx_self.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx_self.exception.detail, "Cannot deactivate or delete the last active administrator")

        # Sub-test D: Jika ada >= 2 admin aktif, deaktifasi atau penghapusan admin diperbolehkan
        def exec_handler_multi(stmt):
            s_str = str(stmt).lower()
            if "get_user" in s_str:
                return solo_admin
            if "count(" in s_str:
                return MockQueryResult(scalar_val=2)
            if "users" in s_str:
                return MockQueryResult([solo_admin])
            return MockQueryResult([])

        mock_db_allowed = MockAsyncSession(execute_handler=exec_handler_multi)
        resp = await admin_router.update_user_status(
            user_id=str(solo_admin.id),
            req=UserStatusUpdateRequest(is_active=False),
            db=mock_db_allowed,
        )
        self.assertFalse(solo_admin.is_active)
        self.assertTrue(mock_db_allowed.committed)

        # Reset solo_admin to active
        solo_admin.is_active = True
        solo_admin.role = "ADMIN"

        # Sub-test E: PUT /admin/users/{user_id} deactivating last admin is blocked
        mock_db_put_deact = MockAsyncSession(execute_handler=exec_handler_solo)
        with self.assertRaises(HTTPException) as ctx_put_deact:
            await admin_router.update_user_admin(
                user_id=str(solo_admin.id),
                req=AdminUserUpdateRequest(is_active=False),
                db=mock_db_put_deact,
            )
        self.assertEqual(ctx_put_deact.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx_put_deact.exception.detail, "Cannot deactivate or delete the last active administrator")

        # Sub-test F: PUT /admin/users/{user_id} demoting last admin role is blocked
        mock_db_put_demote = MockAsyncSession(execute_handler=exec_handler_solo)
        with self.assertRaises(HTTPException) as ctx_put_demote:
            await admin_router.update_user_admin(
                user_id=str(solo_admin.id),
                req=AdminUserUpdateRequest(role="USER"),
                db=mock_db_put_demote,
            )
        self.assertEqual(ctx_put_demote.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx_put_demote.exception.detail, "Cannot deactivate or delete the last active administrator")

    async def test_tc_sec_21_admin_user_deletion_no_foreign_key_violation_500(self):
        """
        [E2 & FINAL-08]:
        Penghapusan user oleh admin menangani cascading anonymization (mis. set actor_id = NULL
        di audit_logs) dan menghapus berkas fisik tanpa error FK constraint 500.
        """
        stored_f, path_f = self._create_temp_upload_file("target_user_file")
        self.assertTrue(os.path.exists(path_f))

        target_user = User(
            id=uuid.uuid4(),
            email="target_student@univ.ac.id",
            full_name="Target Student",
            role="USER",
            is_active=True,
        )

        doc = Document(id=uuid.uuid4(), user_id=target_user.id, stored_filename=stored_f)
        task = AuditTask(id=uuid.uuid4(), user_id=target_user.id, document_id=doc.id)
        wallet = TokenWallet(id=uuid.uuid4(), user_id=target_user.id, balance=10)

        executed_stmts = []

        def exec_handler(stmt):
            executed_stmts.append(stmt)
            s_str = str(stmt).lower()
            if "select" in s_str and "users" in s_str:
                return MockQueryResult([target_user])
            if "select" in s_str and "documents" in s_str:
                return MockQueryResult([doc])
            if "select" in s_str and "token_wallets" in s_str:
                return MockQueryResult([wallet])
            if "select" in s_str and "audit_tasks" in s_str:
                return MockQueryResult([task])
            return MockQueryResult([])

        mock_db = MockAsyncSession(execute_handler=exec_handler)

        resp = await admin_router.delete_user_admin(user_id=str(target_user.id), db=mock_db)

        # 1. Berkas fisik naskah user dihapus dari disk
        self.assertFalse(os.path.exists(path_f), "Berkas fisik tidak dihapus saat admin menghapus pengguna")

        # 2. User dihapus dari database
        self.assertIn(target_user, mock_db.deleted)
        self.assertTrue(mock_db.committed)

        # 3. Cascading anonymization dieksekusi pada audit_logs
        anonymized_audit = False
        anonymized_corpus = False
        for s in executed_stmts:
            s_str = str(s).lower()
            if "update" in s_str and "audit_logs" in s_str:
                anonymized_audit = True
            if "update" in s_str and "corpus_documents" in s_str:
                anonymized_corpus = True
        self.assertTrue(anonymized_audit, "AuditLog actor_id tidak di-anonymize ke NULL saat user dihapus oleh admin")
        self.assertTrue(anonymized_corpus, "CorpusDocument uploaded_by tidak di-anonymize ke NULL saat user dihapus oleh admin")

    async def test_tc_sec_22_csv_formula_injection_sanitization(self):
        """
        [ROUND4-06]:
        Sanitasi karakter formula injection (=, +, -, @, \\t, \\r) pada data sebelum ekspor CSV.
        Mencegah eksekusi ekspresi formula berbahaya di spreadsheet client (Excel / Calc).
        """
        dangerous_inputs = [
            ("=1+1", "'=1+1"),
            ("=cmd|' /C calc'!A0", "'=cmd|' /C calc'!A0"),
            ("+123456", "'+123456"),
            ("-SUM(A1:A10)", "'-SUM(A1:A10)"),
            ("@HYPERLINK(\"http://evil.com\")", "'@HYPERLINK(\"http://evil.com\")"),
            ("\tTAB_FORMULA", "'\tTAB_FORMULA"),
            ("\rCR_FORMULA", "'\rCR_FORMULA"),
            ("   =1+1", "'   =1+1"),
            ("  @SUM(A1:A10)", "'  @SUM(A1:A10)"),
            (" \t=cmd", "' \t=cmd"),
        ]

        for raw_val, expected_sanitized in dangerous_inputs:
            sanitized = sanitize_csv_formula(raw_val)
            self.assertEqual(
                sanitized,
                expected_sanitized,
                f"Formula injection gagal dimitigasi untuk input: {repr(raw_val)}",
            )
            # Karakter pertama harus single quote
            self.assertTrue(
                sanitized.startswith("'"),
                f"Hasil sanitasi harus diawali single quote: {sanitized}",
            )

        # Safe inputs should remain unaltered
        safe_inputs = [
            ("Laporan Integritas", "Laporan Integritas"),
            ("Dr. John Doe, M.Kom.", "Dr. John Doe, M.Kom."),
            ("100%", "100%"),
            ("Normal text 123", "Normal text 123"),
            (None, ""),
            ("", ""),
        ]
        for safe_val, expected in safe_inputs:
            self.assertEqual(sanitize_csv_formula(safe_val), expected)

        # Sub-test: Endpoint /history/export-csv sanitizes dangerous fields
        user = User(id=uuid.uuid4(), email="student@univ.ac.id", role="USER")
        malicious_task = AuditTask(
            id=uuid.uuid4(),
            user_id=user.id,
            document_id=uuid.uuid4(),
            audit_depth="FULL",
            status="=cmd|' /C calc'!A0",  # Injected status
            progress_pct=100,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([malicious_task]))
        csv_resp = await audits_router.export_audit_history_csv(current_user=user, db=mock_db)
        csv_content = csv_resp.body.decode("utf-8")

        # Status harus diawali dengan single quote
        self.assertNotIn("\n=cmd|", csv_content, "Formula injection lolos ke dalam payload berkas CSV!")
        self.assertIn("'=cmd|", csv_content, "Formula injection tidak di-escape dengan tanda kutip tunggal!")


if __name__ == "__main__":
    unittest.main()
