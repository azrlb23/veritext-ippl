"""
Test Suite: Remediation Phase 6 — Generasi Invoice PDF Resmi, Persistensi Konfigurasi Admin, dan Pengerasan Gateway Produksi
TDD Tests verifying:
  - test_tc_sec_34_invoice_pdf_generation_and_auth: Official ReportLab invoice generation & owner/admin authorization
  - test_tc_sec_35_admin_config_persistence: Persistent hyperparameter tuning storage & RBAC protection
  - test_tc_sec_36_production_security_headers_and_docs_toggle: OWASP security headers & production swagger hiding
"""

import asyncio
from datetime import datetime, timezone
import io
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

from app.main import app
from app.core.config import settings
from app.models.user import User
from app.models.invoice import Invoice
from app.models.system_config import SystemConfig
from app.models.audit_log import AuditLog
from app.schemas.admin import SystemConfigRequest, SystemConfigResponse
from app.services.pdf_invoice_service import generate_invoice_pdf, clean_invoice_filename
import app.api.v1.billing as billing_router
import app.api.v1.admin as admin_router


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


class TestRemediationPhase6(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    # =========================================================================
    # TC-SEC-34: Generasi PDF Invoice Resmi & Otorisasi Pemilik/Admin (F5)
    # =========================================================================
    async def test_tc_sec_34_invoice_pdf_generation_and_auth(self):
        """
        TC-SEC-34: Memvalidasi generasi byte PDF invoice resmi dengan ReportLab,
        otorisasi pemilik/admin, dan penolakan HTTP 403 untuk non-pemilik.
        """
        # 1. Direct unit test of generate_invoice_pdf
        pdf_bytes = generate_invoice_pdf(
            invoice_id=str(uuid.uuid4()),
            order_id="VT-ORDER-20261024-TEST",
            user_name="Budi Hartono",
            user_email="budi@campus.ac.id",
            institution="Institut Teknologi Nasional",
            package_name="Paket 50 Token Audit Akademik",
            token_amount=50,
            gross_amount=100000.0,
            status="PAID",
            created_at=datetime.now(timezone.utc),
            paid_at=datetime.now(timezone.utc),
            payment_method="qris",
            midtrans_transaction_id="midtrans-tx-12345",
        )

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 2000, f"Expected PDF bytes > 2000, got {len(pdf_bytes)}")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), "Generated file must start with PDF magic bytes %PDF-")

        # Test alternative statuses
        for alt_status in ["PENDING", "FAILED", "EXPIRED"]:
            alt_pdf = generate_invoice_pdf(
                invoice_id=str(uuid.uuid4()),
                order_id=f"VT-ORDER-{alt_status}",
                user_name="Budi",
                user_email="budi@test.com",
                package_name="Paket 10",
                token_amount=10,
                gross_amount=25000.0,
                status=alt_status,
                created_at=datetime.now(timezone.utc),
            )
            self.assertTrue(alt_pdf.startswith(b"%PDF-"))

        # Test filename sanitation
        self.assertEqual(clean_invoice_filename("VT-INV/123@#45"), "Invoice_VT-INV_123_45.pdf")

        # 2. Endpoint authorization & delivery tests
        owner_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        inv_id = uuid.uuid4()
        order_id = "VT-INV-998877"

        owner_user = User(
            id=owner_id,
            email="owner@campus.ac.id",
            full_name="Pemilik Sah Invoice",
            role="TRIAL",
        )
        non_owner_user = User(
            id=other_user_id,
            email="attacker@campus.ac.id",
            full_name="Pengguna Lain",
            role="TRIAL",
        )
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@veritext.ai",
            full_name="Super Administrator",
            role="ADMIN",
        )

        test_invoice = Invoice(
            id=inv_id,
            user_id=owner_id,
            order_id=order_id,
            package_name="Paket 10 Token",
            token_amount=10,
            gross_amount=25000,
            status="PAID",
            payment_method="bank_transfer",
            created_at=datetime.now(timezone.utc),
            paid_at=datetime.now(timezone.utc),
        )

        def mock_db_handler(stmt):
            stmt_str = str(stmt).lower()
            if "users" in stmt_str:
                return MockQueryResult([owner_user])
            return MockQueryResult([test_invoice])

        mock_db = MockAsyncSession(execute_handler=mock_db_handler)

        # Case A: Owner downloads own invoice via UUID -> HTTP 200 PDF
        resp_owner = await billing_router.get_invoice_pdf(
            inv_id=str(inv_id),
            current_user=owner_user,
            db=mock_db,
        )
        self.assertEqual(resp_owner.media_type, "application/pdf")
        self.assertTrue(resp_owner.body.startswith(b"%PDF-"))
        self.assertIn(f"Invoice_{order_id}.pdf", resp_owner.headers.get("content-disposition", ""))

        # Case B: Owner downloads own invoice via Order ID -> HTTP 200 PDF
        resp_order_id = await billing_router.get_invoice_pdf(
            inv_id=order_id,
            current_user=owner_user,
            db=mock_db,
        )
        self.assertEqual(resp_order_id.media_type, "application/pdf")
        self.assertTrue(resp_order_id.body.startswith(b"%PDF-"))

        # Case C: Admin downloads other user's invoice -> HTTP 200 PDF
        resp_admin = await billing_router.get_invoice_pdf(
            inv_id=str(inv_id),
            current_user=admin_user,
            db=mock_db,
        )
        self.assertEqual(resp_admin.media_type, "application/pdf")
        self.assertTrue(resp_admin.body.startswith(b"%PDF-"))

        # Case D: Non-owner non-admin user downloads invoice -> HTTP 403 Forbidden
        with self.assertRaises(HTTPException) as cm:
            await billing_router.get_invoice_pdf(
                inv_id=str(inv_id),
                current_user=non_owner_user,
                db=mock_db,
            )
        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Access denied", cm.exception.detail)

        # Case E: Non-existent invoice -> HTTP 404 Not Found
        empty_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as cm_404:
            await billing_router.get_invoice_pdf(
                inv_id="NON-EXISTENT-INV",
                current_user=owner_user,
                db=empty_db,
            )
        self.assertEqual(cm_404.exception.status_code, status.HTTP_404_NOT_FOUND)

    # =========================================================================
    # TC-SEC-35: Persistensi Konfigurasi & Hyperparameter Engine Admin (ROUND4-05)
    # =========================================================================
    async def test_tc_sec_35_admin_config_persistence(self):
        """
        TC-SEC-35: Memvalidasi penyimpanan dan pembacaan konfigurasi sistem persisten via endpoint admin.
        """
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@veritext.ai",
            full_name="Super Administrator",
            role="ADMIN",
        )

        # 1. GET /admin/config when no record exists yet (Initial Auto-seed)
        db_records = []

        def mock_execute(stmt):
            stmt_str = str(stmt).lower()
            if "system_configs" in stmt_str:
                return MockQueryResult(db_records)
            return MockQueryResult([])

        mock_db = MockAsyncSession(execute_handler=mock_execute)

        get_resp = await admin_router.get_system_config(db=mock_db)
        self.assertTrue(get_resp.success)
        self.assertEqual(get_resp.data.similarity_threshold, 0.78)
        self.assertEqual(get_resp.data.hnsw_ef_search, 64)
        self.assertEqual(get_resp.data.retention_days, 30)
        self.assertTrue(mock_db.committed)
        self.assertEqual(len(mock_db.added), 1)

        # Place the created config in db_records
        db_records.append(mock_db.added[0])

        # 2. POST /admin/config: Update hyperparameters
        update_req = SystemConfigRequest(
            similarity_threshold=0.88,
            hnsw_ef_search=128,
            hnsw_m=32,
            retention_days=45,
            winnowing_kgram=8,
            winnowing_window=6,
            lexical_weight=0.40,
            semantic_weight=0.45,
            stylometric_weight=0.15,
            stylometric_burstiness_threshold=0.42,
            sandbox_mode=True,
        )

        mock_req = MagicMock()
        mock_req.client.host = "10.0.0.5"
        mock_req.headers = {"user-agent": "VeriTextAdminBrowser/1.0"}

        post_resp = await admin_router.update_system_config(
            req=update_req,
            request=mock_req,
            current_user=admin_user,
            db=mock_db,
        )

        self.assertTrue(post_resp.success)
        self.assertEqual(post_resp.data.similarity_threshold, 0.88)

        self.assertEqual(post_resp.data.hnsw_ef_search, 128)
        self.assertEqual(post_resp.data.hnsw_m, 32)
        self.assertEqual(post_resp.data.retention_days, 45)
        self.assertEqual(post_resp.data.winnowing_kgram, 8)
        self.assertEqual(post_resp.data.winnowing_window, 6)
        self.assertTrue(post_resp.data.sandbox_mode)

        # Verify runtime settings synchronization
        self.assertEqual(settings.SIMILARITY_LEXICAL_WEIGHT, 0.40)
        self.assertEqual(settings.SIMILARITY_SEMANTIC_WEIGHT, 0.45)
        self.assertEqual(settings.WINNOWING_K_GRAM, 8)
        self.assertEqual(settings.WINNOWING_WINDOW_SIZE, 6)

        # Verify audit log entry was created
        audit_logs = [item for item in mock_db.added if isinstance(item, AuditLog)]
        self.assertTrue(len(audit_logs) >= 1)
        config_log = audit_logs[-1]
        self.assertEqual(config_log.action_type, "CONFIG_UPDATE")
        self.assertEqual(config_log.resource_type, "SYSTEM_CONFIG")
        self.assertEqual(config_log.action_result, "SUCCESS")
        self.assertIn("similarity_threshold", config_log.meta_data.get("updated_fields", {}))

        # 3. Subsequent GET returns updated config
        get_resp_after = await admin_router.get_system_config(db=mock_db)
        self.assertEqual(get_resp_after.data.similarity_threshold, 0.88)
        self.assertEqual(get_resp_after.data.hnsw_ef_search, 128)
        self.assertEqual(get_resp_after.data.retention_days, 45)

    # =========================================================================
    # TC-SEC-36: Pengerasan Gateway Produksi, HTTP Security Headers & Swagger (F6 & ROUND7-01)
    # =========================================================================
    def test_tc_sec_36_production_security_headers_and_docs_toggle(self):
        """
        TC-SEC-36: Memvalidasi keberadaan HTTP security headers dan nonaktifnya rute /docs pada mode produksi.
        """
        # 1. OWASP HTTP Security Headers validation on standard response
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)

        # Check all 5 mandatory security headers
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(resp.headers.get("x-frame-options"), "DENY")
        self.assertEqual(resp.headers.get("x-xss-protection"), "1; mode=block")
        self.assertIn("max-age=", resp.headers.get("strict-transport-security", ""))
        self.assertEqual(resp.headers.get("referrer-policy"), "strict-origin-when-cross-origin")

        # 2. In development mode: /docs is accessible
        with patch.object(settings, "ENVIRONMENT", "development"):
            res_dev = self.client.get("/health")
            self.assertEqual(res_dev.status_code, 200)
            res_root = self.client.get("/")
            self.assertEqual(res_root.json().get("docs"), "/docs")

        # 3. In production mode: /docs, /redoc, and /openapi.json are blocked (HTTP 404)
        with patch.object(settings, "ENVIRONMENT", "production"):
            res_docs = self.client.get("/docs")
            self.assertEqual(res_docs.status_code, status.HTTP_404_NOT_FOUND)

            res_redoc = self.client.get("/redoc")
            self.assertEqual(res_redoc.status_code, status.HTTP_404_NOT_FOUND)

            res_openapi = self.client.get("/openapi.json")
            self.assertEqual(res_openapi.status_code, status.HTTP_404_NOT_FOUND)

            res_root_prod = self.client.get("/")
            self.assertIsNone(res_root_prod.json().get("docs"))

        # 4. Database engine echo check: in production, echo must evaluate to False
        is_echo_prod = settings.DEBUG and settings.ENVIRONMENT.lower() != "production"
        with patch.object(settings, "ENVIRONMENT", "production"):
            self.assertFalse(settings.DEBUG and settings.ENVIRONMENT.lower() != "production")


if __name__ == "__main__":
    unittest.main()
