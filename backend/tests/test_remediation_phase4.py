"""
Test Suite: Remediation Phase 4 — Ketahanan Worker Celery, Pemulihan Task & Tata Kelola Sesi
TDD Tests verifying:
  - test_tc_sec_23_account_lockout_after_failed_logins
  - test_tc_sec_24_refresh_token_expiration_and_rotation
  - test_tc_sec_25_password_reset_flow_with_token
  - test_tc_sec_26_celery_worker_resilience_configuration
  - test_tc_sec_27_reaper_zombie_task_cleanup
  - test_tc_sec_28_pydantic_validation_error_handler_format
  - test_tc_sec_29_frontend_axios_401_interceptor
"""

import asyncio
from datetime import datetime, timedelta, timezone
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, Request, Response, status
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, hash_token, create_refresh_token
from app.models.user import User
from app.models.session import Session
from app.models.password_reset import PasswordReset
from app.models.audit import AuditTask
from app.models.wallet import TokenWallet, TokenTransaction
from app.schemas.auth import UserLoginRequest, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.services.auth_service import AuthService
from app.api.v1 import auth as auth_router


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
        if self.get_handler:
            return self.get_handler(entity, ident)
        if self.execute_handler:
            res = self.execute_handler(f"GET_{entity.__name__}_{ident}")
            if res is not None:
                if isinstance(res, MockQueryResult):
                    return res.scalar_one_or_none()
                return res
        return None


class MockSyncQuery:
    def __init__(self, items):
        self._items = list(items)

    def filter(self, *conds):
        return self

    def all(self):
        return list(self._items)

    def first(self):
        return self._items[0] if self._items else None

    def delete(self):
        cnt = len(self._items)
        self._items.clear()
        return cnt


class MockSyncSession:
    def __init__(self, query_map=None):
        self.query_map = query_map or {}
        self.added = []
        self.committed = False

    def query(self, entity):
        items = self.query_map.get(entity, [])
        return MockSyncQuery(items)

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.committed = True

    def close(self):
        pass


class TestRemediationPhase4(unittest.IsolatedAsyncioTestCase):
    """
    Test Suite Fase 4:
    Ketahanan Worker Celery, Pemulihan Task & Tata Kelola Sesi
    """

    async def test_tc_sec_23_account_lockout_after_failed_logins(self):
        """
        [C1] Proteksi Akun Lockout & Counter Percobaan Gagal Login.
        - 5 kali berturut-turut gagal login menaikkan failed_login_count hingga mengunci akun (lockout_until = now + 15m).
        - Percobaan login ke-6 saat terkunci ditolak dengan HTTP 429 atau 401 dan detail menginformasikan akun terkunci.
        - Login sukses mereset failed_login_count ke 0 dan lockout_until ke None.
        """
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            full_name="Mahasiswa Penguji Lockout",
            email="lockout_user@kampus.ac.id",
            password_hash=get_password_hash("PasswordBenar#123"),
            role="TRIAL",
            is_active=True,
            failed_login_count=0,
            lockout_until=None,
        )

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([user]))
        req_wrong = UserLoginRequest(email="lockout_user@kampus.ac.id", password="PasswordSalah!!")

        # 1. Empat kali gagal login pertama menaikkan counter secara berurutan
        for attempt in range(1, 5):
            with self.assertRaises(HTTPException) as ctx:
                await AuthService.authenticate_user(mock_db, req_wrong)
            self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(user.failed_login_count, attempt)
            self.assertIsNone(user.lockout_until)

        # 2. Percobaan gagal ke-5 memicu penguncian akun selama 15 menit
        with self.assertRaises(HTTPException) as ctx5:
            await AuthService.authenticate_user(mock_db, req_wrong)
        self.assertEqual(ctx5.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(user.failed_login_count, 5)
        self.assertIsNotNone(user.lockout_until)
        self.assertGreater(user.lockout_until, datetime.now(timezone.utc) + timedelta(minutes=14))

        # 3. Percobaan login saat akun terkunci langsung ditolak dengan HTTP 429 (Too Many Requests) / 401
        with self.assertRaises(HTTPException) as ctx_locked:
            await AuthService.authenticate_user(mock_db, req_wrong)
        self.assertIn(ctx_locked.exception.status_code, (status.HTTP_429_TOO_MANY_REQUESTS, status.HTTP_401_UNAUTHORIZED))
        self.assertTrue(
            "locked" in ctx_locked.exception.detail.lower() or "terkunci" in ctx_locked.exception.detail.lower(),
            f"Detail must indicate locked account: {ctx_locked.exception.detail}",
        )

        # 4. Setelah masa lockout berakhir, login dengan password benar berhasil dan me-reset counter ke 0
        user.lockout_until = datetime.now(timezone.utc) - timedelta(seconds=1)
        req_correct = UserLoginRequest(email="lockout_user@kampus.ac.id", password="PasswordBenar#123")
        auth_user, access_tok, refresh_tok = await AuthService.authenticate_user(mock_db, req_correct)

        self.assertEqual(auth_user.id, user_id)
        self.assertEqual(user.failed_login_count, 0)
        self.assertIsNone(user.lockout_until)
        self.assertTrue(bool(access_tok))
        self.assertTrue(bool(refresh_tok))

    async def test_tc_sec_24_refresh_token_expiration_and_rotation(self):
        """
        [C2 & C3] Validasi Kedaluwarsa dan Rotasi Refresh Token pada /auth/refresh.
        - Memvalidasi session.expires_at > now(). Token yang kedaluwarsa ditolak dengan HTTP 401 dan sesi dihapus.
        - Token yang valid dirotasi (menghasilkan refresh token baru, memperbarui hash di basis data, dan memperbarui cookie).
        """
        user_id = uuid.uuid4()
        user = User(id=user_id, email="session_user@kampus.ac.id", role="PREMIUM", is_active=True)

        # Kasus A: Sesi sudah kedaluwarsa (expires_at di masa lampau)
        old_raw_token = create_refresh_token(subject=str(user_id))
        expired_session = Session(
            id=uuid.uuid4(),
            user_id=user_id,
            refresh_token_hash=hash_token(old_raw_token),
            expires_at=datetime.now(timezone.utc) - timedelta(days=2),
        )

        mock_db_expired = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([expired_session]),
            get_handler=lambda e, ident: user,
        )

        with self.assertRaises(HTTPException) as ctx_exp:
            await auth_router.refresh_token_endpoint(
                response=MagicMock(),
                refresh_token=old_raw_token,
                db=mock_db_expired,
            )
        self.assertEqual(ctx_exp.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("expired", ctx_exp.exception.detail.lower())
        self.assertIn(expired_session, mock_db_expired.deleted)

        # Kasus B: Sesi valid -> Refresh Token Rotation
        valid_raw_token = create_refresh_token(subject=str(user_id))
        original_hash = hash_token(valid_raw_token)
        valid_session = Session(
            id=uuid.uuid4(),
            user_id=user_id,
            refresh_token_hash=original_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )

        mock_db_valid = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([valid_session]),
            get_handler=lambda e, ident: user,
        )
        mock_response = MagicMock()

        resp = await auth_router.refresh_token_endpoint(
            response=mock_response,
            refresh_token=valid_raw_token,
            db=mock_db_valid,
        )

        # Harus menghasilkan access_token baru
        self.assertIn("access_token", resp.data)
        self.assertTrue(bool(resp.data["access_token"]))

        # Rotasi: Hash di sesi harus berubah dan tidak lagi sama dengan hash token lama
        self.assertNotEqual(valid_session.refresh_token_hash, original_hash)

        # Cookie refresh_token baru harus dipasang pada response
        mock_response.set_cookie.assert_called_once()
        cookie_call_kwargs = mock_response.set_cookie.call_args[1]
        self.assertEqual(cookie_call_kwargs["key"], "refresh_token")
        self.assertTrue(cookie_call_kwargs["httponly"])
        self.assertNotEqual(cookie_call_kwargs["value"], valid_raw_token)

    async def test_tc_sec_25_password_reset_flow_with_token(self):
        """
        [NEW-REV-06 & C2] Alur Pemulihan Sandi Kriptografis & Pencabutan Sesi Aktif.
        - POST /auth/forgot-password membuat token acak aman di tabel password_resets.
        - POST /auth/reset-password memvalidasi token, memperbarui password hash pengguna,
          menandai reset record is_used = True, dan mencabut sesi aktif di tabel sessions.
        - POST /auth/change-password juga mencabut seluruh sesi aktif lainnya.
        """
        user_id = uuid.uuid4()
        old_password = "PasswordLama#123"
        user = User(
            id=user_id,
            full_name="Mahasiswa Reset Sandi",
            email="reset_target@kampus.ac.id",
            password_hash=get_password_hash(old_password),
            role="TRIAL",
            is_active=True,
        )

        # 1. Forgot password request
        mock_db = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([user]),
            get_handler=lambda e, ident: user,
        )

        req_forgot = ForgotPasswordRequest(email="reset_target@kampus.ac.id")
        resp_forgot = await auth_router.forgot_password(req=req_forgot, db=mock_db)
        self.assertEqual(resp_forgot.success, True)

        # Verifikasi bahwa objek PasswordReset telah dibuat dan ditambahkan ke database
        added_resets = [r for r in mock_db.added if isinstance(r, PasswordReset)]
        self.assertEqual(len(added_resets), 1)
        reset_obj = added_resets[0]
        self.assertEqual(reset_obj.user_id, user_id)
        self.assertIsNotNone(reset_obj.token_hash)
        self.assertFalse(reset_obj.is_used)

        # 2. Reset password request dengan token yang tidak valid -> Ditolak HTTP 400
        req_invalid_token = ResetPasswordRequest(token="token_palsu_random_123", new_password="PasswordBaru#456")
        mock_db_invalid = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as ctx_inv:
            await auth_router.reset_password(req=req_invalid_token, db=mock_db_invalid)
        self.assertEqual(ctx_inv.exception.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Reset password request dengan token valid
        # Ambil raw token dari response forgot password data atau mock
        raw_token = resp_forgot.data.get("reset_token", "sample_test_token_32chars_secure_value!")
        if "reset_token" not in resp_forgot.data:
            reset_obj.token_hash = hash_token(raw_token)

        mock_db_reset = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([reset_obj]),
            get_handler=lambda e, ident: user,
        )

        req_reset = ResetPasswordRequest(token=raw_token, new_password="PasswordBaru#456")
        resp_reset = await auth_router.reset_password(req=req_reset, db=mock_db_reset)
        self.assertEqual(resp_reset.success, True)

        # Verifikasi: Kata sandi pengguna telah diperbarui
        self.assertTrue(verify_password("PasswordBaru#456", user.password_hash))
        self.assertFalse(verify_password(old_password, user.password_hash))

        # Verifikasi: Token reset ditandai telah dipakai (is_used = True)
        self.assertTrue(reset_obj.is_used)
        self.assertIsNotNone(reset_obj.used_at)

        # Verifikasi: Eksekusi DELETE pada tabel sessions untuk mencabut semua sesi aktif pengguna
        deleted_stmts = [str(stmt) for stmt in mock_db_reset.executed_statements if "DELETE FROM SESSIONS" in str(stmt).upper()]
        self.assertGreater(len(deleted_stmts), 0)

        # 4. Ganti password via change_password juga harus mencabut seluruh sesi
        mock_db_change = MockAsyncSession()
        req_change = ChangePasswordRequest(old_password="PasswordBaru#456", new_password="PasswordGanti#789")
        resp_change = await auth_router.change_password(req=req_change, current_user=user, db=mock_db_change)
        self.assertEqual(resp_change.success, True)
        self.assertTrue(verify_password("PasswordGanti#789", user.password_hash))
        change_deleted_stmts = [str(stmt) for stmt in mock_db_change.executed_statements if "DELETE FROM SESSIONS" in str(stmt).upper()]
        self.assertGreater(len(change_deleted_stmts), 0)

    def test_tc_sec_26_celery_worker_resilience_configuration(self):
        """
        [FINAL-09 & FINAL-10] Konfigurasi Ketahanan Celery Worker & Result Expiration.
        - task_acks_late = True (Mencegah kehilangan task jika worker crash mendadak).
        - task_reject_on_worker_lost = True (Re-queue task jika worker mati).
        - result_expires = 86400 (TTL 24 jam mencegah penimbunan kunci Redis).
        - broker_connection_retry_on_startup = True.
        - task_time_limit = 1800 & task_soft_time_limit = 1500.
        - beat_schedule mendaftarkan periodic task reap_zombie_tasks.
        """
        from app.workers.celery_app import celery_app

        conf = celery_app.conf
        # Mendukung akses kamus maupun atribut pada objek konfigurasi Celery
        self.assertTrue(conf.get("task_acks_late") or getattr(conf, "task_acks_late", False))
        self.assertTrue(conf.get("task_reject_on_worker_lost") or getattr(conf, "task_reject_on_worker_lost", False))
        self.assertEqual(conf.get("result_expires") or getattr(conf, "result_expires", None), 86400)
        self.assertTrue(conf.get("broker_connection_retry_on_startup") or getattr(conf, "broker_connection_retry_on_startup", False))
        self.assertEqual(conf.get("task_time_limit") or getattr(conf, "task_time_limit", None), 1800)
        self.assertEqual(conf.get("task_soft_time_limit") or getattr(conf, "task_soft_time_limit", None), 1500)

        # Memverifikasi registrasi beat_schedule untuk zombie task reaper
        beat = conf.get("beat_schedule") or getattr(conf, "beat_schedule", {})
        self.assertTrue(any("reap_zombie_tasks" in str(item.get("task", "")) for item in beat.values()))

    def test_tc_sec_27_reaper_zombie_task_cleanup(self):
        """
        [ROUND3-06] Pembersihan Task Zombie yang Menggantung di Status PROCESSING.
        - Task yang berstatus PROCESSING melebihi ambang batas (> 30 menit) diubah ke FAILED dengan keterangan timeout.
        - Kuota token yang sebelumnya didebit dikembalikan secara otomatis ke wallet pengguna (CREDIT_REFUND).
        - Task yang masih berjalan normal (< 30 menit) atau berstatus QUEUED/SUCCESS tidak diubah.
        """
        from app.workers.tasks import clean_zombie_tasks

        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()

        # Task 1: Menggantung di PROCESSING selama 45 menit (Zombie Task)
        task_zombie = AuditTask(
            id=uuid.uuid4(),
            user_id=user1_id,
            status="PROCESSING",
            started_at=datetime.now(timezone.utc) - timedelta(minutes=45),
            audit_depth="FULL",
        )
        wallet_user1 = TokenWallet(id=uuid.uuid4(), user_id=user1_id, balance=3)
        tx_debit = TokenTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet_user1.id,
            transaction_type="DEBIT_AUDIT",
            amount=-2,
            balance_after=3,
            reference_id=task_zombie.id,
        )

        # Task 2: PROCESSING normal baru berjalan 10 menit (Belum timeout)
        task_normal = AuditTask(
            id=uuid.uuid4(),
            user_id=user2_id,
            status="PROCESSING",
            started_at=datetime.now(timezone.utc) - timedelta(minutes=10),
            audit_depth="FULL",
        )
        wallet_user2 = TokenWallet(id=uuid.uuid4(), user_id=user2_id, balance=5)

        # Task 3: QUEUED (Bukan zombie)
        task_queued = AuditTask(
            id=uuid.uuid4(),
            user_id=user2_id,
            status="QUEUED",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=40),
            audit_depth="TIER1_ONLY",
        )

        # Siapkan Mock Session yang mendukung kueri filter
        class ReaperMockSession:
            def __init__(self, tasks, wallets, txs):
                self.tasks = tasks
                self.wallets = {w.user_id: w for w in wallets}
                self.txs = {t.reference_id: t for t in txs}
                self.added = []
                self.committed = False

            def query(self, model):
                sess = self
                class MockQ:
                    def __init__(self):
                        self._conds = []

                    def filter(self, *conds):
                        self._conds.extend(conds)
                        return self

                    def all(self):
                        if model == AuditTask:
                            # Mengembalikan task zombie (PROCESSING > 30 menit)
                            cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
                            return [
                                t for t in sess.tasks
                                if t.status == "PROCESSING" and ((t.started_at and t.started_at < cutoff) or (not t.started_at and t.created_at and t.created_at < cutoff))
                            ]
                        return []

                    def first(self):
                        if model == TokenTransaction:
                            target_type = None
                            for c in self._conds:
                                val = getattr(getattr(c, "right", None), "value", None)
                                if val in ("CREDIT_REFUND", "DEBIT_AUDIT"):
                                    target_type = val
                                    break
                            all_txs = list(sess.txs.values()) + [x for x in sess.added if isinstance(x, TokenTransaction)]
                            for t in all_txs:
                                if target_type is None or t.transaction_type == target_type:
                                    return t
                            return None
                        return None
                
                # Mock khusus untuk Wallet
                if model == TokenWallet:
                    class WalletQ:
                        def filter(self, *conds):
                            class WalletFirst:
                                def first(inner_self):
                                    # Kembalikan wallet user1
                                    return sess.wallets.get(user1_id)
                            return WalletFirst()
                    return WalletQ()

                return MockQ()

            def add(self, item):
                self.added.append(item)

            def commit(self):
                self.committed = True

        mock_db = ReaperMockSession(
            tasks=[task_zombie, task_normal, task_queued],
            wallets=[wallet_user1, wallet_user2],
            txs=[tx_debit],
        )

        reaped_count = clean_zombie_tasks(mock_db, threshold_minutes=30)

        # 1. Hanya 1 task yang direap
        self.assertEqual(reaped_count, 1)

        # 2. Task zombie diubah statusnya ke FAILED dengan pesan timeout
        self.assertEqual(task_zombie.status, "FAILED")
        self.assertIn("timed out", task_zombie.error_message.lower())
        self.assertIsNotNone(task_zombie.completed_at)

        # 3. Saldo token dikembalikan (+2) ke dompet user1 (3 -> 5)
        self.assertEqual(wallet_user1.balance, 5)

        # 4. Transaksi CREDIT_REFUND tercatat
        refund_txs = [t for t in mock_db.added if isinstance(t, TokenTransaction) and t.transaction_type == "CREDIT_REFUND"]
        self.assertEqual(len(refund_txs), 1)
        self.assertEqual(refund_txs[0].amount, 2)
        self.assertEqual(refund_txs[0].balance_after, 5)

        # 5. Task normal dan task queued tidak disentuh
        self.assertEqual(task_normal.status, "PROCESSING")
        self.assertEqual(task_queued.status, "QUEUED")

        # 6. Idempotency: Eksekusi reaper kedua kali tidak melakukan reap ganda (0 task reaped) dan saldo tetap 5
        reaped_second = clean_zombie_tasks(mock_db, threshold_minutes=30)
        self.assertEqual(reaped_second, 0)
        self.assertEqual(wallet_user1.balance, 5)

    def test_tc_sec_28_pydantic_validation_error_handler_format(self):
        """
        [FINAL-07] Penanganan Kesalahan Validasi Masukan Pydantic HTTP 422.
        - Exception handler mengembalikan format JSON standar:
          {"status": "error", "message": "Validation Error", "detail": [...]}
        - Memastikan field 'input' yang memuat data mentah sensitif (seperti password) tidak dibocorkan.
        """
        client = TestClient(app)

        # Kirim payload register dengan tipe data yang salah dan password terlalu pendek
        invalid_payload = {
            "full_name": "A",  # min_length 2
            "email": "bukan_email_valid",
            "password": "123",  # min_length 8
        }

        resp = client.post("/api/v1/auth/register", json=invalid_payload)
        self.assertEqual(resp.status_code, getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY))

        data = resp.json()
        self.assertEqual(data.get("status"), "error")
        self.assertEqual(data.get("message"), "Validation Error")
        self.assertIsInstance(data.get("detail"), list)
        self.assertGreater(len(data["detail"]), 0)

        # Sensor data sensitif: pastikan nilai masukan '123' tidak dibocorkan pada field error
        for err_item in data["detail"]:
            self.assertIn("field", err_item)
            self.assertIn("message", err_item)
            self.assertNotIn("input", err_item)
            # Nilai mentah password dilarang muncul di respons
            self.assertNotEqual(err_item.get("field"), "123")

    def test_tc_sec_29_frontend_axios_401_interceptor(self):
        """
        [ROUND4-02] Respons Interceptor Axios 401 pada Frontend.
        - Memverifikasi implementasi frontend/src/services/api.ts menangani respons HTTP 401:
          1. Menghapus 'veritext_access_token' dan 'veritext_user' dari localStorage.
          2. Memanggil logout pada auth store untuk mereset reactive state Pinia.
          3. Mengarahkan peramban ke rute '/login'.
        """
        api_ts_path = os.path.abspath(
            os.path.join(BACKEND_DIR, "..", "frontend", "src", "services", "api.ts")
        )
        self.assertTrue(os.path.exists(api_ts_path), f"File {api_ts_path} must exist")

        with open(api_ts_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Harus memiliki penanganan status 401
        self.assertIn("401", content)

        # 2. Harus membersihkan storage token dan user
        self.assertIn('localStorage.removeItem("veritext_access_token")', content)
        self.assertIn('localStorage.removeItem("veritext_user")', content)

        # 3. Harus mereset state auth Pinia (logout)
        self.assertTrue(
            "logout" in content or "useAuthStore" in content,
            "api.ts response interceptor must trigger authStore logout/reset",
        )

        # 4. Harus mengarahkan ke '/login'
        self.assertIn("/login", content)


if __name__ == "__main__":
    unittest.main()
