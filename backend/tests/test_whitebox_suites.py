"""
Matriks Pengujian Whitebox Otomatis VeriText AI
Mencakup 7 Fitur Utama Sistem dengan minimal 10 Test Case per Fitur.
Kategori Kasus: Happy Ending, Bad Case, dan Blocker.
Memverifikasi Statement Coverage, Branch Coverage, Condition Coverage, dan Boundary Value.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

# Pastikan path backend terdaftar
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.api.deps import get_current_user, require_role
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine
from app.engine.tier3_stylometric import StylometricEngine
from app.engine.tier4_aggregator import HybridAggregator
from app.engine.reference_corpus import ReferenceCorpusBank

from app.models.audit import AuditReport, AuditSentence, AuditTask
from app.models.audit_log import AuditLog
from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
from app.models.document import Document
from app.models.invoice import Invoice
from app.models.session import Session
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet

from app.schemas.admin import (
    AdminResetPasswordRequest,
    AdminUserCreateRequest,
    AdminUserUpdateRequest,
    TokenAdjustmentRequest,
)
from app.schemas.auth import (
    ChangePasswordRequest,
    UserLoginRequest,
    UserProfileUpdate,
    UserRegisterRequest,
)
from app.schemas.audit import AuditStartRequest
from app.schemas.billing import MidtransWebhookPayload
from app.schemas.corpus import CorpusDocUpdateRequest

from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.services.audit_service import AuditService
from app.services.billing_service import BillingService, PACKAGES
from app.services.corpus_service import CorpusService
from app.services.pdf_certificate_service import generate_pdf_certificate, clean_pdf_filename

import app.api.v1.auth as auth_router
import app.api.v1.documents as doc_router
import app.api.v1.reports as report_router
import app.api.v1.admin as admin_router


class MockQueryResult:
    """Mock pembantu untuk membungkus hasil eksekusi SQLAlchemy."""
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
    """Mock AsyncSession untuk pengujian whitebox isolasi logika bisnis database."""
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


# ===========================================================================
# FITUR 1: AUTENTIKASI PENGGUNA & MANAJEMEN SESI (TC-AUTH-001 s/d TC-AUTH-011)
# ===========================================================================
class TestWhiteboxFeature1Auth(unittest.IsolatedAsyncioTestCase):
    """Pengujian Whitebox Fitur 1: Autentikasi Pengguna & Manajemen Sesi."""

    async def test_tc_auth_001_register_user_happy_path(self):
        """TC-AUTH-001 [Happy Ending]: Registrasi user baru sukses, alokasi 5 trial token, dan sesi tersimpan."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        req = UserRegisterRequest(
            full_name="Azriel Albian",
            email="azriel.new@kampus.ac.id",
            password="SecurePassword123!",
            institution="Institut Teknologi Nasional",
        )
        user, access_token, refresh_token = await AuthService.register_user(mock_db, req)

        self.assertEqual(user.email, "azriel.new@kampus.ac.id")
        self.assertEqual(user.role, "TRIAL")
        self.assertTrue(user.is_active)
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)

        # Cek alokasi 5 token trial di wallet
        wallets = [x for x in mock_db.added if isinstance(x, TokenWallet)]
        self.assertEqual(len(wallets), 1)
        self.assertEqual(wallets[0].balance, 5)

        # Cek sesi tersimpan
        sessions = [x for x in mock_db.added if isinstance(x, Session)]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].refresh_token_hash, hash_token(refresh_token))

    async def test_tc_auth_002_login_valid_credentials_happy_path(self):
        """TC-AUTH-002 [Happy Ending]: Login dengan email & password valid mengembalikan JWT dan sesi."""
        pwd = "SecretPassword123!"
        hashed = get_password_hash(pwd)
        existing_user = User(
            id=uuid.uuid4(),
            full_name="Mahasiswa Uji",
            email="mhs@kampus.ac.id",
            password_hash=hashed,
            role="TRIAL",
            is_active=True,
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([existing_user]))
        req = UserLoginRequest(email="mhs@kampus.ac.id", password=pwd)

        user, access_token, refresh_token = await AuthService.authenticate_user(mock_db, req)
        self.assertEqual(user.id, existing_user.id)
        decoded = decode_access_token(access_token)
        self.assertEqual(decoded["sub"], str(existing_user.id))
        self.assertEqual(decoded["role"], "TRIAL")

    async def test_tc_auth_003_refresh_token_valid_happy_path(self):
        """TC-AUTH-003 [Happy Ending]: Refresh token valid menghasilkan token akses baru."""
        user = User(id=uuid.uuid4(), email="active@kampus.ac.id", role="PREMIUM", is_active=True)
        raw_refresh = create_refresh_token(subject=str(user.id))
        sess = Session(user_id=user.id, refresh_token_hash=hash_token(raw_refresh))

        mock_db = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([sess]),
            get_handler=lambda m, ident: user,
        )
        resp = await auth_router.refresh_token_endpoint(refresh_token=raw_refresh, db=mock_db)
        self.assertIn("access_token", resp.data)
        decoded = decode_access_token(resp.data["access_token"])
        self.assertEqual(decoded["sub"], str(user.id))

    async def test_tc_auth_004_logout_session_revocation_happy_path(self):
        """TC-AUTH-004 [Happy Ending]: Logout mencabut sesi refresh token dari basis data."""
        user = User(id=uuid.uuid4(), email="logout@kampus.ac.id", role="TRIAL", is_active=True)
        sess = Session(user_id=user.id, refresh_token_hash=hash_token("dummy-refresh"))
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([sess]))
        mock_response = MagicMock()

        res = await auth_router.logout(response=mock_response, refresh_token="dummy-refresh", current_user=user, db=mock_db)
        self.assertIn(sess, mock_db.deleted)
        self.assertTrue(mock_db.committed)
        mock_response.delete_cookie.assert_called_with(key="refresh_token")

    async def test_tc_auth_005_update_user_profile_happy_path(self):
        """TC-AUTH-005 [Happy Ending]: Pengguna memperbarui nama lengkap dan institusi profil."""
        user = User(
            id=uuid.uuid4(),
            full_name="Nama Lama",
            email="user@kampus.ac.id",
            institution="Institusi Lama",
            role="TRIAL",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        req = UserProfileUpdate(full_name="Nama Baru", institution="Institut Teknologi Bandung")

        res = await auth_router.update_profile(req=req, current_user=user, db=mock_db)
        self.assertEqual(user.full_name, "Nama Baru")
        self.assertEqual(user.institution, "Institut Teknologi Bandung")
        self.assertTrue(mock_db.committed)

    async def test_tc_auth_006_register_duplicate_email_bad_case(self):
        """TC-AUTH-006 [Bad Case]: Registrasi dengan email yang sudah ada memicu HTTP 400 Bad Request."""
        existing = User(email="duplicate@kampus.ac.id")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([existing]))
        req = UserRegisterRequest(
            full_name="Duplikat",
            email="duplicate@kampus.ac.id",
            password="Password123!",
            institution="Kampus A",
        )
        with self.assertRaises(HTTPException) as ctx:
            await AuthService.register_user(mock_db, req)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email is already registered", ctx.exception.detail)

    async def test_tc_auth_007_login_invalid_password_bad_case(self):
        """TC-AUTH-007 [Bad Case]: Login dengan password salah memicu HTTP 401 Unauthorized."""
        user = User(
            id=uuid.uuid4(),
            email="user@kampus.ac.id",
            password_hash=get_password_hash("Benar123!"),
            is_active=True,
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([user]))
        req = UserLoginRequest(email="user@kampus.ac.id", password="SalahPassword!")
        with self.assertRaises(HTTPException) as ctx:
            await AuthService.authenticate_user(mock_db, req)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid email or password", ctx.exception.detail)

    async def test_tc_auth_008_change_password_incorrect_old_bad_case(self):
        """TC-AUTH-008 [Bad Case]: Ganti password dengan password lama keliru ditolak HTTP 400."""
        user = User(id=uuid.uuid4(), password_hash=get_password_hash("PasswordAsli123!"))
        mock_db = MockAsyncSession()
        req = ChangePasswordRequest(old_password="PasswordPalsu!", new_password="PasswordBaru123!")

        with self.assertRaises(HTTPException) as ctx:
            await auth_router.change_password(req=req, current_user=user, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Current password is incorrect", ctx.exception.detail)

    async def test_tc_auth_009_inactive_suspended_account_blocker(self):
        """TC-AUTH-009 [Blocker]: Akun nonaktif/suspended diblokir saat login dengan HTTP 403 Forbidden."""
        pwd = "Password123!"
        inactive_user = User(
            id=uuid.uuid4(),
            email="banned@kampus.ac.id",
            password_hash=get_password_hash(pwd),
            is_active=False,
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([inactive_user]))
        req = UserLoginRequest(email="banned@kampus.ac.id", password=pwd)

        with self.assertRaises(HTTPException) as ctx:
            await AuthService.authenticate_user(mock_db, req)
        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("inactive or suspended", ctx.exception.detail)

    async def test_tc_auth_010_tampered_jwt_token_blocker(self):
        """TC-AUTH-010 [Blocker]: Token JWT palsu/rusak ditolak dependency get_current_user dengan HTTP 401."""
        tampered_cred = MagicMock()
        tampered_cred.credentials = "header.payload_palsu.signature_rusak"
        mock_db = MockAsyncSession()

        with self.assertRaises(HTTPException) as ctx:
            await get_current_user(credentials=tampered_cred, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid or expired access token", ctx.exception.detail)

    async def test_tc_auth_011_rbac_unauthorized_role_blocker(self):
        """TC-AUTH-011 [Blocker]: Pengguna role TRIAL diblokir saat mengakses endpoint khusus ADMIN."""
        trial_user = User(id=uuid.uuid4(), role="TRIAL", is_active=True)
        checker = require_role("ADMIN")

        with self.assertRaises(HTTPException) as ctx:
            await checker(current_user=trial_user)
        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Access forbidden", ctx.exception.detail)

    async def test_tc_auth_012_malformed_token_subject_bad_case(self):
        """TC-AUTH-012 [Bad Case]: Token JWT dengan subject non-UUID ditolak HTTP 401 Malformed token subject."""
        raw_token = create_access_token(subject="not-a-valid-uuid-format", role="TRIAL")
        mock_cred = MagicMock()
        mock_cred.credentials = raw_token
        mock_db = MockAsyncSession()

        with self.assertRaises(HTTPException) as ctx:
            await get_current_user(credentials=mock_cred, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Malformed token subject", ctx.exception.detail)

    async def test_tc_auth_013_missing_credentials_blocker(self):
        """TC-AUTH-013 [Blocker]: Request tanpa Authorization credentials ditolak HTTP 401."""
        mock_db = MockAsyncSession()
        with self.assertRaises(HTTPException) as ctx:
            await get_current_user(credentials=None, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("credentials were not provided", ctx.exception.detail)

    async def test_tc_auth_014_user_not_found_for_valid_token_bad_case(self):
        """TC-AUTH-014 [Bad Case]: Token JWT valid namun user telah dihapus dari DB ditolak HTTP 401."""
        user_id = uuid.uuid4()
        raw_token = create_access_token(subject=str(user_id), role="TRIAL")
        mock_cred = MagicMock()
        mock_cred.credentials = raw_token
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))

        with self.assertRaises(HTTPException) as ctx:
            await get_current_user(credentials=mock_cred, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("no longer exists", ctx.exception.detail)


# ===========================================================================
# FITUR 2: MANAJEMEN DOKUMEN & WORKSPACE (TC-DOC-001 s/d TC-DOC-012)
# ===========================================================================
class TestWhiteboxFeature2Documents(unittest.IsolatedAsyncioTestCase):
    """Pengujian Whitebox Fitur 2: Manajemen Dokumen & Workspace Pengguna."""

    def test_tc_doc_001_validate_allowed_extensions_happy_path(self):
        """TC-DOC-001 [Happy Ending]: Validasi format file PDF, DOCX, dan TXT lolos pemeriksaan."""
        for fname in ["laporan.pdf", "skripsi.docx", "draft.txt", "TESIS.PDF"]:
            fake_file = MagicMock()
            fake_file.filename = fname
            try:
                DocumentService.validate_file(fake_file)
            except HTTPException:
                self.fail(f"Ekstensi valid '{fname}' keliru ditolak")

    def test_tc_doc_002_extract_text_txt_happy_path(self):
        """TC-DOC-002 [Happy Ending]: Ekstraksi teks naskah TXT menghasilkan string teks lengkap."""
        content = "Sistem deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi semantik."
        tmp_path = os.path.join(settings.UPLOAD_DIR, "test_extract_doc.txt")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        extracted = TextPreprocessor.extract_text_from_file(tmp_path, mime_type="text/plain")
        self.assertEqual(extracted.strip(), content)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    def test_tc_doc_003_normalize_whitespace_and_case_folding_happy_path(self):
        """TC-DOC-003 [Happy Ending]: Normalisasi teks merapikan spasi tak beraturan dan case folding."""
        raw = "   Analisis   Performa \t\n Algoritma \t WINNOWING!   "
        norm = TextPreprocessor.normalize_whitespace(raw)
        folded = TextPreprocessor.case_folding(norm)
        clean = TextPreprocessor.clean_for_lexical(folded)

        self.assertEqual(norm, "Analisis Performa Algoritma WINNOWING!")
        self.assertEqual(folded, "analisis performa algoritma winnowing!")
        self.assertEqual(clean, "analisisperformaalgoritmawinnowing")

    async def test_tc_doc_004_list_documents_pagination_happy_path(self):
        """TC-DOC-004 [Happy Ending]: Menampilkan daftar dokumen pengguna dengan paginasi terstruktur."""
        user = User(id=uuid.uuid4())
        doc1 = Document(
            id=uuid.uuid4(),
            user_id=user.id,
            original_filename="doc1.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            status="READY",
            created_at=datetime.now(timezone.utc),
        )
        doc2 = Document(
            id=uuid.uuid4(),
            user_id=user.id,
            original_filename="doc2.docx",
            file_size_bytes=2048,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            status="READY",
            created_at=datetime.now(timezone.utc),
        )

        call_count = 0
        def exec_handler(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MockQueryResult(scalar_val=2)
            return MockQueryResult([doc1, doc2])

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        resp = await doc_router.list_documents(page=1, limit=10, current_user=user, db=mock_db)
        self.assertEqual(resp.data.total, 2)
        self.assertEqual(len(resp.data.items), 2)
        self.assertEqual(resp.data.pages, 1)

    async def test_tc_doc_005_soft_delete_document_uu_pdp_happy_path(self):
        """TC-DOC-005 [Happy Ending]: Soft delete dokumen pengguna untuk kepatuhan UU PDP No. 27/2022."""
        user = User(id=uuid.uuid4())
        doc = Document(id=uuid.uuid4(), user_id=user.id, status="READY", deleted_at=None)
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([doc]))

        resp = await doc_router.delete_document(doc_id=doc.id, current_user=user, db=mock_db)
        self.assertEqual(doc.status, "DELETED")
        self.assertIsNotNone(doc.deleted_at)
        self.assertTrue(mock_db.committed)
        self.assertIn("UU PDP", resp.message)

    def test_tc_doc_006_unsupported_file_extension_bad_case(self):
        """TC-DOC-006 [Bad Case]: Format berkas ilegal (.exe, .zip, .py) ditolak dengan HTTP 400."""
        for invalid in ["virus.exe", "arsip.zip", "script.py", "program.sh"]:
            fake_file = MagicMock()
            fake_file.filename = invalid
            with self.assertRaises(HTTPException) as ctx:
                DocumentService.validate_file(fake_file)
            self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Unsupported file format", ctx.exception.detail)

    def test_tc_doc_007_missing_filename_no_extension_bad_case(self):
        """TC-DOC-007 [Bad Case]: Berkas tanpa ekstensi atau nama kosong memicu HTTP 400."""
        for bad_name in ["", "   ", "filenotanextension"]:
            fake_file = MagicMock()
            fake_file.filename = bad_name
            with self.assertRaises(HTTPException) as ctx:
                DocumentService.validate_file(fake_file)
            self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Filename is missing or has no valid extension", ctx.exception.detail)

    async def test_tc_doc_008_empty_zero_byte_file_bad_case(self):
        """TC-DOC-008 [Bad Case]: Pengunggahan berkas kosong berukuran 0 byte ditolak HTTP 400."""
        mock_file = AsyncMock()
        mock_file.filename = "kosong.pdf"
        mock_file.read.return_value = b""
        mock_db = MockAsyncSession()

        with self.assertRaises(HTTPException) as ctx:
            await DocumentService.save_uploaded_file(mock_db, uuid.uuid4(), mock_file)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("File is empty (0 bytes)", ctx.exception.detail)

    async def test_tc_doc_009_file_size_exceeds_max_limit_bad_case(self):
        """TC-DOC-009 [Bad Case]: Pengunggahan berkas melampaui batas maksimal (10MB) ditolak HTTP 413."""
        mock_file = AsyncMock()
        mock_file.filename = "raksasa.pdf"
        oversized_bytes = (settings.MAX_FILE_SIZE_MB * 1024 * 1024) + 1024
        mock_file.read.return_value = b"X" * oversized_bytes
        mock_db = MockAsyncSession()

        with self.assertRaises(HTTPException) as ctx:
            await DocumentService.save_uploaded_file(mock_db, uuid.uuid4(), mock_file)
        self.assertEqual(ctx.exception.status_code, status.HTTP_413_CONTENT_TOO_LARGE)
        self.assertIn("exceeds maximum allowed size", ctx.exception.detail)

    async def test_tc_doc_010_tenant_isolation_cross_user_access_blocker(self):
        """TC-DOC-010 [Blocker]: Akses dokumen milik pengguna lain diblokir (Tenant Isolation HTTP 404)."""
        user_a = User(id=uuid.uuid4())
        user_b = User(id=uuid.uuid4())
        doc_of_user_b = Document(id=uuid.uuid4(), user_id=user_b.id)

        # Database hanya mengembalikan dokumen jika user_id cocok
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))

        with self.assertRaises(HTTPException) as ctx:
            await doc_router.get_document(doc_id=doc_of_user_b.id, current_user=user_a, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Document not found", ctx.exception.detail)

    async def test_tc_doc_011_get_document_detail_happy_path(self):
        """TC-DOC-011 [Happy Ending]: Pengguna mengambil detail naskah miliknya sendiri."""
        user = User(id=uuid.uuid4())
        doc = Document(
            id=uuid.uuid4(),
            user_id=user.id,
            original_filename="tesis.pdf",
            status="READY",
            file_size_bytes=1024,
            mime_type="application/pdf",
            created_at=datetime.utcnow(),
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([doc]))

        resp = await doc_router.get_document(doc_id=doc.id, current_user=user, db=mock_db)
        self.assertEqual(resp.data.id, doc.id)
        self.assertEqual(resp.data.original_filename, "tesis.pdf")

    def test_tc_doc_012_extract_text_nonexistent_file_bad_case(self):
        """TC-DOC-012 [Bad Case]: Ekstraksi berkas pada path tidak ada memicu FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            TextPreprocessor.extract_text_from_file("/path/tidak/pernah/ada/naskah.txt")


# ===========================================================================
# FITUR 3: MESIN DETEKSI PLAGIARISME HYBRID 4-TIER (TC-DET-001 s/d TC-DET-013)
# ===========================================================================
class TestWhiteboxFeature3HybridEngine(unittest.TestCase):
    """Pengujian Whitebox Fitur 3: Mesin Deteksi Plagiarisme Hybrid 4-Tier."""

    def test_tc_det_001_sentence_segmentation_exact_char_offsets_happy_path(self):
        """TC-DET-001 [Happy Ending]: Segmentasi kalimat menghasilkan character offset persis sesuai teks asli."""
        text = (
            "Penelitian Dr. Budi Santoso, M.Kom. membahas deteksi plagiarisme cerdas. "
            "Algoritma Winnowing membagi naskah menjadi rangkaian k-gram berurutan. "
            "Tingkat akurasi mencapai 98.5% pada data uji!"
        )
        sentences = TextPreprocessor.segment_sentences(text)
        self.assertEqual(len(sentences), 3)

        for s in sentences:
            sliced = text[s.start_char : s.end_char]
            self.assertEqual(sliced, s.text, f"Offset tidak cocok: '{sliced}' != '{s.text}'")
            self.assertGreater(s.word_count, 0)

    def test_tc_det_002_tier1_winnowing_verbatim_copy_detection_happy_path(self):
        """TC-DET-002 [Happy Ending]: Tier 1 Winnowing mendeteksi 100% kemiripan pada teks copy-paste verbatim."""
        engine = WinnowingLexicalEngine(k=5, w=4)
        sample_text = "algoritma winnowing cerdas mendeteksi duplikasi naskah akademik secara presisi"
        hashes_a = engine.extract_fingerprints(sample_text)
        hashes_b = engine.extract_fingerprints(sample_text)

        set_a = {h for h, pos in hashes_a}
        set_b = {h for h, pos in hashes_b}
        self.assertGreater(len(set_a), 0)
        self.assertEqual(set_a, set_b)

        # Uji Rabin-Karp rolling update konsisten dengan hash polinomial langsung
        clean = TextPreprocessor.clean_for_lexical(sample_text)
        direct_hashes = [engine.polynomial_hash(clean[i : i + engine.k]) for i in range(len(clean) - engine.k + 1)]
        rolling_hashes = [h for h, pos in engine.compute_kgram_hashes(sample_text)]
        self.assertEqual(direct_hashes, rolling_hashes)

    def test_tc_det_003_tier2_semantic_paraphrase_similarity_happy_path(self):
        """TC-DET-003 [Happy Ending]: Tier 2 mendeteksi parafrase konsep sinonim akademik di atas threshold 0.75."""
        engine = SemanticEngine()
        s1 = "Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi semantik berbasis deep learning."
        s2 = "Pendeteksian plagiarisme pintar menggunakan kombinasi algoritma leksikal serta representasi semantik deep learning."

        emb1 = engine.embed_sentence(s1)
        emb2 = engine.embed_sentence(s2)
        sim = engine.cosine_similarity(emb1, emb2)

        self.assertGreaterEqual(sim, 0.75, f"Kemiripan semantik parafrase {sim} di bawah threshold 0.75")

    def test_tc_det_004_tier3_stylometric_burstiness_stats_happy_path(self):
        """TC-DET-004 [Happy Ending]: Tier 3 menghitung mean, standar deviasi, dan burstiness variasi kalimat manusia."""
        engine = StylometricEngine()
        text = (
            "Ini singkat. "
            "Kalimat kedua ini memiliki panjang sedang yang memberikan variasi ritme sintaksis tulisan manusia. "
            "Adapun kalimat ketiga ini dirancang sengaja sangat panjang agar terdapat disparitas deviasi standar yang signifikan di antara seluruh kalimat pengujian."
        )
        sentences = TextPreprocessor.segment_sentences(text)
        mu, sigma, burstiness = engine.calculate_sentence_length_stats(sentences)

        self.assertGreater(mu, 0.0)
        self.assertGreater(sigma, 0.0)
        self.assertTrue(-1.0 <= burstiness <= 1.0)

    def test_tc_det_005_tier4_composite_weighted_aggregation_happy_path(self):
        """TC-DET-005 [Happy Ending]: Tier 4 menggabungkan bobot 50% T1 + 35% T2 + 15% T3 sesuai formula SDD."""
        aggregator = HybridAggregator(w_lexical=0.50, w_semantic=0.35, w_stylometric=0.15)
        t1, t2, t3 = 60.0, 40.0, 20.0
        expected = round(0.50 * 60.0 + 0.35 * 40.0 + 0.15 * 20.0, 2)
        score = aggregator.calculate_composite_score(t1, t2, t3)
        self.assertEqual(score, expected)
        self.assertEqual(score, 47.0)

    def test_tc_det_006_empty_text_input_bad_case(self):
        """TC-DET-006 [Bad Case]: Teks masukan kosong atau whitespace ditangani tanpa exception crash."""
        self.assertEqual(TextPreprocessor.segment_sentences(""), [])
        self.assertEqual(TextPreprocessor.segment_sentences("   \t\n  "), [])
        self.assertEqual(TextPreprocessor.tokenize_words(""), [])
        self.assertEqual(TextPreprocessor.clean_for_lexical(""), "")

    def test_tc_det_007_short_text_below_kgram_boundary_bad_case(self):
        """TC-DET-007 [Bad Case]: Teks lebih pendek dari ukuran k-gram (n < k) aman dari IndexOutOfBounds."""
        engine = WinnowingLexicalEngine(k=5, w=4)
        short_text = "abc"  # n=3 < k=5
        hashes = engine.compute_kgram_hashes(short_text)
        self.assertEqual(len(hashes), 1)
        self.assertEqual(hashes[0][1], 0)

    def test_tc_det_008_monotonous_ai_sentence_lengths_bad_case(self):
        """TC-DET-008 [Bad Case]: Teks AI monoton (panjang seragam) menghasilkan burstiness negatif dan anomali."""
        engine = StylometricEngine()
        # 4 kalimat masing-masing 5 kata persis
        uniform_sentences = [
            SentenceSpan(index=0, text="Satu dua tiga empat lima.", start_char=0, end_char=25, word_count=5),
            SentenceSpan(index=1, text="Satu dua tiga empat lima.", start_char=26, end_char=51, word_count=5),
            SentenceSpan(index=2, text="Satu dua tiga empat lima.", start_char=52, end_char=77, word_count=5),
            SentenceSpan(index=3, text="Satu dua tiga empat lima.", start_char=78, end_char=103, word_count=5),
        ]
        mu, sigma, burstiness = engine.calculate_sentence_length_stats(uniform_sentences)
        self.assertEqual(sigma, 0.0)
        self.assertEqual(burstiness, -1.0)

    def test_tc_det_009_zero_vector_cosine_similarity_bad_case(self):
        """TC-DET-009 [Bad Case]: Cosine similarity pada vektor nol mengembalikan 0.0 tanpa ZeroDivisionError."""
        engine = SemanticEngine()
        zero_v1 = [0.0] * 384
        zero_v2 = [0.0] * 384
        normal_v = [1.0] + [0.0] * 383

        self.assertEqual(engine.cosine_similarity(zero_v1, zero_v2), 0.0)
        self.assertEqual(engine.cosine_similarity(zero_v1, normal_v), 0.0)

    def test_tc_det_010_academic_citation_filter_blocker(self):
        """TC-DET-010 [Blocker]: Pola sitasi akademik otomatis dilewati agar tidak memicu false positive blocker."""
        cits = [
            "[1] Santoso, B. (2024). Deteksi Plagiarisme Cerdas Menggunakan Winnowing.",
            "(Gunawan dan Hermawan, 2023)",
            "[12] Pratama et al. Journal of Computer Science, 2025.",
        ]
        normal = "Penelitian ini menggunakan arsitektur hybrid leksikal dan semantik."

        for c in cits:
            self.assertTrue(TextPreprocessor.is_citation_sentence(c), f"Sitasi '{c}' gagal terdeteksi")
        self.assertFalse(TextPreprocessor.is_citation_sentence(normal))

    def test_tc_det_011_calculate_type_token_ratio_happy_path(self):
        """TC-DET-011 [Happy Ending]: Perhitungan TTR (Type-Token Ratio) dan keanekaragaman leksikal akurat."""
        engine = StylometricEngine()
        sample_text = "analisis sistem cerdas untuk analisis performa sistem deteksi"
        ttr, total, unique = engine.calculate_type_token_ratio(sample_text)
        self.assertEqual(total, 8)
        self.assertEqual(unique, 6)
        self.assertEqual(ttr, round(6 / 8, 4))

    def test_tc_det_012_tier1_only_pipeline_fast_path(self):
        """TC-DET-012 [Happy Ending]: Pipeline hybrid depth TIER1_ONLY hanya mengeksekusi leksikal Winnowing."""
        aggregator = HybridAggregator()
        text = "Penelitian ini menguji akurasi algoritma leksikal secara cepat."
        result = aggregator.run_pipeline(text, audit_depth="TIER1_ONLY")
        self.assertEqual(result.audit_depth, "TIER1_ONLY")
        self.assertEqual(result.score_semantic, 0.0)
        self.assertEqual(result.score_stylometric, 0.0)
        self.assertEqual(result.score_composite, result.score_lexical)

    def test_tc_det_013_stylometric_analysis_empty_document_bad_case(self):
        """TC-DET-013 [Bad Case]: Evaluasi stilometri pada teks kosong mengembalikan skor 0.0 deterministik."""
        engine = StylometricEngine()
        res = engine.analyze_document("", [])
        self.assertEqual(res.score_t3, 0.0)
        self.assertEqual(res.total_words, 0)
        self.assertFalse(res.is_ai_monotonous)


# ===========================================================================
# FITUR 4: LAPORAN AUDIT, HEATMAP & VERIFIKASI QR (TC-REP-001 s/d TC-REP-012)
# ===========================================================================
class TestWhiteboxFeature4ReportsVerification(unittest.IsolatedAsyncioTestCase):
    """Pengujian Whitebox Fitur 4: Laporan Audit, Heatmap Viewer & Verifikasi Publik QR."""

    def test_tc_rep_001_generate_heatmap_annotations_happy_path(self):
        """TC-REP-001 [Happy Ending]: Generator heatmap menghasilkan data anotasi warna RED/ORANGE/YELLOW."""
        from app.engine.tier4_aggregator import HeatmapAnnotationData

        anno_t1 = HeatmapAnnotationData(
            start=0, end=25, tier="T1", color="RED", similarity=1.0,
            source_title="Paper Sumber A", text_snippet="Kalimat copy paste persis.",
        )
        anno_t2 = HeatmapAnnotationData(
            start=26, end=50, tier="T2", color="ORANGE", similarity=0.88,
            source_title="Paper Sumber B", text_snippet="Kalimat hasil parafrase semantik.",
        )
        anno_t3 = HeatmapAnnotationData(
            start=51, end=75, tier="T3", color="YELLOW", similarity=0.45,
            source_title="AI Stylometry Anomaly", text_snippet="Kalimat ritme monoton terdeteksi AI.",
        )

        d1 = anno_t1.to_dict()
        d2 = anno_t2.to_dict()
        d3 = anno_t3.to_dict()

        self.assertEqual(d1["color"], "RED")
        self.assertEqual(d1["tier"], "T1")
        self.assertEqual(d2["color"], "ORANGE")
        self.assertEqual(d2["tier"], "T2")
        self.assertEqual(d3["color"], "YELLOW")
        self.assertEqual(d3["tier"], "T3")

    async def test_tc_rep_002_get_report_by_id_happy_path(self):
        """TC-REP-002 [Happy Ending]: Mengambil laporan audit berdasarkan report ID berhasil."""
        user = User(id=uuid.uuid4(), full_name="Azriel")
        doc = Document(id=uuid.uuid4(), original_filename="Tesis.pdf")
        task = AuditTask(id=uuid.uuid4(), document=doc, user=user)
        report = AuditReport(
            id=uuid.uuid4(),
            audit_task=task,
            audit_task_id=task.id,
            score_composite=24.5,
            score_lexical=20.0,
            score_semantic=25.0,
            score_stylometric=10.0,
            verification_uuid=uuid.uuid4(),
            heatmap_annotations=[],
            matched_sources=[],
            generated_at=datetime.now(timezone.utc),
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([report]))
        resp = await report_router.get_report(report_id=report.id, current_user=user, db=mock_db)
        self.assertEqual(resp.data.id, report.id)
        self.assertEqual(resp.data.score_composite, 24.5)

    def test_tc_rep_003_generate_pdf_certificate_happy_path(self):
        """TC-REP-003 [Happy Ending]: Ekspor sertifikat PDF menghasilkan byte stream format %PDF- valid."""
        pdf_bytes = generate_pdf_certificate(
            report_id=str(uuid.uuid4()),
            verification_uuid=str(uuid.uuid4()),
            document_title="Tesis_Akhir.pdf",
            user_name="Mochammad Azriel Albian Putra",
            institution="Institut Teknologi Nasional",
            generated_at=datetime.now(timezone.utc),
            score_composite=18.5,
            score_lexical=20.0,
            score_semantic=15.0,
            score_stylometric=10.0,
            matched_sources=[],
        )
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 1000)

    async def test_tc_rep_004_verify_certificate_public_valid_happy_path(self):
        """TC-REP-004 [Happy Ending]: Verifikasi publik QR UUIDv4 mengembalikan keaslian dokumen."""
        user = User(id=uuid.uuid4(), full_name="Ibnu Dwiki", institution="Universitas Airlangga")
        doc = Document(id=uuid.uuid4(), original_filename="Skripsi_Ibnu.pdf", deleted_at=None, status="READY")
        task = AuditTask(id=uuid.uuid4())
        v_uuid = uuid.uuid4()
        report = AuditReport(id=uuid.uuid4(), verification_uuid=v_uuid, score_composite=21.2)

        # Database returns tuple of (AuditReport, AuditTask, Document, User)
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([(report, task, doc, user)]))
        resp = await report_router.verify_certificate_public(verification_uuid=v_uuid, db=mock_db)

        self.assertTrue(resp.data.is_valid)
        self.assertEqual(resp.data.document_title, "Skripsi_Ibnu.pdf")
        self.assertEqual(resp.data.user_name, "Ibnu Dwiki")

    def test_tc_rep_005_clean_pdf_filename_happy_path(self):
        """TC-REP-005 [Happy Ending]: Pembersihan nama berkas sertifikat PDF membuang karakter ilegal."""
        self.assertEqual(clean_pdf_filename("LPJ FPK.docx_compressed.pdf"), "Sertifikat_VeriText_LPJ_FPK_docx_compressed.pdf")
        self.assertEqual(clean_pdf_filename("Tesis / Skripsi: Final?.pdf"), "Sertifikat_VeriText_Tesis_Skripsi_Final.pdf")
        self.assertEqual(clean_pdf_filename("   "), "Sertifikat_VeriText_Naskah_Akademik.pdf")

    async def test_tc_rep_006_get_report_not_found_bad_case(self):
        """TC-REP-006 [Bad Case]: Pengambilan laporan audit ID tak terdaftar memicu HTTP 404."""
        user = User(id=uuid.uuid4())
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as ctx:
            await report_router.get_report(report_id=uuid.uuid4(), current_user=user, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Audit report not found", ctx.exception.detail)

    async def test_tc_rep_007_verify_unregistered_uuid_bad_case(self):
        """TC-REP-007 [Bad Case]: Verifikasi publik UUID tak terdaftar menghasilkan is_valid: False."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        fake_uuid = uuid.uuid4()
        resp = await report_router.verify_certificate_public(verification_uuid=fake_uuid, db=mock_db)
        self.assertFalse(resp.data.is_valid)
        self.assertIn("tidak terdaftar", resp.data.message)

    def test_tc_rep_008_pdf_certificate_boundary_score_bad_case(self):
        """TC-REP-008 [Bad Case]: Ekspor sertifikat PDF pada batas nilai skor 0.0 tetap valid tanpa crash."""
        pdf_bytes = generate_pdf_certificate(
            report_id=str(uuid.uuid4()),
            verification_uuid=str(uuid.uuid4()),
            document_title="Naskah_Nol.pdf",
            user_name="Pengguna Baru",
            institution="Institut",
            generated_at=datetime.now(timezone.utc),
            score_composite=0.0,
            score_lexical=0.0,
            score_semantic=0.0,
            score_stylometric=0.0,
            matched_sources=[],
        )
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    async def test_tc_rep_009_cancel_completed_task_bad_case(self):
        """TC-REP-009 [Bad Case]: Membatalkan tugas audit berstatus 'COMPLETED' ditolak HTTP 400 Bad Request."""
        task = AuditTask(id=uuid.uuid4(), user_id=uuid.uuid4(), status="COMPLETED")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([task]))

        with self.assertRaises(HTTPException) as ctx:
            await AuditService.cancel_task(mock_db, task.id, task.user_id)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot cancel task in 'COMPLETED' state", ctx.exception.detail)

    async def test_tc_rep_010_verify_deleted_document_uu_pdp_blocker(self):
        """TC-REP-010 [Blocker]: Verifikasi dokumen yang dihapus sesuai UU PDP dinyatakan kedaluwarsa."""
        user = User(id=uuid.uuid4(), full_name="User PDP")
        doc = Document(id=uuid.uuid4(), original_filename="Dihapus_PDP.pdf", deleted_at=datetime.now(timezone.utc), status="DELETED")
        task = AuditTask(id=uuid.uuid4())
        v_uuid = uuid.uuid4()
        report = AuditReport(id=uuid.uuid4(), verification_uuid=v_uuid)

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([(report, task, doc, user)]))
        resp = await report_router.verify_certificate_public(verification_uuid=v_uuid, db=mock_db)

        self.assertFalse(resp.data.is_valid)
        self.assertIn("UU PDP No. 27/2022", resp.message)
        self.assertIn("kedaluwarsa", resp.data.message)

    async def test_tc_rep_011_export_pdf_endpoint_happy_path(self):
        """TC-REP-011 [Happy Ending]: Endpoint export_pdf mengembalikan response HTTP binary PDF."""
        report_id = uuid.uuid4()
        user = User(id=uuid.uuid4(), full_name="Azriel")
        doc = Document(id=uuid.uuid4(), original_filename="Tesis.pdf")
        task = AuditTask(id=uuid.uuid4(), document=doc, user=user)
        report = AuditReport(
            id=report_id,
            audit_task=task,
            audit_task_id=task.id,
            score_composite=15.0,
            score_lexical=10.0,
            score_semantic=20.0,
            score_stylometric=5.0,
            verification_uuid=uuid.uuid4(),
            heatmap_annotations=[],
            matched_sources=[],
            generated_at=datetime.now(timezone.utc),
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([report]))
        resp = await report_router.export_pdf(report_id=report_id, db=mock_db)
        self.assertEqual(resp.media_type, "application/pdf")
        self.assertTrue(resp.body.startswith(b"%PDF-"))

    async def test_tc_rep_012_export_pdf_not_found_bad_case(self):
        """TC-REP-012 [Bad Case]: Endpoint export_pdf untuk report ID tak terdaftar memicu HTTP 404."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as ctx:
            await report_router.export_pdf(report_id=uuid.uuid4(), db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Audit report not found", ctx.exception.detail)


# ===========================================================================
# FITUR 5: BANK KORPUS ILMIAH (TC-CRP-001 s/d TC-CRP-013)
# ===========================================================================
class TestWhiteboxFeature5CorpusBank(unittest.IsolatedAsyncioTestCase):
    """Pengujian Whitebox Fitur 5: Bank Korpus Ilmiah."""

    async def test_tc_crp_001_list_corpus_with_category_filter_happy_path(self):
        """TC-CRP-001 [Happy Ending]: Listing korpus terindeks dengan filter kategori berhasil."""
        c1 = CorpusDocument(id=uuid.uuid4(), title="Paper A", category="Informatika", status="INDEXED")
        c2 = CorpusDocument(id=uuid.uuid4(), title="Paper B", category="Informatika", status="INDEXED")

        call_idx = 0
        def exec_handler(stmt):
            nonlocal call_idx
            call_idx += 1
            if call_idx == 1:
                return MockQueryResult(scalar_val=2)
            return MockQueryResult([c1, c2])

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        items, total = await CorpusService.list_corpus_documents(mock_db, category="Informatika")
        self.assertEqual(total, 2)
        self.assertEqual(len(items), 2)

    async def test_tc_crp_002_ingest_zip_corpus_happy_path(self):
        """TC-CRP-002 [Happy Ending]: Unggah arsip ZIP korpus baru berhasil dan status PENDING_INDEX."""
        mock_file = AsyncMock()
        mock_file.filename = "kumpulan_jurnal.zip"
        mock_file.read.return_value = b"PK\x03\x04batchcontent123"

        # Check existing hash returns None (belum ada)
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        user_id = uuid.uuid4()

        res = await CorpusService.ingest_zip_corpus(mock_db, user_id, mock_file, category="Jurnal", academic_year="2025/2026")
        self.assertEqual(res, 1)
        added_docs = [x for x in mock_db.added if isinstance(x, CorpusDocument)]
        self.assertEqual(len(added_docs), 1)
        self.assertEqual(added_docs[0].status, "PENDING_INDEX")
        self.assertEqual(added_docs[0].category, "Jurnal")

        # Cleanup created upload file
        stored_path = os.path.join(settings.UPLOAD_DIR, added_docs[0].stored_filename)
        if os.path.exists(stored_path):
            os.remove(stored_path)

    async def test_tc_crp_003_update_corpus_metadata_happy_path(self):
        """TC-CRP-003 [Happy Ending]: Memperbarui metadata korpus (judul, kategori, tahun akademik) berhasil."""
        doc = CorpusDocument(id=uuid.uuid4(), title="Judul Lama", category="Umum", academic_year="2024", status="INDEXED")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([doc]))

        req = CorpusDocUpdateRequest(title="Judul Baru", category="Kecerdasan Buatan", academic_year="2025/2026")
        updated = await CorpusService.update_corpus_doc(mock_db, doc.id, req)

        self.assertEqual(updated.title, "Judul Baru")
        self.assertEqual(updated.category, "Kecerdasan Buatan")
        self.assertEqual(updated.academic_year, "2025/2026")
        self.assertTrue(mock_db.committed)

    async def test_tc_crp_004_delete_corpus_doc_happy_path(self):
        """TC-CRP-004 [Happy Ending]: Soft delete dokumen korpus mengubah status menjadi DELETED."""
        doc = CorpusDocument(id=uuid.uuid4(), status="INDEXED")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([doc]))

        res = await CorpusService.delete_corpus_doc(mock_db, doc.id)
        self.assertTrue(res)
        self.assertEqual(doc.status, "DELETED")
        self.assertTrue(mock_db.committed)

    def test_tc_crp_005_reference_corpus_bank_singleton_happy_path(self):
        """TC-CRP-005 [Happy Ending]: Singleton ReferenceCorpusBank memuat paper referensi built-in."""
        bank = ReferenceCorpusBank.get_instance()
        self.assertIsNotNone(bank)
        fps = bank.get_fingerprint_index()
        chunks = bank.get_corpus_chunks()
        self.assertGreater(len(fps), 0)
        self.assertGreater(len(chunks), 0)

    async def test_tc_crp_006_update_nonexistent_corpus_bad_case(self):
        """TC-CRP-006 [Bad Case]: Update korpus ID yang tidak ditemukan memicu HTTP 404 Not Found."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        req = CorpusDocUpdateRequest(title="Baru")

        with self.assertRaises(HTTPException) as ctx:
            await CorpusService.update_corpus_doc(mock_db, uuid.uuid4(), req)
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Corpus document not found", ctx.exception.detail)

    async def test_tc_crp_007_delete_nonexistent_corpus_bad_case(self):
        """TC-CRP-007 [Bad Case]: Hapus korpus ID tak ditemukan memicu HTTP 404 Not Found."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as ctx:
            await CorpusService.delete_corpus_doc(mock_db, uuid.uuid4())
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Corpus document not found", ctx.exception.detail)

    async def test_tc_crp_008_empty_corpus_category_filter_bad_case(self):
        """TC-CRP-008 [Bad Case]: Kategori yang tidak memiliki dokumen mengembalikan list kosong."""
        call_count = 0
        def exec_handler(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MockQueryResult(scalar_val=0)
            return MockQueryResult([])

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        items, total = await CorpusService.list_corpus_documents(mock_db, category="KategoriTakAda")
        self.assertEqual(total, 0)
        self.assertEqual(len(items), 0)

    async def test_tc_crp_009_duplicate_corpus_sha256_blocker(self):
        """TC-CRP-009 [Blocker]: Unggah korpus dengan SHA-256 identik diblokir dengan HTTP 409 Conflict."""
        mock_file = AsyncMock()
        mock_file.filename = "duplikat.zip"
        content = b"PK\x03\x04duplikasi_konten_arsip"
        mock_file.read.return_value = content

        existing = CorpusDocument(sha256_hash=hashlib.sha256(content).hexdigest())
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([existing]))

        with self.assertRaises(HTTPException) as ctx:
            await CorpusService.ingest_zip_corpus(mock_db, uuid.uuid4(), mock_file)
        self.assertEqual(ctx.exception.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("identical content hash already exists", ctx.exception.detail)

    async def test_tc_crp_010_mahasiswa_role_blocked_from_corpus_blocker(self):
        """TC-CRP-010 [Blocker]: Role Mahasiswa (TRIAL) dilarang mengakses manajemen korpus (Dosen/Admin only)."""
        mahasiswa = User(id=uuid.uuid4(), role="TRIAL")
        checker = require_role("REVIEWER", "ADMIN")

        with self.assertRaises(HTTPException) as ctx:
            await checker(current_user=mahasiswa)
        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)

    async def test_tc_crp_011_ingest_non_zip_extension_bad_case(self):
        """TC-CRP-011 [Bad Case]: Unggah berkas korpus non-ZIP (.pdf, .exe, .py) ditolak HTTP 400."""
        mock_file = AsyncMock()
        mock_file.filename = "naskah_bukan_zip.pdf"
        mock_file.read.return_value = b"konten bukan zip"
        mock_db = MockAsyncSession()

        with self.assertRaises(HTTPException) as ctx:
            await CorpusService.ingest_zip_corpus(mock_db, uuid.uuid4(), mock_file)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only ZIP archives (.zip) are allowed", ctx.exception.detail)

    async def test_tc_crp_012_ingest_empty_archive_bad_case(self):
        """TC-CRP-012 [Bad Case]: Unggah arsip ZIP korpus kosong (0 byte) ditolak HTTP 400."""
        mock_file = AsyncMock()
        mock_file.filename = "kosong.zip"
        mock_file.read.return_value = b""
        mock_db = MockAsyncSession()

        with self.assertRaises(HTTPException) as ctx:
            await CorpusService.ingest_zip_corpus(mock_db, uuid.uuid4(), mock_file)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Corpus archive is empty (0 bytes)", ctx.exception.detail)

    async def test_tc_crp_013_ingest_corrupted_zip_header_bad_case(self):
        """TC-CRP-013 [Bad Case]: Unggah berkas ber-ekstensi .zip namun bukan format ZIP valid (bukan magic PK) ditolak HTTP 400."""
        mock_file = AsyncMock()
        mock_file.filename = "rusak.zip"
        mock_file.read.return_value = b"BUKAN_ZIP_HEADER_DATA_12345"
        mock_db = MockAsyncSession()

        with self.assertRaises(HTTPException) as ctx:
            await CorpusService.ingest_zip_corpus(mock_db, uuid.uuid4(), mock_file)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid ZIP archive header", ctx.exception.detail)


# ===========================================================================
# FITUR 6: DOMPET TOKEN & BILLING (TC-BIL-001 s/d TC-BIL-014)
# ===========================================================================
class TestWhiteboxFeature6WalletBilling(unittest.IsolatedAsyncioTestCase):
    """Pengujian Whitebox Fitur 6: Dompet Token & Billing."""

    async def test_tc_bil_001_get_wallet_new_user_initialization_happy_path(self):
        """TC-BIL-001 [Happy Ending]: Inisialisasi dompet baru dengan saldo 0 jika belum ada wallet."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        user_id = uuid.uuid4()

        wallet = await BillingService.get_wallet(mock_db, user_id)
        self.assertEqual(wallet.user_id, user_id)
        self.assertEqual(wallet.balance, 0)
        self.assertTrue(mock_db.committed)

    async def test_tc_bil_002_create_topup_invoice_valid_package_happy_path(self):
        """TC-BIL-002 [Happy Ending]: Pembuatan invoice paket mahasiswa menghasilkan order ID & snap token."""
        mock_db = MockAsyncSession()
        user_id = uuid.uuid4()

        invoice = await BillingService.create_topup_invoice(mock_db, user_id, "pkg_10token")
        self.assertTrue(invoice.order_id.startswith("VT-"))
        self.assertTrue(invoice.snap_token.startswith("SNAP-"))
        self.assertEqual(invoice.token_amount, 10)
        self.assertEqual(invoice.gross_amount, 25000)
        self.assertEqual(invoice.status, "PENDING")

    async def test_tc_bil_003_midtrans_webhook_settlement_credit_happy_path(self):
        """TC-BIL-003 [Happy Ending]: Settlement Midtrans menambah saldo token dan mencatat CREDIT_TOPUP."""
        invoice = Invoice(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            order_id="VT-20261021-ORDER123",
            token_amount=10,
            gross_amount=25000,
            status="PENDING",
            package_name="Paket Mahasiswa",
        )
        wallet = TokenWallet(id=uuid.uuid4(), user_id=invoice.user_id, balance=5)

        exec_count = 0
        def exec_handler(stmt):
            nonlocal exec_count
            exec_count += 1
            if exec_count == 1:
                return MockQueryResult([invoice])
            return MockQueryResult([wallet])

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        sig = hashlib.sha512(f"VT-20261021-ORDER12320025000.00{settings.MIDTRANS_SERVER_KEY}".encode("utf-8")).hexdigest()
        payload = MidtransWebhookPayload(
            order_id="VT-20261021-ORDER123",
            status_code="200",
            gross_amount="25000.00",
            signature_key=sig,
            transaction_status="settlement",
            payment_type="bank_transfer",
        )

        res = await BillingService.process_midtrans_webhook(mock_db, payload)
        self.assertTrue(res)
        self.assertEqual(invoice.status, "PAID")
        self.assertEqual(wallet.balance, 15)  # 5 + 10

        txs = [x for x in mock_db.added if isinstance(x, TokenTransaction)]
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].transaction_type, "CREDIT_TOPUP")
        self.assertEqual(txs[0].amount, 10)

    async def test_tc_bil_004_audit_token_deduction_full_depth_happy_path(self):
        """TC-BIL-004 [Happy Ending]: Eksekusi audit kedalaman FULL mendebit 2 token dari saldo pengguna."""
        user_id = uuid.uuid4()
        doc = Document(id=uuid.uuid4(), user_id=user_id, original_filename="tesis.pdf")
        wallet = TokenWallet(user_id=user_id, balance=10)

        mock_file = AsyncMock()
        mock_file.filename = "tesis.pdf"
        mock_file.read.return_value = b"konten valid untuk audit naskah akademik"
        mock_file.content_type = "application/pdf"

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([wallet]))
        from app.workers.celery_app import celery_app
        with patch.object(celery_app.control, "inspect", return_value=None), patch("threading.Thread"):
            uploaded_doc, task = await DocumentService.save_uploaded_file_and_create_task(
                db=mock_db, user_id=user_id, file=mock_file, audit_depth="FULL"
            )

        self.assertEqual(wallet.balance, 8)  # 10 - 2
        txs = [x for x in mock_db.added if isinstance(x, TokenTransaction)]
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].amount, -2)
        self.assertEqual(txs[0].transaction_type, "DEBIT_AUDIT")

        # Cleanup created upload file
        fpath = os.path.join(settings.UPLOAD_DIR, uploaded_doc.stored_filename)
        if os.path.exists(fpath):
            os.remove(fpath)

    async def test_tc_bil_005_midtrans_idempotent_duplicate_settlement_happy_path(self):
        """TC-BIL-005 [Happy Ending]: Webhook transaksi berstatus PAID bersifat idempoten tanpa saldo ganda."""
        invoice = Invoice(order_id="VT-PAID-ALREADY", status="PAID", token_amount=50)
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([invoice]))

        sig = hashlib.sha512(f"VT-PAID-ALREADY200100000.00{settings.MIDTRANS_SERVER_KEY}".encode("utf-8")).hexdigest()
        payload = MidtransWebhookPayload(
            order_id="VT-PAID-ALREADY",
            status_code="200",
            gross_amount="100000.00",
            signature_key=sig,
            transaction_status="settlement",
        )
        res = await BillingService.process_midtrans_webhook(mock_db, payload)
        self.assertTrue(res)
        # Tidak ada penambahan ke mock_db.added
        self.assertEqual(len(mock_db.added), 0)

    async def test_tc_bil_006_invalid_package_id_topup_bad_case(self):
        """TC-BIL-006 [Bad Case]: Pemilihan package_id tidak valid ditolak HTTP 400 Bad Request."""
        mock_db = MockAsyncSession()
        with self.assertRaises(HTTPException) as ctx:
            await BillingService.create_topup_invoice(mock_db, uuid.uuid4(), "pkg_ilegal_hacked")
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid package_id", ctx.exception.detail)

    async def test_tc_bil_007_webhook_cancelled_expired_status_bad_case(self):
        """TC-BIL-007 [Bad Case]: Webhook Midtrans transaksi expire/cancel mengubah status tanpa menambah token."""
        invoice = Invoice(order_id="VT-EXPIRE-001", status="PENDING")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([invoice]))

        sig = hashlib.sha512(f"VT-EXPIRE-00120025000.00{settings.MIDTRANS_SERVER_KEY}".encode("utf-8")).hexdigest()
        payload = MidtransWebhookPayload(
            order_id="VT-EXPIRE-001",
            status_code="200",
            gross_amount="25000.00",
            signature_key=sig,
            transaction_status="expire",
        )
        await BillingService.process_midtrans_webhook(mock_db, payload)
        self.assertEqual(invoice.status, "EXPIRED")
        self.assertEqual(len(mock_db.added), 0)

    async def test_tc_bil_008_webhook_nonexistent_invoice_order_bad_case(self):
        """TC-BIL-008 [Bad Case]: Webhook untuk invoice order ID tidak terdaftar memicu HTTP 404."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        sig = hashlib.sha512(f"VT-TIDAK-ADA-99920025000.00{settings.MIDTRANS_SERVER_KEY}".encode("utf-8")).hexdigest()
        payload = MidtransWebhookPayload(
            order_id="VT-TIDAK-ADA-999",
            status_code="200",
            gross_amount="25000.00",
            signature_key=sig,
            transaction_status="settlement",
        )
        with self.assertRaises(HTTPException) as ctx:
            await BillingService.process_midtrans_webhook(mock_db, payload)
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Invoice order not found", ctx.exception.detail)

    async def test_tc_bil_009_midtrans_tampered_signature_blocker(self):
        """TC-BIL-009 [Blocker]: Webhook Midtrans dengan signature key palsu diblokir HTTP 400 Bad Request."""
        mock_db = MockAsyncSession()
        payload = MidtransWebhookPayload(
            order_id="VT-TEST-SIG",
            status_code="200",
            gross_amount="25000.00",
            signature_key="signature_palsu_peretas",
            transaction_status="settlement",
        )
        with self.assertRaises(HTTPException) as ctx:
            await BillingService.process_midtrans_webhook(mock_db, payload)
        self.assertIn(ctx.exception.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))
        self.assertIn("Invalid Midtrans signature key", ctx.exception.detail)

    async def test_tc_bil_010_insufficient_token_balance_audit_blocker(self):
        """TC-BIL-010 [Blocker]: Audit ditolak HTTP 402 Payment Required jika saldo token tidak mencukupi."""
        user_id = uuid.uuid4()
        wallet = TokenWallet(user_id=user_id, balance=0)  # Saldo 0, butuh 2

        mock_file = AsyncMock()
        mock_file.filename = "naskah.pdf"
        mock_file.read.return_value = b"konten teks dokumen uji"
        mock_file.content_type = "application/pdf"

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([wallet]))
        with self.assertRaises(HTTPException) as ctx:
            await DocumentService.save_uploaded_file_and_create_task(
                mock_db, user_id, mock_file, audit_depth="FULL"
            )
        self.assertEqual(ctx.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertIn("Saldo token tidak mencukupi", ctx.exception.detail)

    async def test_tc_bil_011_webhook_settlement_creates_missing_wallet_happy_path(self):
        """TC-BIL-011 [Happy Ending]: Webhook settlement menginisialisasi wallet baru jika user belum memiliki wallet."""
        invoice = Invoice(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            order_id="VT-NEW-WALLET-01",
            token_amount=20,
            gross_amount=50000,
            status="PENDING",
            package_name="Paket Peneliti",
        )
        call_count = 0
        def exec_handler(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MockQueryResult([invoice])
            # Wallet query returns None
            return MockQueryResult([])

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        sig = hashlib.sha512(f"VT-NEW-WALLET-0120050000.00{settings.MIDTRANS_SERVER_KEY}".encode("utf-8")).hexdigest()
        payload = MidtransWebhookPayload(
            order_id="VT-NEW-WALLET-01",
            status_code="200",
            gross_amount="50000.00",
            signature_key=sig,
            transaction_status="settlement",
        )
        res = await BillingService.process_midtrans_webhook(mock_db, payload)
        self.assertTrue(res)
        self.assertEqual(invoice.status, "PAID")

        # New wallet added with credited balance 20
        new_wallets = [x for x in mock_db.added if isinstance(x, TokenWallet)]
        self.assertEqual(len(new_wallets), 1)
        self.assertEqual(new_wallets[0].balance, 20)

    async def test_tc_bil_012_list_user_invoices_happy_path(self):
        """TC-BIL-012 [Happy Ending]: Mengambil daftar seluruh riwayat invoice top-up pengguna."""
        user = User(id=uuid.uuid4())
        now = datetime.utcnow()
        inv1 = Invoice(
            id=uuid.uuid4(),
            user_id=user.id,
            order_id="VT-INV-001",
            status="PAID",
            token_amount=10,
            gross_amount=25000,
            package_name="Paket 10",
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )
        inv2 = Invoice(
            id=uuid.uuid4(),
            user_id=user.id,
            order_id="VT-INV-002",
            status="PENDING",
            token_amount=50,
            gross_amount=100000,
            package_name="Paket 50",
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([inv1, inv2]))

        import app.api.v1.billing as billing_router
        resp = await billing_router.list_invoices(current_user=user, db=mock_db)
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0].order_id, "VT-INV-001")

    async def test_tc_bil_013_get_invoice_pdf_happy_path(self):
        """TC-BIL-013 [Happy Ending]: Mengunduh berkas kwitansi/invoice resmi berformat PDF."""
        user = User(id=uuid.uuid4())
        inv = Invoice(id=uuid.uuid4(), user_id=user.id, order_id="VT-PDF-001", status="PAID", token_amount=10, gross_amount=25000)
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([inv]))

        import app.api.v1.billing as billing_router
        resp = await billing_router.get_invoice_pdf(inv_id=inv.id, current_user=user, db=mock_db)
        self.assertEqual(resp.media_type, "application/pdf")
        self.assertTrue(resp.body.startswith(b"%PDF-"))

    async def test_tc_bil_014_webhook_deny_failed_status_bad_case(self):
        """TC-BIL-014 [Bad Case]: Webhook Midtrans transaksi ditolak/gagal mengubah status invoice menjadi FAILED."""
        invoice = Invoice(order_id="VT-DENY-001", status="PENDING")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([invoice]))

        sig = hashlib.sha512(f"VT-DENY-00120025000.00{settings.MIDTRANS_SERVER_KEY}".encode("utf-8")).hexdigest()
        payload = MidtransWebhookPayload(
            order_id="VT-DENY-001",
            status_code="200",
            gross_amount="25000.00",
            signature_key=sig,
            transaction_status="deny",
        )
        await BillingService.process_midtrans_webhook(mock_db, payload)
        self.assertEqual(invoice.status, "FAILED")


# ===========================================================================
# FITUR 7: KONSOL TATA KELOLA ADMIN & UU PDP (TC-ADM-001 s/d TC-ADM-015)
# ===========================================================================
class TestWhiteboxFeature7AdminGovernance(unittest.IsolatedAsyncioTestCase):
    """Pengujian Whitebox Fitur 7: Konsol Tata Kelola Administrator & Kepatuhan UU PDP."""

    async def test_tc_adm_001_list_users_with_filter_happy_path(self):
        """TC-ADM-001 [Happy Ending]: Admin menampilkan daftar pengguna dengan filter role dan pencarian."""
        u1 = User(
            id=uuid.uuid4(),
            full_name="Admin Sistem",
            email="admin@veritext.ai",
            role="ADMIN",
            is_active=True,
            failed_login_count=0,
            created_at=datetime.now(timezone.utc),
        )
        call_count = 0
        def exec_handler(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MockQueryResult(scalar_val=1)
            return MockQueryResult([u1])

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        resp = await admin_router.list_users_admin(role="ADMIN", search="veritext", page=1, limit=10, db=mock_db)
        self.assertEqual(resp.data.total, 1)
        self.assertEqual(len(resp.data.items), 1)

    async def test_tc_adm_002_create_user_admin_with_tokens_happy_path(self):
        """TC-ADM-002 [Happy Ending]: Admin membuat user baru beserta dompet token awal."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        req = AdminUserCreateRequest(
            full_name="Dosen Penguji",
            email="penguji@kampus.ac.id",
            password="PasswordDosen#123",
            role="REVIEWER",
            initial_tokens=50,
        )
        resp = await admin_router.create_user_admin(req=req, db=mock_db)
        self.assertEqual(resp.data.email, "penguji@kampus.ac.id")
        self.assertEqual(resp.data.role, "REVIEWER")

        wallets = [x for x in mock_db.added if isinstance(x, TokenWallet)]
        self.assertEqual(len(wallets), 1)
        self.assertEqual(wallets[0].balance, 50)

    async def test_tc_adm_003_update_user_admin_happy_path(self):
        """TC-ADM-003 [Happy Ending]: Admin memperbarui profil, role, dan institusi user."""
        user = User(
            id=uuid.uuid4(),
            full_name="Nama Awal",
            email="user@kampus.ac.id",
            role="TRIAL",
            institution="Kampus Lama",
            is_active=True,
            failed_login_count=0,
            created_at=datetime.now(timezone.utc),
        )
        mock_db = MockAsyncSession(
            get_handler=lambda m, ident: user,
            execute_handler=lambda s: MockQueryResult([user]),
        )
        req = AdminUserUpdateRequest(full_name="Nama Baru", role="PREMIUM", institution="Kampus Baru")

        resp = await admin_router.update_user_admin(user_id=str(user.id), req=req, db=mock_db)
        self.assertEqual(user.full_name, "Nama Baru")
        self.assertEqual(user.role, "PREMIUM")
        self.assertEqual(user.institution, "Kampus Baru")

    async def test_tc_adm_004_reset_password_admin_happy_path(self):
        """TC-ADM-004 [Happy Ending]: Admin mereset password akun pengguna dengan hash baru."""
        user = User(id=uuid.uuid4(), full_name="Mhs Reset", password_hash="old_hash")
        mock_db = MockAsyncSession(get_handler=lambda m, ident: user)
        req = AdminResetPasswordRequest(new_password="PasswordBaruAdmin#2026")

        resp = await admin_router.reset_password_admin(user_id=str(user.id), req=req, db=mock_db)
        self.assertTrue(verify_password("PasswordBaruAdmin#2026", user.password_hash))
        self.assertTrue(mock_db.committed)

    async def test_tc_adm_005_adjust_user_tokens_credit_debit_happy_path(self):
        """TC-ADM-005 [Happy Ending]: Admin menyesuaikan saldo token (kredit/debit) & mencatat transaksi audit."""
        user = User(id=uuid.uuid4())
        wallet = TokenWallet(id=uuid.uuid4(), user_id=user.id, balance=20)
        mock_db = MockAsyncSession(
            get_handler=lambda m, ident: user,
            execute_handler=lambda s: MockQueryResult([wallet]),
        )
        req = TokenAdjustmentRequest(amount=15, note="Bonus publikasi Q1")

        resp = await admin_router.adjust_user_tokens(user_id=str(user.id), req=req, db=mock_db)
        self.assertEqual(wallet.balance, 35)  # 20 + 15
        txs = [x for x in mock_db.added if isinstance(x, TokenTransaction)]
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].transaction_type, "CREDIT_ADMIN")
        self.assertEqual(txs[0].amount, 15)

    async def test_tc_adm_006_system_health_metrics_happy_path(self):
        """TC-ADM-006 [Happy Ending]: Mengambil metrik kesehatan sistem, CPU, RAM, DB status, dan Redis."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult(scalar_val=10))
        resp = await admin_router.get_health_metrics(db=mock_db)
        self.assertEqual(resp.data.database_status, "HEALTHY")
        self.assertGreater(resp.data.cpu_percent, 0.0)
        self.assertGreater(resp.data.memory_percent, 0.0)

    async def test_tc_adm_007_reindex_hnsw_pgvector_happy_path(self):
        """TC-ADM-007 [Happy Ending]: Menjadwalkan rekonstruksi indeks HNSW pgvector."""
        resp = await admin_router.reindex_hnsw()
        self.assertEqual(resp.data["status"], "SCHEDULED")
        self.assertIn("HNSW", resp.message)

    async def test_tc_adm_008_list_audit_logs_happy_path(self):
        """TC-ADM-008 [Happy Ending]: Mengambil rekam jejak audit log forensik aktivitas sistem."""
        log1 = AuditLog(
            id=uuid.uuid4(),
            action_type="USER_LOGIN",
            action_result="SUCCESS",
            created_at=datetime.now(timezone.utc),
            meta_data={"ip": "127.0.0.1"},
        )
        call_idx = 0
        def exec_handler(stmt):
            nonlocal call_idx
            call_idx += 1
            if call_idx == 1:
                return MockQueryResult(scalar_val=1)
            return MockQueryResult([log1])

        mock_db = MockAsyncSession(execute_handler=exec_handler)
        resp = await admin_router.list_audit_logs(action_type="USER_LOGIN", page=1, limit=10, db=mock_db)
        self.assertEqual(resp.data.total, 1)
        self.assertEqual(len(resp.data.items), 1)

    async def test_tc_adm_009_purge_expired_retention_uu_pdp_happy_path(self):
        """TC-ADM-009 [Happy Ending]: Purge dokumen retensi 30 hari permanen untuk kepatuhan UU PDP No. 27/2022."""
        doc_old = Document(
            id=uuid.uuid4(),
            original_filename="naskah_lama.pdf",
            stored_filename="naskah_lama.pdf",
            status="DELETED",
            deleted_at=datetime.now(timezone.utc) - timedelta(days=35),
            created_at=datetime.now(timezone.utc) - timedelta(days=40),
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([doc_old]))

        resp = await admin_router.purge_retention_data(retention_days=30, db=mock_db)
        self.assertEqual(resp.data["purged_count"], 1)
        self.assertIn(doc_old, mock_db.deleted)

        logs = [x for x in mock_db.added if isinstance(x, AuditLog)]
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].action_type, "DOCUMENT_PURGE")
        self.assertIn("UU PDP", logs[0].meta_data["compliance"])

    async def test_tc_adm_010_token_adjustment_negative_balance_bad_case(self):
        """TC-ADM-010 [Bad Case]: Penyesuaian token yang mengakibatkan saldo negatif ditolak HTTP 400."""
        user = User(id=uuid.uuid4())
        wallet = TokenWallet(user_id=user.id, balance=5)  # Saldo 5, dikurangi 10 -> -5
        mock_db = MockAsyncSession(
            get_handler=lambda m, ident: user,
            execute_handler=lambda s: MockQueryResult([wallet]),
        )
        req = TokenAdjustmentRequest(amount=-10, note="Pengurangan saldo berlebih")

        with self.assertRaises(HTTPException) as ctx:
            await admin_router.adjust_user_tokens(user_id=str(user.id), req=req, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("result in negative balance", ctx.exception.detail)

    async def test_tc_adm_011_nonexistent_user_identifier_bad_case(self):
        """TC-ADM-011 [Bad Case]: Akses detail pengguna dengan ID tidak dikenal memicu HTTP 404."""
        mock_db = MockAsyncSession(
            get_handler=lambda m, ident: None,
            execute_handler=lambda s: MockQueryResult([]),
        )
        with self.assertRaises(HTTPException) as ctx:
            await admin_router.get_user_detail_admin(user_id=str(uuid.uuid4()), db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("User not found", ctx.exception.detail)

    async def test_tc_adm_012_non_admin_rbac_blocked_blocker(self):
        """TC-ADM-012 [Blocker]: Pengguna non-admin (TRIAL/REVIEWER) diblokir dari konsol admin (HTTP 403)."""
        dosen = User(id=uuid.uuid4(), role="REVIEWER")
        checker = require_role("ADMIN")

        with self.assertRaises(HTTPException) as ctx:
            await checker(current_user=dosen)
        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)

    async def test_tc_adm_013_update_user_status_suspend_activate_happy_path(self):
        """TC-ADM-013 [Happy Ending]: Admin memperbarui status akun pengguna (suspend/activate)."""
        user = User(id=uuid.uuid4(), is_active=True)
        mock_db = MockAsyncSession(get_handler=lambda m, ident: user)
        from app.schemas.admin import UserStatusUpdateRequest

        # Suspend
        resp = await admin_router.update_user_status(user_id=str(user.id), req=UserStatusUpdateRequest(is_active=False), db=mock_db)
        self.assertFalse(user.is_active)
        self.assertIn("suspended", resp.message)

        # Re-activate
        resp2 = await admin_router.update_user_status(user_id=str(user.id), req=UserStatusUpdateRequest(is_active=True), db=mock_db)
        self.assertTrue(user.is_active)
        self.assertIn("activated", resp2.message)

    async def test_tc_adm_014_delete_user_and_wallet_admin_happy_path(self):
        """TC-ADM-014 [Happy Ending]: Admin menghapus akun pengguna beserta dompet tokennya."""
        user = User(id=uuid.uuid4(), full_name="User Hapus")
        wallet = TokenWallet(user_id=user.id, balance=10)
        mock_db = MockAsyncSession(
            get_handler=lambda m, ident: user,
            execute_handler=lambda s: MockQueryResult([wallet]),
        )
        resp = await admin_router.delete_user_admin(user_id=str(user.id), db=mock_db)
        self.assertIn(wallet, mock_db.deleted)
        self.assertIn(user, mock_db.deleted)
        self.assertTrue(mock_db.committed)

    async def test_tc_adm_015_find_user_by_email_identifier_happy_path(self):
        """TC-ADM-015 [Happy Ending]: Pencarian helper admin menemukan pengguna menggunakan string email (bukan UUID)."""
        user = User(id=uuid.uuid4(), email="dosen@kampus.ac.id")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([user]))

        found = await admin_router.find_user_by_identifier("dosen@kampus.ac.id", mock_db)
        self.assertIsNotNone(found)
        self.assertEqual(found.email, "dosen@kampus.ac.id")


if __name__ == "__main__":
    unittest.main()
