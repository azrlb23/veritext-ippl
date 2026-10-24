"""
Test Suite: Remediation Phase 1 — Kritis, Backdoor, Autentikasi & Mitigasi DoS Gateway
TDD Tests verifying:
  - test_tc_sec_01_seed_backdoor_eliminated
  - test_tc_sec_02_export_pdf_requires_authentication_and_ownership
  - test_tc_sec_03_reportlab_html_escape_sanitization
  - test_tc_sec_04_no_inprocess_thread_hijacking_on_celery_offline
  - test_tc_sec_05_token_adjustment_integer_bounds
  - test_tc_sec_06_chunked_upload_file_size_exceeded_413
  - test_tc_sec_07_chunked_upload_multi_chunk_success
  - test_tc_sec_08_redis_url_authenticated_configuration
"""

import asyncio
from datetime import datetime, timezone
import hashlib
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.core.config import Settings, settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.document import Document
from app.models.audit import AuditTask, AuditReport
from app.models.wallet import TokenWallet
from app.schemas.auth import UserLoginRequest
from app.schemas.admin import TokenAdjustmentRequest, AdminUserCreateRequest
from app.schemas.audit import AuditStartRequest
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.services.document_service import DocumentService
from app.services.pdf_certificate_service import generate_pdf_certificate
from app.api.v1 import reports as report_router


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
        self.added = []
        self.deleted = []
        self.committed = False
        self.flushed = False

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

    async def execute(self, stmt):
        if self.execute_handler:
            return await self.execute_handler(stmt) if asyncio.iscoroutinefunction(self.execute_handler) else self.execute_handler(stmt)
        return MockQueryResult()

    async def get(self, model, ident):
        if self.get_handler:
            return await self.get_handler(model, ident) if asyncio.iscoroutinefunction(self.get_handler) else self.get_handler(model, ident)
        return None


class TestRemediationPhase1(unittest.IsolatedAsyncioTestCase):
    """Test suite memvalidasi remediations Fase 1."""

    async def test_tc_sec_01_seed_backdoor_eliminated(self):
        """
        [B2] Eliminasi Backdoor Seed di Layanan Autentikasi.
        - Mencoba login dengan kata sandi backdoor 'VeriText#2026' pada akun
          yang hash bcrypt-nya berbeda WAJIB gagal (HTTP 401).
        - Mencoba login dengan 'VeriText#2026' pada user yang belum ada di basis data
          TIDAK boleh meng-auto-create admin akun, melainkan WAJIB gagal (HTTP 401).
        - Login dengan password asli yang sesuai dengan bcrypt hash berhasil.
        """
        real_hash = get_password_hash("RealSecretPassword#2026!")
        user = User(
            id=uuid.uuid4(),
            full_name="Super Administrator VeriText",
            email="admin@veritext.ai",
            password_hash=real_hash,
            role="ADMIN",
            is_active=True,
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([user]))

        # 1. Attacker tries backdoor password 'VeriText#2026' on existing user -> 401
        req = UserLoginRequest(email="admin@veritext.ai", password="VeriText#2026")
        with self.assertRaises(HTTPException) as ctx:
            await AuthService.authenticate_user(mock_db, req)

        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid email or password", ctx.exception.detail)

        # 2. Attacker tries backdoor on azriel@kampus.ac.id -> 401
        user_azriel = User(
            id=uuid.uuid4(),
            full_name="Mochammad Azriel Albian Putra",
            email="azriel@kampus.ac.id",
            password_hash=real_hash,
            role="TRIAL",
            is_active=True,
        )
        mock_db_azriel = MockAsyncSession(execute_handler=lambda s: MockQueryResult([user_azriel]))
        req_azriel = UserLoginRequest(email="azriel@kampus.ac.id", password="VeriText#2026")
        with self.assertRaises(HTTPException) as ctx:
            await AuthService.authenticate_user(mock_db_azriel, req_azriel)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)

        # 3. Attacker tries backdoor on seed email when user does NOT exist in DB -> 401, NO auto-provisioning
        mock_db_empty = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        req_empty = UserLoginRequest(email="admin@veritext.ai", password="VeriText#2026")
        with self.assertRaises(HTTPException) as ctx:
            await AuthService.authenticate_user(mock_db_empty, req_empty)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(mock_db_empty.added), 0)

        # 4. Legitimate login with real secret password -> succeeds
        req_valid = UserLoginRequest(email="admin@veritext.ai", password="RealSecretPassword#2026!")
        auth_user, access_tok, refresh_tok = await AuthService.authenticate_user(mock_db, req_valid)
        self.assertEqual(auth_user.id, user.id)
        self.assertTrue(bool(access_tok))

    async def test_tc_sec_02_export_pdf_requires_authentication_and_ownership(self):
        """
        [A1 & A2] Otorisasi Ketat pada Export PDF.
        - Memanggil /reports/{id}/export-pdf tanpa Bearer token mengembalikan 401.
        - Memanggil dengan token user lain yang bukan pemilik dan bukan admin mengembalikan 403.
        - Parameter query ?token= diabaikan/ditolak.
        - Memanggil dengan pemilik atau admin mengembalikan PDF binary (200).
        """
        owner_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        admin_id = uuid.uuid4()

        owner_user = User(id=owner_id, full_name="Pemilik Naskah", email="owner@kampus.ac.id", role="TRIAL", institution="Institut Teknologi Nasional", is_active=True)
        other_user = User(id=other_user_id, full_name="User Asing", email="other@kampus.ac.id", role="TRIAL", is_active=True)
        admin_user = User(id=admin_id, full_name="Admin VeriText", email="admin@veritext.ai", role="ADMIN", is_active=True)

        doc = Document(id=uuid.uuid4(), user_id=owner_id, original_filename="Skripsi_Akhir.pdf")
        task = AuditTask(id=uuid.uuid4(), user_id=owner_id, document=doc, document_id=doc.id, user=owner_user)
        report_id = uuid.uuid4()
        report = AuditReport(
            id=report_id,
            audit_task=task,
            audit_task_id=task.id,
            verification_uuid=uuid.uuid4(),
            score_composite=12.5,
            score_lexical=10.0,
            score_semantic=15.0,
            score_stylometric=5.0,
            matched_sources=[],
            generated_at=datetime.now(timezone.utc),
        )

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([report]))

        # Direct call with other_user (not owner, not admin) -> MUST raise 403 Forbidden
        with self.assertRaises(HTTPException) as ctx:
            await report_router.export_pdf(report_id=report_id, current_user=other_user, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Forbidden", ctx.exception.detail)

        # Direct call with owner -> 200 OK binary
        resp_owner = await report_router.export_pdf(report_id=report_id, current_user=owner_user, db=mock_db)
        self.assertEqual(resp_owner.media_type, "application/pdf")
        self.assertTrue(resp_owner.body.startswith(b"%PDF-"))

        # Direct call with admin -> 200 OK binary
        resp_admin = await report_router.export_pdf(report_id=report_id, current_user=admin_user, db=mock_db)
        self.assertEqual(resp_admin.media_type, "application/pdf")
        self.assertTrue(resp_admin.body.startswith(b"%PDF-"))

        # HTTP Endpoint Integration Check via TestClient
        client = TestClient(app)

        # 1. Tanpa header Authorization -> 401
        res_no_auth = client.get(f"/api/v1/reports/{report_id}/export-pdf")
        self.assertEqual(res_no_auth.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Dengan query ?token= tanpa Bearer token -> Tetap 401 (token query parameter diabaikan/ditolak)
        fake_token = create_access_token(subject=str(owner_id), role="TRIAL")
        res_query_only = client.get(f"/api/v1/reports/{report_id}/export-pdf?token={fake_token}")
        self.assertEqual(res_query_only.status_code, status.HTTP_401_UNAUTHORIZED)

        # 3. HTTP Integration dengan user lain (bukan owner & bukan admin) -> 403 Forbidden
        app.dependency_overrides[get_current_user] = lambda: other_user
        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            res_forbidden = client.get(
                f"/api/v1/reports/{report_id}/export-pdf",
                headers={"Authorization": f"Bearer {fake_token}"},
            )
            self.assertEqual(res_forbidden.status_code, status.HTTP_403_FORBIDDEN)

            # 4. HTTP Integration dengan owner -> 200 OK
            app.dependency_overrides[get_current_user] = lambda: owner_user
            res_allowed = client.get(
                f"/api/v1/reports/{report_id}/export-pdf",
                headers={"Authorization": f"Bearer {fake_token}"},
            )
            self.assertEqual(res_allowed.status_code, status.HTTP_200_OK)
            self.assertEqual(res_allowed.headers["content-type"], "application/pdf")
            self.assertTrue(res_allowed.content.startswith(b"%PDF-"))
        finally:
            app.dependency_overrides.pop(get_current_user, None)
            app.dependency_overrides.pop(get_db, None)

    def test_tc_sec_03_reportlab_html_escape_sanitization(self):
        """
        [F1, NEW-03 & NEW-REV-01] Sanitasi ReportLab PDF & Dinamisasi URL.
        Memastikan input berbahaya (XSS / malformed XML) di-escape dan tidak memicu crash.
        """
        malicious_title = "<script>alert('XSS')</script><b>Judul Naskah & Riset</b><font color='red'>Malicious</font>"
        malicious_author = "John Doe <script>evil()</script> & Son"
        malicious_institution = "Institut Teknologi <img src=x onerror=alert(1)>"
        malicious_sources = [
            {"source_title": "<unclosed tag='foo'> & Research Paper 2026", "similarity": 0.45, "tier": "T1"}
        ]

        # Should render valid PDF without raising reportlab.lib.styles.Paragraph or XML parsing errors
        pdf_bytes = generate_pdf_certificate(
            report_id=str(uuid.uuid4()),
            verification_uuid=str(uuid.uuid4()),
            document_title=malicious_title,
            user_name=malicious_author,
            institution=malicious_institution,
            generated_at=datetime.now(timezone.utc),
            score_composite=20.0,
            score_lexical=15.0,
            score_semantic=25.0,
            score_stylometric=10.0,
            matched_sources=malicious_sources,
            verify_base_url=settings.FRONTEND_URL.rstrip("/"),
        )

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    async def test_tc_sec_04_no_inprocess_thread_hijacking_on_celery_offline(self):
        """
        [NEW-REV-07 & FINAL-REV-04] Eliminasi In-Process Threading Fallback.
        Memastikan baik save_uploaded_file_and_create_task MAUPUN create_audit_task
        TIDAK memanggil threading.Thread jika Celery offline / ping gagal / delay melempar error.
        """
        user_id = uuid.uuid4()
        wallet = TokenWallet(user_id=user_id, balance=10)

        # 1. DocumentService.save_uploaded_file_and_create_task
        mock_file = AsyncMock()
        mock_file.filename = "research_paper.pdf"
        mock_file.read.return_value = b"konten valid untuk pengujian TDD eliminasi threading"
        mock_file.content_type = "application/pdf"

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([wallet]))

        from app.workers.celery_app import celery_app
        with patch.object(celery_app.control, "inspect", return_value=None), \
             patch("threading.Thread") as mock_thread:
            uploaded_doc, task = await DocumentService.save_uploaded_file_and_create_task(
                db=mock_db, user_id=user_id, file=mock_file, audit_depth="FULL"
            )

            # Verification: threading.Thread MUST NOT be called!
            mock_thread.assert_not_called()
            self.assertEqual(task.status, "QUEUED")

        # Cleanup created upload file if exists
        fpath = os.path.join(settings.UPLOAD_DIR, uploaded_doc.stored_filename)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except OSError:
                pass

        # 2. AuditService.create_audit_task must ALSO NOT spawn threading.Thread!
        doc_id = uuid.uuid4()
        doc = Document(id=doc_id, user_id=user_id, original_filename="existing_doc.pdf")

        def exec_handler(s):
            s_str = str(s)
            if "documents" in s_str:
                return MockQueryResult([doc])
            return MockQueryResult([wallet])

        mock_db_audit = MockAsyncSession(execute_handler=exec_handler)
        req_start = AuditStartRequest(document_id=doc_id, audit_depth="FULL")

        with patch("app.workers.tasks.preprocess_and_audit.delay", side_effect=Exception("Redis down")), \
             patch("threading.Thread") as mock_thread_audit:
            audit_task = await AuditService.create_audit_task(mock_db_audit, user_id, req_start)
            mock_thread_audit.assert_not_called()
            self.assertEqual(audit_task.status, "QUEUED")

    def test_tc_sec_05_token_adjustment_integer_bounds(self):
        """
        [ROUND7-03 & FINAL-05] Batasan Numerik Token.
        Schema TokenAdjustmentRequest menolak nilai integer di luar [-1_000_000, 1_000_000].
        """
        # Exceeds maximum 1,000,000
        with self.assertRaises(ValidationError):
            TokenAdjustmentRequest(amount=1_000_001, note="Valid note but too high")

        # Below minimum -1,000,000
        with self.assertRaises(ValidationError):
            TokenAdjustmentRequest(amount=-1_000_001, note="Valid note but too negative")

        # Boundaries MUST pass
        req_max = TokenAdjustmentRequest(amount=1_000_000, note="Boundary max")
        self.assertEqual(req_max.amount, 1_000_000)

        req_min = TokenAdjustmentRequest(amount=-1_000_000, note="Boundary min")
        self.assertEqual(req_min.amount, -1_000_000)

        req_zero = TokenAdjustmentRequest(amount=0, note="Boundary zero")
        self.assertEqual(req_zero.amount, 0)

        # AdminUserCreateRequest initial_tokens bounds: 0 <= initial_tokens <= 1_000_000
        with self.assertRaises(ValidationError):
            AdminUserCreateRequest(
                full_name="Overflow Admin",
                email="overflow@example.com",
                initial_tokens=1_000_001,
            )

        with self.assertRaises(ValidationError):
            AdminUserCreateRequest(
                full_name="Negative Admin",
                email="negative@example.com",
                initial_tokens=-1,
            )

    async def test_tc_sec_06_chunked_upload_file_size_exceeded_413(self):
        """
        [ROUND7-03] Pengerasan Buffer Unggahan Berkas.
        Memastikan streaming upload chunked 64KB segera menolak berkas yang melebihi
        MAX_FILE_SIZE_MB dengan HTTP 413 dan membersihkan berkas parsial dari disk.
        """
        user_id = uuid.uuid4()
        mock_db = MockAsyncSession()

        # Simulate upload larger than MAX_FILE_SIZE_MB
        # We will patch MAX_FILE_SIZE_MB to 1 MB for fast deterministic test
        chunk_64k = b"A" * (64 * 1024)
        chunks = [chunk_64k] * 20  # 20 * 64KB = 1.28MB (> 1MB)
        chunks.append(b"")

        mock_file = AsyncMock()
        mock_file.filename = "large_thesis.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(side_effect=chunks)

        with patch.object(settings, "MAX_FILE_SIZE_MB", 1):
            with self.assertRaises(HTTPException) as ctx:
                await DocumentService.save_uploaded_file(mock_db, user_id, mock_file)

            self.assertEqual(ctx.exception.status_code, status.HTTP_413_CONTENT_TOO_LARGE)
            self.assertIn("exceeds maximum allowed size", ctx.exception.detail)

    async def test_tc_sec_07_chunked_upload_multi_chunk_success(self):
        """
        [ROUND7-03] Pengerasan Buffer Unggahan Berkas.
        Memastikan berkas multi-chunk (> 64KB) berhasil dibaca secara bertahap,
        disimpan utuh ke disk, dan hash SHA-256 terhitung akurat.
        """
        user_id = uuid.uuid4()
        mock_db = MockAsyncSession()

        chunk1 = b"B" * (64 * 1024)
        chunk2 = b"C" * (64 * 1024)
        chunk3 = b"D" * (10 * 1024)
        full_content = chunk1 + chunk2 + chunk3
        expected_hash = hashlib.sha256(full_content).hexdigest()

        mock_file = AsyncMock()
        mock_file.filename = "valid_paper.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(side_effect=[chunk1, chunk2, chunk3, b""])

        doc = await DocumentService.save_uploaded_file(mock_db, user_id, mock_file)
        self.assertEqual(doc.file_size_bytes, len(full_content))
        self.assertEqual(doc.sha256_hash, expected_hash)

        # Cleanup created upload file
        fpath = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
        self.assertTrue(os.path.exists(fpath))
        os.remove(fpath)

    def test_tc_sec_08_redis_url_authenticated_configuration(self):
        """
        [A4, NEW-05 & FINAL-14] Pengerasan Jaringan & Konfigurasi Kontainer.
        Memastikan Settings menyusun REDIS_URL dan CELERY_BROKER_URL dengan kredensial
        autentikasi password saat REDIS_PASSWORD disetel.
        """
        cfg = Settings(
            REDIS_HOST="10.0.0.5",
            REDIS_PORT=6380,
            REDIS_PASSWORD="SuperSecretRedisPass2026",
            REDIS_DB=2,
            REDIS_URL=None,
            CELERY_BROKER_URL=None,
            CELERY_RESULT_BACKEND=None,
        )
        expected_url = "redis://:SuperSecretRedisPass2026@10.0.0.5:6380/2"
        self.assertEqual(cfg.REDIS_URL, expected_url)
        self.assertEqual(cfg.CELERY_BROKER_URL, expected_url)
        self.assertEqual(cfg.CELERY_RESULT_BACKEND, expected_url)
